import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection

r = STEPControl_Reader(); r.ReadFile("spine_3mm_6061_threaded.step"); r.TransferRoots(); s = r.OneShape()

def section_xz(y, x0, x1):
    sec = BRepAlgoAPI_Section(s, gp_Pln(gp_Pnt(0, y, 0), gp_Dir(0, 1, 0))); sec.Build()
    ex = TopExp_Explorer(sec.Shape(), TopAbs_EDGE); segs = []
    while ex.More():
        c = BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()))
        d = GCPnts_QuasiUniformDeflection(c, 0.002)
        pts = [c.Value(d.Parameter(i)) for i in range(1, d.NbPoints() + 1)]
        xs = [p.X() for p in pts]; zs = [p.Z() for p in pts]
        if max(xs) >= x0 and min(xs) <= x1: segs.append((xs, zs))
        ex.Next()
    return segs

fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1, 1]})
for ax, (y, xc, title) in zip(axs, ((15.0, 30.0, "M4 x 0.7 tapped hole (cut through its axis)"),
                                     (20.0, 15.0, "M2.5 clearance hole, 90° countersink"))):
    for xs, zs in section_xz(y, xc - 5, xc + 5):
        ax.plot([x - xc for x in xs], zs, color="#222222", lw=1.2)
    ax.set_xlim(-5, 5); ax.set_ylim(-0.6, 3.9); ax.set_aspect("equal")
    ax.axhspan(-0.6, 0, color="#f3e1c8", zorder=-1); ax.axhspan(3.0, 3.9, color="#dfe7f3", zorder=-1)
    ax.text(-4.9, -0.45, "epoxy face (to rear panel)", fontsize=8); ax.text(-4.9, 3.6, "LCD side", fontsize=8, color="#2a4a7a")
    ax.set_title(title, fontsize=10); ax.set_xlabel("mm from hole axis"); ax.set_ylabel("mm (plate thickness 3.0)")
    ax.grid(alpha=0.25)
axs[0].annotate("ISO 60° flanks, P 0.7\nmajor Ø4.0, bore Ø3.3", (1.95, 1.6), (2.6, 2.4), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.6))
axs[1].annotate("Ø4.8 x 90°", (2.3, 3.0), (2.6, 3.45), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.6))
fig.suptitle("Aluminium spine, sections from spine_3mm_6061_threaded.step", fontsize=11)
fig.tight_layout(); fig.savefig("spine_3mm_sections.png", dpi=160); print("ok")
