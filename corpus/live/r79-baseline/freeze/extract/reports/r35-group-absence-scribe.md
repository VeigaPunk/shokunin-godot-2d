# Round 35 group-absence scribe — raw comparison and admission checklist

## Scope / precondition

Read-only evidence note for calibration of **native Godot `Button(toggle_mode=true)` controls** (not a nonexistent `RadioButton` class). The paired arms use the same two controls, one `ButtonGroup` containing A, initial A-selected/B-unselected, connected `toggled(bool)` callbacks and Label update handlers, then the same target-focus B → `ui_accept`, A → `ui_accept` actions. The only intended variable is B membership in the group. The test is headless synthetic `root.push_input(ui_accept)`, not rendered/pointer UI or production behavior.

This is a scribe's raw comparison, **not** the required named non-author full-battery verifier receipt. Evidence comes from Godot 4.7.2 scratch runs and the r34 tracked grouped positive/raw verifier. No tracked source was edited by me; own scratch is `corpus/live/r35-group-absence-scribe/`.

## Observed pair

| Point | B in shared group (r34 positive) | B not in group (scratch, same action sequence) |
|---|---|---|
| Setup before actions | A=true, B=false; receipts=[]; Label=A | A=true, B=false; receipts=[]; Label=A |
| Focus B + complete `ui_accept` | A=false, B=true; receipts=[A:false,B:true]; Label=B | A=true, B=true; receipts=[B:true]; Label=B |
| Focus A + complete `ui_accept` | A=true, B=false; receipts=[A:false,B:true,B:false,A:true]; Label=A | A=true, B=true; receipts=[B:true,A:true]; Label=A |

The grouped sequence is reproduced in r34 `corpus/lessons/r34-button-group-verifier.json` (Godot 4.7.2, connected row PASS) and my own scratch replay. Ungrouped observations are in my raw `scout_probe.gd` run: stdout explicitly prints states/receipts/Label after both focused actions. Deleting only `b.button_group = group` from a scratch copy of the tracked fixture also causes its existing grouped state assertion to exit 2 after B, but that assertion stops before exposing the measured ungrouped state; this is a rejection signal, not a substitute for the observational trace.

Disconnected ungrouped scratch still traversed both actions: A=true/B=true at both observations, receipts=[] and Label=A throughout; it ended exit 2 on the existing missing-signal assertion. That disconnected arm confirms UI action/property behavior without callback updates, but is **not** the proposed new ordinary negative row: the new row should remain connected so it can prove B:true and Label B, then fail specifically on after-B exclusivity (`A=true B=true`).

## Calibration / verdict

The observed ungrouped arm sharply contrasts with grouped behavior under matched initial state, focus targets and action sequence: without B membership, the first action leaves both Buttons selected and emits only `B:true`, while grouped A emits `A:false,B:true`. A second action is still informative: ungrouped A is already selected, yet focused acceptance emits `A:true` and leaves B selected. Do not assume a no-op/callback-free second action. This supports adding an expected-negative **after-B exclusivity** arm that asserts exact state, callbacks, and Label before reporting the intended exclusivity failure. It would be a bounded calibration improvement, not general proof of ButtonGroup behavior.

Provisional axis disposition if the executor's row is validated by the named verifier: **calibration improved** (paired causal absence control now distinguishes the exclusive-selection expectation from ordinary independent toggles); **depth unchanged**, **coverage unchanged**; no harm observed in this finite scratch pair. Do not claim admission on this note alone. Existing baseline target from LOG: 47 ordinary / 58 full; proposed addition 48 / 59, with prior 58 result triples unchanged. The fresh full replay and exact row classification remain verifier-owned.

## HOLD / admission checklist

- [x] Two native toggle-mode Buttons, shared group only in positive; literal RadioButton coverage is not claimed.
- [x] Same initial state, connected callback wiring, focused B→A `ui_accept`, and Label handlers in paired scratch arms.
- [x] Raw observations include after-B **and** after-A state, ordered receipts, and Label for grouped and ungrouped arms.
- [x] Ungrouped expected contrast is specific: after B A=true/B=true, receipts `[B:true]`, Label B; after A A=true/B=true, receipts `[B:true,A:true]`, Label A.
- [ ] Named non-author verifier replays full battery and validates exact new negative row, intended after-B exclusivity signature/exit, and unchanged prior 58 triples.
- [ ] Verify new row is connected (not `--disconnect-signal`) and its diagnostic is a deliberate expected negative, not setup/focus failure, unrelated engine error, or timeout.
- [ ] Verify exact source/runner hashes and byte-stable raw receipt; separate fault injection must not be conflated with battery results.
- [ ] If B is auto-grouped, does not toggle, paired setup/action wiring differs, receipts/Label mismatch, prior result triples drift, or verifier evidence is unavailable: HOLD calibration claim and count; do not force admission.

No RadioButton claim, engine/editor or seeded fixture edits, pointer/rendered UI, accessibility, physical timing, production behavior, push, merge, or commit is covered here.
