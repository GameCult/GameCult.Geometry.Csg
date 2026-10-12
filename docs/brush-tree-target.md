# Brush tree: target (r4)

Campaign `brush-tree`, owned by the Aetheria/Ghostlight Self. Drafted by Imagination
(`imagination-brush-tree-target-r4b`, session `self-2026-10-12-ag`) on 2026-10-13.
It supersedes r3 (`842d101`). This page holds the ends, not the means: no cut plan. The typed
`brush-tree:target:r4` holds the invariants, the not-in-scope list and the canonical implementations;
this page holds why, the authority map, and what is still unknown.

- **Repos:** `GameCult/GameCult.Geometry.Csg` (the tree, booleans, the weld, the scorer, and the Blender
  extension that runs them live), `GameCult/Brokkr` (the agent's hands in Blender), `GameCult/Aetheria`
  (the first consumer).
- **Working branch:** `eureka/brush-tree`.

## The rulings this target rests on

Read them in the mind by id; their operator quotes are the authority, not this page.

- `brush-tree:ruling:hand-cages-enter-the-tree` (Operator, 2026-10-12): a continuous hull's primary form
  is an artist's cage, entered as a tree primitive; detail is cut into its evaluated surface. Automatic
  cage generation is research and gates nothing.
- `brush-tree:ruling:blender-evaluates-cages` (Operator): Blender evaluates the cage's Mirror and
  Subdivision; Geometry.Csg cuts, splits and welds the result. One evaluator by construction.
- `brush-tree:ruling:brush-modes-add-subtract-split` (Operator): a detail brush is add (union), subtract
  (cut) or split (keep both sides). All three are booleans on the evaluated cage mesh and never move the
  cage.
- `brush-tree:ruling:weld-owner-local-corners-kept` (Operator): ownership is local along each loop. At
  each stretch, the surface whose vertices carry more of the silhouette keeps them and the other's spare
  vertices near that stretch merge away. A hard-edged cutter's corners always survive. On a flat split
  the hull carries the silhouette everywhere and the seam stays on the cutter's plane. It refines
  `weld-owner-defines-silhouette`, which superseded `boolean-cleanup-tighter-curve-wins`; neither is in
  force.
- `brush-tree:ruling:weld-runs-as-live-result-object` (Operator): the cage keeps its own Mirror and
  Subdivision; brushes are ordinary objects in a brush collection, listed in order on the result object's
  Cuts panel (mode, enable, bevel weight); a Rust step in a GPL extension wheel runs the booleans and the
  weld and writes the result object's mesh, whose own stack is Bevel (weight mode) then Weighted Normal.
  Nothing is ever applied; the same code produces the shipped lowering.
- `brush-tree:ruling:panel-lines-by-split-boolean-r2` (Operator): a panel line is a through-cut that keeps
  both sides, then the one-segment bevel with face-weighted normals. It is the only panel-line method
  (`aetheria-release:ruling:panel-lines-are-geometry`). Its text names the superseded cleanup ruling; the
  weld rule that applies to its seams is now `weld-owner-local-corners-kept`.
- `brush-tree:ruling:no-unownable-tools-in-loop` (Operator): everything in the loop is open source we can
  build and patch. This now excludes Shewchuk's Triangle, whose licence bars commercial use.
- `brush-tree:ruling:primary-form-is-the-hand-cage`, `:representation-per-hull`, `:shippable-part-bar`,
  `:openscad-target`, `:brokkr-beats-blender-mcp`, `:cli-not-mcp`, and the defaulted rulings on the
  Blender sink, `run`, docs lookup, look files, the per-ship tree `.cc`, persistence through
  cultcache-rs, the Package path, Studio and impostors: unchanged from r3.
- `brush-tree:ruling:settled-direction-2026-10-10` still says "mesh CSG is the main representation". r4
  agrees in substance (every production part lowers to a mesh and all detail is mesh booleans) but its
  primary form for continuous hulls is a subdivision cage, which `representation-per-hull` already
  ruled. Self holds a draft superseding text that states this; until it is admitted, read "mesh CSG" as
  "meshes and mesh booleans, over a cage or kernel primary form".

## What changed from r3, in one paragraph

r3 had one weld rule (the surface with larger normal curvature across the loop owns the whole loop),
detail as cut or split only, an open question about who evaluates the cage, and no answer to where the
weld runs. Spike rounds 1 to 3 (`spike-boolean-weld.md` on `spike/boolean-weld` @ db2c162) showed that
curvature across the loop picks the wrong owner for every cylinder cut, that a flat split's seam must stay
on the cutter's plane, and that ownership must be decided per stretch with corners protected. The operator
then ruled the three modes, the local owner with corners kept, Blender as the cage evaluator, and a live
result object fed by a Rust wheel. So in r4 Blender owns evaluation and finishing, Geometry.Csg owns
everything between, and the authoring buffer is Blender objects that commit into the typed tree.

## What the pipeline turns a brush tree into

**The tree** is one typed document per ship (`tree-store-per-ship-cc`). Every part declares its
representation, `cage` or `kernel`, and carries an ordered detail list. Each entry names a brush, its
mode (`add`, `subtract`, `split`), an enable flag and a bevel weight. A brush is a closed manifold mesh:
either a kernel primitive lowered alone or a mesh authored in Blender (a polyhedron in the text).

**A `cage` part** (continuous body, Dexter Quiet):

1. **Primary form: the cage primitive.** Control points, quad and triangle faces, edge crease weights,
   the mirror plane, and her UVs if she has unwrapped it. She authors it in Blender; a commit reads the
   cage object into a new revision against its base revision. A commit is refused when a crease chain is
   open and does not end on the mirror plane.
2. **Evaluated mesh, by Blender.** The cage object's own Mirror and Subdivision modifiers, at the declared
   level. Blender is the only evaluator (`blender-evaluates-cages`). Geometry.Csg never subdivides a cage,
   for production or for measurement.
3. **Detail, by Geometry.Csg.** The detail list is folded over the evaluated mesh left to right: `add` is
   union, `subtract` is difference, `split` is difference plus intersection kept as two pieces sharing one
   seam loop. A disabled entry stays in the tree and is not applied; that is authored state, not a skip.
   Every intersection loop is welded by the rule below. The edges each brush creates take its bevel
   weight; per-edge weights authored on the brush mesh carry onto the edges it creates; the cage's crease
   weights carry through as bevel weights. Detail never moves the cage, and outside the weld band the
   output's vertices are the evaluated mesh's vertices, unchanged.
4. **Finishing, by Blender.** The result object's own stack: Bevel (one segment, weight-limited), then
   Weighted Normal. Nothing in the stack is ever applied.

**A `kernel` part** (mechanical, the squatter mech ship): the polygon kernel builds exact planar faces
with scoped booleans and per-face brush and surface ids; its detail list runs through the same booleans,
weld and finishing stack as a cage part's.

**Both** reach Aetheria the same way (`lowered-hull-through-package`): an object in the ship file,
exported by the existing Package.

### The weld, as ruled

The weld's job is to choose which samples of each intersection curve survive and to clean the band
around it. It never chooses the curve's path.

- **Owner, per stretch.** Along each loop, compare each surface's curvature along the loop,
  `k = II(t, t)` with `t` the loop tangent. Spike round 1 showed this is the reading that matches her
  sentence; curvature across the loop gives the opposite owner for every cylinder. The surface whose
  vertices carry more of the silhouette at that stretch owns it. A planar brush face has `k = 0`, so on a
  flat split or a box cut-in the hull owns every stretch. A small curved brush in a flatter surface owns
  its loop.
- **Spare vertices.** The yielding surface's spare vertices near an owned stretch merge away: loop
  vertices made only by the yielding side's edges merge along the loop into the nearest owner-made loop
  vertex, and yielding-side vertices one ring off the loop merge onto it.
- **Corners survive.** A loop vertex on a hard brush edge (dihedral above a threshold) or on a hull crease
  edge is never a merge source and never moves.
- **The path is fixed.** No weld step moves a loop vertex off the intersection of the two surfaces. A flat
  seam stays on the cutter's plane to float precision. No snapping of the loop onto owner vertices on any
  stretch, curved cutters included.
- **Band vertices move only within their own surface,** by at most the bevel width. This is how a vertex
  that sits almost on the seam (round 3's residual 0.04 to 0.7 deg needles and bevel-clamped edges) is
  resolved: it slides onto the seam inside its own surface, never across it. Whether this applies to the
  owner's own vertices on a flat split is spike round 4's measure and the operator's eye (see "Not yet
  known").
- **Created faces are ours to re-triangulate:** split caps, and brush walls trimmed by the hull, are
  re-triangulated within their own plane by a constrained Delaunay triangulation with the loop, crease
  and brush edges as constraints and interior Steiner points only. The CDT is `spade` or our own; never
  Triangle.
- **Guards.** No collapse or flip inverts a triangle or drops the band's worst angle below the floor. In a
  split, every operation must pass both pieces' guards, so the shared seam stays identical vertex for
  vertex (crack 0).
- **Brush density.** A brush's tessellation along the loop stays near the hull's local density (about a
  quarter to a third of the local edge length, never far finer): round 2's 48-segment port kept fans no
  merge could remove.

Still undefined: equal curvature (spike: ties to the hull), saddles, and the vertex where ownership
switches. Round 3's switch probe keeps a 1.2e-6 deg needle on the owner side.

### What Blender evaluates and what Rust owns

| Step | Owner | Notes |
|---|---|---|
| Cage evaluation (Mirror, Subdivision, crease rules) | Blender, the cage object's own modifiers | `blender-evaluates-cages`; Geometry.Csg reads the evaluated mesh |
| Brush lowering (kernel primitive to mesh) | Geometry.Csg kernel | a Blender-authored brush mesh is read as is |
| Booleans, all three modes | Geometry.Csg, behind a port | boolmesh or manifold-csg; identical outputs in round 1 |
| Weld, re-triangulation, bevel-weight transfer, face provenance | Geometry.Csg | pure mesh math, testable on exported fixtures |
| Result object's mesh | written by the extension from Geometry.Csg's output | derived; never hand-edited |
| Finishing (Bevel then Weighted Normal) | Blender, the result object's own stack | never applied |
| Tree revision | Geometry.Csg tree, through the one commit primitive | the truth at rest |

Blender's Boolean modifier, Weld modifier and Geometry Nodes Mesh Boolean decide no shipped detail. The
nondestructive-weld pass (`nondestructive-weld-in-blender.md` @ 19e2f9b) found that Python cannot
register a modifier and that Geometry Nodes cannot express the guarded sequential collapse or the joint
split guard, so a wheel feeding a result object is the route that keeps one implementation.

### Where the truth is while she edits

The typed tree is the truth at rest. The Blender objects (the cage, the brush collection, the Cuts panel
rows) are its edit buffer. The result object regenerates from the buffer on every change, so it is a
preview of uncommitted edits as well as of committed ones. The shipped lowering comes from a committed
revision only: whatever Package exports must be the result of a revision, and a scene that differs from
its revision is committed first or refused. This keeps `one-truth` with a live, nondestructive loop. How
the dirty check is made is a cut's business. If the operator expects the `.blend` itself to be the
truth, that is a different machine (Blender scene authority, the tree as an export) and needs her ruling
first.

### Distance, collapsed to one definition

r3 defined the cage's distance as distance to its limit surface, which would have needed a limit
evaluator in Geometry.Csg beside Blender's. Under `blender-evaluates-cages` that is a second evaluator. In
r4 there is one mesh distance in Geometry.Csg: unsigned distance to a closed mesh, signed by winding
number. A cage's distance is that distance to Blender's evaluated mesh at a declared measuring level; a
Blender-authored brush's is the same distance to its own mesh. Kernel primitives keep their analytic
distance in `field.rs`. Mesh distances serve measurement only (heatmaps, scores, fit residuals); they
have no cheap bound away from the surface, so they are refused in any field composition and in sphere
tracing.

### Authority map (r3 to r4)

- **Owner of evaluation:** Blender. Geometry.Csg is no longer a candidate cage evaluator; the r3
  `one-subdivision-rule` question is closed.
- **Owner of detail and the weld:** Geometry.Csg, run in Blender by the extension, and run headless by
  the same code for the shipped lowering.
- **Owner of finishing:** Blender's Bevel and Weighted Normal on the result object.
- **Inputs:** the cage object's evaluated mesh; the brush objects and their Cuts rows; the tree revision.
- **Outputs:** the result object's mesh (with bevel weights, face provenance and UVs), and scores.
- **Derived state:** the evaluated mesh, brush meshes, boolean pieces, the welded mesh, the result
  object, heatmaps and renders. Cache only.
- **Forbidden writers:** Blender's Boolean and Weld modifiers and Geometry Nodes deciding shipped detail;
  hand edits to the result object; any applied modifier; a Rust subdivision evaluator; a research
  generator writing a production cage; the "curvature across the loop" owner and loop snapping (both
  demoted by the spike and the ruling).
- **Shared paths:** her edit in Blender, a model's script through `brokkr-ctl blender run`, and a
  research generator's candidate all reach the tree through the one commit primitive. The live preview
  and the shipped lowering call the same Rust entry point. All three brush modes and both part
  representations use the same booleans and weld.
- **Deletion line:** r3's `weld-rule` (across-loop curvature, one owner per loop), `detail-is-boolean`
  (cut and split only) and `one-subdivision-rule` (owner open) leave the target. The cage limit-surface
  distance leaves Geometry.Csg's plans. The spike's Triangle dependency and its Python weld are scratch
  and do not carry.

### Owners, inputs, outputs, mock points

| Owner | Inputs | Outputs | Mock point |
|---|---|---|---|
| Tree (Geometry.Csg) | text, a cage object or brush objects, through the one commit primitive | typed tree revision | in-memory store |
| Cage evaluator (Blender) | cage object at a declared level | evaluated mesh | exported fixtures (no Bevel) |
| Brush lowering | kernel primitive or authored mesh | closed brush mesh | the kernel, per brush |
| Boolean | evaluated mesh, brush mesh, mode | pieces with per-corner provenance | trait; boolmesh or manifold-csg |
| Weld | pieces, provenance, curvature along the loop | welded pieces, loop edges with bevel weights | pure mesh math |
| Extension (Blender) | cage, brush collection, Cuts rows | result object's mesh | the Rust entry point, called headless |
| Scorer | two meshes | the bar's numbers | pure mesh math, no Blender |
| Research generators | a reference | candidate cage | port; never a production writer |
| Brokkr bridge | intents from `brokkr-ctl` | receipts, commits, exported fixtures | per `blender-transport` |

## The hand cage

`docs/research/dexter-quiet-cage/` @ d426f86 (note @ 4b55c58): half hull of 29 vertices and 25 faces (19
quads, 6 triangles); nine creases that the mirror closes into one loop round the wing rim. At level 3 it
evaluates to 3,154 vertices and 3,152 quads with 31 irregular vertices and no UVs. It is the production
primary form and the yardstick research generators are scored against (`primary-form-is-the-hand-cage`),
with the cage bar unchanged from r3: at most about 200 faces, at most 24 % triangles, closed creases, and
a watertight level-3 limit mesh with at most 62 irregular vertices.

## Not yet known (owed before or during the next cuts)

- **The flat seam's last needles.** Round 3 kept the seam on the plane and reached crack 0, but a
  boolean-inserted seam vertex almost on a hull vertex leaves a 0.04 to 0.7 deg triangle and
  bevel-clamped edges, so her uniform Longinus groove is not reached. Round 4 slides such vertices onto
  the seam within the hull's surface. On a flat split those are the owner's own vertices, and her words
  were "they survive"; a moved vertex survives in identity, not in position. Her eye on the round-4 render
  decides whether that reading holds.
- **Add mode.** No union has been run. A union's loop is a concave edge; the same owner rule and guards
  apply, and the brush's outer faces are its own surfaces.
- **Which boolean kernel.** boolmesh (pure Rust, MPL-2.0, 14 s build) and Manifold through manifold-csg
  (Apache-2.0, C++ fetched at build, 89 s) gave identical output on all 11 cases. A per-platform Blender
  wheel favours pure Rust; Imagination's lean is boolmesh behind the port, decided by the first cut, not
  here.
- **The extension wheel's build.** Per-platform wheels for the Extensions platform (windows-x64,
  macos-arm64, linux-x64 at least), Blender's pinned Python, GPL-3.0-or-later for the extension: no cut
  has built one.
- **How a `cage` part and a `kernel` part meet** on one hull: presumably `add` with the same weld;
  unmeasured.
- **Text for a cage part and its detail list.** `subdivision_cage(points, faces, creases, mirror, uv)`
  followed by the ordered detail entries. OpenSCAD renders neither the limit surface nor the weld, so cage
  parts and detail modes sit outside the "OpenSCAD renders it the same" half of `text-round-trips`.
- **UVs on created faces.** Her unwrap rides through Subdivision and the booleans as UV0; split caps and
  trimmed brush walls need placement that keeps UV0 unique (`aetheria-release:ruling:hull-paint-mask-texture`
  samples the livery mask on UV0).

## Research it rests on

All in GameCult.Geometry.Csg `docs/research/` on `eureka/brush-tree` unless named:

- `spike-boolean-weld.md` on `spike/boolean-weld` @ db2c162: rounds 1 to 3, the along-loop owner, the
  flat seam on the plane, the cap CDT, local ownership with corners kept, the kernel comparison.
- `nondestructive-weld-in-blender.md` @ 19e2f9b: modifier routes, Geometry Nodes limits, Hard Ops and
  Boxcutter cleanup (distance welds, no ownership rule), Manifold timings in Blender.
- `boolean-cleanup-prior-art.md` @ 34cccf3: no named precedent for the rule; Manifold's collapse guard;
  ownable kernels.
- `detail-on-subd-prior-art.md` @ c513992: cut into the evaluated mesh keeps the cage independent.
- `cage-connectivity-prior-art.md` @ 492f83a: no open method reaches a coarse quad cage at this quality.
- `dexter-quiet-cage/` @ 4b55c58, `sdf-authoring-text-prior-art.md` @ 6a575d2,
  `subd-cages-mixed-hulls-and-open-kernels.md` @ 390db63, `shippable-bar/`, `mesh-probe-run1/` to
  `mesh-probe-run7-im-field/`, `openscad-evaluators-and-csg-export.md`,
  `primitive-seams-and-sdf-bevel-meshing-prior-art.md`, `brush-surfaces-and-sdf-bricks-prior-art.md`,
  `octahedral-impostors-prior-art.md`: as in r3.
