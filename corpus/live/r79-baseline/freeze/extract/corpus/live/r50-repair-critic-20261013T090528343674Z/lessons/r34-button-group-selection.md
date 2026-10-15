# Round 34: native ButtonGroup exclusive selection

Sources: `corpus/fixtures/button_group_selection.gd`, `run_battery.py`, named non-author `corpus/lessons/r34-button-group-verifier.json`, `reports/r34-button-group-verifier.md`. Godot 4.7.2 has **no `RadioButton` GDScript class**; literal attempts failed to parse. The tested controls are two native `Button`s with `toggle_mode=true` in one `ButtonGroup`.

| Point | A selected | B selected | Connected `toggled(bool)` receipts | Connected Label | Disconnected receipts / Label |
|---|---|---|---|---|---|
| Setup before signal connection | true | false | [] | A | [] / A |
| Focus B + complete `ui_accept` | false | true | [A:false,B:true] | B | [] / A |
| Focus A + complete `ui_accept` | true | false | [A:false,B:true,B:false,A:true] | A | [] / A; exit2 final intended signal assertion |

Initial `a.button_pressed=true` is setup before connections/stimulus, not manual transition evidence. Both actions are routed `root.push_input(ui_accept)` with target focus checked. Scratch removing B's ButtonGroup membership causes after-B exclusivity assertion failure. Named full replay 58/58 PASS (47 ordinary +2 mutants +9 opt-ins), all prior 56 result triples unchanged. Separate fault injection outer PASS contains deliberate inner FAILs. Literal RadioButton parse failure and scout's non-exiting ClassDB attempt (parent terminated PID1593651) plus an extra-B-refocus scratch variant are adverse telemetry, not PASS evidence; corrected scout, reviewer, critic and named verifier support the narrower claim. No pointer/rendered UI, physical timing, accessibility, production behavior or general group guarantee.
