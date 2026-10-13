# Round 55 frame-gap executor — additive case and author evidence

## Claim and causal scratch

Read the standing mission in `.shokunin/game-dev-2d/LOG.md`, including r55 scope/constraints, and r53–r54 lessons/reports. This tests one bounded claim: separate r54 edge10 `Input.action_release("ui_left")` and matching `root.push_input(InputEventAction(ui_left, false))` by one `process_frame`, preserving parsed edges 0–9. The scope is synthetic Godot 4.7.2 frames only.

Unique scratch project: `corpus/live/r55-frame-executor/scratch/project/`. Instrumented only scratch `slider_adjust.gd`; no tracked edit preceded causal measurement. Godot `4.7.2.stable.arch_linux.ed1daf0bf`, flags `--repeat-right --second-focus-restore --clear-then-push-release`.

After clear + first frame: observer remained 3, `pressed=false`, numeric value 3, receipts `[6.0, 3.0]`, Label `Value 3`, focus owner slider, callback connected. After matching pushed release + second frame: observer became 4, with the same other values. The full eleven-edge scratch route reached its unique expected-negative terminal (exit 2) after all assertions. This shows a directly observed intermediate substep that the r54 same-frame route does not measure; final measured state matches r54.

## Additive implementation

After the causal scratch and explicit parent authorization, sole executor added one dedicated `--clear-frame-then-push-release` branch in tracked `slider_adjust.gd`, one expected-negative row and one exact terminal allowance in `run_battery.py`. The branch preserves the parsed edges 0–9, focus handoffs/restores, disconnect/reconnect, owner and callback checks before every edge, and full per-edge numeric/receipt/Label postchecks. At edge10 it first clears the action and awaits a frame, then asserts observer remains 3, action state false, value 3, receipts `[6,3]`, Label `Value 3`, focus/callback true. It then pushes the matching release and awaits another frame; it asserts observer increments exactly once to 4, action remains false, and full numeric/receipts/Label terminal checks still hold. Its unique exact expected-negative terminal is only reached after the eleven-edge assertions. The r51–r54 branches and rows were retained byte-exact; no constants changed.

- Fresh ordinary author battery: **69/69 PASS** (68 prior + new row). Raw: `corpus/live/runs/20261013T103830363105Z/verdicts.json`.
- Fresh full seven-flag author battery: **80/80 PASS** (69 ordinary + 2 mutants + 9 opt-ins). Raw: `corpus/live/runs/20261013T103908594963Z/verdicts.json`.
- Compared full replay with committed `corpus/lessons/r54-order-non-author.json`: all **70** prior tuple-bearing `(case, verdict, actual_exit, signature)` rows are present and byte-value equal by case; the new row is `slider_adjust_repeat_right_second_focus_restore_clear_frame_then_push_release`, expected-negative exit 2 with its exact terminal signature. Existing nine opt-in classifications remain unchanged. Intentional inner `godot_error_unrelated` and `stream_reject` are FAIL under their outer probe PASS, not clean fixture passes.

A first implementation pass accidentally changed the existing r54 branch print marker while renaming the new marker. The parent flagged the diff; I restored the r54 marker byte-exact and reran both batteries. Those earlier raw runs are tainted and must not be used as evidence; the corrected rerun raw paths above supersede them. The task began in a HOLD because the initial executor had not been authorized and had no battery/tuple evidence. Parent's subsequent explicit authorization resolved that interruption. The initial HOLD is coordination state, not adverse test evidence. After authorization, additive implementation and author evidence above completed. No non-author verifier or admission verdict is claimed here.

## Scope and limits

Only this synthetic Godot 4.7.2 fixture and explicitly separated process-frame cadence. No claim about HSlider internal consumption, physical timing, OS input, rendering, pointer/accessibility, production, or generic event ordering. No engine/editor/seeded edits, commit, push, or merge.
