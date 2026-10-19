# r105 seat report — R105TileRidExec (executor)

Verbatim final output of L2 `W2RoundGameDev2d.R105TileRidExec` (round 105, batched swarm; transcript `history://W2RoundGameDev2d.R105TileRidExec` is session-scoped and not evidence — this file is).

---

K1 complete. Files touched (write set honored — nothing else modified):

- `corpus/fixtures/r105_tile_rid.gd` (new, 218 lines, 4 arms)
- `corpus/knowledge/2026-10-19-tilemaplayer-body-rid-attribution.md` (new)

## CASES tuples (PASS lines verbatim from serial runs, 4/4 byte-identical)

```python
('r105_tile_rid_exact', 'r105_tile_rid.gd', ['--arm=exact'], 0,
 'PASS r105_tile_rid exact quad=1 c5_is_layer=1 c5_collider_class=TileMapLayer c5_has=1 c5_coords=5,0 c21_is_layer=1 c21_collider_class=TileMapLayer c21_has=1 c21_coords=21,0'),
('r105_tile_rid_chunked', 'r105_tile_rid.gd', ['--arm=chunked'], 0,
 'PASS r105_tile_rid chunked quad=16 c5_is_layer=1 c5_collider_class=TileMapLayer c5_has=1 c5_coords=0,0 c15_is_layer=1 c15_collider_class=TileMapLayer c15_has=1 c15_coords=0,0 c21_is_layer=1 c21_collider_class=TileMapLayer c21_has=1 c21_coords=1,0 same_quad_agree=1 cross_quad_diverge=1'),
('r105_tile_rid_kinematic', 'r105_tile_rid.gd', ['--arm=kinematic'], 0,
 'PASS r105_tile_rid kinematic quad=1 kinematic_use=1 c5_is_layer=1 c5_collider_class=TileMapLayer c5_has=1 c5_coords=5,0'),
('r105_tile_rid_wrongrid', 'r105_tile_rid.gd', ['--arm=wrongrid'], 0,
 'PASS r105_tile_rid wrongrid c5_is_layer=1 c5_collider_class=TileMapLayer c5_has=1 c5_coords=5,0 own_has=0 own_coords=0,0'),
```

**expected_errors needed** for the wrongrid row (measured on every run; `get_coords_for_body_rid` on an untracked RID emits it — this is exactly the engine diagnostic r92's pin rode on):

```python
'r105_tile_rid_wrongrid': ('ERROR: Parameter "found" is null.',),
```

…and a matching `r105_expected_errors_all_matched` gate clause (same named-by-round shape as r87–r103). Other three arms are ERROR:-clean.

## Run evidence

Scratch: `/var/tmp/gd2d-r105/R105TileRidExec/proj` (copy of `corpus/fixtures/project.godot` + the fixture). Command per arm:

```
timeout --signal=TERM --kill-after=2s 15s godot --headless --path /var/tmp/gd2d-r105/R105TileRidExec/proj --script res://r105_tile_rid.gd -- --arm=<arm>
```

4 serial reps × 4 arms, all rc=0, PASS lines byte-identical each rep (verbatim lines above; each run ~1 s). Godot `4.7.2.stable.arch_linux.ed1daf0bf`.

## Mutant / negative evidence (both discriminate)

| mutant | arm | result |
|---|---|---|
| `_mk_scene(1)` → `_mk_scene(16)` (quadrant 16 inside `exact`) | exact | `FAIL r105_tile_rid exact reason=c5_coords_0,0`, rc=1 |
| `hit.get_collider_rid()` → `probe.get_rid()` (RID swap) | exact | `FAIL r105_tile_rid exact reason=c5_untracked`, rc=1 |

`wrongrid` itself is the paired in-arm negative: same collision session, collider RID → `has=1 coords=5,0`; `probe.get_rid()` → `has=0 coords=0,0`, reproducing r92's `has_body_rid=0 / coords_for_untracked_body=0,0` pin verbatim and showing r92 measured the argument-error path, not API reachability.

## Doc quotes (all Godot 4.7 docs)

- **S002** `docs.godotengine.org/en/4.7/classes/class_tilemaplayer.html`, `get_coords_for_body_rid`: "Such an RID can be retrieved from KinematicCollision2D.get_collider_rid(), when colliding with a tile." Plus, under `physics_quadrant_size`: "To get the exact cell coordinates, you need to set physics_quadrant_size to 1, which disables physics chunking."
- **S005** `docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html`, Behavior changes → TileMapLayer: "get_coords_for_body_rid() will return different values in 4.5 compared to 4.4, as TileMapLayer physics chunking is enabled by default."
- **S027** `docs.godotengine.org/en/4.7/classes/class_kinematiccollision2d.html`, `get_collider_rid`: "Returns the colliding body's RID used by the PhysicsServer2D."

## Headline measured finding

Docs confirmed **and sharpened**: at quadrant 16 the return is the *quadrant index* (`floor(cell/16)` — (5,0)→`0,0`, (15,0)→`0,0`, (21,0)→`1,0`), not a cell coordinate of any kind; `use_kinematic_bodies` leaves attribution identical; `get_collider()` is the `TileMapLayer` node in both modes. Hypothesis confirmed: r92's pin measured the wrong RID.

## Risks/notes

- One fixture-ordering lesson baked into a code comment: `TileData` collision polygons must be written **after** `ts.add_source(src)` (`physics.size()=0` bound error otherwise).
- `wrongrid` emits one engine ERROR (allowlisted above); if L1 prefers ERROR-clean rows, dropping `own_coords` loses the r92-pin reproduction — keep it.
- Fixture runs ~1 s/arm; never echoes nested ERROR text itself.
- Not edited: `run_battery.py` (tuples + expected_errors dict entry + gate clause above are L1's to land).
