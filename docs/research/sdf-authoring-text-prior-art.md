# SDF authoring text: prior art

Fork: campaign `brush-tree`, question `openscad-surface` (map rows "Parametric layer" and "Authoring text", `docs/brush-tree-map.md`; invariants `text-round-trips` and `text-is-a-surface`, `docs/brush-tree-target.md`; GameCult.Geometry.Csg branch `eureka/brush-tree`, commit a7879dad). Gathered by Eyes agent `eyes-bt-sdf-text`, session `self-2026-10-11-ag2`, 2026-10-12. Facts with pointers; lines marked "(inferred)" are not facts from a source.

Method limits: web pages were read through a summarising fetcher, not raw. Several raw-file fetches returned 404, so items under "Not verified" (section 5) were not read. The mind query for `brush-tree:question:openscad-surface` returned the whole store with no match for that id, so the question text itself was not read; its content is taken from the map and target docs. The commit is in `F:\Projects\GameCult.Geometry.Csg`, not in the CultLib checkout.

## 0. The local side (what the text must express)

- `src/field.rs` @ a7879dad: `Add` = `min`, `Subtract` = `d.max(-b)`, `Intersect` = `d.max(b)` (`stream_distance`), all f32 (bevy_math). Primitive distances: oriented box exact; cylinder exact; ellipsoid is a bound; floret arm a max-of-planes bound. No smooth union exists in the file at this commit.
- Target needs (`docs/brush-tree-target.md`): primitives, transforms, scoped booleans, smooth unions with a named radius, creases as hard `max`, per-part `field`/`kernel` declaration. Map row Brush: identity "carried in the text as a named argument, plus a human name".
- Map row "Authoring text (OpenSCAD-shaped)": not persisted as truth; header names tree key and base revision; parsed back only through the commit primitive; stale base refused.
- OpenSCAD has no smooth union. Searched: no native OpenSCAD smooth-union feature or PR was found; mailing-list threads (lists.openscad.org) point to `minkowski()` and hull-based fillets; BOSL2 offers `round_corners`, `offset_sweep`, `rounded_prism` (rounding of paths and prisms, not a field blend; github.com/BelfrySCAD/BOSL2 wiki rounding.scad).

## 1. Survey

### libfive
- Syntax: Scheme (Guile) `(union a b)`, `(blend-expt a b m)`; Python bindings from the same stdlib; C API; Studio GUI (OpenSCAD-like live coding).
- Round trip: shapes evaluate to an expression `Tree`; no documented text print/parse of the tree. The Scheme source is the text.
- Smooth: `blend_expt(a,b,m)` ("using exponents"), `blend_expt_unit`, `blend_rough` ("may not preserve gradients"), `blend_difference(a,b,m,o)`. Hard: `union`/`intersection`/`difference` (variadic; difference = intersection with inverse of the union of the rest). Formulas not read (header comments only).
- Licence: libfive, stdlib, Python bindings MPL-2.0; Guile bindings and Studio GPL-2.0+. README copyright 2015-2021, no status statement; Guile bindings Linux/macOS only.
- Rust: community bindings listed in README, not checked. Vocabulary: large stdlib.
- Source: github.com/libfive/libfive README; stdlib Guile csg.scm; libfive_stdlib.h.

### Fidget (Matthew Keeter)
- Syntax: Rust library; Rhai scripts via `fidget-rhai` 0.5.1: `circle(#{ center: [1, 2], radius: 3 }).move(#{ offset: [1, 1] })`, `difference(a, b)`, `union(a, b, c, ...)`, `axes()` returns x,y,z; operators on trees build nodes rather than compute. `fidgetpy` (Python) and a third-party Koto fork exist (README).
- Round trip: `Context::from_text` parses a flat node-per-line form (address, op name, operand addresses; `var-x`, `const 1`, `square <addr>`); docs.rs: "loosely defined and only intended for use in quick experiments". `Context` ops: add sub mul div modulo min max atan2 mix compare and or, neg recip abs sqrt square sin cos tan asin acos atan exp ln floor ceil round not rand, `if_nonzero_else`, `deriv`. Canonical tape bytecode exists (README). A Rhai script is a general program (loops, conditionals) evaluated once; no printer from tree back to script is documented.
- Smooth: no smooth-min builtin seen in `Context`; the docs.rs rhai page lists only `union`/`difference` and does not mention min/max/blend. Smooth forms would be composed from the math ops. Crease = `max`.
- Licence MPL-2.0. Maintenance: sole maintainer, "personal-scale experimental project"; README recommends pinning 0.4.1 to avoid LLM-influenced code; unlikely to merge changes with substantial maintenance burden.
- Rust: native (`fidget` on crates.io; JIT aarch64/x86_64; Manifold Dual Contouring meshing). Rhai vocabulary on docs.rs: circle, sphere, move, union, difference, vec2/vec3, sin/cos, constants (partial list).
- Source: github.com/mkeeter/fidget; docs.rs/fidget-rhai; docs.rs/fidget Context.

### Curv
- Own pure functional language; shapes are first-class values; GPU render, mesh export STL/OBJ/X3D. `lib.blend`: "14+ blending kernels" (Codeberg README); names not read.
- Round trip: not documented. Licence Apache-2.0 (GitHub sidebar). GitHub repo archived 2023-09-27, development moved to Codeberg (codeberg.org/doug-moen/curv, maintained by Tim Ayres; most recent commit shown 2026-09-26). No Rust.

### fogleman/sdf (Python)
- Syntax: `sphere(1) & box(1.5)`, `a | b.k(0.25)`, `union(a, b, k=0.25)`, `.translate((1,2,3))`; `@sdf3` / `@op3` decorators for custom ones.
- Round trip: none; the Python expression is the text; no serialisation mentioned.
- Smooth (dn.py): union `h=clip(0.5+0.5*(d2-d1)/K,0,1); m=d2+(d1-d2)*h; d=m-K*h*(1-h)`; difference `h=clip(0.5-0.5*(d2+d1)/K,0,1); m=d1+(-d2-d1)*h; d=m+K*h*(1-h)`; intersection `h=clip(0.5-0.5*(d2-d1)/K,0,1); m=d2+(d1-d2)*h; d=m+K*h*(1-h)`. Hard: np.minimum / np.maximum / `max(d1,-d2)`. `K = k or operand._k`, so `k=0` is falsy and falls to the operand's `_k` or the hard form. Separate `blend` is linear `K*d2+(1-K)*d1`, default 0.5.
- Vocabulary (about 60 names): 3D primitives sphere box rounded_box wireframe_box torus capsule capped_cylinder rounded_cylinder capped_cone rounded_cone ellipsoid pyramid; 4 Platonics; plane slab cylinder; text image; translate scale rotate orient; union difference intersection and smooth versions; repeat circular_array; blend dilate erode shell elongate twist bend bend_linear bend_radial transition_linear transition_radial wrap_around; extrude extrude_to revolve slice; 2D set.
- Licence MIT. 209 commits, 28 open issues, 8 open PRs; last-commit date not shown. No Rust.

### hg_sdf (Mercury)
- GLSL library: primitives, domain folds (`pMod1`, `pModPolar`, ...), booleans in rounded, chamfered, columned and stairs variants: `fOpUnionRound`, `fOpUnionChamfer`, `fOpUnionStairs`, `fOpPipe`, `fOpEngrave`. `fOpUnionSoft` not on the fetched page.
- Not a language; no tree. Licence "MIT OR CC-BY-NC-4.0" (page, 2021-07-28 entry). No Rust.

### Inigo Quilez (distfunctions, smin)
- GLSL snippets. From the smin article (via search summary): exponential, power, root, polynomial families; polynomial `h=max(k-|a-b|,0)/k; min(a,b)-h*h*k/4`, equivalent to the clamped-`h` form. "opSmoothUnion" is a library name (Houdini HDK, pyssv); pyssv uses a cubic `h^3*k/6`. Smooth intersection is the negated smin of negations. Code licence not found; distfunctions page fetch returned 404.

### Shadertoy convention
- `float map(vec3 p)` returning `min(...)` or `smin(a,b,k)` copied from IQ; crease by `max`. Hand-written code; no round trip; per-shader licence. (From general knowledge, not fetched.)

### OpenSCAD and BOSL2
- Tree-structured CSG text; OpenSCAD's own `.csg` export prints a CSG tree (general knowledge, not fetched). No smooth operation; see section 0.

### ImplicitCAD (Haskell)
- Haskell DSL plus `extopenscad`, an OpenSCAD dialect with extensions (README): rounded union `union(r=14){...}`; `linear_extrude` accepts `r`; curried functions, `map`. Haskell API: `unionR`, `differenceR`, `intersectR :: ℝ -> [obj] -> obj` (radius first); internal constructors `UnionR`, `DifferenceR`, `IntersectR` in 0.4.1.0 source. README shows rounded union only; rounding formula not read.
- Licence AGPL-3.0+ (source headers on Hackage). README status dated 2020-01-26, "very much a work in progress"; hull and minkowski unfinished. No Rust.

### sdfx (Go)
- Go code: `Union3D(sdf ...SDF3)`, `Difference3D(s0, s1)`, `Intersect3D`, `Transform3D(sdf, M44)`; `SetMin(MinFunc)` / `SetMax(MaxFunc)` replace the min and max a boolean uses (default `math.Min`/`math.Max`). Smooth-min type names not found in the visible file. Licence MIT; 850 commits, 12 open PRs; latest commit date not shown. No tree text. No Rust.

### Blender geometry nodes SDF
- SDF Grid Boolean (Intersect, Union, Difference), SDF Fillet, SDF Grid Offset, Mean, Median, Laplacian, Mean Curvature, Mesh to SDF Grid, Grid to Mesh (Volume Nodes manual, 5.1; 5.3 adds Deactivate Voxels and Grid Topology Boolean). Node graphs live in .blend datablocks, scriptable by `bpy`; operate on voxel grids, not closed-form distance. Licence GPL. No smooth-union parameter read on the Boolean node.

### MagicaCSG, Womp
- Closed GUI products; not fetched. Nothing verified.

## 2. Findings that bear on the fork

1. No surveyed tool documents a typed field tree printed to a text surface and parsed back as its canonical form. Nearest: Fidget `Context::from_text`, a flat math-node DAG (min, max, sqrt, ...), self-described as experiment-only; it carries no primitives, transforms or named radii.
2. libfive, Fidget-Rhai, fogleman, Curv and sdfx authoring surfaces are general programming languages evaluated to a value. A printed typed tree would be a restricted subset of such a language (inferred); none documents a canonical printer.
3. Smooth union is a binary operator with a scalar width everywhere: fogleman `a | b.k(k)` / `union(a,b,k=)`, ImplicitCAD `union(r=)` / `unionR r [..]`, hg_sdf `fOpUnionRound(a,b,r)`, libfive `blend_expt(a,b,m)`, IQ `smin(a,b,k)`.
4. The blend function differs per tool, so a radius number is not interchangeable: quadratic `k*h*(1-h)` (fogleman, IQ polynomial), cubic `h^3*k/6` (pyssv), exponent-based (libfive), round/chamfer/stairs (hg_sdf). "Named radius" means whatever `src/field.rs` implements.
5. Crease is hard `max`/`min` in all of them; no surveyed text language has a separate crease token.
6. Precedent for an OpenSCAD-syntax dialect carrying rounded union: ImplicitCAD `extopenscad` `union(r=...)`. README shows no rounded difference or intersection there; Haskell AGPL; 2020 status note.
7. None of the surveyed surfaces has a first-class stable-id slot for nodes; named arguments are available in OpenSCAD, Python and Rhai (`#{k: v}` maps) (inferred carrier).

## 3. Evaluating exactly our distance function (invariant one-distance-per-primitive)

- Libraries with their own primitives (libfive, Fidget stdlib, fogleman, hg_sdf, sdfx, Curv) compute their own formulas. Our ellipsoid and floret are explicit bounds in `field.rs`; library ellipsoids are different formulas (inferred; fogleman's ellipsoid not read).
- Fidget could evaluate our distance only if each primitive is written out in its math nodes (it has sqrt, min, max, abs, mul, compare, if_nonzero_else, exp, ln). Whether its interpreter and JIT backends give bit-equal f32 results to our `bevy_math` code was not examined (inferred risk).
- A text front end that only parses into our typed tree and leaves evaluation to `src/field.rs` has one distance by construction (inferred); the other systems then serve as syntax prior art only.
- fogleman's smooth forms are plain arithmetic and can be compared term by term with a Rust implementation of the same quadratic form.

## 4. Rust availability

- Fidget and `fidget-rhai`: yes (crates.io, MPL-2.0, file-level copyleft). Rhai is itself a Rust embedded scripting engine (used by fidget-rhai). libfive: C++, community Rust bindings listed, unchecked. Others: none. Rust OpenSCAD parser crates were not surveyed.

## 5. Not verified

- libfive `blend_expt`/`blend_rough` formulas; Curv `lib.blend` kernel names; sdfx smooth-min type names; IQ code licence; hg_sdf `fOpUnionSoft`; ImplicitCAD rounded difference/intersection syntax and blend formula; full Fidget Rhai function list; whether `fidgetpy` exposes smooth ops; MagicaCSG and Womp text forms; BOSL2 and OpenSCAD licences as fetched; OpenSCAD `.csg` export behaviour; Shadertoy conventions (from general knowledge); the text of `brush-tree:question:openscad-surface`.
