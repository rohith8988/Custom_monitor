"""
iPad Studio Stand V2 (Mason Warner, MakerWorld 942779, BY-NC) remixed to hold display
case v2 on its VESA-100 spine.  The original's foot, fillets and cable window are kept
as-is; above the window the upright continues as one 6.1 mm sheet that sweeps forward in
an S-bend and becomes the VESA plate, leaning back 12.6 deg like the iPad cradle.

  * one continuous piece: upright -> S-bend -> plate, R10 blends, no separate arm
  * 10 % wider (101.6 -> 112) so the 100 x 100 holes fit inside the width, which keeps it
    printable on its side like the original
  * bend lands at the middle of the plate (case y = +45), so the io_block top vents get ~37 mm of
    free rise and the lower VESA screws stay reachable from behind

Mesh booleans (manifold3d + shapely) - FreeCAD's OCCT crashes on the source mesh.
Run:  python3 build_stand.py
"""
import math
import os

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold, Mesh
from shapely.geometry import LineString, Polygon, box as sbox
from shapely.geometry.polygon import orient

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source", "ipad_studio_stand_v2_original.stl")
REFS = os.path.join(HERE, "source", "_case_refs")

# original, measured (X width, -Y front, Z up, desk at Z = -83.54)
DESK_Z, TILT, REAR_OFF, ARM_ZC = -83.54, 12.6, -10.14, 52.35
UP_Y0, UP_Y1 = 32.004, 38.1
Z_CUT = 41.0                     # keep the original below this (above its cable window)
S_START_Z = 82.0                 # upright runs straight to here, then bends
JOIN_Y = 45.0                    # case y where the bend lands on the plate
BEND_FILLET = 10.0
# changes
SX, RAISE, PLATE_T, HINGE_Y = 112.0 / 101.6, 40.0, 6.0, 0.0
PLATE_Y0, PLATE_Y1, PLATE_HX, PLATE_CH = -19.0, 101.0, 56.0, 6.0
VESA = [(-50.0, -10.0), (50.0, -10.0), (-50.0, 90.0), (50.0, 90.0)]
HOLE_D, CBORE_D, UNDER_HEAD, SCREW_L = 4.6, 8.2, 3.6, 8.0
# case v2
REAR_FACE_Z, TAP_LIMIT, MON_MASS, MON_CG = 11.3, 5.0, 0.922, np.array([0.18, 0.94, 7.55])
PETG = 1.27

st, ct = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
X, T_UP, N_R = np.array([1.0, 0, 0]), np.array([0, st, ct]), np.array([0, ct, -st])
P_CUT = np.array([0, (REAR_OFF + st * ARM_ZC) / ct, ARM_ZC])   # arm centre on cradle back
P0 = P_CUT + np.array([0, 0, RAISE])


def frame(origin):
    """3x4 affine: local (x, a, b) -> origin + x X + a T_UP - b N_R  (b = toward the user)."""
    return np.column_stack([X, T_UP, -N_R, origin])


# case x, y, z(rearward) -> -X, T_UP, N_R (right-handed); rear panel face on the plate front
CASE_TO_STAND = np.column_stack([-X, T_UP, N_R, P0 - N_R * (PLATE_T + REAR_FACE_Z) - T_UP * HINGE_Y])


def to_manifold(tm):
    return Manifold(Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                         tri_verts=np.asarray(tm.faces, np.uint32)))


def to_trimesh(mf):
    m = mf.to_mesh()
    tri = np.array(m.tri_verts)
    remap = np.arange(len(m.vert_properties))
    remap[np.array(m.merge_from_vert, int)] = np.array(m.merge_to_vert, int)
    return trimesh.Trimesh(m.vert_properties[:, :3], remap[tri], process=True)


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def teardrop_z(x, y, z0, d, h, up=(-1.0, 0.0)):
    """Hole along +z with a 45 deg point toward `up` (print up when on its side)."""
    r = d / 2
    cyl = Manifold.cylinder(h, r, circular_segments=48).translate([x, y, z0])
    u = np.array(up) / np.linalg.norm(up)
    s = np.array([-u[1], u[0]])
    k = r / math.sqrt(2)
    pts = [(s * k + u * k) * 0.97, u * r * math.sqrt(2), (-s * k + u * k) * 0.97, np.zeros(2)]  # 0.97: keep kite corners off the cylinder's facet vertices
    area = sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(4))
    pts = pts if area < 0 else pts[::-1]                     # counter-clockwise
    kite = Manifold.extrude(CrossSection([[(x + p[0], y + p[1]) for p in pts]]), h).translate([0, 0, z0])
    return cyl + kite


def _ccw(pts):
    area = sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))
    return pts if area < 0 else pts[::-1]


def plate_cuts():
    """Holes, counterbores, seam relief and corner chamfers in plate-local (x, a, b)."""
    a0, a1, c, hx = PLATE_Y0 - HINGE_Y, PLATE_Y1 - HINGE_Y, PLATE_CH, PLATE_HX
    cuts = []
    for x, y in VESA:
        a = y - HINGE_Y
        cuts.append(teardrop_z(x, a, -1, HOLE_D, PLATE_T + 2))
        cuts.append(teardrop_z(x, a, -12, CBORE_D, PLATE_T - UNDER_HEAD + 12))  # from behind
    cuts.append(box(-8, 8, a0 - 1, a1 + 1, PLATE_T - 0.5, PLATE_T + 1))       # seam relief
    for sx in (-1, 1):
        for aa, sa in ((a0, -1), (a1, 1)):
            # chamfer line through (hx-c, aa) and (hx, aa -/+ c), extended past both faces
            tri = [(sx * (hx - c - 5), aa + sa * 5), (sx * (hx + 5), aa - sa * (c + 5)),
                   (sx * (hx + 5), aa + sa * 5)]
            cuts.append(Manifold.extrude(CrossSection([_ccw(tri)]), PLATE_T + 2).translate([0, 0, -1]))
    return Manifold.batch_boolean(cuts, __import__("manifold3d").OpType.Add)


def _bezier(p0, p1, p2, p3, n=120):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def profile():
    """Side profile (Y, Z) of everything above Z_CUT: upright, S-bend, plate, R10 blends."""
    yz = lambda v: (float(v[1]), float(v[2]))
    yc, h = (UP_Y0 + UP_Y1) / 2, (UP_Y1 - UP_Y0) / 2
    up = sbox(UP_Y0, Z_CUT - 1, UP_Y1, S_START_Z + 0.5)
    plate = Polygon([yz(P0 + T_UP * a - N_R * b) for a, b in
                     ((PLATE_Y0, 0), (PLATE_Y1, 0), (PLATE_Y1, PLATE_T), (PLATE_Y0, PLATE_T))])
    A = np.array([yc, S_START_Z])
    J = np.array(yz(P0 + T_UP * JOIN_Y - N_R * (PLATE_T / 2)))
    t_end = np.array([T_UP[1], T_UP[2]])
    L = 0.45 * (J[1] - A[1])
    curve = _bezier(A, A + [0, L], J - t_end * L, J)
    line = LineString([tuple(A - [0, 1])] + [tuple(p) for p in curve] + [tuple(J + t_end)])
    poly = up.union(line.buffer(h, cap_style=2)).union(plate)
    poly = poly.buffer(BEND_FILLET, join_style=1).buffer(-BEND_FILLET, join_style=1)
    # the blend must not move the plate's front face: clip to it exactly
    far = 400
    behind = Polygon([yz(P0 + T_UP * a - N_R * b) for a, b in
                      ((-far, PLATE_T), (far, PLATE_T), (far, -far), (-far, -far))])
    poly = poly.intersection(behind).union(plate)
    assert poly.geom_type == "Polygon" and not poly.interiors
    return orient(poly, 1.0)


def build():
    src = trimesh.load(SRC)
    src.apply_scale([SX, 1, 1])
    s = to_manifold(src)
    # keep foot, fillets, upright and cable window; drop the cradle/lip (all of it is in
    # front of the upright and above the foot)
    lower = (s ^ box(-80, 80, -100, 100, -100, Z_CUT)) - box(-80, 80, -100, 25, 15, Z_CUT + 1)
    pts = list(profile().exterior.coords)[:-1]
    sheet = Manifold.extrude(CrossSection([pts]), 2 * PLATE_HX).transform(
        np.column_stack([[0, 1, 0], [0, 0, 1], [1, 0, 0], [-PLATE_HX, 0, 0]]))
    return (lower + sheet) - plate_cuts().transform(frame(P0))


def print_pose(s):
    """On its side like the original (+X face on the bed), turned 40 deg on the bed: the
    stand is ~276 mm tall now, which only fits the 256 bed on the diagonal."""
    t = to_trimesh(s)
    t.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    t.apply_transform(trimesh.transformations.rotation_matrix(math.radians(40), [0, 0, 1]))
    b = t.bounds
    t.apply_translation([128 - b[:, 0].mean(), 128 - b[:, 1].mean(), -b[0, 2]])
    return t


def checks(s):
    rep = []
    line = lambda x: (rep.append(x), print(x))
    M4 = np.vstack([CASE_TO_STAND, [0, 0, 0, 1]])
    parts = {}
    for n in ("front_frame", "rear_panel", "io_block", "spine"):
        t = trimesh.load(os.path.join(REFS, n + ".stl"))
        t.apply_transform(M4)
        parts[n] = to_manifold(t)
    ok = True
    for n, p in parts.items():
        v = (s ^ p).volume()
        ok &= v < 0.05
        line(f"{n:12s} overlap {v:6.3f} mm3, gap {s.min_gap(p, 50):6.2f} mm")
    cab = box(-50, 50, -95 - 45, -95, REAR_FACE_Z, 30.8).transform(CASE_TO_STAND)
    cb = cab.bounding_box()
    line(f"cable box (45 mm below the ports): gap to stand {s.min_gap(cab, 50):5.1f} mm, "
         f"lowest {cb[2] - DESK_Z:5.1f} mm above desk")
    # how far the io_block's outlet plume rises before it meets the stand
    col = box(-45, 45, -26.9, 120, 17.6, 30.8).transform(CASE_TO_STAND) ^ s
    if not col.is_empty():
        R, t0 = CASE_TO_STAND[:, :3], CASE_TO_STAND[:, 3]
        cy = ((np.asarray(col.to_mesh().vert_properties[:, :3]) - t0) @ R)[:, 1]
        line(f"io_block outlet plume rises {cy.min() + 26.9:5.1f} mm before it meets the stand")
    fb = parts["front_frame"].bounding_box()
    line(f"bezel bottom {fb[2] - DESK_Z:5.1f} mm, top {fb[5] - DESK_Z:5.1f} mm above desk, "
         f"screen leans back {TILT} deg (the iPad angle)")
    prot = SCREW_L - UNDER_HEAD
    line(f"M4x8 sticks {prot:.1f} mm past the plate: {prot - 2.5:.1f} of the spine's 2.5 mm thread, "
         f"{TAP_LIMIT - prot:.1f} short of bottoming")
    t = to_trimesh(s)
    V, A = t.volume, t.area
    for k, (wl, inf) in (("2 walls 12 % (original's settings)", (0.8, 0.12)), ("3 walls 15 %", (1.2, 0.15))):
        sh = min(V, A * wl)
        line(f"filament {k}: {PETG * (sh + inf * (V - sh)) / 1000:4.0f} g")
    sh = min(V, A * 1.2)
    m_s = PETG * (sh + 0.15 * (V - sh)) / 1e6 + 0.008
    g_m = CASE_TO_STAND @ np.append(MON_CG, 1)
    M = MON_MASS + m_s
    G = (g_m * MON_MASS + t.center_mass * m_s) / M
    b = t.bounds
    h, top = G[2] - DESK_Z, fb[5] - DESK_Z
    for name, mg in (("forward", G[1] - b[0, 1]), ("back", b[1, 1] - G[1]), ("sideways", b[1, 0] - abs(G[0]))):
        ang = math.degrees(math.atan2(mg, h))
        ok &= ang > 10
        line(f"tip {name:8s}: {ang:4.1f} deg of desk tilt, or {M * 9.81 * mg / top:3.1f} N at the screen top")
    p = print_pose(s)
    e = p.extents
    fit = e[0] <= 244 and e[1] <= 244
    ok &= fit and p.is_watertight
    line(f"print on its side (as the original): {e[0]:.0f} x {e[1]:.0f} x {e[2]:.0f} mm, "
         f"{'fits' if fit else 'DOES NOT FIT'}, watertight {p.is_watertight}")
    line("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    return ok, rep, p


if __name__ == "__main__":
    s = build()
    assert s.status().name == "NoError" and len(s.decompose()) == 1
    ok, rep, p = checks(s)
    os.makedirs(os.path.join(HERE, "3d_print_files"), exist_ok=True)
    p.export(os.path.join(HERE, "3d_print_files", "stand_vesa.stl"))
    to_trimesh(s).export(os.path.join(HERE, "source", "stand_vesa_assembly_frame.stl"))
    with open(os.path.join(HERE, "checks.txt"), "w") as fh:
        fh.write("\n".join(rep) + "\n")
