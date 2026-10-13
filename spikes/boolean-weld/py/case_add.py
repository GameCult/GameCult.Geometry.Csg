"""Round 4 cases: add mode (union). An oriented box raised panel at the flank box's placement and a 16-segment cylinder
boss at the gun port's placement, each half sunk into the hull. Appends to cases.json; writes the cylinder's 1024-segment
reference. Usage: case_add.py <cases.json> <cutters-dir>"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import save_obj
cf, outd = sys.argv[1:3]
cases = [c for c in json.load(open(cf)) if c['op'] != 'add']
fl = next(c for c in cases if c['name'] == 'probe_box_flank'); port = next(c for c in cases if c['name'] == 'port_flank_s16')
p, R = np.array(fl['p']), np.array(fl['R']); lo, hi = np.array([-0.025, -0.025, -0.02]), np.array([0.025, 0.025, 0.02])
Vb = p + np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) @ R.T
Q = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
Tb = np.array([[q[0], q[1], q[2]] for q in Q] + [[q[0], q[2], q[3]] for q in Q])
if np.einsum('ij,ij->i', Vb[Tb[:, 0]], np.cross(Vb[Tb[:, 1]], Vb[Tb[:, 2]])).sum() < 0: Tb = Tb[:, ::-1]
save_obj(f'{outd}/add_box_flank.obj', Vb, Tb)
cases.append(dict(name='add_box_flank', kind='obox', op='add', cutter=f'{outd}/add_box_flank.obj', p=p.tolist(), n=fl['n'], R=R.tolist(),
                  lo=lo.tolist(), hi=hi.tolist(), note='add: oriented box raised panel, half-width 0.025, 0.02 proud'))
pc, n = np.array(port['p']), np.array(port['n']) / np.linalg.norm(port['n'])
e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < .9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
for seg in (16, 1024):
    ang = np.arange(seg) * 2 * np.pi / seg; ring = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
    Vc = np.vstack([pc - 0.02 * n + 0.015 * ring, pc + 0.02 * n + 0.015 * ring, [pc - 0.02 * n], [pc + 0.02 * n]]); cb, ct = 2 * seg, 2 * seg + 1
    Tc = []
    for i in range(seg):
        j = (i + 1) % seg; Tc += [[i, j, seg + j], [i, seg + j, seg + i], [cb, j, i], [ct, seg + i, seg + j]]
    Tc = np.array(Tc)
    if np.einsum('ij,ij->i', Vc[Tc[:, 0]], np.cross(Vc[Tc[:, 1]], Vc[Tc[:, 2]])).sum() < 0: Tc = Tc[:, ::-1]
    tag = 's16' if seg == 16 else 'ref'; save_obj(f'{outd}/add_cyl_flank_{tag}.obj', Vc, Tc)
cases.append(dict(name='add_cyl_flank_s16', kind='cyl', op='add', cutter=f'{outd}/add_cyl_flank_s16.obj', p=pc.tolist(), n=n.tolist(), r=0.015, seg=16,
                  depth=0.02, note='add: 16-segment cylinder boss r 0.015, 0.02 proud, at the gun port'))
json.dump(cases, open(cf, 'w'), indent=1); print('ok', len(cases))
