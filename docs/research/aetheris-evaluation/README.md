# Aetheris evaluation (2026-10-14)

Serves the operator's request to evaluate https://github.com/yuechen-li-dev/Aetheris (a C# AGPL-3.0 B-rep kernel) for capability and ideas, campaign brush-tree, session self-2026-10-14-ag. Facts only, measured at Aetheris 335dfb07df on Yggdrasil; Self's reading is in the conversation, not here. The torture harness is in `harness/`.

# Aetheris evaluation facts

Measured at Aetheris commit 335dfb07df97295c541ab3fcf50e37b9f97b1846 (2026-10-13, "Claude Perf optimization M3"), cloned to
`<scratch>\eyes-aetheris\repo` (read only on Starfire; every build/run on Yggdrasil via ygg-verify.sh, image mcr.microsoft.com/dotnet/sdk:10.0, Linux).
Tags: [V] measured or read this pass; [S] stated by the repo's own docs only, not verified; [M] the author's marketing claim.
Job logs: `<scratch>\eyes-aetheris\jobs\job1..job9.log` (job2 = tests, job6 = torture+canonical, job7/8/9 = OCCT detail probes).
Harness (mine, not Aetheris's): `harness\Program.cs`, `harness\cases.json`, `jobs\ocp_check.py`, `jobs\inspect.py`.

## Q1 Shape of the codebase

- [V] History: 2002 commits, all by one author (Yuechen Li), first 2026-02-25, last 2026-10-13. GitHub: 47 stars, AGPL-3.0 (gh api). 5119 files, 1545 .cs files, 293,876 lines of C#.
- [V] Lines of C# (git ls-files, `.cs`): Kernel.Firmament 66,280; Kernel.Core 57,373; Kernel.Firmament.Tests 40,718; Kernel.Core.Tests 25,513; CLI 12,119; CLI.Tests 10,172; Continuum 8,511; Firmament.FrictionLab 8,244; Surfacing 6,217; SheetMetal 5,749; StandardLibrary 3,831; the rest each under 3.7k. ~50 projects in `Aetheris.slnx`.
- [V] Test attribute counts ([Fact]/[Theory] lines): Firmament.Tests 1886, Core.Tests 909, CLI.Tests 379, FrictionLab.Tests 225, Continuum.Tests 135, Modules.Tests 94, SheetMetal.Tests 85, others smaller. 15 xunit projects.
- [V] CI: one workflow `.github/workflows/dotnet.yml`; the main job is `ubuntu-latest`: restore/build server and kernel tests, `dotnet test Aetheris.Kernel.Core.Tests --filter "Category!=SlowCorpus"`, then build and test the whole solution (`-m:1`). A Windows job (`public-library-build`, `workflow_dispatch` only) packs NuGet libraries. It also checks out a second repo, `yuechen-li-dev/Copeland` at a pinned commit (`scripts/managed-wgsl-commit-pin.txt`), packs it into a local NuGet feed (`.github/actions/prepare-managed-wgsl`).
- [V] Dependencies: Kernel.Core has one NuGet package, `Machina.Typography.OpenFont` (csproj). Kernel.Firmament adds `Copeland.TS.Backend.Wgsl 0.1.0-preview.1-a3.16c0ce996358af80`, which is NOT on nuget.org (restore error NU1101 `Copeland.TS`, job1.log) and has to be built from the Copeland repo. Copeland's licence is GPL-3.0 (gh api repos/yuechen-li-dev/Copeland/license). Other packages: Rhino3dm (3dm import), EF Core Sqlite, Roslyn, Swashbuckle, WebView2, DocumentFormat.OpenXml, PDFtoImage (each one project).
- [V] No OCCT or other native geometry kernel: no P/Invoke except one DllImport in `Aetheris.CLI/CadAssistantInspection.cs`; grep for opencascade/occt in Kernel.Core and Kernel.Firmament .cs finds nothing. OCCT appears only as an interop/validation reference in docs and tests. Geometry code is all C#.
- [V] Surface types (`Aetheris.Kernel.Core/Geometry/Surfaces/`): PlaneSurface, CylinderSurface, ConeSurface, SphereSurface, TorusSurface, LinearExtrusionSurface, SurfaceOfRevolutionSurface, BSplineSurfaceWithKnots (+ BSplineSurfaceRationalReduction), HelicalRibSurfaceRealizer. Curves (`Geometry/Curves/`): Line3, Circle3, Ellipse3, Hyperbola3, BSpline3Curve, CylindricalHelix3, CylinderCylinderIntersectionCurve, plus pcurves.
- [V] So "NURBS genuinely absent" is false as stated: B-spline curve and surface types exist in the kernel, and the STEP outputs of the Perforation/Presentation fixtures contain `B_SPLINE_CURVE_WITH_KNOTS` (job7 ZERO probe). Docs say products are "rational-free"/non-rational (docs/public/reference/supported-features.md, README.md:"exact analytical geometry as its foundation").
- [V] Booleans are not a general intersection engine. `Brep/Boolean/BrepBoolean.cs` (2158 lines) plus ~20 sibling files (8,346 lines total) classify the pair into hard-coded recognition families (`BooleanExecutionClass { PlanarOnly, PlanarWithAnalyticHole, UnsupportedGeneralCase }`, BrepBoolean.cs:36-41; `BooleanTopLevelCase` enum at :74-84): axis-aligned box vs box (orthogonal cells), box with a world-Z cylinder/cone/sphere hole ("safe composition"), cylinder-root centre bore / keyway, prismatic through-cuts. Selection is by `JudgmentEngine` utility scoring (Kernel.Core/Judgment). Everything else returns an Error diagnostic `NotImplemented`. Tolerances: `ToleranceContext.Default` = linear 1e-6, angular 1e-9, relative 1e-12 (Numerics/ToleranceContext.cs:36); the family validators compare against `tolerance.Linear`.
- [V] No exact surface-surface intersection curve solver is used by the boolean entry point; the intersection-curve classes (CylinderCylinderIntersectionCurve, TransverseConePlaneIntersection) are used by feature builders, not by arbitrary boolean pairs (observed behaviour in Q3: Steinmetz refused).
- [V] Firmament does not expose CSG: docs/public/firmament/geometry.md:136 states "public Union / Subtract / Intersect, and general CSG trees are not Preview 3 Firmament features"; `scripts/Test-CanonicalFixtures.ps1` lists `Union|Subtract|Intersect` as a forbidden "legacy arbitrary Boolean authoring" pattern in canonical fixtures. Firmament authors feature-based models (Base, Boss, Pocket, Hole, Slot, Revolve, Loft, SectionChain...). Pocket is documented as "intentionally not arbitrary solid subtraction" (geometry.md:90).
- [V] Firmament -> kernel for CSG-ish work goes through `Aetheris.Kernel.Firmament/Materializer/CirBrepMaterializer.cs`: a registry of exactly three strategies, `subtract(box,cylinder)`, `subtract(box,box)`, `subtract(box,torus)` (the last one an "Unsupported" strategy), chosen by JudgmentEngine, from an SDF graph (`Aetheris.Continuum.Backends.Sdf`) (CirBrepMaterializer.cs:11-18).
- [S] README claims Aetheris is "a solved problem" relative to Parasolid/ACIS/OpenCascade; supported-features.md labels nearly everything "Bounded"/"Experimental" and says "general blend networks ... remain unsupported".

## Q2 Build and tests on Linux (Yggdrasil container)

- [V] Builds clean on Linux: `dotnet build` of Kernel.Core.Tests, Kernel.Firmament.Tests and Aetheris.CLI, Release, 0 errors, 0 warnings in the shown tails (job1/job2), after packing Copeland at the pin by hand. SDK 10.0 image; global.json asks 10.0.203 with latestFeature rollForward.
- [V] `Aetheris.Kernel.Core.Tests` (filter `Category!=SlowCorpus`): Passed 1063, Failed 0, Skipped 0, 27 s (job1.log).
- [V] `Aetheris.Kernel.Firmament.Tests`: Passed 2131, Failed 0, Skipped 0, 4 m 35 s (job2.log).
- [V] SlowCorpus lane (`Category=SlowCorpus`, 52 occurrences in Core.Tests): the run produced no output lines in my tail (job2.log "CORE-SLOW" empty); not established whether it ran zero tests or lacks the NIST corpus files. Unmeasured.
- [-] The other 13 test projects (CLI.Tests, Continuum.Tests, SheetMetal.Tests, Server.Tests, etc.) were not run; the web/TypeScript parts (Telos, Cadmata) were not built.
- [S] README/known-issues: "Release binaries are qualified for Windows x64 only. Framework tests on other platforms are not a binary-support promise." CI nonetheless runs the kernel and full solution tests on ubuntu-latest.

## Q3 Boolean torture (35 cases through `BrepBoolean.Union/Subtract/Intersect` via the public Core API; plus 11 Firmament models; plus 320 canonical fixtures)

Method: `harness/Program.cs` is a console app compiled as assembly `Aetheris.Kernel.Core.Tests` (to reuse the kernel's InternalsVisibleTo, same as the repo's own tests) that builds `BrepPrimitives.CreateBox/Cylinder/Sphere/Torus`, places them with a copy of the repo tests' `TransformBody` helper (extended to Sphere and Torus; plane/cylinder/line/circle only otherwise), runs the boolean, then `Step242Exporter.ExportBody`. Cases in `harness/cases.json`. Primitives are origin-centred; translation/rotation only. Caveat: the test helper does not transform cone surfaces or ellipse curves, which the cases do not use.
Results (job6.log; "vol" is Aetheris's own mass-property status):

| # | case | outcome |
|---|---|---|
| 01 | coplanar face union, box+box face contact | OK, exported |
| 02 | flush slab subtract (coplanar top and sides) | OK |
| 03 | coplanar top pocket | OK |
| 04 | coincident-edge union (edge-only contact) | REFUSED "edge-only/point-only unions are non-manifold" |
| 05 | coincident-edge subtract | REFUSED "rejects tangent/zero-thickness subtract contact" |
| 06 | tangent cylinders union | REFUSED "only supports recognized axis-aligned boxes" |
| 07/08/09 | Steinmetz: cyl r5 x cyl r5 intersect / union / subtract | all REFUSED (07, 08 "only supports ... boxes"; 09 "supports only world-Z aligned root and center-bore cylinders") |
| 10 | subtract leaving two 1e-7 side walls | REFUSED, with the misleading message "subtraction fully removes the left box" |
| 11 | pocket leaving a 1e-7 floor | OK, exported (no sliver refusal at kernel level) |
| 12 | pocket leaving a 1e-4 floor | OK |
| 13/14/15/16 | spheres: tangent / 1e-9 / 1e-4 overlap / 6-apart union | all REFUSED "only supports ... boxes" |
| 17 | box minus sphere centred on top face | OK, exported (see Q4: wrong volume) |
| 18 | torus half cut by a box | REFUSED "only supports ... boxes" |
| 19/20 | torus union cyl / torus minus cyl | REFUSED |
| 21 | 10x10 hole grid, 100 sequential cylinder subtracts | OK, 100/100 steps, 954 ms |
| 22 | two tangent holes | REFUSED "tangent safe-hole composition is rejected to avoid zero-thickness geometry" |
| 23 | hole tangent to side wall | REFUSED with a long explanatory message ("would leave a wall of zero thickness along a line") |
| 24 | two holes with a 1e-7 web | REFUSED (same "tangent" message: 1e-7 < tolerance 1e-6 treated as tangent) |
| 25 | perpendicular cylinder through cylinder, union | REFUSED |
| 26 | coaxial tube (cyl minus smaller coaxial cyl) | OK, exported (see Q4: OCCT segfaults reading it) |
| 27 | blind hole from top | OK |
| 28 | oblique (30 deg) through hole | OK (Aetheris mass-property call threw ArgumentOutOfRangeException; STEP exported) |
| 29 | box intersect sphere | REFUSED |
| 30 | box union box overlapping at an offset corner | OK |
| 31 | blind pocket leaving a 1e-7 side wall | REFUSED "bounded orthogonal pocket family only supports a single mouth or one opposite-face through-slot" (refused for family reasons, not sliver) |
| 32 | union of boxes overlapping by a 1e-7 slab | OK |
| 33 | union with partial face contact | OK |
| 34 | sphere fully inside box subtract (void) | OK, exported as BREP_WITH_VOIDS (see Q4) |
| 35 | cylinder minus enclosed sphere | REFUSED "does not support analytic tool surface kind 'Sphere'" |

- [V] Score: 35 cases: 14 succeeded, 21 refused (typed `NotImplemented` errors, no exceptions), 0 crashed, 0 timeouts. Every refusal message names a missing family rather than the geometry's true difficulty; only 04, 05, 22, 23, 24 are refusals of degeneracy (tangent/edge contact/zero-thickness).
- [V] All general curved-curved cases (tangent cylinders, Steinmetz x3, spheres x4, torus x3, perpendicular cylinders) are refused; none produced a result. The Steinmetz case is not computed.
- [V] A kernel-level sliver of thickness 1e-7 is NOT refused when it is a pocket floor (11) or a union overlap slab (32); the refusal claim holds for hole-hole and hole-wall tangency (22-24) and for pocket floor policy at the Firmament layer (below).
- [V] Firmament models (`harness/fa/*.firmament`, job6.log "FIRMAMENT-TORTURE"): 11 models via `aetheris build`: 4 built (fa05 hole poking through the edge, fa06 two holes with ample web, fa07 10x10 hole grid, fa10 pocket with a 3 mm floor), 7 refused with named diagnostics:
  - fa01 hole tangent to side face: `FirmamentV2.SemanticHoleBuild: rejected: Hole 'Base.H0' ... is exactly tangent to the +X face ... zero thickness along a line` (Materializer/AirHoleFootprint.cs:55)
  - fa02 tangent pair and fa03 1e-7 web: `firmament-v2-semantic-hole-overlap ... would be tangent to previously accepted hole` (AirHoleCompositeMaterializer.cs:80; Core BrepBooleanSafeCompositionGraphValidator.cs:229)
  - fa04 overlapping holes: `overlaps previously accepted hole ... overlapping safe-hole composition is not supported`
  - fa11 pocket with floor 9.9999999 mm deep in 10 mm host, required floor 1e-7: `firmament-pocket-through-depth ... remainingFloor=9.99999993922529E-08mm requiredFloor=1E-07mm` (float rounding put the floor just under the required value)
  - fa12 required floor 0 mm: `firmament-pocket-minimum-floor-policy-invalid`
  - fa13 floor 2 mm < required 3 mm: `firmament-pocket-minimum-floor-thickness` (PrismaticProfileComposition.cs:404)
- [V] Canonical fixtures (`fixtures/Canonical`, 320 `.firmament` files) through `aetheris build` (job6.log): 249 exit 0, 71 exit non-zero. The 71 are almost all not buildable by the `build` verb: garments (11, "garment-step-export-unsupported ... use garment build"), scenes (8, "scene-step-export-unsupported"), FEA/Analysis files (7, "firmament-v2-canonical-declaration-unknown:Analysis"), gear pairs (7, "gear-build-body-count-invalid ... use Assembly"), BodyState (6, "section-chain-section-count-invalid:minimum=2"), assembly components and Guitar/Atlas sub-files (~30, parse errors for partial files or "AssemblyIR must be successfully materialized"), 1 `Pipeline/profile-with-inner-loop` ("profile-segment-identity-collision"). I did not confirm each as expected-failure; they are reported as the CLI printed them.

## Q4 STEP validity checked independently with OpenCASCADE

Method: cadquery-ocp (pip, Ubuntu 24.04, Python 3.12) `STEPControl_Reader` default settings (`ReadFile`, `TransferRoots`, `OneShape`), `BRepCheck_Analyzer.IsValid`, `TopExp_Explorer` counts, `BRepGProp.VolumeProperties`; volume reference from an OCCT boolean (`BRepAlgoAPI_Fuse/Cut/Common`) on identical OCCT primitives and from analytic formulas. (job7.log OCP-CASES, job8.log INSPECT.)

- [V] Harness cases that produced STEP (14): BRepCheck_Analyzer.IsValid = True for the 12 that OCCT could read. Detail:

| case | OCCT reads as | volume Aetheris STEP | OCCT reference |
|---|---|---|---|
| 01 face union | 1 solid, 1 shell, 6 faces | 2000 | 2000 |
| 02 flush slab | 1 solid, 6 faces | 500 | 500 |
| 03 top pocket | compound, 0 solids, 4 shells, 14 faces | 920 | 920 |
| 11 floor 1e-7 | compound, 0 solids, 6 shells, 16 faces | 839.999992 | 840.000001 |
| 12 floor 1e-4 | compound, 0 solids, 4 shells, 14 faces | 840.0016 | 840.0016 |
| 17 box minus sphere (dimple) | 1 solid, 7 faces | **8261.799** | **7738.201** (= 8000 - 261.8); Aetheris's result is 8000 + 261.8, a bump, not a dimple |
| 21 hole grid 10x10 | 1 solid, 1 shell, 106 faces | 87433.629386 | 87433.629386 (analytic 87433.6294) |
| 27 blind hole | 1 solid, 8 faces | 3858.628331 | 3858.628331 |
| 28 oblique hole | 1 solid, 7 faces | 3673.516114 | 3673.516114 |
| 30 offset corner union | compound, 0 solids, 3 shells, 18 faces | 1875 | 1875 |
| 32 1e-7 slab union | 1 solid, 6 faces | 1999.99999 | 1999.999993 |
| 33 partial face contact | single SHELL, 0 solids, 10 faces | 1500 | 1500 |
| 26 coaxial tube | OCCT **segfaults** inside `TransferRoots` (python faulthandler: job9.log SEGV-26) | n/a | 904.1 analytic |
| 34 enclosed sphere void | OCCT **segfaults** inside `TransferRoots` (BREP_WITH_VOIDS + ORIENTED_CLOSED_SHELL .F., job8.log STEP-HEAD-34) | n/a | 7886.9 analytic |

- [V] Every STEP file contains one `MANIFOLD_SOLID_BREP` over one `CLOSED_SHELL` (job8 INSPECT), but for cases 03, 11, 12, 30, 33 OCCT returns no SOLID. Inspecting the case-03 file (job9.log STEPFILE-03, saved as `jobs/case03.step`): 38 `EDGE_CURVE`s, 14 faces, 20 vertices; of the 56 `ORIENTED_EDGE` uses, 18 edges are used twice and 20 edges are used once. A closed shell requires every edge used twice, so this "CLOSED_SHELL" has 20 unmatched edges: faces are fragmented at coplanar/face-contact boundaries without edge sharing. OCCT's volume still sums to the right number; BRepCheck calls the result valid; downstream tooling expecting one solid gets a compound of shells.
- [V] Case 26's file (first 70 non-point lines, `jobs/case26.step`): two sets of three faces, circles r=5 and r=3, each end face a full disc with a single outer loop, no annulus; i.e. the "tube" is expressed as two cylinder shells, not a through-bore. Remaining entities were not inspected.
- [V] Case 17 (box minus sphere): both Aetheris's tessellated volume (8263.2) and OCCT's volume of Aetheris's STEP (8261.8) say the exported body is box + hemisphere. Cause not isolated (could be face orientation of the sphere face in the STEP, `ADVANCED_FACE(...,#119 SPHERICAL_SURFACE, .T.)`, or the harness's translated sphere frame).
- [V] Aetheris's own `BrepMassProperties` returned status `Unavailable` (volume 0) for cases 03, 11, 12, 26, 30, 33, and threw ArgumentOutOfRangeException for 28; `NumericalWithBound` (tessellation based, "not authoritative") for the others.
- [V] Firmament outputs (job6.log OCP-FA): fa05, fa06, fa07, fa10 all read as 1 solid, 1 shell, BRepCheck valid; fa07 (10x10 holes) 106 faces, volume 87433.629386 equals the analytic value; fa10 volume 13648.0 equals 16000-2352 exactly; fa05 8326.43, fa06 8434.51.
- [V] Canonical STEP outputs (253 files from job6, job6.log OCP-CANON, `jobs/canon_dir.txt`): all 253 read by OCCT, BRepCheck valid 253/253. Solid counts: 199 files with 1 solid; 48 multi-solid (assemblies and scenes, 2 to 1366 solids); 6 with 0 solids: SectionChain/open-chain (1 shell, 4 faces, intended open) and 5 where OCCT reported 1 root transferred but 0 solids/shells/faces and volume 0 (Perforation cylindrical-grid-8, -24, -ordning-blank, -staggered-32, Presentation ordning-utensil-holder-blended; files of 0.86 MB to 18 MB with many `B_SPLINE_CURVE_WITH_KNOTS`, `PCURVE`, `EDGE_CURVE`; a rebuild confirmed `success: true` from the CLI, job7 ZBUILD). Why those read as empty was not determined.
- [S] The "no healing needed" claim: the measurement above uses OCCT's default reader (which applies its own shape processing); I did not disable it.

## Q5 GPU renderer ("Three Telos")

- [V] Location `Aetheris.Web.Runtime/telos/` (TypeScript package `@aetheris/three-telos`, AGPL-3.0-only): 3,169 lines of TS/WGSL (host.ts 1067, device.ts 284, temporal.ts 302...). First commit touching it 2026-10-05; 6 commits, latest 2026-10-07.
- [V] It is a WebGPU renderer (`navigator.gpu`, `@webgpu/types`), not CUDA/Vulkan/native. It owns device, attachments, camera, ray queries, mesh/field/line submission; Three.js 0.183.2 is used only for math, input adapters and CPU triangle picks ("Three supplies math and input adapters, never a GPU renderer", telos/README.md).
- [V] Two draw paths: (a) rasterising tessellated triangle meshes (`src/shaders/mesh.wgsl`, `line.wgsl`, `background.wgsl`, 4x MSAA, experimental temporal AA); (b) "field" draws: a per-occurrence quad whose fragment shader sphere-traces a signed distance function with a fixed 512-step budget, normal by central differences, writes `frag_depth` (`Aetheris.Kernel.Firmament/Display/telos-field.v.ts`; docs/release/THREE-TELOS-X0.md). The WGSL is compiled from typed shader source by the Copeland compiler (GPL-3.0 repo), browsers receive WGSL only. The field path is documented only for the cylinder/sphere smoke shaders; "Full CIR-DISPLAY-X1B packet/admission/field default qualification is not claimed" (X0.md), and docs/release/CIR-DISPLAY-X1.md is an "Honest stop" (Cadmata/Helios cannot yet use the field path by default).
- [V] It does not ray trace the B-rep exactly. The B-rep is tessellated by `Brep/Tessellation/*` for the mesh path; picking is CPU (Three Raycaster/server BRep query).
- [V] Headless: the only automation found is Playwright with `chromium.launch({executablePath: msedge.exe, headless: true})` hard-coded to a Windows Edge path (`scripts/display-qa-x1-playwright.mjs:12,51`) and a `tests/browser-witness.ts`; unit tests run with `node --test` on camera/inspection/overlay/temporal logic. Not run in the container; no WebGPU device was tried.

## Q6 Mechanisms

- Degeneracy refusal [V]: it is not a type-system or compile-time proof. It is a layered set of runtime checks that return Error diagnostics before geometry is emitted:
  1. Kernel family validators compare geometry to `ToleranceContext.Linear` (1e-6): tangent hole-hole (`BrepBooleanSafeCompositionGraphValidator.cs:224-233`, `:827`), hole-wall tangency (`BrepBooleanCylinderRecognition.cs:452`), box-box edge/point-only contact ("non-manifold"), tangent spherical cavity (test `Subtract_BoxSphereTangentBoundary_ReturnsTangentContactDiagnostic`, BrepBooleanTests.cs:1555).
  2. Firmament semantic layer: `AirHoleFootprint.cs:55`, `AirHoleCompositeMaterializer.cs:80`, `PrismaticProfileComposition.cs:404` (pocket `MinimumFloorThickness`), profile-level checks (explicit polygons reject degenerate area and self-intersection, boundaries.md:62), template `Require` clauses.
  3. Anything outside the recognised families is refused wholesale (Q3), which also blocks most degenerate cases by construction.
  Observed gap: 1e-7 pocket floors and 1e-7 overlap slabs pass the kernel API (cases 11, 32) and only the Firmament Pocket policy refuses (fa11-fa13).
- Firmament -> kernel [V]: V2 frontend in `Kernel.Firmament/FirmamentV2` (parse, static authoring, Concepts/Templates, validation, lowering), features lowered to "section-stack" operations and `PrismaticProfileComposition`/`AirHole*` materializers, then `BrepPrimitives`/`BrepBoolean`/`Step242Exporter`. V1 TOON/JSON path is kept as frozen compatibility (Kernel.Firmament/README.md). Ownership audit at `docs/development/architecture/system/artifacts/archaeology-m1/`.
- "Constraints erased at compile time" [V]: Firmament has no 2D constraint solver; layout is explicit coordinates in a `Concept Struct Layout On XY { Rect2 Stock { Center; Size } }` block and profiles are built by naming edges with `|>` (fixtures/Canonical/Integration/machined-mounting-block.firmament). Static Records/arrays/Tables, `with` derivation, `Template<...>` specialisation and `Pattern ... Over` are expanded and discarded before geometry (docs/public/firmament/overview.md; templates.md:100-108: `Require Name => BooleanExpression` is finite comparisons "not a general constraint solver", failure stops specialisation before materialisation). Units are part of value types and checked by the binder.
- Forge Host [V]: `Aetheris.Forge.Host` (1.4k lines) is a process protocol "Forge Host Protocol v1": commands `list`, `describe <stable-id>`, `invoke <id> --request - --out <dir>` with a JSON envelope (`protocolVersion`, `arguments` with unit strings like "120 mm", `artifacts`), response JSON with `success`; `describe` returns signature, units, defaults, enum cases, nested Record fields and named `Require` constraints. Clients in Python, Go, Rust, TypeScript shipped in `samples/forge-interop-x1/`; released as NativeAOT exe (Windows-qualified). Doc: docs/public/forge/interop.md; code `Aetheris.Forge.Host/ForgeProtocolHost.cs`, `Aetheris.Forge.KernelSDK/KernelSdk.cs`.
- LLM authoring [V]: repo-level `AGENTS.md` (use the CLI as ground truth, convergence rule: Success / Meaningful progression / Honest stop, fixture-location policy); a skill `docs/public/skills/firmament-modeling-strategy/SKILL.md` (+ `agents/openai.yaml`) on planning shape spines, separating measured vs estimated dimensions, and reporting compiler gaps with reproducible evidence; canonical cookbook `fixtures/Canonical/README.md`; `docs/development` has language audits and grammar inventory. README credits models (GPT-5/6, Claude 4/5, Gemini 3) for both the code and the showcase parts.
- GPU/CIR [V]: see Q5; the shared SDF "CIR" graph (`Aetheris.Continuum`, 8.5k lines) feeds both the field shader and the materializer strategies in Q1.

## Q7 Licence

- [V] `LICENSE` is the 661-line unmodified GNU AGPL v3 text; every csproj inherits `PackageLicenseExpression AGPL-3.0-only` from `Directory.Build.props`; the Telos package.json says AGPL-3.0-only.
- [V] README (section "License and acknowledgments"): "Aetheris code is licensed under the GNU Affero General Public License v3.0. Alternative licensing is available on request. Third-party assets retain their own terms and provenance; see THIRD_PARTY_NOTICES.md." The same line appears in docs/release/*README*.md and the preview-3 notes.
- [V] CONTRIBUTING.md ("Contributor license agreement status"): intended CLA lets contributors keep copyright and grants the owner "non-exclusive rights to distribute contributions under AGPL-3.0 and alternative licenses", with a commitment to continued AGPL availability; `docs/legal/CLA-CANDIDATE.md` is "candidate only; pending review by qualified human legal counsel", no acceptance mechanism is defined, maintainers "should not represent a contribution as having accepted that draft". Companion `CLA-COUNSEL-QUESTIONS.md`.
- [V] All 2002 commits are by the one author, so no third-party contributions exist yet to cover. NIST STEP models and the Stanford Bunny are noted as not under the Aetheris licence (README, THIRD_PARTY_NOTICES.md; earcut adapted from Mapbox, ISC).
- [V] Kernel.Firmament depends at build time on the Copeland repo, licensed GPL-3.0 (gh api), same author.
