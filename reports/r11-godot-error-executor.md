# Round 11 real-Godot diagnostic executor

Implemented the opt-in `--probe-godot-error` path in `corpus/fixtures/run_battery.py` and added only `corpus/fixtures/godot_error_probe.gd`. The fixture is copied into the battery's scratch project with the other fixtures. It uses real `push_error()` calls; both variants invoke the same script, with the second passing `--unrelated-error`. The runner records each command, expected/actual exit, signature, classifier result, raw combined stdout/stderr and lines in `godot-error-verdicts.json`. The exact expected `ERROR:` line is the sole case-owned allowance passed to the production `classify_process` function. Meta PASS requires clean inner PASS, fault inner FAIL, both exact expected diagnostic lines, the unrelated diagnostic in fault output, and matching script/exit/signature.

## Evidence

Godot: `4.7.2.stable.arch_linux.ed1daf0bf`.

Command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --runs /tmp/r11-full
```

Process exit: **0**. Meta battery: **PASS**. Full run evidence: `/tmp/r11-full/20261012T174643320026Z/verdicts.json`; paired process evidence: `/tmp/r11-full/20261012T174643320026Z/godot-error-verdicts.json`.

Inner subprocesses, both actually run by Godot:

- `godot --headless --path /tmp/r11-full/20261012T174643320026Z/scratch --script res://godot_error_probe.gd --` — exit **1**, no launch/timeout error, production `classify_process` **true**. Raw output includes `ERROR: EXPECTED_NEGATIVE: deliberate assertion rejected`, followed by Godot's `push_error` location and GDScript backtrace.
- Same command plus `--unrelated-error` — exit **1**, no launch/timeout error, same expected signature and expected diagnostic, plus real `ERROR: UNRELATED_FAULT: unrelated engine diagnostic` and its own location/backtrace. Production `classify_process` **false**.

Both processes use the same script, expected exit 1, signature `EXPECTED_NEGATIVE: deliberate assertion rejected`; only the second receives the unrelated-error flag. This intentionally models the existing negative fixtures' nonzero exit. The transcript records actual combined stdout/stderr as well as exact ERROR lines. There is no captured-output editing in this probe.

Regression command above also preserved the opt-in failing-mutant, unrelated-error and export-launch probes. Final battery exit was 0; all 27 seeded cases, two mutants, unrelated-error probes, export launch probe and Godot diagnostic meta-case passed. Existing `--fault-injection` was separately re-run:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection --runs /tmp/r11-fault-regression
```

Exit **0**, `PASS fault injection`; artifact `/tmp/r11-fault-regression/20261012T174541583504Z/fault-verdicts.json`.

## Scope and limits

The paired cases establish this real Godot diagnostic classification behavior for this fixture/process on the installed Godot version. They do not establish general stderr behavior, gameplay or crash coverage. I did not change engine/editor sources or existing seeded fixtures, and did not delegate, commit, or push. Existing `--probe-failing`, `--probe-unrelated-error`, `--probe-export-launch`, and `--fault-injection` options remain present.
