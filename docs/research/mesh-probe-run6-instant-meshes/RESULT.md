# Mesh probe run 6: Instant Meshes (Jakob et al. 2015, BSD-3) built and run headless on Dexter Quiet

Agent `probe-instant-meshes`, session `self-2026-10-10-ag2`, 2026-10-11. Scratch only; no repo edited. Root: this directory.

## Build recipe
- Source `C:\Tools\instant-meshes-src` at 7b3160864a2e1025af498c84cfed91cbfb613698 (with submodules). Output `C:\Tools\instant-meshes-build\Release\Instant Meshes.exe`.
- No option disables the GUI: nanogui/glfw/GL are linked into the one exe (batch mode is just `-o`, which never opens a window). Built whole.
- Toolchain: VS 2022 BuildTools (MSVC 14.44), CMake 4.3.2, `tools/build.sh`: `cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_POLICY_VERSION_MINIMUM=3.5`, `_CL_=-MP4` (note: `/MP4` gets path-mangled by git-bash), `cmake --build . --config Release -- -m:2`. It waits for other agents' blender/cargo/node first. The VS "18" toolset was not needed.
- **Source changes (one):** `ext/nanogui/ext/glfw/CMakeLists.txt` line 10, `cmake_policy(SET CMP0042 OLD)` to `NEW` (CMake 4 rejects OLD; the policy only affects macOS install names). Nothing in the C++ needed to change.

## Flags (`tools/runim.sh`)
`-d -r 4 -p 4 -c 40 -S 2 -f N` (deterministic, 4-RoSy/4-PoSy, crease 40 deg, 2 reprojection steps). Variants at -f 2000 (zero set): no crease, `-i` (intrinsic), `-D` (quad-dominant), `-S 8`, `-c 20`. `-b` is moot: the inputs are closed or nearly so. Inputs: `in/zeroset.obj` (run 4's `sdf_fit.stl`, welded: 49k v / 98.6k tris) and `in/tripo.obj` (run 1 `dexter_main.obj`, 4.8k v / 9.5k tris).
- Fast: 0.4-3.5 s per run on 1 job. Singularities in the orientation field: 304 (zero set), 483-700 (Tripo; its noisy surface makes more).
- **`-f N` is not the output face count.** The pure-quad output has about 4x N faces (N=40 gives 105-144, 100 gives 330-342, 400 gives 1.3-1.6k, 2000 gives 7.4-8k, 8000 gives 31k). Read the real count from the table.
- Guidance accepted: target size (`-f/-v/-s`), RoSy/PoSy, crease angle (hard feature edges found by dihedral threshold), boundary alignment, intrinsic/extrinsic, smoothing, dominance. **No input for an orientation/cross field, no per-region density, no feature curves.**

## Measurements (run 2/4 measure.py, score.py unchanged; raw = IM output, no subdivision/UV; L_ = cage refit to run 4's SDF, CC level 2, run 4's lower.py)
| mesh | faces (q/t/n) | poles/1000v | boundary / nonmanifold edges | shells | slivers <10deg | longest loop | closed loops>=20 | chamfer % | F@2% | sil-IoU |
|---|---|---|---|---|---|---|---|---|---|---|
| zeroset_f40 | 144 (144/0/0) | 161.1 | 8 / 8 | 3 | 0.0 | 20 | 0 | 0.743 | 0.924 | 0.828 |
| zeroset_f100 | 342 (342/0/0) | 114.6 | 8 / 8 | 5 | 0.0088 | 45 | 5 | 0.607 | 0.945 | 0.853 |
| zeroset_f400 | 1596 (1596/0/0) | 77.7 | 28 / 28 | 2 | 0.0003 | 96 | 0 | 0.477 | 0.959 | 0.904 |
| zeroset_f2000 | 8027 (8027/0/0) | 36.8 | 50 / 50 | 1 | 0.0001 | 284 | 0 | 0.498 | 0.954 | 0.900 |
| zeroset_f8000 | 31967 (31967/0/0) | 19.8 | 98 / 98 | 3 | 0.0001 | 386 | 3 | 0.505 | 0.953 | 0.899 |
| tripo_f40 | 105 (105/0/0) | 168.1 | 14 / 14 | 1 | 0.0 | 14 | 0 | 1.562 | 0.689 | 0.665 |
| tripo_f100 | 330 (330/0/0) | 151.1 | 0 / 0 | 1 | 0.0 | 42 | 0 | 0.619 | 0.953 | 0.859 |
| tripo_f400 | 1349 (1349/0/0) | 127.2 | 70 / 70 | 6 | 0.0019 | 38 | 0 | 0.199 | 0.994 | 0.949 |
| tripo_f2000 | 7430 (7430/0/0) | 77.3 | 240 / 240 | 10 | 0.0009 | 120 | 0 | 0.053 | 1.000 | 0.986 |
| tripo_f8000 | 30707 (30707/0/0) | 43.1 | 810 / 810 | 25 | 0.0004 | 314 | 4 | 0.017 | 1.000 | 0.994 |
| zeroset_f2000_nocrease | 7984 (7984/0/0) | 37.6 | 48 / 48 | 2 | 0.0006 | 210 | 3 | 0.492 | 0.956 | 0.905 |
| zeroset_f2000_intr | 7975 (7975/0/0) | 26.1 | 92 / 92 | 4 | 0.0 | 272 | 0 | 0.491 | 0.956 | 0.904 |
| zeroset_f2000_dom | 2017 (1888/90/39) | 78.8 | 35 / 35 | 1 | 0.0 | 86 | 0 | 0.489 | 0.956 | 0.901 |
| zeroset_f2000_S8 | 8022 (8022/0/0) | 36.3 | 54 / 54 | 2 | 0.0001 | 284 | 0 | 0.499 | 0.954 | 0.901 |
| zeroset_f2000_c20 | 7891 (7891/0/0) | 38.0 | 64 / 64 | 6 | 0.0003 | 244 | 1 | 0.498 | 0.954 | 0.902 |
| L_zeroset_f40 | 2980 (2699/146/135) | 118.9 | 49 / 50 | 1 | 0.2136 | 73 | 0 | 0.589 | 0.933 | 0.866 |
| L_zeroset_f100 | 6981 (6426/308/247) | 103.5 | 68 / 68 | 2 | 0.2163 | 101 closed | 9 | 0.527 | 0.947 | 0.881 |
| L_tripo_f40 | 2730 (2395/223/112) | 215.9 | 65 / 65 | 1 | 0.4027 | 64 | 0 | 0.690 | 0.916 | 0.854 |
| L_tripo_f100 | 6750 (6211/310/229) | 123.4 | 4 / 4 | 1 | 0.2336 | 153 | 0 | 0.508 | 0.950 | 0.904 |

Reference rows (from run 3/4/5 RESULTs): run 4 L: poles 140/1000v, 846 boundary edges, chamfer 0.531 / F@2% 0.950 / sil 0.875. run 3 v7 (designed cage): poles 47.1, 1 shell, longest loop 148 closed, 0.228 / 0.990 / 0.967. QuadriFlow (run 5), 1.8k-11.5k faces: poles 13-39, slivers <=0.3%, longest loop open, 0.494-0.501 / 0.954 / 0.90.

Cage refit (limit |f| and score before refit, then after; `out/chain1.log`, `chain2.log`):
| cage (IM faces) | before refit: chamfer / sil | after refit: chamfer / sil |
|---|---|---|
| zero set, 144 faces | 0.871 / 0.754 | 0.669 / 0.837 |
| zero set, 342 faces | 0.646 / 0.814 | 0.555 / 0.868 |
| Tripo, 105 faces | 1.806 / 0.604 | 0.970 / 0.770 |
| Tripo, 330 faces | 0.746 / 0.800 | 0.553 / 0.889 |
Lowered through run 4's stack (rows L_ above): the 342-face cage gives 0.527 / 0.947 / 0.881 but with 21 % sliver tris (bevel strips), 103 poles/1000v, 68 boundary edges and 160+ crumbs of UV islands; none reaches run 3 (0.228). The 1.5k-face (f400) refits were abandoned: `refit.py`'s dense Catmull-Clark operator ran over 30 min; I killed my PIDs.

## Reading
- Raw IM output is pure quads, almost sliver-free, loops long (284 edges at 8k faces), poles fall with density (37/1000v at 8k, 20 at 32k): same class as QuadriFlow, far better than run 4's numpy attempt. Open boundaries/non-manifold edges (8-98) come from the zero set's own thin-wing holes.
- Fidelity is the same wall as QuadriFlow: chamfer 0.48-0.50 on the zero set at every density from 1.6k to 32k faces, sil 0.90. The thin wing and the sharp rim are below its lattice; `-c`, `-i`, `-S 8` do not move it (0.49-0.50). The crease flag only changes the field (222 vs 304 singularities), not the score.
- Fed the Tripo scan it reproduces the scan (0.05 % at 7k faces), meaning it is just a retopo of whatever noise is in the input (10-25 shells, up to 810 open edges).
- A cage-like count (144-342 faces) is blocky: loops are not designed (longest 20-45 edges), poles are 115-170/1000v. Refit helps (0.87 to 0.67) but not to run 3's level.
- It does not replace run 3's designed cage. As a body retopo it is as good as QuadriFlow, and it is BSD-3 source we can own and patch (QuadriFlow in Blender is closed to us).

## Injecting an external cross field: feasible, modest
Source reading (`src/batch.cpp`, `field.cpp`, `hierarchy.cpp`): the batch path already has the hook. `align_to_boundaries` writes per-vertex constraints `mRes.CQ().col(i)` (direction), `CQw()[i]` (weight), `CO/COw` (position pin) and calls `mRes.propagateConstraints(rosy, posy)`; `Optimizer::optimizeOrientations` (field.cpp ~632-660) blends CQ by CQw. So run 4's exact-Hessian field goes in as: read a per-vertex tangent direction + weight file, set CQ/CQw (and optionally CO/COw on creases for position pinning), propagate, optimize. Alternatively set `mRes.Q(0)` directly and skip the orientation solve. Work: roughly 50-100 lines in batch.cpp plus a reader, around half a day to a day, no change to the solver. Gotchas: `subdivide()` may add vertices before the constraints (pre-subdivide the input so indices match, or evaluate the analytic field at `mRes.V()`), constraints must lie in the vertex tangent plane, and the weight scale is empirical. Whether it fixes the thin-wing fidelity wall is untested (the wall is lattice size vs. wing thickness, not orientation).

## Files
`sheet-main.png`, `sheet-closeup.png` (rows: Tripo target, SDF zero set, run 3 v7, run 4 L, QuadriFlow 6000, IM zero-set f40/f100/f400/f2000, IM Tripo f400, L_zeroset_f100, L_tripo_f100; columns as run 2). `out/*.obj` (IM outputs), `out/*.metrics.json`, `*.score.txt`, `out/table.md`, `tools/` (build.sh, runim.sh, chain.sh, refit.py, rawmeasure.py, table.py, stl2obj.py). Processes: all mine ended; operator GUI Blender PID 36324 untouched.
