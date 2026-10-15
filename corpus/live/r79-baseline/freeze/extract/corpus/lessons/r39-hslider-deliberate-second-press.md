# Round 39: deliberate second HSlider right-press event

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r39-repeat-verifier.json`, `reports/r39-repeat-verifier.md`.

| Event + one process frame | Focused connected value/receipts/Label | Focused disconnected value/receipts/Label |
|---|---|---|
| first fresh ui_right press | 6 / [6] / Value 6 | 6 / [] / Value 5 |
| second fresh ui_right press, no intervening release | 7 / [6,7] / Value 7 | 7 / [] / Value 5 |
| ui_right release | 7 / [6,7] / Value 7 | 7 / [] / Value 5 |
| first ui_left press/release | 6 / [6,7,6] / Value 6 (both edges) | 6 / [] / Value 5 |
| second ui_left press/release | 5 / [6,7,6,5] / Value 5 (both edges) | 5 / [] / Value 5 |

Same in-tree focused slider, bounds 0..10 step1 initial5 and same event sequence; disconnected omits only signal consumer. Its intended missing-signal exit2 occurs after all seven edge checks. Author initial 63/64 failed only because expected-negative classifier omitted exact terminal error, then corrected. Named verifier 64/64 PASS, prior 62 tuples unchanged, fault outer PASS with deliberate inner FAILs. First scratch sabotage mistakenly removed an event and loop entry and failed at release; corrected scratch keeps seven checks, omits only second dispatch and fails at second right-press assertion. This is deliberate distinct synthetic event history, not OS auto-repeat, physical keyboard/timing, rendered/pointer input, accessibility, production or generic slider behavior.
