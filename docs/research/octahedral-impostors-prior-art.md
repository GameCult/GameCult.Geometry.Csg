# Relightable octahedral impostors: prior art

Eyes pass, 2026-10-10. Operator: "Wild idea, if we are marching, why not output into an impostor. Go look at those fancy impostors that shade and everything." and "Octahedral is what I was thinking. But we are just using it to cache ray marching samples? Kind of a stretch feels like". Companion to brush-surfaces-and-sdf-bricks-prior-art.md. Facts only; tags mark FETCHED, SEARCH and KNOWLEDGE (unverified).

# Relightable impostors: prior-art facts (eyes-impostors, 2026-10-10)
Tags: FETCHED = read on the page; SEARCH = from search-result summary only; KNOWLEDGE = unverified recall.
Gaps: shaderbits.com (Brucks blog) returned only tag list via WebFetch; fortnite.com 403; NVIDIA GPU Gems 3 ch.21 404; Amplify wiki 403; EG digital library 403; web.archive.org blocked. Brucks' primary text was NOT read; Epic's ImpostorBaker doc (primary) was.

## 1. Techniques
### Octahedral impostors / Epic ImpostorBaker (UE)
- FETCHED (dev.epicgames.com/documentation/en-us/unreal-engine/impostor-baker-plugin-in-unreal-engine): baker captures GBuffer, no material switch needed; translucent materials unsupported.
  Colour maps: BaseColor, Normal, Emissive, Subsurface, Tangent, CustomLighting, Lit (most need only BaseColor+Normal).
  Channel-packed masks: Specular, Roughness, Metallic, Opacity, Opacity Mask, Depth/Anisotropy, ClearCoat, ClearCoatRoughness; no alpha channel => DXT1 instead of DXT5.
- FETCHED (same): FramesXY per axis; 16 => 256 frames. Epic uses 12 (144 frames) for distant foliage in Fortnite, final texture 2048 (~170 px per frame). Capture res default 512, >= 2x final subframe for supersampling. Traditional billboards = 3x3 (8 side + 1 top).
- FETCHED (same): runtime finds the 3 nearest captured frames and blends them on one sprite (8 tris, 9 verts; billboard cross 72 tris/81 verts). Mobile: single frame sample. Pixel shader costlier from 3-frame blend.
- FETCHED (same): parallax modes None / Single Sample (bump-offset-like) / Iterative (most expensive, reference quality; with Depth Derived Weights "nearly identical" to source mesh if all channels captured). Needs sprite vertex shader (clipping, more masked overdraw). Artifacts on very dense objects.
- FETCHED (same): lighting is dynamic from baked normals + material masks; "Impostor Casts Shadows" affects editor preview only. Perspective capture needed for fresnel. No memory figures, no runtime switch distance (only editor "Swap by Distance").
- FETCHED (80.lv/articles/impostor-baker-for-ue4/, 2018-04-09): modes Full Sphere / Upper Hemisphere / Traditional Billboards; octahedral layout uses texture space better than old generator; Pixel Depth Offset uses captured depth so cards intersect world; POM smooths frame transitions but expensive.
- SEARCH: Brucks' 2018 blog (shaderbits.com/blog/octahedral-impostors, not read) is the origin cited by three.js, Godot, Unity ports.

### Open-source ports (reference code)
- FETCHED (github.com/Usnul/IMP): Unity billboard-impostor baker, CC0, hemisphere or full sphere, Window>IMP, written for Unity 2017/2018. Credits Brucks, Bruneton&Neyret forest paper, Todt/Rezk-Salama/Kolb spherical light-field rendering. README gives no channels/frames/depth detail.
- FETCHED (github.com/SIsilicon/Godot-Octahedral-Impostors): MIT; bakes base.png, norm_depth.png, orm.png; recommended grid 16; hemi vs full; grid blending; depth map (+Depth Scale) only in Standard shader, which also does shadows, metallic/roughness, alpha prepass. Names Unity impl as github.com/xraxra/IMP.
- FETCHED (discourse.threejs.org/t/a-forest-of-octahedral-impostors/85735): demo 200k trees, mesh LOD 15-100 units, impostor beyond 100; hemi-oct, 16 sprites/side, 2048 texture, parallaxScale 0.5. Usnul's impl: variable atlas/grid res, mip margins, bakes depth/normal/PBR/albedo/alpha ("enabling relighting and depth compositing"); convex-hull sprite fit removed ~30% pixels with 5 verts; interpolation lines likely from missing secondary reprojection; switch only when impostor <= bake resolution on screen (no dithering needed); fading draws two LODs. Repo github.com/Ctrlmonster/three-octahedral-impostor (not read, licence unchecked).
- FETCHED (app.cinevva.com blog 2026-05-04 part 19, hobby blog): diffuse + world-normal atlases only; 12x12 hemi-oct = 144 tiles x 2 passes = 288 RT passes, ~9 MB; 5x5 az-el ~1.6 MB; bilinear 2x2 tile blend = 8 taps; popping at tile swaps cured by blending; top-down view collapses azimuth; hemi-oct bake ~5x slower than az-el, run once at load.
- SEARCH: SideFX Houdini impostor tool bakes full octahedral/3D/fixed-axis/animated, Unity package in its GitHub download (licence unverified). Unity asset "Impostor Graph" (octahedral) exists, not read.

### Amplify Impostors (Unity)
- FETCHED (amplify.pt/_AI): types Spherical (no smooth view blend), Octahedron (smooth blend), HemiOctahedron (top-view games, more res per view). Bakes views plus "normals and depth"; depth enables intersection with meshes/impostors; casts and receives shadows, full lighting. Built-in, URP, HDRP; Forward and Deferred. Standard bake needs a shader with Deferred path (e.g. Standard); forward-only shaders need custom bake shader from Amplify Shader Editor. Channel list/parallax not on page.
- FETCHED (assetstore.unity.com/packages/tools/utilities/amplify-impostors-119877): EUR 55.20 (search snippet: $60); Extension Asset, Standard Unity Asset Store EULA; v1.0.4, 2026-05-28; 201.2 MB; Built-in/URP/HDRP listed compatible (2019.4, 2021.3, 2022.3). Whether C# source ships: not stated.
- KNOWLEDGE (unverified): Amplify bakes albedo/alpha, normal+depth, spec/smoothness, emission; depth offset via SV_Depth.
- FETCHED (docs.unity3d.com Industry Toolkit 3.0 create-impostors): octahedron/hemi-octahedron; "Atlas size" = sqrt(frames); maps res e.g. 4096; shadows in BiRP/URP/HDRP; depth-offset object intersections HDRP only; LOD crossfade; not for Unity built-in trees; licence unstated.

### Relief / true impostors / IBR with depth
- FETCHED (history.siggraph.org/?p=139448): Risser "True Imposters", SIGGRAPH 2006 poster (GPU Gems 3 ch.21, 2007 per SEARCH): billboard as window onto height-fields, up to 4 height-fields per texture, per-fragment linear march + binary search, any view angle, regenerated per frame; no cost/artefact numbers on page.
- SEARCH: Andujar et al. "Omni-directional Relief Impostors", CGF 26(3) 2007 pp553-560: reduced set of relief maps, typically 3 selected per view, ray-heightfield intersection on GPU. Clua 2004 PUC-Rio thesis: relief impostors refreshed dynamically. Policarpo&Oliveira relaxed cone stepping (GPU Gems 3) is the march basis.
- SEARCH: Decoret/Schaufler/Sillion/Dorsey 1999 "Multi-layered impostors for accelerated rendering" (EG99): dynamically refreshed layers, progressive refinement when viewer slows, de-occlusion error bounded to user threshold, update must fit frame budget. Jeschke thesis (cg.tuwien.ac.at/research/publications/2005/jeschke-05-ARI): impostor valid only in bounded view region; high memory for common scenes open problem; layer placement bounds parallax error; Jeschke&Wimmer 2002 textured depth meshes. Billboard clouds (Decoret 2003), Schaufler "dynamically generated impostors" 1995: not fetched (KNOWLEDGE).

### Artefacts, general
- FETCHED/SEARCH: frame popping from angular undersampling or bad blend; hemi-oct top-down degeneracy; parallax artefacts on dense objects; sprite clipping with parallax; close-range disocclusion (regions unseen at bake appear); memory = frames x res x channels (9 MB for 12x12 two-channel example).

## 2. Raymarcher -> impostor atlas
- SEARCH (several queries): no system found that raymarches SDFs/volumes into octahedral impostor atlases, offline or runtime re-bake; no re-bake cost figures.
- Closest: Polycount thread (polycount.com/discussion/comment/2614341): SDF baked into impostor-style atlas in Houdini/Substance; raw SDF atlas needed 16K x 8K for 512 output vs 8K x 4K for 16x8 impostor layout (offline, not raymarcher output).
- Cost data points only for mesh bakers: Epic captures 144-256 frames at 512 capture res (editor time); cinevva bake 288 RT passes once at load. Runtime re-bake benchmarks: none.
- Dynamic impostor refresh is old art (Schaufler 1995, Decoret 1999, Clua 2004): refresh when error metric exceeds threshold, budgeted per frame; trigger details not fetched.

## 3. Depth-correct compositing
- SEARCH (Unity forum 830595, gamedev.net MJP, Khronos): writing SV_Depth disables early-Z regardless of value; discard/clip/alpha-test likewise on most hardware; cost large under overdraw. Conservative outputs (SV_DepthGreaterEqual/LessEqual) can keep early-Z; gamedev.net thread reports mixed results (GreaterEqual+Less OK, LessEqual+Greater seemed to defeat early-Z); hardware-dependent.
- FETCHED: Amplify and Epic both advertise depth-offset intersection (Epic Pixel Depth Offset; Unity Toolkit HDRP only). Amplify: shadow cast+receive. Godot port: shadows only in Standard shader (with depth). Unity Toolkit: depth capture enables shadow casting.
- No shipped-title profiling numbers found.

## 4. Where impostors are used
- FETCHED: Epic uses 12x12 octahedral for distant foliage in Fortnite. Unity Toolkit: "mainly far-distance LODs". three.js demo switches at 100 units (trees). Rule of thumb (Usnul): use when impostor <= bake resolution on screen.
- SEARCH: asset listing warns impostors are designed for trees/thin foliage, other shapes mixed; one dev reports popping at LOD3 impostor switch on an asteroid. MSFS tree-LOD forum thread surfaced, not read.
- NOT FOUND: any documentation of impostors for hero/mid-distance ships in Elite Dangerous, Star Citizen, EVE, Homeworld, No Man's Sky (Homeworld hit was a hyperspace-cut article, unrelated). KNOWLEDGE (unverified): none publish impostor details.
- Near-hero fidelity claims only: Epic iterative parallax "nearly identical" to source mesh; Risser true impostors (per-frame, arbitrary angle) as the non-baked alternative.

## 5. Unity built-in specifics
- Amplify Impostors: Built-in supported; paid (EUR 55.20 / ~$60); Standard Asset Store EULA; built-in bake needs Deferred-path shader or custom bake shader (so hand-written HLSL needs a deferred pass or Amplify custom bake shader).
- Usnul/IMP: CC0, 2017/2018-era Unity, reference only. SIsilicon Godot port: MIT. three.js port: Ctrlmonster (licence unchecked). SideFX Unity package (licence unchecked). Unity Industry Toolkit impostors: licence unstated.
