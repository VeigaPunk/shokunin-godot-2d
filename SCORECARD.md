# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `test -f .shokunin/game-dev-2d/corpus/lessons/r1-headless-verification.md` → true; cited decision/error tables at 4468c15740ecbf7c53340cb8c85023df2fd35177 | r1 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch` → 32/32 PASS including scratch exported executable startup/control; independent `corpus/lessons/r10-launch-verifier.json` at 7670476f7d7d9336b296669aca28587bcb9012dd | r10 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error` → 33/33 PASS incl paired real Godot push_error acceptance/rejection; independent `corpus/lessons/r11-godot-error-verifier.json` at 8728fe7667b4853b286022cc7411a4323dae662c | r11 |

planned: calibration — paired real Godot push_error is probed but stdout/stderr attribution, crash, process-tree timeout and other diagnostics remain unprobed. Coverage: production-project launch, GUI/rendering, audio and other platforms remain unprobed.
retired: none.
