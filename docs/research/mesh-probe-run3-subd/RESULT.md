# Mesh probe run 3: Dexter Quiet as one Catmull-Clark body

Agent `probe-subd-cage-quiet`, session `self-2026-10-10-ag2`, 2026-10-11. Disposable scratch; no repo was edited.
Root: this directory (`...\scratchpad\mesh-probe\run3-subd\`). Blender 5.2.2, `--background` only, bundled numpy
and mathutils only. No downloads, no pip, no closed tools.

Serves brush-tree:ruling:representation-per-hull, :no-unownable-tools-in-loop and :shippable-part-bar.

## What I built

**One closed Catmull-Clark cage** (`tools/build.py`, about 330 lines), mirror-symmetric, fitted to the run-1
target (`run1/targets/dexter_main.obj`). It has three parts.

1. **Designed topology. This is the part no prior art automates.** It is a "pillow" of a top sheet and a
   bottom sheet, joined by a rim band two faces tall. Each sheet has:
   - A **spine strip** along the centreline, 2 x 16 quads.
   - **5 concentric rings** from the spine out to the outline. Their loops run parallel to the manta outline:
     beak side, leading edge, wing tip, trailing scallop, stinger.
   - **Spokes** (the radial edges) from the spine out to the outline. These carry the wing sweep into the
     body.

   The outline is 18 edges per half: beak 2, leading edge 8, tip 1, scallop 4, stinger 3. It comes from run
   1's planform numbers plus the scallop circle.

   The only poles in the cage are the 4 strip corners per sheet plus the inset corners. The rim band is
   creased 1.0 along the wing stretch only; the beak and stinger stay smooth.
2. **The fused mechanical sweep: a canopy frame.**
   - The region is chosen by topology, not by position: spine rows 11-15 plus rings 1-2 beside them.
   - It is inset twice, with creases of 0.5 and 0.6.
   - The frame loop is raised 6 mm after the fit.
   - It carries a 20x local shape regulariser, so the fit cannot crumple it.

   The belly keel and side lobes come out of the fit on the bottom sheet; I modelled no separate parts for
   them. I did not model the chin pods, dorsal vents, wing strakes or the tail nozzle (see "Where it falls
   short").
3. **Least-squares fit of cage positions.** This is my own, simpler version of the Marinov and Kobbelt
   approach:
   - The level-2 limit-surface vertices are linear in the cage, `X = S c`. I extract `S` exactly by probing
     Blender's Subdivision modifier with unit vectors, 2 s.
   - Each iteration: point-to-plane from the surface to the target, with a 0.15 point-to-point term; a
     coverage term from the target to the surface with normal-compatible correspondences; a fairness term
     ‖Lc‖²; and a shape term ‖L(c − c₀)‖² that keeps the designed layout.
   - The solve is in a mirror-reduced space: 843 unknowns for a 542-vertex cage. 30 iterations take about
     55 s.

**Lowering** (same script):
- Seams go on the cage: the rim's middle loop (top / bottom) and the canopy glass loop. The seam flags
  propagate through the subdivision.
- Apply subdivision at the ship level, then Minimum Stretch (SLIM) unwrap, average island scale, pack.
- Bevel, 1 segment, angle 30°, width 0.004, then Weighted Normal (face area, keep sharp). The stack is the
  same as run 2's B and C.

**Final variant `v7`:** ship level 2. `v7L1` is the same cage at ship level 1. `v7e` is the edit test.

## Contact sheets (orange squares = row number)

- **`sheet-main.png`**, the best one to judge at a glance. Rows: 1 Tripo target, 2 run 2's B (bmesh loft +
  boolean), 3 v7 (level 2), 4 v7L1 (level 1). Columns: 3/4 front, side, 3/4 rear, wireframe overlay, UV
  layout. The target has no UVs, so its tile is black.
- `sheet-closeup.png`: the wing edge and wing-body junction (shaded, then wireframe), then a top view with
  wireframe. Rows: T, B, v7, v7L1.
- **`sheet-cage.png`**: the cage I designed (orange) over its limit surface. Views: 3/4, top, side, bottom.
- `sheet-edit.png`: v7 against v7e (wider sweep plus longer beak). Columns: 3/4, top, top with cage, side.
- `sheet-under.png`: bottom and 3/4 front-high. Rows: T, v7.
- Per-variant frames are in `out/<name>.v0-6.png`, `.w0/.w2/.w4.png` and `.c0/.c1/.c2/.c5.png` (cage).
  Metrics are in `.metrics.json`, scores in `.score.txt`, build info in `.build.json` and the .blend files
  in `out/`.
- Renders use run 2's look. An earlier render pass shaded the live cage limit surface over the hull (it
  z-fought); that is fixed, and the sheets above are the clean re-renders.

## Measurements (same measure.py as run 2)

| | B (run 2) | **v7: subd, level 2** | v7L1: subd, level 1 |
|---|---|---|---|
| Faces: quads / tris / ngons | 3039 / 49 / 215 | 9297 / 196 / 180 | 2533 / 158 / 130 |
| Largest ngon | 11 (boolean seam) | 6 (bevel corners) | 6 |
| Shells | 4 | **1** | 1 |
| Poles per 1000 verts | 100.1 | **47.1** | 108.7 |
| Poles of valence 6 or more | 0 | 0 | 0 |
| Longest loop (edges) | 86, open | **148, closed** | 62 |
| Closed loops ≥ 20 edges | 41 | 30 | 3 |
| Share of edges in loops ≥ 20 | 0.528 | **0.755** | 0.417 |
| Exported triangles | 6914 | 19340 | **5624** |
| Sliver tris < 10° (share) | 31% | 24% | 33% |
| …excluding faces of bevel width | 336 | 254 | 340 |
| Dihedral > 60° / > 80° left after bevel | **83 / 7** | 546 / 316 | 352 / 223 |
| UV islands: total / ≥ 1% of area / crumbs | 23 / 11 / 2 | **3 / 3 / 0** | 3 / 3 / 0 |
| UV area distortion, mean \|log2\| | 0.113 | **0.076** | 0.078 |
| UV area outside 0.5-2x | 0.7% | 0.8% | 0.9% |
| UV angle error, mean | **1.04°** | 2.61° | 3.04° |
| UV space wasted | 47% | 59% | 60% |
| Chamfer % diag / F@2% / sil-IoU | 0.852 / 0.898 / 0.920 | **0.228 / 0.990 / 0.967** | 0.233 / 0.990 / 0.965 |

- **Scorer.** Run 1's `mp` binary was deleted, and rebuilding it means a cargo build against
  GameCult.Geometry.Csg. I ported `mp score` to numpy instead (`tools/score.py`, same sample counts, views
  and τ). It scores B at 0.852 / 0.898 / 0.920; `mp` gave 0.841 / 0.899 / 0.920. The B column above is
  rescored with the port, so the comparison is like for like.
- **Cage.** 542 vertices, 540 faces, 118 creased edges. The free parameters are 843 coordinates from 301
  half-cage vertices; the fitter owns those numbers.
- **What a designer touches.**
  - Topology knobs: L, K, the 5 outline segment counts, strip width and extent, canopy rows, rings and front.
  - Look knobs: wing crease, 2 canopy creases, 2 inset widths, frame height, bevel width and angle, ship level.
  - Fit weights: lam, lam_s, canopy_reg.

  That is about 20 numbers, plus the 25-point outline polyline.
- **Overfitting is real.** The first fit, v1, had weak regularisation. It scored chamfer **0.128** / IoU
  0.979 but tangled the canopy and rippled the wings (`out/v1.v0.png`). v7 trades about 0.1% chamfer for
  clean surfaces. Fidelity is cheap with this method; cleanliness is what costs.

## Against her bar

- **Topology flow: met, and better than B or C, on the body and wings.**
  - It is one shell; nothing is booleaned, so there is no boolean seam.
  - Loops run unbroken around the whole outline (closed loops of 148 edges).
  - Pole density is half of B's at level 2.
  - Missed in three places:
    - The concentric rings crowd into the narrow beak and stinger, because a ring cannot end without a pole.
    - The stinger's tall walls have only the two-face rim band, so they fold.
    - The thin wing edge is thinner than its band, so the band folds there too.
  - Those three account for most of the 316 edges over 80°. The breakdown is from `tools/dbg_edges.py`:
    stinger about 100, wing outline about 160, canopy about 36, beak and tip about 20. A bevel can't fix a
    fold of nearly 180°.
- **UVs: met.**
  - 3 islands: top (with the canopy frame), bottom, canopy glass. The parts stay together and there are no
    crumbs.
  - Area distortion 0.076 is better than B's.
  - Angle error is 2.6° against B's 1.0°. That is the SLIM trade-off: angle-based unwrap of the same seams
    gave area 0.63, which is unusable.
  - Packing is plain and wastes 59%.
- **Hard edges (one-segment bevel + face-weighted normals):** the stack is in place, but partly met.
  - The creased wing band comes out as a soft rounded edge with a highlight. It does not read as the crisp
    single-face bevel in her test render (closeup row 3).
  - Where the crease meets the folds, the bevel can't resolve the angle.
  - Her look needs a deliberate edge design: a band of chosen thickness with support loops, or a knife edge
    with the crease on the middle loop. I did not get there.
- **Triangle budget.** Level 2 exports 19.3k triangles, 2.8x B. Level 1 exports 5.6k, under B, at almost the
  same fidelity (0.233), but its flow metrics fall to B's level. A per-region level, or level 1 plus
  normal-map baking, is the real shipping question.

## Editability (v7 to v7e: wing sweep 0.06 plus beak 0.05)

- **The edit is 2 numbers.** Each is a smooth falloff field applied to the fitted cage.
- **It moves 315 of the 542 cage vertices.** No hand-dragging is needed.
- **The cage topology is identical, and the lowered topology stays stable:**
  - faces 9673 to 9686 (the angle-limited bevel picks up 13 more);
  - islands 3 to 3;
  - poles 456 to 452;
  - longest loop 148 to 202, because the stretched wing loop now crosses the loop-length cut-off differently.
- **Rerun cost.** About 60 s with the refit, then lowering. An edit-only rerun without the refit would take a
  few seconds; I did not time one separately.
- **The limit.** An edit is a deformation of fitted numbers. Moving a feature (a canopy further back, a new
  strake) is a topology edit: change knobs, rebuild and refit.

## What worked

- Exact `S` by probing the modifier (2 s, error 1.5e-7). It turns Blender's OpenSubdiv into an owned,
  linear fitting kernel, with creases included.
- Concentric pillow topology for a manta. One coherent body with no booleans, which B and C could not
  achieve.
- Selecting feature regions by topology index instead of by position. The position-picked canopy came out
  jagged and crumpled (v1-v4); the topology-picked one is clean (v5+).
- The shape regulariser ‖L(c − c₀)‖², weighted up locally on the mechanical feature. It keeps designed
  geometry designed while the rest of the cage fits.
- Seams authored on the cage propagate through the subdivision. Those seams plus SLIM give 3 clean islands.

## Where the cage design was hard

- **Concentric rings carry a constant loop count everywhere.** The wing tip gets about 9 cm spacing; the beak
  and stinger get 1-2 cm. A proper cage terminates rings (3-to-1 or 2-to-1 poles) where the body narrows,
  or uses a separate tail-boom tube. I tried neither.
- **Feature insets on a fitted surface.**
  - `bmesh.ops.inset_region` with even offset fired spikes off the crowded beak (v0 to v2).
  - Thin insets crumple under the fit unless they are regularised.
  - The canopy reads as a recessed slot with a crisp rear arc, not the target's raised bubble with a framed
    rim. Getting there needs a glass-crown height knob and support loops, and more iteration than I had.
- **Fidelity against fairness.** The target is Tripo output with lumpy panel detail. A coarse cage that
  chases it ripples. The fairness weights are the most consequential numbers in the file, and nobody
  designs them.
- **Mechanical detail at this scale** (pods, vents, strakes, nozzle) does not belong in this cage. It
  belongs in either support-loop sub-features (more cage design) or separate bevelled primitives and decals
  (the mixed-hull path from the prior-art doc). I did neither.
- **Pitfalls I hit:**
  - A Python late-binding closure bug.
  - Dense numpy matmuls in Blender's numpy were orders of magnitude slow. I worked around it with a sparse
    bincount assembly; I never checked whether the bundled numpy has an optimised BLAS.
  - Twice I started a job while another agent's Blender (PIDs 58156, 34064) was running. After that,
    `run.sh` waits for other Blender jobs.

## What a future brokkr-ctl command would have saved

- **`cage new --pillow --outline <poly> --spine L --rings K --segments …`.** Generates the concentric pillow
  cage with its index maps (spine, ring, spoke, rim), so regions are addressed by name. About 40% of my
  effort.
- **`cage region <name> --rows a..b --rings 1..k` plus `cage inset/crease/seam`.** Topology-addressed
  features, which never fold the way position-picked ones do.
- **`cage fit --target X --level 2 --fair λ --keep λs --lock <region>`.** The `S` probe, the sparse solve
  and the mirror reduction, with per-region locks. Iterations would drop from minutes of script surgery to
  one flag.
- **`cage terminate-ring` / `cage reroute`.** Pole-placing ring terminations, for the beak and stinger
  crowding. This is the operation I most needed and did not have.
- **`lower --level N --bevel … --uv slim --measure --score --sheet`.** Run 2 and run 3's measure, score,
  render and sheet scripts as one call, with the cage hidden in shaded renders by default.

## Verdict

**Can this path produce a hull she would ship? Yes, I think so, but this cage is not that hull yet.** Of the
three paths probed, subdivision is the first whose structure matches her bar:
- one continuous body;
- loops that follow the manta's curves;
- 3 part-coherent islands with low area stretch;
- and, from the same fit, fidelity 3.7x closer to the target than run 2's lowerings (chamfer 0.23 against
  0.85).

**What is missing is cage design**, which is exactly where prior art is silent:
- ring terminations at the beak and stinger;
- a deliberately designed wing edge, so her one-segment bevel reads crisp instead of folding;
- a canopy with crown and frame support loops;
- the pods, strakes and nozzle as support-loop features or separate bevelled parts.

Each is a known modeller's move. None is automated, and each needs her eye in the loop.

Confidence:
- **Moderate** that the representation can meet her bar.
- **Low** that an agent reaches her standard on this hull without the cage tooling listed above, or without
  her reviewing cage topology at the sheet level.

The renders were judged by my eye, not hers.

## Caveats

- **One hull, one target, one topology family.** I did not try a tube-plus-wing cage, a quad-remesher seed
  or ring terminations.
- **No retopology by a human** for comparison. Her studio scene, texture baking, decals and engine export
  were not tested.
- **Scores come from the numpy port** of `mp score`; it matches `mp` to within 0.011 on B.
- **Fit distances in `.build.json` are proxies**: level-2 vertex distances, not exact limit-surface
  closest points.
- **Processes.** No processes of mine are running. The operator's GUI Blender (PID 36324) was never touched.
  Nothing outside this scratch directory was written. `F:\Projects\Aetheria` and the brush-tree worktree
  were only read, and only the research docs.
- **Tools** (all in `tools/`):
  - `build.py`: cage, fit, edit, lowering. Use `CAGE_OVERRIDES` for knobs.
  - `run.sh build|post|render <name> [json]`: one Blender job at a time; waits for other Blender jobs.
  - `measure.py`, `render.py`, `sheet.py`, `desc.py`: copied from run 2. `render.py` gained bottom and
    front-high views, cage views, and the cage hidden in shaded renders.
  - `score.py`: the `mp` port.
  - `study.py`: target height fields and samples, written to `out/target.npz`.
  - `dbg_edges.py`: the location of the leftover hard edges.
