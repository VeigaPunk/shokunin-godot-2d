# Round 38: HSlider press/release edge attribution

Sources: `corpus/fixtures/slider_adjust.gd`, unchanged `run_battery.py`, named non-author `corpus/lessons/r38-edge-verifier.json`, `reports/r38-edge-verifier.md`.

| Event followed by one process frame | Focused connected value/receipts/Label | Focused disconnected | No-focus connected |
|---|---|---|---|
| ui_right press | 6 / [6] / Value 6 | 6 / [] / Value 5 | 5 / [] / Value 5 |
| ui_right release | 6 / [6] / Value 6 | 6 / [] / Value 5 | 5 / [] / Value 5 |
| ui_left press | 5 / [6,5] / Value 5 | 5 / [] / Value 5 | 5 / [] / Value 5 |
| ui_left release | 5 / [6,5] / Value 5 | 5 / [] / Value 5 | 5 / [] / Value 5 |

Existing disconnected and no-focus negatives exit2 only after all four edges. `Input.parse_input_event` itself has not yet changed state when called synchronously; observation is after yielding one frame. A separate extra repeated `pressed=true` event advances 6→7, so no auto-repeat immunity claim. First executor implementation failed all three slider cases by assigning an untyped conditional Array to `Array[float]` (then 8-second timeouts); corrected typed append replay and named verification pass. Named non-author full 62/62 PASS, all prior r37 62 result triples unchanged, runner unchanged. Scratch omitting ui_right press fails the specific new press assertion. Scope is synthetic one-event-plus-frame edge behavior, not physical key timing/repeat, rendered/pointer input, accessibility, production or generic Range behavior.
