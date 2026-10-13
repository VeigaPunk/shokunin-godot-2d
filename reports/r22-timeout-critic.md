# Round 22 timeout critic — read-only falsification

## Scope and verdict

Read-only review of the in-progress opt-in `--probe-timeout` in `corpus/fixtures/run_battery.py` and its `timeout_probe.gd`. I did not edit the runner or fixture. On Linux (`sys.platform=linux`) with `godot --version` reporting `4.7.2.stable.arch_linux.ed1daf0bf`, I independently exercised the copied scratch script. I found no false-PASS path in the submitted gates for the stated, narrow direct-child timeout claim. The probe is useful calibration evidence if the named verifier replays the complete battery and confirms raw artifacts. It does not establish process-tree cleanup or general hang detection.

## Independent scratch checks

Scratch only: `.shokunin/game-dev-2d/corpus/live/r22-timeout-critic-scratch/`.

- Positive command, exact script `res://timeout_probe.gd`, no hold flag: returned `0` in 0.394s; stdout included `TIMEOUT_PROBE: expected signature`, stderr empty. This matches `classify_process(... expected_exit=0 ...) == True`.
- Reject command used that same script and `-- --hold-open`, with a 0.75s `communicate` deadline. It timed out at 0.753s; captured output already contained the same marker; `poll()` showed the direct child still running at timeout. After `kill()` and bounded `communicate(timeout=3)`, it exited `-9` and `poll()` was not `None`. Timeout/error plus `actual_exit=None` make the inner process classifier false despite the marker. `cleanup_exit_code=-9` is correctly separate from the timeout observation (`actual_exit=None`).
- Scratch script contents implement normal `quit(0)` and hold-open `create_timer(30.0)` arms; no seeded control or source/editor files touched.

## Falsification review

- **Marker after timeout:** For the expected hanging arm, the marker is captured from `TimeoutExpired.stdout` before the probe kills the child; same-marker predicate therefore really is satisfied. If no marker is emitted/captured, `same_marker`/`marker_observed` prevents meta PASS. The normal arm separately needs marker and expected exit.
- **Classification:** Reject classification receives a non-null `TIMEOUT after 0.75 seconds` error even when signature is present, so `classify_process` cannot pass it. Meta PASS also requires timeout flag, still-running-at-timeout observation, `actual_exit is None`, exact timeout error, no live direct child after cleanup, and same script/marker/expected code. A cleanup failure or launch/read error changes the error and fails the meta gate.
- **Stale process:** Independent timeout run confirmed direct child was killed/reaped (`returncode=-9`, `poll()` non-None). Runner has bounded cleanup, retry cleanup in `finally`, and records whether direct child remains. It does not inspect descendants; correctly excluded from claim.
- **Setup failure / wrong script:** Launch errors, missing marker, early exit, parse/script error, or unexpected normal exit cannot satisfy both arms' classification and reject predicates. `same_script` compares the literal `--script` argument in both commands, not a content hash; however both use the same fixture path in the same battery-created scratch project. This supports the limited “same path” claim, not provenance against a malicious replacement. The explicit `timeout_probe.gd` is copied into scratch from the fixture directory.
- **Timing caveat:** The 0.75s timeout is short relative to the observed 0.394s positive startup (roughly 0.36s margin); CPU load can make positive acceptance fail, which is a false negative/unstable replay, not a false PASS. The reject's marker plus live process at timeout establishes execution reached the marker and was still live, but not direct observation that Godot had begun waiting on the 30s timer. The branch immediately awaits that timer after marker/argument check. Keep the claim to this exact fixture and timeout path.

No source/runner changes recommended by this critic. No assumptions beyond Linux/Godot 4.7.2 execution stated above.
