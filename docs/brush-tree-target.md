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

**A `field` part** (continuous body, Dexter Quiet):

1. Field: the part's signed-distance program, every primitive and blend defined once in Geometry.Csg.
   Hard edges the author wants crisp are declared as creases (a hard `max`, run 4's wing rim), not
   detected afterwards.
2. Cage: a coarse quad-dominant control cage whose crease edges lie on the declared creases and form
   closed loops, refit so its Catmull-Clark limit surface lies on the field's zero set (run 4's refit,
   run 3's least-squares in a mirror-reduced space).
3. Evaluated mesh: the operator's own stack, Mirror, Subdivision (limit surface), Bevel (one segment,
   on the creases), Weighted Normal (`dexter-quiet-cage/README.md`). Seams lie on the closed crease
   loops and part boundaries; run 7 showed seams through a broken crease join wing top and bottom.
4. Output: the cage with its stack, as an object in the ship's `.blend`; Package applies and exports it.

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
| Cage generator | field, declared creases, target face budget | cage with crease flags | trait; the hand cage is a fixed implementation |
| Refit | cage, field, subdivision rule | moved cage vertices | linear limit operator, injectable |
| Kernel | tree part | mesh with per-face brush and surface ids | trait |
| Scorer | two meshes | the bar's numbers | pure mesh math, no Blender |
| Brokkr bridge | intents from `brokkr-ctl` | receipts, objects in the ship file | directory store or loopback, per `blender-transport` |

The cage generator is the owner nobody has built: runs 5-7 produced dense field-aligned meshes, never
a cage. It sits behind a port so that candidates can be swapped and scored against the bar below.

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

**Why the scan stays the shape reference.** The operator's words: "I'm afraid I had to take a bit of
artistic liberty to get the cage to behave, mostly because of how creases work in Blender (generates
horrible geometry if the crease path isn't closed)". The liberty was a concession to the tool, so the
cage's departures are a tolerance band, not a new shape. Whether her cage should instead become the
shape reference is question `fidelity-reference`.

**The fidelity bar.** The evaluated output of a `field` part, measured the way the cage was (vertex to
nearest vertex against the same scan, both directions, at a vertex count within half to double the
cage's 3,154), is no worse than the hand cage in any of the six numbers above. Before the first cut
uses the shared scorer (chamfer, F@2 %, silhouette IoU, run 4's `tools/common.py`), the hand cage's
score under it is recorded as a body fact, and the bar is then also "no worse than the cage there".

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

- **How the cage is generated.** Candidates in the research: a quad layout from the cross field
  (patent US 12086939; Kloiber and Augsdorfer 2020), a coarse remesh then refit (run 6 at 144-342 faces:
  115-170 poles per 1000 vertices), a template cage refit (run 7 "Next" item 4). No measured source
  covers coarse feature-aligned patch layouts.
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
