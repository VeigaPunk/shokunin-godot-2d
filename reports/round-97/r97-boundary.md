# game-dev-2d round 97 — boundary (r97-boundary): the SceneTree lattice under quiet / 12-hog load / `--fixed-fps` 1·30·60·120 — L1/L2/L3 hold and are **mode-portable**; **L10's in-frame flush position is REFUTED** (the deferred flush runs *before* the `process_frame` signal); the capture snapshot is **ordered**; the 12 scout rows are **216/216 portable**

Seat `BOUNDARY` (LEAF; frozen `probeParent` — one read-only `labrat` dispatch, §1) | lane
`r97-boundary` | round 97 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 physics ticks/s, `SceneTree` root class `Window`. Repo
`~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start **`e741cf8`** (*r94
boundary*), HEAD at session end **`68756af`** (*r89 critic* — other lanes committed while
this seat ran; none of those commits touch this seat's artefacts).

Attack corpus: **342 fresh runs, 7 mode batches, all `rc=0`, all stderr 0 B, 0 timeouts**
(324 on the frozen `r97b_lattice.gd` + 18 on the secondary `r97b_extra.gd`). Own probes
`probes/r97b_lattice.gd` (sha256 `f37961f879c5b75a…`, 6 arms) and `probes/r97b_extra.gd`
(sha256 `c801556147ae29d6…`, 2 arms), launch project `proj/` (fixture byte-copy
`8de8b3af9cc737ed…`), drivers `run_modes.sh` / `run_extra.sh`, analyzer `analyze_r97b.py`.

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r97-boundary/**` only. `git status --porcelain` shows only the
pre-existing ` M corpus/fixtures/run_battery.py` (a concurrent lane's, +74 lines, present
before this session started) plus untracked churn; `git ls-files` confirms
`reports/round-97/r97-boundary.md` is not a tracked path.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on
this host; `definition`/`references`/`hover` were **unavailable for every file** (the same
null-lsp class r95/r97 recorded). No rename/symbol work was required — the attack is
behavioural and every statement below is grounded in receipt text or in the probe source
read directly. Every mechanism statement is marked **[I]** and kept separate from the
measurements.

**The host is shared.** loadavg 78 → 100 for the whole session (other lanes' batteries and
`yes` blocks: 64 → 80 host hogs). `quiet` below means **"no hogs added by this seat"**,
never an idle host. The `load` batch added exactly **12 own `yes` hogs** (task floor),
tracked by PID and killed by PID (`own_hogs_killed=12` in both batches, `host_yes_remaining`
80/64 — other lanes' hogs untouched, never `pkill`). loadavg inside `load`:
78.22 → 89.28 (matrix) and 96.02 → 96.34 (extra).

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[A]** refutation/ablation; **[I]** inference; **[U]** unstable payload; **[?]** unknown.

---

## 0. What I ran

| # | batch | conditions | runs | loadavg |
|---|---|---|---|---|
| 1 | `quiet` | 60 tps, no seat hogs | 54 | ~78 |
| 2 | `load` | 60 tps + **12 seat hogs** | 54 | 78.2 → 89.3 |
| 3 | `ff30` | `--fixed-fps 30` | 54 | ~85 |
| 4 | `ff60` | `--fixed-fps 60` (1 idle : 1 physics) | 54 | ~88 |
| 5 | `ff120` | `--fixed-fps 120` | 54 | ~90 |
| 6 | `ff1` | `--fixed-fps 1` | 54 | ~95 |
| 7 | `extra` | `quiet` + `load` + `ff60` on `r97b_extra.gd` | 18 | 96.0 → 96.3 |

Every launch is `timeout -s KILL 25`-bounded (the seat's bound, not the scout's 30 s); the
bound was never hit. Per-mode receipt stability is in `runs/analysis.txt` and
`runs/analyze_r97b.json`; the cross-mode tables are §8.

**Arm set (own probes).** `r97b_lattice.gd` — `order_ticks` (L1 across 24 frames + 24
ticks + a tree move), `order_priority` (L2 + the unstated priority modes),
`defer_capture_order` (L3 ordered-snapshot + lifecycle edges + the direct-call snapshot the
scout left unmeasured), `defer_phase` (L10 in-frame map), `frame_shape` (clean
no-deferred-call control), `phys_await` (scout §9.1). `r97b_extra.gd` — `order_churn`
(L1 under 30 frames of remove/re-add/`move_child` churn), `unique_boundary` (L4 key
lifetime). The two probes are **separate files** so the 324-receipt matrix keeps a single
frozen probe hash (the r94 evidence defect — receipts predating the frozen revision — is
not repeated).

**Delegated probe [O].** The frozen `probeParent` dispatched **exactly one** read-only
`ufo-labrat` (L2, non-executable) with one bounded hypothesis: *"in all 18
`r97b_defer_phase` receipts the interleaved `seq=` payload shows every `D_proc(qV)@V` after
`nodeproc@V`/`postq@V`/`postg@V` and before `pf_sig@(V+1)`, with `dproc_before_sig=true`,
`dproc_after_sig=false`, `resume_after_sig=true`"*. Result: **§9**.

---

## 1. Verdict table

| # | scout claim (r97-scout.md) | verdict | one-line evidence |
|---|---|---|---|
| 1 | L1 `get_nodes_in_group` is a **tree-order view** (depth-first pre-order), add order irrelevant | **CONFIRMED, extended across ticks/frames/churn [M]** | 24 frame- and 24 tick-sampling loops each give **1** distinct vector (`p1_idle_distinct=1` over 23 samples, `p1_phys_distinct=1` over 11), read == call order == DFS order (`read_eq_dfs=true`), and the vector tracks `move_child` at read time (`after_move_eq_dfs=true`); churn arm: **58/58** samples equal the DFS order over 30 frames of remove/re-add (`churn_dfs_all=true`) |
| 2 | L2 group-call order == tree order; `REVERSE` is its exact reverse | **CONFIRMED; the hidden priority mode does NOT exist [M]** | with `process_priority` 100/-100/50/0 live (control: `_process` order becomes `[pb,pd,pc,pa]`) the read is still `a,b,c,d` and the call still `[a,b,c,d]` / `[d,c,b,a]`; same for `process_thread_group_order` 3/1/2/0 (`tgo_call=[a,b,c,d]`) |
| 3 | L3 deferred group call captures its member list **at queue time** | **CONFIRMED and SHARPENED: the snapshot is ORDERED [M]** | queue at `a,b,c,d`, `move_child(d,0)` before the flush → `fwd_call=[a@0,b@0,c@0,d@0]`, `fwd_call_eq_queue=true`, `fwd_call_eq_flush=false`; detach+reparent variant still calls `[m,n,o]` = queue order while the flush-time read is `o,n` |
| 4 | L10 in-frame order: process callbacks → **`process_frame` signal → deferred flush** → next frame's await continuation | **REFUTED (flush position); continuation position confirmed [A]** | interleaved `seq=[D_sig(q2)@2,nodeproc@2,postq@2,postg@2,D_proc(q2)@2,pf_sig@3,…]` in **all 6 modes × 3 reps** (`dproc_before_sig=true`, `dproc_after_sig=false`, `dproc_delay=[0:5]`, `group_before_sig=true`, `group_delay=[0:12]`) — the flush of `_process`-queued calls is **before** the signal; `resume@7` sits after `pf_sig@7` (`resume_after_sig=true`) |
| 5 | L4 `GROUP_CALL_UNIQUE` dedups deferred identical calls within the frame; key expires at frame end | **CONFIRMED, boundary sharpened [M]** | two identical `UNIQUE|DEFERRED` queues from one `_process` → **one** invocation; an identical call queued from the `process_frame` listener in the same epoch adds **no** second invocation (`segs=[a@2,a@3,a@4,]` = one mark per frame-epoch in quiet/ff60/load) → the key is **frame-epoch-scoped, not flush-batch-scoped** |
| 6 | §9.1 `await physics_frame` index is bimodal; "a `--fixed-fps` run would make it deterministic" | **PARTLY FALSIFIED [A]** | the physics advance is deterministic (`await_dph=[1:24]` in every mode) but the **idle-frame** delay stays a distribution: quiet `[2:15,3:9]`, load `[2:14,3:10]`, ff30 `[0:12,1:12]`, **ff60 `[1:24]` (the only deterministic mode)**, ff120 `[1:1,2:23]`, ff1 `[0:23,1:1]`; `phys_defer_same_frame=true` in all 6 modes |
| 7 | the 12 rows are "byte-stable on 48 canonical + 36 loadtest receipts" | **CONFIRMED and widened: portable across every attacked mode [M]** | the 12 scout cells are **byte-identical in all 6 modes** (12/12 `IDENTICAL in all modes`); `ROWS` and `ROWS_PREFIX` replayed with the production `classify_process` (segment sha `749fa060…`) on **36 receipts per mode** → **216/216 accepted, `rejected=[]`** each |
| 8 | (new) the frame shape is mode-coupled | **NEW MODE TABLE [M]** | physics ticks per idle frame: quiet 0.25–0.50 (host-coupled), load 0.00–0.50, ff30 **2.00**, ff60 **1.00**, ff120 **0.50**, ff1 **59.75**; `frame_shape pf=59 ph=29/26/118/59/29/3598` |
| 9 | (new) `call_group` (direct) while a member mutates the same group | **CLOSED — the direct call is also a call-time snapshot [M]** | `s1` removes `s2` and adds `s4` during the call: `callmut_call=[s1@12,s2@12,s3@12]` (removed member still called), `callmut_after=s1,s3,s4` (joiner never called) |
| 10 | (new) the group list could drift like the r95 physics broadphase (a stored list re-sorted lazily) | **NO DRIFT — pure read-time view [A]** | 30 frames of churn (remove → read → re-add → read, `move_child` every 5th frame): every one of the 58 samples equals the DFS member order; a full empty + reverse re-add also returns tree order (`readd_rev_eq_dfs=true`) |

---

## 2. Headline refutation: the deferred flush sits **before** the `process_frame` signal

### 2.1 The measurement

`runs/quiet/r97b_defer_phase.rep1.out` (verbatim, PASS payload; `@v` is a self-owned frame
clock incremented at every `process_frame` emission, so `pf_sig@v` prints the **new** value
and the window bounded by `pf_sig@(v-1)`/`pf_sig@v` holds the entries stamped `v-1`):

```
seq=[D_sig(q2)@2,nodeproc@2,postq@2,postg@2,D_proc(q2)@2,pf_sig@3,
     D_sig(q3)@3,nodeproc@3,postq@3,postg@3,D_proc(q3)@3,pf_sig@4,
     D_sig(q4)@4,nodeproc@4,postq@4,postg@4,D_proc(q4)@4,pf_sig@5,
     D_sig(q5)@5,nodeproc@5,postq@5,postg@5,D_proc(q5)@5,phys@5,postp@5,D_phys(q5)@5,pf_sig@6,
     D_sig(q6)@6,nodeproc@6,postq@6,postg@6,D_proc(q6)@6,pf_sig@7,resume@7]
dproc_delay=[0:5] dsig_delay=[0:5] dproc_before_sig=true dproc_after_sig=false
gmarks=[pf_sig@1,a(q1)@1,b(q1)@1,pf_sig@2,a(q2)@2,b(q2)@2,…] group_delay=[0:12]
group_before_sig=true resume=resume@7 resume_after_sig=true
```

Reading it as a timeline (all entries between two consecutive signals belong to the same
frame window):

| step | entry | meaning |
|---|---|---|
| 1 | `D_sig(q_k)` | a `call_deferred` queued from the **previous** signal listener runs before this frame's node `_process` pass |
| 2 | `nodeproc@k` | the node `_process` callback |
| 3 | `postq@k`, `postg@k` | logged **immediately after** the `call_deferred` / `call_group_flags(DEFERRED)` calls — they precede the callbacks, so the calls did **not** run synchronously |
| 4 | `D_proc(q_k)@k` | the deferred callback — same frame window, **before the signal** |
| 5 | `phys@k`, `postp@k`, `D_phys(q_k)@k` | the physics tick(s) and their deferred flush, also before the signal |
| 6 | `pf_sig@(k+1)` | the `process_frame` signal is emitted **after** those flushes |
| 7 | `resume@(k+1)` | the `await process_frame` continuation resumes **at** the signal, i.e. **after** the flush |

The `postq`/`postg` controls matter: they rule out the trivial alternative explanation
(synchronous execution inside the queue call). The `group_*` keys show the deferred
**group** call uses the same flush points as `call_deferred`.

### 2.2 It is not a mode artifact

The decisive keys are **identical in all 6 modes × 3 reps** (bucket `LAW` in
`runs/analyze_r97b.json`): `dproc_before_sig=true`, `dproc_after_sig=false`,
`dproc_delay=[0:5]`, `dsig_delay=[0:5]`, `group_before_sig=true`, `group_delay=[0:12]`,
`resume_after_sig=true`. The `seq` payload itself differs only by how many `phys` entries
fit into a frame (2 at ff30, 1 at ff60, ~60 at ff1).

### 2.3 Why the scout's payload could not have shown it

`_arm_defer_ladder` and `_arm_defer_order` keep the deferred callback in a **separate**
array (`DFNODE.log` → `df_log=…` / `df=[…]`) from the phase log (`ladder=…` /
`frame2=[queued,pf_sig,resume2]`). The two arrays are never interleaved, so
`defer_order`'s `frame2=[queued,pf_sig,resume2] | df=[cd]` is consistent with **either**
flush position. The scout's L10 sentence — *"a deferred call queued anywhere in the frame
runs after the `process_frame` signal, in the same idle frame"* — is an **unmeasured
inference**, and its universal quantifier is false for `_process`- and
`_physics_process`-queued calls (measured above). The continuation half of L10
(`await process_frame` resumes at/after the signal) **is** confirmed (`resume_after_sig`,
`frame1=[pf_sig,resume]` in the scout's own payload).

### 2.4 The frame shape around it (clean control, no deferred calls)

`frame_shape` (`runs/ff60/r97b_frame_shape.rep1.out`):

```
seq=[nodeproc@2,postq@2,postg@2,D_proc(q2)@2,phys@2,postp@2,D_phys(q2)@2,pf_sig@3,
     nodeproc@3,…,pf_sig@4,nodeproc@4,…,phys@4,…,pf_sig@5,nodeproc@5,…]
proc_before_sig=true  phys_before_sig=true  proc_before_phys=true
```

So inside one signal-bounded frame window the node `_process` pass comes **before** the
physics tick(s) in this build (`proc_before_phys=true` at ff30/ff60/ff120/ff1; in quiet/load
the same when a tick falls in the window). A minimal scratch run with the engine counters
(`--fixed-fps 60`, not a receipt) confirms the ordering and the counter motion:

```
pf_sig pf=0 ph=1 | resume pf=0 ph=1 | nodeproc pf=0 ph=1 | phys pf=1 ph=2 | pf_sig pf=1 ph=2
```

`Engine.get_process_frames()` advances between the node `_process` pass and the physics
tick, and the `process_frame` signal carries the post-increment value — i.e. the signal is
emitted **after** the physics phase of the window. Mechanism **[?]** (no engine source on
this host); the observable is **[M]** and mode-stable.

**Consequence for authors [I]:** "the deferred call lands after `process_frame`" is the
wrong mental model. A `call_deferred`/`call_group_flags(DEFERRED)` issued from `_process`
or `_physics_process` is already executed when the frame's `process_frame` listeners and
`await process_frame` continuations run; a call issued *from* a signal listener or from a
deferred callback is served before the next frame's `_process`.

---

## 3. L1/L2 confirmed — and the priority mode that is not there

### 3.1 Order is a read-time tree view, not a stored list

`runs/quiet/r97b_order_ticks.rep1.out` (6-node construction, `add_to_group` in the shuffled
order `c,a,ch,d,b,p`, sampled every frame and every tick, then `move_child(a, end)`):

```
add_order=[c,a,ch,d,b,p] t0_read=a,b,c,d,p,ch t0_eq_dfs=true
p1_idle_n=23 p1_idle_distinct=1 p1_idle_cycle=1 p1_idle_vec=a,b,c,d,p,ch
p1_icall_distinct=1 p1_call_eq_read=true
p1_phys_n=11 p1_phys_distinct=1 p1_phys_cycle=1 p1_phys_vec=a,b,c,d,p,ch
after_move_read=b,c,d,p,ch,a after_move_eq_dfs=true
p2_idle_n=24 p2_idle_distinct=1 p2_idle_vec=b,c,d,p,ch,a p2_idle_eq_moved=true
p2_call_eq_read=true read_eq_dfs=true
```

- **One distinct vector per phase** — no r95-style tick-phase cycle, no drift across 23
  idle frames or 11 physics ticks (the counts themselves are host-coupled; the **vectors**
  are not).
- The vector follows a tree move at read time and never lags it.
- The `call_group` invocation order always equals the read order (`p1_call_eq_read`,
  `p2_call_eq_read`).

`r97b_order_churn` (secondary probe, quiet/ff60/load — 16/16 keys LAW): 30 frames of
`remove_from_group` → read → `add_to_group` → read with `move_child` every 5th frame gives
**58/58** samples equal to the DFS member order, 12 distinct vectors (the tree really is
reordered), and a full empty + reverse re-add returns tree order
(`readd_rev=b,c,d,p,ch,a`, `readd_rev_eq_dfs=true`). **[A]** for any "lazily re-sorted
stored list" model.

### 3.2 The priority modes: armed, live, and irrelevant to groups

`runs/quiet/r97b_order_priority.rep1.out`:

```
base_read=a,b,c,d base_call=[a,b,c,d] base_call_rev=[d,c,b,a]
prio_available=true prio_get=100/-100/50/0 prio_proc_order=[pb,pd,pc,pa]
gprio_get=100/-100/50/0 prio_read=a,b,c,d prio_call=[a,b,c,d] prio_call_rev=[d,c,b,a]
tgo_available=true tgo_get=3/1/2/0 tgo_read=a,b,c,d tgo_call=[a,b,c,d] tgo_call_rev=[d,c,b,a]
after_move_read=d,a,b,c after_move_eq_dfs=true after_move_call=[d,a,b,c]
```

- The `_process` control proves the priorities are **live**: four sibling nodes with
  priorities `pa=100, pb=-100, pc=50, pd=0` process in the order `[pb, pd, pc, pa]`, i.e.
  **ascending** priority (lowest first) in this build — the opposite of the documented
  "higher priority runs first" phrasing. Side finding, **[M]**, worth a hazard note.
- With those same priorities on group members, `get_nodes_in_group` **and** `call_group`
  keep returning pure tree order (`[a,b,c,d]`, reverse `[d,c,b,a]`).
- `process_thread_group_order` (censused by the scout, never armed) likewise does not
  touch group reads or group calls.

**[A]** for a "priority-sorted group call" mode; **[M]** for the L2 law.

---

## 4. L3 sharpened: the snapshot is **ordered**, and it survives tree surgery

`runs/quiet/r97b_defer_capture_order.rep1.out` (all 26 keys LAW across 6 modes × 3 reps):

```
fwd_queue_read=a,b,c,d            fwd_flush_read=d,a,b,c        (move_child(d,0) between queue and flush)
fwd_call=[a@0,b@0,c@0,d@0]        fwd_call_eq_queue=true  fwd_call_eq_flush=false
rev_queue_read=e,f,g              rev_flush_read=g,e,f
rev_call=[g@2,f@2,e@2]            rev_call_eq_queue_rev=true  rev_call_eq_flush_rev=false
mut_queue_read=h,j,k              mut_call=[j@4,k@4]  mut_read_after=i  mut_k_valid=false
det_queue_read=m,n,o              det_flush_read=o,n  det_call=[m@6,n@6,o@6]
setg_queue_read=q1                setg_join_pos=(0.0,0.0)  setg_old_pos=(5.0,5.0)
nested_call=[r1!@10,r1@10]
callmut_before=s1,s2,s3           callmut_call=[s1@12,s2@12,s3@12]  callmut_after=s1,s3,s4
```

- **Ordered snapshot [M]:** the invocation order is the **queue-time tree order**, not the
  flush-time one — for the forward and the `REVERSE` variants (the reverse call is the
  reverse of the *queue* list, not of the flush list).
- **Tree surgery [M]:** a member removed from the tree (`m`) and a member reparented into a
  different subtree (`n`) are both still called, in queue-time order (`det_call=[m,n,o]`),
  while the flush-time read is `o,n`.
- **Lifecycle [M]:** removed-after-queue and `queue_free`d members are called; a joiner is
  not (`mut_read_after=i`); `free()` drops the call; `set_group_flags(DEFERRED)` writes only
  queue-time members (`q2` stays at `(0,0)`).
- **Nested [M]:** a deferred group call queued from **inside** the deferred flush runs in
  the **same** flush (`nested_call=[r1!@10,r1@10]`, same clock stamp) — matching the
  scout's `nested`/`nested_t1` for `call_deferred`.
- **NEW — the direct call is also a snapshot [M]** (the scout's §9.5 gap): `s1` removes
  `s2` and adds `s4` while `call_group("g10","mark_mut")` is running; `s2` **is** still
  called (`callmut_call=[s1,s2,s3]`) and `s4` is **not** (`callmut_after=s1,s3,s4`). The
  member list is resolved once, at call time, for direct and deferred forms alike.

---

## 5. `await physics_frame` and the fixed-fps prediction (scout §9.1)

`runs/*/r97b_phys_await.rep1.out` (24 awaits per receipt):

| mode | `await_dph` | `await_dpf` (idle frames skipped) | `await_same_frame` | `phys_defer_same_frame` |
|---|---|---|---|---|
| quiet | `[1:24]` | `[2:15,3:9]` (rep3 `[1:1,2:14,3:9]`) | 0 | true |
| load | `[1:24]` | `[2:14,3:10]` (rep2 `[1:1,…]`) | 0 | true |
| ff30 | `[1:24]` | `[0:12,1:12]` | **12** | true |
| ff60 | `[1:24]` | `[1:24]` | 0 | true |
| ff120 | `[1:24]` | `[1:1,2:23]` | 0 | true |
| ff1 | `[1:24]` | `[0:23,1:1]` | **23** | true |

- **The physics advance is deterministic** in every mode (`await_dph=[1:24]`): one
  `physics_frame` emission per awaited tick, no skipped/merged ticks.
- **The idle-frame index is not made deterministic by `--fixed-fps`** in general: ff30
  yields its own bimodal `0/1` split, ff120 a `1/2` split, ff1 a `0/1` split; **only ff60
  (1 idle : 1 physics) is deterministic** (`[1:24]`). The scout's prediction in §9.1 is
  therefore **[A] falsified as stated**, and the correct author rule is "the index is a
  function of the idle:physics ratio, not of the `--fixed-fps` flag".
- `phys_defer_same_frame=true` (LAW, all 6 modes) confirms the scout's in-frame claim: a
  deferred call queued from a `physics_frame` continuation lands in the same frame window.

---

## 6. Secondary arms

### 6.1 `order_churn` — no stored-list drift

```
t0=a,b,c,d,p,ch t0_eq_dfs=true
churn_samples=58 churn_distinct=12 churn_dfs_ok=58 churn_v1_ok=29 churn_v2_ok=29 churn_mism=none
churn_dfs_all=true after_churn=b,c,d,p,ch,a after_churn_eq_dfs=true
emptied= readd_rev=b,c,d,p,ch,a readd_rev_eq_dfs=true
```

Identical in `quiet`, `ff60` and `load` (16/16 keys LAW). Every read — mid-churn and after
a full empty + reverse re-add — equals the depth-first member order. **[A]** for any
"insertion list that only re-sorts on some engine event" model, which is the shape r95
found for the physics broadphase; groups do not have it.

### 6.2 `unique_boundary` — where the `UNIQUE` key dies

```
seq=[a@2,pf_sig@3,a@3,pf_sig@4,a@4,pf_sig@5]   segs=[a@2,a@3,a@4,]   mark_n=6
```

Identical in `quiet`, `ff60`, `load` (4/4 keys LAW). The node queues the **same**
`GROUP_CALL_UNIQUE|GROUP_CALL_DEFERRED` call twice from `_process` (collapses to one
invocation — scout's L4 confirmed), and the `process_frame` listener queues the same call
again in the same frame epoch: **still one invocation per frame-epoch**. So the key is not
cleared by the flush that serves it; it lives for the **frame epoch** (`pf_sig` window), not
for the flush batch. Authors who re-queue the same "unique" call after the flush point and
expect a second invocation get none.

---

## 7. Row portability — the author-facing deliverable

The scout's 12 cells were re-run on the **frozen** probe
(`4dd18e10e84f0da2…`, byte-identical to `corpus/live/r97-scout/probes/stree_lattice.gd`)
under all six modes:

- **12/12 cells byte-identical in all 6 modes** — `out_uniq=1 err_uniq=1 pass_uniq=1
  rc=[0] errB=[0]` everywhere; the cross-mode comparison prints
  `IDENTICAL in all modes` for every `scout_*` cell (`runs/analysis.txt`).
- **`ROWS` (full-line) and `ROWS_PREFIX`: `checked=36 rejected=0` in each of the six
  modes** → **216/216 accepted each**, `rejected=[]`, with the production
  `classify_process` extracted by AST from `corpus/fixtures/run_battery.py` (segment
  sha256 `749fa0607e7707e6…`, the same segment r89–r95 pinned).
- This is the opposite of the r94 `cpu_pause` result (3/57 rejections at `--fixed-fps 30`):
  no r97 row is mode-coupled, including the frame-bound `defer_order` / `defer_slots` /
  `defer_ladder` / `scene_probe` cells (frame counts inside them are **relative**, so the
  physics/idle ratio does not move them).

**Verdict:** the 12 rows are safe to ship **as-is** on this host; the scout's
`ROWS_PREFIX` recommendation remains the robust form for the four vector-bearing cells, and
its "do not pin `phys_*` frame indices" rule is confirmed (the indices are mode-coupled
even though the two booleans are LAW).

---

## 8. Mode matrix (stability + mode coupling)

Per-cell stability per mode is `runs/analysis.txt`; the full per-key buckets are in
`runs/analyze_r97b.json`. Summary:

| cell | reps/mode | within-mode | across modes |
|---|---|---|---|
| `scout_*` (12 cells) | 3 × 6 | byte-stable (12/12) | **identical in all 6 modes** |
| `r97b_order_ticks` | 3 × 6 | LAW except the tick counts | 26 LAW, 1 MODE (`p2_phys_n`), 1 BOTH (`p1_phys_n`) |
| `r97b_order_priority` | 3 × 6 | byte-stable | 20/20 LAW |
| `r97b_defer_capture_order` | 3 × 6 | byte-stable | 26/26 LAW |
| `r97b_defer_phase` | 3 × 6 | the 7 ordering keys LAW; `seq` varies with the phys ratio | 18 LAW, 1 MODE, 6 BOTH |
| `r97b_frame_shape` | 3 × 6 | `n_nodeproc`, `n_sig`, `proc_before_sig` LAW | 3 LAW, 5 BOTH (phys counts; `phys_before_sig`/`proc_before_phys` read `false` in reps where **no** phys entry landed in the window — an artifact of the empty set, not a mode flip) |
| `r97b_phys_await` | 3 × 6 | `await_dph`, `await_n`, `phys_defer_same_frame` LAW | 3 LAW, 1 MODE, 6 BOTH |
| `r97b_order_churn` | 3 × 3 | byte-stable | 16/16 LAW |
| `r97b_unique_boundary` | 3 × 3 | byte-stable | 4/4 LAW |

**Frame shape per mode [M]** (`phys_await`'s 59-process-frame window, `pf=59` in every
mode; the `frame_shape` cell's 4-frame window gives 0.25/0.50, 0.00–0.50, 2.00, 1.00, 0.50,
59.75 respectively):

| mode | `ph` (reps) | ticks/frame |
|---|---|---|
| quiet | 27, 29 | 0.46–0.49 (host-coupled) |
| load | 26, 28 | 0.44–0.47 |
| ff30 | 118 | 2.00 |
| ff60 | 59 | 1.00 |
| ff120 | 29 | 0.49 |
| ff1 | 3598 | **60.98** |

`--fixed-fps 1` does **not** hang or stall: all 54 ff1 cells completed `rc=0` within the
25 s bound, and the mode is a *simulation-time accelerator* (~60 physics ticks per idle
frame, no 8-step clamp observed on this host) — a useful contrast with the r94
`Engine.fixed_fps = 1` particle stall, which was a different lever.

---

## 9. Delegated `labrat` result

Frozen `probeParent` dispatched **exactly one** read-only `ufo-labrat` (L2, non-executable)
with the bounded hypothesis in §0. It could not execute godot (its seat has no shell — the
same null-execution class the r91/r95/r97 scouts recorded) and said so honestly; it read
the 18 `r97b_defer_phase` receipts (all present, `{quiet,load,ff30,ff60,ff120,ff1}` ×
`rep{1,2,3}`) and checked per file: (a) a `D_proc(qV)@V` after `nodeproc@V` and before
`pf_sig@(V+1)`; (b) `postq@V`/`postg@V` strictly between them; (c) `resume@` after the last
`pf_sig@`; (d) the PASS tokens.

Result: **CONFIRMED, 18/18 on every check, failures none** — the literal substring
`nodeproc@V,postq@V,postg@V,D_proc(qV)@V` occurs 5× per file (frames v2–v6), every seq ends
`…,pf_sig@7,resume@7]`, `dproc_before_sig=true`/`dproc_after_sig=false` in 18/18,
`dproc_delay=[0:5]` in 18/18, and the adversarial pattern `pf_sig@\d+,D_proc` (a deferred
callback landing after its own frame-closing signal) matches **0** files. It also noted
that the ff1 seqs carry ~40 `phys@V,postp@V,D_phys(qV)@V` triplets per frame window —
consistent with the measured tick/frame ratio, not a contradiction. One probe-hygiene note
came back: the `v*_pre`/`v*_post` keys are *derived* views of `seq` and must not be pinned
separately (they are already excluded from the decisive keys — `seq`,
`dproc_before_sig`, `dproc_after_sig`, `resume_after_sig`). No second dispatch.

---

## 10. Hazards for the author (updated from the scout's list)

1. **Deferred group calls capture at queue time — and in order** (L3, sharpened). Reordering
   the tree between the queue and the flush does **not** change who is called or in what
   order; a member removed from the tree, reparented, `queue_free`d, or removed from the
   group is still called; a node that joins later is not.
2. **A direct `call_group` is also a snapshot** (new). Mutating the group from inside a
   member's callback cannot suppress the call for the members already resolved, and cannot
   add a newly joined member to the current call.
3. **`call_deferred` from `_process`/`_physics_process` runs before that frame's
   `process_frame` signal** (new, refutes L10). Code that waits on `process_frame` (or
   `await process_frame`) to observe a deferred effect sees it already applied — the
   opposite of the scout's L10 phrasing. Calls queued from a signal listener or from a
   deferred callback are served before the next frame's `_process`.
4. **The `GROUP_CALL_UNIQUE` key is frame-epoch scoped, not flush-batch scoped** (new).
   Re-queueing the identical call after the flush point inside the same frame does **not**
   produce a second invocation.
5. **`process_priority` reorders `_process` callbacks but not groups** (new negative
   result) — and the measured `_process` order is **ascending** priority (lowest first),
   which is the reverse of the documented phrasing. Do not use `process_priority` to steer
   `call_group` order.
6. **`--fixed-fps` does not make frame-bound probes deterministic** (corrects scout §9.1):
   only a 1:1 idle:physics ratio does. Authoring a probe against a fixed-fps harness still
   needs an envelope if the ratio is not 1:1.
7. **The r97 rows are portable** (new, positive): unlike r94's `cpu_pause`, no r97 row
   changes verdict under 12-hog load or `--fixed-fps` 1/30/60/120.

---

## 11. Falsification list

| # | claim (starting assumption) | verdict | evidence |
|---|---|---|---|
| F1 | the scout's L10 order "process → `process_frame` → deferred flush" holds for every queue context | **FALSIFIED [A]** | `seq` + `postq`/`postg` controls, all 6 modes |
| F2 | a deferred group call re-derives its invocation order at flush time | **FALSIFIED [A]** | `fwd_call_eq_queue=true`, `fwd_call_eq_flush=false` (and the REVERSE pair) |
| F3 | a direct `call_group` sees group mutations made during the call | **FALSIFIED [A]** | `callmut_call=[s1,s2,s3]` with `callmut_after=s1,s3,s4` |
| F4 | `process_priority` / `process_thread_group_order` steer group order | **FALSIFIED [A]** | `prio_call`/`tgo_call` = tree order while the `_process` control reorders |
| F5 | a `--fixed-fps` run makes the `await physics_frame` index deterministic | **FALSIFIED as stated [A]** | ff30 `[0:12,1:12]`, ff120 `[1:1,2:23]`, ff1 `[0:23,1:1]`; only ff60 `[1:24]` |
| F6 | the group order could drift across ticks (r95 lesson) | **NOT FALSIFIED** | 1 distinct vector over 23 frames + 11 ticks, 58/58 churn samples = DFS order |
| F7 | the group order could lag a `move_child` by a frame | **NOT FALSIFIED** (it tracks immediately) | `after_move_read` == `after_move_dfs` == `p2_idle_vec` |
| F8 | the deferred snapshot might be a live set re-read at flush | **NOT FALSIFIED** (it is an ordered snapshot) | detach/reparent/remove/join blocks |
| F9 | `UNIQUE|DEFERRED`'s key might die at each flush | **FALSIFIED [A]** | one mark per frame-epoch with the listener and `_process` queueing in the same epoch |
| F10 | the 12 rows might be mode-coupled (r94 `cpu_pause` lesson) | **FALSIFIED [A]** | 12/12 cells byte-identical in 6 modes; 216/216 + 216/216 row acceptances |
| F11 | the deferred flush might be synchronous | **FALSIFIED [A]** | `postq`/`postg` precede the callback entries |
| F12 | `--fixed-fps 1` is a hang (r94 particle lesson) | **FALSIFIED for this lattice [A]** | 54/54 ff1 cells rc=0, ~60 ticks/frame |

---

## 12. Remaining unknowns / not measured

1. **Engine-side mechanism** of the two flush points and of the process-before-physics
   window order — **[?]** (no engine source tree on this host); the observables are **[M]**
   and identical in all six modes.
2. **Threaded scene processing** (`set_process_thread_group`, `*_deferred_thread_group`,
   `get/set_process_thread_group*`) — censused, still not armed (needs a `Thread` harness);
   the *ordering* fields (`set_process_thread_group_order`) were armed and are inert for
   groups (§3.2).
3. **`UNIQUE` key internals** — the epoch-scoped lifetime is measured; whether the key is
   stored per group+method+args or per callable **[?]**.
4. **`reload_current_scene` / `unload_current_scene`**, `SceneTreeTimer` interaction with
   the two flush points, `CONNECT_REFERENCE_COUNTED` N≥3 — still open (scout §9.2/§9.3/§9.6).
5. **`--fixed-fps 1` tick/frame ratio** measured 59.75–60.98 ticks per idle frame; whether
   that is exactly 60 plus the startup tick **[?]**.
6. **Rendered behaviour** — irrelevant here (headless).

---

## 13. Host cleanup and evidence index

- Every launch was `timeout -s KILL 25`-bounded; the bound was never hit
  (`rc=[0]` for all 342 receipts, no `137`). No seat-owned godot process was left running
  (`ps` at the end shows only other lanes' godot processes: g3d `r93` battery, `r96b_phase`,
  `r90-author`). The `load` and `load_extra` batches started 12 own `yes` hogs each and
  killed exactly those PIDs (`own_hogs_killed=12` twice; `host_yes_remaining` 64/80 —
  other lanes' hogs untouched, no `pkill`).
- No tracked file modified; no commit; the only tracked modification in `git status` is the
  concurrent lane's pre-existing `corpus/fixtures/run_battery.py`.

| artefact | content |
|---|---|
| `corpus/live/r97-boundary/probes/r97b_lattice.gd` | frozen attack probe, 6 arms, sha256 `f37961f879c5b75a…` — the revision behind the 324-receipt matrix |
| `corpus/live/r97-boundary/probes/r97b_extra.gd` | secondary probe, 2 arms, sha256 `c801556147ae29d6…` — 18 receipts |
| `corpus/live/r97-boundary/run_modes.sh` / `run_extra.sh` | mode drivers (25 s KILL bound, PID-tracked hogs) |
| `corpus/live/r97-boundary/runs/{quiet,load,ff30,ff60,ff120,ff1}/*.{out,err,rc}` | 342 receipts + `hogs.txt` / `hogs_extra.txt` |
| `corpus/live/r97-boundary/runs/analyze_r97b.json` / `analysis.txt` | per-cell stability, cross-mode buckets, row replay |
| `corpus/live/r97-boundary/analyze_r97b.py` | analyzer (AST-extracted production `classify_process`, segment sha `749fa060…`) |
| `corpus/live/r97-boundary/proj/` | launch project: fixture byte-copy `8de8b3af…`, both probes, the **frozen scout probe** `4dd18e10…`, scene files |
| `corpus/live/r97-boundary/RECEIPTS.md` / `manifest.sha256` | receipt map + hashes |

**Reproduce:** `bash run_modes.sh quiet 3 && bash run_modes.sh load 3 && bash run_modes.sh
ff30 3 && bash run_modes.sh ff60 3 && bash run_modes.sh ff120 3 && bash run_modes.sh ff1 3
&& bash run_extra.sh quiet 3 && bash run_extra.sh ff60 3 && bash run_extra.sh load 3 &&
python3 analyze_r97b.py`
