# Round 44 named non-author verifier — second focus restoration

## Result

**Verified; parent retains admission decision.** I read the standing brief, round 44 LOG, all eight wave-1 reports, and tracked fixture/runner. The fixture change is additive: the existing r43 `--second-focus-loss` branch and runner row/classifier remain intact, with a separate `--second-focus-restore` branch requiring both `--repeat-right` and `--second-focus-restore`, plus one positive row. The r43 exact expected terminal diagnostic remains unchanged. The interrupted author run at `20261013T072845553725Z` has no verdict artifact and is not evidence or PASS.

## Independent paired scratch

Real Godot `4.7.2.stable.arch_linux.ed1daf0bf`. In an isolated scratch copy, I first replayed r43 `--repeat-right --second-focus-loss`: exit 2 after its seven checks; values `6,6,6,5,5,5,5`, receipts `[6,5]`. The separate nine-edge `--repeat-right --second-focus-restore` sequence used connected in-tree HSlider (0..10, step 1, initial 5), focusable Button, Label and receipt callback. It checked focus owner before each fresh parsed action and value, full receipt prefix, and Label after each process frame. Slider owned edges 0,3,4,7,8; Button owned 1,2,5,6. Observed `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, final `Value 4`, exit 0 only after all nine checks.

Sabotage in isolated copies: omitting final slider restoration failed owner assertion before edge 7; replacing initial right press with release failed edge 0 state assertion. Both exited 2 without the positive PASS signature.

## Full default-path replay and comparison

Command:
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r44-second-restore-verifier/runs`

Completed exit 0. Run raw `corpus/live/r44-second-restore-verifier/runs/20261013T073342315142Z/verdicts.json`; 69/69 PASS = 58 ordinary rows (57 prior plus exactly one new positive), 2 mutants, 9 opt-in rows. All 59 prior tuple-bearing `(case, verdict, actual_exit, signature)` rows are unchanged; the nine opt-in rows are compared separately by stable classifications. All nine opt-in classifications are stable against r43: outer classifications remain PASS; inner diagnostics/stream/crash/timeout classifications remain unchanged (paths excluded). The new row alone is `slider_adjust_repeat_right_second_focus_restore`, PASS exit 0. `corpus/lessons/r44-second-restore-verifier.json` is byte-identical to that verdict artifact (SHA-256 `81bc2aa83080c293b73b19acbc794101e70a0f5e0f5c1a6d98b2219798912f74`).

Separate `--fault-injection` run: outer PASS; `fault_hang` inner timeout FAIL, `fault_unrelated_error` inner FAIL, `fault_clean_expected_negative` inner PASS. Raw `corpus/lessons/r44-fault-verifier.json` copies the run artifact. These are deliberate inner failures, not clean PASS cases.

## Integrity and bounds

Before/after SHA-256 unchanged: `slider_adjust.gd` `20d7b833f79bd407f0def517c0a84bdf63d6bbb9ad9e9b17dc5627f87e5592b2`; `run_battery.py` `27733e94007023c5bd78d9a49f8c78b34ac2a10d942ab91b4fdd1b36af8bd2f8`. I made no tracked fixture/runner edits, commit, push, or merge. The earlier interrupted run remains adverse telemetry, not PASS.

Scope: headless Godot 4.7.2, synthetic parsed actions plus process-frame yields, observable focus/value/receipt/Label checks. Not OS repeat, physical keyboard/timing, rendered/pointer behavior, accessibility, production behavior, nor internal consumption of unchanged edges; not a generic slider guarantee.
