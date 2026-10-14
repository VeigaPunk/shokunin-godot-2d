# Round 4 level/collision scout

## Suggested minimal check

Use a tiny packed level scene with a `TileMapLayer` and one `TileSetAtlasSource` tile placed at `Vector2i(0, 0)`. The positive should inspect the placed cell, not merely that a `TileSet` exists:

1. Load/instantiate the packed scene and find its `TileMapLayer`.
2. Assert `get_cell_source_id(Vector2i(0, 0)) >= 0`, then fetch `get_cell_tile_data(Vector2i(0, 0))` and require it is non-null.
3. Require `get_collision_polygons_count(0) > 0` and that the first `get_collision_polygon_points(0, 0)` polygon has at least three points. Configure physics layer 0 on the TileSet and a nonzero collision layer on the tile.
4. Print a unique positive signature only after all assertions pass.

The isolated negative should copy the scene/TileSet into the battery's scratch project, remove only the placed tile's collision polygon (or replace its TileSet with a copy whose tile has zero collision polygons), and run the same assertion. Expect a distinct assertion-failure exit/signature; do not mutate the seeded fixture. Keep the cell placement and tile source intact so the negative specifically tests collision data, rather than missing-cell/scene-load failure.

## API / cautions

Godot executable is `4.7.2.stable.arch_linux.ed1daf0bf`. Relevant Godot 4 APIs are `TileMapLayer.get_cell_tile_data(coords)`, `TileMapLayer.get_cell_source_id(coords)`, and `TileData.get_collision_polygons_count(physics_layer)` / `get_collision_polygon_points(physics_layer, polygon_index)`. `TileSet` needs physics layer 0 (`add_physics_layer()`); ensure the tile polygon is authored on that same layer. Check points as well as polygon count to reject a zero/degenerate polygon. This is a TileSet collision-data assertion for an actually occupied cell; it does not establish runtime body-vs-tile contact, visible map correctness, or production level quality.

If the intended scope specifically requires runtime collision rather than authored collision data, add a `CharacterBody2D`/shape and physics-frame query in the loaded scene; avoid treating scene load or cell occupancy alone as evidence of solid collision.
