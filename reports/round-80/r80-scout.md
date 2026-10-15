# game-dev-2d round 80 — scout (g2d): `RigidBody2D` CCD + the motion-query family, measured and pinned

Seat `SCOUT` (LEAF) | lane `g2d` | round 80 | wave `shokunin-train-20261101-w19` | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`884a4c4`** (*r78 report-last:
adjudicator ADMIT-corr + ledger*). Tracked Godot battery re-run by this seat: **111/111 PASS**
(`corpus/live/r80-scout/runs/20261015T050846740845Z/verdicts.json`) — that count already
includes the r79 author's in-flight `phys2d_events` rows (`M corpus/fixtures/run_battery.py`,
`?? corpus/fixtures/phys2d_events.gd`; their `M`/`??` state is untouched by this seat).

**No git mutation, no tracked file read-modified, no subagent.** Writes are this report and
`corpus/live/r80-scout/**` only. `reports/round-79/` was not touched (read-only reference).
`corpus/fixtures/` is read-only per the brief — nothing under it was written, copied over, or
re-generated; the battery was only *executed* with `--runs` pointed at my scratch dir.

**Backend scope (census, `corpus/live/r80-scout/runs/engine-census.txt`, fresh process):**
`physics/2d/physics_engine = DEFAULT`, hint `DEFAULT,GodotPhysics2D,Dummy` — **there is no
Jolt-2D backend in this build**. The 3-D hint in the same project *does* list
`DEFAULT,Jolt Physics,GodotPhysics3D,Dummy`, so Jolt is installed but is a **3-D-only**
backend here; every 2-D row below is **GodotPhysics2D** and nothing in this report claims a
Jolt-2D measurement. `physics/common/physics_ticks_per_second = 60`,
`physics/2d/run_on_separate_thread = false` (default; the threaded twin flips it to `true`).
Project carries no physics overrides; engine defaults apply (measured in-probe:
`default_linear_damp = 0.1`, `default_angular_damp = 1.0` — the angular damp is load-bearing
for `ccd_spin`'s pose cycle).

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this session and no
GDScript language server is installed. Semantic carriers are (a) fresh-process execution
receipts, (b) the tracked harness's **own** `classify_process` predicate extracted verbatim
from `corpus/fixtures/run_battery.py` lines 215–233 (sha256 `615d332ed428db66…` of the
extracted block; `run_arms.py` `exec`s the extracted source, never re-implements it), (c)
line-exact engine error anchors in the receipts. No cold-start empty result is recorded as
absence; every cited arm ran to rc=0 inside an 8 s bound.

**Legend:** **[M]** measured (fresh process, ×3 byte-stable unless stated); **[I]** inference;
**[A]** ablation (the pinned row was shown to FAIL when the pin is removed/flipped).

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r80-scout/runs` | 0 | **111/111 PASS** (`runs/20261015T050846740845Z/verdicts.json`) — host/build sanity on the tracked lattice incl. the r79 author's in-flight rows |
| 2 | `… corpus/live/r80-scout/run_arms.py --mode discover` | 0 | 28 arms, one fresh Godot per arm — `arms-discover.json`, the receipts the frozen pins were transcribed from |
| 3 | `… run_arms.py --mode verify --reps 3` | 0 | **28 rows × 3 reps = 84 processes; 28/28 PASS and `stable_bytes=true` for all 28**, ablation matrix clean — `arms-verify.json` carrying per-rep stdout/stderr, engine `at:` anchors, and merged-stream sha256 |
| 4 | `godot --headless --path proj_thr --script res://phys2d_motion.gd -- --arm=<a>` ×7 arms | 0 | threaded twin `proj_thr` (`2d/run_on_separate_thread=true`): **6/7 byte-identical to DEFAULT**; `bds_windows` differs only at the process-time fetch — `arms-thr.txt` |
| 5 | `godot --headless --path proj --script /tmp/engine_census.gd` | 0 | `runs/engine-census.txt` — engine/hint census (backend scope block above) |
| 6 | `grep`/`read` census of `corpus/fixtures/` for the motion family | 0 | HEAD has **0** hits for `body_test_motion`, `move_and_collide`, `test_move`, `cast_motion`, `collide_shape`, `intersect_shape`, `get_rest_info`, `continuous_cd`, `get_colliding_bodies`, `body_get_direct_state` — the whole family is unarmed territory |

**~100 cited fresh Godot processes** (28 discover + 84 verify + 7 threaded + census), each arm
in its own process, 8 s bound.

**Harness fidelity.** Every arm runs in the battery's exact launch shape —
`godot --headless --path <scratch> --script res://phys2d_motion.gd -- --arm=<name>`, merged
stdout+stderr, judged by the production `classify_process` extracted verbatim (never
re-implemented). The scratch `proj/` is a copy of `corpus/fixtures/` minus `run_battery.py`
plus `phys2d_motion.gd` at the root — i.e. exactly where the author's fixture lands and
exactly what the battery copies per-case. `proj_thr/` is the same copy plus one key
(`[physics] 2d/run_on_separate_thread=true`).

---

## 1. The r80 arm — 28 cells, verbatim-armable

One new fixture `corpus/fixtures/phys2d_motion.gd` (scratch source:
`corpus/live/r80-scout/proj/phys2d_motion.gd`, 876 lines, sha256
`ddb5921d4aff5f37…`), one `--arm=` per cell, all `expected_exit = 0`, no cell is a crash.
**The ready-to-paste `CASES` rows and `expected_errors` entries are in
`corpus/live/r80-scout/author-rows.py.txt` and reproduced at §1.4.** Insert ahead of the
crash/descendant tail exactly like the r79 block did (the `sleep 8` orphan window still
forbids rows between `descendant_pipe_detached_control` and the meta probes).

Shared scene grammar (probe constants): `WALL_X=100`, thin walls `4×400` (face at x=98),
`BULLET_R=8` circle RigidBody2D, `CharacterBody2D` r=10. All runs headless, 60 tps,
`gravity_scale=0` on bullets, `can_sleep=false`, `contact_monitor`+`body_entered` wired on
the CCD bullets. Coordinates are deterministic; every signature is an exact full-line pin.

### 1.1 Class table — what each row pins (Q1: `RigidBody2D.continuous_cd`)

| # | arm | class | decisive witness keys (measured, ×3 stable) | `expected_errors` |
|---|---|---|---|---|
| 1 | `ccd_ladder` | **lattice-phase tunneling** | v/step = v/60 px ∈ {10, 19.17, 20, 33.3, 40, 50, 60}; `d_cross=[0,0,0,0,1,0,1]` — disabled tunnels at 2400 & 3600 but **stops at 3000** (lands inside the wall); `r_cross` all-0 (ray catches every speed, stops x=90.16); `s_cross` **byte-identical to disabled** | — |
| 2 | `ccd_gap` | **cast_ray ≫ cast_shape (counterintuitive)** | 16×16 box, 12px slot, v=2400: `d_cross=1 d_hit=0`; **`r_cross=0 r_hit=2`** — the center ray *was* stopped by the slot's corner faces; `s_cross=1 s_hit=0` — cast-shape tunneled clean | — |
| 3 | `ccd_edge` | **cast_shape misses a real edge clip** | circle r8 center ray 4px above a 4×10 wall top; swept overlap exists (y∈[6,10] band) at intermediate poses; `d/r/s_cross=[1,1,1]`, `*_hit=0` for all three | — |
| 4 | `ccd_spin` | **absence + tolerated end-overlap** *(weak cell — see §6)* | bar 8×128, ω=90°/step, wall 20×4@(40,+40): `*_hit=0` in all modes, `endposes=[308.05]×3`, **`endpose_overlap=[1,1,1]`** — every mode's rest pose overlaps the wall per a motion-0 `body_test_motion`, yet no entry fired | — |

### 1.2 Class table — Q2/Q3: `body_test_motion` / `move_and_collide` / `test_move`

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 5 | `btm_from` | **`from` honored literally** | body node at (0,1000), wall@200 y∈[-200,200]: `no_from` hit `pt=(198,0)` (query ran at origin — resolved by #9); `with_from=(0,1000)` → `hit=false travel=(400,0)` | — |
| 6 | `btm_hit` | **clean hit fields** | motion (200,0) vs wall face 98: `travel=(87.5,0)` `rem=(112.5,0)` `pt=(98,0)` `n=(-1,0)` `depth=0.2813` `sf=0.4375 uf=0.4414` — `remainder = motion − travel`; `sf<uf` with the margin band between | — |
| 7 | `btm_embed` | **recovery always reported; flag inert** | embedded 8px start, 5 cells (±50px motion, separation-ray): all `hit=true travel=(-6.9633,0)` `sf=0 uf=0` `depth=1.0368` — negative travel = depenetration, identical with `recovery_as_collision` true/false and `collide_separation_ray` | — |
| 8 | `btm_margin` | **margin inflates `depth`, not `travel`** | margin {0, 0.08, 1, 4}: `travel/fractions/pt` **invariant**; `depth = 0.2813 + margin` (0.2813 → 0.3613 → 1.2813 → 4.2813) | — |
| 9 | `btm_from2` | **unset-`from` = `Transform2D()` origin** (discriminator) | bodies at (0,3000) and (0,3600) with *no* writes, plus a server-teleported (0,4200): every unset-`from` query hit the **y=0** wall (`pt=(198,0)`); explicit `from=identity` behaves identically; `from=(0,3600)` → miss. Body/server/node pose is **never** consulted | — |
| 10 | `btm_recflag` | **`recovery_as_collision` inert (isolator)** | embedded start + `motion=ZERO` and `motion=(0.01,0)`: `zero_off`/`zero_on`/`tiny_off`/`tiny_on` all `hit=true travel=(-6.9633,0)` `sf=0 uf=0` — the flag changes nothing observable | — |
| 11 | `mac_hit` | **`move_and_collide` = btm + position write** | same numbers as #6 (depth 0.3613 = default margin 0.08); `bodypos=(87.5,0)` — moved | — |
| 12 | `mac_miss` | **miss → null + full travel** | `col=null bodypos=(60,0)` | — |
| 13 | `tm_hit` | **`test_move` pure twin** | `ret=true`, populated `KinematicCollision2D` identical to #11, `bodypos=(0,0)` — no movement | — |
| 14 | `mac_test_only` | **`test_only` side-effect-free, both tiers** | col1 hit fields full; `pos_after_test=(0,0)` **and `srv_after_test=(0,0)`** (server read via `body_get_state`); follow-up real call → `pos_after_real=(87.5,0)` | — |
| 15 | `mac_nodecomp` | **no auto-decomposition/slide** | diagonal (200,−200) into an L-wall: single call `travel=(87.5,−87.5)`, stops at first contact `pos=(98,−88.28)`; `remainder` is the *unconsumed* vector, not slid | — |
| 16 | `mac_chain` | **chaining is caller-managed** | `remainder.slide(normal)` → second call hits the floor `n=(0,1)` `travel=(0,−10.33)`, L-corner `(87.5,−97.83)`; third call `null` | — |
| 17 | `mac_maxcol` | **arity = 4, no `max_collisions`** | `callv` with 5 args → `callv5=null`, rc=0, body unmoved | `Method expected 4 argument(s), but called with 5.` |
| 18 | `mac_rigid` | **RigidBody2D honors `move_and_collide`; server adopts pose** | miss lane: `col=null` moved to (60,0), `srv_late=(60,0)` persists ×3 frames; hit lane: full `KinematicCollision2D`, `hpos_late=(87.5,900)` = `hsrv_late` — survives the server-driven rigid sync that r79 showed *reverting* raw node writes | — |
| 19 | `mac_embed` | **embedded recovery + margin arg-vs-prop inert** | three bodies, `rec_off`/`rec_on`/`safe_margin=5 property` all `travel=(-7.0294,0)` → land at `pos=(88.9706,*)` — recovery ejects to face+margin; flag and margin channel show no observable difference here | — |

### 1.3 Class table — Q4/Q5: `PhysicsDirectSpaceState2D` + contact/body-state windows

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 20 | `dss_motion` | **split: `cast_motion`+`get_rest_info` sweep; `collide_shape`+`intersect_shape` pose** | `cm=[0.44921875, 0.453125]` (two fractions) toward wall; `cm_away`/`cm_zero=[1,1]`; `cs_n=2` (point pairs), `is_n=1`; `ri={pt=(98,0), n=(-1,0), lv=(0,0), keys=[collider_id,linear_velocity,normal,point,rid,shape]}`; **`ri_zero={}`** — zero-motion control proves the hit was swept | — |
| 21 | `dss_embed` | **`cast_motion` blind to initial overlap** | embedded start: `cm_toward=cm_away=[1,1]` — free path reported *while penetrating*; `cs_n=2 pts=[(88,0),(102,0)]`, `ri={pt=(102,0), n=(1,0)}` still report the overlap | — |
| 22 | `dss_shapes` | **return shapes; `max_results` counts contacts not points** | `intersect_ray` hit `{collider,collider_id,normal,position,rid,shape}` / miss `{}`; `rest_info` on a mover exposes `linear_velocity=(119.6003,0)`; `intersect_shape[0]` `{collider,collider_id,rid,shape}`; `collide_shape` `cap1=2` = `full=2` — one contact = one point *pair* | — |
| 23 | `dss_purity` | **query params are read-only** | `equal=true` — transform/motion/margin/mask/flags/exclude identical before and after all four methods | — |
| 24 | `dss_wrongarg` | **typed refusal, no crash** | wrong-typed/null query objects → `is=0 cm=[] ri={} cs=0 is_null=0 ray_null={} pt_null=0`, rc=0 | `Required object "rp_shape_query" is null.` + `"rp_ray_query"` + `"rp_point_query"` (anchors `physics_server_2d.cpp:{388,408,423,441,342,363}`) |
| 25 | `cont_windows` | **contact materialization windows** | `entry_f=4`: `in_cb=[2,1]` populated at callback; `pp_entry`/`proc_entry=[2,1]`; **`in_exit_cb=[0,1]`** — `get_contact_count()` already 0 while `get_colliding_bodies()` still lists the exiter; `pp_exit`/`proc_exit=[0,0]` | — |
| 26 | `cont_cap` | **count = contact points, array = bodies; cap truncates** | `max_contacts_reported=1` → `count=1 arr=1`; `max=4` corner wedge → `count=4 arr=2` (2 bodies × 2 points) | — |
| 27 | `bds_windows` | **`body_get_direct_state` windows** | `oop=obj cnt=0` — out-of-phase fetch returns an object reading the pre-contact snapshot (not null, not refused on DEFAULT); `in_cb`/`in_phase`/`proc` → `cnt=2`; `_integrate_forces` `step0 count=0` → `count=2` after landing | — |
| 28 | `cont_persist` | **array clears next frame, no linger** | `exit_f=5`: `seq=[[5,1],[6,0],[7,0],…]` — the exiter lingers exactly one window then empties | — |

### 1.4 The verbatim rows

```python
# --- CASES rows (append to the CASES list in corpus/fixtures/run_battery.py; ---
# --- insert ahead of the crash/descendant tail, same constraint as the r79 block) ---
    ("phys2d_motion_ccd_ladder", "phys2d_motion.gd", ["--arm=ccd_ladder"], 0,
     "PASS phys2d_motion ccd_ladder vels=[600.0, 1150.0, 1200.0, 2000.0, 2400.0, 3000.0, 3600.0] entries=17 d_cross=[0, 0, 0, 0, 1, 0, 1] d_x=[90.3, 90.3, 90.3, 90.3, 1169.494, 90.3, 1754.241] d_vx=[0.0, 0.0, 0.0, 0.0, 2282.856, 0.0, 3424.283] d_ccd=0 r_cross=[0, 0, 0, 0, 0, 0, 0] r_x=[90.16, 90.16, 90.16, 90.16, 90.16, 90.16, 90.16] r_vx=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] r_ccd=1 s_cross=[0, 0, 0, 0, 1, 0, 1] s_x=[90.3, 90.3, 90.3, 90.3, 1169.494, 90.3, 1754.241] s_vx=[0.0, 0.0, 0.0, 0.0, 2282.856, 0.0, 3424.283] s_ccd=2"),
    ("phys2d_motion_ccd_gap", "phys2d_motion.gd", ["--arm=ccd_gap"], 0,
     "PASS phys2d_motion ccd_gap v=2400 box16x16 gap12 d_cross=1 d_hit=0 d_x=1169.494 r_cross=0 r_hit=2 r_x=90.157 s_cross=1 s_hit=0 s_x=1169.494"),
    ("phys2d_motion_ccd_spin", "phys2d_motion.gd", ["--arm=ccd_spin"], 0,
     "PASS phys2d_motion ccd_spin w=90deg_per_step bar8x128 wall20x4@(40,+40) d_hit=0 d_rot=308.05 d_ccd=0 r_hit=0 r_rot=308.05 r_ccd=1 s_hit=0 s_rot=308.05 s_ccd=2 endposes=[308.05, 308.05, 308.05] endpose_overlap=[1, 1, 1]"),
    ("phys2d_motion_ccd_edge", "phys2d_motion.gd", ["--arm=ccd_edge"], 0,
     "PASS phys2d_motion ccd_edge v=2400 circle8@y14 wall4x10@[0,10] d_cross=1 d_hit=0 d_pos=(1169.4938,814.0000) r_cross=1 r_hit=0 r_pos=(1169.4938,1614.0000) s_cross=1 s_hit=0 s_pos=(1169.4938,2414.0000)"),
    ("phys2d_motion_btm_from", "phys2d_motion.gd", ["--arm=btm_from"], 0,
     "PASS phys2d_motion btm_from body@(0,1000) wall@200 no_from[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] with_from[hit=false travel=(400.0000,0.0000) rem=(0.0000,0.0000)] bodypos=(0.0000,1000.0000)"),
    ("phys2d_motion_btm_hit", "phys2d_motion.gd", ["--arm=btm_hit"], 0,
     "PASS phys2d_motion btm_hit hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(0.0000,0.0000)"),
    ("phys2d_motion_btm_embed", "phys2d_motion.gd", ["--arm=btm_embed"], 0,
     "PASS phys2d_motion btm_embed rec_off[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] rec_on[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] rec_on_sepray[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] away_off[hit=true travel=(-6.9633,0.0000) rem=(-50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] away_on[hit=true travel=(-6.9633,0.0000) rem=(-50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D]"),
    ("phys2d_motion_btm_margin", "phys2d_motion.gd", ["--arm=btm_margin"], 0,
     "PASS phys2d_motion btm_margin m0.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m0.08[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m1.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m4.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=4.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D]"),
    ("phys2d_motion_btm_from2", "phys2d_motion.gd", ["--arm=btm_from2"], 0,
     "PASS phys2d_motion btm_from2 n1[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] n2[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] srv_tele[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] ident_from[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] with_from3600[hit=false travel=(400.0000,0.0000) rem=(0.0000,0.0000)] b1pos=(0.0000,3000.0000) b3pos=(0.0000,0.0000)"),
    ("phys2d_motion_btm_recflag", "phys2d_motion.gd", ["--arm=btm_recflag"], 0,
     "PASS phys2d_motion btm_recflag zero_off[hit=true travel=(-6.9633,0.0000) rem=(0.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] zero_on[hit=true travel=(-6.9633,0.0000) rem=(0.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] tiny_off[hit=true travel=(-6.9633,0.0000) rem=(0.0100,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] tiny_on[hit=true travel=(-6.9633,0.0000) rem=(0.0100,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D]"),
    ("phys2d_motion_mac_hit", "phys2d_motion.gd", ["--arm=mac_hit"], 0,
     "PASS phys2d_motion mac_hit travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(87.5000,0.0000)"),
    ("phys2d_motion_mac_miss", "phys2d_motion.gd", ["--arm=mac_miss"], 0,
     "PASS phys2d_motion mac_miss col=null bodypos=(60.0000,0.0000)"),
    ("phys2d_motion_tm_hit", "phys2d_motion.gd", ["--arm=tm_hit"], 0,
     "PASS phys2d_motion tm_hit ret=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(0.0000,0.0000)"),
    ("phys2d_motion_mac_test_only", "phys2d_motion.gd", ["--arm=mac_test_only"], 0,
     "PASS phys2d_motion mac_test_only col1=travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos_after_test=(0.0000,0.0000) srv_after_test=(0.0000,0.0000) col2=hit pos_after_real=(87.5000,0.0000)"),
    ("phys2d_motion_mac_nodecomp", "phys2d_motion.gd", ["--arm=mac_nodecomp"], 0,
     "PASS phys2d_motion mac_nodecomp travel=(87.5000,-87.5000) rem=(112.5000,-112.5000) pos=(98.0000,-88.2812) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(87.5000,-87.5000)"),
    ("phys2d_motion_mac_chain", "phys2d_motion.gd", ["--arm=mac_chain"], 0,
     "PASS phys2d_motion mac_chain h0[t=(87.5000,-87.5000) r=(112.5000,-112.5000) n=(-1.0000,0.0000) pos=(87.5000,-87.5000)] h1[t=(0.0000,-10.3271) r=(0.0000,-102.1729) n=(0.0000,1.0000) pos=(87.5000,-97.8271)] n2=null pos=(87.5014,-97.8271)"),
    ("phys2d_motion_mac_maxcol", "phys2d_motion.gd", ["--arm=mac_maxcol"], 0,
     "PASS phys2d_motion mac_maxcol callv5=null bodypos=(0.0000,0.0000)"),
    ("phys2d_motion_mac_rigid", "phys2d_motion.gd", ["--arm=mac_rigid"], 0,
     "PASS phys2d_motion mac_rigid col=null pos_now=(60.0000,0.0000) pos_late=(60.0000,0.0000) srv_late=(60.0000,0.0000) hitcol=travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,900.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D hpos_now=(87.5000,900.0000) hpos_late=(87.5000,900.0000) hsrv_late=(87.5000,900.0000)"),
    ("phys2d_motion_mac_embed", "phys2d_motion.gd", ["--arm=mac_embed"], 0,
     "PASS phys2d_motion mac_embed rec_off[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,0.0000)] rec_on[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,600.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,600.0000)] prop5_argdefault[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,1200.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,1200.0000)]"),
    ("phys2d_motion_dss_motion", "phys2d_motion.gd", ["--arm=dss_motion"], 0,
     "PASS phys2d_motion dss_motion cm=[0.44921875, 0.453125] cm_away=[1.0, 1.0] cm_zero=[1.0, 1.0] cs_n=2 is_n=1 ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(98.0000,0.0000) n=(-1.0000,0.0000) lv=(0.0000,0.0000) cls=null} ri_zero={}"),
    ("phys2d_motion_dss_embed", "phys2d_motion.gd", ["--arm=dss_embed"], 0,
     "PASS phys2d_motion dss_embed cm_toward=[1.0, 1.0] cm_away=[1.0, 1.0] cs_n=2 cs_pts=[(88.0, 0.0), (102.0, 0.0)] is_n=1 ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(102.0000,0.0000) n=(1.0000,0.0000) lv=(0.0000,0.0000) cls=null}"),
    ("phys2d_motion_dss_shapes", "phys2d_motion.gd", ["--arm=dss_shapes"], 0,
     "PASS phys2d_motion dss_shapes ray_hit={keys=[\"collider\", \"collider_id\", \"normal\", \"position\", \"rid\", \"shape\"] cls=StaticBody2D pos=(98.0000,0.0000) n=(-1.0000,0.0000)} ray_miss={} ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(303.9900,-8.0000) n=(0.0000,-1.0000) lv=(119.6003,0.0000) cls=null} is_n=1 is0={keys=[\"collider\", \"collider_id\", \"rid\", \"shape\"] cls=RigidBody2D} cs_full=2 cs_cap1=2"),
    ("phys2d_motion_dss_purity", "phys2d_motion.gd", ["--arm=dss_purity"], 0,
     "PASS phys2d_motion dss_purity equal=true before=[[X: (0.955337, 0.29552), Y: (-0.29552, 0.955337), O: (5.0, 7.0)], (150.0, -40.0), 0.5, 4294967295, true, false, []] after=[[X: (0.955337, 0.29552), Y: (-0.29552, 0.955337), O: (5.0, 7.0)], (150.0, -40.0), 0.5, 4294967295, true, false, []]"),
    ("phys2d_motion_dss_wrongarg", "phys2d_motion.gd", ["--arm=dss_wrongarg"], 0,
     "PASS phys2d_motion dss_wrongarg is=0 cm=[] ri={  } cs=0 is_null=0 ray_null={  } pt_null=0"),
    ("phys2d_motion_cont_windows", "phys2d_motion.gd", ["--arm=cont_windows"], 0,
     "PASS phys2d_motion cont_windows entry_f=4 exit_f=6 in_cb=[2, 1] pp_entry=[2, 1] proc_entry=[2, 1] in_exit_cb=[0, 1] pp_exit=[0, 0] proc_exit=[0, 0]"),
    ("phys2d_motion_cont_cap", "phys2d_motion.gd", ["--arm=cont_cap"], 0,
     "PASS phys2d_motion cont_cap capped=[count=1 arr=1] uncapped=[count=4 arr=2 cls=StaticBody2D,StaticBody2D]"),
    ("phys2d_motion_bds_windows", "phys2d_motion.gd", ["--arm=bds_windows"], 0,
     "PASS phys2d_motion bds_windows oop=obj cnt=0 in_cb={ \"obj\": true, \"count\": 2 } in_phase=obj cnt=2 proc=obj cnt=2 integ_first={ \"count\": 0, \"lv\": (0.0, 65.33334) } integ_last={ \"count\": 2, \"lv\": (0.0383, -0.006104) }"),
    ("phys2d_motion_cont_persist", "phys2d_motion.gd", ["--arm=cont_persist"], 0,
     "PASS phys2d_motion cont_persist entry_f=4 exit_f=5 seq[frame,size]=[[5, 1], [6, 0], [7, 0], [8, 0], [9, 0], [10, 0], [11, 0]]"),

# --- expected_errors entries (merge into the expected_errors map inside execute()) ---
                "phys2d_motion_mac_maxcol": ("ERROR: Error calling method from 'callv': 'CharacterBody2D::move_and_collide': Method expected 4 argument(s), but called with 5.",),
                "phys2d_motion_dss_wrongarg": ("ERROR: Required object \"rp_shape_query\" is null.",
                                         "ERROR: Required object \"rp_ray_query\" is null.",
                                         "ERROR: Required object \"rp_point_query\" is null.",),
```

---

## 2. Fail-closed evidence (the pins are load-bearing) **[A]**

`arms-verify.json` `verdict=PASS`, `bad=[]`, 28 rows. Per row: `rc=[0,0,0]`,
`verdicts=[PASS,PASS,PASS]`, `stable_bytes=true` — all three reps byte-identical on merged
stdout+stderr (sha256 `merged_sha256` per rep recorded). Ablation matrix, judged by the
**production** `classify_process` (extracted `run_battery.py:215-233`, sha256
`615d332ed428db66…`):

| ablation | expected verdict | 28/28 observed |
|---|---|---|
| signature dropped (`PASS phys2d_motion __absent__`) | FAIL | FAIL on all 28 |
| `expected_exit` flipped 0→1 | FAIL | FAIL on all 28 |
| `expected_errors` whitelist dropped | FAIL *iff the row emits errors* | FAIL on exactly `mac_maxcol` and `dss_wrongarg`; PASS on the 26 error-free rows (whitelist is vacuous there — correct semantics) |
| clean control | PASS | PASS on all 28 |

The error-bearing rows are therefore **three-clause** pins (exit + signature + error
whitelist); the other 26 are two-clause. Engine `at:` anchors persisted per rep:
`mac_maxcol` → `at: callv (core/object/object.cpp:763)`;
`dss_wrongarg` → `at: _intersect_shape/_cast_motion/_get_rest_info/_collide_shape
(servers/physics_2d/physics_server_2d.cpp:{388,408,441,423})` + `_intersect_ray:342` +
`_intersect_point:363`. The `dss_wrongarg` process emits **7** `ERROR:` lines (4×
`rp_shape_query`, one per shape method) — the 3 distinct `ERROR:`-line strings cover all 7
under the production prefix classifier; raw stderr is in the receipt for the author to
tighten if desired.

---

## 3. Threading (twin, and it sharpens the r77/r88 gate map) **[M]**

`proj_thr` = `proj` + `[physics] 2d/run_on_separate_thread=true`. Seven arms re-run, receipts
in `arms-thr.txt`:

| arm | threaded result |
|---|---|
| `cont_windows`, `dss_motion`, `ccd_ladder`, `mac_test_only`, `btm_from2`, `btm_recflag` | **byte-identical** to the DEFAULT pin |
| `bds_windows` | `oop=obj cnt=0` unchanged (fetch issued before the first step — thread not yet owning state); `in_cb`/`in_phase` unchanged (count=2); **`proc=null cnt=-2`** — the `process_frame`-time `body_get_direct_state` is now **refused**: `ERROR: Body state is inaccessible right now, wait for iteration or physics process notification.` `at: body_get_direct_state (modules/godot_physics_2d/godot_physics_server_2d.cpp:1005)` |

So the interior-window lattice of this arm is threading-invariant, and the one difference is
the already-known direct-body-state phase gate: on a separate physics thread, a
`_process`-time fetch returns `null` + error, while the same fetch on DEFAULT silently
returns the last completed snapshot (which is why `cnt=0` pre-contact, `cnt=2` post-contact).
`space_get_direct_state` + shape/ray queries fetched *inside* the physics-phase continuation
answer identically on both schedulings — the space-state handle is phase-bound, not
thread-bound, at this call site.

---

## 4. Headline measured findings

1. **Unset `from` on `body_test_motion` resolves to `Transform2D()` — the world origin —
   not the body's transform** **[M]**. `btm_from2` discriminates three candidate referents:
   bodies at (0,3000) and (0,3600) (node-init, no writes, empty lanes at their y) each hit
   the wall at `pt.y=0`; a **server-teleported** body at (0,4200) also hit `pt.y=0`
   (so it is neither node pose nor server pose); explicit `from=Transform2D()` reproduces
   the same origin query; only an explicit non-identity `from=(0,3600)` moved the query.
   Practical rule measured here: *always* set `params.from`; "unset" is not shorthand for
   "the body".
2. **`recovery_as_collision` is inert in GodotPhysics2D across all 9 measured embedded
   cells** **[M]**: `btm_embed` (±50 px motion, separation-ray variant), `btm_recflag`
   (zero- and tiny-motion isolators), `mac_embed` (flag + `safe_margin` property cell).
   Every embedded start returns `hit=true` with negative recovery travel
   (`-6.9633`/`-7.0294` px, `sf=uf=0`) regardless of the flag — recovery is always
   reported as a hit in this build/geometry. The flag may gate a channel no geometry here
   observes; the armable claim is the measured invariance, not "the flag does nothing
   anywhere".
3. **RigidBody2D honors `move_and_collide`, and the server adopts the resulting pose**
   **[M]**: miss moves it `(60,0)` and `body_get_state` still shows `(60,0)` three frames
   later; hit stops it at `(87.5,900)` with a full `KinematicCollision2D`, server pose
   identical. Contrast r79: a *raw* node position write on a `RigidBody2D` inside the
   callback window is silently reverted by the server-driven sync — `move_and_collide`
   does not suffer that revert because it writes through the body-test path the server
   itself executes.
4. **In 2-D, `get_rest_info` honors `motion` (sweep), splitting the family differently
   than r88 measured for 3-D** **[M]**: `ri` returns a swept contact
   (`pt=(98,0) n=(-1,0)` incl. `linear_velocity`) while `collide_shape`/`intersect_shape`
   act as pose queries and `cast_motion` returns `[safe,unsafe]` fractions. The
   `ri_zero={}` control proves the rest-info hit came from the sweep, not the pose.
   Whether r88's pose-query characterization for 3-D `get_rest_info` is a real
   backend/dimension difference or a geometry artifact of that probe is an open question
   (§6) — the 2-D measurement here is unambiguous.
5. **`get_colliding_bodies()` lags `get_contact_count()` at the exit window** **[M]**:
   inside `body_exited` the count is already 0 but the array still contains the exiter
   (`[0,1]`); the array is empty by the next physics frame. Entry is symmetric-populated
   at callback time (`[2,1]`).

---

## 5. Threading + stability summary

- 28/28 rows `stable_bytes=true` across 3 fresh processes each (merged stdout+stderr
  sha-identical), 8 s bound, no flaky rep in 84 processes.
- 6/7 threaded-twin arms byte-identical; the single delta is the engineered
  `body_get_direct_state` phase gate (§3).
- Tracked battery 111/111 on the same host/build within the same session.

## 6. Falsification list / surprises (measured negatives)

| # | plausible claim | measured result | witness |
|---|---|---|---|
| F1 | `cast_shape` catches what `cast_ray` misses | **False here, twice**: ladder `s_cross` ≡ `d_cross` exactly; gap slot stops the ray (`r_hit=2`) while `cast_shape` tunnels clean | `ccd_ladder`, `ccd_gap` |
| F2 | `cast_shape` catches off-center swept overlap | **False**: a real edge clip (swept overlap band 4px) tunnels in all three modes | `ccd_edge` |
| F3 | tunneling is a monotonic speed threshold | **False**: 2400 (40px/step) and 3600 (60px/step) tunnel while 3000 (50px/step) *lands inside* the wall and stops — discrete-mode crossing is a lattice-phase artifact | `ccd_ladder` |
| F4 | unset `body_test_motion.from` = body transform | **False**: unset ≡ `Transform2D()` origin, body pose never consulted | `btm_from2` |
| F5 | `recovery_as_collision` changes reporting | **No observable effect** in 9 embedded cells; recovery is always `hit=true` | `btm_embed`, `btm_recflag`, `mac_embed` |
| F6 | `move_and_collide` auto-decomposes/slides | **False**: stops at first contact; `remainder` is unconsumed motion; sliding is the caller's `slide()` + re-call loop | `mac_nodecomp`, `mac_chain` |
| F7 | `move_and_collide` takes a `max_collisions` arg | **False**: arity is exactly 4; 5th arg → typed callv error + null | `mac_maxcol` |
| F8 | `cast_motion` detects initial overlap | **False**: embedded start returns `[1,1]` both directions | `dss_embed` |
| F9 | `collide_shape` `max_results` caps *points* | **False**: caps contacts; `cap1` still returns 2 points (one pair) | `dss_shapes` |
| F10 | `get_colliding_bodies` empty by the exit callback | **False**: count=0 while the exiter is still listed `[0,1]` | `cont_windows` |
| F11 | `get_rest_info` ignores `motion` in 2-D (r88-3-D analog) | **False for 2-D**: rest info consumed the sweep; zero-motion control returned `{}` | `dss_motion` |
| F12 | RigidBody2D can't use `move_and_collide` / write won't stick | **False**: miss and hit both land and persist on the server tier | `mac_rigid` |

## 7. Remaining unknowns / not measured

- **`ccd_spin` is a weak cell, kept pinned but not claim-bearing.** All three modes end at
  identical rotation 308.05° with `endpose_overlap=[1,1,1]` (a motion-0
  `body_test_motion` reports overlap at the *rest* pose) yet no `body_entered` ever fired.
  Either the solver tolerates resting interpenetration without a contact event, or the
  wall/band geometry makes the overlap an edge-graze the monitor doesn't report. It
  *cannot* currently support a rotational-CCD claim either direction; a sharper arm needs
  a swept-only intersection with a clean non-overlapping sampled pose (the angular damp
  1.0/frame also drifts ω −1.6%/step, bending the pose schedule — confound noted).
- **`cast_shape` ≡ `disabled` on the ladder/gap is surprising** and likely an
  implementation detail of GodotPhysics2D's shape-CCD for these box/circle-vs-flat-wall
  cases, not a universal statement that `cast_shape` never differs from `disabled`. A
  convex-vs-convex or capsule geometry may split them; not measured.
- **`recovery_as_collision` semantics unresolved**: shown inert, not shown useless — a
  channel it might gate (e.g. collider metadata on the recovery hit, `separation-ray`
  interplay at shallow overlap) wasn't observed to differ.
- **CCD velocity ceilings/shape families**: only circle r8, box 16×16, bar 8×128 vs 4px
  and 20×4 walls at 10–60 px/step. No polygons, capsules, tilemaps, or multi-shape bodies.
- **`move_and_collide` on `RigidBody2D` under load**: measured with `gravity_scale=0` and
  zero velocity; behavior while the integrator is actively driving the body (forces,
  velocity) is unknown — the server could re-impose dynamics next step.
- **Jolt-2D**: absent from this build's 2-D hint; no claim made or possible here.
- **Contact counts >4 / `max_contacts_reported` boundary off-by-one**: only caps 1 and 4
  measured.
- **`_integrate_forces` state window under `separate_thread`**: covered only indirectly
  (the `proc` fetch gate); the callback state itself is expected live (it answered in-cb).
- **3-D `get_rest_info` discrepancy vs r88**: unresolved which side is geometry-specific;
  would take a paired 3-D re-run on the r88 rig to reconcile.
- All values are **this host, this build, headless, 60 tps, GodotPhysics2D, these
  geometries** — no portability claim.

## 8. Author directives (exact)

1. Copy `corpus/live/r80-scout/proj/phys2d_motion.gd` → `corpus/fixtures/phys2d_motion.gd`
   (876 lines, sha256 `ddb5921d4aff5f37…` — full hash in `MANIFEST.sha256`).
2. Append the 28 `CASES` rows from `author-rows.py.txt` / §1.4 **ahead of the
   crash/descendant tail** — same ordering constraint the r79 block already encodes in its
   comment (the `sleep 8` orphan window forbids CASES between
   `descendant_pipe_detached_control` and the meta probes).
3. Merge the two `expected_errors` entries verbatim (`phys2d_motion_mac_maxcol` ×1 line,
   `phys2d_motion_dss_wrongarg` ×3 distinct lines covering 7 emitted).
4. No harness edits needed: the battery's launch shape, 8 s bound, classifier and
   `expected_errors` machinery already fit these rows — verified against the extracted
   production predicate, not a re-implementation.
5. Optional: `ccd_spin` may be armed for its *absence* signature but should be labeled
   weak in the class table until a non-overlapping-pose discriminator lands (§7).

## 9. Evidence index

| artifact | path | sha256 (prefix) |
|---|---|---|
| probe (author fixture source) | `corpus/live/r80-scout/proj/phys2d_motion.gd` | `ddb5921d4aff5f37` |
| runner (classifier extractor + verify) | `corpus/live/r80-scout/run_arms.py` | `b2d60bc96fe196d1` |
| threaded twin project | `corpus/live/r80-scout/proj_thr/` | (`project.godot` differs only by `2d/run_on_separate_thread=true`) |
| discovery receipts | `corpus/live/r80-scout/arms-discover.json` | `a7844ac5da5c7cfd` |
| verify receipts (28×3, ablations, per-rep raw streams) | `corpus/live/r80-scout/arms-verify.json` | `b177c708af48d7d7` |
| threaded twin outputs | `corpus/live/r80-scout/arms-thr.txt` | — |
| paste-ready rows | `corpus/live/r80-scout/author-rows.py.txt` | `12026134dbc4bf98` |
| engine/backend census | `corpus/live/r80-scout/runs/engine-census.txt` | — |
| tracked-battery sanity | `corpus/live/r80-scout/runs/20261015T050846740845Z/verdicts.json` | 111/111 |
| artifact manifest | `corpus/live/r80-scout/MANIFEST.sha256` | — |

Prior-round references (read-only): `reports/round-79/r79-scout.md` (interior-window
lattice, tier-lag, the arming pattern this table follows);
`~/Projects/shokunin/game-dev-3d-shokunin/reports/round-88/r88-scout.md` (3-D motion-query
split compared at §4.4/F11).
