"""Round 2 runner (ruling weld-owner-defines-silhouette). Usage: run2.py <fixtures> <cases.json> <runs> <out-dir> <tag>
MIN_ANGLE and SNAP come from the environment (owner_weld.py)."""
import sys, os, json, numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *
from weld import Hull, Cutter, measures, loops_of, densify, analyse_loops
import owner_weld as OW

fx, casesf, runs, outd, tag = sys.argv[1:6]
os.makedirs(outd, exist_ok=True)
hull = Hull(fx); TOL = 1e-6 * hull.diag
cases = {c['name']: c for c in json.load(open(casesf))}
rows = []


def load_run(name):
    V, F = load_obj(f'{runs}/boolmesh_{name}.obj'); T = triangulate(F)
    return V, T, np.array([int(x) for x in open(f'{runs}/boolmesh_{name}.prov').read().split()])


def refpts(c, V, T, prov):
    if c['kind'] == 'cyl':
        Vr, Tr, pr = load_run(c['name'] + '_REF'); return densify(Vr, loops_of(Tr, pr)[0], 4)
    return densify(V, loops_of(T, prov)[0], 64)


def short_edges(V, T, prov, w=0.001):
    loops, _ = loops_of(T, prov); lv = {v for L in loops for v in L}
    ls = [np.linalg.norm(V[a] - V[b]) for a, b in edge_faces(T) if a in lv or b in lv]
    return float(min(ls)), int(sum(l < w for l in ls))


def save(stem, V, T, prov, info=None):
    save_obj(f'{outd}/{stem}.obj', V, T)
    _, le = loops_of(T, prov)
    with open(f'{outd}/{stem}.loop', 'w') as f:
        for a, b in le:
            f.write(f"{a} {b} {info[a]['owner'] if info and a in info else -1}\n")


def row(name, variant, V, T, prov, c, ref, extra):
    m = measures(V, T, prov, hull, Cutter(c), ref)
    se = short_edges(V, T, prov)
    rows.append(dict(case=name, variant=variant, shortest_loop_edge=se[0], loop_edges_under_bevel=se[1], **m, **extra))


for name, c in cases.items():
    if c['kind'] == 'box' and c['op'] == 'int':
        continue
    cut = Cutter(c)
    if c['kind'] == 'box':
        other = name[:-4] + '_int'
        A, B = load_run(name), load_run(other)
        pieces = [A, B]
    else:
        A = load_run(name); pieces = [A]
    welded, st, done, infos = OW.owner_weld(pieces, hull, cut, TOL)
    for k, ((V, T, p), (Vw, Tw, pw)) in enumerate(zip(pieces, welded)):
        pname = name if k == 0 else other
        ref = refpts(c, V, T, p)
        row(pname, 'naive', V, T, p, c, ref, {})
        loops, info = infos[k]
        own = dict(hull_owned=sum(i['owner'] == 0 for i in info.values()), cutter_owned=sum(i['owner'] == 1 for i in info.values()))
        # how far each merged-away hull vertex lies from the welded surface (hull silhouette change), in local h
        from weld import tri_dist
        kdw = cKDTree(Vw[np.unique(Tw)]); uv = np.unique(Tw); sdev = 0.0
        for pv_, pw_ in done:
            if hull.kd.query(pv_)[0] < TOL:
                _, j = kdw.query(pw_); j = uv[j]
                fs = [t for t in Tw if j in t]
                dd = min(tri_dist(pv_, Vw[t])[0] for t in fs) if fs else 0.0
                sdev = max(sdev, dd / hull.vlen[hull.kd.query(pv_)[1]])
        row(pname, f'owner-weld[{tag}]', Vw, Tw, pw, c, ref, dict(applied=len(done), stats=st if k == 0 else {}, hull_vertex_surface_dev_h=sdev, **own))
        save(f'{pname}_naive', V, T, p, info)
        _, _, info_w = analyse_loops(Vw, Tw, pw, hull, cut, 'along', TOL)
        save(f'{pname}_owner-{tag}', Vw, Tw, pw, info_w)
    if len(welded) == 2:
        for lab, (P1, P2) in (('naive', pieces), ('welded', welded)):
            la = densify(P1[0], loops_of(P1[1], P1[2])[0], 1); lb = densify(P2[0], loops_of(P2[1], P2[2])[0], 1)
            gap = max(cKDTree(lb).query(la)[0].max(), cKDTree(la).query(lb)[0].max())
            rows.append(dict(case=name, variant=f'seam-gap-{lab}[{tag}]', split_loop_gap=float(gap), loop_samples=(len(la), len(lb))))
    print('done', name, st, flush=True)

json.dump(rows, open(f'{outd}/measures2-{tag}.json', 'w'), indent=1, default=float)
cols = ['case', 'variant', 'applied', 'tris_band', 'slivers_band', 'min_angle_band', 'p5_angle_band', 'flipped_hull_band', 'dev_max_pct',
        'dev_max_h', 'outside_band_moved', 'shortest_loop_edge', 'loop_edges_under_bevel', 'hull_owned', 'cutter_owned', 'split_loop_gap', 'hull_vertex_surface_dev_h']
f = lambda v: '' if v is None else (f'{v:.3g}' if isinstance(v, float) else str(v))
with open(f'{outd}/table2-{tag}.md', 'w') as o:
    o.write('| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n')
    for r in rows:
        o.write('| ' + ' | '.join(f(r.get(k)) for k in cols) + ' |\n')
