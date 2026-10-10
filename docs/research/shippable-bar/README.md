# What a finished hull part is (operator, 2026-10-10)

The bar the brush-tree output is judged against. Operator's words:

> A part is done for me when its topo flow is reasonably clean and unbroken, and I try to unwrap such
> that parts of the same object stay together with minimal distortion. Bevels are used to sharpen edges
> (sharp shading requires duplicating geo anyway, while a single faced bevel shades flawlessly with
> face-weighted normals. See this test render showing a simple bevel, face weighted simple bevel, and
> expensive perfect bevel next to each other, and a little test box showing off that and decals for that
> Star Citizen effect)

`operator-bevel-test.webp`, left to right: single-segment bevel with plain normals; the same bevel with
face-weighted normals (the target look); a multi-segment "perfect" bevel (too expensive); a test box
with face-weighted bevels and decals (decals are the separate panel-decals campaign).

Measurable reading of the bar:
- Topology: clean, unbroken edge flow (quad-dominant loops, few poles, no triangle fans or slivers).
- UVs: islands follow the object's parts, kept together, with minimal stretch.
- Edges: one-segment bevels on hard edges, shaded with face-weighted normals; no duplicated split
  geometry for sharpness, no multi-segment bevels.
