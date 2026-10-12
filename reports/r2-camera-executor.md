# Round 2 camera executor report

Added two new scratch-copied fixtures: `corpus/fixtures/camera_follow.gd` parents a Camera2D beneath a Node2D, moves the target only after a baseline frame, and verifies that camera global position changed and matches the moved target. `camera_no_follow.gd` uses the same movement/assertion but omits the follow relationship; it must exit 2 with the behavioral failure signature. No direct camera-position update is used.

Added both cases to `run_battery.py` without removing prior cases. Executed:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing
```

Result: exit 0, 17/17 listed battery cases PASS, including both camera cases and the existing broken-scene mutant. Camera-positive exited 0 with `PASS camera_follow target_x=120 camera_x=120 moved=true`; no-follow exited 2 with `camera follow assertion failed: target moved but camera did not`. Raw machine-readable results: `.shokunin/game-dev-2d/corpus/live/runs/20261012T161501317448Z/verdicts.json` (ignored live scratch output). The runner copied fixtures into scratch before execution; seeded fixture files were not edited.
