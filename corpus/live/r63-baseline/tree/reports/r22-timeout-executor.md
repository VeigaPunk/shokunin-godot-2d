# Round 22 timeout executor report

## Changes

- Added only `corpus/fixtures/timeout_probe.gd`, the opt-in `--probe-timeout` branch in `corpus/fixtures/run_battery.py`, and this report.
- Fixture prints the same exact marker (`TIMEOUT_PROBE: expected signature`) in both arms. Normal arm exits 0; `--hold-open` arm waits 30 seconds.
- Opt-in branch runs normal arm through existing bounded runner helper (8 seconds), then launches the hold-open arm and bounds it at 0.75 seconds. The timeout arm must have emitted the marker and still be live at timeout. It is killed as a direct child; cleanup is bounded at 3 seconds. Timeout classification retains `actual_exit: null` and `error: TIMEOUT after 0.75 seconds`; cleanup return code is recorded separately. The reject classifier is false. The runner records post-cleanup direct-child liveness, not process-tree state.
- Existing `CASES` and prior flags remain unchanged; no engine/editor/source changes.

## Replay

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-timeout`

Exit 0; all 35 ordinary cases PASS and opt-in probe PASS (36 aggregate rows). Godot identified as 4.7.2.stable on Linux. Raw evidence is `.shokunin/game-dev-2d/corpus/live/runs/20261013T010717688215Z/timeout-verdicts.json` and its enclosing `verdicts.json`.

- Accept: marker observed, exit 0, no error, classifier true.
- Reject: same script/marker, timeout at 0.75s, process live at timeout, `actual_exit: null`, explicit TIMEOUT error, classifier false; cleanup code -9 and `direct_child_alive_after_cleanup: false` within the 3-second bound.

## Scope

This is one actual Godot 4.7.2 headless normal-exit versus timeout contrast. It supports timeout rejection despite a matching pre-timeout marker, and observed cleanup of this direct child only. It does not establish descendant/process-tree cleanup, arbitrary hang or freeze handling, platform portability, or export reliability. Constants: 0.75-second timeout, 3-second cleanup bound, 30-second fixture hold. No commit/push/merge performed.
