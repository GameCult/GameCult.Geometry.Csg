"""Write Blender render jobs and the cap-dropped split meshes. Usage: jobs.py <cases.json> <runs> <weld-dir>"""
import sys, os, json, shutil, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *
cases = {c['name']: c for c in json.load(open(sys.argv[1]))}; runs, wd = sys.argv[2], sys.argv[3]
for piece in ('split_fwd_sub', 'split_fwd_int'):
    V, F = load_obj(f'{runs}/boolmesh_{piece}.obj'); T = triangulate(F)
    pr = np.array([int(x) for x in open(f'{runs}/boolmesh_{piece}.prov').read().split()])
    save_obj(f'{wd}/boolmesh_{piece}_nocap.obj', V, T[pr == 0]); shutil.copy(f'{wd}/boolmesh_{piece}_naive.loop', f'{wd}/boolmesh_{piece}_nocap.loop')
J = []
def port(name, scale):
    n = np.array(cases[name]['n']); n /= np.linalg.norm(n); side = np.cross(n, [0, 0, 1.0]); side /= np.linalg.norm(side) + 1e-12
    d = n + 0.35 * side
    for tag in ('naive', 'weld-across', 'weld-along'):
        J.append(f'{name}_{tag} {scale} {d[0]:.4f} {d[1]:.4f} {d[2]:.4f} boolmesh_{name}_{tag}')
    J.append(f'{name}_owner-along {scale} {n[0]:.4f} {n[1]:.4f} {n[2]:.4f} boolmesh_{name}_weld-along tubes')
    J.append(f'{name}_owner-across {scale} {n[0]:.4f} {n[1]:.4f} {n[2]:.4f} boolmesh_{name}_naive tubes')
port('port_flank_s16', 0.07); port('port_flank_s48', 0.07); port('probe_saddle_s16', 0.07); port('probe_equalk_s16', 0.09); port('probe_switch_s48', 0.3)
J.append('split_fwd_both-capped 0.12 0.3 0.15 1 boolmesh_split_fwd_sub_naive,boolmesh_split_fwd_int_naive')
J.append('split_fwd_both-nocap 0.12 0.3 0.15 1 boolmesh_split_fwd_sub_nocap,boolmesh_split_fwd_int_nocap')
J.append('split_fwd_sub-only 0.12 0.3 0.15 1 boolmesh_split_fwd_sub_naive')
J.append('split_fwd_wire 0.12 0.3 0.15 1 boolmesh_split_fwd_sub_naive tubes')
J.append('probe_crease_both 0.08 1 -0.3 0.25 boolmesh_probe_crease_sub_naive,boolmesh_probe_crease_int_naive')
J.append('probe_crease_sub-only 0.08 1 -0.3 0.25 boolmesh_probe_crease_sub_naive tubes')
open(f'{wd}/jobs.txt', 'w').write('\n'.join(J) + '\n'); print(len(J), 'jobs')
