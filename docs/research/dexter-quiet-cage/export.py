import bpy, sys, bmesh
d=sys.argv[-1]
dg=bpy.context.evaluated_depsgraph_get()
cage=bpy.data.objects['Dexter Quiet Cage']; ref=bpy.data.objects['Dexter Quiet']
def dump(o, ev, path):
    src=o.evaluated_get(dg) if ev else o
    me=src.to_mesh()
    with open(path,'w') as f:
        for v in me.vertices:
            p=o.matrix_world @ v.co; f.write(f"v {p.x:.6f} {p.y:.6f} {p.z:.6f}\n")
        for poly in me.polygons: f.write("f "+" ".join(str(i+1) for i in poly.vertices)+"\n")
    n=(len(me.vertices),len(me.polygons)); src.to_mesh_clear(); return n
info=[]
info.append(("cage_raw",dump(cage,False,d+"/cage_raw.obj")))
info.append(("cage_limit_eval",dump(cage,True,d+"/cage_eval.obj")))
info.append(("dexter_ref",dump(ref,False,d+"/dexter_ref.obj")))
me=cage.data; a=me.attributes.get('crease_edge')
cr=[(e.vertices[0],e.vertices[1],round(a.data[e.index].value,3)) for e in me.edges if a and a.data[e.index].value>0]
mods=[(m.type,{k:getattr(m,k) for k in ('levels','render_levels','use_limit_surface','width','segments','limit_method','use_clip','use_mirror_merge') if hasattr(m,k)}) for m in cage.modifiers]
open(d+"/cage_info.txt","w").write(f"{info}\ncreases={cr}\nmods={mods}\ncage_dims={tuple(cage.dimensions)} ref_dims={tuple(ref.dimensions)}\n")
