# game-dev-2d round 91 — scout (r91-scout): the Navigation2D authorability lattice, pre-measured; 9 rows verbatim-ready

Seat `SCOUT` (LEAF) | lane `r91-scout` | round 91 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps default, GodotPhysics2D. Repo `~/Projects/shokunin/game-dev-2d-shokunin`,
HEAD at session start **`0628932`** (*r88 verifier*); no probe-relevant tracked file changed
during the session (the two modified tracked files, `corpus/fixtures/run_battery.py` and
`corpus/fixtures/r88_surfaces.gd`, are the **concurrent r88-fold lane's** edits — their
diff adds `input_lattice_phys_peer` envelope payloads and `r88_surfaces.gd` changes, none
of it this seat's). The launch `project.godot` is the byte-copy of
`corpus/fixtures/project.godot` (`8de8b3af…`).

**No git mutation, no tracked file written, no subagent, no commit.** Writes are this
report and `corpus/live/r91-scout/**` only. `git status --porcelain` shows no tracked
modification attributable to this seat.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server
installed; `definition`/`references`/`hover` were **unavailable for every file touched**.
Semantic carriers: fresh-process execution receipts, `ClassDB`/runtime introspection inside
the probes, and engine-emitted error text. Every `file:line` below is engine-emitted `at:`
backtrace text, never a source read (no engine source tree on this host).

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Primary: the Navigation2D authorability lattice** — `NavigationServer2D` map/region/link
lifecycle and **map-sync timing**, `NavigationPolygon` (hand-built and baked), exact
`map_get_path`/`query_path` geometry, `NavigationRegion2D` cost/layer/enable/transform
steering, the `NavigationAgent2D` node, **agent avoidance** (server agents + obstacle), and
**headless navmesh baking** (outline route + modern `parse_source_geometry_data` /
`bake_from_source_geometry_data` route). This is the brief's candidate (a), and the
adjacents were weighed as follows **[O]/[I]**:

- **(b) TileMapLayer** — rich, but every interesting cell (terrain autotiling, physics-layer
  readback) first needs a hand-built `TileSet` with physics polygons/terrains; the
  falsifiability is mostly data-structure readback, and the physics side duplicates the
  already-admitted `phys2d_*` batteries.
- **(c) AnimationPlayer 2D** — method tracks/call queues are timing-bound; the r87 lesson
  says such cells become envelopes, and the *positive* determinism lives in
  `playback_process_mode=PHYSICS`, which is a subset of (d).
- **(d) Tween/interpolator** — high pure-function value (`Tween.interpolate_value` is a
  static, measured exact: `linear@0.25=2.5`, `quad/EASE_IN_OUT@0.25=1.25`,
  `expo/EASE_OUT@0.5=9.69718754291534` **[M]**, `runs/disc-tweenval.out`), but its timing
  half is the same physics-vs-idle pulse territory r87 already armed.
- **(e) Audio bus routing** — r88 §3.15 already measured the headless Dummy driver as
  **headless-null** (`playing=false`, peaks −200 dB); routing readbacks are shallow.
- **(f) OS/Engine meta** — cheap but broad; no single contract to pin.

Navigation2D wins on **coverage gain** (zero nav rows exist anywhere in the 207-row
battery; `grep -rin "navigation\|nav2d" corpus/fixtures/*.gd` finds only unrelated
`NavigationMesh`-free code) and on **falsifiability**: the subsystem is a server with an
explicit synchronization contract, and the scout's first four probes refuted the naive
"create → query" model on the spot (§4.1). The census did not rank it (it is a new
adjacent, not one of the r88 families), so this round also settles whether nav is
headless-authorable at all — **it is**, with a documented sync gate.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (20 arms, fresh process) | feasibility: API census, sync ladder, bake routes, avoidance teardown matrix, polygon-connection control | `runs/disc-*.{out,err}` |
| 2 | `bash run_cells.sh` | **9 cells** (3 pure ×3, 6 sync/await ×6) = **45 runs** | `runs/r91_*.{out,err,rc}` |
| 3 | `python3 analyze_r91.py` | per-cell reps / out-uniq / err-uniq / rc vectors | `runs/analyze_r91.json` |
| 4 | loadtest (deliberate `yes` hogs, load avg 20–25) | 31 runs over all 9 arms | `runs/loadtest/` |
| 5 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 9 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |

**Canonical cell set: 45 runs across 9 cells** — `nav_census`/`nav_path`/`nav_query` ×3
(pure/readback), `nav_sync`/`nav_region`/`nav_agent`/`nav_avoid`/`nav_bake`/`nav_link` ×6
(every physics-await/lifecycle cell). All rc=0; no cell crashed; no run left running.

**Byte-stability: 8 of 9 cells are `out_uniq=1 err_uniq=1` with a constant rc vector**
(`runs/analyze_r91.json`: `UNSTABLE=['nav_avoid']`). **`nav_avoid` is a true mode cell**:
its RVO numeric payload differs per process (6/6 distinct), while every structural field
is stable (§3.7). stderr: 7 of 9 cells are **0 B**; `nav_sync` carries exactly one
deterministic ERROR (511 B, the pre-sync refusal) and `nav_bake` one WARNING + one ERROR
(712 B, deprecation notice + orphan-node refusal).

**Arm-dispatch integrity [O]:** every arm prints its own name on its `PASS` line
(`PASS nav_lattice <arm> …`), so a silent `_:` fallback (the r88 dead-seat failure) is
impossible to miss; `arm` is parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan).

**Sync gate [M]:** the initial map synchronization is a *mode* (typical 4–6 frames,
observed up to >10 in one rep), so the probe polls
`map_get_iteration_id(map) >= 2 and reach(map,from,to)` (bounded 24 frames) before any
payload; the frames-waited counter (`settle=`) is a load-sensitive tail field and is
**excluded from the recommended row signatures** (§6).

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **Class/enum/default census** (server, polygon, region, agent, query params) | **PINNABLE** | 3 | uniq=1 |
| **Map sync ladder + pre-sync refusal** | **PINNABLE law** (ladder is a mode) | 6 | uniq=1 (settle counter load-variable) |
| **Exact path geometry** (funnel vs raw, clamping, gaps, edge-connection margin) | **PINNABLE** | 3 | uniq=1 |
| **`query_path` lattice** (postproc, metadata flags, truncation, layers) | **PINNABLE** | 3 | uniq=1 |
| **Region steering** (travel/enter cost, layers, enable, live polygon swap) | **PINNABLE** — all four levers measured | 6 | uniq=1 |
| **`NavigationAgent2D` node path following** | **PINNABLE** | 6 | uniq=1 |
| **Agent avoidance** (server agents, callback safe velocity) | **PINNABLE structurally; numeric payload is a MODE** (closing-speed invariant) | 6 | uniq=6 (digits only) |
| **Headless navmesh baking** (outline route + modern route) | **PINNABLE** — both routes, incl. hole/obstruction detours | 6 | uniq=1 |
| **Links** (off-mesh traversal, bidirectional default, enable, layers) | **PINNABLE** | 6 | uniq=1 |
| **Teardown discipline** (avoidance callback crash class) | **PINNABLE hazard** (rc=134 vector, not a row) | discovery | deterministic |

---

## 3. Measured values, verbatim

All payloads are `runs/r91_nav_<cell>.rep1.out` unless noted; `%.4f` coordinates; paths are
`[(x,y),…]`.

### 3.1 Census (`nav_census`) — [M]

```
PASS nav_lattice census srv_methods=199 poly_methods=134 srv_info=[0,1,2,3,9,4,5,7,6,8] pgt=[0,1,2,3] sgm=[0,1,2,3] sp=[0,1,2] pp=[2,0,1] md=[0,2,1,4,7] alg=0 poly_defaults=agent_r=10.0000,cell=1.0000,border=0.0000,pgt=2,sgm=0,sp=0,cmask=4294967295,brect=[P: (0.0, 0.0), S: (0.0, 0.0)],boff=(0.0, 0.0),polys=0 reg_defaults=cost=1.0000,enter=0.0000,en=true,edge=true agent_defaults=r=10.0000,path_d=20.0000,tgt_d=10.0000,maxspeed=100.0000,nd=500.0000,mn=10,tha=1.0000,tho=0.0000,avoid=false,prio=1.0000,layers=1,pp=0,simpl=false,eps=0.0000 qp_defaults=pp=0,md=7,layers=1,maxlen=0.0000,maxrad=0.0000,maxdist=0.0000,maxpolys=4096,simpl=false,eps=0.0000
```

- **`PATH_POSTPROCESSING_NONE = 2`**, `CORRIDORFUNNEL = 0`, `EDGECENTERED = 1` — the enum
  order is not the "none first" order an author would guess **[M]**.
- Metadata flags: `NONE=0, TYPES=1, RIDS=2, OWNERS=4, ALL=7` **[M]**.
- `query_path` defaults are **not** neutral: `pp=0` (CORRIDORFUNNEL), `md=7` (ALL),
  `maxpolys=4096` **[M]**; `path_return_max_length/radius/search_max_distance=0`
  (unlimited).
- Map defaults (read post-sync, §3.3): `cell_size=1.0`, `edge_connection_margin=1.0`,
  `link_connection_radius=4.0`, `merge_rasterizer_cell_scale=0.1`,
  `use_edge_connections=true`, **`use_async_iterations=true`** **[M]**.
- Region defaults: `travel_cost=1.0`, `enter_cost=0.0`, `enabled=true`,
  `use_edge_connections=true`. Agent defaults: `radius=10`, `path_desired=20`,
  `target_desired=10`, `max_speed=100`, `neighbor_distance=500`, `max_neighbors=10`,
  `time_horizon_agents=1.0`, `time_horizon_obstacles=0.0`, `avoidance=false`,
  `priority=1.0`, `layers=1`, `postprocessing=0`, `simplify=false` **[M]**.
- NavigationPolygon defaults: `agent_radius=10`, `cell_size=1`, `border_size=0`,
  `parsed_geometry_type=2` (BOTH), `source_geometry_mode=0` (ROOT_NODE_CHILDREN),
  `sample_partition_type=0` (CONVEX_PARTITION), `parsed_collision_mask=0xFFFFFFFF`,
  `baking_rect` empty **[M]**.

### 3.2 Path geometry (`nav_path`) — [M]

L-map = two regions (vertical bar x0..40 y0..200, horizontal bar x40..200 y0..40); a third
region at x210..310 (10 px gap at y0..40).

```
PASS nav_lattice path diag=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)] diag_raw=[(20.0000,180.0000),(40.0000,20.0000),(180.0000,20.0000)] same=[(20.0000,20.0000),(20.0000,20.0000)] out_start=[(0.0000,0.0000),(40.0000,8.8889),(90.0000,20.0000)] out_target=[(20.0000,20.0000),(40.0000,22.2222),(200.0000,40.0000)] gap=[(20.0000,20.0000),(40.0000,20.0000),(200.0000,20.0000)] closest_in=(20.0000,20.0000) closest_out=(0.0000,0.0000) owner_in_is_rv=true owner_out_is_rv=true settle=5 iter=2
gap_margin20=[(20.0000,20.0000),(40.0000,20.0000),(205.0000,20.0000),(250.0000,20.0000)] reach=true margin=20.0000
```

- **`optimize=true` (funnel) cuts the inner corner**: `(40,40)`; `optimize=false` keeps the
  polygon-edge waypoint `(40,20)` **[M]**.
- `start==target` returns a **2-point degenerate path** at the point **[M]**.
- A start outside the navmesh is **clamped to the closest point** (`(0,0)`) and the path is
  built from there; an outside target clamps to `(200,40)` **[M]**.
- The 10 px gap is **not** bridged at margin 1.0 (`gap` ends at the near edge `(200,20)`);
  raising `edge_connection_margin` to 20 **does** bridge it and inserts the connection
  midpoint `(205,20)` as a waypoint — `reach=true` **[M]**. This is the first
  edge-connection-margin measurement in the battery.
- `map_get_closest_point_owner` is the region that owns the closest polygon; compare as a
  **boolean against the region RID**, not as a raw RID (RIDs are allocation-order-dependent).
- **`map_get_random_point()` is random per call** (`rand1=(18.9645,1.8745)`,
  `rand2=(24.1719,139.86)` same process) — **never pin it** (§5).

### 3.3 Sync ladder + refusal (`nav_sync`) — [M], the core law

```
PASS nav_lattice sync pre_iter=0 pre_regions=0 pre_path=[] pre_closest=(0.0000,0.0000) cellsize=1.0000 edgemargin=1.0000 linkradius=4.0000 merge_scale=0.1000 useedge=true async=true active_after=true chg_same=false chg_iter_same=2 chg_settled=true chg_iter_settled=3 dis_same=true dis_settled=false ladder=[f0:0/0/0,f1:0/0/0,f2:1/1/0,f3:1/1/0,f4:2/1/1,f5:2/1/1,f6:2/1/1,f7:2/1/1,f8:2/1/1,f9:2/1/1] first_reach=4 first_reach_sync=1
```

stderr (511 B, exactly one ERROR):
```
ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.
	NavigationServer 'map_changed' signal can be used to receive update notifications.
	NavigationServer 'map_get_iteration_id()' can be used to check if a map has finished its newest iteration.
   at: get_closest_point (modules/navigation_2d/nav_map_2d.cpp:165)
```

- **Before the first synchronization the map is not queryable** — and the two entry points
  fail differently: `map_get_closest_point` emits the loud ERROR above and returns `(0,0)`,
  while `map_get_path` silently returns `[]` **[M]**. `pre_iter=0 pre_regions=0` (the region
  RID has not even landed yet) **[M]**.
- **Map getters read queued-but-unapplied values pre-sync**: `cellsize=0.0 edgemargin=0.0
  useedge=false async=false` if read before the first sync; after it they read
  `1.0/1.0/true/true` **[M]**. (`map_is_active` likewise reads `false` pre-sync and `true`
  after — it is not a configuration readback.) This is an author trap: read map config
  **after** `map_get_iteration_id >= 1`.
- **Ladder** (`f<frame>:<map_iter>/<region_iter>/<reach>`): the region lands at f1, the map
  iteration bumps at f2, region geometry (bounds) lands f3, and the path is live at f4 —
  this ladder is the **default async-iterations mode**, and under concurrent-lane load the
  same ladder was observed shifted by 1–2 frames (`first_reach ∈ {4,5}`, `settle ∈ {4..7}`;
  §1/§6). With `use_async_iterations=false` the first reachable frame is **f1** **[M]**.
- **Live changes are not synchronous** [M]: after `region_set_transform` **+**
  `map_force_update`, the new geometry is *not* reachable in the same frame
  (`chg_same=false`); after 4 frames it is (`chg_settled=true`) and the map iteration has
  bumped (`chg_iter_settled=3`). Disabling the region behaves the same way: the old path is
  still served in the same frame (`dis_same=true`) and disappears only after the change
  settles (`dis_settled=false`). **`map_force_update` is not a synchronous apply** — a
  same-frame readback after a write is stale.

### 3.4 `query_path` lattice (`nav_query`) — [M]

```
PASS nav_lattice query postproc=[pp2=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)],pp0=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)],pp1=[(20.0000,180.0000),(40.0000,20.0000),(180.0000,20.0000)]] metadata=[md0:[]|n0|n0,md2:[]|n3|n0,md1:[0,0,0]|n0|n0,md4:[]|n0|n3,md7:[0,0,0]|n3|n3] maxlen=[(20.0000,180.0000),(24.2426,150.3015)] maxrad=[(20.0000,180.0000),(20.0814,179.4301)] maxdist=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)] maxpolys=[(20.0000,180.0000),(40.0000,20.0000)] simplify=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)] layers0=[] length=282.8427 settle=5 iter=2
```

- **Postprocessing is discriminating**: `EDGECENTERED (1)` returns the edge-center waypoint
  `(40,20)` while `CORRIDORFUNNEL (0)` and `NONE (2)` return the corner-cut `(40,40)` **[M]**.
- Metadata: `md2` (RIDS) fills `path_rids` (`n3`) but not `path_owner_ids`; `md4` (OWNERS)
  the reverse; `md1` (TYPES) fills `path_types=[0,0,0]`; `md7` (ALL) all three; `md0` none
  **[M]**.
- Truncation levers: `path_return_max_length=30` cuts the path mid-segment
  (`(24.2426,150.3015)`); `path_return_max_radius=60` returns a tiny start-anchored stub;
  `path_search_max_polygons=1` truncates to the first edge (`(40,20)`); `simplify_path=true`
  with `epsilon=5` is **inert on this 3-point path**; `path_search_max_distance=40` is
  **inert** (the full 282.8-length path is still returned) **[M]**.
- `navigation_layers=0` ⇒ `[]` (no region matches) **[M]**.
- `length=282.8427` = the funnel path length (2 × 141.4214) **[M]**.

### 3.5 Region steering (`nav_region`) — [M]

```
PASS nav_lattice region base=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] top_cost1=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] bot_cost1=[(10.0000,50.0000),(20.0000,40.0000),(80.0000,40.0000),(90.0000,50.0000)] enter500=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] l1=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] l2=[(20.0000,40.0000),(80.0000,40.0000)] l3=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] dis_same=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] dis_settled=[(10.0000,50.0000),(20.0000,40.0000),(80.0000,40.0000),(90.0000,50.0000)] reenabled=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] swapped=[(10.0000,50.0000),(20.0000,40.0000),(80.0000,40.0000),(90.0000,50.0000)] restored=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] counts=regs=4,cost_a=1.0,cost_b=1.0,en_a=true,en_b=true settle=5 iter=11
```

Four independent steering levers, all measured on the same two-corridor map
(C junction → A top / B bottom → D junction):
- **travel cost** flips the route: A=1/B=10 ⇒ top (`…(80,60)…`); A=10/B=1 ⇒ bottom
  (`…(80,40)…`) **[M]**;
- **enter cost** alone flips it back: A enter 500 (costs equal) ⇒ top **[M]**;
- **navigation layers** filter per-region: A=1,B=2 with query layer 1 ⇒ top; query layer 2
  ⇒ a **partial path inside B only** (`[(20,40),(80,40)]`, because C/D are layer 1); layer 3
  ⇒ top **[M]**;
- **disable + live polygon swap** steer after settling: disabling A ⇒ bottom after settle
  (still top in the same frame), swapping A's polygon to an unreachable sliver ⇒ bottom,
  restoring ⇒ top **[M]**.

### 3.6 `NavigationAgent2D` node (`nav_agent`) — [M]

```
PASS nav_lattice agent settled=(180.0000,180.0000)/false/true/false/226.27/226.27/1 walk_steps=28 reached_at=-1 fin=true reached=true reachable=true dist=2.2741 final_pos=(178.3920,178.3920) final_target=(180.0000,180.0000) path=[(20.0000,20.0000),(180.0000,180.0000)] desired=4.0 target_desired=8.0 first_reachable=4
```

- **`NavigationAgent2D extends Node`**, not `Node2D` — `position` is an invalid assignment
  and aborts the arm (r88 §7.2 hang class); the agent rides a parent `Node2D` **[M]**.
- Before sync: `get_next_path_position()=(0,0)`, `path_length=0`, `reachable=false`;
  after: target + `226.27` (straight-line distance) and `reachable=true` **[M]**. The
  reachable flip is a mode (`first_reachable ∈ {4,5,6,7}` across reps/load).
- `distance_to_target()` is the **straight-line** distance (226.27), not the path length
  (identical here only because the path is straight) **[M]**.
- Walking the parent along `get_next_path_position()` at 8 px/step takes **28 steps** to
  finish; the final state is `fin=true reached=true reachable=true dist=2.2741`, parent at
  `(178.3920,178.3920)`, `final_position=(180,180)`, current path = the straight 2-point
  line **[M]**.
- `reached_at=-1` is a measured **1-frame split**: `is_navigation_finished()` became true
  in the same frame that `is_target_reached()` was still false, and `reached` was true at
  the next readback **[M]** (a pin must not assume the two flip together).

### 3.7 Avoidance (`nav_avoid`) — [M], a mode cell with a stable invariant

Structural fields are identical across 6 reps; the numeric tail is process-dependent
(6/6 distinct payloads):

```
PASS nav_lattice avoid pa=(150.0000,150.0000) pb=(190.0000,150.0000) warm_n_a=16 seq_a=[10.502,…,10.737] seq_b=[-9.381,…,-9.144] n_a=21 n_b=21 vel_a=(10.7373,0.0000) vel_b=(-9.1436,0.0000) has_cb_a=true radius_a=10.0 maxspeed_a=50.0 obs_pos=(170.0000,150.0000) obs_en=false settle=5
PASS nav_lattice avoid … seq_a=[12.607,…,12.798] seq_b=[-7.256,…,-7.086] … vel_a=(12.7981,0.0000) vel_b=(-7.0865,0.0000) …
PASS nav_lattice avoid … seq_a=[13.222,…,13.517] seq_b=[-6.632,…,-6.483] … vel_a=(13.5174,0.0000) vel_b=(-6.4826,0.0000) …
PASS nav_lattice avoid … seq_a=[13.552,…,13.855] seq_b=[-6.298,…,-5.992] … vel_a=(13.8547,0.0000) vel_b=(-5.9917,0.0000) …
PASS nav_lattice avoid … seq_a=[13.812,…,14.119] seq_b=[-6.037,…,-5.724] … vel_a=(14.1193,0.0000) vel_b=(-5.7241,0.0000) …
PASS nav_lattice avoid … seq_a=[14.310,…,14.519] seq_b=[-5.541,…,-5.322] … vel_a=(14.5194,0.0000) vel_b=(-5.3221,0.0000) …
```

| rep | a₀ | b₀ | \|a₀\|+\|b₀\| |
|---|---|---|---|
| 1 | 14.310 | −5.541 | **19.851** |
| 2 | 10.502 | −9.381 | **19.883** |
| 3 | 12.607 | −7.256 | **19.863** |
| 4 | 13.222 | −6.632 | **19.854** |
| 5 | 13.812 | −6.037 | **19.849** |
| 6 | 13.552 | −6.298 | **19.850** |

- **Law [M]: the avoidance callback fires once per agent per frame (n_a=n_b=21 after a
  16-frame warmup + 5 measured frames) and enforces a safe closing speed ≈ 20 px/s** for
  two agents at 40 px separation with desired closing 100 px/s (radius 10, max_speed 50,
  horizon 1.0) — `|safe_a|+|safe_b| ∈ [19.849,19.883]` — while the **split between the two
  agents is process-dependent** (10.5/9.4 … 14.5/5.3). The last callback value is also
  written back into `agent_get_velocity` **[M]**.
- The obstacle (radius 12 at the midpoint, `avoidance_enabled=false`) is a readback control;
  obstacle avoidance itself was **not** engaged.
- Pre-sync history is not the variance source: creating the agents **after** the map sync
  and warming 16 frames to a steady state still leaves the split process-dependent
  (measured; the mechanism is unexplained — §8).

### 3.8 Headless baking (`nav_bake`) — [M]

```
PASS nav_lattice bake outline_polys=4 outline_verts=8 hole_across=[(100.0000,20.0000),(140.0000,60.0000),(140.0000,140.0000),(100.0000,180.0000)] hole_straight=[(20.0000,100.0000),(60.0000,60.0000),(140.0000,60.0000),(180.0000,100.0000)] parse_obs=1 parse_trav=0 parse_has=false baked_polys=4 baked_verts=8 collider_only_polys=0 iter_b=2 through=[(-100.0000,0.0000),(-55.0000,55.0000),(55.0000,55.0000),(100.0000,-0.0000)] around=[(-100.0000,-100.0000),(-55.0000,55.0000),(100.0000,100.0000)] outside=[(-145.0000,-145.0000),(-55.0000,55.0000),(100.0000,100.0000)] settle_a=3 settle_b=1
```

stderr (712 B): the deprecation WARNING for `make_polygons_from_outlines()` plus exactly
one ERROR:
```
ERROR: The root node needs to be inside the SceneTree.
   at: parse_source_geometry_data (modules/navigation_2d/2d/godot_navigation_server_2d.cpp:115)
```

- **Outline route works headless**: a 200×200 outline + a 60..140 hole outline →
  `make_polygons_from_outlines()` → **4 polygons / 8 vertices**, and the server region
  serves **hole-detouring paths** (`hole_across` goes around the hole's right side via
  `(140,60)/(140,140)`) **[M]**. (Deprecated WARNING — tolerated by the battery classifier;
  budget it or expect it.)
- **Modern route works with an explicit traversable outline**: parse a `StaticBody2D` +
  `RectangleShape2D(100×100)` under the region node (→ `parse_obs=1`, `parse_trav=0`,
  `parse_has=false`) then `sgd.add_traversable_outline(±150)` and bake with
  `baking_rect=(-150,-150,300,300)`, `agent_radius=5` → **4 polygons / 8 vertices**; paths
  route around the 100×100 obstruction via `y=55` (`through`/`around`), and an outside
  start clamps to the eroded border `(-145,-145)` **[M]**. The `agent_radius=5` erosion is
  visible in the coordinates (150→145 outer, 50→55 inner) **[M]**.
- **Collider-only source geometry bakes to an empty navmesh silently**:
  `collider_only_polys=0` with `baking_rect` set and no traversable outline — no error, no
  navmesh, `map_get_path=[]` **[M]**. (The bake needs at least one traversable outline;
  collision shapes are parsed as *obstructions* only.)
- **Baking requires the tree**: calling `bake_navigation_polygon()` on a region node that
  is not inside the tree (including a node added during `_initialize`, before the first
  frame) emits the deterministic ERROR above **[M]**.
- The modern-route bake output must be **fed to a region after baking** — a region node
  that already holds the polygon does not re-register in place (measured in discovery:
  paths stayed empty; reassignment to a server region served them) **[M]**.

### 3.9 Links (`nav_link`) — [M]

```
PASS nav_lattice link bidir_default=true en_default=true fwd_default=[(10.0000,50.0000),(100.0000,50.0000),(400.0000,50.0000),(490.0000,50.0000)] rev_default=[(490.0000,50.0000),(400.0000,50.0000),(100.0000,50.0000),(10.0000,50.0000)] rev_bidir=[(490.0000,50.0000),(400.0000,50.0000),(100.0000,50.0000),(10.0000,50.0000)] fwd_disabled_same=[(10.0000,50.0000),(100.0000,50.0000),(400.0000,50.0000),(490.0000,50.0000)] fwd_disabled_settled=[(10.0000,50.0000),(100.0000,50.0000)] cost300=[(10.0000,50.0000),(100.0000,50.0000),(400.0000,50.0000),(490.0000,50.0000)] layer1=[(10.0000,50.0000),(100.0000,50.0000)] layer2=[] start=(100.0000,50.0000) end=(400.0000,50.0000) bidir=false en=true cost=1.0 enter=0.0 layers=2 settle=5 iter=5 link_iter=4
```

- **A created link is bidirectional by default** (`bidir_default=true`, `en_default=true`) —
  the reverse path traverses it with no configuration **[M]**. (The final `bidir=false` is
  the probe's own reset.)
- The link's start/end become **path waypoints** (`(100,50)`→`(400,50)`) **[M]**.
- `link_set_enabled(false)` is **not live in the same frame** (`fwd_disabled_same` still
  traverses) and removes the link after settle (`fwd_disabled_settled` stops at the link
  start) **[M]**.
- `link_set_navigation_layers(2)` with query layer 1 excludes the link (path stops at
  `(100,50)`); query layer 2 returns `[]` (regions are layer 1) **[M]**.
- `travel_cost=300` **does not** prevent traversal when no alternative route exists (the
  target is unreachable without the link, so any finite link cost wins) — a
  non-discriminating control, kept as measured **[M]**.

---

## 4. Laws

### 4.1 The sync law [M]
The map is a *server-side* structure with a synchronization step: a freshly created
map+region is **not queryable**; `map_get_closest_point` refuses loudly
(`nav_map_2d.cpp:165`) and `map_get_path` returns `[]`. The region RID lands on frame 1,
the map iteration id bumps on frame 2, region geometry on frame 3, and paths are live from
frame 4 (default `use_async_iterations=true`); with `use_async_iterations=false` the first
reachable frame is **f1**. **Author rule: gate every nav readback on
`map_get_iteration_id(map)` and on a reachability probe — never on a frame count.**

### 4.2 The change-application law [M]
Live region changes (transform, enable, polygon, cost, layers) and link changes are applied
**2–4 physics frames later**; `map_force_update` does **not** make them synchronous
(same-frame reads after a write are stale — measured for transform and disable). The
`chg_iter_same/chg_iter_settled` pair pins this: the same-frame read is the *old* answer,
the settled read is the new one.

### 4.3 The polygon-connection law [M]
Two hand-built polygons inside **one** `NavigationPolygon` that share an edge do **not**
connect (path stops at the shared edge); the same L built as **two regions** connects and
funnels. Baked polygon lists (both routes) *do* connect across their polygon edges.
**Author rule: build multi-part navmeshes as multiple regions (or bake); do not hand-author
polygon lists expecting edge merging.**

### 4.4 The bake law [M]
Headless baking works on this host, but: (a) the region node must be inside the tree
(otherwise a deterministic refusal ERROR); (b) collider-only source geometry bakes to an
**empty** navmesh silently — at least one traversable outline is required; (c) the bake
erodes by `agent_radius` and clips to `baking_rect`; (d) feed the baked polygon to the
region **after** baking.

### 4.5 The avoidance law [M]
Avoidance is a server-side RVO step driven per physics frame; the callback receives the
safe velocity each frame, and the server writes it back into `agent_get_velocity`. With
two agents closing at 100 px/s at radius 10/max_speed 50/horizon 1.0, the safe closing
speed converges to **≈ 20 px/s** (`|a|+|b| ∈ [19.849,19.883]`) while the per-agent split is
process-dependent. **Teardown law:** a registered avoidance callback must be cleared and
≥ 1 physics frame awaited before `free_rid` — otherwise `double free or corruption`
(rc=134); agents leaked at exit crash too. This is the same crash class as r85's
`joint_make_pin` SIGSEGV: an engine-side unchecked state reachable from script.

### 4.6 The agent-frame law [M]
`is_navigation_finished()` and `is_target_reached()` do **not** flip in the same frame
(`reached_at=-1` while `fin=true`); `distance_to_target()` is straight-line, not path
length; `get_next_path_position()` is `(0,0)` before the path syncs.

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **Pre-sync reads** (§3.3): loud ERROR from `map_get_closest_point`, silent `[]` from
   `map_get_path`; map config getters read 0/false pre-sync. Gate on iteration id.
2. **`map_force_update` is not synchronous** (§4.2) — do not pin a post-write readback
   taken in the same frame.
3. **Avoidance teardown crash [M]**: `agent_set_avoidance_callback` + `free_rid` in the
   same frame ⇒ `double free or corruption` (rc=134, deterministic; also on
   leak-at-exit). Discipline: clear callbacks, await ≥ 1 frame, then free. Never author a
   cell that frees a callback-bearing agent without the delay.
4. **`NavigationAgent2D` is a Node** (§3.6): `position` assignment is invalid and aborts
   the arm (timeout/hang class).
5. **Bake without a traversable outline is silently empty** (§3.8) — a vacuous pin.
6. **Bake outside the tree refuses loudly** (§3.8) — including any call during
   `_initialize` on a node added that frame (node tree state is not live until a frame
   passes).
7. **`map_get_random_point()` is random per call** (§3.2) — not pinnable.
8. **RIDs are allocation-order-dependent**: compare `map_get_closest_point_owner` as a
   boolean against a region RID, never pin the RID text.
9. **Hand-built polygon lists do not connect** (§4.3).
10. **Counter fields (`settle=`, `iter=`, `ladder=`, `first_reach*`) are load-sensitive**
    (measured: full-line signatures fail under load avg 20–25) — exclude them from pinned
    signatures or envelope them.
11. **The outline bake route emits a deprecation WARNING** (§3.8) — tolerated by
    `classify_process` (no `ERROR:` substring) but it is real stderr; budget it if a
    future classifier tightens.
12. **The avoid numeric payload is a mode** (§3.7): pin the prefix and the closing-speed
    invariant, or envelope the six observed payloads.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (9, exec-checked)

`corpus/live/r91-scout/author-rows.py.txt` holds two 5-tuple sets and the
`expected_errors` dict; `python3 verify_rows.py` classifies every row against **every**
canonical + loadtest receipt with the production `classify_process` (AST-extracted from
`corpus/fixtures/run_battery.py`, segment sha256 `749fa060…` — the same segment r89/r90
pinned):

- **`ROWS_PREFIX` (recommended, gating): 76/76 receipts accepted, `rejected=[]`.**
  Signatures end before the async-sync counters:
  ```
  nav_lattice_census   PASS nav_lattice census …eps=0.0000
  nav_lattice_path     PASS nav_lattice path …owner_out_is_rv=true
  nav_lattice_query    PASS nav_lattice query …length=282.8427
  nav_lattice_sync     PASS nav_lattice sync …dis_same=true dis_settled=false
  nav_lattice_region   PASS nav_lattice region …en_a=true,en_b=true
  nav_lattice_agent    PASS nav_lattice agent …target_desired=8.0
  nav_lattice_avoid    PASS nav_lattice avoid pa=(150.0000,150.0000) pb=(190.0000,150.0000) warm_n_a=16
  nav_lattice_bake     PASS nav_lattice bake …outside=[(-145.0000,-145.0000),(…),(100.0000,100.0000)]
  nav_lattice_link     PASS nav_lattice link …layers=2
  ```
  (Exact strings in `author-rows.py.txt`.)
- **`ROWS` (full-line, informational): 4 loadtest rejections** for
  `nav_lattice_path` (2), `nav_lattice_query` (1), `nav_lattice_sync` (1) — the counters
  moved under load. Use these only in a quiet window or as mode envelopes.

`expected_errors` additions (keyed by case name):
```python
'nav_lattice_sync': (
    'ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.',
),
'nav_lattice_bake': (
    'ERROR: The root node needs to be inside the SceneTree.',
),
```
Every other row is `ERROR:`-clean with 0 B stderr (measured; `nav_bake`'s remaining stderr
is the deprecation WARNING only).

Probe file lands at `corpus/fixtures/nav_lattice.gd` (sha256 `efb496e5…`, self-contained
`SceneTree` script, battery `--arm=` convention). Insert the rows ahead of the
crash/descendant tail like prior blocks; no other fixture change is needed.

### 6.2 What to pin and what not to pin

1. **Pin the `PASS nav_lattice …` line (or its stable prefix)** — it carries the arm name,
   so the r88 silent-fallback failure cannot recur.
2. **Gate nav cells on the sync poll** (iteration id + reach) and pin the settled payload;
   record `settle=` only as a mode if at all.
3. **Pin the avoid prefix + the closing-speed invariant** (`|a|+|b| ∈ [19.8,19.9]`) — or
   mode-envelope the six observed payloads; never pin a single split value.
4. **Pin `chg_same=false` / `chg_settled=true` / `dis_same=true` / `dis_settled=false`** —
   that quartet *is* the change-application law.
5. **Pin the metadata/tail-readback** (`owner_in_is_rv=true`, `parse_obs=1`,
   `collider_only_polys=0`, `bidir_default=true`) — booleans are RID/alloc-safe.
6. **Do not pin** raw RIDs, `map_get_random_point`, `settle=`/`iter=` counters, or ideal
   geometry (the erosion/clamp values are the measurement).
7. **No envelope is needed for 8 of 9 cells** — they are single-valued across 3–6 reps
   (canonical run). Only `nav_avoid` is a mode cell.

---

## 7. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | a freshly created map+region is queryable immediately | **REFUTED [A]** — pre-sync ERROR from `map_get_closest_point`, `[]` from `map_get_path`; ladder f4 |
| F2 | `map_force_update` applies a live change synchronously | **REFUTED [A]** — `chg_same=false` after force_update; `dis_same=true` |
| F3 | map config getters are readable before the first sync | **REFUTED [A]** — `cellsize=0.0 edgemargin=0.0 useedge=false` pre-sync; real values after |
| F4 | `map_is_active=false` means the map is not processing | **REFUTED [A]** — reads false pre-sync, true after; paths work regardless |
| F5 | two hand-built polygons in one `NavigationPolygon` connect across a shared edge | **REFUTED [A]** — path stops at the shared edge; two regions connect (positive control) |
| F6 | `NavigationAgent2D` is a `Node2D` | **REFUTED [A]** — `position` assignment is invalid (aborts the arm) |
| F7 | avoidance safe velocities are process-stable | **REFUTED [A]** — 6/6 distinct payloads; but `|a|+|b| ≈ 19.85` is invariant |
| F8 | freeing an avoidance agent with a registered callback is safe | **REFUTED [A]** — `double free or corruption`, rc=134 ×3; clear+frame+free is clean |
| F9 | collider-only source geometry bakes a navmesh | **REFUTED [A]** — `collider_only_polys=0`, silent |
| F10 | the deprecated outline bake route is dead | **REFUTED [A]** — 4 polys / 8 verts, hole respected |
| F11 | links are one-way by default | **REFUTED [A]** — `bidir_default=true`; reverse path traverses |
| F12 | link travel cost steers away from the link when it is the only route | **REFUTED [A]** — `cost300` still traverses (no alternative) |
| F13 | baking can be called during `_initialize` on a just-added node | **REFUTED [A]** — `ERROR: The root node needs to be inside the SceneTree.` |
| F14 | a path to an unreachable target is empty | **REFUTED [A]** — a partial path to the closest reachable point is returned; `[]` only when no region is reachable |
| F15 | within-region polygon swap is live in the same frame | **REFUTED [A]** — settles after 2–4 frames |
| F16 | the sync/`settle` counters are load-stable | **REFUTED [A]** — `settle ∈ {4,5}` under load; full-line signatures fail 1/3–2/3 |

---

## 8. Remaining unknowns / not measured

- **`NavigationObstacle2D` / server obstacle avoidance**: the obstacle was present but
  `avoidance_enabled=false` (readback control); obstacle-avoidance callback payloads and
  `affect_navigation_mesh`/`carve_navigation_mesh` were **not** measured (carving needs a
  baked navmesh + the node flag).
- **`NavigationLink2D` node** (only the server link was measured); link `enter_cost`,
  link-to-link chains, `link_set_bidirectional` mid-sync edge cases.
- **Node-agent avoidance observability**: setting the server callback on a node agent's RID
  did not fire (0 hits in discovery); overriding `_avoidance_done` in GDScript is a
  **warning-as-error** parse failure on this build — the node-side avoided velocity
  observable is unresolved.
- **Avoidance determinism mechanism**: the per-agent split varies across processes even
  with identical fixed inputs, identical warmup, and agents created after sync; the closing
  speed is invariant. Whether this is a time-based seed, an internal iteration-order
  effect, or float non-associativity is **[I]** and unproven.
- **`map_get_path` partial-path semantics** (F14): the exact clamping/truncation rule when
  the target is unreachable but regions are reachable was measured on 3 layouts only.
- **tps dependence**: all cells are 60 tps; a 120 tps variant (r86 nested-boot pattern) was
  not run for nav.
- **`map_set_use_async_iterations=false` + live changes**: the async=false path was measured
  for the *initial* sync (f1) only; change-application timing under async=false was not
  split (looked the same in discovery, 2–3 frames).
- **`NavigationServer2D.get_process_info(INFO_*)` values** (map/region/agent counts) were
  not read.
- **Agent `path_postprocessing`/`simplify_path`/`path_max_distance` levers** on the node
  (only the query-params object was latticed).
- **Threaded/`run_on_separate_thread` navigation** not tested.
- **Portability**: every value is this host/build/`--headless`/60 tps/GodotPhysics2D.
- **The other candidates** (TileMapLayer, AnimationPlayer, Tween timing, audio routing,
  OS/Engine meta) were weighed but not measured this round (§0); `Tween.interpolate_value`
  got three discovery receipts (`runs/disc-tweenval.out`).

---

## 9. Host cleanup

- **45 canonical runs + 31 loadtest runs + 82 discovery/smoke runs** (158 godot launches),
  all `--headless`, all `timeout -s KILL`-bounded (30 s bound; none hit), no run left
  running (`pgrep -fa godot` shows only concurrent lanes' processes — g3d r92/r93,
  r88-fold, r89-boundary, r90 boundary — **none from this seat**).
- The loadtest `yes` hogs were cleared after each block (`pgrep -c -x yes` → 0).
- No tracked file written: `git status --porcelain` shows only the concurrent r88-fold
  lane's two fixture edits (not this seat's) and untracked `corpus/live/*` churn.
- `manifest.sha256` (398 lines) covers every artefact under `corpus/live/r91-scout/`.

---

## 10. Evidence index

All under `corpus/live/r91-scout/`; `manifest.sha256` (398 lines) covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| **frozen primary probe, 9 arms** | `probes/nav_lattice.gd` | `efb496e5fe08e667` |
| discovery micro-probe (20 arms) | `probes/discover.gd` | `f409c04dbb660f50` |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| driver (9 cells, 45 runs) | `run_cells.sh` | `de59a62b51d618cb` |
| analyzer → json | `analyze_r91.py` → `runs/analyze_r91.json` | `d5ae1fadf6f1b6b2` / `4948319c4f1c4bad` |
| author rows + verifier | `author-rows.py.txt`, `verify_rows.py`, `make_author_rows.py` | `52c4bdd0befb28d9` / `9346a867168ddb22` / `fa81c891fe197d2b` |
| per-cell receipts (45 × 3 files) | `runs/r91_*.{out,err,rc}` | `manifest.sha256` |
| loadtest receipts (31 runs, load 20–25) | `runs/loadtest/` | `manifest.sha256` |
| discovery/smoke receipts | `runs/disc-*.{out,err}`, `runs/smoke*.{out,err}` | `manifest.sha256` |

Reproduce: `bash run_cells.sh && python3 analyze_r91.py && python3 make_author_rows.py &&
python3 verify_rows.py` (expect `UNSTABLE=['nav_avoid']`, `ROWS_PREFIX … rejected=[]`).
