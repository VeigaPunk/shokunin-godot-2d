# Round 43: second focus loss blocks final HSlider adjustment

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r43-second-loss-verifier.json`, `reports/r43-second-loss-verifier.md`.

| Fresh parsed action + process frame | Focus owner before | Second-loss value / cumulative receipts / Label afterward | R42 restored-focus value/receipts |
|---|---|---|---|
| first `ui_right` press | HSlider | 6 / [6] / Value 6 | 6 / [6] |
| second `ui_right` press/release | Button | 6 / [6] / Value 6 at both | 6 / [6] |
| first `ui_left` press/release | HSlider restored | 5 / [6,5] / Value 5 at both | 5 / [6,5] |
| second `ui_left` press/release | Button AGAIN | 5 / [6,5] / Value 5 at both | 4 / [6,5,4] |

Connected HSlider range0..10 step1 initial5, signal-driven Label. Focus owner verified before every event, state after every frame. Exact expected-negative exit2 only after seven checks. Author's first integrated battery was not PASS: export-preset negative and initially empty diagnostic allowlist; corrected to permit only new exact terminal diagnostic. Two fresh named-verifier full replays 68/68 PASS, prior 58 tuple rows unchanged, nine opt-ins stable on comparable classifications; separate fault outer PASS with deliberate inner FAILs. Missing second focus transfer fails early owner assertion, missing first press fails early state assertion, not false expected-negative PASS. Reviewer parse/type/hung scratch failures remain telemetry. Owner/state checks do not prove internal consumption of unchanged actions. Claim only synthetic parsed actions and frames; not OS repeat, physical keyboard/timing, rendered/pointer input, accessibility, production or generic slider guarantee.
