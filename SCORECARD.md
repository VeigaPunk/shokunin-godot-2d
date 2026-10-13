# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 53/53 PASS; named non-author `corpus/lessons/r30-edge-verifier.json`: Button press/release edge receipts [0,1,1,2] / texts Ready, Activated 1, Activated 1, Activated 2; scratch missing-release fails release1; work commit cited r30 report | r30 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 52/52 PASS, 41 ordinary incl Button positive/disconnected vs 39 at HEAD `a25ca36abcf4ae92ea42549d5cb464e2988761d9`; named non-author `corpus/lessons/r27-button-verifier.json`, work commit cited in r27 report; four wave1 leaves unreachable | r27 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 53/53 PASS, 42 ordinary; named non-author `corpus/lessons/r29-focus-verifier.json`: focused owner true receipts [1,2], no-focus null owner receipts0/Ready exit2 intended step1, previous 52 verdicts/exits/signatures unchanged; work commit cited r29 report | r29 |

planned: calibration — direct-child Linux SIGTERM and one real Godot timeout are probed; spontaneous crashes, process-tree timeout, startup-margin robustness, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The relative-export-target failure is causally reproduced and both fixture export targets normalized at r25; historical r16/r20/r24 adverse and first r25 49/50 remain recorded, with production/general export reliability unproven.
retired: none.
