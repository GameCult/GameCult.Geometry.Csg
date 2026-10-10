# Probe plan: can Opus describe a messy Tripo hull as a brush list?

Imagination, agent `imagination-brokkr-mesh-probe`, session `self-2026-10-10-ag2`, 2026-10-10.
Ruling in force: `aetheria-release:ruling:brokkr-mesh-probe-ag-self`. Operator: "What if the model
had some trash geo and its goal is to describe it parametrically?"

This is a probe plan, not a campaign. Nothing here is admitted. The probe is disposable scratch;
only its result document is kept.

## 1. The question, narrowed

Given a messy hull mesh, can Opus write a GameCult.Geometry.Csg brush list that matches it? How
close does it get, and does a render-and-compare loop improve the match?

The probe separates two things that VibeGeometry never separated:

- **Model reasoning.** Can the model place, size and cut brushes to match a shape it can only see?
  This is tested on a **control hull**: a synthetic target that is itself a known brush list, so the
  vocabulary can express it exactly.
- **Vocabulary and noise.** Can the vocabulary describe a real Tripo hull, with its floaters,
  non-manifold edges and soft forms? This is tested on **Dexter Quiet**.

The pairing decides the next step. If the control passes and Quiet fails, the bottleneck is the
vocabulary or the noise. If the control fails, the bottleneck is the model with this harness.

## 2. What exists today (facts the plan rests on)

**Brokkr cannot run this loop today.** The Blender adapter (`F:\Projects\Brokkr\surfaces\blender\brokkr_bridge`)
admits eight commands: createObject, deleteObject, setObjectTransform, setObjectVisibility,
setObjectParent, setObjectCustomProperty, selectObject and assignMaterial. It also captures a scene
snapshot. It cannot render, import or export meshes, read mesh data, or run code. It needs GUI
Blender with the add-on and CultLib's Python packages loaded. `docs/research/blender-mcp-capability-bar.md`
records that rendering, code execution and mesh reads are exactly what the Blender MCP servers have
and Brokkr lacks.

The probe therefore runs as plain `blender --background` scripts. It answers the same question,
and its harness doubles as the requirements list for a Brokkr Blender surface, if the probe earns one.

**Blender.** Blender 5.2.2 LTS is at `C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe`.
This is the binary the Aetheria release map's probes used (M8, M16). It bundles numpy 2.3.4 but not
scipy. `mathutils.bvhtree` provides nearest-point and ray queries. The probe needs no other Python
packages, since system Python has no numpy, trimesh or open3d. Two other installs exist and are not
used: `D:\Steam\SteamApps\common\Blender` (5.0), and 2.77 and 2.78 under `D:\Applications`.

**GameCult.Geometry.Csg (0.1.0, Rust 2024, deps bevy_math 0.17, rmp-serde, serde, sha2).**
- `Primitive` has five variants: Box{bounds}, OrientedBox{center,size,rotation}, CylinderZ,
  DomeCapZ and FloretArm. The ops are Add, Subtract and Intersect, applied as one ordered stream.
- Only Box and OrientedBox take part in the polygon CSG (`convex_cutter`, `assembler.rs:677`).
  Each of the other three is appended as its own mesh. A Subtract or Intersect brush of one of those
  types is skipped, and the build records `SubtractIgnoredForNonBox` or `IntersectIgnoredForNonBox`
  (`assembler.rs:803,836`).
- CylinderZ is fixed to the Z axis. `Brush.rotation` is not read when CylinderZ is compiled.
- Intersect is global: it clips every solid accumulated before it. `CsgTree` branches exist in
  `tree.rs`, but the assembler stream does not consume them.
- `Assembler::distance(p)` and `stream_distance` honour every op on every primitive. For boxes,
  oriented boxes and CylinderZ, the field is the exact signed distance.
- OBJ output lives in the examples (`examples/dream_machine_level.rs:355`), not the library. No
  primitive derives `Deserialize`.

**Hulls.** `C:\Users\Meta\Desktop\Quiet.blend` is the operator's file. Treat it as read-only and use
it only through a copy. Measurements from M8 and M16 of `docs/aetheria-release-map.md` on
Aetheria origin/master:

| Hull | Tris | Parts | Largest part | Parts < 2% length | Non-manifold edges | Size (Blender units) |
|---|---|---|---|---|---|---|
| Dexter Quiet | 9,614 | 12 | 87% | 8 | 524 | 0.98 x 1.05 x 0.41 |
| Sinister Quiet | 10,880 | 12 | 88% | 7 | 356 | 1.07 x 1.05 x 0.41 |
| Headliner | 50,008 | 189 | 33% | 23 | 6,145 | 0.68 x 1.00 x 0.35 |

Schematics are on the Desktop beside the .blend: `DexterQuietSchematic.png`, `SinisterQuietSchematic.png`
and `HeadlinerSchematic.png`. The nose points along Blender -Y, and starboard is -X. The add-on keeps
the Tripo mesh in the `Source` child collection (`tools/blender/aetheria_ships/__init__.py:30`), which
is never exported. The release map already makes the Tripo mesh a bake source for the operator's
rebuild (M16). A brush hull would be that rebuild's geometry.

## 3. Candidate targets, in increasing difficulty

1. **Control hull (synthetic).** Hands writes 12-20 Box and OrientedBox brushes in Quiet's
   proportions: a core hull, a wedge nose made by subtracting angled boxes, wings or sponsons,
   engine blocks and a bridge. It is meshed by the same evaluator as candidates. The truth file is
   never shown to the probe agent.
2. **Dexter Quiet.** One dominant part (87%), a moderate number of non-manifold edges, and an
   operator schematic. This is the real test.
3. **Headliner.** 189 parts, of which the largest is only 33%. Stretch only. Run it only if Quiet
   reaches at least the partial band (section 8).

Sinister Quiet is held back. It is a near-sibling of Dexter and adds little until variance is known.

## 4. Representation the model writes

The model writes the Geometry.Csg brush stream as-is, in a thin line form, with one brush per line.
The fields map one-to-one onto `Primitive`:

```
# op   shape  name             center x y z         size x y z          rot_deg x y z (obox only)
add    box    hull_core        0.00 0.02 0.00       0.34 0.80 0.16
sub    obox   nose_chine_top   0.00 -0.46 0.10      0.50 0.30 0.12      -28 0 0
add    obox   sponson_port     0.30 0.10 -0.02      0.14 0.55 0.10      0 0 4
int    box    clip_envelope    ...
```

- `box` becomes `Primitive::Box { bounds: Aabb::from_center_size(..) }`.
- `obox` becomes `Primitive::OrientedBox` with `Quat::from_euler(EulerRot::XYZ, ..)` in degrees.
- Ops are add, sub and int, in stream order. Material is fixed at `MaterialId(0)`.
- The vocabulary is Box and OrientedBox only (fork F3). These are the only primitives the kernel
  actually runs CSG on. A curved primitive cannot be cut, so offering one invites silent skips.

Why this form and not Rust `LevelDsl` source:
- A Rust source form needs a compile on every round.
- Rust source invites helper loops and abstractions. VibeGeometry's own failure record names "valid
  Python, … high node counts, … parameter sliders" among its seductive proxies.
- Euler degrees in plain columns are easier to read and edit than quaternions. BenchCAD records
  single-literal errors as a failure mode, and a flat table makes each literal one visible edit.
- No new DSL is introduced. A line is a Brush with its fields written out.

What Geometry.Csg cannot express for hard-surface hulls. Each gap is a probe readout to tally, not
something to build:
- Cylinders on any axis other than Z. Engines along Y need these.
- Boolean cuts by curved primitives.
- Bevels and chamfers, except as subtracted angled boxes.
- Mirror and array constructs.
- Scoped intersect, meaning an intersect that clips one part instead of the whole stream.

The probe counts how often the model wanted each one: brush pairs that duplicate each other as
mirror images, faceted stand-ins for a cylinder, and many small chamfer cuts. Those counts are the
evidence for any later vocabulary cut.

## 5. The verifier

Two disposable tools live in the probe scratch directory. Neither is committed to any repo.

**(a) `csgeval`.** A scratch Rust binary with a path dependency on `F:\Projects\GameCult.Geometry.Csg`,
and `CARGO_TARGET_DIR` set inside scratch. It parses the line form (about 80 lines), assembles it,
and writes:
- an OBJ (using the example's `obj_text`);
- the build warnings;
- about 20k surface samples, area-weighted, kept only where `|stream_distance| <= 1e-4 x target
  diagonal`.

The sample filter exists because overlapping Add brushes can leave internal faces in the mesh. Only
points on the field's zero set count as surface, so the kernel's own field decides what the surface is.
The binary is built once; each round only runs it.

**(b) `eval.py`.** A Blender 5.2.2 background script, run as
`blender --background --factory-startup --python eval.py -- <cand.obj> <cand_samples> <target.obj> <out>`.
It uses only bundled numpy and mathutils, and computes:

| Metric | How | Role | Prior art |
|---|---|---|---|
| Chamfer, symmetric mean | 20k area-weighted target samples to the candidate BVH via `find_nearest`, plus candidate samples to the target BVH. Reported as % of the target bbox diagonal. | Headline | BlenderGym geometry metric; CAD-Recode and MeshCoder rank by it |
| F-score at 1% and 2% of the diagonal | From the same nearest distances (precision and recall at threshold tau) | Headline. Chamfer hides outliers and F-score does not. | Tatarchenko et al., CVPR 2019 (KNOWLEDGE) |
| Silhouette IoU per view | Workbench flat renders at 384 px. Masks for 6 axis views and 2 obliques. IoU per view and the mean. | Robust to the Tripo target's non-manifold edges and floaters | ShapeCraft and SEIG render loops; multi-view beat single-view (prior-art section 4) |
| Volumetric IoU | 64^3 voxels. Inside test by majority vote over ray parity on 3 axes. | Control hull only. Too unreliable on the non-manifold Tripo target to report. | MeshCoder and CAD-Recode report IoU |
| Brush count; mirror-pair count; kernel warnings | From the brush file and `csgeval` | Compactness and parametric quality | ShapeMOD, which minimises calls and free parameters |

Two target scopes are fixed in advance:
- **Main body:** face-connected parts at least 2% of hull length. This is the headline scope.
- **Full:** every part. Reported alongside.

The pre-registration is the point: the brush list should not be scored on the 8 greeble floaters,
and choosing the scope after seeing the numbers would invite rationalisation.

**Reference band.** BlenderGym's procedural-geometry task scored Chamfer 0.334 for humans against
1.120 for the best VLM (GPT-4-Turbo), a 3.4x gap. Those numbers are in BlenderGym's own units and
from 2024-25 models, so only the ratio carries over. The probe's own band:
- **Floor (B0):** one oriented bounding box, scored by the same verifier. It is computed once per hull.
- **Ceiling:** the control's truth list, which scores 0 by construction. On Quiet, the floor is the
  self-Chamfer between the full and main-body scopes.
- **Human band:** optional (fork F4).

## 6. What the model sees each round

The model receives two contact sheets of about 1536x1152 px, roughly 2.4k image tokens each, plus
one text block.

1. **Views sheet.** Four rows (front -Y, side +X, top +Z, iso) by three columns: target shaded,
   candidate shaded, and a silhouette diff. In the diff, target-only pixels are red, candidate-only
   pixels are blue, and overlap is grey.
   - Prior art: SceneCraft and SEIG render-critique-revise. ShapeCraft bbox and global views.
     Multi-view conditioning beat single-view.
   - The diff column is there because BlenderGym's verifier agreement was low (Claude 3.5 Sonnet
     0.66 against human 0.79), so the model should not have to judge "close" unaided.
2. **Stations sheet.** Seven cross-sections at fixed stations along Y. Each is a front orthographic
   slab render with clip start and end 1% of length apart, with target and candidate outlines
   overlaid.
   - This is naval architecture's own hull description, the station lines.
   - It also gives the model the interior profile that silhouettes hide. Text-to-B-Rep and BenchCAD
     name spatial misalignment and dropped features as the dominant failures.
3. **Text block.**
   - The metrics table for this round and the best round so far.
   - Per-view IoU.
   - Brush count and kernel warnings.
   - Round 0 adds the target bbox and the per-station width and height extents as numbers.

Per prior art, numeric feedback alone peaked at round 1 (2607.05573), while render critique kept
improving through rounds 2-3. Both are given. BenchCAD found the image "at best a clarifier" for
thinking models, so the numeric extents carry the measurements and the images carry the shape.

## 7. The loop

**Session.** One fresh Opus agent session per hull run. The brief contains:
- the operator's quote;
- the line-form grammar and its semantics: stream order, global intersect, obox Euler XYZ in degrees;
- the axis convention (nose -Y, starboard -X);
- the brush budget;
- the single evaluation command.

**Sight.** Eyes-only (fork F2). The agent may write `cand.txt`, run `eval.cmd`, which chains
`csgeval` and `eval.py`, and read the sheets and text the command emits. It may not open the target
mesh, the control truth file or the schematics. This restriction is a brief instruction, not
something enforced, so the transcript is audited afterwards for any read of target paths.

**Rounds.**
- Round 0 writes a first list from the target pack.
- Rounds 1 to 7 each revise the list, so there are at most 8 evaluations per run.
- The best round is the one with the lowest main-body Chamfer. A regression is kept in the log but
  never replaces the best, as in CAD-Recode's min-Chamfer selection.

**Stop** at the first of these:
- the round cap is reached;
- main-body Chamfer improves less than 2% (relative) for two consecutive rounds;
- every success threshold is met.

**Held fixed across rounds and runs:**
- the camera rig, resolution and sample counts, with a fixed seed;
- the target scopes;
- the vocabulary;
- the brief text;
- the model, Opus 5.5;
- the brush budget: 40 for Quiet, 30 for the control, 80 for Headliner.

The budget forces description rather than voxelisation. A list of 500 tiny boxes is not parametric.

**Edit readout (one extra turn after the best round).** The model is asked to "lengthen the nose 20%
and widen the sponsons 10%". The readout is how many lines it touches and whether Chamfer to a
correspondingly scaled target stays within 1.5x of its best. That measures whether the description
is parametric in the operator's sense, editable intent, or only a fit.

**Runs.**
- Control x1.
- Dexter Quiet x2, because one run of a stochastic model is an anecdote.
- Headliner x1, only if Quiet reaches the partial band or better.

All runs go on Starfire, one at a time. Blender 5.2.2 is installed only there, and each evaluation is
a small background Workbench job.

## 8. Success and failure, fixed before running

The thresholds are judgment calls, written down now so the result cannot move them.

| Target | Pass | Partial (blockout-grade) | Fail |
|---|---|---|---|
| Control | Chamfer <= 1% diag, mean sil-IoU >= 0.95, vol-IoU >= 0.90, brushes <= 1.5x truth | Chamfer <= 3%, sil-IoU >= 0.85 | Worse than partial |
| Dexter Quiet (main body, best of 8, both runs) | Chamfer <= 2% diag, F@2% >= 0.80, mean sil-IoU >= 0.90, Chamfer <= 0.33 x B0 | sil-IoU 0.80-0.90 and Chamfer <= 0.5 x B0 | sil-IoU < 0.80, or Chamfer > 0.5 x B0 |
| Loop effect (any target) | Best-round Chamfer <= 0.7 x round-0 Chamfer | | Best is round 0 or within 10% of it |

What each outcome means for the operator's plan:
- **A. Control passes, Quiet passes.** The idea earns a campaign. The scope would be:
  - Brokkr's Blender surface gains the harness's capabilities as typed commands: import mesh,
    render views, evaluate against a target, apply a brush list.
  - Geometry.Csg gains only the vocabulary gaps the tallies prove.
  - The hull rebuild in M16 starts from the model's brush list, and the Tripo mesh stays the bake
    source.
- **B. Control passes, Quiet partial or fails.** The model reasons well enough and the vocabulary or
  the noise is the limit. The next probe arm is either one vocabulary extension from the tallies, or a
  classical front end that hands the model primitive hints. RANSAC planes (Schnabel 2007) and the
  discretisation step from InverseCSG are the candidates. Neither is built before this result.
- **C. Control fails.** Even in-vocabulary placement fails with this harness. Do not build Brokkr
  features for this. Two alternatives remain:
  - fitting without the model: InverseCSG-style search, or differentiable CSG refinement (UCSG-Net,
    the fuzzy-Boolean paper);
  - keeping the operator as the modeller, with the model editing her blockout instead of writing one.
- **D. Loop effect fails, whatever the absolute scores.** Render-compare is not buying anything. One
  shot plus human editing is the shape, and a Brokkr render loop is not justified by this use.
- **Edit readout.** If the edit touches more than 5 lines or blows the 1.5x bound, the output is a
  fit, not a description, even under outcome A. The campaign would then need structure the
  line form lacks (named parts, mirror), and that must be decided before any build.

## 9. Cost

- **Harness (Hands, one bounded batch, cap of about 60 calls).**
  - Copy `Quiet.blend` to scratch and export Dexter, Headliner and both main-body scopes to OBJ.
  - Write the control truth list.
  - Write `csgeval` (about 120 lines) and `eval.py` (about 250 lines) and `eval.cmd`.
  - Compute B0 for each hull.
  - Self-check: the control truth scores Chamfer about 0 and IoU 1; the OBB scores below truth.
  - One cargo build of a small dependency set (bevy_math, serde, rmp-serde, sha2) into scratch. That
    is a few hundred MB, deleted afterwards. This is the only compile.
- **Probe runs.** About 30 calls per run (setup, then about 3 per round over 8 rounds, plus the edit
  readout).
  - Four runs make about 120 calls. Headliner is conditional, so three runs make about 90.
  - Each round adds roughly 5k image tokens, so context peaks around 60-80k tokens per run. Total input
    is about 1.5-2M tokens per run, mostly cache reads.
- **Blender.** About 35 evaluations across all runs plus about 5 harness checks. Each is 15-40 s of
  background Workbench work. They run serially on Starfire, never two at once and never alongside
  another heavy job, for about 20 minutes of Blender time in all.
- **Total.** About 150-190 agent calls and one session-day of wall clock. Self reads the results;
  Soul is not needed for a probe that admits nothing.

## 10. What not to build

- No Brokkr changes: no new commands, no render surface, no MCP server install. The Blender Lab MCP
  is GPL-3.0 and unauthenticated, and background scripts answer the question without it.
- No service, daemon, Eve surface or CultCache persistence. The probe's state is files in scratch.
- No new crate or package in any repo, and no commits to Geometry.Csg. `csgeval` is a scratch binary
  with a path dependency.
- No grammar beyond the line form: no mirror, array or bevel constructs. Their absence is measured,
  not fixed.
- No RANSAC front end, differentiable optimiser or point-cloud encoder in v1.
- No writes to `C:\Users\Meta\Desktop\Quiet.blend` or anything under `F:\Projects\Aetheria`.
- The VibeGeometry scar applies directly. That project "dived almost immediately into CSG grammar,
  parity fixtures, native bridge probing, mesh generation, and performance work" before measuring
  whether the authoring loop worked. This probe measures first. Infrastructure is earned by outcome A
  and scoped by the tallies.

Kept afterwards: one result document. It holds the metrics table per run and round, the best sheets,
the brush lists, the vocabulary tallies, the transcript-audit line, and which outcome A-D held. Its
home is suggested below.

## 11. Forks for the operator (questions, with recommendations; not admitted)

**F1. Evaluator: Geometry.Csg's own kernel, or Blender's exact booleans?**
- (a) Scratch `csgeval` on the real kernel. This needs one small cargo build.
- (b) `eval.py` builds the boxes in Blender with exact boolean modifiers. No Rust at all.

Recommend (a), confidence moderate. The question is whether the Geometry.Csg brush list can be the
durable design surface, and only its own kernel and field prove that the list meshes. Kernel faults
that turn up are findings, not noise. (b) answers "can Opus box-model this", which is a weaker
question.

**F2. What the probe agent may see.**
- (a) Eyes-only: renders, sections and scores.
- (b) Full tool access, so the agent may script numeric analysis of the target mesh: sections, plane
  fits, its own optimiser.

Recommend (a) first, confidence high, because the operator asked about Opus's spatial reasoning.
(b) answers "can Opus write a fitter", which is a different and probably easier question. It is a
cheap second arm if (a) lands in B or C.

**F3. Vocabulary: boxes and oriented boxes only, or include CylinderZ, DomeCapZ and FloretArm?**
- (a) Boxes only.
- (b) All five, with the curved ones additive-only, since the kernel skips cuts by them.

Recommend (a), confidence moderate. In (b), a cut by a curved primitive is silently skipped, which
corrupts the comparison. The cylinder demand is tallied instead.

**F4. Human reference band.** Should the operator spend about 30 minutes box-modelling Dexter Quiet
by hand in Blender, scored by the same verifier?

Recommend no for v1. Ask only if Quiet lands on the partial and pass boundary, where a human number
would decide the outcome.

**F5. Brokkr in the path now?**
- (a) No Brokkr. Plain background scripts.
- (b) First give Brokkr's Blender adapter render, import and evaluate commands, then probe through it.

Recommend (a), confidence high. Brokkr lacks every capability the loop needs, and building them first
repeats VibeGeometry's order. Outcome A makes the harness the spec for those commands.

**F6. Targets and runs.** Control x1, Dexter Quiet x2, Headliner x1 only on a partial or better.
Alternative: Quiet x1 to halve the cost.

Recommend x2. With n = 1, a pass or fail is indistinguishable from sampling luck.

Suggested home for the result document (Self decides): `F:\Projects\Brokkr\docs\research\parametric-hull-probe.md`,
beside the capability bar. If outcome A holds, the result steers Brokkr's Blender surface. If B or C
holds, it steers Aetheria's hull rebuild instead, and a pointer belongs in the release map.
