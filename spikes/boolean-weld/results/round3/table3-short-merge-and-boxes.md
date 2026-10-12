| case | variant | merges | seam_chord_dev_pct | flips_applied | hull_band_tris | hull_slivers | hull_min_angle | hull_p5 | cap_tris | cap_slivers | cap_min_angle | flipped_hull | seam_off_plane_max | loop_to_naive_max | loop_edges_under_bevel | crack |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| split_fwd_sub | naive |  |  | 0 | 410 | 37 | 0.676 | 3.86 | 122 | 85 | 0.0584 | 0 | 3.05e-16 | 0 | 15 |  |
| split_fwd_int | naive |  |  | 0 | 348 | 32 | 0.539 | 4.36 | 122 | 85 | 0.0555 | 0 | 3.05e-16 | 0 | 14 |  |
| split_fwd | naive seam crack |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| split_fwd_sub | short+flip+cdt-q | 3 | 0.00692 | 138 | 407 | 26 | 0.676 | 5.3 | 313 | 1 | 5.5 | 0 | 3.05e-16 | 0 | 16 |  |
| split_fwd_int | short+flip+cdt-q | 3 | 0.00692 | 99 | 343 | 17 | 0.539 | 6.69 | 313 | 1 | 5.5 | 0 | 3.05e-16 | 0 | 16 |  |
| split_fwd | short+flip+cdt-q seam crack |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_crease_sub | naive |  |  | 0 | 260 | 22 | 0.377 | 3.73 | 82 | 22 | 0.0326 | 0 | 7.22e-16 | 0 | 12 |  |
| probe_crease_int | naive |  |  | 0 | 237 | 25 | 0.0405 | 5.61 | 82 | 22 | 0.0326 | 0 | 7.22e-16 | 0 | 11 |  |
| probe_crease | naive seam crack |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_crease_sub | short+flip+cdt-q | 5 | 0.00404 | 65 | 255 | 12 | 2.41 | 6.64 | 147 | 3 | 0.714 | 0 | 7.22e-16 | 0 | 6 |  |
| probe_crease_int | short+flip+cdt-q | 5 | 0.00404 | 79 | 234 | 10 | 0.0405 | 7.14 | 147 | 3 | 0.714 | 0 | 7.22e-16 | 0 | 5 |  |
| probe_crease | short+flip+cdt-q seam crack |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_box_flank | naive |  |  | 0 | 83 | 2 | 0.952 | 8.55 | 22 | 1 | 0.285 | 0 |  | 0 | 0 |  |
| probe_box_flank | flip |  |  | 24 | 84 | 0 | 6 | 12.1 | 22 | 1 | 0.285 | 0 |  | 0 | 0 |  |
| probe_box_ridge | naive |  |  | 0 | 243 | 19 | 0.715 | 4.9 | 71 | 48 | 0.0703 | 0 |  | 0 | 4 |  |
| probe_box_ridge | flip |  |  | 118 | 243 | 7 | 1.75 | 7.24 | 71 | 48 | 0.0703 | 0 |  | 0 | 4 |  |
