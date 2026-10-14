# Round 40 named non-author verifier — repeat-right focus absence

## Verdict: PASS; evidence supports the bounded focus-absence control

I independently verified the in-progress candidate; I did not author the fixture/runner changes. Godot 4.7.2.stable headless scratch paired replay used the same in-tree HSlider (min=0, max=10, step=1, initial=5), connected `value_changed` callback, and Label consumer in both arms. Each of these seven fresh parsed actions was followed by one process frame: `ui_right` pressed, `ui_right` pressed, `ui_right` released, `ui_left` pressed, `ui_left` released, `ui_left` pressed, `ui_left` released.

Focused arm (`--repeat-right`): before every edge slider was GUI focus owner; values were `6,7,7,6,6,5,5`, cumulative receipts ended `[6,7,6,5]`, and Label tracked each value. Exit 0.

No-focus arm (`--repeat-right --no-focus`): before every edge focus owner was not slider; after every edge value remained 5, receipts remained `[]`, and Label remained `Value 5`. It exited 2 only after all seven checks, with exact terminal diagnostic `SLIDER REPEAT NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,7,7,6,6,5,5`. This is a parsed synthetic-action/frame test, not physical keyboard, OS auto-repeat, rendered/pointer, accessibility, or production evidence.

## Full battery and baseline comparison

Full requested default-path command, with this verifier's explicit `--runs` directory:

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --runs .shokunin/game-dev-2d/corpus/live/r40-repeat-focus-verifier/runs --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

Exit 0, 65/65 PASS: 54 ordinary, 2 mutants, 9 opt-in probe groups. Compared with `corpus/lessons/r39-repeat-verifier.json`, all 55 prior rows with `(case, verdict, actual_exit, signature)` are exactly unchanged, mutants included. The nine opt-in groups retain their stable overall verdict and inner classifications (run-specific paths are expected to vary). Exactly one new ordinary case, `slider_adjust_repeat_right_no_focus`, PASS with actual exit 2 and the exact terminal signature above.

Full raw JSON: `corpus/live/r40-repeat-focus-verifier/runs/20261013T064518726275Z/verdicts.json`; copied byte-identically to `corpus/lessons/r40-repeat-focus-verifier.json` (SHA-256 `0de4471c784e5e69d5e3a384436f5a734fb7548e4824fe948d4822ffb8d51167`).

Separate `--fault-injection` run: outer harness exit 0/PASS; deliberate inner hang and unrelated-error cases FAIL, expected-negative case PASS. Raw `corpus/live/r40-repeat-focus-verifier/fault-runs/20261013T064635394074Z/fault-verdicts.json`, copied byte-identically to `corpus/lessons/r40-fault-verifier.json` (SHA-256 `68dbd098c882a2d09e688568201fbc335138d1553f5c8a909a6ff88e964d8620`).

## Adversarial checks, integrity, and caveats

- Scratch sabotage that assigns focus before no-focus edge 0 failed the per-edge focus assertion (`SLIDER repeat no-focus assertion failed before edge 0`), not the terminal expected-negative diagnostic.
- Scratch sabotage skipping a no-focus action still failed the focused positive edge check where run in the paired focused arm. A no-focus-only skipped event cannot be distinguished by that negative arm's intended invariant because no-focus actions leave value/receipts/Label unchanged; seven loop iterations and per-edge assertions are present in source. The focus-positive path does detect a skipped adjustment edge.
- Prior reviewer telemetry of a typed-array scratch error and an earlier failed/misclassified replay against an old fixture is retained as historical process telemetry only. It is not attributed to the candidate; the corrected independent replay and this full replay are the evidence.
- Tracked `slider_adjust.gd` and `run_battery.py` SHA-256 values were identical before and after verifier execution (`fedcf166aefb7386a2399bbccce6f0bded227023538e933ca76b1ad6ee21ec2b`, `d2df3ec96ba37032aa0cf9f39f9776e977bf69fa6191513ae6230115f14e2f18`). I made no tracked source changes, commit, push, or merge. Candidate-vs-r39 `git diff` reflects the declared change; verifier left it unchanged.
