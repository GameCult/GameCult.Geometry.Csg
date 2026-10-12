# Nondestructive weld in Blender 5.2: shipping routes, Geometry Nodes feasibility, precedents, cost

Eyes pass for campaign `brush-tree`, session `self-2026-10-11-ag2`, agent `eyes-bt-gn-weld`, 2026-10-12. Facts with evidence
pointers; "(inferred)" marks reasoning, not observation. No recommendation.

Operator's request, verbatim: "If we can turn this into a modifier then we can go fully nondestructive".
"This" is ruling `brush-tree:ruling:weld-owner-defines-silhouette` (in force, ruled 2026-10-12): at each intersection loop, the
surface whose own geometry shapes the loop keeps its vertices; the other surface's spare vertices near the loop merge away.
Flat cutter on a hull (panel line): the hull owns. Small curved cutter in a flatter surface (gun port, dimple): the cutter
owns. The ruling's equivalent probe is "curvature of each surface along the loop". Spike: GameCult.Geometry.Csg
`spike/boolean-weld` (a507760), `docs/research/spike-boolean-weld.md`, code `spikes/boolean-weld/`. Note: the spike's weld pass
(`py/weld.py`) is Python/numpy over a Rust driver (`src/main.rs`) that calls boolmesh and Manifold, not Rust throughout.

Blender: 5.2.2 LTS (hash d13f752e3b9c) at `C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe`, run headless.

## 1. Ways to ship a live, nondestructive mesh operation in the modifier stack

| Route | Appears in the modifier stack | Native code | Evidence |
|---|---|---|---|
| Geometry Nodes node group on a Nodes modifier | yes, as a Nodes modifier | no (nodes only) | below |
| Node group flagged `is_modifier`, marked as asset | yes, offered as a modifier | no | below |
| Python add-on registering its own modifier type | no | n/a | `register_class` test below |
| Python add-on driving existing modifiers / depsgraph handlers | indirectly | n/a | below |
| C/C++ modifier | yes | yes, Blender fork | below |
| Extensions platform with wheels | not a modifier route | yes, as Python wheels | below |

- **Geometry Nodes modifier.** `obj.modifiers.new(name, 'NODES')` with `.node_group = ng` works headless in 5.2.2 (used
  for every test below). `bpy.types.NodesModifier` carries `node_group`, `bakes`, `properties` and panel-state members
  (printed from `NodesModifier.bl_rna.properties`). In 5.2 `m['Socket_n'] = value` on the modifier raised
  `TypeError: bpy_struct[key] = val: id properties not supported for this type`; a Collection input was therefore set as the
  node's default value in the test, and `NodesModifier.properties` exists as the member to try instead (untested).
- **Modifier-flagged node group.** `GeometryNodeTree.is_modifier` exists in 5.2.2 and defaults False (printed); the 5.3 API
  doc lists it with `is_tool` and `is_mode_*` flags (docs.blender.org/api/5.3/bpy.types.GeometryNodeTree.html). The Add
  Modifier menu and asset-library presentation of such groups was not verified here (searched, not found in sources read).
- **Python cannot register a modifier.** Test: `class M(bpy.types.Modifier): pass; bpy.utils.register_class(M)` raised
  `ValueError: ... (Modifier does not support registration)`. The prior survey lists the registrable classes (Panel, Operator,
  NodeTree, Node, NodeSocket, ...; no Modifier) at `F:\Projects\blender-tooling-surface-prior-art.md` section 1, from
  `bpy.utils.register_class` docs. A community wiki draft proposing Python modifiers shows a nonexistent
  `bpy.types.Custom_Modifier` base (wiki.blender.jp/利用者:Vitorbalbio/PythonModifier); nothing shipped.
- **Depsgraph handlers.** `bpy.app.handlers` has `depsgraph_update_pre` and `depsgraph_update_post` (printed). They run
  around evaluation, not inside the modifier stack; they cannot return a mesh into the stack position (inferred from
  the handler list; not exercised).
- **Custom node tree.** Python can register a `NodeTree`/`Node` (prior survey section 1): Sverchok and Animation Nodes
  are such trees evaluated by their own add-on code, not by the modifier stack. Animation Nodes uses Cython per platform.
- **C/C++ modifier.** Modifier types are registered in Blender's C tables (`ModifierTypeInfo`); no source was read here, so
  this rests on the `register_class` error above ("does not support registration") and general knowledge (inferred).
  Reaching it means a Blender fork.
- **Extensions platform.** Extensions are manifests (`blender_manifest.toml`) with `platforms` (windows-x64, windows-arm64,
  macos-x64, macos-arm64, linux-x64) and `wheels`; compiled code ships as Python binary wheels bundled in the extension and
  built per platform with `--split-platforms` (docs.blender.org/manual/en/5.2/advanced/extensions/python_wheels.html and
  getting_started). The sources read describe no extension point that accepts a native modifier or node. A wheel's code runs
  from Python. Prior survey section 4f: distributed add-ons must be GPL (Extensions platform requires GPL-3.0-or-later).
  Both vendored add-ons below declare `SPDX:GPL-3.0-or-later`.

## 2. Can Geometry Nodes express the rule

### 2a. What exists in 5.2.2 (printed by `dir(bpy.types)`, 274 `GeometryNode*` classes)

Present: `GeometryNodeMeshBoolean`, `MergeByDistance`, `SampleNearest`, `SampleNearestSurface`, `SampleIndex`,
`EdgePathsToSelection`, `EdgePathsToCurves`, `InputShortestEdgePaths`, `EdgesToFaceGroups`, `InputMeshIsland`,
`InputMeshEdgeAngle`, `InputMeshEdgeNeighbors`, `InputMeshEdgeVertices`, `InputMeshVertexNeighbors`, `EdgesOfVertex`,
`CornersOfEdge`, `RepeatInput`, `ForeachGeometryElementInput`, `CaptureAttribute`, `StoreNamedAttribute`, `DeleteGeometry`,
`SetPosition`, `MeshToCurve`, `SplitEdges`, `MeshBevel`, `DualMesh`, `ScaleElements`, `AccumulateField`,
`SDFGridMeanCurvature`, `GetGeometryBundle`, `SetGeometryBundle`, `ClosureToList*`, `Warning`. No class matched `Dissolve*`
or an `EvaluateOnDomain` name by my substring query; the `FieldOnDomain` class exists (HOps' group lists
`GeometryNodeFieldOnDomain`). No node named for surface curvature (second fundamental form) exists in that list; the
only curvature-named class is `SDFGridMeanCurvature` (volume grids).

### 2b. Mesh Boolean node (printed from the node, then run)

- `solver` enum items: `EXACT`, `FLOAT`, `MANIFOLD` (Manifold is in 5.2.2). `operation`: `INTERSECT`, `UNION`, `DIFFERENCE`.
- Inputs: `Mesh 1`, `Mesh 2`, `Self Intersection`, `Hole Tolerant`. Outputs: `Mesh`, `Intersecting Edges`.
- Per solver (socket `enabled`): EXACT shows all four inputs and both outputs; MANIFOLD hides Self Intersection and Hole
  Tolerant and keeps `Intersecting Edges`; FLOAT hides `Intersecting Edges` (linking it raised an error in the test).
- Manual 5.2: Manifold fastest and manifold-only (special case: Difference with a plane); Exact for coplanar/overlap, slower;
  Float lacks overlap support.

### 2c. Headless test on the spike's gun port (run, not just read)

Scripts: `...\scratchpad\eyes-bt-gn-weld\gn_probe2.py`, `q.py`; logs `out\probe_*.txt`. Inputs: `cage_eval.obj` was not found
on disk (searched `F:\Projects` to depth 6), so the test used the spike's own fixtures from the branch: `hull_nobevel.obj`
(3,010 vertices, 3,008 faces after OBJ import, the hull the spike measured) and `port_flank_s16.obj` (the 16-segment gun
port cylinder, 34 vertices). No .blend was opened or saved; factory startup, scene built by script.

Group: Group Input hull -> Store Named Attribute (INT, FACE, `src`=0) -> Mesh Boolean Mesh 1; Collection Info (cutters,
relative transform) -> Realize Instances -> Store Named Attribute (INT, FACE, `src`=1) -> Mesh 2; Boolean DIFFERENCE;
output Mesh -> Store Named Attribute (BOOLEAN, EDGE, `isect`) fed by `Intersecting Edges`.

| case | solver | result verts / faces | `Intersecting Edges` selected | faces by `src` after boolean | time (s) |
|---|---|---|---|---|---|
| port s16 | MANIFOLD | 3,067 / 3,056 | 42 | {0: 3,008, 1: 48} | 0.026, 0.023 |
| port s16 | EXACT | 3,067 / 3,056 | 42 | {0: 3,008, 1: 48} | 0.048, 0.041 |

Observed: the `src` face attribute written before the boolean survives onto the result faces (hull 3,008, cutter 48), so
face provenance is available in nodes without a geometric test. `Intersecting Edges` evaluates on the result mesh and
was stored as an edge attribute. 42 selected edges against the spike's 36 loop vertices: not reconciled (the spike loop is
traced between provenance faces; this selection's definition for the extra 6 edges was not inspected).
Manifold and Exact gave identical vertex and face counts and edge selection on this case.

### 2d. Sketch of the rule in nodes (inferred unless stated)

1. **Provenance and loop.** Face `src` before the boolean (tested) and `Intersecting Edges` (tested) give the loop edges and,
   by edge-to-point evaluation, loop vertices. Per loop vertex, which surface's original edge it sits on (the spike's H/C/both
   test, tolerance 1.5e-6): Sample Nearest or Sample Nearest Surface against the original hull and original cutter geometry
   (both exist as streams before the boolean); compare distances to a tolerance.
2. **Loop ordering and tangent.** Mesh to Curve restricted to the intersecting edges gives ordered splines; Curve
   Tangent / Sample Curve give `t`. Edge Neighbors / Edge Vertices / Vertex Neighbors give local adjacency.
3. **Curvature along the loop, `k = II(t,t)`.** No curvature node exists (2a). Nodes can read normals (Input Normal, Sample
   Index on neighbours) and form finite differences of normal along `t`: `k` approximated by
   `(n_next - n_prev) . t / |p_next - p_prev|` using the original surface's normal sampled at loop points (Sample Nearest
   Surface). The spike used a per-vertex quadric fit over the 2-ring, with hull crease edges counted as infinite curvature;
   the nodes version would be a different estimator. Its noise near creases/saddles is untested. A cutter with known shape has
   analytic `k` (cylinder `e_theta e_theta^T / r`); nodes see only a mesh.
4. **Owner per loop vertex** = larger `|k|`, ties to the hull; Math/Compare/Switch nodes, per vertex. Fine.
5. **Selecting yielding vertices.** Loop vertices whose origin is the non-owner surface, merged onto "the nearest owner-origin
   loop vertex along the loop". Nodes can: Sample Nearest on the owner subset (spatial nearest, not along-loop), Set Position
   of yielders onto that point, then Merge by Distance with Selection and a tiny distance. Merge by Distance semantics from the
   manual (3.5 page): selected points merge only among selected; `Mode` All/Connected; "merging surrounding geometry where
   necessary". Which position a merged group takes was not tested; the snap-first pattern avoids depending on it (inferred).
   Merge by Distance has no owner argument and no guard.
6. **What nodes cannot express directly.**
   - The collapse guard: refuse a collapse on a face flip (old.new normal <= 0), on a worst angle under 10 degrees if worse, on
     a failed link condition. Each collapse is accepted or refused on the current mesh. Merge by Distance is one batch over the
     whole selection. A sequential accept/refuse needs a Repeat Zone holding the mesh as loop state with one candidate
     per iteration, each iteration running Merge by Distance and a flip test on the mesh (cost below), or a batch with a
     post-check that discards the whole batch (coarser than the spike's per-collapse refusal). A For-Each Geometry Element zone
     processes elements independently and joins results, so it cannot commit one collapse and see it before the next
     (inferred from the zone semantics; not run). Iteration count and the repeat zone's 5.2 limits were not tested.
   - Both-pieces acceptance for splits: the spike found replaying one piece's collapses opened a 6.8e-4 crack. Nodes would
     evaluate two Mesh Boolean nodes (Difference, Intersect) and need one decision applied to both: compute candidates
     deterministically on both, AND them by matching positions (Sample Nearest across the two meshes). Possible in principle;
     heavy; untested.
   - The panel-split case: the spike found the rule is a no-op there and the remaining slivers are the owner's own plus the cap
     triangulation (spike "Smallest changes" 3). Nodes have no retriangulate/dissolve node (2a); Mesh Bevel exists.
   - Cutter tessellation ("spacing no finer than about a quarter of the hull's local edge length") is an input constraint, not
     a node matter.
7. **Not tested:** nodes 1 to 6 beyond the Boolean/attribute/edge-selection part. No weld chain was built.

## 3. Precedents

- **Searches.** Web searches for nondestructive boolean-cleanup node groups and developer discussion on post-boolean cleanup in
  Geometry Nodes returned only Blender manual pages (Merge by Distance, mesh Clean Up operators: Degenerate Dissolve, Limited
  Dissolve, Make Planar). No devtalk thread or community "clean boolean" group was found. One commercial add-on appeared:
  Hardsurface Doctor (superhivemarket.com/products/hardsurface-doctor), listed as scanning/repairing boolean-damaged meshes and
  re-applying bevel weights, Blender 4.2+; its code was not available to read.
- **Operator-supplied copies of Hard Ops 26.1.7 and Boxcutter 26.1.5**, read as text only (untrusted; nothing run, imported or
  opened in Blender; .blend contents read as byte strings). Root: `...\scratchpad\vendor-src\hardops\HOps` and
  `...\vendor-src\boxcutter\Boxcutter` (abbreviated `HOps/` and `BC/` below).

### 3a. Licence field verbatim

- Hard Ops `HOps/blender_manifest.toml`: `license = ["SPDX:GPL-3.0-or-later"]` (name "Hard Ops 26'", version "26.1.7",
  `blender_version_min = "4.2.0"`).
- Boxcutter `BC/blender_manifest.toml`: `license = [ "SPDX:GPL-3.0-or-later", ]` (name "BoxCutter 26'", version "26.1.5",
  `blender_version_min = "4.2.0"`). A `BC/LICENSE` file is present (not read).

### 3b. What their "cleanup" does

Neither contains an ownership, curvature or silhouette rule. Searches for `sstep`, `clean_boolean`, `boolean_clean`,
`csharpen` found Csharpen as an operator and `Sstep` only as an icon name (`HOps/ui/Panels/a4_operations.py:40`).

- **Boolean modifier creation (Boxcutter).** `BC/addon/operator/shape/utility/modifier.py:395-400`: `obj.modifiers.new(name=
  'Boolean', type='BOOLEAN')`, `solver` from preferences (EXACT when mode is JOIN and `join_exact`), `show_viewport = show`.
  Lines 414-416: `sort(obj, option=preference.behavior)` and `sort(obj, types=['WEIGHTED_NORMAL'], last=True)`, so Weighted
  Normal is moved to the end of the target's stack. In the "nodes workflow" the boolean is the `NodeBoolean` wrapper
  (`BC/utility/geometry_nodes/node_boolean.py`) around the group `HOPS_Boolean`.
- **Cutter-side modifier stack (Boxcutter), nondestructive.** `BC/addon/operator/shape/utility/data.py:117-141` builds on the
  cutter shape, in this order: `bevel_main` (BEVEL, `limit_method='WEIGHT'`, `edge_weight='bevel_weight_edge'`), `weld_main`
  (WELD, `mode='CONNECTED'`, `merge_threshold = MIN_DIM * 0.8`, line 120), `bevel_quad`, `weld_quad`, `bevel_front`, `weld_front`,
  then a `BC_Clean` Nodes modifier (data.py:143 on; class `BC/addon/operator/shape/utility/nodes/clean.py:8-12`, asset
  `BC_Clean` in `BC_Nodes/BC_Shape_nodes.blend`; inputs `Flipped Faces`, `Mark Sharp Angle`, `Mark Sharp`, `Remove Attrs`,
  `Geometry`, clean.py:5; set `remove_attrs='bevel*'`, `mark_sharp=False` at data.py ~143-147). So BC_Clean cleans attributes
  and flipped faces, not boolean seams. Bevel-dependent welds are re-added in `modal/bevel.py:161,184,220,249` with
  `merge_threshold = max(dimensions()) * 0.001` and re-ordered at `modal/bevel.py:264`:
  `modifier.sort(bc.shape, types=['VERTEX_WEIGHT_EDIT','VERTEX_WEIGHT_MIX','BEVEL','WELD'])`. These welds are on the cutter
  shape before it is used, not on the boolean result.
- **Applied (destructive) cleanup in Boxcutter.** On accept, `clean_nodes` (data.py:1066 on): if `keep_modifiers` is false it
  applies all cutter modifiers except Smooth by Angle (data.py ~1124); otherwise `apply_unkept` (data.py ~1130-1156) applies
  those not kept and keeps `WELD`/`CLEAN` when a Bevel is kept; if no bevels remain only the last Weld is kept
  (data.py:1160-1170). bmesh calls (applied, on the cutter mesh): `bmesh.ops.remove_doubles` + two
  `dissolve_degenerate` passes (`BC/addon/operator/shape/utility/custom.py:130-133`); for circle cutters
  `spin`, `remove_doubles(dist=0.01)`, `dissolve_limit(angle_limit=0.01, use_dissolve_boundaries=False)`
  (data.py:455-456); further `remove_doubles` at data.py:560, 586 (1e-5), 1832 (1e-4) and `shader/snap_alt.py:880`
  (context not read). `BC/.../mesh.py:1034-1035` sets `use_merge_vertices = True`, `merge_threshold = 1e-7` on a modifier
  (which one not read). `BC/addon/property/preference/utility/update.py:347` adds an "Inset Weld" WELD modifier after an
  inset's Boolean.
- **Hard Ops boolean as a node group.** `HOps/operators/booleans/bool_stack.py` converts a target's BOOLEAN modifiers into one
  Nodes modifier named `"{n} Booleans"` with `GeometryNodeMeshBoolean` nodes (bool_stack.py:266, 296-300; solver FLOAT/EXACT/
  MANIFOLD, Exact tracked in the node label because "nodes do not support it" per the option text at :66) and back to
  Boolean modifiers (:354-363). Hard Ops and Boxcutter both ship `HOPS_Boolean.blend` (`HOps/utility/geometry_nodes/
  HOPS_Nodes/HOPS_Boolean.blend`; `BC/utility/geometry_nodes/HOPS_Nodes/HOPS_Boolean.blend`; Blender 4.5 file header
  `BLENDER-v405`). Its interface (python wrapper input list, `BC/utility/geometry_nodes/node_boolean.py:6`): `Input Geometry`,
  `Object`, `Operation` (INTERSECT, UNION, DIFFERENCE, INSET, KNIFE), `Solver`, `Self Intersection`/`Non Manifold`,
  `Merge Threshold`, `Stitch Distance`, `Weld`, `Transfer Normals`, `Material Cut`, `Inset Thickness`, `Inset Slice`,
  `Inset Slice Offset`, tag names/values for faces and edges, `Clean Attribute 1` to `5` (wrapper properties for `weld` at
  node_boolean.py:130 and `merge_threshold` at :139). Byte-string scan of that file (wiring not read, so order inside the group
  is unknown): node classes `GeometryNodeMeshBoolean` (many), `GeometryNodeMergeByDistance` (at least 5 instances, tooltips
  "Merge distance for combining geometry", a label "Weld After Boolean"), `GeometryNodeSetMeshNormal`,
  `GeometryNodeCaptureAttribute`, `GeometryNodeInputNormal`, `GeometryNodeStoreNamedAttribute`, `GeometryNodeSetPosition`,
  `GeometryNodeFlipFaces`, `GeometryNodeJoinGeometry`, `GeometryNodeSwitch`/`IndexSwitch`, `GeometryNodeSetMaterial`, and
  descriptions "Subtract and intersect then stitch original geometry." (Knife) and "Fastest. Only Supports manifold
  geometry." Weld there is distance-based Merge by Distance after the boolean; it is a threshold, with no per-surface
  ownership (from the interface and node classes above; the graph itself was not read).
- **Hard Ops Csharpen.** `HOps/operators/sharpeners/complex_sharpen.py:231-270`: `apply_mod` applies (destructively) the
  selected modifier types in this order of selection: BOOLEAN, MIRROR, BEVEL (all but the last), SOLIDIFY, ARRAY, plus any
  "others"; then `soft_sharpen_object`. `HOps/src/operator/shape/sharpen.py:263-273` adds a `WEIGHTED_NORMAL` modifier with
  `keep_sharp = True`; :281 `smart_apply`. So Csharpen = apply the stack, mark sharp edges, add Weighted Normal. No weld or
  dissolve in that path.
- **Nondestructive or applied?** The boolean (Boolean modifier or `HOPS_Boolean` group), Bevel, Weld (on the cutter and an
  "Inset Weld" after an inset), BC_Clean and Weighted Normal are live modifiers until the user applies or accepts; the bmesh
  `remove_doubles`/`dissolve_*` calls and Csharpen's apply step are destructive. Hard Ops/Boxcutter therefore demonstrate that
  a GN node group with Mesh Boolean plus Merge by Distance can ship as a stack modifier; nothing read shows any
  curvature- or ownership-aware merge.

## 4. Performance

Measured, Blender 5.2.2 headless, same machine session (Starfire), hull 3,010 vertices, 16-segment cylinders at hull
vertex xy positions (z centred, depth 0.2, radius 0.03, spaced > 0.1 apart, random seed 3; the cutters were not
checked for non-overlap on the hull surface, but the cutter face counts below show each case cut). Time = one `depsgraph.update()`
plus `evaluated_get().to_mesh()` after toggling the modifier, last two repetitions; includes the two Store Named Attribute
nodes and Collection Info/Realize Instances.

| cutters | solver | result verts / faces | intersecting edges | cutter faces kept | time (s) |
|---|---|---|---|---|---|
| 1 (gun port) | MANIFOLD | 3,067 / 3,056 | 42 | 48 | 0.026, 0.023 |
| 1 | EXACT | 3,067 / 3,056 | 42 | 48 | 0.048, 0.041 |
| 10 | MANIFOLD | 3,209 / 3,074 | 155 | 78 | 0.021, 0.019 |
| 10 | EXACT | 3,209 / 3,074 | 155 | 78 | 0.128, 0.152 |
| 23 | MANIFOLD | 3,306 / 3,100 | 247 | 113 | 0.028, 0.019 |
| 23 | EXACT | 3,306 / 3,100 | 247 | 113 | 0.191, 0.203 |
| 26 | MANIFOLD | 3,346 / 3,107 | 298 | 121 | 0.028, 0.024 |

Requested 30 and 60 cutters; the placement filter yielded 23 and 26. All cutters go through the one Mesh 2 input as a
realized single mesh (Collection Info); the Boolean node takes Mesh 2 as one geometry here. No sequential or chained
boolean run was timed. Repeat-zone cost: not measured. Sources read give no benchmark (manual: zone semantics only;
search returned no timing data). A repeat-zone weld would run Merge by Distance plus a flip test per iteration over the
mesh (3.0k to 3.3k vertices); Merge by Distance's selection input is documented as a way to speed the nearest-point search
(manual 3.5 page). Per-iteration time at this size is untested (inferred only).

The spike's own kernel numbers for comparison: boolmesh 8 to 25 ms, Manifold 13 to 20 ms per op on these cases.

## Gaps

- The Add Modifier menu behaviour of `is_modifier` groups and the asset flow.
- Whether `NodesModifier.properties` accepts Collection/Object inputs in 5.2 (item assignment failed).
- Any weld chain beyond Boolean + `src` + `Intersecting Edges`; every node-level claim in 2d is inferred.
- The 42-versus-36 count.
- Hard Ops/Boxcutter node group wiring (strings only).
