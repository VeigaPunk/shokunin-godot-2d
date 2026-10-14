# Round 41 focus-handoff scribe — evidence/admission checklist (read-only)

## Assignment and evidence boundary
Read-only scribe. I did not run Godot, edit fixture/runner, alter corpus, or delegate. This report is a checklist, not a measurement or admission verdict. Round-41 claim and planned roles are in `.shokunin/game-dev-2d/LOG.md`; prior admitted baseline is r40. Relevant precedent: `reports/r40-repeat-focus-verifier.md`, `reports/r40-repeat-focus-reviewer.md`, and `corpus/lessons/r40-repeat-focus-verifier.json`. The r40 verifier reports 54 ordinary + 2 mutant + 9 opt-in cases (65 total), with 55 prior tuple rows compared to r39; r41 must compare against r40, not reuse the older baseline.

## Required real-engine scratch evidence before any tracked edit
- Use real installed Godot 4.7.2, scratch project/control only. Preserve evidence paths and raw stdout/stderr/exit status.
- Same in-tree HSlider, min 0/max 10/step 1/initial 5, connected `value_changed` consumer and Label throughout; no disconnect or synthetic receipts/state.
- Dispatch seven deliberate fresh parsed events in existing order, each followed by one process frame: `ui_right` press, `ui_right` press, `ui_right` release, `ui_left` press, `ui_left` release, `ui_left` press, `ui_left` release.
- Before edge 1 (first right press), slider owns GUI focus. After edge 1, value=6, receipts `[6]`, Label `Value 6`.
- Before edge 2, transfer focus to a separate in-tree focusable Control and assert GUI focus owner is exactly that Control and slider is unfocused. If focus transfer fails, or second/remaining event changes any target observation/focus unexpectedly, HOLD and report exact result; do not proceed to implement/admit candidate.
- After every remaining event/frame (six checks), focus remains on separate Control, slider remains unfocused, value remains 6, receipts remain `[6]`, Label remains `Value 6`.
- Distinct expected-negative terminal exit 2 must happen only after all seven per-edge checks. Early setup/focus/assertion failure is not the intended negative result.

## Admission checklist (all required)
1. Direct scratch run establishes the exact sequence above; independent reviewer repeats it from their own scratch. Preserve any adverse scratch attempts as telemetry, not passing evidence.
2. Only after causal scratch, executor may edit only `corpus/fixtures/slider_adjust.gd` and `run_battery.py`; exactly one new ordinary case with exact expected terminal signature. Existing paths/arguments/signatures remain unchanged.
3. Named non-author verifier independently runs the full requested default-path battery and fault injection; compares all 56 pre-existing `(case, verdict, actual_exit, signature)` rows to r40 raw baseline, and nine opt-in groups by stable classifications/inner verdicts (not run-specific paths). Expect 55 ordinary + 2 mutants + 9 opt-ins = 66 total only if the one candidate row is causally admitted. Capture raw JSON byte-identically in `corpus/lessons/r41-focus-handoff-verifier.json` and separate fault result in `r41-fault-verifier.json`; establish tracked fixture/runner hashes unchanged during verification.
4. Exercise relevant focus/edge sabotage: it must fail at the relevant assertion, not masquerade as the intended terminal expected-negative.
5. Calibration improved only if the same-wiring focus-handoff contrast is observed and independently reproduced; depth and coverage unchanged as axes; no harmed axes. Otherwise HOLD/no admission.

## Scope and non-claims
This is limited to headless/synthetic parsed actions plus one process frame per event in Godot 4.7.2. It does not establish OS auto-repeat, physical keyboard/timing, rendered or pointer UI, accessibility, production behavior, or a generic HSlider guarantee. No engine/editor/seeded source mutation, publishing, commit, push, or merge by this scribe.
