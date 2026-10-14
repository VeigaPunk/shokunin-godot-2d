# Round 22 timeout scribe — read-only evidence and verdict checklist

## Scope and before-state

This is a read-only scribe note, not a replay or an admission verdict. Round 22 LOG declares a calibration move: prove that a real headless Godot process is not accepted solely because it printed the expected signature before hanging. No engine/editor/seeded-control changes are in scope.

At HEAD `8f87c585bfcf6a7eb56b8b84cb4f95420aa66f90` (round 21), the named verifier record `corpus/lessons/r21-crash-verifier.json` has 45 PASS records: 35 ordinary, 2 mutants, and 8 opt-in records. Its two crash-exit arms used the same script and marker; normal expected exit 1 classified true, and live-child SIGTERM returned -15 and classified false. Separate Python-only fault injection contains a timeout case, but that is not evidence of a real Godot script timing out. The before hashes at HEAD are:

- `corpus/fixtures/run_battery.py`: `2f00636388a7b98d2ddc51ac78ac020df3717b7fa70768000c315666ff47ec1b`
- `corpus/fixtures/crash_exit_probe.gd`: `ef8bccb7ab0118552d2e1baa4a9194faa4201d0bf2b352276fa2052e9df7bb63`

A local untracked `corpus/fixtures/timeout_probe.gd` is presently visible, with marker `TIMEOUT_PROBE: expected signature`, normal `quit(0)`, and an optional 30-second timer before quit. This is source-state only: it does not establish the runner integration, that either process was executed, that timeout cleanup succeeds, or any verdict. I made no edits to it or other files.

## Evidence checklist for verifier / parent

Require raw paired details plus the complete full-replay result, not merely a console summary:

1. Both commands invoke the same scratch copy/script and emit the exact same marker (`TIMEOUT_PROBE: expected signature`); preserve the commands and raw stdout/stderr.
2. Accept arm completes normally within a stated bound, has expected exit 0, no timeout/error, marker present, and the existing classifier returns true.
3. Reject arm demonstrably emitted the marker before timeout (ideally capture marker while child is still live); it remains held open long enough to trigger the *battery's configured timeout*. Record exact timeout duration, elapsed time, command, and raw output.
4. Reject record has `actual_exit`/code `null` (`None`), explicit timeout error, marker present, and classifier false. A nonzero normal exit, missing marker, startup failure, or killed-before-marker run does not satisfy the contrast.
5. Establish bounded cleanup: the timed-out direct child has exited after the runner's cleanup path; record how liveness was checked and any cleanup exception. Any surviving child, unbounded wait, or inability to prove pre-timeout marker is HOLD. Do not infer descendant/process-tree cleanup.
6. Named non-author verifier replays full opt-in battery at the default/absolute runs path. Expected invariant per LOG: exit 0; 35 ordinary and previous 10 mutant/meta records remain PASS; one new timeout meta row passes (46 total if exactly one is added). Include raw JSON path and SHA256 hashes before/after for tracked fixtures/runner as available. Run Python fault-injection regression separately and report it as supplemental, not real-Godot evidence.
7. Preserve the existing unresolved explicit-relative-`--runs` export `StopIteration` and earlier export intermittence as caveats; a successful default-path replay does not erase them.

## Verdict template (only after raw verifier evidence)

- **Calibration improved** only if all paired accept/reject criteria above pass on actual Godot, timeout and cleanup are bounded, and the complete verifier replay has no regressions.
- **Coverage unchanged** (35 ordinary seeded rows, unless evidence shows the target changed); **depth unchanged** (no game mechanic claim). Record any harmed axis and HOLD admission if any axis is harmed or evidence is incomplete.
- Bound the claim to this tested Godot/version/platform, exact script/signature, timeout path, and direct child. This is not arbitrary-freeze robustness, process-tree cleanup, cross-platform behavior, export reliability, or a general crash guarantee.

## Limits of this scribe observation

I did not run Godot, the battery, or fault injection; did not inspect a round-22 verifier raw result (none was present in `corpus/lessons/r22*` at inspection); and did not modify runner, probe, fixtures, or controls. No constants beyond those already visible in the round-22 probe source are endorsed by this report.
