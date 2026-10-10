// Dexter Quiet, run 2, round 3: a compact description instead of a table of offsets.
// Manta: beak +Y, stinger tail -Y, starboard -X. Parts: wing sheet, body, tail.
nose_root = 0.36; nose_k = 1.0;                      // beak starts at nose_root; nose_k stretches it
function ny(y) = y > nose_root ? nose_root + nose_k*(y - nose_root) : y;

// Wing sheet: the planform (top view, +x half, beak tip to wingtip) cut by the trailing scallops,
// lying on one plane per side, z = a + b|x| + c y, of thickness wing_t.
planform = [[0,0.52],[0.011,0.51],[0.033,0.461],[0.062,0.412],[0.146,0.363],[0.184,0.265],[0.238,0.216],
            [0.289,0.167],[0.332,0.118],[0.369,0.069],[0.402,0.02],[0.431,-0.03],[0.46,-0.086],[0.475,-0.135],
            [0.49,-0.19],[0.49,-0.245],[0,-0.245]];
wing_plane = [0.0146, 0.1735, -0.3128]; wing_t = 0.045;
scallop_r = 0.2904; scallop_c = [0.3018, -0.4593];

// Body and tail: elliptical stations [y, z_bottom, z_top, half_width], skinned by pairwise hull.
body = [[-0.185, 0.005, 0.178, 0.12], [-0.08, -0.075, 0.175, 0.17], [0.02, -0.10, 0.158, 0.19], [0.118, -0.127, 0.131, 0.21],
        [0.216, -0.13, 0.101, 0.19], [0.314, -0.165, 0.047, 0.13], [0.40, -0.16, -0.03, 0.065], [0.51, -0.189, -0.176, 0.012]];
tail = [[-0.525, 0.146, 0.191, 0.024], [-0.42, 0.065, 0.187, 0.05], [-0.33, 0.03, 0.184, 0.077], [-0.24, 0.02, 0.18, 0.12]];

sect_n = 3;   // station cross-section is a superellipse of this exponent (2 = ellipse)
function se(t) = sign(t)*pow(abs(t), 2/sect_n);
module station(s) translate([0, ny(s[0]), (s[1] + s[2])/2]) rotate([90, 0, 0]) linear_extrude(0.001, center = true)
    polygon([for (a = [0:10:359]) [s[3]*se(cos(a)), (s[2] - s[1])/2*se(sin(a))]]);
module loft(st) for (i = [0:len(st)-2]) hull() { station(st[i]); station(st[i+1]); }
module wing_side(s) intersection() {             // s = +1 port, -1 starboard
    multmatrix([[1,0,0,0],[0,1,0,0],[s*wing_plane[1], wing_plane[2], 1, wing_plane[0]],[0,0,0,1]])
        translate([s > 0 ? 0 : -1, -1, -wing_t/2]) cube([1, 2, wing_t]);
    linear_extrude(height = 2, center = true) planform2d();
}
module planform2d() difference() {
    polygon(concat([for (p = planform) [p[0], ny(p[1])]], [for (i = [len(planform)-1:-1:0]) [-planform[i][0], ny(planform[i][1])]]));
    for (s = [1, -1]) translate([s*scallop_c[0], scallop_c[1]]) circle(scallop_r, $fn = 96);
}
union() {
    for (s = [1, -1]) wing_side(s);
    loft(body);
    loft(concat(tail, [body[0]]));          // tail runs into the body
    for (s = [1, -1]) pod(s);
    chin_fin();
}
// Under-body pods either side of the keel, and the chin fin under the beak root.
pod_a = [0.13, 0.22, -0.085, 0.03]; pod_b = [0.135, 0.38, -0.10, 0.035];   // [x, y, z, r] at each end
module pod(s) hull() for (p = [pod_a, pod_b]) translate([s*p[0], ny(p[1]), p[2]]) sphere(p[3], $fn = 24);
module chin_fin() hull() for (p = [[0.30, -0.15], [0.363, -0.215], [0.40, -0.16]]) translate([0, ny(p[0]), p[1]]) cube([0.012, 0.01, 0.01], center = true);
