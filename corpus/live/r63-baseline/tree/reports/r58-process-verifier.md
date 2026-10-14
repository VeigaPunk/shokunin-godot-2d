# Round 58 named non-author process verification

## Verdict

**PASS for the bounded declared claim.** I ran the seven declared flags (not `--probe-audio-warning`) under Godot 4.7.2. The fresh battery has 87 rows and verdict `PASS`; its opt-in probes intentionally include inner `FAIL` classifications while asserting classifier behavior. Exactly the 83 old records were found and their `case`, `script`, `flags`, `expected_exit`, `actual_exit`, `signature`, `verdict`, and `error` fields match the Round 57 receipt (0 differences). Four new records are the writer, reader, missing-file negative, and process meta probe.

## Commands and retained evidence

Seeded command (exit 0):

```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot --runs .shokunin/game-dev-2d/corpus/live/r58-process-verifier/full-runs --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Unique run: `.shokunin/game-dev-2d/corpus/live/r58-process-verifier/full-runs/20261013T132838657775Z/`. Raw command stdout/stderr/exit are `full-run.stdout` (exit 0), `full-run.stderr` (empty), and `full-run.exit` (`0`). Raw receipt is `verdicts.json` (SHA-256 `9d3b1587cb0beebc9124b2e98d57922bfe1d7f44471a3645f42be343fcafb440`); process evidence is `save-process-verdicts.json` (SHA-256 `503acfbcd1d01330c0fece528c515bb48fb24a4a7a6bedd22bca6da9d27cf4d4`). The runner loop executes cases synchronously in declared order; each process record captures command/PID/output/exit, and process meta checks same copied project path, absolute XDG, script, PID distinction and containment. The raw receipt's writer/reader commands are distinct Godot invocations with `--script res://save_process.gd` and respectively no mode vs `--reader`; missing is a third command with `--missing`.

Writer PID 3256826 exited 0 before the subsequent reader launch; reader PID 3256864 exited 0. Both used the same copied project `.shokunin/game-dev-2d/corpus/live/r58-process-verifier/full-runs/20261013T132838657775Z/scratch`, same app identity `MechanicOneShotTest-20261013T132838657775Z`, and absolute `XDG_DATA_HOME=/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r58-process-verifier/full-runs/20261013T132838657775Z/xdg-data`. Both output the exact same globalized target `.../xdg-data/godot/app_userdata/MechanicOneShotTest-20261013T132838657775Z/r58-process-save.json`; writer reports completion after close. The reader opens it in READ mode, parses JSON, checks exact nested dictionary/array/bool/float values, and emits its success signature only after comparison. The artifact's three process PIDs are distinct (writer 3256826, reader 3256864, missing 3256911). The missing invocation used separate `r58-process-missing.json`; its output explicitly proves absence before returning the expected `FILE_NOT_FOUND` error and exit 2. It cannot pass from writer's file.

Previous receipt: `.shokunin/game-dev-2d/corpus/live/r57-save-verifier/corrected-seven-flag-runs/20261013T131017016504Z/verdicts.json`.

## Adverse/sabotage evidence

Fault injection was a distinct command and unique path; it was not part of battery coverage:

```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot --runs .shokunin/game-dev-2d/corpus/live/r58-process-verifier/fault-injection --fault-injection
```

Exit 0; receipt `.shokunin/game-dev-2d/corpus/live/r58-process-verifier/fault-injection/20261013T132940828954Z/fault-verdicts.json` reports overall `PASS`: hang timed out (inner `FAIL`, no exit), clean expected negative exit 2 (`PASS`), unrelated-error case exit 2 (inner `FAIL`). Raw captured invocation logs are `fault.stdout`, `fault.stderr` (empty), `fault.exit` (`0`).

Scratch-only sabotage copied the run's project to `.shokunin/game-dev-2d/corpus/live/r58-process-verifier/sabotage/`. Wrong expected value: modified only copied reader expectation from `Ada` to `Wrong`, used the real run's writer save and same absolute run XDG; Godot exited 2 with `SAVE PROCESS ASSERTION FAILED: independent reader mismatch` (not the required reader-success signature, hence classifier mismatch). Missing-file existence: seeded only the copied missing XDG's `r58-process-missing.json`, then ran its separate `--missing` reader; it exited 2 with `SAVE PROCESS ASSERTION FAILED: missing file existed` before emitting the expected-negative signature. Exact outputs/exits and copied projects are retained in `sabotage/wrong-value/` and `sabotage/missing-exists/`. No sabotage can be mistaken for a clean negative.

## Integrity and limits

Before and after seeded/fault/sabotage work, `corpus/fixtures/run_battery.py` SHA-256 remained `571261e4ceec4fc6ab2b0883ebe0a49ca474198449a0bde439e4a8244bb6e9be`; `corpus/fixtures/save_process.gd` remained `25ad005a207abf95f81be7e9d3cfb51af98831cc42e71287a3a6e55c1ea05020`. No tracked fixture/runner, LOG, SCORECARD, prior receipt, or other report was edited; no commit/push/merge. One early scratch sabotage invocation accidentally passed relative XDG, which Godot ignored and fell back to account data; it is preserved in the same adverse scratch output and excluded from evidence. Corrected sabotage invocations use absolute paths and were contained in assigned scratch.

This establishes only orderly headless Godot 4.7.2 JSON write, process exit, subsequent independent read/structural check, and the designated missing-file negative in this runner/project setup. It does not establish power-loss/crash durability, fsync guarantees, atomicity, arbitrary-corruption detection, production persistence, or other-platform behavior.
