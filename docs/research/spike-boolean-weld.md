# Spike: boolean cut and split on the Dexter Quiet hull, welded by the operator's rule

Campaign brush-tree, target r3 (invariants weld-rule, detail-is-boolean, two-layers, shippable-stack). Serves rulings
`boolean-cleanup-tighter-curve-wins` and `panel-lines-by-split-boolean-r2`. Plan: Imagination's `spike-boolean-weld.md`.
Agent `spike-bt-boolean-weld`, 2026-10-12. A spike, not a cut: the code under `spikes/boolean-weld/` is scratch.

Her words, the spec of the rule: "the surface with the tighter curve defines the silhouette of the cut, and the spare
vertices that come from the flatter surface all get merged away."

## Round 2: ruling weld-owner-defines-silhouette

The operator answered round 1's question (ruling `weld-owner-defines-silhouette`, superseding
`boolean-cleanup-tighter-curve-wins`):

> "When i cut a panel line with a flat cutter, it's the hull's vertices that define the silhouette, so they survive,
> this is what the tighter curve rule is for. When I cut a small thing out of a bigger thing like your first example
> (which looks like a sphere cutting into a flat surface to make a dimple), the bigger thing is contributing fewer
> (none, in your example) vertices to the silhouette, so its vertices get merged away"

Implemented in `spikes/boolean-weld/py/owner_weld.py`, run by `py/run2.py`, with boolmesh output (Manifold's is
identical, round 1).

- **Owner:** curvature along the loop.
- **Spare vertices merged:**
  - `loop`: a loop vertex made only by the yielding side's edges merges into the nearest owner-made loop vertex.
  - `ring`: where the cutter owns, hull vertices one ring off the loop merge onto it.
  - `snap`: where the hull owns, a loop vertex the boolean inserted on a hull edge, within SNAP local edge lengths
    of an existing hull vertex, merges into that hull vertex. This is Self's specification: the hull vertex survives
    and the loop goes through it.
- **Splits:** both pieces are welded jointly, and every operation must pass both pieces' guards or it is refused.
  In the piece that lacks the surviving hull vertex, the loop vertex moves to it.
- **Guard thresholds:** worst angle 10 and 5 deg, both reported; SNAP 0.25 and 0.5 h.
- **New probe:** a vertical cylinder of r 0.03, 16 and 48 segments, cut through the wing-rim crease (a notch).

Full tables: `spikes/boolean-weld/results/round2/table2-*.md`. Tags: `a10s25` = 10 deg and SNAP 0.25 h; `a5s50` =
5 deg and SNAP 0.5 h; `r*` = the reverse snap direction.

### Answer, per case family

- **Small curved cutter in a larger surface (gun ports, dimple probes): the rule works.** The cutter owns the loop
  and the hull's spare vertices merge away.
  - Port, 16 segments, at 10 deg: slivers 32 to 5, worst angle 0.007 to 5.09 deg, p5 1.14 to 6.68 deg, silhouette
    unchanged (0.0198 %), 0 flips, 0 vertices moved outside the band. Edges under the bevel width touching the loop
    drop from 6 to 0. The 5 deg guard gives the same numbers.
  - At 48 segments the hull-side fans to the dense cutter remain: slivers 227 to 211 (10 deg) or 207 (5 deg). The
    cutter's tessellation should stay near the hull's density.
- **Flat cutter splitting the hull (panel line): the rule as specified does not fix the seam, and it bends it.**
  - At 10 deg and 0.25 h, both pieces accepted 16 of 78 snaps; 35 were refused on angle, 25 on flips and 2 on the
    link condition.
  - Slivers 97 to 85 on the subtract piece and 92 to 82 on the intersect piece.
  - The worst angle is unchanged: 0.058 deg and 0.056 deg.
  - Seam crack 0. The joint guard holds, so both pieces' loops stay identical.
  - At 5 deg / 0.25 h: 22 snaps applied, slivers 83 / 79. At 5 deg / 0.5 h: 54 applied, slivers 71 / 64.
  - Where they are: hull-side slivers barely move (37 to 35 and 32 to 32). The worst angle and most slivers (61 per
    piece) are in the planar cap's triangulation, which no vertex merge reaches.
  - The cost: the seam leaves the cutter's plane, by up to 0.40 % of the diagonal (0.23 h) at 0.25 h and 0.95 %
    (0.56 h) at 0.5 h. After Bevel and Weighted Normal this shows as visible kinks and a step in the panel line
    (`r2_splitclose.jpg`). The naive seam stays straight apart from one bright sliver highlight. Her Longinus seams
    are straight bevelled grooves (`r2_longinus_vs_split.jpg`).
  - The reverse direction does no better. Sliding the hull vertex onto the loop keeps the seam on the plane, but the
    guards refuse nearly all of it (1 of 78 applied at 10 deg / 0.25 h; 11 of 156 at 5 deg / 0.5 h), and it moves
    hull vertices up to 0.38 h off the hull surface.
- **Equal curvature, saddle, ownership switch: the rule cleans up but does not reach the needles.**
  - Slivers: equal-k 87 to 35 (10 deg) or 31 (5 deg); saddle 50 to 25 or 26; switch 112 to 54 or 53.
  - Worst angle: the 1e-6 to 3e-3 deg needles survive at 10 deg. At 5 deg equal-k reaches 0.71 deg.
  - The hull-owned stretches now snap, so the loop moves where ownership flips to the hull: equal-k 0.056 to 0.098 %
    (0.13 h), switch 0.013 to 0.32 % (0.16 h).
  - The saddle's 1 "flipped" near-vertical sliver remains at 10 deg and is gone at 5 deg.
- **Crease: the rule works.**
  - Curved cutter (the notch): the cutter owns the arc and the hull owns at the 2 crease crossings (6 of 41 loop
    vertices at 16 segments, 4 and 6 owner switches). Both crease vertices survive, no collapse uses a crease vertex
    as its source, and the hull's crease bevel weights are untouched (144 weighted edges before and after).
  - Notch results at 10 deg: 16 segments, slivers 27 to 8, worst angle 0.21 to 3.91 deg (4.31 at 5 deg), edges under
    the bevel width 4 to 0, silhouette 0.043 to 0.061 %; 48 segments, slivers 64 to 27, worst angle 0.10 to 0.79 deg.
  - Box across the crease: like the panel split, 40 of 44 slivers remain, the worst angle is unchanged, the seam
    crack is 0 and the seam moves 0.26 h.

### Renders, round 2

![Longinus vs split](spike-boolean-weld/r2_longinus_vs_split.jpg)
![split seam close](spike-boolean-weld/r2_splitclose.jpg)
![split](spike-boolean-weld/r2_split2.jpg)
![notch 16](spike-boolean-weld/r2_creasecyl16.jpg)
![notch 48](spike-boolean-weld/r2_creasecyl48.jpg)
![notch side](spike-boolean-weld/r2_creasecylside.jpg)

### Questions for Self (round 2, text only)

1. On a panel split, the snap makes the hull's vertices the seam's path as well as its silhouette, and the seam
   kinks. Should the hull vertices survive while the seam stays on the cutter's plane? If so, the seam's cleanup is
   not a vertex merge but a retriangulation of the cap and of the hull faces next to the loop. That is untested;
   both pieces would get the same loop, so no crack.
2. The cap's triangulation holds the worst angle and most slivers of every planar split, and the cap is kept for the
   bevel. Is the cap ours to remesh? It is interior, planar and invisible except through the Bevel and Weighted
   Normal it feeds.
3. Angle bar: 5 deg lets more merges through (split 22 vs 16 at 0.25 h; equal-k worst angle 0.71 vs 1.7e-6) and
   never produced a flip. 10 deg is safer on the saddle. Both are reported; Self decides.

## Round 1

### Answer

- **As the plan wrote it (owner by curvature across the loop, `u = n x t`), the rule fails on the gun port.** A
  cylinder has zero curvature across its own cut loop (that direction is its axis), so the hull owns 34 of 36 loop
  vertices and the weld merges away the cylinder's circle samples. The port's silhouette error doubles (max 0.0198 %
  to 0.045 % of the diagonal) and the worst angle does not improve (0.007 deg).
- **Measured along the loop (`k = II(t, t)` on each surface), the rule works for the gun port.** The cylinder owns
  every loop vertex, the 10 hull-made loop vertices merge onto it, and none is refused. Slivers in the band drop from 32 to 5. The minimum
  angle goes from 0.007 to 5.1 deg and the 5th percentile from 1.1 to 6.7 deg. The silhouette is unchanged, nothing
  flips and no vertex moves outside the band. Edges shorter than the bevel width touching the loop drop from 6 to 0,
  so the shipped Bevel's clamp no longer chokes the seam: the render shows a continuous bevel highlight where the
  naive cut has almost none. This reading, the curvature that bends the cut curve, matches her sentence ("defines
  the silhouette of the cut"). That is inference, and a question for Self below.
- **For the panel split the rule is a no-op.** A planar cutter contributes no loop vertices, since every one of the
  124 loop vertices is a hull edge crossing the plane. The hull owns all of them in every direction mode, and nothing
  merges. The 97 slivers in the band (37 hull-side, 60 in the cap; worst angle 0.058 deg) are the owner's own, and
  her rule does not speak to them.
- **Kernel: boolmesh 0.2.1.** It gives the same output as Manifold to the bit (identical vertex sets and triangle
  counts on every case), builds as pure Rust in 14 s on Windows, and carries provenance as a per-corner value.
  Manifold (manifold-csg 0.4.1 over Manifold v3.5.3) builds in 89 s on Linux and fetches upstream C++ source at
  build time.

### Inputs

- Hull: `Dexter Quiet Cage` re-exported from a copy of Ships.blend with Bevel and Weighted Normal off (Mirror, then
  Subsurf level 3 with limit surface): 3,010 vertices, 6,016 triangles, 0 non-manifold edges, 0 misoriented, Euler 2
  (watertight, genus 0), diagonal 1.4584, mean edge 0.0256 (p5 0.0067, p95 0.048). The 144 evaluated crease edges
  equal the cage's bevel-weight edges (midpoint match 8e-8). Fixtures: `spikes/boolean-weld/fixtures/`.
  `cage_eval.obj` (3,154 vertices, Bevel baked in) was not used.
- Curvature: a per-vertex quadric fit over the 2-ring of the evaluated mesh, giving a 3x3 second fundamental form;
  sign positive for convex. This is not the limit-surface `X = S c` (S not extracted). Hull crease edges count as
  infinite curvature, so the hull always owns there. Cutter curvature is analytic: cylinder `e_theta e_theta^T / r`,
  box faces 0.
- Cutters (`cases.py`). Gun port: cylinder r 0.015 on the upper flank at (0.17, 0.0), axis on the face normal,
  sunk 0.02, 16 and 48 segments. Split: box over y > 0.22, a transverse break round the forward body; both pieces
  kept. Probes:
  - equal-k: cylinder r 0.0199 = 1/|k|max at hull vertex 1799.
  - saddle: cylinder r 0.015 at vertex 538, k1 = -7.0, k2 = 55.2. The hull is 0.0143 thick there, so the port is sunk
    0.0086, not 0.02.
  - crease: box x > 0.33, a chordwise split across the wing-rim crease.
  - switch: cylinder r 0.08 across the dorsal ridge.
  - True-curve reference: the same cylinder at 1,024 segments. For planes the boolean loop is exact.

### Weld pass (`py/weld.py`)

1. Loop = edges between a hull-provenance face and a cutter-provenance face, traced into cycles. Neither kernel
   returns the loop or each loop vertex's source edge, so origin is a geometric test: whether the vertex lies on an
   original hull edge (H), a cutter edge (C) or both (1.5e-6 tolerance).
2. Owner per loop vertex = larger |k|, ties to the hull. The direction modes are `across` (the plan), `along` and
   `mean`.
3. Collapses: a loop vertex of yielding-side origin merges into the nearest owner-origin loop vertex along the loop.
   The `literal` scope also merges the yielding surface's one-ring onto the loop; `looponly` does not.
4. Guard: refuse a collapse on a face flip (old·new normal <= 0), on a worst angle below 10 deg when it got worse,
   on a missing edge, or on a failed link condition. Refusals are counted, never forced.
5. Split: collapses from the subtract piece are replayed by position on the intersect piece.
6. Candidate change tested (`-snap`), not her rule: the owner's own vertices within 0.25 local edge lengths of a loop
   vertex, and loop edges shorter than the 0.001 bevel width, also collapse, with the same guard.

### Measures (boolmesh; Manifold's numbers are identical)

Band = triangles whose centroid is within 2 local edge lengths of the loop. Sliver = longest edge squared over twice
the area > 10, or area < 1e-4 of the mean. Dev = welded loop polyline to the true intersection curve, in % of the
diagonal and in local edge lengths h. Out = hull vertices moved outside the band.

| case | variant | collapses | band tris | slivers | min deg | p5 deg | flips | dev max % | dev max /h | out |
|---|---|---|---|---|---|---|---|---|---|---|
| port s16 | naive | | 157 | 32 | 0.007 | 1.14 | 0 | 0.0198 | 0.0096 | 0 |
| port s16 | across (plan) | 12 | 133 | 12 | 0.007 | 2.83 | 0 | 0.045 | 0.022 | 0 |
| port s16 | **along** | 10 | 137 | **5** | **5.09** | **6.68** | 0 | 0.0198 | 0.0096 | 0 |
| port s48 | naive | | 339 | 227 | 0.016 | 0.92 | 0 | 0.0023 | 0.0011 | 0 |
| port s48 | across | 19 | 301 | 173 | 0.016 | 1.47 | 0 | 0.0064 | 0.0031 | 0 |
| port s48 | along | 8 | 323 | 211 | 0.47 | 1.57 | 0 | 0.0023 | 0.0011 | 0 |
| port s48 | along-snap | 40 | 259 | 119 | 0.93 | 2.25 | 0 | 0.0055 | 0.0027 | 0 |
| split sub | naive = every rule variant | 0 | 507 | 97 | 0.058 | 1.46 | 0 | 0 | 0 | 0 |
| split sub | along-snap | 7 | 496 | 85 | 0.058 | 2.07 | 0 | 0.0087 | 0.0051 | 0 |
| equal-k s16 | naive | | 457 | 87 | 1.5e-6 | 1.65 | 0 | 0.056 | 0.072 | 0 |
| equal-k s16 | along | 38 | 359 | 38 | 1.7e-6 | 3.67 | 0 | 0.055 | 0.073 | 0 |
| equal-k s48 | along | 53 | 506 | 73 | 0.157 | 2.98 | 0 | 0.0064 | 0.0082 | 0 |
| saddle s16 | naive | | 209 | 50 | 2.8e-6 | 0.61 | 0 | 0.094 | 0.067 | 0 |
| saddle s16 | along | 21 | 167 | 25 | 0.003 | 0.94 | **1** | 0.094 | 0.067 | 0 |
| saddle s48 | along | 28 | 309 | 83 | 0.003 | 0.85 | 0 | 0.012 | 0.0088 | 0 |
| crease sub | naive = every rule variant | 0 | 342 | 44 | 0.033 | 2.41 | 0 | 0 | 0 | 0 |
| switch s48 | naive | | 488 | 112 | 1.2e-6 | 0.62 | 0 | 0.0128 | 0.0062 | 0 |
| switch s48 | along | 48 | 392 | 57 | 1.2e-6 | 2.12 | 0 | 0.0196 | 0.0095 | 0 |

The full table (every variant, both kernels' rows, refusal counts) is in `spikes/boolean-weld/results/`.

Ownership per mode, as owner counts (hull / cutter) and owner switches per loop:

| case | across | along | mean |
|---|---|---|---|
| port s16 | 34 / 2, 4 switches | 0 / 36, 0 | 0 / 36, 0 |
| split | 124 / 0, 0 | 124 / 0, 0 | 124 / 0, 0 |
| equal-k s16 | 50 / 41, 10 | 21 / 70, 8 (11 within 10 % of a tie) | 16 / 75, 2 |
| equal-k s48 | 82 / 54, 10 | 24 / 112, 6 (15 near-tie) | 21 / 115, 2 |
| saddle s16 | 36 / 21, 18 | 9 / 48, 14 | 13 / 44, 10 |
| switch s48 | 79 / 53, 12 | 24 / 108, 4 | 22 / 110, 4 |

Shortest edge touching the loop, which bounds the bevel through Bevel's overlap clamp; the count is edges under the
0.001 bevel width:

| case | naive | across | along |
|---|---|---|---|
| port s16 | 5.3e-5 (6) | 5.3e-4 (4) | 2.3e-3 (0) |
| port s48 | 5.6e-5 (52) | 5.6e-5 (32) | 2.2e-4 (40) |
| saddle s16 | 1.4e-6 (19) | 1.4e-6 (3) | 1.4e-6 (9) |
| split | 2.6e-4 (15) | unchanged | unchanged |

### Per case

1. **Gun port, 16 segments.** With `along` the rule passes, apart from a 5.1 deg worst angle against a 10 deg guard.
   With `across` it fails (see Answer).
2. **Gun port, 48 segments (probe 5).** The rule keeps the cutter's dense samples, which is the right silhouette, but
   leaves 86 hull-side fans: hull vertices about 0.025 away fanned to cutter samples 0.002 apart. Another 125
   "slivers" are the cylinder's own wall quads, 0.05 tall by 0.002 wide, which are inherent to the cutter's
   tessellation and not caused by the boolean. The 16-segment cutter (spacing 0.0059, about 0.23 h) welds clean; at
   48 (about 0.08 h) only the snap variant helps much. The rule needs the cutter's spacing no finer than about a
   quarter of the hull's local edge length; finer than that, fans remain that no merge can remove.
3. **Panel split.** No-op, as above. The two pieces' loops coincide vertex for vertex (gap 0). Caps: with both caps
   kept, the bevelled seam reads as a panel line. With both caps dropped, nothing shows, because Bevel on an open
   boundary edge makes no seam. So the caps must stay for her panel-line method. The capped render shows a light
   streak partway along the seam, at the cap's sliver triangles (cutter side, worst 0.058 deg). Replaying the snap
   variant's collapses onto the second piece split the loops apart: the second piece refused 2 and could not match 1
   by position, opening a 6.8e-4 gap, a crack in the panel. A split's collapses must be accepted by both pieces'
   guards or by neither.
4. **Equal curvature (probe 1).** Ownership flickers: 6 to 10 owner switches per loop, and 11 to 15 loop vertices
   within 10 % of a tie in `along` mode. It produced no flips and no silhouette step (along dev 0.055 % against
   naive 0.056 %). When the two |k| are close, either owner gives about the same curve. The 1.5e-6 deg needle
   survives every variant: it belongs to the owner, and the rule never touches it.
5. **Saddle (probe 2).** The owner depends on the direction: across 36 / 21, along 9 / 48, mean 13 / 44, with 10 to 18
   switches. The hull's normal curvature there ranges from -7.0 to 55.2 with direction. Mean curvature gives fewer
   switches than along, but it answers a different question: how curved the surface is, not how much it bends the
   cut. After every weld variant one hull triangle in the band counts as "flipped" (normal · hull normal = -0.013,
   0.76 h from the rim crease): a near-vertical sliver whose normal is noise. It fails the zero-flip measure, and
   the cut here also reaches the crease (2 crease loop vertices).
6. **Cut across a crease (probe 3).** Passes, trivially. The 2 crease loop vertices are hull-owned (infinite k), no
   collapse happens near them, both crease vertices survive, and every crease edge keeps its bevel weight on both
   pieces (144 weighted edges become 126 + 20: the 2 crossed crease edges each split into weighted halves). Nothing
   merges across the crease. The plane contributes nothing to merge, so this probe does not stress the rule. A
   curved cutter across a crease would; it was not run.
7. **Ownership switch (probe 4).** Along the r 0.08 loop the owner switches 4 times. At the switch vertices: no
   flips, slivers 112 to 57, and a silhouette that moves from 0.0128 to 0.0196 % max (0.0095 h). The steps are
   below a tenth of a local edge. The worst angle stays 1.2e-6 deg, another owner-side needle. The render shows
   radial shading streaks round this cut in every variant, naive and welded: Weighted Normal over long hull-side
   fan triangles.

Locality held everywhere (invariant two-layers): 0 hull vertices moved outside the band in every case and variant.

### Renders

Each sheet shows the naive result, the ownership along the loop (blue = hull owns, orange = cutter owns) under
`across` and under `along`, and the welded results. Every result is shown after the shipped stack: Bevel 0.001,
1 segment, weight-limited, plus Weighted Normal, with settings copied from the cage's own modifiers, rendered
headless with Workbench. Loop edges carry bevel weight 1 and hull crease edges keep theirs.

![port s16](spike-boolean-weld/port_flank_s16.jpg)
![port s48](spike-boolean-weld/port_flank_s48.jpg)
![split](spike-boolean-weld/split_fwd.jpg)
![equal-k](spike-boolean-weld/probe_equalk_s16.jpg)
![saddle](spike-boolean-weld/probe_saddle_s16.jpg)
![switch](spike-boolean-weld/probe_switch_s48.jpg)
![crease](spike-boolean-weld/probe_crease.jpg)

The split sheet shows four panels: both pieces with caps, both pieces without caps, the subtract piece alone, and the
loop. The crease sheet's framing is poor; its numbers carry the result. Her Longinus panel-line screenshot was not
available to this agent, so no side-by-side was made with it.

### Kernels

| | boolmesh 0.2.1 | manifold-csg 0.4.1 (Manifold v3.5.3) |
|---|---|---|
| licence | MPL-2.0 | Apache-2.0 OR MIT bindings over Apache-2.0 |
| build | pure Rust, 14 s release on Starfire (Windows) | C++ through the -sys build script, 89 s on Yggdrasil (Linux container, `eureka-verify-rust`); fetches Manifold source by git at build time |
| time per op | 8 to 25 ms | 13 to 20 ms |
| output | identical vertex sets (max difference 0.0) and identical triangle counts on all 11 cases | same |
| provenance | per-corner value carried through (0 hull, 1 cutter) | `run_original_id` with `run_index` after `as_original` |
| intersection loop | not returned; derived from provenance | not returned; derived from provenance |
| output before internal cleanup | not exposed (`simplify_topology` runs inside `compute_boolean`) | not exposed (`RemoveDegenerates` runs inside the op) |

The "naive" rows are therefore already after each kernel's own degenerate cleanup. It leaves worst angles down to
1e-6 deg, because epsilon-length collapse does not remove slivers with long edges.

### Smallest changes, in order

1. **Measure curvature along the loop, not across it.** This is the fix. Without it the rule fails the canonical
   gun port; with it the 16-segment port passes.
2. **Tie the cutter's tessellation to the hull's local density** (segment length about 0.2 to 0.3 h, never far
   finer). The rule keeps the tighter surface's samples; when those are much denser than the flatter surface's,
   fans remain that no merge can remove.
3. **Split seams need a cleanup the rule does not cover.** Two sources of slivers remain. One is the owner's own
   samples near the loop. The other is the planar cap's triangulation, which matters because the caps must be kept
   for the bevelled seam. Candidates, not tested: retriangulate the cap (it is planar and interior, so free to
   remesh), and collapse owner edges shorter than the bevel width. The `-snap` variant got only part of the way:
   slivers 97 to 85, worst angle unchanged at 0.058 deg.
4. **In a split, apply a collapse only if both pieces' guards accept it.** Replaying one piece's collapses opened a
   crack.

### Questions for Self, round 1 (answered: ruling weld-owner-defines-silhouette)

1. Does "the surface with the tighter curve" mean curvature along the cut, so that the circle comes from the
   cylinder? The plan's `u = n x t` formulation gives the opposite owner for every cylinder cut. The operator should
   confirm which reading she means; this spike's renders and numbers show the two.
2. For panel splits her rule never fires, since a plane is never tighter than the hull. Is the cleanup she does by
   hand on panel seams this same rule, or a different one (merging the hull's own near-loop vertices)? If it is
   different, the weld rule needs a second clause, and that is an operator call.
3. Is a 5 deg worst angle in the band acceptable for the shippable bar, or does the bar want the 10 deg the guard
   uses?
4. The path to the Longinus panel-line screenshot, for the side-by-side the plan asks for.
5. Should the curvature come from the cage's limit surface (`X = S c`) rather than the 2-ring quadric fit? The fit is
   noisy near creases and at the saddle, but no result here turned on it.
