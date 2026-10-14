# Round 14 — case-scoped ObjectDB leak warning calibration

Reproduce with Godot 4.7.2: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-audio-warning` → independent non-author verifier **38/38 PASS** (`r14-warning-verifier.json`), including 31 ordinary cases, four unrelated-error probes, export launch, actual-Godot error, and the new audio warning meta record. `--fault-injection` meta PASS (`r14-fault-regression.json`). Named verifier `.shokunin/game-dev-2d/reports/r14-warning-verifier.md`.

| Captured positive `audio_playback` output | Earlier shared classifier | New production audio-only classifier |
|---|---|---|
| R12 actual Godot output in `r12-initial-hold.json`: exit 0 and correct playback signature, plus `WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).` | PASS despite warning, causing initial R12 verifier HOLD | FAIL; anchored warning grammar checked alongside existing exit/signature/ERROR rules |
| R12 clean non-author capture `r12-battery-verifier.json`: same exit/signature, no ObjectDB warning | PASS | PASS |
| Current live clean audio | PASS | PASS |
| Export readiness/missing-preset with `WARNING: Detected another project.godot at res://controls. The folder will be ignored.` | PASS | PASS; export uses unchanged general classifier |

The first executor draft missed the Godot verbose-details suffix; the second draft misplaced punctuation inside the parenthesis. Critic and parent caught these errors, then the executor matched the actual raw warning line and reran; the adverse history is in `reports/r14-warning-executor.md` and `reports/r14-warning-critic.md`. Verifier disabled `and not leaked_objectdb` only in a disposable `/tmp` runner, making the warning meta and battery FAIL. Adding an unrelated warning to clean capture still passed; adding a matching ObjectDB warning with count 3 failed. The meta uses **captured real Godot output** from R12, not newly emitted leaks or synthetic game behavior; those scratch data mutations are classifier controls. All 40 tracked fixture hashes remained unchanged during independent verification. This does not detect all leaks, every warning grammar, other cases, or output stream provenance.
