# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → 19/19 PASS including two synthetic UI cases and prior 17; independent `corpus/lessons/r3-ui-verifier.json` at a0d3f239a5e989f69e39028d034cc7d4e9a9d3c2 | r3 |
| calibration | unscored | `git show 4468c15740ecbf7c53340cb8c85023df2fd35177:.shokunin/game-dev-2d/corpus/knowledge/2026-10-12-production-checklist.md` → camera/UI/export unprobed | r1 |

planned: coverage — levels/juice/export and real/rendered HUD remain unprobed; synthetic UI signal-to-Label property positive and disconnected control 19/19 at r3 (`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`, `corpus/lessons/r3-ui-verifier.json`). Rendered viewport tracking remains unprobed.
retired: none.
