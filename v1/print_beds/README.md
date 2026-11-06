# Print beds — B160QAN02.Q monitor case, v2, VESA 100x100 variant

Built from `v2/monitor_case_v2.py` (already generated, unmodified). This folder
just repackages the 7 parts you need for the **VESA + fully-enclosed** build
into 4 print-ready beds sized for the **Elegoo Centauri Carbon (256x256x256mm)**.
The flip-stand parts (`stand_bracket`, `stand_leg`) are left out — you chose
VESA, not the stand — but every rear panel is stand-ready if you want to add
it later without reprinting anything.

Each `bedN.../bedN_*.stl` is a single mesh with all of that bed's parts
already laid out flat on the 256x256 plate with clearance between them and the
edges — drop it straight into your slicer, no rearranging needed. The matching
`.step` next to it is the same layout for reference/measuring. Each bed folder
also has an `originals/` subfolder with the individual, unmerged part files
(step + stl) in case you want to reprint just one part or edit it.

| Bed | Parts | Footprint (mm) | Orientation | Supports |
|---|---|---|---|---|
| `bed1_front_frame_L` | front_frame_L | 183.2 x 237.2 | bezel face down | none |
| `bed2_front_frame_R` | front_frame_R | 183.2 x 237.2 | bezel face down | none |
| `bed3_rear_panel_L_vesa` | rear_panel_L (VESA) + rear_splice | 240.4 x 233.9 | visible back down | none |
| `bed4_rear_panel_R_vesa` | rear_panel_R (VESA) + io_block (rotated 90 deg) + frame_key | 240.8 x 234.9 | visible back down / roof down | none |

All four fit the 256x256 bed with >=10mm margin on every side. Nothing needs
supports — every unsupported span in the source meshes is <=2mm (verified by
the build script's own asserts).

## What you're building

Two shells around a salvaged AUO B160QAN02.Q 16" panel (349.68 x 224.92mm
outline, 2.60/4.60mm thick) driven by an XY_H2EDP_UHD95T_V3.1 board
(95.0 x 60.1mm, 12.6mm tall). Assembled case: 366.5 x 237.2 x 27.6mm,
10.5mm uniform border. VESA 100x100 (M4, 4 heat-set inserts, flush,
blind bores) is built into the rear panel — no bolt-on bracket.

## Assembly order

1. Press the four M4 heat-set inserts into the VESA rear-panel halves from
   the outside, panel flat on the bench, flush not proud.
2. Screw the driver board to the four standoffs inside `io_block` (M3x8 pan),
   block roof-down on the bench, components facing the roof.
3. Bond `rear_splice` into the recess across the rear-panel seam, and
   `frame_key` across the front-frame seam. Let cure flat.
4. Apply 1mm foam tape along the rear panel's clamp ribs.
5. Lay both front-frame halves face-down and drop the LCD panel into the
   pocket — it squares the halves up.
6. Route eDP (panel -> CN10) and backlight (CN11) through the bay opening.
7. Invert `io_block` onto the rear panel (locating ring into groove), 4x M3x8
   countersunk from inside.
8. Snap the rear panel's bottom edge under the frame's tongue, pivot down,
   fit the 18 perimeter screws.

## Screws — everything is M3, one length family

| Where | Qty | Screw | Head |
|---|---|---|---|
| perimeter: rear panel -> frame | 18 | M3 x 8 | countersunk |
| I/O block -> rear panel | 4 | M3 x 8 | countersunk |
| driver board -> block standoffs | 4 | M3 x 8 | pan/cheese |
| VESA arm -> case | 4 | M4 (short, 4mm insert length) | per your VESA arm |

Bond seams with thin CA or slow epoxy. Turn on elephant-foot compensation
(0.15-0.20mm) in your slicer so the visible bed-face seams close flush.

## Before you print bed4 (io_block)

The board's mounting-hole and connector positions were measured off the
datasheet's dimensioned drawing, not quoted from a text spec — **verify them
against your actual XY_H2EDP_UHD95T_V3.1 board before printing**, especially
if you're on a different revision. `BRD_STACK` (board + tallest component
height) is assumed at 13.5mm against a spec of 12.6 +/-0.3mm; measure your
board's actual stack height and re-run `monitor_case_v2.py` with the corrected
value if it differs, before committing to this io_block print.

## Source dimensions

Panel: AUO B160QAN02.Q spec v1.4, Sec 2.1 / 8.1 — active area 344.678 x
215.424mm, outline 349.678 x 224.524mm (224.924 max with FPC bend),
2.60mm thick / 4.60mm at the FPC.

Board: XY_H2EDP_UHD95T_V3.1 spec Sec 4 — 95.0 x 60.1mm, 12.6mm tall, four
R1.6 mounting holes at x=4.7/85.0, y=23.0/56.5; connectors centred at
x=6.0, 24.0, 46.6, 69.0, 87.2mm from the board's left edge.
