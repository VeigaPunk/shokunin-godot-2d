# Round 22 regression scout — prior timeout, stream, signal, and export probes

## Scope and method

Read-only inspection of `corpus/fixtures/run_battery.py`, Round 19–21 reports and raw lesson artifacts, plus the recorded export adverse/hold evidence. I did not run Godot or modify fixtures, runner, corpus controls, or prior artifacts. This report is the only file written by this scout.

## Existing fault-timeout regression surface

`run_process(command, timeout_seconds)` in the runner uses `subprocess.run(..., capture_output=True, text=True, timeout=...)`. A `TimeoutExpired` becomes combined partial output, `code=None`, and exact `TIMEOUT after N seconds`; `classify_process` requires `code == expected_exit`, no error, marker, and no unallowed error/parse diagnostics, so a retained marker alone cannot pass. The existing separate `--fault-injection` path is Python-only, exits before seeded cases, and tests a `time.sleep(30)` command bounded at 0.25 seconds, expected-negative diagnostic, and unrelated-error rejection. The saved Round 21 fault artifact (`corpus/lessons/r21-fault-verifier.json`) has the expected inner outcomes (hang FAIL with marker/code null/timeout; clean expected-negative PASS; unrelated-error FAIL) and outer meta verdict PASS. This does not demonstrate a real Godot timeout.

For the proposed Godot timeout pair, reuse of `run_process` and `classify_process` is behaviorally aligned with current timeout semantics. However, aggregate `subprocess.run` output does not itself establish marker arrival before the deadline or explicitly record post-timeout direct-child liveness. Python's timeout path kills and waits for its direct child; this is not a process-tree/descendant cleanup guarantee. If the declared claim requires explicit marker-before-timeout and no direct survivor, record those facts with a bounded Popen/selector/cleanup path (as in the signal probe) or keep the claim narrower. Do not conflate `error != None` with `actual_exit`: timeout returns `code=None`.

## Prior stream and signal probes

Round 19 `--probe-stream-attribution` is a real-Godot same-script paired stdout-marker accept / stderr-diagnostic reject. It tests stream attribution, not termination. Its existing checks require stdout marker and reject unexpected stderr; it offers no timeout calibration. Round 21's `--probe-crash-exit` and `corpus/lessons/r21-crash-detail.json` record a distinct direct-child SIGTERM contrast: both arms use `res://crash_exit_probe.gd` and marker `CRASH_EXIT_PROBE: expected signature`; normal arm exits 1/classifies true, while hold-open arm is observed live after marker, receives SIGTERM, returns -15/classifies false. That is Linux/POSIX-specific evidence, not a timeout test. Preserve the expected normal exit/marker behavior and signal arm while adding the timeout pair; keep its timeout and cleanup limits explicit. Neither probe covers process trees.

## Export regressions and caveat

Keep the unresolved export evidence unchanged and separate from this calibration move:

- `corpus/lessons/r16-export-adverse.json`: real Godot 4.7.2 export exited 1 with `Prepare Template: The given export path doesn't exist.` and no product.
- `corpus/lessons/r17-export-path-hold.md`: later scratch exports passed, but causal isolation failed; relative-vs-absolute `--runs` was confounded, and no cause was established. Do not auto-retry/replace the adverse record.
- `reports/r20-regression-scout.md` and `reports/r21-regression-scout.md`: explicit relative `--runs` plus `--probe-unrelated-error` raised `StopIteration` when expected `savepack` output was absent; the export diagnostic probe assumes that line while constructing same-line spoof cases. This is a harness exception, not a verdict, and remains unresolved. Default absolute-path successes do not close it.

Do not alter export behavior or include export results as evidence for the timeout classifier. Maintain the established full replay baseline (35 ordinary, two mutants, prior opt-in rows) and compare all existing rows; export caveat remains adverse telemetry, not a Round 22 timeout result.

## Conclusion

Existing Python fault injection establishes only Python timeout classification; Round 19 stream and Round 21 signal probes test different classifier dimensions. A same-marker real Godot normal-exit versus timeout pair is a distinct calibration contrast. No prior evidence supports descendant cleanup, arbitrary-freeze guarantees, cross-platform behavior, or export reliability. No regressions were executed in this read-only scout.
