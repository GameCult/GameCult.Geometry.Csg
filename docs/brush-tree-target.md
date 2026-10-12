# Brush tree: target (r2)

Campaign `brush-tree`, owned by the Aetheria/Ghostlight Self. Drafted by Imagination
(`imagination-brush-tree-target-r2`, session `self-2026-10-11-ag2`) on 2026-10-12.
It supersedes r1 (`49948c8b`, the CSG-only target). This page holds the ends, not the means:
no cut plan. The typed `brush-tree:target:r2` holds the invariants, the not-in-scope list and the
canonical implementations; this page holds why, and the numbers behind the bars.

- **Repos:** `GameCult/GameCult.Geometry.Csg` (the tree, the field, the kernel, the scorer),
  `GameCult/Brokkr` (the agent's hands in Blender), `GameCult/Aetheria` (the first consumer).
- **Working branch:** `eureka/brush-tree`.

## The rulings this target rests on

Read them in the mind by id; their operator quotes are the authority, not this page.

- `brush-tree:ruling:representation-per-hull`: subdivision limit surfaces for continuous bodies like
  Dexter Quiet, primitives for mechanical hulls like the squatter mech ship; both paths, per hull or
  per part. It narrows the "mesh CSG is the main representation" clause of
  `settled-direction-2026-10-10` to mechanical hulls.
- `brush-tree:ruling:pursue-sdf-composition-remeshing`: the continuous path is an SDF composition
  remeshed automatically; viability rests on the remesher; the operator's own Dexter Quiet rebuild is
  the reference it is measured against.
- `brush-tree:ruling:shippable-part-bar`: clean unbroken flow, part-coherent low-distortion UVs,
  one-segment bevels with face-weighted normals.
- `brush-tree:ruling:no-unownable-tools-in-loop`: only code we can own is in the loop.
- `brush-tree:ruling:spike-sdf-smin-to-cage`, `:spike-instant-meshes-field-features`: the spikes
  whose results (runs 4 and 7) this target reads.
- Unchanged from r1 and still in force: `openscad-target`, `brokkr-beats-blender-mcp`, `cli-not-mcp`,
  and the defaulted rulings on the Blender sink, `run`, docs lookup, look files, the per-ship tree
  `.cc`, persistence through cultcache-rs, the Package path, Studio and impostors.

## What changed from r1, in one paragraph

r1 lowered every hull through mesh CSG with field-derived microbevels. The probes showed CSG cannot
build Dexter Quiet's continuous curvature (run 2), and the operator ruled the representation per hull.
A hand-designed cage (run 3, v7: chamfer 0.228 %) beat every automated route; SDF composition with
smooth-min fuses the body and its sweeps "without breaking a sweat" (run 4) but its program fidelity
(0.52 %) and the remeshers' flow (runs 5-7: open field loops, 38-69 poles per 1000 vertices, UV area
distortion 6-10x the designed cage's) fall short. Run 7 also found that the fidelity wall belonged to
the SDF program, not the remesher: measured against the SDF itself, every remesh sat at 0.01-0.07 %.
Microbevels from the field are gone: the bar names one-segment mesh bevels.

## What the pipeline turns a brush tree into

**The tree** is one typed document per ship (`tree-store-per-ship-cc`): primitives, transforms,
scoped booleans, and smooth unions with a named radius. Every part (top-level branch) declares its
representation, `field` or `kernel`. The declaration is authored, never inferred from the shape.

**A `field` part** (continuous body, Dexter Quiet) has two layers. The operator, 2026-10-12, on her
cage: "Note that I'm specifically trying to be faithful here to the curves of the original, and my
control points can go to unexpected places to achieve that. The cage controls the surface, the cage
is not the surface." Her cage carries the primary form (silhouette and main curves); the canopy,
vents, intakes and nose details are absent by design.

- **Primary-form layer.** Owner: the part's field, in the tree.
  1. Field: a signed-distance composition of the large forms (body, wing, pods, fused sweeps), every
     primitive and blend defined once in Geometry.Csg. Hard edges meant to be crisp are declared as
     creases (a hard `max`, run 4's wing rim), not detected afterwards.
  2. Cage, derived: a coarse quad-dominant control cage whose crease edges form closed loops on the
     declared creases, with its control points *fitted* so the Catmull-Clark limit surface lies on the
     field's zero set. The control points sit off the surface; producing the cage is subdivision-surface
     fitting (Hoppe et al. 1994; Marinov and Kobbelt 2005), not remeshing the surface.
  3. Evaluated mesh: the operator's own stack, Mirror, Subdivision (limit surface), Bevel (one segment,
     on the creases), Weighted Normal (`dexter-quiet-cage/README.md`). Seams lie on the closed crease
     loops and part boundaries; run 7 showed seams through a broken crease join wing top and bottom.
- **Detail layer.** Owner: the part's detail brushes, in the tree. Canopy, vents, intakes and nose
  details are brushes placed on the evaluated limit surface. They never move the cage, and the cage
  never encodes them. How a detail brush lowers onto a curved subdivision surface is not known yet
  (below).
- **Output:** the cage with its stack and the lowered detail, as objects in the ship's `.blend`;
  Package applies and exports them.

**What the probes tested.** Position fitting was tested: run 3 fitted a designed cage's control points
to the scan by least squares on the limit operator (v7, chamfer 0.228 %), run 4 refit a cage to the
field, run 6 refit Instant Meshes cages of 144-342 faces (best 0.527 % lowered, 103 poles per 1000
vertices). Runs 5-7 otherwise remeshed the surface, which cannot yield a cage of this kind. What no run
tested is generating cage *connectivity* automatically: run 3's topology was designed by hand, and run
6's came from a remesher at cage density, which was blocky and pole-heavy.

**A `kernel` part** (mechanical, the squatter mech ship): the polygon kernel builds exact planar faces
with scoped booleans, a one-segment bevel on hard edges, face-weighted normals, and UVs from each
brush's declared charts. The r1 kernel machinery and its open questions serve this path.

**Both** reach Aetheria the same way (`lowered-hull-through-package`): an object in the ship file,
exported by the existing Package. Nothing reads a cage, mesh or render back as truth.

### Owners, inputs, outputs, mock points

| Owner | Inputs | Outputs | Mock point |
|---|---|---|---|
| Tree (Geometry.Csg) | text through the one commit primitive | typed tree revision | in-memory store |
| Field | tree part | distance and gradient at a point | trait; analytic test shapes |
| Cage connectivity generator | field, declared creases, target face budget | cage connectivity with crease flags | trait; the hand cage is a fixed implementation |
| Cage fitter | cage connectivity, field, subdivision rule | fitted control points | linear limit operator, injectable |
| Detail lowering | detail brushes, evaluated limit mesh | detail geometry | trait |
| Kernel | tree part | mesh with per-face brush and surface ids | trait |
| Scorer | two meshes | the bar's numbers | pure mesh math, no Blender |
| Brokkr bridge | intents from `brokkr-ctl` | receipts, objects in the ship file | directory store or loopback, per `blender-transport` |

The connectivity generator is the owner nobody has built: runs 5-7 produced dense field-aligned
meshes, and run 6's cage-density remesh was blocky. It sits behind a port so that candidates can be swapped and scored against the bar below.

## The hand cage as the measuring stick

**What it is** (GameCult.Geometry.Csg `docs/research/dexter-quiet-cage/` @ d426f86, measured
2026-10-12 from `cage_raw.obj` and `cage_eval.obj`):

- Half hull: 29 vertices, 25 faces (19 quads, 6 triangles), the mirror seam open (12 boundary edges).
  Mirrored, about 50 faces for the whole hull.
- Creases: 9 edges at 1.0 forming one chain, vertex 5 (x = 0, nose) to vertex 22 (x = 0.003, tail),
  so the mirror closes it into one loop round the wing rim.
- Evaluated at subdivision level 3: 3,154 vertices, 3,152 faces, all quads, no boundary, 31 vertices
  of valence other than 4 (about 10 per 1000 vertices).
- No UVs.
- Fidelity to the scan, vertex to nearest vertex, % of the hull diagonal (1.492):
  cage to scan mean 0.88, p95 2.04, max 3.11; scan to cage mean 1.29, p95 4.12, max 6.03.

**Why the scan stays the shape reference.** She was "specifically trying to be faithful here to the
curves of the original"; the liberty she took was a concession to Blender's creases ("I'm afraid I had
to take a bit of artistic liberty to get the cage to behave, mostly because of how creases work in
Blender (generates horrible geometry if the crease path isn't closed)"). So the scan's primary form is
the shape, and the cage's departures from it are a tolerance band.

**The six numbers above are not the bar yet.** They mix two things: her liberty, and the detail the
cage omits by design (scan to cage max 6.03 % is most likely the canopy or a vent, not the curves). A
fidelity bar must measure primary form only. How primary form is separated from detail is question
`primary-form-measure`; the recommendation is a detail mask the operator paints once on the scan.

**The fidelity bar.** The primary-form layer's evaluated output, measured against the scan with detail
excluded by that rule, vertex to nearest vertex in both directions at a vertex count within half to
double the cage's 3,154, is no worse than the hand cage measured the same way, in mean, p95 and max;
and its silhouette IoU from the three axes is no lower than the hand cage's. The hand cage's numbers
under the rule, and its score under the shared scorer (chamfer, F@2 %, silhouette IoU, run 4's
`tools/common.py`), are recorded as body facts before the first cut is measured. Until then the six
numbers above are a loose upper bound only.

**Attribution.** Every measurement reports two parts separately: the program's zero set against the
scan, and the cage's limit surface against the field. Run 7 misdiagnosed the wall for a whole spike
because only the end-to-end number existed.

**The cage-quality bar**, from the same cage:

- Size: at most 4x the hand cage's face count for the hull (about 200 faces). The factor is a proposal.
- Faces: quads and triangles only, no n-gons; triangle share at most the hand cage's (6 of 25, 24 %).
- Creases: every crease chain is a closed loop, or ends on the mirror plane where its mirror closes it.
- Limit mesh at level 3: one shell, watertight, at most 2x the hand cage's 31 irregular vertices.
- UVs (the cage has none, so this comes from the bar's words and run 3's v7): islands follow parts,
  seams on crease loops and part boundaries, mean |log2| area distortion at most 0.1 (v7: 0.076).

## Not yet known (research owed before cuts are mapped)

- **How the cage's connectivity is generated for fitting.** Position fitting is covered and tested.
  Connectivity is not: Hoppe et al. 1994 optimise the control mesh's connectivity as one phase, and
  Marinov and Kobbelt's Solid Modeling 2004 version restructures the control mesh adaptively, but the
  research file has neither full text read (subd-cages file s.1, Gaps). Other candidates: a quad layout
  from the cross field (patent US 12086939; Kloiber and Augsdorfer 2020), QEM simplification to a base
  mesh, a coarse remesh then refit (run 6), a template cage refit (run 7 "Next" item 4).
- **How a detail brush lowers onto the limit surface** (a boolean into the evaluated mesh, an inset in
  the cage, or a separate interpenetrating piece). The research found booleans on curved surfaces give
  stretched faces and no convention for subd body plus primitive inserts (subd-cages file s.0, s.5).
- **What text authors a `field` part.** OpenSCAD has no smooth union, so `openscad-target` and
  `text-is-a-surface` from r1 cannot both hold for smooth-min parts.
- **How a `field` part and a `kernel` part meet** on one hull. The research found no convention
  (subd-cages file s.0, s.5).

## Research it rests on

All in GameCult.Geometry.Csg `docs/research/` on `eureka/brush-tree`:

- `dexter-quiet-cage/` @ d426f86: the reference cage.
- `shippable-bar/` @ 253f34d: the operator's bar and render.
- `mesh-probe-run1/` to `mesh-probe-run7-im-field/`: OpenSCAD and CSG fits (1), CSG lowerings (2),
  a designed cage (3), SDF with smin and a field cage (4), QuadriFlow (5), Instant Meshes (6), the
  Instant Meshes fork with the SDF's cross field and a hard rim (7).
- `subd-cages-mixed-hulls-and-open-kernels.md` @ 390db63: cage fitting, remeshers as cage seeds,
  creases versus bevels, mixed assets, open kernels.
- `primitive-seams-and-sdf-bevel-meshing-prior-art.md`, `brush-surfaces-and-sdf-bricks-prior-art.md`,
  `openscad-evaluators-and-csg-export.md`, `octahedral-impostors-prior-art.md`: the kernel path.
