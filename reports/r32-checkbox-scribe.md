# Round 32 CheckBox scribe checklist (read-only)

## Scope and claim
- Candidate is distinct from the existing `Button` pressed-receipt fixture only if the new treatment establishes stateful `CheckBox.button_pressed` transitions and emits/observes `toggled(bool)` on two completed focused `ui_accept` press/release actions.
- A paired signal-disconnected control must execute the same actions and still toggle the CheckBox state, while having no toggled receipts / Label update. This isolates signal delivery from action routing and property state.
- Do not claim coverage from a Label-only callback or a paired generic Button control. The existing Button fixture already covers focused `ui_accept` routing, `pressed`, and Label receipt; repeating those mechanics is not this coverage increment.

## Evidence to record / admit checklist
- [ ] Record the exact named non-author replay command, Godot version, raw output path, and exit status. Keep raw verdict JSON byte-for-byte in the assigned lesson artifact if verifier performs the replay.
- [ ] Connected treatment: confirm in-tree setup and initial unchecked state / initial Label; after first full action, checked=true, one `toggled(true)` receipt, Label reflects On; after second full action, checked=false, receipts ordered `[true, false]`, Label reflects Off. Show separate press/release edge completion and intermediate state so two actions are established.
- [ ] Disconnected treatment: same initial conditions and both actions; check state still changes true then false, but signal receipt/Label remains absent/stale, with failure at the intended signal/Label assertion (not setup, focus, or action dispatch).
- [ ] Confirm emitted `toggled(bool)` payloads are observed, not manually fabricated, and Label changes via the connected handler. Keep expected exact output/signatures aligned with actual runner conventions.
- [ ] Compare all prior r31 cases' `verdict`, `actual_exit`, and `signature` against the committed r31 raw baseline. Report ordinary/full totals and the number/type of added rows; don't call intentional negative classifications battery failures.
- [ ] Record separate fault-injection outcomes if run; distinguish harness exit from intentional inner FAIL results.
- [ ] Record tracked source hashes/diff scope before/after verifier replay. No edits to seeded fixtures, engine/editor, or verifier-owned files by this scribe.

## Axis verdict template
- **Coverage:** improved only if the independent real-Godot replay proves the connected state + bool signal sequence and paired disconnected causal contrast; otherwise unchanged / HOLD.
- **Depth:** unchanged (same two focused actions/edge structure; new widget mechanism is coverage, not extra depth).
- **Calibration:** unchanged unless evidence actually changes sensitivity/specificity behavior; do not infer calibration from one positive/negative pair.
- Admit only at least one improved axis and zero harmed axes. State raw totals, verdict, and any regression explicitly.

## Caveats / prohibited inferences
- Headless synthetic `root.push_input(ui_accept)` only; not rendered layout, pointer/hit-testing, physical keyboard, accessibility, focus behavior in production, or real-user timing.
- A state transition alone does not prove the signal; a signal receipt alone does not prove two distinct toggles or final state. Require both channels and disconnected control.
- One CheckBox setup does not establish generalized UI coverage or production correctness. No engine/editor, seeded controls, commit, push, or merge.
- If Godot cannot isolate the signal-disconnected contrast while preserving same actions and state transitions, HOLD and preserve adverse raw evidence; do not weaken assertions to claim coverage.

Scribe scope: read-only evidence/verdict checklist. This report is not a replay, independent verification, or a claim that the candidate passed.
