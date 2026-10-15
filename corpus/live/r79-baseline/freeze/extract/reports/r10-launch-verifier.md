# Round 10 launch verifier (independent)

## Verdict: PASS, narrowly scoped

Named non-author verifier replayed the requested combined command:

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch`

Exit **0**, **32/32 PASS**. Raw battery JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T173815862058Z/verdicts.json`. Raw launch JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T173815862058Z/export-launch-verdicts.json`. Both raw records contain the complete export/launch command, captured outputs, exits/errors, signatures, artifacts, and cleanup inventory. I independently inspected the runner branch and JSON rather than relying on executor claims.

## Direct-launch evidence

Both separate scratch variants exported Linux/X11 successfully (export exit 0, observed `[ DONE ]` and `savepack`, executable size 73,703,800 bytes). Both were invoked directly as `<out>/fixture-launch.x86_64 --headless`, with `cwd=<variant>/out`; the out directory contained only the executable, `.pck`, and `.sh` at launch, and no `project.godot`, scene, or script. Each process exited 0 without error/timeout. Each export output is free of `EXPORT_LAUNCH_READY scene=fixture`.

- Positive raw record: `.../export-launch-verdicts.json`, result `export_launch_positive`. PCK 28,020 bytes, SHA-256 `139a3544864aa4699d13ebe48dff9e0c59958444cb722ace35c6ae23522eb55e`; launch output contains the exact token line once; same predicate **true**.
- Negative/control raw record: same JSON, result `export_launch_missing_startup_event`. PCK 27,956 bytes, SHA-256 `6ede44d02e41778690699c95d4122248e2bc22f7b7df17915ff32a6df1419a7c`; distinct PCK digest; launch exit 0, clean output, token count zero; same predicate **false**. It uses the same configured main scene and script, with only the event-print line omitted. The exact token is absent from negative script and source tree (excluding binary PCK); negative PCK is a separately exported artifact. Both products inventories were `[fixture-launch.pck, fixture-launch.sh, fixture-launch.x86_64]` and both `products_after_cleanup` are empty.

Runner predicate is shared for both variants: successful export, launch exit 0/no error, expected token in output, exactly one matching line, and no source project/script/scene in launch cwd. Overall launch probe also requires negative export success/nonempty executable, clean negative launch without token, different PCK digests, and empty cleanup inventories. No source-project/editor launch substitution detected.

## Adversarial scratch-only falsification

Copied fixture runner to disposable `/tmp` scratch and removed the event-print generation from the positive as well as control source. Replay `python /tmp/.../fixtures/run_battery.py --probe-export-launch --runs /tmp/r10-verifier-runs` exited **1**; both separately exported processes exited 0 but emitted no token, both same launch assertions were false, and launch meta verdict was **FAIL**. Raw falsification JSON (deleted after inspection): `/tmp/r10-verifier-runs/20261012T174004114109Z/export-launch-verdicts.json`. No repository fixture or runner was modified by this mutation. The scratch replay ran from `/tmp` so nested project fixture files were outside the staged project.

## Additional required replay and integrity

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection` exited **0**, meta PASS, raw record `.shokunin/game-dev-2d/corpus/live/runs/20261012T174030286217Z/fault-verdicts.json`: injected hang classified FAIL at 0.25 seconds, clean expected negative PASS, unrelated-error case FAIL.

Hashed all **37 tracked fixture/runner paths** immediately before and after verification; zero changes. No engine/editor/project source changes by verifier; only this report was written. Scratch evidence remains under ignored `corpus/live/runs/` for replay inspection; adversarial `/tmp` scratch was removed.

## Limits

This is a synthetic finite startup event on this host's Godot 4.7.2 Linux/X11 export in headless mode. It does not establish production-project launchability, visual correctness, GUI behavior, other platforms, publishing readiness, or asset rights. The token is stdout evidence for the fixture's `_ready()` event, not a test of gameplay.
