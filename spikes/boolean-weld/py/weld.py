"""Weld pass for the boolean-weld spike: the operator rule, automated, plus the measures.

Rule (ruling boolean-cleanup-tighter-curve-wins, plan steps 1-5): along the intersection loop the surface with
the larger |normal curvature| owns the loop; the yielding surface's spare vertices collapse onto the owner's loop
vertices, each collapse guarded (no flip, worst angle not driven below 10 deg, link condition).
Curvature direction modes: 'across' (plan: u = n x t), 'along' (t projected into each surface), 'mean'.
Scope variants: 'literal' (loop vertices from the yielding side's edges AND the yielding side's one-ring),
'looponly' (loop vertices from the yielding side's edges only). Scratch code."""
import sys, os, numpy as np
from collections import defaultdict
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *

MIN_ANGLE = 10.0
SNAP = 0.25
BEVEL_W = 0.001


def seg_dist(x, a, b):
    ab = b - a
    t = np.clip((x - a) @ ab / max(ab @ ab, 1e-300), 0, 1)
    return np.linalg.norm(x - (a + t * ab))


def tri_dist(p, P):
    a, b, c = P
    ab, ac, ap = b - a, c - a, p - a
    n = np.cross(ab, ac); nn = n @ n
    if nn < 1e-300:
        return 1e9, (1 / 3, 1 / 3, 1 / 3)
    q = p - (ap @ n) / nn * n
    v0, v1, v2 = ab, ac, q - a
    d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
    den = d00 * d11 - d01 * d01
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den; u = 1 - v - w
    if min(u, v, w) >= -1e-9:
        return np.linalg.norm(p - q), (u, v, w)
    d = min(seg_dist(p, a, b), seg_dist(p, b, c), seg_dist(p, a, c))
    bw = np.clip([u, v, w], 0, None); bw = bw / bw.sum()
    return d, tuple(bw)


class Hull:
    def __init__(s, fx):
        V, F = load_obj(fx + '/hull_nobevel.obj'); s.V, s.T = V, triangulate(F)
        s.S = np.load(fx + '/../_curv.npy'); s.N = vertex_normals(s.V, s.T); s.FN, _ = face_normals(s.V, s.T)
        s.kd = cKDTree(V); s.adj = vertex_adj(s.T, len(V))
        s.vf = defaultdict(list)
        for fi, t in enumerate(s.T):
            for v in t:
                s.vf[int(v)].append(fi)
        E = np.loadtxt(fx + '/hull_creases.txt', dtype=int)
        s.crease = {(min(a, b), max(a, b)) for a, b in E}
        s.crease_v = set(np.unique(E).tolist())
        s.diag = np.linalg.norm(V.max(0) - V.min(0))
        el = defaultdict(list)
        for a, b in edge_faces(s.T):
            l = np.linalg.norm(V[a] - V[b]); el[a].append(l); el[b].append(l)
        s.vlen = np.array([np.mean(el[i]) for i in range(len(V))])

    def edge_of(s, x, tol):
        _, idx = s.kd.query(x, 6)
        best = None
        for a in idx:
            for b in s.adj[a]:
                d = seg_dist(x, s.V[a], s.V[b])
                if d < tol and (best is None or d < best[0]):
                    best = (d, (min(a, b), max(a, b)))
        return best[1] if best else None

    def frame(s, x):
        _, idx = s.kd.query(x, 4)
        bestf, bd, bw = None, 1e9, None
        for a in idx:
            for f in s.vf[int(a)]:
                d, w = tri_dist(x, s.V[s.T[f]])
                if d < bd:
                    bestf, bd, bw = f, d, w
        vs = s.T[bestf]
        Sx = sum(w * s.S[v] for w, v in zip(bw, vs))
        n = sum(w * s.N[v] for w, v in zip(bw, vs)); n = n / np.linalg.norm(n)
        return n, Sx, bestf


class Cutter:
    def __init__(s, c):
        s.c = c; s.kind = c['kind']
        Vc, Fc = load_obj(c['cutter']); s.V, s.T = Vc, triangulate(Fc); s.adj = vertex_adj(s.T, len(Vc))
        if s.kind == 'obox':
            s.p = np.array(c['p']); s.R = np.array(c['R']); s.lo = np.array(c['lo']); s.hi = np.array(c['hi'])
        if s.kind == 'cyl':
            s.p, s.r = np.array(c['p']), c['r']
            s.a = np.array(c['n']) / np.linalg.norm(c['n'])

    def edge_of(s, x, tol):
        best = None
        for a in range(len(s.V)):
            for b in s.adj[a]:
                if b < a:
                    continue
                d = seg_dist(x, s.V[a], s.V[b])
                if d < tol and (best is None or d < best[0]):
                    best = (d, (a, b))
        return best[1] if best else None

    def frame(s, x):
        if s.kind == 'cyl':
            d = x - s.p; er = d - (d @ s.a) * s.a; er = er / np.linalg.norm(er)
            et = np.cross(s.a, er)
            return er, np.outer(et, et) / s.r
        if s.kind == 'obox':
            xl = s.R.T @ (x - s.p); dd = np.concatenate([xl - s.lo, s.hi - xl]); i = int(np.argmin(np.abs(dd)))
            nl = np.zeros(3); nl[i % 3] = -1 if i < 3 else 1
            return s.R @ nl, np.zeros((3, 3))
        lo, hi = np.array(s.c['lo']), np.array(s.c['hi'])
        dd = np.concatenate([x - lo, hi - x]); i = int(np.argmin(np.abs(dd)))
        n = np.zeros(3); n[i % 3] = -1 if i < 3 else 1
        return n, np.zeros((3, 3))


def loops_of(T, prov):
    ef = edge_faces(T)
    le = [e for e, fs in ef.items() if len(fs) == 2 and prov[fs[0]] != prov[fs[1]]]
    g = defaultdict(list)
    for a, b in le:
        g[a].append(b); g[b].append(a)
    seen, loops = set(), []
    for s0 in g:
        if s0 in seen:
            continue
        L = [s0]; seen.add(s0); prev, cur = None, s0
        while True:
            nx = [x for x in g[cur] if x != prev and x not in seen]
            if not nx:
                break
            prev, cur = cur, nx[0]; L.append(cur); seen.add(cur)
        loops.append(L)
    return loops, le


def kvals(mode, n, S, t):
    if mode == 'mean':
        return float(np.trace(S) / 2)
    if mode == 'along':
        tt = t - (t @ n) * n; tt = tt / np.linalg.norm(tt)
        return float(tt @ S @ tt)
    u = np.cross(n, t); u = u / np.linalg.norm(u)
    return float(u @ S @ u)


def analyse_loops(V, T, prov, hull, cut, mode, tol):
    loops, le = loops_of(T, prov)
    info = {}
    for L in loops:
        n = len(L)
        for i, v in enumerate(L):
            x = V[v]
            t = V[L[(i + 1) % n]] - V[L[i - 1]]; t = t / np.linalg.norm(t)
            he = hull.edge_of(x, tol); ce = cut.edge_of(x, tol)
            nh, Sh, _ = hull.frame(x); nc, Sc = cut.frame(x)
            crease = he is not None and he in hull.crease
            kh = np.inf if crease else kvals(mode, nh, Sh, t)
            kc = kvals(mode, nc, Sc, t)
            origin = (('H' if he else '') + ('C' if ce else '')) or 'X'
            info[v] = dict(kh=kh, kc=kc, owner=0 if abs(kh) >= abs(kc) else 1, origin=origin, crease=crease)
    return loops, le, info


def angles(P):
    a, b, c = P; out = []
    for p, q, r in ((a, b, c), (b, c, a), (c, a, b)):
        u, w = q - p, r - p
        out.append(np.degrees(np.arccos(np.clip(u @ w / max(np.linalg.norm(u) * np.linalg.norm(w), 1e-300), -1, 1))))
    return out


def try_collapse(V, faces, vf, v, w, stats):
    """Merge vertex v into w (w keeps its position). Guards: edge exists, link condition, no flip, worst angle."""
    fv = [f for f in vf[v] if faces[f] is not None]
    fw = [f for f in vf[w] if faces[f] is not None]
    shared = [f for f in fv if w in faces[f]]
    if not shared:
        stats['refused_not_edge'] += 1; return False
    nv = {x for f in fv for x in faces[f]} - {v}
    nw = {x for f in fw for x in faces[f]} - {w}
    opp = {x for f in shared for x in faces[f]} - {v, w}
    if (nv & nw) != opp:
        stats['refused_link'] += 1; return False
    for f in fv:
        if f in shared:
            continue
        P = V[faces[f]]; old = np.cross(P[1] - P[0], P[2] - P[0])
        Q = np.array([V[w] if x == v else V[x] for x in faces[f]]); new = np.cross(Q[1] - Q[0], Q[2] - Q[0])
        if old @ new <= 0:
            stats['refused_flip'] += 1; return False
        na, oa = min(angles(Q)), min(angles(P))
        if na < MIN_ANGLE and na < oa:
            stats['refused_angle'] += 1; return False
    for f in shared:
        faces[f] = None
    for f in fv:
        if faces[f] is None:
            continue
        faces[f] = [w if x == v else x for x in faces[f]]; vf[w].append(f)
    vf[v] = []; stats['collapsed'] += 1
    return True


def weld(V, T, prov, hull, cut, mode, scope, tol, forced=None):
    """Returns new (T, prov), the collapses [(pos_v, pos_w)], stats, loop analysis. `forced` replays a collapse
    list by position (split: the second piece gets the first piece's collapses)."""
    loops, le, info = analyse_loops(V, T, prov, hull, cut, mode, tol)
    faces = [list(map(int, t)) for t in T]; vf = defaultdict(list)
    for fi, t in enumerate(faces):
        for x in t:
            vf[x].append(fi)
    stats = defaultdict(int); done = []
    if forced is not None:
        kd = cKDTree(V)
        for pv, pw in forced:
            dv, v = kd.query(pv); dw, w = kd.query(pw)
            if dv > tol or dw > tol:
                stats['replay_unmatched'] += 1; continue
            if try_collapse(V, faces, vf, int(v), int(w), stats):
                done.append((V[v].copy(), V[w].copy()))
    else:
        cand = []
        for L in loops:
            n = len(L)
            for i, v in enumerate(L):
                inf = info[v]; own = inf['owner']
                ychar = 'C' if own == 0 else 'H'; ochar = 'H' if own == 0 else 'C'
                if inf['origin'] == ychar:
                    best = None
                    for step in (1, -1):
                        for j in range(1, n):
                            u = L[(i + step * j) % n]
                            if ochar in info[u]['origin']:
                                d = np.linalg.norm(V[u] - V[v])
                                if best is None or d < best[0]:
                                    best = (d, u)
                                break
                    if best:
                        cand.append((best[0], v, best[1], 'loop'))
        if scope == 'literal':
            loopset = set(info)
            for v, inf in info.items():
                ys = 1 - inf['owner']
                for f in vf[v]:
                    if prov[f] != ys:
                        continue
                    for x in faces[f]:
                        if x in loopset or any(prov[g] != ys for g in vf[x]):
                            continue
                        cand.append((np.linalg.norm(V[x] - V[v]), x, v, 'ring'))
        if scope.endswith('snap'):
            # candidate change, not her rule: owner-side vertices off the loop but within SNAP x local edge length
            # of a loop vertex collapse onto it (removes the slivers a cut leaves next to an existing vertex)
            loopset = set(info)
            for v in info:
                for f in vf[v]:
                    for x in faces[f]:
                        if x in loopset: continue
                        d = np.linalg.norm(V[x] - V[v]); hl = hull.vlen[hull.kd.query(V[x])[1]]
                        if d < SNAP * hl: cand.append((d, x, v, 'snap'))
            # and loop edges shorter than the bevel width: merge the later loop vertex into the earlier one
            for L in loops:
                for i in range(len(L)):
                    a, b = L[i], L[(i + 1) % len(L)]; d = np.linalg.norm(V[a] - V[b])
                    if d < BEVEL_W: cand.append((d, b, a, 'shortloop'))
        cand.sort(key=lambda z: z[0])
        removed = set()
        for d, v, w, kind in cand:
            if v in removed or w in removed:
                stats['skipped_gone'] += 1; continue
            stats['cand_' + kind] += 1
            if try_collapse(V, faces, vf, v, w, stats):
                removed.add(v); done.append((V[v].copy(), V[w].copy()))
    keep = [i for i, f in enumerate(faces) if f is not None]
    T2 = np.array([faces[i] for i in keep]); P2 = np.array([prov[i] for i in keep])
    return T2, P2, done, dict(stats), (loops, le, info)


# ---------------------------------------------------------------- measures
def densify(V, loops, per=16):
    pts = []
    for L in loops:
        for i in range(len(L)):
            a, b = V[L[i]], V[L[(i + 1) % len(L)]]
            pts += [a + (b - a) * s for s in np.linspace(0, 1, per, endpoint=False)]
    return np.array(pts)


FLIPS = []

def measures(V, T, prov, hull, cut, ref_pts, removed=(), tol=1e-7):
    loops, le = loops_of(T, prov)
    lv = sorted({v for L in loops for v in L})
    h = float(np.median(hull.vlen[hull.kd.query(V[lv])[1]]))
    band = 2 * h
    dense = densify(V, loops); kd = cKDTree(dense)
    T = np.asarray(T); cen = V[T].mean(1); inb = kd.query(cen)[0] < band
    FN, FA = face_normals(V, T); meanA = FA.mean()
    lmax = np.linalg.norm(V[T] - V[np.roll(T, -1, 1)], axis=2).max(1)
    AR = lmax ** 2 / np.maximum(2 * FA, 1e-300)
    sliver = ((AR > 10) | (FA < 1e-4 * meanA)) & inb
    ang = np.array([min(angles(V[t])) for t in T[inb]])
    flips = 0
    for fi in np.where(inb)[0]:
        if prov[fi] == 0:
            n, _, hf = hull.frame(cen[fi])
            if FN[fi] @ n < 0:
                flips += 1; near_crease = min(np.linalg.norm(hull.V[list(hull.crease_v)] - cen[fi], axis=1)) / h
                FLIPS.append(dict(c=cen[fi].tolist(), dot=float(FN[fi] @ n), dot_face=float(FN[fi] @ hull.FN[hf]), crease_dist_h=float(near_crease)))
    dref = cKDTree(ref_pts)
    d_tr = dref.query(dense)[0]; d_rt = kd.query(ref_pts)[0]
    moved_out = [r for r in removed if kd.query(r[0])[0] >= band and hull.kd.query(r[0])[0] < tol]
    return dict(h_local=h, tris_band=int(inb.sum()), tris_total=int(len(T)), slivers_band=int(sliver.sum()),
                min_angle_band=float(ang.min()), p5_angle_band=float(np.percentile(ang, 5)), flipped_hull_band=int(flips),
                loops=len(loops), loop_verts=len(lv),
                dev_mean_pct=float(d_tr.mean() / hull.diag * 100), dev_max_pct=float(d_tr.max() / hull.diag * 100),
                dev_mean_h=float(d_tr.mean() / h), dev_max_h=float(d_tr.max() / h),
                ref_to_loop_max_pct=float(d_rt.max() / hull.diag * 100),
                outside_band_moved=len(moved_out),
                outside_band_max_disp=float(max([np.linalg.norm(a - b) for a, b in moved_out], default=0.0)))
