# Round 41 focus-handoff simplifier (read-only proposal)

I inspected `corpus/fixtures/slider_adjust.gd` and the round-41 claim in `LOG.md`; no fixture or runner edits, Godot execution, or scratch experiment were performed in this lane.

## Minimum isolated implementation

Add a dedicated `--focus-handoff` mode rather than altering `--repeat-right`, `--no-focus`, or their expected values/diagnostics. Construct one separate in-tree `Control` with `FOCUS_ALL` (a `Button` is sufficient), add it alongside the existing slider under the same `CanvasLayer`, and keep the current initial slider focus setup. Gate this addition/use to the new mode so existing modes retain their scene and setup.

In the mode's own seven-edge branch, preserve the existing `edges` sequence verbatim. Dispatch the first right press and await one frame while the slider owns focus; assert value `6`, receipts `[6]`, and label `Value 6`. Before dispatching edge index 1 (the second right press), call `other_control.grab_focus()` and assert the root GUI focus owner is exactly that control and `slider.has_focus()` is false. Dispatch the remaining six original events with one frame each; after every edge assert that focus still belongs to `other_control`, the slider is unfocused, value is `6`, receipts are `[6]`, and label is `Value 6`. Do not disconnect the signal or synthesize receipts/state.

Only after all seven per-edge checks pass, print a distinct handoff diagnostic and emit the intentional `push_error`/`quit(2)` negative result. This terminal nonzero is the expected negative row; any setup, focus-transfer, focus-retention, or edge-invariant failure must exit early as a different assertion failure. Add exactly one ordinary battery case for the new flag and exact terminal signature (not an opt-in probe group). Leave all existing case arguments and signatures untouched.

## Caution

This is a proposal, not evidence that Godot 4.7.2 will focus the separate control or route the synthetic events as expected. Per the round contract, executor must first run the direct scratch probe; HOLD and report if transfer/result differs. The claim remains limited to synthetic parsed actions and process frames, not physical keyboard/OS repeat, rendered/pointer behavior, accessibility, production, or general slider guarantees.
