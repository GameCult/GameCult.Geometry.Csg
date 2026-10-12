"""Round 3 case: an oriented box cut into the curved flank (a square port; its 4 vertical edges cross the hull,
putting 4 cutter corners on the loop). Appends to cases.json. Usage: case_obox.py <cases.json> <cutters-dir>"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import save_obj
cf, outd = sys.argv[1:3]
cases = [c for c in json.load(open(cf)) if c['kind'] != 'obox']
base = next(c for c in cases if c['name'] == 'port_flank_s16')
for name, src, half in (('probe_box_flank', base, 0.02), ('probe_box_ridge', next(c for c in cases if c['name'] == 'probe_switch_s48'), 0.06)):
    p, n = np.array(src['p']), np.array(src['n']); n /= np.linalg.norm(n)
    a = np.cross(n, [0.6, 0.8, 0]); a /= np.linalg.norm(a); b = np.cross(n, a)  # rotated off the tessellation
    R = np.stack([a, b, n], 1); lo, hi = np.array([-half, -half, -0.02]), np.array([half, half, 0.03])
    Vl = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    Vb = p + Vl @ R.T
    Q = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    Tb = np.array([[q[0], q[1], q[2]] for q in Q] + [[q[0], q[2], q[3]] for q in Q])
    if np.einsum('ij,ij->i', Vb[Tb[:, 0]], np.cross(Vb[Tb[:, 1]], Vb[Tb[:, 2]])).sum() < 0: Tb = Tb[:, ::-1]
    fn = f'{outd}/{name}.obj'; save_obj(fn, Vb, Tb)
    cases.append(dict(name=name, kind='obox', op='sub', cutter=fn, p=p.tolist(), n=n.tolist(), R=R.tolist(), lo=lo.tolist(), hi=hi.tolist(), note=f'oriented box half-width {half}'))
json.dump(cases, open(cf, 'w'), indent=1); print('ok')
