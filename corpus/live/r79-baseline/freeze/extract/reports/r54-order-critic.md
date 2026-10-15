# R54 order critic — reversed composite edge10

- Role: LEAF critic, no delegation; tracked fixture/runner read-only. Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Scratch only: `.shokunin/game-dev-2d/corpus/live/r54-order-critic-scratch/`.
- Read the standing mission, R54 LOG claim and the R51–R53 lessons/reports. The exact hypothesis is order sensitivity: compare parsed release (R51), push then clear (R53), and clear then push (R54), with edges 0–9 and frame boundary otherwise unchanged.

## Reversed-order result

Copied the fixture/project into private scratch and changed only the existing composite branch's edge10 order to `Input.action_release("ui_left")` then `root.push_input(matching InputEventAction(ui_left, pressed=false))`, before the same `await process_frame`. Added a scratch-only diagnostic immediately after that frame. Owner and callback-connection checks remain before every edge; numeric value, full receipts, and Label are checked after each frame; the existing observer count and action-state assertions run at edge10.

Command: `godot --headless --path <scratch>/project --script slider_adjust.gd -- --repeat-right --second-focus-restore --composite-push-and-clear`.

Observed edge10 diagnostic: `observer=3->4 pressed=false value=3.0 receipts=[6.0, 3.0] label=Value 3 focus_owner=true callback_connected=true`. The trace reached the unique expected-negative terminal only after all eleven checks (exit 2). No assertion failed. This reproduces both R51 parsed and R53 push-then-clear measured postconditions; reversed order is not distinguishable by these checks in this synthetic sequence.

## Controls and interpretation

Fresh baseline scratch copies of the unmodified fixture ran the R51 `--observe-parsed-release` route and R52 `--observe-push-input-release` route; both reached their own expected-negative terminal (exit 2). R51 assertions require observer +1 and cleared action state; R52 assertions require observer +1 and action still pressed. These controls corroborate that the reverse-order composite's observed combination is not a misread of push-only behavior. R53's push-then-clear result and the R54 instrumentation agree; the order change preserves the measured combination, rather than revealing order sensitivity.

The result supports an additive expected-negative branch/row only if it explicitly names reversed order and preserves all prior branches/rows. It weakens any claim that the R53 push-then-clear order is necessary to obtain those postconditions. It does not show arbitrary orders/timing are equivalent: only these two synchronous call orders before the same frame were tested. Keep output diagnostics subordinate to direct post-frame measurements; the historical composite terminal text is not state evidence.

Scope: synthetic Godot 4.7.2 route only. No inference about HSlider internal consumption, OS input, physical timing/input, rendering, pointer/accessibility, production behavior, or general event provenance. No tracked/seeded/engine/editor edits, constants changed, commit, push, or merge.
