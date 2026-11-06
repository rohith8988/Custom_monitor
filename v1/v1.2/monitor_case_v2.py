"""
Standalone-monitor enclosure, v2.  Same panel (AUO B160QAN02.Q), board
(XY_H2EDP_UHD95T_V3.1) and slab as v1 - the border is still 10.50mm, the
bottom edge is still the snap tongue, the screw line still runs three edges.

What v2 adds
  * every rear panel is STAND-READY: six M3 seats above the I/O block, so the
    flip stand bolts on without reprinting anything.
  * v2-vesa   - VESA 100 built INTO the rear panel.  Not a bolt-on: four
                integral bosses with heat-set M4 inserts flush in the back
                face, tied together by a rib grid.  No screws in the load path.
  * v2-stand  - a flip-out U leg on a bracket that lands on those six seats.

Why the VESA is flush and not a pedestal
  The rear panel prints visible-face-DOWN, so anything proud of that face
  becomes the bed contact and throws the clamp ribs, splice recess and block
  groove into overhang.  A flush mount avoids that completely: the bosses point
  INWARD into the panel gap, the insert bores open on the back face, and the
  bores are BLIND - no screw can reach the panel behind them, whatever length
  someone fits.  The trade is depth: the gap allows 4.5mm of bore, so this
  takes short (4mm) M4 inserts.  Raising REAR_GAP to 8.0 buys full 8.1mm
  inserts at the cost of 5mm of case thickness - one constant, see _check().

All dimensions mm.  Origin = centre of the panel's ACTIVE AREA, X right,
Y up, Z rearward (z=0 is the front face of the bezel).

Run:  python monitor_case_v2.py
      -> "3d_print files"/*.stl        frame, block, keys, plain rear panel
      -> "3d_print files"/vesa/        rear panel with the VESA built in
      -> "3d_print files"/stand/       bracket + leg
      -> build/*.step                  assemblies
"""

import math
import os
import cadquery as cq

# ---------------------------------------------------------------- panel ------
# AUO B160QAN02.Q, product spec v1.4, sec. 2.1 + 8.1 "LCM Outline Dimension"
AA_W, AA_H      = 344.678, 215.424   # active area
BEZ_SIDE        = 2.50               # AA -> outline, left / right / top
BEZ_FPC         = 6.60               # AA -> outline, bottom (COF + FPC side)
FPC_BULGE       = 0.40
PANEL_T         = 2.60
PANEL_T_FPC     = 4.60
FPC_ZONE        = 9.0
BEZEL_GAP       = 0.40
PANEL_CLEAR     = 0.35

# ---------------------------------------------------------------- board ------
# XY_H2EDP_UHD95T_V3.1 spec sheet, sec. 4 "Structural Dimension Diagram"
BRD_W, BRD_H    = 95.0, 60.1
BRD_PCB_T       = 1.6
BRD_STACK       = 13.5               # PCB + tallest part.  MEASURE YOURS.
BRD_HOLES       = [(4.7, 23.0), (85.0, 23.0),
                   (4.7, 56.5), (85.0, 56.5)]
BRD_HOLE_D      = 3.2
BRD_CLEAR       = 1.0
BRD_TAIL        = 1.6

BRD_PORTS = [( 6.0, 11.0, 11.0),     # CN1  12 V barrel jack
             (24.0, 16.5,  8.0),     # CN4  HDMI 2.0
             (46.6, 16.5,  8.0),     # CN5  HDMI 2.0
             (69.0, 19.0,  9.0),     # CN3  DisplayPort 1.2
             (87.2, 11.0,  9.0)]     # CN7  3.5 mm audio

BRD_Y_BOT       = -92.0

# ------------------------------------------------------------ enclosure ------
BORDER_W        = 10.5   # unchanged from v1
FRONT_LIP_T     = 1.2
REAR_GAP        = 3.0    # panel back -> rear panel inner face.  This is what
                         # limits how deep an integral VESA boss can be.
REAR_PLATE_T    = 2.5
WALL_T          = 1.4
OUT_R           = 3.0
FRONT_CHAM      = 0.6

RIB_W           = 4.0
RIB_GAP         = 0.4
RIB_INSET       = 1.0
RIB_BOT_Y       = -102.0

SCREW_INSET     = 5.4
SCREW_CLEAR_D   = 3.2
SCREW_CSK_D     = 5.6
SCREW_PILOT_D   = 2.5
SCREW_DEPTH     = 5.5
BLK_PILOT_DEPTH = 6.0
BRD_PILOT_DEPTH = 8.0
CSK_RIM_MIN     = 0.8
BOSS_WALL_MIN   = 1.2
SCREW_PITCH     = 55.0
SCREW_BOSS_R    = SCREW_CSK_D / 2 + 0.6
SEAM_STRADDLE   = 10.0
SEAM_KEEPOUT    = 7.0
SCREW_MIN_GAP   = 9.0

TONGUE_W        = 1.15   # bottom-edge snap lip (no room for screws down there)
TONGUE_T        = 0.9
TONGUE_CHAM     = 0.5
PLATE_CLEAR     = 0.25

BLK_WALL        = 2.0
BLK_R           = 6.0
BLK_TOP_CH      = 1.2
BLK_BOSS_D      = 6.5
BLK_BOSS_ROOM   = 7.0
BLK_BOSS_DY     = 22.0
BRD_LIFT        = 2.0
BLK_SPIGOT_W    = 2.0
BLK_SPIGOT_T    = 0.6
ROOF_CLEAR      = 0.8
VENT_W, VENT_H  = 2.0, 12.0
VENT_N          = 5
VENT_PITCH      = 7.5
KEYPAD_W, KEYPAD_H = 9.0, 3.5

# --------------------------------------------------------------- splitting ---
BED             = 256.0
FRAME_SEAM_X    = 0.0
PLATE_SEAM_X    = 30.0
KEY_T           = 1.2
KEY_W           = 4.0
KEY_LEN         = 14.0
SPLICE_W        = 24.0
FIT_CLEAR       = 0.15

# ------------------------------------------------------------- derived -------
SLAB_T   = FRONT_LIP_T + PANEL_T + REAR_GAP + REAR_PLATE_T
Z_PANEL  = FRONT_LIP_T
Z_CAV    = FRONT_LIP_T + PANEL_T
Z_LEDGE  = SLAB_T - REAR_PLATE_T

OD_W     = AA_W + 2 * BEZ_SIDE
OD_TOP   =  AA_H / 2 + BEZ_SIDE
OD_BOT   = -(AA_H / 2 + BEZ_FPC + FPC_BULGE)

OPEN_W, OPEN_H = AA_W + 2 * BEZEL_GAP, AA_H + 2 * BEZEL_GAP
OUT_HX   = OPEN_W / 2 + BORDER_W
OUT_HY   = OPEN_H / 2 + BORDER_W
POC_HX   = OD_W / 2 + PANEL_CLEAR
POC_TOP  = OD_TOP + PANEL_CLEAR
POC_BOT  = OD_BOT - PANEL_CLEAR
POC_CY   = (POC_TOP + POC_BOT) / 2
POC_H    = POC_TOP - POC_BOT

REC_HX   = OUT_HX - WALL_T
REC_HY   = OUT_HY - WALL_T
PLT_HX   = REC_HX - PLATE_CLEAR
PLT_HY   = REC_HY - PLATE_CLEAR

BAND_SIDE = OUT_HX - POC_HX
BAND_TOP  = OUT_HY - POC_TOP
BAND_BOT  = OUT_HY + POC_BOT

RIB_H    = REAR_GAP - RIB_GAP

PLATE_EDGE = WALL_T + PLATE_CLEAR
CSK_RIM    = SCREW_INSET - PLATE_EDGE - SCREW_CSK_D / 2
BOSS_WALL  = min(BAND_SIDE, BAND_TOP) - SCREW_INSET - SCREW_PILOT_D / 2
CSK_DEPTH  = (SCREW_CSK_D - SCREW_CLEAR_D) / 2

BLK_W    = BRD_W + 2 * (BRD_CLEAR + BLK_BOSS_ROOM + BLK_WALL)
BLK_H    = BRD_H + 2 * (BRD_CLEAR + BLK_WALL)
BLK_Y0   = BRD_Y_BOT - BRD_CLEAR - BLK_WALL
BLK_Y1   = BLK_Y0 + BLK_H
BLK_CY   = BLK_Y0 + BLK_H / 2
BLK_BOSS_X = BRD_W / 2 + BRD_CLEAR + BLK_BOSS_ROOM / 2
Z_PCB     = SLAB_T + BRD_LIFT
Z_PCB_TOP = Z_PCB + BRD_PCB_T
Z_ROOF    = Z_PCB + BRD_STACK + ROOF_CLEAR + BLK_WALL
BLOCK_H   = Z_ROOF - SLAB_T
STANDOFF_H = (Z_ROOF - BLK_WALL) - Z_PCB_TOP

BAY_SEAM_CLEAR = 6.0
BAY_INSET = 6.0
BAY_HX    = min(BRD_W / 2 - BAY_INSET, abs(PLATE_SEAM_X) - BAY_SEAM_CLEAR)

# ------------------------------------------------ v2-vesa: built-in mount ----
# VESA 100 x 100, M4.  100 rather than 75 because a 75 pattern puts its right
# column at x=37.5, inside the splice recess (x=18..42) and 7.5mm off the rear
# panel seam.  100 clears both.
VESA_PITCH   = 100.0
VESA_CY      = 34.0      # pattern centre.  The I/O block owns the back from
                         # y=-95 to y=-28.9 and stands 18.30 proud, so the arm
                         # plate has to sit above it - see _check().
VESA_BOSS_D  = 11.0      # integral boss, projects INWARD from the plate
VESA_INS_D   = 5.6       # heat-set M4 insert, 4.0mm long, pressed in from the
VESA_INS_L   = 4.0       # back face and finishing flush with it
VESA_BORE    = 4.5       # bore depth from the back face.  BLIND: a screw
VESA_CAP_MIN = 0.5       # cannot pass it, so it cannot reach the panel.
VESA_RIB_W   = 2.5       # rib grid tying the four bosses into the plate
VESA_TIE_X   = 65.0      # where the grid ties up into the top clamp rib

# ------------------------------------------------ v2-stand: flip stand -------
# A U leg that flips out of the back.  The arms straddle the I/O block and the
# crossbar folds in below it, so the stowed leg lies flat across the panel.
STAND_TILT    = 12.0     # design lean-back of the finished monitor
STAND_PIV_Y   = 80.0
STAND_PIV_H   = 8.0      # pivot axis above the rear panel's outer face.  Set by
                         # the arm's round end, which swings DOWN as it deploys.
STAND_LEG_LEN = 194.0    # capped by the fold: any longer hangs off the bottom
STAND_ARM_W   = 16.0     # arm width, along X
STAND_ARM_T   = 8.0      # arm thickness, perpendicular to its length
STAND_FOOT_W  = 16.0     # crossbar depth, along the leg
STAND_LUG_X   = 80.0
STAND_LUG_T   = 6.0
STAND_GAP     = 0.4
STAND_LUG_Y0, STAND_LUG_Y1 = 54.0, 110.0
STAND_LUG_H   = 21.0
STAND_PLATE_T = 5.0
STAND_BASE_Y0 = 92.0     # footplate starts clear of the arm's pivot boss
STAND_BASE_HX = 95.0
STAND_PIN_R   = 20.0     # stop screw, radius from the pivot
STAND_SLOT_W  = 6.2      # arc slot in the lug: an M3 pan head rides in it
STAND_PIVOT_D = 3.2
STAND_MOUNT   = [(sx * 88.0, y) for sx in (-1, 1) for y in (96.0, 102.0)] + \
                [(sx * 50.0, 99.0) for sx in (-1, 1)]

STAND_ARM_CX  = STAND_LUG_X + STAND_LUG_T / 2 + STAND_GAP + STAND_ARM_W / 2
STAND_PIV_Z   = SLAB_T + STAND_PIV_H


def stand_deploy():
    """Leg angle from straight-down that lands the foot on the desk with the
    case leaning back STAND_TILT.  The leg is a prop, so the tilt and this
    angle are the same fact stated twice - change STAND_TILT and the whole
    stand follows."""
    t = math.radians(STAND_TILT)
    yp, zp = STAND_PIV_Y + OUT_HY, STAND_PIV_Z       # pivot above the bottom edge
    a, b = STAND_LEG_LEN, STAND_LEG_LEN * math.tan(t)
    c, r = yp - zp * math.tan(t), math.hypot(a, b)
    assert abs(c) <= r, "leg too short to reach the desk at this tilt"
    return math.atan2(b, a) + math.acos(c / r)


def vesa_hole_xy():
    return [(sx * VESA_PITCH / 2, VESA_CY + sy * VESA_PITCH / 2)
            for sx in (-1, 1) for sy in (-1, 1)]


def _check():
    # ---- unchanged from v1 --------------------------------------------------
    assert BAND_BOT >= WALL_T + TONGUE_W, (
        f"border {BORDER_W} too thin: only {BAND_BOT:.2f}mm of wall below the "
        f"panel. The panel's bottom bezel is {BEZ_FPC}mm vs {BEZ_SIDE}mm elsewhere.")
    assert CSK_RIM >= CSK_RIM_MIN, (
        f"countersink breaks out of the rear panel edge: only {CSK_RIM:.2f}mm of rim.")
    assert BOSS_WALL >= BOSS_WALL_MIN, (
        f"only {BOSS_WALL:.2f}mm of frame around the pilot hole; an M3 self-tapper "
        f"will split it. Raise BORDER_W.")
    assert CSK_DEPTH + 1.0 <= REAR_PLATE_T, "countersink leaves too little rear panel"
    assert BEZEL_GAP <= 1.0, "datasheet 8.1: bezel opening <= AA + 1.0mm per side"
    assert PANEL_T_FPC + PANEL_CLEAR <= PANEL_T + REAR_GAP, "FPC bulge hits the rear panel"
    assert RIB_BOT_Y - RIB_W / 2 > OD_BOT + FPC_ZONE + 1.0, \
        "bottom clamp rib sits on the FPC fold"
    assert RIB_H > 0 and RIB_H < REAR_GAP, "clamp rib height out of range"
    assert Z_PCB - BRD_TAIL > Z_CAV, "solder tails reach the panel"
    assert STANDOFF_H > BRD_STACK - BRD_PCB_T, "standoffs shorter than the components"
    assert min(Z_PCB_TOP - 0.8 for _ in BRD_PORTS) > SLAB_T + 2.0, \
        "port cutouts leave less than 2mm of rail under them"
    assert max(Z_PCB_TOP + h for _, _, h in BRD_PORTS) < Z_ROOF - BLK_WALL, \
        "a connector is taller than the block"
    assert BLK_BOSS_X - BLK_BOSS_D / 2 > BRD_W / 2 + BRD_CLEAR, "block pillar fouls the board"
    assert BLK_BOSS_X + BLK_BOSS_D / 2 < BLK_W / 2 - BLK_WALL, "block pillar fouls the wall"
    assert BLK_Y0 > POC_BOT + FPC_ZONE + 4.0, "I/O block overlaps the panel's FPC zone"
    assert keypad_y() + KEYPAD_W / 2 < BLK_W / 2 - BLK_WALL, "keypad slot runs off the block"
    for seam, half in ((FRAME_SEAM_X, OUT_HX), (PLATE_SEAM_X, PLT_HX)):
        assert max(half + seam, half - seam) <= BED, \
            f"seam at x={seam} leaves a piece wider than the {BED}mm bed"
    assert abs(FRAME_SEAM_X - PLATE_SEAM_X) > SPLICE_W, \
        "frame and rear-panel seams must be staggered so each splices the other"
    assert abs(PLATE_SEAM_X) < BLK_W / 2 - BLK_WALL, \
        "rear panel seam should run under the I/O block, which splices it"
    assert BAY_HX + BAY_SEAM_CLEAR <= abs(PLATE_SEAM_X), \
        "bay opening reaches the rear panel seam and turns it into an edge notch"
    assert BAY_HX >= 15.0, f"bay only {2*BAY_HX:.0f}mm wide - not enough for the cabling"
    for _, _, _, _, pick, grip, engage, longest, _ in fasteners("v2-stand"):
        assert pick <= longest, "recommended screw bottoms out"
        assert engage >= 3.0, f"only {engage:.1f}mm of thread engagement"
    for sx in (FRAME_SEAM_X, PLATE_SEAM_X):
        assert min(abs(x - sx) for x, y in screw_points() if y > 0) >= SEAM_STRADDLE - 0.01, \
            f"a perimeter screw lands on the seam at x={sx}"

    # ---- everything on the rear panel's inner face has to miss everything ---
    rib_bands = [(RIB_BOT_Y - RIB_W / 2, RIB_BOT_Y + RIB_W / 2),
                 (OD_TOP - RIB_INSET - RIB_W, OD_TOP - RIB_INSET)]
    for x, y in STAND_MOUNT:
        assert abs(x - PLATE_SEAM_X) > SPLICE_W / 2 + SCREW_CSK_D / 2, \
            f"stand seat at x={x} lands in the splice recess"
        for y0, y1 in rib_bands:
            assert not (y0 - SCREW_CSK_D / 2 < y < y1 + SCREW_CSK_D / 2), \
                f"stand seat at y={y} cuts a clamp rib"
        assert abs(x) < PLT_HX - 4 and abs(y) < PLT_HY - 4, \
            "stand seat runs off the rear panel"

    # ---- v2-vesa: the mount is IN the plate, so the panel sets its depth ----
    tip = Z_LEDGE - vesa_boss_proj()
    assert tip >= Z_CAV + RIB_GAP - 1e-9, \
        (f"VESA boss reaches z={tip:.2f}, past the panel's back face at {Z_CAV:.2f}. "
         f"Raise REAR_GAP.")
    cap = (SLAB_T - VESA_BORE) - tip
    assert cap >= VESA_CAP_MIN, (
        f"only {cap:.2f}mm of material closes the insert bore. The bore MUST stay "
        f"blind - it is what stops an over-long M4 reaching the panel. "
        f"Cut VESA_BORE or raise REAR_GAP.")
    assert VESA_INS_L <= VESA_BORE - 0.3, \
        (f"a {VESA_INS_L}mm insert does not fit a {VESA_BORE}mm bore. REAR_GAP={REAR_GAP} "
         f"allows {SLAB_T - Z_CAV - RIB_GAP - VESA_CAP_MIN:.1f}mm of bore; REAR_GAP=8.0 "
         f"would allow 9.6 and take standard 8.1mm inserts, at +5mm of case depth.")
    for x, y in vesa_hole_xy():
        assert abs(x) - VESA_BOSS_D / 2 > abs(PLATE_SEAM_X) + SPLICE_W / 2 or \
               abs(x) + VESA_BOSS_D / 2 < abs(PLATE_SEAM_X) - SPLICE_W / 2, \
            f"VESA boss at x={x} lands in the splice recess"
        assert not (abs(x) < BAY_HX + VESA_BOSS_D / 2 and
                    BRD_Y_BOT + BAY_INSET - 4 < y < BRD_Y_BOT + BRD_H - BAY_INSET + 4), \
            f"VESA boss at {(x, y)} lands in the bay opening"
        assert abs(y) < PLT_HY - VESA_BOSS_D, "VESA boss runs off the rear panel"
    for x, y in STAND_MOUNT:            # the grid and the stand seats share the plate
        for rx in (-VESA_TIE_X, VESA_TIE_X, -VESA_PITCH / 2, VESA_PITCH / 2, 0.0):
            near_rib = abs(x - rx) < VESA_RIB_W / 2 + SCREW_CSK_D / 2
            spans = (VESA_CY - VESA_PITCH / 2 < y < OD_TOP - RIB_INSET - RIB_W
                     if abs(rx) == VESA_TIE_X else
                     VESA_CY - VESA_PITCH / 2 < y < VESA_CY + VESA_PITCH / 2)
            assert not (near_rib and spans), \
                f"stand seat at {(x, y)} would cut the VESA rib at x={rx}"
    # the arm plate lies flat on the back, so it has to clear the I/O block
    assert VESA_CY - VESA_PITCH / 2 - 5.0 > BLK_Y1 + 3.0, (
        f"a VESA plate centred at y={VESA_CY} reaches the I/O block, which tops out "
        f"at y={BLK_Y1:.1f} and stands {BLOCK_H:.2f} proud. Raise VESA_CY.")

    # ---- v2-stand -----------------------------------------------------------
    dep = stand_deploy()
    assert 10.0 < math.degrees(dep) < 45.0, "deploy angle is not a usable prop"
    assert STAND_PIV_Y - STAND_LEG_LEN > -PLT_HY, \
        "stowed leg hangs off the bottom of the rear panel"
    assert STAND_ARM_CX - STAND_ARM_W / 2 > BLK_W / 2 + 2.0, \
        "stowed leg arm lands on the I/O block"
    assert STAND_PIV_Z - STAND_ARM_T / 2 > SLAB_T + 1.0, "stowed leg arm rubs the rear panel"
    swing = STAND_ARM_W / 2 * math.sin(dep) + STAND_ARM_T / 2 * math.cos(dep)
    assert STAND_PIV_Z - swing > SLAB_T + 0.5, (
        f"the arm's round end swings down to {STAND_PIV_Z - swing:.2f} at full deploy "
        f"and hits the rear panel at {SLAB_T:.2f}. Raise STAND_PIV_H.")
    assert STAND_PIV_Y + STAND_ARM_W / 2 + 2.0 < STAND_BASE_Y0, \
        "the arm's pivot boss hits the bracket footplate"
    assert STAND_ARM_CX + STAND_ARM_W / 2 + STAND_FOOT_W / 2 < PLT_HX, \
        "stowed leg is wider than the rear panel"
    assert STAND_PIV_Z + STAND_PIN_R * math.sin(dep) + STAND_SLOT_W / 2 \
        < SLAB_T + STAND_LUG_H - 1.0, "the stop slot runs out of the top of the lug"
    assert STAND_PIV_Y - STAND_PIN_R - STAND_SLOT_W / 2 > STAND_LUG_Y0 + 1.0, \
        "the stop slot runs out of the end of the lug"


def vesa_boss_proj():
    """How far an integral boss may project inward before it fouls the panel."""
    return Z_LEDGE - (Z_CAV + RIB_GAP)


def _even(a, b, pitch):
    """Points from a to b inclusive, as close to `pitch` apart as fits evenly."""
    n = max(1, round(abs(b - a) / pitch))
    return [a + (b - a) * i / n for i in range(n + 1)]


def screw_points():
    """Left, right and top edges plus all four corners - v1's line, unchanged.
    The bottom edge has no room for bosses and uses the snap tongue instead."""
    x, y = OUT_HX - SCREW_INSET, OUT_HY - SCREW_INSET
    y_bot = POC_BOT + SCREW_BOSS_R + 0.4
    pts = [(sx, py) for sx in (-x, x) for py in _even(y, y_bot, SCREW_PITCH)]

    seams = (FRAME_SEAM_X, PLATE_SEAM_X)
    top = [s + d for s in seams for d in (-SEAM_STRADDLE, SEAM_STRADDLE)]
    for px in _even(-x, x, SCREW_PITCH):
        if min(abs(px - s) for s in seams) < SEAM_KEEPOUT:
            continue
        if any(abs(px - k) < SCREW_MIN_GAP for k in top):
            continue
        top.append(px)
    return pts + [(px, y) for px in sorted(top) if abs(abs(px) - x) > 1e-6]


STOCK_LENGTHS = (4, 5, 6, 8, 10, 12, 16, 20)


def fasteners(variant="v2"):
    """The screw schedule, computed from the model so the BOM cannot drift."""
    rows = [("perimeter: rear panel -> frame", len(screw_points()), "M3", "countersunk",
             REAR_PLATE_T, SCREW_DEPTH, SCREW_PILOT_D),
            ("I/O block -> rear panel", len(block_screw_xy()), "M3", "countersunk",
             REAR_PLATE_T, BLK_PILOT_DEPTH, SCREW_PILOT_D),
            ("driver board -> block standoffs", len(BRD_HOLES), "M3", "pan / cheese",
             BRD_PCB_T, BRD_PILOT_DEPTH, SCREW_PILOT_D)]
    if variant == "v2-stand":
        rows += [("stand bracket -> rear panel", len(STAND_MOUNT), "M3", "countersunk",
                  REAR_PLATE_T, BLK_PILOT_DEPTH, SCREW_PILOT_D),
                 ("leg pivot (through arm into lug)", 2, "M3", "pan",
                  STAND_ARM_W, STAND_LUG_T - 0.5, SCREW_PILOT_D),
                 ("leg stop pin (head rides the slot)", 2, "M3", "pan",
                  0.0, 8.0, SCREW_PILOT_D)]
    out = []
    for what, n, thread, head, grip, depth, pilot in rows:
        longest = grip + depth
        pick = max(L for L in STOCK_LENGTHS if L <= longest)
        out.append((what, n, thread, head, pick, grip, pick - grip, longest, pilot))
    return out


def vent_ys():
    return [BLK_CY + (i - (VENT_N - 1) / 2) * VENT_PITCH for i in range(VENT_N)]


def keypad_y():
    return -25.0


def _plate(w, h, z0, z1, r=0.0, cx=0.0, cy=0.0):
    wp = cq.Workplane("XY", origin=(cx, cy, z0)).rect(w, h).extrude(z1 - z0)
    return wp.edges("|Z").fillet(r) if r else wp


def _cyl(x, y, z0, d, h):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(d / 2).extrude(h)


def _tongue(grow, half_len):
    """Bottom-edge snap lip.  `grow` offsets the profile outwards on every face,
    which is how the rear panel's mating rebate is generated."""
    y0, y1 = -REC_HY - grow, -REC_HY + TONGUE_W + grow
    z0, z1 = SLAB_T - TONGUE_T - grow, SLAB_T + grow
    return (cq.Workplane("YZ")
            .polyline([(y0, z0 - TONGUE_CHAM), (y1, z0), (y1, z1), (y0, z1)]).close()
            .extrude(half_len, both=True))


# =============================================================== front =======
KEY_Y = (POC_TOP + REC_HY) / 2                 # ledge key, top rail


def _frame_key_slot(grow):
    return _plate(KEY_LEN + 2 * grow, KEY_W + 2 * grow,
                  Z_LEDGE - KEY_T - grow, Z_LEDGE + 1, cx=FRAME_SEAM_X, cy=KEY_Y)


def front_frame():
    f = _plate(2 * OUT_HX, 2 * OUT_HY, 0, SLAB_T, OUT_R)
    f = f.edges(">Z").chamfer(FRONT_CHAM)          # built front-face-up, then
    f = f.mirror("XY").translate((0, 0, SLAB_T))   # flipped so z=0 is the face

    f = f.cut(_plate(OPEN_W, OPEN_H, -1, FRONT_LIP_T))                 # bezel opening
    f = f.cut(_plate(2 * POC_HX, POC_H, Z_PANEL, Z_LEDGE, cy=POC_CY))  # pocket + cavity
    f = f.cut(_plate(2 * POC_HX, FPC_ZONE, Z_PANEL, Z_PANEL + PANEL_T_FPC + PANEL_CLEAR,
                     cy=POC_BOT + FPC_ZONE / 2))                       # FPC bend relief
    f = f.cut(_plate(2 * REC_HX, 2 * REC_HY, Z_LEDGE, SLAB_T + 1, OUT_R - WALL_T))

    f = f.union(_tongue(0.0, REC_HX - (OUT_R - WALL_T)))
    f = f.cut(_frame_key_slot(FIT_CLEAR))

    for x, y in screw_points():
        f = f.cut(_cyl(x, y, Z_LEDGE - SCREW_DEPTH, SCREW_PILOT_D, SCREW_DEPTH + 0.01))
    return f


# ============================================================ rear panel =====
def _spigot(grow, z0):
    out = _plate(BLK_W - 0.4 + 2 * grow, BLK_H - 0.4 + 2 * grow, z0, SLAB_T + (grow and 1),
                 BLK_R - 0.2 + grow, cy=BLK_CY)
    inn = _plate(BLK_W - 2 * BLK_WALL + 0.4 - 2 * grow, BLK_H - 2 * BLK_WALL + 0.4 - 2 * grow,
                 z0 - 1, SLAB_T + 2, max(BLK_R - BLK_WALL + 0.2 - grow, 0.1), cy=BLK_CY)
    return out.cut(inn)


def block_screw_xy():
    return [(sx * BLK_BOSS_X, BLK_CY + sy * BLK_BOSS_DY)
            for sx in (-1, 1) for sy in (-1, 1)]


def _csk(x, y, z_face, into):
    """Countersunk clearance hole; `into` is +1 to sink from below, -1 from above."""
    d = (SCREW_CSK_D - SCREW_CLEAR_D) / 2
    cone = (cq.Workplane("XY", origin=(x, y, z_face)).circle(SCREW_CSK_D / 2)
            .workplane(offset=into * d).circle(SCREW_CLEAR_D / 2).loft())
    shaft = cq.Workplane("XY", origin=(x, y, z_face - 1 if into > 0 else z_face - 6)) \
        .circle(SCREW_CLEAR_D / 2).extrude(7)
    return cone.union(shaft)


def _vesa_grid():
    """Bosses plus the rib grid that spreads their load into the plate.  All of
    it stands INWARD off the inner face, exactly like the clamp ribs, so the
    outer face stays dead flat and keeps printing against the bed."""
    hx, y0, y1 = VESA_PITCH / 2, VESA_CY - VESA_PITCH / 2, VESA_CY + VESA_PITCH / 2
    z0 = Z_LEDGE - vesa_boss_proj()
    g = None
    # the two ribs that run up to the top clamp rib sit at x=+-VESA_TIE_X, not on
    # the pattern: x=+-50 is where the stand seats are, and a 5.6 countersink
    # would cut a 2.5mm rib clean in half.
    top_rib = OD_TOP - RIB_INSET - RIB_W
    for w, h, cx, cy in ((2 * VESA_TIE_X, VESA_RIB_W, 0, y1),
                         (2 * hx, VESA_RIB_W, 0, y0),
                         (2 * hx, VESA_RIB_W, 0, VESA_CY),      # horizontal rungs
                         (VESA_RIB_W, VESA_PITCH, -hx, VESA_CY),
                         (VESA_RIB_W, VESA_PITCH, hx, VESA_CY),
                         (VESA_RIB_W, VESA_PITCH, 0, VESA_CY),  # verticals
                         (VESA_RIB_W, top_rib - y1, -VESA_TIE_X, (y1 + top_rib) / 2),
                         (VESA_RIB_W, top_rib - y1, VESA_TIE_X, (y1 + top_rib) / 2)):
        r = _plate(w, h, z0, Z_LEDGE, cx=cx, cy=cy)
        g = r if g is None else g.union(r)
    for x, y in vesa_hole_xy():
        g = g.union(_cyl(x, y, z0, VESA_BOSS_D, vesa_boss_proj()))
    return g


def rear_panel(vesa=False):
    """Always stand-ready: the six bracket seats are cut whatever the variant,
    so a plain back can take the flip stand later without a reprint."""
    r = _plate(2 * PLT_HX, 2 * PLT_HY, Z_LEDGE, SLAB_T, OUT_R - WALL_T)
    r = r.cut(_tongue(PLATE_CLEAR, REC_HX))        # rebate for the frame's snap lip

    ro = [POC_HX - PANEL_CLEAR - RIB_INSET, OD_TOP - RIB_INSET]
    for w, h, cy in ((2 * ro[0], RIB_W, ro[1] - RIB_W / 2),          # top
                     (2 * ro[0], RIB_W, RIB_BOT_Y),                  # bottom
                     (RIB_W, ro[1] - RIB_BOT_Y, (ro[1] + RIB_BOT_Y) / 2)):
        for cx in ((0,) if w > RIB_W else (-ro[0] + RIB_W / 2, ro[0] - RIB_W / 2)):
            r = r.union(_plate(w, h, Z_LEDGE - RIB_H, Z_LEDGE, cx=cx, cy=cy))
    if vesa:
        r = r.union(_vesa_grid())
    r = r.intersect(_plate(2 * PLT_HX, 2 * PLT_HY, Z_LEDGE - RIB_H - 1, SLAB_T + 1,
                           OUT_R - WALL_T))        # keep ribs inside the outline

    r = r.cut(_plate(2 * BAY_HX, BRD_H - 2 * BAY_INSET, Z_LEDGE - RIB_H - 1,
                     SLAB_T + 1, cy=BRD_Y_BOT + BRD_H / 2))          # bay opening
    r = r.cut(_spigot(FIT_CLEAR, SLAB_T - BLK_SPIGOT_T - 0.15))      # block locating groove

    if vesa:                                        # blind insert bores, from the back
        for x, y in vesa_hole_xy():
            r = r.cut(_cyl(x, y, SLAB_T - VESA_BORE, VESA_INS_D, VESA_BORE + 0.01))

    for x, y in list(block_screw_xy()) + list(STAND_MOUNT):
        r = r.cut(_csk(x, y, Z_LEDGE, +1))
    for x, y in screw_points():                    # perimeter, sunk on the visible face
        r = r.cut(_csk(x, y, SLAB_T, -1))

    r = r.cut(_plate(SPLICE_W, 2 * PLT_HY + 2, Z_LEDGE - RIB_H - 1, Z_LEDGE + KEY_T,
                     cx=PLATE_SEAM_X))             # splice recess
    return r


# ============================================================== I/O block ====
def io_block():
    b = _plate(BLK_W, BLK_H, SLAB_T, Z_ROOF, BLK_R, cy=BLK_CY)
    b = b.edges(">Z").chamfer(BLK_TOP_CH)
    b = b.cut(_plate(BLK_W - 2 * BLK_WALL, BLK_H - 2 * BLK_WALL, SLAB_T - 1,
                     Z_ROOF - BLK_WALL, max(BLK_R - BLK_WALL, 0.1), cy=BLK_CY))
    b = b.union(_spigot(0.0, SLAB_T - BLK_SPIGOT_T))

    for x, y in block_screw_xy():
        b = b.union(_cyl(x, y, SLAB_T, BLK_BOSS_D, Z_ROOF - BLK_WALL - SLAB_T))
        b = b.cut(_cyl(x, y, SLAB_T - 1, SCREW_PILOT_D, 1 + BLK_PILOT_DEPTH))

    for bx, by in BRD_HOLES:
        x, y = BRD_W / 2 - bx, BRD_Y_BOT + by
        b = b.union(_cyl(x, y, Z_PCB_TOP, BRD_HOLE_D + 2.8, STANDOFF_H))
        b = b.cut(_cyl(x, y, Z_PCB_TOP - 1, SCREW_PILOT_D, 1 + BRD_PILOT_DEPTH))

    for bx, w, h in BRD_PORTS:
        b = b.cut(_plate(w, 3 * BLK_WALL, Z_PCB_TOP - 0.8, Z_PCB_TOP + h,
                         cx=BRD_W / 2 - bx, cy=BLK_Y0 + BLK_WALL / 2))

    zc = (Z_PCB_TOP + Z_ROOF - BLK_WALL) / 2
    for vy in vent_ys():
        for sx in (-1, 1):
            b = b.cut(_plate(3 * BLK_WALL, VENT_W, zc - VENT_H / 2, zc + VENT_H / 2,
                             cx=sx * (BLK_W / 2 - BLK_WALL / 2), cy=vy))
    b = b.cut(_plate(KEYPAD_W, 3 * BLK_WALL, Z_PCB_TOP, Z_PCB_TOP + KEYPAD_H,
                     cx=keypad_y(), cy=BLK_Y0 + BLK_H - BLK_WALL / 2))
    return b


# ============================================================= v2-stand ======
def _stand_lug(sx):
    """One pivot blade.  The arc slot runs from stowed to deployed; the head of
    an M3 threaded into the arm rides in it, so the leg cannot open past the
    design angle.  A through-slot in a standing plate - it bridges 6.2mm."""
    y0, y1 = STAND_LUG_Y0, STAND_LUG_Y1
    z0, z1 = SLAB_T, SLAB_T + STAND_LUG_H
    lug = (cq.Workplane("YZ", origin=(sx * STAND_LUG_X - STAND_LUG_T / 2, 0, 0))
           .moveTo(y0, z0).lineTo(y1, z0).lineTo(y1, z1).lineTo(y0 + 8, z1)
           .lineTo(y0, z0 + 9).close().extrude(STAND_LUG_T))

    dep, slot = stand_deploy(), None
    for i in range(21):
        phi = dep * i / 20
        step = (cq.Workplane("YZ", origin=(sx * STAND_LUG_X - STAND_LUG_T, 0, 0))
                .moveTo(STAND_PIV_Y - STAND_PIN_R * math.cos(phi),
                        STAND_PIV_Z + STAND_PIN_R * math.sin(phi))
                .circle(STAND_SLOT_W / 2).extrude(STAND_LUG_T + 2))
        slot = step if slot is None else slot.union(step)

    pivot = (cq.Workplane("YZ", origin=(sx * STAND_LUG_X - STAND_LUG_T, 0, 0))
             .moveTo(STAND_PIV_Y, STAND_PIV_Z).circle(SCREW_PILOT_D / 2)
             .extrude(STAND_LUG_T + 2))
    return lug.cut(slot).cut(pivot)


def stand_bracket():
    """Footplate + two pivot lugs, one part.  Bolts to the six seats every rear
    panel already has; prints footplate-down, lugs standing up."""
    b = _plate(2 * STAND_BASE_HX, STAND_LUG_Y1 - STAND_BASE_Y0, SLAB_T,
               SLAB_T + STAND_PLATE_T, 4.0, cy=(STAND_BASE_Y0 + STAND_LUG_Y1) / 2)
    for sx in (-1, 1):
        b = b.union(_stand_lug(sx))
    for x, y in STAND_MOUNT:
        b = b.cut(_cyl(x, y, SLAB_T - 1, SCREW_PILOT_D, 1 + BLK_PILOT_DEPTH))
    return b


def stand_leg(phi=0.0):
    """The flip leg: two arms straddling the I/O block, joined at the foot.
    Built flat - pivot at the origin, length along -Y, thickness in Z, which is
    also how it prints - then rotated into the pose."""
    L, t = STAND_LEG_LEN, STAND_ARM_T / 2
    out = STAND_ARM_CX + STAND_ARM_W / 2
    leg = _plate(2 * out, STAND_FOOT_W, -t, t, 3.0, cy=-L + STAND_FOOT_W / 2)  # crossbar
    for sx in (-1, 1):
        leg = leg.union(_plate(STAND_ARM_W, L, -t, t, cx=sx * STAND_ARM_CX, cy=-L / 2))
        leg = leg.union(cq.Workplane("XY", origin=(sx * STAND_ARM_CX, 0, -t))
                        .circle(STAND_ARM_W / 2).extrude(STAND_ARM_T))
        leg = leg.cut(cq.Workplane("YZ", origin=(sx * (STAND_ARM_CX - STAND_ARM_W), 0, 0))
                      .moveTo(0, 0).circle(STAND_PIVOT_D / 2)
                      .extrude(sx * 2 * STAND_ARM_W))          # pivot clearance
        leg = leg.cut(cq.Workplane("YZ",
                                   origin=(sx * (STAND_ARM_CX - STAND_ARM_W / 2 - 0.5), 0, 0))
                      .moveTo(-STAND_PIN_R, 0).circle(SCREW_PILOT_D / 2)
                      .extrude(sx * (STAND_ARM_W - 1)))        # stop screw, blind
    leg = leg.rotate((0, 0, 0), (1, 0, 0), -math.degrees(phi))
    return leg.translate((0, STAND_PIV_Y, STAND_PIV_Z))


# ============================================================ flat inserts ===
def frame_key():
    return _plate(KEY_LEN - FIT_CLEAR, KEY_W - FIT_CLEAR, 0, KEY_T - 0.05)


def rear_splice():
    return _plate(SPLICE_W - FIT_CLEAR, 2 * PLT_HY - 6.0, 0, KEY_T - 0.05)


def panel_stub():
    p = _plate(OD_W, OD_TOP - OD_BOT, Z_PANEL, Z_PANEL + PANEL_T, cy=(OD_TOP + OD_BOT) / 2)
    return p.union(_plate(OD_W, FPC_ZONE, Z_PANEL, Z_PANEL + PANEL_T_FPC,
                          cy=OD_BOT + FPC_ZONE / 2))


# ============================================================== splitting ====
def split_x(solid, x0, big=700.0):
    side = lambda cx: _plate(2 * big, 2 * big, -big, big, cx=cx)
    return solid.intersect(side(x0 - big)), solid.intersect(side(x0 + big))


def _lay_flat(part, name):
    """Orient a piece the way it must be printed, sitting on z=0."""
    if name.startswith("rear_panel") or name == "io_block":
        part = part.rotate((0, 0, 0), (1, 0, 0), 180)   # visible back / roof down
    b = part.val().BoundingBox()
    return part.translate((-b.xmin, -b.ymin, -b.zmin))


def _export(part, name, out_dir):
    p = _lay_flat(part, name)
    bb = p.val().BoundingBox()
    assert bb.xlen <= BED and bb.ylen <= BED, \
        f"{name} does not fit the bed: {bb.xlen:.1f} x {bb.ylen:.1f}"
    cq.exporters.export(p, f"{out_dir}/{name}.stl", tolerance=0.01, angularTolerance=0.1)
    cq.exporters.export(p, f"{out_dir}/{name}.step")
    return bb


if __name__ == "__main__":
    _check()
    here = os.path.dirname(os.path.abspath(__file__))
    out_p = os.path.join(here, "3d_print files")
    out_b = os.path.join(here, "build")
    for d in (out_p, out_b, f"{out_p}/vesa", f"{out_p}/stand"):
        os.makedirs(d, exist_ok=True)

    front, block, stub = front_frame(), io_block(), panel_stub().val()
    dep = stand_deploy()
    rear, rear_v = rear_panel(), rear_panel(vesa=True)
    bracket, leg = stand_bracket(), stand_leg(dep)

    fl, fr = split_x(front, FRAME_SEAM_X)
    rows = []
    for name, part in (("front_frame_L", fl), ("front_frame_R", fr),
                       ("io_block", block), ("frame_key", frame_key()),
                       ("rear_splice", rear_splice())):
        rows.append((".", name, _export(part, name, out_p)))

    for tag, r, d in ((".", rear, out_p), ("vesa/", rear_v, f"{out_p}/vesa")):
        rl, rr = split_x(r, PLATE_SEAM_X)
        assert abs(rl.val().Volume() + rr.val().Volume() - r.val().Volume()) < 1e-3, \
            f"{tag} rear panel split lost material"
        for name, part in (("rear_panel_L", rl), ("rear_panel_R", rr)):
            rows.append((tag, name, _export(part, name, d)))
    assert abs(fl.val().Volume() + fr.val().Volume() - front.val().Volume()) < 1e-3, \
        "front frame split lost material"
    for name, part in (("stand_bracket", bracket), ("stand_leg", leg)):
        rows.append(("stand/", name, _export(part, name, f"{out_p}/stand")))

    # nothing may interfere, and nothing may touch the panel
    variants = {"v2": [("rear_panel", rear)],
                "v2-vesa": [("rear_panel_vesa", rear_v)],
                "v2-stand": [("rear_panel", rear), ("stand_bracket", bracket),
                             ("stand_leg_deployed", leg),
                             ("stand_leg_stowed", stand_leg(0.0))]}
    for variant, extra in variants.items():
        solids = [("front_frame", front), ("io_block", block)] + extra
        for i, (na, a) in enumerate(solids):
            for nb, b in solids[i + 1:]:
                if {na, nb} == {"stand_leg_deployed", "stand_leg_stowed"}:
                    continue
                assert a.val().intersect(b.val()).Volume() < 1e-3, \
                    f"{variant}: {na} and {nb} clash"
            assert a.val().intersect(stub).Volume() < 1e-3, f"{variant}: {na} hits the panel"
        asm = cq.Assembly()
        for n, s in solids:
            if n != "stand_leg_stowed":
                asm.add(s, name=n, color=cq.Color(0.18, 0.18, 0.20))
        asm.add(panel_stub(), name="panel_ref", color=cq.Color(0.1, 0.1, 0.35, 0.4))
        asm.save(f"{out_b}/{variant}_assembly.step")

    print(f"{'dir':<8}{'piece':<16}{'x':>8}{'y':>8}{'z':>8}   fits {BED:.0f}mm bed")
    for tag, name, bb in rows:
        print(f"{tag:<8}{name:<16}{bb.xlen:8.1f}{bb.ylen:8.1f}{bb.zlen:8.1f}   yes")

    print(f"\nslab {SLAB_T:.2f}   border {BORDER_W:.2f}   outer {2*OUT_HX:.1f} x {2*OUT_HY:.1f}"
          f"   (v1, unchanged)")
    print(f"block {BLK_W:.1f} x {BLK_H:.1f} x {BLOCK_H:.2f} proud   max {SLAB_T+BLOCK_H:.2f}")
    tip = Z_LEDGE - vesa_boss_proj()
    print(f"vesa  {VESA_PITCH:.0f}x{VESA_PITCH:.0f} M4 built into the plate, centre y={VESA_CY:.0f}"
          f", back face FLUSH")
    print(f"      boss projects {vesa_boss_proj():.2f} inward to z={tip:.2f} "
          f"(panel back {Z_CAV:.2f}), bore {VESA_BORE:.2f} deep, "
          f"{(SLAB_T - VESA_BORE) - tip:.2f} cap - blind")
    print(f"      4 x M4 heat-set insert, {VESA_INS_D:.1f} dia x {VESA_INS_L:.1f} long, "
          f"M4 screw max {VESA_BORE:.1f} past the arm plate")
    yf = STAND_PIV_Y + OUT_HY - STAND_LEG_LEN * math.cos(dep)
    zf = STAND_PIV_Z + STAND_LEG_LEN * math.sin(dep)
    t = math.radians(STAND_TILT)
    print(f"stand leg {STAND_LEG_LEN:.0f} long, flips out {math.degrees(dep):.1f} deg "
          f"-> {STAND_TILT:.0f} deg lean, foot {yf*math.sin(t)+zf*math.cos(t):.0f}mm "
          f"behind the front edge")
    print(f"      stowed it lies flat, {STAND_PIV_Z - STAND_ARM_T/2 - SLAB_T:.1f}mm off the "
          f"back, clear of the {BLK_W:.0f}mm block")
    for variant in variants:
        print(f"\nscrews - {variant}")
        for what, n, thread, head, pick, grip, engage, longest, pilot in fasteners(variant):
            print(f"  {n:2d} x {thread}x{pick:<3g} {head:<12s} {what:<36s}"
                  f"grip {grip:.1f} + {engage:.1f} into a {pilot:.1f} pilot "
                  f"(max {longest:.1f})")
        if variant == "v2-vesa":
            print(f"   4 x M4 heat-set insert {VESA_INS_D:.1f}x{VESA_INS_L:.1f}"
                  f"      VESA mount - no screw in the load path")
