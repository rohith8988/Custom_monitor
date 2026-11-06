# v2 — M2.5, 9.5 mm border, aluminium spine

Built in FreeCAD, **unsplit**. Run it:

```python
import sys; sys.path.insert(0, "/home/rohith/project_docker/workspace/display_case/v2")
import monitor_case_v2 as m
doc, shapes = m.build()      # prints every check, then builds
m.interference(shapes)       # clash + reflector-clearance report
```

| | v1.2 | v2 |
|---|---|---|
| Fasteners | 26 × M3×8 | **33 × M2.5×8**, one length, + 4 × M4 |
| Plastic border | 10.50 | **9.50** |
| AA → outer edge | 10.90 | **10.05** |
| Slab | 9.30 | **11.30** |
| Max depth | 27.60 | 30.80 |
| Outer | 366.48 × 237.22 | 364.78 × 235.52 |
| Frame halves | 183.2 × 237.2 | 227.4 × 235.5 |
| eDP cable clearance | **−1.20 (interference)** | **+0.80** |

## The seven changes that matter

**1. Staggered front-frame seams.** The top rail is cut at x = +45, the bottom
rail at x = −45. v1.2 cut both at x = 0, and two joints on one line have no
lever arm between them — that is a hinge, not a joint. 90 mm of stagger turns
relative rotation of the halves into a couple the shells actually resist. The
bottom-rail joint also stops being the one with no key and no screw within
178 mm.

**2. Aluminium spine carries the VESA.** 160 × 130 × 3 mm, bonded to the rear
panel's inner face, crossing the rear seam at x = 0. The four M4 are **blind-
tapped 2.5 mm into aluminium**, so there is no thread in plastic, nothing to
creep under preload, and no torque limit to remember. It is 46× the bending
stiffness of the entire 2.5 mm rear plate, and it splices the seam it crosses.
Located by four printed pips, clamped by eight M2.5 while the epoxy cures —
the epoxy is the load path, the screws are shear pins.

**3. REAR_GAP 3.0 → 5.0 fixes the eDP collision.** The datasheet puts the
connector 12.31 ± 1.00 mm from the outline. At v1.2's gap a mated cable
interferes with the rear panel by 1.2 mm. At 5.0 it clears by 0.8.

**4. No clamp rib on the FPC edge, and none behind the active area.** AUO
precaution 8 forbids pressing the reflector. Clamp ribs now sit inside the
2.50 mm bezel band on three edges only; the panel's own 280 × 12 PCB strip owns
everything below y = −102.7 and nothing goes there. Cross-ribs and the spine do
pass over the active area, so they are held **2.0 mm clear of it and carry no
foam** — they are stiffeners that physically cannot reach the panel. There is a
geometric check for exactly this (`reflector_check`).

**5. The panel is datumed, not floating.** Hard pads on +X and +Y, foam on the
opposite two. `BEZEL_GAP` is 0.55, not 0.40 — see below.

**6. The block breathes.** Inlet low in the bottom wall, outlet high in the top
wall: 125 mm² in, 485 mm² out, plus 2.6 mm of roof air. v1.2 had 240 mm² of
side slots all at one height — a dead-air box around a board whose spec
(section 6) is **0 to +40 °C**.

**7. Port capture lips.** Each opening is surrounded by a lip the connector
shell seats into, so insertion load goes into the block instead of the board's
solder joints. The lip stops 0.2 mm short of the board's own PCB edge — the
check caught it at 0.5 mm over on the first build.

## Why BEZEL_GAP is 0.55 and not 0.40

The drawing says `2.50 ± 0.30 (AA TO OD)`. The active area can sit 0.3 mm
off-centre *inside its own outline*, and no amount of datuming fixes that. Add
0.10 for printed pad position and the spread is ±0.40:

| BEZEL_GAP | range | lip overlaps AA? | over AUO's AA+1.0? |
|---|---|---|---|
| 0.40 | −0.00 … 0.80 | **yes** | no |
| **0.55** | **0.15 … 0.95** | **no** | **no** |
| 0.70 | 0.30 … 1.10 | no | **yes** |

0.55 is the only value that clears both bounds. **Measure your panel and this
collapses to ±0.10**: set `PANEL_MEASURED = True`, put caliper readings in
`BEZ_L/R/T/B`, and `BEZEL_GAP` drops to 0.40 — worth another 0.15 mm of border
on all four sides, honestly rather than by hoping.

## Still to verify against the physical parts

Marked `ESTIMATE` in `params.py`. None of these are in either datasheet:

- `EDP_BODY_W` / `EDP_BODY_D` / `EDP_MATED_T` — connector footprint and the
  height of a **mated** cable over the panel's 4.60 mm face. Drives `REAR_GAP`.
- `PANEL_CORNER_R` — must stay under `POC_R` (2.5) or the panel corners bind.
- `BRD_STACK` — 13.5 assumed against a spec of 12.6 ± 0.3. Sets block height 1:1.
- Board hole and connector positions were read off the dimensioned drawing.

## Files

| | |
|---|---|
| `params.py` | every constant, each cited to a datasheet section |
| `checks.py` | design rules — tolerance, load and datasheet limits |
| `monitor_case_v2.py` | FreeCAD geometry + interference and reflector checks |
| `monitor_case_v2.FCStd` | the built document |

`python params.py` and `python checks.py` run without FreeCAD.

## Splitting

`python split_v2.py` inside FreeCAD (`import split_v2 as sp; sp.run()`) cuts the
case into six printed pieces and lays them out on five 256 × 256 beds. See
`print_beds/README.md` for the bed table, assembly order and screw schedule.

The front-frame seams are **lap joints**, staggered at x = +45 (top rail) and
x = −45 (bottom rail), with the step running through the empty bezel opening.
Bond area goes from 64 → 171 mm² on the top rail and 36 → 91 mm² on the bottom,
and the joint works in shear instead of peel. Each half gets one tongue and one
notch, so both come out 227.4 × 235.5.

| | pieces | beds |
|---|---|---|
| v1.2 | 7 (incl. `frame_key`) | 4 |
| v2 | 6 — the lap is its own key | 5 |

Fifth bed because the I/O block no longer squeezes alongside a rear-panel half:
181.0 + 66.1 leaves under 2 mm of edge margin. It shares bed 5 with the splice
instead.
