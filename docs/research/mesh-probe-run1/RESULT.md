# Mesh probe run 1: parametric rebuilds of Tripo hulls, with tools

Agent `probe-mesh-rebuild-1`, session `self-2026-10-10-ag2`, 2026-10-10. Disposable scratch; nothing
committed, no repo edited. Root: this directory (`...\scratchpad\mesh-probe\run1\`).

Governing operator words: "I'm not interested in measuring Opus's spatial reasoning performance, in
interested in exploiting it. Give it access, let it build and use tools." The probe ran the F2(b) arm
(full tool access) with the plan's targets, metrics, pass bars and stopping rules.

## Headline

| Target | Vocabulary | Best chamfer (% diag) | F@1% / F@2% | Mean sil-IoU | Vol-IoU | B0 chamfer | Round-0 chamfer | Loop gain (best / r0) | Edit test | Bars |
|---|---|---|---|---|---|---|---|---|---|---|
| Control | Geometry.Csg (12 brushes, truth 12) | **0.015** | 0.996 / 1.000 | 0.994 | 0.996 | 5.796 | 0.085 | 0.18x | 4 lines; 0.070 (4.7x best) | pass; edit fails the 1.5x bound |
| Control | OpenSCAD | **0.029** | 0.990 / 1.000 | 0.985 | 0.992 | 5.796 | 0.090 | 0.32x | 1 line; 0.030 (1.03x) | pass |
| Dexter Quiet run 1 | OpenSCAD (table of offsets) | **0.266** | 0.954 / 0.973 | 0.973 | n/a | 10.565 | 0.278 | 0.96x | 1 line; 0.266 (1.0x) * | pass; loop effect fails |
| Dexter Quiet run 1 | Geometry.Csg (29 brushes) | **0.463** | 0.888 / 0.985 | 0.911 | n/a | 10.565 | 1.226 | 0.38x | 7 lines; 0.461 (1.0x) * | pass; edit > 5 lines |
| Dexter Quiet run 2 | OpenSCAD (compact) | **0.682** | 0.788 / 0.947 | 0.924 | n/a | 10.565 | 0.803 | 0.85x | 1 line; 0.678 (1.0x) * | pass; loop effect in between |
| Headliner | OpenSCAD | **1.121** | 0.563 / 0.821 | 0.913 | n/a | 8.078 | 1.134 | 0.99x | 1 line; 1.087 * | pass (narrowly); loop effect fails |

Quiet pass bars: chamfer <= 2%, F@2% >= 0.80, mean sil-IoU >= 0.90, chamfer <= 0.33 x B0 (3.49 on Quiet,
2.67 on Headliner). Control pass bars: chamfer <= 1%, sil >= 0.95, vol >= 0.90, brushes <= 1.5x truth.
Headliner has no bar of its own in the plan, so Quiet's bars were applied.

\* On Quiet and Headliner the edit test does not discriminate: the **unedited** model scores almost the
same chamfer on the stretched target (Quiet r1 0.276, Quiet Csg 0.469, Quiet run 2 0.672, Headliner
1.088). The nose is a few percent of the surface. Only side-view sil-IoU moves (Headliner 0.927 to
0.948 with the edit; Quiet run 1 0.963 to 0.980). The control is the only target where the edit test
measures anything.

Full scope (every part) equals main-body scope within 0.001 on every best round: the dropped parts are
8 tiny floaters on Quiet and a few dozen specks on Headliner.

**Outcome letter: A by the table (control passes, Quiet passes, both vocabularies), qualified twice.**
1. The loop effect (outcome D) fails for OpenSCAD on Quiet run 1 and Headliner. Render-compare bought
   little there, because round 0 was already built from measurement tools. It passes for Geometry.Csg
   (0.38x) and on the control. In both of those cases the gain came mostly from tools: numeric refine,
   plane fits, and the winding-number labels. Render critique contributed less.
2. The edit readout says the Geometry.Csg description is a fit, not a description: 7 lines on Quiet,
   and 4.7x on the control. OpenSCAD is one line everywhere, because it has parameters and affine
   transforms. However, the edit test only discriminates on the control.

## What actually produced the numbers (read before trusting the table)

- **Control contamination.** No Hands harness existed, so I wrote the control generator
  (`tools/gen_control.py`). It used a random seed, and the truth (`sealed/truth.csg`) was never read.
  I still knew its *structure* from writing the code: core, nose cuts, sponsons, wings, engines,
  bridge and trench. The control therefore tests numeric recovery of a known structure. It does not
  test discovering structure.
- **Quiet run 1 OpenSCAD is fit-heavy.** The skin is a table of offsets: 21 wing-body stations and 8
  tail stations, each with a half-span and 7 [z_bottom, z_top] pairs, emitted by `mp prof` and
  `tools/table.py` from the target. The model chose the decomposition: one wing-body skin, a separate
  tail skin, two scallop cylinders, and the nose_k parameter. Run 2 is the compact description: a
  17-point planform, one wing plane per side, 8 elliptical body stations, 4 tail stations, pods and a
  chin fin. That is about 110 numbers against about 460. It is 2.5x worse in chamfer and still passes.
- **Run 2 is not independent.** It is the same agent with run 1 in context. It is a different
  *approach*, not a second sample.
- **Nose direction.** The plan says nose -Y. On this mesh the beak and canopy end is at **+Y**: the
  operator's schematic has the canopy arc at the pointed end, and the stinger is at -Y. I used +Y
  for "the nose" in the edit test.
- **Metrics differ from the plan's harness.** Everything was computed by my own `mp` tool. Chamfer is
  point-to-triangle with 30k area-weighted samples each way. Silhouette IoU uses 5 orthographic
  rasters at 384 px: front, side, top, and two obliques. Opposite axis views are identical in
  orthographic projection, so 3 axes and 2 obliques stand in for the plan's 6 + 2 Workbench renders.
  Vol-IoU is on the control only, from 128^3 ray parity. No Blender Workbench renders were made.
- **Geometry.Csg scoring.** The brush list is lowered through the crate's own `Assembler::distance`
  (src/field.rs). Surface nets at 220 cells on the long axis mesh the field, and that mesh is
  scored. The control target is itself a field mesh at the same resolution, which slightly favours
  Csg candidates on the control. Kernel (polygon) meshes were also scored as a side readout; see the
  gaps below.
- **Blender.** One background export job ran on a *copy* of `Desktop\Quiet.blend`
  (`targets/Quiet-copy.blend` to `targets/src_*.obj`). An operator GUI Blender (PID 36324, open on
  `Aetheria\Asset Sources\Ships.blend` since 2026-09-27) was present the whole time. I did not wait
  on it, because it is an interactive session, not a smoke run. A second Blender (PID 59588, not
  mine) appeared near the end, after my last Blender use. Nothing of mine is running.
- **Not done.** Headliner was rebuilt in OpenSCAD only, not in Geometry.Csg. Quiet run 2 was
  OpenSCAD only, which the brief allows. The Quiet run 2 loop stopped after one regression (r3),
  not after two sub-2% rounds, to stay inside the call budget.

## Per-round logs

Scores are main-body chamfer % / mean sil-IoU. "ref" means `mp refine` was run on the round before.

**Control, Csg.** r0 0.085 / 0.977, built from planes, sections and depth readouts. r1 (refine, 12
sweeps, 12 s) 0.015 / 0.994. The tools exposed what the renders did not: the trench length was 0.33,
not 0.24, and the refine also moved the wing roll and the nose_top pitch. The refine also drifted
nuisance parameters, for example a cutter roll of 13 deg that does nothing, which is a fit-not-
description smell.

**Control, OpenSCAD.** r0 0.090 / 0.972, a direct translation. r1 0.029 / 0.985 uses the refined
numbers, restructured with `nose_root`, `nose_len` and a `nose_frame()` that scales the nose cutters.

**Quiet run 1, OpenSCAD.** r0 0.278 / 0.970 (15 + 8 stations). The first render was NotManifold:
the cap winding was wrong in my 10-line skin module, and the mesh tool caught it because Manifold
warned. r1 0.266 / 0.973 adds denser stations at the beak. The residual is mostly the target's
interior shells: cockpit internals and pods, visible as red loops *inside* the outline on
`quiet1/r1.sec.png`. No solid can match those.

**Quiet run 1, Geometry.Csg.**

| Round | Chamfer / sil | Change |
|---|---|---|
| r0 | 1.226 / 0.827 | Hand-estimated wing plane, step boxes, nose wedge, tail block. |
| r0ref | 0.800 / 0.857 | Refine. |
| r1 | 0.971 / 0.873 | Wing plane re-fitted by least squares (`tools/wingfit.py`). The fit showed my hand estimate was wrong: dihedral slope 0.44, where the fit gave 0.17 with 3.5 mm rms. |
| r1ref | 0.875 / 0.841 | Refine. Sil got worse. |
| r2 | 1.025 / 0.860 | Bounded leading-edge and beak cuts for concave outline corners; keel. |
| r2ref | 0.828 / 0.827 | Refine with ray-parity inside labels. |
| r2ref2 | 0.644 / 0.874 | Same refine with **generalized-winding-number labels** (Jacobson 2013). 1454 of 14000 parity labels (10%) on the non-manifold target were wrong; the parity refine had been trading silhouette away. |
| r3 | 0.630 / 0.887 | Inner and outer wing panels on their own fitted planes. |
| r3ref | 0.555 / 0.891 | Refine. |
| r4 | 0.541 / 0.908 | Dorsal spine and nose floor cut, from a centreline profile diff (`mp prof` target vs candidate). |
| r4ref | **0.463 / 0.911** | Refine. |

**Quiet run 2, OpenSCAD.**
- r0 0.803 / 0.919.
- r1 0.729 / 0.926: joined the tail to the body (a gap was visible in the side view), added
  under-body pods and a chin fin.
- r2 **0.682** / 0.924: a station-wise thickness diff showed the body 45-55 mm too thin at
  x = 0.13-0.25, so the body was widened.
- r3 0.852 and r3b 0.775: superellipse sections (n = 3 and 2.5). These are regressions: the target's
  wing-root concavity punishes fuller sections.

**Headliner, OpenSCAD.**
- r0 1.134 / 0.902: fuselage, blade hulls, pods and inner engines as superellipse lofts and
  cylinders, measured with `mp island`.
- r1 1.188 / 0.910: deck and blade fins. Sil went up, chamfer went down: the deck buried target
  side walls.
- r2 **1.121** / 0.913: thinner, higher deck.

## Renders (target | candidate | silhouette diff; red = target only, blue = candidate only)

- Control: `control/best-csg.sheet.png` and `control/best-scad.sheet.png`. Round 0 is
  `control/r0.sheet.png`, the OpenSCAD r0, which ran last under that basename.
- Quiet run 1 OpenSCAD: `quiet1/best-scad.sheet.png` and `quiet1/best-scad.sec.png`. Round 0 is
  `quiet1/r0-scad.sheet.png`.
- Quiet run 1 Csg: `quiet1/best-csg.sheet.png` and `quiet1/r4ref.sec.png`. Round 0 is
  `quiet1/r0-csg.sheet.png`.
- Caveat: `rN.sheet.png` files in `control/` and `quiet1/` hold whichever vocabulary ran last under
  that basename, because .csg and .scad rounds share basenames. Use the `best-*` and `r0-*` files.
- Quiet run 2: `quiet2/r2.sheet.png`, `quiet2/r0.sheet.png`.
- Headliner: `headliner/r2.sheet.png`, `headliner/r0.sheet.png`, target sections `headliner/t_secy.png`.
- B0 baselines: `quiet1/b0.sheet.png`, `headliner/b0.sheet.png`, `control/b0.sheet.png`.

Best programs: `control/r1.csg`, `control/r1.scad`, `quiet1/r1.scad` + `quiet1/tables1.scad`,
`quiet1/r4ref.csg`, `quiet2/r2.scad`, `headliner/r2.scad`. Edits: `*_edit.*` beside each.

## Tools built (candidates for brokkr-ctl commands)

All are in `tools/`. `mp` is one Rust binary, about 650 lines, that depends on GameCult.Geometry.Csg
by path. It was built once locally and offline, in 1 min 10 s; incremental rebuilds took 7-9 s. The
target directory is 156 MB and is safe to delete. Every command runs in well under a second, except
`refine` (12-40 s).

| Tool | What it does | Earned its keep? |
|---|---|---|
| `mp score` | Chamfer (both directions), F@1/2%, 5-view sil-IoU, vol-IoU | Yes, every round. Seeing the t2c/c2t split told me whether a surface was missing or extra. |
| `mp sheet` | Contact sheet (4 views x target, candidate, diff) | Yes. The diff column found every missing part: tail gap, pods, deck, blade fins. |
| `mp sections` | Station slices, overlaid, with numeric extents | Yes. Control round 0 numbers. It showed Quiet's residual is interior shells. |
| `mp prof` | Table of offsets: per station, half-span and z-range at fixed span fractions (with an x window) | **Biggest single lever.** It built Quiet OpenSCAD round 0 at 0.278 directly, and its target-vs-candidate diff drove Quiet csg r4 and run 2 r2. |
| `mp island` | Station extents inside an x/z window (off-centre parts) | Yes on Headliner: engines, blades, pods, deck. |
| `mp depth` | ASCII depth map from an axis | Moderately. Control engines and trench; the Quiet scallop arc (circle fitted by hand from it). |
| `mp planes` | Iterated 1-point RANSAC plus a least-squares plane refit | Yes on the control: every face angle (chines 60.5/124.3 deg, bridge 11.1 deg, wing roll 9.6/8.2 deg). Unused on Quiet, which has few planes. |
| `tools/wingfit.py` | Least-squares plane over a region of the offsets table | Yes. It corrected a wrong hand estimate (dihedral 0.44 to 0.17). |
| `mp sym` | Best mirror plane x0 and residual | Yes. It showed Quiet is exactly mirrored (0.000%) and Headliner 0.089%, so mirror pairs are safe. |
| `mp parts` | Welded connected components, main-body scope, part table | Yes. It set the scope. |
| `mp csg` | Kernel build (warnings, tri count, kernel STL) plus field mesh | Yes. It surfaced SubtractIgnoredForNonBox and the kernel-vs-field divergence. |
| `mp refine` | Coordinate descent on brush parameters. Loss is mean surface \|SDF\| plus volume misclassification. Mirror-tied `_p`/`_s`, symmetry-locked centred brushes, winding-number labels. | **Yes for Csg** (control 0.085 to 0.015; Quiet about -25% per application). It drifts nuisance parameters and is blind to silhouette when its labels are wrong. |
| winding-number labels (in refine) | Robust inside test for non-manifold targets | Yes. It replaced ray parity, which was 10% wrong on Quiet. |
| `tools/warp.py`, `tools/warp_obox.py` | Stretch target forward of y_n; re-fit an obox under that stretch | Needed only because Csg has no scale transform. warp_obox even picked the wrong face for mirrored cutters (beak*_s). |
| `tools/table.py`, `tools/ev.sh`, `tools/gen_control.py`, `tools/export.py` | Glue | Glue. |

As brokkr-ctl commands, the clear candidates are `score`, `sheet`, `sections` / `prof` (as one
"stations" command), `planes` / `fit plane|circle`, `sym`, `parts` and `refine`. Each one is pure mesh
math over exported geometry: no Blender API, millisecond to second latency, files in, text and PNG
out.

## OpenSCAD constructs used and wanted (card fork: real OpenSCAD vs a subset)

Used:
- **Language:** variables and vectors, `function` (the `ny` nose warp, a section generator, a
  superellipse, `mirrored`), list comprehensions with `each`, conditional expressions,
  `include <tables.scad>` for data.
- **Geometry:** `polyhedron` (a hand-written 10-line `skin` loft), `hull()` (pairwise loft chains,
  pods, fins), `multmatrix` (shear: a planar wing slab on z = a + b|x| + c y), `scale` inside a
  module with `children()` (stretching nose cutters, so the edit is one line), `linear_extrude`,
  `polygon`, `circle`, `intersection` (planform with wing slab), `difference`, `union`, `rotate`,
  `translate`, `cube`, `sphere`, `cylinder`, `$fn`, mirroring via `for (s = [1,-1])`.

Not used: `minkowski`, `offset`, `rotate_extrude`, `import`, `surface`.

Wanted and absent even from OpenSCAD: a built-in loft or skin (BOSL2 has `skin()`; I wrote one) and a
superellipse primitive.

**Evidence for the fork.** Every best OpenSCAD result leaned on functions, list comprehensions,
`polyhedron`, `include`d data tables, `multmatrix` and `hull`. A subset limited to CSG-tree syntax
(cube, cylinder, sphere, translate, rotate, the booleans) could not have expressed the Quiet run 1 or
run 2 bodies. It also could not have made the edit a one-line parameter change.

I recommend real OpenSCAD files evaluated by OpenSCAD (or a full evaluator) as the authoring
surface, with the lowering consuming its CSG tree. If a subset is chosen, it must keep `function`,
list comprehensions, `polyhedron` (or a loft), `hull`, `multmatrix` and `scale`. Confidence:
moderate. This is one agent on three hulls.

## Geometry.Csg vocabulary gaps hit (counts)

- **Mirror construct.** On Quiet, 18 of 29 lines are mirror twins (9 pairs); 4 of the 7 edit lines
  are twins. On the control, 2 pairs, and the generator's own engines and wings were asymmetric. The
  `_p`/`_s` tie had to live in my refine tool.
- **Non-box cutters skipped by the polygon kernel.** 2 scallop `cylz` subtracts on Quiet produced
  `SubtractIgnoredForNonBox` x2. The kernel mesh then diverges from the field for the same list:
  Quiet r3ref kernel chamfer 1.170 / sil 0.809, against field 0.555 / 0.891. The concave trailing
  scallop is not expressible as a box cut.
- **Kernel interior faces even with boxes only.** Control r1 kernel mesh chamfer 0.504 (c2t 0.996)
  against field 0.015. The silhouette is identical, so this is internal faces from overlapping Adds,
  not geometry error.
- **No affine or scale transform, no parameters.** The control edit needed 4 hand-recomputed oboxes
  and lost fidelity (4.7x). The Quiet edit needed 7 lines.
- **No curved sweep, loft or ellipsoid.**
  - The body is 4 step boxes plus a keel plus 2 spine blocks.
  - The wing is 2 planar slabs per side.
  - Best Csg 0.463 against OpenSCAD 0.266 on Quiet; the gap is curvature.
  - Headliner (y-axis engines, ellipsoidal pods) was not attempted in Csg.
- **No arbitrary-axis cylinder.** It was needed for Headliner's 4 engines and 2 pods, and on Quiet for
  the pods (skipped in Csg).
- **Global intersect and subtract need ordering tricks.**
  - The wing trims (6 cutters) had to come before the body Adds, so the body survived.
  - The nose cuts had to come after.
  - Concave outlines needed **bounded** cutters, 4 per side (lead0/lead1, beak1/beak2), each with a
    hand-computed extent.
  - A scoped intersect (planform ∩ wing plane, which OpenSCAD run 2 used directly) would have
    replaced all of these.
- **FloretArm and DomeCapZ went unused.** FloretArm has constant thickness and lifts only along its
  arm. DomeCapZ has only a circular base. Both were considered for the wing, tail and canopy, and
  rejected.

## Card fork: where the fitting logic should live

Every fitting step was pure geometry over exported meshes, in a standalone CLI, with no Blender
dependency:
- station profiles;
- plane, RANSAC and least-squares fits;
- symmetry;
- winding-number inside tests;
- coordinate-descent refine;
- scoring.

Blender was needed once, to export. The evidence favours fitting in the CLI process, or a library it
links, operating on a selection or mesh dump. The Blender bridge should only supply geometry
(selection, export) and renders. Confidence: moderate. The probe never exercised a live Edit Mode
selection.

## Continuation

Finished within budget. Not done: Headliner in Geometry.Csg; a genuinely independent Quiet run 2 (fresh
agent); an eyes-only arm for comparison; Workbench renders as the plan specified.
