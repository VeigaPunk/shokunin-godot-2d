# game-dev-2d round 95 — boundary (r95-boundary): the multi-hit ORDER is a tick-phase cycle of length **k(k−1)**; the scout's two "insertion-order" order rows are label permutations, and its "layout" row is a co-presence artifact

Seat `BOUNDARY` (LEAF) | lane `r95-boundary` | round 95 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`, 60 tps,
GodotPhysics2D. Repo `~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start
`2c4b1ff` (*r94 scout*). Attack corpus: **261 fresh runs, 8 batches, all `rc=0`, all stderr 0 B,
0 timeouts**. Own probe `probes/r95b_order.gd` (12 arms, sha256 `4f7e945e1b16f241…`), launch
projects `proj/` (fixtures byte-copy `8de8b3af9cc737ed…`) and `proj_thr/` (same + threaded
physics), driver `run_matrix.sh`, analyzer `analyze_r95b.py`.

**No git mutation, no tracked file written, no commit.** Writes are this report (new, untracked)
and `corpus/live/r95-boundary/**` only. `git status --porcelain` shows only the pre-existing
` M corpus/fixtures/run_battery.py` (a concurrent lane's, no r95b token) plus other lanes'
untracked churn.

**Frozen probeParent disclosure.** The seat dispatched **exactly one** read-only `ufo-labrat`
(L2) with one bounded hypothesis: *"every canonical + loadtest receipt for `dss_order_core` /
`dss_order_core_rev` exists and all same-cell PASS lines are byte-identical to the report's
quoted vectors"*. Result: **evidence chain CONFIRMED** (9 `.out` per cell — 6 canonical + 3
loadtest — one sha256 each, all `.rc=0`, all `.err` empty, vectors verbatim as quoted; the
labrat's own arithmetic guess of 6 was wrong, the report's 6+3 was right). No second dispatch.
The labrat could not execute godot (no shell in its seat) — the same null-execution class the
r91/r95 scouts recorded; it did read and hash receipts, which is what the hypothesis needed.

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host; every
symbol-level statement below is grounded in receipt text or fixture source read directly
(`corpus/live/r95-scout/probes/dss_lattice.gd`). No rename/definition work was required — the
attack is behavioral, not symbol-aware.

**The host is shared.** loadavg 72 → 150 for the whole session (other lanes' batteries and
`yes` blocks: 48 → 112 host hogs). `quiet` below means **"no hogs added by this seat"**, never an
idle host. The seat's own 16 hogs were killed by PID (never `pkill`); other lanes' were untouched.

**Legend:** **[M]** measured (fresh process); **[A]** refutation/ablation; **[I]** inference;
**[U]** unstable payload; **[?]** unknown.

---

## 0. What I ran

| # | batch | conditions | runs | loadavg start→end |
|---|---|---|---|---|
| 1 | `quiet` | 60 tps, no seat hogs | 132 | 72.21 → ~76 |
| 2 | `load` | 60 tps + **16 seat hogs** | 53 | 121.31 → 153.41 |
| 3 | `ff1` | `--fixed-fps 1` | 8 | 146.99 |
| 4 | `ff30` | `--fixed-fps 30` | 16 | 147.91 |
| 5 | `ff120` | `--fixed-fps 120` | 16 | 147.05 |
| 6 | `thr` | `physics/2d/run_on_separate_thread=true` | 13 | 147.41 |
| 7 | `label` | 60 tps (scout `--rev` replication) | 8 | 149.50 |
| 8 | `extra` | 60 tps (period scan k=2…10) | 15 | 150.01 |

58 cells in the quiet batch (69 distinct cell ids across the 8 batches); per-cell receipt stability and cross-condition comparison in
`runs/analyze_r95b.json` + `analysis.txt`. **Every cell except `procwait` is byte-stable within
its batch and identical across all batches it appears in** — including `--fixed-fps` 1/30/120 and
threaded physics (§8). `procwait` (process-frame awaits) is the one unstable cell (§9).

**Attack design.** The scout sampled the order at exactly one tick phase (2 physics frames after
insertion) and never varied the phase, never separated *label* from *geometry* in its `--rev`
variants, and compared "layout" across two piles present in the *same* process. Each arm below
isolates one of those.

---

## 1. Verdict table

| # | scout claim (r95-scout.md) | verdict | one-line evidence |
|---|---|---|---|
| 1 | "repeat queries, no mutation → identical ×3 … order is a stable read" (§3.7b) | **TRUE in-frame, REFUTED across frames [A]** | the vector changes on **every** physics tick: `t0=0,1,2,3,4 … t2=4,0,2,3,1 … t5=3,0,1,2,4`; 20 distinct phases for k=5 |
| 2 | "byte-identical over 6 canonical + 3 loadtest reps … deterministic across processes for a frozen construction" (§3.7b, §6.1) | **CONFIRMED, strengthened [M]** | 261 runs: identical under 16-hog load, `--fixed-fps` 1/30/120, **threaded physics**, and 32-body allocation-history perturbations; instance ids byte-identical across all 7 batches |
| 3 | "insertion-order dependent" evidenced by `--rev` (§3.4 F6, §3.7b F13) | **conclusion CONFIRMED, evidence REFUTED [A]** | `--rev` changes **labels only** (positions are index-based): its vector differs from canon's only by relabelling, and its *position* vector equals canon's exactly; a fixed-map creation-order test gives **8/8 distinct** ladders |
| 4 | "layout dependent … same relative geometry translated +1000 y → different vector" (§3.7b F16) | **REFUTED as a layout effect [A]** | 14/14 isolated translations (x ∈ {±0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, ±1000}, y +1000) return the **identical 8-tick ladder**; the scout's effect is co-presence, not translation |
| 5 | "perturbed by unrelated mutation" (F14) | **CONFIRMED with clean isolation [M]** | A alone at t2 `[e,a,c,d,b]`; A at t4 **with** B present `[e,a,c,b,d]` ≠ A alone at t4 `[e,a,b,c,d]` |
| 6 | "not a function of the set" (F15) | **CONFIRMED + sharpened [M]** | the **free order** changes the surviving order for the same final set (`ab` vs `ba` differ at every sampled tick), and the post-free cycle follows k(k−1) |
| 7 | "point query vs shape query … identical vector — the two families share the order" (§3.7b) | **CONDITIONAL: true for a single-layer pile, FALSE with a CanvasLayer collider [A]** | `layers_k0` `pt_eq_sh=true`; `layers_k1` `pt_eq_sh=false`, `sh_len=6` (shape sees the layer body, the point query does not) |
| 8 | "sorted **set** of hits … the only semantic invariant" (§3.7b) | **REFUTED above the cap [A]** | 40-body pile: 3 creation orders → **3 different** 32-hit subsets; `set32_distinct=5` (the subset changes at every sampled tick) |
| 9 | "the 17 rows are load-stable" (§6.1, 150/150) | **CONFIRMED [M]** | 16 own hogs at loadavg 136–153: every ordering cell byte-identical to its quiet receipt |
| 10 | (brief) "check scheduler-sensitivity everywhere" | **mode-proof for tick-awaiting harnesses; a process-frame harness is nondeterministic even quiet [A]** | ff1/ff30/ff120/thr receipts identical; `procwait` has 2–3 distinct payloads per batch and 5 across modes |
| 11 | "Threaded physics … query *ordering* under the threaded window was not re-measured" (scout §8) | **now measured: unchanged [M]** | 13 runs with `physics/2d/run_on_separate_thread=true` (`sep2d=true`): identical ladder and vectors |
| 12 | (new) the drift is not arbitrary — **it is a cycle** | **NEW LAW [M]** | order cycle length = **k(k−1)** ticks for k = 2,3,4,5,6,7,8,10 (2,6,12,20,30,42,56,90), two layouts, and on post-free 3-/4-body piles |

---

## 2. The headline law: the order is a **tick-phase cycle of length k(k−1)** **[M]**

### 2.1 The scout pinned one phase of a 20-phase cycle

`canon` (5 bodies 40×40 at x=0,8,16,24,32, query (16,0), cap 32), verbatim
`runs/quiet/canon.rep1.out` — `ladder` is the **position permutation** (tag→fixed-x index):

```
PASS r95b_order canon add_order=[a,b,c,d,e] map=[a@0,b@8,c@16,d@24,e@32]
 ladder=[t0:0,1,2,3,4;t1:4,1,2,3,0;t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t5:3,0,1,2,4;
         t6:3,4,1,2,0;t7:3,4,0,2,1;t8:3,4,0,1,2;t9:2,4,0,1,3;t10:2,3,0,1,4;t11:2,3,4,1,0;
         t12:2,3,4,0,1;t13:1,3,4,0,2;t14:1,2,4,0,3;t15:1,2,3,0,4;t16:1,2,3,4,0;
         t17:0,2,3,4,1;t18:0,1,3,4,2;t19:0,1,2,4,3;t20:0,1,2,3,4;t21:4,1,2,3,0;
         t22:4,0,2,3,1;…;t32:2,3,4,0,1;t36:1,2,3,4,0;t40:0,1,2,3,4;t48:3,4,0,1,2;t56:1,2,3,4,0;t64:4,0,1,2,3]
 distinct_ticks=20 cycle_len_dense=20 t2_vec=[e#0,a#0,c#0,d#0,b#0] t64_vec=[e#0,a#0,b#0,c#0,d#0]
 pt_stable_interleaved=true t2_pt_eq_sh=true
```

- **t0 is insertion order** (`0,1,2,3,4`) — a phase the scout never sampled.
- **t2 is exactly the scout's pinned row** (`[e#0,a#0,c#0,d#0,b#0]`, `rep1=rep2=rep3`).
- **t20 == t0 and t22 == t2**: the cycle is closed at 20 ticks; every one of the 20 phases is
  distinct (`distinct_ticks=20`), and the sequence is still cycling at t64.
- **Within one frame the order is a stable read** (`pt_stable_interleaved=true`, three point
  queries interleaved with a shape query) — the scout's "repeat queries" row is correct *for one
  frame*; it does not extend across ticks.

### 2.2 The cycle length is k(k−1), k = colliders in the queried region

`periodx` (k bodies 40×40, all containing (16,0), queried every tick until the cycle closes):

| k | measured `cycle_len` | `distinct_ticks` | k(k−1) | receipt |
|---|---|---|---|---|
| 2 | 2 | 2 | 2 | `periodx_k2` |
| 3 | 6 | 6 | 6 | `periodx_k3` |
| 4 | 12 | 12 | 12 | `periodx_k4`, `period_k4` |
| 5 | 20 | 20 | 20 | `periodx_k5`, `periodx_k5s8`, `period_k5`, `canon` |
| 6 | 30 | 30 | 30 | `periodx_k6` |
| 7 | 42 | 42 | 42 | `periodx_k7` |
| 8 | 56 | 56 | 56 | `periodx_k8` |
| 10 | 90 | 90 | 90 | `periodx_k10` |

- **Two layouts agree**: `periodx_k5` (spacing 4, centred on 16) and `periodx_k5s8`
  (spacing 8, x = 0…32 — the scout's own pile) both give `cycle_len=20` and the **same phase-2
  vector** `[p4,p0,p2,p3,p1]` ( = `[e,a,c,d,b]` with the scout's tags).
- **Independent confirmations on other constructions**: post-free 3-body piles (`free_ab/ac/ba/ca`)
  satisfy `ladder[t] == ladder[t+6]` and post-free 4-body piles (`free_a…free_e`)
  `ladder[t] == ladder[t+12]` — checked in `analysis.txt` (`free/layers period cross-check`).
- **The count is the colliders present, not the hits returned**: `layers_k1` (5 pile bodies +
  1 `CanvasLayer` body at the same spot) returns 5 hits but cycles at **30 = 6·5**
  (`ladder[2] == ladder[32]`).

**What this does to the scout's row [I→M]:** the pinned `dss_lattice_order_core` vector is the
**t = 2 phase of a 20-phase cycle**; the row is reproducible because its own probe fixes the
tick count (`await _frames(2)`). It is not a function of "construction + layout" alone — the
tick phase is a third coordinate. Mechanism of the cycle (broadphase cell re-insertion per
step) is **[I]**; the observable is **[M]**.

---

## 3. The `--rev` order rows are **label permutations**, not add-order permutations **[A]**

The scout's `_pile()` places body *i* at `Vector2(i * 8, 0)` — position depends on the **loop
index**, and `--rev` reverses the **tag list**. So `order_core` and `order_core_rev` are the
*same physical construction* (five bodies inserted at 0,8,16,24,32 in that order); only the node
names move. The `dss_lattice_point_cap_rev` row and the `pile_b`/`pile_rev` rows share this
pattern (all index-positioned); `after_readd` is a genuine free + re-add.

**Direct replication** (`scoutrev` = the scout's `--rev` construction, verbatim
`runs/label/scoutrev.rep1.out`):

```
PASS r95b_order scoutrev add_order=[e,d,c,b,a] map=[e@0,d@8,c@16,b@24,a@32]
 t2_vec=[a#0,e#0,c#0,b#0,d#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000]
 scout_row_rev_t2_vec=[a#0,e#0,c#0,b#0,d#0] t2_vec_matches_scout_row=true t2_relpos_equals_canon=true
```

- The tag vector reproduces the scout's `dss_lattice_order_core_rev` row **exactly** — and the
  *position* vector equals `canon`'s t2 position vector (`t2_relpos_equals_canon=true`).
- The full ladder matches `perm0`'s under the label mirror i → 4−i at all 9 sampled ticks
  (`scoutrev_ladder_mirrors_perm0.all_equal=true`, `runs/analyze_r95b.json`).
- ⇒ **the two rows measure one construction, and their difference is naming, not ordering.**

**The clean test the scout lacked** — `perm*`: tag→position map **fixed**, creation order
permuted (8 permutations), position-normalised output:

| cell | creation order | t2 position vector |
|---|---|---|
| `perm0` | a,b,c,d,e | 32,0,16,24,8 |
| `perm1` | e,d,c,b,a | 0,32,16,8,24 |
| `perm2` | b,c,a,e,d | 0,8,32,24,16 |
| `perm3` | c,a,e,d,b | 16,32,8,24,0 |
| `perm4` | a,c,b,e,d | 32,0,8,24,16 |
| `perm5` | d,a,b,e,c | 24,32,8,16,0 |
| `perm6` | e,a,c,d,b | 32,8,16,24,0 |
| `perm7` | b,a,d,c,e | 8,32,24,16,0 |

**8/8 distinct ladders and 8/8 distinct t2 position vectors** → the scout's *conclusion*
("insertion-order dependent") is **correct**, but its `--rev` evidence does not support it, and
the `order_core_rev` row is not a second test. (The add-order dependence is real: the creation
sequence changes the ids and the insertion history the broadphase records.)

---

## 4. "Layout dependent" is a **co-presence** artifact **[A]**

**Isolated translation** (`celloff`, one pile per process, ladder positions normalised by the
offset): **14/14 offsets return the identical 8-tick ladder** —
x ∈ {0, ±0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, ±1000} and y = +1000. Example:

```
celloff off=1000.0000  ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1;t64:4,0,1,2,3]
celloff off=0.2500    ladder=[t2:4,0,2,3,1;…;t64:4,0,1,2,3]   (identical)
celloff off=-1000.0   ladder=[t2:4,0,2,3,1;…;t64:4,0,1,2,3]   (identical)
celloff off=0 offy=1000.0  ladder=[…]                        (identical)
```

**Co-presence** (`twopiles` = the scout's exact sequence: pile A at y=0, then pile B at y=1000):

```
PASS r95b_order twopiles
 a_t2_vec=[e#0,a#0,c#0,d#0,b#0]                      <- A alone, t2 = canon
 a_t4_with_b_vec=[e#0,a#0,c#0,b#0,d#0]               <- A at t4 WITH B present
 b_t2_vec=[e2#0,a2#0,b2#0,c2#0,d2#0]                 <- B at t2 = the scout's pile_b row, verbatim
```

- `canon`'s A-alone t4 is `[e,a,b,c,d]`; with B present it is `[e,a,c,b,d]` → **B's presence
  perturbs A** (the scout's own `insert_perturbs=true`, now isolated).
- B at t2 with A present is `[e2,a2,b2,c2,d2]` (the scout's `pile_b`), whereas **B alone at
  y=+1000** (`celloff_y1000`) is `[e,a,c,d,b]` — i.e. the same phase as an untranslated pile.
- ⇒ the scout's `layout_changes_order=true` key misattributes a **co-presence** effect to
  **layout**. F16 is refuted as stated; F14 survives with a cleaner control.
- **The scout's own receipts already contain the counter-example**: `pile_b` (y=1000) is
  `[e2,a2,b2,c2,d2]` and `pile_rev` (y=2000) is `[a3,e3,d3,c3,b3]`; with `_pile()`'s index
  positions both map to the **same position vector `[32,0,8,16,24]`** across a 1000-unit y
  translation. Their `layout_changes_order=true` came from comparing pile B against pile A
  (a different *phase/co-presence* state), not from the translation.

---

## 5. Free-order permutations and the post-free cycle **[M]**

Same final set, different free order (`free_order_ab` = free a then b, `free_order_ba` = free b
then a; both leave {c,d,e}):

```
free freed=[a,b] ladder=[t1:4,3,2;t2:2,3,4;t3:2,4,3;t4:3,4,2;t6:4,2,3;t8:2,3,4;t16:3,4,2]
free freed=[b,a] ladder=[t1:3,4,2;t2:2,4,3;t3:2,3,4;t4:4,3,2;t6:3,2,4;t8:2,4,3;t16:4,3,2]
```

- The two ladders differ at **every** sampled tick (t1…t16) — free order is a real coordinate,
  and the final vector is not a function of the final set.
- Each variant is nonetheless **byte-stable** over its reps and batches (2 reps quiet + 2 load),
  and the surviving 3-body cycle obeys k(k−1) = 6 (`t2 == t8`).
- `readd_a`/`readd_c`: a fresh body inserted at a freed body's position takes the freed body's
  slot in the cycle (`f` appears in the pidx at the same relative place), and the 5-body cycle
  resumes (period 20).

---

## 6. Above the cap the **set** is not invariant **[A]**

`cap40` (40 bodies 200×40 at x = 1000+2i, query (1000,0), default cap 32; three creation orders):

```
n32=32 n64=40 n0=0                       (cap 0 = zero results, default truncates — scout's row confirmed)
set32_t2 distinct across the 3 orders = 3
set32_distinct = 5                       (the 32-hit subset changes at every sampled tick t2,4,8,16,32)
```

- The three t2 subsets are disjoint in their omissions: `perm0` drops `{t1, t32…t38}`,
  `perm1` drops `{t1…t7, t38}`, `perm2` drops `{t8, t10, t15, t22, t27, t29, t34, t39}` — **the
  "only semantic invariant" fails above the cap**: the returned set is a phase- and
  construction-dependent 32-prefix of the full 40.
- Below the cap the set is invariant (all five `canon`-family variants return the same 5 tags);
  the invariant is therefore **"set of hits, if n ≤ max_results"**, not "set of hits".

---

## 7. Point vs shape order agreement is layer-conditional **[A]**

| cell | `pt0_t2_eq_sh` | `sh_len` | note |
|---|---|---|---|
| `layers_k0` | **true** | 5 | single-layer pile: the two families share the order (scout's row holds) |
| `layers_k1` | **false** | 6 | pile + one `CanvasLayer` body at the same spot: shape sees `clb#0`, the point query (`canvas_instance_id=0`) does not |

- `layers_k1` `sh_vec=[e#0,a#0,c#0,d#0,clb#0,b#0]` vs `pt0_vec=[e#0,a#0,c#0,d#0,b#0]` — the
  families **interleave differently**, so "the two families share the order" is not a general
  law; it is a single-canvas-layer special case.
- The invisible-to-the-query layer body also changes the **drift path** from t6 on and the cycle
  length to 30 (6 colliders) — a collider the query cannot return still perturbs the returned
  order. Consistent with §4 (co-presence) and the scout's `shape_layer_agnostic` row.

---

## 8. What survived every determinism attack (quiet / load / fixed-fps / threaded) **[M]**

| attack | runs | result |
|---|---|---|
| 16-hog load, loadavg 121→153 | 53 | every cell byte-identical to quiet (`cross-batch uniq_sig=1`) |
| `--fixed-fps 1` (≈60 ticks/process frame) | 8 | `canon`, `perm0`, `celloff_x0`, `period_k5` identical |
| `--fixed-fps 30` / `--fixed-fps 120` | 32 | identical |
| `physics/2d/run_on_separate_thread=true` | 13 | identical (scout §8 unknown now closed) |
| 1…32 far-away bodies created **and freed** before the pile (RID/id history) | 16 | ladder identical to `canon` for k=0,1,2,3,5,8,13,32 |
| instance ids | all | **byte-identical across all 7 batches** (`[26424116681,26491225550,…]`) |
| rigid solver positions at t10 | 5 | byte-identical across quiet + load (`[15.9999,14.8732]`) |

- **The allocation-history attack failed in the most informative way**: `warm_k1` changes the
  instance ids (`[26575111627,…]`) yet returns the *identical* ladder — so the order is **not a
  function of the id values**, only of the insertion sequence/geometry/phase.
- Leaving the far bodies **alive** (`warm_keep8/64`) does change the vector
  (`[a,e,b,c,d]`) — the broadphase-table-pressure effect the scout measured as `insert_perturbs`.

---

## 9. The two real instabilities **[U]**

1. **`procwait` — a harness that awaits process frames instead of physics ticks cannot pin a
   vector.** Physics ticks per `await process_frame`:

   | batch | `pf_per_procawait` | payloads within the batch |
   |---|---|---|
   | `quiet` | `[3,4,4,4]` | **2 distinct** |
   | `load` | `[6,7,7,7]` | **3 distinct** |
   | `ff1` | `[59,119,179,238]` | 2 distinct |
   | `ff30` | `[0,2,4,6]` | 4 distinct |
   | `ff120` | `[0,0,1,1]` | 2 distinct |

   The same source line lands on a different tick phase per rep and per mode → different vector.
   **This is the scheduler-sensitivity the brief asks about: it is not the clock mode that breaks
   the ordering claim, it is the tick-counting discipline.** `await physics_frame` is stable
   everywhere; `await process_frame` is unstable even quiet.
2. **`warm_keep{8,64}`** (unrelated live colliders) — deterministic but a different vector; the
   pinned rows are valid only for a frozen scene composition.

---

## 10. What an author must know now (no shipping decision here)

1. **The four order-vector rows gate today but are phase-locked.** `dss_lattice_order_core`,
   `…_rev`, `dss_lattice_point_cap`, `…_cap_rev` pin the t = 2 phase. They are reproducible
   (261/261) *because the probe awaits exactly 2 physics frames*; any change to the await count,
   to a process-frame await, or to the collider count in the queried region changes them. If a
   row is kept, its phase must be stated in the row's own text (or replaced by the `ladder` +
   `cycle_len` pair, which encodes the law rather than one phase).
2. **`dss_lattice_order_core_rev` is not a second test** — it is the same construction with
   permuted names (§3). If a rev-style row is wanted, permute the **creation order with a fixed
   tag→position map** (`perm1` = 0,32,16,8,24 position vector).
3. **`layout_changes_order=true` misattributes co-presence to layout** (§4). The isolated
   translation result is `layout_changes_order=false` for ±1000 x/y and for sub-cell offsets;
   the true key is `insert_perturbs` (co-presence), which the scout also measured.
4. **`repeat_stable` is a same-frame statement.** Add a phase ladder (`t0…t20`) if the row is to
   describe the law; `t0` is insertion order, `t2` is the pinned vector, `t20 == t0`.
5. **Above the cap the set is not invariant** (§6): pin `n32=32`, `n64=40`, `n0=0` and a
   phase-tagged prefix, never "the set".
6. **Point/shape order agreement is layer-conditional** (§7); the canvas-layer body perturbs the
   default-layer drift path and the cycle length (k counts colliders, not returned hits).
7. **Threaded physics and fixed-fps are order-neutral** (§8) for tick-awaiting harnesses — the
   r91 nav-style "fixed-fps breaks the claim" does **not** reproduce here, and the scout's
   declared §8 unknown (threaded ordering) is now closed.

---

## 11. Remaining risks / not measured

- **Mechanism [I]**: no engine source on this host; "the broadphase re-inserts elements on each
  physics step and the cell/pair containers are traversed in a rotation" is the best fit for a
  cycle of exactly k(k−1) with k = colliders. Not proven; the cycle length itself is **[M]**.
- **k(k−1) was measured for point queries** on overlapping rectangles; `intersect_shape` and
  `intersect_ray` multi-hit families were only spot-checked (`t2_pt_eq_sh`, §7). A ray/`cast_motion`
  cycle was not scanned.
- **Non-rect shapes / rotated / server-tier bodies**: the cycle and its length were not measured
  there (the scout's alt-construction lane used mixed shapes; I did not re-run it).
- **Bodies with multiple shapes** (one hit per shape) and areas: not scanned for phase/period.
- **`k` for colliders that do not overlap the query cell** (e.g. live far bodies) changes the
  vector (`warm_keep8`) but I did not derive a period for that case.
- **The host was never idle** (loadavg 72–150); "quiet" is seat-relative. Absolute values are
  host-conditioned, though the *invariance* results are the point.
- **`--fixed-fps` with `await process_frame`** is unstable by construction (§9); a battery cell
  written that way will not gate on any order vector.

---

## 12. Host cleanup

- **0 timeouts** (no rc=137), 0 non-zero rc, 0 B stderr across 261 runs; no probe process left
  running after any batch (`pgrep -fa r95b_order` → none).
- The seat's 16 `yes` hogs were killed **by PID** (`kill "$p"` in an EXIT trap + explicit
  `stop_load`); `pkill` was never used, so other lanes' hog blocks (48 → 112 during the session)
  were untouched.
- No tracked file written, no commit; `git status --porcelain` shows only the pre-existing
  ` M corpus/fixtures/run_battery.py` (concurrent lane) and untracked `corpus/live/*`.
- `manifest.sha256` covers every artefact under `corpus/live/r95-boundary/` (1062 files,
  itself excluded).

---

## 13. Evidence index

All under `corpus/live/r95-boundary/`; `manifest.sha256` covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| **attack probe, 15 arms** | `probes/r95b_order.gd` | `4f7e945e1b16f241` |
| launch project (fixtures byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| threaded-physics project | `proj_thr/project.godot` | `eb2bda39ce82cd5a` |
| driver (8 batches) | `run_matrix.sh` | `91283b6f0cd0ac42` |
| analyzer → json/text | `analyze_r95b.py` → `runs/analyze_r95b.json`, `analysis.txt` | `9b85499c1c8f851e` |
| batch receipts (261 × 4 files) | `runs/{quiet,load,ff1,ff30,ff120,thr,label,extra}/` | `manifest.sha256` |
| per-batch conditions/loadavg | `runs/*/rc-summary.txt` | `manifest.sha256` |

Reproduce: `bash run_matrix.sh quiet && … && bash run_matrix.sh extra && python3 analyze_r95b.py`
(expect: every cell `key_uniq=1` except `procwait`; `canon` ladder `t2:4,0,2,3,1` … `t20:0,1,2,3,4`;
`periodx` `cycle_len = k(k−1)`).
