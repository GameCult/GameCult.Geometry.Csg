"""Headless Blender: apply the shipped stack (Bevel 1 segment weight-limited 0.001 + Weighted Normal, settings copied
from the cage's own modifiers) to naive and welded boolean results and render them. Run on a COPY of Ships.blend:
blender -b Ships_copy.blend --python render_blender.py -- <weld-dir> <out-dir> <jobs.txt>
jobs.txt lines: <png-name> <ortho-scale> <dx> <dy> <dz> <mesh-stem>[,<mesh-stem>...] [tubes]"""
import bpy, bmesh, sys, os
from mathutils import Vector, kdtree
from mathutils.geometry import intersect_point_line

wd, outd, jobsf = sys.argv[-3:]
os.makedirs(outd, exist_ok=True)
cage = bpy.data.objects['Dexter Quiet Cage']
bev_src = next(m for m in cage.modifiers if m.type == 'BEVEL')
wn_src = next(m for m in cage.modifiers if m.type == 'WEIGHTED_NORMAL')
for m in cage.modifiers:
    if m.type in ('BEVEL', 'WEIGHTED_NORMAL'):
        m.show_viewport = False
dg = bpy.context.evaluated_depsgraph_get()
me = cage.evaluated_get(dg).to_mesh()
att = me.attributes.get('bevel_weight_edge')
segs = []
for e in me.edges:
    w = att.data[e.index].value if att else 0.0
    if w > 0:
        segs.append((cage.matrix_world @ me.vertices[e.vertices[0]].co, cage.matrix_world @ me.vertices[e.vertices[1]].co, w))
print('CAGE weighted edges', len(segs), 'smooth', [p.use_smooth for p in me.polygons][:1])
# Diagnostic: compare the cage's bevel-weight edges with the crease edges exported with the hull fixture.
fx = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fixtures')
HV = [Vector(tuple(map(float, l.split()[1:4]))) for l in open(fx + '/hull_nobevel.obj') if l.startswith('v ')]
csegs = [(HV[int(a)], HV[int(b)]) for a, b in (l.split() for l in open(fx + '/hull_creases.txt') if l.strip())]
ck = kdtree.KDTree(len(csegs))
for i, (a, b) in enumerate(csegs):
    ck.insert((a + b) / 2, i)
ck.balance()
dmax = max((ck.find((a + b) / 2)[2] for a, b, w in segs), default=0)
print('BEVEL-vs-CREASE max midpoint distance', dmax, 'weights', sorted({round(w, 3) for a, b, w in segs}))
segs = [(a, b, 1.0) for a, b in csegs]
kd = kdtree.KDTree(len(segs))
for i, (a, b, w) in enumerate(segs):
    kd.insert((a + b) / 2, i)
kd.balance()
maxlen = max(((a - b).length for a, b, w in segs), default=0)

scene = bpy.data.scenes.new('spike')
bpy.context.window.scene = scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_specular_highlight = True
scene.render.resolution_x = scene.render.resolution_y = 700
scene.world = bpy.data.worlds.new('w')
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.type = 'ORTHO'
scene.collection.objects.link(cam)
scene.camera = cam
grey = bpy.data.materials.new('grey'); grey.diffuse_color = (0.75, 0.75, 0.78, 1)
cmat = bpy.data.materials.new('cut'); cmat.diffuse_color = (0.62, 0.66, 0.75, 1)
own = [bpy.data.materials.new('own_hull'), bpy.data.materials.new('own_cutter'), bpy.data.materials.new('own_none')]
own[0].diffuse_color = (0.1, 0.35, 1.0, 1); own[1].diffuse_color = (1.0, 0.45, 0.05, 1); own[2].diffuse_color = (0.2, 0.2, 0.2, 1)


def load(stem):
    V, F = [], []
    for line in open(f'{wd}/{stem}.obj'):
        s = line.split()
        if s and s[0] == 'v':
            V.append(tuple(map(float, s[1:4])))
        elif s and s[0] == 'f':
            F.append(tuple(int(x) - 1 for x in s[1:]))
    loop = [tuple(map(int, l.split())) for l in open(f'{wd}/{stem}.loop') if l.strip()]
    return V, F, loop


def build(stem, tubes):
    V, F, loop = load(stem)
    used = sorted({i for f in F for i in f}); remap = {o: n for n, o in enumerate(used)}
    m = bpy.data.meshes.new(stem)
    m.from_pydata([V[i] for i in used], [], [tuple(remap[i] for i in f) for f in F])
    m.materials.append(grey)
    ob = bpy.data.objects.new(stem, m); scene.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(m)
    bw = bm.edges.layers.float.get('bevel_weight_edge') or bm.edges.layers.float.new('bevel_weight_edge')
    loopset = {(min(remap[a], remap[b]), max(remap[a], remap[b])) for a, b, o in loop if a in remap and b in remap}
    nloop = nhull = 0
    for e in bm.edges:
        k = (min(e.verts[0].index, e.verts[1].index), max(e.verts[0].index, e.verts[1].index))
        if k in loopset:
            e[bw] = 1.0; nloop += 1; continue
        mid = (e.verts[0].co + e.verts[1].co) / 2
        for co, i, d in kd.find_range(mid, maxlen):
            a, b, w = segs[i]
            ok = True
            for v in e.verts:
                p, t = intersect_point_line(v.co, a, b)
                if (p - v.co).length > 1e-6 or t < -1e-6 or t > 1 + 1e-6:
                    ok = False
            if ok:
                e[bw] = w; nhull += 1; break
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(m); bm.free()
    b = ob.modifiers.new('Bevel', 'BEVEL')
    for k in ('width', 'segments', 'limit_method', 'offset_type', 'profile', 'harden_normals', 'miter_outer', 'miter_inner', 'clamp_overlap', 'loop_slide'):
        if hasattr(bev_src, k):
            setattr(b, k, getattr(bev_src, k))
    w = ob.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
    for k in ('mode', 'weight', 'thresh', 'keep_sharp', 'use_face_influence'):
        if hasattr(wn_src, k):
            setattr(w, k, getattr(wn_src, k))
    print('BUILT', stem, 'loop edges', nloop, 'hull weighted edges', nhull)
    objs = [ob]
    if tubes:
        cu = bpy.data.curves.new(stem + '_own', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0006
        for i in range(3):
            cu.materials.append(own[i])
        for a, bb, o in loop:
            sp = cu.splines.new('POLY'); sp.points.add(1)
            sp.points[0].co = (*V[a], 1); sp.points[1].co = (*V[bb], 1); sp.material_index = o if o in (0, 1) else 2
        co = bpy.data.objects.new(stem + '_own', cu); scene.collection.objects.link(co); objs.append(co)
    return objs, [Vector(V[a]) for a, b, o in loop]


for line in open(jobsf):
    s = line.split()
    if not s or s[0].startswith('#'):
        continue
    png, scale, d = s[0], float(s[1]), Vector(tuple(map(float, s[2:5]))).normalized()
    stems = s[5].split(','); tubes = len(s) > 6 and s[6] == 'tubes'
    objs, pts = [], []
    for st in stems:
        o, p = build(st, tubes); objs += o; pts += p
    target = max(pts, key=lambda p: p.dot(d)) if s[0].startswith('split') or 'crease' in s[0] else sum(pts, Vector()) / len(pts)
    cam.location = target + d * 2.0
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = scale; cam.data.clip_end = 10
    scene.render.filepath = f'{outd}/{png}.png'
    bpy.ops.render.render(write_still=True)
    print('RENDERED', png)
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
print('ALLDONE')
