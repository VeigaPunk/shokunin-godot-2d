# Round 37: HSlider focus-absence control

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r37-focus-verifier.json`, `reports/r37-focus-verifier.md`.

| Same parsed action, callback, Label | Focused HSlider | `--no-focus` HSlider |
|---|---|---|
| Setup | focus owner slider; value5 receipts[] Label Value5 | focus owner not slider; value5 receipts[] Label Value5 |
| ui_right press/release | value6 receipts[6] Label Value6 | value5 receipts[] Label Value5 |
| ui_left press/release | value5 receipts[6,5] Label Value5; exit0 | value5 receipts[] Label Value5; intended diagnostic exit2 after both actions |

The existing disconnected-signal arm retains focus, changes 5→6→5, but receives no callback; it is distinct from focus absence. Fresh `InputEventAction` via `Input.parse_input_event`, process frames between edges, no manual signal or programmatic value assignment as stimulus. No-focus removes only `grab_focus`; a scratch forced-grab sabotage fails no-focus setup before actions, not the expected post-action negative. Executor's earlier observation-line signature/classifier mismatch yielded 50/51 and remains failed scratch telemetry. Named verifier full replay 62/62 PASS (51 ordinary +2 mutants +9 opt-ins), all 61 prior result triples unchanged; separate fault-injection outer PASS with deliberate inner adverse FAIL. This is headless synthetic GUI focus routing, not rendered/pointer input, physical keyboard/timing, OS window focus, accessibility, production or generic slider reliability.
