# Round 23 named non-author verifier

## Full real-Godot replay

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

Exit 0, 48/48 PASS: 37 ordinary + 2 mutants + 9 opt-in probe records. All 46 prior case names and verdicts from `r22-timeout-verifier.json` are unchanged. Raw complete verdict JSON was copied byte-for-byte to `corpus/lessons/r23-left-verifier.json`. Godot 4.7.2.stable.arch_linux.

Left positive `camera_left_limit`: exit 0; active camera current, parent target moved to x=-2000; center matched authored limit -1000 plus viewport half-width (64px width, so -968), and differs from target. `camera_far_left_bound`: exit 2 as intended with center=(-2000,0), target=(-2000,0), expected clamp=-968, and the same intended left-bound center assertion. It was not a setup failure. Disposable scratch sabotage changed only the authored `limit_left` from -1000 to -100000; positive left mode then exited 2 with center following target and the same `camera limit assertion failed: expected active center within left boundary and distinct from target` assertion. Scratch: `corpus/live/r23-left-verifier-scratch/project`. This is headless center-state evidence, not rendered framing.

Tracked hashes before/after replay match: camera_limit.gd `4d86b802205b06527fd84af9f187dd7ad89ea34d12b42995a06620536d3c69ec`; run_battery.py `3f449c02d9539270875fd1a2bda01e37df7e39083fcfc1203f2e87836eef822f`. No tracked fixture/runner edits by verifier.

### Failures/adverse output

No ordinary case or full-battery verdict failed. Nested probes intentionally print inner `FAIL` statuses for their negative arms: `godot_error_unrelated` exit 1/classification false; `stream_reject` exit 0/classification false. Their top-level probe records PASS, as expected for rejection. Export had no adverse exit, launch, or classification: readiness/export-launch positive and missing-startup negative both passed, all exported products were cleaned, and launch positive emitted `EXPORT_LAUNCH_READY scene=fixture`. Godot emitted the existing warning about nested `res://controls/project.godot` being ignored during export; it did not alter success.

## Separate fault-injection meta run

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection`; exit 0, top-level meta PASS. Raw JSON copied byte-for-byte to `corpus/lessons/r23-fault-verifier.json`. Its inner `fault_hang` is FAIL (`actual_exit=null`, `TIMEOUT after 0.25 seconds`) and `fault_unrelated_error` is FAIL (exit 2), which are intentional adversarial inputs, not relabeled as successes; `fault_clean_expected_negative` PASS. This meta run is separate from the 48-case full battery.

No delegation, commits, or publication.
