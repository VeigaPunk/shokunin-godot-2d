# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → 25/25 PASS including scratch Linux/X11 export and missing preset; independent `corpus/lessons/r6-export-verifier.json` at ff0a333, scratch cleanup at 26eb601bc9d7a6f089c647ad95ee08ec7d15d4cf | r6 |
| calibration | unscored | `git show 4468c15740ecbf7c53340cb8c85023df2fd35177:.shokunin/game-dev-2d/corpus/knowledge/2026-10-12-production-checklist.md` → camera/UI/export unprobed | r1 |

planned: coverage — audio and real rendered juice/HUD remain unprobed; scratch Linux/X11 export and missing-preset control 25/25 at r6 (`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`, `corpus/lessons/r6-export-verifier.json`). Runtime tile contact, exported-app launch and other platforms remain unprobed.
retired: none.
