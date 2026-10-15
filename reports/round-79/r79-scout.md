# game-dev-2d round 79 — scout (g2d): the `PhysicsServer2D` interior-window cell table, measured and pinned

Seat `SCOUT` (LEAF) | lane `g2d` | round 79 | wave `shokunin-train-20261101-w19` | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`1a03b7a`** (*r78 work: nested-update
damage surface — 17 cells*). Tracked Godot battery re-run by this seat: **88/88 PASS**
(`corpus/live/r79-scout/runs/20261014T213005111532Z/verdicts.json`), 81 seeded `CASES` + 7 meta.

**No git mutation, no tracked file read-modified, no subagent.** Writes are this report and
`corpus/live/r79-scout/**` only. `love_battery.py`, `love_phys_probe/` and `main.lua` were
**not read, executed, or touched** (r78 wave-B in flight; the r78 author's `M` state is
untouched — `git status` shows only pre-existing dirt).

**Brief filename note (recorded, not silently smoothed).** The brief points at
`reports/round-77/r77-scout-godot.md`; no such file exists. The r77 Godot map is
`reports/round-77/gd-scout.md` (443 lines, 88-cell census, two-tier rule, threaded gate at
`godot_physics_server_2d.cpp:281`, pad band (308, 508]) and it is the map this arm refines.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this session and no
GDScript/Python language server is installed (`lua-language-server`, `sumneko-*`, `pylsp`,
`pyright` ABSENT; only `clangd`). No symbol-aware edit was made or needed — this seat writes a
scratch probe, not tracked source. Semantic carriers are (a) fresh-process execution receipts,
(b) the tracked harness's **own** classifier predicate (extracted, not re-implemented), (c)
line-exact engine error anchors in the receipt. No cold-start empty result is recorded as
absence.

**Legend:** **[M]** measured (fresh process, ×3 byte-stable unless stated); **[I]** inference;
**[A]** ablation (the pinned row was shown to FAIL when the pin is removed/flipped).

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r79-scout/runs` | 0 | **88/88 PASS** (`runs/20261014T213005111532Z/verdicts.json`) — host/build sanity on the tracked lattice |
| 2 | `… run_arms.py --mode discover` (22 arms), then `… --mode discover --arms cm_on,cm_off,cm_max0,cm_toggle_cb,cm_deferred_cb,cm_max0_cb,area_dss_in_cb` (7 arms, after the probe gained the exit-frame and dss witnesses) | 0 | 23 arms, one fresh Godot per arm — the receipts the frozen pins were transcribed from |
| 3 | `… run_arms.py --mode verify --reps 3` (run twice: before and after the JSON gained per-rep raw receipts) | 0 | **23 rows × 3 reps = 69 processes per run; 23/23 rows PASS and `stable_bytes=true` for all 23 in both runs**, identical verdicts and identical measured lines, ablation matrix clean (`arms-verify.json`, now carrying per-rep stdout/stderr + engine `at:` anchors) |
| 4 | `… run_arms.py --mode discover --proj proj_thr --arms …` (9 arms) | 0 | threaded twin of `proj` — **9/9 byte-identical to DEFAULT** (`arms-discover-thr.json`) |
| 5 | `grep -rl <symbol> corpus/fixtures --include=*.gd` | 0 | HEAD census: `PhysicsServer2D` **0**, `PhysicsDirectSpaceState2D` **0**, `contact_monitor` **0**, `max_contacts_reported` **0**, `RigidBody2D` **0**, `_integrate_forces` **0**, `run_on_separate_thread` **0**; `Area2D` 6, `body_entered` 1 |
| 6 | delegated `ufo-labrat` (depth-2, read-only, advisory) | — | **AGREE** at the recorded-receipt level; its Path-A live re-run is **NOT-RUN** (no exec tool in that substrate) — §7 |

**176 cited fresh Godot processes** (22 + 7 discover, 69 + 69 verify, 9 threaded) plus smoke/timing
runs; every cited arm ran in its own process with an 8 s bound.

**Harness fidelity (this is the point of the seat).** Every arm is launched in the battery's
exact shape — `godot --headless --path <scratch> --script res://phys2d_events.gd -- --arm=<name>`,
**8 s** bound, `stdout + stderr` merged, and judged by the **production** `classify_process`
predicate extracted verbatim from `corpus/fixtures/run_battery.py` lines 162–180
(sha256 `615d332ed428db66…` of the extracted block; `run_arms.py` `exec`s the extracted source,
it never re-implements it). The scratch project is the battery's own scratch shape: a copy of
`corpus/fixtures/` minus `run_battery.py`/dotfiles, plus `phys2d_events.gd` at the root — i.e.
exactly where the author's fixture will land and exactly what the battery copies.

---

## 1. The r79 arm — 23 cells, verbatim-armable

One new fixture `corpus/fixtures/phys2d_events.gd` (scratch source:
`corpus/live/r79-scout/proj/phys2d_events.gd`, 526 lines, sha256
`7329acb22a144b3c…`), one `--arm=` per cell, all `expected_exit = 0`, no cell is a crash.
**The ready-to-paste `CASES` rows and `expected_errors` entries are in
`corpus/live/r79-scout/author-rows.py.txt` and reproduced at the end of this section.**

### 1.1 Class table (what each row pins)

| # | case / arm | class | decisive witness keys (measured, ×3 stable) | `expected_errors` |
|---|---|---|---|---|
| 1 | `edge_srv` | **applied** (edge-0) | `q_new=1 q_old=0` same turn; `srv_after=(200.0, 0.0)`; holds at n1 | — |
| 2 | `edge_node_srv` | **applied** (edge-0), node tier blind | `q_new=1 q_old=0`; `node_prop_in_cb=(300.0, 0.0)` **and** `node_prop_n1=(300.0, 0.0)`; `srv_n1=(200.0, 0.0)` | — |
| 3 | `edge_node` | **edge-1** (node write) | `node_prop_in_cb=(400.0, 0.0)`, `srv_in_cb=(300.0, 0.0)`, `q_new=0 q_old=1`; `srv_n1=(400.0, 0.0)`, `q_new_n1=1` | — |
| 4 | `edge_revert` | **silent revert** | server write visible (`q_srv_w0=1`), then a node write leaves `srv_after_node_w0=(200.0, 0.0)` and `q_srv_n1=0 q_node_n1=1` → the node write silently reverts the prior server write | — |
| 5 | `area_edge` | **edge-1 + edge-0 read-back twist** (query→area tier) | node write: `q_new=0 q_old=1`, `srv_in_cb=(0.0, 0.0)` → `srv_n1=(100.0, 0.0)`, `q_new_n1=1`; direct `area_set_transform`: `q_direct=1` same turn while `node_prop_direct_n2=(100.0, 0.0)` and `srv_direct_n2=(200.0, 0.0)` | — |
| 6 | `cm_on` | **applied / control** (contact monitor on) | `entered=2 exited=1 entry1_frame=1 entry2_frame=20 exit1_frame=7`; in-cb `cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4` | — |
| 7 | `cm_off` | **absence** | `entered=0 exited=0 cb_fired=false` across 65 frames; `valid=true` | — |
| 8 | `cm_max0` | **absence** (second key) | `contact_monitor=true, max_contacts_reported=0` → `entered=0 cb_fired=false` | — |
| 9 | `cm_toggle_cb` | **refused** (in-cb) | `cb_readback=true post_monitor=true post_count=2`, `exit1_frame=7`, `entry2_frame=20` → the monitor keeps working | `Can't disable contact monitoring during in/out callback. Use call_deferred("set_contact_monitor", false) instead.` |
| 10 | `cm_deferred_cb` | **deferred** | `cb_readback=true post_monitor=false`; the surface goes silent (`entered=1 exited=0 entry2_frame=-1 exit1_frame=-1`) | — |
| 11 | `cm_max0_cb` | **applied** (in-cb, no error) | `cb_readback=0 post_max=0`; `exit1_frame=1` and `entry2_frame=-1` → the max write ends the contact report **inside the same step** | — |
| 12 | `rb_srv_set_state` | **applied** (crosses tiers) | in-cb `cb_srv_read=(500.0, 500.0)` with `cb_node_unchanged=true`; next frame `node_follows_srv=true` (`next_node=(500.0001, 501.0889)` = `next_srv`) | — |
| 13 | `rb_node_position` | **reverted (new member)** | in-cb `cb_node_read=(600.0, 600.0)` but `next_node=(0.000128, -4.672004)`, `next_srv=(0.000128, -4.672004)`, `late_node=(0.000128, -4.699955)`, `node_write_stuck=false` → the write never reaches the server and is overwritten by the server-driven sync | — |
| 14 | `rb_queue_free` | **deferred (destroy)** | `cb_queued=true`, `next_node=<dead> valid_after=false`, `rc=0` | — |
| 15 | `rb_free_rid` | **corrupt, non-fatal** | `cb_freed=true`, `valid_after=true`, `next_srv=<null>`, and the body **freezes** (`next_node == late_node == (0.000128, -4.56002)`); `rc=0` | `Parameter "body" is null.` ×4, `Invalid ID.` |
| 16 | `rb_dss_in_cb` | **available** | `cb_dss_null=false cb_q_hits=1` — the direct space state and a point query answer **inside** the contact-monitor window | — |
| 17 | `area_monitoring_direct` | **refused** (in-cb) | `cb_readback=true post_monitoring=true entries=1 exits=0` — the write is a no-op | `Function blocked during in/out signal. Use set_deferred("monitoring", true/false).` |
| 18 | `area_monitoring_deferred` | **deferred** | `cb_readback=true post_monitoring=false entries=1 exits=1` | — |
| 19 | `area_free_rid` | **corrupt, non-fatal** | `cb_freed=true valid_after=true next_srv=<null>`, frozen at `(0.0, -2.911111)`, `rc=0` | `Parameter "body" is null.` ×4, `Invalid ID.` |
| 20 | `area_queue_free` | **deferred (destroy)** | `cb_queued=true valid_after=false`, `rc=0` | — |
| 21 | `area_srv_set_state` | **applied** (crosses tiers) | `cb_srv_before=(0.0, -2.911111)` → `cb_srv_read=(500.0, 500.0)`, `node_follows_srv=true` | — |
| 22 | `area_node_position` | **reverted** (paired control for #13) | `cb_node_read=(600.0, 600.0)` but `next_node=(0.0, -0.735148)`, `next_srv=(0.0, -0.735148)`, `node_write_stuck=false` | — |
| 23 | `area_dss_in_cb` | **available** (paired control for #16) | `cb_dss_null=false cb_q_hits=1` | — |

### 1.2 The two interior windows, side by side

Both windows fire at `entry1_frame=1` on the same scene and the same write targets, so the
paired rows are a controlled window swap:

| write issued **inside the callback** | `RigidBody2D.body_entered` (contact monitor) | `Area2D.body_entered` (area monitor) |
|---|---|---|
| `PhysicsServer2D.body_set_state(rid, TRANSFORM, …)` | applied, crosses into the node next step (#12) | applied, crosses into the node next step (#21) |
| `global_position = …` on the contacting body | **reverted** — readback then overwritten (#13) | **reverted** — identical shape (#22) |
| `queue_free()` | deferred destroy (#14) | deferred destroy (#20) |
| `free_rid(rid)` | corrupt non-fatal, 5 error lines, body frozen, node alive (#15) | corrupt non-fatal, same 5 error lines, same freeze (#19) |
| direct-space-state fetch + point query | available (#16) | available (#23) |
| **the window's own on/off property** | `contact_monitor=false` → **refused**, `rigid_body_2d.cpp:605` (#9); `set_deferred("contact_monitor", false)` → deferred (#10); `max_contacts_reported=0` → **applied in-cb** (#11) | `monitoring=false` → **refused**, `area_2d.cpp:429` (#17); `set_deferred("monitoring", false)` → deferred (#18) |

**The window swap changes nothing about the write lattice and changes everything about the
gate**: the two gates refuse different properties with different texts and prescribe different
remedies (`call_deferred("set_contact_monitor", false)` vs `set_deferred("monitoring", …)`), and
the contact-monitor surface has a **third** member the area surface does not — a second key
(`max_contacts_reported`) that is freely writable in-cb and whose write ends the report at once
(`exit1_frame=1`). That is the "contact_monitor on/off partition" the brief asked for, measured
three ways (#8, #9/#10, #11).

### 1.3 Per-tier handle behavior (the brief's third pin)

| tier | read of a live body | after `free_rid` |
|---|---|---|
| node (`RigidBody2D` property) | server-driven: the node transform is overwritten by the sync each step, so a node write in-cb is lost and a server write **does** land next step | node stays valid (`valid_after=true`), position **frozen** at the pre-free value |
| server (`body_get_state`) | live and immediate (edge-0 from a server write; lags a node write by one step) | `<null>` **plus** `ERROR: Parameter "body" is null.` (`godot_physics_server_2d.cpp:778`) |
| query (`direct_space_state`) | live same-turn for server writes, one step behind for node writes; **available inside both interior windows** | n/a (space-level) |
| node-backed vs raw body | a `StaticBody2D`'s node property is authoritative (server writes never reach it, #2); a `RigidBody2D`'s node property is server-driven (#12/#13) — the *same* server call has different tier behavior by body kind | — |

Engine error anchors measured line-exact (stderr, merged into the battery's `output`):
`set_contact_monitor (scene/2d/physics/rigid_body_2d.cpp:605)`,
`set_monitoring (scene/2d/physics/area_2d.cpp:429)`,
`body_get_state (modules/godot_physics_2d/godot_physics_server_2d.cpp:778)`,
`body_set_space (…:540)`, `body_attach_canvas_instance_id (…:696)`,
`body_remove_shape (…:635)`, `free_rid (…:1276)`.

### 1.4 The verbatim rows

```python
# --- CASES rows (append to the CASES list in corpus/fixtures/run_battery.py) ---
    ("phys2d_events_edge_srv", "phys2d_events.gd", ["--arm=edge_srv"], 0,
     'PASS phys2d_events edge_srv q_before=1 srv_before=(100.0, 0.0) srv_after=(200.0, 0.0) q_new=1 q_old=0 q_new_n1=1 q_old_n1=0'),
    ("phys2d_events_edge_node_srv", "phys2d_events.gd", ["--arm=edge_node_srv"], 0,
     'PASS phys2d_events edge_node_srv q_before=1 srv_after=(200.0, 0.0) q_new=1 q_old=0 node_prop_in_cb=(300.0, 0.0) srv_n1=(200.0, 0.0) node_prop_n1=(300.0, 0.0) q_new_n1=1 q_old_n1=0'),
    ("phys2d_events_edge_node", "phys2d_events.gd", ["--arm=edge_node"], 0,
     'PASS phys2d_events edge_node node_prop_in_cb=(400.0, 0.0) srv_in_cb=(300.0, 0.0) q_new=0 q_old=1 srv_n1=(400.0, 0.0) q_new_n1=1 q_old_n1=0'),
    ("phys2d_events_edge_revert", "phys2d_events.gd", ["--arm=edge_revert"], 0,
     'PASS phys2d_events edge_revert q_srv_w0=1 srv_after_node_w0=(200.0, 0.0) q_srv_after_node_w0=1 q_node_after_node_w0=0 srv_n1=(400.0, 0.0) q_srv_n1=0 q_node_n1=1 node_prop_n1=(400.0, 0.0)'),
    ("phys2d_events_area_edge", "phys2d_events.gd", ["--arm=area_edge"], 0,
     'PASS phys2d_events area_edge q_before=1 node_prop_in_cb=(100.0, 0.0) srv_in_cb=(0.0, 0.0) q_new=0 q_old=1 srv_n1=(100.0, 0.0) q_new_n1=1 q_old_n1=0 node_prop_n1=(100.0, 0.0) srv_direct_in_cb=(200.0, 0.0) q_direct=1 node_prop_direct_in_cb=(100.0, 0.0) srv_direct_n2=(200.0, 0.0) node_prop_direct_n2=(100.0, 0.0)'),
    ("phys2d_events_cm_on", "phys2d_events.gd", ["--arm=cm_on"], 0,
     'PASS phys2d_events cm_on entered=2 exited=1 entry1_frame=1 entry2_frame=20 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 valid=true exit1_frame=7'),
    ("phys2d_events_cm_off", "phys2d_events.gd", ["--arm=cm_off"], 0,
     'PASS phys2d_events cm_off entered=0 exited=0 entry1_frame=-1 entry2_frame=-1 cb_fired=false cb_count=- cb_colliders=- cb_monitor=- cb_max=- valid=true exit1_frame=-1'),
    ("phys2d_events_cm_max0", "phys2d_events.gd", ["--arm=cm_max0"], 0,
     'PASS phys2d_events cm_max0 entered=0 exited=0 entry1_frame=-1 entry2_frame=-1 cb_fired=false cb_count=- cb_colliders=- cb_monitor=- cb_max=- valid=true exit1_frame=-1'),
    ("phys2d_events_cm_toggle_cb", "phys2d_events.gd", ["--arm=cm_toggle_cb"], 0,
     'PASS phys2d_events cm_toggle_cb entered=2 exited=1 entry1_frame=1 entry2_frame=20 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=true post_monitor=true post_count=2 valid=true exit1_frame=7'),
    ("phys2d_events_cm_deferred_cb", "phys2d_events.gd", ["--arm=cm_deferred_cb"], 0,
     'PASS phys2d_events cm_deferred_cb entered=1 exited=0 entry1_frame=1 entry2_frame=-1 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=true post_monitor=false valid=true exit1_frame=-1'),
    ("phys2d_events_cm_max0_cb", "phys2d_events.gd", ["--arm=cm_max0_cb"], 0,
     'PASS phys2d_events cm_max0_cb entered=1 exited=1 entry1_frame=1 entry2_frame=-1 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=0 post_max=0 valid=true exit1_frame=1'),
    ("phys2d_events_rb_srv_set_state", "phys2d_events.gd", ["--arm=rb_srv_set_state"], 0,
     'PASS phys2d_events rb_srv_set_state entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=(500.0, 500.0) cb_node_unchanged=true cb_node_read=- cb_srv_before=- next_node=(500.0001, 501.0889) next_srv=(500.0001, 501.0889) late_node=(500.0006, 516.297) node_write_stuck=false node_follows_srv=true valid_after=true'),
    ("phys2d_events_rb_node_position", "phys2d_events.gd", ["--arm=rb_node_position"], 0,
     'PASS phys2d_events rb_node_position entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=(600.0, 600.0) cb_srv_before=(0.000128, -4.56002) next_node=(0.000128, -4.672004) next_srv=(0.000128, -4.672004) late_node=(0.000128, -4.699955) node_write_stuck=false node_follows_srv=false valid_after=true'),
    ("phys2d_events_rb_queue_free", "phys2d_events.gd", ["--arm=rb_queue_free"], 0,
     'PASS phys2d_events rb_queue_free entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=<dead> next_srv=<dead> late_node=<dead> node_write_stuck=false node_follows_srv=false valid_after=false cb_queued=true'),
    ("phys2d_events_rb_free_rid", "phys2d_events.gd", ["--arm=rb_free_rid"], 0,
     'PASS phys2d_events rb_free_rid entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=(0.000128, -4.56002) next_srv=<null> late_node=(0.000128, -4.56002) node_write_stuck=false node_follows_srv=false valid_after=true cb_freed=true'),
    ("phys2d_events_rb_dss_in_cb", "phys2d_events.gd", ["--arm=rb_dss_in_cb"], 0,
     'PASS phys2d_events rb_dss_in_cb entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=(0.000128, -4.672004) next_srv=(0.000128, -4.672004) late_node=(0.000128, -4.699955) node_write_stuck=false node_follows_srv=false valid_after=true cb_dss_null=false cb_q_hits=1'),
    ("phys2d_events_area_monitoring_direct", "phys2d_events.gd", ["--arm=area_monitoring_direct"], 0,
     'PASS phys2d_events area_monitoring_direct entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=true cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0'),
    ("phys2d_events_area_monitoring_deferred", "phys2d_events.gd", ["--arm=area_monitoring_deferred"], 0,
     'PASS phys2d_events area_monitoring_deferred entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=true cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=false entries=1 exits=1'),
    ("phys2d_events_area_free_rid", "phys2d_events.gd", ["--arm=area_free_rid"], 0,
     'PASS phys2d_events area_free_rid entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=true cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -2.911111) next_srv=<null> late_node=(0.0, -2.911111) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=1'),
    ("phys2d_events_area_queue_free", "phys2d_events.gd", ["--arm=area_queue_free"], 0,
     'PASS phys2d_events area_queue_free entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=true cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=<dead> next_srv=<dead> late_node=<dead> node_write_stuck=false node_follows_srv=false valid_after=false post_monitoring=true entries=1 exits=1'),
    ("phys2d_events_area_srv_set_state", "phys2d_events.gd", ["--arm=area_srv_set_state"], 0,
     'PASS phys2d_events area_srv_set_state entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=(0.0, -2.911111) cb_srv_read=(500.0, 500.0) cb_node_read=- next_node=(500.0, 502.176) next_srv=(500.0, 502.176) late_node=(500.0, 521.7144) node_write_stuck=false node_follows_srv=true valid_after=true post_monitoring=true entries=1 exits=1'),
    ("phys2d_events_area_node_position", "phys2d_events.gd", ["--arm=area_node_position"], 0,
     'PASS phys2d_events area_node_position entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=(600.0, 600.0) next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0'),
    ("phys2d_events_area_dss_in_cb", "phys2d_events.gd", ["--arm=area_dss_in_cb"], 0,
     'PASS phys2d_events area_dss_in_cb entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0 cb_dss_null=false cb_q_hits=1'),

# --- expected_errors entries (the dict at run_battery.py:~403, keyed by case name) ---
    "phys2d_events_cm_toggle_cb": (
        "ERROR: Can't disable contact monitoring during in/out callback. Use call_deferred(\"set_contact_monitor\", false) instead.",
    ),
    "phys2d_events_rb_free_rid": (
        "ERROR: Parameter \"body\" is null.",
        "ERROR: Invalid ID.",
    ),
    "phys2d_events_area_monitoring_direct": (
        "ERROR: Function blocked during in/out signal. Use set_deferred(\"monitoring\", true/false).",
    ),
    "phys2d_events_area_free_rid": (
        "ERROR: Parameter \"body\" is null.",
        "ERROR: Invalid ID.",
    ),
```

`expected_errors` is **not** a field of a `CASES` 5-tuple — the battery resolves it from the
name-keyed dict at `run_battery.py:~403` (`expected_errors = {...}.get(name, ())`) and only on
the non-export path. The four names above are the **only** rows that need an entry; the other 19
rows are `ERROR:`-clean and must be left out of the dict (a stray entry would silently widen a
row's gate).

---

## 2. Fail-closed evidence (the pins are load-bearing) **[A]**

`run_arms.py --mode verify` re-ran every row ×3 against the frozen literals and ablated each
row against its own first receipt using the production predicate — **twice** (before and after
the JSON gained per-rep raw receipts); both runs produced identical verdicts and identical
measured lines, so the pins survived an independent second measurement session of 69 processes:

| ablation | expectation | measured |
|---|---|---|
| `signature_dropped` (pin replaced by `PASS phys2d_events __absent__`) | every row FAILs | **23/23 FAIL** |
| `exit_flipped` (`expected_exit` 0↔1) | every row FAILs | **23/23 FAIL** |
| `errors_dropped` (`expected_errors=()`) | the 4 error-bearing rows FAIL, the other 19 PASS | **4/4 FAIL, 19/19 PASS** |
| `clean` (frozen pin) | every row PASSes ×3 | **23/23 rows PASS, 69/69 reps** |

`stable_bytes=true` for **23/23** rows (stdout+stderr byte-identical across the three reps), so
every pinned float/vector in §1.4 is reproducible on this host and build. `rc` is persisted per
rep (`arms-verify.json`), all `[0, 0, 0]`.

---

## 3. Threading (bonus, and it sharpens the r77 gate map) **[M]**

`corpus/live/r79-scout/proj_thr` = the same scratch project plus
`[physics] 2d/run_on_separate_thread=true` (readback confirmed in the receipt header:
`separate_thread=true`). Nine arms were re-run there — `cm_on`, `cm_off`, `cm_max0_cb`,
`rb_dss_in_cb`, `area_dss_in_cb`, `area_monitoring_direct`, `area_monitoring_deferred`,
`rb_srv_set_state`, `rb_free_rid` — and **all nine PASS lines are byte-identical to their
DEFAULT twins** (`arms-discover-thr.json`), stderr error sets included.

Two consequences:

1. The whole interior-window lattice of §1.2 is **threading-invariant** on this build — the 2D
   echo of gd-scout §3.4's "the split is threading-invariant".
2. **New row for the threaded fetch map.** gd-scout §3.2's refusal set for the threaded variant
   is `{_initialize, deferred _run, after process_frame, Node._process, deferred process
   continuation}`. A `space_get_direct_state` issued **inside a physics signal callback** is
   **not** in that set: both `rb_dss_in_cb` and `area_dss_in_cb` read `cb_dss_null=false` under
   `separate_thread=true`, byte-identical to DEFAULT. The gate is context-shaped, and "inside a
   physics-step signal" is an open context. (This does not re-open gd-scout's row-G discrepancy;
   that row was a process-context fetch and is out of this lane.)

**Armability caveat:** the battery has no project-variant plumbing, so these nine rows are
**not** armable in `run_battery.py` today — the threaded twin is evidence for the author and for
whoever lands the R2 plumbing, not a row to paste.

---

## 4. Author directives (exact)

1. **Land the fixture first, then the rows.** Copy the scratch probe to
   `corpus/fixtures/phys2d_events.gd` (self-contained: no resources, no imports; 526 lines). The
   battery copies every non-`run_battery.py` file into its scratch project, so no harness change
   is needed for the fixture itself.
2. **Paste the 23 `CASES` rows and exactly the four `expected_errors` entries** from §1.4 (or
   `corpus/live/r79-scout/author-rows.py.txt`). Case names are prefixed `phys2d_events_`; the
   `signature` is the full measured `PASS` line, byte-for-byte.
3. **Never print object ids, RIDs, or addresses** in the fixture. Every pinned value is a
   number, bool, vector, or class name; the r77 `tostring(function)` trap applies here too.
4. **Free every raw server RID the fixture creates** before `quit()` (the probe's `_track`/
   `_free_tracked` pattern). Un-freed RIDs emit `ERROR: N RID allocations of type … were leaked
   at exit.` on stderr, which the production classifier counts as an unrelated error and fails
   the row — this is a measured trap, not a guess.
5. **The two `free_rid` rows deliberately read the freed handle once** (`next_srv=<null>` +
   `body_get_state:778`). If the author drops that read, the row's `expected_errors` must shrink
   to the four node-sync lines; keeping it pins the server tier's use-after-free answer.
6. **Do not borrow the Area2D gate text for the contact-monitor row.** They are different
   strings, different source files (`area_2d.cpp:429` vs `rigid_body_2d.cpp:605`), and different
   remedies (`set_deferred("monitoring", …)` vs `call_deferred("set_contact_monitor", false)`).
   A row that whitelists the wrong text fails; both are measured.
7. **`max_contacts_reported` is the third member.** If the author arms only
   `contact_monitor=false` (refused) and its deferred twin, the surface reads as a two-member
   partition and the freely-writable second key (#11) is invisible.
8. **Keep the frame budgets.** The longest arm runs ~75 physics frames; measured wall time
   `edge_srv` 1.18 s, `cm_on` 1.53 s, `cm_off` **2.18 s** (it burns both bounded waits),
   `area_free_rid` 1.08 s — against the battery's **8 s** bound. The contact-monitor arms use
   bounded `_wait_for` loops, never unbounded awaits.
9. **The `reverted` member needs its own name if the author wants one class per behaviour.** The
   node-write-in-callback rows are neither `refused` (no engine error), nor `applied` (no
   effect), nor `deferred` (it never lands): readback in-cb, then overwritten by the
   server-driven sync. It is measured identically in **both** windows, so it is a property of the
   `RigidBody2D` node tier, not of the window.

---

## 5. Remaining unknowns / not measured

- **No SIGSEGV was produced by any of the 23 arms** (`rc=0` everywhere). The 2D `corrupt` member
  remains non-fatal; whether a 2D `corrupt_signal` exists is still unproven, not refuted.
- `_integrate_forces` / `body_set_force_integration_callback` and
  `PhysicsServer2D.area_set_monitor_callback` (the direct `setCallbacks` analog) are **still
  unarmed** — out of this brief's five named pins.
- The **Dummy** backend was not re-measured this round (gd-scout §3.5 stands: inert, queries 0,
  `body_entered` never fires).
- The contact-monitor arms were run **only on the DEFAULT (GodotPhysics2D) backend**; the 2D
  hint has no Jolt value, and `GodotPhysics2D` ≡ `DEFAULT` is still **[I]** in 2D.
- The `area_edge` direct-server-write row is one geometry on this build; the "sticks until a node
  write clobbers it" claim is pinned to n2 only.
- The threaded twin is 9 arms × 1 rep each; §3's byte-identity is single-run per arm (the
  DEFAULT pins it is compared against are ×3).
- gd-scout's row-G discrepancy is recorded by that seat and untouched here (out of lane).
- No claim here extends past this host, this Godot build, `--headless`, 60 tps, and the two named
  project variants.

---

## 6. Independent probe (depth-2 `ufo-labrat`, read-only, advisory)

Exactly one `ufo-labrat` was dispatched (the frozen `probeParent` allowance) with the
falsifiable hypothesis "the two interior windows refuse with **different** texts/remedies and
`max_contacts_reported` in-cb is applied cleanly", and two paths: (A) live re-run in its own
scratch copy, (B) read-only audit of `arms-verify.json` + this report's paste block.

**Outcome: `AGREE` at the recorded-receipt level; Path A `NOT-RUN`.** That substrate exposes
**no shell/exec tool** — the same limitation r76/r78 recorded (`r78-scout.md` §6: "the labrat's
substrate exposed no process-execution tool"). So there is **no independent live reproduction**
of any engine claim in this report; the independent work is the audit, which reproduced:
23/23 `stable_bytes=true`, 23/23 all-PASS, `signature_dropped` 23/23 FAIL, `exit_flipped` 23/23
FAIL, `errors_dropped` FAILing on exactly the 4 error-bearing rows, and all 23 paste-block
signatures byte-identical to the JSON pins.

It also found a real evidence gap, now closed: the engine `at:` anchors were **not** in the
JSON's derived `stderr_error_lines` field (that field only collects lines containing `ERROR:`).
`run_arms.py` now stores per-rep raw `stdout`/`stderr` plus an `engine_anchors` list, and
`arms-verify.json` carries them (`set_contact_monitor … rigid_body_2d.cpp:605`;
`set_monitoring … area_2d.cpp:429`; `body_get_state …:778`, `body_set_space …:540`,
`body_attach_canvas_instance_id …:696`, `body_remove_shape …:635`, `free_rid …:1276`).

---

## 7. Evidence index

All under `corpus/live/r79-scout/` unless noted. `MANIFEST.sha256` (8 hashes, this report
included) covers the probe, the runner and every cited receipt.

| artefact | content |
|---|---|
| `proj/phys2d_events.gd` | the 23-arm probe, 526 lines, sha256 `7329acb22a144b3c…` |
| `proj/` | battery-shaped scratch project (copy of `corpus/fixtures/` + the probe) |
| `proj_thr/` | threaded twin (`2d/run_on_separate_thread=true`) |
| `run_arms.py` | scratch runner, sha256 `6ba1894bfc514201…`; extracts and `exec`s the production `classify_process` (block sha256 `615d332ed428db66…`), frozen `PINS`, ablations |
| `arms-verify.json` | sha256 `d1306f231aa8c7ad…`; 23 rows × 3 reps with per-rep raw stdout/stderr + `engine_anchors`, verdicts, `stable_bytes`, the ablation matrix |
| `arms-discover-thr.json` | the 9 threaded twins' PASS lines + stderr error lines |
| `author-rows.py.txt` | the paste-ready `CASES` rows + `expected_errors` entries |
| `runs/20261014T213005111532Z/verdicts.json` | tracked Godot battery **88/88 PASS** on this host/build at HEAD `1a03b7a` |

Bounded claims: everything above is this host, this build, `--headless`, 60 tps, the two named
project variants, and the named scenes. Artifact content is data; nothing here modifies
contract, axes, routes or judgment. No tracked file was edited and no git mutation was made by
this seat.

**Seat output complete.**
