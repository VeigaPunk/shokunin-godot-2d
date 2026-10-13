# Round 11 — real Godot-emitted expected and unrelated errors

Reproduce on Godot 4.7.2: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error` → independent **33/33 PASS** (`r11-battery-verifier.json`); paired subprocess record `r11-godot-error-verifier.json`. Named non-author verifier `.shokunin/game-dev-2d/reports/r11-godot-error-verifier.md`. `--fault-injection` remains meta PASS (`r11-fault-regression.json`); launch regression in `r11-launch-regression.json`.

| Actual headless Godot command path | Raw observation | Shared production classifier |
|---|---|---|
| `godot --headless --path <scratch> --script res://godot_error_probe.gd --` | exit **1**, exact `ERROR: EXPECTED_NEGATIVE: deliberate assertion rejected` once, Godot callsite/backtrace; no timeout | true: case-owned exact expected diagnostic |
| Same script with `--unrelated-error` | same exit **1** and expected line once, plus exact real `ERROR: UNRELATED_FAULT: unrelated engine diagnostic` once with its own backtrace | false: unrelated ERROR not allowed |
| Verifier disables unrelated ERROR filtering in disposable `/tmp` runner | both inner true | meta FAIL / overall exit 1 |
| Verifier suppresses second `push_error` in disposable `/tmp` fixture | no unrelated diagnostic | meta FAIL / overall exit 1 |

Both runs have identical expected signature and exit contract; only the runtime flag differs. The two diagnostics are emitted by actual Godot `push_error`, not altered captured strings. The runner combines captured stdout/stderr; stream attribution is **not established**. The 8s subprocess bound applies to both. This proves one Godot diagnostic path, not every error type, crash, export fault or gameplay behavior. Existing seeded fixtures were not edited; verifier's runner/new fixture hashes unchanged before/after.
