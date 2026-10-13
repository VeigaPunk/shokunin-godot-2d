# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 56/56 PASS; named non-author `corpus/lessons/r33-checkbox-edge-verifier.json`: CheckBox press/release state sequence [false,true,true,false], connected toggled [true,false], scratch missing-first-release fails release-only state; work commit cited r33 report | r33 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 58/58 PASS, 47 ordinary incl native ButtonGroup toggle-mode Button exclusive B→A pair vs 45 at r33; named non-author `corpus/lessons/r34-button-group-verifier.json`, prior 56 tuples unchanged; **not RadioButton**; work commit cited r34 report | r34 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 54/54 PASS; named non-author `corpus/lessons/r31-focus-loss-verifier.json`: after first activation, focus loss/null owner keeps second press/release at receipt1/Activated 1; old 53 tuples unchanged; work commit cited r31 report | r31 |

planned: calibration — direct-child Linux SIGTERM and one real Godot timeout are probed; spontaneous crashes, process-tree timeout, startup-margin robustness, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The relative-export-target failure is causally reproduced and both fixture export targets normalized at r25; historical r16/r20/r24 adverse and first r25 49/50 remain recorded, with production/general export reliability unproven.
retired: none.
