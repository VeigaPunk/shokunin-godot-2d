# 2D: pixel density does not guarantee display geometry

[PNG Second Edition](https://www.w3.org/TR/2003/REC-PNG-20031110/), November 2003, sections 11.3.5.3 and 13.6, and [Third Edition](https://www.w3.org/TR/2025/REC-png-3-20250624/), June 2025, pHYs and Pixel dimensions, preserve the same distinction.

The chunk records pixels per unit on each axis. An unknown unit communicates aspect ratio, not physical size. With no chunk, square pixels are assumed but physical size remains unspecified. Viewers may ignore nonsquare pixels. Therefore metadata interpretation and observed sprite geometry require separate evidence.

**Proposed practice, unperformed:** Use one original 12-by-8 checkerboard. Prepare metadata-only variants with unknown units and density pairs 3:2 and 300:200, plus a no-chunk control. Keep pixel samples identical and preserve their hash separately from file hashes. Predict intended aspect before opening anything. In one pinned importer, record preserved metadata, decoded dimensions and displayed bounds. Treat equal ratios as equivalent metadata, but document any importer policy rather than declaring ignored metadata a format violation. Cap at three files and thirty minutes. Do not alter production imports.

This is a geometry-metadata exercise, distinct from color precedence and atlas filtering. No images, import tests, training or assimilation were performed.

W3C documents carry conditional reuse terms; original commentary and invented fixture only. No source images or code reproduced.

Destination: VeigaPunk/shokunin-godot-2d, main, considerthese/2026-11-12-png-pixel-aspect.md.
