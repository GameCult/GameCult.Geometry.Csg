import sys, numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *
fx = sys.argv[1]
V, F = load_obj(fx + '/hull_nobevel.obj'); T = triangulate(F)
print(manifold_report(V, T))
print('bbox', V.min(0), V.max(0), 'diag', np.linalg.norm(V.max(0) - V.min(0)))
E = np.loadtxt(fx + '/hull_creases.txt', dtype=int)
cv = np.unique(E)
print('crease verts', len(cv), 'bbox', V[cv].min(0), V[cv].max(0))
el = np.linalg.norm(V[T[:, 0]] - V[T[:, 1]], axis=1); print('edge len mean', el.mean(), 'p5', np.percentile(el, 5), 'p95', np.percentile(el, 95))
S, N = curvature_tensors(V, T)
ev = np.linalg.eigvalsh(S)  # includes ~0 along normal
k = np.sort(ev, 1); kmin, kmax = k[:, 0], k[:, 2]
np.save(fx + '/../_curv.npy', S)
for name, idx in [('kmax', np.argsort(-np.abs(kmax))[:5])]:
    for i in idx: print(name, i, V[i], kmin[i], kmax[i])
sad = np.where((kmin < -2) & (kmax > 2))[0]
print('saddle verts (|k|>2 both signs)', len(sad))
if len(sad): print('saddle sample', V[sad[:: max(1, len(sad)//8)]])
# crease chains: print a few crease vertex coordinates sorted by y
print('crease sample', V[cv[np.argsort(V[cv,1])]][::12])
