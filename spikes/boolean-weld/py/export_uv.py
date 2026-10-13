"""Round 4: stand-in UV0 on the hand cage (Smart UV Project on the cage, mirrored half offset by 1 in U), then export
Blender's evaluated mesh (Mirror + Subdivision, Bevel and Weighted Normal off) with per-corner UVs. Never saved."""
import bpy, sys, math
d = sys.argv[-1]
cage = bpy.data.objects['Dexter Quiet Cage']
print('MODS', [(m.type, m.name) for m in cage.modifiers], 'UVLAYERS', [u.name for u in cage.data.uv_layers])
for m in cage.modifiers:
    if m.type in ('BEVEL', 'WEIGHTED_NORMAL'): m.show_viewport = False; m.show_render = False
    if m.type == 'MIRROR': m.use_mirror_u = False; m.offset_u = 1.0; print('MIRROR uv', m.use_mirror_u, m.offset_u)
    if m.type == 'SUBSURF': print('SUBSURF', m.levels, m.render_levels, m.uv_smooth, getattr(m, 'use_limit_surface', None))
vl = bpy.context.view_layer
for o in vl.objects: o.select_set(False)
vl.objects.active = cage; cage.select_set(True)
if not cage.data.uv_layers: cage.data.uv_layers.new(name='UVMap')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
dg = bpy.context.evaluated_depsgraph_get(); src = cage.evaluated_get(dg); me = src.to_mesh()
uv = me.uv_layers.active.data
with open(d + '/hull_uv.obj', 'w') as f:
    for v in me.vertices:
        p = cage.matrix_world @ v.co; f.write(f"v {p.x:.7f} {p.y:.7f} {p.z:.7f}\n")
    for l in me.loops: f.write(f"vt {uv[l.index].uv.x:.9f} {uv[l.index].uv.y:.9f}\n")
    for poly in me.polygons:
        f.write('f ' + ' '.join(f'{me.loops[li].vertex_index + 1}/{li + 1}' for li in poly.loop_indices) + '\n')
print('EXPORTED', len(me.vertices), len(me.polygons), 'loops', len(me.loops))
src.to_mesh_clear()
