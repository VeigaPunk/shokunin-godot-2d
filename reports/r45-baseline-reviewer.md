# Round 45 baseline reviewer — immutable r44

## Result

I reviewed the r44 verifier evidence and ran the paired nine-edge Godot 4.7.2 scratch before any tracked edits. The connected baseline is confirmed: command `godot --headless --path <scratch> --script res://slider_adjust.gd -- --repeat-right --second-focus-restore` exited 0 with the r44 pass marker. Its nine per-edge assertions encode owners (slider 0,3,4,7,8; Button 1,2,5,6), numeric values `6,6,6,5,5,5,5,4,4`, receipts `[6]`, `[6,5]`, `[6,5,4]` at expected prefixes, and matching Label values.

The paired disconnected invocation `... --repeat-right --second-focus-restore --disconnect-signal` also exited 0. This confirms the nine-edge code's per-edge disconnected assertions accept the unchanged numeric series, empty callback receipts, and `Value 5` Label when only the callback connection is omitted. **But it does not yet satisfy the round's expected-negative contract:** the `--second-focus-restore` branch unconditionally prints the connected PASS signature and calls `quit(0)` after its loop, even when `disconnected` is true. So this is not yet a distinct expected-negative exit 2 after nine checks, and its apparent pass marker falsely reports connected receipts/Labels. Do not admit the calibration row until the branch emits an accurate negative signature and exits 2 after all nine disconnected checks, while preserving connected exit 0.

## Baseline integrity

The checked-in r44 report records 69/69 PASS (58 ordinary, two mutants, nine opt-ins). I compared the retained r43 raw baseline with the r44 raw verdicts: all 59 prior tuple-bearing `(case, verdict, actual_exit, signature)` rows are present unchanged; r44 adds one `slider_adjust_repeat_right_second_focus_restore` row. The r44 live run is preserved under `corpus/live/r44-second-restore-verifier/runs/20261013T073342315142Z/`.

I made no tracked fixture/runner edit and did not run the full battery. Scratch is confined to `corpus/live/r45-baseline-reviewer/`. No engine/editor/seeded edits, commit, push, or merge.

## Scope

This checks headless Godot 4.7.2 synthetic parsed actions plus process-frame yields, focus ownership, numeric value, callback receipts, and Label text. It does not establish OS repeat, physical keyboard/timing, rendered/pointer behavior, accessibility, production behavior, or a generic slider guarantee.
