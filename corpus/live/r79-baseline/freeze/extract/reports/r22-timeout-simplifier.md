# Round 22 timeout probe simplifier review

## Scope
Read-only inspection of `corpus/fixtures/run_battery.py` and the existing `crash_exit_probe.gd`; no source, fixture, or control changes made.

## Minimal reuse
The existing `run_process(command, timeout_seconds)` already wraps `subprocess.run(..., capture_output=True, text=True, timeout=...)`, normalizes timeout partial stdout/stderr, and returns `(output, None, "TIMEOUT after N seconds")`. The existing `classify_process` rejects any result unless `code == expected_exit` and `error is None`, even when the expected signature exists. Thus the minimal pair can reuse `crash_exit_probe.gd` and both helpers:

- Accept: current script without `--hold-open`; expect code 1 and `CRASH_EXIT_PROBE: expected signature`, then classify true.
- Reject: same script plus `--hold-open`; use a short explicit timeout (e.g. 1s, rather than the normal fixture 8s); expect marker retained in captured output, code `None`, exact timeout error, then classify false.

This directly distinguishes timeout from the existing normal exit while keeping script and marker constant. No new classifier behavior appears necessary. The fixture's 30-second hold is already long enough to make a 1-second timeout deterministic under ordinary load.

## Reliability boundary
Python `subprocess.run` timeout handling kills and waits for its direct child before raising `TimeoutExpired`; therefore successful return from `run_process`'s timeout handler is reasonable evidence that the direct child was reaped. Captured output is not proof that the marker was emitted before the deadline; the test's bounded timing and the hold fixture make that likely, but the helper only returns aggregate output. If the round requires explicit proof of marker-before-timeout and direct-child liveness/return code, the existing `Popen` + selector + bounded cleanup structure in `--probe-crash-exit` is stronger to adapt; it is more code and should not be duplicated unless that stronger evidence is required. Neither route proves descendant/process-tree cleanup.

## Recommendation
Prefer `run_process`/`classify_process` reuse for a minimal timeout classifier calibration probe, and state the evidence narrowly as same-script normal exit versus timeout with captured marker and direct-child cleanup by `subprocess.run`. If the acceptance contract insists on explicit live-after-marker and no-survivor observations, use a small dedicated `Popen` timeout branch instead; do not claim these from the aggregate helper alone. Existing seeded cases and classifier can remain unchanged.
