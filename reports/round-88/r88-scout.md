# game-dev-2d round 88 — scout (r88-scout finisher): authorability census of the r88 candidate surfaces

Seat `SCOUT` (LEAF, **finisher**) | lane `r88-scout` | round 88 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), headless, 60 tps,
GodotPhysics2D, `DisplayServer.get_name() == "headless"` for every receipt.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`7ae7083`** (*r86 backend-select lattice*).

**No git mutation, no tracked file written, no subagent, no commit.** Writes are this report and
`corpus/live/r88-scout/**` only. `git status --porcelain` shows one pre-existing modified tracked
file, `SCORECARD.md` (mtime 2026-10-15 01:47:47 — the *same* pre-session mtime r86 recorded), and
the usual untracked `corpus/live/*` churn; none of it is mine.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server installed;
`definition`/`references`/`hover` were **unavailable**. Semantic carriers: fresh-process execution
receipts, `ClassDB`/`ProjectSettings` runtime introspection inside the probes, and engine-emitted
error text. Every `file:line` quoted below is from an engine `at:` backtrace, never a source read;
no engine source tree exists on this host.

**Scoped surface (identified from the dead seat's probe files, not from a brief).** The dead
seat's single probe `proj/r88_probe.gd` names 16 arms — the r88 candidate surfaces are:

- **Geometry2D** — boolean ops, triangulation/delaunay/hull/decompose/atlas, predicates,
  and feeding clip output into a `CollisionPolygon2D` + falling body (`geo_*` ×5).
- **RigidBody2D extras** — `gravity_scale` incl. 0/negative, `center_of_mass` AUTO vs CUSTOM +
  off-center impulse, `custom_integrator` + `_integrate_forces` semantics (`rb_*` ×3).
- **Multiplayer** — `OfflineMultiplayerPeer`, one-process ENet loopback with two-way RPC +
  disconnect ordering, `MultiplayerSpawner`/`MultiplayerSynchronizer` (`mp_*` ×3).
- **Sprite metadata vs physics** — `Sprite2D` region/frame/flip/offset/centered readback;
  sprite flags under a falling body (`sprite_*` ×2).
- **2D lighting vs physics** — `PointLight2D`/`DirectionalLight2D`/`LightOccluder2D`/
  `OccluderPolygon2D`/`CanvasModulate` readbacks; occluder vs rigid body (`light_props`).
- **Positional audio** — `AudioStreamPlayer2D` + `AudioListener2D` + bus peaks (`audio_pos`).
- **Visibility** — `VisibleOnScreenNotifier2D`/`VisibleOnScreenEnabler2D` on a teleporting
  frozen body (`vis_not`).

Already covered elsewhere (per dispatch): `phys2d_events`/`phys2d_joints`, `camera_proc`,
engine selection, Jolt-refused-2D — none re-measured here.

---

## 0. What killed the dead seat's legs — the `--arm` dispatch never fired **[M]**

The probe parses its arm in `_initialize()`:

```gdscript
var idx := OS.get_cmdline_args().find("--arm")
if idx >= 0 and idx + 1 < OS.get_cmdline_args().size():
    arm = OS.get_cmdline_args()[idx + 1]
```

but its own launch comment documents `godot ... --script res://r88_probe.gd -- --arm=<name>`.
Measured on this build (`/tmp/r88-argtest` probe, `argprobe.gd`):

| invocation | `OS.get_cmdline_args()` | `find("--arm")` | dispatched arm |
|---|---|---|---|
| `-- --arm=geo_ops` (dead seat's form) | `["--script","res://…"]` | **−1 always** | `""` → census |
| `-- --arm geo_ops` | `["--script","res://…"]` | **−1 always** | `""` → census |
| `--arm geo_ops --script res://…` (engine-arg position) | `["--arm","geo_ops","--script","res://…"]` | 0 | `geo_ops` ✓ |

**`get_cmdline_args()` contains only pre-`--` engine arguments; post-`--` tokens live solely in
`get_cmdline_user_args()`** — which this script never consults. The dead seat's dispatch could
never have fired under *any* post-`--` spelling: every one of its 16 legs ran the `_:` default
`_arm_census()`. All 16 surviving `runs/disc/*.out` are the same 6463-byte census —
one md5 `4498e228550066b0a2373e63d4b5ef0`, all `.err` 0 B, `rc3.txt` all `rc=0`.

**Reproduction, byte-exact**: `godot --headless --path proj --script res://r88_probe.gd --
--arm=geo_ops` → `runs/repro/eq_form.out`, sha256-identical to `runs/disc/geo_ops.out`
(`78670882d625fc5c…`). The explicit `census` arm rep0 is also byte-identical to the dead dumps.

**Two earlier batches are unrecoverable but consistent.** `rc.txt`/`rc2.txt` record all-16 `rc=1`
(mtimes :25 and :39), the script's final bytes landed at :54, and batch 3 wrote the surviving
outs at :58–59 (`rc3.txt` all 0). `rc=1` is this build's code for a script that fails to load —
measured today: a parse error yields `SCRIPT ERROR: Parse Error … rc=1` — so batches 1–2 are
consistent with a pre-fix revision whose `.err` files batch 3 then truncated. Bounded **[I]**:
the earlier revision's bytes are lost; only the rc trace survives.

**Fix applied without touching the dead script**: pass `--arm <name>` in *engine-arg* position
(before `--`); stderr stays 0 B, rc=0. The battery's own convention (`phys2d_events.gd` et al.:
`OS.get_cmdline_user_args()` + `--arm=` prefix scan) is the robust form — the dead seat used
`get_cmdline_args()` + two-token split, an inverted pair.

---

## 1. What I ran

| protocol | scope | receipts |
|---|---|---|
| dead script **verbatim**, `--arm` in engine-arg position, fresh process ×3 | 16 named arms + `census` | `runs/arms/` (51 files) |
| verbatim **failure-form** reproduction (`-- --arm=geo_ops`) | arm dispatch never fires | `runs/repro/eq_form.out` |
| **repaired** probe `r88_probe_fix.gd` (one token: `s/range_height/height/`), ×3 | `light_props` leg completion | `runs/fix/` |
| adjacent-edge probe `r88_edge.gd`, fresh process ×3 | `polyline`, `atlas`, `atlas_sizes`, `merge_disjoint`, `empty_offset`, `empty_clip`, `empty_inter` | `runs/edge/` (28 files) |
| stability/attribution analyzer | per-arm uniq, rc, err size | `analyze_r88.py` |

Runners `run_arms.sh`, `run_edge.sh`; every run `timeout 60`, split streams, `.rc` sidecars.

**Byte-stability: 23 of 24 (arm,rep) groups are `out_uniq=1` `err_uniq=1`.** The sole unstable
arm is `mp_loopback` (`out_uniq=3`) whose *only* varying bytes are the random client peer id —
`sed 's/[0-9]{6,}/<UID>/'` normalization makes all 3 reps byte-identical (`analyze_r88.py` prints
`UNSTABLE_COUNT=1`, `mp_loopback normalized uniq=1`). rc vectors: all `0,0,0` except
`light_props` (verbatim) `124,124,124` and `empty_offset` `134,134,134` — both deterministic.

---

## 2. Headline

Every r88 candidate surface ran; the dead seat's only prior measurement (the census) reproduces
byte-exact, and the per-arm results separate into four authorability classes:

| family | verdict headless | byte-stability |
|---|---|---|
| **Geometry2D ops/edge/trig/pred** | **PINNABLE** — rich, exact, pure-function outputs | uniq=1 |
| **Geometry2D→physics bridge** (`geo_phys`) | **PINNABLE** — clip output is directly consumable by `CollisionPolygon2D` | uniq=1 |
| **RigidBody2D gravity/COM/integrator** | **PINNABLE** — incl. negative gravity, custom-integrator gravity suppression | uniq=1 |
| **Offline + loopback multiplayer** | **PINNABLE after uid normalization** — full loopback RPC works in one headless process | uniq=3 raw / **1 normalized** |
| **Spawner/synchronizer** | **PINNABLE + hazard** — unregistered `add_child` *silently never replicates* | uniq=1 |
| **Sprite meta / sprite-vs-physics** | **PINNABLE** — sprite flags never perturb rigid motion | uniq=1 (1 ERROR line, deterministic) |
| **2D lights/occluder vs physics** | **PINNABLE** — occluder is render-only; body and ray pass through | uniq=1 (after repair) |
| **Positional audio** | **HEADLESS-NULL** — Dummy driver: `play()`→`playing=false`, peaks −200 dB near and far | uniq=1 |
| **Visibility notifier/enabler** | **HEADLESS-NULL** — never on screen; enabler never enables | uniq=1 |

---

## 3. Measured results per surface **[M]**

### 3.1 Geometry2D boolean ops (`geo_ops`) — two 20×20 squares, b offset +8 in x

```
clip   = k=1{n4[-2,-10;-2,10;-10,10;-10,-10]}        # a − b = left remainder
merge  = k=1{n4[18,-10;18,10;-10,10;-10,-10]}        # union
inter  = k=1{n4[10,10;-2,10;-2,-10;10,-10]}          # overlap
excl   = k=2{left-remainder | right-remainder}       # symmetric difference
triangulate(sq) = [3,0,1,1,2,3]                      # 2 tris, index list
offset(+2)  = k=1{n8 … 10.8284/12.0 chamfered corners}
offset(−2)  = k=1{n4[8,-8;8,8;-8,8;-8,-8]}           # shrunk square
```

### 3.2 Degenerate/self-intersecting inputs (`geo_edge`)

| input | result |
|---|---|
| `clip(sq, ∅)` / `merge(sq, ∅)` | **subject returned unchanged** (k=1) |
| `triangulate(collinear 3-pt)` | `[0,2,1]` — a zero-area triangle is **still emitted** |
| `triangulate(bowtie)` | `[]` — self-intersection refused silently |
| `clip(bowtie, sq)` | `k=0{}` |
| `is_point_in_polygon((5,5), bowtie)` | **true** (bowtie center counts as inside) |
| `is_point_in_polygon((1,0), collinear)` | false |
| `is_polygon_clockwise(sq)` | false; reversed winding → true; **clip works on either winding** |

### 3.3 Hull/decompose/delaunay/atlas (`geo_trig`)

`convex_hull(concave)` → `n5` **closed ring** (first vertex repeated at end).
`decompose_polygon_in_convex` → `k=3` triangles. `triangulate_delaunay(5pts)` → 15 indices.
`make_atlas([sq, sq, tri])` → **engine ERROR** `Condition "p_rects[i].width <= 0" is true.
at: make_atlas (core/math/geometry_2d.cpp:150)` and `{ "points": [], "size": (0, 0) }` —
the dead seat's call shape is mis-signatured: the bound form takes a **flat
`PackedVector2Array` of rect sizes**, not an Array of polygons. Proven by `atlas_sizes`
(§5): `make_atlas([(20,10),(5,5),(3,3)])` → `{points: [(0,0),(20,0),(20,5)], size: (25,10)}`,
0 B stderr.

### 3.4 Predicates (`geo_pred`)

Boundary-inclusive: `pip` inside=true, outside=false, **edge=true, corner=true**;
`is_point_in_circle((3,4),0,5)` (exactly on circle) → **true**.
`line_intersects_line`/`segment_intersects_segment` → `Vector2` hit or **`<null>`** on miss.
`get_closest_point_to_segment` caps (→`(3,0)`), `…_uncapped` doesn't (→`(13,0)`);
`get_closest_points_between_segments` → `[(5,0),(5,0)]`.
`point_is_inside_triangle` in/out correct. `bresenham_line((0,0),(5,3))` → 6 cells.
`segment_intersects_circle` → **fraction `0.25`** (parametric t, not bool); miss → `−1.0`.

### 3.5 clip → CollisionPolygon2D → falling body (`geo_phys`)

`clip_polygons(sq(0,0,60), sq(0,-30,60))` → k=1 quad fed verbatim to `CollisionPolygon2D.polygon`
on a `StaticBody2D` at y=60; `RigidBody2D` dropped from y=−100: **`rest_y=82.3000`, vel `0,0`,
`self_hit=1`** (the dropped body is found by `intersect_point`). Geometry2D output is directly
authorable into collision geometry — no post-processing needed.

### 3.6 `gravity_scale` (`rb_gravity`) — exact linearity incl. negative

| scale | y@30f | y@60f |
|---|---|---|
| 0.0 | 0.0000 | 0.0000 |
| 1.0 | 124.5675 | 482.2250 |
| 2.0 | 249.1351 | 964.4500 (exactly 2×) |
| **−1.0** | **−124.5675** | **−482.2250** (rises) |

Default gravity here is `980 px/s²` (this project's `project.godot` does not override
`physics/2d/default_gravity`; measured via `total_gravity` in `rb_integrator`).

### 3.7 `center_of_mass` + off-center impulse (`rb_com`)

Impulse `(0,−60)` at offset `(8,0)`:

| body | com | mass | `angular_velocity` |
|---|---|---|---|
| auto | (0,0) read back | 1 | **−12.6794** |
| custom (4,0) | **(4,0) read back** | 1 | **−4.2265** (lever 4, not naive torque-halving — com shift also moves inertia) |
| custom (0,0) | (0,0) | 4 | **−3.1699** (exactly auto ÷ 4) |

`center_of_mass` reads back the set value under `CENTER_OF_MASS_MODE_CUSTOM`.
**`inertia` reads `0.0000` on all three bodies mid-flight** — the property is a write-override;
`0` means auto, exactly the r86 `linear_damp`-reads-`0.0` pin class. The effective inertia is
**not exposed** through the property; `_integrate_forces` `state.inverse_inertia` is the live oracle.

### 3.8 `custom_integrator` (`rb_integrator`) — gravity suppression proven

| body | calls | y@30f | linear_velocity | notes |
|---|---|---|---|---|
| a — normal | 30 | 124.5675 | (0, 478.3405) | `step=0.016667`, `total_gravity=(0,980)`, `coml=(0,0)` |
| b — `custom_integrator=true` | 30 | **0.0000** | **(0,0)** | **built-in gravity skipped entirely**; callback still fires each physics frame |
| c — custom + manual `v += g·step` | 30 | 118.4167 | (0, 473.6668) | manual gravity nearly reproduces built-in (Δy 6.15, Δv 4.67 — one-step timing offset, bounded [I]) |

### 3.9 Offline peer (`mp_offline`)

`OfflineMultiplayerPeer`: `status=2` (CONNECTED), tree `uid=1`, `is_server=true`,
`transfer_mode=2`, `channel=0`. On a bare `SceneMultiplayer` before tree install: `uid=1`.
An offline peer is a functioning authority-of-one — usable as a same-code-path stand-in.

### 3.10 One-process ENet loopback (`mp_loopback`) — full round trip

Server on `127.0.0.1:41777`, client same process; per-branch `SceneMultiplayer` via
`set_multiplayer(api, "/root/branch")`:

```
rc=[0,0] uid_s=1 uid_c=<random 9-10 digit>
order  = ["c_on_srv", "c_conn1", "s_conn<uid>"]            # client sees server first
limb_s = ["ping7:c2s", "ping5:call_local_c"]               # c→s reliable rpc + call_local echo
limb_c = ["ping5:call_local_c", "ping9:s2c"]               # call_local fires locally FIRST, then s→c rpc
disconn= […, "c_srvdisc", "s_disc<uid>"]                   # client notified before server-side signal
frames=4 wait=1                                          # identical across reps
```

Two-way reliable RPC, `call_local` semantics, connect/disconnect ordering — all measured and
deterministic except `uid_c` (random per process; **the only unstable bytes in the whole lane**).

### 3.11 Spawner vs synchronizer (`mp_spawner`) — silent non-replication hazard

- `MultiplayerSpawner` watching `cont` + server-side `add_child(Node2D("spawned_one"))` of a node
  **not** in `_spawnable_scenes` and not passed to `spawn()`: client received **nothing** after
  600 frames — `spawned_name=` empty, `wait=600`, `srv_children=1`, **zero error lines, rc=0**.
  Silent non-replication.
- `MultiplayerSynchronizer` on manually-mirrored `Node2D` twins with
  `replication_config += ":position"`: replicated `position` `(111,222)` in **wait=2 frames** —
  synchronizer replication works without any spawner involvement.

### 3.12 Sprite metadata (`sprite_meta`)

All assignments read back: `region_enabled`, `region_rect`, `hframes/vframes`, `frame`,
`frame_coords` (`frame=5` in 4×2 → `(1,1)`), flips, `offset`, `centered=false`.
Signals: only `frame_changed` fired; `texture_changed` did not (texture was set **before**
connect and region/frame writes don't emit it). `get_rect()` is the **frame** rect: region
8×8 ÷ 4×2 grid → `P:(3,-2) S:(2,4)` honoring `offset` and `centered=false`; a `scale=(-1,1)`
sibling's `get_rect` is unaffected (`P:(-16,-8) S:(32,16)` — scale is transform, not rect).

### 3.13 Sprite flags do not perturb physics (`sprite_phys`)

Four bodies (plain / flipped / regioned / `scale=(-1,-1)` child sprite) dropped 30 frames:
**all at y=74.5675** (= −50 + the same 124.5675 fall distance as `rb_gravity`). `spr_rel` carries
the local transform (neg-scale visible only in `scaled_neg`); body motion is identical.
Sprite metadata is a render-side axis, invisible to the integrator.
Deterministic **engine ERROR** emitted: `Index p_frame = 3 is out of bounds (vframes * hframes = 2).
at: set_frame (scene/2d/sprite_2d.cpp:299)` — the `regioned` variant sets `frame=3` with only
2 frames; the set is refused loudly, the arm continues, err is byte-identical across reps (254 B).

### 3.14 2D lights / occluder vs physics (`light_props`, repaired)

The verbatim leg **hangs**: `pl.range_height = 42.0` hits
`SCRIPT ERROR: Invalid assignment of property or key 'range_height' … on a base object of type
'PointLight2D'. at: _arm_light_props (res://r88_probe.gd:467)` — the property is named `height`
in 4.7.2 (own-props census: `texture,offset,texture_scale,height`). The coroutine aborts,
`quit()` is never reached, SceneTree idles → **rc=124 at 60 s ×3** — the r86-§4.3 class
(GDScript mid-arm death → harness timeout, not a clean failure). Repaired by one token
(`s/range_height/height/`, `r88_probe_fix.gd`, sha256 `d14ae0ad…`), then:

```
pl=[en=true sh=true en2=2.500 ts=1.500 h=42.000 col=(0.5,0.25,0.125,1.0) mask=4 mo=1]
dl=[en=0.750 mask=1]  occ=[closed=true cull=0 mask=2 sdf=true n=3]  cm=[col=(0.2,0.2,0.4,1.0)]
body_y=118.4614  ray_through_occluder=true  occ_cls=LightOccluder2D  occ_is_co=false
```

**`LightOccluder2D` is render-only**: a body falls through occluder geometry, a physics ray
passes, and it is not a `CollisionObject2D`. All PointLight2D/DirectionalLight2D/OccluderPolygon2D/
CanvasModulate properties read back.

### 3.15 Positional audio (`audio_pos`) — headless-null

`AudioStreamWAV` (0.1 s 440 Hz, `LOOP_FORWARD`) on `AudioStreamPlayer2D` + current
`AudioListener2D`: after `play()` and 20 frames — **`playing=false`, `pos=0.000`,
peaks `[−200.00,−200.00,−200.00,−200.00]` dB near; identical far**. Under the Dummy driver no
buffer advances and `playing` clears; attenuation vs listener distance is unmeasurable.
Only negative pins are authorable headless (e.g. `playing==false` after `play()` under Dummy).

### 3.16 Visibility notifier/enabler (`vis_not`) — headless-null

`VisibleOnScreenNotifier2D` on a frozen body teleported +500 px and back:
`on_screen0=false`, `events=[]`, `on_screen_end=false`; `VisibleOnScreenEnabler2D` never
enabled processing (`enabler_proc=false`). **No screen exists headless — `is_on_screen()` is
always false.** The positive arm is structurally unreachable on this host.

---

## 4. Adjacent edge (`r88_edge.gd`, this seat's addition) **[M]**

`polyline` arm — the unprobed sibling family of `geo_*`:

| call | result |
|---|---|
| `offset_polyline(L, +2)` vs `−2` | **byte-identical** `k=1 n7` — sign-insensitive envelope around open lines |
| `offset_polyline(L, 0)` | passthrough `k=1 n3` (input unchanged) |
| `clip_polyline_with_polygon(L, sq)` | `k=2` — the **outside** pieces |
| `intersect_polyline_with_polygon(L, sq)` | `k=1` — the **inside** piece |
| `offset_polyline(closed tri, 2)` | `k=2` (outer rounded + inner contour) |
| `offset_polyline(1-pt, 2)` | `k=1 n4` — degenerates to a square around the point |
| `clip_polyline_with_polygon(1-pt, sq)` | `k=0{}` |

`merge_disjoint` arm: disjoint `merge`→`k=2` (both, vertex order reversed vs input), disjoint
`intersect`→`k=0{}`, disjoint `clip`→subject unchanged, `merge(sq,sq)`→`k=1`, **`clip(sq,sq)`→`k=0{}`**
(self minus self is empty — a clean self-difference pin).

`atlas` arm: **all 8 Array-of-polygons/points call shapes** (squares, triangle, 1-pt, 2-pt,
`[]`, `[empty]`) emit `p_rects[i].width <= 0` (`geometry_2d.cpp:150`) and return
`{points:[], size:(0,0)}`; `atlas_sizes` with the correct flat `PackedVector2Array`-of-sizes
signature returns real packed points, 0 B stderr.

---

## 5. Crash isolation — `offset_polyline(∅)` is a SIGABRT vector **[M]**

The first `polyline` run died mid-arm at the empty-input line. Isolated one call per process:

| call, empty `PackedVector2Array` | rc | stderr |
|---|---|---|
| `offset_polyline(∅, 2.0)` | **134 = SIGABRT ×3** | `std::vector … operator[] … Assertion '__n < this->size()' failed.` inside **Clipper2Lib**; `timeout: the monitored command dumped core` |
| `clip_polyline_with_polygon(∅, sq)` | 0 | `k=0{}`, clean |
| `intersect_polyline_with_polygon(∅, sq)` | 0 | `k=0{}`, clean |

Deterministic across 3 fresh processes (err byte-identical, 377 B). This is the same boundary
class as r85's `joint_make_pin body_b=RID() → SIGSEGV`: an unchecked C++ assert reachable from
script. **Rule for authors: never feed `offset_polyline` an empty array** — a length check in
GDScript is free; the crash is not catchable, not an `ERROR`, and not an rc-1 — it is a core
dump that takes the whole SceneTree down mid-arm.

---

## 6. Falsification list (measured negatives / live instruments)

| id | must-differ input | result |
|---|---|---|
| F1 | arm dispatch must actually switch arms: `--arm geo_ops` in engine-arg position must differ from `-- --arm=geo_ops` | **PASS** — engine-arg position produced 16 distinct outs; post-`--` reproduced the census md5 `4498e228…` exactly |
| F2 | `get_cmdline_args()` vs `get_cmdline_user_args()` distinction is real, not doc-lore | **PASS** — `argprobe.gd`: post-`--` tokens absent from the former, present in the latter |
| F3 | the `rb_integrator` custom-integrator flag must do something | **PASS** — `custom_integrator=true` suppressed gravity (y=0.0000 vs 124.5675) while callbacks still fired ×30 |
| F4 | `gravity_scale` must scale | **PASS** — exact ×2 and ×−1 at both sample frames |
| F5 | `mp_loopback` instability must be *only* the peer id | **PASS** — uid-normalized reps are byte-identical (uniq 3→1); all payload fields stable |
| F6 | spawner instrumentation is live (it *can* replicate when used correctly) | **BOUNDED** — synchronizer replicated `(111,222)` in 2 frames on the same pair of peers; a registered-scene `spawn()` positive control was **not** run (§8) |
| F7 | audio/vis nulls are instrument-live, not broken probes | **BOUNDED** — `audio_has_peak=true`, `is_current()` returned true, `make_current()` didn't error; the Dummy driver and headless screen are the measured cause, consistent with census (`audio_driver=Dummy`, `display=headless`) |
| F8 | `light_props` hang is the `range_height` assignment, not ambient | **PASS** — one-token rename gives rc=0 ×3 with full readback |
| F9 | `make_atlas` is functional when called with its real signature | **PASS** — `atlas_sizes` returned `{points:[(0,0),(20,0),(20,5)],size:(25,10)}` |

---

## 7. Hazards recorded (for the author/battery)

1. **Arm-dispatch trap (the dead seat's killer)**: `OS.get_cmdline_args()` never contains
   post-`--` tokens. Any probe parsing `--arm` must use `OS.get_cmdline_user_args()` (battery
   convention, e.g. `phys2d_events.gd`) or take `--arm <name>` in engine-arg position. A scout
   harness should assert `arm != ""` (or print `arm=` and diff outs) — this failure mode is
   **silent and produces plausible-looking byte-identical output**.
2. **Invalid property assignment → coroutine abort → hang** (`light_props`, rc=124): one bad
   token in a mid-arm setter kills the function, never `quit()`s. Any scout/battery runner
   **must** wrap runs in `timeout`; authors should expect `Invalid assignment of property or
   key` on stderr when a probe hangs.
3. **`offset_polyline(∅)` SIGABRT** (§5): uncatchable Clipper2Lib assert, rc=134, core dump.
   Length-check inputs; never pin the crash itself.
4. **`make_atlas` signature**: flat `PackedVector2Array` of rect *sizes*. An Array of polygons
   (the dead seat's guess) yields `p_rects[i].width <= 0` ERROR + `{points:[], size:(0,0)}` on
   every input tried — including `[]`.
5. **`MultiplayerSpawner` silent non-replication** (§3.11): unregistered `add_child` under
   `spawn_path` produces no client node, no error, forever. Pinned arms must either register
   `_spawnable_scenes`/`spawn()` or assert with a frame cap.
6. **`mp_loopback` peer id is random per process** — normalize `uid_c`-bearing fields or pin
   `uid_s`/`is_server`/order/rpc-log only. `frames=`/`wait=` were stable here (4/1) but are
   scheduling counters — treat as mode candidates, not pins.
7. **Headless-null surfaces**: Dummy audio (`playing=false`, peaks −200 dB) and no screen
   (`is_on_screen()==false` always, enabler never fires). Authorable only as *negative* pins;
   any positive audio-position/visibility row is unfalsifiable on this host.
8. **Sprite `frame` OOB is loud, not clamped** — `Index p_frame = 3 is out of bounds` ERROR +
   refused set. A pinned arm touching `hframes*vframes` bounds needs `expected_errors` budgeted.
9. **`inertia` (and by r86 precedent `linear_damp`/`angular_damp`) read `0.0000` when
   auto** — these properties are write-overrides; effective values live in
   `PhysicsDirectBodyState2D` (`inverse_inertia`, `total_linear_damp`).
10. **`Geometry2D` predicate boundary semantics**: `pip`/`pic` are boundary-inclusive
    (edge/corner/on-circle all true); `segment_intersects_circle` returns a *fraction* (or −1);
    `triangulate` emits a triangle for collinear input but `[]` for bowtie — do not assume
    empty ⇒ error or error ⇒ empty.
11. **`convex_hull` output is a closed ring** (first point repeated): vertex-count pins must
    expect n+1.

## 8. Remaining unknowns / not measured

- **Earlier dead-seat revision** **[I, bounded]**: rc.txt/rc2.txt's `rc=1 ×16` is consistent
  with a parse-error-era script (rc=1 measured for parse failure) — earlier bytes lost.
- **`custom_integrator` Δ** (c vs a: Δy 6.15, Δv 4.67) — likely callback-vs-integrator ordering;
  not dissected.
- **`rb_com` −4.2265** vs naive −6.34: com shift changes lever arm *and* inertia; the split was
  not decomposed analytically.
- **Spawner positive control**: registered `spawnable_scenes`/`spawn()` path untested (F6) —
  the silent non-replication stands; the working path's receipts would strengthen a battery row.
- **`make_atlas` on `[]`** errors too — coercion mechanics of Array→PackedVector2Array not
  dissected **[I]**.
- **MP legs are loopback-only**: one process, one ENet pair, `127.0.0.1`; no cross-process or
  real-NIC replication measured. `WebSocket`/`WebRTC` peers exist in census but were not run.
- **`vis_not`/`audio_pos` positive arms are structurally impossible headless** — not a coverage
  gap, a host constraint; a `--display-server`/Xvfb host could open them.
- **`lsp` absent**: all file:line citations are engine-emitted text.
- **Portability**: all values are this host/build/`--headless`/60 tps/GodotPhysics2D.

## 9. Authorability directives (exact)

1. **Geometry2D pure-function arms are battery-ready as-is** — deterministic, fast (<1 s),
   boundary semantics measured (§3.2, §3.4). Pin `_poly2str`/`_pva2str` shape verbatim.
2. **Author the geometry→collision bridge** (`geo_phys` shape): `clip_polygons` output feeds
   `CollisionPolygon2D` directly; `rest_y=82.3000`, `self_hit=1` are stable pins.
3. **`rb_gravity`/`rb_integrator`/`rb_com` are battery-ready**; pin `inertia reads 0.0000` as
   the auto-override pin, not "inertia is zero".
4. **MP arms pinnable** only after peer-id normalization (or pin `uid_s=1`, `is_server`,
   order list shape, rpc_log contents). Add the registered-scene `spawn()` positive control if
   the spawner arm is authored (F6).
5. **Never author positive `audio_pos`/`vis_not` rows headless** — only negative pins
   (`playing=false`, `events=[]`) are falsifiable here (§7.7).
6. **`light_props` requires the `height` fix**; the repaired leg pins occluder-noncollision
   (`occ_is_co=false`, `ray_through_occluder=true`, `body_y` falls through).
7. **Budget `expected_errors` where the engine is loud**: `geo_trig` atlas-misuse (1 ERROR),
   `sprite_phys` frame-OOB (1 ERROR). Under the corrected signature `make_atlas` is silent.
8. **Keep `offset_polyline(∅)` out of any probe as a payload** — it is a process-killer;
   document only. If an author wants a crash-row, that is a boundary-seat decision with a
   dedicated bounded harness, not a battery cell.
9. **Assert non-empty `arm`** in any new probe; print `arm=` first line so a silent census
   fallback is visible in receipts (the dead seat's 16 identical outs were detectable by md5 —
   `analyze_r88.py` checks this).
10. No git mutation and no commit were performed by this seat.

---

## 10. Evidence index

All under `corpus/live/r88-scout/`; `MANIFEST.sha256` (269 lines) covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| dead seat's probe (verbatim, audited, dispatched correctly) | `proj/r88_probe.gd` | `3584d2292a686a89` |
| repaired copy (`s/range_height/height/` only) | `proj/r88_probe_fix.gd` | `d14ae0ad6de42f40` |
| adjacent-edge probe (this seat) | `proj/r88_edge.gd` | `1fa389ac994cd21a` |
| dead-seat arm runner (fresh ×3, engine-arg `--arm`) | `run_arms.sh` | `fd6fac04c9c7e1b1` |
| fix + edge runner | `run_edge.sh` | `4bcf416417db7455` |
| stability/attribution analyzer | `analyze_r88.py` | `69651dd41654b696` |
| dead-seat surviving receipts (16 census outs + rc traces) | `runs/disc/` | `geo_ops.out`=`78670882d625fc5c` |
| verbatim failure-form reproduction | `runs/repro/eq_form.out` | `78670882d625fc5c` (identical) |
| per-arm receipts ×3 (16 arms + census) | `runs/arms/` | 51 files |
| repaired light_props receipts ×3 | `runs/fix/` | 12 files |
| edge receipts ×3 (7 arms incl. SIGABRT isolation) | `runs/edge/` | 28 files |

Reproduce: `bash run_arms.sh && bash run_edge.sh && python3 analyze_r88.py`.
