# Brush tree: target (r3)

Campaign `brush-tree`, owned by the Aetheria/Ghostlight Self. Drafted by Imagination
(`imagination-brush-tree-target-r3`, session `self-2026-10-11-ag2`) on 2026-10-12.
It supersedes r2 (`a7879dad`). This page holds the ends, not the means: no cut plan. The typed
`brush-tree:target:r3` holds the invariants, the not-in-scope list and the canonical implementations;
this page holds why, the authority map, and what is still unknown.

- **Repos:** `GameCult/GameCult.Geometry.Csg` (the tree, the cage evaluator, the kernel, booleans and the
  weld, the scorer), `GameCult/Brokkr` (the agent's hands in Blender), `GameCult/Aetheria` (the first
  consumer).
- **Working branch:** `eureka/brush-tree`.

## The rulings this target rests on

Read them in the mind by id; their operator quotes are the authority, not this page.

- `brush-tree:ruling:hand-cages-enter-the-tree` (Operator, 2026-10-12): a continuous hull's primary
  form is an artist's cage, entered as a tree primitive with its distance defined once in Geometry.Csg;
  detail is cut into its evaluated surface. Automatic cage generation is research and gates nothing.
- `brush-tree:ruling:boolean-cleanup-tighter-curve-wins` (Operator): detail is boolean cuts into the
  evaluated hull, and the weld cleanup is automated by her rule. Her words: "the surface with the
  tighter curve defines the silhouette of the cut, and the spare vertices that come from the flatter
  surface all get merged away."
- `brush-tree:ruling:panel-lines-by-split-boolean-r2` (Operator): a panel line is a through-cut that
  keeps both sides; the stack's one-segment Bevel and Weighted Normal turn the split into a seam. The weld
  rule applies to its seams too. It is the only panel-line method: the operator chose geometry over
  parallax decals (`aetheria-release:ruling:panel-lines-are-geometry`), so hull panel lines are in this
  campaign's scope.
- `brush-tree:ruling:primary-form-is-the-hand-cage` (Defaulted): research generators are scored against
  the hand cage's limit surface, not against a masked or smoothed scan.
- `brush-tree:ruling:representation-per-hull`: cages for continuous bodies like Dexter Quiet, primitives
  for mechanical hulls like the squatter mech ship.
- `brush-tree:ruling:shippable-part-bar`, `:no-unownable-tools-in-loop`, `:openscad-target`,
  `:brokkr-beats-blender-mcp`, `:cli-not-mcp`, and the defaulted rulings on the Blender sink, `run`, docs
  lookup, look files, the per-ship tree `.cc`, persistence through cultcache-rs, the Package path,
  Studio and impostors: unchanged from r2.
- `brush-tree:ruling:pursue-sdf-composition-remeshing` and `:spike-sdf-smin-to-cage`: still in force,
  but narrowed by `hand-cages-enter-the-tree`. SDF composition with automated remeshing is one research
  generator among the cage-connectivity candidates, not the production path.

## What changed from r2, in one paragraph

r2 made the SDF composition the authority for a continuous hull's shape and derived a fitted cage from
it, with the operator's hand cage as the measuring stick. Two findings ended that. The
cage-connectivity pass (`cage-connectivity-prior-art.md` @ 492f83a) found no open method that reaches
a coarse quad cage at the hand cage's quality. Every method starts from a dense mesh, and only
Lavoue 2009 reports output at about 200 faces, with n-gons and high valence accepted. The operator then
ruled her own cages into the tree, and named her detail practice: boolean cuts into the subdivided form,
then a weld she does by a rule simple enough to automate. So in r3 the cage is authored, not derived.
The field leaves the production path for continuous hulls. The open engineering problem moves from
generating connectivity to cleaning booleans on a curved evaluated surface.

## What the pipeline turns a brush tree into

**The tree** is one typed document per ship (`tree-store-per-ship-cc`). Every part, meaning a top-level
branch, declares its representation, `cage` or `kernel`. The declaration is authored, never inferred.
Each part carries a detail list of cutters, each tagged `cut` (remove) or `split` (keep both sides).

**A `cage` part** (continuous body, Dexter Quiet):

1. **Primary form: the cage primitive.** The tree holds control points, faces (quads and triangles),
   edge crease weights and the mirror plane. She authors it in Blender. A `brokkr-ctl` commit reads the
   cage object and commits it as a new revision of the part against its base revision. After that the
   Blender cage object is a projection, and an edit to it is a proposed commit, as for any brush proxy.
   A commit is refused when a crease chain is open and does not end on the mirror plane (her finding:
   open crease paths give "horrible geometry" in Blender's Catmull-Clark).
2. **Evaluated mesh, derived.** Mirror, then Catmull-Clark to the limit surface at a declared level,
   with Blender's crease rules (`one-subdivision-rule`). Who runs this evaluation is question
   `cage-evaluator`.
3. **Detail, derived from cutters.** Each cutter is a kernel brush, lowered alone to a closed mesh.
   - `cut`: the evaluated mesh minus the cutter (gun ports, vents, intakes).
   - `split`: the evaluated mesh minus the cutter, plus the evaluated mesh intersected with the cutter,
     kept as two pieces that share one seam loop. This is how every panel line is made; there is no
     decal path.
   Every intersection loop is then welded by the rule below, and its edges get the bevel weight.
   Detail never moves the cage. Outside a band around each loop, the output's vertices are the evaluated
   mesh's vertices, unchanged.
4. **Shipped stack on the output object:** Bevel (one segment, limited by weight: the crease loops
   plus every cut and split loop), then Weighted Normal. Seams for UVs lie on closed crease loops, part
   boundaries and split loops, so every panel is its own island.

**The weld rule**, as specified for the spike (`boolean-cleanup-prior-art.md` @ 34cccf3 found it
nowhere under any name):

- Along each intersection loop, compare the two surfaces' normal curvature across the loop. The across
  direction is the surface tangent perpendicular to the loop tangent.
- The surface with the larger magnitude owns the loop. The loop's vertices are sampled at the owner's
  resolution and lie on the owner's surface.
- The yielding surface's vertices within one ring of the loop, plus any of its loop vertices that are
  not owner vertices, collapse onto the nearest owner loop vertex.
- A collapse is refused if it flips a triangle or drops the worst angle below a floor. This is the
  Manifold `CollapseEdge` guard (same file, s.1).
- In a `split`, the two pieces weld their shared loop identically, so the seam stays closed vertex for
  vertex.

Undefined so far, and named as the spike's failure cases: equal curvature, saddles where the across
direction changes sign, a loop crossing a crease, and an ownership switch partway along one loop.

**A `kernel` part** (mechanical, the squatter mech ship): unchanged from r2. The polygon kernel builds
exact planar faces with scoped booleans, a one-segment bevel on hard edges, face-weighted normals and
UVs from each brush's declared charts. Its cutters use the same boolean and weld as a cage part's
detail.

**Both** reach Aetheria the same way (`lowered-hull-through-package`): an object in the ship file,
exported by the existing Package. Nothing reads an evaluated mesh, cut mesh or render back as truth.

### Distance for a cage primitive, stated honestly

`one-distance-per-primitive` holds for the cage. Its distance is defined once in Geometry.Csg as the
unsigned distance to the limit surface, signed by winding number. The cost is the honest part.

- The limit surface has exact evaluation: Stam 1998, OpenSubdiv `LimitStencilTable`, and run 3's
  `X = S c`, linear in the cage. A closest point on it comes from a Newton search
  (Marinov and Kobbelt 2005). So the distance is computable (`subd-cages-mixed-hulls-and-open-kernels.md`
  @ 390db63, s.1).
- No source gives a **cheap distance bound** away from the surface, that is, a Lipschitz-safe lower
  bound usable for sphere tracing, Newton projection from afar, or smooth-min composition with other
  primitives. The r1 field assumed one for every primitive.
- So the cage primitive is refused inside any field composition (smooth union, hard `max` crease) and in
  sphere tracing (`no-silent-skips`). Its distance serves measurement only: heatmaps, scores and fit
  residuals, evaluated near the surface from a dense limit sample. Nothing in the production path needs
  more. A bound, if one is ever needed, is research.

### Where SDF composition still has a role

- **As a research generator.** An SDF program with smooth-min, remeshed and refit to a cage (runs 4-7),
  is one candidate source of cage connectivity. It is scored like any other candidate.
- **As the kernel brushes' distance.** `field.rs` stays the one distance for kernel primitives, for
  heatmaps and scores.
- **Not as a part representation.** No production part is a `field` part, and smooth union leaves the
  production vocabulary. A generator's output, if it ever meets the bar, enters as a cage, and so does
  every continuous hull.

### Authority map (r2 to r3)

- **Owner of a continuous hull's primary form:** the cage primitive in the tree. The field is no longer
  an owner. The cage is no longer derived from the field; it is authored and committed.
- **Inputs:** the operator's cage object in Blender (through the commit primitive only), the part's
  cutter brushes.
- **Outputs:** the lowered part object (evaluated, cut, split and welded mesh, with bevel weights), and
  scores.
- **Derived state:** the evaluated mesh, the cutter meshes, the cut mesh, UV islands, heatmaps, renders.
  These are cache only, regenerated per revision.
- **Forbidden writers:** the SDF program, the cage fitter and any remesher writing a production cage.
  They write research artifacts only, and a research cage enters only by a commit like any other. Also
  forbidden: Blender's Boolean modifier, or hand edits to the lowered object, deciding the shipped
  detail.
- **Shared paths:** the operator's cage edit, a model's script edit and a research generator's
  candidate all enter through the one commit primitive. Cut-in and split use one boolean and one weld.
  Kernel parts' cutters use the same boolean.
- **Deletion line:** r2's "cage connectivity generator" and "cage fitter" leave the production owner
  table and become research ports. `field` leaves the per-part representation enum. Smooth union is not
  added to the tree vocabulary.

### Owners, inputs, outputs, mock points

| Owner | Inputs | Outputs | Mock point |
|---|---|---|---|
| Tree (Geometry.Csg) | text or a cage object, through the one commit primitive | typed tree revision | in-memory store |
| Cage evaluator | cage primitive, level | evaluated mesh (mirror applied) | trait; Blender's output as the oracle (`cage-evaluator`) |
| Cutter lowering | cutter brush | closed cutter mesh | the kernel, per brush |
| Boolean | evaluated mesh, cutter mesh, `cut` or `split` | pieces, intersection loops with both sides' faces | trait; kernel chosen by the spike |
| Weld | pieces, loops, the two surfaces' curvature | welded pieces, loop edges with bevel weight | pure mesh math |
| Kernel | kernel part | mesh with per-face brush and surface ids | trait |
| Scorer | two meshes | the bar's numbers | pure mesh math, no Blender |
| Research generators | a reference (scan or SDF program) | candidate cage | port; never a production writer |
| Brokkr bridge | intents from `brokkr-ctl` | receipts, cage reads, objects in the ship file | directory store or loopback, per `blender-transport` |

## The hand cage

**What it is** (`docs/research/dexter-quiet-cage/` @ d426f86, note @ 4b55c58): half hull of 29 vertices
and 25 faces (19 quads, 6 triangles); about 50 faces mirrored. Nine creases form one chain that the
mirror closes into a loop round the wing rim. At level 3 it evaluates to 3,154 vertices and 3,152 quads,
with 31 irregular vertices and no UVs. Against the scan (vertex to nearest vertex, % of the 1.492
diagonal): cage to scan mean 0.88, p95 2.04, max 3.11; scan to cage mean 1.29, p95 4.12, max 6.03.
Those numbers mix her declared liberty with detail the cage omits by design. They describe the
reference; they are not a bar any production output is held to.

**It is the production primary form, not only the yardstick.** Production fidelity is by construction:
away from detail loops, the shipped part is the cage's limit surface.

**Research generators are scored against it** (`primary-form-is-the-hand-cage`). A candidate's
evaluated limit surface is compared with the hand cage's (Mirror, limit, no Bevel) vertex to nearest
vertex both ways, at half to double 3,154 vertices, and by three-axis silhouette IoU. Every measurement
reports the candidate's source against its reference and the candidate cage against its own source
separately, besides the end-to-end number; run 7 lost a spike to an unattributed number. The scan is the
reference only for the hand cage's own recorded liberty. A candidate is interesting when it is no worse
than the hand cage's own spread and meets the cage bar: at most about 200 faces (4x), quads and
triangles only with at most 24 % triangles, closed creases, and a watertight level-3 limit mesh with at
most 62 irregular vertices. Meeting the bar makes a candidate committable as a cage. It gates nothing
else.

## Not yet known (owed before or during the next cuts)

- **The weld rule's behaviour on real geometry.** It has never been run. The spike brief is
  `spike-boolean-weld.md` (Self's scratch); its measures and failure cases decide whether the rule ships
  as stated, needs a tiebreak, or needs the cutter tessellated to the hull's density.
- **Which boolean kernel:** Manifold through `manifold-csg` (Apache-2.0, C++ underneath, with provenance
  and its own degenerate cleanup), boolmesh (pure Rust, MPL-2.0, released 2026-10-11, 0 % doc coverage),
  or an extension of the crate's own kernel. The spike measures the first two; the crate's kernel is
  planar-convex today.
- **Who evaluates the cage** for the lowering: question `cage-evaluator`.
- **Split pieces' interior caps:** a through-cut of a closed hull leaves cross-section caps inside both
  pieces. Whether they are kept (closed pieces, hidden triangles) or dropped (open pieces) depends on how
  Bevel and Weighted Normal treat the open boundary. The spike probes it.
- **How a `cage` part and a `kernel` part meet** on one hull. Under r3 a union with the same boolean and
  weld is the natural candidate, but nothing has measured it.
- **Text for a cage part.** It prints as a polyhedron-like `subdivision_cage(points, faces, creases,
  mirror)`. OpenSCAD would render the cage's control polyhedron, not its limit surface, so cage parts sit
  outside the "OpenSCAD renders it the same" half of `text-round-trips`, as smooth-min parts did in r2.

## Research it rests on

All in GameCult.Geometry.Csg `docs/research/` on `eureka/brush-tree`:

- `dexter-quiet-cage/` @ 4b55c58: the reference cage, the primary-form note, her screenshots (cage files
  @ d426f86).
- `cage-connectivity-prior-art.md` @ 492f83a: no open method reaches a coarse quad cage at this quality.
- `boolean-cleanup-prior-art.md` @ 34cccf3: no named precedent for the weld rule; Manifold's collapse
  guard; Adaptive Mesh Booleans' failure modes; ownable kernels.
- `detail-on-subd-prior-art.md` @ c513992: cut into the evaluated mesh is the only option that keeps the
  cage independent and regenerable; support loops grow the cage.
- `sdf-authoring-text-prior-art.md` @ 6a575d2: no SDF tool round-trips a typed tree through text.
- `subd-cages-mixed-hulls-and-open-kernels.md` @ 390db63: limit evaluation, closest point, no cheap
  bound.
- `shippable-bar/`, `mesh-probe-run1/` to `mesh-probe-run7-im-field/`,
  `openscad-evaluators-and-csg-export.md`, `primitive-seams-and-sdf-bevel-meshing-prior-art.md`,
  `brush-surfaces-and-sdf-bricks-prior-art.md`, `octahedral-impostors-prior-art.md`: as in r2.
