"""Run the weld variants and measures over every case and kernel. Usage: run.py <fixtures> <cases.json> <runs-dir> <out-dir>"""
import sys, os, json, numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *
from weld import *

fx, casesf, runs, outd = sys.argv[1:5]
kernels = sys.argv[5].split(',') if len(sys.argv) > 5 else ['boolmesh', 'manifold']
os.makedirs(outd, exist_ok=True)
hull = Hull(fx)
TOL = 1e-7 * hull.diag * 10
cases = {c['name']: c for c in json.load(open(casesf))}
VARIANTS = [('across', 'literal'), ('across', 'looponly'), ('along', 'literal'), ('along', 'looponly'), ('along', 'looponly-snap'), ('across', 'looponly-snap')]
rows, owners = [], {}


def load_run(kernel, name):
    V, F = load_obj(f'{runs}/{kernel}_{name}.obj'); T = triangulate(F)
    prov = np.array([int(x) for x in open(f'{runs}/{kernel}_{name}.prov').read().split()])
    return V, T, prov


def ref_points(c, kernel, V, T, prov):
    if c['kind'] == 'cyl':
        Vr, Tr, pr = load_run('boolmesh', c['name'] + '_REF')
        return densify(Vr, loops_of(Tr, pr)[0], 4)
    return densify(V, loops_of(T, prov)[0], 64)


def owner_summary(info, loops):
    sw = 0
    for L in loops:
        o = [info[v]['owner'] for v in L]; sw += sum(o[i] != o[i - 1] for i in range(len(o)))
    ks = np.array([[info[v]['kh'], info[v]['kc']] for L in loops for v in L])
    fin = np.isfinite(ks[:, 0])
    return dict(hull_owned=int(sum(info[v]['owner'] == 0 for v in info)), cutter_owned=int(sum(info[v]['owner'] == 1 for v in info)),
                switches=int(sw), crease_loop_verts=int(sum(info[v]['crease'] for v in info)),
                kh_abs_median=float(np.median(np.abs(ks[fin, 0]))) if fin.any() else None,
                kc_abs_median=float(np.median(np.abs(ks[:, 1]))),
                near_tie=int(np.sum(np.abs(np.abs(ks[fin, 0]) - np.abs(ks[fin, 1])) < 0.1 * np.maximum(np.abs(ks[fin, 0]), np.abs(ks[fin, 1])) + 1e-9)),
                origins={o: int(sum(info[v]['origin'] == o for v in info)) for o in ('H', 'C', 'HC', 'X')})


def save_for_blender(path, V, T, prov, info=None):
    save_obj(path + '.obj', V[np.unique(T)] if False else V, T)
    loops, le = loops_of(T, prov)
    with open(path + '.loop', 'w') as f:
        for a, b in le:
            oa = info[a]['owner'] if info and a in info else -1
            f.write(f'{a} {b} {oa}\n')


for name, c in cases.items():
    for kernel in kernels:
        if not os.path.exists(f'{runs}/{kernel}_{name}.obj'):
            continue
        V, T, prov = load_run(kernel, name)
        cut = Cutter(c)
        refp = ref_points(c, kernel, V, T, prov)
        m = measures(V, T, prov, hull, cut, refp)
        rows.append(dict(case=name, kernel=kernel, variant='naive', **m))
        for mode in ('across', 'along', 'mean'):
            loops, le, info = analyse_loops(V, T, prov, hull, cut, mode, TOL)
            owners[f'{name}|{kernel}|{mode}'] = owner_summary(info, loops)
            if kernel == 'boolmesh' and mode == 'across':
                save_for_blender(f'{outd}/{kernel}_{name}_naive', V, T, prov, info)
        for mode, scope in VARIANTS:
            T2, P2, done, st, (loops, le, info) = weld(V, T, prov, hull, cut, mode, scope, TOL)
            crease_removed = sum(1 for a, b in done if hull.edge_of(a, TOL) in hull.crease or (hull.kd.query(a)[0] < TOL and int(hull.kd.query(a)[1]) in hull.crease_v))
            m2 = measures(V, T2, P2, hull, cut, refp, removed=done)
            row = dict(case=name, kernel=kernel, variant=f'{mode}-{scope}', collapses=len(done), crease_verts_removed=crease_removed,
                       stats=st, **m2)
            if c['kind'] == 'box' and c['op'] == 'sub':
                # split: replay the same collapses on the other piece and compare the two loops
                other = name[:-4] + '_int'
                Vo, To, po = load_run(kernel, other)
                To2, Po2, done_o, st_o, _ = weld(Vo, To, po, hull, cut, mode, scope, TOL, forced=done)
                la = densify(V, loops_of(T2, P2)[0], 1); lb = densify(Vo, loops_of(To2, Po2)[0], 1)
                gap = max(cKDTree(lb).query(la)[0].max(), cKDTree(la).query(lb)[0].max())
                row.update(split_replay=st_o, split_loop_gap=float(gap), split_loop_verts=(len(la), len(lb)))
                if mode == 'along' and scope in ('looponly', 'looponly-snap') and kernel == 'boolmesh':
                    save_for_blender(f'{outd}/{kernel}_{other}_weld-{mode}' + ('-snap' if 'snap' in scope else ''), Vo, To2, Po2)
            rows.append(row)
            if kernel == 'boolmesh' and scope.startswith('looponly'):
                save_for_blender(f'{outd}/{kernel}_{name}_weld-{mode}' + ('-snap' if 'snap' in scope else ''), V, T2, P2, info)
        if c['kind'] == 'box' and c['op'] == 'sub':
            Vo, To, po = load_run(kernel, name[:-4] + '_int')
            la = densify(V, loops_of(T, prov)[0], 1); lb = densify(Vo, loops_of(To, po)[0], 1)
            rows.append(dict(case=name, kernel=kernel, variant='naive-split-gap',
                             split_loop_gap=float(max(cKDTree(lb).query(la)[0].max(), cKDTree(la).query(lb)[0].max())), split_loop_verts=(len(la), len(lb))))
        print('done', name, kernel, flush=True)

import weld as W
json.dump(dict(rows=rows, owners=owners, flips=W.FLIPS), open(f'{outd}/measures.json', 'w'), indent=1, default=float)
