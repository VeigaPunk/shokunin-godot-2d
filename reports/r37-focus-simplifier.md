# Round 37 focus-absence simplifier — read-only measurement

## Measurement

Ran an independent scratch probe at `corpus/live/r37-focus-simplifier/` under Godot 4.7.2. It creates an in-tree `HSlider` with min=0, max=10, step=1, value=5, `FOCUS_ALL`, a `Label` initially `Value 5`, and the same `value_changed` receipt/Label callback as the connected positive fixture. It makes no `grab_focus` call. It sends the same fresh `InputEventAction` pressed/released pairs through `Input.parse_input_event` for `ui_right`, then `ui_left`, with a process frame between edges.

Raw output: setup and both pre-action checks reported `gui_get_focus_owner() == null` (`has_focus=false`). After `ui_right`, and again after `ui_left`, focus owner stayed null, value stayed 5, receipts stayed `[]`, and Label stayed `Value 5`. Scratch probe exited 0 because its diagnostic accepts that observed state. This is the requested first real-engine focus/action measurement; it supports proceeding, not HOLD. The requested tracked negative should instead intentionally exit 2 only after verifying both complete action pairs and the final expected state.

## Minimal diagnostic design

Keep one setup and one callback wiring shared with the positive. Branch only around focus acquisition: focused positive calls `grab_focus`; no-focus arm does not. Before each action, assert focus owner is not the slider (prefer explicitly `null` for this isolated fixture); inject identical parsed press/release pair; await between edges; capture value/receipts/Label. After both actions, assert owner remains absent and value=5, receipts=`[]`, Label=`Value 5`, then deliberately `push_error`/exit 2 at the named missing-adjustment negative assertion. Do not expect a transition after either action, and do not stop after only `ui_right`. The assertion should distinguish setup/focus-route failures from the intended negative exit; preserve output identifying both actions and their observed state.

This compares input-routing focus presence while holding slider, initial state, signal connection, callback, action sequence, and frame separation constant. It is narrower and cleaner than disconnecting the signal, which is not a focus control. No `set_value`, manual signal emission, `action_press` substitute, or extra control is needed.

## Hold / scope concerns

Hold if a repeat scratch shows the slider owns focus before either action, or if either parsed action changes value/receipts/Label without slider focus; then the proposed contrast is not established and must be re-scoped. Current direct measurement shows neither. This is only a headless synthetic parsed-action focus-routing result in Godot 4.7.2; it does not establish physical key, pointer, rendered UI, accessibility, or production focus guarantees. No tracked files or seeded fixtures were changed.
