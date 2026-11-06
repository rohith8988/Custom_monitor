"""Threaded 3-D model of the display case v2 aluminium spine (OpenCascade / OCP).

Frame: origin at a plate corner, z = 0 is the face epoxied to the rear panel, z = 3 is the LCD side.
M4 x 0.7 ISO internal thread through 4 holes (Ø3.3 bore), 8 x Ø2.7 through with 90 deg csk Ø4.8
on the LCD side.  Writes spine_3mm_6061_threaded.step and spine_3mm_6061_plain_holes.step.
"""
import math
import sys

from OCP.BRep import BRep_Tool
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeWire
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepGProp import BRepGProp
from OCP.BRepLib import BRepLib
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCone, BRepPrimAPI_MakeCylinder
from OCP.GCE2d import GCE2d_MakeSegment
from OCP.Geom import Geom_CylindricalSurface
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Ax2, gp_Ax3, gp_Dir, gp_Pnt, gp_Pnt2d

W, H, T, R = 160.0, 130.0, 3.0, 6.0
VESA = [(30, 15), (130, 15), (30, 115), (130, 115)]
M25 = [(x, y) for y in (20, 110) for x in (15, 55, 105, 145)]
D, P, BORE = 4.0, 0.7, 3.3


def vol(s):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(s, g)
    return g.Mass()


def count(s, kind):
    e = TopExp_Explorer(s, kind)
    n = 0
    while e.More():
        n += 1
        e.Next()
    return n


def cyl(r, h, x, y, z):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z), gp_Dir(0, 0, 1)), r, h).Shape()


def cone(r1, r2, h, x, y, z):
    return BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(x, y, z), gp_Dir(0, 0, 1)), r1, r2, h).Shape()


def cut(a, b):
    op = BRepAlgoAPI_Cut(a, b)
    op.SetFuzzyValue(1e-5)
    op.Build()
    assert op.IsDone()
    return op.Shape()


def thread_groove(x, y):
    """ISO 60 deg internal-thread groove (the material a tap removes beyond the Ø3.3 bore)."""
    rB, rD = BORE / 2, D / 2
    r_in = rB - 0.15
    t = math.tan(math.radians(30))
    hw_root = P / 16
    hw_in = hw_root + (rD - r_in) * t
    z0 = -2 * P
    turns = (T + 4 * P) / P
    surf = Geom_CylindricalSurface(gp_Ax3(gp_Pnt(x, y, 0), gp_Dir(0, 0, 1)), r_in)
    seg = GCE2d_MakeSegment(gp_Pnt2d(0, z0), gp_Pnt2d(2 * math.pi * turns, z0 + P * turns)).Value()
    edge = BRepBuilderAPI_MakeEdge(seg, surf).Edge()
    from OCP.GeomAbs import GeomAbs_C1
    BRepLib.BuildCurves3d_s(edge, 1e-6, GeomAbs_C1, 14, 200)
    spine = BRepBuilderAPI_MakeWire(edge).Wire()
    poly = BRepBuilderAPI_MakePolygon()
    for px, pz in ((r_in, -hw_in), (rD, -hw_root), (rD, hw_root), (r_in, hw_in)):
        poly.Add(gp_Pnt(x + px, y, z0 + pz))
    poly.Close()
    ps = BRepOffsetAPI_MakePipeShell(spine)
    ps.SetMode(gp_Dir(0, 0, 1))                              # fixed binormal = clean thread flanks
    ps.Add(poly.Wire(), False, False)
    ps.Build()
    assert ps.IsDone(), "pipe shell failed"
    ps.MakeSolid()
    return ps.Shape()


def build(threaded=True):
    box = BRepPrimAPI_MakeBox(W, H, T).Shape()
    f = BRepFilletAPI_MakeFillet(box)
    ex = TopExp_Explorer(box, TopAbs_EDGE)
    while ex.More():
        e = TopoDS.Edge_s(ex.Current())
        c, a, b = BRep_Tool.Curve_s(e, 0.0, 1.0), *BRep_Tool.Range_s(e)
        p1, p2 = c.Value(a), c.Value(b)
        if abs(p1.Z() - p2.Z()) > T - 1e-6:                    # the 4 vertical edges
            f.Add(R, e)
        ex.Next()
    s = f.Shape()
    for x, y in VESA:
        s = cut(s, cyl(BORE / 2, T + 2, x, y, -1))
        if threaded:
            s = cut(s, thread_groove(x, y))
            k = D / 2 + 0.3 - BORE / 2                         # 0.3 mm 90 deg entry chamfer both faces
            s = cut(s, cone(D / 2 + 0.3, BORE / 2, k, x, y, -1e-3))
            s = cut(s, cone(BORE / 2, D / 2 + 0.3, k, x, y, T - k + 1e-3))
    for x, y in M25:
        s = cut(s, cyl(1.35, T + 2, x, y, -1))
        s = cut(s, cone(1.35, 2.4, 1.05, x, y, T - 1.05))
        s = cut(s, cyl(2.4, 1.0, x, y, T))
    return s


def check(s, name):
    ok = BRepCheck_Analyzer(s).IsValid()
    v = vol(s)
    # robustness: a section through a VESA hole axis and a boolean common must both work
    sec = BRepAlgoAPI_Section(s, BRepPrimAPI_MakeBox(gp_Pnt(20, 15.0, -1), 20, 0.001, 5).Shape())
    sec.Build()
    n_sec = count(sec.Shape(), TopAbs_EDGE)
    com = BRepAlgoAPI_Common(s, BRepPrimAPI_MakeBox(gp_Pnt(20, 15.03, -1), 20, 7, 5).Shape())
    com.Build()
    v_com = vol(com.Shape())
    print(f"{name}: valid {ok}, solids {count(s, TopAbs_SOLID)}, volume {v:.1f} mm3 ({v * 2.70e-3:.1f} g in 6061), "
          f"section edges {n_sec}, common-test volume {v_com:.2f}")
    return ok and count(s, TopAbs_SOLID) == 1 and n_sec > 0 and v_com > 1.0, v


def write(s, path):
    w = STEPControl_Writer()
    w.Transfer(s, STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone


if __name__ == "__main__":
    plain = build(False)
    ok_p, vp = check(plain, "plain holes")
    thr = build(True)
    ok_t, vt = check(thr, "threaded")
    print(f"material removed by the 4 threads: {vp - vt:.2f} mm3 ({(vp - vt) / 4:.2f} per hole)")
    if not (ok_p and ok_t):
        sys.exit("CHECK FAILED")
    write(plain, "spine_3mm_6061_plain_holes.step")
    write(thr, "spine_3mm_6061_threaded.step")
    print("written")
