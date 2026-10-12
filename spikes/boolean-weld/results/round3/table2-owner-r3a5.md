| case | variant | applied | tris_band | slivers_band | min_angle_band | p5_angle_band | flipped_hull_band | dev_max_pct | dev_max_h | outside_band_moved | shortest_loop_edge | loop_edges_under_bevel | hull_owned | cutter_owned | split_loop_gap | hull_vertex_surface_dev_h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| port_flank_s16 | naive |  | 157 | 32 | 0.00707 | 1.14 | 0 | 0.0198 | 0.00961 | 0 | 5.29e-05 | 6 |  |  |  |  |
| port_flank_s16 | owner-weld[r3a5] | 12 | 133 | 5 | 5.09 | 6.68 | 0 | 0.0198 | 0.00961 | 0 | 0.00226 | 0 | 0 | 36 |  | 0.0175 |
| split_fwd_sub | naive |  | 507 | 97 | 0.0584 | 1.46 | 0 | 0 | 0 | 0 | 0.000263 | 15 |  |  |  |  |
| split_fwd_sub | owner-weld[r3a5] | 0 | 507 | 97 | 0.0584 | 1.46 | 0 | 0 | 0 | 0 | 0.000263 | 15 | 124 | 0 |  | 0 |
| split_fwd_int | naive |  | 445 | 92 | 0.0555 | 1.52 | 0 | 0 | 0 | 0 | 0.000263 | 14 |  |  |  |  |
| split_fwd_int | owner-weld[r3a5] | 0 | 445 | 92 | 0.0555 | 1.52 | 0 | 0 | 0 | 0 | 0.000263 | 14 | 124 | 0 |  | 0 |
| split_fwd_sub | seam-gap-naive[r3a5] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |  |
| split_fwd_sub | seam-gap-welded[r3a5] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |  |
| probe_crease_sub | naive |  | 342 | 44 | 0.0326 | 2.41 | 0 | 0 | 0 | 0 | 1.46e-05 | 12 |  |  |  |  |
| probe_crease_sub | owner-weld[r3a5] | 0 | 342 | 44 | 0.0326 | 2.41 | 0 | 0 | 0 | 0 | 1.46e-05 | 12 | 84 | 0 |  | 0 |
| probe_crease_int | naive |  | 319 | 47 | 0.0326 | 2.7 | 0 | 0 | 0 | 0 | 1.46e-05 | 11 |  |  |  |  |
| probe_crease_int | owner-weld[r3a5] | 0 | 319 | 47 | 0.0326 | 2.7 | 0 | 0 | 0 | 0 | 1.46e-05 | 11 | 84 | 0 |  | 0 |
| probe_crease_sub | seam-gap-naive[r3a5] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |  |
| probe_crease_sub | seam-gap-welded[r3a5] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |  |
| probe_switch_s48 | naive |  | 488 | 112 | 1.21e-06 | 0.624 | 0 | 0.0128 | 0.00624 | 0 | 6.38e-06 | 31 |  |  |  |  |
| probe_switch_s48 | owner-weld[r3a5] | 65 | 364 | 53 | 1.21e-06 | 2.65 | 0 | 0.323 | 0.157 | 0 | 4.71e-05 | 16 | 24 | 108 |  | 0.021 |
| probe_crease_cyl_s16 | naive |  | 206 | 27 | 0.208 | 2.6 | 0 | 0.0434 | 0.0146 | 0 | 0.000247 | 4 |  |  |  |  |
| probe_crease_cyl_s16 | owner-weld[r3a5] | 27 | 133 | 10 | 4.31 | 6.83 | 0 | 0.0609 | 0.0229 | 0 | 0.00135 | 0 | 6 | 35 |  | 0.00665 |
| probe_box_flank | naive |  | 105 | 3 | 0.285 | 6.62 | 0 | 0 | 0 | 0 | 0.0025 | 0 |  |  |  |  |
| probe_box_flank | owner-weld[r3a5] | 2 | 103 | 2 | 0.285 | 9.61 | 0 | 0.0108 | 0.00534 | 0 | 0.0025 | 0 | 16 | 0 |  | 0 |
| probe_box_ridge | naive |  | 314 | 67 | 0.0703 | 1.36 | 0 | 0 | 0 | 0 | 0.000637 | 4 |  |  |  |  |
| probe_box_ridge | owner-weld[r3a5] | 1 | 312 | 66 | 0.0703 | 1.41 | 0 | 0.00142 | 0.000687 | 0 | 0.000637 | 3 | 69 | 0 |  | 0 |
