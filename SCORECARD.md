# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → 23/23 PASS including animation-property positive/stuck and prior 21; independent `corpus/lessons/r5-animation-verifier.json` (work commit in r5 report) | r5 |
| calibration | unscored | `git show 4468c15740ecbf7c53340cb8c85023df2fd35177:.shokunin/game-dev-2d/corpus/knowledge/2026-10-12-production-checklist.md` → camera/UI/export unprobed | r1 |

planned: coverage — audio/export and real rendered juice/HUD remain unprobed; headless in-memory AnimationPlayer property positive/stuck 23/23 at r5 (`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`, `corpus/lessons/r5-animation-verifier.json`). Runtime tile contact and rendered viewport tracking remain unprobed.
retired: none.
