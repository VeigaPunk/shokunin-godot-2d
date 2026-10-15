# game-dev-2d round 98 — boundary (r98-boundary): the `queue_redraw` flush is **per physics step, not per frame** (ff1: 359 draws / 359 ticks / 6 frames; frame-delay control confirms it without `--fixed-fps`); the zero-scale clamp is **1e-5 × parent scale**, not ~2e-5; `clip_children` refusal survives every mode

Seat `BOUNDARY` (LEAF) | lane `r98-boundary` | round 98 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
`RendererDummy`, 60 tps, root viewport 64×64 in `--script` mode.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start **`e741cf8`** (r94 boundary).
Attack corpus: **263 fresh runs, 7 batches, all `rc=0`, 0 timeouts (0 × rc=137)**.
Own probes `probes/r98b_attack.gd` (14 cells), `probes/r98b_rksenum.gd` (one-off);
frozen scout probe byte-copy `probes/scout_canvas_lattice.gd` (sha256
`866480a1aaa0a385…` = the scout's own file); driver `run_matrix.sh`; analyzer
`analyze_r98b.py`. Batches: `quiet` / `load` (16 own hogs) / `--fixed-fps 1,30,120` /
`ff30+load` / `--frame-delay 100` (`slow`, the multi-tick-frame control).

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r98-boundary/**` only. `git status --porcelain` shows only the
pre-existing concurrent-lane churn (` M corpus/fixtures/run_battery.py` and other lanes'
untracked dirs); nothing under `corpus/fixtures/` was touched and the probes were never
copied there.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on
this host; `definition`/`references`/`hover` were **unavailable for every file touched**.
No symbol-level work was required (this is a behavioral attack); every mechanism statement
is marked **[I]** and kept separate from the measurements.

**Legend:** **[M]** measured (fresh process); **[A]** refutation/ablation; **[I]** inference;
**[U]** phase-unstable payload (explained); **[?]** unknown.

---

## 0. What I ran

| # | batch | conditions | runs | loadavg start→end |
|---|---|---|---|---|
| 1 | `quiet` | 60 tps, no seat hogs | 58 | 84.32 → 81.40 |
| 2 | `load` | 60 tps + **16 seat `yes` hogs** | 58 | 81.40 → 92.15 |
| 3 | `ff1` | `--fixed-fps 1` | 29 | 92.15 → 94.56 |
| 4 | `ff30` | `--fixed-fps 30` | 29 | 94.56 → 96.84 |
| 5 | `ff120` | `--fixed-fps 120` | 29 | 96.84 → 96.14 |
| 6 | `ff30load` | `--fixed-fps 30` + 16 hogs | 29 | 96.14 → 101.54 |
| 7 | `slow` | `--frame-delay 100` (no fixed-fps) | 29 | 91.06 → 78.56 |

Each batch runs **both probes**: the scout's frozen 15 cells (`r98_canvas_*`, PASS tag
`canvas_lattice`, so every payload is byte-comparable with the scout's own receipts) and
the 14 attack cells (`r98b_*`). `analyze_r98b.py` gives per-cell/per-key stability and the
scout-receipt comparison.

**Flags [M]:** `SCOUT_DIFF=[]`, `ERR_MISMATCH=[]`, `NONZERO_RC=[]`; `UNSTABLE` only for the
tick-phase keys of `r98b_qflush`/`r98b_qorder`/`r98b_env` in quiet/load (§3);
`MODE_DIFF` only on the two keys that are the finding itself (`coalesce_eq`,
`stag_groups`). Stderr: exactly the expected ERROR lines everywhere (`draw_refusal` 2,
`clip` 1, `clipmatrix` 6 per run, 0 elsewhere).

**Frozen scout probe under all 7 modes [M]:** 15/15 cells byte-identical to the scout's
canonical + loadtest receipts (6 receipts for the two pure cells, 9 for the other 13) and
to each other — including `queue`'s `events_tail=q@pf0|d@pf0|d@pf1|d@pf2|d@pf6|d@pf8|d@pf10|d@pf12`
under `--fixed-fps` and `--frame-delay`. **No r95-style cycle exists in any scout row.**

---

## 1. Verdict table

| # | scout claim (r98-scout.md) | verdict | one-line evidence |
|---|---|---|---|
| 1 | L1 "`queue_redraw()` is an **end-of-frame** coalescing flush; a queue in frame N draws at frame N, **at most once**" | **CONFIRMED for process-step queues; REFUTED-SCOPE for physics-step queues [A]** | ff1: `coalesce_draws=359 ticks_window=359 frames_with_tick=6 coalesce_eq=0 max_draws_per_pf=60`; ff30/ff30load `12/12/6 max=2`; slow `37/37/6 max=7`; quiet/load/ff120 `draws == frames_with_tick max=1` |
| 2 | L1 "a queue from `_process` draws at frame N" | **CONFIRMED all 7 modes [M]** | frozen `queue` cell `proc_same=1 proc_n=1` byte-identical everywhere |
| 3 | L1 same-frame flush (the frame-number claim) | **CONFIRMED all 7 modes [M]** | `same_pf=1 d_pf_delta=0 d_n=1` in every batch |
| 4 | L1 "3 queue calls in one frame → 1 draw" | **CONFIRMED as stated; not the general tick-separated law [M]** | 3 synchronous calls coalesce; 3 calls separated by physics ticks do **not** (ff1 359 draws) |
| 5 | L1 "self-queue from `_draw()` is swallowed" | **CONFIRMED all 7 modes [M]** | `selfq_draws=1` in every batch (incl. ff1, 60 ticks/frame) |
| 6 | L1 "queue then hide before the flush → 0 draws" (hazard #2) | **CONFIRMED as stated; scope widened [A]** | synchronous hide still drops it (frozen `hide_before_flush_n=0` everywhere); a **tick-separated** hide does not: `hide_ticksep_n=1` in all 7 modes, with `hide_span_pf=0` under ff1/ff30/ff30load/slow (same frame, later tick) |
| 7 | L1 hidden/out-of-tree suppression, show/re-add redraw | **CONFIRMED all 7 modes [M]** | `hidden_across_tick_n=0`, `show_after_tick_n=1`; frozen `hidden_n=0 out_n=0 readd_n=1 outadd_n=1` |
| 8 | L3 "`get_transform() == Transform2D(rotation, scale, skew, position)`" | **CONFIRMED for non-degenerate scales (125/125); REFUTED for degenerate scales (75/75 fail) [A]** | `ctor_fail_n=75 ctor_fail_z=75 ctor_fail_nz=0`; `z_tf00=(0.00001000,0.00000000;-0.00000000,0.00001000)` |
| 9 | L3 "the explicit `R·K·S` product matches" (exact `rks=1`) | **CONFIRMED numerically, fragile as an exact pin [M]** | 60/125 non-degenerate combos fail bit-exact; max component diff `4.77e-7` (float32) |
| 10 | L4 "a zero scale reads back as a **~2e-5** epsilon" | **REFUTED as a constant; CONFIRMED as `1e-5 × parent scale` [A]** | `eps_exact=ps=0.001->0.000000010, ps=0.5->0.000005000, ps=1->0.000010000, ps=2->0.000020000, ps=100->0.001000000` |
| 11 | L4 zero-scale angle readbacks (rotation/skew preserved) | **CONFIRMED [M]** | `zero_rot_skew=(0.000020,0.000020)|grot=1.1000|gskew=0.5000` (parent 0.7 + child 0.4; child skew 0.5) |
| 12 | L5 "global setters inverse-compose" | **CONFIRMED (global round-trip ≤1e-4); local readbacks are decompositions, not naive inverses [M]** | non-uniform parent: `gs_local=0.0258`, `gr_local=1.1808 gr_local_skew=0.0258`, `gsc_local=(1.7184,0.7131)`; uniform parent: `gs_local_uniform=0.3000 gr_local_uniform=0.2000` |
| 13 | L9 "`>= MAX` refused with ERROR, previous value kept" | **CONFIRMED + generalized [M]** | `stay99=p0->0,p1->1,p2->2 stay3=1 stay_after_neg=1 stay_repeat=1`; 6 ERROR lines per run in all modes |
| 14 | L9 "negative stored as its uint32 cast (no ERROR)" | **CONFIRMED + extended [M]** | `neg=-1->4294967295,-2->4294967294,-3->4294967293,-5->4294967291,-2147483648->2147483648`; property path `neg_prop=4294967294`; `recover=1`; no ERROR from negatives |
| 15 | F12/§3.14 the context-dependent redraw latch | **CONFIRMED; tick-phase-invariant and one-shot [M]** | `latch_canon 1/0/0`, `t1=1`, `t3=1`, `imm=1`, `second_n=0` in all 7 modes |
| 16 | L6/§3.7 draw order (queue order, never z-sorted) | **CONFIRMED; no cycle across frames/ticks [M]** | `tree=ABC|…` and `rev=CBA|…` every frame in all 7 modes; `flat=CBACBA` invariant |
| 17 | (new, L10 scope) reparent notification set | **CONFIRMED with a flag condition [M]** | with `notify_local_transform` enabled the set includes `35`; the scout's set (flags off on the reparenting node) does not |
| 18 | (new) anything claimed "stable" across ticks | **no r95-style cycle found [M]** | 15/15 scout cells byte-identical across 7 modes + their own receipts; the only phase-varying observables are the tick-driven grouping keys (§3) |

---

## 2. The headline: the flush granularity is the **physics step**

### 2.1 The scout's ladder never separates a queue from a tick

The scout's `coalesce_n=1` queues three times **synchronously** (no physics tick in
between), so it measures pending-flag coalescing, not frame coalescing. My `qflush` cell
queues **once per physics tick** for 6 process frames and counts draws, ticks and frames.

| batch | `coalesce_draws` | `ticks_window` | `frames_with_tick` | `coalesce_eq` | `max_draws_per_pf` | receipt |
|---|---|---|---|---|---|---|
| quiet | 2 | 2 | 2 | 1 | 1 | `runs/quiet/r98b_qflush.rep1.out` |
| load (16 hogs) | 1 | 1 | 1 | 1 | 1 | `runs/load/r98b_qflush.rep1.out` |
| ff1 | **359** | **359** | 6 | **0** | **60** | `runs/ff1/r98b_qflush.rep1.out` |
| ff30 | **12** | **12** | 6 | **0** | **2** | `runs/ff30/r98b_qflush.rep1.out` |
| ff120 | 3 | 3 | 3 | 1 | 1 | `runs/ff120/r98b_qflush.rep1.out` |
| ff30load | **12** | **12** | 6 | **0** | **2** | `runs/ff30load/r98b_qflush.rep1.out` |
| slow (`--frame-delay 100`) | **37** | **37** | 6 | **0** | **7** | `runs/slow/r98b_qflush.rep1.out` |

Verbatim, `runs/ff1/r98b_qflush.rep1.out`:

```
PASS r98b qflush same_pf=1 d_pf_delta=0 d_n=1 coalesce_draws=359 frames_with_tick=6
 ticks_window=359 coalesce_eq=0 max_draws_per_pf=60 distinct_draw_pf=6 selfq_draws=1
 hide_span_pf=0 hide_same_frame=1 hide_ticksep_n=1 hidden_across_tick_n=0 show_after_tick_n=1
```

and `runs/slow/r98b_qflush.rep1.out` (normal mode, **no** `--fixed-fps`, ~6.5 ticks/frame):

```
PASS r98b qflush same_pf=1 d_pf_delta=0 d_n=1 coalesce_draws=37 frames_with_tick=6
 ticks_window=37 coalesce_eq=0 max_draws_per_pf=7 distinct_draw_pf=6 selfq_draws=1
 hide_span_pf=0 hide_same_frame=1 hide_ticksep_n=1 hidden_across_tick_n=0 show_after_tick_n=1
```

- **`draws == ticks`, not frames, whenever more than one physics tick shares a process
  frame.** Under ff1 up to **60 draws share one process frame** (`max_draws_per_pf=60`).
- **The `--frame-delay` control isolates the mechanism [A]:** the per-tick flush is *not*
  a `--fixed-fps` artifact — it reproduces in normal mode whenever frames are slow enough
  that several ticks land in one frame (`slow`: 37 draws / 6 frames / max 7 per frame).
  Under `quiet`/`load` the process frames were still faster than 16.6 ms, so the window
  only ever contained ≤1 tick/frame and the two hypotheses were indistinguishable.
- **`same_pf=1 d_pf_delta=0` in all 7 batches** — the frame-number part of L1 holds; the
  queue is flushed within the same process-frame counter value in every mode.
- **Process-step queues behave differently [M]:** the `qorder` cell queues three siblings
  from `_process` every frame; under ff1 (60 ticks/frame) it still produces **one `ABC`
  group per frame** (`tree=ABC||ABC|…`), not 60. So a queue set during the process step
  flushes at the end of the process frame, while a queue set during a physics step flushes
  at the end of that physics step.

**Corrected L1 [M]:** `queue_redraw()` coalesces pending requests per **flush**; the flush
runs at the end of the physics step that set the pending flag, and at the end of the
process step for process-step queues. The scout's "end-of-frame, at most once" is the
special case where at most one physics tick lands in the frame. Mechanism (why the
renderer syncs per physics step under multi-tick frames) is **[I]**; the observable is
**[M]**.

### 2.2 The hide-timing scope (hazard #2)

`hide_ticksep_n=1` in **all** batches: queue on tick A, hide on tick B. Under
ff1/ff30/ff30load/slow, A and B are in the **same process frame** (`hide_span_pf=0`,
`hide_same_frame=1`) — and the draw still happens, because the queue is flushed at the end
of tick A before the hide at tick B. Under quiet/load/ff120 the ticks are in different
frames (`hide_span_pf≥2`, phase-dependent in quiet), same result. The scout's
`hide_before_flush_n=0` remains true only for a **synchronous** queue+hide (frozen probe,
identical in all 7 modes); "hiding drops the pending draw" is a same-flush condition, not
a same-frame one.

`hidden_across_tick_n=0` and `show_after_tick_n=1` in all 7 modes: queueing while hidden
(across a tick) still drops the pending draw, and `show()` redraws exactly once.

---

## 3. The tick-phase hunt (r95 lesson applied)

The r95 boundary found a `k(k−1)` order cycle for `DirectSpaceState2D` multi-hit queries.
The r98 scout's observables are draw/transform state, not physics query order — but the
lesson ("check anything claimed stable across ticks") was applied in three ways:

1. **The scout's 15 rows are process-frame-driven and byte-stable [M].** All 15 cells are
   identical across quiet / 16-hog load / ff1 / ff30 / ff120 / ff30load / frame-delay and
   match the scout's own 6–9 receipts per cell (`SCOUT_DIFF=[]`). No cycle exists in any
   scout row — including `queue`'s raw `events_tail` frame numbers.
2. **The draw-callback order is temporal and stable [M].** `qorder` samples the order per
   frame for 6–40 frames in each mode: `tree=ABC|ABC|…`, `rev=CBA|CBA|…`,
   `tree_stable=1 rev_stable=1` everywhere; the staggered queue's flattened order is
   `flat=CBACBA` in all 7 modes. Only the **grouping per frame** varies with the
   tick/frame ratio — exactly the same phenomenon as §2:

   | batch | `stag_groups` (queue C@tick0, B@tick1, A@tick2) |
   |---|---|
   | quiet / load / ff120 | `C,B,A` (a tick per frame) |
   | ff1 / slow | `CBA` (all three ticks in one frame) |
   | ff30 / ff30load | `CB,A` (2 ticks/frame) |

3. **The tick-phase-position keys are `[U]` within quiet/load.** `hide_span_pf`,
   `coalesce_draws`, `ticks_window`, the stagger sample strings and `env`'s `ph5` vary
   rep-to-rep in quiet/load because the *scheduling* of ticks against uncapped process
   frames varies; the law keys (`same_pf`, `coalesce_eq`, `stag_groups`, `flat`,
   `max_draws_per_pf` class) are invariant. The analyzer reports them as `UNSTABLE` with
   this explanation; all `--fixed-fps` and `slow` cells are byte-stable (1 rep each).

**F12 latch, tick offsets [M]:** `latch_t1` (one physics frame before the skew write) and
`latch_t3` (three) both give `trigger_n=1`; `latch_imm` (oversampling → same-frame
scale+skew) also `trigger_n=1` — the 3-frame gap in the scout's frozen sequence is not
required. `latch_second` gives `trigger_n=1 second_n=0`: the latch is consumed by the
first transform write (a following `position` write does not redraw).

**Notification timing [M]:** `notifyphase` is identical in all 7 modes — `move_tick=[2000]`
even after a bare physics-frame wait (under quiet that wait spans ≥1 process frame, so the
notification flush lands in between), and `rep_tick`/`rep_frame`/`back_*` all
`[10,11,18,19,27,30,31,32,33,35,2000,2010]`. The `35` in the reparent set is a **scope
clarification**: my node has `set_notify_local_transform(true)` enabled, the scout's did
not — the re-entry set is flag-conditional, not in conflict.

---

## 4. Skew decomposition (L3/L4/L5) — what survives and what does not

### 4.1 Degenerate scales break the exact constructor identity [A]

`skewgrid` runs a 200-combo grid (5 rotations × 8 scales × 5 skews) and compares
`get_transform()` bit-exactly with `Transform2D(r, s, k, Vector2.ZERO)`:

```
PASS r98b skewgrid combos=200 ctor_fail_n=75 ctor_fail_z=75 ctor_fail_nz=0
 rks_fail_n=72 rks_fail_z=12 rks_fail_nz=60 first_fail=ctor@25(r=0.00,s=0.00,0.00,k=0.00)
 z_tf00=(0.00001000,0.00000000;-0.00000000,0.00001000) z_ctor_eq00=0
 z_tf01=(0.00001000,0.00000000;-0.00000000,1.00000000) z_ctor_eq01=0
 y_m0_5=(1.0000,0.0000;0.4794,0.8776;0.0000,0.0000)
 y_2_5=(1.0000,0.0000;-0.5985,-0.8011;0.0000,0.0000)
 rot4=(-0.6536,-0.7568;0.7568,-0.6536;0.0000,0.0000)
```
(`runs/quiet/r98b_skewgrid.rep1.out`; identical in all 7 batches.)

- **All 75 failures are the zero-component scales** `(0,0) (0,1) (1,0)` (3 × 25 combos);
  **0 of 125 non-degenerate combos fail** — the scout's identity is exact for
  negative/non-uniform scales, and wrong only where an axis is zero.
- The cause is a **per-axis 1e-5 clamp on the stored basis** [M]: `z_tf00` shows the local
  matrix is `1e-5·I`, not the zero matrix, so `get_transform() != Transform2D(r, (0,0), k, 0)`.
- The scout's `rks=1` exact pin is **fragile**: 60/125 non-degenerate combos fail
  bit-exact with max component diff **4.77e-7** (`runs/rksenum/rep1.out`:
  `nz_fail_n=60 sign_pairs=++=24,-+=12,+-=12,--=12 max_abs_diff=0.000000477`) — float32
  rounding, matrices agree at `%.4f`. Keep it as a measurement, not a general equality law.
- `y_m0_5`/`y_2_5` confirm the y-basis convention `(-sin k, cos k)` for negative skew and
  |skew| > π; `rot4` confirms the raw (un-normalised) local rotation in the matrix.

### 4.2 The zero-scale epsilon is **scale-proportional** [A]

`epssweep` reads `global_scale` for a `(0,0)` child under parent scales
0.001 … 100 (`runs/quiet/r98b_epssweep.rep1.out`, identical in all 7 batches):

```
eps_exact=ps=0.001->0.000000010,ps=0.500->0.000005000,ps=1.000->0.000010000,
 ps=2.000->0.000020000,ps=100.000->0.001000000
```

- The law is **`global_scale = 1e-5 × parent_scale`** (the clamp lives on the *local*
  basis). The scout's pinned `zero_gscale=(0.000020,0.000020)` is exactly the `ps=2` case;
  under `ps=0.001` the readback is `1e-8`, under `ps=100` it is `1e-3`. Pinning `2e-5` as
  "the" epsilon is wrong for every other parent scale.
- Degenerate one-axis scales clamp **per axis**: `(0,1)` → `(1e-5·ps, 1·ps)`,
  `(1,0)` → `(1·ps, 1e-5·ps)`.
- Angles survive the clamp: `zero_rot_skew=(0.000020,0.000020)|grot=1.1000|gskew=0.5000`
  with `lscale=(0.0000,0.0000)` — the local readback is untouched (still 0), only the
  composed matrix carries the epsilon.

### 4.3 Global setters: global round-trip yes, local inverse no [M]

`gskew` (identical in all 7 batches):

```
PASS r98b gskew gs_rt=1 gs_local=0.0258 gs_local_rot=0.0000 gs_global=0.3000
 gr_rt=1 gr_local=1.1808 gr_local_skew=0.0258 gr_global=0.9000
 gsc_rt=1 gsc_local=(1.7184,0.7131) gsc_global=(2.0000,2.0000)
 gs_rt_uniform=1 gs_local_uniform=0.3000 gr_rt_uniform=1 gr_local_uniform=0.2000
```

Under a non-uniform parent (`rot 0.7, scale (3,0.25)`) the global setters **do** round-trip
in the global readbacks (within 1e-4), but the *local* readbacks are decompositions, not
the naive element-wise inverses: `global_skew=0.3` → local skew `0.0258`;
`global_rotation=0.9` → local rotation `1.1808` **with local skew `0.0258`** (shear stored
locally); `global_scale=(2,2)` → local `(1.7184,0.7131)`. Under a uniform parent the local
readbacks are the naive inverses (`0.3000`, `0.2000`). This sharpens L5: "inverse-compose"
is matrix-level, and any local readback under a non-uniform parent is a shear decomposition.

---

## 5. `clip_children` refusal (L9) — confirmed and generalized

`clipmatrix` is byte-identical in all 7 batches (`runs/quiet/r98b_clipmatrix.rep1.out`):

```
PASS r98b clipmatrix stay99=p0->0,p1->1,p2->2 stay3=1 ok2=2
 neg=-1->4294967295,-2->4294967294,-3->4294967293,-5->4294967291,-2147483648->2147483648
 neg_prop=4294967294 recover=1 stay_after_neg=1 stay_repeat=1 max_const=3 err_lines_expected=6
```

- The refusal keeps **every** prior value (`0,1,2`), not just `ONLY`; the boundary is
  `>= MAX` including `== MAX` (`stay3=1` from prior 1, ERROR emitted); repeated refusals
  keep the value (`stay_repeat=1`).
- Negative casts generalize: `-1→4294967295`, `-2→4294967294`, `-3→4294967293`,
  `-5→4294967291`, `INT_MIN→2147483648`; the property path and the setter agree; after a
  cast, a valid set works (`recover=1`) and a following `99` is still refused
  (`stay_after_neg=1`).
- **Exactly 6 ERROR lines per run in all 7 batches** (`grep -c '^ERROR'` on
  `runs/*/r98b_clipmatrix.rep1.err`), and exactly 2/1 for the scout's `draw_refusal`/`clip`
  cells — the refusal stderr is as mode-stable as the values.

---

## 6. What this does to the scout's author rows

- **Rows that survive unchanged [M]:** all 15 frozen rows are byte-identical under
  quiet / 16-hog load / ff1 / ff30 / ff120 / ff30load / frame-delay and against the
  scout's own receipts. The `queue` prefix cut, the two `EXPECTED_ERRORS` entries, and the
  `redraw_context` latch are all confirmed. No envelope is needed for any cell.
- **Rows whose wording must be scoped [A]:**
  1. L1's "end-of-frame … at most once" → "coalesced per flush; a physics-step queue
     flushes at the end of its physics step (so up to `ticks_per_frame` draws per frame
     when ticks outnumber frames), a process-step queue flushes at the end of the frame".
  2. Hazard #2 "hidden items silently drop queued redraws" → same-flush condition only;
     a tick-separated hide does not drop the draw.
  3. L4's "~2e-5 epsilon" → `1e-5 × parent scale`, per axis.
  4. L3's `ctor=1`/`rks=1` → exact only for non-degenerate scales; `rks` is float-fragile.
  5. L5's global setters → global round-trip is approximate (1e-4); local readbacks under a
     non-uniform parent are decompositions.
  6. L10's reparent set → includes `35` when local-transform notifications are enabled.
- **Not an authorable row:** nothing here changes the scout's 15 rows; the above are scope
  notes for a future author block, not replacements.

---

## 7. Remaining risks / not measured

- **Mechanism [I]:** *why* the flush follows physics steps under multi-tick frames
  (renderer sync per physics step vs. pending-flag consumption per step) is not readable
  from GDScript; only the observable is pinned.
- **Load alone did not create multi-tick frames** on this host (`load`: 1 tick in a
  6-frame window; `ph5=3` vs `pf5=4`): the multi-tick-frame case under pure load is
  demonstrated with `--frame-delay` instead. A combined `slow`+16-hog batch was not run
  (the mechanism is already isolated, but the combination is untested).
- `slow` and all `--fixed-fps` batches have 1 rep per cell (byte-stable); quiet/load have 2.
- The quiet/load rep variance is confined to tick-phase positions (§3.3); the law keys are
  invariant, but a stricter harness would normalize those strings.
- Every value is this host/build/`--headless`/`RendererDummy`; no rendered output was
  measured (the scout's §8 limit still stands).

## 8. Host cleanup

- 16 own `yes` hogs per load batch, killed by PID via the EXIT trap (never `pkill`); other
  lanes' hogs untouched (`pgrep -c yes` returned to the pre-existing level).
- `pgrep -fc 'canvas_lattice|r98b_attack'` → 0 after every batch; 0 × rc=137 across 263 runs.
- No tracked file written; no commit. `git status --porcelain` shows only pre-existing
  concurrent-lane churn plus `corpus/live/r98-boundary/` and this report.

## 9. Independent probe (frozen `probeParent` dispatch) — COMPLETED

The frozen probeParent dispatched exactly one read-only `ufo-labrat` seat (no writes, no
engine launches) with a bounded receipt-audit hypothesis: *the report's quoted payloads
exist verbatim in the named receipts and its headline counts hold*. Its verdict, on the
final receipt set: **10/10 checks CONFIRMED, no counterexamples** —

- `runs/ff1/r98b_qflush.rep1.out` contains `coalesce_draws=359 frames_with_tick=6
  ticks_window=359 coalesce_eq=0 max_draws_per_pf=60 hide_span_pf=0 hide_same_frame=1`;
  `runs/slow/…` contains `37/6/7`; `runs/quiet/…` contains `coalesce_eq=1 max_draws_per_pf=1`.
- `runs/quiet/r98b_skewgrid.rep1.out` contains `ctor_fail_n=75 ctor_fail_z=75 ctor_fail_nz=0`,
  `rks_fail_n=72 rks_fail_z=12 rks_fail_nz=60` and `z_tf00=(0.00001000,…)`;
  `runs/quiet/r98b_epssweep.rep1.out` contains the full `eps_exact` chain.
- `runs/quiet/r98b_clipmatrix.rep1.out` contains the full `stay99`/`neg` vectors and the
  `.err` has exactly 6 `ERROR` lines.
- `runs/slow/r98_canvas_queue.rep1.out` is byte-identical to the scout's
  `r98_canvas_queue.rep1.out` (full file bodies equal).
- 263 `.out` files counted (58/58/29/29/29/29/29 + 2 rksenum); every `.rc` is `0`; no `137`.
- `analysis.txt` contains `SCOUT_DIFF=[]`, `ERR_MISMATCH=[]`, `NONZERO_RC=[]`.

The seat's only note (not a refutation): `runs/rksenum/` uses `rep1.out`/`rep2.out` naming
rather than `<cell>.rep1.out`, consistent with its one-off description.

## 10. Evidence index

All under `corpus/live/r98-boundary/`; `manifest.sha256` covers every artefact except itself.

| artefact | path |
|---|---|
| attack probe (14 cells) | `probes/r98b_attack.gd` |
| frozen scout probe byte-copy | `probes/scout_canvas_lattice.gd` (sha256 `866480a1aaa0a385…`) |
| supplementary R·K·S enumeration | `probes/r98b_rksenum.gd` → `runs/rksenum/rep{1,2}.out` |
| driver (7 batches) | `run_matrix.sh` |
| analyzer → json/text | `analyze_r98b.py` → `runs/analyze_r98b.json`, `analysis.txt` |
| batch receipts | `runs/{quiet,load,ff1,ff30,ff120,ff30load,slow}/*.{out,err,rc,wall_ms}` |
| receipt index | `RECEIPTS.md` |

Reproduce: `bash run_matrix.sh quiet && bash run_matrix.sh load && bash run_matrix.sh ff1
&& bash run_matrix.sh ff30 && bash run_matrix.sh ff120 && bash run_matrix.sh ff30load &&
bash run_matrix.sh slow && python3 analyze_r98b.py` (expect `SCOUT_DIFF=[]`,
`ERR_MISMATCH=[]`, `NONZERO_RC=[]`).
