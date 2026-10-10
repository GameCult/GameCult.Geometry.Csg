# Mesh probe run 4: SDF with smooth-min for the shape, a field-aligned cage for the topology

Agent `spike-sdf-smin-cage`, session `self-2026-10-10-ag2`, 2026-10-11. Disposable scratch; no repo edited.
Root: this directory (`...\scratchpad\mesh-probe\run4-sdf-cage\`). Ruling: `brush-tree:ruling:spike-sdf-smin-to-cage`.

## Verdict

- **SDF for the shape works, and fusion costs nothing.** One program (`tools/sdf_quiet.py`, about 130 lines, 63 fitted
  numbers) fuses the body loft, wing, pods and chin fin with named smin radii. Fitted, it scores chamfer 0.520 % / F@2 % 0.949 / sil-IoU 0.895.
  - Chamfer is better than run 2's description (0.84).
  - Silhouette is worse than the unfitted start (0.934).
  - It is not at run 3's hand cage (0.19-0.23 / 0.967).
- **Automatic field-aligned topology did not reach a cage.** Here is how far each step got:
  - The cross field is good. It uses analytic curvature, the program's exact crease and Ohtake-style ridges.
  - My numpy Instant-Meshes position field and extraction break. Result: 463 faces, of which 102 are quads, with 189 boundary edges (holes).
  - Blender's QuadriFlow refuses to run headless on every input, including a verified-manifold voxel remesh.
- **The Catmull-Clark refit of a cage to the field works** (limit |f| mean 0.0016, chamfer 0.599 to 0.552). It is the
  reusable piece. But it needs a cage with sane topology, and this spike could not make one automatically.
- **The shippable lowering fails her bar.** The cause is upstream: the cage is broken. Measured anyway, see below.
- Plain answer: "SDF for the shape, fitted cage for the topology" is viable only if the cage comes from a designed layout
  (run 3's approach) or from a real global parametrisation (MIQ or the full Instant Meshes hierarchy and extraction). The local
  Jacobi version I could build in the budget does not do it.

## 1. The SDF program and its fidelity

`tools/sdf_quiet.py`:
- `hull = smin(smin(smin(body, wing, k_wing), pods, k_pod), chin_fin, k_fin)`.
- body: superellipse stations with Catmull-Rom between them.
- wing: a slab on z = a + b|x| + c·y, tapered, cut by the planform polygon minus the scallops (IQ sdPolygon).
- The wing edge is `max(slab, planform)` with `k_edge = 0`, a deliberate hard edge.
- Start values: run 2's description numbers. The fit is Levenberg-Marquardt over the named parameters (`tools/fit.py`):
  - residuals: f(p) at 9.7k outer-shell target points, from ray first-hits in 96 directions, so cockpit internals are ignored;
  - a hinge on 15k ray-derived "outside" labels;
  - a small prior;
  - box bounds.

Scores use `tools/common.py`, a numpy/BVH port of run 1's `mp score` (the mp build dir was deleted). It is calibrated on run 2's B.stl: 0.852 / 0.898 / 0.920 here against mp's 0.841 / 0.899 / 0.920.

| Program state | Chamfer % diag | F@2% | Mean sil-IoU | Note |
|---|---|---|---|---|
| p0: run 2's numbers as an SDF (k_wing 0.06) | 0.897 | 0.910 | 0.934 | Smooth fusion alone already beats run 2's silhouette (0.920) |
| LM, unbounded (`out/fit.log`) | 1.348 | 0.840 | 0.798 | Degenerate: self-crossing planform (x = -1.99), negative pod radii, taper -5.5. The fit exploits the program |
| **LM, bounded + prior (`out/params_fit.json`)** | **0.520** | **0.949** | **0.895** | t2c 0.586, c2t 0.454 |

The bounded fit presses on its bounds:
- wing_t is at its 0.08 cap and k_wing at its 0.12 cap;
- a pod coordinate is at its bound;
- the beak station came out inverted (z_bottom above z_top, half-width 0.084), which leaves a flat cap at the nose.

The program lacks structure the target has: canopy, ridges, a wing thicker at the root. The optimiser compensates with blend radius and thickness. The program is still readable, but the fitted values are partly a fit, not a description (run 1's finding again). Zero-set render: row 2 of `sheet-main.png`. The wing edge shows surface-nets staircase, because a hard `max()` edge is not feature-preserved by surface nets. The nose is ragged where the inverted station sits.

## 2. Cross field and quad meshing: how far it got

Pipeline (`tools/quad.py`, `tools/qmesh.py`):
1. Surface nets at h = 0.008, 27,660 vertices, Newton-projected onto f = 0. It has 64 non-manifold edges where the wing is under 3 cells thick.
2. Principal directions and magnitudes come from the program's Hessian, by central differences of the analytic field, not mesh estimates.
3. Ridges: the derivative of |kmax| along dmax, a third-order quantity, crosses zero at strong |kmax| (Ohtake et al. 2004). This found 1,678 vertices.
4. The exact crease comes from the program's structure: the tangent is cross(∇slab, ∇planform) where both are about 0 on the wing part. This found 912 vertices.
5. Flat and umbilic rule: alignment weight = (anisotropy / p90)², so flat or umbilic regions get no curvature constraint and are filled by smoothing from features and curved regions. Ridges and creases are near-hard constraints (weight 5).
6. 4-RoSy smoothing.
   - Representation: power vectors z = e^{4iθ}, with Rodrigues (minimal-rotation) transport between tangent planes. This is the Palacios-Zhang / Ray et al. / Knöppel et al. representation.
   - Method: Jacobi.
   - Why not IM matching: Instant Meshes' per-edge 4-way matching under Jacobi stalled at 1,500 singular faces on the coarse test. Plain projection transport left 404 false singularities on the wing edge; Rodrigues fixed that.
7. Position field: the Instant Meshes 4-PoSy in numpy.
   - Lattice origins start random, because p = V is a harmonic phase ramp that Jacobi never removes.
   - Each edge uses the minimal lattice image.
   - A voxel-cluster hierarchy of 2-3 levels, capped at s/2.
8. Extraction: union-find collapse of zero-offset edges, unit-offset edges become lattice edges, planar face tracing.
9. Catmull-Clark refit (`tools/cc.py`): CC is built as an explicit linear operator. Cage positions are least-squares fitted so the limit points equal their own Newton projections (8 rounds).

Higher-order constraints against plain Instant-Meshes-style smoothing (same mesh and solver, alignment term off: `quad.py ... plain`):

| | Field (curvature + ridge + crease) | Plain IM smoothing |
|---|---|---|
| Misalignment to principal dir (aniso conf > 0.5), median / p90 | **0.3° / 2.1°** | 27.8° / 40.8° |
| Misalignment to the wing-edge crease, median / p90 | **0.1° / 0.7°** | 17.9° / 33.0° |
| Singular faces (±1 / ±2 index) | 220 (196 / 24) | 185 (164 / 21) |
| Extraction at s = 0.035: faces / quads / tris / untraced cycles / boundary edges | 463 / 102 / 342 / 129 / 189 | 444 / 107 / 315 / 159 / 252 |
| Same mesh as a CC cage after refit: chamfer / sil | 0.552 / 0.883 | 0.574 / 0.873 |
| Extraction at s = 0.07 (cage density): faces / quads | 59 / 17 | 47 / 9 |

What the higher-order information bought:
- An exactly aligned field on every feature and curved region.
- 35 more singularities, most of them clustered at the ragged nose, where the fit is bad and the constraints conflict.
- Downstream, slightly fewer holes and slightly better refit fidelity. That gain is swamped, because the position field and extraction break either way.

Pictures:
- `out/X.top.png`, `out/X.q34.png` and `out/X.close.png`: field mode. Orange crosses, red singular faces, blue lines for the IM lattice edges that survived.
- `out/Xplain.*.png`: plain mode.

Where it broke:
- **The position field does not converge globally.** On a flat 60x60 grid test, the lattice phase still drifts (a smooth residual ramp, mean minimal offset 0.025 s). The extraction then splits or merges lattice nodes and produces tris and holes: 40 faces, of which 12 are quads, where about 49 perfect quads were expected. In the paper the hierarchy and its Gauss-Seidel solver are what make the solve global. My voxel-cluster hierarchy is shallow: coarser than s/2 makes the minimal image ambiguous. The paper's extraction also has a cleanup stage I did not build.
- **The zero set has a hard wing edge thinner than the lattice.** Wing thickness is 0.03-0.08 at s = 0.035-0.07, so the top and bottom lattices of the wing interfere.
- **QuadriFlow, Blender's built-in, does not run headless.** It returned `CANCELLED` with "needs to be manifold and have face normals that point in a consistent direction" on:
  - the surface-nets mesh (64 non-manifold edges);
  - a voxel remesh (0 non-manifold edges and 0 non-manifold verts by bmesh, normals made consistent, loose geometry deleted, degenerates dissolved), with and without Newton projection.

  Run 2 hit the same refusal. I did not try the GUI.
- **Not done:** an anisotropic target edge length (finer where |k| is high). The position field uses one global s.

## 3-4. Shippable lowering, measured as run 2 did

There was no automatic cage worth lowering, so I lowered the best automatic output to show where it lands: the field-mode dense IM mesh after CC refit (`out/qm_dense_refit.obj`).
- 154 cage edges with dihedral over 50° were creased.
- Then Subdivision Surface (2 levels, applied) and a Newton snap onto f = 0.
- Seams at the program's part-label boundaries (body / wing / pods / fin from argmin of the part fields), at hard edges and at the mirror plane.
- Angle-based unwrap, averaged scale, pack.
- Bevel 1 segment at 30°, width 0.004, then Weighted Normal (face area, keep sharp).
- Script: `tools/lower.py`. Measured with run 2's `measure.py`, unchanged.

| | **L (run 4: SDF + IM cage)** | run 2 B (bmesh) | run 2 C (geonodes) | run 3 v6 (hand cage, interim, no RESULT yet) |
|---|---|---|---|---|
| Faces quads / tris / ngons | 6662 / 176 / 231 | 3039 / 49 / 215 | 3979 / 127 / 229 | 9395 / 210 / 182 |
| Poles per 1000 verts / valence ≥ 6 | **140.3 / 60** | 100.1 / 0 | 98.0 / 4 | 49.3 / n/a |
| Longest loop / closed loops ≥ 20 / share of edges in loops ≥ 20 | 124 (open) / 7 / 0.243 | 86 / 41 / 0.528 | 35 / 57 / 0.605 | 148 / n/a / 0.753 |
| Boundary edges / shells | **846 / 4 (holes)** | 0 / 4 | 0 / 4 | n/a / 1 |
| Exported tris / sliver fraction / slivers excluding bevel strips | 14236 / 17.6 % / 205 | 6914 / 31 % / 336 | 9022 / 28 % / 157 | 19558 / 25 % / 256 |
| Dihedral > 60° left | 751 | 83 | 77 | n/a |
| UV islands total / ≥ 1 % area / under 4 faces | **182 / 16 / 83** | 23 / 11 / 2 | 21 / 11 / 2 | 3 / 3 / n/a |
| UV area distortion (mean \|log2\|) / angle error | 0.189 / 0.74° | 0.113 / 1.04° | 0.118 / 1.14° | 0.631 / 0.97° |
| UV wasted | 51 % | 47 % | 61 % | n/a |
| Chamfer / F@2% / sil-IoU | 0.531 / 0.950 / 0.875 | 0.841 / 0.899 / 0.920 | 0.840 / 0.900 / 0.920 | 0.229 / 0.989 / 0.967 |

Against her bar, L fails every topology and UV criterion:
- holes and torn shards (visible in row 3 of the sheet);
- 140 poles per 1000 verts;
- 182 UV islands, 83 of them crumbs.

Its high quad share is only Catmull-Clark turning every face into quads; the poles and holes show the real topology. Its chamfer (0.531) beats run 2 because the SDF fit does. Silhouette does not. Run 3's interim hand cage beats everything here on every axis except the UV distortion figure.

The bevel and normals stack runs, but on this geometry the 154 creased cage edges include spurious ones from the wrong-shaped faces. That is why 751 edges over 60° are left.

## Contact sheets (run 2's layout)

- **`sheet-main.png`**. Rows: Tripo target, **SDF zero set (fitted program)**, L, run 2 B, run 2 C. Columns: 3/4 front, side, 3/4 rear, wireframe, UV layout.
- `sheet-closeup.png`. Columns: wing-edge and junction close-up, its wire, and the top wire. Same rows.
- Cross field: **`out/X.q34.png`** (best single view of the field), `out/X.top.png`, `out/X.close.png`; plain: `out/Xplain.*`.
- Per-row frames: `out/<Z|L>.v0-4.png` and `out/<Z|L>.w*.png`; `out/L.uv.png`; `out/L.metrics.json`; `out/L.score.txt`; `out/L.blend`.

## Sources relied on

All of these were used from my own knowledge of the papers and public formulas. Nothing was downloaded, and no third-party code was copied; every algorithm here was re-implemented in numpy. The licences are as I recall them; verify before relying on them.

- **Instant Meshes.** W. Jakob, M. Tarini, D. Panozzo, O. Sorkine-Hornung, "Instant Field-Aligned Meshes", ACM TOG 34(6), SIGGRAPH Asia 2015.
  - Used: the extrinsic orientation and position fields, random lattice initialisation, hierarchy, and extraction by edge-offset classification.
  - Reference code: github.com/wjakob/instant-meshes, BSD 3-clause.
- **QuadriFlow.** J. Huang, Y. Zhou, M. Niessner, J. R. Shewchuk, L. J. Guibas, "QuadriFlow: A Scalable and Robust Method for Quadrangulation", Computer Graphics Forum 37(5), SGP 2018.
  - Code: github.com/hjwdzh/QuadriFlow, BSD-style; built into Blender (GPL) as `object.quadriflow_remesh`. It was tested and refused headless.
- **N-RoSy power-vector representation.**
  - J. Palacios, E. Zhang, "Rotational Symmetry Field Design on Surfaces", SIGGRAPH 2007.
  - N. Ray, B. Vallet, W.-C. Li, B. Lévy, "N-Symmetry Direction Field Design", ACM TOG 2008.
  - F. Knöppel, K. Crane, U. Pinkall, P. Schröder, "Globally Optimal Direction Fields", SIGGRAPH 2013. That paper's global eigen-solve was not done; I used Jacobi.
- **Ridges.** Y. Ohtake, A. Belyaev, H.-P. Seidel, "Ridge-valley Lines on Meshes via Implicit Surface Fitting", SIGGRAPH 2004.
- **Not implemented, the named next step.** D. Bommes, H. Zimmer, L. Kobbelt, "Mixed-Integer Quadrangulation", SIGGRAPH 2009. Open implementation: libigl `igl::copyleft::comiso::miq` (libigl is MPL2; CoMISo is GPL, hence "copyleft").
- **Surface nets.** S. Gibson, "Constrained Elastic Surface Nets", MICCAI 1998.
- **Feature-preserving alternative, not used.** T. Ju, F. Losasso, S. Schaefer, J. Warren, "Dual Contouring of Hermite Data", SIGGRAPH 2002.
- **Subdivision.** E. Catmull, J. Clark, "Recursively generated B-spline surfaces on arbitrary topological meshes", CAD 1978.
- **SDF primitives and smooth-min.** Inigo Quilez, iquilezles.org articles "distfunctions", "smin" and "distfunctions2d" (sdPolygon). These are published formulas, re-implemented.

## What the next spike would need

1. **A global integer-grid parametrisation** instead of local Jacobi. The options are MIQ (libigl, MPL2 plus GPL CoMISo) or a faithful port of Instant Meshes' Gauss-Seidel hierarchy and its extraction cleanup (BSD). Either is open code we could own. The cross field from this spike (analytic curvature, ridges, exact crease) is the input it needs, and that part works.
2. **Feature-aware treatment of the hard wing edge.** Either give the program `k_edge > 0` and crease it later, or extract with dual contouring. A sub-lattice-thin wing also needs the parametrisation to treat top and bottom as separate charts cut at the crease.
3. **A seeded cage.** Run 3's evidence plus this one suggests the practical hybrid: a designed cage layout (run 3) whose vertex positions this spike's CC-to-field least-squares refit sets automatically. That keeps her topology and gets the field's fidelity. It is one small spike, and `tools/cc.py` and the `refit` in `tools/quad.py` / `tools/qf.py` are ready for it.
4. **A better-structured program.** Add a canopy, a root-thickened wing, and a nose that is not a station clamp, so the fit stops pressing on its bounds.

## Process notes

- Blender jobs ran one at a time behind a wait loop on other agents' Blender PIDs. There were three overlaps:
  - My first fit started before probe-subd-cage's job appeared.
  - A 3-second QuadriFlow retry ran while another agent's Blender (PID 58336) was up.
  - A numpy test via Blender's bundled python overlapped my own fit job; I killed that test (PID 40264).
- One job of mine (PID 55532) ran away to 14 GB, because it built a dense Catmull-Clark operator for a 27k-vertex mesh after QuadriFlow returned its input unchanged. I killed it within minutes. `qf.py` now refits only meshes under 2,500 vertices.
- No processes of mine are running. The operator GUI Blender (PID 36324) was never touched.
- Tools: `tools/` (common, sdf_quiet, fit, sn, qmesh, cc, quad, qf, lower, viz, score, chain.sh; measure/render/sheet copied from run 2). Logs: `out/*.log`.
