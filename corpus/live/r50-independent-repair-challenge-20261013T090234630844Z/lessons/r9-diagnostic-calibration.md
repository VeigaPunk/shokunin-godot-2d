# Round 9 — export and mutant diagnostic calibration

Reproduce on Godot 4.7.2: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error` → independent 31 records PASS, consisting of the prior 27 cases and four opt-in classifier checks (`r9-diagnostic-verifier.json`). `--fault-injection` remains meta PASS (`r9-fault-regression.json`). Named non-author verifier: `.shokunin/game-dev-2d/reports/r9-diagnostic-verifier.md`.

| Real captured case output | Clean decision | Modified captured text / decision |
|---|---|---|
| Linux/X11 scratch export: exit 0, `[ DONE ]` and `savepack`, nonempty 73,703,800-byte artifact then deleted | PASS | appended unrelated `ERROR:` and same-line prefix/suffix: classifier false |
| Invalid preset: observed exit **1** (prior CASES expected 2 but special branch ignored it), exact `ERROR: Invalid export preset name: Missing preset.`, no artifact | PASS with declared exit 1 | unrelated appended `ERROR:` and same-line suffix: classifier false |
| Broken scene-route mutant and removed level polygon mutant, each exit 2 with owned expected diagnostic | detected | unrelated appended `ERROR:` and same-line prefix/suffix: classifier false |
| Verifier disables unrelated-error filtering in disposable `/tmp` runner copy | no clean runner changes | all four probe meta verdicts FAIL, battery exits 1 |

Export special branches now call shared `classify_process` with artifact/signature checks; mutants factor the production `classify_mutant(candidate_output)` used by ordinary detection and opt-in modifications. The opt-in checks alter *captured strings* after real Godot commands; they do not inject an error into a Godot process. The positive export is scratch artifact evidence, not app launch. Exact valid ERROR allowances remain case-owned; `SCRIPT ERROR:` and `Parse Error:` fail. The verifier hashed all 37 tracked fixture/runner paths unchanged before/after replay. Other Godot diagnostic formats and real stderr faults remain unproved.
