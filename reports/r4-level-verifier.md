# Round 4 level fixture — independent verifier (LEAF)

## Replay

Independently ran `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` on the current revision. Exit status **0**; the raw record is `corpus/live/runs/20261012T163128956069Z/verdicts.json`. It contains exactly **21 results, all PASS**: the prior 19 cases plus `level_collision` and `mutant_level_collision_removed` (including the existing broken-scene mutant in the total). All cases completed within the runner's 8-second per-process limit; there were no timeouts, launch/parse/script errors, or unexpected runtime diagnostics. Expected negative-control `ERROR` traces are present for existing intentional negatives; they match their expected signatures and exits. The positive level case output contains only the Godot banner and `PASS level_packed_scene=true cell=2,3 collision_vertices=4`, with no leak/RID diagnostic.

The level mutant exits **2**, with exactly the targeted `LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry` diagnostic and no positive `PASS` signature, script/parse error, or timeout. To independently check what it preserves, I instrumented a disposable copy of the generated scratch project (not the fixture or runner) to print the cell/source state before its assertion: `source_id=0 cell_present=true collision_count=0`. Thus the same-script `--no-collision` mutant retains the occupied cell and source while removing its polygon. This diagnostic instrumentation was scratch-only and not part of the battery result.

## Scratch falsification

In two more disposable copies of the battery scratch project, I removed (a) only the authored atlas collision-polygon resource line, and (b) the occupied-cell `tile_map_data`. Each positive probe exited **2** with the intended collision-geometry assertion, not a load/parse failure. These show the asserted condition is sensitive both to polygon metadata and to occupancy; the battery's dedicated mutant isolates polygon removal while preserving occupancy/source.

Before the battery run, I SHA-256 hashed all **32 tracked** paths under `corpus/fixtures`; after it, all hashes matched. The runner copies fixtures to a timestamped scratch project. No seeded fixture changed.

## Scope and verdict

The positive loads/instantiates the authored PackedScene, finds the TileMapLayer's occupied `(2,3)` cell and source 0, and checks its TileData has one physics-layer-0 polygon with four points. This verifies **authored collision metadata on an occupied tile cell**. It does **not** demonstrate a physics body contacting/blocking on that tile, and it does not validate a rendered image, visible tile placement, overall level composition, or production-level quality. Do not describe this as runtime collision/contact or visual level verification.

For the declared round-4 coverage move, the independent replay confirms two level cases (positive and isolated collision-polygon negative) and preserves the prior 19 battery cases: coverage **improved**; depth **unchanged**; calibration **unchanged**. No axis harmed, within the narrow metadata-only scope above.
