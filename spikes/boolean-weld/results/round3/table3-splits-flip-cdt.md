| case | variant | flips_applied | hull_band_tris | hull_slivers | hull_min_angle | hull_p5 | cap_tris | cap_slivers | cap_min_angle | flipped_hull | seam_off_plane_max | loop_to_naive_max | loop_edges_under_bevel | crack |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| split_fwd_sub | naive | 0 | 410 | 37 | 0.676 | 3.86 | 122 | 85 | 0.0584 | 0 | 3.05e-16 | 0 | 15 |  |
| split_fwd_int | naive | 0 | 348 | 32 | 0.539 | 4.36 | 122 | 85 | 0.0555 | 0 | 3.05e-16 | 0 | 14 |  |
| split_fwd | naive seam crack |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| split_fwd_sub | flip+cdt | 138 | 410 | 28 | 0.676 | 4.69 | 122 | 80 | 0.122 | 0 | 3.05e-16 | 0 | 15 |  |
| split_fwd_int | flip+cdt | 99 | 346 | 18 | 0.539 | 5.97 | 122 | 80 | 0.122 | 0 | 3.05e-16 | 0 | 14 |  |
| split_fwd | flip+cdt seam crack |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| split_fwd_sub | flip+cdt-q | 138 | 410 | 28 | 0.676 | 4.69 | 332 | 0 | 6.76 | 0 | 3.05e-16 | 0 | 23 |  |
| split_fwd_int | flip+cdt-q | 99 | 346 | 18 | 0.539 | 5.97 | 332 | 0 | 6.76 | 0 | 3.05e-16 | 0 | 22 |  |
| split_fwd | flip+cdt-q seam crack |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_crease_sub | naive | 0 | 260 | 22 | 0.377 | 3.73 | 82 | 22 | 0.0326 | 0 | 7.22e-16 | 0 | 12 |  |
| probe_crease_int | naive | 0 | 237 | 25 | 0.0405 | 5.61 | 82 | 22 | 0.0326 | 0 | 7.22e-16 | 0 | 11 |  |
| probe_crease | naive seam crack |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_crease_sub | flip+cdt | 67 | 260 | 19 | 0.377 | 4.25 | 82 | 21 | 0.575 | 0 | 7.22e-16 | 0 | 13 |  |
| probe_crease_int | flip+cdt | 79 | 238 | 11 | 0.0405 | 7.1 | 82 | 21 | 0.575 | 0 | 7.22e-16 | 0 | 12 |  |
| probe_crease | flip+cdt seam crack |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_crease_sub | flip+cdt-q | 67 | 260 | 19 | 0.377 | 4.25 | 162 | 4 | 0.714 | 0 | 7.22e-16 | 0 | 18 |  |
| probe_crease_int | flip+cdt-q | 79 | 238 | 11 | 0.0405 | 7.1 | 162 | 4 | 0.714 | 0 | 7.22e-16 | 0 | 17 |  |
| probe_crease | flip+cdt-q seam crack |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
