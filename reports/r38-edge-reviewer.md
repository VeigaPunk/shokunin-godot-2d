# Round 38 independent edge review

## Method
Measured with Godot 4.7.2.stable (`godot --headless`, scratch-only project/script at `corpus/live/r38-edge-reviewer/three_arm/`). Three independent arms used the r38 HSlider setup (in-tree HSlider, min 0, max 10, step 1, initial 5; Label and `value_changed` receipt callback). Each action was a fresh `InputEventAction`, submitted via `Input.parse_input_event`, and followed by `await process_frame` before sampling. Connected arm called `grab_focus`; disconnected arm retained focus but omitted callback connection; no-focus arm omitted `grab_focus`. No engine/editor/seeded corpus controls were changed.

## Observations

| Arm | Focus | ui_right press | ui_right release | ui_left press | ui_left release |
|---|---|---|---|---|---|
| Connected | slider | value 6, receipts `[6]`, Label `Value 6` | value 6, receipts `[6]`, Label `Value 6` | value 5, receipts `[6,5]`, Label `Value 5` | value 5, receipts `[6,5]`, Label `Value 5` |
| Disconnected | slider | value 6, receipts `[]`, Label `Value 5` | value 6, receipts `[]`, Label `Value 5` | value 5, receipts `[]`, Label `Value 5` | value 5, receipts `[]`, Label `Value 5` |
| No-focus | none | value 5, receipts `[]`, Label `Value 5` | value 5, receipts `[]`, Label `Value 5` | value 5, receipts `[]`, Label `Value 5` | value 5, receipts `[]`, Label `Value 5` |

All three arms began at value 5 with empty receipts and Label `Value 5`. Outputs in full are retained alongside the scratch probe at `corpus/live/r38-edge-reviewer/three_arm/` (the first no-focus probe run had an incorrect expected value in the reviewer script and exited 3 at ui_right press; corrected expectation to 5 and repeated, yielding the table above). The final connected and disconnected runs exited 0; corrected no-focus run exited 0.

## Review
The round's proposed press/release attribution is supported by this Godot measurement: values and connected receipts change on each intended press, and releases add neither value changes nor duplicate receipts. Disconnected control isolates numeric adjustment from signal/Label effects; no-focus control has neither adjustments nor receipts. This supports the bounded depth move if the fixture asserts all edge snapshots and the named verifier replays it. Scope is synthetic parsed action events with a process-frame wait; it does not establish physical keyboard timing, auto-repeat, rendered/pointer behavior, accessibility, or general Range guarantees. No contrary measurement; no HOLD indicated by this independent scratch review.
