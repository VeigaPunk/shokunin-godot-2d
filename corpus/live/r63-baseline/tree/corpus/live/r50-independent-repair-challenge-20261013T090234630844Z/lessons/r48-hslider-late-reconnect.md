# Round 48: reconnect only after the final value-changing edge

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r48-late-reconnect-verifier.json`, `reports/r48-late-reconnect-verifier.md`.

In-tree HSlider range0..10 step1 initial5; Button focus transfers at edges1,3,5,7. Nine distinct parsed input events with one process frame each. Focus owner checked before each and numeric value, cumulative receipts, Label checked afterward. Callback connected initially; after checking edge0 numeric6/[6]/Value6 disconnect. Remain disconnected through edge3 numeric5 and edge7 numeric4; only AFTER checking edge7 4/[6]/Value6 reconnect. Edge8 release occurs with callback connected but retains numeric4/[6]/Value6.

| Edge | Action | Owner | Value | Always connected receipts/Label | Reconnect after edge3 receipts/Label | Reconnect after edge7 receipts/Label |
|---|---|---|---:|---|---|---|
|0|right press|slider|6|[6]/Value 6|[6]/Value 6|[6]/Value 6|
|1|right press|Button|6|[6]/Value 6|[6]/Value 6|[6]/Value 6|
|2|right release|Button|6|[6]/Value 6|[6]/Value 6|[6]/Value 6|
|3|left press|slider|5|[6,5]/Value 5|[6]/Value 6|[6]/Value 6|
|4|left release|slider|5|[6,5]/Value 5|[6]/Value 6|[6]/Value 6|
|5|left press|Button|5|[6,5]/Value 5|[6]/Value 6|[6]/Value 6|
|6|left release|Button|5|[6,5]/Value 5|[6]/Value 6|[6]/Value 6|
|7|left press|slider|4|[6,5,4]/Value 4|[6,4]/Value 4|[6]/Value 6|
|8|left release|slider|4|[6,5,4]/Value 4|[6,4]/Value 4|[6]/Value 6|

Tracked branch verifies connected→disconnected after edge0 and disconnected→connected after edge7, then a distinct expected-negative terminal exit2 only after nine checks. First tracked executor edit malformed; reverted to exact HEAD before additive branch. First ordinary run rejected matching diagnostic without an exact ERROR allowance; corrected author ordinary62/62. Critic scratch yielded no result; baseline reviewer corrected an incorrect interpretation of deliberate exit2; scribe corrected an edge8 connection expectation. Named non-author full 73/73 PASS with 63 prior result tuples unchanged and nine opt-in classifications stable; separate fault meta PASS has deliberate inner FAILs. Sabotages early reconnect, omitted reconnect, and omitted first press fail before terminal marker. Evidence is bounded to synthetic parsed input+frames, not OS auto-repeat, physical timing/input, rendered/pointer UI, accessibility, production, generic signal replay, or internal consumption of unchanged edges.
