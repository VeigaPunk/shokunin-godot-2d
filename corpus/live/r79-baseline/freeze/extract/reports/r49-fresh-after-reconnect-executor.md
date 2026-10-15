# Round 49 — fresh adjustment after late reconnect (executor evidence)

## Claim and scope
Extend the r48 nine-edge synthetic HSlider trace with one fresh `ui_left` press while the slider owns focus and the `value_changed` callback is connected. Godot 4.7.2 headless evidence only; this is not physical keyboard, OS repeat, rendered UI, accessibility, or production behavior.

## Causal scratch first
Scratch: `/tmp/r49-fresh-after-reconnect-scratch-20261013-unique/slider_adjust.gd` (isolated project). Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Preserved all r48 edges and callback transitions; appended edge9 `ui_left pressed=true`. Exit 0, signature:
`PASS slider_adjust_repeat_second_focus_restore_press_after_late_reconnect values=6,6,6,5,5,5,5,4,4,3 receipts=6,3 Labels=Value 6,Value 3`.

## Additive tracked change
Only `corpus/fixtures/slider_adjust.gd` and `corpus/fixtures/run_battery.py` changed. New flag `--press-after-late-reconnect` requires `--repeat-right --second-focus-restore`; it retains the existing nine edge history and checks focus owner before every edge, value/receipts/Label after every edge, connected-before-edge0, disconnected-after-edge0 through edge7, reconnected-after-edge7 and connected before edge9. Edge9 yields numeric3, receipts `[6,3]`, Label `Value 3`; positive marker and exit0 occur after all ten checks. Existing r48 `--reconnect-after-final-left` negative remains unchanged and terminates after nine checks.

## Replay
Fresh ordinary battery: exit 0, 63/63 PASS. Full named-path-equivalent battery:
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`
Exit 0, 74/74 PASS = 63 ordinary + 2 mutants + 9 opt-ins. Raw copied byte-for-byte from run artifact: `corpus/lessons/r49-fresh-after-reconnect-verifier.json`. Comparing r48 named verifier raw, all 64 prior tuple-bearing `(case, verdict, actual_exit, signature)` results are identical; exactly one new tuple is the expected PASS/exit0 with edge9 signature. Opt-in probes all PASS at outer level; their expected inner positive/negative classifications remained as listed in the raw artifact.

Separate `--fault-injection` meta-probe exited 0 with expected inner outcomes: timeout fault FAIL, clean expected-negative PASS, unrelated-error fault FAIL (`corpus/live/r49-fresh-after-reconnect-executor/runs/fault/20261013T083750624129Z/fault-verdicts.json`). Scratch sabotage retained all ten assertions but omitted only dispatch for edge9; it failed at intended edge9 value/receipt/Label check (actual value4, receipts `[6]`), not at setup or terminal pass marker.

Fixture SHA-256 `0a21283fafed64f5a1653aa5e29ba9a1f76be848fe48f8e256b6cc05783c58f5`; runner SHA-256 `0cc168fdb16ff3dbbc0f16dddde4698183881365612d45c49e4d7a35f90d6cd0`.

## Round axis
Depth improved: observed a fresh post-reconnection left-press adjustment and new receipt/Label update after the prior nine-edge missed-change history. Calibration and coverage unchanged as axes; no harmed axis observed in finite replay. No engine/editor/seeded control edits. No push or merge.
