# Round 21 simplifier review

## Recommendation

Keep the probe narrow and reuse `classify_process`; do not add a crash-specific classifier, modify ordinary `CASES`, or change the production subprocess runner. The current classifier already rejects the signal outcome because its return code is not the expected normal exit code, even when the expected signature is present.

The smallest credible fixture is one opt-in GDScript emitting the same exact stdout signature in both modes. In normal mode it quits with the expected nonzero code. In the signal mode it stays alive after emitting that signature. A bounded `Popen` helper in the opt-in probe should wait for that marker, verify `poll() is None`, signal only that child PID, and collect its result with a bound. Record the actual platform and return code/signal semantics; do not label a negative return code generically as a crash. Avoid relying on a marker alone: a script that prints and immediately quits can race the signal and fail to prove it was terminated while running.

This requires a scoped process-control helper because `subprocess.run` cannot signal a live child from the parent probe. Keep it local to the opt-in probe, with bounded cleanup if the child does not exit. Prefer POSIX `SIGTERM` only when the runtime platform supports and reports that exact behavior; otherwise hold the probe rather than silently substituting different semantics. No timeout/process-tree claim follows.

## Scope and simplifications

- One script, one pair, one opt-in flag/artifact; same script and signature in both arms.
- Reuse existing `classify_process` with expected normal nonzero code/signature; signal arm must classify false. Do not duplicate its logic or force compatibility into it.
- Do not edit `classify_process`, the global `run_process`, seeded cases, or unrelated probes.
- Keep all process interaction and signal handling in scratch/runtime evidence; no engine/editor mutation.

Read-only review only; no fixture, runner, or corpus edits made.
