# Round 56 push-frame-then-clear simplifier — read-only proposal

I inspected the standing mission, r56 claim, tracked slider fixture and battery, and the r52–r55 executor/verifier reports and committed lessons. This lane made no tracked edits and ran no engine test; it supplies only a minimum additive proposal, not causal evidence or an admission verdict.

## Minimum candidate if causal scratch confirms it

Add one distinct `--push-frame-then-clear-release` path to `slider_adjust.gd`, adjacent to the existing r53/r55/r54 focused/reconnected eleven-edge controls. Keep the parsed edges 0–9, focus transfers, signal disconnect/reconnect, per-edge owner/callback prechecks, and numeric/full-receipt/Label checks unchanged. At edge 10 check `ui_left` is pressed before the operation; construct the matching `InputEventAction(ui_left, pressed=false)`, call `root.push_input(event)`, await `process_frame`, then assert observer 3→4, global `Input.is_action_pressed("ui_left") == true`, value 3, receipts `[6,3]`, Label `Value 3`, slider focus, and callback connected. Next call `Input.action_release("ui_left")`, await `process_frame`, and assert observer remains 4, action is false, and all numeric/receipt/Label/focus/callback values remain unchanged. Require the existing eleven-edge unique expected-negative terminal after all assertions.

Add exactly one battery case with the new flag and a unique exact expected-negative terminal allowance. Do not alter existing r51–r55 branches, rows, signatures, constants, or opt-ins. Candidate arithmetic, if independently verified, is ordinary 70/full 81; prior 71 tuple-bearing rows and nine opt-in classifications must match exactly. The round's stated contrast is r53 same-frame push+clear, r55 clear-frame+push, and r52 push-only. A causal scratch and named independent replay remain prerequisites; absent those, HOLD.

## Calibration boundary / risks

At most this supports the bounded pair of synthetic intermediate observations for this Godot 4.7.2 fixture. It must not be described as frame necessity (r55's ineffective omitted-await sabotage is contrary evidence), physical timing, HSlider internals, OS input, rendering, pointer/accessibility, production behavior, or generic provenance. Setup failures are adverse telemetry, never passes. The committed r52–r55 lesson raws are read-only and must not be rewritten.
