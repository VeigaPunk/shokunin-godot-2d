# Round 47: reconnect the callback after the first left adjustment

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r47-reconnect-verifier.json`, `reports/r47-reconnect-verifier.md`.

In-tree HSlider range0..10 step1 initial5, Button focus transfers at edges1,3,5,7, nine distinct parsed input events with one process frame each. Focus owner is checked before each edge and numeric value, cumulative callback receipts, and Label after each. Callback connected on edge0; only after verifying 6/[6]/Value6 disconnect it. Edge3 changes numeric to5 while disconnected, still [6]/Value6; reconnect only AFTER checking edge3. Edge7 changes to4 with callback restored.

| Edge | Action | Owner | Value | Always connected receipts/Label | Disconnect after edge0 receipts/Label | Reconnect after edge3 receipts/Label |
|---|---|---|---:|---|---|---|
|0|right press|slider|6|[6]/Value 6|[6]/Value 6|[6]/Value 6|
|1|right press|Button|6|[6]/Value 6|[6]/Value 6|[6]/Value 6|
|2|right release|Button|6|[6]/Value 6|[6]/Value 6|[6]/Value 6|
|3|left press|slider|5|[6,5]/Value 5|[6]/Value 6|[6]/Value 6|
|4|left release|slider|5|[6,5]/Value 5|[6]/Value 6|[6]/Value 6|
|5|left press|Button|5|[6,5]/Value 5|[6]/Value 6|[6]/Value 6|
|6|left release|Button|5|[6,5]/Value 5|[6]/Value 6|[6]/Value 6|
|7|left press|slider|4|[6,5,4]/Value 4|[6]/Value 6|[6,4]/Value 4|
|8|left release|slider|4|[6,5,4]/Value 4|[6]/Value 6|[6,4]/Value 4|

Tracked branch asserts connection-state transitions, all nine owner/state checks, then unique positive exit0. Initial executor edit overwrote r46 branch and row; a tainted 1/1 run while 61 displayed and r46 missing is NOT PASS. Corrected additive author ordinary 61/61; named non-author full 72/72, all 62 prior tuple rows unchanged and nine opt-ins stable classifications, separate fault meta PASS with deliberate inner FAILs. Verifier's initial ineffective sabotage was discarded; corrected skip reconnect, early reconnect, and omitted first press each fail before positive marker. Worker typed-array scratch errors/terminated runs remain adverse telemetry. Claims only for headless synthetic parsed actions+frames, not OS auto-repeat, physical timing/input, rendered/pointer UI, accessibility, production, generic slider or internal consumer of unchanged edges.
