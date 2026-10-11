# Run 7: an Instant Meshes fork driven by the SDF (cross field, hard rim crease, per-vertex size)

Agent `spike-im-field-features`, session `self-2026-10-10-ag2`, 2026-10-11. Ruling `brush-tree:ruling:spike-instant-meshes-field-features`, bar `brush-tree:ruling:shippable-part-bar`. Scratch only; no repo touched; operator GUI Blender (PID 36324) untouched; all my processes ended.

## Verdict

1. **The diagnosis was wrong.** The ~0.49 % chamfer wall is not lattice size. It is how well run 4's SDF program fits the Tripo target.
   - Measured against the SDF itself, every Instant Meshes output, plain included, sits at 0.01-0.07 % chamfer and 0.99+ top silhouette IoU.
   - Scored against Tripo, every variant lands at 0.48-0.55 % whatever the field, constraints or density.
   - The program alone scores 0.520 (run 4). No remesher can beat that against Tripo.
2. **The real thin-feature defect was in the program.** Its fitted beak was a pinched neck (half-width 0.006) and an inverted station. That gave:
   - 119 non-manifold input edges;
   - ~300 extra orientation singularities (374 against 62);
   - every hole in the IM outputs (16-122 open edges).

   Reverting those two stations to run 2's description values (`in/params7.json`) leaves every output with 0 holes, 0 non-manifold edges and 1 shell.
3. **Hard rim crease (step 2) is what bought rim fidelity.** It works through position and orientation constraints on the exact crease plus Newton projection: at 8k quads the rim p95 error falls 10x, from 0.20 % to 0.02 % of the diagonal, and the rim renders crisp with a one-segment bevel. It needs the lattice finer than the rim wall (0.035-0.08 high). At 2k quads it only halves the error.
4. **The exact-Hessian cross field (step 1) buys alignment and costs poles.** Median misalignment to the principal directions drops from 13° to 3.4°, but poles rise from 31 to 52 per 1000 v.
5. **The size field (1b) made topology worse.** The isotropic per-vertex scale cost 3-4x poles and up to 1074 open edges for no fidelity gain at equal density. Anisotropic scale is too deep to patch (see 1b).
6. **Step 3 was not run.** Fidelity at the rim was already met, and the wing joins the body through a smooth blend (k_wing 0.12), not a crease, so there is no curve to stitch along.
7. **Her bar is half met.**
   - **Met:** watertight, 1 shell, pure-quad base, crisp beveled rim with face-weighted normals.
   - **Not met:**
     - Flow: loops are not designed, none closes, and poles are 50-69 per 1000 v against v7's 47.
     - UVs: 10 islands with no crumbs, but area distortion of 0.67-0.76 against v7's 0.076. The automatic seams join wing top and bottom wherever the snapped rim has gaps.
   - Automated remeshing of an SDF composition is now a fidelity solution, not yet a topology-and-UV solution.

## The fork

`C:\Tools\instant-meshes-fork` is a copy of `instant-meshes-src` at 7b31608, built out of tree in `C:\Tools\instant-meshes-fork-build` with `/m:4`. Patch: `instant-meshes-field.patch` (100 lines added, 10 removed, plus run 6's glfw CMP0042 line).
- `--field <file>`: a text file of records `x y z  qx qy qz qw  ox oy oz ow  s`.
  - Each solver vertex takes the nearest record through a uniform-grid lookup, so subdivision does not break indexing.
  - q and qw feed `CQ/CQw`. o and ow feed `CO/COw`, the same constraint path `-b` uses. Then `propagateConstraints`.
  - `s > 0` gives a per-vertex target edge length.
- Per-vertex scale: `MultiResolutionHierarchy::mS`, one vector per level, built from `toUpper` averages.
  - `optimize_positions_impl` uses the edge scale s_ij = (s_i + s_j)/2 in the compat functor and s_i in the rounding.
  - `extract_graph` uses s_ij for its edge classification and s_i for its cluster weights.
  - The degenerate-triangle cleanup uses min(s).
- Upstream bug fixed: `propagateConstraints` projected `cq - v` where it meant `co - v` (`hierarchy.cpp`).
- Runtime is 2.4-5 s per run.

## Inputs

`tools/prep.py` and `prep2.py` produce them:
- Surface nets at h 0.005, Newton-projected: 68k vertices for the repaired program, 71k for the fitted one.
- The field is run 4's: exact-Hessian principal directions, anisotropy confidence, Ohtake ridges, and the program's crease.
- New in `tools/feat.py`: the exact crease. Gauss-Newton on {slab = 0, planform = 0}, kept where the wing is the active surface.

Field variants:
- **field2:** curvature weight 0.5·cw where cw > 0.3, else free; ridges 0.5; crease 1.
- **creaseonly:** constraints only on the rim (2,865 vertices, orientation along the crease and position on it).
- **crease2:** field2 plus the rim constraints.

Post-process (`tools/post.py`): output vertices within 0.35·s of the crease are snapped onto the exact crease, and the rest are Newton-projected onto f = 0 (the `_p` meshes).

## Measurements

All rows below are on the repaired program, flags `-d -r 4 -p 4 -c 40 -S 2`; `out/post3.log`.

Fidelity is in % of the bbox diagonal:
- "SDF ch." is chamfer against the dense SDF zero set.
- "rim p95" is the 95th-percentile distance from 2,202 exact crease samples to the mesh, raw then projected.
- "top IoU" is the top-view silhouette against the SDF.
- Tripo is run 4's scorer.

| mesh (IM -f) | quads | poles/1000v | open/nonmanifold | misalign to principal dir, med / p90 | rim edge misalign med / p90 | SDF ch. raw → proj | rim p95 raw → proj | top IoU proj | Tripo ch. / sil |
|---|---|---|---|---|---|---|---|---|---|
| plain f500 | 2020 | 51.4 | 0/0 | 14.5° / 35.9° | 2.9° / 9.1° | 0.046 → 0.033 | 0.644 → 0.541 | 0.9962 | 0.547 / 0.905 |
| field2 f500 | 2010 | 79.0 | 0/0 | 4.9° / 21.3° | 2.4° / 6.7° | 0.043 → 0.031 | 0.552 → 0.513 | 0.9967 | 0.547 / 0.903 |
| creaseonly f500 | 2038 | 67.2 | 0/0 | 17.3° / 37.0° | 2.3° / 6.4° | 0.036 → 0.030 | 0.334 → 0.151 | 0.9961 | 0.545 / 0.904 |
| crease2 f500 | 2086 | 92.4 | 0/0 | 4.9° / 25.0° | 2.0° / 7.2° | 0.038 → 0.030 | 0.459 → 0.302 | 0.9966 | 0.546 / 0.904 |
| plain f2000 | 7978 | **30.7** | 0/0 | 13.2° / 34.7° | 2.2° / 6.2° | 0.011 → 0.008 | 0.257 → 0.202 | 0.9990 | 0.555 / 0.902 |
| field2 f2000 | 8132 | 51.5 | 0/0 | **3.4° / 16.1°** | 2.1° / 5.3° | 0.011 → 0.008 | 0.274 → 0.201 | 0.9991 | 0.554 / 0.903 |
| creaseonly f2000 | 8052 | 41.1 | 0/0 | 15.6° / 37.6° | 1.2° / 4.1° | 0.010 → 0.008 | 0.123 → **0.020** | 0.9990 | 0.554 / 0.903 |
| crease2 f2000 | 8242 | 57.6 | 0/0 | 3.7° / 15.9° | **1.1° / 4.0°** | 0.010 → 0.008 | 0.161 → 0.045 | 0.9991 | 0.553 / 0.904 |

### On the fitted program (beak defect present; `out/post1.log`, `post2.log`)

The same pattern holds, plus holes:
- plain f2000: 39.8 poles, 70 open edges, rim p95 0.262 after projection.
- creaseonly f2000: 48.3 poles, rim p95 0.023.

The open edges sit mostly on the body at the beak, for example 57 body / 28 wing / 12 pods.

### Step 1b, size field

Per vertex, s = min(0.35/|kmax|, inscribed radius, s0), clamped to [0.3, 1]·s0, with 0.6·s0 on the crease and a gradation limit of 0.3·|edge| (`fieldS`, `creaseS`). Fitted program:

| mesh | quads | poles/1000v | open edges | SDF ch. proj | rim p95 proj |
|---|---|---|---|---|---|
| fieldS f500 | 13009 | 115.2 | 134 | 0.010 | 0.235 |
| creaseS f500 | 13229 | 120.7 | 178 | 0.010 | **0.014** |
| plain f3300 (equal density) | 13024 | **33.7** | 104 | 0.010 | 0.198 |
| creaseS f2000 | 26381 | 121.6 | **1074** | 0.009 | 0.214 |
| creaseG f2000 (gentle: ≥ 0.6·s0, gradation 0.15) | 15203 | 78.6 | 250 | 0.009 | 0.006 |

- Why the size field fails: grading the lattice spacing breaks the integer-offset consistency between neighbours, which shows up as poles and holes. Fidelity at equal density is unchanged.
- Thickness never limits the wing body: it is 0.035-0.08 thick against s = 0.025 at 8k quads. The only sub-lattice thing on the wing is the rim wall at 2k quads, and the crease constraint already handles it at 8k.
- Anisotropic scale was not attempted, because the patch would have to go deep:
  - The functions are `position_round_3/4`, `position_floor_3/4`, `compat_position_{extrinsic,intrinsic}_{3,4}` and their `_index` variants (field.cpp ~290-610), `optimize_positions_impl`, `extract_graph`'s classify_edges, and `extract_faces`' scale thresholds.
  - Every one rounds q and n×q by a single scale.
  - A (s_u, s_v) pair must also swap when the 4-RoSy matching rotates q by 90°, but `compat_orientation_*` returns rotated vectors, not the rotation index. So the pair cannot follow without changing that interface across the solver and the extractor.
  - The anisotropic follow-up for that is Panozzo et al. 2014 frame fields with a non-orthogonal parametrisation. That is a different solver, not a patch.

### Lowered and measured as run 2 did

`tools/lower7.py` is run 4's `lower.py` with these changes:
- no Catmull-Clark and no re-projection;
- holes filled (none left on the repaired program);
- seams at part-label boundaries, where the labels are majority-smoothed and split at the mirror;
- seams on edges over 60° and on the exact crease.

It keeps the one-segment bevel at 30° with width 0.004, then Weighted Normal by face area. Measured with run 4's `measure.py`; Tripo score from `score.py`; `out/chain7n.log`, `chain7m.log`.

| | L7nplain (plain f2000, unprojected) | **L7ncreaseM (creaseonly f2000)** | L7nfieldM (crease2 f2000) | L7nfield500M (crease2 f500) | run 3 v7 (designed cage) | run 6 plain IM f2000 raw |
|---|---|---|---|---|---|---|
| faces q/t/n, max ngon | 8382/89/150, 6 | 8468/97/155, 6 | 8635/114/178, 6 | 2311/82/116, 6 | 9297/196/180, 6 | 8027/0/0 |
| shells / open edges | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 50 |
| poles/1000v / valence ≥ 6 | **38.4** / 0 | 50.2 / 4 | 69.0 / 5 | 114.1 / 7 | 47.1 / 0 | 36.8 |
| longest loop / closed ≥ 20 / share in loops ≥ 20 | 253 open / 2 / **0.764** | 274 open / 1 / 0.707 | 105 open / 1 / 0.593 | 94 open / 0 / 0.363 | 148 closed / 30 / 0.755 | 284 open / 0 |
| exported sliver share / excluding bevel strips | 0.1 % / 0 | 1.8 % / 0 | 6.9 % / 1 | 15.7 % / 2 | 24 % / 254 | n/a |
| dihedral > 60° / > 80° left | 28 / 9 | 16 / 3 | 11 / 4 | 22 / 4 | 546 / 316 | n/a |
| UV islands / ≥ 1 % / crumbs | 11 / 6 / 1 | 10 / 6 / 0 | 10 / 6 / 0 | 11 / 6 / 1 | 3 / 3 / 0 | n/a |
| UV area distortion mean \|log2\| / outside 0.5-2x | 1.074 / 25 % | 0.764 / 21 % | 0.668 / 17 % | 0.473 / 7 % | **0.076 / 0.8 %** | n/a |
| UV angle error / wasted | 2.07° / 67 % | 1.50° / 60 % | 1.88° / 70 % | 2.91° / 63 % | 2.61° / 59 % | n/a |
| Tripo chamfer / F@2% / sil | 0.552 / 0.950 / 0.907 | 0.553 / 0.950 / 0.905 | 0.552 / 0.951 / 0.904 | 0.546 / 0.953 / 0.904 | **0.228 / 0.990 / 0.967** | 0.498 / 0.954 / 0.900 |

- **The rim is the visible win.** In L7nplain, IM rounds the rim off the surface-nets staircase. Few edges pass 30°, so almost nothing is beveled, and it shades faceted (sheet row 5). The crease rows (6-8) have a straight, crisp beveled rim that shades clean with face-weighted normals. The rim wall is 1-2 quads high, with some poles on it.
- **Topology.** Pure-quad bases, watertight, near-zero slivers outside the bevel strips.
- **Flow is generic field flow.** Loops are long but open and not designed.
- **The cross field's poles survive lowering.** L7nfieldM has 69 poles per 1000 v against 50 for crease-only and 38 for plain.
- **UVs are the clear failure.**
  - The part-label, mirror and hard-edge seams leave each wing half as one chart, top and bottom joined through gaps in the snapped crease: only ~300 of the rim vertices land on the exact crease.
  - Area distortion is 6-10x v7's. A cut along the exact crease did not change the seams.
  - Fixing this needs either IM vertices placed on the whole crease (so it becomes a closed seam loop) or a distortion-driven seam method. Examples: OptCuts (Li, Kaufman, Kim, Sorkine-Hornung 2018) or Autocuts (Poranne et al. 2017); neither was tried.
- **Tripo fidelity of every lowered row is the program's.** The 0.55 is the repaired beak; it was 0.51 with the fitted beak. v7 wins on Tripo because its cage was fitted to Tripo, not to this SDF.

## What each step bought

| step | bought | cost | where it broke |
|---|---|---|---|
| 1 cross field (field2) | misalignment 13° → 3.4° median; rim edges 2.2° → 1.1° | poles +68 % (31 → 52 per 1000 v); singularities 62 → 120 | no fidelity gain. The unfiltered field (`field`, every vertex weighted) doubled poles. |
| 1b size field | nothing at equal density | poles 3-4x, holes | integer lattice offsets break under spacing gradients |
| 2 rim crease + projection | rim p95 0.20 → 0.02 % at 8k quads; crisp bevelable rim | poles +34 % (31 → 41) | below s ≈ rim wall height (2k quads) it only halves the error. Snapped coverage of the crease is partial (~300 vertices). |
| beak repair (program fix) | 0 holes, 0 non-manifold edges, singularities 374 → 62 | Tripo chamfer +0.05 | degenerate primitives in the program are the real "thin feature" hazard |
| 3 wing as own patch | not run | | no crease between wing and body to stitch along (smooth blend). Fidelity was already met. |

**Next, if pursued:**
1. Make the crease constraint cover the whole curve, so the rim becomes a closed seam loop. Seed lattice vertices along the curve at s spacing as hard COw rather than nearest-vertex hints.
2. Add a validator that rejects degenerate SDF primitives: inverted or near-zero stations.
3. Use a seam method for UVs.
4. To get designed flow, refit run 3's designed cage to the SDF (run 4's refit) rather than an IM field. On this evidence that is still the only path to closed loops and v7-class UVs.

## Files

Root `...\scratchpad\mesh-probe\run7-im-field\`.
- **Sheets:** `sheet-main.png` and `sheet-closeup.png`.
  - Main sheet columns: 3/4 front, side, 3/4 rear, wire, UV.
  - Close-up columns: rim close-up, rim wire, top wire.
  - Rows (in both): 1 Tripo target, 2 SDF zero set (repaired), 3 run 3 v7, 4 run 6 plain IM f2000, 5 L7nplain, 6 L7ncreaseM, 7 L7nfieldM, 8 L7nfield500M.
- **Patch:** `instant-meshes-field.patch`.
- **Tools** (`tools/`):
  - `prep.py`, `prep2.py`, `feat.py`, `post.py`, `lower7.py`;
  - `runim.sh`, `chain7.sh`, `bl.sh` (wait-first Blender wrapper), `build.sh`.
- **Logs:** `out/*.log`; `post1-3.log` hold the per-mesh JSON.
- **Meshes and renders:**
  - `out/<variant>.obj` and the projected `_p.obj`/`.stl`;
  - `out/L7*.blend`, `.metrics.json`, `.score.txt` and renders.
- **Inputs:** `in/`, for the repaired program (`params7.json`); `in_fit/` holds the fitted-program inputs.
