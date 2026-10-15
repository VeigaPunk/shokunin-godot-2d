# Round 4 level collision executor

Implemented an isolated fixture at `corpus/fixtures/level_collision/level_scene.tscn`. The PackedScene authors a `TileMapLayer` with a TileSet atlas tile, physics layer, one collision polygon, and cell `(2, 3)`. The probe loads and instantiates that PackedScene and inspects the authored cell's collision geometry; it does not create/populate level data for the positive case.

The battery now includes one positive level case and, under `--probe-failing`, a scratch-only `--no-collision` mutant that removes the polygon from a duplicated TileSet while preserving the placed cell. Both use the same collision-geometry assertion. The mutant exited 2 with `LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry`, while positive case passed with four vertices.

Validation: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` exited 0, all 21 cases PASS: the original 19 battery cases remain, plus the level positive, existing broken-scene mutant, and new collision mutant. The two mutant probes are opt-in under `--probe-failing`. Raw verdict JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T162919127216Z/verdicts.json`.

Scope: synthetic headless loaded-level cell/collision structure only; no claim about rendered composition or production level design. No seeded fixtures changed.
