# Round 26 timeout scribe — raw evidence and admission checklist

Role: read-only provenance/checklist. I did not edit fixture/runner, execute the battery, alter engine/editor files, or delegate.

## Declared scope

The LOG declaration at round 26 targets calibration: show that a deliberate clean startup delayed beyond the old 0.75s deadline is rejected by that old bound but accepted by a measured larger bound, while a same-script hold-open process still times out and is rejected with its marker observed. The verifier should preserve 39 ordinary records and prior outer probe outcomes. No general freeze, process-tree, or cross-platform claim.

## Source/baseline provenance inspected

- `corpus/fixtures/timeout_probe.gd` at inspection had a worktree edit: `--delay-clean` awaits 1.5s **before** printing `TIMEOUT_PROBE: expected signature`; `--hold-open` awaits 30s after marker. This differs from committed baseline (marker immediately, then optional hold-open).
- `corpus/fixtures/run_battery.py` had no visible worktree diff at inspection. Its timeout probe still set `timeout_seconds = 0.75` for both ordinary accept and hold-open reject, and the accept used `run_process(..., 8)`. Thus the measured-new-bound production runner change was not present yet at inspection.
- Prior committed control: `corpus/lessons/r22-timeout-detail.json` / `r22-timeout-verifier.json`; the paired accept/reject use identical marker/script, expected 0; reject times out at 0.75s with marker observed, `actual_exit=null`, direct child killed/reaped (`cleanup_exit_code=-9`), and classifier false. `r22-real-timeout.md` records critic's normal startup observation ~0.394s and ~0.356s margin; explicitly not a stability guarantee.

## Existing r26 scratch observation — insufficient for the declared contrast

`corpus/live/r26-delay-reviewer/review_probe.py` and `r26-delay-results.json` are independent scratch evidence, not production runner/verifier evidence. The scratch `project/timeout_probe.gd` waits 1.15s, prints a separate `TIMEOUT_PROBE: pre-delay` marker, then prints expected marker and exits (or holds open). Raw observations:

- old 0.75s bound elapsed 0.7535s, timed out, expected marker **not** observed (only pre-delay marker), killed/reaped;
- new 3.0s bound elapsed 1.6088s, expected marker observed, exit 0/classified true;
- new 3.0s hold-open elapsed 3.0031s, expected marker observed, timed out/classified false, killed/reaped.

This tests delay-before-expected-marker and eventual acceptance, but does **not** establish old-bound rejection despite an already-emitted matching success signature. It also measures a 3s bound in an independent reviewer script, not the chosen/used production runner bound. Preserve as useful feasibility telemetry, not admission proof. The current executor fixture edit also delays before marker, so this issue should be resolved before relying on the three-arm claim.

## Independent verifier evidence checklist

1. Record exact committed baseline and final fixture/runner SHA-256; verify only the assigned fixture and runner changed, with no seeded-control or engine/editor mutation.
2. Use the same fixture/script identity and exact expected success marker in each relevant arm. In the delayed-valid arm, capture the marker **before** the intentional delay; raw old-bound capture must show marker=true, timeout=true, classification=false, and cleanup/reaping.
3. Show the same delayed-valid case under the new bound exits 0 cleanly, marker=true, timeout=false, classification=true. Record elapsed wall time and chosen timeout with comfortable observed margin; justify the constant from measured delay/startup, not assertion alone.
4. Show hold-open under the new bound emits the same success marker, remains live at deadline, times out, classifies false, and direct child is reaped. Keep cleanup exit metadata distinct from `actual_exit` on timeout.
5. Save unedited raw commands, exits, timeout/error fields, stdout/stderr, process liveness, cleanup results, and classifier outcomes in the assigned lesson detail. Keep adverse failed attempts visible.
6. Replay full named non-author combined command. Confirm 39 ordinary records and all previous outer probe rows preserved; separately replay fault-injection if required by the standing battery protocol. Compare immutable fixture hashes before/after verifier; label expected inner negative outcomes accurately.
7. Report verdicts per axis (calibration/depth/coverage) and bounded scope. If the old-bound marker is absent, the new bound is not justified/measured, the hold-open negative is admitted, or a child survives, record HOLD rather than claiming the declared improvement.

Constants already evidenced: old timeout 0.75s; reviewer scratch deliberate delay 1.15s, observed total 1.6088s at 3.0s deadline; 30s hold-open fixture. The reviewer scratch values are not automatically the production constants.
