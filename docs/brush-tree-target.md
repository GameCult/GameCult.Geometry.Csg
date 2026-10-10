# Brush tree: target

Campaign `brush-tree`, area geometry, owned by the Aetheria/Ghostlight Self
(`aetheria-release:ruling:brokkr-ctl-job-to-ag-self`). Drafted by Imagination
(`imagination-brush-tree-target`, session `self-2026-10-10-ag2`) on 2026-10-10.
This is step 0: the ends, not the means. It contains no cut plan.

- **Title:** Brush tree: OpenSCAD-shaped CSG trees authored in Blender through `brokkr-ctl`.
- **Repos:** `GameCult/GameCult.Geometry.Csg` (the truth and the kernel),
  `GameCult/Brokkr` (the agent's hands in Blender), `GameCult/Aetheria`
  (the first consumer), and `GameCult/CultLib`, only if a ruling sends work
  there (the cultcache-py directory store, Q `blender-transport`).
  All four remotes are GitHub today; Aetheria moves to Forgejo under
  `aetheria-release:ruling:forgejo-primary-github-mirror`.
- **Working branch:** `eureka/brush-tree` in each repo it touches.
- **This document's home:** `GameCult.Geometry.Csg/docs/brush-tree-target.md`.
  The crate owns the truth the campaign builds, and two of the four research
  passes already live beside it in `docs/research/`.

## Rationale

The operator rebuilds Tripo-generated hard-surface hulls by hand: retopology,
seams and bevels, at about 30 minutes per part. The campaign replaces that with
a collaborative loop in Blender. The work is split by what each party does
well:

- **The operator** points at part of the messy hull, using her Edit Mode
  selection plus the viewport framing.
- **The model** proposes a parametric form, or builds the one she names ("these
  pipes are tubes", "a sphere, solidified, with a prism cut out"). It does the
  naming, grouping, symmetry and composition.
- **A classical fitter** does the numbers: least-squares or RANSAC primitive
  fitting, plus GlobFit-style relations.
- **Feedback** is a deviation heatmap plus a viewport render, iterated.

The output is a typed CSG brush tree. From that one tree come the lowered mesh,
its UVs, its topology near cuts and its microbevels.

Why this shape, by the evidence:

- **Model fluency.** CAD-Recode and MeshCoder emit code (CadQuery, Blender
  Python) precisely because language models write code fluently
  (CultLib `docs/research/inverse-procedural-modelling-prior-art.md` §1,
  6bdc23c9). OpenSCAD is a CSG tree written as text, with a large public
  corpus.
- **Text-only loops fall short.** BlenderGym shows the best VLM still far
  behind humans on geometry editing (Chamfer 1.120 vs 0.334, same doc §4).
  BenchCAD reports single-literal errors at high IoU. That is why numbers go to
  a fitter and judgement goes to the model and the operator, not to unaided
  generation.
- **Failure without coherence.** VibeGeometry's recorded failure was "local
  plausibility without global coherence" (same doc §0b). The defence here is a
  typed tree with one owner, scored against the target by one distance function.
- **Brushes are the durable design surface.** The crate's own doctrine says "the
  brush tree is the authority; the mesh is cache and evidence"
  (`docs/realtime-csg-doctrine.md`, Core Model). This campaign makes that true
  of persisted state, not only of the in-memory assembler.
- **The bar is the Blender MCP servers, and Brokkr exceeds it.** They offer
  viewport sight, code execution and API docs, but none reads selected Edit Mode
  geometry, and none has auth or admission (Brokkr
  `docs/research/blender-mcp-capability-bar.md` §A(b), §B(b), f97d4dc). Brokkr
  already has typed intents, receipts and admission on its Unity side
  (`docs/provider-contract.md`, Admission).

## Body facts the target rests on (probed 2026-10-10)

- **GameCult.Geometry.Csg** (main at `5b5dc34`):
  - Five primitives: Box, OrientedBox, CylinderZ, DomeCapZ, FloretArm (`src/brush.rs`).
  - The polygon kernel runs CSG only for Box and OrientedBox cutters. It skips
    other cutters with `SubtractIgnoredForNonBox` / `IntersectIgnoredForNonBox`
    (`src/assembler.rs` ~803, ~836).
  - The assembler and `field.rs` consume one flat ordered stream in which
    Intersect is global. `CsgTree` branches exist in `src/tree.rs`, but the
    assembler does not honour them as scoped nodes.
  - `field.rs` lowers the stream to a signed-distance bound for every op on
    every primitive. It has no smooth blend.
  - `TriangleMesh` gives every quad 0-1 UVs. It carries per-triangle material
    only: no brush id, surface id, smoothing or tangent (`src/mesh.rs`).
  - `Brush` and `Primitive` derive no serde.
  - The "CultCache records" in `src/cult_geometry.rs` are `rmp_serde`
    msgpack tuples with schema-string constants. They are not written through
    CultLib's `cultcache-rs`, and no record holds brushes.
- **Brokkr** (main at `f97d4dc`):
  - The Blender add-on admits eight object-level commands
    (`surfaces/blender/brokkr_bridge/blender_target.py:402-423`). Its snapshot
    reports mesh counts only (`:568-575`). It has no render, no mesh read, no
    Edit Mode read and no code execution.
  - Its store is the cultcache-py single-file store. cultcache-py has no
    directory store (`CultLib/packages/cultcache-py/src/cultcache_py/stores.py:22,85`).
  - Its optional CultNet server binds 127.0.0.1 with no auth token
    (`blender_target.py:288-350`).
  - `brokkr-command` is a .NET, Unity-only caller (`brokkr-command/Program.cs`).
    `brokkr-ctl` does not exist.
  - The Unity side's rulings F4 to F6 settle a file transport, a sink that is
    off by default, and single-use command ids
    (`docs/brokkr-adoption-cut.md`, Rulings).
- **CultMath:** `BoundedLeastSquares` exists in C#
  (`CultLib/packages/cultmath/src/CultMath/BoundedLeastSquares.cs`).
- **Mesh probe:** the probe running under rulings `mesh-probe-exploit-not-measure`
  and `mesh-probe-both-vocabularies` has not written `run1/RESULT.md` yet.
  Its scratch `demo-hull.scad` already shows the model reaching for top-level
  variables, `module`, `hull()`, `minkowski()`, `polyhedron`, `mirror` and
  `cylinder(r1, r2)`.

## Design truths the campaign produces

1. Each hull rebuilt through the loop exists as one typed brush-tree document in
   CultCache. Everything else is derived from it: text, mesh, UVs, bevels,
   heatmap, projections into Blender.
2. The model reads and writes that tree as OpenSCAD-shaped text. The operator
   reads and writes it through Blender. Both edits land through one commit path.
3. An agent drives Blender with `brokkr-ctl blender look | selection | fit
   <primitive> | run <script>`. Every call is a typed, admitted Brokkr intent
   with a receipt, and `--help` is the schema.
4. Geometry.Csg lowers the tree to a mesh whose faces know their brush and
   surface. The mesh carries the UVs and seams the brushes declare, and smooth
   microbevels at cuts derived from the same tree's field.
5. Aetheria receives the lowered hull through its existing ship pipeline.

## Invariants

- **I1. One truth.** The typed CultCache brush tree is the only authority for a
  hull's shape, surfaces and structure. OpenSCAD-shaped text, Blender objects,
  meshes, fields, heatmaps and impostors are derived. None of them is read back
  as truth except through I3.
- **I2. Text is a surface, not a store.** The OpenSCAD-shaped syntax is an
  authoring and lowering surface. A tree prints to text deterministically.
  Printing a tree and parsing it back yields the same tree (round-trip). Any
  text the parser accepts, which also renders in OpenSCAD, means the same solid
  in both. Where our extensions add surface data, OpenSCAD ignores it and still
  renders the same solid.
- **I3. One commit primitive.** Every change to a tree goes through one commit
  that names the revision it was based on. That covers parsed text, an operator
  edit in Blender, an accepted fit and a scripted change. A stale base is
  refused, never merged silently. No second writer exists: no Blender-side
  cache, no CLI-side tree and no daemon copy.
- **I4. One distance per primitive.** Each primitive's signed distance is
  defined once, in Geometry.Csg. The fit residual, the deviation heatmap, the
  microbevel blend and field-based scoring all evaluate that one definition. A
  fitter that minimised a different distance would fit a shape the kernel does
  not build.
- **I5. No silent skips.** Every primitive and operation the authoring surface
  accepts is honoured by every lowering that claims to build the tree: the
  polygon kernel and the field. Anything a lowering cannot honour is refused at
  parse or commit, never dropped with a warning.
- **I6. The tree is a tree.** A branch's operation applies to its children only.
  Nested `difference` inside `union` means what OpenSCAD means by it. The flat
  global-Intersect stream may survive as an internal lowering, but it cannot
  change meaning.
- **I7. Brushes own their surfaces.**
  - Each brush declares its surfaces: material, UV parameterisation and seams,
    smoothing, and bevel or blend radius.
  - Every emitted face carries the id of the brush and the surface it came
    from. Output UVs are evaluated from that surface's parameterisation.
  - No face gets default 0-1 UVs.
  - Who owns a cut face is one explicit policy (Q `cut-face-surface`), not
    array order.
- **I8. Topology is regenerable.** The tree carries enough to regenerate good
  topology wherever a consumer needs it, without hand retopology: edge flow on
  curved primitives, strips at cuts, and LOD. The mesh is a cache. It is never
  hand-edited and never read back.
- **I9. Microbevels come from the tree.** The fine bevels at brush cuts are
  derived from the same tree's signed-distance field, smooth-min style, with
  radii that are brush or tree parameters. The field stays a distance bound,
  never an overestimate, because sign tests and Newton projection depend on
  that (`src/field.rs` header).
- **I10. Stable identity.** Brushes and surfaces keep their identity across
  print, parse and Blender edits (Q `brush-identity`). A receipt, a fit or a
  heatmap that names a brush still names the same brush after a round-trip.
- **I11. Brokkr's authority map holds.**
  - Blender owns Blender truth: the source mesh, selection, viewport and undo.
  - Brokkr owns the contract, admission and receipts.
  - `brokkr-ctl` is a caller. It owns no state, no policy and no receipt
    ledger (`docs/agent-access-cut.md` Cut 5, authority map).
  - The exit code derives from the receipt, never from "the write succeeded".
  - Agent commands are off until the operator enables them, as on the Unity
    side (F5).
  - Command ids are single-use (F6).
  - Every mutating Blender command is one undo step.
- **I12. Brokkr is better than the MCP bar, not equal to it.** Brokkr matches
  the bar on viewport sight, code execution and API docs. It reads Edit Mode
  selection live. On top of that it adds typed admitted intents with receipts,
  undo-safe transactions, and a transport that does not admit arbitrary local
  processes.
- **I13. A CLI, not an MCP server.** The agent's hands are a stupid-simple CLI
  whose `--help` is the schema, and whose outputs are paths and plain text.
- **I14. Source is evidence.** The Tripo mesh is read-only reference. The loop
  never edits it. The Tripo-mesh-as-bake-source rule of the Aetheria release
  map stands.
- **I15. One consumer path into Aetheria.** The lowered hull reaches Aetheria
  through the existing ship pipeline, Blender add-on Package into the ship
  `.cc` (`aetheria-release:ruling:schematic-is-designated-mesh`). This campaign
  adds no second exporter.
- **I16. Open and general.**
  - Everything is open source (`eureka-body:ruling:always-open-source`).
  - Geometry.Csg stays a general library with a clean public API. A capability
    a reasonable consumer expects is not cut because Aetheria does not use it.
  - The library does not acquire Aetheria vocabulary.

## Settled direction (rulings in the mind, campaign brush-tree)

- Mesh CSG is the main representation.
- Octahedral impostors are a far-LOD tier only.
- Brick-map marching of interval-pruned tapes stays CultMath research.
- Unity's built-in pipeline is used by choice, with our own shaders. Its
  deprecation is never counted as a cost.

## Not in scope, and not consumers

- **Hull panel decals.** A separate later campaign
  (`aetheria-release:ruling:panel-lines-mesh-decals`).
- **The Aetheria/Hull shader.** It belongs to aetheria-release. This campaign
  emits UVs and normals the shader can use. It does not edit the shader.
- **Brick-map or tape SDF rendering, and runtime raymarching.** These stay
  CultMath research (`docs/cultmath-tape-target.md`, parked).
- **Impostor generation.** It is named as a derived far-LOD tier. Whether this
  campaign builds it is Q `impostor-scope`, recommended out.
- **Unity agent access.** Unity's `brokkr-command` and its intents are not
  consumers and are not changed. `brokkr-ctl blender` must not fork the Unity
  contract.
- **CultCache Studio.** It may display the tree `.cc` like any CultCache
  document. It gains no brush-tree editor in this campaign
  (`aetheria-release:ruling:studio-is-the-authoring-pane` covers hull data,
  not brush authoring).
- **The prefab CDN pipeline and the Unity-Blender sync organ.** Not consumers.
- **Training models.** The loop uses a frontier model with tools it builds and
  uses (`aetheria-release:ruling:mesh-probe-exploit-not-measure`). Learned
  encoders of the CAD-Recode or MeshCoder kind are prior art, not scope.
- **Benchmarking the model's unaided spatial reasoning.** Explicitly not a goal
  (same ruling).
- **VibeGeometry's deleted scene-generation tree.** Read for its scars, not
  revived.

## Canonical implementations

- **The brush tree types, the text printer and parser, the kernel, the field,
  per-primitive distance, and the fitter math (subject to Q `fitting-home`):**
  `GameCult.Geometry.Csg`, Rust.
- **Persistence:** through CultLib `packages/cultcache-rs`, not hand-rolled
  `rmp_serde` tuples.
- **Agent CLI and Blender adapter:** `Brokkr`. `brokkr-ctl` and the
  `surfaces/blender/brokkr_bridge` add-on, over a Blender command contract
  extending `brokkr.blender.command_intent.v0` and `.command_receipt.v0`.
- **Consumer:** `Aetheria`'s `tools/blender/aetheria_ships` add-on, through its
  existing Package.

## Evidence (DocRefs)

- `GameCult/GameCult.Geometry.Csg` `docs/research/brush-surfaces-and-sdf-bricks-prior-art.md` @ df89568
- `GameCult/GameCult.Geometry.Csg` `docs/research/octahedral-impostors-prior-art.md` @ 5b5dc34
- `GameCult/CultLib` `docs/research/inverse-procedural-modelling-prior-art.md` @ 6bdc23c9
- `GameCult/Brokkr` `docs/research/blender-mcp-capability-bar.md` @ f97d4dc
- `GameCult/GameCult.Geometry.Csg` `docs/realtime-csg-doctrine.md` @ 5b5dc34
- `GameCult/Brokkr` `docs/agent-access-cut.md`, `docs/brokkr-adoption-cut.md`, `docs/provider-contract.md` @ f97d4dc
- Pending: the mesh probe's `run1/RESULT.md`. Self commits it into Brokkr or the
  crate's `docs/research/` and cites it once it exists.
