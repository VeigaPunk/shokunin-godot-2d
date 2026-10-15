# Round 36: focused HSlider numeric input

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`; independent `corpus/lessons/r36-slider-verifier.json`, `reports/r36-slider-verifier.md`.

| Phase | Connected HSlider (0..10, step 1, initial 5) | Disconnected consumer, same actions |
|---|---|---|
| Setup | focus owner slider; value 5, receipts [], Label Value 5 | same |
| `ui_right` pressed/released | value 6, receipts [6], Label Value 6 | value 6, receipts [], Label Value 5 |
| `ui_left` pressed/released | value 5, receipts [6,5], Label Value 5; exit0 | value 5, receipts [], Label Value 5; intended missing-signal exit2 |

Fresh `InputEventAction` press and release via `Input.parse_input_event`, process frame between edges; no programmatic value assignment as stimulus or manual signal emission. `Input.action_press` alone did not route in scratch; mere receipts do not prove input because programmatic assignment can also emit `value_changed`. Focus owner is checked before each action and a scratch no-input sabotage fails both arms. Earlier executor undeclared `viewport` failure remains adverse scratch telemetry. Named non-author full replay 61/61 PASS (50 ordinary +2 mutants +9 opt-ins), all 59 previous result triples unchanged. Separate fault-injection outer PASS retains deliberate inner FAIL. This is synthetic headless input coverage, not rendered/pointer UI, physical keyboard/timing, accessibility, production or general HSlider reliability.
