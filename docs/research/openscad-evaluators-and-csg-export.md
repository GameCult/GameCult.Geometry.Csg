<!-- Serves brush-tree:question:openscad-surface. Eyes pass eyes-openscad-evaluators, 2026-10-10. -->

# Facts: OpenSCAD evaluators, CSG export, round-trip precedent

Serves: brush-tree:question:openscad-surface (InForce, recommended c; Eyes pass owed before costing options a/b/c; unverified items: Rust evaluator existence, CSG export node set). Eyes, 2026-10-10. Facts only. Tags: FETCHED (page read this session), SEARCH (search-result snippet only), KNOWLEDGE (memory, unverified), LOCAL (ran on installed nightly).

Scratch dir: C:\Users\Meta\AppData\Local\Temp\claude\F--Projects-CultLib\1b994b80-e27e-42a8-8b75-ab8cb1dd9c54\scratchpad\eyes-openscad-evaluators\ (t.scad, t2.scad, out.csg, o2.csg, out.ast, t.nef3, t.param).

## 1. Evaluators / parsers outside OpenSCAD

| Name | What it is | Coverage | State | Licence | Tag |
|---|---|---|---|---|---|
| openscad-rs (github.com/ierror/openscad-rs, docs.rs/openscad-rs) | Rust parser to typed AST. No evaluator, no include resolution, no geometry. | literals, precedence, vectors, ranges, list comprehensions, functions, modules, children, modifiers, include/use (parsed only). Numbers as exact hyperreal::Real. Tested against vendored upstream OpenSCAD fixture corpus (regression floor, not full acceptance); cargo-fuzz. | v0.1.0, release 14 Sep 2026; 15 commits; 2 stars | Apache-2.0 OR MIT (repo page); docs.rs page said GPL-3.0-or-later (the two disagree) | FETCHED |
| scad-rs (github.com/Michael-F-Bryan/scad-rs) | "A Rust implementation of the OpenSCAD virtual machine"; topics bytecode-VM, compiler, parser; scad.ungram grammar; openscad as submodule for compat tests | README gives no feature or maturity detail | 104 commits, 31 stars, not archived; last-commit date not shown; crates.io listing not confirmed | Apache-2.0 / MIT | FETCHED (README), maturity UNKNOWN |
| scad, scadman, scad_tree, flowscad (crates.io) | Generators (Rust emits .scad). Not parsers/evaluators. scad 1.2.2 last updated 2019; scadman 0.2.2 Dec 2025 | n/a | | | SEARCH |
| tree-sitter-openscad (github.com/openscad/tree-sitter-openscad) | Incremental tree-sitter grammar; npm @openscad/tree-sitter-openscad; Rust crate tree-sitter-openscad-ng; pyproject/setup.py present | syntax only | 154 commits, 11 stars; last-commit date not shown | MIT | FETCHED |
| openscad_parser (github.com/BelfrySCAD/openscad_parser, PyPI) | Python parser (Arpeggio PEG; also an LALR variant openscad_lalr_parser feeds the evaluator) to AST | Claims "Full OpenSCAD language support": functions, modules, let/echo/assert, function literals, list comprehensions (for, C-style, if, let, each), modifiers, use/include; strict_commas() mimics 2021.01 | 202 commits; PyPI mirror snippet showed 2.4.7 (SEARCH) | MIT | FETCHED (README), version SEARCH |
| openscad_evaluator / PyPI openscad-evaluator (github.com/BelfrySCAD/openscad_evaluator) | Python AST evaluator producing Manifold geometry from the openscad_lalr_parser AST. v1.8.1 (26 Sep 2026); 1.0.0 was 20 Jul 2026; Python 3.11+; 214 commits | docs/evaluator.md (read first 100k of 127k chars): user functions, closures, default params, tail calls; let (expr+stmt); list comprehensions incl. C-style for, let, intersection_for; modules, children() (index, separate=true extension), $children, parent_module(); include and use with namespace isolation; hull (accepts open meshes); minkowski (+ minkowski_difference extension, 3D); multmatrix (3D only; 2D children pass through unchanged); polyhedron (four input forms; open mesh dropped by booleans). README: full built-in coverage of primitives, transforms, booleans, 2D, text(), surface(), DXF/3MF import, roof(). Noted limitation: same-name double binding in one let "unhandled edge case". | | MIT | FETCHED |
| (same) CSG tree exposure | evaluate() builds persistent `self.csg_tree` (list of CSGNode) in a resolve pass before any Manifold work; generate_tree() fills bodies; flatten_csg_tree(); id_to_node and id_to_call_chain map bodies back to source | | | | FETCHED |
| openscad-wasm (github.com/openscad/openscad-wasm) | Full OpenSCAD port to WASM; ES module; `await OpenSCAD({noInitialRun:true})`, FS.writeFile, `callMain([...cli args])`, FS.readFile. 428 stars, 99 commits; no releases listed; no npm package named on page | same as desktop (it is the C++ core) | | GPL-2.0 | FETCHED |
| openscad-playground (github.com/openscad/openscad-playground; npm openscad-playground "React component") | Browser app on a headless WASM OpenSCAD; README: "Licenses: see LICENSES" | | | not retrieved | SEARCH |
| SolidPython | Generator (Python emits .scad), not an evaluator | | | | KNOWLEDGE (not re-checked) |
| csgrs, synaps-cad | Named as related projects on openscad-rs README (geometry / interactive CAD) | not inspected | | | FETCHED (names only) |

No Rust crate found that evaluates OpenSCAD to a tree or mesh (SEARCH x2; scad-rs is the only candidate, maturity unknown). The only found evaluator is Python (openscad_evaluator).

## 2. OpenSCAD's own export (installed nightly)

LOCAL: `C:\Tools\OpenSCAD-2026.09.23-x86-64\openscad.com --version` -> `OpenSCAD version 2026.09.23` (git 28fe66bc). Default backend Manifold 3.5.2 (CGAL 6.1 available via --backend). `--info` Features list: roof, input-driver-dbus, lazy-union, vertex-object-renderers-indexing, textmetrics, import-function, object-function, predictible-output, vector-swizzle, discretization-by-error, ai-features, unicode-identifiers.

`--help` `-o` extension list: stl, off, wrl, 3mf, csg, dxf, svg, pdf, png, echo, ast, term, nef3, nefdbg, param, pov. `--export-format arg` overrides the format. `-o x.json` -> "Invalid suffix json" (no JSON export). `--summary-file` writes render stats as JSON (not a tree). `--help-export` lists -O settings (grep for csg/ast/json matched nothing). No library mode in help; `--enable` and `-D` exist. KNOWLEDGE: no libopenscad ships; wasm build drives it through callMain (see above).

Test file t.scad (10 lines): function sq, module m with for + translate, `let(a=3) m(a);`, hull{sphere,translate cube}, multmatrix+polyhedron, minkowski, linear_extrude(twist), rotate_extrude of translate+circle.

**.ast export** (out.ast, 558 B): pretty-printed source of the parsed (unevaluated) program. Keeps function/module definitions, `for`, `let`, calls, operators as text, with parentheses inserted: `function sq(x) = (x * x);` `for(i = [0 : (n - 1)]) translate(...)`. Nothing evaluated; named-argument order preserved. Text, not JSON.

**.csg export** (out.csg, 1267 B), evaluated tree as OpenSCAD text, all literals:
- functions, module definitions, `let`, for loops are gone. The for loop becomes `group() { group() { group() { multmatrix(...) { cube } ... } } }` with i*sq(2) folded into translation matrices (4, 8).
- `translate`, `rotate`, `scale`, `mirror` all become `multmatrix([[..4x4..]])` (translate([5,0,0]) -> matrix with 5 in column 4; mirror gives `-0` entries: `[-1, -0, -0, 0]`). No translate/rotate/scale/mirror survive.
- Kept as nodes with literal params: `hull() { sphere($fn=8,$fa=12,$fs=2,r=1); multmatrix(..){cube(size=[2,2,2],center=false);} }`, `polyhedron(points=[..], faces=[..], convexity=1)`, `minkowski(convexity=0){cube; sphere}`, `linear_extrude(height=2, twist=10, $fn=0,$fa=12,$fs=2){square(size=[3,3],center=false);}`, `rotate_extrude(angle=360,start=180,convexity=2,$fn=12,...){multmatrix{circle(...)}}`, `difference(){cube; multmatrix{cube}}`, `polygon(points=..., paths=undef, convexity=1)`, `import(file="nonexist.stl", origin, scale, center, convexity, $fn,$fa,$fs, timestamp=0)` (written even though the file is missing).
- Primitives are fully defaulted: `cube(size=[1,1,1], center=false)`, `cylinder($fn=5,$fa=12,$fs=2,h=1,r1=1,r2=0.5,center=false)`; `sphere(...)` gets `$fn,$fa,$fs,r`.
- Variables/list comprehensions: table `tbl=[for...]` consumed at evaluation; only resolved values appear. `children()` in module `wrap` expanded inline (`multmatrix` for the translate then `group(){...}`).
- Redundant `group()` wrappers appear with default settings (3 nested for the for-loop, extra for children).
- `--enable=all` changes the output (diff vs default): group wrappers collapse (lazy-union) and `$fe = 0` is added to sphere/linear_extrude/rotate_extrude/circle calls. Default and enable=all are different texts for the same program.
- Re-reading: `openscad o2.csg -o o2b.csg` succeeded, byte-identical size (1568 B both); emitted `WARNING: variable "timestamp" not specified as parameter in file o2.csg, line 37` for the import() line.
- No source line numbers, instance paths, names or ids appear in the .csg.
- `.param` export produced 13 bytes (customizer params); `.nef3` 256 KB (CGAL Nef dump of the geometry, not a tree).

## 3. Round-trip precedent: program + edits

- FreeCAD OpenSCAD workbench. FETCHED via search snippets only (wiki page itself returned an Anubis block): contains a CSG importer for OpenSCAD .csg and an exporter of a CSG-based tree; OpenSCAD itself must be installed to convert .scad to .csg first; non-CSG geometry is exported as a mesh; Ply required to parse .csg since 0.19. Sources do not say edits flow back to OpenSCAD variables (UNVERIFIED). https://wiki.freecad.org/OpenSCAD_Workbench
- CadQuery / CQ-editor: SEARCH. CQ-editor edits the script, with debugger and export. CQGI discovers user parameters through script metadata and the host supplies new values at build(). Sketch API has tag()/select(tags); a roadmap page (test mirror) lists tag propagation as planned. No built-in direct-edit-to-override found. https://cadquery-ja.readthedocs.io/ja/latest/cqgi.html , https://cadquery.readthedocs.io/en/latest/selectors.html
- build123d: SEARCH. Python CAD with builder/algebra/direct APIs; no override mechanism found. https://build123d.readthedocs.io/en/latest/
- Fusion 360: SEARCH (2014 Autodesk announcement). Timeline is a history of commands; direct operations such as edit form and patch are not captured in the timeline. Current behaviour not checked. https://www.autodesk.com/products/fusion-360/blog/january-2014-update-is-available/
- Onshape: SEARCH. Direct edits on imported geometry are captured as features in the feature list; a FeatureScript custom feature executes at regeneration and cannot modify the feature list (employee forum answer). https://www.onshape.com/en/blog/parametric-editing-vs-direct-editing-cad-systems , https://forum.onshape.com/discussion/20673/how-to-edit-the-code-of-a-shape
- Blender Geometry Nodes: SEARCH returned nothing on apply-vs-override; the manual states per-modifier input values on a shared group (https://docs.blender.org/manual/es/3.0/modeling/modifiers/generate/geometry_nodes.html). KNOWLEDGE (unverified): the modifier is non-destructive and edit-mode changes to the evaluated mesh are not stored back; "Apply" bakes the result; Blender 4.x adds a Bake node.

## Gaps
- scad-rs maturity/last commit and crates.io status unchecked; openscad-rs licence conflict (Apache/MIT vs GPL-3 on docs.rs) unresolved; openscad_evaluator last 27k chars of evaluator.md and TODO.md unread; no hull/minkowski/multmatrix correctness comparison run against OpenSCAD.
- The Python evaluator's CSGNode shape was not inspected; whether it keeps pre-flattened structure (names, call chains) beyond id_to_call_chain unknown.
- CSG export of `use`/`include`, `children(i)`, `$`-special vars, `text()`, `surface()`, `render`, `intersection_for`, modifiers (#, %, !) not tested.
- FreeCAD importer's per-node mapping (hull, polyhedron, minkowski) not retrieved. Fusion/Onshape/Blender current behaviour not verified from vendor docs.
- openscad-playground and openscad-wasm npm publication/licence text (LICENSES) not retrieved. SolidPython not re-checked.
