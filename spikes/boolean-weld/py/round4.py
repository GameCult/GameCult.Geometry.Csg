"""Round 4 (target r4, Self's calls a-f). Replaces round3.py and its Triangle dependency.
  a. slide: a hull vertex closer to the loop than the bevel width slides inside its own surface onto the loop, and
     the loop vertices its own edges made merge into it (see slide()). Never a crease or corner vertex; joint on both
     pieces of a split.
  b. no snapping of the loop onto owner vertices on any stretch (owner_weld.py has no 'snap' kind any more).
  c. constrained Delaunay by spade (MIT OR Apache-2.0) through the spike driver's `cdt` subcommand.
  d. planar brush facets trimmed by the hull are re-triangulated in their own plane; facet boundary edges (loop and
     brush edges) are constraints and are never split.
  e. add mode (union) cases.
  f. UV0 carry-through: every output face is matched to the operand face it is a fragment of and takes its UVs by
     barycentric interpolation; checks fragment coverage, UV flips and island change under the weld.
Usage: round4.py <fixtures> <cases.json> <runs> <out-dir> <driver-exe> <hull_uv.obj>. Scratch."""
import sys, os, json, copy, subprocess, tempfile, numpy as np
os.environ.setdefault('MIN_ANGLE', '5')
from collections import defaultdict
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *
from weld import Hull, Cutter, loops_of, densify, angles, tri_dist
import owner_weld as OW

fx, casesf, runs, outd, EXE, hull_uv_path = sys.argv[1:7]
os.makedirs(outd, exist_ok=True)
hull = Hull(fx); TOL = 1e-6 * hull.diag; BW = 0.001
cases = {c['name']: c for c in json.load(open(casesf))}
FLIP_COS = np.cos(np.radians(20))
ONLY = os.environ.get('CASES', '').split(',') if os.environ.get('CASES') else None


def tri_min_angle(V, t):
    return min(angles(V[list(t)]))


def load_run(name):
    V, F = load_obj(f'{runs}/boolmesh_{name}.obj'); T = triangulate(F)
    return V, T, np.array([int(x) for x in open(f'{runs}/boolmesh_{name}.prov').read().split()])


# ------------------------------------------------------------------ UV sources
def load_obj_uv(path):
    V, VT, F, FT = [], [], [], []
    for line in open(path):
        s = line.split()
        if not s: continue
        if s[0] == 'v': V.append([float(x) for x in s[1:4]])
        elif s[0] == 'vt': VT.append([float(x) for x in s[1:3]])
        elif s[0] == 'f':
            F.append([int(x.split('/')[0]) - 1 for x in s[1:]]); FT.append([int(x.split('/')[1]) - 1 for x in s[1:]])
    return np.array(V), np.array(VT), F, FT


HV, HVT, HF, HFT = load_obj_uv(hull_uv_path)
assert len(HV) == len(hull.V) and len(HF) == len(load_obj(fx + '/hull_nobevel.obj')[1])
UV_FIXTURE_DIFF = float(np.abs(HV - hull.V).max())
assert UV_FIXTURE_DIFF < 1e-6, UV_FIXTURE_DIFF
HUV = np.array([[HVT[ft[0]], HVT[ft[i]], HVT[ft[i + 1]]] for ft in HFT for i in range(1, len(ft) - 1)])
assert len(HUV) == len(hull.T)


def uv_islands(T, UV):
    """Triangles connected across an edge whose two endpoints carry the same UVs on both sides."""
    key = {}
    par = list(range(len(T)))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for fi, t in enumerate(T):
        for k in range(3):
            a, b = int(t[k]), int(t[(k + 1) % 3]); ua, ub = tuple(np.round(UV[fi, k], 7)), tuple(np.round(UV[fi, (k + 1) % 3], 7))
            e = (a, b, ua, ub) if a < b else (b, a, ub, ua)
            if e in key: par[f(fi)] = f(key[e])
            else: key[e] = fi
    return np.array([f(i) for i in range(len(T))])


def uv_area(UV):
    return 0.5 * ((UV[:, 1, 0] - UV[:, 0, 0]) * (UV[:, 2, 1] - UV[:, 0, 1]) - (UV[:, 2, 0] - UV[:, 0, 0]) * (UV[:, 1, 1] - UV[:, 0, 1]))


HFN, HFA = face_normals(hull.V, hull.T)
H_ISL = uv_islands(hull.T, HUV)
# UV0 seams of the hull: edges whose two triangles give an endpoint different UVs. A loop vertex on one is protected like
# a corner (never merged or moved), and a hull vertex on one never slides, so no weld step drags UVs across a seam.
_uvat = defaultdict(set)
for _fi, _t in enumerate(hull.T):
    for _k in range(3): _uvat[(int(_t[_k]), _fi)] = tuple(np.round(HUV[_fi, _k], 7))
UV_SEAM = set()
for (_a, _b), _fs in edge_faces(hull.T).items():
    if len(_fs) == 2 and (_uvat[(_a, _fs[0])] != _uvat[(_a, _fs[1])] or _uvat[(_b, _fs[0])] != _uvat[(_b, _fs[1])]): UV_SEAM.add((_a, _b))
UV_SEAM_V = {v for e in UV_SEAM for v in e}
PROTECT_UV_SEAMS = os.environ.get('PROTECT_UV_SEAMS', '1') == '1'


def uv_seam_points(V, verts):
    """Positions of the given vertices that lie on a hull UV0 seam edge (or are a seam vertex)."""
    out = []
    for v in verts:
        he = hull.edge_of(V[v], TOL); hi = hull_index(V[v])
        if (he is not None and he in UV_SEAM) or (hi is not None and hi in UV_SEAM_V): out.append(V[v].copy())
    return out
RHO = float(np.median(np.sqrt(np.abs(uv_area(HUV)) / np.maximum(HFA, 1e-300))))  # UV units per world unit


def cutter_uv(cut):
    """A stand-in brush UV chart at the hull's texel density, placed at u >= 3 so a face's side is readable from its UVs.
    Planar facets: projection on the facet's own axes, one tile per facet. Cylinder side: unrolled (r * theta, height)."""
    V, T = cut.V, cut.T; FN, _ = face_normals(V, T); UV = np.zeros((len(T), 3, 2))
    groups = facet_groups(V, T); gi = {g: i for i, g in enumerate(sorted(set(groups)))}
    for fi, t in enumerate(T):
        P = V[t]; n = FN[fi]
        if cut.kind == 'cyl' and abs(n @ cut.a) < 0.5:
            d = P - cut.p; h = d @ cut.a; e1 = np.cross(cut.a, [1, 0, 0] if abs(cut.a[0]) < .9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(cut.a, e1)
            th = np.arctan2(d @ e2, d @ e1); th = np.where(th - th[0] > np.pi, th - 2 * np.pi, np.where(th - th[0] < -np.pi, th + 2 * np.pi, th))
            UV[fi] = np.stack([3 + RHO * cut.r * (th + np.pi), 0.5 + RHO * h], 1)
        else:
            e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < .9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
            o = np.array([4 + 0.6 * (gi[groups[fi]] % 4), 0.6 * (gi[groups[fi]] // 4)])
            UV[fi] = o + RHO * np.stack([P @ e1, P @ e2], 1) - RHO * np.array([V @ e1, V @ e2]).min(1)
    return UV


def facet_groups(V, T):
    """Planar facets of a brush mesh: edge-adjacent triangles with the same plane."""
    FN, _ = face_normals(V, T); ef = edge_faces(T); par = list(range(len(T)))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for e, fs in ef.items():
        if len(fs) == 2 and FN[fs[0]] @ FN[fs[1]] > 1 - 1e-9 and abs((V[T[fs[1]]].mean(0) - V[T[fs[0]]].mean(0)) @ FN[fs[0]]) < 1e-9:
            par[f(fs[0])] = f(fs[1])
    return [f(i) for i in range(len(T))]


class Source:
    """An operand: its triangles, their UVs and the polygon (operand face) each triangle belongs to."""
    def __init__(s, V, T, UV, poly):
        s.V, s.T, s.UV, s.poly = V, np.asarray(T), UV, np.asarray(poly); s.kd = cKDTree(V); s.vf = defaultdict(list)
        s.ptris = defaultdict(list)
        for fi, pl in enumerate(s.poly): s.ptris[int(pl)].append(fi)
        for fi, t in enumerate(s.T):
            for v in t: s.vf[int(v)].append(fi)
        s.key = {tuple(sorted(map(int, t))): fi for fi, t in enumerate(s.T)}

    def near_faces(s, pts, k=6):
        out = set()
        for p in pts:
            for a in s.kd.query(p, k)[1]: out.update(s.vf[int(a)])
        return out

    def bary(s, f, p):
        a, b, c = s.V[s.T[f]]; v0, v1, v2 = b - a, c - a, p - a
        d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1; den = d00 * d11 - d01 * d01
        v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
        return np.array([1 - v - w, v, w])


def assign_uv(V, T, prov, srcs):
    """Per output triangle: the source (operand) triangle that contains all three corners, and UVs by interpolation in
    it. A triangle no single source face contains (a weld changed it) takes each corner's UV from a source face that
    contains that corner, preferring the triangle's majority source face's UV island."""
    UV = np.zeros((len(T), 3, 2)); frag = np.zeros(len(T), bool); src = np.full(len(T), -1); far = np.zeros(len(T))
    for fi, t in enumerate(T):
        S = srcs[int(prov[fi])]; P = V[t]
        d0, i0 = S.kd.query(P)
        if d0.max() < 1e-12:
            sf = S.key.get(tuple(sorted(map(int, i0))))
            if sf is not None:
                o = [list(S.T[sf]).index(int(x)) for x in i0]; UV[fi] = S.UV[sf][o]; frag[fi] = True; src[fi] = sf; continue
        best, bd = None, 1e9
        for f in S.near_faces(P):
            d = max(tri_dist(p, S.V[S.T[f]])[0] for p in P)
            if d < bd: best, bd = f, d
        src[fi] = best; far[fi] = bd
        if bd < TOL:
            frag[fi] = True; UV[fi] = np.array([S.bary(best, p) @ S.UV[best] for p in P]); continue
        # a fragment of the operand polygon (a hull quad, a planar brush facet) that spans two of its triangles
        cen = P.mean(0); cf = min(S.near_faces([cen]), key=lambda f: tri_dist(cen, S.V[S.T[f]])[0])
        pt = S.ptris[int(S.poly[cf])]; per = [min(pt, key=lambda f: tri_dist(p, S.V[S.T[f]])[0]) for p in P]
        dd = max(tri_dist(p, S.V[S.T[f]])[0] for p, f in zip(P, per))
        if dd < TOL:
            frag[fi] = True; src[fi] = cf; far[fi] = dd; UV[fi] = np.array([S.bary(f, p) @ S.UV[f] for p, f in zip(P, per)]); continue
        isl = S.isl[best] if hasattr(S, 'isl') else None
        for k, p in enumerate(P):
            cands = sorted(((tri_dist(p, S.V[S.T[f]])[0], (isl is not None and S.isl[f] != isl), f) for f in S.near_faces([p], 4)), key=lambda z: (z[0] > TOL, z[1], z[0]))
            f = cands[0][2]; UV[fi, k] = S.bary(f, p) @ S.UV[f]
    return UV, frag, src, far


def jac_sigma(P, Q):
    """Singular values of the map from a 3D triangle to its UV triangle, in units of the hull's median density."""
    e1 = P[1] - P[0]; e2 = P[2] - P[0]; n = np.cross(e1, e2); a = np.linalg.norm(e1)
    if a < 1e-300 or np.linalg.norm(n) < 1e-300: return 0.0, 0.0
    x = e1 / a; y = np.cross(n / np.linalg.norm(n), x)
    A = np.array([[e1 @ x, e2 @ x], [e1 @ y, e2 @ y]]); B = np.stack([Q[1] - Q[0], Q[2] - Q[0]], 1)
    try: J = B @ np.linalg.inv(A)
    except np.linalg.LinAlgError: return 0.0, 0.0
    s = np.linalg.svd(J, compute_uv=False) / RHO
    return float(s.min()), float(s.max())


def uv_report(V, T, prov, UV, frag, src, srcs):
    out = dict(faces=len(T), fragments=int(frag.sum()), not_fragments=int((~frag).sum()))
    sgn = np.sign(uv_area(UV)); ssgn = np.array([np.sign(uv_area(srcs[int(p)].UV[[s]])[0]) for p, s in zip(prov, src)])
    fl = sgn != ssgn; out['uv_flipped_hull'] = int((fl & (prov == 0)).sum()); out['uv_flipped_brush'] = int((fl & (prov == 1)).sum())
    out['not_fragments_hull'] = int((~frag & (prov == 0)).sum()); out['not_fragments_brush'] = int((~frag & (prov == 1)).sum())
    h = prov == 0; isl = uv_islands(T[h], UV[h])
    out['hull_islands'] = len(set(isl)); out['hull_uv_area'] = float(np.abs(uv_area(UV[h])).sum())
    out['hull_src_islands'] = len(set(H_ISL[src[h]]))
    nf = np.where(~frag)[0]
    if len(nf):
        sg = np.array([jac_sigma(V[T[i]], UV[i]) for i in nf]); r = sg[:, 0] / np.maximum(sg[:, 1], 1e-300)
        out['moved_face_sigma_min'] = float(sg[:, 0].min()); out['moved_face_sigma_max'] = float(sg[:, 1].max())
        out['moved_face_aniso_min'] = float(r.min())
    return out


# ------------------------------------------------------------------ constrained Delaunay (spade, via the driver)
CDT_CALLS = defaultdict(int)


def spade_cdt(P2, segs, ang=20.0, max_add=5000):
    with tempfile.TemporaryDirectory() as d:
        i, o = os.path.join(d, 'in.txt'), os.path.join(d, 'out.txt')
        with open(i, 'w') as f:
            f.write(f'{len(P2)} {len(segs)} {ang} {max_add}\n')
            for p in P2: f.write(f'{p[0]:.17e} {p[1]:.17e}\n')
            for a, b in segs: f.write(f'{a} {b}\n')
        subprocess.run([EXE, 'cdt', i, o], check=True, capture_output=True)
        L = open(o).read().split('\n'); nv = int(L[0].split()[1])
        pts = np.array([[float(x) for x in l.split()] for l in L[1:1 + nv]]); nt = int(L[1 + nv].split()[1])
        tri = np.array([[int(x) for x in l.split()] for l in L[2 + nv:2 + nv + nt]]); res = L[2 + nv + nt]
    CDT_CALLS['calls'] += 1; CDT_CALLS['complete' if 'complete=true' in res else 'incomplete'] += 1
    CDT_CALLS['steiner'] += nv - len(P2)
    assert np.array_equal(pts[:len(P2)], np.asarray(P2)), 'spade moved an input vertex'
    return pts, tri


def plane_frame(n):
    e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < .9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); return e1, np.cross(n, e1)


def cdt_region(V, faces, n, constrained, splits=None):
    """Re-triangulate a planar face set within its plane. Constraints: its boundary edges plus `constrained` interior
    edges. Returns new vertex positions (appended after len(V)) and triangles, oriented like the old faces."""
    ef = defaultdict(int)
    for t in faces:
        for k in range(3): a, b = int(t[k]), int(t[(k + 1) % 3]); ef[(min(a, b), max(a, b))] += 1
    cons = []
    for e, c in ef.items():
        if c == 1 or e in constrained:
            ch = [e[0]] + list((splits or {}).get(e, [])) + [e[1]]; cons += list(zip(ch, ch[1:]))
    vs = sorted({int(x) for t in faces for x in t} | {int(x) for e in cons for x in e}); li = {v: i for i, v in enumerate(vs)}
    e1, e2 = plane_frame(n); o = V[vs].mean(0); P2 = np.stack([(V[vs] - o) @ e1, (V[vs] - o) @ e2], 1)
    pts, tri = spade_cdt(P2, [(li[a], li[b]) for a, b in cons])
    newV = o + pts[len(vs):, :1] * e1 + pts[len(vs):, 1:2] * e2
    idx = vs + list(range(len(V), len(V) + len(newV)))
    NT = np.array([[idx[k] for k in t] for t in tri])
    VV = np.vstack([V, newV])
    old = face_normals(V, np.asarray(faces))[0].sum(0)
    if face_normals(VV, NT)[0].sum(0) @ old < 0: NT = NT[:, ::-1]
    got = {(min(a, b), max(a, b)) for t in NT for a, b in zip(t, np.roll(t, -1))}
    missing = sum(1 for a, b in cons if (min(a, b), max(a, b)) not in got)
    return newV, NT, missing, len(cons)


# ------------------------------------------------------------------ hull-side repairs
def flip_hull_all(V, T, prov, loopedges, band_faces, cap=4000):
    """Greedy flips on hull faces near the loop (round 3). Constrained: loop edges, hull crease edges and (round 4) UV0
    seams: both faces must lie in the same source UV island. A flip must raise the pair's worst angle and keep both
    normals within 20 deg."""
    isl = {f: H_ISL[hull.frame(V[T[f]].mean(0))[2]] for f in band_faces if not prov[f]}
    T = [list(map(int, t)) for t in T]; nflip = 0
    for _ in range(cap):
        ef = defaultdict(list)
        for fi, t in enumerate(T):
            for k in range(3): a, b = t[k], t[(k + 1) % 3]; ef[(min(a, b), max(a, b))].append(fi)
        changed = False
        for e, fs in ef.items():
            if len(fs) != 2 or e in loopedges: continue
            f1, f2 = fs
            if prov[f1] or prov[f2] or not (f1 in band_faces and f2 in band_faces) or isl[f1] != isl[f2]: continue
            he = hull.edge_of(V[e[0]], TOL), hull.edge_of(V[e[1]], TOL)
            if any(h is not None and h in hull.crease for h in he) and he[0] == he[1]: continue
            c = [x for x in T[f1] if x not in e][0]; d = [x for x in T[f2] if x not in e][0]
            if (min(c, d), max(c, d)) in ef: continue
            old = min(tri_min_angle(V, T[f1]), tri_min_angle(V, T[f2]))
            t1 = T[f1]; i = t1.index(c); p, q = t1[(i + 1) % 3], t1[(i + 2) % 3]; new1, new2 = [c, p, d], [c, d, q]
            if min(tri_min_angle(V, new1), tri_min_angle(V, new2)) <= old + 1e-9: continue
            on = [np.cross(V[t[1]] - V[t[0]], V[t[2]] - V[t[0]]) for t in (T[f1], T[f2])]
            nn = [np.cross(V[t[1]] - V[t[0]], V[t[2]] - V[t[0]]) for t in (new1, new2)]
            on = [x / np.linalg.norm(x) for x in on]; nn = [x / max(np.linalg.norm(x), 1e-300) for x in nn]
            if min(o @ n for o in on for n in nn) < FLIP_COS: continue
            T[f1], T[f2] = new1, new2; nflip += 1; changed = True; break
        if not changed: break
    return np.array(T), nflip


def boundary_loops(T):
    nxt = {}; ef = edge_faces(T)
    for t in T:
        for k in range(3):
            a, b = int(t[k]), int(t[(k + 1) % 3])
            if len(ef[(min(a, b), max(a, b))]) == 1: nxt[a] = b
    loops, seen = [], set()
    for s0 in list(nxt):
        if s0 in seen: continue
        L = [s0]; seen.add(s0); x = nxt[s0]
        while x != s0 and x not in seen: L.append(x); seen.add(x); x = nxt[x]
        loops.append(L)
    return loops


def loop_vertices(P):
    """Loop vertices of a piece: between hull and cutter faces, or the open boundary of a cap-dropped split piece."""
    alive = [i for i, f in enumerate(P.faces) if f is not None]
    T = np.array([P.faces[i] for i in alive]); pr = np.array([P.prov[i] for i in alive])
    if (pr == 1).any():
        L, _ = loops_of(T, pr)
    else:
        L = boundary_loops(T)
    return {v for l in L for v in l}


def hull_index(p):
    d, i = hull.kd.query(p); return int(i) if d < TOL else None


def short_loop_merge(Ps, protected=()):
    """Split only (round 3): consecutive seam vertices closer than the bevel width merge, both pieces jointly; only
    boolean-inserted seam vertices are merge sources. Round 4 guards it like the slide (compound(): local worst angle)."""
    L = boundary_loops(np.array([f for f in Ps[0].faces])); st = defaultdict(int); n = 0
    for lp in L:
        for i in range(len(lp)):
            a, b = lp[i], lp[(i + 1) % len(lp)]
            pa, pb = Ps[0].V[a], Ps[0].V[b]
            if not (Ps[0].alive[a] and Ps[0].alive[b]) or np.linalg.norm(pa - pb) >= BW: continue
            src, dst = (pb, pa) if hull_index(pb) is None else (pa, pb)
            if hull_index(src) is not None: st['refused_both_hull_vertices'] += 1; continue
            if any(np.linalg.norm(src - q) < TOL for q in protected): st['protected'] += 1; continue
            trial = []
            for P in Ps:
                v, w = P.at(src, TOL), P.at(dst, TOL)
                if v is None or w is None: trial = None; st['refused_missing'] += 1; break
                Q = copy.deepcopy(P); r = compound(Q, [('c', v, w)])
                if r: trial = None; st['refused_' + r] += 1; break
                trial.append(Q)
            if trial:
                for i, Q in enumerate(trial): Ps[i] = Q
                n += 1
    st['applied'] = n
    return dict(st)


def compound(Q, ops):
    """Apply a compound weld operation to piece Q and guard its end state: each collapse must be an edge and pass the
    link condition; then no face it touched may invert, and the worst angle over the faces it touched (deleted ones
    included) may not end below the floor if it got worse (target r4: no step drops the band's worst angle below the floor)."""
    before, touched = {}, set()
    for op, v, w in ops:
        if op == 'c':
            r = Q.check_collapse(v, w)
            if r in ('not_edge', 'link'): return r
            for f in Q.vf[v] + Q.vf[w]:
                if Q.faces[f] is not None and f not in before: before[f] = Q.V[Q.faces[f]].copy()
            Q.apply_collapse(v, w); touched |= set(Q.vf[w])
        else:
            for f in Q.vf[v]:
                if Q.faces[f] is not None and f not in before: before[f] = Q.V[Q.faces[f]].copy()
            Q.apply_move(v, w); touched |= set(Q.vf[v])
    new_min = 180.0
    for f in touched:
        if Q.faces[f] is None or f not in before: continue
        P, N = before[f], Q.V[Q.faces[f]]
        if np.cross(P[1] - P[0], P[2] - P[0]) @ np.cross(N[1] - N[0], N[2] - N[0]) <= 0: return 'flip'
        new_min = min(new_min, min(angles(N)))
    old_min = min(min(angles(P)) for P in before.values())
    if new_min < OW.MIN_ANGLE and new_min < old_min: return 'angle'
    return None


def slide(Ps, corners, joint_absent=True):
    """Call (a), joint over the pieces. A hull vertex H (not a crease vertex, not a corner, not on the loop) whose own
    edges cross the loop at loop vertices C(H) (consecutive along the loop), and whose nearest point M on the loop
    polyline between them is closer than the bevel width, slides inside its own surface to M; the loop vertices C(H)
    merge into it. M lies on the intersection, so the loop stays on it (a flat seam stays on the plane). In a split the
    piece without H gets the same loop: its first C(H) vertex moves to M and the others merge into it. Every operation
    must pass every piece's guards, or none is applied. Ps is edited in place (pieces are replaced by their copies)."""
    import copy
    st = defaultdict(int); moved = []
    P0 = Ps[0]; alive = [f for f in P0.faces if f is not None]
    pr0 = np.array([P0.prov[i] for i, f in enumerate(P0.faces) if f is not None])
    loops = loops_of(np.array(alive), pr0)[0] if (pr0 == 1).any() else boundary_loops(np.array(alive))
    cand = []
    for L in loops:
        n = len(L); pos = {v: i for i, v in enumerate(L)}
        cross = defaultdict(list)
        for v in L:
            he = hull.edge_of(P0.V[v], TOL)
            if he is not None and hull.kd.query(P0.V[v])[0] > TOL:
                for h in he: cross[int(h)].append(v)
        for h, C in cross.items():
            if h in hull.crease_v or (PROTECT_UV_SEAMS and h in UV_SEAM_V) or any(np.linalg.norm(hull.V[h] - q) < TOL for q in corners): continue
            idx = sorted(pos[v] for v in C)
            # consecutive along the loop (allow wrap-around)
            span = None
            for s0 in range(len(idx)):
                seq = [(idx[(s0 + k) % len(idx)]) for k in range(len(idx))]
                if all((seq[k + 1] - seq[k]) % n == 1 for k in range(len(seq) - 1)): span = seq; break
            if span is None: st['skip_not_consecutive'] += 1; continue
            Cs = [L[i] for i in span]
            if any(any(np.linalg.norm(P0.V[c] - q) < TOL for q in corners) for c in Cs): st['skip_corner_on_loop'] += 1; continue
            pts = [P0.V[c] for c in Cs]; best = (np.linalg.norm(hull.V[h] - pts[0]), pts[0])
            for a, b in zip(pts, pts[1:]):
                ab = b - a; t = np.clip((hull.V[h] - a) @ ab / max(ab @ ab, 1e-300), 0, 1); m = a + t * ab
                d = np.linalg.norm(hull.V[h] - m)
                if d < best[0]: best = (d, m)
            if best[0] < BW: cand.append((best[0], h, [P0.V[c].copy() for c in Cs], best[1].copy()))
    cand.sort(key=lambda z: z[0]); used = set()
    for d, h, Cpos, M in cand:
        keys = {tuple(np.round(c, 9)) for c in Cpos}
        if keys & used: st['skip_overlap'] += 1; continue
        trial, reason = [], None
        npres = 0
        for P in Ps:
            Q = copy.deepcopy(P); cs = [Q.at(c, TOL) for c in Cpos]
            if any(c is None for c in cs): reason = 'loop_vertex_gone'; break
            hv = Q.at(hull.V[h], TOL)
            if hv is not None:
                npres += 1; r = compound(Q, [('c', c, hv) for c in cs] + [('m', hv, M)])
            else:
                if not joint_absent: trial.append(Q); continue
                r = compound(Q, [('c', c, cs[0]) for c in cs[1:]] + [('m', cs[0], M)])
            if r: reason = r; break
            trial.append(Q)
        if reason or npres == 0: st['refused_' + (reason or 'h_absent')] += 1; continue
        for i, Q in enumerate(trial): Ps[i] = Q
        used |= keys; st['applied'] += 1; st['loop_vertices_merged'] += len(Cpos); moved.append(d)
    st['candidates'] = len(cand); st['max_move'] = max(moved, default=0.0); st['max_move_over_bw'] = st['max_move'] / BW
    return dict(st)


def band_of(V, T, loops, h=0.0256):
    kd = cKDTree(densify(V, loops)); return set(np.where(kd.query(V[T].mean(1))[0] < 2 * h)[0].tolist())


# ------------------------------------------------------------------ measures
def measure(V, T, prov, ref_pts, plane=None):
    loops, le = loops_of(T, prov); lv = sorted({v for L in loops for v in L}); lset = set(lv)
    h = float(np.median(hull.vlen[hull.kd.query(V[lv])[1]]))
    kd = cKDTree(densify(V, loops)); cen = V[T].mean(1); inb = kd.query(cen)[0] < 2 * h
    FN, FA = face_normals(V, T); lmax = np.linalg.norm(V[T] - V[np.roll(T, -1, 1)], axis=2).max(1)
    sl = (lmax ** 2 / np.maximum(2 * FA, 1e-300) > 10) | (FA < 1e-4 * FA[prov == 0].mean())
    ang = np.array([tri_min_angle(V, t) for t in T])
    out = dict(loop_verts=len(lv))
    for nm, m in (('hull', inb & (prov == 0)), ('brush', inb & (prov == 1))):
        out[f'{nm}_tris'] = int(m.sum()); out[f'{nm}_slivers'] = int((sl & m).sum())
        out[f'{nm}_worst'] = float(ang[m].min()) if m.any() else None; out[f'{nm}_p5'] = float(np.percentile(ang[m], 5)) if m.any() else None
    out['hull_flipped'] = int(sum(FN[fi] @ hull.frame(cen[fi])[0] < 0 for fi in np.where(inb & (prov == 0))[0]))
    out['dev_max_pct'] = float(cKDTree(ref_pts).query(densify(V, loops, 16))[0].max() / hull.diag * 100)
    if plane is not None: out['seam_off_plane'] = float(np.abs(V[lv] @ plane[0] - plane[1]).max())
    ls = [np.linalg.norm(V[a] - V[b]) for a, b in edge_faces(T) if a in lset or b in lset]
    out['loop_edges_under_bw'] = int(sum(l < BW for l in ls)); out['shortest_loop_edge'] = float(min(ls))
    return out


def save(stem, V, T, prov, UV, info=None):
    with open(f'{outd}/{stem}.obj', 'w') as f:
        for v in V: f.write(f'v {v[0]:.12f} {v[1]:.12f} {v[2]:.12f}\n')
        for uv in UV.reshape(-1, 2): f.write(f'vt {uv[0]:.9f} {uv[1]:.9f}\n')
        for i, t in enumerate(T): f.write('f ' + ' '.join(f'{t[k] + 1}/{3 * i + k + 1}' for k in range(3)) + '\n')
    _, le = loops_of(T, prov)
    with open(f'{outd}/{stem}.loop', 'w') as f:
        for a, b in le: f.write(f"{a} {b} {info[a]['owner'] if info and a in info else 0}\n")


def piece_arrays(P):
    V, T, pr = P.result(); used = np.unique(T); return V, T, pr


rows = []
HS = Source(hull.V, hull.T, HUV, [i for i, f in enumerate(HF) for _ in range(len(f) - 2)]); HS.isl = H_ISL


def cutter_source(cut):
    return Source(cut.V, cut.T, cutter_uv(cut), facet_groups(cut.V, cut.T))


def finish(case, variant, V, T, prov, srcs, ref, plane=None, extra=None, info=None, stem=None):
    UV, frag, src, far = assign_uv(V, T, prov, srcs)
    m = measure(V, T, prov, ref, plane); u = uv_report(V, T, prov, UV, frag, src, srcs)
    rows.append(dict(case=case, variant=variant, **m, **{'uv_' + k: v for k, v in u.items()}, **(extra or {})))
    save(stem or f'{case}_{variant}', V, T, prov, UV, info)
    print(case, variant, {k: rows[-1][k] for k in ('hull_slivers', 'hull_worst', 'brush_slivers', 'brush_worst', 'loop_edges_under_bw', 'uv_not_fragments_hull', 'uv_not_fragments_brush', 'uv_uv_flipped_hull', 'uv_uv_flipped_brush')}, flush=True)
    return UV


# ------------------------------------------------------------------ flat splits
for base in ('split_fwd', 'probe_crease'):
    if ONLY and base not in ONLY: continue
    c = cases[base + '_sub']; cut = Cutter(c); CS = cutter_source(cut); srcs = {0: HS, 1: CS}
    pieces = {'sub': load_run(base + '_sub'), 'int': load_run(base + '_int')}
    V0, T0, p0 = pieces['sub']; L0, _ = loops_of(T0, p0); refl = densify(V0, L0, 64)
    n, _ = cut.frame(V0[L0[0]].mean(0)); plane = (n, float(V0[L0[0][0]] @ n))
    for pk, (V, T, p) in pieces.items():
        finish(f'{base}_{pk}', 'naive', V, T, p, srcs, refl, plane)
    corners = [V0[v] for v in {v for L in L0 for v in L} if (lambda e: e is not None and e in hull.crease)(hull.edge_of(V0[v], TOL))]
    seam_pts = uv_seam_points(V0, {v for L in L0 for v in L}) if PROTECT_UV_SEAMS else []
    capuv = {}
    for variant in ('r4-noslide', 'r4'):
        Ps = [OW.Piece(V, T[p == 0], np.zeros(int((p == 0).sum()), int)) for V, T, p in pieces.values()]
        stm = short_loop_merge(Ps, corners + seam_pts)
        sls = slide(Ps, corners + seam_pts) if variant == 'r4' else {}
        res = {}
        for pk, P in zip(pieces, Ps):
            V, T, _ = P.result(); L = boundary_loops(T)
            lset = {(min(a, b), max(a, b)) for lp in L for a, b in zip(lp, lp[1:] + lp[:1])}
            T1, nf = flip_hull_all(V, T, np.zeros(len(T), int), lset, band_of(V, T, L))
            VV = V
            # caps: one CDT per seam loop, boundary edges are the constraints
            capT = []
            for lp in L:
                e1, e2 = plane_frame(n); o = VV[lp].mean(0)
                pts, tri = spade_cdt(np.stack([(VV[lp] - o) @ e1, (VV[lp] - o) @ e2], 1), [(i, (i + 1) % len(lp)) for i in range(len(lp))])
                idx = list(lp) + list(range(len(VV), len(VV) + len(pts) - len(lp)))
                VV = np.vstack([VV, o + pts[len(lp):, :1] * e1 + pts[len(lp):, 1:2] * e2]); capT += [[idx[k] for k in t] for t in tri]
            capT = np.array(capT); hd = {(int(t[k]), int(t[(k + 1) % 3])) for t in T1 for k in range(3)}
            if any((int(t[k]), int(t[(k + 1) % 3])) in hd for t in capT for k in range(3)): capT = capT[:, ::-1]
            T2 = np.vstack([T1, capT]); P2 = np.concatenate([np.zeros(len(T1), int), np.ones(len(capT), int)])
            UV = finish(f'{base}_{pk}', variant, VV, T2, P2, srcs, refl, plane, dict(flips=nf, short_merges=stm.get('applied'), slide=sls))
            res[pk] = (VV, T2, P2); capuv[(variant, pk)] = (VV, T2, P2, UV)
        A, B = res['sub'], res['int']
        la = A[0][sorted({v for L in loops_of(A[1], A[2])[0] for v in L})]; lb = B[0][sorted({v for L in loops_of(B[1], B[2])[0] for v in L})]
        crack = float(max(cKDTree(lb).query(la)[0].max(), cKDTree(la).query(lb)[0].max()))
        # split caps: both pieces' caps are fragments of the same cutter face, so carried UVs coincide
        ua = capuv[(variant, 'sub')]; ub = capuv[(variant, 'int')]
        ca = ua[3][ua[2] == 1].reshape(-1, 2); cb = ub[3][ub[2] == 1].reshape(-1, 2)
        rows.append(dict(case=base, variant=f'{variant} pieces', crack=crack, cap_uv_overlap=float(cKDTree(cb).query(ca)[0].max()),
                         cap_uv_area_sub=float(np.abs(uv_area(ua[3][ua[2] == 1])).sum()), cap_uv_area_int=float(np.abs(uv_area(ub[3][ub[2] == 1])).sum())))
        print(rows[-1], flush=True)


# ------------------------------------------------------------------ cut-ins and adds
def facet_cdt(V, T, prov, cut, src, split_brush_edges=False):
    """Call (d): re-triangulate each planar brush facet the hull trimmed (it holds a loop edge), inside its own plane.
    split_brush_edges (a variant, not Self's call): a trimmed facet's brush edges (never loop edges) longer than twice
    the facet's median loop edge get evenly spaced collinear vertices, shared by both facets on that edge (the other
    facet is re-triangulated too), so the edge stays where it is and both halves keep its bevel weight."""
    groups = facet_groups(cut.V, cut.T); FNc, _ = face_normals(cut.V, cut.T)
    by = defaultdict(list)
    for fi in np.where(prov == 1)[0]: by[groups[src[fi]]].append(fi)
    loops, le = loops_of(T, prov); lset = {(min(a, b), max(a, b)) for a, b in le}
    keep = np.ones(len(T), bool); add = []; VV = V; st = defaultdict(int)
    def bnd(fs):
        ef = defaultdict(int)
        for fi in fs:
            for k in range(3): a, b = int(T[fi][k]), int(T[fi][(k + 1) % 3]); ef[(min(a, b), max(a, b))] += 1
        return [e for e, c in ef.items() if c == 1]
    todo = {g for g, fs in by.items() if any(e in lset for e in bnd(fs))}
    splits = {}
    if split_brush_edges:
        for g in list(todo):
            be = bnd(by[g]); ll = [np.linalg.norm(V[a] - V[b]) for a, b in be if (a, b) in lset]
            s_ = float(np.median(ll))
            for a, b in be:
                L = np.linalg.norm(V[a] - V[b])
                if (a, b) in lset or (a, b) in splits or L <= 2 * s_: continue
                k = int(round(L / s_)) - 1; P = [V[a] + (V[b] - V[a]) * (i + 1) / (k + 1) for i in range(k)]
                splits[(a, b)] = list(range(len(VV), len(VV) + k)); VV = np.vstack([VV, P]); st['brush_edge_points'] += k
        for g, fs in by.items():
            if any(e in splits for e in bnd(fs)): todo.add(g)
    for g, fs in by.items():
        if g not in todo: continue
        nv, nt, miss, nc = cdt_region(VV, T[fs], FNc[g], set(), splits)
        VV = np.vstack([VV, nv]); keep[fs] = False; add.append(nt)
        st['facets'] += 1; st['old_tris'] += len(fs); st['new_tris'] += len(nt); st['constraint_edges'] += nc; st['constraint_edges_missing'] += miss; st['steiner'] += len(nv)
    if not add: return VV, T, prov, dict(st)
    NT = np.vstack(add)
    return VV, np.vstack([T[keep], NT]), np.concatenate([prov[keep], np.ones(len(NT), int)]), dict(st)


for name in ('port_flank_s16', 'probe_switch_s48', 'probe_crease_cyl_s16', 'probe_box_flank', 'probe_box_ridge', 'add_box_flank', 'add_cyl_flank_s16'):
    if ONLY and name not in ONLY: continue
    c = cases[name]; cut = Cutter(c); CS = cutter_source(cut); srcs = {0: HS, 1: CS}
    V, T, p = load_run(name)
    if c['kind'] == 'cyl':
        Vr, Tr, pr = load_run(name + '_REF'); ref = densify(Vr, loops_of(Tr, pr)[0], 4)
    else:
        ref = densify(V, loops_of(T, p)[0], 64)
    finish(name, 'naive', V, T, p, srcs, ref)
    seam_pts = (uv_seam_points(V, {v for L in loops_of(T, p)[0] for v in L}) + [hull.V[v].copy() for v in UV_SEAM_V]) if PROTECT_UV_SEAMS else []
    welded, st, done, infos = OW.owner_weld([(V, T, p)], hull, cut, TOL, extra_protected=seam_pts)
    Vw, Tw, pw = welded[0]; info = infos[0][1]
    own = dict(hull=sum(1 for i in info.values() if i['owner'] == 0), brush=sum(1 for i in info.values() if i['owner'] == 1))
    finish(name, 'owner-r4', Vw, Tw, pw, srcs, ref, extra=dict(weld=st, owners=own), info=info)
    corners = OW.corners_of(OW.Piece(Vw, Tw, pw), {v: i for v, i in info.items()}, hull, cut, TOL)
    corners_all = corners + seam_pts
    PL = [OW.Piece(Vw, Tw, pw)]; sls = slide(PL, corners_all, joint_absent=False); Vs, Ts, ps = PL[0].result()
    L, le = loops_of(Ts, ps); lset = {(min(a, b), max(a, b)) for a, b in le}
    T1, nf = flip_hull_all(Vs, Ts, ps, lset, band_of(Vs, Ts, L))
    _, _, srcf, _ = assign_uv(Vs, T1, ps, srcs)
    if os.environ.get('SPLIT_BRUSH_EDGES') != '0':
        V3, T3, p3, fst3 = facet_cdt(Vs, T1, ps, cut, srcf, split_brush_edges=True)
        finish(name, 'r4-split-brush-edges', V3, T3, p3, srcs, ref, extra=dict(facet_cdt=fst3), info=info)
    V2, T2, p2, fst = facet_cdt(Vs, T1, ps, cut, srcf)
    kept = sum(int(np.linalg.norm(V2[np.unique(T2)] - q, axis=1).min() < TOL) for q in corners)
    finish(name, 'r4', V2, T2, p2, srcs, ref, extra=dict(weld=st, slide=sls, flips=nf, facet_cdt=fst, corners=len(corners), corners_kept=kept), info=info)

rows.append(dict(case='spade', variant='cdt calls', **CDT_CALLS))
rows.append(dict(case='uv', variant='fixture', uv_fixture_max_diff=UV_FIXTURE_DIFF, hull_islands=len(set(H_ISL)), rho=RHO))
json.dump(rows, open(f'{outd}/measures4.json', 'w'), indent=1, default=lambda x: x if not hasattr(x, 'item') else x.item())
print('ALLDONE')
