# Round 55 frame-gap reviewer — independent scratch

## Result

Godot `4.7.2.stable.arch_linux.ed1daf0bf` direct scratch supports the proposed bounded distinction check. I copied the fixture to `corpus/live/r55-frame-reviewer/scratch-project/` and changed only that scratch `slider_adjust.gd`. Edges 0–9 remained parsed, including both focus transfers and callback disconnect/reconnect. Before each edge the owner and callback state are checked; the existing edge receipts and labels/numeric values are checked throughout.

At edge 10 the scratch calls `Input.action_release("ui_left")`, awaits one `process_frame`, then checks the first substep: observer remains 3, `ui_left` is no longer pressed, slider value is 3, receipts are `[6,3]`, Label is `Value 3`, slider owns focus, and callback is connected. It then pushes a matching `InputEventAction` release and awaits another frame. Observer becomes 4; pressed remains false; numeric/receipts/Label/focus/callback remain exactly as specified. Eleven-edge sequence ends at the intentional exact expected-negative terminal (`SLIDER CLEAR FRAME THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks`), exit 2.

Scratch controls copied from the same fixture also reached their expected-negative terminal with all eleven edge checks: r54 same-frame clear-then-push, r53 same-frame push-then-clear, and parsed edge10. Each gives observer 3→4, action false, numeric 3 / `[6,3]` / `Value 3`, focus owner and callback true. The intervening clear frame itself did not change the measured values/receipts/label or focus/callback; the matching push in the next frame delivered the observer increment. Thus the added frame does not distinguish these measured outcomes, but it is a distinct synthetic sequence worth a dedicated expected-negative case if the executor independently confirms.

## Execution and limits

Commands used Godot headless 4.7.2. All three controls and candidate exited 2 only at their intentional expected-negative terminals after the positive checks; these are causal scratch observations, not a battery PASS. No tracked fixture/runner edits, engine/editor or seeded edits, commits, pushes, or merges. No claim about physical timing, HSlider internal consumption, OS/render/pointer/accessibility, or production behavior. Scope is explicit synthetic frames only.
