"""
I/O block for monitor_case_v2 - corrected build (2026-10-05).

What changed vs the original io_block() in monitor_case_v2.py:
  * The driver board sits ON TOP of the standoffs with its components (and
    ports) facing the rear panel.  The original put the connectors on the roof
    side of the PCB, so the ports hung past the open rim.
  * Standoffs 13.9 -> 3.0 mm.  The 11 mm DC jack (board spec: 12.6 +-0.3 mm
    total) now sits inside the block with 1.2 mm of wall under its opening.
  * Port openings re-cut on the component side, at the datasheet x centres,
    sized to the connector bodies + 0.4 mm clearance.
  * Board screws are M2.5x5 (the blind pilot is 4.4 mm deep).
  * The wall opposite the ports steps out by EXTRA_Y (2 mm) above the rim band
    so the 40-pin eDP plug (CN10) can seat and its cable can bend.  The rim,
    spigot and screw bosses that join the rear panel are unchanged.

Run inside FreeCAD (document monitor_case_v2 open):
    import sys; sys.path.insert(0, "/home/rohith/project_docker/workspace/display_case/v2")
    import io_block_fix as f; f.apply(export_files=True, save=True)
"""
import os

import FreeCAD as App
import Part
import MeshPart

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- unchanged v2 parameters (params.py) ----
SLAB_T = 11.3
BLK_WALL, BLK_R, BLK_TOP_CH = 2.0, 6.0, 1.2
BRD_W, BRD_H, BRD_PCB_T, BRD_Y_BOT, BRD_CLEAR = 95.0, 60.1, 1.6, -92.0, 1.0
BLK_BOSS_ROOM, BLK_BOSS_D, BLK_BOSS_DY = 6.0, 5.5, 22.0
BLK_W = BRD_W + 2 * (BRD_CLEAR + BLK_BOSS_ROOM + BLK_WALL)       # 113.0
BLK_H = BRD_H + 2 * (BRD_CLEAR + BLK_WALL)                       # 66.1
BLK_Y0 = BRD_Y_BOT - BRD_CLEAR - BLK_WALL                        # -95.0
BLK_Y1 = BLK_Y0 + BLK_H                                          # -28.9
BLK_CY = BLK_Y0 + BLK_H / 2
BLK_BOSS_X = BRD_W / 2 + BRD_CLEAR + BLK_BOSS_ROOM / 2
Z_ROOF = 30.8
ROOF_IN = Z_ROOF - BLK_WALL
BLK_SPIGOT_T = 0.6
SCREW_PILOT_D = 2.10
BRD_HOLES = [(4.7, 23.0), (85.0, 23.0), (4.7, 56.5), (85.0, 56.5)]
BRD_HOLE_D, BRD_HOLE_KEEPOUT = 3.2, 7.0
VENT_W, VENT_H, VENT_N, VENT_PITCH = 2.0, 12.0, 5, 7.5
VENT_TOP_N, VENT_TOP_W, VENT_TOP_L = 7, 2.5, 14.0
VENT_BOT_W, VENT_BOT_L = 2.5, 10.0
PORT_CLEAR, PORT_LIP = 0.40, 0.80
KEYPAD_W, KEYPAD_H = 9.0, 3.5
SIDE_SLOT_W, SIDE_SLOT_H = 8.0, 4.0
BRD_SIDE_CONN_Y = (23.4, 47.4)
BRD_EDP_X = (53.3, 78.0)

# ---- the fix ----
STANDOFF_H = 3.0                         # was 13.9
Z_PCB_BACK = ROOF_IN - STANDOFF_H        # 25.8  PCB back face on the standoff tips
Z_COMP = Z_PCB_BACK - BRD_PCB_T          # 24.2  component face, ports hang toward the rear panel
COMP_MAX = 12.6 + 0.3 - BRD_PCB_T        # 11.3  datasheet sec 4: height 12.6 +-0.3
# name, datasheet x centre, body W, body H below the PCB face, overhang past PCB edge, shape
PORTS = [("CN1 DC",    6.0,  9.5, 11.3, 2.0, "rect"),
         ("CN4 HDMI", 24.0, 15.0,  6.1, 2.0, "rect"),
         ("CN5 HDMI", 46.6, 15.0,  6.1, 2.0, "rect"),
         ("CN3 DP",   69.0, 17.0,  6.3, 2.0, "rect"),
         ("CN7 3.5",  87.2,  6.0,  5.6, 0.0, "round")]
AUDIO_HOLE_D = 8.0
EXTRA_Y = 2.0                            # eDP room on the wall opposite the ports
Z_STEP0 = SLAB_T + 2.0                   # rim band below this is untouched
Z_STEP1 = Z_STEP0 + EXTRA_Y              # 45 deg step, full extra room above


def cx(bx):
    return BRD_W / 2 - bx                # board mirrored in case X (holes line up)


def _box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def _edges_par(s, axis):
    out = []
    for e in s.Edges:
        try:
            t = e.tangentAt(e.FirstParameter)
        except Exception:
            continue
        if abs(abs(t.dot(axis)) - 1) < 1e-6:
            out.append(e)
    return out


def _rr(x0, x1, y0, y1, z0, z1, r=0.0):
    s = _box(x0, x1, y0, y1, z0, z1)
    if r > 1e-9:
        r = min(r, (x1 - x0) / 2 - 1e-3, (y1 - y0) / 2 - 1e-3)
        if r > 1e-9:
            s = s.makeFillet(r, _edges_par(s, V(0, 0, 1)))
    return s


def _rry(x0, x1, y0, y1, z0, z1, r):
    s = _box(x0, x1, y0, y1, z0, z1)
    r = min(r, (x1 - x0) / 2 - 1e-3, (z1 - z0) / 2 - 1e-3)
    return s.makeFillet(r, _edges_par(s, V(0, 1, 0))) if r > 1e-9 else s


def _cyl(x, y, z0, d, h):
    return Part.makeCylinder(d / 2, h, V(x, y, z0))


def _ycyl(x, z, y0, d, L):
    return Part.makeCylinder(d / 2, L, V(x, y0, z), V(0, 1, 0))


def _rr_wire(x0, x1, y0, y1, z, r):
    s = _rr(x0, x1, y0, y1, z, z + 1.0, r)
    f = [f for f in s.Faces
         if abs(f.BoundBox.ZMax - z) < 1e-6 and abs(f.BoundBox.ZMin - z) < 1e-6][0]
    return f.OuterWire


def _stepped(x_half, y0, y1, r, z_lo, z_top, grow):
    """Rounded-rect prism whose +Y face moves out by `grow` through a 45 deg
    step between Z_STEP0 and Z_STEP1 (prints roof-down with no overhang)."""
    lower = _rr(-x_half, x_half, y0, y1, z_lo, Z_STEP0, r)
    trans = Part.makeLoft([_rr_wire(-x_half, x_half, y0, y1, Z_STEP0, r),
                           _rr_wire(-x_half, x_half, y0, y1 + grow, Z_STEP1, r)],
                          True, True)
    upper = _rr(-x_half, x_half, y0, y1 + grow, Z_STEP1, z_top, r)
    return lower.fuse(trans).fuse(upper).removeSplitter()


def _spigot(grow, z0):
    ohx = BLK_W / 2 - 0.2 + grow
    oy0, oy1 = BLK_Y0 + 0.2 - grow, BLK_Y1 - 0.2 + grow
    ihx = BLK_W / 2 - BLK_WALL + 0.2 - grow
    iy0, iy1 = BLK_Y0 + BLK_WALL - 0.2 + grow, BLK_Y1 - BLK_WALL + 0.2 - grow
    z1 = SLAB_T + (1.0 if grow else 0.0)
    out = _rr(-ohx, ohx, oy0, oy1, z0, z1, BLK_R - 0.2 + grow)
    inn = _rr(-ihx, ihx, iy0, iy1, z0 - 1.0, SLAB_T + 2.0,
              max(BLK_R - BLK_WALL + 0.2 - grow, 0.1))
    return out.cut(inn)


def block_screw_xy():
    return [(sx * BLK_BOSS_X, BLK_CY + sy * BLK_BOSS_DY) for sx in (-1, 1) for sy in (-1, 1)]


def port_tool(p, grow, y0, y1):
    name, bx, w, h, ovh, shape = p
    x = cx(bx)
    if shape == "round":
        return _ycyl(x, Z_COMP - h / 2, y0, AUDIO_HOLE_D + 2 * grow, y1 - y0)
    hw = w / 2 + PORT_CLEAR + grow
    return _rry(x - hw, x + hw, y0, y1,
                Z_COMP - h - PORT_CLEAR - grow, Z_COMP + PORT_CLEAR + grow, 1.0 + grow)


def io_block():
    b = _stepped(BLK_W / 2, BLK_Y0, BLK_Y1, BLK_R, SLAB_T, Z_ROOF, EXTRA_Y)
    top = [e for e in b.Edges if min(v.Point.z for v in e.Vertexes) > Z_ROOF - 1e-6]
    b = b.makeChamfer(BLK_TOP_CH, top)
    b = b.cut(_stepped(BLK_W / 2 - BLK_WALL, BLK_Y0 + BLK_WALL, BLK_Y1 - BLK_WALL,
                       max(BLK_R - BLK_WALL, 0.1), SLAB_T - 1.0, ROOF_IN, EXTRA_Y))
    b = b.fuse(_spigot(0.0, SLAB_T - BLK_SPIGOT_T)).removeSplitter()
    for x, y in block_screw_xy():
        b = b.fuse(_cyl(x, y, SLAB_T, BLK_BOSS_D, ROOF_IN - SLAB_T))
    b = b.removeSplitter()
    for x, y in block_screw_xy():
        b = b.cut(_cyl(x, y, SLAB_T - 1.0, SCREW_PILOT_D, 7.0))

    # standoffs: 3 mm, PCB back face on the tips, blind pilot leaves 0.6 mm of roof
    for bx, by in BRD_HOLES:
        b = b.fuse(_cyl(cx(bx), BRD_Y_BOT + by, Z_PCB_BACK, BRD_HOLE_D + 2.8, STANDOFF_H + 0.01))
    b = b.removeSplitter()
    for bx, by in BRD_HOLES:
        b = b.cut(_cyl(cx(bx), BRD_Y_BOT + by, Z_PCB_BACK - 1.0, SCREW_PILOT_D,
                       1.0 + (Z_ROOF - 0.6 - Z_PCB_BACK)))

    # port openings + capture lips on the component side
    yw0, yw1 = BLK_Y0, BLK_Y0 + BLK_WALL
    for p in PORTS:
        b = b.cut(port_tool(p, 0.0, yw0 - 1.0, yw1 + 1.0))
    for p in PORTS:
        b = b.fuse(port_tool(p, PORT_LIP, yw1, yw1 + PORT_LIP))
    b = b.removeSplitter()
    for p in PORTS:
        b = b.cut(port_tool(p, 0.0, yw0 - 1.0, yw1 + PORT_LIP + 1.0))

    # side vents (as v2)
    zc = (14.9 + ROOF_IN) / 2
    for i in range(VENT_N):
        vy = BLK_CY + (i - (VENT_N - 1) / 2) * VENT_PITCH
        for sx in (-1, 1):
            c = sx * (BLK_W / 2 - BLK_WALL / 2)
            b = b.cut(_box(c - BLK_WALL, c + BLK_WALL, vy - VENT_W / 2, vy + VENT_W / 2,
                           zc - VENT_H / 2, zc + VENT_H / 2))
    # outlet vents in the (now stepped-out) wall opposite the ports
    y1n = BLK_Y1 + EXTRA_Y
    for i in range(VENT_TOP_N):
        c = (i - (VENT_TOP_N - 1) / 2) * (VENT_TOP_L + 5.0)
        b = b.cut(_box(c - VENT_TOP_L / 2, c + VENT_TOP_L / 2, y1n - BLK_WALL - 1.0, y1n + 1.0,
                       ROOF_IN - VENT_TOP_W - 1.0, Z_ROOF + 1.0))
    # inlet vents in the port wall, minus the one that would run into the DC jack
    for i in range(5):
        c = (i - 2) * (VENT_BOT_L + 8.0)
        if abs(c - cx(6.0)) < 12.0:
            continue
        b = b.cut(_box(c - VENT_BOT_L / 2, c + VENT_BOT_L / 2, BLK_Y0 - 1.0, BLK_Y0 + BLK_WALL + 1.0,
                       SLAB_T + 1.0, SLAB_T + 1.0 + VENT_BOT_W))
    # keypad harness and right-edge connectors, component side
    b = b.cut(_box(-25.0 - KEYPAD_W / 2, -25.0 + KEYPAD_W / 2, y1n - BLK_WALL - 1.0, y1n + 1.0,
                   Z_COMP - KEYPAD_H, Z_COMP + PORT_CLEAR))
    for cy in BRD_SIDE_CONN_Y:
        y = BRD_Y_BOT + cy
        b = b.cut(_box(-BLK_W / 2 - 1.0, -BLK_W / 2 + BLK_WALL + 1.0,
                       y - SIDE_SLOT_W / 2, y + SIDE_SLOT_W / 2,
                       Z_COMP - SIDE_SLOT_H, Z_COMP + PORT_CLEAR))
    return b.removeSplitter()


def board_ref():
    b = _box(-BRD_W / 2, BRD_W / 2, BRD_Y_BOT, BRD_Y_BOT + BRD_H, Z_COMP, Z_PCB_BACK)
    env = _box(-BRD_W / 2, BRD_W / 2, BRD_Y_BOT + 2.0, BRD_Y_BOT + BRD_H, Z_COMP - COMP_MAX, Z_COMP)
    for bx, by in BRD_HOLES:
        env = env.cut(_cyl(cx(bx), BRD_Y_BOT + by, Z_COMP - COMP_MAX - 1.0,
                           BRD_HOLE_KEEPOUT, COMP_MAX + 2.0))
    b = b.fuse(env)
    for name, bx, w, h, ovh, shape in PORTS:
        x = cx(bx)
        b = b.fuse(_box(x - w / 2, x + w / 2, BRD_Y_BOT - ovh, BRD_Y_BOT + 12.0, Z_COMP - h, Z_COMP))
    x0, x1 = cx(BRD_EDP_X[1]), cx(BRD_EDP_X[0])
    b = b.fuse(_box(x0, x1, BRD_Y_BOT + BRD_H - 4.0, BRD_Y_BOT + BRD_H, Z_COMP - 2.0, Z_COMP))
    return b.removeSplitter()


# ------------------------------------------------------------------ export --
def _write(shape, p):
    shape.exportStep(p + ".step")
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.02,
                               AngularDeflection=0.15, Relative=False)
    m.write(p + ".stl")


def export(blk, out_root=HERE):
    BED, BED_GAP, BED_MARGIN = 256.0, 6.0, 10.0
    flat = blk.copy()
    flat.rotate(V(0, 0, 0), V(1, 0, 0), 180)          # roof down, cavity up
    bb = flat.BoundBox
    flat.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    spl = Part.Shape()
    spl.read(os.path.join(out_root, "print_beds/bed5_io_block_splice/originals/rear_splice.step"))
    sb = spl.BoundBox
    spl.translate(V(-sb.XMin, -sb.YMin, -sb.ZMin))
    parts = [flat, spl]
    w = sum(s.BoundBox.XLength for s in parts) + BED_GAP
    h = max(s.BoundBox.YLength for s in parts)
    assert w <= BED - 2 * BED_MARGIN and h <= BED - 2 * BED_MARGIN
    x, placed = (BED - w) / 2, []
    for s in parts:
        c = s.copy()
        c.translate(V(x, (BED - s.BoundBox.YLength) / 2, 0))
        placed.append(c)
        x += s.BoundBox.XLength + BED_GAP
    _write(flat, os.path.join(out_root, "3d_print_files/io_block"))
    _write(flat, os.path.join(out_root, "print_beds/bed5_io_block_splice/originals/io_block"))
    _write(Part.makeCompound(placed),
           os.path.join(out_root, "print_beds/bed5_io_block_splice/bed5_io_block_splice"))
    return flat, (w, h)


def apply(doc_name="monitor_case_v2", export_files=False, save=False):
    doc = App.getDocument(doc_name)
    blk, brd = io_block(), board_ref()
    assert blk.isValid() and len(blk.Solids) == 1
    for other in ("rear_panel", "front_frame", "spine"):
        v = blk.common(doc.getObject(other).Shape).Volume
        assert v < 1e-3, f"io_block hits {other} by {v:.3f} mm3"
    v = blk.common(brd).Volume
    assert v < 1e-3, f"io_block hits the board by {v:.3f} mm3"
    doc.io_block.Shape = blk
    doc.board_ref.Shape = brd
    doc.recompute()
    if export_files:
        export(blk)
    if save:
        doc.save()
    return blk, brd
