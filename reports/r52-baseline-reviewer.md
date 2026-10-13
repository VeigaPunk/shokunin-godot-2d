# Round 52 baseline review and causal route probe

Role: read-only baseline reviewer / direct scratch probe. No delegation and no tracked edits.

## Immutable r51 baseline

Round 51 LOG and lesson record define the baseline: named non-author default-path 76/76 (67 tuple-bearing rows, nine opt-ins); paired parsed edge10 on the ordinary eleven-action synthetic HSlider history reached numeric 3, receipts `[6,3]`, Label `Value 3`, observer count 3→4 and `Input.is_action_pressed("ui_left")` true→false. Focus owner and callback connection were checked before edges; values/receipts/Label after frames. Direct state-clear and omission controls failed early. Preserve r51 source and its raw/report unchanged.

## Round 52 causal scratch result — hypothesis holds

Copied the in-tree fixtures to `/tmp/r52-route-contrast/project` and changed only scratch `slider_adjust.gd` routing at action index 10: same `InputEventAction` fields, but `root.push_input(event)` instead of `Input.parse_input_event(event)`. Ran the exact Godot 4.7.2 headless route with `--repeat-right --second-focus-restore --observe-parsed-release`.

Control using unchanged parsed route: terminal marker emitted, exit 2 at the expected deliberate terminal assertion; route’s in-loop checks pass, including edge10 observer increment exactly once, global pressed-state transition and slider receipts/state.

Push route: after edge10, observer count was 3→4, `Input.is_action_pressed("ui_left")` remained true, and numeric value/receipts/Label were still `3 / [6,3] / Value 3`; focus owner remained slider and callback remained connected. The pre-release checks established the same focused owner/callback before edge10. The route then failed before its terminal marker on the existing non-allowlisted global post-release assertion (`SLIDER input-state post-release assertion failed: ui_left remains pressed`), exit 2. This directly demonstrates the proposed distinction: `root.push_input` delivers a matching release to this separate in-tree `_input` observer, but in this fixture does not update the global action pressed state as `Input.parse_input_event` does.

No tracked fixture/runner edits, battery run, or case addition was made. Scratch only. This supports a bounded negative control for the synthetic route distinction; it says nothing about OS input, HSlider internal consumption, physical timing, rendering, pointer/accessibility, or production behavior.
