# Round 37 focus-absence reviewer

## Independent scratch measurement

Real Godot 4.7.2.stable (`godot --headless`; output retained at `corpus/live/r37-focus-reviewer-scratch/raw.txt`) tested a fresh synthetic parsed `InputEventAction` press/release pair for `ui_right`, then `ui_left`, with a frame between press and release and between actions. Both counterfactual and focused runs used an in-tree HSlider (min 0, max 10, step 1, initial value 5), the same `value_changed(float)` callback and Label consumer (`Value %d`), and inspected the actual viewport focus owner. The no-focus variant did not call `grab_focus()`.

- **No focus, same connected signal wiring:** before input, viewport focus owner was null, `has_focus=false`, value 5, receipts `[]`, Label `Value 5`. Owner remained null and those state values remained unchanged after `ui_right` and after `ui_left`. The intended negative emitted the missing-adjustment error only after both actions and exited 2. Raw output ends `EXIT:2`.
- **Focused positive:** using the tracked r36 `slider_adjust.gd` in independent scratch, focus was grabbed and checked; the same two actions passed with values `6,5`, receipts `6,5`, Labels `Value 6,Value 5`, exit 0 (`focused-raw.txt`).

This supports the proposed focus-absence counterfactual: parsed actions alone did not adjust the unfocused slider, while the focused positive did. No values or signals were manually changed/emitted. No engine/editor or tracked files were modified. Scope is headless synthetic parsed action/focus routing only.
