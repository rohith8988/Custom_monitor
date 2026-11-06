# B160QAN02.Q standalone monitor enclosure

Two shells around a salvaged AUO **B160QAN02.Q** 16" panel driven by an
**XY_H2EDP_UHD95T_V3.1** board. Flat slab, uniform border, featureless rear with a
single low I/O block. No stand, no VESA pattern — deliberately omitted.

`python monitor_case.py` → `3d_print files/*.stl` (+ `.step`), `build/*.step`.

| | |
|---|---|
| Assembled | 366.5 × 237.2 × 27.6 mm |
| Slab thickness | 9.30 mm |
| Visible border | 10.50 mm, equal on all four sides |
| I/O block | 115.0 × 66.1 mm, 18.30 mm proud |
| Fasteners | **26 × M3 × 8** — 22 countersunk, 4 pan. One size. See **Screws** below |

## The 7 printed pieces

| Piece | Size | Orientation | Supports |
|---|---|---|---|
| `front_frame_L` / `_R` | 183.2 × 237.2 × 9.3 | **bezel face down** | none |
| `rear_panel_L` | 211.6 × 233.9 × 5.1 | **visible back down** | none |
| `rear_panel_R` | 151.6 × 233.9 × 5.1 | **visible back down** | none |
| `io_block` | 115.0 × 66.1 × 18.9 | **roof down, cavity up** | none |
| `frame_key` | 13.8 × 3.9 × 1.1 | flat | none |
| `rear_splice` | 23.9 × 227.9 × 1.1 | flat | none |

Nothing needs support. Every unsupported region in the exported meshes is a
bridge of 2 mm or less (port and vent sills 2.0, the frame's snap tongue 1.15,
the tongue rebate 1.4, the block's locating groove 1.9). The build script
verifies this — it also proves the three shells have zero intersection volume
with each other and with a panel stub, and that the splits conserve volume
exactly.

Both visible surfaces — the bezel face and the rear panel — print **against the
bed**, so their finish is the bed's finish. A smooth PEI sheet gives the matte
grey of the reference photos directly; no ironing needed.

## Why the block is its own part

Making it separate is what removes all supports. The rear panel can then print
visible-face-down, which puts its clamp ribs, splice recess and block groove on
the up-face; and the block prints roof-down with its cavity open upward, so the
board standoffs come out as upright pillars instead of something hanging off a
17 mm ceiling. It also drops the block 0.6 mm and matches the reference photos,
where the block reads as an applied element with a parting line at its base.

The board hangs from four standoffs under the block's roof, components facing
the roof. Screw it in with the block sitting roof-down on the bench, then invert
the whole thing onto the rear panel.

## Seams, and keeping them tight

Three seams, all straight butt joints at **nominal zero clearance** — they are
meant to close, not to slip together:

* **Front frame** splits at `x = 0`, through the top and bottom rails.
* **Rear panel** splits at `x = 30`, deliberately *not* the same line, so each
  shell spans the other's joint. Two perimeter screws straddle every seam
  (`SEAM_STRADDLE`), and the build asserts no screw lands on one.
* **Block base** meets the rear panel on a 1.9 mm locating ring.

The bay opening under the block is sized to stop 6 mm short of the panel seam
(`BAY_SEAM_CLEAR`, asserted). If it reached the seam it would open into a notch
in both halves and leave 44 mm of that joint held by nothing but the splice bar.

What holds each seam:

| Seam | Located by | Held by |
|---|---|---|
| Front frame | `frame_key` in the top rail's ledge + the panel itself, which is a ground rectangle sitting across the joint in a 0.35 mm-clearance pocket | rear panel spanning it, 4 straddle screws, bonded faces |
| Rear panel | `rear_splice` bonded into a 1.2 mm recess down the full seam | that splice + the I/O block, which bolts to both pieces |
| Block base | locating ring, 0.15 mm fit | 4 × M3 from inside |

**The visible seam quality is a slicer setting, not a geometry problem.** Both
visible faces are bed faces, so elephant foot lands exactly on the seam line.
Turn on elephant-foot / first-layer compensation (0.15–0.20 mm) or scrape the
first half-millimetre of the mating faces flat before you bond. Without that,
a squashed first layer holds the joint open by exactly the amount it bulges.

Bond the seams with thin CA or slow epoxy. Only the keys and the block ring get
clearance (`FIT_CLEAR = 0.15`); widen it if your printer runs tight.

## Screws

**Everything is M3 × 8. One size, 26 of them** — 22 countersunk, 4 pan head.
The build script prints this table and asserts each length neither bottoms out
nor drops below 3 mm of engagement, so it stays true to the model.

| Where | Qty | Screw | Head | Grip | Engagement | Pilot in the print | Max length |
|---|---|---|---|---|---|---|---|
| perimeter: rear panel → frame | 18 | **M3 × 8** | countersunk (DIN 965 / 90°) | 2.5 | 5.5 | Ø2.5 | 8.0 |
| I/O block → rear panel | 4 | **M3 × 8** | countersunk (DIN 965 / 90°) | 2.5 | 5.5 | Ø2.5 | 8.5 |
| driver board → block standoffs | 4 | **M3 × 8** | pan or cheese | 1.6 | 6.4 | Ø2.5 | 9.6 |

### Fit

* **Front frame pilots: Ø2.5, blind, no thread.** That is the tight one — an M3
  self-tapper cuts its own thread in it. It should need a driver, not drop in.
  Ø2.5 is 0.83 × the major diameter; go to Ø2.6 only if your printer runs tight
  and you are splitting bosses (`SCREW_PILOT_D`).
* **Rear panel clearance: Ø3.2**, which is the ISO 273 *close* fit — the
  tightest standard M3 clearance there is. This one deliberately is not
  interference: 22 screws have to line up across two printed panel halves and
  two printed frame halves, and the clearance is what lets the joint pull flush
  instead of jacking itself open. If it binds, open it to Ø3.4
  (`SCREW_CLEAR_D`).
* **Countersinks: Ø5.6 × 1.2 deep, 90°.** A DIN 965 M3 head (Ø5.5 × 1.65) sits
  just below flush. Don't substitute pan heads in the 22 countersunk positions —
  the perimeter heads are the visible screw line, and the block heads sit on the
  rear panel's inner face where a proud head would foul the panel.

Nothing longer than the "max length" column will work; the pilots are blind.

### Why the border went from 9.5 to 10.5 mm

An M3 countersunk head is Ø5.6 against M2.5's Ø5.0, and that head has to sit
entirely inside the rear panel's rim while still leaving the frame enough wall
around the pilot hole. The 7.05 mm band a 9.5 mm border gives could not do both.
At 10.5 mm the band is 8.05 mm, which leaves **0.95 mm of rim** outboard of each
countersink and **1.40 mm of frame wall** inboard of each pilot. Both are
asserted on every build (`CSK_RIM_MIN`, `BOSS_WALL_MIN`).

## How the panel is held

Nothing is glued or screwed to the panel. It drops face-down into the frame's
pocket, landing on a 1.2 mm front lip that overlaps the bezel by 2.1 mm — inside
the datasheet's "system bezel opening no more than 1.0 mm larger than active
area" limit (§8.1). Printed ribs 2.60 mm tall on the rear panel then press it
forward; **1 mm foam tape on the rib faces** supplies the compliance and the
preload, and absorbs the tolerance between a salvaged panel and a printed part.

The bottom rib is deliberately held at `y = −102`, clear of the FPC fold, which
the frame reliefs to 4.6 mm depth over the bottom 9 mm.

## Why the bottom edge has no screws

The panel's bezel is 2.50 mm on three sides but 6.60 mm on the FPC edge, so its
active area sits 2.05 mm off the outline's centre. Centring the *outer rectangle
on the active area* is what makes the visible border uniform, and it leaves only
`BORDER_W − 6.95` mm of wall below the panel — 3.55 mm at the current 10.5 mm
border. That is plenty for the 1.4 mm wall plus 1.15 mm ledge the rear panel
lands on, but nowhere near the ~8 mm an M3 seat needs.

So the bottom edge is retained by an integral snap tongue instead, and the
perimeter screw line runs down both sides, across the top, and into all four
corners.

## Assembly

1. Screw the board to the four standoffs inside `io_block` (M3×8 pan), block
   roof-down on the bench, components toward the roof.
2. Bond `rear_splice` into the recess across the rear panel seam; bond
   `frame_key` across the frame seam. Let them cure flat.
3. Apply 1 mm foam tape along the rear panel's clamp ribs.
4. Lay both frame halves face-down on a flat table and drop the panel into the
   pocket — it squares them up.
5. Connect eDP (panel → CN10) and backlight (CN11) through the bay opening.
6. Invert `io_block` onto the rear panel, ring into groove, 4 × M3×8 csk from
   the inside.
7. Snap the rear panel's bottom edge under the frame's tongue, pivot down, fit
   the 18 perimeter screws.

The keypad harness leaves through a 9 × 3.5 mm slot in the block's far wall.

## Parameters worth touching

| Name | Why |
|---|---|
| `BRD_STACK` | PCB + tallest part, 13.5 assumed (spec says 12.6 ±0.3). **Measure yours** — it sets the block height 1:1. |
| `BED`, `FRAME_SEAM_X`, `PLATE_SEAM_X` | Where it splits. Asserts fire if a piece exceeds the bed, if the seams stop being staggered, or if a screw lands on one. |
| `FIT_CLEAR` | Keys and block ring only. Printer fit. |
| `SCREW_PILOT_D` / `SCREW_CLEAR_D` | Screw fit: Ø2.5 tight into the frame, Ø3.2 close clearance through the rear panel. |
| `RIB_H`, `RIB_GAP` | Panel preload. |
| `BORDER_W` | Border width. Floor is set by the panel's asymmetry *and* the M3 head; see above. |
| `BRD_PORTS` | Connector openings, `(centre x from PCB left edge, width, height)`. |

## Source dimensions

Panel: AUO B160QAN02.Q product spec v1.4, §2.1 and §8.1 — AA 344.678 × 215.424,
outline 349.678 × 224.524 (224.924 max with FPC bend), 2.60 mm thick / 4.60 mm at
the FPC.

Board: XY_H2EDP_UHD95T_V3.1 spec §4 — 95.0 × 60.1 mm, 12.6 mm tall, four R1.6
holes at x = 4.7 / 85.0, y = 23.0 / 56.5, connectors centred at x = 6.0, 24.0,
46.6, 69.0, 87.2. Hole and connector positions were measured off the dimensioned
drawing, not quoted from text — **verify against your board before printing.**
