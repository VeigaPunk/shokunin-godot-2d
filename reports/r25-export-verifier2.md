# Round 25 second independent export verifier

## Scope and runner diff

I made no code/fixture edits and did not spawn or delegate. Against `HEAD`, the only `run_battery.py` changes are the two export destinations made absolute: readiness `export_path = (out_dir / "fixture.x86_64").resolve()` and launch `executable = (out_dir / "fixture-launch.x86_64").resolve()`. No changes to classifier, expected exits/signatures, missing-preset branch, export/product cleanup, ordinary case table or seeded fixtures. Both export destinations are resolved before Godot receives them.

## Explicit-relative full battery

Ran from repo root:

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --runs .shokunin/game-dev-2d/corpus/live/r25-verifier2-relative --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

Exit 0; **50/50 outer records PASS**. This independently repeats the prior first-fix adverse case after the second call-site correction. `export_readiness` passed (exit 0; executable 73,703,800 bytes, SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`). `export_preset_missing` correctly produced exit 1 and `ERROR: Invalid export preset name: Missing preset.` and was classified PASS (expected negative; not a process-success claim).

The separate `probe_export_launch` outer row passed. Its detail raw shows both independent scratch exports exit 0 and create 73,703,800-byte executables with the same hash. Positive binary launch exits 0 and prints `EXPORT_LAUNCH_READY scene=fixture`; missing-startup-event control exits 0 and emits no token. Both product directories are empty after cleanup. Thus the first replay's two relative-target launch failures are not repeated here.

The 50-row raw JSON was copied byte-for-byte to `corpus/lessons/r25-export-verifier2.json` (98,577 bytes; SHA-256 `5a4a00cb686155a1b64237c5e0ff767ef4113f3475e27fe55c3bdee108641bab`). Export-launch details are byte-identical at `corpus/lessons/r25-export-launch-verifier2.json` (24,803 bytes; SHA-256 `4f4d0475a9e761bed7973498c8671a1c3e25283930b89122e89f3626369310b2`). The earlier verifier's adverse 49/50 raw and reports remain untouched.

## Separate fault injection and absolute-root control

`--fault-injection` exited 0/meta PASS; inner timeout and unrelated-error cases were FAIL, clean expected-negative was PASS. Raw copied byte-for-byte to `corpus/lessons/r25-fault-verifier2.json` (1,153 bytes; SHA-256 `68dbd098c882a2d09e688568201fbc335138d1553f5c8a909a6ff88e964d8620`).

A separate absolute-root ordinary control (`--runs /tmp/r25-verifier2-absolute-ordinary --probe-failing`) exited 0 with 39/39 PASS, including readiness and expected missing-preset classification. This is a control replay, not the basis for or a general reliability claim.

## Integrity and scope

All 45 tracked fixture/runner files were hashed before/after; every digest matched. The runner's current SHA-256 is `ab0d0352445113b2ba7f742b57500f97e62b2196411f96fe7f8b594e69cdab41`. Exact commands, cwd, outputs, paths, raw hashes, and artifact facts are retained in my scratch under `corpus/live/r25-verifier2-relative/` and `corpus/live/r25-verifier2-fault/` (additional absolute control scratch under `/tmp`).

This is one full synthetic fixture replay confirming both current relative export call sites and the expected missing-preset failure behavior. It does not establish general or production export reliability or resolve other historical intermittent export failures. No commit, push, or merge.
