# 2D: calibrated distance is not measured geometry

[SVG1.1](https://www.w3.org/TR/2011/REC-SVG11-20110816/paths.html), August 2011, section 8.4, uses pathLength to calibrate distance-along-path operations. [SVG2 paths](https://www.w3.org/TR/2026/CR-SVG2-20261006/paths.html), October 2026 Candidate Recommendation Snapshot, retains calibration. Its [geometry interface](https://www.w3.org/TR/2026/CR-SVG2-20261006/types.html#InterfaceSVGGeometryElement) explicitly excludes pathLength from getTotalLength and getPointAtLength calculations.

Changing an authored calibration therefore need not change the API's geometric length. This is continuity with an explicit interface boundary, not demonstrated browser interoperability or a completed SVG2 standard.

**Proposed practice, unperformed:** Author one straight 120-unit path twice, with pathLength values 60 and 240, identical endpoints and unitless dash lengths. In an isolated page on one pinned browser, record computed total length, the point at geometric distance thirty, and dash locations separately. Predict unchanged geometry but different calibrated stroke spacing. Add a control that actually moves an endpoint. Report document hashes, browser version, numeric results and any captured pixels; distinguish DOM evidence from rendering evidence. Cap at three paths and thirty minutes. Do not infer Godot importer support from browser behavior.

This extends stroke-closure reading with distance semantics. No page or experiment was run; no training or assimilation.

W3C terms are conditional. Original commentary and invented geometry only; no copied source examples.

Destination: VeigaPunk/shokunin-godot-2d, main, considerthese/2026-11-12-svg-distance-calibration.md.
