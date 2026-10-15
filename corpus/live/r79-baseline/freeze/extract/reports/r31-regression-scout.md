# Round 31 regression scout — prior controls and opt-in baselines

Read-only review of the r31 claim, current tracked Button fixture/runner, and committed r29/r30 verifier evidence. I made no fixture/runner edits and ran no Godot or battery commands; this report is my only artifact.

## Relevant prior state

The current tracked `button_activation.gd` (the r30 edge fixture) has one connected `Button.pressed` handler incrementing `pressed_receipts` and updating the Label. Both actions use `_send_action_edge` to push the same `ui_accept` `InputEventAction` through `root.push_input`; each press and release is separated by a `process_frame`. Focused positive starts with verified Button owner, checks press1 remains 0/Ready, release1 gives 1/Activated 1, press2 remains 1/Activated 1, and release2 gives 2/Activated 2. It currently verifies focus at release1 and after release2, but does **not** withdraw focus between the completed first pair and second press. Thus it does not itself answer r31's continued-focus question.

`corpus/lessons/r30-edge-verifier.json` (SHA-256 `890042e23e8533f27b50f9758517ed3e448cfd5472dc0addf86a93872532829f`) is the named r30 full replay, 53/53 PASS (42 ordinary +2 mutants +9 opt-in probes). Its focused Button row is PASS exit 0 with signature `edge_texts=[Ready,Activated 1,Activated 1,Activated 2] receipts=[0,1,1,2]`; disconnected and no-focus controls are expected-negative PASS records, exit 2 at `release1`. `reports/r30-edge-verifier.md` says direct runs found focus true through both releases; it does not test losing focus between pairs. This is prior evidence, not a fresh r31 replay.

## Controls that must remain diagnostic

- **Disconnected:** keep the same routed input and focus setup; without the `Button.pressed` connection, expect failure at release1 with zero receipts/Ready. Do not let r31's second-action checks mask this earlier intended negative.
- **Initially unfocused:** keep the `--no-focus` setup check proving no Button focus and null viewport focus owner before input; it should remain the existing expected failure at release1, zero receipts/Ready. This control diagnoses focus absence from the outset, not focus loss after action1.
- **Focused positive:** retain the r30 edge assertions and connected callback. For an r31 mid-sequence arm, establish focus before action1, complete and check release1, explicitly release focus, await a frame, and verify both `button.has_focus()==false` and null focus owner before action2. Then preserve the press2 and release2 waits/assertions. An expected negative should stay at one receipt/Activated 1 on both second edges. This controls focus at the critical transition rather than assuming `release_focus()` worked. Keep `ui_accept`, `root.push_input`, and callback wiring identical across positive and contrast; do not substitute direct signal emission.

The existing focused arm is a useful control that continued focus still permits action2. An independently checked focus-loss arm is necessary to distinguish dependence on continued focus from merely having focus at action1. If the post-release owner is not null, the contrast is not isolated and should be HOLD, not attributed to focus loss.

## Unrelated full-battery paths and fault evidence

The r30 full raw record classifies `probe_export_launch` PASS with `positive_assertion=true` / `negative_assertion=false`; `probe_timeout` PASS with inner classifications `[false,true,false]`; `probe_godot_error` PASS `[true,false]`; and `probe_crash_exit` PASS `[true,false]`. These are frozen r30 baselines, not fresh r31 replay claims. The separate `corpus/lessons/r30-fault-verifier.json` (SHA-256 `cc50beaf84dfdc2010358eafda5dbb50e217ed6327d8e39fd7b3538cc612fd8f`) is fault-injection mode: outer PASS intentionally contains `fault_hang` timeout FAIL and `fault_unrelated_error` FAIL, with `fault_clean_expected_negative` PASS. Do not describe that as a clean full battery or use it as Button evidence. A named r31 full replay is needed to establish unchanged outcomes and preserve the 53 prior cases if an edit is admitted.

## Bounded conclusion

The prior r30 positive verifies two complete edge-separated actions only while focus remains; it does not show whether the second activation requires continued focus. Preserve the disconnected and initially-unfocused diagnostics and all edge observations. The r31 contrast is causal only if focus ownership is verified absent after action1 and before action2, while the original positive still activates action2. My review makes no new runtime, regression, or focus-loss finding and no claim about pointer/rendered UI, real-user timing/debounce, or production focus behavior. No engine/editor or seeded controls were changed; no commit, push, or merge.
