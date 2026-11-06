"""
display case v3 = v2 with NO aluminium.  Run inside FreeCAD:

    import sys; sys.path.insert(0, "/home/rohith/project_docker/workspace/display_case/v3")
    import build_v3 as b; b.build()

What changes from v2 (everything else is copied unchanged):
  * the 160 x 130 x 3 aluminium spine is gone
  * rear panel: 4 printed bosses with M4 brass heat-set insert pockets, pressed in FROM THE INSIDE,
    plus a 2 mm rib grid, all in the 3 mm the spine used (z 5.8 .. 8.8, still 2.0 mm off the LCD)
  * the 8 x M2.5 spine pilot holes are filled
  * new printed part `seam_bridge` (30 x 127.5 x 3) bonded over the rear seam between the existing
    locating fences - it takes over the spine's job of bridging the seam

Case frame (same as v2): x right, y up, z from the bezel face (0) to the rear face (11.3).
Rear-panel print files are in print orientation: outer face on the bed, so
    print = Rotation(X, 180) * case + (dx, 116.36, 11.3),  dx = 180.99 for the L half, 0 for R.
"""
import os
import shutil

import FreeCAD as App
import Part

V = App.Vector
ROOT = "/home/rohith/project_docker/workspace/display_case/"
V2, V3 = ROOT + "v2/", ROOT + "v3/"

# --------------------------------------------------------------- parameters --
VESA = [(-50.0, -10.0), (50.0, -10.0), (-50.0, 90.0), (50.0, 90.0)]
SPINE_PILOTS = [(x, y) for x in (-65.0, -25.0, 25.0, 65.0) for y in (-5.0, 85.0)]
Z_LCD_SIDE, Z_INNER, Z_OUTER = 5.8, 8.8, 11.3        # boss bottom (2.0 off the LCD), skin inner, outer face
INSERT_OD, INSERT_L = 5.6, 4.0                       # M4 x 4 x 5.6 knurled brass insert (change to yours)
POCKET_D = INSERT_OD - 0.2                           # heat-set interference
POCKET_DEPTH = INSERT_L + 0.3                        # from the inner (LCD-side) face of the boss
CLEAR_D = 4.5                                        # M4 clearance through the remaining skin
BOSS_D = 11.0
RIB_W = 2.0
GRID_X = (16.3, 50.0, 79.0)                          # |x| of vertical ribs (inner edge, VESA column, outer edge)
GRID_Y = (-24.0, -10.0, 40.0, 90.0, 104.0)           # horizontal ribs
GRID_X0, GRID_X1 = 15.3, 80.0                        # grid spans |x| 15.3 .. 80 (seam bridge lives in |x| < 15)
BRIDGE = (-14.85, 14.85, -24.85, 102.5)              # x0, x1, y0, y1 between the fences, clear of the 2 seat holes
SCREW_MAX_PAST_PLATE = 5.0                           # VESA screw length rule (tip stays 0.5 mm inside the insert)


def _box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def _cyl(r, z0, z1, x, y):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def add_tools(side):
    """Material added on the inner face (case frame).  side = -1 (L half), +1 (R half), 0 = both."""
    out = []
    sides = (-1, 1) if side == 0 else (side,)
    zt = Z_INNER + 0.05
    for sg in sides:
        for x, y in VESA:
            if x * sg > 0:
                out.append(_cyl(BOSS_D / 2, Z_LCD_SIDE, zt, x, y))
        for ax in GRID_X:
            x = sg * ax
            out.append(_box(x - RIB_W / 2, x + RIB_W / 2, -25.0, 105.0, Z_LCD_SIDE, zt))
        x0, x1 = sorted((sg * GRID_X0, sg * GRID_X1))
        for y in GRID_Y:
            out.append(_box(x0, x1, y - RIB_W / 2, y + RIB_W / 2, Z_LCD_SIDE, zt))
        for x, y in SPINE_PILOTS:                                       # fill the old spine pilots
            if x * sg > 0:
                out.append(_cyl(1.1, Z_INNER, Z_OUTER - 0.4, x, y))      # flush with the inner face
    return out


def cut_tools(side):
    out = []
    sides = (-1, 1) if side == 0 else (side,)
    for sg in sides:
        for x, y in VESA:
            if x * sg > 0:
                out.append(_cyl(POCKET_D / 2, Z_LCD_SIDE - 0.5, Z_LCD_SIDE + POCKET_DEPTH, x, y))
                out.append(Part.makeCone(POCKET_D / 2 + 0.4, POCKET_D / 2, 0.4, V(x, y, Z_LCD_SIDE - 0.001)))  # lead-in
                out.append(_cyl(CLEAR_D / 2, Z_LCD_SIDE, Z_OUTER + 1, x, y))
    return out


def apply(shape, side, pl=None):
    adds, cuts = add_tools(side), cut_tools(side)
    if pl is not None:
        adds = [_moved(t, pl) for t in adds]
        cuts = [_moved(t, pl) for t in cuts]
    a = adds[0].fuse(adds[1:])
    c = cuts[0].fuse(cuts[1:])
    s = shape.fuse(a).cut(c)
    s = s.removeSplitter()
    assert s.isValid() and len(s.Solids) == 1, "v3 rear panel boolean failed"
    return Part.Solid(s.Solids[0])


def _moved(s, pl):
    c = s.copy()
    c.Placement = pl.multiply(c.Placement)
    return c


def print_placement(side):
    return App.Placement(V(180.99 if side < 0 else 0.0, 116.36, Z_OUTER), App.Rotation(V(1, 0, 0), 180))


def seam_bridge():
    x0, x1, y0, y1 = BRIDGE
    s = _box(x0, x1, y0, y1, Z_LCD_SIDE, Z_INNER)
    s = s.makeChamfer(0.6, [e for e in s.Edges if abs(e.BoundBox.ZMin - Z_LCD_SIDE) < 1e-6 and e.BoundBox.ZLength < 1e-6])
    return s


def write(shape, path):
    import MeshPart
    shape.exportStep(path + ".step")
    MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.02, AngularDeflection=0.15, Relative=False).write(path + ".stl")


def build():
    rep = []

    def line(x):
        rep.append(x)
        print(x)

    for d in ("", "3d_print_files", "print_beds"):
        os.makedirs(V3 + d, exist_ok=True)
    # ---------------- assembly document
    src = V2 + "monitor_case_v2.FCStd"
    v2doc = next((d for d in App.listDocuments().values() if d.FileName == src), None) or App.openDocument(src, True)
    shapes = {o.Name: o.Shape.copy() for o in v2doc.Objects if hasattr(o, "Shape") and o.Shape.Volume > 0}
    rp3 = apply(shapes["rear_panel"], 0)
    bridge = seam_bridge()
    if "monitor_case_v3" in App.listDocuments():
        App.closeDocument("monitor_case_v3")
    doc = App.newDocument("monitor_case_v3")
    colors = {"front_frame": (0.12, 0.12, 0.13), "rear_panel": (0.30, 0.30, 0.32), "io_block": (0.20, 0.20, 0.22),
              "panel_ref": (0.05, 0.10, 0.20), "board_ref": (0.10, 0.45, 0.20), "seam_bridge": (0.90, 0.45, 0.10)}
    for n, s in (("front_frame", shapes["front_frame"]), ("rear_panel", rp3), ("seam_bridge", bridge),
                 ("io_block", shapes["io_block"]), ("panel_ref", shapes["panel_ref"]), ("board_ref", shapes["board_ref"])):
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
        if App.GuiUp:
            o.ViewObject.ShapeColor = colors[n]
    doc.recompute()
    doc.saveAs(V3 + "monitor_case_v3.FCStd")
    # ---------------- checks in the assembly frame
    lcd, brd, io = shapes["panel_ref"], shapes["board_ref"], shapes["io_block"]
    new = rp3.cut(shapes["rear_panel"])                       # only the added material
    line("== display case v3 checks ==")
    line(f"added material {new.Volume / 1000:.1f} cm3; rear panel {shapes['rear_panel'].Volume / 1000:.1f} -> {rp3.Volume / 1000:.1f} cm3")
    line(f"new ribs/bosses to LCD: {new.distToShape(lcd)[0]:.2f} mm (AUO: nothing may press the reflector; v2 kept 2.0)")
    line(f"seam bridge to LCD: {bridge.distToShape(lcd)[0]:.2f} mm")
    for n, s in (("LCD", lcd), ("driver board", brd), ("io_block", io), ("front frame", shapes["front_frame"])):
        v = rp3.common(s).Volume + bridge.common(s).Volume
        line(f"overlap rear panel v3 + seam bridge vs {n:12s}: {v:.3f} mm3")
    line(f"seam bridge vs rear panel: {bridge.common(rp3).Volume:.3f} mm3 overlap, gap {bridge.distToShape(rp3)[0]:.2f} mm")
    stack = (Z_OUTER - (Z_LCD_SIDE + POCKET_DEPTH))
    line(f"insert M4 x {INSERT_L:g} x Ø{INSERT_OD:g}: pocket Ø{POCKET_D:.1f} x {POCKET_DEPTH:.1f} from the LCD side, "
         f"skin shoulder {stack:.1f} mm, then Ø{CLEAR_D} to the outside")
    line(f"VESA screw: at most {SCREW_MAX_PAST_PLATE:.1f} mm past the arm plate (insert bottom is at "
         f"{Z_OUTER - Z_LCD_SIDE:.1f} mm). M4 x 8 with the stands' plates = 4.4 mm -> "
         f"{4.4 - stack - 0.3:.1f} mm of thread in the insert")
    # ---------------- print files: the v2 halves with the same changes
    pf2, pf3 = V2 + "3d_print_files/", V3 + "3d_print_files/"
    for fn in sorted(os.listdir(pf2)):
        if fn.startswith("rear_panel_"):
            continue
        shutil.copy(pf2 + fn, pf3 + fn)                       # front frames, io_block, rear_splice unchanged
    for base in ("rear_panel_L", "rear_panel_R", "rear_panel_L_selfsupport", "rear_panel_R_selfsupport"):
        side = -1 if "_L" in base else 1
        half = Part.read(pf2 + base + ".step")
        pl = print_placement(side)
        # sanity: the transform puts v2's VESA clearance holes where the file has them
        h = [f for f in half.Faces if type(f.Surface).__name__ == "Cylinder" and abs(2 * f.Surface.Radius - 4.5) < 0.01]
        want = sorted((round(pl.multVec(V(x, y, 0)).x, 2), round(pl.multVec(V(x, y, 0)).y, 2)) for x, y in VESA if x * side > 0)
        got = sorted(set((round(f.Surface.Center.x, 2), round(f.Surface.Center.y, 2)) for f in h))
        assert want == got, (base, want, got)
        new_half = apply(half, side, pl)
        bb = new_half.BoundBox
        write(new_half, pf3 + base)
        line(f"{base:26s} {half.Volume / 1000:6.1f} -> {new_half.Volume / 1000:6.1f} cm3, "
             f"{bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.2f} (bed 256), z min {bb.ZMin:.2f}")
    b = seam_bridge()
    b.rotate(V(0, 0, 0), V(1, 0, 0), 180)                    # bonding face (z 8.8) on the bed
    b.translate(V(-b.BoundBox.XMin, -b.BoundBox.YMin, -b.BoundBox.ZMin))
    write(b, pf3 + "seam_bridge")
    # ---------------- print beds: same layout as v2; beds 3/4 rebuilt, bed 6 = seam bridge
    pb2, pb3 = V2 + "print_beds/", V3 + "print_beds/"
    for bed in sorted(os.listdir(pb2)):
        if not os.path.isdir(pb2 + bed):
            continue
        if bed.startswith(("bed3", "bed4")):
            base = "rear_panel_L" if bed.startswith("bed3") else "rear_panel_R"
            old_bed = Part.read(pb2 + bed + "/" + bed + ".step")
            old_part = Part.read(pf2 + base + ".step")
            off = old_bed.BoundBox.Center - old_part.BoundBox.Center      # same placement on the bed as v2
            assert abs(old_bed.Volume - old_part.Volume) < 1.0, (bed, "v2 bed is not the plain half")
            p = Part.read(pf3 + base + ".step")
            p.translate(off)
            os.makedirs(pb3 + bed + "/originals", exist_ok=True)
            write(p, pb3 + bed + "/" + bed)
            for ext in ("step", "stl"):
                shutil.copy(pf3 + base + "." + ext, pb3 + bed + "/originals/" + base + "." + ext)
        else:
            if os.path.exists(pb3 + bed):
                shutil.rmtree(pb3 + bed)
            shutil.copytree(pb2 + bed, pb3 + bed)
    os.makedirs(pb3 + "bed6_seam_bridge", exist_ok=True)
    bb6 = Part.read(pf3 + "seam_bridge.step")
    bb6.translate(V(128 - bb6.BoundBox.Center.x, 128 - bb6.BoundBox.Center.y, 0))
    write(bb6, pb3 + "bed6_seam_bridge/bed6_seam_bridge")
    line("print beds: bed1/2/5 copied from v2, bed3/4 rebuilt at v2's positions, bed6 = seam bridge "
         "(tiny - add it to any other bed in the slicer)")
    with open(V3 + "checks.txt", "w") as fh:
        fh.write("\n".join(rep) + "\n")
    return doc
