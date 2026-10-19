# TileMapLayer body-RID attribution: the tile body's RID, not the mover's, and quadrant-size governs granularity

source: S002 — https://docs.godotengine.org/en/4.7/classes/class_tilemaplayer.html — get_coords_for_body_rid / has_body_rid / physics_quadrant_size (4.7 docs rev. 2026-10-19); S005 — https://docs.godotengine.org/en/4.5/tutorials/migrating/upgrading_to_godot_4.5.html — "Behavior changes → TileMapLayer" (4.4→4.5 migration); S027 — https://docs.godotengine.org/en/4.7/classes/class_kinematiccollision2d.html — get_collider_rid; S029 — corpus/fixtures/tilemap_lattice.gd — r92 `_physics`/`_quadrant` arms ~L720–741 (untracked-body pin); S030 — corpus/fixtures/r105_tile_rid.gd — arms exact/chunked/kinematic/wrongrid (this round)
verified-at: 2026-10-19 (godot 4.7.2.stable.arch_linux.ed1daf0bf; corpus/fixtures/r105_tile_rid.gd --arm=exact|chunked|kinematic|wrongrid)
recheck: on-release — from lane root: `timeout --signal=TERM --kill-after=2s 1800s python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --res-uid-order forward --probe-res-uid-shared` → expects `PASS r105_tile_rid_exact:` (runner stages fresh scratch projects; full battery, not just this row)

## Claim

`TileMapLayer.has_body_rid(rid)` / `get_coords_for_body_rid(rid)` answer about the
**tile body's** RID — the `RID` delivered by `KinematicCollision2D.get_collider_rid()`
when a `PhysicsBody2D` collides with a tile. Feeding any other RID (e.g. the moving
body's own `get_rid()`) yields `has_body_rid == false` and `get_coords_for_body_rid
== Vector2i(0,0)` plus one engine ERROR (`Parameter "found" is null`,
`tile_map_layer.cpp:3124`). With `physics_quadrant_size = 1` the returned coords are
the exact collided cell in the tested cases; with the default 16 the tested cells
(5,0)/(15,0) return (0,0), while (21,0) returns (1,0). [inf] Consistent with quadrant
indices, but no general formula is established for Y or negative coordinates.
`use_kinematic_bodies = true` preserved exact attribution in the tested (5,0) case.
Scoped to Godot 4.7.2 headless on this host.

## Evidence

[obs] `exact` arm (quadrant 1; cells (5,0) and (21,0), probe = 8×8 CharacterBody2D
dropped 16px onto a full-cell collision square, real `move_and_collide`):
`c5_is_layer=1 c5_collider_class=TileMapLayer c5_has=1 c5_coords=5,0` and
`c21_has=1 c21_coords=21,0` — exact-cell attribution, `get_collider()` is the
TileMapLayer node itself. 4/4 serial runs byte-identical.

[obs] `chunked` arm (default quadrant 16): cells (5,0) and (15,0) — same quadrant —
both return coords `0,0`; cell (21,0) in quadrant (1,0) returns `1,0`
(`same_quad_agree=1 cross_quad_diverge=1`). [inf] These samples are consistent with
per-quadrant attribution, not exact cells; they do not prove a universal
`floor(cell / 16)` formula. 4/4 runs identical.

[obs] `kinematic` arm (`use_kinematic_bodies=1`, quadrant 1): `c5_has=1
c5_coords=5,0`, collider still `TileMapLayer`. Body-RID tracking IS reachable from
script with kinematic tile bodies, through the collision's collider RID.

[obs] `wrongrid` arm (paired negative control): after the same positive collision
(`c5_has=1 c5_coords=5,0`), the moving probe's own `get_rid()` gives `own_has=0
own_coords=0,0`. This reproduces the r92 `physics` arm's pin
(`coords_for_untracked_body=0,0 has_body_rid=0 kinematic_body_tracked=0`) almost
verbatim — r92 measured `probe.get_rid()`, the *argument-error* path, so its
comment "body tracking stays unreachable … from script" is refuted: the API was
never given the right argument.

[obs] Discriminating mutants (scratch copies): (a) `_mk_scene(16)` inside the
`exact` arm → `FAIL r105_tile_rid exact reason=c5_coords_0,0`; (b) substituting
`probe.get_rid()` for `hit.get_collider_rid()` → `FAIL … reason=c5_untracked`.

[obs] Calling `get_coords_for_body_rid` on an untracked RID returns `Vector2i(0,0)`
but ALSO emits `ERROR: Parameter "found" is null.` — the (0,0) fallback is
distinguishable from a real cell only by `has_body_rid` (and the error line), since
(0,0) is a legal cell coordinate.

Source quotes:
- S002 `get_coords_for_body_rid`: "Such an RID can be retrieved from
  KinematicCollision2D.get_collider_rid(), when colliding with a tile." Also, under
  `physics_quadrant_size`: "To get the exact cell coordinates, you need to set
  physics_quadrant_size to 1, which disables physics chunking."
- S005 Behavior changes → TileMapLayer: "get_coords_for_body_rid() will return
  different values in 4.5 compared to 4.4, as TileMapLayer physics chunking is
  enabled by default."
- S027 `get_collider_rid`: "Returns the colliding body's RID used by the
  PhysicsServer2D."

## Decision

To attribute a tile collision to map coordinates: take `hit.get_collider_rid()` from
the `KinematicCollision2D`, check `has_body_rid(rid)` first, then read
`get_coords_for_body_rid(rid)`. Set `physics_quadrant_size = 1` when exact cells
matter; at the default 16 do not treat the result as an exact cell, nor extrapolate
a universal block-coordinate formula from these three horizontal samples. Never
test the API with an arbitrary body RID — a `(0,0)` refusal fallback can mimic a
real cell unless `has_body_rid` is consulted. This corrects the interpretation of
the r92 pin without editing r92's historical fixture.

## Limits

Measured on one host, Godot 4.7.2 headless, single atlas source, square 16×16
collision polygon, static and `use_kinematic_bodies` tile bodies only. [unk]
Whether alternative tile layouts (half-offset, isometric), scaled/rotated layer
transforms, or multi-physics-layer tilesets change attribution granularity.
[unk] The exact return when a RID is valid-but-foreign (another layer's tile body)
was not probed — `has_body_rid` should stay false, unverified. [inf] The (0,0)
fallback on untracked RIDs looks like a map miss of the quadrant hash; the ERROR
text pins engine revision sensitivity.

## Claim-to-CASES binding (Q6)

Exact five-field tuples, including byte-exact signatures, are committed in
`reports/round-105/r105-claim-tuples.json`, keyed by the case names below (no
wildcard lookup). Both serial receipts are in `r105-battery-receipts.json`
under the same report directory; every named row has `signature_in_output=true`.

| claim | exact tuple key | fixture / arm / expected exit |
|---|---|---|
| exact cell attribution | `r105_tile_rid_exact` | `r105_tile_rid.gd`, `--arm=exact`, 0 |
| coarse measured attribution | `r105_tile_rid_chunked` | `r105_tile_rid.gd`, `--arm=chunked`, 0 |
| kinematic tile attribution | `r105_tile_rid_kinematic` | `r105_tile_rid.gd`, `--arm=kinematic`, 0 |
| wrong-RID refusal | `r105_tile_rid_wrongrid` | `r105_tile_rid.gd`, `--arm=wrongrid`, 0 (one expected engine ERROR; origin is a refusal fallback) |
