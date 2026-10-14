# Round 26 independent delayed-startup timeout review

## Setup and bounded claim
I independently copied the seeded fixture project to `.shokunin/game-dev-2d/corpus/live/r26-delay-reviewer/project` and changed only that disposable copy's `timeout_probe.gd`. The scratch script prints `TIMEOUT_PROBE: pre-delay`, awaits Godot `create_timer(1.25)`, then prints the existing `TIMEOUT_PROBE: expected signature` marker and exits 0. Its `--hold-open` arm waits 30 seconds after printing the same marker. Godot was `godot --headless` (4.7.2.stable.arch_linux). The reviewer harness, raw three-arm evidence, and scratch script are in that own live directory; script SHA-256 is `0ddb6413b4def868fd9206124c2bc7bfb2504c80f0279a1b870d73ac1264dd26`.

## Results
`review_probe.py` ran sequentially with the same project/script/expected marker and old/new timeout bounds:

| Arm | Bound | Elapsed | Pre-delay marker | Expected marker | Exit / timeout | Direct child reaped | Classification |
|---|---:|---:|---|---|---|---|---|
| delayed valid, old | 0.75 s | 0.7532 s | yes | no (killed before marker) | timeout; -9 after kill | yes | false |
| delayed valid, new | 3.0 s | 1.7034 s | yes | yes | clean exit 0 | yes | true |
| hold-open, new | 3.0 s | 3.0033 s | yes | yes (before hang) | timeout; -9 after kill | yes | false |

The old-bound failure is consistent with a timeout occurring at 0.75s before the intentional 1.25s wait completes. At the measured successful 1.70s runtime, 3 seconds allows about 1.30s additional margin in this environment; this is a bound justified by the deliberately measured delay, not a general guarantee. The hold-open control demonstrates the longer positive bound did not turn this particular marker-then-hang process into a success. Captured raw stdout/stderr, exact commands, elapsed durations, child status and hashes are in `corpus/live/r26-delay-reviewer/r26-delay-results.json` and `project/timeout_probe.gd`.

## Review conclusion
The requested three-arm contrast is independently reproduced for this Godot build and scratch fixture: old 0.75s rejects a clean but deliberately delayed startup, new 3.0s accepts it, and the marker-emitting hold-open control remains timed out/rejected with its direct child reaped. This supports the bounded calibration claim only. It does not establish portability, arbitrary-hang detection, process-tree cleanup, or general startup reliability. No tracked fixture/runner or seeded control was modified; no engine/editor source changed. Reviewer edited only own scratch and this assigned report.
