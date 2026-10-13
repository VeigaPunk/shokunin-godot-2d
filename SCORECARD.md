# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 50/50 PASS, 39 ordinary incl bottom-limit positive/control vs 37 at HEAD `3b23caa25f00d3929a863ba9d3515be9aa5bb760`; named non-author `corpus/lessons/r24-bottom-verifier.json`, work commit cited in r24 report; adverse author export raw `corpus/lessons/r24-export-adverse.json` | r24 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 46/46 PASS vs 45/45 at r21; named non-author `corpus/lessons/r22-timeout-{verifier,detail}.json`, work commit cited in r22 report; direct-child timeout only | r22 |

planned: calibration — direct-child Linux SIGTERM and one real Godot timeout are probed; spontaneous crashes, process-tree timeout, startup-margin robustness, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The r16 intermittent export-path failure and r20 explicit-relative-`--runs` export probe StopIteration remain unresolved.
retired: none.
