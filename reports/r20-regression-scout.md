# Round 20 regression scout — runner flags and export adverse telemetry

Read-only scope: runner CLI/regression surface and prior export-path caveat. No fixture or runner edits made.

## Observed CLI surface

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --help` (exit 0).

The parser exposes `--probe-failing`, `--fault-injection`, `--probe-unrelated-error`, `--probe-export-launch`, `--probe-godot-error`, `--probe-stream-attribution`, `--probe-audio-warning`, `--godot GODOT`, and `--runs RUNS`. It does not expose a top-edge-only/regression selection: ordinary `CASES` run as a whole. `--probe-failing` adds two scratch mutations; `--fault-injection` is a separate early-return mode. The parser default for `--runs` is `HERE.parent / "live" / "runs"` (absolute when `HERE` is resolved); therefore no explicit `--runs` is the known default-path replay. Standard final artifact is `verdicts.json`; export launch and stream/Godot-error diagnostic probes add separate artifacts.

The current runner ordinary list includes paired `camera_follow`/`camera_no_follow` and `camera_limit`/`camera_far_bound`. The latter's existing negative signature is specifically a right-bound assertion. Round 19 records the independent verifier command as `--probe-failing`; it reported 42/42 (33 ordinary + 2 mutants + 6 previous opt-in + stream attribution). Round 20 declared a target of 35 ordinary cases after adding two top-edge rows; I did not run that replay.

## Export caveat / regression telemetry

`corpus/lessons/r16-export-adverse.json` records a real Godot 4.7.2 `export_readiness` failure: exit 1, `ERROR: Prepare Template: The given export path doesn't exist.`, zero-byte/no products, while the adjacent `export_preset_missing` negative correctly reports the invalid preset. `corpus/lessons/r17-export-path-hold.md` states that later bounded scratch exports passed, no cause was isolated, and explicitly says not to auto-retry or replace an adverse record. It notes relative `--runs` for the adverse run versus absolute `/tmp` roots on passing replays as a confounded difference, not a proven cause.

New same-round telemetry received from parent: a baseline using an explicit relative `--runs` failed inside `--probe-unrelated-error` with `StopIteration` at runner line 245 (`next(line for line in output.splitlines() if "savepack" in line)`). Parent says it will rerun with default absolute `--runs`. This is an observed harness exception, not evidence that a changed top-edge probe failed, and not proof of a causal link to r16. Do not fold an export-path/classifier fix into the top-coverage move; retain the failure as adverse evidence and compare the parent's default-path rerun separately. Positive export remains fail-closed; the prior negative invalid-preset case is a separate contract.

Relevant source location inspected: `corpus/fixtures/run_battery.py` around export classification / `--probe-unrelated-error` (export classifier requires exit 0, `[ DONE ]`, `savepack`, and a nonempty artifact; diagnostic probe assumes a `savepack` line exists when constructing same-line spoof variants). No mutation performed.

## Commands and scope

- `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --help` — exit 0, flags recorded above.
- Read `corpus/lessons/r16-export-adverse.json`, `corpus/lessons/r17-export-path-hold.md`, `corpus/lessons/r19-stream-verifier.json`, round 20 LOG declaration, and the current runner. No Godot replay was run by this scout; no tracked files other than this report were written.
