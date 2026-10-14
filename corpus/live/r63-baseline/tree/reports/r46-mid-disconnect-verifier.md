# Round 46 named non-author verifier — mid-run callback disconnect

## Result: verified; bounded calibration claim supported

I independently ran the full requested default-path battery with Godot 4.7.2:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r46-mid-disconnect-verifier/runs
```

Exit 0, **71/71 PASS** (60 ordinary cases, two mutants, nine opt-ins). The new `slider_adjust_repeat_right_second_focus_restore_disconnect_after_first` case has expected/actual exit 2 and exact terminal signature `SLIDER MID-DISCONNECT ASSERTION FAILED: expected cumulative callback history to stay [6]`. Its unique marker reports values `6,6,6,5,5,5,5,4,4`, receipts `[6]`, Label `Value 6`. Source assertions check owner before each of nine edges and numeric value, full receipts, and Label after each; edge 0 requires connected callback result `[6]`/`Value 6` before disconnect. The terminal marker and expected-negative diagnostic occur only after all nine checks.

Independent bounded direct controls from copied fixture projects reproduced the connected r44 arm (exit 0; values `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, final Label `Value 4`), disconnected-at-start r45 arm (exit 2; same values, receipts `[]`, Label `Value 5`), and mid-disconnect arm (exit 2; same values, receipts `[6]`, Label `Value 6`). Godot reported `4.7.2.stable.arch_linux.ed1daf0bf`. In a separate verifier-owned instrumented scratch copy, I explicitly checked `slider.value_changed.is_connected(_on_value_changed)` true immediately before the edge-0 observation/disconnect and false immediately after the disconnect; that run still completed with the expected terminal marker and exit 2. The tracked candidate itself disconnects at that point but does not include those explicit connection-state assertions.

Raw full battery evidence was copied byte-for-byte to `corpus/lessons/r46-mid-disconnect-verifier.json` (125631 bytes). Against r45's 70 case records, all 70 prior case identities retained their exact tuple `(case, verdict, actual_exit, signature)` where tuple-bearing, or same outer/inner classification for opt-in rows, excluding run paths; precisely one case was added. This means all 61 prior tuple-bearing records (59 ordinary + 2 mutants) are unchanged and the nine opt-in classifications are stable. New row is PASS/exit 2. Separate `--fault-injection` replay exited 0 at meta-level; raw `corpus/lessons/r46-fault-verifier.json` shows intended inner hang and unrelated-error FAIL, clean expected-negative PASS. These injected negatives are not treated as battery passes.

Three scratch-only sabotage checks rejected the candidate before terminal classification: skipping disconnect failed at edge 3's value/receipt/Label assertion; omitting the first press failed the edge-0 numeric assertion; disconnecting before the first press failed the edge-0 receipts/Label assertion. Fixture/runner SHA-256 were captured before and after verifier battery and unchanged: `slider_adjust.gd` `74e9e65096a8a5de8610850ee5f8639a645430f277d6415b811f575dbaa2ad2e`; `run_battery.py` `aa070aeb318e7adadf50051d3a459f67f5eec84be99e34dff54c5bc311a46ef2`. No tracked edits, commits, pushes, or merges were made by verifier.

## Axis verdict and scope

**Calibration improved** for the bounded same-history callback-discontinuity observation; depth and coverage unchanged as axes; no harm observed in this finite replay. This evidence is limited to headless Godot 4.7.2 synthetic parsed action events plus process-frame yields and observed focus/value/receipt/Label state. It does not establish OS repeat, physical input/timing, rendered or pointer behavior, accessibility, production behavior, or internal consumer behavior for unchanged edges.
