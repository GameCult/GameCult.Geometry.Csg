# Run 5: Blender 5.2.2 QuadriFlow, headless, on Dexter Quiet's SDF zero set

## Why it "refused"
Not headless, not context. The operator's exec path runs blocking when called from Python (`OP_IS_INVOKE` unset), poll needs only an active editable
mesh object in object mode, and no window/area is used. An ico sphere and a UV sphere remesh fine with `--background --factory-startup` and no
temp_override (`tools/diag.py`: both FINISHED).
The refusal text comes from `mesh_is_manifold_consistent` (object_remesh.cc). Besides edge-with-3-faces, flipped winding and wire edges, it
rejects **any edge shorter than 1e-4 (compare_v3v3)**. Run 2/4's voxel remesh (voxel 0.005, Newton-projected) had 20 edges of 1e-5..1e-4 although
bmesh called it manifold and consistent. The message is the same for all four failure causes, which is why it looked like a headless problem.

## Recipe (works)
Voxel remesh -> project onto f=0 -> `bmesh.ops.remove_doubles` on the verts of edges < 1.2e-4 (dist 2e-4) -> dissolve_degenerate ->
recalc_face_normals -> (optional) mark edges with dihedral > 30 deg as sharp (`e.smooth=False`) ->
`bpy.ops.object.quadriflow_remesh(target_faces=N, use_mesh_symmetry=False, use_preserve_sharp=..., use_preserve_boundary=False, seed=0)`.
Active object, object mode, no override. Script `tools/qf5.py`; measure/score/render via `tools/one.py` + `tools/chain.sh` (run 4's measure/score/render unchanged).
Input 69,911 faces; each run 6-30 s. One case hung: sharp-preserve at target 15000 ran >25 min, I killed my PID 55924 (no output).
Guidance: QuadriFlow takes no cross field or user-supplied orientation; it computes its own from the (sharp-flagged) mesh. Only knobs:
target faces/edge length, sharp, boundary, symmetry (mesh symmetry axes), seed, curvature (compiled out). Run 4's field cannot be fed in.

## Measurements (run 2/4 scorer; out/*.metrics.json, *.score.txt)
| | QF 1796 f | QF 5032 f | QF 11534 f | QF sharp 1831 f | QF sharp 5581 f | run 4 L | run 3 v7 |
|---|---|---|---|---|---|---|---|
| tris / ngons | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 176 / 231 | 196 / 180 |
| poles per 1000 v | 39.0 | 20.3 | 12.8 | 36.5 | 18.6 | 140.3 | 47.1 |
| boundary edges (holes) | 6 | 6 | 0 | 12 | 20 | 846 | 0 |
| slivers <10 deg (share) | 0.3% | 0.03% | 0.08% | 3.0% | 0.5% | 17.6% | 24% |
| longest loop (edges) | 346 open | 823 open | 1389 open | 561 | 800 | 124 | 148 closed |
| closed loops >= 20 edges | 0 | 0 | 0 | 0 | 6 | 7 | 30 |
| chamfer % diag | 0.494 | 0.495 | 0.501 | 0.502 | 0.501 | 0.531 | **0.228** |
| F@2% / sil-IoU | 0.955 / 0.908 | 0.955 / 0.906 | 0.954 / 0.901 | 0.953 / 0.900 | 0.954 / 0.903 | 0.950 / 0.875 | **0.990 / 0.967** |
(Targets 2000/6000/15000/sharp 2000/6000; QF returns about 0.75-0.9x the target. "Loops" are open and meander: no designed edge flow.)

## Reading
- Topology is clean: pure quads, low poles (13-39/1000 v, falling with density), almost no slivers, near-watertight. Better than run 4 on every count
  and on poles/slivers better than v7. But loops are not aligned to design features and no loop closes.
- Fidelity does NOT improve with face count and sits at 0.49-0.50, close to run 4 and 2x worse than v7. The sheet shows why: the thin wing
  (0.03-0.08 thick) is below QuadriFlow's lattice, so the trailing/leading rim is eaten into a ragged saw-edge and the wing-tip/tail go jagged; the
  body and dorsal detail (canopy ridge, pods, strakes) smooth away. Sharp preservation (dihedral > 30 flags, 3648 edges) did not fix the rim; it
  added boundary holes (12-20) and slivers. Unprojected output; I did not re-project QF verts onto f=0 (would help a little, not the rim).
- So: QuadriFlow is a viable automatic quad-dominant retopo for the thick body, a poor one for a knife-edge wing. It does not replace run 3's designed
  cage; at best it could cover body parts with the wing handled separately.

## Files
sheet-quadriflow.png (rows: target, SDF zero set, run 4 L, run 3 v7, QF 1796, QF 5032, QF-sharp 5581; cols 3/4, top-ish, side, wire 3/4, wire top).
out/qf_s{0,1}_{N}.obj, out/*.metrics.json, out/chain.log, tools/diag.py qf5.py one.py chain.sh.
Processes: all mine ended; operator GUI Blender PID 36324 untouched.
