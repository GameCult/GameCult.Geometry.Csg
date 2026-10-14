using System.Diagnostics;
using System.Text.Json;
using Aetheris.Kernel.Core.Brep;
using Aetheris.Kernel.Core.Brep.Boolean;
using Aetheris.Kernel.Core.Brep.Verification;
using Aetheris.Kernel.Core.Geometry;
using Aetheris.Kernel.Core.Geometry.Curves;
using Aetheris.Kernel.Core.Geometry.Surfaces;
using Aetheris.Kernel.Core.Math;
using Aetheris.Kernel.Core.Results;
using Aetheris.Kernel.Core.Step242;
using Aetheris.Kernel.Core.Topology;
using Aetheris.Kernel.Core.Diagnostics;

static class P
{
    static (double c, double s) CS(double deg)
    {
        var d = ((deg % 360) + 360) % 360;
        if (d == 0) return (1, 0);
        if (d == 90) return (0, 1);
        if (d == 180) return (-1, 0);
        if (d == 270) return (0, -1);
        var r = deg * Math.PI / 180;
        return (Math.Cos(r), Math.Sin(r));
    }

    static Transform3D Make(double rxDeg, double ryDeg, double[] p)
    {
        var (cx, sx) = CS(rxDeg);
        var (cy, sy) = CS(ryDeg);
        var rx = Transform3D.FromRowMajor(new double[] { 1, 0, 0, 0, 0, cx, sx, 0, 0, -sx, cx, 0, 0, 0, 0, 1 });
        var ry = Transform3D.FromRowMajor(new double[] { cy, 0, -sy, 0, 0, 1, 0, 0, sy, 0, cy, 0, 0, 0, 0, 1 });
        var t = Transform3D.CreateTranslation(new Vector3D(p[0], p[1], p[2]));
        return rx * ry * t;
    }

    static BrepBody Tr(BrepBody body, Transform3D t)
    {
        var g = new BrepGeometryStore();
        foreach (var c in body.Geometry.Curves)
        {
            g.AddCurve(c.Key, c.Value.Kind switch
            {
                CurveGeometryKind.Line3 => CurveGeometry.FromLine(new Line3Curve(t.Apply(c.Value.Line3!.Value.Origin), t.Apply(c.Value.Line3.Value.Direction))),
                CurveGeometryKind.Circle3 => CurveGeometry.FromCircle(new Circle3Curve(t.Apply(c.Value.Circle3!.Value.Center), t.Apply(c.Value.Circle3.Value.Normal), c.Value.Circle3.Value.Radius, t.Apply(c.Value.Circle3.Value.XAxis))),
                _ => c.Value
            });
        }
        foreach (var s in body.Geometry.Surfaces)
        {
            g.AddSurface(s.Key, s.Value.Kind switch
            {
                SurfaceGeometryKind.Plane => SurfaceGeometry.FromPlane(new PlaneSurface(t.Apply(s.Value.Plane!.Value.Origin), t.Apply(s.Value.Plane.Value.Normal), t.Apply(s.Value.Plane.Value.UAxis))),
                SurfaceGeometryKind.Cylinder => SurfaceGeometry.FromCylinder(new CylinderSurface(t.Apply(s.Value.Cylinder!.Value.Origin), t.Apply(s.Value.Cylinder.Value.Axis), s.Value.Cylinder.Value.Radius, t.Apply(s.Value.Cylinder.Value.XAxis))),
                SurfaceGeometryKind.Sphere => SurfaceGeometry.FromSphere(new SphereSurface(t.Apply(s.Value.Sphere!.Value.Center), t.Apply(s.Value.Sphere.Value.Axis), s.Value.Sphere.Value.Radius, t.Apply(s.Value.Sphere.Value.XAxis))),
                SurfaceGeometryKind.Torus => SurfaceGeometry.FromTorus(new TorusSurface(t.Apply(s.Value.Torus!.Value.Center), t.Apply(s.Value.Torus.Value.Axis), s.Value.Torus.Value.MajorRadius, s.Value.Torus.Value.MinorRadius, t.Apply(s.Value.Torus.Value.XAxis))),
                _ => s.Value
            });
        }
        var vp = new Dictionary<VertexId, Point3D>();
        foreach (var v in body.Topology.Vertices)
            if (body.TryGetVertexPoint(v.Id, out var pt)) vp[v.Id] = t.Apply(pt);
        return new BrepBody(body.Topology, g, body.Bindings, vp, body.SafeBooleanComposition);
    }

    static KernelResult<BrepBody> Prim(JsonElement e)
    {
        var k = e.GetProperty("k").GetString()!;
        var d = e.GetProperty("d").EnumerateArray().Select(x => x.GetDouble()).ToArray();
        var p = e.GetProperty("p").EnumerateArray().Select(x => x.GetDouble()).ToArray();
        var rx = e.GetProperty("rx").GetDouble();
        var ry = e.GetProperty("ry").GetDouble();
        KernelResult<BrepBody> r;
        if (k == "box") r = BrepPrimitives.CreateBox(d[0], d[1], d[2]);
        else if (k == "cyl") r = BrepPrimitives.CreateCylinder(d[0], d[1]);
        else if (k == "sph") r = BrepPrimitives.CreateSphere(d[0]);
        else if (k == "tor") r = BrepPrimitives.CreateTorus(d[0], d[1]);
        else throw new Exception("kind " + k);
        if (!r.IsSuccess) return r;
        if (rx == 0 && ry == 0 && p.All(x => x == 0)) return r;
        return KernelResult<BrepBody>.Success(Tr(r.Value, Make(rx, ry, p)));
    }

    static string Short(IEnumerable<KernelDiagnostic> ds, int n = 3)
        => string.Join(" || ", ds.Take(n).Select(d => "[" + d.Severity + "/" + d.Code + "] " + d.Message)).Replace("\n", " ");

    static int Main(string[] a)
    {
        var cases = JsonDocument.Parse(File.ReadAllText(a[0])).RootElement;
        var outDir = a[1];
        Directory.CreateDirectory(outDir);
        var only = a.Length > 2 ? a[2] : null;
        foreach (var c in cases.EnumerateArray())
        {
            var name = c.GetProperty("name").GetString()!;
            if (only != null && !name.StartsWith(only)) continue;
            var line = new Dictionary<string, object?> { ["name"] = name };
            var sw = Stopwatch.StartNew();
            var cc = c;
            var task = Task.Run(() =>
            {
                var cur = Prim(cc.GetProperty("a"));
                if (!cur.IsSuccess) throw new Exception("PRIM(a): " + Short(cur.Diagnostics));
                var op = cc.GetProperty("op").GetString();
                int i = 0;
                int n = cc.GetProperty("bs").GetArrayLength();
                foreach (var b in cc.GetProperty("bs").EnumerateArray())
                {
                    var rb = Prim(b);
                    if (!rb.IsSuccess) throw new Exception("PRIM(b" + i + "): " + Short(rb.Diagnostics));
                    if (op == "union") cur = BrepBoolean.Union(cur.Value, rb.Value);
                    else if (op == "subtract") cur = BrepBoolean.Subtract(cur.Value, rb.Value);
                    else cur = BrepBoolean.Intersect(cur.Value, rb.Value);
                    i++;
                    if (!cur.IsSuccess) { line["failedAtStep"] = i + "/" + n; return cur; }
                }
                line["stepsDone"] = i + "/" + n;
                return cur;
            });
            try
            {
                if (!task.Wait(TimeSpan.FromSeconds(180))) { line["status"] = "TIMEOUT"; }
                else
                {
                    var r = task.Result;
                    if (!r.IsSuccess) { line["status"] = "REFUSED"; line["msg"] = Short(r.Diagnostics); }
                    else
                    {
                        line["status"] = "OK";
                        line["warn"] = Short(r.Diagnostics.Where(d => d.Severity != KernelDiagnosticSeverity.Info), 2);
                        try
                        {
                            var m = BrepMassProperties.Evaluate(r.Value);
                            line["vol"] = m.Status + ":" + m.AbsoluteVolume.ToString("R") + ":" + m.EvaluationMethod;
                        }
                        catch (Exception ex) { line["vol"] = "EX " + ex.GetType().Name; }
                        try
                        {
                            var s = Step242Exporter.ExportBody(r.Value);
                            if (s.IsSuccess) { File.WriteAllText(Path.Combine(outDir, name + ".step"), s.Value); line["step"] = "exported"; }
                            else line["step"] = "EXPORT_REFUSED " + Short(s.Diagnostics);
                        }
                        catch (Exception ex) { line["step"] = "EXPORT_CRASH " + ex.GetType().Name + ": " + ex.Message; }
                    }
                }
            }
            catch (AggregateException ex)
            {
                var m = ex.InnerException?.Message ?? ex.Message;
                bool prim = m.StartsWith("PRIM");
                line["status"] = prim ? "HARNESS_PRIM_FAIL" : "CRASH";
                line["msg"] = (ex.InnerException?.GetType().Name + ": " + m).Replace("\n", " ");
                if (!prim) line["stack"] = (ex.InnerException?.StackTrace ?? "").Split('\n').Take(3).Select(s => s.Trim()).ToArray();
            }
            line["ms"] = sw.ElapsedMilliseconds;
            Console.WriteLine("RESULT " + JsonSerializer.Serialize(line));
        }
        return 0;
    }
}
