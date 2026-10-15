# Round 29 focus scribe — paired raw/admission checklist

Scope: read-only probe/report. No delegation. No engine/editor/seeded corpus changes. No tracked fixture or runner edit.

## Raw paired observation

Scratch probe: `corpus/live/r29-focus-scribe/paired.gd`; exact command outputs and script/tracked-file hashes: `corpus/live/r29-focus-scribe/paired-raw.json`. Godot `4.7.2.stable.arch_linux.ed1daf0bf`.

- Focused arm: focus owner was `ActivateButton`; `Button.has_focus()` true before and after each action. Two complete `ui_accept` press/release pairs produced receipts 1 then 2 and Label states `Activated 1`, `Activated 2`.
- Unfocused arm: after adding the Button/Label and waiting a frame, did not call `grab_focus`; focus owner was a different `LineEdit`; `Button.has_focus()` false before input and remained false. Same two complete actions produced zero receipts and Label stayed `Ready`.
- Both arms used the same scratch script logic, signal, action and sequence, differing only in whether `grab_focus()` was called. This is a real focused-versus-unfocused contrast in this headless Godot 4.7.2 probe. The unexpectedly focused unrelated LineEdit is recorded; the test establishes Button is unfocused, not that the entire GUI has no focus owner.

## Admission / HOLD checklist

- [x] Positive actually verifies Button focus and shows expected receipts/states.
- [x] Control verifies Button is not focused before and after input; same `ui_accept` input yields no callback/state change.
- [x] Paired raw stdout, exit codes, script hash, tracked fixture/runner hashes saved.
- [x] No tracked modifications made by this scribe.
- [ ] Round-level admission still requires executor implementation only if parent judges contrast causal, plus named non-author verifier replay and full battery/regression evidence. This read-only result alone is not admission.
- HOLD only if subsequent isolated replay fails to reproduce contrast or cannot establish Button focus state. Current probe does reproduce a contrast; avoid claiming global UI focus absence, accessibility, pointer behavior, production scene behavior, or arbitrary mutation resistance.

Recommendation: proceed to the assigned executor's minimal causal fixture/control only if parent independently accepts this contrast. Otherwise preserve this as scratch evidence and HOLD; do not speculate or broaden claims.
