# Round 45: disconnect only the signal consumer in nine-edge double restoration

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r45-double-restore-disconnect-verifier.json`, `reports/r45-double-restore-disconnect-verifier.md`.

In-tree HSlider range0..10 step1 initial5 with Button focus transfers. Nine distinct parsed action events with one process frame per event. Focus owner verified before each; numeric value, cumulative receipts, and Label checked after each.

| Edge | Action | Owner before | Numeric value after | Connected cumulative receipts / Label | Disconnected cumulative receipts / Label |
|---|---|---|---:|---|---|
| 0 | right press | slider | 6 | [6] / Value 6 | [] / Value 5 |
| 1 | right press | Button | 6 | [6] / Value 6 | [] / Value 5 |
| 2 | right release | Button | 6 | [6] / Value 6 | [] / Value 5 |
| 3 | left press | slider | 5 | [6,5] / Value 5 | [] / Value 5 |
| 4 | left release | slider | 5 | [6,5] / Value 5 | [] / Value 5 |
| 5 | left press | Button | 5 | [6,5] / Value 5 | [] / Value 5 |
| 6 | left release | Button | 5 | [6,5] / Value 5 | [] / Value 5 |
| 7 | left press | slider | 4 | [6,5,4] / Value 4 | [] / Value 5 |
| 8 | left release | slider | 4 | [6,5,4] / Value 4 | [] / Value 5 |

The sole wiring difference is `--disconnect-signal`, omitting `value_changed.connect(_on_value_changed)`. The old r44 branch falsely ended connected PASS/exit0 even on the disconnected arm; it was held and preserved as adverse telemetry. The corrected separate branch checks all nine disconnected states before its distinct expected-negative diagnostic/exit2. An initial scribe scratch expected numeric5 in error; measured numeric6 with receipts[]/Value5 at edge0 supports this claim, and the corrected scratch confirms all nine. The named non-author full replay passed 70/70; 60 old result tuples unchanged and nine opt-in classifications stable. Separate fault meta PASS has deliberate inner FAILs. Reconnect callback and omit-first-press sabotages both fail at edge0, before terminal classification. Neither focus ownership nor unchanged numeric values prove internal event consumption. Bounds: synthetic parsed events+frames, not OS auto-repeat, physical timing, rendered/pointer UI, accessibility, production or generic slider behavior.
