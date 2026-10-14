# Round 40: seven-edge focus-absence control

Sources: `corpus/fixtures/slider_adjust.gd`, `run_battery.py`, named non-author `corpus/lessons/r40-repeat-focus-verifier.json`, `reports/r40-repeat-focus-verifier.md`.

| Fresh parsed action + one process frame | Focused connected HSlider value and cumulative receipts | Same wiring, no focus value/receipts/Label |
|---|---|---|
| first `ui_right` press | 6 / [6] | 5 / [] / Value 5 |
| second `ui_right` press | 7 / [6,7] | 5 / [] / Value 5 |
| `ui_right` release | 7 / [6,7] | 5 / [] / Value 5 |
| first `ui_left` press | 6 / [6,7,6] | 5 / [] / Value 5 |
| first `ui_left` release | 6 / [6,7,6] | 5 / [] / Value 5 |
| second `ui_left` press | 5 / [6,7,6,5] | 5 / [] / Value 5 |
| second `ui_left` release | 5 / [6,7,6,5] | 5 / [] / Value 5 |

In-tree slider range0..10 step1 initial5 and same signal-driven Label; focus owner checked before every edge. Terminal expected-negative exit2 only after all seven no-focus checks. Named verifier 65/65 PASS, 55 prior tuple rows unchanged and nine opt-ins stable on comparable classifications; separate fault outer PASS with expected deliberate inner FAILs. Focus-assignment sabotage failed early (not terminal classifier), focused skipped edge detected; skipping an action in the invariant no-focus arm is not independently observable from unchanged response, although seven dispatch calls are in reviewed source. Historical typed-array scratch failure and old-fixture early focus failure are telemetry, not positive evidence. Bounded to deliberate synthetic input and frames, not OS auto-repeat, physical timing, rendered/pointer interaction, accessibility, production, or a generic slider guarantee.
