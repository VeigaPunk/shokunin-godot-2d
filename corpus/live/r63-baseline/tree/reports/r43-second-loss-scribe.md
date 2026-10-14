# Round 43 second-loss scribe — evidence and admission checklist

## Declared claim
Calibration candidate: repeat the r42 seven-event HSlider history but transfer focus back to the Button before the second left press. With the same connected signal consumer, expected values are `6,6,6,5,5,5,5`, receipts `[6,5]`, and corresponding Labels `Value 6, Value 5`; terminal expected-negative exit 2 only after all seven edge checks. Paired positive contrast is r42: final value 4, receipts `[6,5,4]`. Before-state: r42 has 56 ordinary / 67 full cases. Proposed addition is one negative ordinary row, 57 / 68, only if causal and verified.

## Scratch evidence reviewed
- Scout raw artifacts: `corpus/live/r43-second-loss-scout/{probe.gd,project.godot,run.log,exit-code}`. The run log identifies Godot 4.7.2.stable and shows all seven expected owner/value/receipt/Label states, followed by `R43_EXPECTED_NEGATIVE_CONFIRMED`; recorded process exit is 2.
- Sequence: slider right press→`6/[6]/Value 6`; Button right press and release hold; restored slider left press→`5/[6,5]/Value 5`, release holds; Button reacquires focus before second left press, which and its release hold `5/[6,5]/Value 5`.
- Scout reports a connected in-tree HSlider, Label callback, and focusable Button; fresh parsed action per edge and one process frame. This matches the r42 positive contrast in `reports/r42-focus-restore-verifier.md` and the r42 depth scratch.
- The separate `corpus/live/r43-second-loss-direct-scratch` is a pre-existing collection of unrelated mechanics probes and is not evidence for this claim. Use the named scout artifacts above.

## Admission checklist — not yet complete
- [x] Standing brief and r43 LOG claim reviewed; axis is calibration; scope and HOLD condition noted.
- [x] Real Godot 4.7.2 scratch preceded fixture/battery candidate edits; observed second focus loss matches the declared hypothesis.
- [ ] Confirm only the intended `slider_adjust.gd` branch and one negative `run_battery.py` case were added, after scratch; no engine/editor or seeded corpus edits.
- [ ] Named non-author verifier replays the complete default-path battery and confirms all 58 prior r42 tuple rows unchanged, nine opt-ins have stable comparable classifications, and exactly one new expected-negative exit-2 row is present (57 ordinary / 68 full).
- [ ] Verifier checks fault-injection behavior and targeted sabotage rejects missing second transfer / missing first adjustment before terminal expected-negative classification.
- [ ] Preserve raw byte-identical lesson, report, scratch output, and tracked hashes; report-last commit only by parent if admitted. No push/merge.

## Scope and verdict boundary
The scratch supports the bounded focus-loss calibration claim for synthetic parsed actions plus process frames in headless Godot. It does not establish OS auto-repeat, physical keyboard timing, rendered/pointer UI, accessibility, production behavior, internal consumption of unchanged edges, or generic slider behavior. No axis verdict or admission is claimed here: full non-author verification is pending. HOLD if replay, tuple comparison, sabotage, or candidate causality differs.
