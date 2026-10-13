# Round 31: continued focus for second Button action

Sources: `corpus/fixtures/button_activation.gd`, `run_battery.py`, named non-author `corpus/lessons/r31-focus-loss-verifier.json`, `reports/r31-focus-loss-verifier.md`.

| After edge | Continuously focused | Focus lost after completed release1 |
|---|---|---|
| Release1 | receipt1 / Activated 1, focus owner Button | same |
| Before press2 | focus owner Button | explicit `release_focus`, null GUI owner and Button.has_focus false |
| Press2 | receipt1 / Activated 1 | receipt1 / Activated 1; still null owner |
| Release2 | receipt2 / Activated 2 | receipt1 / Activated 1; still null owner |

Identical routed `root.push_input(ui_accept)` second press/release edges and signal wiring are retained. A disposable sabotage copy removes only `release_focus()` while leaving null-owner mid-sequence assertion: exit2 at intended assertion. Named replay 54/54 (43 ordinary +2 mutants +9 opt-ins); all prior 53 verdict/exit/signature triples unchanged. Separate fault-injection outer PASS contains deliberate inner FAILs. The initial no-focus and disconnected rows still fail at release1. One extra ordinary row is a calibration control, not a separate coverage gain. Scope is synthetic headless Godot 4.7.2 action routing; not pointer/rendered UI, physical timing, accessibility or production focus.
