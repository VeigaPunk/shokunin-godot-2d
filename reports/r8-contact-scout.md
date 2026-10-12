# Round 8 runtime tile contact scout

## Read-only recommendation

Use a temporary runtime `CharacterBody2D` and `move_and_collide()` against the instantiated authored `res://level_collision/level_scene.tscn`, rather than inferring runtime behavior from `TileData` polygon metadata. Existing authored scene has a 16×16 atlas tile with a square `(-8,-8)..(8,8)` collision polygon on physics layer 0 (collision layer bit 1), and the requested occupied cell is `(2,3)`. Existing `level_probe.gd` only validates the cell and polygon data; it does not exercise physics.

## Paired finite probe

1. In a disposable copy of the fixture project, load and instantiate `level_scene.tscn`, add it to the SceneTree root, and get its `Ground` TileMapLayer. Keep the positive run unchanged.
2. For the paired negative run only, deep-duplicate the layer's TileSet, call `get_source(0)` as `TileSetAtlasSource`, and set `get_tile_data(Vector2i.ZERO, 0).set_collision_polygons_count(0, 0)`, then assign the duplicate to `Ground`. This mirrors the existing probe's scratch-only removal and leaves the authored fixture untouched.
3. Add a `CharacterBody2D` with `collision_layer = 2`, `collision_mask = 1`, plus a child `CollisionShape2D` using `RectangleShape2D.size = Vector2(8,8)`. Place the body at `(20,56)` (left of cell `(2,3)` center `(40,56)` for 16px tiles). After adding it and awaiting at least one `physics_frame` so TileMap static bodies are synchronized, invoke `move_and_collide(Vector2(30,0))` once. Keep the entire run bounded, e.g. maximum 3 physics frames; don't wait on an unbounded loop.
4. Positive assertion: returned `KinematicCollision2D` is non-null, collider is the `Ground` TileMapLayer (or its generated tile body where Godot reports it), and travel is blocked near the target tile's left edge (body center around x=28; allow a small tolerance). Optionally assert nonzero normal pointing left. This is an actual CharacterBody physics motion/contact, not an overlap inferred from tile data.
5. Negative assertion: after polygon removal, the same motion returns null and body reaches x≈50. Require the same finite-frame bound and geometry/body parameters. Check that the control still has the occupied cell but zero collision polygons, so it isolates polygon removal rather than accidentally testing a missing tile.

Run headless with the installed `godot --version` observed as `4.7.2.stable.arch_linux.ed1daf0bf`. A small `SceneTree` GDScript can defer setup from `_initialize()`, await `physics_frame`, make the direct motion call, print one unambiguous PASS/FAIL line per mode, and `quit(nonzero)` on failed assertions. Launch each mode in a separate headless process under a shell timeout; enforce exit status and output signature as well as the script's own frame bound.

## Caveats / falsification checks

- Confirm `Ground.map_to_local(Vector2i(2,3))` resolves to `(40,56)` at identity transform, and use `to_global()` if scene transforms change. Assert `get_cell_source_id(Vector2i(2,3)) == 0` in both modes.
- Ensure the body's shape is added before the synchronization frame, and the positive motion starts outside the tile. A spawn-overlap could report a collision without proving blocking motion.
- Avoid using `intersect_shape()` alone as proof of blocking: overlap is not a swept body-motion assertion. `move_and_collide()` makes the positive/negative pair directly comparable.
- If the runtime reports collider RIDs rather than the TileMapLayer node, report the contact's non-null collider/RID and inspect its object ID against the layer where available; the primary distinguishing assertion is collision result versus full unobstructed travel.
- This demonstrates only a headless physics contact with this authored cell and this simple body, not rendered gameplay, full-level playability, or production behavior.

Scope observed: read-only scout. No engine/editor or authored fixture edits, no delegation, commit, or push.
