//! Signed distance over the ordered brush stream.
//!
//! The polygon assembler lowers brushes to triangles; this lowers the same
//! brushes to a scalar field: negative inside, positive outside, zero on the
//! surface. Isosurface meshers and GPU field refiners consume it.
//!
//! The fold matches the stream's meaning: starting from empty space, `Add`
//! unions (`min`), `Subtract` removes (`max(d, -b)`), `Intersect` clips
//! (`max`). Unlike the polygon kernel, which currently warns and skips
//! non-convex cutters, the field honours every operation on every primitive.
//!
//! Boxes, oriented boxes and Z cylinders are exact distances. The dome is a
//! half-ellipsoid bound and the floret arm is a max-of-planes bound: both are
//! exact on the surface and never overestimate, which is what sign tests,
//! zero-crossing interpolation and Newton projection need.

use bevy_math::{Vec2, Vec3};

use crate::{Assembler, Brush, BrushOp, Primitive};

impl Primitive {
    /// Signed distance from `p` to this primitive's solid.
    pub fn distance(&self, p: Vec3) -> f32 {
        match *self {
            Self::Box { bounds } => box_distance(p - bounds.center(), bounds.size() * 0.5),
            Self::OrientedBox {
                center,
                size,
                rotation,
            } => box_distance(rotation.inverse() * (p - center), size * 0.5),
            Self::CylinderZ {
                center,
                radius,
                depth,
                ..
            } => {
                let q = p - center;
                let d = Vec2::new(q.truncate().length() - radius, q.z.abs() - depth * 0.5);
                d.max(Vec2::ZERO).length() + d.x.max(d.y).min(0.0)
            }
            Self::DomeCapZ {
                center,
                radius,
                height,
                ..
            } => {
                // Half-ellipsoid with radii (radius, radius, height) above its base plane.
                let ellipsoid = ellipsoid_bound(p - center, Vec3::new(radius, radius, height));
                ellipsoid.max(center.z - p.z)
            }
            Self::FloretArm {
                anchor,
                direction,
                length,
                root_width,
                tip_width,
                thickness,
                tip_lift,
            } => floret_distance(
                p, anchor, direction, length, root_width, tip_width, thickness, tip_lift,
            ),
        }
    }
}

impl Brush {
    /// Signed distance from `p` to this brush's solid, ignoring its operation.
    pub fn distance(&self, p: Vec3) -> f32 {
        self.primitive.distance(p)
    }
}

/// Fold an ordered brush stream into one signed distance at `p`.
pub fn stream_distance<'a>(brushes: impl IntoIterator<Item = &'a Brush>, p: Vec3) -> f32 {
    brushes.into_iter().fold(f32::INFINITY, |d, brush| {
        let b = brush.distance(p);
        match brush.op {
            BrushOp::Add => d.min(b),
            BrushOp::Subtract => d.max(-b),
            BrushOp::Intersect => d.max(b),
        }
    })
}

impl Assembler {
    /// Signed distance from `p` to the solid this assembler's brush stream describes.
    pub fn distance(&self, p: Vec3) -> f32 {
        stream_distance(self.brushes(), p)
    }
}

fn box_distance(q: Vec3, half: Vec3) -> f32 {
    let d = q.abs() - half;
    d.max(Vec3::ZERO).length() + d.max_element().min(0.0)
}

/// Standard ellipsoid distance bound (Quilez): exact on the surface, never an overestimate.
fn ellipsoid_bound(q: Vec3, radii: Vec3) -> f32 {
    let k0 = (q / radii).length();
    let k1 = (q / (radii * radii)).length();
    if k1 == 0.0 {
        return -radii.min_element();
    }
    k0 * (k0 - 1.0) / k1
}

#[allow(clippy::too_many_arguments)]
fn floret_distance(
    p: Vec3,
    anchor: Vec3,
    direction: Vec3,
    length: f32,
    root_width: f32,
    tip_width: f32,
    thickness: f32,
    tip_lift: f32,
) -> f32 {
    // Same frame as the mesh and bounds builders in primitives.rs and brush.rs.
    let forward = direction.normalize_or_zero();
    let forward = if forward.length_squared() == 0.0 { Vec3::X } else { forward };
    let mut side = forward.cross(Vec3::Z).normalize_or_zero();
    if side.length_squared() == 0.0 {
        side = Vec3::Y;
    }
    let tip = anchor + forward * length + Vec3::Z * tip_lift;
    let z = Vec3::Z * (thickness * 0.5);
    let r = side * (root_width * 0.5);
    let t = side * (tip_width * 0.5);
    let pts = [
        anchor - r - z, anchor + r - z, anchor - r + z, anchor + r + z,
        tip - t - z, tip + t - z, tip - t + z, tip + t + z,
    ];
    let centroid = pts.iter().copied().sum::<Vec3>() / 8.0;
    // bottom, top, -side, +side, root, tip
    const FACES: [[usize; 3]; 6] = [[0, 1, 4], [2, 3, 6], [0, 2, 4], [1, 3, 5], [0, 1, 2], [4, 5, 6]];
    FACES
        .iter()
        .map(|&[a, b, c]| {
            let mut n = (pts[b] - pts[a]).cross(pts[c] - pts[a]).normalize_or_zero();
            if n.dot(centroid - pts[a]) > 0.0 {
                n = -n; // face normals point out of the solid
            }
            n.dot(p - pts[a])
        })
        .fold(f32::NEG_INFINITY, f32::max)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Aabb, MaterialId};
    use bevy_math::Quat;

    const EPS: f32 = 1e-5;

    fn unit_box() -> Primitive {
        Primitive::Box { bounds: Aabb::from_center_size(Vec3::ZERO, Vec3::splat(2.0)) }
    }

    #[test]
    fn box_distance_is_exact_inside_on_faces_edges_and_corners() {
        let b = unit_box();
        assert!((b.distance(Vec3::ZERO) + 1.0).abs() < EPS);
        assert!((b.distance(Vec3::new(3.0, 0.0, 0.0)) - 2.0).abs() < EPS);
        assert!((b.distance(Vec3::new(2.0, 2.0, 0.0)) - 2f32.sqrt()).abs() < EPS);
        assert!((b.distance(Vec3::splat(2.0)) - 3f32.sqrt()).abs() < EPS);
        assert!(b.distance(Vec3::new(1.0, 0.3, -0.2)).abs() < EPS);
    }

    #[test]
    fn oriented_box_rotates_the_query_not_the_answer() {
        let rotation = Quat::from_rotation_z(std::f32::consts::FRAC_PI_4);
        let b = Primitive::OrientedBox { center: Vec3::ONE, size: Vec3::splat(2.0), rotation };
        let along_local_x = Vec3::ONE + rotation * Vec3::new(3.0, 0.0, 0.0);
        assert!((b.distance(along_local_x) - 2.0).abs() < EPS);
        // A world-axis point that the unrotated box would contain lies outside this one.
        assert!(b.distance(Vec3::ONE + Vec3::new(0.95, 0.95, 0.0)) > 0.0);
    }

    #[test]
    fn cylinder_distance_is_exact_radially_and_on_caps() {
        let c = Primitive::CylinderZ { center: Vec3::ZERO, radius: 1.0, depth: 2.0, segments: 16 };
        assert!((c.distance(Vec3::new(3.0, 0.0, 0.0)) - 2.0).abs() < EPS);
        assert!((c.distance(Vec3::new(0.0, 0.0, 4.0)) - 3.0).abs() < EPS);
        assert!((c.distance(Vec3::ZERO) + 1.0).abs() < EPS);
    }

    #[test]
    fn dome_is_zero_at_apex_and_rim_and_solid_only_above_its_base() {
        let d = Primitive::DomeCapZ { center: Vec3::ZERO, radius: 2.0, height: 1.0, rings: 4, segments: 8 };
        assert!(d.distance(Vec3::new(0.0, 0.0, 1.0)).abs() < EPS);
        assert!(d.distance(Vec3::new(2.0, 0.0, 0.0)).abs() < EPS);
        assert!(d.distance(Vec3::new(0.0, 0.0, 0.5)) < 0.0);
        assert!(d.distance(Vec3::new(0.0, 0.0, -0.5)) > 0.0);
    }

    #[test]
    fn floret_contains_its_axis_and_excludes_beyond_the_tip() {
        let f = Primitive::FloretArm {
            anchor: Vec3::ZERO, direction: Vec3::X, length: 4.0, root_width: 1.0,
            tip_width: 0.5, thickness: 0.4, tip_lift: 0.0,
        };
        assert!(f.distance(Vec3::new(2.0, 0.0, 0.0)) < 0.0);
        assert!((f.distance(Vec3::new(2.0, 0.0, 0.2))).abs() < EPS); // top face
        assert!(f.distance(Vec3::new(4.5, 0.0, 0.0)) > 0.0);
        assert!(f.distance(Vec3::new(3.9, 0.3, 0.0)) > 0.0); // tapered past the tip half-width
    }

    #[test]
    fn stream_folds_add_subtract_intersect_in_order() {
        let mut asm = Assembler::new();
        assert_eq!(asm.distance(Vec3::ZERO), f32::INFINITY);
        asm.solid_box("slab", Aabb::from_center_size(Vec3::ZERO, Vec3::new(4.0, 4.0, 2.0)), MaterialId(1));
        asm.cut_box("hole", Aabb::from_center_size(Vec3::ZERO, Vec3::splat(1.0)));
        assert!((asm.distance(Vec3::ZERO) - 0.5).abs() < EPS); // inside the hole: 0.5 to its wall
        assert!(asm.distance(Vec3::new(1.5, 0.0, 0.0)) < 0.0);
        asm.add_brush(
            "clip",
            BrushOp::Intersect,
            Primitive::Box { bounds: Aabb::from_center_size(Vec3::new(2.0, 0.0, 0.0), Vec3::splat(4.0)) },
            MaterialId(1),
        );
        assert!(asm.distance(Vec3::new(-1.5, 0.0, 0.0)) > 0.0); // clipped away
        assert!(asm.distance(Vec3::new(1.5, 0.0, 0.0)) < 0.0); // kept
    }

    #[test]
    fn field_agrees_with_the_sample_room_door() {
        let room = Assembler::sample_room_with_door();
        assert!(room.distance(Vec3::new(0.0, 4.0, 2.5)) < 0.0, "wall above the door is solid");
        assert!(room.distance(Vec3::new(0.0, 4.0, 1.0)) > 0.0, "door void is empty");
        assert!(room.distance(Vec3::new(2.0, 4.0, 1.0)) < 0.0, "wall beside the door is solid");
        assert!(room.distance(Vec3::new(0.0, 0.0, -0.1)) < 0.0, "floor is solid");
    }
}
