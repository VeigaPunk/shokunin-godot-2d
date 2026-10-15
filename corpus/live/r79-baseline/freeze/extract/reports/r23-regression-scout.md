# Round 23 regression scout — existing runtime probes and export caveat

## Scope

Read-only inspection of the existing round 19–22 reports, raw lesson artifacts, `corpus/fixtures/run_battery.py`, and the declared Round 23 move. I did not run Godot or the battery, change fixtures/runner/controls, or alter prior artifacts. This report is my only write.

## Relevant existing probe surface

- **Stream attribution (r19):** `--probe-stream-attribution` checks a real-Godot stdout marker against an unrelated stderr diagnostic. Both arms use the same script and exit 0; accept classifies true, reject false. It is stream attribution, not a left-camera check or process-termination test. The r19 verifier recorded 42/42 PASS at that time.
- **Signal termination (r21):** `--probe-crash-exit` runs the same script and marker in both arms. The normal arm exits 1 and classifies true; on Linux the live reject arm receives SIGTERM and returns -15, classifying false. Raw evidence is in `corpus/lessons/r21-crash-detail.json`; the verifier reports 45/45 full replay PASS. This is direct-child SIGTERM evidence only, not general crash, descendant cleanup, or cross-platform coverage.
- **Timeout (r22):** `--probe-timeout` pairs a normal same-marker exit with a real Godot hold-open arm. The r22 verifier recorded marker-before-timeout, `actual_exit=null`, explicit `TIMEOUT after 0.75 seconds`, false classification, and direct-child cleanup; its full replay was 46/46 PASS. Details: `corpus/lessons/r22-timeout-detail.json`. This is bounded to that direct child/fixture; no process-tree or general freeze guarantee.
- **Error diagnostic classifier:** `--probe-godot-error` has a real-Godot expected diagnostic and unrelated-error control. The expected-negative arm is accepted and the unrelated diagnostic is rejected; this is diagnostic classification, not a runtime failure injection relevant to camera coverage.

These are independent opt-in probes. The Round 23 camera pair should preserve their existing results in the named full replay; their existence does not validate the camera fixture itself.

## Export adverse evidence remains unresolved

Do not alter, retry-overwrite, or recast prior export evidence as resolved by this camera move:

- `corpus/lessons/r16-export-adverse.json` preserves a real Godot 4.7.2 `export_readiness` exit 1 with `ERROR: Prepare Template: The given export path doesn't exist.` and no product.
- `reports/r17-export-path-hold.md` documents later successful scratch exports but no established cause; relative versus absolute `--runs` roots were confounded, and it explicitly retains the adverse record.
- `reports/r20-regression-scout.md` and `reports/r21-regression-scout.md` record the separate explicit-relative-`--runs` harness exception: `--probe-unrelated-error` hit `StopIteration` looking for a `savepack` line that was absent while building spoof cases. It is a harness exception, not a verdict or established cause of the r16 failure. Default-path successful export replays do not close either issue.

Keep export claims out of the left-edge coverage evidence. A successful default-path full replay would only establish that the existing export rows passed in that replay; it would not prove export reliability or resolve the adverse observation.

## Conclusion

The prior real timeout, signal, stream, and diagnostic probes exercise separate runner behavior and should be compared unchanged in the full replay. The r16 export failure and later relative-`--runs` exception remain adverse/unresolved telemetry. No regression execution or source mutation was performed by this scout.
