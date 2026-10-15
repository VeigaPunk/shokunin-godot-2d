# Round 42: restored focus resumes HSlider adjustment

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r42-focus-restore-verifier.json`, `reports/r42-focus-restore-verifier.md`.

| Fresh parsed action + process frame | Focus owner before action | Value / cumulative receipts / Label afterward |
|---|---|---|
| first `ui_right` press | HSlider | 6 / [6] / Value 6 |
| second `ui_right` press | separate in-tree Button | 6 / [6] / Value 6 |
| `ui_right` release | Button | 6 / [6] / Value 6 |
| first `ui_left` press | restored HSlider | 5 / [6,5] / Value 5 |
| first `ui_left` release | HSlider | 5 / [6,5] / Value 5 |
| second `ui_left` press | HSlider | 4 / [6,5,4] / Value 4 |
| second `ui_left` release | HSlider | 4 / [6,5,4] / Value 4 |

Connected HSlider range0..10 step1 initial5 and signal-driven Label. Focus owner verified before each event; state checked afterward; positive exit0 only after all seven. Named verifier 67/67 PASS, all 57 prior tuple rows unchanged, nine opt-ins stable on comparable classifications, separate fault outer PASS with deliberate inner FAILs. Missing restoration fails early edge3 owner check; missing first press fails early edge0 state check. Scout first expected an extra receipt on unchanged second edge, an incorrect scratch expectation corrected before positive run. Owner/state checks do not identify internal consumer of no-change actions. Claim bounded to deliberate synthetic input and frames, not OS repeat, physical keyboard/timing, rendered/pointer behavior, accessibility, production, or generic slider guarantee.
