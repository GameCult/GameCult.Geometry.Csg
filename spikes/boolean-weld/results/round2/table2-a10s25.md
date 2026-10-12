| case | variant | applied | tris_band | slivers_band | min_angle_band | p5_angle_band | flipped_hull_band | dev_max_pct | dev_max_h | outside_band_moved | shortest_loop_edge | loop_edges_under_bevel | hull_owned | cutter_owned | split_loop_gap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| port_flank_s16 | naive |  | 157 | 32 | 0.00707 | 1.14 | 0 | 0.0198 | 0.00961 | 0 | 5.29e-05 | 6 |  |  |  |
| port_flank_s16 | owner-weld[a10s25] | 11 | 135 | 5 | 5.09 | 6.68 | 0 | 0.0198 | 0.00961 | 0 | 0.00226 | 0 | 0 | 36 |  |
| port_flank_s48 | naive |  | 339 | 227 | 0.016 | 0.923 | 0 | 0.00233 | 0.00113 | 0 | 5.63e-05 | 52 |  |  |  |
| port_flank_s48 | owner-weld[a10s25] | 8 | 323 | 211 | 0.47 | 1.57 | 0 | 0.00233 | 0.00113 | 0 | 0.000224 | 40 | 0 | 95 |  |
| split_fwd_sub | naive |  | 507 | 97 | 0.0584 | 1.46 | 0 | 0 | 0 | 0 | 0.000263 | 15 |  |  |  |
| split_fwd_sub | owner-weld[a10s25] | 16 | 492 | 85 | 0.0584 | 1.55 | 0 | 0.396 | 0.234 | 0 | 0.000263 | 13 | 124 | 0 |  |
| split_fwd_int | naive |  | 445 | 92 | 0.0555 | 1.52 | 0 | 0 | 0 | 0 | 0.000263 | 14 |  |  |  |
| split_fwd_int | owner-weld[a10s25] | 16 | 431 | 82 | 0.0555 | 1.77 | 0 | 0.396 | 0.234 | 0 | 0.000263 | 12 | 124 | 0 |  |
| split_fwd_sub | seam-gap-naive[a10s25] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| split_fwd_sub | seam-gap-welded[a10s25] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_equalk_s16 | naive |  | 457 | 87 | 1.48e-06 | 1.65 | 0 | 0.0559 | 0.0718 | 0 | 6.99e-05 | 36 |  |  |  |
| probe_equalk_s16 | owner-weld[a10s25] | 42 | 362 | 35 | 1.71e-06 | 4.03 | 0 | 0.0976 | 0.131 | 0 | 6.99e-05 | 14 | 21 | 70 |  |
| probe_equalk_s48 | naive |  | 612 | 167 | 0.0118 | 1.05 | 0 | 0.00638 | 0.0082 | 0 | 6.5e-05 | 81 |  |  |  |
| probe_equalk_s48 | owner-weld[a10s25] | 56 | 512 | 74 | 0.157 | 2.98 | 0 | 0.0976 | 0.125 | 0 | 8.49e-05 | 25 | 24 | 112 |  |
| probe_saddle_s16 | naive |  | 209 | 50 | 2.83e-06 | 0.608 | 0 | 0.0937 | 0.0667 | 0 | 1.35e-06 | 19 |  |  |  |
| probe_saddle_s16 | owner-weld[a10s25] | 24 | 163 | 25 | 0.00328 | 0.875 | 1 | 0.0937 | 0.0667 | 0 | 1.35e-06 | 9 | 9 | 48 |  |
| probe_saddle_s48 | naive |  | 365 | 140 | 0.00328 | 0.502 | 0 | 0.0107 | 0.00764 | 0 | 1.35e-06 | 64 |  |  |  |
| probe_saddle_s48 | owner-weld[a10s25] | 28 | 309 | 83 | 0.00328 | 0.846 | 0 | 0.0123 | 0.00876 | 0 | 1.35e-06 | 34 | 18 | 88 |  |
| probe_crease_sub | naive |  | 342 | 44 | 0.0326 | 2.41 | 0 | 0 | 0 | 0 | 1.46e-05 | 12 |  |  |  |
| probe_crease_sub | owner-weld[a10s25] | 9 | 336 | 40 | 0.0326 | 2.67 | 0 | 0.528 | 0.263 | 0 | 1.46e-05 | 10 | 84 | 0 |  |
| probe_crease_int | naive |  | 319 | 47 | 0.0326 | 2.7 | 0 | 0 | 0 | 0 | 1.46e-05 | 11 |  |  |  |
| probe_crease_int | owner-weld[a10s25] | 9 | 312 | 46 | 0.0326 | 3.45 | 0 | 0.528 | 0.263 | 0 | 1.46e-05 | 8 | 84 | 0 |  |
| probe_crease_sub | seam-gap-naive[a10s25] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_crease_sub | seam-gap-welded[a10s25] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_switch_s48 | naive |  | 488 | 112 | 1.21e-06 | 0.624 | 0 | 0.0128 | 0.00624 | 0 | 6.38e-06 | 31 |  |  |  |
| probe_switch_s48 | owner-weld[a10s25] | 56 | 378 | 54 | 1.21e-06 | 2.01 | 0 | 0.323 | 0.157 | 0 | 4.71e-05 | 18 | 24 | 108 |  |
| probe_crease_cyl_s16 | naive |  | 206 | 27 | 0.208 | 2.6 | 0 | 0.0434 | 0.0146 | 0 | 0.000247 | 4 |  |  |  |
| probe_crease_cyl_s16 | owner-weld[a10s25] | 19 | 157 | 8 | 3.91 | 8.28 | 0 | 0.0609 | 0.0221 | 0 | 0.00135 | 0 | 6 | 35 |  |
| probe_crease_cyl_s48 | naive |  | 272 | 64 | 0.102 | 1.55 | 0 | 0.00501 | 0.00169 | 0 | 0.000239 | 13 |  |  |  |
| probe_crease_cyl_s48 | owner-weld[a10s25] | 22 | 223 | 27 | 0.791 | 3.46 | 0 | 0.0286 | 0.01 | 0 | 0.000239 | 3 | 11 | 62 |  |
