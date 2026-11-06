"""
Portable tripod stand for display case v2: puts the display above a Legion Slim 7 16" lid.

  * printed rounded-square telescoping mast (30 x 30), constant-force spring counterbalance:
    push the screen up/down and it stays; side thumb-knob = friction + transport lock
  * three folding legs on M4 pivots; the two front legs end in thin toes that slide under the
    laptop's rear corners
  * tilt by a knob-driven printed lead screw (no push on the screen = no tipping force)
  * display rides on a dovetail: the VESA plate stays on the case and slides off the head

Run inside FreeCAD:
    import sys; sys.path.insert(0, "/home/rohith/project_docker/workspace/display_case/stand_portable")
    import stand_portable as s
    s.build()        # assembly (stacked over the laptop) + folded copy
    s.checks()       # clearance sweep, stops, stability, bed fit, overhangs -> checks.txt
    s.export()       # 3d_print_files/*.stl|step in print orientation

Frames: stand X right, Y toward the user / laptop, Z up, desk Z = 0, mast axis X = Y = 0.
        case  x, y up, z from the bezel face (0) rearward; rear panel face z = 11.3
"""
import math
import os

import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
CASE_FCSTD = os.path.normpath(os.path.join(HERE, "..", "v2", "monitor_case_v2.FCStd"))
GRAV = 9.81

# ------------------------------------------------------------------ case v2 --
VESA = [(-50.0, -10.0), (50.0, -10.0), (-50.0, 90.0), (50.0, 90.0)]
REAR_FACE_Z = 11.30
IO_TOP_Y, IO_BOT_Y, IO_ROOF_Z = -26.9, -95.0, 30.8
MON_MASS, MON_CG = 0.922, V(0.18, 0.94, 7.55)
CABLE_DROP = 45.0
BEZEL_BOT_Y, BEZEL_TOP_Y = -117.76, 117.76
MON_PARTS = ("front_frame", "rear_panel", "io_block", "spine", "panel_ref", "board_ref")

# ------------------------------------------- laptop (Legion Slim 7 16IRH8) --
LAP_W, LAP_D, LAP_H = 357.7, 259.3, 19.9            # PSREF
LID_LEN, LAP_HINGE_Z, LID_T, LAP_FOOT = 250.0, 12.0, 6.0, 3.5   # ESTIMATES
LAP_REAR_Y = 112.0          # laptop rear edge, in front of the mast axis

# ---------------------------------------------------------------- printing --
BED, ABS = 256.0, 1.04
WALL, INFILL = 1.6, 0.25

# -------------------------------------------------------------------- mast --
OUT_W, OUT_R, OUT_WALL = 30.0, 8.0, 2.6         # outer tube: 30 x 30 rounded square
BORE_W = OUT_W - 2 * OUT_WALL                    # 24.8
BORE_R = OUT_R - OUT_WALL
GUIDE_W, GUIDE_L = 24.0, 65.0                    # top 65 mm of the bore narrowed in X = guide + stop
IN_W, IN_D, IN_R, IN_WALL = 23.6, 24.0, 5.0, 3.0  # inner tube
REC_W, REC_D = 14.4, 1.3                         # strip recess down the inner tube's rear face
OT_Z0, OT_Z1 = 30.0, 280.0
IT_L = 240.0
PLUG_H, PLUG_SPIGOT, PLUG_W = 6.0, 14.0, 24.5    # inner-tube foot: ears 0.45 wider than the guide zone

# --------------------------------------------------------- top collar --
COL_Z0, COL_H = OT_Z1 - 12.0, 44.0
COL_Z1 = COL_Z0 + COL_H
COL_W, COL_R = 36.0, 10.0
COIL_Y, COIL_Z = -25.0, OT_Z1 + 17.0
COIL_OD, COIL_W = 22.0, 12.7                     # chamber 24.5 x 14.2
HOUSE_W, HOUSE_Y0 = 22.0, -40.0
BRAKE_Y, BRAKE_Z = 2.0, OT_Z1 + 16.0

# ---------------------------------------------------------- spring ---------
SPRING_N = 10.5             # nominal; anything 9.5 .. 12 N works (brake covers the rest)

# -------------------------------------------------------------- legs --
HINGE_R, HINGE_Z = 26.0, 58.0
LEG_T, LEG_DEPTH0, LEG_DEPTH1 = 8.0, 13.0, 9.0
LEGS = {   # name: (plan angle from +Y, deg; foot centre radius; toe tip radius or None)
    "leg_front_L": (-45.0, 128.0, None),
    "leg_front_R": (45.0, 128.0, None),
    "leg_rear": (180.0, 160.0, None),
}
TOE_T = 3.5
SNAP_Z, RAIL_H, RAIL_T = 4.0, 8.0, 2.2
LP_W, LP_Y0, LP_Y1, LP_T = 224.0, 76.0, 190.0, 3.5      # laptop plate (front feet peg into it)

# ------------------------------------------------------ head (local) --
# local: inner tube top at z = 0, mast axis x = y = 0
HEAD_W, HEAD_Y0, HEAD_Y1, HEAD_Z0, HEAD_Z1, HEAD_R = 30.0, -15.0, 25.0, -18.0, 50.0, 6.0
SOCKET_D = 18.0
PIV_Y, PIV_DZ = 43.0, 8.0
NOSE_HW, KNUCKLE_R = 9.0, 9.0
L_TILT = 30.0
T_TILT = (14.0, 3.0, 0.4)
C_SMALL = 0.15
NUT_AF, NUT_T = 20.0, 10.0
PIVOT_HOLE = 5.4            # M5 shoulder / SHCS

# ------------------------------------------------ bracket + VESA (case) --
HY = 0.0                    # tilt axis at case y = 0 (CG at 0.94)
AXIS_N = 22.0
PT = 7.0
AXIS_Z_CASE = REAR_FACE_Z + AXIS_N
BR_T, BR_HX, BR_Y0, BR_Y1 = 5.0, 20.0, -18.0, 48.0
CHEEK_IN, CHEEK_T, CHEEK_R, CHEEK_ROOT = NOSE_HW + 0.3, 6.0, 11.0, 13.0
DT_W0, DT_W1, DT_H, DT_Y1 = 26.0, 32.0, 3.0, 48.0      # dovetail: root, outer width, height, top
DT_CLR = 0.25
RIB_HX, RIB_S0, RIB_S1 = 9.0, 18.0, 44.0
BALL_D, NECK_D, NECK_L = 10.0, 6.5, 12.0
CH_D, CH_WALL = BALL_D + 0.7, 2.5
CH_SLOT = 7.6
PLATE_HX, PLATE_Y0, PLATE_Y1, PLATE_R = 56.0, -19.0, 101.0, 8.0
VESA_HOLE_D, CBORE_D, UNDER_HEAD = 4.6, 8.2, 3.6
KNOB_D, KNOB_H = 26.0, 11.0
TILT_RANGE, TILT_NOM = (-15.0, 15.0), -8.0

# --------------------------------------------------------- derived --
BR_Z_REAR = REAR_FACE_Z + PT + BR_T                     # bracket rear face (case z)
CH_ZC = BR_Z_REAR + CH_WALL + CH_D / 2                  # channel centre (case z)
E_CH = AXIS_Z_CASE - CH_ZC                              # channel line in front of the tilt axis
RIB_Z1 = CH_ZC + CH_D / 2 + 1.0
Z_IT_MIN = COL_Z1 - HEAD_Z0 + 2.0                       # head sleeve 2 mm above the collar
Z_IT_MAX = (OT_Z1 - GUIDE_L) + IT_L                     # foot ears reach the guide zone
TRAVEL = Z_IT_MAX - Z_IT_MIN


def ball_y(theta):
    t = math.radians(theta)
    return E_CH / math.cos(t) - L_TILT * math.tan(t)


def ball_s(theta):
    t = math.radians(theta)
    return (L_TILT - E_CH * math.sin(t)) / math.cos(t)


SCREW_BALL_Z = KNOB_H + (PIV_Y + ball_y(TILT_RANGE[0])) - (HEAD_Y0 - 1.0)


# ------------------------------------------------------------------ helpers --
def _box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def _cyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def _cone(r0, r1, z0, z1, x=0.0, y=0.0):
    return Part.makeCone(r0, r1, z1 - z0, V(x, y, z0))


def rrect(w, d, r, z0, z1, cx=0.0, cy=0.0):
    b = _box(cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z0, z1)
    if r > 0:
        b = b.makeFillet(r, [e for e in b.Edges if e.BoundBox.ZLength > (z1 - z0) - 1e-6])
    return b


def _fuse(a, bs):
    bs = bs if isinstance(bs, (list, tuple)) else [bs]
    r = a.fuse(bs)
    if len(r.Solids) != 1:
        r = a.fuse(bs, 0.01)
    return r


def _solid(s):
    try:
        r = s.removeSplitter()
        if r.isValid() and len(r.Solids) == 1:
            s = r
    except Exception:
        pass
    assert s.isValid(), "invalid shape"
    assert len(s.Solids) == 1, f"{len(s.Solids)} solids"
    return Part.Solid(s.Solids[0])


def _revolve(rz):
    pts = [V(r, 0, z) for r, z in rz]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).revolve(V(0, 0, 0), V(0, 0, 1), 360)


def _prism_yz(pts, x0, x1):
    """Extrude a (y, z) polygon along X."""
    p = [V(x0, y, z) for y, z in pts]
    return Part.Face(Part.makePolygon(p + [p[0]])).extrude(V(x1 - x0, 0, 0))


def _place(shape, pl):
    c = shape.copy()
    c.Placement = pl.multiply(c.Placement)
    return c


def teardrop(p, axis, L, d, up=V(0, 0, 1)):
    axis, up = V(axis).normalize(), V(up).normalize()
    side = axis.cross(up).normalize()
    r = d / 2
    k = r / math.sqrt(2) * 0.99
    cyl = Part.makeCylinder(r, L, p, axis)
    pts = [p + side * k + up * k, p + up * (r * math.sqrt(2)), p - side * k + up * k, p]
    return cyl.fuse(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(axis * L))


def scallops(shape, R, n, d, z0, z1):
    cuts = [_cyl(d / 2, z0 - 1, z1 + 1, R * math.cos(2 * math.pi * i / n), R * math.sin(2 * math.pi * i / n))
            for i in range(n)]
    return shape.cut(Part.makeCompound(cuts))


def hexagon(af, z0, z1, rot=0.0):
    rh = af / math.sqrt(3)
    pts = [V(rh * math.cos(math.radians(60 * i + rot)), rh * math.sin(math.radians(60 * i + rot)), z0)
           for i in range(6)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, z1 - z0))


def _thread_rod(D, P, flat, z0, z1):
    ax = P / 2 - flat
    R, r = D / 2, D / 2 - ax
    e = 0.05
    pts = [V(r - e, 0, -(flat / 2 + ax) - e), V(R, 0, -flat / 2), V(R, 0, flat / 2), V(r - e, 0, flat / 2 + ax + e)]
    prof = Part.makePolygon(pts + [pts[0]])
    n = (z1 - z0) / P + 4
    hx = Part.makeHelix(P, n * P, r - e)
    hx.translate(V(0, 0, -2 * P))
    sw = Part.Wire(hx).makePipeShell([prof], True, True)
    rod = _cyl(r, -2.5 * P, n * P - 1.5 * P).fuse(sw)
    rod.translate(V(0, 0, z0))
    return rod, R, r


def ext_thread(spec, z0, z1, c, ch0=True, ch1=True):
    D, P, flat = spec
    rod, R, r = _thread_rod(D - 2 * c, P, flat, z0, z1)
    h = R - r
    rz = [(0, z0)] + ([(r - 0.3, z0), (R + 1, z0 + h + 1.3)] if ch0 else [(R + 1, z0)]) \
        + ([(R + 1, z1 - h - 1.3), (r - 0.3, z1)] if ch1 else [(R + 1, z1)]) + [(0, z1)]
    return rod.common(_revolve(rz))


def tap(spec, z0, z1, c):
    D, P, flat = spec
    rod, R, r = _thread_rod(D + 2 * c, P, flat, z0 - P, z1 + P)
    rod = rod.common(_cyl(R + 1, z0 - 0.5, z1 + 0.5))
    k = R - r + 0.8
    return rod.fuse([_cone(R + 0.8, r - 0.2, z0 - 0.01, z0 + k), _cone(r - 0.2, R + 0.8, z1 - k, z1 + 0.01)])


def thread_depth(spec):
    return spec[1] / 2 - spec[2]


# ===================================================================== parts ==
def inner_profile(z0, z1, grow=0.0, recess=True):
    s = rrect(IN_W + 2 * grow, IN_D + 2 * grow, IN_R + grow, z0, z1)
    if recess:
        s = s.cut(_box(-REC_W / 2 + grow, REC_W / 2 - grow, -IN_D / 2 - grow - 1, -IN_D / 2 + REC_D, z0 - 1, z1 + 1))
    return s


def outer_tube():
    """Stand frame.  Prints upright.  Leg clevises are part of it."""
    s = rrect(OUT_W, OUT_W, OUT_R, OT_Z0, OT_Z1)
    lugs = []
    for name, (ang, _, _) in LEGS.items():
        for side in (-1, 1):
            w0 = side * (LEG_T / 2 + 0.2)
            w1 = side * (LEG_T / 2 + 0.2 + 3.5)
            prof = [(10.0, OT_Z0 + 2), (HINGE_R + 7.5, OT_Z0 + 2 + HINGE_R + 7.5 - 10.0),
                    (HINGE_R + 7.5, HINGE_Z), (HINGE_R + 5.3, HINGE_Z + 5.3), (HINGE_R, HINGE_Z + 7.5),
                    (10.0, HINGE_Z + 7.5)]
            lug = _prism_yz(prof, min(w0, w1), max(w0, w1))       # x = hinge-axis offset, y = radius
            lug = lug.cut(teardrop(V(min(w0, w1) - 1, HINGE_R, HINGE_Z), V(1, 0, 0), 6, 4.3))
            # local (x = along hinge axis, y = radial) -> plan angle
            lug.rotate(V(0, 0, 0), V(0, 0, 1), -ang)
            lugs.append(lug)
    s = s.fuse(lugs)
    s = s.cut(rrect(BORE_W, BORE_W, BORE_R, OT_Z0 - 1, OT_Z1 + 1))
    # guide zone: narrow the bore in X at the top
    for sg in (-1, 1):
        x0, x1 = sorted((sg * GUIDE_W / 2, sg * BORE_W / 2))
        rib = _box(x0, x1, -BORE_W / 2 + BORE_R, BORE_W / 2 - BORE_R, OT_Z1 - GUIDE_L, OT_Z1)
        cham = _prism_yz([(-BORE_W / 2 + BORE_R, OT_Z1 - GUIDE_L), (BORE_W / 2 - BORE_R, OT_Z1 - GUIDE_L),
                          (BORE_W / 2 - BORE_R, OT_Z1 - GUIDE_L - 0.01)], x0, x1)
        s = s.fuse(rib)
    # M3 pilot holes for the collar and the bottom cap
    for z in (OT_Z1 - 6.0, OT_Z0 + 5.0):
        s = s.cut(teardrop(V(-OUT_W / 2 - 1, 0, z), V(1, 0, 0), OUT_WALL + 2, 2.5))
    return _solid(s)


def bottom_cap():
    s = rrect(BORE_W - 0.2, BORE_W - 0.2, BORE_R - 0.1, OT_Z0, OT_Z0 + 10).fuse(
        rrect(OUT_W, OUT_W, OUT_R, OT_Z0 - 2.0, OT_Z0 + 0.01))
    s = s.cut(rrect(BORE_W - 5, BORE_W - 5, 2, OT_Z0 + 1.5, OT_Z0 + 11))
    s = s.cut(teardrop(V(-OUT_W / 2 - 1, 0, OT_Z0 + 5.0), V(1, 0, 0), 6, 2.5))
    return _solid(s)


def top_collar():
    """Guide bushing + spring housing + brake.  Stand frame.  Prints upright."""
    z0, z1 = COL_Z0, COL_Z1
    s = rrect(COL_W, COL_W, COL_R, z0, z1)
    house = rrect(HOUSE_W, -HOUSE_Y0 - 4, 6.0, z0 + 6, z1, 0, (HOUSE_Y0 - 4) / 2)
    # 45 deg underside on the housing so it prints without support
    house = house.cut(_prism_yz([(HOUSE_Y0 - 1, z0 + 5), (-COL_W / 2 + 0.5, z0 + 5),
                                 (HOUSE_Y0 - 1, z0 + 5 + (-COL_W / 2 + 0.5 - HOUSE_Y0 + 1))], -20, 20))
    # brake boss on +X, 45 deg underside
    bz = BRAKE_Z
    boss = Part.Face(Part.makePolygon([V(COL_W / 2 - 2, BRAKE_Y - 7, bz - 17), V(COL_W / 2 + 5, BRAKE_Y - 7, bz - 10),
                                       V(COL_W / 2 + 5, BRAKE_Y - 7, bz + 9), V(COL_W / 2 - 2, BRAKE_Y - 7, bz + 9),
                                       V(COL_W / 2 - 2, BRAKE_Y - 7, bz - 17)])).extrude(V(0, 14, 0))
    s = s.fuse([house, boss])
    s = s.cut(rrect(OUT_W + 0.3, OUT_W + 0.3, OUT_R + 0.15, z0 - 1, OT_Z1))          # socket
    w_lo = rrect(OUT_W + 0.3, OUT_W + 0.3, OUT_R + 0.15, OT_Z1 - 0.01, OT_Z1).Faces
    lo = Part.Wire(Part.__sortEdges__([e for e in rrect(OUT_W + 0.3, OUT_W + 0.3, OUT_R + 0.15, 0, 1).Edges
                                       if e.BoundBox.ZMax < 1e-6]))
    hi = Part.Wire(Part.__sortEdges__([e for e in rrect(IN_W + 0.4, IN_D + 0.4, IN_R + 0.2, 0, 1).Edges
                                       if e.BoundBox.ZMax < 1e-6]))
    lo.translate(V(0, 0, OT_Z1 - 0.01))
    hi.translate(V(0, 0, OT_Z1 + 3.4))
    s = s.cut(Part.makeLoft([lo, hi], True))                                         # 45 deg roof
    s = s.cut(inner_profile(OT_Z1 - 0.5, z1 + 1, grow=0.2, recess=False))           # guide passage
    # coil chamber (axis X), open to the top for assembly, + M3 drum axle
    ch = Part.makeCylinder((COIL_OD + 2.5) / 2, COIL_W + 1.5, V(-(COIL_W + 1.5) / 2, COIL_Y, COIL_Z), V(1, 0, 0))
    ch = ch.fuse(_box(-(COIL_W + 1.5) / 2, (COIL_W + 1.5) / 2, COIL_Y - (COIL_OD + 2.5) / 2,
                      COIL_Y + (COIL_OD + 2.5) / 2, COIL_Z, z1 + 1))
    s = s.cut(ch)
    s = s.cut(teardrop(V(-HOUSE_W / 2 - 1, COIL_Y, COIL_Z), V(1, 0, 0), HOUSE_W + 2, 3.2))
    # strip window from the chamber into the guide passage
    s = s.cut(_box(-REC_W / 2 + 0.2, REC_W / 2 - 0.2, COIL_Y, -IN_D / 2 + 1, OT_Z1 + 1, COIL_Z + 2))
    # brake: pad window in the +X wall, M5 nut slot (drop-in from the top), screw hole
    xin = IN_W / 2 + 0.2
    s = s.cut(_box(xin - 0.5, xin + 3.0, BRAKE_Y - 8, BRAKE_Y + 8, BRAKE_Z - 9, BRAKE_Z + 9))
    s = s.cut(teardrop(V(xin, BRAKE_Y, BRAKE_Z), V(1, 0, 0), COL_W, 5.4))
    nx = COL_W / 2 - 0.5
    nut = hexagon(8.4, 0, 4.4, rot=0.0)                   # flats top/bottom after the turn
    nut.rotate(V(0, 0, 0), V(0, 1, 0), 90)
    nut.translate(V(nx, BRAKE_Y, BRAKE_Z))
    s = s.cut(nut.fuse(_box(nx, nx + 4.4, BRAKE_Y - 4.2, BRAKE_Y + 4.2, BRAKE_Z, BRAKE_Z + 12)))
    s = s.cut(teardrop(V(-COL_W / 2 - 1, 0, OT_Z1 - 6.0), V(1, 0, 0), 8, 3.4))   # M3 to the tube
    return _solid(s)


def brake_pad():
    """Print frame: flat."""
    return _solid(rrect(15.4, 17.4, 2.0, 0, 2.8))


def spring_drum():
    s = _cyl(13.8 / 2, 0, COIL_W + 1.0).cut(_cyl(1.7, -1, COIL_W + 2))
    return _solid(s)


def inner_tube():
    """Local: bottom at z = 0.  Prints upright."""
    s = inner_profile(0, IT_L)
    s = s.cut(rrect(IN_W - 2 * IN_WALL, IN_D - 2 * IN_WALL, max(IN_R - IN_WALL, 0.5), -1, IT_L + 1))
    s = s.cut(teardrop(V(-IN_W / 2 - 1, 6.0, IT_L - SOCKET_D / 2), V(1, 0, 0), IN_WALL + 2, 2.5))
    return _solid(s)


def inner_foot():
    """Local: inner tube bottom at z = 0 (foot below it, spigot inside)."""
    s = rrect(PLUG_W, IN_D, IN_R, -PLUG_H, 0.01)
    s = s.cut(_box(-REC_W / 2, REC_W / 2, -IN_D / 2 - 1, -IN_D / 2 + REC_D, -PLUG_H - 1, 1))
    sp = rrect(IN_W - 2 * IN_WALL - 0.2, IN_D - 2 * IN_WALL - 0.2, 0.6, -0.5, PLUG_SPIGOT)
    s = s.fuse(sp)
    s = s.cut(_box(-4, 4, -4, 4, 2, PLUG_SPIGOT + 1))                            # lightening
    # M3 strip hook: screw from the front, tip sticks 1 mm through the recess face
    s = s.cut(Part.makeCylinder(1.25, IN_D, V(0, -IN_D / 2 - 1, -PLUG_H / 2), V(0, 1, 0)))
    s = s.cut(Part.makeCylinder(2.8, 4, V(0, IN_D / 2 - 3.0, -PLUG_H / 2), V(0, 1, 0)))   # M3 head
    return _solid(s)


def head():
    """Local: inner tube top at z = 0.  Prints upright."""
    s = rrect(HEAD_W, HEAD_Y1 - HEAD_Y0, HEAD_R, HEAD_Z0, HEAD_Z1, 0, (HEAD_Y0 + HEAD_Y1) / 2)
    t = math.sqrt(0.5) * KNUCKLE_R
    pz = PIV_DZ
    nose = _prism_yz([(0, HEAD_Z0), (PIV_Y - t - (pz - t - HEAD_Z0), HEAD_Z0), (PIV_Y - t, pz - t),
                      (PIV_Y, pz + KNUCKLE_R), (0, pz + KNUCKLE_R)], -NOSE_HW, NOSE_HW)
    nose = nose.fuse([Part.makeCylinder(KNUCKLE_R, 2 * NOSE_HW, V(-NOSE_HW, PIV_Y, pz), V(1, 0, 0)),
                      _prism_yz([(PIV_Y - t, pz - t), (PIV_Y, pz - KNUCKLE_R * math.sqrt(2)), (PIV_Y + t, pz - t)],
                                -NOSE_HW, NOSE_HW)])
    s = s.fuse(nose)
    s = s.cut(inner_profile(HEAD_Z0 - 1, 0, grow=0.15, recess=False))
    lo = Part.Wire(Part.__sortEdges__([e for e in rrect(IN_W + 0.3, IN_D + 0.3, IN_R + 0.15, 0, 1).Edges
                                       if e.BoundBox.ZMax < 1e-6]))
    hi = Part.Wire(Part.__sortEdges__([e for e in rrect(4.0, 4.4, 1.0, 0, 1).Edges if e.BoundBox.ZMax < 1e-6]))
    lo.translate(V(0, 0, -0.01))
    hi.translate(V(0, 0, 12.5))
    s = s.cut(Part.makeLoft([lo, hi], True))                                       # 45 deg socket roof
    s = s.cut(teardrop(V(-NOSE_HW - 1, PIV_Y, pz), V(1, 0, 0), 2 * NOSE_HW + 2, PIVOT_HOLE))
    zs = PIV_DZ + L_TILT
    s = s.cut(teardrop(V(0, HEAD_Y0 - 1, zs), V(0, 1, 0), HEAD_Y1 - HEAD_Y0 + 2, T_TILT[0] + 0.8))
    af = NUT_AF + 0.4
    rh = af / math.sqrt(3)
    hexf = Part.Face(Part.makePolygon([V(rh * math.cos(math.radians(60 * i + 90)), 0,
                                         rh * math.sin(math.radians(60 * i + 90))) for i in range(6)]
                                      + [V(rh * math.cos(math.radians(90)), 0, rh * math.sin(math.radians(90)))]))
    slot = hexf.extrude(V(0, NUT_T + 0.5, 0)).fuse(_box(-af / 2, af / 2, 0, NUT_T + 0.5, 0, 40))
    slot.translate(V(0, -(NUT_T + 0.5) / 2, zs))
    s = s.cut(slot)
    s = s.cut(teardrop(V(-HEAD_W / 2 - 1, 6.0, -SOCKET_D / 2), V(1, 0, 0), 8, 3.4))   # M3 to the tube
    return _solid(s)


def tilt_nut():
    s = hexagon(NUT_AF, 0, NUT_T, rot=30.0)
    s = s.makeChamfer(0.6, [e for e in s.Edges if e.BoundBox.ZLength < 1e-6])
    return _solid(s.cut(tap(T_TILT, 0, NUT_T, C_SMALL)))


def tilt_screw():
    zb = SCREW_BALL_Z
    k = _cyl(KNOB_D / 2, 0, KNOB_H)
    k = k.makeChamfer(0.8, [e for e in k.Edges if e.BoundBox.ZMax < 1e-6 or e.BoundBox.ZMin > KNOB_H - 1e-6])
    k = scallops(k, KNOB_D / 2 + 1.3, 10, 5.0, 0, KNOB_H)
    zt = zb - NECK_L
    th = ext_thread(T_TILT, KNOB_H - 0.3, zt, C_SMALL, ch0=False)
    rb = BALL_D / 2
    rt = rb / math.sqrt(2)
    neck = _cyl(NECK_D / 2, zt - 0.5, zb - rt)
    cone = _cone(NECK_D / 2, rt, zb - rt - (rt - NECK_D / 2), zb - rt + 0.01)
    return _solid(_fuse(k, [th, neck, cone, Part.makeSphere(rb, V(0, 0, zb))]))


def brake_knob():
    """M5 x 20 hex bolt pressed into it from the bottom."""
    s = _cyl(9.0, 0, 9.0)
    s = scallops(s, 9.0 + 1.0, 8, 4.0, 0, 9)
    s = s.cut(hexagon(8.15, -1, 3.6, rot=30.0)).cut(_cyl(2.75, -1, 10))
    return _solid(s)


def bracket():
    """Tilting bracket, case frame (moves with the display).  Prints dovetail-face down."""
    zf, zr = REAR_FACE_Z + PT, BR_Z_REAR
    hw = DT_W0 / 2
    s = Part.Face(Part.makePolygon([V(-hw, BR_Y0, zf), V(hw, BR_Y0, zf), V(hw + BR_T, BR_Y0, zr),
                                    V(-hw - BR_T, BR_Y0, zr), V(-hw, BR_Y0, zf)])).extrude(V(0, BR_Y1 - BR_Y0, 0))
    s = s.makeFillet(4.0, [e for e in s.Edges if e.BoundBox.YLength < 1e-6 and e.BoundBox.ZLength > 1])
    # dovetail tongue on the front face (wider at its tip = into the VESA plate)
    hw0, hw1 = DT_W0 / 2, DT_W1 / 2
    tongue = Part.Face(Part.makePolygon([V(-hw0, BR_Y0, zf + 0.01), V(hw0, BR_Y0, zf + 0.01),
                                         V(hw1, BR_Y0, zf - DT_H), V(-hw1, BR_Y0, zf - DT_H),
                                         V(-hw0, BR_Y0, zf + 0.01)])).extrude(V(0, DT_Y1 - BR_Y0, 0))
    add = [tongue]
    for sg in (-1, 1):
        x0 = CHEEK_IN if sg > 0 else -CHEEK_IN - CHEEK_T
        add.append(_prism_yz([(HY - CHEEK_ROOT, zr - 0.5), (HY + CHEEK_ROOT, zr - 0.5),
                              (HY + CHEEK_R, AXIS_Z_CASE), (HY - CHEEK_R, AXIS_Z_CASE)], x0, x0 + CHEEK_T))
        add.append(Part.makeCylinder(CHEEK_R, CHEEK_T, V(x0, HY, AXIS_Z_CASE), V(1, 0, 0)))
    add.append(_box(-RIB_HX, RIB_HX, HY + RIB_S0, HY + RIB_S1, zr - 0.5, RIB_Z1))
    s = s.fuse(add)
    ch = Part.makeCylinder(CH_D / 2, RIB_S1 - RIB_S0 - 3, V(0, HY + RIB_S0 - 1, CH_ZC), V(0, 1, 0))
    sl = _box(-CH_SLOT / 2, CH_SLOT / 2, HY + RIB_S0 - 1, HY + RIB_S1 - 4, CH_ZC, RIB_Z1 + 1)
    s = s.cut([ch, sl])
    s = s.cut(teardrop(V(-CHEEK_IN - CHEEK_T - 1, HY, AXIS_Z_CASE), V(1, 0, 0), 2 * (CHEEK_IN + CHEEK_T) + 2,
                       PIVOT_HOLE, up=V(0, 0, 1)))
    return _solid(s)


def vesa_plate():
    """Stays on the case.  Case frame, prints face down."""
    z0, z1 = REAR_FACE_Z, REAR_FACE_Z + PT
    s = rrect(2 * PLATE_HX, PLATE_Y1 - PLATE_Y0, PLATE_R, z0, z1, 0, (PLATE_Y0 + PLATE_Y1) / 2)
    hw0, hw1 = DT_W0 / 2 + DT_CLR, DT_W1 / 2 + DT_CLR
    sock = Part.Face(Part.makePolygon([V(-hw0, PLATE_Y0 - 1, z1 + 0.01), V(hw0, PLATE_Y0 - 1, z1 + 0.01),
                                       V(hw1, PLATE_Y0 - 1, z1 - DT_H - DT_CLR), V(-hw1, PLATE_Y0 - 1, z1 - DT_H - DT_CLR),
                                       V(-hw0, PLATE_Y0 - 1, z1 + 0.01)])).extrude(V(0, DT_Y1 - PLATE_Y0 + 1, 0))
    s = s.cut(sock)
    for x, y in VESA:
        s = s.cut(_cyl(VESA_HOLE_D / 2, z0 - 1, z1 + 1, x, y))
        s = s.cut(_cyl(CBORE_D / 2, z1 - (PT - UNDER_HEAD), z1 + 1, x, y))
    s = s.cut(_box(-8, 8, PLATE_Y0 - 1, PLATE_Y1 + 1, z0 - 1, z0 + 0.5))
    arrow = Part.Face(Part.makePolygon([V(-7, 76, z1 - 0.6), V(7, 76, z1 - 0.6), V(0, 90, z1 - 0.6), V(-7, 76, z1 - 0.6)]))
    return _solid(s.cut(arrow.extrude(V(0, 0, 2))))


def leg(name, rotated=True):
    """Deployed, in its swing plane: local x = along the hinge axis, y = radial out, z = up.
    Returns the leg in the stand frame (rotated=False: swing-plane frame)."""
    ang, rf, rtoe = LEGS[name]
    hz = HINGE_Z
    zf = 7.0 + LEG_DEPTH1 / 2                             # foot centre height
    # bar as a 2-D (y, z) polygon around the centreline hinge -> foot
    dy, dz = rf - HINGE_R, zf - hz
    L = math.hypot(dy, dz)
    nY, nZ = -dz / L, dy / L                              # unit normal (up-out side)
    h0, h1 = LEG_DEPTH0 / 2, LEG_DEPTH1 / 2
    bar = [(HINGE_R - 12 * dy / L + nY * h0, hz - 12 * dz / L + nZ * h0),
           (rf + nY * h1, zf + nZ * h1), (rf - nY * h1, zf - nZ * h1),
           (HINGE_R - 12 * dy / L - nY * h0, hz - 12 * dz / L - nZ * h0)]
    x0, x1 = -LEG_T / 2, LEG_T / 2
    s = _prism_yz(bar, x0, x1)
    s = s.fuse(Part.makeCylinder(7.5, LEG_T, V(x0, HINGE_R, hz), V(1, 0, 0)))
    foot = rrect(LEG_T, 26.0, 3.0, 0, 7.0 + LEG_DEPTH1, 0, rf)
    s = s.fuse(foot.common(_box(-50, 50, rf - 13, rf + 13, 0, zf + h1 + 3)))
    ft = 7.0 + LEG_DEPTH1                                              # chamfer: clears the mast when folded
    s = s.cut(_prism_yz([(rf + 13.5, ft - 8.5), (rf + 13.5, ft + 5), (rf + 13.5 - 13.5, ft + 5)], x0 - 1, x1 + 1))
    if rtoe:
        toe = _box(x0, x1, rf, rtoe, 0, TOE_T)
        toe = toe.makeFillet(3.5, [e for e in toe.Edges if e.BoundBox.ZLength > TOE_T - 1e-6 and e.BoundBox.YMin > rtoe - 1e-6])
        s = s.fuse(toe)
    # heel stop: flat face exactly on the tube surface along this direction
    rs = _tube_surface_r(ang)
    s = s.cut(_box(-50, 50, -50, rs, -10, 200))
    s = s.cut(Part.makeCylinder(2.15, LEG_T + 2, V(x0 - 1, HINGE_R, hz), V(1, 0, 0)))
    if name == "leg_rear":                                              # stands on the table; fronts on the plate
        s = s.fuse(rrect(LEG_T, 26.0, 3.0, -LP_T, 0.5, 0, rf))
    else:                                                               # snap dimples for the plate's rails
        for dy in (-7.0, 7.0):
            s = s.cut(Part.makeCylinder(1.6, LEG_T + 2, V(x0 - 1, rf + dy, SNAP_Z), V(1, 0, 0)).cut(
                _box(x0 + 0.6, x1 - 0.6, rf + dy - 3, rf + dy + 3, SNAP_Z - 3, SNAP_Z + 3)))
    s = _solid(s)
    if rotated:
        s.rotate(V(0, 0, 0), V(0, 0, 1), -ang)
    return s


def _tube_surface_r(ang):
    a = math.radians(ang)
    ux, uy = abs(math.sin(a)), abs(math.cos(a))
    h, r = OUT_W / 2, OUT_R
    # ray from the centre to a rounded square
    for t in [x * 0.01 for x in range(1000, 3000)]:
        px, py = ux * t, uy * t
        qx, qy = max(px - (h - r), 0), max(py - (h - r), 0)
        if (px > h or py > h) or (qx > 0 and qy > 0 and math.hypot(qx, qy) > r):
            return t
    return h


def foot_xy(name):
    ang, rf, _ = LEGS[name]
    a = math.radians(ang)
    return V(rf * math.sin(a), rf * math.cos(a), 0)


def laptop_plate():
    """Thin plate that slides under the Legion's rear edge.  The two front feet snap between its
    rails, so when the laptop sits on it the laptop's weight anchors the stand.  Prints flat."""
    s = rrect(LP_W, LP_Y1 - LP_Y0, 10.0, 0, LP_T, 0, (LP_Y0 + LP_Y1) / 2)
    s = s.makeChamfer(1.0, [e for e in s.Edges if e.BoundBox.ZMin > LP_T - 1e-6 and e.BoundBox.YMin > LP_Y1 - 12])
    for sg in (-1, 1):                                                 # lightening windows
        s = s.cut(rrect(52, 30, 8, -1, LP_T + 1, sg * 50, (LP_Y0 + LP_Y1) / 2 + 6))
    rails = []
    for n in ("leg_front_L", "leg_front_R"):
        ang, rf, _ = LEGS[n]
        r = []
        for sg in (-1, 1):
            x0 = sg * (LEG_T / 2 + 0.2) if sg > 0 else -(LEG_T / 2 + 0.2) - RAIL_T
            rail = _box(x0, x0 + RAIL_T, rf - 12, rf + 12, LP_T - 0.01, LP_T + RAIL_H)
            rail = rail.makeFillet(1.0, [e for e in rail.Edges if e.BoundBox.ZMin > LP_T + RAIL_H - 1e-6])
            for dy in (-7.0, 7.0):                                     # snap bumps, 0.6 proud
                bx = LEG_T / 2 + 0.2 if sg > 0 else -(LEG_T / 2 + 0.2)
                rail = rail.fuse(Part.makeSphere(1.5, V(bx - sg * 0.9, rf + dy, LP_T + SNAP_Z)).common(
                    _box(min(bx, bx - sg * 2), max(bx, bx - sg * 2), rf + dy - 2, rf + dy + 2, 0, 50)))
            r.append(rail)
        rr = r[0].fuse(r[1])
        rr.rotate(V(0, 0, 0), V(0, 0, 1), -ang)
        rails.append(rr)
    return _solid(_fuse(s, rails))


def leg_beta(name):
    _, rf, _ = LEGS[name]
    return math.degrees(math.atan2(HINGE_Z - (7.0 + LEG_DEPTH1 / 2), rf - HINGE_R))


def fold_placement(name, frac=1.0):
    """Rotation about the hinge axis that folds the leg up along the mast (frac 0..1)."""
    ang = LEGS[name][0]
    a = math.radians(ang)
    axis = V(math.cos(a), -math.sin(a), 0)                 # local +x after the plan rotation
    hp = V(HINGE_R * math.sin(a), HINGE_R * math.cos(a), HINGE_Z)
    return App.Placement(V(0, 0, 0), App.Rotation(axis, frac * (90.0 + leg_beta(name))), hp)


# ================================================================ assembly ==
def z_it(h):
    return Z_IT_MIN + h


def case_to_stand(theta, h):
    p = V(0, PIV_Y, z_it(h) + PIV_DZ)
    return (App.Placement(p, App.Rotation(V(1, 0, 0), 90.0 + theta))
            .multiply(App.Placement(V(0, -HY, -AXIS_Z_CASE), App.Rotation())))


def poses(h, theta):
    zt = z_it(h)
    I = App.Placement()
    pl = {n: I for n in ("outer_tube", "bottom_cap", "top_collar")}
    pl.update({n: App.Placement(V(0, 0, LP_T), App.Rotation()) for n in LEGS})
    pl["laptop_plate"] = I
    pl["outer_tube"] = pl["bottom_cap"] = pl["top_collar"] = App.Placement(V(0, 0, LP_T), App.Rotation())
    pl["inner_tube"] = App.Placement(V(0, 0, zt - IT_L), App.Rotation())
    pl["inner_foot"] = App.Placement(V(0, 0, zt - IT_L), App.Rotation())
    pl["head"] = App.Placement(V(0, 0, zt), App.Rotation())
    zs = zt + PIV_DZ + L_TILT
    pl["tilt_screw"] = App.Placement(V(0, PIV_Y + ball_y(theta) - SCREW_BALL_Z, zs), App.Rotation(V(1, 0, 0), -90))
    pl["tilt_nut"] = App.Placement(V(0, -NUT_T / 2, zs), App.Rotation(V(1, 0, 0), -90))
    pl["spring_drum"] = App.Placement(V(-(COIL_W + 1.0) / 2, COIL_Y, COIL_Z), App.Rotation(V(0, 1, 0), 90))
    pl["brake_pad"] = App.Placement(V(IN_W / 2 + 0.2 + 2.8, BRAKE_Y, BRAKE_Z), App.Rotation(V(0, 1, 0), -90))
    pl["brake_knob"] = App.Placement(V(COL_W / 2 + 5.5, BRAKE_Y, BRAKE_Z), App.Rotation(V(0, 1, 0), 90))
    c2s = case_to_stand(theta, h)
    pl["bracket"] = c2s
    pl["vesa_plate"] = c2s
    pl["monitor"] = c2s
    return pl


BUILDERS = {
    "outer_tube": outer_tube, "bottom_cap": bottom_cap, "top_collar": top_collar, "brake_pad": brake_pad,
    "brake_knob": brake_knob, "spring_drum": spring_drum, "inner_tube": inner_tube, "inner_foot": inner_foot,
    "head": head, "tilt_nut": tilt_nut, "tilt_screw": tilt_screw, "bracket": bracket, "vesa_plate": vesa_plate,
    "leg_front_L": lambda: leg("leg_front_L"), "leg_front_R": lambda: leg("leg_front_R"),
    "leg_rear": lambda: leg("leg_rear"), "laptop_plate": laptop_plate,
}
_CACHE = {}


def part(name):
    if name not in _CACHE:
        _CACHE[name] = BUILDERS[name]()
    return _CACHE[name]


def hardware(h, theta):
    """Bought parts as simple proxies, stand frame."""
    zt = z_it(h)
    out = {}
    coil = Part.makeCylinder(COIL_OD / 2, COIL_W, V(-COIL_W / 2, COIL_Y, COIL_Z), V(1, 0, 0))
    out["cf_spring_coil"] = coil
    za = zt - IT_L - PLUG_H / 2
    out["cf_spring_strip"] = _box(-COIL_W / 2, COIL_W / 2, -IN_D / 2 + REC_D - 0.25, -IN_D / 2 + REC_D - 0.05,
                                  za, COIL_Z)
    pz = zt + PIV_DZ
    out["m5_pivot"] = Part.makeCylinder(2.5, 2 * (CHEEK_IN + CHEEK_T) + 10, V(-(CHEEK_IN + CHEEK_T) - 5, PIV_Y, pz),
                                        V(1, 0, 0))
    return out


def monitor_shapes():
    doc = next((d for d in App.listDocuments().values() if os.path.normpath(d.FileName) == CASE_FCSTD), None)
    opened = doc is None
    if opened:
        doc = App.openDocument(CASE_FCSTD, True)
    out = {n: doc.getObject(n).Shape.copy() for n in MON_PARTS}
    if opened:
        App.closeDocument(doc.Name)
    return out


def laptop(lid_angle=110.0):
    y0 = LAP_REAR_Y
    deck = _box(-LAP_W / 2, LAP_W / 2, y0, y0 + LAP_D, LAP_FOOT, LAP_H)
    lid = _box(-LAP_W / 2, LAP_W / 2, -LID_T, 0, 0, LID_LEN)
    lid.rotate(V(0, 0, 0), V(1, 0, 0), lid_angle - 90.0)
    lid.translate(V(0, y0 + LID_T, LAP_HINGE_Z))
    return deck, lid


def lid_top(lid_angle):
    a = math.radians(lid_angle - 90.0)
    return LAP_REAR_Y + LID_T - LID_LEN * math.sin(a), LAP_HINGE_Z + LID_LEN * math.cos(a)


COLORS = {"outer_tube": (0.92, 0.92, 0.93), "bottom_cap": (0.2, 0.2, 0.22), "top_collar": (0.2, 0.2, 0.22),
          "brake_pad": (0.9, 0.45, 0.1), "brake_knob": (0.9, 0.45, 0.1), "spring_drum": (0.4, 0.4, 0.4),
          "inner_tube": (0.78, 0.79, 0.81), "inner_foot": (0.2, 0.2, 0.22), "head": (0.2, 0.2, 0.22),
          "tilt_nut": (0.4, 0.4, 0.4), "tilt_screw": (0.9, 0.45, 0.1), "bracket": (0.92, 0.92, 0.93),
          "vesa_plate": (0.55, 0.57, 0.6), "leg_front_L": (0.2, 0.2, 0.22), "leg_front_R": (0.2, 0.2, 0.22),
          "leg_rear": (0.2, 0.2, 0.22), "cf_spring_coil": (0.7, 0.72, 0.75), "cf_spring_strip": (0.7, 0.72, 0.75),
          "m5_pivot": (0.5, 0.5, 0.5), "front_frame": (0.12, 0.12, 0.13), "rear_panel": (0.18, 0.18, 0.19),
          "io_block": (0.18, 0.18, 0.19), "spine": (0.75, 0.76, 0.78), "panel_ref": (0.05, 0.1, 0.2),
          "board_ref": (0.1, 0.45, 0.2), "laptop_deck": (0.35, 0.36, 0.4), "laptop_lid": (0.35, 0.36, 0.4)}


def build(h=None, theta=TILT_NOM, lid_angle=110.0, name="stand_portable", with_laptop=True):
    if h is None:
        h = min(TRAVEL, max(0.0, lid_top(lid_angle)[1] + 15.0 - (Z_IT_MIN + PIV_DZ - (HY - BEZEL_BOT_Y))))
    mon = monitor_shapes()
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    pl = poses(h, theta)
    objs = {n: _place(part(n), pl[n]) for n in BUILDERS}
    objs.update(hardware(h, theta))
    for n in MON_PARTS:
        objs[n] = _place(mon[n], pl["monitor"])
    if with_laptop:
        objs["laptop_deck"], objs["laptop_lid"] = laptop(lid_angle)
    for n, s in objs.items():
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
        if App.GuiUp:
            o.ViewObject.ShapeColor = COLORS.get(n, (0.3, 0.3, 0.3))
            if n.startswith("laptop"):
                o.ViewObject.Transparency = 55
    doc.recompute()
    return doc, h


# ==================================================================== checks ==
def print_shape(name):
    if name.startswith("leg_"):
        sh = leg(name, rotated=False)
        sh.rotate(V(0, 0, 0), V(0, 1, 0), 90)                 # swing plane on the bed
    elif name in ("bracket",):
        sh = part(name).copy()                                # dovetail tip on the bed
    elif name == "vesa_plate":
        sh = part(name).copy()                                # monitor face on the bed
    elif name == "bracket_flip":
        sh = part("bracket").copy()
    else:
        sh = part(name).copy()
    if name == "bracket":
        sh = _place(sh, App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), 0)))
    bb = sh.optimalBoundingBox()
    sh.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    return sh


def _overhang(shape, crit=46.0):
    import MeshPart
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.08, AngularDeflection=0.25, Relative=False)
    zmin, lim = shape.BoundBox.ZMin, -math.sin(math.radians(crit))
    flat = steep = 0.0
    for f in m.Facets:
        if f.Normal.z < lim and min(p[2] for p in f.Points) > zmin + 0.3:
            if f.Normal.z < -0.999:
                flat += f.Area
            else:
                steep += f.Area
    return flat, steep


def printed_mass(shape):
    vol, area = shape.Volume, shape.Area
    sh = min(vol, area * WALL)
    return ABS * (sh + INFILL * (vol - sh)) / 1000.0


def _com(sh):
    return sum((x.CenterOfMass * x.Volume for x in sh.Solids), V(0, 0, 0)) * (1 / sh.Volume)


MOVING = ("inner_tube", "inner_foot", "head", "tilt_nut", "tilt_screw", "bracket", "vesa_plate")
HW_MASS = {"cf_spring": 0.030, "m5_pivot": 0.008, "m4_legs": 0.012, "m5_brake": 0.005, "m3": 0.006,
           "vesa_m4": 0.008, "rubber_feet": 0.006}


LAPTOP_ON_PLATE_N = 8.0      # ESTIMATE: share of the Legion's 2 kg resting on the plate


def foot_points(with_plate):
    pts = []
    if with_plate:
        for x in (-LP_W / 2, LP_W / 2):
            for y in (LP_Y0, LP_Y1):
                pts.append(V(x, y, 0))
    for n, (ang, rf, rtoe) in LEGS.items():
        if with_plate and n != "leg_rear":
            continue
        a = math.radians(ang)
        u = V(math.sin(a), math.cos(a), 0)
        w = V(math.cos(a), -math.sin(a), 0)
        for r in (rf - 13, rf + 13) + ((rtoe,) if rtoe else ()):
            for sg in (-1, 1):
                pts.append(u * r + w * (sg * LEG_T / 2))
    return pts


def _hull(pts):
    p = sorted(set((round(q.x, 4), round(q.y, 4)) for q in pts))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for q in p:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], q) <= 0:
            hi.pop()
        hi.append(q)
    return lo[:-1] + hi[:-1]


def tip_margins(G, hull):
    """Distance from the CG projection to each hull edge (positive inside) and the edge's outward normal."""
    out = []
    n = len(hull)
    for i in range(n):
        a, b = hull[i], hull[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ey)
        nx, ny = ey / L, -ex / L                     # outward for a CCW hull
        d = -((G.x - a[0]) * nx + (G.y - a[1]) * ny)
        out.append((d, (nx, ny)))
    return out


def checks(verbose=True, hs=None, ths=(-15.0, 0.0, 15.0), printing=True):
    rep, ok = [], True

    def line(x):
        rep.append(x)
        if verbose:
            print(x)

    mon = monitor_shapes()
    line("== portable tripod stand for display case v2 ==")
    zb = lambda h: z_it(h) + PIV_DZ - (HY - BEZEL_BOT_Y)
    line(f"height travel {TRAVEL:.0f} mm on the constant-force spring; bezel bottom {zb(0):.0f} .. {zb(TRAVEL):.0f} mm, "
         f"screen top {zb(0) + 235.5:.0f} .. {zb(TRAVEL) + 235.5:.0f} mm above the table (tilt 0)")
    for a in (90.0, 100.0, 110.0, 120.0, 135.0):
        y, z = lid_top(a)
        need = z + 10 - zb(0)
        line(f"  Legion lid {a:3.0f} deg: top edge {z:5.1f} high, {y:6.1f} in front of the mast -> "
             f"raise the mast >= {max(0, need):5.1f} mm for a 10 mm gap {'(OK)' if need <= TRAVEL else '(OUT OF RANGE)'}")
    dy = abs(ball_y(TILT_RANGE[0]) - ball_y(TILT_RANGE[1]))
    line(f"tilt {TILT_RANGE[0]:+.0f} .. {TILT_RANGE[1]:+.0f} deg: lead screw {dy:.1f} mm = {dy / T_TILT[1]:.1f} turns "
         f"({(TILT_RANGE[1] - TILT_RANGE[0]) / (dy / T_TILT[1]):.1f} deg/turn); ball s {ball_s(TILT_RANGE[1]):.1f} .. "
         f"{ball_s(TILT_RANGE[0]):.1f} in channel {RIB_S0 - 1 + BALL_D / 2:.0f} .. {RIB_S1 - 4 - BALL_D / 2:.0f}")
    # ---- moving mass vs spring
    m_mov = MON_MASS + sum(printed_mass(part(n)) for n in MOVING) / 1000 + 0.008 + 0.008
    line(f"moving mass {m_mov * 1000:.0f} g -> {m_mov * GRAV:.1f} N; spring {SPRING_N:.1f} N; "
         f"brake must cover {abs(m_mov * GRAV - SPRING_N):.1f} N")
    # ---- clearance sweep
    static = {n: part(n) for n in ("outer_tube", "top_collar", "brake_knob", "leg_front_L", "leg_front_R", "leg_rear")}
    deck, lid = laptop(110.0)
    hs = hs if hs is not None else (0.0, TRAVEL)
    line(" h     tilt | monitor->stand  cables->stand  bracket->head  ball-in-channel  knob gap | lid(110)->monitor")
    for h in hs:
        for th in ths:
            pl = poses(h, th)
            stand = list(static.values()) + [_place(part(n), pl[n]) for n in ("inner_tube", "head")]
            hd = _place(part("head"), pl["head"])
            mons = [_place(mon[n], pl["monitor"]) for n in ("front_frame", "rear_panel", "io_block")]
            dm = min(m.distToShape(x)[0] for m in mons for x in stand)
            cab = _place(_box(-50, 50, IO_BOT_Y - CABLE_DROP, IO_BOT_Y, REAR_FACE_Z, IO_ROOF_Z), pl["monitor"])
            dc = min(cab.distToShape(x)[0] for x in stand)
            br = _place(part("bracket"), pl["bracket"])
            dbh, vbh = br.distToShape(hd)[0], br.common(hd).Volume
            sc = _place(part("tilt_screw"), pl["tilt_screw"])
            vb = br.common(sc).Volume
            dk = sc.distToShape(hd)[0]
            dl = min(m.distToShape(lid)[0] for m in mons + [br])
            good = dm > 3.0 and vbh < 0.01 and dbh > 0.2 and vb < 0.05
            ok &= good
            line(f"{h:5.1f} {th:+5.0f} | {dm:12.1f} {dc:14.1f} {dbh:13.2f} {vb:14.2f} {dk:10.2f} | {dl:6.1f} "
                 f"{'' if good else '<-- FAIL'}")
    # ---- legs: deployed stop, folded clearance, toe under the laptop
    ot = part("outer_tube")
    for n in LEGS:
        lg = part(n)
        v = lg.common(ot).Volume
        d = lg.distToShape(ot)[0]
        f = _place(lg, fold_placement(n))
        others = [ot, part("top_collar")] + [_place(part(m), fold_placement(m)) for m in LEGS if m != n]
        df = min(f.distToShape(o)[0] for o in others)
        vf = sum(f.common(o).Volume for o in others)
        ok &= v < 0.05 and vf < 0.05
        line(f"{n:12s} deployed: heel on the tube (gap {d:.2f}, overlap {v:.2f} mm3) | folded: clearance {df:.2f} mm "
             f"(overlap {vf:.2f}), top at {f.BoundBox.ZMax:.0f}")
    pl0 = poses(0, 0)
    lp = part("laptop_plate")
    vl = sum(_place(part(n), pl0[n]).common(deck).Volume for n in LEGS) + lp.common(deck).Volume
    vr = sum(_place(part(n), pl0[n]).common(lp).Volume for n in ("leg_front_L", "leg_front_R"))
    dr = min(_place(part(n), pl0[n]).distToShape(lp)[0] for n in ("leg_front_L", "leg_front_R"))
    line(f"laptop plate: {LP_Y1 - LAP_REAR_Y:.0f} mm under the Legion (rear edge {LAP_REAR_Y:.0f} in front of the mast); "
         f"stand vs laptop overlap {vl:.2f} mm3; front feet in the rails: overlap {vr:.2f} mm3 (snap bumps), gap {dr:.2f}")
    # ---- stability
    masses = {n: printed_mass(part(n)) / 1000 for n in BUILDERS}
    hulls = {"tripod alone": _hull(foot_points(False)), "with laptop plate": _hull(foot_points(True))}
    line(f"printed ABS {sum(masses.values()) * 1000:.0f} g + hardware {sum(HW_MASS.values()) * 1000:.0f} g")
    for h, th in ((0.0, 0.0), (TRAVEL / 2, -8.0), (TRAVEL, 0.0), (TRAVEL, -15.0), (TRAVEL, 15.0)):
        pl = poses(h, th)
        items = [(MON_MASS, pl["monitor"].multVec(MON_CG))]
        for n in BUILDERS:
            items.append((masses[n], pl[n].multVec(_com(part(n)))))
        items.append((sum(HW_MASS.values()), V(0, 0, 200)))
        M = sum(m for m, _ in items)
        Gc = sum((c * m for m, c in items), V(0, 0, 0)) * (1 / M)
        top = _place(mon["front_frame"], pl["monitor"]).BoundBox.ZMax
        msg = f"h {h:5.1f} tilt {th:+4.0f}: {M:.2f} kg, CG z {Gc.z:3.0f}, screen top {top:3.0f} |"
        for hn, hull in hulls.items():
            mg = tip_margins(Gc, hull)
            dmin, nrm = min(mg)
            F = M * GRAV * dmin / top
            msg += f" {hn}: {math.degrees(math.atan2(dmin, Gc.z)):4.1f} deg / {F:3.1f} N"
            if hn == "with laptop plate":
                LP = V(0, (LAP_REAR_Y + LP_Y1) / 2, 0)
                Fl = min((M * GRAV * d + LAPTOP_ON_PLATE_N * tip_margins(LP, hull)[i][0]) / top
                         for i, (d, _) in enumerate(mg))
                msg += f", Legion on it: {Fl:3.1f} N"
        line(msg)
    line(f"  (N = horizontal push at the screen top that tips it; Legion share on the plate assumed {LAPTOP_ON_PLATE_N:.0f} N)")
    # ---- printing
    if printing:
        for n in BUILDERS:
            ps = print_shape(n)
            bb = ps.optimalBoundingBox()
            fits = max(bb.XLength, bb.YLength) <= BED - 10 and bb.ZLength <= BED - 2
            flat, steep = _overhang(ps)
            ok &= fits
            line(f"print {n:12s} {bb.XLength:6.1f} x {bb.YLength:6.1f} x {bb.ZLength:6.1f} {'fits' if fits else 'NO FIT'}"
                 f" | >46 deg {steep:6.1f} mm2, flat {flat:6.1f} mm2")
    line("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    with open(os.path.join(HERE, "checks.txt"), "w") as fh:
        fh.write("\n".join(rep) + "\n")
    return ok, rep


# ==================================================================== export ==
def export(out=HERE):
    import MeshPart
    d = os.path.join(out, "3d_print_files")
    os.makedirs(d, exist_ok=True)
    for n in BUILDERS:
        sh = print_shape(n)
        sh.exportStep(os.path.join(d, n + ".step"))
        m = MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.02, AngularDeflection=0.15, Relative=False)
        m.write(os.path.join(d, n + ".stl"))
    return d


def build_folded(name="stand_portable_folded"):
    """Packed: legs folded, mast down, display + VESA plate off."""
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    pl = poses(0.0, 0.0)
    for n in BUILDERS:
        if n in ("vesa_plate", "laptop_plate"):
            continue
        p = pl[n]
        if n in LEGS:
            p = fold_placement(n).multiply(p)
        o = doc.addObject("Part::Feature", n)
        o.Shape = _place(part(n), p)
        if App.GuiUp:
            o.ViewObject.ShapeColor = COLORS.get(n, (0.3, 0.3, 0.3))
    doc.recompute()
    return doc


def _camera(c):
    import FreeCADGui as Gui
    Z = V(*c).normalize()
    X = V(0, 0, 1).cross(Z).normalize()
    Y = Z.cross(X)
    m = App.Matrix(X.x, Y.x, Z.x, 0, X.y, Y.y, Z.y, 0, X.z, Y.z, Z.z, 0, 0, 0, 0, 1)
    v = Gui.ActiveDocument.ActiveView
    v.setCameraOrientation(App.Placement(m).Rotation.Q)
    Gui.updateGui()
    v.fitAll()
    Gui.updateGui()
    return v


def render(out=os.path.join(HERE, "renders"), w=1400, h=1100):
    import FreeCADGui as Gui
    os.makedirs(out, exist_ok=True)
    prm = App.ParamGet("User parameter:BaseApp/Preferences/View")
    anim = prm.GetBool("UseNavigationAnimations", True)
    prm.SetBool("UseNavigationAnimations", False)
    shots = []
    doc, hh = build()
    Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
    for nm, c in (("stacked_front_three_quarter", (0.75, 1.25, 0.55)), ("stacked_rear_three_quarter", (-0.9, -1.2, 0.6)),
                  ("stacked_side", (1.0, 0.0, 0.0))):
        if nm == "stacked_side":
            Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
        p = os.path.join(out, nm + ".png")
        _camera(c).saveImage(p, w, h, "White")
        shots.append(p)
    for n in MON_PARTS + ("laptop_deck", "laptop_lid", "vesa_plate"):
        doc.getObject(n).ViewObject.Visibility = False
    Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
    p = os.path.join(out, "stand_only.png")
    _camera((0.9, -1.0, 0.55)).saveImage(p, w, h, "White")
    shots.append(p)
    build_folded()
    Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
    p = os.path.join(out, "folded.png")
    _camera((0.9, 1.1, 0.35)).saveImage(p, 900, h, "White")
    shots.append(p)
    prm.SetBool("UseNavigationAnimations", anim)
    return shots
