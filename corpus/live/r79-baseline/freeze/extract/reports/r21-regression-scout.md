# Round 21 regression scout — timeout/fault/stream flags and export exception

Read-only scout. I inspected `corpus/fixtures/run_battery.py`, ran its `--help` and the separate `--fault-injection` mode, and read the prior export-adverse records. No fixture, runner, seeded corpus, engine/editor file, or control was changed. This scout did not run the full Godot battery.

## Existing timeout and fault behavior

The CLI currently exposes `--fault-injection`, `--probe-godot-error`, `--probe-stream-attribution`, `--probe-unrelated-error`, `--probe-export-launch`, `--probe-audio-warning`, `--probe-failing`, `--godot`, and `--runs`; there is no general timeout setting or signal/crash-injection flag.

`run_process` wraps `subprocess.run(..., capture_output=True, text=True, timeout=...)`. On `TimeoutExpired` it returns captured output, `code=None`, and `TIMEOUT after N seconds`; on `OSError` it returns a launch error. Ordinary Godot script cases have an 8-second bound, exports 60 seconds. Export-launch starts an exported process with a 5-second bound. Python's `subprocess.run` timeout bounds the direct child operation; this runner has no explicit process-group/tree termination or separately asserted cleanup contract. The isolated fault mode is an early-return branch and does not execute seeded cases: it uses a Python 30-second sleep bounded at 0.25s, a clean expected exit-2 diagnostic, and an exit-2 unrelated-error control. The re-run for this scout exited 0 with the expected meta PASS; rows were fault_hang=FAIL (`code=null`, timeout), clean expected-negative=PASS, unrelated-error=FAIL. Raw run: `corpus/live/runs/20261013T005952599789Z/fault-verdicts.json`.

## Error and stream probe surface

`--probe-godot-error` runs two real Godot invocations of the same `godot_error_probe.gd`, expected exit 1: one expected diagnostic and one with an unrelated diagnostic. It classifies combined stdout+stderr with `classify_process`, which requires exact expected exit, no timeout/launch error, signature, no unallowed `ERROR:`, and no script/parse error. `--probe-stream-attribution` captures streams separately and requires its signature on stdout; its stderr classifier rejects any nonempty unallowed stderr line. These are diagnostic/stream attribution contrasts, not termination/signal classification.

## Unresolved relative export-path exception

Round 20's recorded explicit relative `--runs` plus `--probe-unrelated-error` baseline raised `StopIteration` at the export diagnostic probe's `next(line for line in output.splitlines() if "savepack" in line)` because the output lacked a `savepack` line. This occurs after export classification and assumes the success marker exists before constructing same-line spoof cases. It is a harness exception, not a reported FAIL verdict, and is not evidence of a Round 21 regression. Do not silently retry or recast it as a pass. The prior R16 export adverse (`lessons/r16-export-adverse.json`) records exit 1, `Prepare Template: The given export path doesn't exist.`, and zero products; R17's `lessons/r17-export-path-hold.md` says repeated later scratch exports passed but no cause was isolated. Relative-vs-absolute runs roots were confounded; causal source remains unresolved. The default `--runs` is `HERE.parent / "live" / "runs"` and resolves from the fixture directory; supplying a relative path preserves the observed path sensitivity in artifacts.

## Scope / conclusion

Existing coverage handles a hang through timeout and an unrelated diagnostic through error classification. It does not establish external signal termination, process-tree cleanup, or an export-path fix. Preserve the relative-export `StopIteration` and R16 adverse as unresolved telemetry; keep export readiness fail-closed and do not combine an export fix with the Round 21 calibration move. No changes made outside this report.
