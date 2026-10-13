## Geometry (band = within 2 local edge lengths of the loop)

| case | variant | hull_slivers | hull_worst | hull_p5 | brush_slivers | brush_worst | brush_p5 | hull_flipped | dev_max_pct | seam_off_plane | loop_edges_under_bw | shortest_loop_edge |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| split_fwd_sub | naive | 37 | 0.676 | 3.86 | 60 | 0.0584 | 0.197 | 0 | 0 | 0 | 15 | 0.000263 |
| split_fwd_int | naive | 32 | 0.539 | 4.36 | 60 | 0.0555 | 0.192 | 0 | 1.9e-15 | 0 | 14 | 0.000263 |
| split_fwd_sub | r4-noslide | 23 | 1.37 | 5.72 | 6 | 7.57 | 13.5 | 0 | 0.00692 | 0 | 6 | 0.000295 |
| split_fwd_int | r4-noslide | 16 | 2.51 | 6.69 | 6 | 7.57 | 13.5 | 0 | 0.00692 | 0 | 5 | 0.000786 |
| split_fwd_sub | r4 | 19 | 1.37 | 6.83 | 8 | 6.79 | 12.5 | 0 | 0.00925 | 0 | 4 | 0.000295 |
| split_fwd_int | r4 | 18 | 2.51 | 5.62 | 8 | 6.79 | 12.5 | 0 | 0.00925 | 0 | 5 | 0.000786 |
| probe_crease_sub | naive | 22 | 0.377 | 3.73 | 22 | 0.0326 | 1.19 | 0 | 0 | 0 | 12 | 1.46e-05 |
| probe_crease_int | naive | 25 | 0.0405 | 5.61 | 22 | 0.0326 | 1.64 | 0 | 0 | 0 | 11 | 1.46e-05 |
| probe_crease_sub | r4-noslide | 12 | 2.36 | 6.77 | 0 | 6.85 | 11 | 0 | 0.00404 | 0 | 6 | 0.000127 |
| probe_crease_int | r4-noslide | 10 | 1.4 | 7.14 | 0 | 6.85 | 11 | 0 | 0.00404 | 0 | 5 | 0.000151 |
| probe_crease_sub | r4 | 9 | 2.51 | 7.26 | 0 | 7.42 | 14.3 | 0 | 0.00779 | 0 | 1 | 0.000993 |
| probe_crease_int | r4 | 7 | 2.08 | 7.29 | 0 | 7.42 | 14.3 | 0 | 0.00779 | 0 | 0 | 0.00101 |
| port_flank_s16 | naive | 20 | 0.108 | 2.09 | 12 | 0.00707 | 0.778 | 0 | 0.0198 |  | 6 | 5.29e-05 |
| port_flank_s16 | owner-r4 | 5 | 5.09 | 5.78 | 0 | 6.68 | 6.68 | 0 | 0.0198 |  | 0 | 0.00226 |
| port_flank_s16 | r4-split-brush-edges | 4 | 5.4 | 6.09 | 0 | 19.2 | 21.5 | 0 | 0.0198 |  | 0 | 0.00226 |
| port_flank_s16 | r4 | 4 | 5.4 | 6.09 | 0 | 6.68 | 6.68 | 0 | 0.0198 |  | 0 | 0.00226 |
| probe_switch_s48 | naive | 71 | 1.21e-06 | 1.06 | 41 | 0.0104 | 0.443 | 0 | 0.0128 |  | 31 | 6.38e-06 |
| probe_switch_s48 | owner-r4 | 44 | 1.21e-06 | 2.04 | 11 | 0.0592 | 4.73 | 0 | 0.0196 |  | 16 | 4.71e-05 |
| probe_switch_s48 | r4-split-brush-edges | 23 | 0.144 | 4.42 | 36 | 0.304 | 4.02 | 0 | 0.0196 |  | 28 | 4.71e-05 |
| probe_switch_s48 | r4 | 23 | 0.144 | 4.42 | 16 | 0.304 | 5.24 | 0 | 0.0196 |  | 22 | 4.71e-05 |
| probe_crease_cyl_s16 | naive | 20 | 0.208 | 2.69 | 7 | 0.848 | 2.15 | 0 | 0.0434 |  | 4 | 0.000247 |
| probe_crease_cyl_s16 | owner-r4 | 15 | 2.65 | 5.78 | 2 | 4.31 | 5.38 | 0 | 0.0609 |  | 0 | 0.00104 |
| probe_crease_cyl_s16 | r4-split-brush-edges | 7 | 2.65 | 7.52 | 1 | 4.47 | 10.4 | 0 | 0.0609 |  | 0 | 0.00104 |
| probe_crease_cyl_s16 | r4 | 7 | 2.65 | 7.52 | 2 | 4.47 | 5.81 | 0 | 0.0609 |  | 0 | 0.00104 |
| probe_box_flank | naive | 2 | 0.952 | 8.55 | 1 | 0.285 | 6.49 | 0 | 0 |  | 0 | 0.0025 |
| probe_box_flank | owner-r4 | 1 | 4.92 | 11.9 | 1 | 0.285 | 6.59 | 0 | 0.0108 |  | 0 | 0.0025 |
| probe_box_flank | r4-split-brush-edges | 0 | 6 | 14.6 | 0 | 13.7 | 21.4 | 0 | 0.0108 |  | 0 | 0.0025 |
| probe_box_flank | r4 | 0 | 6 | 14.6 | 0 | 6.92 | 8.98 | 0 | 0.0108 |  | 0 | 0.0025 |
| probe_box_ridge | naive | 19 | 0.715 | 4.9 | 48 | 0.0703 | 0.407 | 0 | 0 |  | 4 | 0.000637 |
| probe_box_ridge | owner-r4 | 19 | 0.715 | 4.9 | 47 | 0.0703 | 0.4 | 0 | 0.00142 |  | 3 | 0.000637 |
| probe_box_ridge | r4-split-brush-edges | 7 | 1.75 | 7.8 | 5 | 4.91 | 18.1 | 0 | 0.00142 |  | 5 | 0.000637 |
| probe_box_ridge | r4 | 7 | 1.75 | 7.8 | 48 | 0.192 | 0.469 | 0 | 0.00142 |  | 3 | 0.000637 |
| add_box_flank | naive | 10 | 0.444 | 4.07 | 4 | 3.01 | 5.86 | 0 | 0 |  | 0 | 0.00114 |
| add_box_flank | owner-r4 | 10 | 0.444 | 4.23 | 2 | 3.01 | 5.74 | 0 | 0.00402 |  | 0 | 0.00114 |
| add_box_flank | r4-split-brush-edges | 4 | 2.37 | 7.32 | 0 | 17.8 | 22.4 | 0 | 0.00402 |  | 0 | 0.00114 |
| add_box_flank | r4 | 4 | 2.37 | 7.32 | 1 | 4.97 | 6.52 | 0 | 0.00402 |  | 0 | 0.00114 |
| add_cyl_flank_s16 | naive | 19 | 0.108 | 1.91 | 16 | 0.15 | 2.23 | 0 | 0.0198 |  | 6 | 5.29e-05 |
| add_cyl_flank_s16 | owner-r4 | 4 | 3.92 | 6.68 | 0 | 7.64 | 8.08 | 0 | 0.0198 |  | 0 | 0.00283 |
| add_cyl_flank_s16 | r4-split-brush-edges | 4 | 5.47 | 6.68 | 0 | 21.1 | 23.4 | 0 | 0.0198 |  | 0 | 0.00282 |
| add_cyl_flank_s16 | r4 | 4 | 5.47 | 6.68 | 0 | 7.8 | 8.16 | 0 | 0.0198 |  | 0 | 0.00283 |

## UV0 carry-through

| case | variant | uv_faces | uv_not_fragments_hull | uv_not_fragments_brush | uv_uv_flipped_hull | uv_uv_flipped_brush | uv_hull_islands | uv_hull_src_islands | uv_hull_uv_area | uv_moved_face_sigma_min | uv_moved_face_sigma_max | uv_moved_face_aniso_min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| split_fwd_sub | naive | 4404 | 0 | 0 | 0 | 122 | 11 | 11 | 0.523 |  |  |  |
| split_fwd_int | naive | 2104 | 0 | 0 | 0 | 0 | 5 | 4 | 0.112 |  |  |  |
| split_fwd_sub | r4-noslide | 4692 | 23 | 0 | 0 | 417 | 11 | 11 | 0.523 | 0.867 | 1.33 | 0.668 |
| split_fwd_int | r4-noslide | 2392 | 39 | 0 | 0 | 0 | 5 | 4 | 0.112 | 0.476 | 1.32 | 0.393 |
| split_fwd_sub | r4 | 4654 | 32 | 0 | 0 | 393 | 11 | 11 | 0.523 | 0.867 | 1.33 | 0.668 |
| split_fwd_int | r4 | 2362 | 46 | 0 | 0 | 0 | 5 | 4 | 0.112 | 0.476 | 1.32 | 0.393 |
| probe_crease_sub | naive | 5890 | 0 | 0 | 0 | 82 | 11 | 11 | 0.589 |  |  |  |
| probe_crease_int | naive | 458 | 0 | 0 | 0 | 0 | 5 | 3 | 0.0459 |  |  |  |
| probe_crease_sub | r4-noslide | 6006 | 41 | 0 | 0 | 203 | 15 | 11 | 0.589 | 0.273 | 2.93 | 0.131 |
| probe_crease_int | r4-noslide | 574 | 57 | 0 | 1 | 0 | 4 | 3 | 0.0459 | 3.34e-05 | 3.25 | 1.08e-05 |
| probe_crease_sub | r4 | 5982 | 43 | 0 | 0 | 184 | 14 | 11 | 0.589 | 0.273 | 2.92 | 0.131 |
| probe_crease_int | r4 | 548 | 63 | 0 | 1 | 0 | 4 | 3 | 0.0459 | 3.34e-05 | 3.25 | 1.08e-05 |
| port_flank_s16 | naive | 6118 | 0 | 0 | 0 | 68 | 11 | 11 | 0.635 |  |  |  |
| port_flank_s16 | owner-r4 | 6094 | 14 | 0 | 0 | 58 | 11 | 11 | 0.635 | 0.623 | 1.14 | 0.602 |
| port_flank_s16 | r4-split-brush-edges | 6246 | 12 | 0 | 0 | 210 | 11 | 11 | 0.635 | 0.67 | 1.09 | 0.633 |
| port_flank_s16 | r4 | 6094 | 12 | 0 | 0 | 58 | 11 | 11 | 0.635 | 0.67 | 1.09 | 0.633 |
| probe_switch_s48 | naive | 6238 | 0 | 0 | 0 | 186 | 11 | 11 | 0.627 |  |  |  |
| probe_switch_s48 | owner-r4 | 6120 | 37 | 6 | 0 | 133 | 11 | 11 | 0.627 | 0.467 | 88 | 0.0112 |
| probe_switch_s48 | r4-split-brush-edges | 6426 | 88 | 60 | 0 | 433 | 11 | 11 | 0.627 | 0.249 | 2.45e+03 | 0.000158 |
| probe_switch_s48 | r4 | 6200 | 88 | 6 | 0 | 213 | 11 | 11 | 0.627 | 0.249 | 88 | 0.0112 |
| probe_crease_cyl_s16 | naive | 6086 | 0 | 0 | 0 | 39 | 11 | 11 | 0.633 |  |  |  |
| probe_crease_cyl_s16 | owner-r4 | 6046 | 24 | 1 | 0 | 23 | 11 | 11 | 0.633 | 0.365 | 109 | 0.00335 |
| probe_crease_cyl_s16 | r4-split-brush-edges | 6056 | 31 | 1 | 0 | 33 | 11 | 11 | 0.633 | 0.365 | 109 | 0.00335 |
| probe_crease_cyl_s16 | r4 | 6046 | 31 | 1 | 0 | 23 | 11 | 11 | 0.633 | 0.365 | 109 | 0.00335 |
| probe_box_flank | naive | 6052 | 0 | 0 | 0 | 22 | 11 | 11 | 0.634 |  |  |  |
| probe_box_flank | owner-r4 | 6048 | 0 | 0 | 0 | 20 | 11 | 11 | 0.634 |  |  |  |
| probe_box_flank | r4-split-brush-edges | 6076 | 5 | 0 | 0 | 48 | 11 | 11 | 0.634 | 0.647 | 1.1 | 0.59 |
| probe_box_flank | r4 | 6048 | 5 | 0 | 0 | 20 | 11 | 11 | 0.634 | 0.647 | 1.1 | 0.59 |
| probe_box_ridge | naive | 6080 | 0 | 0 | 0 | 71 | 11 | 11 | 0.629 |  |  |  |
| probe_box_ridge | owner-r4 | 6078 | 0 | 0 | 0 | 70 | 11 | 11 | 0.629 |  |  |  |
| probe_box_ridge | r4-split-brush-edges | 6342 | 61 | 0 | 0 | 334 | 11 | 11 | 0.629 | 0.249 | 3.86 | 0.102 |
| probe_box_ridge | r4 | 6084 | 61 | 0 | 0 | 76 | 11 | 11 | 0.629 | 0.249 | 3.86 | 0.102 |
| add_box_flank | naive | 6074 | 0 | 0 | 0 | 0 | 11 | 11 | 0.634 |  |  |  |
| add_box_flank | owner-r4 | 6068 | 0 | 0 | 0 | 0 | 11 | 11 | 0.634 |  |  |  |
| add_box_flank | r4-split-brush-edges | 6194 | 0 | 0 | 0 | 0 | 11 | 11 | 0.634 |  |  |  |
| add_box_flank | r4 | 6068 | 0 | 0 | 0 | 0 | 11 | 11 | 0.634 |  |  |  |
| add_cyl_flank_s16 | naive | 6122 | 0 | 0 | 0 | 0 | 11 | 11 | 0.635 |  |  |  |
| add_cyl_flank_s16 | owner-r4 | 6098 | 14 | 0 | 0 | 0 | 11 | 11 | 0.635 | 0.623 | 1.14 | 0.602 |
| add_cyl_flank_s16 | r4-split-brush-edges | 6276 | 11 | 0 | 0 | 0 | 11 | 11 | 0.635 | 0.67 | 1.09 | 0.633 |
| add_cyl_flank_s16 | r4 | 6098 | 11 | 0 | 0 | 0 | 11 | 11 | 0.635 | 0.67 | 1.09 | 0.633 |

## Operations

- split_fwd_sub r4-noslide: {"short_merges": 7, "slide": {}, "flips": 126}
- split_fwd_int r4-noslide: {"short_merges": 7, "slide": {}, "flips": 95}
- split_fwd r4-noslide pieces: {"crack": 0.0, "cap_uv_overlap": 9.485749680535094e-16, "cap_uv_area_sub": 0.03215925424058465, "cap_uv_area_int": 0.03215925424058465}
- split_fwd_sub r4: {"short_merges": 7, "slide": {"applied": 4, "loop_vertices_merged": 10, "skip_overlap": 2, "candidates": 6, "max_move": 0.0008734691178165358, "max_move_over_bw": 0.8734691178165358}, "flips": 118}
- split_fwd_int r4: {"short_merges": 7, "slide": {"applied": 4, "loop_vertices_merged": 10, "skip_overlap": 2, "candidates": 6, "max_move": 0.0008734691178165358, "max_move_over_bw": 0.8734691178165358}, "flips": 88}
- split_fwd r4 pieces: {"crack": 0.0, "cap_uv_overlap": 9.485749680535094e-16, "cap_uv_area_sub": 0.032159390160617016, "cap_uv_area_int": 0.032159390160617016}
- probe_crease_sub r4-noslide: {"short_merges": 5, "slide": {}, "flips": 60}
- probe_crease_int r4-noslide: {"short_merges": 5, "slide": {}, "flips": 78}
- probe_crease r4-noslide pieces: {"crack": 0.0, "cap_uv_overlap": 9.155133597044475e-16, "cap_uv_area_sub": 0.005371482651150788, "cap_uv_area_int": 0.005371482651150788}
- probe_crease_sub r4: {"short_merges": 5, "slide": {"applied": 3, "loop_vertices_merged": 6, "candidates": 3, "max_move": 0.0008445767319343955, "max_move_over_bw": 0.8445767319343954}, "flips": 59}
- probe_crease_int r4: {"short_merges": 5, "slide": {"applied": 3, "loop_vertices_merged": 6, "candidates": 3, "max_move": 0.0008445767319343955, "max_move_over_bw": 0.8445767319343954}, "flips": 77}
- probe_crease r4 pieces: {"crack": 0.0, "cap_uv_overlap": 9.155133597044475e-16, "cap_uv_area_sub": 0.005371328187600327, "cap_uv_area_int": 0.0053713281876003275}
- port_flank_s16 owner-r4: {"weld": {"cand_loop": 10, "applied_loop": 10, "cand_ring": 44, "refused_angle": 5, "refused_flip": 21, "refused_target_gone": 12, "applied_ring": 2, "refused_empty": 4, "corners": 0, "corners_kept_in_place": 0}, "owners": {"hull": 0, "brush": 36}}
- port_flank_s16 r4-split-brush-edges: {"facet_cdt": {"brush_edge_points": 76, "facets": 16, "old_tris": 42, "new_tris": 194, "constraint_edges": 226, "constraint_edges_missing": 0, "steiner": 0}}
- port_flank_s16 r4: {"slide": {"candidates": 0, "max_move": 0.0, "max_move_over_bw": 0.0}, "weld": {"cand_loop": 10, "applied_loop": 10, "cand_ring": 44, "refused_angle": 5, "refused_flip": 21, "refused_target_gone": 12, "applied_ring": 2, "refused_empty": 4, "corners": 0, "corners_kept_in_place": 0}, "flips": 18, "facet_cdt": {"facets": 16, "old_tris": 42, "new_tris": 42, "constraint_edges": 74, "constraint_edges_missing": 0, "steiner": 0}, "corners": 0, "corners_kept": 0}
- probe_switch_s48 owner-r4: {"weld": {"cand_loop": 56, "applied_loop": 52, "refused_angle": 36, "cand_ring": 133, "refused_flip": 37, "refused_link": 2, "refused_target_gone": 46, "applied_ring": 7, "refused_empty": 9, "corners": 4, "corners_kept_in_place": 4}, "owners": {"hull": 24, "brush": 108}}
- probe_switch_s48 r4-split-brush-edges: {"facet_cdt": {"brush_edge_points": 67, "facets": 30, "old_tris": 134, "new_tris": 440, "constraint_edges": 326, "constraint_edges_missing": 0, "steiner": 86}}
- probe_switch_s48 r4: {"slide": {"candidates": 0, "max_move": 0.0, "max_move_over_bw": 0.0}, "weld": {"cand_loop": 56, "applied_loop": 52, "refused_angle": 36, "cand_ring": 133, "refused_flip": 37, "refused_link": 2, "refused_target_gone": 46, "applied_ring": 7, "refused_empty": 9, "corners": 4, "corners_kept_in_place": 4}, "flips": 112, "facet_cdt": {"facets": 30, "old_tris": 134, "new_tris": 214, "constraint_edges": 192, "constraint_edges_missing": 0, "steiner": 40}, "corners": 4, "corners_kept": 4}
- probe_crease_cyl_s16 owner-r4: {"weld": {"cand_loop": 22, "applied_loop": 15, "protected_corner": 20, "refused_angle": 7, "cand_ring": 50, "refused_flip": 5, "refused_not_edge": 3, "refused_target_gone": 9, "applied_ring": 5, "refused_empty": 8, "corners": 2, "corners_kept_in_place": 2}, "owners": {"hull": 6, "brush": 35}}
- probe_crease_cyl_s16 r4-split-brush-edges: {"facet_cdt": {"brush_edge_points": 3, "facets": 8, "old_tris": 24, "new_tris": 34, "constraint_edges": 46, "constraint_edges_missing": 0, "steiner": 2}}
- probe_crease_cyl_s16 r4: {"slide": {"skip_not_consecutive": 2, "candidates": 0, "max_move": 0.0, "max_move_over_bw": 0.0}, "weld": {"cand_loop": 22, "applied_loop": 15, "protected_corner": 20, "refused_angle": 7, "cand_ring": 50, "refused_flip": 5, "refused_not_edge": 3, "refused_target_gone": 9, "applied_ring": 5, "refused_empty": 8, "corners": 2, "corners_kept_in_place": 2}, "flips": 27, "facet_cdt": {"facets": 8, "old_tris": 24, "new_tris": 24, "constraint_edges": 40, "constraint_edges_missing": 0, "steiner": 0}, "corners": 2, "corners_kept": 2}
- probe_box_flank owner-r4: {"weld": {"cand_loop": 6, "protected_corner": 4, "applied_loop": 2, "corners": 4, "corners_kept_in_place": 4}, "owners": {"hull": 16, "brush": 0}}
- probe_box_flank r4-split-brush-edges: {"facet_cdt": {"brush_edge_points": 13, "facets": 5, "old_tris": 20, "new_tris": 48, "constraint_edges": 56, "constraint_edges_missing": 0, "steiner": 1}}
- probe_box_flank r4: {"slide": {"skip_not_consecutive": 2, "candidates": 0, "max_move": 0.0, "max_move_over_bw": 0.0}, "weld": {"cand_loop": 6, "protected_corner": 4, "applied_loop": 2, "corners": 4, "corners_kept_in_place": 4}, "flips": 17, "facet_cdt": {"facets": 4, "old_tris": 18, "new_tris": 18, "constraint_edges": 26, "constraint_edges_missing": 0, "steiner": 0}, "corners": 4, "corners_kept": 4}
- probe_box_ridge owner-r4: {"weld": {"cand_loop": 9, "protected_corner": 6, "applied_loop": 1, "refused_angle": 2, "corners": 6, "corners_kept_in_place": 6}, "owners": {"hull": 69, "brush": 0}}
- probe_box_ridge r4-split-brush-edges: {"facet_cdt": {"brush_edge_points": 59, "facets": 5, "old_tris": 70, "new_tris": 334, "constraint_edges": 198, "constraint_edges_missing": 0, "steiner": 73}}
- probe_box_ridge r4: {"slide": {"skip_not_consecutive": 9, "candidates": 0, "max_move": 0.0, "max_move_over_bw": 0.0}, "weld": {"cand_loop": 9, "protected_corner": 6, "applied_loop": 1, "refused_angle": 2, "corners": 6, "corners_kept_in_place": 6}, "flips": 107, "facet_cdt": {"facets": 5, "old_tris": 70, "new_tris": 76, "constraint_edges": 80, "constraint_edges_missing": 0, "steiner": 3}, "corners": 6, "corners_kept": 6}
- add_box_flank owner-r4: {"weld": {"cand_loop": 8, "protected_corner": 4, "applied_loop": 3, "refused_angle": 1, "corners": 4, "corners_kept_in_place": 4}, "owners": {"hull": 28, "brush": 0}}
- add_box_flank r4-split-brush-edges: {"facet_cdt": {"brush_edge_points": 36, "facets": 5, "old_tris": 31, "new_tris": 157, "constraint_edges": 113, "constraint_edges_missing": 0, "steiner": 27}}
- add_box_flank r4: {"slide": {"skip_not_consecutive": 9, "candidates": 0, "max_move": 0.0, "max_move_over_bw": 0.0}, "weld": {"cand_loop": 8, "protected_corner": 4, "applied_loop": 3, "refused_angle": 1, "corners": 4, "corners_kept_in_place": 4}, "flips": 25, "facet_cdt": {"facets": 4, "old_tris": 29, "new_tris": 29, "constraint_edges": 37, "constraint_edges_missing": 0, "steiner": 0}, "corners": 4, "corners_kept": 4}
- add_cyl_flank_s16 owner-r4: {"weld": {"cand_loop": 10, "applied_loop": 10, "cand_ring": 46, "refused_angle": 8, "refused_flip": 20, "refused_target_gone": 12, "applied_ring": 2, "refused_empty": 4, "corners": 0, "corners_kept_in_place": 0}, "owners": {"hull": 0, "brush": 38}}
- add_cyl_flank_s16 r4-split-brush-edges: {"facet_cdt": {"brush_edge_points": 86, "facets": 17, "old_tris": 60, "new_tris": 238, "constraint_edges": 264, "constraint_edges_missing": 0, "steiner": 3}}
- add_cyl_flank_s16 r4: {"slide": {"candidates": 0, "max_move": 0.0, "max_move_over_bw": 0.0}, "weld": {"cand_loop": 10, "applied_loop": 10, "cand_ring": 46, "refused_angle": 8, "refused_flip": 20, "refused_target_gone": 12, "applied_ring": 2, "refused_empty": 4, "corners": 0, "corners_kept_in_place": 0}, "flips": 18, "facet_cdt": {"facets": 16, "old_tris": 44, "new_tris": 44, "constraint_edges": 76, "constraint_edges_missing": 0, "steiner": 0}, "corners": 0, "corners_kept": 0}
- spade cdt calls: {"calls": 177, "complete": 177, "steiner": 1057}
- uv fixture: {"uv_fixture_max_diff": 2.0000000000575113e-07, "hull_islands": 11, "rho": 0.7804576905498148}

## Bevel strips (bmesh.ops.bevel with the modifier settings; sigma = 3D-to-UV singular values / hull median density)

| mesh | weighted_edges | strips | spans | sigma_min_p5 | sigma_min_median | sigma_max_median | sigma_max_p95 | sigma_max_max | collapsed_lt_0p05 |
|---|---|---|---|---|---|---|---|---|---|
| split_fwd_sub_r4-noslide | 213 | 119 | {"hull": 119, "brush": 0, "both": 0} | 0.556 | 0.601 | 1.01 | 1.33 | 1.45 | 0 |
| split_fwd_int_r4-noslide | 167 | 121 | {"hull": 121, "brush": 0, "both": 0} | 0.664 | 0.805 | 1.03 | 1.59 | 19.8 | 0 |
| split_fwd_sub_r4 | 207 | 113 | {"hull": 113, "brush": 0, "both": 0} | 0.568 | 0.599 | 1 | 1.32 | 1.45 | 0 |
| split_fwd_int_r4 | 161 | 115 | {"hull": 115, "brush": 0, "both": 0} | 0.628 | 0.806 | 1.03 | 1.64 | 19.8 | 0 |
| probe_crease_sub_r4-noslide | 205 | 81 | {"hull": 81, "brush": 0, "both": 0} | 0.269 | 0.604 | 1.04 | 2.94 | 3.42 | 0 |
| probe_crease_int_r4-noslide | 99 | 82 | {"hull": 82, "brush": 0, "both": 0} | 0.283 | 0.648 | 1.01 | 2.53 | 107 | 1 |
| probe_crease_sub_r4 | 202 | 78 | {"hull": 78, "brush": 0, "both": 0} | 0.254 | 0.606 | 1.06 | 2.86 | 96.7 | 0 |
| probe_crease_int_r4 | 96 | 79 | {"hull": 79, "brush": 0, "both": 0} | 0.248 | 0.648 | 1.02 | 2.5 | 156 | 1 |
| probe_box_ridge_naive | 213 | 69 | {"hull": 49, "brush": 20, "both": 0} | 0.336 | 0.555 | 1.13 | 1.95 | 2.1 | 0 |
| probe_box_ridge_r4 | 212 | 68 | {"hull": 68, "brush": 0, "both": 0} | 0.22 | 0.479 | 1.22 | 2.25 | 3.45 | 0 |
| probe_box_ridge_r4-split-brush-edges | 212 | 68 | {"hull": 68, "brush": 0, "both": 0} | 0.253 | 0.517 | 1.18 | 2.17 | 2.72 | 0 |
| probe_box_flank_naive | 160 | 16 | {"hull": 16, "brush": 0, "both": 0} | 0.505 | 0.556 | 1.01 | 1.11 | 1.11 | 0 |
| probe_box_flank_r4 | 158 | 14 | {"hull": 14, "brush": 0, "both": 0} | 0.505 | 0.601 | 0.992 | 1.12 | 1.12 | 0 |
| add_box_flank_naive | 172 | 28 | {"hull": 28, "brush": 0, "both": 0} | 0.427 | 0.565 | 1.01 | 1.17 | 1.2 | 0 |
| add_box_flank_r4 | 169 | 25 | {"hull": 25, "brush": 0, "both": 0} | 0.472 | 0.567 | 0.996 | 1.14 | 1.15 | 0 |
| add_cyl_flank_s16_naive | 182 | 38 | {"hull": 38, "brush": 0, "both": 0} | 0.472 | 0.591 | 0.955 | 1.07 | 1.08 | 0 |
| add_cyl_flank_s16_r4 | 172 | 28 | {"hull": 28, "brush": 0, "both": 0} | 0.519 | 0.608 | 0.95 | 1.05 | 1.05 | 0 |
| port_flank_s16_owner-r4 | 170 | 26 | {"hull": 26, "brush": 0, "both": 0} | 0.473 | 0.577 | 0.951 | 1.05 | 1.07 | 0 |
| port_flank_s16_r4 | 170 | 26 | {"hull": 26, "brush": 0, "both": 0} | 0.482 | 0.59 | 0.951 | 1.05 | 1.07 | 0 |
| probe_switch_s48_owner-r4 | 224 | 80 | {"hull": 49, "brush": 31, "both": 0} | 0 | 0 | 0 | 0 | 6.88e+06 | 80 |
| probe_switch_s48_r4 | 224 | 80 | {"hull": 80, "brush": 0, "both": 0} | 0.253 | 0.456 | 1.05 | 2.41 | 2.85 | 0 |
