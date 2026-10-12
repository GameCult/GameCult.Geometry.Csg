# Detail on a subdivision hull: prior art

Fork: brush-tree, detail layer. How does hard-surface detail (canopy, vents, intakes, gun ports, panel insets) get onto a smooth subdivision hull without moving the primary-form cage? Options floated: boolean into the evaluated mesh; inset/support loops in the cage; a separate interpenetrating (floating) piece.

Provenance: Eyes pass, 2026-10-12, agent `eyes-bt-detail-layer`. Facts carry sources; "(inferred)" marks inference; "(unsourced)" marks recall not checked against a page. Not read: `docs/brush-tree-target.md` at a7879dad (the commit did not resolve in the CultLib object store, so invariant wording is from the brief only).

Operator workflow (verbatim, 2026-10-12): "expressing the form elegantly with as few control points as possible, then I go and start cutting into it for all the hard surface details and bits that interrupt the idealized form like those gun ports". The detail layer in her practice is subtractive cuts into the subdivided form.

## 1. Cut into the evaluated mesh (boolean after subdivision)

- Blender modifiers run top to bottom, each taking the output above; order decides which operator sees which geometry. Boolean below Bevel means bevel acts on the clean base first; boolean above Bevel makes bevel work on boolean-generated geometry and can narrow it ([stack order](https://steveyang.readthedocs.io/Modeling/Non-destructive/ND-Beginning/Modifier_Stack_Order/), [cgcookie thread](https://cgcookie.com/community/9780-change-to-modifier-stack-changes-bevel-width)). Subdivision Surface docs: stack position "significantly affects the result" ([Blender 4.2 manual](https://docs.blender.org/manual/en/4.2/modeling/modifiers/generate/subdivision_surface.html)).
- Blender Boolean modifier: Exact solver handles overlap and self-intersection, slow; Fast does not handle overlapping geometry; only manifold inputs are guaranteed correct ([manual](https://docs.blender.org/manual/en/4.2/modeling/modifiers/generate/booleans.html)).
- Regenerable: yes. Cutter list plus cage are the inputs and the stack re-runs. Cage independence: full, cutters never touch cage vertices. Triangles: dense, because the cut runs on the subdivided mesh, scaling with subdivision level (inferred). Practitioners report booleans leave extra vertices and ragged n-gons/triangles along the cut, which they weld and clean ([Blender Artists](https://blenderartists.org/t/how-to-create-this-kind-of-side-cut-in-hard-surface-modeling-with-good-topology/1482837), [Blender Artists](https://blenderartists.org/t/questions-regarding-hard-surface-modeling/1207286)).
- Shading: the cut wall meets the hull at a hard crease; the practitioner fix is a bevel/chamfer on the cut edges ([same thread](https://blenderartists.org/t/how-to-create-this-kind-of-side-cut-in-hard-surface-modeling-with-good-topology/1482837)). Weighted Normal rewrites custom normals by corner angle/face area; Keep Sharp preserves sharp edges; Face Influence uses per-face strength set by Set Strength or the Bevel modifier's Set Strength mode, so bevel faces drive the result ([manual 4.2](https://docs.blender.org/manual/fi/4.2/modeling/modifiers/normals/weighted_normal.html)). One add-on doc says at least a one-step bevel matters for good weighted-normal shading ([page](https://superhivemarket.com/products/shadingmod)). That matches the one-segment-bevel plus weighted-normals shippable stack.
- Tooling precedent: Hard Ops cSharpen applies booleans by default (to keep cutting) but keeps bevel modifiers live and never applies bevels; default 3 segments, 0.7 profile, weight-limited; WN and Harden Normals are optional toggles ([manual](https://hardops-manual.readthedocs.io/en/latest/csharpen/)). Another add-on says it re-establishes non-destructive Bevel and Weighted Normal finishing layers after apply ([Arcane Rifter](https://superhivemarket.com/products/arcane-rifter)). These tools bake cuts into the mesh, so they are not regenerable; only a stack that never applies is.
- No source found describing "boolean after Subsurf" as a deliberate standard modifier order. The sourced practice cuts the cage first (section 2); the usual finishing order Boolean, Bevel, Weighted Normal, Subsurf last is unsourced recall.

## 2. Cut the cage with support loops (subd modelling)

- Practitioners: after a boolean cut and subdivision "everything falls apart"; the fix is supporting loops around the cut, clean and weld verts, then chamfer/bevel the cut edges so it stays sharp after smoothing ([Blender Artists](https://blenderartists.org/t/how-to-create-this-kind-of-side-cut-in-hard-surface-modeling-with-good-topology/1482837)). Artifacts come from too few segments for the curvature; abrupt loop routing causes smoothing artifacts; carrying loops across the surface smooths more consistently ([Blender Artists](https://blenderartists.org/t/questions-regarding-hard-surface-modeling/1207286)).
- Game-art counterpoint: some artists use bevel-first low poly instead of subd because a subdivided hull bakes less cleanly (bevel widens, wavy artifact, extra supports did not fix it) ([CG Cookie](https://cgcookie.com/community/9686-why-not-use-subdivision-surface-modifier-on-this-weapon), [polycount](https://polycount.com/discussion/comment/2573659)). Others hold that subd with support loops remains best for normal-mapped hard surface ([polycount](https://polycount.com/discussion/comment/2573688)).
- Regenerable: only if loop insertion is itself generated from the tree. Cage independence: lost by construction, since loops and cut-ring vertices are cage vertices and the cage grows with every detail. The "detail never moves the cage" invariant excludes this option (inferred).
- Semi-sharp creases are the in-cage alternative to extra loops. OpenSubdiv: per-edge sharpness, 10 or more is infinite, Chaikin rule propagates sharpness; infinite creases are tangent discontinuities where normal displacement can tear ([OpenSubdiv](https://graphics.pixar.com/opensubdiv/docs_3x_alpha/subdivision_surfaces.html)). Blender: weighted edge crease, Boundary Smooth, Use Limit Surface and Quality ([manual](https://docs.blender.org/manual/en/4.2/modeling/modifiers/generate/subdivision_surface.html)). Creases mark edges already in the cage, so a cut still needs cage edges where it falls (inferred).
- OpenSubdiv feature-adaptive refinement clusters subdivision near creases, extraordinary points, boundaries, corners ([release info](https://graphics.pixar.com/opensubdiv/release_info.html)). Hierarchical edits (override values at any refinement level, localized detail without specifying the whole surface) were removed in OpenSubdiv 3.0 ([hedits](https://graphics.pixar.com/opensubdiv/docs/hedits.html)).

## 3. Boolean then retopo

- Common practice: model the high poly, copy, strip support loops and subdivisions that do not affect silhouette to a low poly, bake ([polycount](https://polycount.com/discussion/comment/2573659)). Retopo output is a new mesh with its own topology: not regenerable from a tree, and cage-independent only if the retopo output is itself the cage. No source found automating retopo from a CSG tree (gap).

## 4. Floating geometry / mid-poly (separate interpenetrating pieces)

- Mid-poly workflow, attributed to Star Citizen and Alien: Isolation by one tutorial: face-weighted normals, high-poly detail in normal maps rather than geometry ([80.lv](https://80.lv/articles/how-to-create-a-detailed-large-scale-scene-with-rich-props-assets-in-unreal-engine/)).
- A polycount developer describes tri-planar local-space decals that modify only normals in targeted areas, usable for panel lines, "but sometimes it's worth more to cut that into the topology" ([polycount](https://polycount.com/discussion/comment/2333210)). Baked bevels in normal maps are cheap but resolution-dependent; the alternative cited is real bevels plus adjusted vertex normals ([polycount](https://polycount.com/discussion/comment/2333606)).
- Regenerable: yes, pieces are tree outputs. Cage independence: full. Triangles: each piece adds its own, including hidden interior geometry; the hull is not cut. Shading: the intersection seam is a hard visual line unless a normal bake or bevel masks it. Floaters rely on a bake, which this campaign does not have (inferred; no source on floaters without a bake).

## 5. NURBS / CAD closed prior art

- Plasticity: pure NURBS, booleans advertised as watertight, fillets adapting to edge conditions, direct-edit with no history tree, meshes only on export (OBJ, STEP, IGES); no subdivision-surface mention found ([DigitalProduction](https://digitalproduction.com/2023/10/04/plasticity-3d-cad-for-artists/), [Plasticity](https://plasticity.xyz/)). Its boolean-then-fillet works on exact surfaces and tessellates afterwards, not on a subdivided mesh (inferred).

## 6. Displacement and detail transfer on subdivision surfaces

- Displaced Subdivision Surfaces (Lee, Moreton, Hoppe, SIGGRAPH 2000): scalar displacement over a smooth subdivision domain surface in one framework; the hard part is finding a simple domain surface; the project page does not discuss overhangs, holes or hard creases ([Hoppe](https://hhoppe.com/proj/dss/)). A scalar over a surface cannot represent undercuts or cut-through (inferred).
- Kobbelt, Campagna, Vorsatz, Seidel, Interactive Multi-Resolution Modeling on Arbitrary Meshes (SIGGRAPH 1998): detail coefficients coded in local frames over a decimation hierarchy for detail-preserving edits ([RWTH](https://www.graphics.rwth-aachen.de/publication/03156/)). Frame definition not read.
- Biermann, Martin, Bernardini, Zorin, Cut-and-paste editing of multiresolution surfaces (SIGGRAPH 2002): split source and target into base and detail, parameterize bases to a common domain, transfer detail offsets ([SIGGRAPH history](https://history.siggraph.org/learning/cut-and-paste-editing-of-multiresolution-surfaces-by-biermann-martin-bernardini-and-zorin/)). Same group, Approximate Boolean Operations on Free-Form Solids (Biermann, Kristjansson, Zorin, SIGGRAPH 2001), is cited as related; contents not read.
- All three keep the base fixed and put detail in coefficients on top, which is the two-layer invariant in academic form. None addresses hard-edged cut-through features with bevels (inferred). Multires (sculpt subsurf) versus plain subsurf with runtime GPU subdivision instead of baked displacement is noted in a forum answer ([Blender Artists](https://blenderartists.org/t/difference-between-subdivision-surface-and-multiresolution/1277968)).

## Summary table

| Approach | Regenerable from tree | Cage independent | Triangles | Shading under 1-seg bevel + WN |
|---|---|---|---|---|
| Boolean on evaluated mesh, bevel + WN live | yes | yes | high, ragged along cuts | works if bevel sits below boolean and WN last; ragged cut tris need cleanup |
| Support loops in cage | only if loop insertion is generated | no, cage grows | cage low, subdivided high | well behaved; artifact-prone with loop routing |
| Boolean then retopo | no | only if retopo is the cage | controlled | controlled, bake needed |
| Floaters / mid-poly | yes | yes | adds interior tris | seam visible without bake |
| Displacement / detail transfer | yes | yes | displaced mesh resolution | no hard cut-through; bevel not in model |

## Gaps

- `brush-tree-target.md` unread (commit not resolvable locally).
- Blender Bevel (Harden Normals, Set Strength) and Weighted Normal read via search summaries only; raw manual RST URLs 404 and the 4.2 pages returned navigation text first.
- No primary source for Star Citizen, Sea of Thieves, or CDPR pipelines; mid-poly claim rests on one tutorial.
- No source on boolean-after-subdivision as a named deliberate workflow with documented shading outcome.
- OpenSubdiv limit-evaluation pages not reached; Support Loop Pro behaviour not read.
