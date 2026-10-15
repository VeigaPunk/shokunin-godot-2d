# Round 7 fault verifier (named non-author)

## Independent replay

I independently ran both requested commands from the repository root:

- `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection` → exit 0 in 0.296 s. Raw JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T170528770300Z/fault-verdicts.json`.
- `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → exit 0 in 13.980 s; top-level PASS, 25/25 PASS (23 ordinary seeded cases plus both existing mutants). Raw JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T170539762746Z/verdicts.json`.

Fault-mode raw results:

| case | actual exit | inner verdict | error / output | elapsed |
|---|---:|---|---|---:|
| `fault_hang` | null | FAIL | `TIMEOUT after 0.25 seconds`; captured `FAULT_HANG_STARTED` | 0.252 s |
| `fault_clean_expected_negative` | 2 | PASS | exact `ERROR: expected negative diagnostic` | 0.006 s |
| `fault_unrelated_error` | 2 | FAIL | expected diagnostic plus `ERROR: unrelated engine failure` | 0.006 s |

Fault-mode top-level verdict is PASS only when the expected inner verdicts and expected output markers match. Timeout remained finite and below 2 seconds, with `actual_exit: null`, TIMEOUT error, and inner FAIL. The clean expected negative remains accepted; adding a distinct unrelated ERROR changes it to FAIL.

## Classifier-use check and falsification

Inspected `run_battery.py`: ordinary `execute()` cases pass through `run_process()` and the shared `classify_process()`; the fault branch calls those same functions rather than a duplicated test classifier. The expected-error allowlist is applied by that classifier to normal cases as well. This is consistent with the 25/25 replay, including the intentional-error negatives and both mutation controls.

Scratch-only falsification: copied the runner to `/tmp/r7-classifier-falsify-3djopbkr/fixtures/`, modified only that copy so the classifier always returns true, then ran its fault mode. The unrelated-error inner record became PASS and the overall fault mode correctly exited 1 / reported FAIL. Scratch raw JSON: `/tmp/r7-classifier-falsify-3djopbkr/runs/20261012T170609732253Z/fault-verdicts.json`. This demonstrates the fault probe depends on the shared classifier outcome, not merely matching the expected printed substrings. Scratch files are outside the repository and are not submitted as fixtures.

## Integrity, scope, and verdict

Hashed the 35 tracked fixture files other than the runner before and after replay; all 35 hashes were unchanged. The tracked runner hash was also unchanged by verification. No fixture or runner changes were made by this verifier. The worktree's pre-existing executor/LOG changes were left untouched. I did not commit or delegate.

Verifier finding: requested timeout and unrelated-engine-ERROR behaviors are reproduced, ordinary battery and known negatives/mutants remain green, and scratch falsification rejects a sabotaged classifier. This supports the Round 7 fault-detection claim for these injected cases; it does not establish coverage of every possible timeout, diagnostic, Godot version, or export path.
