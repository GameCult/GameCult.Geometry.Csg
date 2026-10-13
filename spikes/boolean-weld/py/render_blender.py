"""Headless Blender: apply the shipped stack (Bevel 1 segment weight-limited 0.001 + Weighted Normal, settings copied
from the cage's own modifiers) to naive and welded boolean results and render them. Run on a COPY of Ships.blend:
blender -b Ships_copy.blend --python render_blender.py -- <weld-dir> <out-dir> <jobs.txt>
jobs.txt lines: <png-name> <ortho-scale> <dx> <dy> <dz> <mesh-stem>[,<mesh-stem>...] [tubes] [uvgrid]
Round 4: reads per-corner UVs (vt); 'uvgrid' renders a UV-grid texture view; for every mesh built it measures the bevel
strips' UVs with bmesh.ops.bevel (the BM bevel the modifier runs) with the modifier's settings on the weighted edges,
whose new faces are the strips; written to <out-dir>/bevel_uv.json."""
import bpy, bmesh, sys, os, json, math
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
print('CAGE clamp_overlap', bev_src.use_clamp_overlap, 'width', bev_src.width, 'offset_type', bev_src.offset_type, 'WN', wn_src.mode, wn_src.keep_sharp)
# Hull crease edges, exported with the hull fixture, carry bevel weight 1 (they equal the cage's bevel-weight edges, round 1).
fx = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fixtures')
HV = [Vector(tuple(map(float, l.split()[1:4]))) for l in open(fx + '/hull_nobevel.obj') if l.startswith('v ')]
segs = [(HV[int(a)], HV[int(b)], 1.0) for a, b in (l.split() for l in open(fx + '/hull_creases.txt') if l.strip())]
kd = kdtree.KDTree(len(segs))
for i, (a, b, w) in enumerate(segs):
    kd.insert((a + b) / 2, i)
kd.balance()
maxlen = max(((a - b).length for a, b, w in segs), default=0)

scene = bpy.data.scenes.new('spike')
bpy.context.window.scene = scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.show_specular_highlight = True
scene.render.resolution_x = scene.render.resolution_y = 700
scene.world = bpy.data.worlds.new('w')
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.type = 'ORTHO'
scene.collection.objects.link(cam)
scene.camera = cam
grey = bpy.data.materials.new('grey'); grey.diffuse_color = (0.75, 0.75, 0.78, 1)
own = [bpy.data.materials.new('own_hull'), bpy.data.materials.new('own_cutter'), bpy.data.materials.new('own_none')]
own[0].diffuse_color = (0.1, 0.35, 1.0, 1); own[1].diffuse_color = (1.0, 0.45, 0.05, 1); own[2].diffuse_color = (0.2, 0.2, 0.2, 1)
grid = bpy.data.images.new('grid', 1024, 1024); grid.generated_type = 'UV_GRID'
gmat = bpy.data.materials.new('uvgrid'); gmat.use_nodes = True
tex = gmat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image = grid; gmat.node_tree.nodes.active = tex
bsdf = gmat.node_tree.nodes.get('Principled BSDF')
if bsdf:
    gmat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
MEAS = {}


def load(stem):
    V, F, VT, FT = [], [], [], []
    for line in open(f'{wd}/{stem}.obj'):
        s = line.split()
        if s and s[0] == 'v':
            V.append(tuple(map(float, s[1:4])))
        elif s and s[0] == 'vt':
            VT.append(tuple(map(float, s[1:3])))
        elif s and s[0] == 'f':
            F.append(tuple(int(x.split('/')[0]) - 1 for x in s[1:]))
            FT.append(tuple(int(x.split('/')[1]) - 1 for x in s[1:]) if '/' in s[1] else None)
    loop = [tuple(map(int, l.split())) for l in open(f'{wd}/{stem}.loop') if l.strip()]
    return V, F, loop, VT, FT


def bevel_uv(m, bev):
    """Strip faces from bmesh.ops.bevel on the weighted edges (all weights are 1 here), with the modifier's settings.
    Per strip: singular values of its 3D-to-UV map in units of the mesh's median hull density, and which charts its
    corners lie in (hull UVs at u < 2.5, brush UVs at u >= 3)."""
    bm = bmesh.new(); bm.from_mesh(m)
    bw = bm.edges.layers.float.get('bevel_weight_edge'); uvl = bm.loops.layers.uv.active
    if uvl is None:
        bm.free(); return None

    def tri_sig(P, Q):
        e1, e2 = P[1] - P[0], P[2] - P[0]; n = e1.cross(e2)
        if e1.length < 1e-15 or n.length < 1e-18:
            return 0.0, 0.0
        x = e1.normalized(); y = n.normalized().cross(x)
        a11, a12, a21, a22 = e1.dot(x), e2.dot(x), e1.dot(y), e2.dot(y); det = a11 * a22 - a12 * a21
        b1, b2 = Q[1] - Q[0], Q[2] - Q[0]
        j11 = (b1.x * a22 - b2.x * a21) / det; j12 = (-b1.x * a12 + b2.x * a11) / det
        j21 = (b1.y * a22 - b2.y * a21) / det; j22 = (-b1.y * a12 + b2.y * a11) / det
        t = j11 * j11 + j12 * j12 + j21 * j21 + j22 * j22; dd = abs(j11 * j22 - j12 * j21)
        r = math.sqrt(max(t * t / 4 - dd * dd, 0))
        return math.sqrt(max(t / 2 - r, 0)), math.sqrt(max(t / 2 + r, 0))

    def sig(f):
        ls = f.loops
        out = [tri_sig([ls[0].vert.co, ls[i].vert.co, ls[i + 1].vert.co], [ls[0][uvl].uv, ls[i][uvl].uv, ls[i + 1][uvl].uv]) for i in range(1, len(ls) - 1)]
        return min(o[0] for o in out), max(o[1] for o in out)

    dens = sorted(math.sqrt(sig(f)[0] * sig(f)[1]) for f in bm.faces if max(l[uvl].uv.x for l in f.loops) < 2.5 and f.calc_area() > 1e-9)
    rho = dens[len(dens) // 2]
    edges = [e for e in bm.edges if bw and e[bw] > 0]
    res = bmesh.ops.bevel(bm, geom=edges, offset=bev.width, offset_type=bev.offset_type, segments=bev.segments, profile=bev.profile,
                          affect='EDGES', clamp_overlap=bev.use_clamp_overlap, loop_slide=bev.loop_slide, miter_outer=bev.miter_outer.replace('MITER_', ''),
                          miter_inner=bev.miter_inner.replace('MITER_', ''), profile_type='SUPERELLIPSE')
    rows = []
    for f in [f for f in res['faces'] if f.is_valid]:
        us = [l[uvl].uv.x for l in f.loops]; smin, smax = sig(f)
        rows.append((smin / rho, smax / rho, 'both' if min(us) < 2.5 <= max(us) else ('hull' if max(us) < 2.5 else 'brush')))
    bm.free()
    q = lambda xs, p: sorted(xs)[min(len(xs) - 1, int(p * len(xs)))] if xs else None
    smin = [r[0] for r in rows]; smax = [r[1] for r in rows]
    return dict(weighted_edges=len(edges), strips=len(rows), spans={k: sum(r[2] == k for r in rows) for k in ('hull', 'brush', 'both')},
                sigma_min_p5=q(smin, .05), sigma_min_median=q(smin, .5), sigma_max_median=q(smax, .5), sigma_max_p95=q(smax, .95),
                sigma_max_max=max(smax, default=None), collapsed_lt_0p05=sum(x < 0.05 for x in smin), rho=rho)


def build(stem, tubes, uvgrid=False):
    V, F, loop, VT, FT = load(stem)
    used = sorted({i for f in F for i in f}); remap = {o: n for n, o in enumerate(used)}
    m = bpy.data.meshes.new(stem)
    m.from_pydata([V[i] for i in used], [], [tuple(remap[i] for i in f) for f in F])
    if VT:
        uvl = m.uv_layers.new(name='UVMap')
        for poly, ft in zip(m.polygons, FT):
            for li, ti in zip(poly.loop_indices, ft):
                uvl.data[li].uv = VT[ti]
    m.materials.append(gmat if uvgrid else grey)
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
    for k in ('width', 'segments', 'limit_method', 'offset_type', 'profile', 'harden_normals', 'miter_outer', 'miter_inner', 'loop_slide'):
        if hasattr(bev_src, k):
            setattr(b, k, getattr(bev_src, k))
    b.use_clamp_overlap = bev_src.use_clamp_overlap if os.environ.get('CLAMP0') != '1' else False
    w = ob.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
    for k in ('mode', 'weight', 'thresh', 'keep_sharp', 'use_face_influence'):
        if hasattr(wn_src, k):
            setattr(w, k, getattr(wn_src, k))
    print('BUILT', stem, 'loop edges', nloop, 'hull weighted edges', nhull)
    if stem not in MEAS:
        MEAS[stem] = bevel_uv(m, b); print('BEVELUV', stem, MEAS[stem])
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
    stems = s[5].split(','); tubes = 'tubes' in s[6:]; uvgrid = 'uvgrid' in s[6:]
    scene.display.shading.color_type = 'TEXTURE' if uvgrid else 'MATERIAL'
    objs, pts = [], []
    for st in stems:
        o, p = build(st, tubes, uvgrid); objs += o; pts += p
    target = max(pts, key=lambda p: p.dot(d)) if s[0].startswith('split') or 'crease' in s[0] else sum(pts, Vector()) / len(pts)
    cam.location = target + d * 2.0
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = scale; cam.data.clip_end = 10
    scene.render.filepath = f'{outd}/{png}.png'
    bpy.ops.render.render(write_still=True)
    print('RENDERED', png)
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
json.dump(MEAS, open(f'{outd}/bevel_uv.json', 'w'), indent=1)
print('ALLDONE')
