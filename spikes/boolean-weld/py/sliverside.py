"""Sliver breakdown by side (hull face vs cutter face) within the band, for saved Blender meshes."""
import sys, os, glob, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *
from weld import Hull, loops_of, densify, angles
from scipy.spatial import cKDTree
hull = Hull(sys.argv[1]); runs, wd = sys.argv[2], sys.argv[3]
for name in sys.argv[4:]:
    for tag in ('naive', 'weld-along', 'weld-across'):
        p = f'{wd}/boolmesh_{name}_{tag}.obj'
        if not os.path.exists(p): continue
        V, F = load_obj(p); T = triangulate(F)
        # provenance: faces adjacent to cutter in the saved run; recover by matching to the raw run's faces
        Vr, Fr = load_obj(f'{runs}/boolmesh_{name}.obj'); Tr = triangulate(Fr)
        pr = np.array([int(x) for x in open(f'{runs}/boolmesh_{name}.prov').read().split()])
        key = {tuple(sorted(t)): pr[i] for i, t in enumerate(Tr)}
        prov = np.array([key.get(tuple(sorted(t)), -1) for t in T])
        # faces changed by the weld: inherit by vertex majority of the raw run's faces
        unk = prov < 0
        vside = np.zeros(len(V)); cnt = np.zeros(len(V))
        for i, t in enumerate(Tr):
            for v in t: vside[v] += pr[i]; cnt[v] += 1
        vs = vside / np.maximum(cnt, 1)
        for i in np.where(unk)[0]: prov[i] = int(round(vs[T[i]].mean()))
        loops, _ = loops_of(T, prov); lv = sorted({v for L in loops for v in L})
        h = float(np.median(hull.vlen[hull.kd.query(V[lv])[1]])); kd = cKDTree(densify(V, loops))
        cen = V[T].mean(1); inb = kd.query(cen)[0] < 2 * h
        FN, FA = face_normals(V, T); lmax = np.linalg.norm(V[T] - V[np.roll(T, -1, 1)], axis=2).max(1)
        sl = ((lmax ** 2 / np.maximum(2 * FA, 1e-300) > 10) | (FA < 1e-4 * FA.mean())) & inb
        mins = {s: (min([min(angles(V[t])) for t in T[inb & (prov == s)]], default=None)) for s in (0, 1)}
        print(f'{name:18s} {tag:12s} slivers hull={int((sl & (prov==0)).sum())} cutter={int((sl & (prov==1)).sum())}  min-angle hull={mins[0]:.3g} cutter={mins[1]:.3g}')
