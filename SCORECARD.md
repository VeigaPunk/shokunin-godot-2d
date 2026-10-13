# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 74/74 PASS; named non-author `corpus/lessons/r49-fresh-after-reconnect-non-author.json`: after late callback reconnection and edge8 release held4/[6]/Value6, fresh focused edge9 left press changes 4→3 with receipts `[6,3]`/Value3; 64 prior tuples unchanged, nine opt-ins stable comparable classifications; author raw separate; work commit cited r49 report | r49 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 61/61 PASS, 50 ordinary incl focused HSlider ui_right→ui_left 5→6→5 and paired disconnected signal consumer; named non-author `corpus/lessons/r36-slider-verifier.json`, prior 59 triples unchanged; work commit cited r36 report | r36 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → named non-author 77/77 PASS; `corpus/lessons/r52-route-non-author.json`: r51 parsed edge10 and r52 same-field `root.push_input` both reach `_input` observer 3→4 and leave numeric3/[6,3]/Value3, but only parsed route clears global `ui_left` state (false vs pushed true); 67 prior tuples and nine opt-ins unchanged. Both route substitutions fail early. Simplifier unauthorized edits/failed runs retained adverse. No HSlider internal consumption or OS input claim; work commit cited r52 report | r52 |

planned: calibration — direct-child Linux SIGTERM and one real Godot timeout are probed; spontaneous crashes, process-tree timeout, startup-margin robustness, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The relative-export-target failure is causally reproduced and both fixture export targets normalized at r25; historical r16/r20/r24 adverse and first r25 49/50 remain recorded, with production/general export reliability unproven.
retired: none.
