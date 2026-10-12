"""Print measures.json as Markdown tables. Usage: table.py <measures.json> [kernel]"""
import sys, json
d = json.load(open(sys.argv[1])); kern = sys.argv[2] if len(sys.argv) > 2 else None
cols = ['case', 'kernel', 'variant', 'collapses', 'tris_band', 'tris_total', 'slivers_band', 'min_angle_band', 'p5_angle_band',
        'flipped_hull_band', 'dev_mean_pct', 'dev_max_pct', 'dev_max_h', 'ref_to_loop_max_pct', 'outside_band_moved', 'crease_verts_removed', 'split_loop_gap']
print('| ' + ' | '.join(cols) + ' |'); print('|' + '---|' * len(cols))
def f(v):
    if v is None: return ''
    if isinstance(v, float): return f'{v:.3g}'
    return str(v)
for r in d['rows']:
    if kern and r['kernel'] != kern: continue
    print('| ' + ' | '.join(f(r.get(c)) for c in cols) + ' |')
print()
print('| case/kernel/mode | hull-owned | cutter-owned | switches | near-tie | crease loop verts | median abs k_hull | median abs k_cutter | origins |')
print('|---|---|---|---|---|---|---|---|---|')
for k, o in d['owners'].items():
    if kern and k.split('|')[1] != kern: continue
    print(f"| {k} | {o['hull_owned']} | {o['cutter_owned']} | {o['switches']} | {o['near_tie']} | {o['crease_loop_verts']} | {f(o['kh_abs_median'])} | {f(o['kc_abs_median'])} | {o['origins']} |")
if len(sys.argv) > 3:
    for r in d['rows']:
        if 'stats' in r and (not kern or r['kernel'] == kern): print(r['case'], r['variant'], r['stats'], r.get('split_replay', ''))
