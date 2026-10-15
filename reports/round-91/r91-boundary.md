# game-dev-2d round 91 — boundary (r91-boundary): the Navigation2D lattice under quiet / 16-hog load / `--fixed-fps` 30/60/120

Seat `BOUNDARY` (LEAF) | lane `r91-boundary` | round 91 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
GodotPhysics2D. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at session start
**`520ed6d`** (r90 boundary). Probe corpus: byte-copy of the r91 scout's frozen
`nav_lattice.gd` (sha256 `efb496e5…`) as `probes/scout_nav_lattice.gd`, plus the seat's own
`probes/r91b_nav.gd` and `probes/r91b_agent_diag.gd`.

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r91-boundary/**` only. `git status --porcelain` shows only the
pre-existing ` M corpus/fixtures/run_battery.py` (concurrent r88-fold lane) and other lanes'
untracked churn; none of it this seat's.

**Frozen probeParent disclosure.** The seat dispatched **exactly one** `ufo-labrat` (L2,
read-only) with one bounded hypothesis: reproduce the scout's teardown crash class from the
scout's *own* `discover.gd`. The labrat seat had **no exec tool** and returned a null result
(9/9 rows "NOT RUN — no exec capability"), wrote nothing, spawned nothing. Recorded, not
silently omitted; no second dispatch was made. The seat then ran the same hypothesis itself
(`runs/dc_*`, §6.2) with the scout's frozen probe.

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host; every
`file:line` below is engine-emitted `at:` backtrace text. Probe authoring was direct file
writes (the fallback); no symbol-aware rename was needed.

**The host is shared.** Concurrent lanes held the box at **loadavg 58–118** for the whole
session. `quiet` below means **"no hogs added by this seat"**, never an idle host. Every batch
records `loadavg_start/end` in `runs/rc-summary.txt`. The seat's own `yes` hogs were killed
after each batch (`stop_load` + EXIT trap); other lanes' hogs were left untouched.

**Legend:** **[M]** measured (fresh process); **[A]** ablation/refutation; **[I]** inference;
**[U]** unstable (payloads differ); **[?]** unknown.

---

## 0. What I ran

**403 fresh godot runs, 9 batches, 0 timeouts** (346 rc=0, 57 rc=134 expected SIGABRT, 0
rc=137). All `timeout -s KILL 25`-bounded; stdout/stderr split into per-cell sidecars plus
`.rc`/`.wall`. Full batch table and replay commands: `RECEIPTS.md`; machine summary:
`runs/analyze_r91b.json` + `analysis.txt`.

| batch | conditions | runs | loadavg start→end |
|---|---|---|---|
| `quiet` | 60 tps, no seat hogs | 60 | 58.51 → 72.42 |
| `load` | 60 tps + **16 seat hogs** | 100 | 76.28 → 93.33 |
| `ff30` | `--fixed-fps 30` | 60 | 89.78 (start) |
| `ff120` | `--fixed-fps 120` | 60 | 112.57 (start) |
| `ff120load` | `--fixed-fps 120` + 16 seat hogs | 60 | 96.03 → 100.07 |
| `quiet2` | 60 tps repeat window | 18 | 100.07 → 118.17 |
| `ab` | paired default vs ff30/ff60/ff120, interleaved | 24 | 117.36 → 106.80 |
| `disc` | scout's own `discover.gd` crash arms | 9 | 106.80 → 98.33 |
| `diag2` | v9 triple + bent lane, quiet + 16 hogs | 12 | 95.02 → 88.63 |

Cells: 5 scout-verbatim (`sv_sync/region/agent/avoid/bake`), 5 attack
(`b_gate/change/agent/avoid/bake`), 6 teardown arms, 6 agent diagnostics
(`d_v1/v5/v7/v8/v9/bent`), 3 scout discovery arms (`dc_navfree2/5/6`).

**Scope.** The attack covers exactly the five claim families the assignment names: the
sync-gate ladder, 2–4-frame change application, the bake routes, the avoidance callback +
teardown crash class, and the agent `fin`/`reached` split. `sv_census`/`sv_path`/`sv_query`/
`sv_link` were **not** re-run; their canonical receipts stand unchallenged here.

---

## 1. Verdict table

| # | attack | verdict | one-line evidence |
|---|---|---|---|
| 1 | sync gate `iteration_id >= 2` (+ reach) | **CONFIRMED as a law; the ladder is NOT a constant** | `gate_first == first_reach` and no reach-before-`iter>=2` in **every** synced run (20/20 `b_gate` + 17/17 `sv_sync` ladders + 24/24 paired `ab`); but `first_reach` ranges **4–10** at 60 tps (two windows), **5–43** at ff30, and is **never ≤60** in ff120 3/3 and ff120load 2/3 |
| 2 | async=false initial sync = "f1" | **CONFIRMED at 60 tps (2 in 1-based = scout f1); FALSIFIED as general** | 60 tps: `async_first_reach=2` in 8/8; ff30: 40 (one run); ff120: ≥40 / never in 2/3; ff120load: 26 in one run |
| 3 | live changes apply in 2–4 frames | **CONFIRMED at 60 tps (1–3 frames, 0 misses in 56 lever-runs); FALSIFIED under `--fixed-fps`** | 60 tps quiet+load: every one of 7 levers settles ≤3 frames (8 runs × 7); ff30/ff120: **27 lever-runs never apply within 24 frames**, settles hit the 24-frame poll bound |
| 4 | bake routes (outline + modern, holes, collider-only, orphan refusal) | **CONFIRMED (CPU side, all conditions); server-side path half is not fixed-fps-portable** | `outline_polys=4/verts=8`, `baked_polys=4/verts=8`, `collider_only_polys=0`, orphan ERROR + deprecation WARNING in **34/34** bake runs; but `iter_b ∈ {0,1,2}` and path fields empty when the map sync stalls |
| 5 | avoidance callback cadence + closing-speed invariant | **cadence CONFIRMED; the scout's range FALSIFIED** | exactly 1 callback/agent/frame (`per_a=per_b=[1,1,1,1,1]`) in the 20 `b_avoid` runs incl. ff30/ff120; `n_a=21` in all 37 `b_avoid`+`sv_avoid` runs; `\|a\|+\|b\| ∈ [19.835, 20.0000]` (100 samples) — never >20, but **below** the scout's `[19.849,19.883]` floor and hitting exactly `20.0000` |
| 6 | avoidance teardown crash class (rc=134) | **CONFIRMED in every condition; one qualifier added** | 51/51 seat crash arms → rc=134 + `double free or corruption`; 51/51 clean arms → rc=0; scout's own `navfree2/5` → 134 ×6, `navfree6` → 0 ×3; **`leak_clean` (leaked agent, cleared callback) exits clean** — the exit crash needs a *live* callback |
| 7 | agent `fin`/`reached` do not flip in the same frame | **FALSIFIED as a temporal law — it is a query-order artifact** | scout-exact `d_v1` → `reached_at=-1` 20/20; fin-read-first `d_v5` → `reached_at=28` in all 16 non-vacuous runs; single-frame triple read `d_v9`: `r1=false fin=true r2=true` 6/6; `b_agent split=0` in 15/20 (all non-vacuous) |
| 8 | `distance_to_target()` is straight-line, not path length | **CONFIRMED with a discriminating lane** | bent L path: `dist=226.2742` vs `plen=282.8427` (Δ=`56.5685`) ×6 |
| 9 | `--fixed-fps` is a benign harness variation | **NEW MODE: it is not** | the ratio control `--fixed-fps 60` (1 idle : 1 physics, like default) stalls too (`first_reach` 4,6,7,20,31,49); `def` in the same interleaved window is 4,5,5,4,5,5 |

---

## 2. Attack 1 — the sync-gate ladder (`iteration_id >= 2`) **[M]**

### 2.1 The law holds; the timing does not

Across **61 gate runs** (20 `b_gate` matrix + 17 `sv_sync` + 24 paired `ab`), all conditions:

- **No reach-before-`iter>=2` in any run** — no path was ever reachable while
  `map_get_iteration_id(map) < 2`. The gate is *necessary* (checked on the 17 `sv_sync`
  ladders + 20 `b_gate` `reach_before_iter2` fields + 24 `ab` runs).
- **`gate_first == first_reach` in every synced run** (36/36 `b_gate`+`ab` where a reach was
  found, 12/12 `sv_sync` ladders that show one) — the conjunction
  `iteration_id >= 2 AND reach` is never stricter than reachability itself. The
  gate is *sufficient* (no wasted wait). In every synced run the map iteration first reads
  `>=2` in the *same* physics frame the path becomes live (`frames_iter2_to_reach = 0`,
  20/20). Of the 61 runs, 48 showed a reach inside their window (the other 13 are the
  fixed-fps stalls below).
- The ordering `iter=0 → iter=1 → iter=2 & reach` was preserved in 100 % of runs.

But the **frame numbers are window- and mode-dependent** (1-based physics frames):

| window | `first_iter1` | `first_iter2` | `first_reach` |
|---|---|---|---|
| `quiet` (loadavg 58→72) | 4–7 | 8–9 | **8, 8, 9** |
| `quiet2` (loadavg 100→118) | 4–8 | 6–10 | **6, 9, 10** |
| `load` (+16 hogs, loadavg 76→93) | 2–6 | 4–8 | **4, 6, 7, 7, 8** |
| `ab def` (loadavg 117→107) | 4–5 | 4–5 | **4, 5, 5, 4, 5, 5** |
| `ff30` | 3 | 5, 7, **43** | **5, 7, 43** |
| `ff120` | — | — | **−1, −1, −1** |
| `ff120load` | 4 / — | 7 / — | **7, −1, −1** |

The scout's "typical 4–6 frames" is reproducible in some windows (`ab def`: 4–5; `sv_sync`
quiet: 3–4) but **not a constant**: 8–10 in this host's ambient contention, and the tail
extends far beyond their "up to >10 in one rep". Verbatim, the 43-frame run:

```
PASS r91b_nav gate pre_iter=0 pre_regions=0 pre_path=[] pre_closest=(0.0000,0.0000)
 first_iter1=3 first_iter2=43 first_reach=43 gate_first=43 reach_before_iter2=false
 frames_iter2_to_reach=0 pf_per_await=1.000 proc_per_await=0.512
 trace=[f1:0/0/0,f2:0/0/0,f3:1/1/0,f4:1/1/0,…,f42:1/1/0,f43:2/1/1]
 async_first_reach=3 async_chg_same=false async_chg_t=-1 async_old_gone_t=-1
 async_sync3=2 async_dis_same=true async_dis_t=-1
```
(`runs/f30_b_gate.rep3.out` — the map iteration id sits at **1** for 40 physics frames
before the second iteration lands.)

And the ff120 stall (3/3 in the ff120 batch, 2/3 in ff120load):
```
PASS r91b_nav gate … first_iter1=-1 first_iter2=-1 first_reach=-1 gate_first=-1
 reach_before_iter2=false frames_iter2_to_reach=-1 pf_per_await=0.000 …
 trace=[f1:0/0/0,f2:0/0/0,f3:0/0/0,…] async_first_reach=3 …
```
(`runs/f120_b_gate.rep1.out` — 60 physics frames, the map never leaves `iter=0`; the
async=false map in the same process synced in 3.)

**Consequence for the scout's recipe.** `_await_sync(..., max_frames=24)` **silently
proceeds on a stale map** in all of these runs (it returns `24` and the caller reads an
unsynced map: empty paths, `iter` counters at 0/1). The scout's own `settle_a/settle_b`
receipts show this: **8 bake runs ended with `settle_*=24`** and empty path fields
(`f30_sv_bake.rep1/2`, `f120_sv_bake.rep2/3`, `f120l_b_bake.rep2/3`, …). The pinned rows are
still safe (a mismatch rejects loudly), but the *probe pattern* is not: the bound must be
treated as a failure, not a settle.

### 2.2 `use_async_iterations=false` is not a "f1" guarantee **[A]**

At 60 tps the scout's claim reproduces exactly: `async_first_reach = 2` (1-based) in
**8/8** quiet+load runs — their `first_reach_sync=1` is 0-based, same frame. But:

- `ff30`: 2, 2, 3 in the matrix; **40** in the interleaved pair 6 (`ab6_f30`).
- `ff120`: 3 in one matrix run, **−1** (never within 40) in two; the paired window: 2, 2, 4,
  **−1**, 3, 2.
- `ff120load`: **26** (one run), 3, 3.

So the "fast path" (`async=false`) can be the *stalled* path: at ff120 the async=false map
needed 26–≥40 physics frames while an async=true map in the same process synced in 5–7.

### 2.3 The async=false live-change timing the scout left unmeasured (§8) **[M]**

| lever (async=false) | 60 tps quiet | 60 tps load | ff30 | ff120 | ff120load |
|---|---|---|---|---|---|
| transform → new path live | 2,2,2 | 2,1,1,2,1 | 1,1,**−1** | −1,1,−1 | 2,2,2 |
| transform → old path gone | 1,1,1 | 1×5 | 1,1,−1 | −1,1,−1 | 1,1,1 |
| disable → old path gone | 2,2,2 | 2,2,1,1,1 | **−1,−1,−1** | **−1,−1,−1** | **−1,−1,−1** |

At 60 tps the async=false path behaves like the async=true path (1–2 frames, stale
same-frame read). Under `--fixed-fps` the **disable never applies within 30 physics frames**
in **9/9** ff30+ff120+ff120load runs.

---

## 3. Attack 2 — "live changes are applied 2–4 physics frames later" **[M]/[A]**

Seven independent levers were polled frame-by-frame to settle (`POLL=24`; `−1` = not applied
within the window).

**At 60 tps the law holds, with the bound on the fast side:** quiet+load = **56 lever-runs
(8 runs × 7 levers), `max_t = 3`, zero non-applications**:

```
quiet : tr=2/3/3 dis=2/3/3 cost=3/3/3 lay=3/3/3 poly=3/3/3 link=2/2/2 gap=2/1/2
load  : tr=3×5 dis=3×5 cost=3×5 lay=3×5 poly=3×5 link=2×5 gap=2,2,2,1,1
```
(`runs/q_b_change.rep*.out`, `runs/l_b_change.rep*.out`; also `sv_sync`'s
`chg_same=false chg_settled=true dis_same=true dis_settled=false` held 8/8.)

**Under `--fixed-fps` it is falsified.** 27 lever-runs never applied within 24 frames:

```
f30_b_change.rep1: tr_same_new=false tr_same_old=false tr_t=-1 dis_same_reach=false dis_t=1
  base_top=true cost_same=false cost_t=-1 lay_same_top=true lay_t=13 poly_same_top=false
  poly_t=1 link_same=false link_t=1 gap_same=false gap_t=15
  settle1=24 settle2=13 settle3=24 settle4=24
```
(`runs/f30_b_change.rep1.out`; rep2/rep3 similar — `tr_t=-1` in **3/3**, `cost_t=-1` 2/3,
`lay_t ∈ {7,13,−1}`, `poly_t ∈ {1,−1}`, `gap_t ∈ {15,−1}`.) At ff120: `tr_t=-1`, `cost_t=-1`,
`lay_t=-1`, `poly_t=-1` in 3/3, `settle1=24` in 3/3.

**The same-frame asymmetry [U].** The scout's rule "same-frame reads after a write are
stale" holds for the *new* answer (100 % of 60-tps runs: `tr_same_new=false`,
`cost_same=false`, `gap_same=false`), but the *old* answer can already be invalidated:
`tr_same_old=false` and `dis_same_reach=false` occur at 60 tps under load (1/5 `l_b_change`
runs) and dominate at ff30/ff120. I.e. **invalidation is immediate while the rebuild is
deferred** — a pinned "the old path is still served in the same frame" claim is not portable.

One more same-frame exception at 60 tps: `gap_same=true` (the edge-connection-margin
bridging visible at frame 0) in **1/5** `l_b_change` and 1/3 `f120l_b_change` runs —
`map_set_edge_connection_margin` is not strictly non-synchronous.

---

## 4. Attack 3 — the bake routes **[M]**

All **34** bake runs (5 cells × conditions + `sv_bake`), including the stalled ones:

- outline route: `outline_polys=4 outline_verts=8`, hole detour path present when the map
  synced (`hole_across` via `(140,60)/(140,140)`, `hole_straight` via `(60,60)/(140,60)`);
- modern route: `parse_obs=1 parse_trav=0 parse_has=false`, `baked_polys=4 baked_verts=8`,
  `through/around/outside` matching the scout's erosion values;
- `collider_only_polys=0` (silent empty bake) and the orphan refusal ERROR
  (`ERROR: The root node needs to be inside the SceneTree.`) in **100 %** of runs; the
  `make_polygons_from_outlines()` deprecation WARNING likewise.

**The CPU-side bake is mode-independent; the server-side half is not.** Under `--fixed-fps`
the bake's region maps often never sync inside the 24-frame poll, so the *path* fields are
empty even though the polygon counts are exact:

```
f30_b_bake.rep1 : outline=4/8 baked=4/8 collider_only=0 iter_b=1 settle_a=24 settle_b=24
                  hole_across=[] hole_straight=[] through=[] around=[] outside=[]
f120_sv_bake.rep3: iter_b=0 settle_a=24 settle_b=24 through=[] outline=4/8 baked=4/8
```
(`iter_b ∈ {0,1,2}` across ff runs; **2/2/2** in every quiet/load run.)

**Row portability note.** The scout's recommended `nav_lattice_bake` prefix
(`author-rows.py.txt` line 14) includes **`iter_b=2`** — a synchronization counter — *and*
the exact path geometry. That row is byte-stable at 60 tps (all 16 quiet/load bake runs here
agree) but it **rejects under `--fixed-fps`** whenever `iter_b ∈ {0,1}` or the map stalls.
This contradicts the scout's own §6.2 rule ("do not pin counters") for a counter they left
inside the prefix; it is a portability defect of the row, not a 60-tps falsification.

---

## 5. Attack 4 — avoidance cadence, invariant, teardown **[M]/[A]**

### 5.1 Cadence — confirmed in every condition

`per_a=per_b=[1,1,1,1,1]` in all 20 `b_avoid` runs, `n_a=n_b=21` (16 warmup + 5 measured),
`warm_n_a=16` in **all 37** `b_avoid`+`sv_avoid` runs, including ff30/ff120 where the map was
stalled. The "once per agent per frame" law is solid.

### 5.2 The closing-speed invariant is `≤ 20`, not `[19.849,19.883]` **[A]**

All 100 measured-frame sums (20 `b_avoid` runs × 5 frames; the scout's `sv_avoid` prints no
`sums` field), by condition:

| cond | min | max | sample values (rounded) |
|---|---|---|---|
| quiet | 19.8380 | 20.0000 | 19.838…20.0000 |
| quiet2 | 19.8470 | 19.8540 | 19.847…19.854 |
| load | 19.8430 | 20.0000 | 19.843…20.0000 |
| ff30 | 19.8390 | 20.0000 | 19.839…20.0000 |
| ff120 | 19.8370 | 19.9150 | 19.837…19.915 |
| ff120load | 19.8350 | 19.9180 | 19.835…19.918 |

**Never above 20.0000** (the ORCA bound `(r_a+r_b)/τ = 20/1.0`), but values **below** the
scout's floor `19.849` occur in 4/6 conditions (down to `19.835`), and the bound itself is
hit exactly (`20.0000`) in quiet/load/ff30. The author rule should be: pin
`sum <= 20.0` (or envelope), never the scout's tight sample range. The per-agent split stays
process-dependent as the scout said (e.g. `vel_a=(14.6450,0) vel_b=(-5.2705,0)` in
`f120_b_avoid.rep1`).

### 5.3 Teardown crash class — deterministic everywhere; one qualifier **[M]**

| arm | operation | quiet | load(5) | ff30 | ff120 | ff120load | verdict |
|---|---|---|---|---|---|---|---|
| `c_noclear` | free agent with live callback | 134×3 | 134×5 | 134×3 | 134×3 | 134×3 | crash |
| `c_clear0` | clear callback, free same frame | 134×3 | 134×5 | 134×3 | 134×3 | 134×3 | crash |
| `c_leak_cb` | live callback, no free, exit | 134×3 | 134×5 | 134×3 | 134×3 | 134×3 | crash |
| `c_clear1` | clear, await 1 frame, free | 0×3 | 0×5 | 0×3 | 0×3 | 0×3 | clean |
| `c_clear2` | clear, await 2 frames, free | 0×3 | 0×5 | 0×3 | 0×3 | 0×3 | clean |
| **`c_leak_clean`** | **cleared callback, no free, exit** | **0×3** | **0×5** | **0×3** | **0×3** | **0×3** | **clean — new mode** |

Every rc=134 run carries `double free or corruption (!prev)` on stderr; every clean arm has
0 B stderr. The scout's "agents leaked at exit crash too" needs the qualifier **"if the
callback is still registered"**: a leaked agent whose callback was cleared exits cleanly
(15/15).

### 5.4 Independent reproduction with the scout's own probe **[M]**

`runs/dc_*` (9 runs, loadavg 98–107, scout's `discover.gd` from `../r91-scout/proj`):

```
dc_navfree2 (clear+free same frame): rc = 134, 134, 134   stderr "double free or corruption"
dc_navfree5 (two agents + callbacks): rc = 134, 134, 134   stderr "double free or corruption"
dc_navfree6 (clear + 1 frame + free): rc =   0,   0,   0   stderr 0 B
```

This is the hypothesis the blocked labrat could not run; the seat ran it as its own bounded
probe.

---

## 6. Attack 5 — the agent `fin`/`reached` split is a query-order artifact **[A]**

The scout's §3.6 measured `reached_at=-1` (fin true, reached false in one readback). The
seat's instrumented lane (fin read before reached) measured **`split=0`** — so the seat
built a controlled matrix of read orders on identical geometry (target `(180,180)`, holder
from `(20,20)`, 8 px/step, `target_desired_distance=8`).

| arm | post-await read order | `reached_at` | runs |
|---|---|---|---|
| `d_v1` scout-exact | `reached` only | **−1** | 20/20 (all conditions) |
| `d_v2` (smoke) | `reached`, then `fin` | **−1** | 2/2 |
| `d_v3` (smoke) | scout minus `s_idx` pre-read | **−1** | 2/2 |
| `d_v4` (smoke) | scout minus all pre-reads | **−1** | 2/2 |
| `d_v5` | `fin`, then `reached` | **28** | 16/20; `−1` in the 3 vacuous ff30 runs + 1 ff120load run |
| `d_v6` (smoke) | full pre-reads, `fin` then `reached` | **28** | 2/2 |
| `d_v7` | `reached`, `reached`, then `fin` | **−1** | 17/17 |
| `d_v8` | `fin`, `fin`, then `reached` | **28** (12), **42** (1 ff120load), `−1` (4) | 17 |
| **`d_v9`** | **`reached`, `fin`, `reached`** | **−1** + triple note | 6/6 |
| `b_agent` (seat) | `fin` then `reached` | split=0 | 15/20 (the other 5 are vacuous ff runs) |
| `sv_agent` (scout) | `reached` only | **−1** | 17/17 |

The single-frame triple read is decisive (6/6, quiet + 16 hogs):
```
PASS r91b_agent_diag arm=v9 … walk_steps=28 reached_at=-1 fin_at=28 fin_same_frame=false
 post_fin=true post_reached=true … note=step=28 r1=false fin=true r2=true
```
**In one and the same frame**, `is_target_reached()` returns `false`, then after
`is_navigation_finished()` returns `true`, the next `is_target_reached()` returns `true`.
`is_navigation_finished()` refreshes the agent state; `is_target_reached()` alone can be one
update stale. `d_v7` (reached ×2) stays false, so repeated `reached` reads do **not** refresh.

**Verdict:** the scout's §3.6 "they do not flip in the same frame" is **FALSIFIED as a
temporal law**; it is a read-order artifact of their probe. The author rule is: read
`is_navigation_finished()` before `is_target_reached()` (or re-read reached after a fin
query). A pinned `reached_at=-1` row would pin the artifact, not the engine.

**The straight-line claim is confirmed with a discriminating lane** (`d_bent`, L navmesh,
target across the corner, 6/6):
```
dist=226.2742  plen=282.8427  delta=56.5685  path=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)]
dist_eq_straight=true plen_eq_L=true
```
`distance_to_target()` is the straight-line distance (the scout's straight-path case could
not discriminate; this one does).

**Bimodality under `--fixed-fps`.** The agent lane is either normal or **vacuous**: at ff30
2/3 `sv_agent` runs never became reachable in 60 frames (`settled=(20,20)/false/false/false
walk_steps=60 first_reachable=-1`, `final_target=(0,0)`), and 2/3 `b_agent` runs walked 80
steps with `split=-1`; at ff120load 2/3 `sv_agent` runs failed the same way. The
fin/reached question cannot even be asked in those runs.

---

## 7. Attack 6 — `--fixed-fps` as a mode **[M]/[I]**

The paired, interleaved window (`ab`, loadavg 117→107, 1 rep each) isolates the mode from
window drift:

| pair | `def` | `ff30` | **`ff60`** | `ff120` |
|---|---|---|---|---|
| 1 | fr=4 | 3 | **31** | 7 |
| 2 | fr=5 | 6 | **20** | 3 |
| 3 | fr=5 | **−1** | 6 | 6 |
| 4 | fr=4 | 6 | 4 | 6 |
| 5 | fr=5 | **−1** | 7 | 5 |
| 6 | fr=5 | **−1** | **49** | 7 |

`def` is tight (4–5) in the same window; `ff30`/`ff120` stall intermittently; **`ff60` — the
1:1 ratio control — stalls worst (20, 31, 49)**. Since ff60 has the same idle:physics ratio
as default, the stall tracks **the fixed-fps mode itself** (real-time decoupling), not the
tps ratio. **[I]** The most consistent mechanism is that the NavigationServer's async map
iteration is gated by *real elapsed time*; with `--fixed-fps` the physics-frame clock runs
far ahead of wall time, so a fixed wall-clock delay spans many more physics frames (and,
inversely, this host's heavy ambient load makes each frame slower in real time, which is why
the 60-tps ladder was 4–5 in the loadavg-90 window but 8–10 in the loadavg-58/118 windows).
Unproven; the observable (frame-count laws do not survive fixed-fps) is **[M]**.

**Physics-frame accounting is intact:** `pf_per_await = 1.000` in every gate run;
`proc_per_await` = 0.5 (ff30), 1.0–2.5 (default, window-dependent), 2.0 (ff120) — the
`--fixed-fps` ratio is in effect exactly as documented.

---

## 8. Unstated modes (hunted, all with receipts)

1. **The sync ladder's tail is far wider than "up to >10":** 43 frames (ff30), never ≤60
   (ff120 3/3, ff120load 2/3), 8–10 at 60 tps in busy windows. The scout's 24-frame
   `_await_sync` bound **silently proceeds stale** (8 bake runs with `settle_*=24`).
2. **`--fixed-fps 60` stalls too** (4–49) — the fixed-fps mode, not the tps ratio, is the
   cause (ratio control).
3. **`use_async_iterations=false` is not a fast path under fixed-fps**: 26–40+ frames or
   never (ff120), while async=true maps in the same process synced in 3–7.
4. **Invalidation/rebuild asymmetry:** `tr_same_old=false` / `dis_same_reach=false` at frame
   0 (old answer already invalidated) while the new answer takes 1–3 frames — even at 60 tps
   under load (1/5). "Same-frame reads are stale" is one-sided.
5. **`map_set_edge_connection_margin` can be visible at frame 0** (`gap_same=true`, 1/5 load,
   1/3 ff120load) — not strictly non-synchronous.
6. **The fin/reached "split" is a query-order artifact** (§6) — `is_navigation_finished()`
   refreshes; `is_target_reached()` alone is stale.
7. **`leak_clean`:** a leaked avoidance agent with a *cleared* callback exits cleanly
   (15/15) — the exit crash requires a live callback.
8. **The avoidance invariant is `≤ 20.0`, not `[19.849,19.883]`** — 100 samples in
   `[19.835, 20.0000]`, never above 20, exact bound hit.
9. **The pinned `nav_lattice_bake` prefix contains `iter_b=2`** (a sync counter) and exact
   path geometry — it rejects under `--fixed-fps` (`iter_b ∈ {0,1}`, empty paths) though it
   is byte-stable at 60 tps.
10. **The agent lane (and any nav readback) is bimodal under `--fixed-fps`:** either normal
    (walk 28, split 0) or vacuous (never reachable within 60–80 frames, empty path, empty
    `final_target`). A third shape exists: one ff120load run walked **42** steps
    (`f120l_d_v8.rep1`: `first_reachable=-1 walk_steps=42 reached_at=42 fin_at=42`) — the
    path appeared only during the walk, so the walk length is not a constant either.
11. **`async=false` disable never applies within 30 frames** at ff30/ff120/ff120load
    (9/9) — the one lever that is *slower* under fixed-fps than transform/cost.
12. **Callback cadence is mode-proof** (1/agent/frame in all conditions, including stalled
    maps) — the avoidance server is independent of the map-sync gate.

---

## 9. Remaining risks / not measured

- **Mechanism of the fixed-fps stall is [I]**, not proven (no engine source tree on this
  host). The observable is solid; the "real-time gating" explanation is the best fit for
  the ff60 control and the ambient-load correlation.
- **The host was never idle** (loadavg 58–118, concurrent batteries). Every "quiet" number
  is host-conditioned; the absolute ladder values (4–10 at 60 tps) will move on a quiet box.
- **Not re-tested:** `NavigationAgent2D`-is-a-`Node` (no `position` assignment), links,
  `query_path` lattice, `sv_census`/`sv_path`, region travel/enter-cost steering beyond the
  three levers polled, `map_get_process_info`, threaded navigation,
  `NavigationObstacle2D` avoidance (the obstacle stayed `avoidance_enabled=false`, as in the
  scout's control), `NavigationLink2D` node, `run_on_separate_thread`.
- **`--fixed-fps` is a harness mode**, not a shipping config — but any battery cell that
  boots with it (r86 nested-boot pattern) will read stale/vacuous nav payloads unless the
  sync gate treats `max_frames` exhaustion as failure.
- The one permitted labrat dispatch was blocked (no exec in its seat); its null result is
  recorded and the same hypothesis was reproduced by this seat (`dc_*`).

---

## 10. Host cleanup

- **0 timeouts** (no rc=137); no godot process from this lane remains
  (`pgrep -fa 'r91b_nav|r91b_agent_diag|scout_nav_lattice|discover.gd'` → 0).
- The seat's own `yes` hogs were killed after every batch (`stop_load` + EXIT trap); the
  system-wide `yes` count (12–72, other lanes') was never touched.
- No tracked file written (`git status --porcelain`: only the pre-existing
  ` M corpus/fixtures/run_battery.py` and other lanes' untracked churn). No core files (core
  pattern pipes to systemd-coredump); no `.godot/` cache written into any project dir.
- `manifest.sha256` covers every artefact under `corpus/live/r91-boundary/`.

---

## 11. Evidence index

All under `corpus/live/r91-boundary/`; `manifest.sha256` covers every artefact.

| artefact | path | notes |
|---|---|---|
| scout frozen probe (byte-copy) | `probes/scout_nav_lattice.gd` | sha256 `efb496e5fe08e667…` |
| seat attack probe | `probes/r91b_nav.gd` | arms gate/change/agent/avoid/bake + 6 teardown |
| seat diagnostic probe | `probes/r91b_agent_diag.gd` | v1–v9 + bent |
| launch project | `proj/project.godot` | sha256 `8de8b3af9cc737ed…` |
| driver | `run_matrix.sh` | 9 batches, `timeout -s KILL 25` |
| analyzer → JSON + text | `analyze_r91b.py` → `runs/analyze_r91b.json`, `analysis.txt` | |
| receipts | `runs/*.{out,err,rc,wall}` | 403 runs |
| batch log | `runs/rc-summary.txt` | loadavg per batch, timeout/hog checks |
| scout discovery crash receipts | `runs/dc_navfree{2,5,6}.*` | 9 runs |
| batch/evidence table | `RECEIPTS.md` | |

Key verbatim receipts: `runs/f30_b_gate.rep3.out` (43-frame ladder),
`runs/f120_b_gate.rep1.out` (never-sync), `runs/f30_b_change.rep1.out` (−1 levers),
`runs/f30_sv_sync.rep1.out` (quartet broken), `runs/q_b_change.rep1.out` (60-tps law),
`runs/q_b_avoid.rep1.out` / `runs/f120l_b_avoid.rep1.out` (invariant),
`runs/*_d_v9.rep*.out` (triple read), `runs/*_d_bent.rep*.out` (straight-line),
`runs/q_c_*.out` (teardown matrix), `runs/ab*_*.out` (paired ff control).
