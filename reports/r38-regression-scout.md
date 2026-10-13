# Round 38 regression scout — UI edge and battery caveats

Read-only review of the r38 claim, current `slider_adjust.gd` / runner, prior Button edge evidence, and export/fault/timeout boundaries. No Godot execution or tracked fixture/runner edit was performed; this report is the only write.

## Prior Button edge precedent

Round 30 scratch evidence (`reports/r30-edge-scout.md`) measured a focused Button: `ui_accept` press-only did not invoke `pressed`; the matching release and process-frame wait produced the receipt/Label change. This supports measuring each distinct input edge, but it is a Button-specific result and cannot establish HSlider semantics. The current slider sends parsed `InputEventAction` separately and waits `process_frame` after every edge; r38 must provide fresh Godot measurements for right press, right release, left press, left release. Do not infer the release outcome from the Button precedent.

Current `slider_adjust.gd` asserts only after each full press/release pair: connected receipts/Label at right and final, disconnected after right and final, no-focus final. A four-edge depth change should make each observation immediately after its edge/frame, checking value, receipt list, and Label. Check release does not duplicate. Keep existing controls and their diagnostics: disconnected focused slider must still numerically move while having no receipts and `Value 5`; no-focus must remain at 5 with no receipts and `Value 5`; their intentional negative diagnostics should remain after both actions. Preserve runner rows, case signatures and expected exits unless the measurement disproves the declared premise, in which case correct/HOLD rather than encode false timing. The claim explicitly limits inference to synthetic process-frame observations, not physical-key repeat/timing.

## Battery and fault boundaries

The prior r37 named verifier report establishes the 51 ordinary / 62 full current baseline and that its full result includes opt-ins; r38 must use its named full replay/raw comparison, not this source review, to assert no regression. Preserve the runner's default cases and existing classification behavior. The established `--fault-injection` path is a separate executor self-test: its outer meta PASS can contain intentional timeout or unrelated-error inner failures and is not fixture evidence. Likewise opt-in timeout, crash/exit, Godot-error and stream-attribution probes are distinct boundary checks, not slider behavior. Do not conflate expected negative fixture exits with tool/runtime failure.

## Export boundary

Prior regression-scout evidence documents the export readiness / missing-preset ordinary cases and opt-in export-launch probe, including bounded 60-second export execution and Linux artifact assertions. This round should leave that machinery untouched and rely on full replay for current evidence; synthetic successful export is not a general ship-readiness claim.

## Bounded verdict

The proposed per-edge observation is a defensible depth move if fresh scratch Godot confirms values and signal receipts at each edge. Button precedent makes release non-duplication a plausible hypothesis, not an HSlider fact. No new cases are proposed; retain the disconnected and no-focus controls, expected-negative diagnostics, runner rows/signatures, and existing fault/export/timeout behavior. No new depth/calibration claim follows from this read-only review alone.
