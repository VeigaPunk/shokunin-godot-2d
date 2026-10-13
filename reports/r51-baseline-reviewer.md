# Round 51 baseline review — immutable r50

Role: read-only baseline reviewer; no delegation and no tracked edits. I reviewed the append-only r51 claim in `LOG.md`, r50 author/verifier/critic reports, and preserved r49/r50 raw lesson records.

## Repaired r50 baseline

- The named non-author raw `corpus/lessons/r50-release-repaired-non-author.json` records `PASS`, 75 result entries (64 ordinary, 2 mutants, 9 opt-ins). Separate fault-injection raw `corpus/lessons/r50-release-repaired-fault-non-author.json` records outer PASS with intentional inner hang/unrelated-error FAIL and clean expected-negative PASS.
- By `(case, verdict, actual_exit, signature)`, all 65 tuple-bearing r49 rows match r50 exactly. r50 adds only `slider_adjust_repeat_right_second_focus_restore_release_after_late_reconnect_press`, expected-negative exit 2 with the exact eleven-check terminal diagnostic. All nine opt-in classifications are retained.
- The repaired release report records ordinary parsed `_action` edge10 after the preceding press: `Input.is_action_pressed("ui_left")` true before and false after; value remains 3, full receipts `[6,3]`, Label `Value 3`. Owner/callback checks precede edge delivery and numeric/receipts/Label checks follow one frame.
- Its no-dispatch edge10 sabotage fails the distinct post-release state assertion before the terminal marker. The prior pre-repair raw `r50-release-non-author.json` remains preserved and must not be mistaken for repaired evidence; that old false-PASS was acknowledged in the report/LOG.
- The critic's stronger `Input.action_release("ui_left")` direct state-clear bypass passes the r50 state/value/receipt/Label checks and reaches the expected-negative terminal marker. It bypasses parsed-event dispatch. This is the precise adverse r50 boundary the r51 claim targets.

Tracked fixture/runner currently match repaired r50 hashes: `slider_adjust.gd` `abf833021df686f01d6778646a9d1a96bbabab00905bcb554ac7f8e2d68e7434`; `run_battery.py` `4afc03127ecd13d274eb6bfe8f569bbdd849108558b3884c8d7247775ad3d77c`. `git status --short` for these paths is empty.

## Calibration boundary

The r50 source is a valid immutable comparison point: it demonstrates ordinary parsed release/state transition, detects exact omission, and retains a concrete direct-state-clear counterexample. It does not demonstrate a delivered parsed release receipt. The proposed r51 `_input` observer would add a distinct observable and can support improved calibration only if causal scratch confirms normal parsed edge10 increments exactly once while direct `Input.action_release` and no-dispatch do not, with all pre/post owner and slider checks retained. Keep the claim confined to synthetic parsed `InputEventAction` delivery in this fixture. Do not claim HSlider consumes the event or infer OS/physical timing, rendering, pointer/accessibility, or production behavior.

No r51 causal probe or tracked change was performed by this reviewer; baseline review alone does not establish the new hypothesis or admit the round.
