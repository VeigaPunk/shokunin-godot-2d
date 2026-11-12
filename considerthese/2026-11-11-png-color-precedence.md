# 2D: color chunks are not cumulative corrections

[PNG Second Edition](https://www.w3.org/TR/2003/REC-PNG-20031110/), Recommendation, 10 November 2003, already makes recognized sRGB or iCCP override gAMA. Encoders can supply fallback metadata for less capable decoders.

[Third Edition](https://www.w3.org/TR/2025/REC-png-3-20250624/), Recommendation, 24 June 2025, adds cICP and orders color interpretation: cICP, iCCP, sRGB, then cHRM with gAMA. Use the highest priority understood by the decoder; do not stack their corrections. This extends an existing compatibility strategy, not PNG's first color management.

Curator inference: when a sprite changes appearance after import, record which chunks survived and which interpretation each tool selected before repainting pixels. Equal samples alone do not establish equal displayed color. These specifications do not establish Godot's implementation or display calibration. No importer tested.

Original commentary; no copied examples. W3C copyright 2003 and 1996–2025; conditional Document and Software and Document licenses respectively, with notice obligations for reuse.

Reviewed 2026-11-11. Unassimilated.

Destination: https://github.com/VeigaPunk/shokunin-godot-2d, main, considerthese/2026-11-11-png-color-precedence.md.
