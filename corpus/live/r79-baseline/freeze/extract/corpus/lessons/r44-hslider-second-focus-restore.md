# Round 44: second focus restoration resumes HSlider adjustment

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r44-second-restore-verifier.json`, `reports/r44-second-restore-verifier.md`.

| Fresh parsed action + process frame | Focus owner before | Value / cumulative receipts / Label afterward |
|---|---|---|
| first `ui_right` press | HSlider | 6 / [6] / Value 6 |
| second `ui_right` press/release | Button | 6 / [6] / Value 6 at both |
| first `ui_left` press/release | HSlider restored | 5 / [6,5] / Value 5 at both |
| second `ui_left` press/release | Button again | 5 / [6,5] / Value 5 at both |
| third `ui_left` press/release | HSlider restored again | 4 / [6,5,4] / Value 4 at both |

Connected HSlider range0..10 step1 initial5, signal-driven Label. Nine distinct parsed events, one process frame each; owner verified before each, state after each. Positive exit0 only after nine. First executor edit overwrote r43 branch/runner row and was caught before admission; interrupted run had no verdict. Corrected additive implementation preserves r43 exact negative. Named verifier full 69/69 PASS, prior 59 tuple rows unchanged, nine opt-ins stable comparable classifications; separate fault outer PASS with deliberate inner FAILs. Missing second restoration fails edge7 owner check; missing first press fails edge0 state check. Owner/state checks do not identify internal consumer of no-change events. Only deliberate synthetic input+frames, not OS repeat, physical timing, rendered/pointer UI, accessibility, production or generic slider guarantee.
