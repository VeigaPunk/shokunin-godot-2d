# game-dev-2d round 97 — scout (r97-scout): the SceneTree groups / signal connect flags / `call_deferred` timing lattice, pre-measured; 12 rows verbatim-ready

Seat `SCOUT` (LEAF; frozen `probeParent` — one labrat dispatch, non-executable, §9) | lane
`r97-scout` | round 97 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 physics ticks/s, `SceneTree` root class `Window`, no rendering server. Repo
`~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at session start **`2c4b1ff`**
(*r94 scout*), HEAD at session end **`7a45a60`** (*r92 boundary* — other lanes committed
while this seat ran; none of those commits touch this seat's artefacts). The only tracked
modification in `git status` is a concurrent lane's `corpus/fixtures/run_battery.py` edit
(already `M` before this session, +74 lines, **contains no r97/`stree_lattice` token** —
untouched by me).

**No git mutation, no tracked file written, no commit.** Writes are this report and
`corpus/live/r97-scout/**` only. The launch `project.godot` is the byte-copy of
`corpus/fixtures/project.godot` (`8de8b3af…`).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on
this host; `definition`/`references`/`hover` were **unavailable for every file**. All
symbol/API knowledge below comes from runtime `ClassDB` introspection inside the probes
(the `census` arm) and from the engine's own output — never from engine source (no engine
source tree on this host). Every mechanism statement is marked **[I]** and kept separate
from the measurements.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Primary: the SceneTree group/signal/deferred lattice** — the group ops
(`add_to_group`/`remove_from_group`/`is_in_group`/`get_groups`/`get_nodes_in_group`/
`get_first_node_in_group`/`get_node_count_in_group`/`has_group`; `call_group`,
`call_group_flags`, `notify_group`, `notify_group_flags`, `set_group`, `set_group_flags`
with `GROUP_CALL_{DEFAULT,REVERSE,DEFERRED,UNIQUE}`), the signal connection lattice
(emission order, `CONNECT_DEFERRED`/`ONE_SHOT`/`PERSIST`/`REFERENCE_COUNTED`,
`await signal`), the `call_deferred`/`set_deferred`/`await process_frame`/`await
physics_frame` timing ladder, and `change_scene_to_*` mechanics.

Why this surface, against the brief's other candidates **[O]/[I]**:

- **It is a true blind spot.** `grep -rin "call_group\|notify_group\|get_nodes_in_group\|
  add_to_group" corpus/fixtures/*.gd` finds **nothing** — not one fixture in 29 touches a
  group op, and no prior round's report mentions them. `call_deferred` appears in
  fixtures only as incidental plumbing. The battery CASES list has no group row and no
  deferred-timing row.
- **It is the highest-frequency lifecycle API in 2D gameplay code** (pause trees, damage
  fan-out, "all enemies", save-all, scene teardown) and the deferred/timing ladder is the
  #1 source of "my callback did not run / ran too early" author bugs.
- **Falsifiability was immediate** (§4, §7): the discovery probe refuted three of the
  scout's own starting assumptions — `GROUP_CALL_UNIQUE` does *not* dedup two separate
  direct calls, the deferred group call resolves its member list at **queue time** (not
  flush time), and `change_scene_to_file` does **not** complete at the next frame.
- The other candidates were weighed and left: TileMapLayer/r92, AnimationPlayer+Tween/r93,
  CPUParticles2D/r94 and PhysicsDirectSpaceState2D/r95 are sibling scout seats this wave;
  physics body/event/joint surfaces belong to r79–r81; input to r87.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (28 arms, fresh process each) | feasibility: API census, group order/forms/flags/lifecycle/reorder/dup/setters, signal forms/flags/await, deferred ladder/nest/slots/order, scene file/packed/missing/node | one-off scratch runs (findings in §3, §4) |
| 2 | one-off falsification scripts (`/tmp/uniq*.gd`, `/tmp/cap*.gd`) | `UNIQUE` semantics (4 scripts), deferred capture-time (3 scripts) | scratch, findings in §4 |
| 3 | `bash run_cells.sh` | **12 cells** (8 pure ×3, 4 frame-bound ×6) = **48 runs** | `runs/r97_*.{out,err,rc}` |
| 4 | `bash run_loadtest.sh` (10 own `yes` hogs, load avg 110–138) | 36 runs over all 12 cells | `runs/loadtest/*.{out,err,rc}` |
| 5 | `python3 analyze_r97.py` | per-cell reps / out-uniq / err-uniq / rc / PASS-line uniqueness | `runs/analyze_r97.json` |
| 6 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 12 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |

**Canonical cell set: 48 runs across 12 cells** — 8 pure cells ×3, 4 frame-bound cells ×6.
All rc=0; no cell crashed; no run left running; **all stderr 0 B**.

**Byte-stability: 12 of 12 cells are `out_uniq=1 err_uniq=1 pass_uniq=1 rc=[0]`**
(`runs/analyze_r97.json`: `UNSTABLE=[]`, `CRASH_CELLS=[]`) — including the four cells whose
PASS line carries order vectors and the four frame-bound cells.

**Load-stability [M]:** re-running all 12 cells ×3 at load avg 110–138 (10 own `yes` hogs
on top of a host already at ~113 from other lanes) produced **36/36 rc=0**, 0 B stderr, and
**every cell byte-identical to its canonical rep1**. `verify_rows.py` → `ROWS`
**84/84 accepted**, `ROWS_PREFIX` **84/84 accepted**, `rejected=[]`.

**Arm-dispatch integrity [O]:** every arm prints its own name on the `PASS` line
(`PASS stree_lattice <arm> …`), so a silent `_:` fallback (the r88 dead-seat failure) is
impossible to miss; `arm` is parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan).

**Delegated probe [O]:** the frozen probeParent dispatched exactly one read-only
`ufo-labrat` seat (independent falsification of the group-order and capture-time laws).
**It could not execute** — that seat's tool surface has no shell/exec and no write
capability, so it ran **0** godot launches and reported honestly rather than fabricating
vectors. It did return one **real defect**: its adversarial read found that the probe
header contradicted itself (L2 "resolved at CALL time" vs L3 "resolved at flush time") —
that defect is fixed in the frozen revision. It also proposed a sharper group-order
counterexample (tree order `a,b,c`, group-add order `c,a,b`), which **this seat ran**: the
group order still came back `[a,b,c]`, confirming L1 (§7 F6). The falsification ladder was
otherwise run by this seat (§4, §7).

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **API census + signatures + flag values** (10 group methods, 6 flags) | **PINNABLE** | 3 | uniq=1 |
| **Group order = TREE order** (depth-first pre-order, not insertion) | **PINNABLE law** | 3 + 3 rev | uniq=1 |
| **Group-call order / REVERSE / arg forwarding / silent method skip** | **PINNABLE law** | 3 | uniq=1 |
| **DEFERRED member list captured at QUEUE time** | **PINNABLE law** | 3 | uniq=1 |
| **UNIQUE dedup: off for direct, on for deferred within the frame** | **PINNABLE hazard** | 3 | uniq=1 |
| **Group lifecycle** (snapshot vs live, parent/child, free/queue_free, odd names) | **PINNABLE** | 3 | uniq=1 |
| **`set_group`/`set_group_flags`** (real properties only; silent skip) | **PINNABLE** | 3 | uniq=1 |
| **Signal emission order / reconnect moves to end / bind** | **PINNABLE law** | 3 | uniq=1 |
| **`CONNECT_DEFERRED`** (one global FIFO queue; survives disconnect) | **PINNABLE law** | 3 | uniq=1 |
| **`CONNECT_ONE_SHOT` severs AT EMIT** (deferred included) | **PINNABLE law** | 3 | uniq=1 |
| **`CONNECT_PERSIST` = serialization only** | **PINNABLE law** | 3 | uniq=1 |
| **`CONNECT_REFERENCE_COUNTED`** (duplicate connect tolerated, N disconnects) | **PINNABLE law** | 3 | uniq=1 |
| **`await <signal>` resumes AT EMIT** | **PINNABLE law** | 3 | uniq=1 |
| **Deferred flush position in the idle frame** | **PINNABLE law** | 6 | uniq=1 |
| **Deferred target survival** (freed dropped, out-of-tree runs, queue_free runs) | **PINNABLE law** | 6 | uniq=1 |
| **`await physics_frame` frame index** | **PARTIALLY MEASURED** — phase-coupled bimodal (1 or 2); in-frame ordering pinned | 6 | uniq=1 |
| **`change_scene_to_*` completion timing** | **PINNABLE** (file async ≈5 frames, packed 1 frame, node 2 frames) | 6 | uniq=1 |

---

## 3. Measured values, verbatim

All payloads are `runs/r97_<cell>.rep1.out`. Identities are node tags; no RID, object id,
instance id or address is ever printed.

### 3.1 Census (`census`) — [M]

```
group_meths=[call_group,call_group_flags,get_first_node_in_group,get_node_count_in_group,get_nodes_in_group,has_group,notify_group,notify_group_flags,set_group,set_group_flags]
group_sigs=[call_group(group:21,method:21),call_group_flags(flags:2,group:21,method:21),notify_group(group:21,notification:2),notify_group_flags(call_flags:2,group:21,notification:2),set_group(group:21,property:4,value:0),set_group_flags(call_flags:2,group:21,property:4,value:0)]
group_flags=DEFAULT=0 REVERSE=1 DEFERRED=2 UNIQUE=4
connect_flags=DEFERRED=1 PERSIST=2 ONE_SHOT=4 REFERENCE_COUNTED=8
node_group_meths=[add_to_group,call_deferred_thread_group,get_groups,get_process_thread_group,get_process_thread_group_order,is_in_group,notify_deferred_thread_group,remove_from_group,set_deferred_thread_group,set_process_thread_group,set_process_thread_group_order]
object_defer_meths=[call_deferred,set_deferred]
scene_meths=[change_scene_to_file,change_scene_to_node,change_scene_to_packed,reload_current_scene,unload_current_scene]
tree_cls=SceneTree root_cls=Window ticks=60 group_signal=process_frame=true physics_frame=true
```

Type codes are `ClassDB` `Variant::Type` numbers (`21`=StringName, `2`=int, `4`=String,
`0`=Nil/Variant). **[O]** `SceneTree` has no `set_group_flags`-free `notify_group` overload
beyond the two listed, and `Object` exposes exactly two deferred entry points
(`call_deferred`, `set_deferred`).

### 3.2 Group order is TREE order (`group_order`, `group_order_rev`) — [M], the headline law

```
add_order=[a,b,c,d] t0=[a,b,c,d] first=a last=d count=4 removed=[a,c]
readd_d_then_b=[a,b,c,d] tree_order=[DF,a,b,c,d] after_reparent=[a,b,d,c]
after_move_child=[b,d,c,a] tree_order2=[DF,b,d,c,a] rep1=[b,d,c,a] rep2=[b,d,c,a]
nested=[b,d,c,a,p,ch] nested_tree=[DF,b,d,c,a,p] dup_add=[b,d,c,a,p,ch] dup_count=6
double_remove=[d,c,a,p,ch] membership=has=true nothas=false in=true groups_a=[grp] unknown=[] first=null
```

`group_order_rev` (children created in tree order, `add_to_group` called in the REVERSE
order `d,c,b,a`) produces the **identical** group order — `add_order=[d,c,b,a]
t0=[a,b,c,d] …` — i.e. the `add_to_group` call order is irrelevant; the returned order is
the tree's. `DF` is this probe's helper node (a child of `G`, created before the test
nodes) and appears exactly where the tree puts it. `nested` pins depth-first pre-order
(parent `p` before its child `ch`, both after the earlier siblings).

- **[M] L1.** `get_nodes_in_group` is a tree-order view (depth-first pre-order over the
  SceneTree), not an insertion list. Remove+re-add restores the node's tree position;
  `reparent` (remove+add_child) and `move_child` reorder the group; the add-order does not.
- **[M]** `get_first_node_in_group` = the first entry, `get_nodes_in_group(g)[-1]` = the
  last; `get_node_count_in_group` matches the array size; `has_group` and `is_in_group`
  agree; an unknown group yields `[]`, `null`, `0`; duplicate `add_to_group` and double
  `remove_from_group` are idempotent; `get_groups()` includes the engine-internal
  `_root_canvas<id>` group (filtered here — it carries an instance id and is not
  byte-stable).

### 3.3 Group calls (`group_flags`) — [M]

```
direct=[direct1,direct1,direct1] reverse=[rev2,rev2,rev2] args=9/9
deferred_t0=[] deferred_t1=[def3,def3,def3] def_rev_t1=[dr4,dr4,dr4]
cap_members_t0=[e] cap_t1=[cap1] cap_d_membership=false cap_e_membership=true
drev_members=[f,h] drev_t1=[drev1,drev1]
fifo=[q11,q11,q22,q22]
uniq_direct_1=[u1] uniq_direct_2_same_args=[u2] uniq_direct_3_new_args=[u23]
uniq_def_t0=[] uniq_def_t1=[ud1] uniq_def_next_frame=[ud2]
plain_deferred_twice=[p1,p2]
set_def_capture=(7.0000,7.0000)/(7.0000,7.0000)
notify=[p.paused] paused_seen=1 paused_seen=2 missing_method=silent
```

- **[M] L2.** `call_group` calls every member in tree order; `GROUP_CALL_REVERSE` is the
  exact reverse; args are forwarded; a node without the method is silently skipped.
- **[M] L3 — capture-time law.** In `g2`, `d` is a member when the deferred call is queued,
  then leaves the group before the flush; `e` joins after the queue call. At flush time
  `get_nodes_in_group("g2")` is `[e]` and `cap_d_membership=false`, yet `cap_t1=[cap1]`
  contains exactly one call — **`d`'s**, not `e`'s (`e` was never called). The deferred
  group call therefore **resolves its member list at queue time**, then invokes that
  snapshot at the flush. `set_group_flags(DEFERRED, …)` obeys the same rule
  (`set_def_capture`: the node that left still receives the write, `(7.0,7.0)/(7.0,7.0)`).
- **[M] L4 — `UNIQUE` hazard.** Two *separate direct* identical `UNIQUE` calls both run
  (`uniq_direct_1=[u1]`, `uniq_direct_2_same_args=[u2]` — two distinct invocations, not a
  dedup). With `DEFERRED` the identical queued calls **do** collapse to one
  (`uniq_def_t1=[ud1]` after three identical queued calls) and the key expires at the
  frame end (`uniq_def_next_frame=[ud2]`). Plain `DEFERRED` does not dedup
  (`plain_deferred_twice=[p1,p2]`).
- **[M]** `notify_group` delivers `_notification` to every member (`paused_seen` 1 then 2
  for two `notify_group` calls); `notify_group_flags(REVERSE, …)` likewise.

### 3.4 Group lifecycle (`group_lifecycle`) — [M]

```
snapshot=[a,b] live=[a,b,c] root_in_group=[root] root_groups=[rootgrp]
parent_child=[a,b,c,p,ch] child_stays=[a,b,c,ch]
after_free=[b,c,ch] after_queue_free_t0=[b,c,ch] after_queue_free_t1=[c,ch]
weird_group=[s] weird_groups=[a/b.c] multi_groups=[a/b.c]/true
```

- **[M]** `get_nodes_in_group` returns a fresh snapshot (a node added after the call is not
  in it); removing a parent from a group does **not** remove its child; `free()` removes
  the member immediately, `queue_free()` by the next frame; the root `Window` can carry
  groups; group names with `/` and `.` are accepted verbatim.

### 3.5 Group setters (`group_setters`) — [M]

```
set_group=(9.0000,9.0000)/(9.0000,9.0000) set_group_flags=(3.0000,3.0000)/(3.0000,3.0000)
set_group_deferred_t0=(3.0000,3.0000)/(3.0000,3.0000) set_group_deferred_t1=(4.0000,4.0000)/(4.0000,4.0000)
missing_prop=silent paused_seen=0 unknown_group=(4.0000,4.0000) rev=false
```

- **[M] L13.** `set_group`/`set_group_flags` write **real properties** (Node2D `position`
  here) on every member; the `DEFERRED` variant lands at the same flush point; a
  non-property name (`set_group("sg","no_such_prop",1)`) and an unknown group are silently
  skipped (no error, no partial write).

### 3.6 Signal emission order (`signal_order`) — [M]

```
connect_order=[a1,b2] conn_n=2 flags_default=0 after_disconnect=[b3] reconnect_order=[b4,a5]
byname_connected=false byname_order=[b6,a7] bind_order=[a1,b2] bind_conn_n=2 no_listeners=[]
await_before=[] await_same_frame=[w1] await_next_frame=[w1] await_two=[w1,w2]
```

- **[M] L5.** Emission is synchronous and in connect order; `flags_default=0`; disconnect
  drops the entry; **disconnect+reconnect moves the callable to the END of the connection
  list** (`reconnect_order=[b4,a5]` after re-connecting `b` then `a`); a method-name
  `Callable` is the same identity as the property form (`byname_connected=false` after
  `disconnect(Callable(s,"on_a"))`, and the re-connect lands at the end); `bind()` args are
  one connection entry each; emitting with no listeners is a no-op.
- **[M] L9.** `await <signal>` resumes **at emit time, in the same frame**
  (`await_same_frame=[w1]` immediately after `emit()`), and two waiters both resume
  (`await_two=[w1,w2]`).

### 3.7 Signal connect flags (`signal_flags`) — [M]

```
mixed_t0=[a1] mixed_t1=[b2] defer_two_t0=[] defer_two_t1=[a1,a2]
disc_t0_connected=false disc_t1_ran=[a1] oneshot=[a1] oneshot_connected=false
osd_connected_t0=false osd_second_emit=[] osd_flush=[a1] osd_connected_t1=false
rc_conn_n=1 rc_emit=[a1] rc_after_one_disconnect=true rc_emit2=[a2] persist=[a1] persist_flags=2
cross_t0=true cross_t1=[a1,b2] cross_rev_t1=[b3,a4]
```

- **[M] L6.** `CONNECT_DEFERRED` queues at emit time into **one global FIFO queue**: two
  emits in one frame produce two calls in order (`defer_two_t1=[a1,a2]`); two *different*
  signals on the same object interleave by emission order, not by signal
  (`cross_t1=[a1,b2]`, and reversing the emit order gives `cross_rev_t1=[b3,a4]`); a
  queued callback still runs after the connection is disconnected before the flush
  (`disc_t1_ran=[a1]`).
- **[M] L7.** `CONNECT_ONE_SHOT` severs **at emit time**: the second emit in the same
  frame is a no-op (`oneshot=[a1]`, `oneshot_connected=false`); with
  `DEFERRED|ONE_SHOT` the connection is already gone right after the first emit
  (`osd_connected_t0=false`), the second emit is a no-op, and the already-queued call
  still runs (`osd_flush=[a1]`).
- **[M] L8.** `CONNECT_PERSIST` is a serialization flag only — delivery is immediate and
  `get_connections()[0]["flags"]==2`.
- **[M]** `CONNECT_REFERENCE_COUNTED` tolerates a duplicate connect of the same callable
  (`rc_conn_n=1` — `get_connections()` still reports one entry, no error) and the signal
  still fires after one `disconnect` (`rc_after_one_disconnect=true`, `rc_emit2=[a2]`).

### 3.8 The `call_deferred` ladder (`defer_ladder`) — [M]

```
ladder=[t0,t0_end,co_pf,after_pf1,after_pf2] df_log=[cd] no_wait=[no_wait]
phys_defer_same_frame=true phys_co_in_log=true nested=[outer,inner] nested_t1=[outer,inner]
```

`co_pf` is the `await process_frame` continuation; `df_log=[cd]` is the deferred callback
queued *before* that await. **[M] L10**: the deferred callback runs **after** the await
continuation resumes, i.e. the deferred flush is at the END of the idle frame, after the
`process_frame` signal. A deferred call with no await at all still lands (`no_wait`).
`nested`/`nested_t1` show a `call_deferred` issued from inside a deferred callback running
in the **same** flush.

### 3.9 Exact in-frame ordering (`defer_order`) — [M], the timing law

```
frame1=[pf_sig,resume] | df=[]
frame2=[queued,pf_sig,resume2] | df=[cd]
emit_t0=[] | ord=[]
emit_t1=[pf_sig] | ord=[a1]
frame4=[sig_frame,pf_sig] | df=[from_sig]
early_t1=[early]
```

`pf_sig` is a `process_frame` signal listener; `resume*` is the `await process_frame`
continuation.

- `frame1`: the process callback fires **before** the await continuation resumes
  (`[pf_sig,resume]`) — the continuation is the *next* frame's process pass, not the
  current one.
- `frame2`: a deferred call queued mid-frame (`cd`) lands after `pf_sig` and before the
  next `resume2`.
- `emit_t1`: a **deferred signal** emitted mid-frame lands in the same flush
  (`ord=[a1]`), and `emit_t0=[]` shows nothing happened synchronously.
- `frame4`: a deferred call queued *from inside* the `process_frame` signal still lands in
  the same frame (`df=[from_sig]`).

**[M] L10 (exact).** Within one idle frame the order is: process callbacks → the
`process_frame` signal → the deferred flush (deferred calls, deferred signal callbacks,
deferred group calls) → next frame's `await process_frame` continuation.

### 3.10 Deferred target survival (`defer_slots`) — [M]

```
t0=[] after_pf=[node1,tree] set_deferred_t0=false set_deferred_t1=true
detached=[detached1] queue_free=[s41] queue_free_valid=false free_dropped=[]
slots_t0=[] slots_t1=[A,B] slot_meta=z
```

- **[M] L11.** A deferred call on a node **out of the tree** still runs (`detached`); a
  node that is `queue_free()`d in the same frame still runs its deferred call
  (`queue_free=[s41]`) and is gone by the next frame (`queue_free_valid=false`); a node
  `free()`d immediately has its deferred call **dropped** (`free_dropped=[]`); FIFO within
  one object (`slots_t1=[A,B]`); `set_deferred("position", …)` lands at the same flush
  point (`set_deferred_t0=false` → `t1=true`).

### 3.11 `physics_frame` (`defer_ladder`) — [M] partial

`phys_defer_same_frame=true` and `phys_co_in_log=true` are byte-stable across 18 fresh
runs. **[M]** a deferred call queued from a `physics_frame` continuation lands in the same
frame as that continuation. **[M] NOT PINNED:** the continuation's *frame index* is
phase-coupled and bimodal (measured 1 or 2 frames depending on where the await lands
relative to the physics tick) — the probe deliberately does not pin it.

### 3.12 `change_scene_to_*` (`scene_probe`) — [M]

```
current_scene_t0=null file_t0=null file_children_t0=1 file_t1=null file_t5=SceneA tag=A
file_children_t5=2 packed_loaded=true packed_t0=null packed_t1=SceneB tag=B packed_t3=SceneB tag=B
packed_children_t3=2 node_t0=null node_t2=AdHoc node_children_t2=2 reload_exists=true
```

- **[M] L14.** `change_scene_to_file` is asynchronous: `current_scene` is still `null` at
  the next `process_frame` and the new scene is installed by the 5th frame (measured
  between frame 1 and frame 5; the scene node is added to `root` alongside the probe's own
  node). `change_scene_to_packed` completes **at the next frame**; `change_scene_to_node`
  within **two** frames. `current_scene` stays `null` until the frame the change completes.
- **[A]** the scout's starting assumption that all three complete "at the next frame" was
  refuted by this ladder (§7 F3).

---

## 4. How the laws were found (falsification-driven discovery)

1. **`UNIQUE` does not dedup direct calls (F1).** The first `group_flags` draft read
   `unique_2_same_args` as a dedup, but the per-node call counters proved a *second
   invocation* (`[u2]`). Three focused scratch scripts (`/tmp/uniq_probe.gd`,
   `/tmp/uniq2.gd`, `/tmp/uniq3.gd`, `/tmp/uniq4.gd`) established: direct = never deduped;
   `DEFERRED|UNIQUE` = deduped within the frame; the key expires at frame end; plain
   `DEFERRED` = never deduped. The probe now pins all four behaviours.
2. **The deferred capture point (F2).** The first draft's member-list debug stamp showed
   the snapshot disagreed with the live member set. Three scratch scripts
   (`/tmp/cap.gd`, `/tmp/cap2.gd`, `/tmp/cap3.gd`) ran the leave-before-flush and
   join-after-queue cases side by side with a membership readback *inside* the callback:
   a member that leaves is still called (its own `is_in_group` already `false`), a node
   that joins is not. The probe's `cap_*` trio now pins queue-time capture.
3. **`change_scene_to_file` is not one-frame (F3).** A 2-frame ladder looked like a
   silent failure; extending to 6 frames showed the install at frame 5.
4. **The `--script` deferred-target scare (F4, self-falsified).** A `call_deferred` on the
   SceneTree script itself reported `Error calling deferred method: 'SceneTree(discover.gd)
   ::_ladder_cb': Method not found` (`core/object/message_queue.cpp:220`). Two control
   scripts proved that call shape works fine — the target method simply did not exist in
   that revision (an edit artifact). The claim was struck from the probe header and is
   recorded here as a **falsified** scout assumption, not an engine law.
5. **The labrat's contradiction (F5).** The delegated read-only seat could not execute, but
   its adversarial read of the probe source caught that the header simultaneously claimed
   "resolved at CALL time" and "resolved at flush time". Fixed in the frozen revision
   (L3 now states capture-at-queue-time, measured by `cap_*`).
6. **The labrat's sharper counterexample (F6).** Tree order `a,b,c` with `add_to_group`
   called `c,a,b` returns `[a,b,c]` — the strongest form of the L1 falsifier, run by this
   seat (3/3 identical). No falsification.
7. **Order-vector hygiene.** Early drafts leaked the helper node and cross-experiment
   state into the order vectors, producing ambiguous multi-node vectors; every experiment
   now runs on its own group (`g1`…`g8`) with the helper node present in the tree and
   accounted for.

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **Deferred group calls capture at queue time** (L3). The most likely author surprise:
   `call_group_flags(GROUP_CALL_DEFERRED, "enemies", "die")` followed by
   `enemy.remove_from_group("enemies")` **still calls `die`** on that enemy; a node that
   joins the group later in the same frame is **not** called. If the intent is "whatever is
   in the group at flush time", use a direct call or re-queue after the membership change.
2. **`GROUP_CALL_UNIQUE` does not dedup direct calls** (L4). Authors who reach for it to
   collapse "the same call twice in a frame" get nothing for the immediate form; only the
   deferred form collapses, and only within the frame.
3. **`CONNECT_ONE_SHOT` severs at emit, not at callback** (L7). A deferred one-shot is
   already disconnected when the deferred call runs — `is_connected` is `false` inside the
   callback, and re-connecting after the emit re-arms a *new* connection.
4. **`await <signal>` resumes at emit time** (L9), i.e. **inside** the emitting call stack;
   code that assumes "next frame" ordering (e.g. after a `queue_free`) will observe the
   object mid-emission. `await process_frame` is the one that defers past the current frame.
5. **A `free()`d target silently drops a pending `call_deferred`** (L11) while
   `queue_free()` does not — the same source line behaves differently depending on which
   free is used.
6. **`set_group` only writes real properties** (L13) and silently skips everything else
   (including `meta` keys) — a typo in the property name produces no error and no effect.
7. **`change_scene_to_file` is not one-frame** (L14) — teardown code that assumes the new
   scene exists at the next `process_frame` will read `current_scene == null`.
8. **`get_groups()` leaks an engine-internal group name** (`_root_canvas<instance id>`)
   which is per-process and not byte-stable; any pinned output must filter `_`-prefixed
   groups.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (12, exec-checked)

`corpus/live/r97-scout/author-rows.py.txt` (5-tuples `(case, script, flags,
expected_exit, signature)`, `ROWS` full-line and `ROWS_PREFIX` recommended; the fixture
must be staged as `corpus/fixtures/stree_lattice.gd` and is byte-identical to
`probes/stree_lattice.gd`, sha256 `4dd18e10e84f0da2…`):

| # | case | arm | flags | exit |
|---|---|---|---|---|
| 1 | `stree_lattice_census` | census | — | 0 |
| 2 | `stree_lattice_group_order` | group_order | — | 0 |
| 3 | `stree_lattice_group_order_rev` | group_order | `--rev` | 0 |
| 4 | `stree_lattice_group_flags` | group_flags | — | 0 |
| 5 | `stree_lattice_group_lifecycle` | group_lifecycle | — | 0 |
| 6 | `stree_lattice_group_setters` | group_setters | — | 0 |
| 7 | `stree_lattice_signal_order` | signal_order | — | 0 |
| 8 | `stree_lattice_signal_flags` | signal_flags | — | 0 |
| 9 | `stree_lattice_defer_ladder` | defer_ladder | — | 0 |
| 10 | `stree_lattice_defer_slots` | defer_slots | — | 0 |
| 11 | `stree_lattice_defer_order` | defer_order | — | 0 |
| 12 | `stree_lattice_scene_probe` | scene_probe | — | 0 |

Insertion point: anywhere in the CASES tail — **no ordering dependency** (the probe never
touches the crash/descendant/export families; it only creates and frees its own nodes under
a private `G` root and restores `current_scene` in `scene_probe`). `EXPECTED_ERRORS = {}`:
every cell is ERROR:-clean with 0 B stderr on all 84 receipts.

The two `change_scene_to_*` cells need `scene_a.tscn`, `scene_b.tscn` and
`scene_marker.gd` staged next to the probe in the fixture directory (byte-identical copies
are in `corpus/live/r97-scout/proj/`); without them the `scene_probe` row fails loudly
(`Cannot open file`), it does not silently pass.

### 6.2 What to pin and what not to pin

**Pin:** the full `ROWS` signatures. They are byte-stable on 48 canonical + 36 loadtest
receipts at load avg 110–138, and the discriminating checks (§8) show a token flip is
rejected.

**Do not pin (or cut before):** the multi-element order vectors are the only
volatile-shaped content — `tree_order`, `after_reparent`, `after_move_child`, `rep1/2`,
`nested*`, `double_remove`, `fifo`, `uniq_def_t1`, `cross_t1`, `cross_rev_t1`,
`drev_t1` — because they are views of the probe's own construction. They are stable *for
this frozen construction* (proven 84/84), but `ROWS_PREFIX` is the recommended form: it
keeps the discriminating scalars (`add_order`, `t0`, `first`, `last`, `count`, `removed`,
`readd_d_then_b`, the `cap_*` trio, `uniq_*`, the `set_def_capture` pair) and drops the
vectors. `phys_*` frame **indices** must never be pinned (bimodal); only the
`phys_defer_same_frame`/`phys_co_in_log` booleans are pinned.

**Known harness-wide property (r79 C3, unchanged):** `classify_process` matches by
substring, so a *shortened* signature that is still a prefix-substring of the real line is
accepted. The pinned rows are the full lines; the mutation checks in §8 are the evidence
that matters.

---

## 7. Falsification list

| # | claim (starting assumption) | verdict | evidence |
|---|---|---|---|
| F1 | `GROUP_CALL_UNIQUE` dedups repeated direct calls in a frame | **FALSIFIED** | `uniq_direct_2_same_args=[u2]` (a second invocation); 4 scratch scripts |
| F2 | deferred group calls resolve their members at flush time | **FALSIFIED** | `cap_t1=[cap1]` + `cap_d_membership=false` + `cap_e_membership=true`; 3 scratch scripts |
| F3 | `change_scene_to_file` completes at the next frame | **FALSIFIED** | `file_t1=null` … `file_t5=SceneA` |
| F4 | a SceneTree script's own methods are not resolvable by `call_deferred` | **FALSIFIED (self-inflicted edit artifact)** | control script: `T1 ["cd"]`, rc=0, 3/3 |
| F5 | the probe header's two capture-time statements were consistent | **FALSIFIED by the labrat's read** | header L2 vs L3 contradiction; fixed in the frozen revision |
| F6 | group order might follow `add_to_group` call order | **NOT FALSIFIED** | tree `a,b,c` + add order `c,a,b` → group `[a,b,c]`, 3/3 |
| F7 | the returned group order might drift call-to-call | **NOT FALSIFIED** | `rep1=rep2=[b,d,c,a]` and the whole cell `out_uniq=1` over 6 reps |
| F8 | a deferred call might be dropped for an out-of-tree node | **NOT FALSIFIED** (it runs) | `detached=[detached1]` |
| F9 | `CONNECT_DEFERRED` might defer only until the next signal | **NOT FALSIFIED** | `defer_two_t1=[a1,a2]`, one global FIFO across signals |
| F10 | a disconnected deferred callback might be cancelled | **NOT FALSIFIED** (it still runs) | `disc_t1_ran=[a1]` |
| F11 | `CONNECT_ONE_SHOT` might sever after the deferred callback | **NOT FALSIFIED** | `osd_connected_t0=false` |
| F12 | `physics_frame` continuation frame index might be deterministic | **FALSIFIED (bimodal)** | 1 or 2 frames across 18 runs; not pinned |
| F13 | `set_group` might accept `meta` keys | **FALSIFIED** | `set_group_meta=A0/B0` (unchanged), `missing_prop=silent` |
| F14 | `notify_group` might not reach `_notification` | **NOT FALSIFIED** | `paused_seen=1` then `2` |
| F15 | the `--rev` variant might change the group order | **FALSIFIED** | `group_order_rev` identical to `group_order` except `add_order`/`rev` |

---

## 8. Discriminating-power checks (run in-session)

| check | result |
|---|---|
| every row signature is a byte-exact line of its receipt | 12/12 true |
| flip the `cap_d_membership` token inside a row | rejected 6/6 receipts |
| `--rev` negative control: forward row vs `--rev` receipts | accepted 0/6 (of 6) |
| `--rev` negative control: `--rev` row vs forward receipts | accepted 0/6 |
| drop one row (`census`, `signal_flags`, `scene_probe`) and re-verify the rest | 11/11 rows clean, 0 collateral rejections |
| full-line rows across 48 canonical + 36 loadtest receipts | 84/84 accepted |
| prefix rows across 48 canonical + 36 loadtest receipts | 84/84 accepted |

---

## 9. Remaining unknowns / not measured

1. **`physics_frame` frame index** — phase-coupled, bimodal (1 or 2). Only the in-frame
   ordering is pinned. A `--fixed-fps` run would make it deterministic; not measured.
2. **Threaded group variants** (`call_deferred_thread_group`,
   `notify_deferred_thread_group`, `set_deferred_thread_group`,
   `get/set_process_thread_group*`) — censused, **not armed** (needs a `Thread` harness).
3. **`reload_current_scene`/`unload_current_scene`** — existence pinned; behaviour not
   measured (a reload of the `--script` tree has no obvious battery shape).
4. **Scene change under `--script` with an `_init`-error or a node that is already
   parented** — not measured; `change_scene_to_node` was exercised only with a fresh
   unparented `Node2D`.
5. **Group ops from inside a group callback that mutates the same group** — only the
   reentrant direct call (`outer`/`inner`) was measured; add/remove *during* a group call
   is not (the r95 pattern suggests the member list is resolved once per call).
6. **`CONNECT_REFERENCE_COUNTED` N-disconnect ladder** — measured for N=2 (one disconnect
   leaves it connected); N≥3 not measured.
7. **`SceneTreeTimer` (`create_timer`/`process_always`) interaction with the deferred
   flush** — not measured; only its method census is pinned.
8. **`get_groups()` ordering across several groups** — the returned order was observed to
   be non-sorted in one early draft (`[_root_canvas…,g3,g2,g1]`); the probe therefore
   sorts public groups, and the raw order is **not** pinned.
9. **Rendered behaviour** — irrelevant here (headless); `current_scene` change with a
   `CanvasItem`-only scene and no rendering server is what was measured.

---

## 10. Host cleanup

All launches were `timeout -s KILL`-bounded (30 s) and none hit; no godot process was left
running. The loadtest started 10 own `yes` hogs and killed exactly those 10
(`own_hogs_killed=10`, `host_yes_remaining=80` — the remaining ones belong to other lanes).
No tracked file was modified; `git status` for this lane is unchanged apart from the
concurrent lane's pre-existing `corpus/fixtures/run_battery.py` modification.

## 11. Evidence index

| artefact | content |
|---|---|
| `corpus/live/r97-scout/probes/stree_lattice.gd` | frozen primary probe, sha256 `4dd18e10e84f0da2…` (12 cells) |
| `corpus/live/r97-scout/probes/discover.gd` | discovery micro-probe, 28 arms (provenance only), sha256 `b74b13b346a71206…` |
| `corpus/live/r97-scout/run_cells.sh` / `run_loadtest.sh` | canonical + load drivers |
| `corpus/live/r97-scout/runs/r97_*.{out,err,rc}` | 48 canonical receipts + `rc-summary.txt` |
| `corpus/live/r97-scout/runs/loadtest/` | 36 loadtest receipts + `hogs.txt` |
| `corpus/live/r97-scout/runs/analyze_r97.{json,txt}` | per-cell stability report (`UNSTABLE=[]`, `CRASH_CELLS=[]`) |
| `corpus/live/r97-scout/author-rows.py.txt` | 12 `ROWS` + 12 `ROWS_PREFIX` + `EXPECTED_ERRORS={}` |
| `corpus/live/r97-scout/verify_rows.py` | AST-extracted production classifier, 84/84 + 84/84 |
| `corpus/live/r97-scout/make_author_rows.py` / `analyze_r97.py` | generators |
| `corpus/live/r97-scout/RECEIPTS.md` | receipt map + reproduce command |
| `corpus/live/r97-scout/manifest.sha256` | sha256 of every other artefact in the lane plus this report (272 entries; self excluded so `sha256sum -c` passes clean) |
