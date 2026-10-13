# Round 46: disconnect the value_changed callback after the first edge

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r46-mid-disconnect-verifier.json`, `reports/r46-mid-disconnect-verifier.md`.

In-tree HSlider range0..10 step1 initial5; Button focus transfers at edges1,3,5,7. Nine distinct parsed input events, one process frame each; focus owner checked before and numeric value, cumulative receipts, Label checked after each. Unlike r45 disconnected-at-start, callback is connected on edge0; after verifying numeric6, `[6]`, and `Value 6`, only `value_changed.disconnect(_on_value_changed)` occurs before edge1.

| Edge | Action | Owner | Numeric after | Connected receipts / Label | After-first-disconnect receipts / Label | Start-disconnected receipts / Label |
|---|---|---|---:|---|---|---|
|0|right press|slider|6|[6] / Value 6|[6] / Value 6|[] / Value 5|
|1|right press|Button|6|[6] / Value 6|[6] / Value 6|[] / Value 5|
|2|right release|Button|6|[6] / Value 6|[6] / Value 6|[] / Value 5|
|3|left press|slider|5|[6,5] / Value 5|[6] / Value 6|[] / Value 5|
|4|left release|slider|5|[6,5] / Value 5|[6] / Value 6|[] / Value 5|
|5|left press|Button|5|[6,5] / Value 5|[6] / Value 6|[] / Value 5|
|6|left release|Button|5|[6,5] / Value 5|[6] / Value 6|[] / Value 5|
|7|left press|slider|4|[6,5,4] / Value 4|[6] / Value 6|[] / Value 5|
|8|left release|slider|4|[6,5,4] / Value 4|[6] / Value 6|[] / Value 5|

Dedicated candidate branch emits distinct expected-negative exit2 only after nine owner/state checks. Named non-author full default-path 71/71 PASS, 61 prior result tuples unchanged, nine opt-in classifications stable; separate fault meta PASS has deliberate inner FAILs. Sabotages: skip disconnection fails at edge3 receipt/Label; omit first press or disconnect too early fail edge0. An independent reviewer initial scratch had typed-array failure and was corrected in bounded run; a baseline review overlapped executor edits without pre-change hashes, so is not immutable baseline proof. These remain adverse telemetry. Claims are only for synthetic parsed events/frames, not OS auto-repeat, physical timing/input, rendered/pointer UI, accessibility, production, generic slider, or internal consumer of unchanged edges.
