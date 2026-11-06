"""Laser-cut DXFs + 1:1 A4 drawing for the display case v2 aluminium spine (160 x 130 x 3)."""
import math
import ezdxf
from ezdxf import units
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

W, H, T, R = 160.0, 130.0, 3.0, 6.0
VESA = [(30, 15), (130, 15), (30, 115), (130, 115)]
M25 = [(x, y) for y in (20, 110) for x in (15, 55, 105, 145)]
D_M4, D_M25, D_CSK = 3.3, 2.7, 4.8
B = math.tan(math.radians(90) / 4)          # bulge for a 90 deg arc


def dxf(path, with_m25):
    """R2000 DXF in mm with LINE / ARC / CIRCLE only (no polylines): the most widely accepted form."""
    doc = ezdxf.new("R2000")
    doc.units = units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    m = doc.modelspace()
    for p, q in (((R, 0), (W - R, 0)), ((W, R), (W, H - R)), ((W - R, H), (R, H)), ((0, H - R), (0, R))):
        m.add_line(p, q)
    for c, s0, s1 in (((W - R, R), 270, 360), ((W - R, H - R), 0, 90), ((R, H - R), 90, 180), ((R, R), 180, 270)):
        m.add_arc(c, R, s0, s1)
    for x, y in VESA:
        m.add_circle((x, y), D_M4 / 2)
    if with_m25:
        for x, y in M25:
            m.add_circle((x, y), D_M25 / 2)
    doc.saveas(path)


dxf("spine_3mm_laser_cut.dxf", True)
dxf("spine_3mm_laser_cut_no_M2.5_holes.dxf", False)

# ---- verify the DXFs read back with the right geometry
for f in ("spine_3mm_laser_cut.dxf", "spine_3mm_laser_cut_no_M2.5_holes.dxf"):
    d = ezdxf.readfile(f)
    msp = d.modelspace()
    from ezdxf import bbox
    ext = bbox.extents(msp)
    circ = sorted((round(c.dxf.center.x, 3), round(c.dxf.center.y, 3), round(2 * c.dxf.radius, 3)) for c in msp.query("CIRCLE"))
    print(f, d.dxfversion, "units", d.header["$INSUNITS"], "extents", round(ext.size.x, 3), "x", round(ext.size.y, 3),
          "lines", len(msp.query("LINE")), "arcs", len(msp.query("ARC")), "circles", len(circ), sorted(set(c[2] for c in circ)))

# ---- 1:1 drawing on A4 landscape (also a drilling template)
PW, PH = 297.0, 210.0
fig = plt.figure(figsize=(PW / 25.4, PH / 25.4))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PW); ax.set_ylim(0, PH); ax.set_aspect("equal"); ax.axis("off")
ox, oy = 22.0, 40.0                              # plate origin on the page
K = "#111111"
ax.add_patch(FancyBboxPatch((ox + R, oy + R), W - 2 * R, H - 2 * R, boxstyle=f"round,pad={R}", fc="#eceef0", ec=K, lw=0.8))
for x, y in VESA:
    ax.add_patch(Circle((ox + x, oy + y), D_M4 / 2, fc="white", ec=K, lw=0.6))
    ax.add_patch(Circle((ox + x, oy + y), 2.0, fc="none", ec=K, lw=0.4, ls=(0, (2, 1.5))))
for x, y in M25:
    ax.add_patch(Circle((ox + x, oy + y), D_CSK / 2, fc="none", ec="#c85a0a", lw=0.5))
    ax.add_patch(Circle((ox + x, oy + y), D_M25 / 2, fc="white", ec=K, lw=0.6))
for x, y in VESA + M25:                          # centre crosses for punching / drilling
    for dx, dy in ((-3, 0), (0, -3)):
        ax.plot([ox + x + dx, ox + x - dx], [oy + y + dy, oy + y - dy], color=K, lw=0.25)
fs = 5.6
def hdim(x0, x1, y, txt, off=0):
    ax.annotate("", (ox + x0, y), (ox + x1, y), arrowprops=dict(arrowstyle="<->", lw=0.4, shrinkA=0, shrinkB=0))
    ax.text(ox + (x0 + x1) / 2, y + 0.8, txt, ha="center", va="bottom", fontsize=fs)
def vdim(y0, y1, x, txt):
    ax.annotate("", (x, oy + y0), (x, oy + y1), arrowprops=dict(arrowstyle="<->", lw=0.4, shrinkA=0, shrinkB=0))
    ax.text(x - 0.8, oy + (y0 + y1) / 2, txt, ha="right", va="center", fontsize=fs, rotation=90)
hdim(0, W, oy - 12, "160")
hdim(30, 130, oy - 6, "100 (VESA)")
for x in (15, 55, 105, 145):
    ax.plot([ox + x, ox + x], [oy + H + 1, oy + H + 9], color=K, lw=0.2)
ax.text(ox + W / 2, oy + H + 10.5, "M2.5 holes at x = 15, 55, 105, 145", ha="center", fontsize=fs)
vdim(0, H, ox - 9, "130")
vdim(15, 115, ox - 4, "100 (VESA)")
ax.text(ox + W + 3, oy + 15, "y 15", fontsize=fs, va="center"); ax.text(ox + W + 3, oy + 115, "y 115", fontsize=fs, va="center")
ax.text(ox + W + 3, oy + 20, "y 20", fontsize=fs, va="center", color="#c85a0a"); ax.text(ox + W + 3, oy + 110, "y 110", fontsize=fs, va="center", color="#c85a0a")
ax.text(ox + W + 3, oy + 2, "x 30 / 130 = VESA", fontsize=fs)
ax.text(ox + 2, oy + 2, "origin (0,0)", fontsize=4.5, color="#555555")
# scale check bar
ax.plot([ox, ox + 50], [16, 16], color=K, lw=0.8)
for xx in (ox, ox + 50): ax.plot([xx, xx], [14.5, 17.5], color=K, lw=0.8)
ax.text(ox + 25, 17.5, "50 mm: measure this after printing (print at 100 %, no 'fit to page')", ha="center", va="bottom", fontsize=fs)
# section detail (4:1) at the right
sx, sy, S = 214.0, 120.0, 4.0
def P(x, z): return (sx + x * S, sy + z * S)
# plate section around one M4 hole (x -6..6) and one M2.5 csk hole (x 9..21)
ax.add_patch(Polygon([P(-6, 0), P(-1.65, 0), P(-1.65, T), P(-6, T)], fc="#d7dade", ec=K, lw=0.5, hatch="////"))
ax.add_patch(Polygon([P(1.65, 0), P(10.65, 0), P(10.65, T - 1.05), P(9.6, T), P(1.65, T)], fc="#d7dade", ec=K, lw=0.5, hatch="////"))
ax.add_patch(Polygon([P(13.35, 0), P(18, 0), P(18, T), P(14.4, T), P(13.35, T - 1.05)], fc="#d7dade", ec=K, lw=0.5, hatch="////"))
for side in (-1, 1):                              # M4 thread major diameter (tapped)
    ax.plot([P(side * 2.0, 0)[0]] * 2, [P(0, 0)[1], P(0, T)[1]], color=K, lw=0.4, ls=(0, (1.5, 1)))
ax.text(P(0, T + 1.0)[0], P(0, T + 1.0)[1], "M4 x 0.7\ntap through\n(Ø3.3 cut)", ha="center", va="bottom", fontsize=fs)
ax.text(P(12, T + 1.0)[0], P(12, T + 1.0)[1], "Ø2.7 through,\n90° csk Ø4.8\non the LCD side", ha="center", va="bottom", fontsize=fs)
ax.text(P(-6, -1.2)[0], P(0, -1.2)[1], "face glued to the rear panel (z = 0)", fontsize=fs - 0.6, va="top")
ax.text(P(-6, T + 0.2)[0], P(0, T + 0.2)[1] + 0.3, "LCD side", fontsize=fs - 0.6, va="bottom", color="#c85a0a")
ax.text(sx - 2, sy - 12, "Section detail, 4:1 (not to scale with the plate)", fontsize=fs, style="italic")
# notes / title block
notes = [
    "DISPLAY CASE v2 - ALUMINIUM SPINE (VESA carrier)",
    "Material: aluminium 6061-T6 (5052 OK), 3.0 mm.  Qty 1.  Deburr all edges.",
    "Outline 160 x 130, R6 corners.  Drawing is 1:1 on A4 (also a drilling template).",
    "Laser cut: outline + 4 x Ø3.3 (+ 8 x Ø2.7 if accepted).",
    "After cutting: tap the 4 x Ø3.3 holes M4 x 0.7 THROUGH (plain M4 tap,",
    "  cutting fluid).  Countersink the 8 x Ø2.7 holes 90° to Ø4.8 on ONE face",
    "  = the LCD side.  The other face is epoxied to the rear panel.",
    "VESA screw: M4 must stick out <= 5.5 mm past the arm plate (M4 x 8 with the",
    "  portable stand's plate gives 4.4).  Longer reaches toward the LCD.",
    "Plate is symmetric: any orientation, only the countersink face matters.",
]
for i, n in enumerate(notes):
    ax.text(198, 100 - i * 4.6, n, fontsize=fs if i else fs + 1.2, weight="bold" if i == 0 else "normal", va="top")
ax.add_patch(Rectangle((5, 5), PW - 10, PH - 10, fill=False, ec=K, lw=0.6))
fig.savefig("spine_3mm_drawing_1to1_A4.pdf")
fig.savefig("spine_3mm_drawing_preview.png", dpi=150)
print("drawing ok")
