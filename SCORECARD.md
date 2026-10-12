# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → 21/21 PASS including loaded-level metadata positive/mutant and prior 19; independent `corpus/lessons/r4-level-verifier.json` at 543fe2c43cd77e8edd8aac8037493422e786c9c8 | r4 |
| calibration | unscored | `git show 4468c15740ecbf7c53340cb8c85023df2fd35177:.shokunin/game-dev-2d/corpus/knowledge/2026-10-12-production-checklist.md` → camera/UI/export unprobed | r1 |

planned: coverage — runtime tile contact, juice/export and real/rendered HUD remain unprobed; authored level collision metadata positive and polygon-removed control 21/21 at r4 (`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`, `corpus/lessons/r4-level-verifier.json`). Rendered viewport tracking remains unprobed.
retired: none.
