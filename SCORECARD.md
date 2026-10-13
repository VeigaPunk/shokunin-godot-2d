# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution` → 44/44 PASS, 35 ordinary incl top-bound positive/control vs 33 at HEAD `3d19377a604df726377e53b8007b284a3607875d`; named non-author `corpus/lessons/r20-top-verifier.json`, work commit recorded in r20 report | r20 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution` → 42/42 PASS incl one paired real Godot stdout/stderr attribution accept/reject; independent `corpus/lessons/r19-stream-verifier.json` (measured before the report-only commit; work commit cited in the round-19 report) | r19 |

planned: calibration — crash-exit classification, process-tree timeout, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The r16 intermittent export-path failure and r20 explicit-relative-`--runs` export probe StopIteration remain unresolved.
retired: none.
