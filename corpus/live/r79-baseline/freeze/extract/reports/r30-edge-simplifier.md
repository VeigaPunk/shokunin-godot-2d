# Round 30 edge simplifier review

Read-only review of the tracked `button_activation.gd` and the r30 depth claim. No source edits or engine runs performed.

## Minimal change

Keep the existing event construction and the same focused Button. Change the action sender to emit exactly one `InputEventAction` for a supplied `pressed` value, then have the positive path alternate:

1. Send press; await one `process_frame`; assert receipts/text remain at the previous completed count (`0`/`Ready` for action 1, `1`/`Activated 1` for action 2).
2. Send release; await one `process_frame`; assert the next count/text (`1`/`Activated 1`, then `2`/`Activated 2`).

This is the narrowest meaningful split: no extra controls, signal rewiring, helper state, timing knobs, or production changes. Keep existing setup/focus checks and final PASS. A tiny helper can compare expected count/text if it makes duplicated assertions shorter, but do not obscure which edge is under assertion.

## Attribution and controls

The press-only check must require no new receipt; the release-only check must require exactly one. Thus an activation on press is exposed rather than silently counted as release behavior. Existing disconnected and no-focus cases should continue to fail when their first activation is expected (after first release), while their setup checks continue to establish the intended control condition. Do not add release suppression/delay switches to the tracked fixture; any adverse probe belongs in scratch and should demonstrate failure at a named release assertion.

This supports only the existing focused headless `root.push_input(ui_accept)` path and two press/release pairs. It does not establish pointer, rendered UI, debounce, or production focus behavior. Confirm all previous 53 outcomes and scratch mutation evidence via the named non-author verifier before admission.
