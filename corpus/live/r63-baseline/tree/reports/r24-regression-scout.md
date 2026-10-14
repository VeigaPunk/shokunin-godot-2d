# Round 24 regression scout — prior probes and export adverse caveat

## Scope and method

Read-only review of the Round 24 declaration, existing Camera2D fixture/runner, prior runtime-probe reports and raw details, and export adverse records. I did not execute Godot or change any fixture, runner, control, or prior artifact; this report is my only write.

## Camera change compatibility

The Round 24 declaration adds a bottom-edge pair to the existing ordinary camera suite: authored bottom limit `1000`, target y=`2000`, expected active center `1000 - viewport_height/2`, and a far-bottom control with `limit_bottom=100000` that must fail that SAME authored-boundary assertion. The existing `camera_limit.gd` currently has explicit right, top, and left flags/branches; it has no bottom flag/path. Its current camera rows and expected diagnostics are in `run_battery.py` lines 35–40 and 340–342. The executor will therefore need to add a distinct bottom selection without letting the far-bottom limit redefine the assertion boundary or disturb existing axis selection. Compute half-height from the camera viewport at runtime (do not hard-code the 64px battery's observed 32px); retain the setup/current-camera and target-moved guards. Expected negative should reach the intended bottom assertion (exit 2), not a setup/parser error.

The declared ordinary baseline is 37; adding the positive and far-bottom rows targets 39 ordinary and 50 total on the full replay. This scout did not replay or verify those counts. Existing right/top/left pairs are not evidence for the bottom pair; compare their prior outcomes in the independent full replay.

## Existing opt-in probe behavior to preserve

- **r19 stream attribution:** paired same-script Godot stdout marker accept / unexpected-stderr reject. Distinct from camera geometry and termination.
- **r21 SIGTERM:** raw `corpus/lessons/r21-crash-detail.json` records the same marker/script accepted on normal exit 1, while a live hold-open process receives Linux/POSIX SIGTERM and returns -15, rejected. Direct-child, Linux evidence only.
- **r22 timeout:** raw `corpus/lessons/r22-timeout-detail.json` records normal accept and a real-Godot hold-open reject with marker observed before 0.75s timeout, `actual_exit=null`, explicit timeout, false classification, cleanup -9, and no surviving direct child. This is not a process-tree cleanup guarantee.
- The Godot error diagnostic probe is separate classifier coverage; preserve prior rows rather than treating them as camera evidence.

These probes should be invoked and compared unchanged by the named full replay; this scout did not run them. Existing `--fault-injection` is a separate early-return Python-only mode, not part of the ordinary Godot camera count.

## Export caveat remains unresolved

Keep export evidence out of the bottom-camera claim and do not alter or overwrite it. `corpus/lessons/r16-export-adverse.json` records a real Godot 4.7.2 export exit 1 with `ERROR: Prepare Template: The given export path doesn't exist.` and no product. The R17 hold report (referenced in prior logs) says later scratch exports passed without isolating a cause and retains the adverse record. Reports `r20-regression-scout.md` through `r23-regression-scout.md` preserve a separate explicit-relative-`--runs` + `--probe-unrelated-error` harness exception: `StopIteration` when no `savepack` output line existed for spoof construction. It is not an export verdict and is not a proven cause of the R16 failure. A default-path replay passing its export row does not close either issue; do not retry/reclassify the adverse record as resolved.

## Conclusion

No regression execution was performed. A complete default-path replay should preserve the 48 pre-existing outcomes and prove both added bottom rows plus their intended assertion/error distinction before coverage is credited. The export failures/exceptions remain separate unresolved adverse telemetry. No source, seeded control, prior artifact, or export behavior was changed.
