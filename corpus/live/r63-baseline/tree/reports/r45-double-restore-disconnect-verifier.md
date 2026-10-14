# Round 45 named non-author verifier — disconnected double-restore control

## Result: verified; bounded calibration claim supported

I independently ran the full requested default-path battery with Godot 4.7.2 using:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r45-double-restore-disconnect-verifier/runs
```

It exited 0, **70/70 PASS** (59 ordinary rows, two mutants, nine opt-in checks). The new `slider_adjust_repeat_right_second_focus_restore_disconnected` row has expected/actual exit 2 and the exact terminal signature `SLIDER DOUBLE-RESTORE DISCONNECTED ASSERTION FAILED: expected signal-consumer updates`. Its output includes the distinct terminal marker `SLIDER_DOUBLE_RESTORE_DISCONNECTED values=6,6,6,5,5,5,5,4,4 receipts=[] Label=Value 5`; it is emitted only after the nine asserted edges. The connected companion remains exit 0 with values `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, and matching Labels.

The raw full result was copied byte-for-byte to `corpus/lessons/r45-double-restore-disconnect-verifier.json`. Compared with `corpus/lessons/r44-second-restore-verifier.json`, all **60** prior tuple-bearing `(case, verdict, actual_exit, signature)` records are exactly unchanged; one new PASS/exit-2 tuple was added. The nine opt-in rows retain stable comparable outer verdicts and inner classifications; artifact paths differ as expected.

Separate `--fault-injection` replay exited 0 at the meta-level: expected inner classifications were hang/timeout FAIL, unrelated-error FAIL, clean-negative PASS. This is a successful fault-classifier test, not evidence that the injected faults themselves pass. Scratch sabotage that reconnects the callback fails at edge 0 (receipts/Label assertion), and omitting the first press likewise fails at edge 0 numeric assertion; neither reaches the terminal expected-negative classifier. The initially observed r44 disconnected hard-coded connected PASS/exit 0, and scribe's initial wrong expected numeric 5, remain adverse telemetry; neither was hidden by the corrected result.

Fixture and runner SHA-256 before and after verifier execution were unchanged: `slider_adjust.gd` `e08a203c6a420e2e28e02bd867a08804a4d346c248922961fe7a9c665d164c22`; `run_battery.py` `11690c7acba4575a2fcbe2498aed9679ac635b0b5653bbb20b6280a17d627325`. No tracked edits, commits, pushes, or merges were made by this verifier.

## Axis verdict and scope

**Calibration improved** for the paired connected/disconnected nine-edge double-restoration history: focus ownership and numeric values match edge-for-edge while callback receipts and callback-driven Label remain absent in the disconnected arm. Depth and coverage are unchanged as axes; no axis harmed in this finite replay. Counts advance 58→59 ordinary and 69→70 full.

Evidence is limited to headless Godot 4.7.2 synthetic parsed action events plus process-frame yields and observed GUI focus/value/receipt/Label state. It does not establish OS auto-repeat, physical keyboard timing, rendered or pointer behavior, accessibility, production behavior, generic slider behavior, or internal consumption of unchanged edges.
