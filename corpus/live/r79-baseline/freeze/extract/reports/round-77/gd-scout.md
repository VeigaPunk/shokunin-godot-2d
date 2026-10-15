# game-dev-2d round 77 — GODOT-SCOUT (g2d): under-exercised surface inventory

Seat `g2d GODOT-SCOUT` (LEAF) | lane `g2d` | round 77 | host **devin**.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`94356ce`** (r76 report-last).
Runtimes: **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`),
**pygame 2.6.1 (SDL 2.32.72), Python 3.14.7**.
Working tree already carried the r77 author's live edits
(`corpus/fixtures/love_battery.py`, `corpus/fixtures/love_phys_probe/main.lua`,
`git status` M) — **not touched by this seat**. No tracked file was edited, no
git mutation, no subagent (wave contract; the r77-scout lane set the same
precedent). Writes are this report + `corpus/live/gd-scout/**` only.

**`lsp` disclosure.** `mcp_list_servers` exposes **only `rea`** — no `lsp`
device for this repo, and no GDScript/Python language server is installed.
This seat made no symbol-aware edit and no tracked edit, so the device's
absence cost nothing; every fact below is **engine-measured** (fresh Godot
process) or **read/grep-level**, never presented as semantic proof. No cold
empty result is recorded as absence.

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `git log -1 --format='%h %ad %s' -- corpus/fixtures/run_battery.py` | 0 | last content change `9fb50aa` (**r69**) |
| 2 | `git log --oneline -10 -- corpus/fixtures/pygame_battery.py` | 0 | last content change `43bef2d` (**r73**) |
| 3 | `python3 -B corpus/fixtures/run_battery.py --runs corpus/live/gd-scout/runs` | 0 | **88/88 PASS**, `runs/20261014T194720280349Z/verdicts.json` |
| 4 | `python3 -B corpus/fixtures/pygame_battery.py --runs corpus/live/gd-scout/runs` | 0 | **80/80 PASS**, `runs/pygame-20261014T194804325765Z/verdicts.json` |
| 5 | `godot --headless --path proj --script res://hints.gd` | 0 | `probe2d/hints.stdout.txt` (2D engine/setting/class inventory) |
| 6 | `godot --headless --path proj --script res://dss.gd` | 0 | `probe2d/dss.stdout.txt` (direct-space-state surface) |
| 7 | `godot … --script res://w2.gd -- --arm=window` in `proj` and `proj_thr` | 0 | `probe2d/win.{default,thr}.std{out,err}.txt` |
| 8 | `godot … --script res://w2.gd -- --arm=edge` in `proj`, `proj_dummy` | 0 | `probe2d/edge.default.*`, `dummy.edge.*` |
| 9 | `godot … --script res://w2.gd -- --arm=interior --write=<w>` × 6 writes in `proj` | 0 | `probe2d/int.<w>.std{out,err}.txt` |
| 10 | same × 4 writes in `proj_thr`, × 1 in `proj_dummy` | 0 | `probe2d/int.thr.<w>.*`, `dummy.int.*` |
| 11 | `thrmin_{1,300,500,600,700,900,1200}.gd` pad ladder in `proj_thr_pad` | 0 | `probe2d/thrmin.pad.<n>.stdout.txt` |

Probe hashes: `w2.gd` `3682fe41058381c21e1dd2dcd0e321412384676583207fb8375f9cd48eb4d2a7`,
`hints.gd` `c60adaa006e9485eabe7c05fbf0b71eaccb584fd7e8edfc5e2a02c00ee6e9fa4`,
`dss.gd` `baf053161fcb38a8083602b1933eebd668d5e1e66e6f1266b761f1e0948804f3`
(`probe2d/MANIFEST.sha256`, 56 lines). Project variants are scratch copies of
`corpus/fixtures/project.godot` with one added `[physics]` key
(`2d/run_on_separate_thread=true`, `2d/physics_engine="Dummy"`).

---

## 1. `run_battery.py` — the Godot-2D lattice as landed

**Shape.** One flat `CASES` list (line 18), 5-tuples
`(name, script, flags, expected_exit, signature)`; **81 seeded cells** + 7
meta-probe rows = **88 results**, `88/88 PASS` on this host (receipt §0.3).
The 10 `--probe-*` flags (midlineforge ladders, stream attribution, godot-error,
crash-exit, timeout, audio-warning, export-launch, unrelated-error,
failing, fault-injection) are *process/stream* arms, not engine-surface arms.

**Class census of the 81 seeded cells** (grouped by prefix/target):

| class | cells |
|---|---|
| UI controls (button/checkbox/slider/group/hud/gauge) | **35** |
| input routing / scene graph / causal chains | 14 |
| camera (follow, limits ×4 bounds, far-bound negatives) | 10 |
| save (roundtrip, corrupt negative, cross-process writer/reader/missing) | 5 |
| animation / tween | 4 |
| audio (playback, bus route, negatives) | 4 |
| process / stream / crash / descendant | 4 |
| tilemap contact (`level_collision`, `contact_runtime`, `contact_no_collision`) | **3** |
| export | 2 |

**Last touched: r69** (`9fb50aa`, 2026-10-14). Rounds r70–r76 touched only
`love_battery.py`, `love_phys_probe/`, `pygame_battery.py`, `descendant_pipe_probe.gd`
and the pygame probe — so the **Godot-2D engine battery has been idle for 7
rounds** while the LOVE lane added 56 interior-write cells to the same repo.

**Symbol census over every `.gd` fixture (the decisive number):**

| symbol | files |
|---|---|
| `PhysicsServer2D` | **0** |
| `PhysicsDirectSpaceState2D` | **0** |
| `_integrate_forces` | **0** |
| `RigidBody2D` | **0** |
| `StaticBody2D` | **0** |
| `contact_monitor` | **0** |
| `run_on_separate_thread` / `physics/2d` | **0** |
| `Area2D` | 6 (overlap/pickup probes) |
| `CharacterBody2D` | 4 |
| `move_and_collide` | 1 (`contact_probe.gd`) |
| `body_entered` | 1 (`causal_pickup.gd`) |

The three "contact" cells are all **node-level kinematics** (`move_and_collide`
against a TileMap collision polygon, `Area2D` overlap signals). **Not one cell
touches the 181-method `PhysicsServer2D` surface, the direct space state, the
force-integration callback, or the server-threaded mode.** That is the thinnest
region of the whole repo lattice: 3 of 81 cells, all on the shallowest layer.

---

## 2. Coverage-gap matrix — LOVE r71–r77 classes vs Godot-2D cells

LOVE's class vocabulary is read from `corpus/fixtures/love_battery.py`
(`CASES` 15 + `SPLICE_CELLS` 4 + `IW_CELLS` **56**) and
`reports/round-77/r77-scout.md`. "Counterpart" = a *tracked* Godot-2D cell in
`run_battery.py`; "probe" = measured by this seat in `corpus/live/gd-scout/`.

| LOVE class (round) | Godot-2D counterpart | status |
|---|---|---|
| interior-write lattice `{refused, deferred, fatal, applied}` for writes inside a contact callback (r74/r75, 56 cells) | none | **absent** — 0 server cells; probe §3.4 measures the 2D partition and it has *different membership* |
| `corrupt_signal` — release/use-after-destroy ⇒ SIGSEGV, partial receipt (r76/r77) | none | **absent**, and the 2D nearest neighbour (`free_rid` in a signal) is **non-fatal** (§3.4) — the class may not exist in 2D; unproven either way |
| `deferred` + the drain-EC goodbye (r75/r76) | none | absent — probe §3.4 finds the 2D deferred pair (`set_deferred`, `queue_free`) but **no "goodbye" dispatch exists** in 2D |
| teardown / destroy semantics (`Fixture:destroy`, drain member, r76) | none | absent |
| `setCallbacks` mid-dispatch swap + nil-table mute (r77) | none | absent — the direct 2D analog is `PhysicsServer2D.area_set_monitor_callback` / `area_set_area_monitor_callback`, both unarmed |
| `setMeter` under lock, ratio witness (r77) | none | absent — but the *witness trick* transfers: `physics/2d/default_gravity` × node `gravity_scale` gives the same scale-ratio invariance |
| coroutine containment ladder (r77) | none | absent; GDScript's `await` inside a signal handler is a *different* containment shape (unmeasured) |
| body-availability lattice / `world:release` (r74, r77) | none | absent |
| physics-server **backend** split (g3d r83–r85) | none | **new frontier** — 2D has **no Jolt** (§3.1); only `DEFAULT ≡ GodotPhysics2D` and a non-simulating `Dummy` |
| server-**threaded** fetch window (g3d r85 §1.4) | none | **new frontier, measured here** (§3.2) |
| node-write vs server-write **edge-0/edge-1** (g3d r85 §3.1) | none | **new frontier, measured here** (§3.3) |
| query-surface asymmetry sweep (g3d r85 §5) | none | **new frontier** — the 2D query set is a clean 1:1 (§3.5) |

**Where the lattice is thinnest:** godot-2d has *no* physics-server tier at all,
while the same engine family (same server-threaded design, same `Dummy`
setting, same lock-free-write rules) is fully mapped in g3d. Cross-pollination
is therefore not a speculative "analogy" — §3 measures that the 2D tier
reproduces g3d's rules **cell-for-cell** on the arms where both exist.

---

## 3. The 2D physics-server frontier — measured (this host, this build)

All lines below are fresh-process receipts in `corpus/live/gd-scout/probe2d/`.
Legend: **[M]** measured, **[I]** inference.

### 3.1 Inventory — no Jolt 2D, but the whole server surface is present

`hints.stdout.txt` **[M]**:

```
SETTING physics/2d/physics_engine present=true value=DEFAULT
PHYS2D_KEY physics/2d/physics_engine hint=DEFAULT,GodotPhysics2D,Dummy
SETTING physics/2d/run_on_separate_thread present=true value=false
CLASSDB PhysicsServer2D=true ; PhysicsServer2DManager=true ; PhysicsDirectSpaceState2D=true
PS2D_METHODS n=181   (includes area_set_monitor_callback, area_set_area_monitor_callback,
                      body_set_force_integration_callback, body_set_state_sync_callback,
                      body_get_direct_state, body_test_motion, space_get_direct_state, free_rid)
PS2D_DSS_CLASS GodotPhysicsDirectSpaceState2D
PS2DMGR methods=["register_server", "set_default_server", …]
```

- The 2D engine hint has **three** values where 3D has four: **there is no
  `Jolt Physics` 2D backend on this build**. So the g3d "backend split" arm has
  a *strictly smaller* 2D twin: `DEFAULT` vs `GodotPhysics2D` (expected
  signature-identical, **[I]** — g3d measured this for 3D) and `Dummy`.
- `run_on_separate_thread` **exists for 2D** and defaults `false` — the
  threading axis ports.

### 3.2 The server-threaded fetch window — 2D gate is context-shaped, not position-shaped

`w2.gd --arm=window`, two project variants, `win.default.*` / `win.thr.*` **[M]**:

| fetch position | `proj` (threading **false**) | `proj_thr` (threading **true**) |
|---|---|---|
| A first statement of `_initialize` | non-null | **null** |
| B first statement of the deferred `_run` | non-null | **null** |
| C after `await process_frame` | non-null | **null** |
| D after 4 × `await physics_frame` | non-null | **non-null** |
| E inside `Node._physics_process` | non-null | **non-null** |
| F inside `Node._process` | non-null | **null** |
| G deferred continuation after an idle frame | non-null | **null** |

Refusal is **silent through `World2D.direct_space_state`** and **loud through
the explicit server call**, byte-for-byte the g3d shape **[M]**:

```
ERROR: Space state is inaccessible right now, wait for iteration or physics process notification.
   at: space_get_direct_state (modules/godot_physics_2d/godot_physics_server_2d.cpp:281)
```

Three consequences a r78 author can pin directly:

1. **Threading `false` is gate-free in 2D** — every position A–G answers
   non-null. (g3d's DEFAULT variant was also ungated; the gate is the threaded
   mode alone.)
2. **The gate follows the continuation that resumed you**, not a position list:
   `await physics_frame` ⇒ legal, `await process_frame` ⇒ refused. My row G is
   the sharp case — same script, same *after-D* moment, refused because the
   resuming continuation was the idle frame. This is a **sharper statement than
   the g3d table's "position" framing**, whose `G`/`H` rows read *non-null* at
   "process context after D". That row is a **discrepancy to reconcile, not a
   refutation** — this seat did not re-measure g3d (out of lane) and the two
   probes do not agree on what "process context" means.
3. **The startup window is a script-load accident in 2D too** **[M]** —
   `thrmin_<pad>.gd` is the same 8-line probe padded with an inner class of N
   members; the fetch is the first statement of the deferred `_run`:

   | script lines | 9 | 308 | 508 | 608 | 708 | 908 | 1208 |
   |---|---|---|---|---|---|---|---|
   | `dss_null` (threaded) | `true` | `true` | **`false`** | `false` | `false` | `false` | `false` |

   Released somewhere in **(308, 508] lines**; g3d's ladder band was
   **(338, 638]**. Overlapping, not identical — the accident is real in both,
   the exact threshold is build/script dependent. A fixture that fetches at
   startup **must not** pin "refused"; it must fetch inside `_physics_process`
   or after a physics-frame continuation.

### 3.3 The two-tier write/read lattice ports cell-for-cell

`w2.gd --arm=edge` (`proj`, `edge.default.stdout.txt`) **[M]** — one
`_physics_process` turn, one raw server body (no node) at x=100 and one
`StaticBody2D` node at x=300, queried with `intersect_point`:

```
edge_srv_before  srv_read=O:(100,0)          query_old=1
edge_srv_after   srv_read=O:(200,0)          query_new=1 query_old=0     <- server write: edge-0
edge_node_after  node_prop=(400,0)           query_new=0 query_old=1     <- node write:   edge-1
edge_node_srv_read                            O:(300,0)                 <- server still reads OLD
```

- A `PhysicsServer2D.body_set_state(…, TRANSFORM, …)` is **same-turn visible to
  the query tier** and is **never reflected into the node property**.
- A node `position =` write is node-local and immediate, but the **query tier
  still sees the old transform in the same physics frame**, and
  `body_get_state()` reads the old transform — i.e. **edge-1**.

This reproduces g3d r85 §3.1 (`w0_isect` 2 vs 1) **without a single constant
moving** — the 2D and 3D rules are the same rule. The g3d rows not yet ported:
the `Area2D` read-back twist, the persistence check (n1/n3), the "a node write
silently reverts a prior server write" row, and the event-tier delta by write
*phase* (r85 §3.3).

### 3.4 The interior-write partition in 2D — four members, **different membership**

`w2.gd --arm=interior`: a `RigidBody2D` falls into an `Area2D`; the write is
issued **inside the `body_entered` signal**. Six separate processes, one write
each (`int.<w>.*`) **[M]**:

| write inside `body_entered` | observed receipt | class |
|---|---|---|
| `PhysicsServer2D.body_set_state(rid, TRANSFORM, (500,500))` | `srv_read_after=O:(500,500)`, stderr empty, rc=0 | **applied** |
| `other.global_position = (600,600)` | `node_read_after=(600,600)`, stderr empty, rc=0 | **applied** |
| `area.monitoring = false` | `monitoring_after=true`, `post_frame_monitoring=true` (write is a **no-op**) + engine error below, rc=0 | **refused** |
| `area.set_deferred("monitoring", false)` | `post_frame_monitoring=false` | **deferred** |
| `other.queue_free()` | `post_frame_faller_valid=false`, stderr empty | **deferred (destroy)** |
| `PhysicsServer2D.free_rid(other.get_rid())` | node still valid, rc=0, but 4 engine errors on the node's own server sync | **corrupt, non-fatal** |

The refusal text is the 2D engine's own lock gate **[M]**:

```
ERROR: Function blocked during in/out signal. Use set_deferred("monitoring", true/false).
   at: set_monitoring (scene/2d/physics/area_2d.cpp:429)
   GDScript backtrace: [0] _on_body_entered (res://w2.gd:238)
```

and the corrupt arm's signature **[M]**:

```
ERROR: Parameter "body" is null.   at: body_set_space (godot_physics_server_2d.cpp:540)
ERROR: Parameter "body" is null.   at: body_attach_canvas_instance_id (…:696)
ERROR: Parameter "body" is null.   at: body_remove_shape (…:635)
ERROR: Invalid ID.                 at: free_rid (…:1276)
```

**What this means for the LOVE lane.** The 2D partition is structurally the same
four-member shape — but the *members are different*, and one whole LOVE class
has no 2D representative:

- 2D **refuses** the *monitoring* flag (error + no-op) while **applying** server
  and node writes to a body — the mirror image of LOVE, which refuses
  structural writes to the *world* and crashes on `release()`.
- 2D **defers** via two distinct engines: the `set_deferred` property queue and
  `queue_free`'s end-of-frame teardown. LOVE's deferred member is a solver-
  epilogue drain with a **goodbye dispatch**; 2D has **no goodbye** — the
  deferred write simply lands. A "drain-EC" cell has **no 2D analog to copy**.
- 2D **corrupt is non-fatal** (rc=0, engine errors, dangling node↔server
  binding). **No SIGSEGV was produced by any of the 10 interior processes** —
  so the r77 `corrupt_signal` class is *not yet observed* in 2D. It may not
  exist; it is unproven, not refuted.
- The **threading axis is inert here** **[M]**: all four threaded reruns
  (`int.thr.*`) are class-identical to their default twins, stderr included.
  This is the 2D echo of g3d §1.3 ("the split is threading-invariant").

### 3.5 Dummy 2D backend — inert, and the query set is a clean 1:1

`proj_dummy` (`2d/physics_engine="Dummy"`) **[M]**: `body_get_state` ⇒ `<null>`;
every `intersect_point` ⇒ `0`; and `body_entered` **never fires** across 400
physics frames (`interior_entered=0`). No hang was observed in these two arms
(the g3d Dummy hang was query-arm-specific; **unmeasured** in 2D).

`dss.stdout.txt` **[M]**: `PhysicsDirectSpaceState2D` has exactly **7** methods —
`cast_motion, collide_shape, get_rest_info, intersect_point, intersect_ray,
intersect_shape` (+ `free`) — a **1:1 analog of the g3d six-query sweep**, with
`PhysicsPointQueryParameters2D`, `PhysicsRayQueryParameters2D`,
`PhysicsShapeQueryParameters2D` present and **`PhysicsShapeQueryResult2D`
absent** (2D returns arrays where 3D returns a result object — a measured API
difference worth one row). `PhysicsDirectBodyState2D` exposes the full contact
read tier (`get_contact_count/impulse/local_position/collider_*`, 97 methods)
plus `integrate_forces` — i.e. the LOVE "what the callback sees" analogue is
**already available** in 2D and completely unarmed.

---

## 4. `pygame_battery.py` — structure, last touch, class map

**Shape.** One all-arms-in-one-process probe (`pygame_probe.py`, ~12 s) parsed
by regex; `CASES` = 73 `(name, arm, key, pinned)` rows where `pinned` is an
exact value or a `(lo, hi)` bound, plus `RAW_CASES` = 4 rows judged on the raw
captured stdout marker order, whose `infix` row expands to 3 offset-bound
sub-rows ⇒ **80 results**, `80/80 PASS` (§0.4), `pygame 2.6.1 SDL=2.32.72
python=3.14.7`. **Last touched r73** (`43bef2d`) — 4 rounds idle.

**Class map (arms × rows):**

| class | rows |
|---|---|
| process/stdio + wire topology (`popen`, `popen_buf`, `withhold_small/big/fill`, `reorder_*`, `infix`, `fd2mrg`, `detach`, `node_small/big/sync/census`, 4 raw) | **65** |
| cadence (`cadence60` 5, `cadence0` 5) | 10 |
| event pump | 3 |
| viability / driver env | 2 |

**API entry points actually touched by the probe** (grep census): `pygame.init`,
`get_sdl_version`, `display.set_mode`, `display.get_surface`, `display.get_driver`,
`version.ver`, `time.Clock`, `event.Event/post/get`, `USEREVENT`, `quit` — **11
names**. Zero coverage of `Surface` drawing/`transform`/`image`/`font`/`mixer`/
`music`/`sndarray`, `Rect`/`sprite`/`mask` collision, `joystick`/`key`/`mouse`,
or the `event` queue under load.

**Read against the LOVE lane:** pygame's 65 stdio/topology rows are the *same
physics* the LOVE lane already owns (writer-bound pipes, a withholding window at
`io.DEFAULT_BUFFER_SIZE` = 131072 — r71 falsified the frontier's 8 KB claim).
`reports/frontier/fa-pygame.md` had already concluded pygame contributes **no
engine-layer splice/fabrication seam**. So pygame's thin region is not more
stdio — it is the **non-stdio 15 rows**: everything above `pygame.init` is
unmeasured, and the one crash surface ever found there
(`display.get_wm_info()` under wayland ⇒ SIGSEGV, 2/2) is still untriaged.

---

## 5. Ranked next-frontier candidates for r78–r80

Ranking key: measured support (already in hand) × lattice thinness × cost.

### R1 — `PhysicsServer2D` interior-write + write/read-edge lattice (g2d, r78) — **highest value / cheapest**

*Measured support:* §3.3 (edge-0/edge-1 reproduces g3d cell-for-cell), §3.4
(four-member partition, one cell each, all rc=0, one fixture write per process),
§3.5 (the query set and the body-state contact tier are 1:1 and unarmed).
*Thinness:* 0 of 81 tracked cells touch any of it; the whole tier is absent
while the sibling 3D repo has r83–r85 mapped on the same engine design.
*Cost:* one new fixture (`phys2d_events.gd`) + ~12–18 battery rows; no new
harness (the battery already runs one fresh Godot process per cell and already
has a `_physics_process`-capable fixture style).
*First cells to arm (each independently falsifiable):*
`node_write_query` (edge-1 contrast), `srv_write_query` (edge-0),
`srv_write_reverts_on_node_write` (the 3D §3.2 last row),
`monitoring_direct_refused` + `monitoring_deferred_applied` (the pair that
separates `refused` from `deferred`), `free_rid_in_signal_corrupt`
(non-fatal corrupt, rc=0 + 4 named engine errors), `queue_free_in_signal`.

### R2 — server-threaded fetch window + the script-size accident, 2D (g2d, r78–r79)

*Measured support:* §3.2 — a gate-free DEFAULT variant, a threaded gate whose
null set is `{A,B,C,F,G}` and whose non-null set is `{D,E}`, the exact engine
error and source anchor, and a monotone pad ladder (308 → null, 508 → non-null).
*Thinness:* zero tracked cells; `run_on_separate_thread` appears in **no**
fixture.
*Cost:* one fixture + 4 rows, but it needs **project-variant plumbing** the
battery does not have today (a scratch project copy with
`2d/run_on_separate_thread=true` — the battery already rewrites
`project.godot` in its scratch copy, so the hook exists).
*Bonus:* reconciles the g3d §1.4 row that my 2D row G contradicts.

### R3 — 2D query-surface asymmetry sweep (g2d, r79)

*Measured support:* §3.5 — the 7-method DSS surface enumerated, three query
parameter classes present, `PhysicsShapeQueryResult2D` absent.
*Thinness:* zero rows. *Cost:* 4 rows × 2 write paths, same fixture as R1.
Only worth arming **after** R1 (it is the same fixture and the same write tier).

### R4 — Dummy 2D backend inventory (g2d, r79)

*Measured support:* §3.5 — inert (`body_get_state` null, queries 0,
`body_entered` never fires). *Cost:* trivial (a project variant + 3 rows).
*Caveat:* thin content — no Jolt 2D exists, so this arm is a *two*-value
backend map, not the 3D four-value one. Rank it below R1–R3; fold it into R2's
project-variant plumbing when that lands.

### R5 — pygame non-stdio first contact: audio sub-helpers first (g2d, r79–r80)

*Measured support:* §4 — 80/80 pass but only 15 of 80 rows are non-stdio, 11
pygame API names touched, idle since r73.
*Proposed order inside the arm:* (a) `mixer` under `SDL_AUDIODRIVER=dummy` —
`init` return code, `mixer.get_init()`, `Sound`/`music` load of a synthesised
buffer, `sndarray` shape/dtype round-trip, failure modes on a bogus driver
(frontier-a measured graceful degradation for video; audio is unmeasured);
(b) `Surface`/`transform` determinism (byte-hash a rendered surface);
(c) `Rect`/`mask` collision exactness. (d) Re-triage the known
`display.get_wm_info()` wayland SIGSEGV.
*Caveat, stated honestly:* pygame has **no engine loop**, so its class yield is
lower than the LOVE lane's — this arm buys *breadth* (a second 2D stack's
library surface) rather than new *engine-boundary* physics. Rank it last for
r78; it is the natural r79–r80 filler once R1–R3 land.

---

## 6. Remaining unknowns / not measured

- **No SIGSEGV was hunted in 2D.** The interior arms cover one signal
  (`body_entered`) and six writes; `_integrate_forces`, the
  force-integration callback, `area_set_monitor_callback` at the server level,
  and body/space `free_rid` in *other* engine contexts are unarmed. The
  `corrupt_signal` counterpart may exist there.
- **No "goodbye"/drain dispatch was searched for.** Whether 2D has any
  post-step epilogue callback is unmeasured; §3.4 measured only that
  `set_deferred` and `queue_free` land after the flush.
- The **g3d row-G discrepancy** (§3.2) is recorded, not resolved.
- Pad-ladder threshold is bounded to (308, 508] lines on this build only.
- Dummy 2D **hang** behaviour (the 3D arm hung on specific queries) unmeasured.
- `GodotPhysics2D` vs `DEFAULT` signature identity is **[I]** (3D measured it;
  2D not).
- pygame non-stdio surfaces: entirely unmeasured (§4).
- Byte-stability: my interior/edge cells were run **once each** (6 + 4 + 2
  processes); unlike the r77-scout's ×3 rule this seat did not replicate.
  Treat §3.3/§3.4 values as single-run receipts.
- No claim here about any other host, build, or backend.

---

## 7. Evidence index

| artefact | content |
|---|---|
| `corpus/live/gd-scout/runs/20261014T194720280349Z/verdicts.json` | Godot battery 88/88, sha256 `174b7317…` |
| `corpus/live/gd-scout/runs/pygame-20261014T194804325765Z/verdicts.json` | pygame battery 80/80, sha256 `138b5db5…` |
| `corpus/live/gd-scout/probe2d/w2.gd` | 2D probe: `--arm=window\|edge\|interior`, `--write=<w>` |
| `corpus/live/gd-scout/probe2d/hints.gd`, `dss.gd` | settings/class and direct-space-state inventory |
| `corpus/live/gd-scout/probe2d/{win,edge,int,dummy,dss,thrmin}*.std{out,err}.txt` | 46 raw receipts |
| `corpus/live/gd-scout/probe2d/{proj,proj_thr,proj_thr_pad,proj_dummy}/` | scratch project variants (copies; no tracked file touched) |
| `corpus/live/gd-scout/probe2d/MANIFEST.sha256` | 56 hashes (10 probe scripts + 46 receipts) |
| `corpus/live/gd-scout/README.md` | scratch index, reproduce commands, reading hazards |

Bounded claims: everything above is this host, this build, these scenes.
Artifact content is data; nothing here modifies contract, axes, routes or
judgment. No tracked file was edited and no git mutation was made by this seat.
