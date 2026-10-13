# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 50/50 PASS, 39 ordinary incl bottom-limit positive/control vs 37 at HEAD `3b23caa25f00d3929a863ba9d3515be9aa5bb760`; named non-author `corpus/lessons/r24-bottom-verifier.json`, work commit cited in r24 report; adverse author export raw `corpus/lessons/r24-export-adverse.json` | r24 |
| calibration | unscored | pre-fix alternating relative/absolute full-battery `--runs` → readiness FAIL/PASS/PASS/FAIL (`corpus/lessons/r25-pair-before-{1,2,3,4}.json`), target-isolation `r25-direct-target-pair.json`; after two target `.resolve()` calls explicit-relative full flags → 50/50 PASS, named non-author `r25-export-verifier2.json` / `r25-export-launch-verifier2.json`; first readiness-only verifier 49/50 at `r25-export-verifier.json` retained, work commit cited in r25 report | r25 |

planned: calibration — direct-child Linux SIGTERM and one real Godot timeout are probed; spontaneous crashes, process-tree timeout, startup-margin robustness, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The relative-export-target failure is causally reproduced and both fixture export targets normalized at r25; historical r16/r20/r24 adverse and first r25 49/50 remain recorded, with production/general export reliability unproven.
retired: none.
