"""Round 2 weld: ruling weld-owner-defines-silhouette. The surface whose own vertices shape the loop owns it
(measured as curvature along the loop); its vertices survive, the other surface's spare vertices near the loop
merge onto them:
  - 'loop': a loop vertex made only by the yielding side's edges merges into the nearest owner-made loop vertex.
  - 'ring' (cutter owns): a hull vertex one ring off the loop merges onto that loop vertex.
  - 'snap' (hull owns): a loop vertex the boolean inserted on a hull edge, within SNAP local edge lengths of an
    existing hull vertex, merges INTO that hull vertex (the hull vertex survives where it is).
A split is welded jointly: every operation is checked on both pieces and applied only if both accept, so the two
pieces' loops stay identical. In the piece that lacks the surviving hull vertex, the loop vertex moves to it.
Guards (both pieces): no face flip, worst angle not driven below MIN_ANGLE, edge exists, link condition."""
import os, numpy as np
from collections import defaultdict
from scipy.spatial import cKDTree
from weld import analyse_loops, loops_of, angles

MIN_ANGLE = float(os.environ.get('MIN_ANGLE', '10'))
SNAP = float(os.environ.get('SNAP', '0.25'))
# SNAPDIR=reverse: the hull vertex slides onto the loop vertex instead (the loop stays on the cutter; spike variant)
SNAPDIR = os.environ.get('SNAPDIR', 'loop-to-hull')


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
                elif own == 0 and inf['origin'] == 'H' and hull.kd.query(P.V[v])[0] > tol and hull.kd.query(P.V[x])[0] < tol:
                    if d < SNAP * hull.vlen[hull.kd.query(P.V[x])[1]]:
                        if SNAPDIR == 'reverse':
                            cand.append((d, P.V[x].copy(), P.V[v].copy(), 'snap'))
                        else:
                            cand.append((d, P.V[v].copy(), P.V[x].copy(), 'snap'))
    return cand


def owner_weld(pieces, hull, cut, tol):
    """pieces: list of (V, T, prov); one for a cut-in, two for a split. Returns welded pieces, stats, done ops, info."""
    Ps = [Piece(*p) for p in pieces]
    infos = []
    cand = []
    for P in Ps:
        loops, le, info = analyse_loops(P.V, np.array([f for f in P.faces]), np.array(P.prov), hull, cut, 'along', tol)
        infos.append((loops, info)); cand += candidates(P, info, loops, hull, tol)
    cand.sort(key=lambda z: z[0])
    stats = defaultdict(int); done = []; seen = set()
    for d, pv, pw, kind in cand:
        key = (tuple(np.round(pv, 9)), tuple(np.round(pw, 9)))
        if key in seen:
            continue
        seen.add(key); stats['cand_' + kind] += 1
        plan, reason = [], None
        for P in Ps:
            v = P.at(pv, tol); w = P.at(pw, tol)
            if v is None:
                if w is None:
                    continue
                if kind == 'loop' or (kind == 'snap' and SNAPDIR != 'reverse'):
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
    return [P.result() for P in Ps], dict(stats), done, infos
