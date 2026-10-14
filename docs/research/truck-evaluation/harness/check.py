"""Independent checks of truck output with OpenCASCADE (cadquery-ocp) and plain-python OBJ analysis.
modes:
  ref <cases.json> <outdir>   OCCT reference boolean per case: volume + writes ref_NN.step
  one <file.step>             BRepCheck / counts / volume of one STEP (own process; OCCT may segfault)
  obj <file.obj>              watertightness and volume of an OBJ mesh
  all <dir>                   run `one` per *.step and `obj` per *.obj in subprocesses
"""
import sys, json, subprocess, math, os, glob


def vol_of(shape):
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, p)
    return p.Mass()


def count(shape, kind):
    from OCP.TopExp import TopExp_Explorer
    e = TopExp_Explorer(shape, kind)
    n = 0
    while e.More():
        n += 1
        e.Next()
    return n


def one(path):
    from OCP.STEPControl import STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE
    r = STEPControl_Reader()
    st = r.ReadFile(path)
    out = {"file": os.path.basename(path), "read_ok": st == IFSelect_RetDone}
    if st != IFSelect_RetDone:
        print("RES " + json.dumps(out)); return
    nroots = r.TransferRoots()
    s = r.OneShape()
    out.update({"roots": nroots, "null": s.IsNull()})
    if not s.IsNull():
        out.update({"valid": BRepCheck_Analyzer(s).IsValid(), "solids": count(s, TopAbs_SOLID),
                    "shells": count(s, TopAbs_SHELL), "faces": count(s, TopAbs_FACE), "volume": vol_of(s)})
    print("RES " + json.dumps(out))


def objcheck(path):
    pts, tris = [], []
    for line in open(path):
        t = line.split()
        if not t:
            continue
        if t[0] == "v":
            pts.append((float(t[1]), float(t[2]), float(t[3])))
        elif t[0] == "f":
            idx = [int(x.split("/")[0]) - 1 for x in t[1:]]
            for i in range(1, len(idx) - 1):
                tris.append((idx[0], idx[i], idx[i + 1]))
    key = {}
    remap = []
    for p in pts:
        k = (round(p[0] / 1e-6), round(p[1] / 1e-6), round(p[2] / 1e-6))
        remap.append(key.setdefault(k, len(key)))
    edges = {}
    vol = 0.0
    degenerate = 0
    for a, b, c in tris:
        pa, pb, pc = pts[a], pts[b], pts[c]
        vol += (pa[0] * (pb[1] * pc[2] - pb[2] * pc[1]) - pa[1] * (pb[0] * pc[2] - pb[2] * pc[0]) + pa[2] * (pb[0] * pc[1] - pb[1] * pc[0])) / 6.0
        ra, rb, rc = remap[a], remap[b], remap[c]
        if len({ra, rb, rc}) < 3:
            degenerate += 1
            continue
        for u, v in ((ra, rb), (rb, rc), (rc, ra)):
            edges[(u, v)] = edges.get((u, v), 0) + 1
    unmatched = sum(1 for (u, v), n in edges.items() if edges.get((v, u), 0) != n)
    multi = sum(1 for n in edges.values() if n > 1)
    print("RES " + json.dumps({"file": os.path.basename(path), "tris": len(tris), "welded_vertices": len(key),
                               "degenerate_after_weld": degenerate, "unmatched_directed_edges": unmatched,
                               "multi_edges": multi, "watertight_oriented": unmatched == 0 and multi == 0,
                               "volume": vol}))


def build_ref(cases_path, outdir):
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeTorus
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Trsf, gp_Ax1, gp_Ax2, gp_Pnt, gp_Dir, gp_Vec
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCP.BRepCheck import BRepCheck_Analyzer
    cases = json.load(open(cases_path))
    o = gp_Pnt(0, 0, 0)
    z = gp_Dir(0, 0, 1)

    def prim(e):
        d, k = e["d"], e["k"]
        if k == "box":
            s = BRepPrimAPI_MakeBox(gp_Pnt(-d[0] / 2, -d[1] / 2, -d[2] / 2), d[0], d[1], d[2]).Shape()
        elif k == "cyl":
            s = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, -d[1] / 2), z), d[0], d[1]).Shape()
        elif k == "sph":
            s = BRepPrimAPI_MakeSphere(o, d[0]).Shape()
        else:
            s = BRepPrimAPI_MakeTorus(gp_Ax2(o, z), d[0], d[1]).Shape()
        for axis, key in ((gp_Dir(1, 0, 0), "rx"), (gp_Dir(0, 1, 0), "ry")):
            if e[key]:
                t = gp_Trsf(); t.SetRotation(gp_Ax1(o, axis), math.radians(e[key]))
                s = BRepBuilderAPI_Transform(s, t, True).Shape()
        t = gp_Trsf(); t.SetTranslation(gp_Vec(*e["p"]))
        return BRepBuilderAPI_Transform(s, t, True).Shape()

    for i, c in enumerate(cases):
        rec = {"case": c["name"], "idx": i, "exp": c["exp"]}
        try:
            cur = prim(c["a"])
            for b in c["bs"]:
                bb = prim(b)
                alg = {"union": BRepAlgoAPI_Fuse, "subtract": BRepAlgoAPI_Cut, "intersect": BRepAlgoAPI_Common}[c["op"]](cur, bb)
                cur = alg.Shape()
            rec["occt_volume"] = vol_of(cur)
            rec["occt_valid"] = BRepCheck_Analyzer(cur).IsValid()
            w = STEPControl_Writer(); w.Transfer(cur, STEPControl_AsIs)
            w.Write(os.path.join(outdir, "ref_%02d.step" % (i + 1)))
        except Exception as ex:
            rec["error"] = str(ex)[:200]
        print("RES " + json.dumps(rec))


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "one":
        one(sys.argv[2])
    elif m == "obj":
        objcheck(sys.argv[2])
    elif m == "ref":
        build_ref(sys.argv[2], sys.argv[3])
    elif m == "all":
        for f in sorted(glob.glob(sys.argv[2] + "/*.step")) + sorted(glob.glob(sys.argv[2] + "/*.obj")):
            if os.path.basename(f).startswith("ref_"):
                continue
            mode = "one" if f.endswith(".step") else "obj"
            try:
                r = subprocess.run([sys.executable, "-I", __file__, mode, f], capture_output=True, text=True, timeout=180)
                lines = [l for l in r.stdout.splitlines() if l.startswith("RES ")]
                if r.returncode != 0 or not lines:
                    print("RES " + json.dumps({"file": os.path.basename(f), "rc": r.returncode, "stderr_tail": r.stderr[-300:]}))
                else:
                    print(lines[0])
            except subprocess.TimeoutExpired:
                print("RES " + json.dumps({"file": os.path.basename(f), "timeout": True}))
