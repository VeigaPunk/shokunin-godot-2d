# Round 26 timeout simplifier report

## Scope

Read-only review of the existing timeout fixture and runner shape. I did not change either. The old probe uses a 0.75 s `communicate` deadline for the `--hold-open` arm, while its clean arm is not deadline-bounded by that same assertion. The prior critic measured ordinary startup at 0.394 s; that leaves only about 0.356 s of positive margin and does not test a deliberately slow clean startup.

## Minimal case design

Keep this to one fixture and one opt-in meta row with three runs of that same script, recording commands, measured durations, output, exits, timeout observations, and cleanup state:

1. **Slow-clean / old bound:** a fixture flag delays a clean `quit(0)` by a measured, bounded interval greater than 0.75 s. Run it with the old 0.75 s deadline. Require timeout, process still alive at the deadline, and classifier false. This is the explicit before-bound negative calibration; do not treat the absence of a later marker as a successful clean run.
2. **Same slow-clean / new bound:** run the identical command and fixture flag with a new deadline chosen from observed elapsed time, not an arbitrary constant. Require the same marker, exit 0, no error, and classifier true. Record the measured slow-clean duration and the positive headroom so a reader can judge whether the new bound was actually justified. Use a separately measured run (or stable repeated observations) to select the bound; one run barely under a limit is weak evidence.
3. **Hold-open / new bound:** run the existing marker-then-hold-open mode at the new deadline. Require marker observed, process alive at deadline, timeout error, false classification, and direct child dead after bounded cleanup. This guards against fixing the slow-positive false negative by making the negative deadline ineffective.

The slow flag should delay only the clean path before it prints the existing marker and exits; keep `--hold-open`'s marker-before-wait ordering. Avoid a generalized timeout framework or changing ordinary cases. A single explicit `timeout_seconds` parameter/local for the three arms is enough; preserve the old 0.75 s constant for arm 1 and use the measured new value only for arms 2–3. Distinguish timeout observation (`actual_exit: null`) from cleanup return code, as the existing probe does.

## Admission checks / limits

The meta verdict must fail closed if the old-bound arm exits cleanly, is not observed running at timeout, or cannot be cleaned up; if the new-bound arm lacks marker/clean exit; or if the hold-open arm exits early, lacks marker, is not still running at timeout, or remains alive after cleanup. Verify all three commands use the exact same fixture path and expected exit. Preserve the raw three-arm observations, not only the aggregate PASS. This supports only a bounded delayed-clean-startup contrast and direct-child cleanup on the measured platform; it does not prove arbitrary startup latency, freeze detection, process-tree cleanup, or cross-platform timing.

No code, fixture, engine/editor, or seeded control was changed. No constants changed by this reviewer. No commit/push/merge.
