"""Round 3 (Self's calls): a flat split keeps its seam exactly on the cutter plane. Hull vertices survive; hull-side
slivers along the seam get edge flips only (loop and crease edges constrained); each cap polygon is re-triangulated
with a constrained Delaunay (loop as boundary), plain ('p') or with interior-only Steiner refinement ('pq<deg>Y').
Usage: round3.py <fixtures> <cases.json> <runs> <out-dir>. Scratch. Uses the `triangle` package (Shewchuk's Triangle)."""
import sys, os, json, numpy as np
from collections import defaultdict
from scipy.spatial import cKDTree
import triangle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *
from weld import Hull, Cutter, loops_of, densify, angles

fx, casesf, runs, outd = sys.argv[1:5]
os.makedirs(outd, exist_ok=True)
hull = Hull(fx); TOL = 1e-6 * hull.diag
cases = {c['name']: c for c in json.load(open(casesf))}
FLIP_DIHEDRAL_COS = np.cos(np.radians(20))


def load_run(name):
    V, F = load_obj(f'{runs}/boolmesh_{name}.obj'); T = triangulate(F)
    return V, T, np.array([int(x) for x in open(f'{runs}/boolmesh_{name}.prov').read().split()])


def tri_min_angle(V, t):
    return min(angles(V[list(t)]))


def flip_hull(V, T, prov, loopedges, band_faces):
    """Greedy Delaunay-style flips on hull-provenance faces near the loop. Constrained: loop edges, hull crease edges.
    A flip must raise the pair's worst angle, keep both normals within 20 deg of the old ones, and not duplicate an edge."""
    T = [list(t) for t in T]; nflip = 0
    crease_pos = hull.crease
    for _ in range(20):
        ef = defaultdict(list)
        for fi, t in enumerate(T):
            for k in range(3):
                a, b = t[k], t[(k + 1) % 3]; ef[(min(a, b), max(a, b))].append(fi)
        changed = False
        for e, fs in ef.items():
            if len(fs) != 2 or e in loopedges:
                continue
            f1, f2 = fs
            if prov[f1] or prov[f2] or not (f1 in band_faces or f2 in band_faces):
                continue
            he = hull.edge_of(V[e[0]], TOL), hull.edge_of(V[e[1]], TOL)
            if any(h is not None and h in crease_pos for h in he) and he[0] == he[1]:
                continue
            a, b = e; c = [x for x in T[f1] if x not in e][0]; d = [x for x in T[f2] if x not in e][0]
            if (min(c, d), max(c, d)) in ef:
                continue
            old = min(tri_min_angle(V, T[f1]), tri_min_angle(V, T[f2]))
            # keep orientation: T[f1] has a->b in some order; build new faces with the same winding
            t1 = T[f1]; i = t1.index(c); n1 = [t1[i], t1[(i + 1) % 3], t1[(i + 2) % 3]]  # c, p, q
            p, q = n1[1], n1[2]
            new1, new2 = [c, p, d], [c, d, q]
            new = min(tri_min_angle(V, new1), tri_min_angle(V, new2))
            if new <= old + 1e-9:
                continue
            on = [np.cross(V[t[1]] - V[t[0]], V[t[2]] - V[t[0]]) for t in (T[f1], T[f2])]
            nn = [np.cross(V[t[1]] - V[t[0]], V[t[2]] - V[t[0]]) for t in (new1, new2)]
            on = [x / np.linalg.norm(x) for x in on]; nn = [x / max(np.linalg.norm(x), 1e-300) for x in nn]
            if min(o @ n for o in on for n in nn) < FLIP_DIHEDRAL_COS:
                continue
            T[f1], T[f2] = new1, new2; nflip += 1; changed = True
            break  # edge map is stale after a flip
        if not changed:
            break
    return np.array(T), nflip


def flip_hull_all(V, T, prov, loopedges, band_faces, cap=4000):
    total = 0
    for _ in range(cap // 20):
        T, n = flip_hull(V, T, prov, loopedges, band_faces); total += n
        if n == 0:
            break
    return T, total


def cdt_caps(V, T, prov, cut, opts):
    """Replace every cap (cutter-provenance) face set with a CDT of its boundary loop in the cutter plane."""
    loops, _ = loops_of(T, prov)
    capF = np.where(prov == 1)[0]
    old_n = face_normals(V, T[capF])[0].mean(0)
    keep = [i for i in range(len(T)) if prov[i] == 0]
    newV = [V]; newT = []; nv = len(V)
    for L in loops:
        P = V[L]; n, _ = cut.frame(P.mean(0))
        e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < .9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
        o = P.mean(0); P2 = np.stack([(P - o) @ e1, (P - o) @ e2], 1)
        seg = np.array([[i, (i + 1) % len(L)] for i in range(len(L))])
        r = triangle.triangulate({'vertices': P2, 'segments': seg}, opts)
        rv, rt = r['vertices'], r['triangles']
        assert np.allclose(rv[:len(L)], P2), 'Triangle moved a boundary vertex'
        idx = list(L) + list(range(nv, nv + len(rv) - len(L)))
        if len(rv) > len(L):
            newV.append(o + rv[len(L):, :1] * e1 + rv[len(L):, 1:2] * e2); nv += len(rv) - len(L)
        for t in rt:
            tt = [idx[k] for k in t]; newT.append(tt)
    V2 = np.vstack(newV); NT = np.array(newT)
    nn = face_normals(V2, NT)[0].mean(0)
    if nn @ old_n < 0:
        NT = NT[:, ::-1]
    T2 = np.vstack([T[keep], NT]); P2 = np.concatenate([prov[keep], np.ones(len(NT), int)])
    return V2, T2, P2


def side_measures(V, T, prov, ref_loop_pts, plane=None):
    loops, le = loops_of(T, prov); lv = sorted({v for L in loops for v in L})
    h = float(np.median(hull.vlen[hull.kd.query(V[lv])[1]]))
    kd = cKDTree(densify(V, loops)); cen = V[T].mean(1); inb = kd.query(cen)[0] < 2 * h
    FN, FA = face_normals(V, T); lmax = np.linalg.norm(V[T] - V[np.roll(T, -1, 1)], axis=2).max(1)
    sl = (lmax ** 2 / np.maximum(2 * FA, 1e-300) > 10) | (FA < 1e-4 * FA[prov == 0].mean())
    ang = np.array([tri_min_angle(V, t) for t in T])
    hs, cs = inb & (prov == 0), prov == 1
    flips = 0
    for fi in np.where(hs)[0]:
        n, _, _ = hull.frame(cen[fi]); flips += int(FN[fi] @ n < 0)
    out = dict(h=h, hull_band_tris=int(hs.sum()), hull_slivers=int((sl & hs).sum()), hull_min_angle=float(ang[hs].min()),
               hull_p5=float(np.percentile(ang[hs], 5)), cap_tris=int(cs.sum()), cap_slivers=int((sl & cs).sum()),
               cap_min_angle=float(ang[cs].min()) if cs.any() else None, flipped_hull=flips,
               loop_verts=len(lv), loop_to_naive_max=float(cKDTree(ref_loop_pts).query(V[lv])[0].max()))
    if plane is not None:
        n, d = plane; out['seam_off_plane_max'] = float(np.abs(V[lv] @ n - d).max())
    ls = [np.linalg.norm(V[a] - V[b]) for a, b in edge_faces(T) if a in set(lv) or b in set(lv)]
    out['loop_edges_under_bevel'] = int(sum(l < 0.001 for l in ls))
    return out


def save(stem, V, T, prov):
    save_obj(f'{outd}/{stem}.obj', V, T)
    _, le = loops_of(T, prov)
    with open(f'{outd}/{stem}.loop', 'w') as f:
        for a, b in le:
            f.write(f'{a} {b} 0\n')


def boundary_loops(T):
    nxt = {}
    ef = edge_faces(T)
    for t in T:
        for k in range(3):
            a, b = int(t[k]), int(t[(k + 1) % 3])
            if len(ef[(min(a, b), max(a, b))]) == 1:
                nxt[a] = b
    loops, seen = [], set()
    for s0 in list(nxt):
        if s0 in seen:
            continue
        L = [s0]; seen.add(s0); x = nxt[s0]
        while x != s0 and x not in seen:
            L.append(x); seen.add(x); x = nxt[x]
        loops.append(L)
    return loops


def short_loop_merge(pieces, bevel_w=0.001):
    """Split only: merge consecutive seam vertices closer than the bevel width, both pieces jointly. Both endpoints lie
    on the cutter plane, so the seam stays on it; only boolean-inserted seam vertices are merge sources (hull vertices
    survive). Caps are dropped first (rebuilt afterwards by the CDT), so the guard sees hull faces only."""
    import owner_weld as OW
    Ps = [OW.Piece(V, T[p == 0], np.zeros(int((p == 0).sum()), int)) for V, T, p in pieces]
    L = boundary_loops(np.array([f for f in Ps[0].faces]))
    st = defaultdict(int); n = 0
    for lp in L:
        for i in range(len(lp)):
            a, b = lp[i], lp[(i + 1) % len(lp)]
            pa, pb = Ps[0].V[a], Ps[0].V[b]
            if not (Ps[0].alive[a] and Ps[0].alive[b]) or np.linalg.norm(pa - pb) >= bevel_w:
                continue
            src, dst = (pb, pa) if hull.kd.query(pb)[0] > TOL else (pa, pb)
            if hull.kd.query(src)[0] < TOL:
                st['refused_both_hull_vertices'] += 1; continue
            plan = []
            for P in Ps:
                v, w = P.at(src, TOL), P.at(dst, TOL)
                if v is None or w is None:
                    plan = None; st['refused_missing'] += 1; break
                r = P.check_collapse(v, w)
                if r:
                    plan = None; st['refused_' + r] += 1; break
                plan.append((P, v, w))
            if plan:
                for P, v, w in plan:
                    P.apply_collapse(v, w)
                n += 1
    out = []
    for P in Ps:
        V, T, _ = P.result(); out.append((V, T))
    return out, n, dict(st)


def cdt_boundary(V, T, cut, opts, flip_orient):
    newV, newT, nv = [V], [], len(V)
    for L in boundary_loops(T):
        P = V[L]; n, _ = cut.frame(P.mean(0))
        e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < .9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
        o = P.mean(0); P2 = np.stack([(P - o) @ e1, (P - o) @ e2], 1)
        r = triangle.triangulate({'vertices': P2, 'segments': np.array([[i, (i + 1) % len(L)] for i in range(len(L))])}, opts)
        idx = list(L) + list(range(nv, nv + len(r['vertices']) - len(L)))
        if len(r['vertices']) > len(L):
            newV.append(o + r['vertices'][len(L):, :1] * e1 + r['vertices'][len(L):, 1:2] * e2); nv += len(r['vertices']) - len(L)
        # boundary runs a->b in the hull faces, so the cap must run b->a: orient each cap triangle against the loop
        tri = [[idx[k] for k in t] for t in r['triangles']]
        newT += tri
    V2 = np.vstack(newV); NT = np.array(newT)
    # orientation: the cap must use each boundary edge in the opposite direction to the hull face that owns it
    hd = {(int(t[k]), int(t[(k + 1) % 3])) for t in T for k in range(3)}
    bad = sum(1 for t in NT for k in range(3) if (int(t[k]), int(t[(k + 1) % 3])) in hd)
    if bad:
        NT = NT[:, ::-1]
    return V2, np.vstack([T, NT]), np.concatenate([np.zeros(len(T), int), np.ones(len(NT), int)])


rows = []
for base in [b for b in ('split_fwd', 'probe_crease') if os.environ.get('SKIP_SPLITS') != '1']:
    c = cases[base + '_sub']; cut = Cutter(c)
    lo, hi = np.array(c['lo']), np.array(c['hi'])
    pieces = {'sub': load_run(base + '_sub'), 'int': load_run(base + '_int')}
    V0, T0, p0 = pieces['sub']; L0, _ = loops_of(T0, p0); refl = V0[sorted({v for L in L0 for v in L})]
    n, _ = cut.frame(refl.mean(0)); plane = (n, float(refl.mean(0) @ n))
    out = {}
    for variant, opts in ((('naive', None), ('flip+cdt', 'p'), ('flip+cdt-q', 'pq20Y')) if os.environ.get('ONLY_SHORT') != '1' else (('naive', None),)):
        for pk, (V, T, p) in pieces.items():
            if variant != 'naive':
                loops, le = loops_of(T, p); lset = {(min(a, b), max(a, b)) for a, b in le}
                kd = cKDTree(densify(V, loops)); h = float(np.median(hull.vlen))
                band = set(np.where(kd.query(V[T].mean(1))[0] < 2 * 0.0256)[0].tolist())
                T1, nf = flip_hull_all(V, T, p, lset, band)
                V2, T2, P2 = cdt_caps(V, T1, p, cut, opts)
            else:
                V2, T2, P2, nf = V, T, p, 0
            m = side_measures(V2, T2, P2, refl, plane)
            out[(variant, pk)] = (V2, T2, P2)
            rows.append(dict(case=f'{base}_{pk}', variant=variant, flips_applied=nf, **m))
            save(f'{base}_{pk}_{variant}', V2, T2, P2)
        A, B = out[(variant, 'sub')], out[(variant, 'int')]
        la = A[0][sorted({v for L in loops_of(A[1], A[2])[0] for v in L})]; lb = B[0][sorted({v for L in loops_of(B[1], B[2])[0] for v in L})]
        rows.append(dict(case=base, variant=f'{variant} seam crack', crack=float(max(cKDTree(lb).query(la)[0].max(), cKDTree(la).query(lb)[0].max()))))
    merged, nm, stm = short_loop_merge([pieces['sub'], pieces['int']])
    naive_dense = cKDTree(densify(V0, L0, 64)); res = {}
    for pk, (Vm, Tm) in zip(('sub', 'int'), merged):
        p0 = np.zeros(len(Tm), int); L = boundary_loops(Tm)
        lset = {(min(a, b), max(a, b)) for lp in L for a, b in zip(lp, lp[1:] + lp[:1])}
        kd = cKDTree(densify(Vm, L)); band = set(np.where(kd.query(Vm[Tm].mean(1))[0] < 2 * 0.0256)[0].tolist())
        T1, nf = flip_hull_all(Vm, Tm, p0, lset, band)
        V2, T2, P2 = cdt_boundary(Vm, T1, cut, 'pq20Y', None)
        m = side_measures(V2, T2, P2, refl, plane)
        chord = float(naive_dense.query(densify(V2, loops_of(T2, P2)[0], 16))[0].max())
        rows.append(dict(case=f'{base}_{pk}', variant='short+flip+cdt-q', flips_applied=nf, merges=nm, merge_stats=stm,
                         seam_chord_dev=chord, seam_chord_dev_pct=chord / hull.diag * 100, **m))
        save(f'{base}_{pk}_short+flip+cdt-q', V2, T2, P2); res[pk] = (V2, T2, P2)
    A, B = res['sub'], res['int']
    la = A[0][sorted({v for L in loops_of(A[1], A[2])[0] for v in L})]; lb = B[0][sorted({v for L in loops_of(B[1], B[2])[0] for v in L})]
    rows.append(dict(case=base, variant='short+flip+cdt-q seam crack', crack=float(max(cKDTree(lb).query(la)[0].max(), cKDTree(la).query(lb)[0].max()))))
    print('done', base, nm, stm, flush=True)

# Box cut-ins into the curved hull: the flat faces own nothing (the hull owns every stretch, corners kept), so the
# hull-side repair is the same edge flips; the pocket walls and floor are the cutter's own faces, not a cap.
for base in [b for b in ('probe_box_flank', 'probe_box_ridge') if b in cases]:
    c = cases[base]; cut = Cutter(c); V, T, p = load_run(base)
    L0, le = loops_of(T, p); refl = V[sorted({v for L in L0 for v in L})]
    lset = {(min(a, b), max(a, b)) for a, b in le}
    kd = cKDTree(densify(V, L0)); band = set(np.where(kd.query(V[T].mean(1))[0] < 2 * 0.0256)[0].tolist())
    for variant in ('naive', 'flip'):
        T2, nf = (T, 0) if variant == 'naive' else flip_hull_all(V, T, p, lset, band)
        m = side_measures(V, T2, p, refl)
        rows.append(dict(case=base, variant=variant, flips_applied=nf, **m)); save(f'{base}_{variant}', V, T2, p)
    print('done', base, flush=True)

json.dump(rows, open(f'{outd}/measures3.json', 'w'), indent=1, default=float)
cols = ['case', 'variant', 'merges', 'seam_chord_dev_pct', 'flips_applied', 'hull_band_tris', 'hull_slivers', 'hull_min_angle', 'hull_p5', 'cap_tris', 'cap_slivers',
        'cap_min_angle', 'flipped_hull', 'seam_off_plane_max', 'loop_to_naive_max', 'loop_edges_under_bevel', 'crack']
f = lambda v: '' if v is None else (f'{v:.3g}' if isinstance(v, float) else str(v))
with open(f'{outd}/table3.md', 'w') as o:
    o.write('| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n')
    for r in rows:
        o.write('| ' + ' | '.join(f(r.get(k)) for k in cols) + ' |\n')
print(open(f'{outd}/table3.md').read())
