# Round 58 process baseline — independent seven-flag replay

## Result
PASS: the exact seven declared r57 flags replayed successfully in a fresh run-local scratch. All 83 old case/script/flags keys are present and all 83 match their prior `expected_exit`, `actual_exit`, `signature`, `verdict`, and `error` classifications (83/83). This is a baseline replay only; it does not establish the newly declared independent-process claim.

## Method and evidence
I made no tracked edits and did not delegate. Godot reported 4.7.2.stable.arch_linux.ed1daf0bf. Exact command (exit 0):
```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs '.shokunin/game-dev-2d/corpus/live/r58-process-baseline/seven-flag-runs'
```
Raw result: `.shokunin/game-dev-2d/corpus/live/r58-process-baseline/seven-flag-runs/20261013T131526768618Z/verdicts.json` (overall verdict `PASS`, 83 rows, all PASS). Exact prior raw: `.shokunin/game-dev-2d/corpus/lessons/r57-save-non-author.json` (83 rows, PASS). Comparison key was `(case, script, flags)`; classification fields compared were `expected_exit`, `actual_exit`, `signature`, `verdict`, and `error`. No mismatches.

The save positive and malformed-JSON negative remain classified PASS, with respective actual exits 0 and 2. Positive output records an absolute `user://` path under this run's `xdg-data` directory: `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r58-process-baseline/seven-flag-runs/20261013T131526768618Z/xdg-data/godot/app_userdata/MechanicOneShotTest-20261013T131526768618Z/r57-save.json`. The present fixture baseline is not evidence of a writer-exits/independent-reader process boundary.

Source hashes (read-only, before/after this replay): `run_battery.py` `b3d721f923feda6b04b9cc9b78278f5b41c1e7a9df4e3215eb13e73505f982a8`; `save_roundtrip.gd` `ba66befa6d41d6eeb99001183e67e88422288bebc8b0d0295117ea2cb909dfea`. No LOG/SCORECARD/prior receipt/other lane edits; no commit/push/merge/publish.
