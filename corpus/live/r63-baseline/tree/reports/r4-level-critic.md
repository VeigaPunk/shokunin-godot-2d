# Round 4 level/collision critic

## Finding

The current fixture is a useful **TileData collision-metadata** probe, but it does **not establish actual solid collision**. It should not be counted as a runtime tile-collision demonstration without a body/physics-space contact or query.

`level_scene.tscn` contains only an empty `Node2D` and an empty `TileMapLayer`. `level_probe.gd` creates a TileSet, atlas texture, tile, physics layer, collision polygon, and occupied cell at runtime. Its positive assertion checks `get_cell_tile_data()` and polygon count/point count. That is stronger than cell occupancy or merely loading a PackedScene, and confirms collision geometry is authored on the occupied cell; it still does not show the TileMapLayer created a physics body that blocks motion or overlaps a query shape. No `CharacterBody2D`, `move_and_collide`/`move_and_slide`, or `PhysicsDirectSpaceState2D` query appears. The signature `collision_vertices=4` means polygon metadata, not a verified solid contact.

The test runs via `--headless --script`; it observes neither rendered pixels nor visible tile placement. Since the packed scene itself has no tile data and construction is procedural, it also does not validate a composed/authored level. State only that it loads an empty level shell and constructs/checks a tile cell's collision metadata in headless script mode. Do not imply visual map correctness or production-level readiness.

## Mutant isolation

The `--no-collision` branch skips only the calls that add collision polygons. It still creates the same PackedScene, TileMapLayer, TileSet, atlas source/tile, and places the tile at `(2,3)`. The negative uses the same `cell == null || polygon_count != 1 || points < 3` assertion and a targeted `LEVEL ASSERTION FAILED` diagnostic. This is good causal isolation for the narrow claim “the occupied tile has collision polygon metadata”: cell presence and scene load remain intact, so a missing cell/scene failure is not the reason it fails.

It is not a mutation of an independent copied level asset; the same script's flag changes setup behavior. That is acceptable as a controlled negative for this assertion, but evidence should retain the negative output and preferably record that the cell/source remain occupied in the negative before reporting the collision assertion. The current output only emits the failure diagnostic, so the report/battery record should be checked for raw proof of the preserved cell state. Also, mutant acceptance must require the intended diagnostic/exit and absence of the positive signature (and reject parse/script errors); generic exit 2 alone is not enough.

## Suggested scope correction / next test

For current evidence, rename/describe this as a headless TileData collision-metadata fixture, not “solid collision.” To substantiate solid collision, place a `CharacterBody2D` with a known shape above/against the tile, synchronize/run physics frames, then demonstrate that movement/query is blocked by the positive tile and succeeds with only the collision polygon removed. Keep the same cell, TileSet source, and assertion path in both runs; verify collision layer/mask configuration and report the observed contact/result. This would prove runtime physics, still not rendering. Pixel/visual claims require a rendering-capable run and image/pixel observation, separate from this headless physics check.
