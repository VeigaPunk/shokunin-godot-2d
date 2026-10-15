# Round 18 limit executor

Implemented a headless Camera2D right-limit fixture and added positive/far-bound control records to the existing battery.

- `camera_limit.gd` parents the Camera2D under a Node2D target, waits for setup, makes it current, moves the parent target to `(2000, 0)`, then forces camera scroll update. It checks movement/current status, verifies screen center is the expected viewport-adjusted clamp (`limit_right - viewport_width / 2`), has advanced from the prior center, and differs from target. This observes Godot's camera screen-center coordinates, not rendered pixels.
- `--far-bound` changes only the right-limit setting (from 1000 to 100000); it retains the same authored boundary assertion at 1000 and exits 2 with the narrow expected assertion diagnostic. Raw far-bound control observed center `(2000,0)`, expected clamp x `968` (viewport width 64), target `(2000,0)`. It does not disable Camera2D limits; it moves the right limit farther away.
- Direct Godot 4.7.2 positive run exited 0; far-bound control exited 2 with that assertion. Full `python corpus/fixtures/run_battery.py --probe-failing` completed PASS: 35 records (previous 31 base + 2 camera cases + 2 mutation probes); exports passed this run (73,703,800 bytes). Raw results: `corpus/live/runs/20261012T185955392126Z/verdicts.json`.
- No editor, seeded fixtures, or production project files changed. No delegation or commit.

The earlier Round 16 export-path failure remains adverse and unexplained (Round 17 HOLD); this successful export run does not resolve or negate that intermittent observation.
