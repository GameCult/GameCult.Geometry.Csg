"""Pick placements on the hull and write cutter meshes plus a case manifest (cases.txt)."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *
fx, outd = sys.argv[1], sys.argv[2]
os.makedirs(outd, exist_ok=True)
V, F = load_obj(fx + '/hull_nobevel.obj'); T = triangulate(F)
FN, FA = face_normals(V, T)
S = np.load(fx + '/../_curv.npy')
VN = vertex_normals(V, T)

def ray_hits(o, d):
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    e1, e2 = b - a, c - a; p = np.cross(d, e2); det = e1 @ np.zeros(3) + np.einsum('ij,ij->i', e1, p)
    inv = 1 / np.where(np.abs(det) < 1e-15, np.nan, det); s = o - a
    u = np.einsum('ij,ij->i', s, p) * inv; q = np.cross(s, e1); v = (q @ d) * inv; t = np.einsum('ij,ij->i', e2, q) * inv
    ok = (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0)
    idx = np.where(ok)[0]; return sorted((t[i], i) for i in idx)

def surf_point(x, y, top=True):
    o = np.array([x, y, 1.0 if top else -1.0]); d = np.array([0, 0, -1.0 if top else 1.0])
    h = ray_hits(o, d); t, fi = h[0]; p = o + t * d
    w = V[T[fi]]; n = FN[fi]
    hs = [hh for hh in h if hh[0] - t > 1e-6]
    thick = hs[0][0] - t if hs else None
    return p, n, thick

def cylinder(p, n, r, depth, height, seg):
    a = n / np.linalg.norm(n); e1 = np.cross(a, [1, 0, 0] if abs(a[0]) < .9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(a, e1)
    ang = np.arange(seg) * 2 * np.pi / seg
    ring = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
    bot = p - depth * a + r * ring; top = p + height * a + r * ring
    Vc = np.vstack([bot, top, [p - depth * a], [p + height * a]]); cb, ct = 2 * seg, 2 * seg + 1
    Tc = []
    for i in range(seg):
        j = (i + 1) % seg
        Tc += [[i, j, seg + j], [i, seg + j, seg + i], [cb, j, i], [ct, seg + i, seg + j]]
    return Vc, np.array(Tc)

def box(lo, hi):
    lo, hi = np.array(lo, float), np.array(hi, float)
    Vb = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    Q = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    return Vb, np.array([[q[0], q[1], q[2]] for q in Q] + [[q[0], q[2], q[3]] for q in Q])

def orient_out(Vc, Tc):
    vol = np.einsum('ij,ij->i', Vc[Tc[:, 0]], np.cross(Vc[Tc[:, 1]], Vc[Tc[:, 2]])).sum()
    return Tc if vol > 0 else Tc[:, ::-1]

cases = []
def add_cyl(name, x, y, r, segs, top=True, note=''):
    p, n, th = surf_point(x, y, top); dep = min(0.02, 0.6 * th) if th else 0.02
    for sg in segs:
        Vc, Tc = cylinder(p, n, r, dep, 0.03, sg); Tc = orient_out(Vc, Tc)
        fn = f'{outd}/{name}_s{sg}.obj'; save_obj(fn, Vc, Tc)
        cases.append(dict(name=f'{name}_s{sg}', kind='cyl', op='sub', cutter=fn, p=p.tolist(), n=n.tolist(), r=r, seg=sg, thick=th, depth=dep, note=note))
    # reference: same cylinder, 1024 segments, for the true intersection curve
    Vc, Tc = cylinder(p, n, r, dep, 0.03, 1024); Tc = orient_out(Vc, Tc); save_obj(f'{outd}/{name}_ref.obj', Vc, Tc)

def add_split(name, lo, hi, note=''):
    Vb, Tb = box(lo, hi); Tb = orient_out(Vb, Tb); fn = f'{outd}/{name}.obj'; save_obj(fn, Vb, Tb)
    for op in ('sub', 'int'):
        cases.append(dict(name=f'{name}_{op}', kind='box', op=op, cutter=fn, lo=list(lo), hi=list(hi), note=note))

# 1. gun port on the upper flank
add_cyl('port_flank', 0.17, 0.0, 0.015, (16, 48), note='flank gun port')
# 2. transverse panel split round the forward body
add_split('split_fwd', (-0.8, 0.22, -0.6), (0.8, 0.8, 0.6), note='transverse split, forward body (crosses the rim crease twice)')
# probe 1: equal curvature. Non-crease, upward-facing vertex whose max |k| is nearest 1/0.02; the cylinder radius
# is 1/|k| there, so |k_hull| and |k_cutter| (around) match at the placement.
E0 = np.loadtxt(fx + '/hull_creases.txt', dtype=int); cv0 = set(np.unique(E0).tolist()); adj0 = vertex_adj(T, len(V)); nr0 = set(cv0)
for c in cv0: nr0 |= adj0[c]
for c in list(nr0): nr0 |= adj0[c]
km = np.abs(np.linalg.eigvalsh(S)).max(1); score = np.abs(km - 50.0); score[list(nr0)] = 1e9; score[VN[:, 2] < 0.5] = 1e9
i = int(np.argmin(score)); kr = km[i]
add_cyl('probe_equalk', float(V[i, 0]), float(V[i, 1]), float(1 / kr), (16, 48), note=f'vertex {i}, r=1/|k|max={1/kr:.4f}, |k|={kr:.2f}')
# probe 1b: planar split near-flat region (longitudinal plane through the lower belly)
# probe 2: saddle, strongest opposite-sign principal curvatures away from creases
E = np.loadtxt(fx + '/hull_creases.txt', dtype=int); cv = set(np.unique(E).tolist())
adj = vertex_adj(T, len(V)); near = set(cv)
for c in cv: near |= adj[c]
for c in list(near): near |= adj[c]
kk = np.sort(np.linalg.eigvalsh(S), 1); sad = np.minimum(-kk[:, 0], kk[:, 2])
sad[list(near)] = -1; sad[VN[:, 2] < 0.3] = -1
si = int(np.argmax(sad)); sp = V[si]
add_cyl('probe_saddle', float(sp[0]), float(sp[1]), 0.015, (16, 48), note=f'saddle vertex {si} k1={kk[si,0]:.2f} k2={kk[si,2]:.2f}')
# probe 3: split across the wing-rim crease (chordwise plane through the wing)
add_split('probe_crease', (0.33, -0.8, -0.6), (0.9, 0.8, 0.6), note='chordwise split x>0.33 crosses the rim crease')
# probe 4: big cylinder across the dorsal ridge to the flank (ownership switch along one loop)
add_cyl('probe_switch', 0.0, -0.05, 0.08, (48,), note='r=0.08 across the dorsal ridge')
json.dump(cases, open(outd + '/cases.json', 'w'), indent=1)
for c in cases: print(c['name'], c.get('thick'), c['note'])
