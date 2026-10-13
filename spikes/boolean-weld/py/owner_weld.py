"""Owner weld: rulings weld-owner-local-corners-kept and brush-modes-add-subtract-split, target r4. Ownership is local
along the loop (curvature along the loop); the owner's vertices survive and the other surface's spare vertices near
that stretch merge onto them:
  - 'loop': a loop vertex made only by the yielding side's edges merges into the nearest owner-made loop vertex.
  - 'ring' (cutter owns): a hull vertex one ring off the loop merges onto that loop vertex.
Round 4 cut the 'snap' kind (loop vertex merged into a nearby hull vertex on hull-owned stretches) and its knobs
(SNAP, SNAPDIR, NOSNAP_FLAT): target r4's weld-path-fixed forbids snapping the loop on any stretch. Rounds 2 and 3 ran
with it; that code is at db2c162.
A split is welded jointly: every operation is checked on both pieces and applied only if both accept, so the two
pieces' loops stay identical. Guards (both pieces): no face flip, worst angle not driven below MIN_ANGLE, edge exists,
link condition. Corners (sharp cutter edge or hull crease on the loop) are never a merge source and never moved."""
import os, numpy as np
from collections import defaultdict
from scipy.spatial import cKDTree
from weld import analyse_loops, loops_of, angles

MIN_ANGLE = float(os.environ.get('MIN_ANGLE', '10'))
CORNER_DEG = 30.0


def sharp_cutter_edges(cut):
    from geo import edge_faces, face_normals
    FN, _ = face_normals(cut.V, cut.T); out = set()
    for e, fs in edge_faces(cut.T).items():
        if len(fs) == 2 and FN[fs[0]] @ FN[fs[1]] < np.cos(np.radians(CORNER_DEG)):
            out.add(e)
    return out


def corners_of(P, info, hull, cut, tol):
    sharp = sharp_cutter_edges(cut); out = []
    for v, inf in info.items():
        ce = cut.edge_of(P.V[v], tol)
        if (ce is not None and (min(ce), max(ce)) in sharp) or inf['crease']:
            out.append(P.V[v].copy())
    return out


class Piece:
    def __init__(s, V, T, prov):
        s.V = V.copy(); s.prov = list(prov); s.faces = [list(map(int, t)) for t in T]
        s.vf = defaultdict(list)
        for fi, t in enumerate(s.faces):
            for x in t:
                s.vf[x].append(fi)
        s.kd = cKDTree(V); s.alive = np.ones(len(V), bool); s.moved = {}

    def at(s, p, tol):
        m = s.moved.get(tuple(np.round(p, 9)))
        if m is not None and s.alive[m]:
            return m
        d, i = s.kd.query(p)
        if d < tol and np.linalg.norm(s.V[i] - p) > tol:
            return None  # that vertex has moved away
        return int(i) if d < tol and s.alive[i] else None

    def nbrs(s, v):
        return {x for f in s.vf[v] if s.faces[f] is not None for x in s.faces[f]} - {v}

    def _face_ok(s, f, v, newpos):
        P = s.V[s.faces[f]]; old = np.cross(P[1] - P[0], P[2] - P[0])
        Q = np.array([newpos if x == v else s.V[x] for x in s.faces[f]]); new = np.cross(Q[1] - Q[0], Q[2] - Q[0])
        if old @ new <= 0:
            return 'flip'
        na, oa = min(angles(Q)), min(angles(P))
        if na < MIN_ANGLE and na < oa:
            return 'angle'
        return None

    def check_collapse(s, v, w):
        fv = [f for f in s.vf[v] if s.faces[f] is not None]
        shared = [f for f in fv if w in s.faces[f]]
        if not shared:
            return 'not_edge'
        opp = {x for f in shared for x in s.faces[f]} - {v, w}
        if (s.nbrs(v) & s.nbrs(w)) != opp:
            return 'link'
        for f in fv:
            if f not in shared:
                r = s._face_ok(f, v, s.V[w])
                if r:
                    return r
        return None

    def apply_collapse(s, v, w):
        for f in s.vf[v]:
            if s.faces[f] is None:
                continue
            if w in s.faces[f]:
                s.faces[f] = None
            else:
                s.faces[f] = [w if x == v else x for x in s.faces[f]]; s.vf[w].append(f)
        s.vf[v] = []; s.alive[v] = False

    def check_move(s, v, p):
        for f in s.vf[v]:
            if s.faces[f] is not None:
                r = s._face_ok(f, v, p)
                if r:
                    return r
        return None

    def apply_move(s, v, p):
        s.V[v] = p; s.moved[tuple(np.round(p, 9))] = v

    def result(s):
        keep = [i for i, f in enumerate(s.faces) if f is not None]
        return s.V, np.array([s.faces[i] for i in keep]), np.array([s.prov[i] for i in keep])


def candidates(P, info, loops, hull, tol, scope_ring=True):
    """Operations as (dist, v_pos, w_pos, kind): v merges into w."""
    cand = []; loopset = set(info)
    for L in loops:
        n = len(L)
        for i, v in enumerate(L):
            inf = info[v]; own = inf['owner']; ychar, ochar = ('C', 'H') if own == 0 else ('H', 'C')
            if inf['origin'] == ychar:
                best = None
                for step in (1, -1):
                    for j in range(1, n):
                        u = L[(i + step * j) % n]
                        if ochar in info[u]['origin']:
                            d = np.linalg.norm(P.V[u] - P.V[v])
                            if best is None or d < best[0]:
                                best = (d, u)
                            break
                if best:
                    cand.append((best[0], P.V[v].copy(), P.V[best[1]].copy(), 'loop'))
            for x in P.nbrs(v):
                if x in loopset or any(P.prov[g] != 0 for g in P.vf[x] if P.faces[g] is not None):
                    continue  # only hull-side, non-loop vertices
                d = np.linalg.norm(P.V[x] - P.V[v])
                if own == 1 and scope_ring:
                    cand.append((d, P.V[x].copy(), P.V[v].copy(), 'ring'))
    return cand


def owner_weld(pieces, hull, cut, tol):
    """pieces: list of (V, T, prov); one for a cut-in, two for a split. Returns welded pieces, stats, done ops, info."""
    Ps = [Piece(*p) for p in pieces]
    infos = []
    cand = []; corners = []
    for P in Ps:
        loops, le, info = analyse_loops(P.V, np.array([f for f in P.faces]), np.array(P.prov), hull, cut, 'along', tol)
        infos.append((loops, info)); cand += candidates(P, info, loops, hull, tol)
        corners.extend(corners_of(P, info, hull, cut, tol))
    cand.sort(key=lambda z: z[0])
    stats = defaultdict(int); done = []; seen = set()
    for d, pv, pw, kind in cand:
        key = (tuple(np.round(pv, 9)), tuple(np.round(pw, 9)))
        if key in seen:
            continue
        seen.add(key); stats['cand_' + kind] += 1
        if any(np.linalg.norm(pv - q) < tol for q in corners):
            stats['protected_corner'] += 1; continue
        plan, reason = [], None
        for P in Ps:
            v = P.at(pv, tol); w = P.at(pw, tol)
            if v is None:
                if w is None:
                    continue
                if kind == 'loop':
                    reason = 'gone'; break  # the loop vertex is already gone in this piece
                continue
            if w is not None:
                r = P.check_collapse(v, w); plan.append((P, 'c', v, w))
            else:
                if kind == 'ring':
                    reason = 'target_gone'; break
                r = P.check_move(v, pw); plan.append((P, 'm', v, pw))
            if r:
                reason = r; break
        if reason or not plan:
            stats['refused_' + (reason or 'empty')] += 1; continue
        for P, op, v, w in plan:
            if op == 'c':
                P.apply_collapse(v, w)
            else:
                P.apply_move(v, w)
        stats['applied_' + kind] += 1; done.append((pv, pw))
    res = [P.result() for P in Ps]
    kept = 0
    for q in corners:
        kept += int(any(np.linalg.norm(Vr[np.unique(Tr)] - q, axis=1).min() < tol for Vr, Tr, _ in res))
    stats['corners'] = len(corners); stats['corners_kept_in_place'] = kept
    return res, dict(stats), done, infos
