# Dexter Quiet: the operator's reference cage (2026-10-12)

The reference brush-tree target r2 is measured against (ruling brush-tree:ruling:pursue-sdf-composition-remeshing:
the operator rebuilds Dexter Quiet by hand as the reference cage).

Source: `Asset Sources/Ships.blend` in Aetheria, object `Dexter Quiet Cage` (collection Quiet), saved 2026-10-12 17:31.
Exported from a copy by `export.py` (Blender, background mode). Files:

- `cage_raw.obj`: the cage as authored, half a hull: 29 vertices, 25 faces, 9 edges creased at 1.0 (`cage_info.txt`).
- `cage_eval.obj`: the evaluated stack: Mirror (merge on) -> Subsurf level 3 (render 2, limit surface on) ->
  Bevel (0.001, 1 segment, weight-limited) -> Weighted Normal. 3,154 vertices, 3,152 faces.
- The scanned original `Dexter Quiet` (4,832 vertices, 5,600 faces) is not copied here; it stays in Ships.blend.

Fidelity of the hand cage to the scan (vertex-to-nearest-vertex, an upper bound on surface distance; hull diagonal 1.492):
cage->scan mean 0.88% p95 2.04% max 3.11% of the diagonal; scan->cage mean 1.29% p95 4.12% max 6.03%.
That spread is the artistic liberty a human cage takes, and is the fidelity band an automated remesh is measured against.

Operator, 2026-10-12: "I'm afraid I had to take a bit of artistic liberty to get the cage to behave, mostly because
of how creases work in Blender (generates horrible geometry if the crease path isn't closed)". Body fact for the
remesher: crease chains in the cage are closed loops; an open crease path ending inside a face region produces
bad subdivision geometry in Blender's Catmull-Clark (OpenSubdiv) evaluation, so a generated cage must close its creases.
