# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 56/56 PASS; named non-author `corpus/lessons/r33-checkbox-edge-verifier.json`: CheckBox press/release state sequence [false,true,true,false], connected toggled [true,false], scratch missing-first-release fails release-only state; work commit cited r33 report | r33 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 61/61 PASS, 50 ordinary incl focused HSlider ui_right→ui_left 5→6→5 and paired disconnected signal consumer; named non-author `corpus/lessons/r36-slider-verifier.json`, prior 59 triples unchanged; work commit cited r36 report | r36 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 62/62 PASS; named non-author `corpus/lessons/r37-focus-verifier.json`: same-wiring HSlider unfocused stays value5 after both parsed actions/no receipts vs focused 5→6→5/[6,5]; all prior 61 result triples unchanged; work commit cited r37 report | r37 |

planned: calibration — direct-child Linux SIGTERM and one real Godot timeout are probed; spontaneous crashes, process-tree timeout, startup-margin robustness, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The relative-export-target failure is causally reproduced and both fixture export targets normalized at r25; historical r16/r20/r24 adverse and first r25 49/50 remain recorded, with production/general export reliability unproven.
retired: none.
