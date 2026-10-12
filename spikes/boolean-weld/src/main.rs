//! Boolean driver for the boolean-weld spike. Reads two closed OBJ meshes (hull, cutter), runs one
//! boolean in one kernel, writes the result OBJ and a per-triangle provenance file (0 = hull face,
//! 1 = cutter face). Usage: spike-boolean-weld <boolmesh|manifold> <sub|int> <hull.obj> <cutter.obj> <out-prefix>
use std::{fs, time::Instant};

fn load_obj(p: &str) -> (Vec<f64>, Vec<usize>) {
    let (mut v, mut t) = (vec![], vec![]);
    for l in fs::read_to_string(p).expect("read obj").lines() {
        let s: Vec<&str> = l.split_whitespace().collect();
        match s.first() {
            Some(&"v") => v.extend(s[1..4].iter().map(|x| x.parse::<f64>().unwrap())),
            Some(&"f") => {
                let f: Vec<usize> = s[1..].iter().map(|x| x.split('/').next().unwrap().parse::<usize>().unwrap() - 1).collect();
                for i in 1..f.len() - 1 { t.extend([f[0], f[i], f[i + 1]]); }
            }
            _ => {}
        }
    }
    (v, t)
}

fn write(prefix: &str, v: &[f64], t: &[usize], prov: &[u8]) {
    let mut s = String::new();
    for p in v.chunks(3) { s += &format!("v {:.12} {:.12} {:.12}\n", p[0], p[1], p[2]); }
    for f in t.chunks(3) { s += &format!("f {} {} {}\n", f[0] + 1, f[1] + 1, f[2] + 1); }
    fs::write(format!("{prefix}.obj"), s).unwrap();
    fs::write(format!("{prefix}.prov"), prov.iter().map(|p| p.to_string()).collect::<Vec<_>>().join("\n")).unwrap();
}

fn run_boolmesh(op: &str, a: &(Vec<f64>, Vec<usize>), b: &(Vec<f64>, Vec<usize>)) -> (Vec<f64>, Vec<usize>, Vec<u8>) {
    use boolmesh::prelude::*;
    // Provenance rides as a per-corner scalar: 0 on every hull corner, 1 on every cutter corner.
    let va = vec![0.0f64; a.1.len()];
    let vb = vec![1.0f64; b.1.len()];
    let ma = Manifold::new_with_values(&a.0, &a.1, &va).expect("hull not manifold for boolmesh");
    let mb = Manifold::new_with_values(&b.0, &b.1, &vb).expect("cutter not manifold for boolmesh");
    let op = if op == "sub" { OpType::Subtract } else { OpType::Intersect };
    let r = compute_boolean(&ma, &mb, op).expect("boolmesh failed");
    let v: Vec<f64> = r.ps.iter().flat_map(|p| [p.x as f64, p.y as f64, p.z as f64]).collect();
    let t: Vec<usize> = r.hs.iter().map(|h| h.tail).collect();
    let prov: Vec<u8> = (0..t.len() / 3).map(|f| if r.vals[3 * f] > 0.5 { 1 } else { 0 }).collect();
    (v, t, prov)
}

#[cfg(feature = "manifold")]
fn run_manifold(op: &str, a: &(Vec<f64>, Vec<usize>), b: &(Vec<f64>, Vec<usize>)) -> (Vec<f64>, Vec<usize>, Vec<u8>) {
    use manifold_csg::{Manifold, MeshGL64};
    let mk = |m: &(Vec<f64>, Vec<usize>)| {
        let idx: Vec<u64> = m.1.iter().map(|&i| i as u64).collect();
        Manifold::from_meshgl64(&MeshGL64::new(&m.0, 3, &idx).unwrap()).expect("not manifold for Manifold").as_original()
    };
    let (ha, hb) = (mk(a), mk(b));
    let hull_id = ha.original_id() as u32;
    let r = if op == "sub" { ha.difference(&hb) } else { ha.intersection(&hb) };
    let g = r.to_meshgl64();
    let v = g.vert_properties();
    let np = g.num_prop();
    let v: Vec<f64> = v.chunks(np).flat_map(|p| [p[0], p[1], p[2]]).collect();
    let t: Vec<usize> = g.tri_verts().iter().map(|&i| i as usize).collect();
    let (ri, ro) = (g.run_index(), g.run_original_id());
    let mut prov = vec![0u8; t.len() / 3];
    for r in 0..ro.len() {
        for f in (ri[r] as usize / 3)..(ri[r + 1] as usize / 3) { prov[f] = if ro[r] == hull_id { 0 } else { 1 }; }
    }
    (v, t, prov)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (kernel, op, hull, cutter, out) = (&a[1], &a[2], &a[3], &a[4], &a[5]);
    let (h, c) = (load_obj(hull), load_obj(cutter));
    let t0 = Instant::now();
    let (v, t, prov) = match kernel.as_str() {
        "boolmesh" => run_boolmesh(op, &h, &c),
        #[cfg(feature = "manifold")]
        "manifold" => run_manifold(op, &h, &c),
        k => panic!("kernel {k} not built"),
    };
    let ms = t0.elapsed().as_secs_f64() * 1e3;
    write(out, &v, &t, &prov);
    println!("RESULT kernel={kernel} op={op} cutter={cutter} verts={} tris={} cutter_tris={} ms={ms:.1}", v.len() / 3, t.len() / 3, prov.iter().filter(|&&p| p == 1).count());
}
