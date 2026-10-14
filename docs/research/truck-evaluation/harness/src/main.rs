// Torture harness for truck (ricosjp/truck), mirrors the Aetheris harness cases (cases.json).
use serde_json::{json, Value};
use std::f64::consts::PI;
use std::io::BufWriter;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Mutex;
use std::time::Instant;
use truck_meshalgo::prelude::*;
use truck_modeling::*;
use truck_stepio::out;

static PANIC: Mutex<String> = Mutex::new(String::new());

fn take_panic() -> String {
    let mut g = PANIC.lock().unwrap();
    let s = g.clone();
    g.clear();
    s.chars().take(300).collect()
}

fn box_(d: &[f64]) -> Solid {
    let v = builder::vertex(Point3::origin());
    let e = builder::tsweep(&v, Vector3::unit_x());
    let f = builder::tsweep(&e, Vector3::unit_y());
    let c: Solid = builder::tsweep(&f, Vector3::unit_z());
    let c = builder::scaled(&c, Point3::origin(), Vector3::new(d[0], d[1], d[2]));
    builder::translated(&c, Vector3::new(-d[0] / 2.0, -d[1] / 2.0, -d[2] / 2.0))
}

fn cyl(r: f64, h: f64) -> Solid {
    let v = builder::vertex(Point3::new(r, 0.0, -h / 2.0));
    let circle = builder::rsweep(&v, Point3::new(0.0, 0.0, -h / 2.0), Vector3::unit_z(), Rad(7.0), 2);
    let disk = builder::try_attach_plane(&[circle]).unwrap();
    builder::tsweep(&disk, Vector3::new(0.0, 0.0, h))
}

fn sph(r: f64) -> Solid {
    let v0 = builder::vertex(Point3::new(0.0, r, 0.0));
    let wire: Wire = builder::rsweep(&v0, Point3::origin(), Vector3::unit_x(), Rad(PI), 3);
    let shell = builder::cone(&wire, Vector3::unit_y(), Rad(7.0), 4);
    Solid::new(vec![shell])
}

fn tor(big: f64, small: f64) -> Solid {
    let v = builder::vertex(Point3::new(big, 0.0, small));
    let w = builder::rsweep(&v, Point3::new(big, 0.0, 0.0), Vector3::unit_y(), Rad(7.0), 2);
    let shell = builder::rsweep(&w, Point3::origin(), Vector3::unit_z(), Rad(7.0), 2);
    Solid::new(vec![shell])
}

fn mesh_of(s: &Solid, tol: f64) -> PolygonMesh {
    let mut m = s.triangulation(tol).to_polygon();
    m.put_together_same_attrs(TOLERANCE * 50.0).remove_degenerate_faces();
    m
}

fn orient(mut s: Solid) -> Solid {
    if mesh_of(&s, 0.05).volume() < 0.0 {
        s.not();
    }
    s
}

fn nums(v: &Value) -> Vec<f64> {
    v.as_array().unwrap().iter().map(|x| x.as_f64().unwrap()).collect()
}

fn prim(e: &Value) -> Solid {
    let d = nums(&e["d"]);
    let s = match e["k"].as_str().unwrap() {
        "box" => box_(&d),
        "cyl" => cyl(d[0], d[1]),
        "sph" => sph(d[0]),
        "tor" => tor(d[0], d[1]),
        k => panic!("kind {k}"),
    };
    let mut s = orient(s);
    let rx = e["rx"].as_f64().unwrap();
    let ry = e["ry"].as_f64().unwrap();
    if rx != 0.0 {
        s = builder::rotated(&s, Point3::origin(), Vector3::unit_x(), Rad(rx.to_radians()));
    }
    if ry != 0.0 {
        s = builder::rotated(&s, Point3::origin(), Vector3::unit_y(), Rad(ry.to_radians()));
    }
    let p = nums(&e["p"]);
    builder::translated(&s, Vector3::new(p[0], p[1], p[2]))
}

fn apply(op: &str, a: &Solid, b: &Solid, tol: f64) -> Option<Solid> {
    match op {
        "union" => truck_shapeops::or(a, b, tol),
        "intersect" => truck_shapeops::and(a, b, tol),
        "subtract" => {
            let mut nb = b.clone();
            nb.not();
            truck_shapeops::and(a, &nb, tol)
        }
        o => panic!("op {o}"),
    }
}

fn mesh_stats(s: &Solid, tol: f64, objpath: Option<&str>) -> Value {
    let t = Instant::now();
    let r = catch_unwind(AssertUnwindSafe(|| mesh_of(s, tol)));
    let ms = t.elapsed().as_secs_f64() * 1e3;
    match r {
        Ok(m) => {
            if let Some(p) = objpath {
                let f = std::fs::File::create(p).unwrap();
                let _ = truck_meshalgo::rexport_polymesh::obj::write(&m, BufWriter::new(f));
            }
            json!({"tol": tol, "ms": ms, "tris": m.faces().triangle_iter().count(), "faces": m.faces().len(),
                   "closed": format!("{:?}", m.shell_condition()), "vol": m.volume()})
        }
        Err(_) => json!({"tol": tol, "panic": take_panic()}),
    }
}

fn step_string(s: &Solid) -> String {
    let c = s.compress();
    let repr = out::StepDesign::from_model(out::StepModel::from(&c));
    out::StepDisplay::new(
        out::StepHeaderDescriptor { organization_system: "trucktorture".to_owned(), ..Default::default() },
        repr,
    )
    .to_string()
}

fn reread(text: &str) -> Value {
    use truck_stepio::r#in::*;
    let r = catch_unwind(AssertUnwindSafe(|| {
        let table = Table::from_step(text).ok_or("parse failed")?;
        let mut shells = vec![];
        for (_, sh) in table.shell.iter() {
            match table.to_compressed_shell(sh) {
                Ok(cs) => {
                    let mut m = cs.triangulation(0.01).to_polygon();
                    m.put_together_same_attrs(TOLERANCE * 50.0).remove_degenerate_faces();
                    shells.push(json!({"closed": format!("{:?}", m.shell_condition()), "vol": m.volume(),
                        "tris": m.faces().triangle_iter().count()}));
                }
                Err(e) => shells.push(json!({"err": format!("{e:?}").chars().take(200).collect::<String>()})),
            }
        }
        Ok::<_, &str>(json!({"shells": shells}))
    }));
    match r {
        Ok(Ok(v)) => v,
        Ok(Err(e)) => json!({"err": e}),
        Err(_) => json!({"panic": take_panic()}),
    }
}

fn run_case(cases: &Value, idx: usize, tol: f64, out_dir: &str) {
    let c = &cases[idx];
    let name = c["name"].as_str().unwrap();
    let op = c["op"].as_str().unwrap();
    let bs = c["bs"].as_array().unwrap();
    let t0 = Instant::now();
    let mut step_ms: Vec<f64> = vec![];
    let r = catch_unwind(AssertUnwindSafe(|| {
        let mut cur = prim(&c["a"]);
        for b in bs {
            let bb = prim(b);
            let t = Instant::now();
            let n = apply(op, &cur, &bb, tol);
            step_ms.push(t.elapsed().as_secs_f64() * 1e3);
            match n {
                Some(n) => cur = n,
                None => return None,
            }
        }
        Some(cur)
    }));
    let total = t0.elapsed().as_secs_f64() * 1e3;
    eprintln!("STAGE boolean done {:.0}ms", total);
    let maxstep = step_ms.iter().cloned().fold(0.0, f64::max);
    let mut res = json!({"case": name, "idx": idx, "tol": tol, "steps_done": step_ms.len(), "steps_total": bs.len(),
        "boolean_ms_total": total, "boolean_ms_max_step": maxstep, "exp": c["exp"]});
    match r {
        Err(_) => {
            res["status"] = json!("panic");
            res["panic"] = json!(take_panic());
        }
        Ok(None) => res["status"] = json!("refused_none"),
        Ok(Some(s)) => {
            res["status"] = json!("ok");
            res["shells"] = json!(s.boundaries().len());
            res["faces"] = json!(s.boundaries().iter().map(|b| b.len()).sum::<usize>());
            let tag = format!("{}/{:02}_t{}", out_dir, idx + 1, tol);
            res["mesh"] = json!([
                mesh_stats(&s, 0.1, None),
                mesh_stats(&s, 0.01, Some(&format!("{tag}.obj"))),
                mesh_stats(&s, 0.001, None)
            ]);
            eprintln!("STAGE meshes done {:.0}ms", t0.elapsed().as_secs_f64() * 1e3);
            let t = Instant::now();
            let sr = catch_unwind(AssertUnwindSafe(|| step_string(&s)));
            match sr {
                Ok(text) => {
                    res["step_ms"] = json!(t.elapsed().as_secs_f64() * 1e3);
                    res["step_bytes"] = json!(text.len());
                    std::fs::write(format!("{tag}.step"), &text).unwrap();
                    eprintln!("STAGE step written {:.0}ms", t0.elapsed().as_secs_f64() * 1e3);
                    res["step_reread"] = reread(&text);
                    eprintln!("STAGE reread done {:.0}ms", t0.elapsed().as_secs_f64() * 1e3);
                }
                Err(_) => res["step_panic"] = json!(take_panic()),
            }
        }
    }
    println!("RES {}", res);
}

fn read_step(path: &str) {
    let text = std::fs::read_to_string(path).unwrap();
    let t = Instant::now();
    let mut v = reread(&text);
    v["file"] = json!(path);
    v["ms"] = json!(t.elapsed().as_secs_f64() * 1e3);
    println!("RES {}", v);
}

fn prims() {
    for (n, s, exp) in [
        ("box 10x10x10", box_(&[10.0, 10.0, 10.0]), 1000.0),
        ("cyl r5 h10", cyl(5.0, 10.0), PI * 25.0 * 10.0),
        ("sph r5", sph(5.0), 4.0 / 3.0 * PI * 125.0),
        ("tor 10,3", tor(10.0, 3.0), 2.0 * PI * PI * 10.0 * 9.0),
    ] {
        let raw = mesh_of(&s, 0.01).volume();
        let o = orient(s.clone());
        println!(
            "RES {}",
            json!({"prim": n, "analytic": exp, "mesh_vol_raw_orientation": raw,
                   "mesh_vol_after_orient": mesh_of(&o, 0.01).volume()})
        );
    }
}

fn main() {
    std::panic::set_hook(Box::new(|i| {
        let bt = std::backtrace::Backtrace::force_capture().to_string();
        let frames: Vec<String> = bt
            .lines()
            .filter(|l| l.contains("truck_") && !l.trim_start().starts_with("at "))
            .map(|l| l.trim().chars().take(70).collect::<String>())
            .take(6)
            .collect();
        *PANIC.lock().unwrap() = format!("{i}").replace('\n', " | ") + " || " + &frames.join(" ; ");
    }));
    let a: Vec<String> = std::env::args().collect();
    match a[1].as_str() {
        "run" => {
            let cases: Value = serde_json::from_str(&std::fs::read_to_string(&a[2]).unwrap()).unwrap();
            run_case(&cases, a[3].parse().unwrap(), a[4].parse().unwrap(), &a[5]);
        }
        "readstep" => read_step(&a[2]),
        "prims" => prims(),
        _ => panic!("mode"),
    }
}
