# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 69/69 PASS; named non-author `corpus/lessons/r44-second-restore-verifier.json`: after two focus losses, second restoration before third left press resumes 5→4 with final receipts `[6,5,4]`; prior 59 tuple rows unchanged, nine opt-ins stable comparable classifications; work commit cited r44 report | r44 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 61/61 PASS, 50 ordinary incl focused HSlider ui_right→ui_left 5→6→5 and paired disconnected signal consumer; named non-author `corpus/lessons/r36-slider-verifier.json`, prior 59 triples unchanged; work commit cited r36 report | r36 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 70/70 PASS; named non-author `corpus/lessons/r45-double-restore-disconnect-verifier.json`: paired nine-edge second-restoration numeric 6,6,6,5,5,5,5,4,4 with connected receipts `[6,5,4]`/Value4 versus disconnected receipts `[]`/Value5; 60 prior tuple rows unchanged, nine opt-ins stable comparable classifications; work commit cited r45 report | r45 |

planned: calibration — direct-child Linux SIGTERM and one real Godot timeout are probed; spontaneous crashes, process-tree timeout, startup-margin robustness, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The relative-export-target failure is causally reproduced and both fixture export targets normalized at r25; historical r16/r20/r24 adverse and first r25 49/50 remain recorded, with production/general export reliability unproven.
retired: none.
