# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → 27/27 PASS including runtime tile contact and scratch polygon-removed control; independent `corpus/lessons/r8-contact-verifier.json` at 2fd8eeae2226092ada5c3d1e613063bca0dd8fe4 | r8 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection` → meta PASS (hang inner FAIL, clean negative PASS, unrelated ERROR inner FAIL); independent `corpus/lessons/r7-fault-verifier.json` at 8c9799e23dd590a435e3b3a2af3a80f7323db7eb | r7 |

planned: coverage — headless runtime tile contact at one authored cell passes 27/27; rendered level, audio, real rendered juice/HUD, exported-app launch and other platforms remain unprobed. Calibration next: diagnostic spoofing / process-tree timeout.
retired: none.
