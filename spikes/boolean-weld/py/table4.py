"""Round 4 tables from measures4.json (and bevel_uv.json when given). Usage: table4.py <measures4.json> <out.md> [bevel_uv.json]"""
import sys, json
rows = json.load(open(sys.argv[1])); out = open(sys.argv[2], 'w')
f = lambda v: '' if v is None else (f'{v:.3g}' if isinstance(v, float) else str(v))
geo = ['case', 'variant', 'hull_slivers', 'hull_worst', 'hull_p5', 'brush_slivers', 'brush_worst', 'brush_p5', 'hull_flipped',
       'dev_max_pct', 'seam_off_plane', 'loop_edges_under_bw', 'shortest_loop_edge']
uv = ['case', 'variant', 'uv_faces', 'uv_not_fragments_hull', 'uv_not_fragments_brush', 'uv_uv_flipped_hull', 'uv_uv_flipped_brush',
      'uv_hull_islands', 'uv_hull_src_islands', 'uv_hull_uv_area', 'uv_moved_face_sigma_min', 'uv_moved_face_sigma_max', 'uv_moved_face_aniso_min']
for title, cols in (('Geometry (band = within 2 local edge lengths of the loop)', geo), ('UV0 carry-through', uv)):
    out.write(f'## {title}\n\n| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n')
    for r in rows:
        if 'uv_faces' in r: out.write('| ' + ' | '.join(f(r.get(k)) for k in cols) + ' |\n')
    out.write('\n')
out.write('## Operations\n\n')
for r in rows:
    ex = {k: r[k] for k in ('short_merges', 'slide', 'weld', 'owners', 'flips', 'facet_cdt', 'corners', 'corners_kept', 'crack', 'cap_uv_overlap',
                            'cap_uv_area_sub', 'cap_uv_area_int', 'calls', 'complete', 'incomplete', 'steiner', 'uv_fixture_max_diff', 'hull_islands', 'rho') if k in r}
    if ex: out.write(f"- {r['case']} {r['variant']}: {json.dumps(ex, default=str)}\n")
if len(sys.argv) > 3:
    b = json.load(open(sys.argv[3]))
    cols = ['weighted_edges', 'strips', 'spans', 'sigma_min_p5', 'sigma_min_median', 'sigma_max_median', 'sigma_max_p95', 'sigma_max_max', 'collapsed_lt_0p05']
    out.write('\n## Bevel strips (bmesh.ops.bevel with the modifier settings; sigma = 3D-to-UV singular values / hull median density)\n\n| mesh | ' + ' | '.join(cols) + ' |\n|' + '---|' * (len(cols) + 1) + '\n')
    for k, v in b.items():
        if v: out.write(f'| {k} | ' + ' | '.join(f(v.get(c)) if not isinstance(v.get(c), dict) else json.dumps(v[c]) for c in cols) + ' |\n')
out.close(); print(open(sys.argv[2]).read())
