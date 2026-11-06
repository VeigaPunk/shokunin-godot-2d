# Visibility promises need geometry and policy

[Milazzo](https://www.adammil.net/blog/v125_Roguelike_Vision_Algorithms.html),dated2014, separates terrain visibility, seeing creatures and targeting. His comparison weighs reciprocity, room-wall coverage, pillar shadows and diagonal-corner surprises. Symmetrical variants trade wall-occupant behavior against wall coverage; this is practitioner analysis, not a universal ranking.

[Ford](https://www.albertford.com/shadowcasting/) credits Milazzo and offers floor-to-floor symmetry. Floor centers and wall diamonds differ; casting from walls requires modifications. Maintaining expansive walls then produces constant-width pillar shadows. Small gaps can still cause discontinuous visibility. No article publication date is established.

The older comparison helps choose intended behavior; the later contract makes one geometry inspectable. Neither decides whether remembered terrain, decorative light and attack permission should coincide. Asymmetric senses can be deliberate design.

Selected article prose read. Milazzo's2021 comment grants public-domain status to code, not article or figures. Ford's pinned2022 implementation and CC0 attribution remain historical, not newly checked or extended to prose. Original commentary only, no layouts or code reproduced. No engine compatibility, performance, rendering or implementation test.

Optional exercises omitted; originals retained.
