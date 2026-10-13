# Round 44 second-focus-restore executor report

## Claim and scratch-first evidence
Real Godot `4.7.2.stable.arch_linux.ed1daf0bf` scratch replay, connected in-tree HSlider range 0..10 step 1 initial 5, Button focus target. First ran unchanged r43 `--repeat-right --second-focus-loss`; observed seven-edge expected negative (exit 2 after checks): values `6,6,6,5,5,5,5`, receipts `[6,5]`, Labels Value 6 / Value 5. Then scratch-only nine-edge candidate restored slider focus before edge 7 (third fresh left press), checking focus owner before every edge and value, receipt history, and Label after each edge. `--repeat-right --second-focus-restore` exited 0: values `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, Labels Value 6 / Value 5 / Value 4.

## Integrated additive change
Added a separate `--second-focus-restore` fixture branch (requires BOTH `--repeat-right` and `--second-focus-restore`) and one positive `slider_adjust_repeat_right_second_focus_restore` runner row plus classifier entry. Existing r43 `--second-focus-loss` branch, runner row, and exact expected-failure classifier remain byte-for-byte present. The first integrated replay was stopped before completion after recognizing an edit that replaced r43; scratch artifacts remain at `corpus/live/runs/20261013T072845553725Z/` with no `verdicts.json` (interrupted, not a verdict). Corrected edits were inspected with `git diff` before replay.

## Verification
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py` exited 0; raw JSON `corpus/live/runs/20261013T073023219652Z/verdicts.json` says PASS, 58/58 ordinary cases (57 prior ordinary rows plus the new r44 positive row; no opt-ins or mutants in this default run). All 57 prior ordinary rows passed; r43 expected-negative remained exit 2 and PASS; new positive exit 0 and PASS. This is additive versus r43's 57 ordinary / 68 full baseline (including mutants and opt-ins); corresponding expected full total is 69 if those same optional modes are run. No opt-in replay performed in this executor turn.

## Scope and limits
This is headless synthetic parsed actions plus frames. It verifies focus owner and observable state, not internal consumption of unchanged edges. It does not establish OS auto-repeat, physical keyboard/timing, rendered or pointer UI, accessibility, or production behavior. No engine/editor/seeded edits, commit, push, or merge.
