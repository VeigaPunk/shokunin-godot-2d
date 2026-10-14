# Round 54 order simplifier — read-only tracked proposal

## Reverse-order scratch observation

I did not edit tracked `slider_adjust.gd` or `run_battery.py`. I copied the fixture project into `corpus/live/r54-order-simplifier-unique/project/` and modified only the copied composite edge10 to call `Input.action_release("ui_left")` first, then `root.push_input(matching InputEventAction(ui_left, pressed=false))`, before the same `process_frame`. Edges 0–9 remain parsed; focus transfers/restorations, callback disconnect/reconnect, owner/connection prechecks and per-frame numeric/full receipt/Label assertions remain as in r53.

Godot 4.7.2 reversed-order run reached `SLIDER_COMPOSITE_PUSH_AND_CLEAR` terminal and exited 2 as intended by this scratch fixture. Its eleven edge checks passed. Output values `6,6,6,5,5,5,5,4,4,3,3`, receipts `[6,3]`, Labels `Value 6,Value 3`, callback connected true. The branch's explicit edge10 observer +1 and global action false checks also passed. This run itself does not print observer counts or edge10 value separately; the corresponding r53 report/fixture branch identifies those checks, while this scratch's successful terminal establishes they held. Parsed r51 control from prior report has same measured state. r53 push-then-clear control likewise reached its terminal. Therefore reverse order also mimics the compared measured postconditions in this synthetic route; the ordering in the composite is not necessary for that outcome.

## Minimum additive proposal (tracked files remain read-only)

If the sole executor proceeds, add one dedicated flag/branch for clear-then-push-release, one exact expected-negative row and one exact terminal allowance. Clone the r53 composite checks, with edge10 ordered `Input.action_release("ui_left")` then `root.push_input(matching release)` before the frame. Keep r51 parsed, r52 push-only and r53 push-then-clear branches/rows byte-exact. Expected ordinary/full totals from r53 baseline: 68/79; preserve all prior 69 tuple-bearing records and nine opt-in classifications. This is only a proposal, not tracked implementation or admission evidence. Independent route/fault/sabotage and named non-author verification remains necessary.

No failed scratch setup occurred. The scratch altered only its copied slider script; tracked fixtures/runner unchanged by me, and constants unchanged.

Scope: only the bounded synthetic Godot 4.7.2 routed sequence. No inference about HSlider internal event consumption, OS input, physical timing, rendering, pointer behavior, accessibility, production behavior, or general route provenance.
