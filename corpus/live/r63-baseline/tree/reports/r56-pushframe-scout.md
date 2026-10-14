# R56 push-frame scout — complementary frame-separated release

## Result

Independent scratch in Godot `4.7.2.stable.arch_linux.ed1daf0bf` observed the requested bounded complementary substeps. On edge10, after the same ten parsed action edges, the scratch dispatched matching `InputEventAction(action="ui_left", pressed=false)` via `root.push_input`, awaited one `process_frame`, and measured observer releases **3→4**, `Input.is_action_pressed("ui_left") == true`, numeric slider value `3.0`, full receipts `[6.0, 3.0]`, Label `Value 3`, focus owner on slider, and callback connected. It then called `Input.action_release("ui_left")`, awaited a second `process_frame`, and measured observer still 4, action false, value/receipts/Label unchanged, focus/callback true. All edge assertions reached the exact expected-negative terminal after eleven checks (exit 2).

This matches r52 push-only at the first substep and r51 parsed / r53 same-frame push-then-clear / r55 clear-frame-then-push at final measurements. In particular, the push-frame intermediate explicitly records the observer increment while action state is still pressed; second-frame clear changes action state without another observer receipt. This is only the bounded synthetic substep observation, not necessity of an extra frame or a physical-timing claim.

## Method and controls

Unique scratch project: `corpus/live/r56-pushframe-scout/scratch/project/`; independent controls: `corpus/live/r56-pushframe-scout/controls/{r51,r52,r53,r55}/`. The scratch copied the tracked fixture and modified only its scratch GDScript branch. Earlier ten edges remained parsed; the existing focus handoffs/restores and signal disconnect/reconnect were retained. Owner and callback connection were checked before every edge; numeric value/full receipts/Label were checked after each ordinary edge and at both edge10 substeps. Explicit edge10 checks captured observer/action/value/receipts/Label/focus/callback at the pushed frame, followed by final action/observer and all terminal state checks after the clear frame.

Observed scratch stdout: `SLIDER_PUSH_FRAME_THEN_CLEAR_RELEASE values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true`; exact intentional terminal `ERROR: SLIDER PUSH FRAME THEN CLEAR RELEASE ASSERTION FAILED: expected no new receipt after eleven checks`, exit 2.

Isolated current-baseline controls all reached their exact terminal with exit 2: r52 push-only printed observer_delta=1 and `pressed=true`; r53 same-frame push-then-clear printed the full eleven-edge terminal with receipts `[6,3]`; r55 clear-frame-then-push printed the full terminal; r51 parsed release printed the full terminal. These control reruns are scout scratch only, not new non-author verifier receipts and not replacements for committed lesson raws.

## Scope

Only this synthetic Godot 4.7.2 action-routing history and the two measured `process_frame` substeps. Does not claim frame necessity, physical input/timing, HSlider internal consumption, OS behavior, rendering, pointer/accessibility behavior, production, or general event provenance. No tracked fixture/runner edits, seeded or engine/editor changes, commits, pushes, or merges. No constants changed.
