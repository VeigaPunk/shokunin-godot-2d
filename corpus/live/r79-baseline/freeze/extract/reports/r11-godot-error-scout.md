# R11 Godot error scout (read-only)

## Findings from current runner and prior fixture JSON

- `corpus/fixtures/run_battery.py::classify_process` receives one concatenated `output` string. `run_process` currently calls `subprocess.run(..., capture_output=True, text=True)` but immediately returns `proc.stdout + proc.stderr`; it loses the stream boundary. The classifier checks expected exit, `error is None`, signature presence, and rejects every `ERROR:` line not covered by `allowed_errors`, plus `SCRIPT ERROR:` / `Parse Error:`.
- Prior captured fixture evidence provides a real expected diagnostic with controlled exit: `corpus/lessons/r10-battery-verifier.json`, case `negative_overlap`, script `controls/overlap_negative.gd`, expected/actual exit `1`, verdict PASS. Its output includes exact line `ERROR: negative control: expected collected signal was absent with disabled mask`, then Godot's `at: push_error (core/variant/variant_utility.cpp:1023)` and GDScript backtrace. The fixture executes `push_error(...)` then `quit(1)` when its expected absence condition holds.
- Other usable examples include `negative_signal` (expected exit 1, but output includes resource-load errors as well, so it is a poorer calibration target) and `negative_transition` (has a native `change_scene_to_packed` error plus intended `push_error`, likewise less clean). Prefer `negative_overlap`.
- The saved JSON represents `output` as merged lines, not stdout/stderr fields. It proves actual Godot diagnostic text and exit status, but cannot tell which stream emitted it. Do not claim stream provenance from these records.

## Finite paired real-Godot probe recommendation

Use the existing `controls/overlap_negative.gd` as the basis for two scratch-only runs (not seeded edits): (1) expected-negative path unchanged; (2) identical path and same intended `push_error`, then a second `push_error("R11 unrelated diagnostic sentinel")`, before `quit(1)`. Keep process command, expected exit `1`, signature and scene/setup otherwise identical. The first should classify expected-negative PASS; the paired case must classify FAIL because the second independent `ERROR:` is not allowlisted. Assert raw output contains each exact diagnostic once, actual exit is 1 in both, and neither has timeout/launch error or script/parse error. This exercises Godot's own push_error formatter rather than appending edited text to a captured transcript. Run from the normal scratch copy, preserve raw outputs in JSON; no broad/unbounded probe.

The current allowlist model supports this cleanly: allow only the complete expected diagnostic line (not a broad `ERROR:` prefix); its subsequent `at: push_error` / backtrace lines do not themselves contain `ERROR:`. An unrelated `push_error` produces a separate `ERROR:` line and must remain disallowed. Keep expected and unrelated diagnostic strings distinct and check both lines are actually emitted; otherwise the negative control is invalid.

## stdout/stderr attribution

`subprocess.run(capture_output=True)` already captures streams separately. To measure source, retain `proc.stdout` and `proc.stderr` separately in the raw probe result, then build classifier input as `stdout + stderr` (or classify across both as a combined line sequence) so current verdict semantics do not change. Record which stream contains each sentinel and its exit code. Godot's prior JSON merged the streams, so the stream carrying `push_error` is unknown until this probe. Avoid requiring a particular stream in the verdict; platform/runtime may route diagnostics differently. If runner API changes are out of scout scope, simply report stream source as unmeasured rather than infer it.

## Scope / limitations

This pair calibrates one headless Godot version, one expected-negative fixture, and one explicit unrelated `push_error`; it does not prove every engine error source is captured or establish GUI/production behavior. Keep all execution artifacts in scratch/live runs and leave seeded fixtures, runner, engine/editor, and exports untouched for this scout.
