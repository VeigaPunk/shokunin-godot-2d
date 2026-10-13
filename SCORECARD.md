# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 64/64 PASS; named non-author `corpus/lessons/r39-repeat-verifier.json`: deliberate second fresh synthetic ui_right press advances 6→7, return via two left presses, cumulative [6,7,6,5], paired disconnected; all prior 62 triples unchanged; work commit cited r39 report | r39 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 61/61 PASS, 50 ordinary incl focused HSlider ui_right→ui_left 5→6→5 and paired disconnected signal consumer; named non-author `corpus/lessons/r36-slider-verifier.json`, prior 59 triples unchanged; work commit cited r36 report | r36 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 66/66 PASS; named non-author `corpus/lessons/r41-focus-handoff-verifier.json`: after focused HSlider first press 5→6/[6], separate Button takes focus and six remaining synthetic edges retain 6/[6]/Value6; prior 56 tuple rows unchanged and nine opt-ins stable on comparable classifications; work commit cited r41 report | r41 |

planned: calibration — direct-child Linux SIGTERM and one real Godot timeout are probed; spontaneous crashes, process-tree timeout, startup-margin robustness, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The relative-export-target failure is causally reproduced and both fixture export targets normalized at r25; historical r16/r20/r24 adverse and first r25 49/50 remain recorded, with production/general export reliability unproven.
retired: none.
