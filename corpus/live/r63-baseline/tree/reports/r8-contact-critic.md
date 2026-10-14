# Round 8 runtime tile-contact adversarial review

Read-only review of `corpus/fixtures/contact_probe.gd` and the staged level scene. I copied the probe into an existing ignored scratch project (seed fixtures were not changed) and ran both modes with Godot 4.7.2 headless.

## Evidence

- Normal run: exit 0, `PASS runtime_tile_contact=true cell=2,3 collider=Ground`.
- `--no-collision`: exit nonzero as intended, with `ERROR: CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3`.
- Neither run emitted `SCRIPT ERROR`, `Parse Error`, resource-load, or physics setup diagnostics. The negative's expected assertion is not evidence of invalid setup.
- Probe instantiates the authored packed `level_collision/level_scene.tscn`, waits two physics frames, then adds a `CharacterBody2D` with a 6×6 rectangle and moves it 40 px downward from 20 px above the target cell center. The tile set physics layer is 1; the body defaults to collision layer 1/mask 1, so it can collide with the tile layer. `move_and_collide` is synchronous and checks its returned collider is the `Ground` TileMapLayer. The negative duplicates the TileSet and removes the atlas tile's physics polygon before running the same body placement and displacement. This counterfactual shows contact depends on the authored atlas polygon in this scene.

## Adversarial qualification

The fixture supports runtime contact with the `Ground` TileMapLayer, and the negative establishes dependence on the authored atlas polygon. It does not inspect `KinematicCollision2D` position/normal or otherwise bind the returned contact to map cell `(2,3)`; the `cell=2,3` text is hardcoded. Collider identity alone would allow a different collidable cell on the same layer to satisfy the assertion if the scene later gained one. The current small fixture appears arranged around the target tile and the body path crosses its expected top edge, but that attribution is inferred from scene geometry rather than asserted at runtime.

To make the cell-level claim robust against future fixture edits, assert the contact point (and optionally normal) lies on the expected target tile boundary, or query/assert the relevant cell and exclude other collidable cells in the swept path. Avoid treating the printed cell label as proof. No evidence here addresses rendering or production playability.

**Assessment:** runtime TileMapLayer contact and polygon-removal sensitivity verified; specific-cell attribution is an explicit limitation, not a setup failure. No fixture/runner or engine/editor source edits; report only.
