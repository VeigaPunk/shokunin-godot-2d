# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → 27/27 PASS including runtime tile contact and scratch polygon-removed control; independent `corpus/lessons/r8-contact-verifier.json` at 2fd8eeae2226092ada5c3d1e613063bca0dd8fe4 | r8 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error` → 27 retained + four export/mutant classifier probes PASS; independent `corpus/lessons/r9-diagnostic-verifier.json` (r9 work commit) | r9 |

planned: calibration — real Godot-emitted stderr fault, process-tree timeout, other diagnostic formats still unprobed; coverage: rendered level, audio, real rendered juice/HUD, exported-app launch and other platforms remain unprobed.
retired: none.
