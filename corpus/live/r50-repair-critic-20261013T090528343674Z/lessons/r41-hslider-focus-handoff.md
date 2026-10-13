# Round 41: HSlider focus handoff after observed adjustment

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r41-focus-handoff-verifier.json`, `reports/r41-focus-handoff-verifier.md`.

| Synthetic action + process frame | Focus owner before action | Connected HSlider value/receipts/Label afterward |
|---|---|---|
| first fresh `ui_right` press | HSlider | 6 / [6] / Value 6 |
| second `ui_right` press | separate in-tree Button | 6 / [6] / Value 6 |
| `ui_right` release | Button | 6 / [6] / Value 6 |
| first `ui_left` press/release | Button | 6 / [6] / Value 6 at both edges |
| second `ui_left` press/release | Button | 6 / [6] / Value 6 at both edges |

Initial HSlider range0..10 step1 value5, signal connected to Label. Transfer GUI focus to a separate Button before the second event; assert slider unfocused and Button owner before each subsequent event. Dedicated terminal expected-negative exit2 only after seven checks. Named verifier 66/66 PASS, all 56 prior tuple rows unchanged, nine opt-ins stable on comparable classifications, separate fault outer PASS with deliberate inner FAILs. Missing focus transfer fails early owner check, omitting first press fails early state check; neither classified as terminal negative. Hung scratch runs and timed battery attempt remain adverse telemetry; later bounded replay supports admission. Post-handoff invariant does not independently prove each remaining action was consumed; source dispatch loop was reviewed. Scope only deliberate synthetic parsed actions+frames, not OS auto-repeat, physical timing, rendered/pointer interaction, accessibility, production, generic slider behavior or arbitrary focus target.
