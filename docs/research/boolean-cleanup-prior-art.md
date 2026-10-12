# Boolean cleanup near the intersection curve: prior art

Serves ruling `brush-tree:ruling:boolean-cleanup-tighter-curve-wins` (campaign brush-tree, Operator, 2026-10-12): along a boolean cut into the hull's evaluated surface, the surface with the higher curvature owns the cut's silhouette, and the vertices the flatter surface contributes near the cut are merged into it. Prior art first, then a spike on the Dexter Quiet cage with a cutter.

Pass: Eyes, 2026-10-12, agent `eyes-bt-boolean-cleanup`. Facts with evidence pointers; "(inferred)" marks inference; "(recall, unverified)" marks things stated from memory that were not fetched this pass. No recommendation. Builds on `detail-on-subd-prior-art.md` @ c513992 (section 1 records that practitioners weld and clean ragged vertices after a boolean cut).

Tool caveat: the page fetcher summarises with a small model; Blender manual pages returned only navigation, so Blender operator behaviour below comes from search snippets, not full pages.

## Headline findings

1. No source found that names or specifies "the tighter-curved surface defines the cut, merge the flatter surface's vertices onto it" as an algorithm. Nearest relatives are in section 2.
2. Every mainstream tool found treats post-boolean cleanup as a distance or length threshold operation (merge-by-distance, collapse edges shorter than epsilon, aspect-ratio sliver removal), not a curvature-ownership rule. The one curvature-driven item found (Hu et al., SPIE 2022) sets target edge length from curvature before the boolean, not merge direction after it.
3. Manifold runs a post-boolean degenerate-edge collapse internally with a triangle-flip guard; CGAL returns the intersection curve as a constrained-edge map that its isotropic remesher can protect; Houdini outputs seam edge groups and PolyReduce has hard/soft edges. These are the "intersection loop as protected feature" mechanisms found.

## 1. Research and tools that clean booleans near the intersection

### Libraries and kernels

- **Manifold** (Apache-2.0, C++). After assembling a boolean result, `boolean_result.cpp` calls `outR.RemoveDegenerates(nPv + nQv)` then `RemoveUnreferencedVerts()` (https://github.com/elalish/manifold/blob/master/src/boolean_result.cpp). In `edge_op.cpp` (https://raw.githubusercontent.com/elalish/manifold/master/src/edge_op.cpp; fetcher summary, function names as reported):
  - `RemoveDegenerates`: `CleanupTopology`, collapse edges shorter than `epsilon_`, `SwapDegenerateEdges`, collapse colinear edges, recompute vertex normals.
  - `CheckEdge`/`CollapseEdge`: short edges collapse to the midpoint; longer edges get a fitted position in the plane of the edge and averaged normal, clamped to [-0.5, 0.5] along the edge, with cost in squared-length units. A collapse is rejected if a surrounding triangle would flip (cross product against face normal); a Delaunay-style worst-angle threshold (0.5 or 0.99) also gates it.
  - `Colinear`: an edge may collapse only if each rotated neighbour stays within epsilon of the face plane and does not invert.
  - `SwapDegenerateEdges`: swaps the longest edge of a degenerate triangle only if that reduces degenerates; per-edge cap `kMaxSwapsPerEdge = 255`.
  - `Decimate(tolerance)`: collapse/swap in cost-sorted rounds, `maxCost = tolerance^2`, tolerance floored at epsilon.
  - Epsilon is a global length tolerance, not curvature based; its value is set outside these files. The README (https://github.com/elalish/manifold) does not mention epsilon or short-edge collapse; it states reliability and guaranteed-manifold output as the goal. Whether `Decimate` is on the public API was not confirmed.
- **CGAL Polygon Mesh Processing** (GPL v3+, some core parts LGPL; commercial licences from GeometryFactory). Corefinement booleans `corefine_and_compute_union/intersection/difference`; with a constrained-edge map supplied, edges on the intersection of the inputs are marked constrained, and sub-edges stay marked when split (search result quoting https://doc.cgal.org/latest/PMP_Boolean_operations/group__PMP__boolop__grp.html). Exact predicates needed for correct topology; exact constructions recommended when chaining. As of CGAL 6.2 remeshing lives in "Meshing and Remeshing of Polygon Meshes"; `isotropic_remeshing` with `protect_constraints(true)` and `face_patch_map` limits remeshing to a region and keeps constraint edges (https://doc.cgal.org/latest/PMP_Remeshing/PMP_Remeshing_2isotropic_remeshing_of_patch_example_8cpp-example.html). Curvature-adaptive sizing in that remesher: not confirmed in fetched pages (recall, unverified: a sizing-field parameter exists in recent versions).
- **libigl**: README says "MPL-2.0-licensed", repo also carries LICENSE.GPL (https://github.com/libigl/libigl). `igl::copyleft::cgal::mesh_boolean` implements Mesh Arrangements for Solid Geometry (Zhou, Grinspun, Zorin, Jacobson, SIGGRAPH 2016; https://alecjacobson.com/weblog/4573.html) under a `copyleft/cgal` path; an old mirror header shows an MPL-2.0 notice and a CGAL dependency, so the effective licence is bounded by CGAL's (inferred). Related functions named there: `mesh_boolean_cork`, `intersect_other`, `remesh_self_intersections`. C++; no Rust bindings found.
- **Cherchi et al., Fast and Robust Mesh Arrangements using Floating-point Arithmetic** (TOG 2020): https://github.com/gcherchi/FastAndRobustMeshArrangements, MIT, header-only (C++ presumed), four `solveIntersections` variants; no remeshing or cleanup mentioned on the page.
- **Cherchi, Pellacini, Attene, Livesu, Interactive and Robust Mesh Booleans** (2022; https://ar5iv.arxiv.org/html/2205.14151): output triangles are portions of input triangles; the only cleanup stated is per-frame "degeneracy removal and rebuilding of adjacencies"; no simplification or coplanar merging described; C++ with CinoLib, Indirect Predicates, Abseil, TBB; code "will be released", no repo given in the text read.
- **Exact predicates, exact constructions and combinatorics for mesh CSG** (arXiv 2405.12949; fetch failed on size, search snippet only): says results keep "scars" of intersection from co-refinement that the final mesh does not need; finds coplanar regions by traversal and simplifies them; notes poorly triangulated planar input areas are worth remeshing.
- **Adaptive Mesh Booleans**, Schmidt and Brochu, Autodesk Research (https://arxiv.org/abs/1605.01760; read via https://ar5iv.arxiv.org/html/1605.01760). Steps: refine locally around the intersection (split, collapse, flip, smooth), delete intersecting triangles, zipper the two boundary loops by iterative closest-point evolution, reproject loop vertices onto the input surfaces with sharp-edge constraints (3.5, 3.6), simplify the intersection region as post-process (3.7). Density: constant max edge length `l_max`, min `0.4*l_max`; the paper "does not adapt density to surface curvature", adapting to local feature size is future work (3.4). Failure modes listed: loop-count mismatch giving holes or floating patches; 5-iteration refinement cap; slow convergence near coplanar; loops of very different shape give self-intersections or non-manifold seams; sharp-edge constraints can leave triangular corner holes (3.6.1). Shipped in Meshmixer (since 2011) without the sharp-edge enhancements; no source release stated. Closest published "both sides conform to one loop" method found.
- **Hu et al., adaptive remeshing from local information for mesh booleans** (SPIE vol. 12331, 123314S; title and full text not obtained, search summary only, https://spiedigitallibrary.org/conference-proceedings-of-spie/12331/123314S/An-adaptive-remeshing-method-based-on-local-information-for-mesh/10.1117/12.2652878.full): edge length from local edge length and curvature; reported average edge length 55% shorter in high-curvature areas, 78% longer in low-curvature areas versus uniform remeshing. Verify before citing.

### Applications and add-ons

- **Houdini Boolean SOP** (https://www.sidefx.com/docs/houdini/nodes/sop/boolean.html): "Collapse tiny seam-adjacent edges" fuses microscopic edges from misaligned inputs with an Edge length threshold; Detriangulate (All / Only Unchanged / None) merges triangles back into original polygons; "Assume seam polygons are flat" drops the triangulation-crease point; "Unique Points Along Seams"; Output Edge Groups for A-A, B-B, A-B seams. Arbitrary precision internally, snapped to float on output, which can produce microscopic self-intersections when chained.
- **Houdini PolyReduce SOP** (https://www.sidefx.com/docs/houdini/nodes/sop/polyreduce.html): hard points/edges never move, soft ones carry a weight, Boundaries weight, vertex-attribute seam weight, "Only use original point positions", normal-deviation limit, density retention by attribute or by view silhouette, Equalize lengths. Fetcher found no mention of quadric error on the page.
- **Blender** (search snippets of https://docs.blender.org/manual/en/dev/modeling/meshes/editing/mesh/cleanup.html; bodies not read): Merge by Distance (can merge selected into unselected; newer manual preserves sharp edges when custom split normals exist), Degenerate Dissolve (collapses edges shorter than a length), Limited Dissolve (only linked in snippets), Weld modifier = non-destructive Merge by Distance, Decimate modifier Collapse mode = non-destructive Degenerate Dissolve. Boolean modifier Exact solver: overlap and self-intersection options, only manifold inputs guaranteed (https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/booleans.html, via search). Nothing found saying Exact minimises vertices along the cut.
- **Hard Ops / Boxcutter / Bool Tool / Fluent**: Hard Ops manual boolean page (https://hardops-manual.readthedocs.io/en/latest/boolean/) names no dissolve or weld options in the text fetched. The Blender Bros bundle page lists a "Boolean Cleanup" feature without detail (search snippet). A Blender Nation Bool Tool tutorial summary cleans up with the native Weld modifier, not a Bool Tool option. Add-on source not inspected (`F:\Projects\blender-tooling-surface-prior-art.md` line 71 says the same).
- **Hardsurface Doctor** (https://superhivemarket.com/products/hardsurface-doctor/docs, snippet): "Safe Repair" merges doubles, removes zero-area and loose geometry, dissolves multi-face non-manifold edges. **Boolmend** (https://blenderartists.org/t/boolmend-one-click-post-boolean-cleanup-topology-repair-shading-fix-15-early-access/1650088): early-access add-on claiming one-click post-boolean cleanup and sliver-edge removal; vendor claims, unverified.
- **Meshmixer**: Boolean adds triangles around the intersection, deletes strips to form clean boundary loops on each side, applies Reduce as post-process; on failure remeshes denser and retries (search snippets of https://help.autodesk.com/cloudhelp/2019/ENU/MSHMXR/files/GUID-355503DE-889B-4168-8398-084F9BBD508B.htm).
- **Altair HyperMesh** `fix 2d mesh` (https://help.altair.com/hwdesktop/hwd/topics/reference/hm/_fix_2d_mesh.htm, snippet): sliver removal by minimum aspect ratio, intersection removal that avoids sub-threshold triangles, bitmask to disable edge swaps, collapses, node moves.
- **COMSOL, Intersect with Line** (https://doc.comsol.com/6.3/doc/com.comsol.help.comsol/comsol_ref_mesh.24.70.html, snippet): vertices on intersected edges are snapped onto the intersection line, bounded by a repair tolerance. Closest found to "move one side's vertices onto the other's curve", but FE meshing and tolerance-driven.
- **ZBrush**: DynaMesh with Groups, Polish by Features after remesh (Novedge tip, snippet). Not an ownership rule.

### Simplification with locked features

- **meshoptimizer** (MIT, C++; Rust `meshopt` crate; https://github.com/zeux/meshoptimizer): `meshopt_simplifyWithAttributes`, per-vertex `vertex_lock` array (Lock, Protect, Priority), `meshopt_SimplifyLockBorder`, absolute or relative error bound. Quadric basis not stated in the fetched text (recall, unverified: it is quadric-based).
- Garland-Heckbert QEM with boundary constraint planes as the standard way to protect a loop in constrained collapse (recall, unverified; not fetched).

## 2. "Tighter-curved surface owns the cut; flatter surface's vertices merge onto it"

### Name or precedent

- No source found with this rule under any name. Searches for it returned Adaptive Mesh Booleans (symmetric: both sides conform to one loop, no side ownership), COMSOL snapping (tolerance based), Hu et al. (pre-boolean curvature sizing).
- CAD trimmed-surface tessellation: the common boundary edge is discretised once and both faces reuse those vertices (patent text US 9,836,884 / 9,875,577, mental ray "Edge Merging" doc, a BUAA paper on trimmed-surface meshing using distance and angle tolerances; all search snippets, not read in full). Shared-edge-first has precedent, but sampling follows the edge's own chord and angle tolerance, not which adjoining surface is more curved.
- Meshmixer deletes strips from each object and leaves loops on both sides, then zips: the loop is a joint product (inferred).
- Practitioner side (`detail-on-subd-prior-art.md` section 1 @ c513992): booleans leave extra vertices and ragged tris/n-gons along the cut, which practitioners weld and clean by hand. The operator's rule describes what that manual weld converges to; no tool found automates it as stated.

### What goes wrong: sourced

- Triangle flips on collapse: Manifold `CollapseEdge` rejects flips and gates on worst angle (edge_op.cpp summary).
- Collapse position bounded to [-0.5, 0.5] along the edge, epsilon-scale moves (same).
- Loop mismatch when the two sides differ in feature size or shape: Adaptive Mesh Booleans 3.2, 3.4.
- Sharp-edge constraints leaving corner holes: same paper, 3.6.1.
- Chained booleans accumulate microscopic self-intersections after float snapping: Houdini Boolean page.
- Merging across sharp edges loses them unless guarded: Blender Merge by Distance now marks edges to keep sharp edges when custom split normals exist (snippet).
- Density near the cut scales with subdivision level, so the flatter surface's contribution count depends on level: `detail-on-subd-prior-art.md` section 1 (inferred there).

### What goes wrong: inferred, no source either way

(inferred) Cases the rule leaves undefined and no source addresses: both surfaces comparably curved (ownership ambiguous); saddle intersections where one surface has opposite-sign principal curvatures, so "tighter" depends on direction along versus across the curve; the cut crossing a crease or hard edge of either surface (local curvature unbounded; the stack's one-segment Bevel and Weighted Normal introduce creases); ownership switching along one loop and what happens at the switch vertex; a flatter-surface vertex moved onto the tighter surface's curve changing the flat surface's silhouette or flipping its triangles when the displacement is large relative to local edge length; curvature measured on a tessellated polyline being noisy at sliver density; moved vertices leaving the cage's Subsurf limit surface because the cut is on the evaluated mesh.

## 3. Implementations we could own

| Item | Licence | Language | Rust | Does |
|---|---|---|---|---|
| Manifold (elalish) | Apache-2.0 | C++ | `manifold-csg` safe bindings over the C API (docs.rs lists Apache-2.0 OR MIT for the crate; `manifold3d` re-exports it, v0.3.3 seen; f64 via MeshGL64). README also lists a native Rust port `manifold-rust` with no C++ dependency (not verified further). Other bindings: C, JS/WASM, Python, C# (`ManifoldNET`, external) | boolean with epsilon degenerate cleanup; decimate (public status unconfirmed) |
| boolmesh | MPL-2.0 | pure Rust, `glam`, optional `rayon`/`bevy` | native | from-scratch boolean "inspired by Manifold"; v0.2.1 released 2026-10-11 (0.2.0 yanked); input must be manifold; per-corner attribute carry; docs.rs doc coverage 0%; whether it ports `RemoveDegenerates` not stated (https://docs.rs/crate/boolmesh/latest) |
| meshoptimizer | MIT | C++ | `meshopt` crate | simplify with vertex locks and attribute weights |
| CGAL PMP | GPL v3+ (LGPL parts), commercial available | C++ | none found | corefinement with constrained-edge output; isotropic remeshing with protected constraints |
| libigl | MPL-2.0 core, GPL file present; copyleft/cgal boolean tied to CGAL | C++ | none found | Mesh Arrangements boolean |
| FastAndRobustMeshArrangements | MIT | C++ header-only | none found | arrangement via indirect predicates, no cleanup |
| Interactive and Robust Mesh Booleans | unstated | C++ | none found | per-frame degeneracy removal only |
| csgrs | not checked | Rust | native | appeared in search results; not inspected |

Local: `F:\Projects\GameCult.Geometry.Csg` checkout is on branch main with `docs/research` holding brush-surfaces-and-sdf-bricks and octahedral-impostors notes; the eureka/brush-tree branch and the boolean kernel the crate uses were not inspected this pass.

## Not resolved in budget

- Blender Limited Dissolve semantics; Hard Ops / Boxcutter cleanup option names.
- Whether Manifold's `Decimate`/`Simplify` is on the public C API and the Rust crate.
- Full text of arXiv 2405.12949 and of Hu et al.
- CGAL adaptive sizing field and curvature-adaptive isotropic remeshing parameters.
- Garland-Heckbert boundary-constraint details and meshoptimizer's quadric basis (recall only).
