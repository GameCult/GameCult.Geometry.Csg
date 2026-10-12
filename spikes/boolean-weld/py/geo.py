"""Scratch geometry helpers for the boolean-weld spike (not production code)."""
import numpy as np
from collections import defaultdict

def load_obj(path):
    V, F = [], []
    for line in open(path):
        s = line.split()
        if not s: continue
        if s[0] == 'v': V.append([float(x) for x in s[1:4]])
        elif s[0] == 'f': F.append([int(x.split('/')[0]) - 1 for x in s[1:]])
    return np.array(V), F

def triangulate(F):
    T = []
    for f in F:
        for i in range(1, len(f) - 1): T.append([f[0], f[i], f[i + 1]])
    return np.array(T, dtype=np.int64)

def save_obj(path, V, T, extra=None):
    with open(path, 'w') as f:
        for v in V: f.write(f"v {v[0]:.9f} {v[1]:.9f} {v[2]:.9f}\n")
        for t in T: f.write("f " + " ".join(str(i + 1) for i in t) + "\n")

def edge_faces(T):
    ef = defaultdict(list)
    for fi, t in enumerate(T):
        for k in range(3):
            a, b = int(t[k]), int(t[(k + 1) % 3]); ef[(min(a, b), max(a, b))].append(fi)
    return ef

def manifold_report(V, T):
    ef = edge_faces(T)
    bad = sum(1 for e, fs in ef.items() if len(fs) != 2)
    # orientation: each directed edge once
    de = defaultdict(int)
    for t in T:
        for k in range(3): de[(int(t[k]), int(t[(k + 1) % 3]))] += 1
    misor = sum(1 for e, c in de.items() if c != 1 or de.get((e[1], e[0]), 0) != 1)
    used = np.unique(T); 
    vol = np.einsum('ij,ij->i', V[T[:, 0]], np.cross(V[T[:, 1]], V[T[:, 2]])).sum() / 6
    return dict(V=len(V), T=len(T), nonmanifold_edges=bad, misoriented=misor, unused_verts=len(V) - len(used),
                euler=len(V) - len(ef) + len(T), volume=vol)

def face_normals(V, T):
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    a = np.linalg.norm(n, axis=1)
    return n / np.maximum(a, 1e-300)[:, None], a / 2

def vertex_normals(V, T):
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    vn = np.zeros_like(V)
    for k in range(3): np.add.at(vn, T[:, k], n)
    return vn / np.maximum(np.linalg.norm(vn, axis=1), 1e-300)[:, None]

def vertex_adj(T, nv):
    adj = [set() for _ in range(nv)]
    for t in T:
        for k in range(3):
            a, b = int(t[k]), int(t[(k + 1) % 3]); adj[a].add(b); adj[b].add(a)
    return adj

def curvature_tensors(V, T, crease_verts=()):
    """Per-vertex second fundamental form as a 3x3 tensor in world space, from a quadric fit
    h = a x^2 + b x y + c y^2 + d x + e y over the 2-ring. Sign: positive = convex (bends away from
    the outward normal). Crease vertices get +inf flag (returned separately)."""
    N = vertex_normals(V, T); adj = vertex_adj(T, len(V))
    S = np.zeros((len(V), 3, 3))
    for i in range(len(V)):
        ring = set(adj[i]); r2 = set(ring)
        for j in ring: r2 |= adj[j]
        r2.discard(i); r2 = list(r2)
        n = N[i]; e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < .9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
        d = V[r2] - V[i]; x, y, h = d @ e1, d @ e2, d @ n
        A = np.stack([x * x, x * y, y * y, x, y], 1)
        if len(r2) < 5: continue
        coef = np.linalg.lstsq(A, h, rcond=None)[0]
        a, b, c = coef[:3]
        II = -np.array([[2 * a, b], [b, 2 * c]])  # convex positive
        E = np.stack([e1, e2], 1)
        S[i] = E @ II @ E.T
    return S, N

def normal_curvature(S, u):
    return float(u @ S @ u)
