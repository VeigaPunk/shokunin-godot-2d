# Round 32 CheckBox simplifier

## Minimal causal contrast

A distinct fixture can cover the stateful `CheckBox` mechanism with one focused, in-tree `CheckBox` and one `Label` initialized to `Ready`. Leave the CheckBox initially unchecked (`button_pressed == false`); verify its in-tree state and focus owner before input. Connect `toggled(bool)` to a callback that appends the bool to a receipt list and changes the Label to `On` or `Off`.

Send two identical complete `ui_accept` press/release pairs through `root.push_input`, awaiting a frame after each edge. Check state after each edge (press must not toggle; release must): initial false → press1 false → release1 true; press2 true → release2 false. After each release, also assert the corresponding receipt list (`[true]`, then `[true, false]`) and Label (`On`, then `Off`). Check state before checking receipt/Label so the disconnected arm establishes that the Control itself toggled even though its signal path did not update observations. The connected run should end with exact output such as `PASS checkbox_toggle states=[false,true,false] toggled=[true,false] labels=[Ready,On,Off]`.

Use the same fixture and same focus/input/frame sequence for one disconnected-signal arm (single opt-in switch, e.g. `--disconnect-signal`). It must still pass setup and each checked-state assertion. With the connection omitted, at release1 it should fail specifically at the expected first signal/Label receipt, e.g. `UI CHECKBOX ASSERTION FAILED: expected release1 toggled=[true] label=On, got toggled=[] label=Ready` (exit 2). This is the intended diagnostic, not a setup failure or a separate unpaired UI. Do not branch around state checks or synthesize callback receipts in this arm.

## Runner/evidence boundary

If the executor confirms this real-Godot contrast, the smallest runner addition is two ordinary rows for the same fixture: connected positive expecting exit 0 and the exact `PASS checkbox_toggle ...` line; disconnected expecting exit 2 and the exact `ERROR: UI CHECKBOX ASSERTION FAILED: expected release1 ...` diagnostic prefix. Register the negative signature in the runner's expected-signature map. Preserve all existing fixture rows and diagnostics. This is coverage of CheckBox checked-state transitions and `toggled(bool)` delivery, distinct from Button `pressed`; the paired arm helps attribute the observed Label/receipt change to the signal.

No manual `pressed`/`toggled` emission, paired second Control, focus removal, pointer event, rendered UI, or assertion-suppression mode. Scope is only headless Godot `ui_accept` behavior, not pointer interaction, real-user timing, accessibility, or production UI behavior. Read-only design only; no Godot probe or source/runner edit performed.
