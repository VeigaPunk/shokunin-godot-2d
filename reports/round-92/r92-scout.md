# game-dev-2d round 92 — scout (r92-scout): the TileMapLayer/TileSet authorability lattice, pre-measured; 13 rows verbatim-ready

Seat `SCOUT` (LEAF) | lane `r92-scout` | round 92 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps default (plus a generated 120 tps project variant), GodotPhysics2D.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at session start **`520ed6d`**
(*r90 boundary: 281 runs — ordering confirmed 60/120tps…*); HEAD moved to **`506ec8b`**
mid-session (a concurrent lane's r88 ADMIT-corr fold, touching `LOG.md`, `SCORECARD.md` and
two `reports/round-88/*` files only — **no probe-relevant file**; `git diff --stat
520ed6d..506ec8b` = 4 files, 240 insertions). All measurements here are probe/API receipts
independent of that commit. The launch `project.godot` is the byte-copy of
`corpus/fixtures/project.godot` (`8de8b3af…`).

**No git mutation, no tracked file written, no subagent, no commit.** Writes are this
report and `corpus/live/r92-scout/**` only. `git status --porcelain` shows no tracked
modification attributable to this seat (the one pre-existing modified tracked file,
`corpus/fixtures/run_battery.py`, is a concurrent lane's edit and is untouched here).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server
installed; `definition`/`references`/`hover` were **unavailable for every file touched**.
Semantic carriers: fresh-process execution receipts, `ClassDB`/runtime introspection inside
the probes, and engine-emitted error text. Every `file:line` below is engine-emitted `at:`
backtrace text, never a source read (no engine source tree on this host).

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Primary: the TileMapLayer/TileSet authorability lattice** — cell set/erase/readback,
atlas-source and alternative-tile management, custom data layers, the terrain/autotiling
placement API, `TileMapPattern` get/set/`map_pattern`, the `tile_map_data` byte encoding,
invalid-tile repair, source-id allocation, the physics quadrant and per-tile collision
polygons, navigation layers and region registration, and **update timing vs physics
frames** (the `set_cell`/`erase_cell`/`collision_enabled`/transform/`update_internals`
lever lattice). This is the brief's assigned surface.

Three facts justify the pick, all measured or verified this session:

- **Near-zero existing coverage.** `grep -rin "tilemap\|tile_set\|TileSet" corpus/fixtures/
  --include=*.gd --include=*.py --include=*.tscn` finds only three *consumer* fixtures
  (`contact_probe.gd`, `level_collision/level_probe.gd`, `level_collision/level_scene.tscn`)
  that instantiate a scene and read one cell's collision polygon. **No battery row touches
  the TileMapLayer/TileSet runtime API** — `set_cell`, terrains, custom data, patterns,
  encoding, quadrant, navigation and update timing are all unmeasured **[O]**.
- **The r91 scout explicitly handed it over.** r91 §0 weighed TileMapLayer as candidate (b)
  and deferred it ("every interesting cell … first needs a hand-built `TileSet` with physics
  polygons/terrains"), and r91 §8 lists TileMapLayer among the candidates "weighed but not
  measured" **[O]**. This round builds the hand-built TileSet and closes it.
- **The surface has a real falsifiable contract.** The naive author model — "`set_cell`
  writes the cell, so the collision is there" — is refuted in four independent ways below
  (§4.1–§4.3), and the surface also hides a **deterministic SIGSEGV reachable from script**
  (§5.1) in the same crash class as r85's `joint_make_pin` and r91's avoidance teardown.

**Bounded secondary split (3 arms × 3 reps):** a generated **120 tps** project variant for
`timing`/`physics`/`nav`. Reason: the central law is a *frame-count* claim, so it must be
shown to be clock-independent; the three receipts are byte-identical to their 60 tps
counterparts (§4.1), which converts "1 frame" from an observation into a law.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (23 arms, fresh process each) | feasibility: class census, atlas/alternative tiles, cell lattice, custom data, physics contact, timing, terrain, nav, pattern, encoding, quadrant, source ids, null-TileSet crash | `runs/disc-*.{out,err}` |
| 2 | `bash run_cells.sh` | **13 cells** (9 pure ×3, 4 physics-await ×6) = **51 runs** | `runs/r92_tm_*.{out,err,rc}` |
| 3 | `python3 analyze_r92.py` | per-cell reps / out-uniq / err-uniq / rc vectors | `runs/analyze_r92.json` |
| 4 | `bash run_loadtest.sh` (16 deliberate `yes` hogs, load avg **118.85**) | 13 runs over all 13 arms | `runs/loadtest/` |
| 5 | 120 tps project variant | 3 arms × 3 reps = 9 runs | `runs/tps120/` |
| 6 | `python3 make_author_rows.py` → `verify_rows.py` → `forge_rows.py` | 13 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) + 368 mutant kills | `author-rows.py.txt` |

**Canonical cell set: 51 runs across 13 cells**, all `rc=0`; no cell crashed; no run left
running. **Byte-stability: all 13 cells are `out_uniq=1 err_uniq=1` with a constant `rc`
vector** (`runs/analyze_r92.json`: `UNSTABLE=[]`, `CRASH_CELLS=[]`). Unlike r87/r89/r91 —
each of which carried at least one bimodal or counter-bearing cell — **this lattice has no
mode cell and no load-sensitive counter**: all 13 loadtest receipts are **byte-identical**
to their canonical reps (`LOAD_REJECTIONS: []`), and all 9 tps-120 receipts are
byte-identical to their 60 tps counterparts.

**Arm-dispatch integrity [O]:** every arm prints its own name on its `PASS` line
(`PASS tilemap_lattice <arm> …`), so a silent `_:` fallback (the r88 dead-seat failure) is
impossible to miss; `arm` is parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan). The probe carries a 20 s watchdog
that quits `FAIL … reason=watchdog` instead of hanging if an arm dies mid-way.

**Error budget [M]:** 9 of 13 cells emit deterministic engine ERROR lines (they are
documented refusals; all are in the row allowlists, §6.1); `census`, `timing`, `quadrant`
are `ERROR:`-clean with 0 B stderr; `nav` carries only the `make_polygons_from_outlines()`
deprecation WARNING (no `ERROR:` line, so it is classifier-inert — the same warning r91
§3.8 budgeted).

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **Class/property/default census** (TileMapLayer/TileSet/AtlasSource/TileData/Pattern) | **PINNABLE** | 3 | uniq=1 |
| **Atlas source + alternative tiles** (tile creation, alt ids, source ids) | **PINNABLE** | 3 | uniq=1 |
| **Cell set/erase/clear lattice** (incl. poison cells, mapping, neighbors, flips) | **PINNABLE** | 3 | uniq=1 |
| **Custom data layers** (registration, defaults, wrong-typed writes, removal) | **PINNABLE** | 3 | uniq=1 |
| **Terrain sets + `set_cells_terrain_connect`/`_path`** | **PINNABLE** | 3 | uniq=1 |
| **`TileMapPattern`** (get/set/`map_pattern`, sparse bounding box) | **PINNABLE** | 3 | uniq=1 |
| **`tile_map_data` encoding** (header + 12 B/cell, tombstones, round trip, refusals) | **PINNABLE** | 3 | uniq=1 |
| **Invalid-tile repair** (`fix_invalid_tiles`) | **PINNABLE** | 3 | uniq=1 |
| **Source-id allocation** (auto/explicit/move/remove/refusals) | **PINNABLE** | 3 | uniq=1 |
| **Physics quadrant + per-tile collision** | **PINNABLE** (lever lattice, 1-frame deferral) | 6 | uniq=1 |
| **Update timing vs physics frames** | **PINNABLE law** — one physics step; `update_internals()` is the only synchronous lever | 6 | uniq=1 (60 = 120 tps) |
| **`physics_quadrant_size`** | **PINNABLE control** (partitioning knob, not a correctness knob) | 6 | uniq=1 |
| **Navigation layers + region registration** | **PINNABLE** (same 1-frame deferral) | 6 | uniq=1 |
| **Null-TileSet + written cell + `get_cell_tile_data`** | **PINNABLE hazard** (rc=134 SIGSEGV vector, not a row) | discovery ×3 | deterministic |
| **`has_body_rid` / `get_coords_for_body_rid`** | **PINNABLE negative** (never true from script) | discovery ×4 | deterministic |

---

## 3. Measured values, verbatim

All payloads are `runs/r92_tm_<cell>.rep1.out`; coordinates `%.4f`; coords lists
`n<N>[x,y;…]`; booleans `1`/`0`.

### 3.1 Census (`tm_census`) — [M]

```
PASS tilemap_lattice census layer_defaults=enabled=1 collision_enabled=1 nav_enabled=1 use_kinematic=0 phys_quad=16 rend_quad=16 col_vis=0 nav_vis=0 y_sort_origin=0 x_draw_rev=0 occl=1 layer_props=n16[collision_enabled,collision_visibility_mode,enabled,navigation_enabled,navigation_visibility_mode,occlusion_enabled,physics_quadrant_size,rendering_quadrant_size,tile_map_data,tile_set,use_kinematic_bodies,x_draw_order_reversed,y_sort_origin] layer_no_collision_priority=1 ts_defaults=tile_size=16,16 physics_layers=0 nav_layers=0 custom_data_layers=0 terrain_sets=0 occlusion_layers=0 sources=0 tile_shape=0 tile_layout=0 tile_offset_axis=0 uv_clipping=0 atlas_defaults=region=16,16 margins=0,0 separation=0,0 tiles=0 padding=1 enum_terrainset=MATCH_CORNERS_AND_SIDES=0 MATCH_CORNERS=1 MATCH_SIDES=2 enum_tileshape=SQUARE=0 ISOMETRIC=1 HALF_OFFSET_SQUARE=2 HEXAGON=3 enum_neighbor=RIGHT_SIDE=0 RIGHT_CORNER=1 BOTTOM_RIGHT_SIDE=2 BOTTOM_RIGHT_CORNER=3 BOTTOM_SIDE=4 TOP_RIGHT_CORNER=15 invalid_source=-1 class_method_counts=TileMapLayer=58 TileSet=90 TileSetAtlasSource=41 TileData=54 TileMapPattern=10
```

- `TileMapLayer` has **16 properties and no `collision_priority`** (`layer_no_collision_priority=1`)
  — the property does not exist on this build even though the class docs name it **[M]**. The
  layer's own defaults are all permissive: `enabled=true`, `collision_enabled=true`,
  `navigation_enabled=true`, `occlusion_enabled=true`, `physics_quadrant_size=16`,
  `rendering_quadrant_size=16`, `collision_visibility_mode=0`,
  `navigation_visibility_mode=0`, `y_sort_origin=0`, `use_kinematic_bodies=false` **[M]**.
- `TileSet` defaults: `tile_size=(16,16)`, **zero** physics/navigation/custom-data/terrain/
  occlusion layers, `tile_shape=0` (SQUARE), `tile_layout=0`, `tile_offset_axis=0`,
  `uv_clipping=false` **[M]**. A fresh `TileSetAtlasSource` has `texture_region_size=(16,16)`,
  `margins=(0,0)`, `separation=(0,0)`, `use_texture_padding=true`, **0 tiles** **[M]**.
- Enum orders are author-traps: `PATH_POSTPROCESSING`-style ordering does not apply here, but
  **`TERRAIN_MODE_MATCH_CORNERS_AND_SIDES=0`** (not "none"), and `CELL_NEIGHBOR` starts
  `RIGHT_SIDE=0, RIGHT_CORNER=1, BOTTOM_RIGHT_SIDE=2, BOTTOM_RIGHT_CORNER=3, BOTTOM_SIDE=4,
  … TOP_RIGHT_CORNER=15` **[M]** — the "corner" and "side" neighbours interleave, so an
  author who assumes `RIGHT_SIDE`/`LEFT_SIDE` are 0/1 gets the wrong cell.
- Class method counts (`58/90/41/54/10`) are the **only engine-build constants** in the row
  set; §6.1 gives a prefix form that cuts them.

### 3.2 Atlas source + alternative tiles (`tm_atlas`) — [M]

```
PASS tilemap_lattice atlas sid_first=0 count_1=1 has_source_0=1 src_class=TileSetAtlasSource tiles_after_2=2 has_tile_00=1 has_tile_11=0 tiles_list=n2[0,0;1,0] tiles_after_dup=2 alt_id=1 alt_count=2 alt_list=n2[0;1] has_alt_0=1 has_alt_1=1 has_alt_7=0 td_class=TileData td_alt_distinct=1 td_missing=null tiles_after_remove=1 has_tile_10_after=0 sid_explicit_7=7 ids=n2[0;7] next_source_id=1 grid_size=2,2 tile_size_in_atlas=1,1 tex_region=[P: (0, 0), S: (16, 16)]
```

- The first `add_source` returns **id 0**; a second with an explicit id returns **7** and the
  id list is `[0;7]` while **`get_next_source_id()` stays 1** — the "next id" is the lowest
  free slot, not `max+1` **[M]**.
- `create_tile` is **idempotent-by-refusal**: the second call on the same coords logs
  `ERROR: Cannot create tile. The tile is outside the texture or tiles are already present…`
  and the tile count does not change (`tiles_after_dup=2`) **[M]**.
- `create_alternative_tile` on a tile that already has alternative 0 returns **1**; the tile
  now has alternatives `[0;1]` (`alt_count=2`), each with a **distinct `TileData`**
  (`td_alt_distinct=1`) **[M]**. `has_alternative_tile(coords, 7)` is false.
- `get_tile_data` on a coords with no tile logs `ERROR: The TileSetAtlasSource atlas has no
  tile at (5, 5).` and returns **null** **[M]**.
- `grid_size=(2,2)`, `tile_size_in_atlas=(1,1)`, `tex_region=[P: (0, 0), S: (16, 16)]` for a
  32×32 texture with 16×16 regions **[M]**.

### 3.3 Cell set/erase/clear (`tm_cells`) — [M]

```
PASS tilemap_lattice cells empty_used=n0[] empty_rect=[P: (0, 0), S: (0, 0)] empty_source=-1 empty_atlas=-1,-1 empty_alt=-1 empty_td=null used_after_3=n3[0,0;3,2;-2,-1] rect_after_3=[P: (-2, -1), S: (6, 4)] src_3_2=0 atlas_3_2=1,0 td_3_2=obj same_frame_td=obj same_frame_used_has=1 erase_src=-1 erase_used_n=3 erase_used_n2=2 erase_absent_ok=1 bad_src_readback=42 bad_src_in_used=1 bad_atlas_readback=9,9 bad_atlas_td=null used_by_id_src=n3[-2,-1;9,9;6,6] used_by_id_bad=n1[5,5] clear_used_n=0 clear_rect=[P: (0, 0), S: (0, 0)] map_to_local_1_1=24.0000,24.0000 map_to_local_neg=-8.0000,-8.0000 local_to_map_16_16=1,1 local_to_map_8_8=0,0 local_to_map_neg=-1,-1 surrounding=n4[1,0;0,1;-1,0;0,-1] neighbors_valid8=BOTTOM_LEFT_CORNER:-1,1|BOTTOM_RIGHT_CORNER:1,1|BOTTOM_SIDE:0,1|LEFT_SIDE:-1,0|RIGHT_SIDE:1,0|TOP_LEFT_CORNER:-1,-1|TOP_RIGHT_CORNER:1,-1|TOP_SIDE:0,-1 neighbors_invalid4=BOTTOM_CORNER:0,0|BOTTOM_RIGHT_SIDE:0,0|RIGHT_CORNER:0,0|TOP_RIGHT_SIDE:0,0 empty_flip_h=1 empty_flip_v=1 empty_transpose=1 set_flip_h=0 set_flip_v=0 set_transpose=0
```

- The empty-cell sentinel is **`source_id=-1`, `atlas=(-1,-1)`, `alternative=-1`,
  `tile_data=null`**, and `get_used_rect()` on an empty layer is `[P: (0, 0), S: (0, 0)]` **[M]**.
- **The data side of a write is immediate**: `same_frame_td=obj` and
  `same_frame_used_has=1` — a cell set at frame N is readable as `TileData` at frame N. (The
  *physics* side is not; §4.1.) **[M]**
- **Poison cells are stored verbatim.** `set_cell(coords, 42, …)` with a non-existent source
  id reads back **42** and the cell **appears in `get_used_cells()` and in
  `get_used_cells_by_id(42)`** (`bad_src_readback=42 bad_src_in_used=1`,
  `used_by_id_bad=n1[5,5]`) **[M]**. `set_cell(coords, sid, (9,9), 0)` with coords outside
  the atlas stores `(9,9)` and its `TileData` is **null** (with one engine ERROR) **[M]**.
  There is no validation on the write path — the only repair is `fix_invalid_tiles()` (§3.9).
- `erase_cell` on an absent cell is a silent no-op (`erase_absent_ok=1`) **[M]**.
- Mapping is centre-based and floor-based: `map_to_local(1,1)=(24,24)` = `(1+0.5)*16`;
  `map_to_local(-1,-1)=(-8,-8)`; `local_to_map((16,16))=(1,1)`; `local_to_map((8,8))=(0,0)`;
  `local_to_map((-1,-1))=(-1,-1)` **[M]**.
- **`get_neighbor_cell` refuses half the enum on a square TileSet**: the 8 square-valid
  peering bits return real neighbours (`RIGHT_SIDE:1,0 … TOP_RIGHT_CORNER:1,-1`), while
  `RIGHT_CORNER`, `BOTTOM_RIGHT_SIDE`, `BOTTOM_CORNER`, `TOP_RIGHT_SIDE` all log
  `ERROR: Method/function failed. Returning: p_coords` and return **the input cell** `(0,0)`
  — a silent wrong answer unless the stderr line is budgeted **[M]**.
- **Empty cells read as flipped *and* transposed** (`empty_flip_h=1 empty_flip_v=1
  empty_transpose=1`), while a real cell reads `0/0/0` **[M]**. `is_cell_flipped_*` is not a
  "is this cell flipped?" query for empty cells — it is a raw flag read.

### 3.4 Custom data layers (`tm_custom`) — [M]

```
PASS tilemap_lattice custom layers_0=0 layers_2=2 name_0=hp type_0=2 index_of_hp=0 index_of_missing=-1 has_layer_hp=1 default_hp=0 default_tag= has_hp=1 hp_7=7 tag_alpha=alpha by_index_0=7 by_index_1=alpha hp_wrongtype=not-an-int hp_wrongtype_still=not-an-int layer_hp=not-an-int layer_tag=alpha ghost=<null> missing=<null> layers_after_remove=1 tag_after_remove=<null> hp_after_remove=not-an-int dup_layers=1 dup_hp=0 dup_is_distinct=1
```

- Custom-data **defaults follow the declared layer type**: `default_hp=0` (int),
  `default_tag=` (empty string) **[M]**; `has_custom_data("hp")` is true for a registered
  layer even when unset **[M]**.
- **The declared type is advisory only**: after declaring layer 0 as `TYPE_INT`, writing the
  string `"not-an-int"` **stores and reads back verbatim** (`hp_wrongtype=not-an-int`), and
  the wrong value is visible through the layer's `TileData` (`layer_hp=not-an-int`) **[M]**.
  Nothing coerces or refuses.
- Unregistered names **refuse loudly**: `set_custom_data("ghost", …)` and
  `get_custom_data("absent")` each log `ERROR: TileSet has no layer with name: …` and return
  `<null>` **[M]**.
- Removing layer 1 makes its name unresolvable — `get_custom_data("tag")` logs
  `ERROR: TileSet has no layer with name: tag` and returns `<null>`, while layer 0's value
  survives (`hp_after_remove=not-an-int`) **[M]**.
- `TileSet.duplicate(true)` keeps the layer registry (`dup_layers=1`, `dup_name`=hp) but the
  duplicated `TileData` is a **distinct object with the tile's default value**, not the
  mutated one (`dup_hp=0`, `dup_is_distinct=1`) — the deep copy is taken from the *source*
  tile data, so a wrong-typed write made through one `TileData` handle is not what the
  duplicate carries **[M]**. (Bounded: measured on one tile/one layer only.)

### 3.5 Terrain (`tm_terrain`) — [M]

```
PASS tilemap_lattice terrain sets_0=0 sets_1=1 mode_default=0 mode_set=0 terrains_0=0 terrains_2=2 names=grass,dirt color_0=(0.0, 1.0, 0.0, 1.0) td_terrain_set_default=-1 td_terrain_default=-1 td_terrain_set=0 td_terrain=0 peering_right=1 peering_left=-1 peering_right_valid=1 peering_right_corner_valid=0 connect_used=n2[1,0;0,0] connect_src_0_0=0 connect_atlas_0_0=0,0 connect_atlas_1_0=0,0 connect_atlas_2_0=-1,-1 connect_dirt_used=n3[1,0;0,0;2,0] connect_dirt_atlas_0_0=1,0 path_used=n2[1,0;0,0] bad_set_used=n0[] bad_terrain_used=n0[] no_terrain_used=n0[]
```

- `TileData.terrain_set` and `terrain` default to **-1** (unassigned) **[M]**;
  `TERRAIN_MODE_MATCH_CORNERS_AND_SIDES` is **0** and is already the default
  (`mode_default=0 mode_set=0`) **[M]**.
- Peering bits: `peering_right=1` after a set; an unset bit reads **-1**;
  `is_valid_terrain_peering_bit(RIGHT_SIDE)=1` but **`(RIGHT_CORNER)=0`** — the same
  8-of-16 square rule as `get_neighbor_cell` **[M]**.
- **`set_cells_terrain_connect` places only cells whose tile carries the requested terrain.**
  With only tile `(0,0)` assigned grass and `(1,0)` assigned dirt, connecting
  `[(0,0),(1,0),(2,0)]` with terrain 0 places **2 cells** (`n2[1,0;0,0]`) and both use atlas
  `(0,0)`; the third cell is simply absent (`connect_atlas_2_0=-1,-1`) **[M]**. Asking for
  terrain 1 places **3 cells** (`n3[1,0;0,0;2,0]`) and the tile used is the dirt tile
  (`connect_dirt_atlas_0_0=1,0`) **[M]**. **The placement API silently drops the cells it
  cannot fill** — no error, no partial-failure signal.
- `set_cells_terrain_path` on this single-terrain layout produces the same 2-cell result as
  `_connect` (`path_used=n2[1,0;0,0]`) **[M]** — the two differ only on multi-terrain paths.
- Refusals are loud and total: terrain-set index 5 → `ERROR: Index p_terrain_set = 5 is out of
  bounds (tile_set->get_terrain_sets_count() = 1).` and **0 cells**; terrain index 9 → 0 cells;
  a tileset with no terrains at all → 0 cells **[M]**.

### 3.6 Pattern (`tm_pattern`) — [M]

```
PASS tilemap_lattice pattern class=TileMapPattern size=2,2 used=n3[0,0;1,0;0,1] src_0_0=0 atlas_1_0=1,0 has_cell_0_0=1 empty_at_1_1=-1 is_empty=0 empty_size=0,0 empty_used=n0[] empty_is_empty=1 set_used=n3[4,4;5,4;4,5] set_rect=[P: (4, 4), S: (2, 2)] set_atlas_5_4=1,0 sparse_size=5,5 sparse_used=n2[0,0;4,4] sparse_hole_src=-1 map_pattern_10_10_1_0=11,10 map_pattern_0_0_0_0=0,0 cross_layer_used=n1[-2,-2] cross_layer_atlas=0,0
```

- `get_pattern(coords)` returns a `TileMapPattern` whose **size is the bounding box** of the
  requested coords and whose `get_used_cells()` lists only the non-empty ones **[M]**.
- **Querying an empty cell inside a pattern refuses loudly**:
  `ERROR: Condition "!pattern.has(p_coords)" is true. Returning: TileSet::INVALID_SOURCE`
  and `-1` — the refusal is per-query, so a probe that reads a hole must budget it **[M]**.
- `get_pattern([])` yields an empty pattern with **size `(0,0)`**, `is_empty()=true` **[M]**.
- `set_pattern((4,4), pattern)` offsets the whole pattern (`n3[4,4;5,4;4,5]`,
  `rect=[P: (4, 4), S: (2, 2)]`) and works across layers, including negative positions
  (`cross_layer_used=n1[-2,-2]`) **[M]**.
- `map_pattern(position_in_this, position_in_pattern, pattern)` is a **pure translation**
  (`(10,10),(1,0)→(11,10)`; `(0,0),(0,0)→(0,0)`) — argument order is
  `(this, pattern, pattern)` and the return is a single `Vector2i`, not a list **[M]**
  (three parse failures pinned the signature during discovery).

### 3.7 `tile_map_data` encoding (`tm_encoding`) — [M]

```
PASS tilemap_lattice encoding empty_bytes_len=0 empty_arr_len=0 one_bytes_len=14 one_bytes=[0,0,3,0,4,0,0,0,1,0,0,0,0,0] two_bytes_len=26 two_bytes=[0,0,3,0,4,0,0,0,1,0,0,0,0,0,7,0,254,255,0,0,0,0,1,0,0,0] two_arr_len=26 two_arr_equals_bytes=1 stride=12 alt_bytes=[0,0,3,0,4,0,0,0,1,0,0,0,1,0,7,0,254,255,255,255,255,255,255,255,255,255] alt_id_created=1 tomb_set_bytes=[0,0,1,0,1,0,0,0,0,0,0,0,0,0] tomb_erase_len=14 tomb_erase_bytes=[0,0,1,0,1,0,255,255,255,255,255,255,255,255] tomb_erase_used=n0[] tomb_reset_len=14 tomb_reset_bytes=[0,0,1,0,1,0,0,0,0,0,0,0,0,0] tomb_clear_len=14 tomb_clear_bytes=[0,0,1,0,1,0,255,255,255,255,255,255,255,255] tomb_clear_set_len=26 tomb_clear_set_bytes=[0,0,1,0,1,0,255,255,255,255,255,255,255,255,5,0,5,0,0,0,0,0,0,0,0,0] arr_roundtrip_used=n2[3,4;7,-2] arr_roundtrip_src=0 arr_roundtrip_atlas=0,1 short_arr_used=n0[] short_arr_len=0 truncated_used=n1[3,4] truncated_len=14
```

- **Layout [M]:** a 2-byte header (`[0,0]`) followed by **12-byte little-endian cell
  records** — `x:int16, y:int16, source_id:int16, atlas_x:int16, atlas_y:int16,
  alternative:int16`. A 1-cell layer is 14 B, a 2-cell layer 26 B (`stride=12`), an empty
  layer 0 B. `(3,4)`/source 0/atlas `(1,0)`/alt 0 encodes as `[3,0,4,0,0,0,1,0,0,0,0,0]`;
  `(7,-2)` encodes `y` as `[254,255]` (= `0xFFFE`) **[M]**.
- **`get_tile_map_data_as_array()` is the same bytes widened to ints** — `two_arr_len=26`
  and `two_arr_equals_bytes=1`, i.e. the array form is *not* a structured row list **[M]**.
- **Erasure is an in-place tombstone, not a removal [M]:** `erase_cell` rewrites the record's
  last 6 fields to `0xFFFF` (`[1,0,1,0, 255,255,255,255,255,255,255,255]` = source -1,
  atlas (-1,-1), alt -1) and **keeps the 14 bytes**; `get_used_cells()` is empty but
  `tile_map_data.size()` is unchanged. Re-setting the same cell restores the record in place
  (`tomb_reset_len=14`). **`clear()` tombstones every record rather than truncating**
  (`tomb_clear_len=14`, all-`0xFFFF` payload), and a later `set_cell` at a new coord
  **appends** (`tomb_clear_set_len=26`) **[M]**. Author consequence: buffer size tracks the
  high-water mark of written cells, never shrinks, and a "did I erase this?" check must read
  `get_used_cells()`, not the buffer.
- Round trip works through both forms (`arr_roundtrip_used=n2[3,4;7,-2]`,
  `bytes_roundtrip` identical) **[M]**.
- Refusals are loud and *destructive*: a 3-int array logs
  `ERROR: Unsupported tile map data format: 513. Expected format ID lower or equal to: 0`
  (the header is read as a format id) and leaves the layer **empty** (`short_arr_len=0`);
  a truncated real buffer logs `ERROR: Corrupted tile map data: tiles might be missing.` and
  keeps only the records it could fully parse (`truncated_used=n1[3,4]`, `truncated_len=14`)
  **[M]** — the malformed path does not preserve the prior contents.

### 3.8 Source ids (`tm_srcids`) — [M]

```
PASS tilemap_lattice srcids auto_id=0 next_after_auto=1 explicit_5=5 next_after_explicit=1 ids=n2[0;5] id_index_0=0 id_index_1=5 moved_ids=n2[0;2] has_2=1 has_5=0 removed_ids=n1[0] count=1 add_null=-1 count_after_null=1 add_colliding=-1 count_after_colliding=1 add_negative=-1 ids_after_refusals=n1[0]
```

- `add_source` auto-allocates 0, then `get_next_source_id()` is **1**; after an explicit id 5
  it **stays 1** — the next id is the lowest free slot, not `max+1` **[M]**.
- `set_source_id(old, new)` **moves** the source (`ids=n2[0;5] → moved_ids=n2[0;2]`,
  `has_2=1 has_5=0`) **[M]**.
- All three refusal paths return **`-1` and leave the count unchanged**: a null source
  (`ERROR: Condition "p_tile_set_source.is_null()" is true. Returning:
  TileSet::INVALID_SOURCE`), a colliding id (`ERROR: Cannot create TileSet atlas source.
  Another atlas source exists with id 0.`), and a negative id (`ERROR: Provided source ID -3
  is not valid. Negative source IDs are not allowed.`) **[M]**.

### 3.9 Invalid-tile repair (`tm_fixinvalid`) — [M]

```
PASS tilemap_lattice fixinvalid before_used=n3[0,0;1,0;2,0] after_used=n1[0,0] after_src_1_0=-1 after_src_2_0=-1 removed_used=n1[0,0] removed_fixed_used=n0[]
```

- `fix_invalid_tiles()` **deletes** cells whose source id or atlas coords do not resolve: the
  poison cells `(1,0)` (source 42) and `(2,0)` (atlas `(9,9)`) are gone, the valid `(0,0)`
  survives **[M]**.
- Removing the source invalidates every cell that used it (`removed_used=n1[0,0]` — the cell
  is still *present* until repaired), and a second `fix_invalid_tiles()` clears the layer
  (`removed_fixed_used=n0[]`) **[M]**. Repair is explicit; nothing self-heals.

### 3.10 Physics (`tm_physics`) — [M]

```
PASS tilemap_lattice physics phys_layers=1 layer_defaults=cl=1 cm=1 prio=1.0000 mat_null=1 polys_0=0 polys_1=1 poly_pt0=-8.0000,-8.0000 poly_oneway=0 poly_oneway_set=1 m=4.0000 tile0=hit tile1_no_polygon=null tile0_again=hit disabled_same_frame=hit disabled_f1=null enabled_same_frame=null enabled_f1=hit erase_same_frame=hit erase_f1=null collider=class=TileMapLayer travel=0.0000,1.9531 normal=0.0000,-1.0000 is_layer=1 shape=true coords_for_untracked_body=0,0 has_body_rid=0 kinematic_use=1 kinematic_body_tracked=0 kinematic_coords=0,0
```

- A fresh physics layer is `collision_layer=1 collision_mask=1 priority=1.0 material=null` **[M]**.
- Collision is **per tile**: `(0,0)` (with the polygon) hits, `(1,0)` (same source, no polygon)
  does not (`tile1_no_polygon=null`), and `(0,0)` still hits afterwards **[M]**.
- **All four physics levers defer by exactly one physics step** — `disabled_same_frame=hit`
  then `disabled_f1=null`; `enabled_same_frame=null` then `enabled_f1=hit`;
  `erase_same_frame=hit` then `erase_f1=null` **[M]**. The naive "`collision_enabled=false`
  takes effect immediately" model is **refuted** (it was my own working hypothesis, §7 F4).
- The collider is the **TileMapLayer node itself** (`class=TileMapLayer`, `is_layer=1`), with
  `local_shape` present and a **surface normal of `(0,-1)`** and `travel=(0, 1.9531)` for a
  20 px downward test motion from `y=-6` (probe half-height 4 ⇒ contact at `y=0`; the
  measured travel is 0.0469 px short of the geometric 2.0, a constant of this
  shape/step combination, byte-stable over 7 receipts) **[M]**.
- `get_coords_for_body_rid` on a body the layer never tracked logs
  `ERROR: Parameter "found" is null.` and returns **`(0,0)`**, and `has_body_rid` is **0** **[M]**.
- **Body tracking is unreachable from script on this build [M]:** even with
  `use_kinematic_bodies=true` and a body resting on the tiles for 3 frames,
  `kinematic_body_tracked=0` and `kinematic_coords=0,0`. An independent discovery run with a
  `RigidBody2D` falling under gravity onto the tile row (position `y: -40 → 60.3`, stopping
  exactly at the tile top, i.e. collision confirmed) also never set `has_body_rid`
  (`runs/disc3-kin.err`) **[M]**. Both API calls are therefore **unusable as author
  witnesses** — a probe must use a `move_and_collide` witness instead.

### 3.11 Update timing vs physics frames (`tm_timing`) — [M], the core law

```
PASS tilemap_lattice timing empty=null set_same_frame_physics=null set_same_frame_td=obj set_same_frame_used=1 set_f1=hit set_f2=hit move_same_frame=hit move_f1=null move_f2=null moved_back=hit erase_same_frame=hit erase_f1=null notify_same_frame=null notify_f1=hit update_erase_same_frame=null update_erase_f1=null update_set_same_frame=hit data_immediate_control=1
```

| lever | same frame | +1 physics frame | +2 |
|---|---|---|---|
| `set_cell` (data: `get_cell_tile_data`, `get_used_cells`) | **visible** | visible | visible |
| `set_cell` (physics: `move_and_collide` witness) | **absent** | **present** | present |
| `erase_cell` (physics) | **present** | **absent** | absent |
| `layer.position` change (physics) | **old place** | **new place** | new place |
| `collision_enabled=false/true` (§3.10) | **old state** | **new state** | new state |
| `notify_runtime_tile_data_update()` | **absent** | present | present |
| **`update_internals()`** | **applied** | applied | applied |

- **The law: a runtime cell/transform/flag write is applied to the physics space at the
  next physics step; the tile-data side is immediate. `update_internals()` is the only
  synchronous apply lever; `notify_runtime_tile_data_update()` is not.** **[M]**
- The synchronous apply is symmetric: `update_set_same_frame=hit` **and**
  `update_erase_same_frame=null` in the same frame, with `update_erase_f1=null` (it stays
  applied) **[M]**.
- **The law is a frame count, not a duration [M]:** the identical arm under a generated
  **120 tps** project is byte-identical to the 60 tps receipt (9/9 receipts, `uniq=1`).

### 3.12 Physics quadrant (`tm_quadrant`) — [M]

```
PASS tilemap_lattice quadrant default_quad=16 quad16_near=hit quad16_far=hit quad_set=2 quad2_same_frame_far=hit quad2_f1_far=hit quad2_near=hit quad2_spread=0,0:hit|15,0:hit|16,0:hit|40,0:hit quad16_spread=0,0:hit|15,0:hit|16,0:hit|40,0:hit quad_restored=16 rendering_quad_untouched=16
```

- `physics_quadrant_size` defaults to **16** and is independent of
  `rendering_quadrant_size` (also 16) **[M]**.
- **It is a partitioning knob, not a correctness knob [M]:** four cells at `x ∈ {0, 15, 16,
  40}` — deliberately straddling the 16-cell quadrant boundary — stay collidable under both
  `physics_quadrant_size=16` and `=2` (`quad16_spread` and `quad2_spread` are all `hit`), and
  the runtime change is itself deferred one step (`quad2_same_frame_far=hit` is the stale
  read) **[M]**. The row is a *control*: it pins that the knob does not change collision
  availability on this geometry.

### 3.13 Navigation (`tm_nav`) — [M]

```
PASS tilemap_lattice nav nav_layers=1 nav_layer_defaults=layers=1 value1=1 nav_layer_set=3 nav_poly_default=null nav_poly_set=obj layer_nav_enabled=1 layer_nav_vis=0 nav_map_valid=1 regions_empty=0 regions_same_frame=0 regions_f1=1 regions_f2=1 regions_after_plain_cell=1 regions_disabled_same_frame=1 regions_disabled_f1=0 regions_reenabled=1 regions_erased_same_frame=1 regions_erased_f1=0
```

- A fresh navigation layer is `layers=1` with bit 1 set (`value1=1`); `TileData.navigation_polygon(0)`
  defaults to **null** and accepts a hand-built `NavigationPolygon` **[M]**.
- **The TileMapLayer auto-registers a navigation region per cell that carries a navigation
  polygon** — `regions_empty=0` → `regions_same_frame=0` → **`regions_f1=1`** (one physics
  step) **[M]**.
- A cell whose tile has **no** navigation polygon does not add a region
  (`regions_after_plain_cell=1` — unchanged) **[M]**.
- `navigation_enabled=false` and `erase_cell` both remove the region **one step later**
  (`..._same_frame=1`, `..._f1=0`), and re-enabling restores it (`regions_reenabled=1`) **[M]**.
  This is the same one-physics-step law as §4.1, on a third independent subsystem.
- The nav WARNING from `make_polygons_from_outlines()` is the r91-known deprecation line; it
  carries no `ERROR:` substring and is classifier-inert **[M]**.

---

## 4. Laws

### 4.1 The one-physics-step application law [M]
Runtime writes that affect the physics/navigation space — `set_cell`, `erase_cell`,
`collision_enabled`, the layer transform, `navigation_enabled` — are **applied at the next
physics step**, never in the frame that performed the write. The tile-data side of the same
write (`get_cell_tile_data`, `get_used_cells`, `get_cell_source_id`) **is** immediate. The
same-frame read after a write is therefore the *stale* answer, and a probe that reads it
without a step will pin the old state. **Author rule: after any runtime cell/flag/transform
write, await at least one `physics_frame` before asserting collision, navigation, or body
state — or call `update_internals()` if the same frame must see it.** The law is a frame
count, not a duration (60 tps ≡ 120 tps, byte-identical).

### 4.2 The `update_internals` law [M]
`update_internals()` applies pending tile changes to the physics space **synchronously**;
`notify_runtime_tile_data_update()` does **not**. The two are not interchangeable, and only
the former closes the same-frame window opened by §4.1. (Both are public methods on
`TileMapLayer`; `_update_cells`/`_use_tile_data_runtime_update`/`_tile_data_runtime_update`
are the engine's virtual hooks and were not exercised.)

### 4.3 The poison-cell law [M]
The `set_cell` write path performs **no validation**: an unknown `source_id` (42), an
atlas coords outside the texture, and a null `TileSet` are all accepted and stored verbatim.
The invalid cell then participates in `get_used_cells()` and `get_used_cells_by_id()`, and
its `TileData` is null. **Repair is explicit** via `fix_invalid_tiles()`; nothing self-heals,
and removing a source leaves its cells present-but-invalid until repaired. **Author rule:
validate `source_id`/`atlas_coords` yourself, or call `fix_invalid_tiles()` after any
`remove_source`/`remove_tile`.**

### 4.4 The tombstone-encoding law [M]
`tile_map_data` is a 2-byte header plus 12-byte little-endian cell records
(`x, y, source_id, atlas_x, atlas_y, alternative`). **`erase_cell` writes an in-place
tombstone (`source_id = atlas = alternative = -1`) rather than removing the record, and
`clear()` tombstones every record instead of truncating**; later writes append at the end.
The buffer therefore grows to the high-water mark of written cells and never shrinks, while
`get_used_cells()` reports the semantic truth. `get_tile_map_data_as_array()` is the same
byte sequence widened to ints, not a row list.

### 4.5 The terrain-placement law [M]
`set_cells_terrain_connect`/`_path` **silently drop any requested cell whose tile cannot
satisfy the requested terrain** — no error, no partial-failure signal, and the resulting
`get_used_cells()` simply lacks those cells. Only an out-of-range *terrain set* or *terrain*
index refuses loudly (and then places nothing). **Author rule: never infer "the connect
succeeded" from the call returning; assert `get_used_cells()`.**

### 4.6 The square-shape 8-of-16 law [M]
On a `TILE_SHAPE_SQUARE` TileSet only 8 of the 16 `CellNeighbor` values are valid: the four
sides plus the four diagonals. The other eight (`*_CORNER` half-offsets and the
hex/isometric `*_SIDE` half-offsets) are **refused with an engine ERROR and return the input
cell** from `get_neighbor_cell`, and are **invalid** for `is_valid_terrain_peering_bit` /
`get_terrain_peering_bit`. A caller that does not budget the stderr line silently reads the
wrong cell.

### 4.7 The null-TileSet crash law [M] — hazard, not a row
A `TileMapLayer` whose `tile_set` is null **crashes the process (SIGSEGV, rc=134)** when
`get_cell_tile_data` is called on a cell that was written while the TileSet was null. The
trigger needs **both** halves: a null TileSet with *no* written cell is safe
(`get_cell_tile_data` returns null), and `set_cell` itself is safe; only the pair crashes.
Deterministic ×3 (§5.1).

### 4.8 The body-tracking negative [M]
`has_body_rid` / `get_coords_for_body_rid` never report a script-created body on this build —
not for a stationary `CharacterBody2D`, not with `use_kinematic_bodies=true`, and not for a
`RigidBody2D` that fell onto the tiles and stopped. Untracked calls log
`ERROR: Parameter "found" is null.` and return `(0,0)`. Use a `move_and_collide` witness for
collision assertions.

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **Null-TileSet SIGSEGV [M]** (§4.7, §5.1) — a crash class reachable from script in three
   lines. Never call `get_cell_tile_data` (or any tile-data read) on a layer whose
   `tile_set` may be null; guard the assignment instead.
2. **The one-physics-step deferral [M]** (§4.1) — the single most likely source of a
   flaky or silently-stale probe on this surface. Do not pin a same-frame readback after a
   write; use `update_internals()` if you must.
3. **Poison cells [M]** (§4.3) — an invalid `source_id` is stored, appears in
   `get_used_cells()`, and has null `TileData`; it survives until `fix_invalid_tiles()`.
4. **Silent terrain drops [M]** (§4.5) — `set_cells_terrain_connect` returns void and can
   place fewer cells than requested with no diagnostic.
5. **Tombstone buffers [M]** (§4.4) — `clear()` does not shrink `tile_map_data`; a
   size-based "is the layer empty?" test is wrong.
6. **`is_cell_flipped_*` on empty cells reads `true` [M]** (§3.3) — the flag read is raw.
7. **`get_neighbor_cell` half-offset refusals [M]** (§4.6) — the refused values return the
   *input* cell, i.e. a plausible-looking wrong answer plus one ERROR line per call.
8. **`get_cell_tile_data` on a missing atlas coord logs an ERROR and returns null [M]**
   (§3.2/§3.3) — a probe that queries holes must budget the line or use `has_tile` first.
9. **`TileSet.add_source` refusals return `-1` [M]** (§3.8) — a caller that ignores the
   return value silently has no source.
10. **`has_body_rid`/`get_coords_for_body_rid` are unusable as witnesses [M]** (§4.8) — and
    they log an ERROR on the untracked path.
11. **The terrain-path bake WARNING [M]** (§3.13) — `make_polygons_from_outlines()` is
    deprecated on this build; the line has no `ERROR:` substring so it is classifier-inert,
    but a future classifier that tightens WARNING handling would reject the `nav` row.
12. **`tm_census` carries engine-build constants** (`class_method_counts`) — the only field
    in the row set that is not a runtime measurement; §6.1 supplies a prefix form that cuts
    it.

### 5.1 Hazard receipt — the null-TileSet crash [M]

| variant | result | receipt |
|---|---|---|
| null TileSet, no cells, `get_cell_tile_data` | safe, returns null (`td=null`) | `runs/disc4-fresh_td.out` |
| null TileSet, `set_cell` only | safe, `used=1`, `src=0` | `runs/disc4-setcell_only.out` |
| null TileSet, `get_used_cells`/`map_to_local` | safe | `runs/disc4-fresh_used.out`, `runs/disc4-fresh_map.out` |
| **null TileSet + `set_cell` + `get_cell_tile_data`** | **SIGSEGV, rc=134** ×3 | `runs/disc4-setcell_td.r{1,2,3}.err`, `runs/hazard-nullts.r{1,2,3}.err` |

Last diagnostics before the crash (identical in all three reps):
```
R92 nullts tileset_null=1
R92 nullts used_after_set=n1[0,0]
R92 nullts src_after_set=0
R92 nullts about_to_call_tile_data=1
```
`at:` text is a bare `handle_crash: Program crashed with signal 11` + backtrace dump; the
`nullts` arm is **not** a row (rc≠0) — it is filed as a hazard.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (13, exec-checked)

`corpus/live/r92-scout/author-rows.py.txt` holds the 5-tuple sets and the `expected_errors`
dict; `python3 verify_rows.py` classifies every row against **every** canonical + loadtest
receipt with the production `classify_process` (AST-extracted from
`corpus/fixtures/run_battery.py`, segment sha256 `749fa060…` — the same segment r89/r90/r91
pinned):

- **`ROWS` (recommended, gating): 64/64 receipts accepted, `rejected=[]`.**
  Every cell is byte-stable over 3–6 canonical reps *and* byte-identical under load avg
  118.85, so the full-line form is safe — no counter to exclude, no mode envelope needed.
- **`ROWS_PREFIX` (identical except the census tail): 64/64 accepted.** The only difference
  is that `r92_tilemap_census` stops before `class_method_counts=` (an engine-build
  constant); use this form if a future engine bump moves the method counts.

Row names / arms / signature lengths:

| case | flag | sig len |
|---|---|---|
| `r92_tilemap_census` | `--arm=census` | 1103 |
| `r92_tilemap_atlas` | `--arm=atlas` | 463 |
| `r92_tilemap_cells` | `--arm=cells` | 1048 |
| `r92_tilemap_custom` | `--arm=custom` | 436 |
| `r92_tilemap_terrain` | `--arm=terrain` | 560 |
| `r92_tilemap_pattern` | `--arm=pattern` | 428 |
| `r92_tilemap_encoding` | `--arm=encoding` | 912 |
| `r92_tilemap_fixinvalid` | `--arm=fixinvalid` | 157 |
| `r92_tilemap_srcids` | `--arm=srcids` | 301 |
| `r92_tilemap_physics` | `--arm=physics` | 539 |
| `r92_tilemap_timing` | `--arm=timing` | 366 |
| `r92_tilemap_quadrant` | `--arm=quadrant` | 286 |
| `r92_tilemap_nav` | `--arm=nav` | 391 |

`expected_errors` additions (keyed by case name; exact strings in `author-rows.py.txt`):

```python
'r92_tilemap_atlas': (
    'ERROR: Cannot create tile. The tile is outside the texture or tiles are already present in the space the tile would cover.',
    'ERROR: The TileSetAtlasSource atlas has no tile at (5, 5).',
),
'r92_tilemap_cells': (
    'ERROR: Method/function failed. Returning: p_coords',
    'ERROR: The TileSetAtlasSource atlas has no tile at (9, 9).',
),
'r92_tilemap_custom': (
    'ERROR: TileSet has no layer with name: absent',
    'ERROR: TileSet has no layer with name: ghost',
    'ERROR: TileSet has no layer with name: tag',
),
'r92_tilemap_terrain': (
    'ERROR: Index p_terrain_set = 5 is out of bounds (tile_set->get_terrain_sets_count() = 1).',
),
'r92_tilemap_pattern': (
    'ERROR: Condition "!pattern.has(p_coords)" is true. Returning: TileSet::INVALID_SOURCE',
),
'r92_tilemap_encoding': (
    'ERROR: Corrupted tile map data: tiles might be missing.',
    'ERROR: Unsupported tile map data format: 513. Expected format ID lower or equal to: 0',
),
'r92_tilemap_fixinvalid': (
    'ERROR: No TileSet atlas source with id -1.',
    'ERROR: No TileSet atlas source with id 0.',
    'ERROR: No TileSet atlas source with id 42.',
),
'r92_tilemap_srcids': (
    'ERROR: Cannot create TileSet atlas source. Another atlas source exists with id 0.',
    'ERROR: Condition "p_tile_set_source.is_null()" is true. Returning: TileSet::INVALID_SOURCE',
    'ERROR: Provided source ID -3 is not valid. Negative source IDs are not allowed.',
),
'r92_tilemap_physics': (
    'ERROR: Parameter "found" is null.',
),
```

`census`, `timing`, `quadrant` need **no** allowlist entry (0 B stderr over 4 receipts
each); `nav` needs none either (its only stderr is the deprecation WARNING, which contains
no `ERROR:` substring).

Probe file lands at `corpus/fixtures/tilemap_lattice.gd` (sha256 `a699138945ec7c1c…`,
self-contained `SceneTree` script, battery `--arm=` convention, 20 s watchdog). Insert the
rows ahead of the crash/descendant tail like prior blocks; no other fixture change is needed.

### 6.2 What to pin and what not to pin

1. **Pin the `PASS tilemap_lattice …` line** — it carries the arm name, so the r88 silent
   fallback cannot recur.
2. **Pin the lever quartets, not single reads**: `disabled_same_frame=hit disabled_f1=null
   enabled_same_frame=null enabled_f1=hit` and `set_same_frame_physics=null … set_f1=hit`
   *are* the timing law. A row that pins only the settled value loses the law.
3. **Pin `update_set_same_frame=hit` / `update_erase_same_frame=null`** — that pair is the
   only evidence that `update_internals()` is the synchronous lever.
4. **Pin the encoding bytes verbatim** (`stride=12`, the tombstone records) — they are the
   contract an author round-tripping `tile_map_data` depends on.
5. **Pin the refusal returns** (`add_null=-1`, `bad_src_readback=42`, `after_used=n1[0,0]`)
   — they are the poison/repair contract.
6. **Do not pin** `coords_for_untracked_body` / `has_body_rid` / `kinematic_*` as *positive*
   evidence — they are a measured negative (§4.8); they are pinned here only as the negative.
7. **No envelope is needed** — 13/13 cells are single-valued across 3–6 reps and under load.

### 6.3 Falsification of the rows themselves (forge test)

`python3 forge_rows.py` mutates every `key=value` token of every row (value-flip mutants)
and appends four plausible never-emitted conjuncts per row, then classifies each mutant with
the production `classify_process`:

```
TOTAL mutants=368 rejected=368 accepted=0
```

Every row is discriminating; no row is vacuous, and the appended-conjunct forge
(`forged=1`, `empty_source=-2`, `disabled_f1=hit`, `regions_f1=0`) is rejected on all 13 rows
— i.e. the classifier cannot be satisfied by a signature the engine did not emit.

---

## 7. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | `set_cell` makes the cell collidable in the same frame | **REFUTED [A]** — `set_same_frame_physics=null`, `set_f1=hit` |
| F2 | `erase_cell` removes collision in the same frame | **REFUTED [A]** — `erase_same_frame=hit`, `erase_f1=null` |
| F3 | a layer transform is live in the same frame | **REFUTED [A]** — `move_same_frame=hit`, `move_f1=null` |
| F4 | `collision_enabled=false` takes effect immediately | **REFUTED [A]** — `disabled_same_frame=hit`, `disabled_f1=null` |
| F5 | `notify_runtime_tile_data_update()` forces a synchronous physics apply | **REFUTED [A]** — `notify_same_frame=null`, `notify_f1=hit` |
| F6 | `update_internals()` is equivalent to `notify_runtime_tile_data_update()` | **REFUTED [A]** — `update_set_same_frame=hit` vs `notify_same_frame=null` |
| F7 | the deferral is a wall-clock duration (so tps-dependent) | **REFUTED [A]** — 120 tps receipts byte-identical to 60 tps |
| F8 | `set_cell` validates the source id / atlas coords | **REFUTED [A]** — source 42 and atlas (9,9) stored verbatim and listed in `get_used_cells` |
| F9 | an invalid cell self-heals or is skipped by reads | **REFUTED [A]** — it is listed by `get_used_cells`/`get_used_cells_by_id`; only `fix_invalid_tiles()` removes it |
| F10 | `clear()` truncates `tile_map_data` | **REFUTED [A]** — tombstones in place, `tomb_clear_len=14` |
| F11 | `erase_cell` removes the encoded record | **REFUTED [A]** — `tomb_erase_bytes` is all-`0xFFFF` at unchanged length |
| F12 | `get_tile_map_data_as_array()` returns structured rows | **REFUTED [A]** — it is the byte array widened to ints (`two_arr_equals_bytes=1`) |
| F13 | a malformed data array is ignored, preserving prior contents | **REFUTED [A]** — format refusal empties the layer (`short_arr_len=0`); a truncated buffer keeps only whole records |
| F14 | custom data writes are type-coerced or refused on mismatch | **REFUTED [A]** — `hp` declared `TYPE_INT` stores `"not-an-int"` verbatim |
| F15 | custom-data defaults are null/absent for a registered layer | **REFUTED [A]** — `default_hp=0`, `default_tag=`, `has_hp=1` |
| F16 | `set_cells_terrain_connect` places every requested cell | **REFUTED [A]** — only terrain-carrying tiles are placed (`n2` for 3 requested), silently |
| F17 | an out-of-range terrain index is silently ignored like a missing tile | **REFUTED [A]** — it refuses loudly with a line-numbered ERROR and places 0 cells |
| F18 | `get_neighbor_cell` returns a neighbour for every enum value | **REFUTED [A]** — 8 of 16 refuse and return the *input* cell |
| F19 | `is_cell_flipped_h` on an empty cell is false | **REFUTED [A]** — `empty_flip_h=1 empty_flip_v=1 empty_transpose=1` |
| F20 | `physics_quadrant_size` changes collision availability | **REFUTED [A]** — all four spread cells hit under size 16 and size 2 |
| F21 | a TileMapLayer with a null TileSet is inert | **REFUTED [A]** — `set_cell`+`get_cell_tile_data` ⇒ SIGSEGV rc=134 ×3 |
| F22 | `has_body_rid`/`get_coords_for_body_rid` track a script-created body | **REFUTED [A]** — never true, incl. kinematic mode and a falling RigidBody2D |
| F23 | a cell with a navigation polygon registers its region immediately | **REFUTED [A]** — `regions_same_frame=0`, `regions_f1=1` |
| F24 | `navigation_enabled=false` removes the region in the same frame | **REFUTED [A]** — `regions_disabled_same_frame=1`, `regions_disabled_f1=0` |
| F25 | `TileSet.get_next_source_id()` is `max(id)+1` | **REFUTED [A]** — stays 1 after an explicit id 5 |

---

## 8. Remaining unknowns / not measured

- **`TileData` virtual runtime hooks** (`_use_tile_data_runtime_update`,
  `_tile_data_runtime_update`, `_update_cells`): they are `TileMapLayer` virtuals requiring a
  script attached to the layer node, which a single-file `SceneTree` probe cannot provide.
  `notify_runtime_tile_data_update()` and `update_internals()` were measured; the hook
  dispatch itself was not.
- **Animated tiles** (`set_tile_animation_frames_count`, `animation_columns`,
  `animation_mode`, `animation_speed`, `animation_total_duration`) and **random-tile
  probability** were not exercised.
- **`TileSet` tile proxies** (`set_coords_level_tile_proxy`, `set_alternative_level_tile_proxy`,
  `set_source_level_tile_proxy`, `map_tile_proxy`, `cleanup_invalid_tile_proxies`) and
  **`TileSetScenesCollectionSource`** (`create_scene_tile`, scene-tile instantiation) were
  enumerated in the census but not measured.
- **Isometric / hex / half-offset TileSets**: the 8-of-16 neighbour law (§4.6) is measured
  for `TILE_SHAPE_SQUARE` only; the other three shapes' valid sets are unmeasured.
- **`y_sort_origin`, `x_draw_order_reversed`, `z_index`, `texture_origin`, `modulate`,
  `material`, occlusion layers/polygons, `collision_visibility_mode`,
  `navigation_visibility_mode`**: properties enumerated and read (defaults pinned) but their
  rendering/occlusion behaviour was not exercised (no display server).
- **`TileMapLayer.enabled=false`** was read back but its effect on collision/navigation in
  the tree was not isolated from `collision_enabled`/`navigation_enabled`.
- **`get_used_cells_by_id` with an `alternative` filter**, and `get_surrounding_cells` on
  non-square shapes.
- **`TileSetAtlasSource` texture-region changes at runtime** (`set_texture_region_size`,
  `set_margins`, `set_separation`, `move_tile_in_atlas`, `clear_tiles_outside_texture`,
  `get_tiles_to_be_removed_on_change`) — only the creation path was measured.
- **The `duplicate(true)` semantics of `TileData`** (§3.4) were measured for one tile/one
  layer; whether a wrong-typed write is ever propagated by a duplicate is **[I]** and unproven.
- **Threaded/physics-server variants**: all cells are default GodotPhysics2D, 60 tps (+ one
  120 tps split on 3 arms); a Jolt/Dummy variant (r86's nested-boot pattern) was not run.
- **`get_coords_for_body_rid` on a *tilemap-created* kinematic body** (i.e. whether any
  script-reachable path ever sets `has_body_rid=true`) — the negative in §4.8 is bounded to
  `CharacterBody2D`/`RigidBody2D` created from script on this build.
- **Portability**: every value is this host/build/`--headless`/GodotPhysics2D.

---

## 9. Host cleanup

- **73 rc-captured runs** (51 canonical + 13 loadtest + 9 tps-120) **plus ad-hoc discovery
  launches** (56 retained discovery sidecars under `runs/`; 83 `.out` receipts in total under
  `runs/`, since several early discovery stdout streams were piped rather than retained), all
  `--headless`, all `timeout -s KILL`-bounded (30 s bound; the three `nullts` hazard runs
  exited at rc=134 on their own), no run left running.
- The loadtest `yes` hogs were started with an internal `timeout 90` and cleared; `pgrep -c -x
  yes` after the block shows only other lanes' hogs (this host was at load **118.85** with
  concurrent g3d/2d lanes throughout).
- No tracked file written: `git status --porcelain` shows only the concurrent lane's
  pre-existing `corpus/fixtures/run_battery.py` modification and untracked `corpus/live/*`.
- `manifest.sha256` (295 lines) covers every artefact under `corpus/live/r92-scout/`.

---

## 10. Evidence index

All under `corpus/live/r92-scout/`; `manifest.sha256` (295 lines) covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| **frozen primary probe, 13 arms + 1 hazard arm** | `probes/tilemap_lattice.gd` | `a699138945ec7c1c` |
| discovery micro-probe (23 arms) | `probes/discover.gd` | `858438b8ec8f98c1` |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| 120 tps launch project | `proj_tps120/project.godot` | `0b7c64916f8c2aee` |
| driver (13 cells, 51 runs) | `run_cells.sh` | `manifest.sha256` |
| loadtest driver | `run_loadtest.sh` | `manifest.sha256` |
| analyzer → json | `analyze_r92.py` → `runs/analyze_r92.json` | `manifest.sha256` / `879b32348f060f3a` |
| author rows + verifier + forge | `author-rows.py.txt`, `verify_rows.py`, `forge_rows.py` | `59e06c6f05b7694a` / … |
| per-cell receipts (51 × 3 files) | `runs/r92_tm_*.{out,err,rc}` | `manifest.sha256` |
| loadtest receipts (13 runs, load 118.85) | `runs/loadtest/` | `manifest.sha256` |
| 120 tps receipts (9 runs) | `runs/tps120/` | `manifest.sha256` |
| hazard receipts (nullts ×3 + isolation) | `runs/hazard-nullts.r*.{out,err}`, `runs/disc4-*.{out,err}` | `manifest.sha256` |
| discovery receipts | `runs/disc-*.{out,err}`, `runs/disc2-*.{out,err}`, `runs/disc3-kin.err` | `manifest.sha256` |
| run inventory + verification transcripts | `RECEIPTS.md` | `9dcfb71ddf9b00f4` |
