# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch` → 32/32 PASS including scratch exported executable startup/control; independent `corpus/lessons/r10-launch-verifier.json` at 7670476f7d7d9336b296669aca28587bcb9012dd | r10 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution` → 42/42 PASS incl one paired real Godot stdout/stderr attribution accept/reject; independent `corpus/lessons/r19-stream-verifier.json` (measured before the report-only commit; work commit cited in the round-19 report) | r19 |

planned: calibration — stdout/stderr attribution for one print/printerr pair is probed; crash-exit classification, process-tree timeout, and other diagnostic shapes remain unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The r16 intermittent export-path failure remains unresolved.
retired: none.
