# v2 — built-in VESA, flip stand, v1 slab untouched

Same case as v1: **366.5 × 237.2 × 27.6 mm, 10.50 mm border, 9.30 mm slab, 18
perimeter screws on three edges, snap tongue on the bottom.** Nothing about the
shell changed. `python monitor_case_v2.py` builds everything and asserts every
number below.

| | |
|---|---|
| `3d_print files/` | `front_frame_L/R`, `io_block`, `frame_key`, `rear_splice`, `rear_panel_L/R` |
| `3d_print files/vesa/` | `rear_panel_L/R` with the VESA built in — swaps for the plain pair |
| `3d_print files/stand/` | `stand_bracket`, `stand_leg` — adds to either rear panel |
| `build/` | `v2` / `v2-vesa` / `v2-stand` assembly `.step` |

**Every rear panel is stand-ready.** Six M3 seats sit above the I/O block in
*both* versions, so you can add the flip stand later without reprinting the
back. On a case with no stand they read as six 3.2 mm dots.

## VESA — built into the rear panel

**VESA 100 × 100, M4, flush with the back face. No bolt-on part, no screws in
the load path.** Four bosses are part of the plate, pointing *inward*, tied
together by a rib grid that also ties up into the top clamp rib. The mount is
four **heat-set M4 inserts** pressed into the back face until flush.

It is flush rather than a pedestal because the rear panel prints
**visible-face-down**. Anything proud of that face becomes the bed contact and
throws the clamp ribs, splice recess and block groove into overhang. Pointing
the bosses inward costs nothing: they print as short pillars on the up-face,
right alongside the clamp ribs.

**The bores are blind — that is the point.** Depth is set by the panel behind:
the boss may project 2.60 mm before it reaches the 0.4 mm clamp-rib clearance
line, so the bore is 4.50 mm deep with a 0.60 mm cap closing it. An M4 cannot
pass that cap, so it cannot reach the display, whatever length someone fits.
A bolt-on pedestal screwed through the plate has the opposite failure mode.

That depth takes **short 4 mm M4 inserts** (5.6 dia). Four of them in PETG pull
out at several hundred N each against a ~12 N monitor, so the margin is large,
but if you want full 8.1 mm inserts set `REAR_GAP = 8.0` — the assert message
says so, and everything re-derives. It costs 5 mm of case depth.

VESA 100 rather than 75: a 75 pattern puts its right column at x = 37.5, inside
the splice recess (x = 18…42) and 7.5 mm off the rear panel seam. 100 clears
both, and the seam then runs *between* the columns where the grid splices it.

The pattern centre is at **y = +34**, not on the case centre. The arm plate lies
flat on the back and the I/O block stands 18.30 mm proud from y = −95 to
y = −28.9; a centred pattern would put the plate on top of the block. Asserted.
The mount is 34 mm above the centre of mass, so the arm carries a small
nose-down moment — any arm with tilt friction handles it.

## Flip stand

A U leg that flips out of the back and lies flat when stowed. Two printed parts
plus 10 M3.

* **Stowed** it sits flat across the panel, 4.0 mm off the back — arms outboard
  of the I/O block (±91.4 vs the block's ±57.5), crossbar folded in below it.
  Asserted, both for the block and for the rear panel edge.
* **Flips out 22.6° → the case leans back 12°**, foot 94 mm behind the front
  edge. `stand_deploy()` solves that from the geometry; the leg is a prop, so
  the tilt and the leg angle are the same fact stated twice. Change
  `STAND_TILT` and the leg, the lug and the stop all follow.
* **The stop is a hard stop, not friction.** An arc slot in each lug runs from
  stowed to deployed; the head of an M3 threaded into the arm rides in it. The
  leg physically cannot open past the design angle. The pivot screw's friction
  only has to hold the leg *stowed* — it never carries the monitor.
* Pivot is 8.0 mm above the back. That height is set by the arm's round end,
  which swings **down** as the leg opens; at 6 mm it dipped into the rear panel.
  Asserted now.
* Centre of mass sits 29.5 mm behind the front edge on a 94 mm base — it will
  not tip either way.

Bracket prints footplate-down, lugs standing up (the arc slot bridges 6.2 mm).
Leg prints flat. No supports on either.

## Assembly deltas from v1

* **VESA back:** press the four M4 inserts in from the outside before anything
  else, with the panel flat on the bench. Flush, not proud. M4 × (arm plate
  + 4.5 max).
* **Stand:** bracket goes on before the rear panel meets the frame — its six
  screws come from inside. Then hang the leg on the lugs: pivot M3×20 from
  outboard through the arm into the lug, stop M3×8 from the lug side into the
  arm so its head lands in the slot. Tighten the pivots until the leg stays put
  when you fold it.
