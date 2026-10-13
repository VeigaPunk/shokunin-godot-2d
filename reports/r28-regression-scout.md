# Round 28 regression scout — UI, export, timeout boundaries

Read-only review of current tracked UI fixture/runner, r27 verifier raw, and round 28 declared claim. No files outside this report were changed; no Godot process was run. The r27 raw is prior-round evidence, not a substitute for r28 replay.

## Existing UI boundary

- `corpus/fixtures/button_activation.gd` currently builds in-tree Button and Label, verifies Ready, focuses the button, sends one `ui_accept` pressed action immediately followed by release via `root.push_input`, waits one process frame, then asserts `Activated` and exactly one callback. The disconnected case uses the same script flag and expects intended assertion exit 2.
- `run_battery.py` currently has the two ordinary cases `button_activation` and `button_activation_disconnected`, and each case signature encodes the one-action contract. The declared r28 behavior is not yet in this source at inspection time: there is no ordered `[1,2]` receipt or per-step label-state boundary. Keep the two row count and all prior case signatures stable except these two deliberate button signatures/expected diagnostics.
- Important regression boundary for the executor: two distinct activations require release plus a process-frame gap before the second press. A single press followed by release must not produce a second receipt; assert receipt count/state after the first press and then after second press. The disconnected control should continue to fail at the first intended final UI assertion (receipts 0, Ready), not setup. The separate scratch suppression of second action should fail at the second-step assertion, not be confused with ordinary disconnected case.
- This fixture reaches the focused button through headless SceneTree `ui_accept`; it does not exercise pointer hit-testing, rendered layout, OS/window events, debounce timing or real users. A printed counter alone is insufficient: final Label state and callback receipt must agree per step.

## Export readiness boundary

The existing ordinary `export_readiness` and `export_preset_missing` cases are in `CASES` and r27 raw records both PASS (positive exit 0 with nonempty Linux/X11 artifact; missing preset exit 1 with expected diagnostic and empty output dir). Runner also has opt-in `--probe-export-launch` and `--probe-unrelated-error`; export uses a 60-second process timeout. Preserve their behavior and outputs when changing only button fixture/runner. Prior raw r27 reports 52/52, but no r28 execution was done here, so current health is unverified.

## Timeout and fault boundaries

`execute()` applies 8 seconds to script cases and 60 seconds to export; the runner has distinct opt-in `--probe-timeout` (and crash-exit / Godot diagnostic probes). Keep fixture command/process classification and timeout code untouched. `--fault-injection` is a separate executor self-test, not an ordinary seeded fixture; a top-level meta PASS is not evidence for button behavior. r27 raw shows prior timeout/export paths were green only in r27; rerun the named r28 verifier over full suite plus timeout/export probes to establish no regression.

## Recommendation / bounded verdict

On source inspection alone, I see no contradiction with the r28 plan, but cannot certify regression-free behavior without replay. Preserve row count at 41 ordinary, full run at prior 52 records when opt-ins are enabled, and compare prior outcomes/signatures while allowing only the intended button positive/negative signature changes. Claim depth only if independent raw proves two distinct input events, ordered per-step state/receipt, release non-duplication, disconnected control, and scratch skip-second failure. UI coverage and calibration remain monitored/unchanged if those existing boundaries still hold; do not claim export readiness or timeout calibration improvement from this work.
