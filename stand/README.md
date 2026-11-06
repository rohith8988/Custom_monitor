# VESA iPad Studio Stand for display case v2

A remix of Mason Warner's *iPad Studio Stand V2* (MakerWorld 942779, BY-NC, so keep it
non-commercial), built from the original mesh. The foot, its fillets and the cable window
are unchanged, and so is the cradle's **12.6° lean**, so the screen sits at the same
angle the iPad did. Fixed angle, no hinge.

## What changed (only these)

1. **Cradle, lip and arm replaced** by one continuous 6 mm sheet: above the cable window the upright sweeps forward in an S-bend and becomes the VESA-100 plate (bend lands mid-plate, R10 blends), leaning back 12.6° like the cradle. No joint.
2. **40 mm taller** than the original. At the original height the
   bezel would sit about 25 mm off the desk and the I/O block's cables would land on the foot.
3. **10 % wider (101.6 → 112 mm)**. The 100 × 100 holes need 112 mm, and keeping the
   plate inside the stand's width lets it print on its side like the original.

## Mounting: no heat inserts

The M4 threads are already in the case's aluminium spine. The plate only has plain
holes. Use **4 × M4×8** socket-head screws from the back of the plate. **Not M4×10**:
8 mm puts 1.9 mm of thread into the spine's 2.5 mm tapped hole, and a 10 bottoms out
before the plate is tight.

## Print

`3d_print_files/stand_vesa.stl` is one part, already in position for a 256 × 256 bed:

- It lies **on its side like the original**, turned 40° so it fits diagonally (236 × 237 × 112 mm).
- Use **supports, same as the original**: tree supports from the build plate only. Only the
  cable window needs them; the bend is support-free.
- Filament: about 134 g at the original's 2 walls / 12 %, or about 186 g at 3 walls / 15 %
  (recommended for a 0.92 kg monitor). PETG or PLA.

## Checks (`checks.txt`, all pass)

| | |
|---|---|
| Fit against the v2 case | no overlap; plate stops 7.9 mm above the I/O block |
| Bezel bottom / screen top | 62 / 295 mm above the desk |
| Cables | 45 mm plug box under the ports clears the stand by 30 mm and sits 36 mm off the desk |
| Tipping | needs 17–20° of desk tilt; about 2 N pushed at the screen top, same class as an iPad on the original |

## Files

| | |
|---|---|
| `3d_print_files/stand_vesa.stl` | the print |
| `stand.FCStd` | FreeCAD: stand with the case mounted (meshes) |
| `build_stand.py` | rebuilds the STL and `checks.txt` from `source/` (needs numpy, trimesh, manifold3d) |
| `source/` | original iPad mesh, case reference meshes |
| `backup_revA_rod_hinge/` | the earlier hinge version, kept for reference |
