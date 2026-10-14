import sys, re, collections, math
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE, TopAbs_COMPOUND
from OCP.TopExp import TopExp_Explorer
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds
from OCP.TopoDS import TopoDS
def vol(s):
    p = GProp_GProps(); BRepGProp.VolumeProperties_s(s, p); return round(p.Mass(), 6)
KEYS = ["MANIFOLD_SOLID_BREP","BREP_WITH_VOIDS","CLOSED_SHELL","OPEN_SHELL","ORIENTED_CLOSED_SHELL","SHELL_BASED_SURFACE_MODEL","ADVANCED_FACE","SPHERICAL_SURFACE","CYLINDRICAL_SURFACE","PLANE","FACE_BOUND","FACE_OUTER_BOUND"]
for f in sys.argv[1:]:
    t = open(f).read()
    ents = collections.Counter(re.findall(r"=\s*([A-Z_0-9]+)\s*\(", t))
    print("INSPECT", f.split("/")[-1], {k: ents[k] for k in KEYS if ents[k]})
    rd = STEPControl_Reader(); rd.ReadFile(f); rd.TransferRoots(); s = rd.OneShape()
    print("  OCCT shape type", s.ShapeType(), "valid", BRepCheck_Analyzer(s).IsValid(), "vol", vol(s))
    for kind, nm in ((TopAbs_SOLID, "solid"), (TopAbs_SHELL, "shell")):
        ex = TopExp_Explorer(s, kind); i = 0
        while ex.More():
            sh = ex.Current()
            try:
                fb = ShapeAnalysis_FreeBounds(sh)
                nopen = fb.GetOpenWires().NbChildren() if hasattr(fb.GetOpenWires(), "NbChildren") else "?"
            except Exception as e:
                nopen = "err"
            print("  ", nm, i, "vol", vol(sh), "valid", BRepCheck_Analyzer(sh).IsValid(), "freeOpenWires", nopen)
            i += 1; ex.Next()
