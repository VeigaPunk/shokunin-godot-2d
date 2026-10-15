# Round 40 repeat-right no-focus executor report

## Scratch measurement and change

Before editing tracked files, ran the proposed `--repeat-right --no-focus` sequence in a copied Godot 4.7.2 project. With the same in-tree HSlider (0..10, step 1, initial 5), connected `value_changed` callback and Label, omitting `grab_focus` left focus owner null. Seven fresh parsed action events, each followed by a process frame (right pressed, right pressed, right release, left pressed, left release, left pressed, left release), measured value 5 at every edge, receipts `[]`, and Label `Value 5`. It did not acquire focus. This supports the expected-negative focus-absence control; it makes no OS auto-repeat or physical timing claim.

Added `--repeat-right` handling for `--no-focus`: require no slider focus before each edge, assert value=5/receipts[]/Label Value5 after every edge, then emit expected diagnostic and exit 2 only after all seven edges. Focused repeat positive remains the existing 6,7,7,6,6,5,5 and `[6,7,6,5]` receipt behavior. Added exactly one ordinary battery row `slider_adjust_repeat_right_no_focus` and the corresponding exact expected-error classifier. Only `slider_adjust.gd` and `run_battery.py` were edited. A preliminary run against the unmodified tracked script was retained in scratch; it stopped at its existing focused-only repeat focus assertion, so it is not treated as outcome evidence.

## Replay evidence

Direct real-Godot commands:

- `godot --headless --path .shokunin/game-dev-2d/corpus/fixtures --script res://slider_adjust.gd -- --repeat-right --no-focus` → exit 2, prints seven fives, receipts `[]`, Label `Value 5`, `focus_owner=<Object#null>`, then exact expected diagnostic.
- Same command without `--no-focus` → exit 0, existing focused positive output unchanged.

Author default battery: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --runs .shokunin/game-dev-2d/corpus/live/r40-repeat-focus-executor-scratch/runs` → exit 0, all 65 rows PASS (54 ordinary, 2 mutants, 9 opt-ins). Raw verdicts: `corpus/live/r40-repeat-focus-executor-scratch/runs/20261013T063652767000Z/verdicts.json`.

Full author replay with `--probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → exit 0, battery PASS, 65 total rows. Raw verdicts: `corpus/live/r40-repeat-focus-executor-scratch/full-runs/20261013T063736973967Z/verdicts.json`. All 55 prior ordinary/mutant result tuples `(case, verdict, actual_exit, signature)` match the r39 verifier baseline exactly when the newly inserted row is excluded; the new row is the sole added case. Prior opt-in probe inner outcomes also remain PASS/expected-negative as before.

Scratch corpus is under `corpus/live/r40-repeat-focus-executor-scratch/`; no seeded fixture controls or engine/editor source were changed. No commits, pushes, or merges.

## Verdict and scope

Calibration improves: same-wiring focus-absence control now tests the longer repeated seven-edge event history, with no adjustment or signal/Label changes at any edge, contrasted against the unchanged focused positive. Depth and coverage unchanged as axes; no observed regression in finite full replay. The evidence is limited to synthetic fresh `InputEventAction` events and a process frame per edge in headless Godot 4.7.2. It does not establish OS keyboard auto-repeat, physical timing, rendered/pointer behavior, accessibility, production behavior, or a generic HSlider guarantee. Constants changed: ordinary count 53→54, full count 64→65; all existing slider range/step/event histories and existing expected outcomes unchanged.
