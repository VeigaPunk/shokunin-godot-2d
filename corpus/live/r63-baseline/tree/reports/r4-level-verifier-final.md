# Round 4 final independent verification — level collision metadata

Verifier: `r4-level-verifier-final` (non-author; independent replay). Scope: inspect final fixture and replay the requested battery after the earlier verifier's HOLD. This report supersedes neither the recorded HOLD telemetry nor expands the claim beyond the checks below.

## Replay

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`

Result: exit 0; raw verdict artifact: `.shokunin/game-dev-2d/corpus/live/runs/20261012T163249328551Z/verdicts.json`; 21/21 case verdicts PASS. All 19 previous cases remain in the result and PASS. New level evidence:

- `level_collision`: exit 0, `PASS level_packed_scene=true cell=2,3 collision_vertices=4`.
- `mutant_level_collision_removed`: exit 2 and the exact intended `LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry` assertion; no parse/script error.

The positive level process output contains no `ERROR`, `WARNING`, or leak indication. The probe instantiates the PackedScene, adds the level to the SceneTree, samples the cell, queues the level for freeing, awaits a process frame, then exits; this is the corrected tree/free-await lifecycle and the old RID/resource-leak concern did not recur in this replay. Other cases intentionally emit expected error text for negative controls/mutants; these are not positive-level errors.

## Fixture inspection and mutation

`level_scene.tscn` contains a TileMapLayer (`Ground`) and a TileSet atlas tile whose physics polygon points are `(-8,-8), (8,-8), (8,8), (-8,8)`. The probe checks source id 0 at cell `(2,3)`, a non-null TileData, one collision polygon and at least three points. The scratch-only `--no-collision` branch duplicates the TileSet, sets that tile's collision polygon count to zero, and leaves the cell in place. It runs the same probe/assertion and fails precisely as intended; the raw scratch scene still contains the authored cell (`tile_map_data`) and source polygon metadata. No seeded fixture is mutated by the battery.

I SHA-256 hashed all 32 tracked fixture paths before and after replay; every hash was unchanged.

## Verdict and limits

The level coverage evidence is independently reproduced and the prior HOLD caused by the old positive-probe lifecycle issue is resolved for this run. This validates authored collision metadata on a packed level cell and its detection when collision metadata is removed. It does **not** test actual physics blocking/contact behavior or rendered appearance, nor establish production level readiness.
