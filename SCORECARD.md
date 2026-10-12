# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → 17/17 PASS including two camera cases and prior mutant; independent `corpus/lessons/r2-camera-verifier.json` at 7f3c927 (headless effective center only) | r2 |
| calibration | unscored | `git show 4468c15740ecbf7c53340cb8c85023df2fd35177:.shokunin/game-dev-2d/corpus/knowledge/2026-10-12-production-checklist.md` → camera/UI/export unprobed | r1 |

planned: coverage — UI/levels/juice/export remain unprobed; camera headless center-follow positive and detached control 17/17 at round 2 (`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`, `corpus/lessons/r2-camera-verifier.json`; work commit recorded in round-2 report). Rendered viewport tracking remains unprobed.
retired: none.
