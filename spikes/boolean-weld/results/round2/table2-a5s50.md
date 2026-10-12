| case | variant | applied | tris_band | slivers_band | min_angle_band | p5_angle_band | flipped_hull_band | dev_max_pct | dev_max_h | outside_band_moved | shortest_loop_edge | loop_edges_under_bevel | hull_owned | cutter_owned | split_loop_gap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| port_flank_s16 | naive |  | 157 | 32 | 0.00707 | 1.14 | 0 | 0.0198 | 0.00961 | 0 | 5.29e-05 | 6 |  |  |  |
| port_flank_s16 | owner-weld[a5s50] | 12 | 133 | 5 | 5.09 | 6.68 | 0 | 0.0198 | 0.00961 | 0 | 0.00226 | 0 | 0 | 36 |  |
| port_flank_s48 | naive |  | 339 | 227 | 0.016 | 0.923 | 0 | 0.00233 | 0.00113 | 0 | 5.63e-05 | 52 |  |  |  |
| port_flank_s48 | owner-weld[a5s50] | 10 | 319 | 207 | 0.47 | 1.69 | 0 | 0.00233 | 0.00113 | 0 | 0.000756 | 37 | 0 | 95 |  |
| split_fwd_sub | naive |  | 507 | 97 | 0.0584 | 1.46 | 0 | 0 | 0 | 0 | 0.000263 | 15 |  |  |  |
| split_fwd_sub | owner-weld[a5s50] | 54 | 453 | 71 | 0.0584 | 1.66 | 0 | 0.952 | 0.561 | 0 | 0.000263 | 13 | 124 | 0 |  |
| split_fwd_int | naive |  | 445 | 92 | 0.0555 | 1.52 | 0 | 0 | 0 | 0 | 0.000263 | 14 |  |  |  |
| split_fwd_int | owner-weld[a5s50] | 54 | 391 | 64 | 0.0555 | 1.95 | 0 | 0.952 | 0.561 | 0 | 0.000263 | 12 | 124 | 0 |  |
| split_fwd_sub | seam-gap-naive[a5s50] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| split_fwd_sub | seam-gap-welded[a5s50] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_equalk_s16 | naive |  | 457 | 87 | 1.48e-06 | 1.65 | 0 | 0.0559 | 0.0718 | 0 | 6.99e-05 | 36 |  |  |  |
| probe_equalk_s16 | owner-weld[a5s50] | 66 | 330 | 25 | 0.712 | 5.91 | 0 | 0.208 | 0.279 | 0 | 0.000191 | 4 | 21 | 70 |  |
| probe_equalk_s48 | naive |  | 612 | 167 | 0.0118 | 1.05 | 0 | 0.00638 | 0.0082 | 0 | 6.5e-05 | 81 |  |  |  |
| probe_equalk_s48 | owner-weld[a5s50] | 76 | 486 | 69 | 0.157 | 2.98 | 0 | 0.237 | 0.304 | 0 | 8.49e-05 | 19 | 24 | 112 |  |
| probe_saddle_s16 | naive |  | 209 | 50 | 2.83e-06 | 0.608 | 0 | 0.0937 | 0.0667 | 0 | 1.35e-06 | 19 |  |  |  |
| probe_saddle_s16 | owner-weld[a5s50] | 28 | 156 | 26 | 0.00328 | 0.819 | 0 | 0.0937 | 0.0664 | 0 | 1.35e-06 | 9 | 9 | 48 |  |
| probe_saddle_s48 | naive |  | 365 | 140 | 0.00328 | 0.502 | 0 | 0.0107 | 0.00764 | 0 | 1.35e-06 | 64 |  |  |  |
| probe_saddle_s48 | owner-weld[a5s50] | 31 | 303 | 80 | 0.00328 | 0.845 | 0 | 0.0123 | 0.00872 | 0 | 1.35e-06 | 32 | 18 | 88 |  |
| probe_crease_sub | naive |  | 342 | 44 | 0.0326 | 2.41 | 0 | 0 | 0 | 0 | 1.46e-05 | 12 |  |  |  |
| probe_crease_sub | owner-weld[a5s50] | 33 | 310 | 38 | 0.0326 | 2.58 | 0 | 1.26 | 0.63 | 0 | 1.46e-05 | 10 | 84 | 0 |  |
| probe_crease_int | naive |  | 319 | 47 | 0.0326 | 2.7 | 0 | 0 | 0 | 0 | 1.46e-05 | 11 |  |  |  |
| probe_crease_int | owner-weld[a5s50] | 33 | 281 | 43 | 0.0326 | 3.19 | 0 | 1.26 | 0.63 | 0 | 1.46e-05 | 8 | 84 | 0 |  |
| probe_crease_sub | seam-gap-naive[a5s50] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_crease_sub | seam-gap-welded[a5s50] |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| probe_switch_s48 | naive |  | 488 | 112 | 1.21e-06 | 0.624 | 0 | 0.0128 | 0.00624 | 0 | 6.38e-06 | 31 |  |  |  |
| probe_switch_s48 | owner-weld[a5s50] | 69 | 356 | 54 | 1.21e-06 | 2.52 | 0 | 0.323 | 0.157 | 0 | 4.71e-05 | 16 | 24 | 108 |  |
| probe_crease_cyl_s16 | naive |  | 206 | 27 | 0.208 | 2.6 | 0 | 0.0434 | 0.0146 | 0 | 0.000247 | 4 |  |  |  |
| probe_crease_cyl_s16 | owner-weld[a5s50] | 31 | 147 | 10 | 4.31 | 7.05 | 0 | 0.877 | 0.308 | 0 | 0.00135 | 0 | 6 | 35 |  |
| probe_crease_cyl_s48 | naive |  | 272 | 64 | 0.102 | 1.55 | 0 | 0.00501 | 0.00169 | 0 | 0.000239 | 13 |  |  |  |
| probe_crease_cyl_s48 | owner-weld[a5s50] | 24 | 226 | 27 | 0.791 | 3.48 | 0 | 0.8 | 0.275 | 0 | 0.000239 | 3 | 11 | 62 |  |
