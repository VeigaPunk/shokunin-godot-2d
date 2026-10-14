# Round 32 CheckBox scout — stateful toggle evidence

## Scope
Scratch-only real-Godot 4.7.2 probe in `.shokunin/game-dev-2d/corpus/live/r32-checkbox-scout/`. No fixture or runner edits. The CheckBox begins unchecked with Label `Off`, receives focus, then gets two `ui_accept` press/release pairs with frames between edges. Connected treatment records `toggled(bool)` and changes the Label; disconnected control uses the same input/state flow without a signal callback.

## Raw evidence
- `connected.log` (exit 0): press1 leaves unchecked/receipts `[]`/Label `Off`; release1 gives checked/receipts `[true]`/Label `On`; press2 keeps that state; release2 gives unchecked/receipts `[true,false]`/Label `Off`. Both releases report focus true. Final marker: `PASS checkbox_toggle initial=false focus=true states=[true,false] toggled=[true,false] labels=[On,Off]`.
- `disconnected.log` (exit 0): identical focused input transitions checked `[true,false]`, with receipts `[]` and Label `Off` throughout. Final marker: `PASS checkbox_disconnected states=[true,false] receipts=[] labels=[Off,Off]`.
- `connected.log` was overwritten by the successful run; the earlier initial scratch attempt is preserved as `initial-typed-array-error.log` below. That run exposed a scratch-only typed-array assignment error and remained alive because the script did not quit on that script error; it was terminated by the parent. It is not a PASS and is not the successful replay. I corrected the scratch script and bounded both subsequent commands with 12s `timeout`; each completed in under 0.5s with exit 0.

## Conclusion
This scratch probe demonstrates on Godot 4.7.2 a stateful CheckBox `ui_accept` toggle and `toggled(bool)` → Label behavior, with a paired disconnected control that still changes widget state but produces no callback receipts or Label changes. It supports the proposed distinct UI coverage contrast; it does not establish fixture/battery integration or independent verification. No rendered/pointer interaction, accessibility, production behavior, or real-user timing claim.
