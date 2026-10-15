# game-dev-2d round 93 — boundary (r93-boundary): the Anim+Tween lattice under quiet / 16-hog / 32-hog load / `--fixed-fps` 30/60/120

Seat `BOUNDARY` (LEAF) | lane `r93-boundary` | round 93 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps default, GodotPhysics2D. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at
session start **`2c4b1ff`** (*r94 scout*). Probe corpus: byte-copy of the r93 scout's frozen
`anim_lattice.gd` (sha256 `6a919ae04d4e7549…`) as `probes/scout_anim_lattice.gd`, plus this
seat's `probes/r93b_anim.gd` (6 arms: clock, manual_inv, frame, deferred, purity, blend).

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r93-boundary/**` only. `git status --porcelain` shows only the
pre-existing ` M corpus/fixtures/run_battery.py` (concurrent r89-fold lane) and other lanes'
untracked churn — none of it this seat's.

**The host is shared.** Concurrent lanes held the box at **loadavg 57–149** for the whole
session (measured start/end per batch in `runs/rc-summary.txt`). `quiet` below means **"no
hogs added by this seat"**, never an idle host — the `q` batch itself shows process-frame
deltas from 0.36 ms to 46.5 ms within 20 frames. The seat's own `yes` hogs (marked
`r93b-hog`) were killed after every batch; other lanes' hogs were never touched.

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host; every
`file:line` below is engine-emitted `at:` backtrace text. No symbol-aware work was needed
(the deliverable is a new probe plus receipts), so no cross-file rename was performed; probe
authoring was direct file writes (the fallback), and the one `proj/` copy of the scout probe
is byte-verified by sha256.

**Labrat disclosure (frozen `probeParent`, exactly one dispatch).** The one permitted
`ufo-labrat` (L2, read-only) was given one bounded hypothesis: *"the scout's §1 byte-stability
claim matches its receipts, and the two quoted `stable=[…]` clauses are byte-identical in all
9 canonical+loadtest reps"*. It returned **INCONCLUSIVE with a false negative**: its substrate
reported `corpus/live/r93-scout/runs/` as **absent** ("zero `runs/` files") and it could only
audit `manifest.sha256` hashes — yet this seat's shell reads those receipt files directly
(`cmp` byte comparisons below). Its hash-level audit is still useful corroboration and is
recorded: canonical `.out` hashes 1,1,1,1,1,1,1,1,1,**5**,**6** distinct per cell (census …
animproc); loadtest (8 cells) 1,1,1,**3**,1,1,1,**3**; every `.err` hash = SHA256 of the empty
file; every `.rc` hash = SHA256 of `"0\n"`; and the 6 manual/pure cells' loadtest `.out`
hashes equal their canonical hashes. That agrees with the scout's §1 and with this seat's own
byte-level check (§2). The blocking gap the labrat named (no verbatim clause check) was closed
by this seat.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation;
**[U]** unstable (payload differs); **[?]** unknown.

---

## 0. What I ran

**258 canonical runs in 7 batches + 16 extended-purity runs**, all rc=0, all stderr 0 B,
**0 timeouts** (0× rc=137), wall max 2.26 s. Full table, replay commands and per-cell
stability: `corpus/live/r93-boundary/RECEIPTS.md`; machine summary:
`runs/analyze_r93b.json` + `runs/analysis.txt`.

| batch | conditions | runs | loadavg start→end |
|---|---|---|---|
| `q` | no seat hogs | 51 | 57.33 → 56.41 |
| `l` | **16 seat hogs** | 51 | 57.74 → 74.56 |
| `f30` | `--fixed-fps 30` | 34 | 74.56 → 72.45 |
| `f60` | `--fixed-fps 60` | 34 | 72.45 → 70.03 |
| `f120` | `--fixed-fps 120` | 34 | 70.03 → 69.34 |
| `f120l` | `--fixed-fps 120` + 16 hogs | 34 | 69.34 → 75.30 |
| `l32` | **32 seat hogs** (32 cores), mode+attack subset | 20 | 75.30 → 80.82 |
| `p` | extended purity, all conditions | 16 | 147.47 → 149.02 |

Cells: 11 scout arms (byte-copy probe) + 6 seat arms. **Scope.** The attack covers the claim
families the assignment names: byte-stability/out_uniq, the manual-clock law, the two mode
cells, the crossfade weight law, callback timing, and scheduler-sensitivity everywhere
(`--fixed-fps` × load). `census`/`tweenval_grid`/`animtrack` were re-run but not
re-litigated beyond byte-identity.

**Harness defect [O], recorded.** The first pass launched the scout cells without the probe
copied into `proj/`: 162 runs were vacuous (rc=1, no `PASS` line, 3 `ERROR:` lines). Evidence
preserved in `runs/defect/noscript.{out,err,rc}`; the receipts were re-run in a second pass
and overwritten in place. A second defect (editing `run_matrix.sh` while bash was executing
it → re-read at a shifted offset → syntax error, exit 2) is in `runs/matrix-scout.log`; no
receipt was affected.

---

## 1. Verdict table

| # | attack | verdict | one-line evidence |
|---|---|---|---|
| 1 | independent replication of the scout's receipts (quiet, whole-file `cmp`) | **CONFIRMED for 9/11 byte-for-byte; 2/11 are modes** | census, tweenval, tweenval_grid, animtrack, tweenstep, tweenchain, animseek, animmethod, animblend → **IDENTICAL** to `../r93-scout/runs/r93_<cell>.rep1.out` (and to the scout's loadtest bytes); tweenproc/animproc **differ** |
| 2 | scout §1: "9/11 cells `out_uniq=1`; tweenproc 5, animproc 6; 0 B stderr; rc=0" | **CONFIRMED at byte level (own hashes)** | re-hash of the scout's 54 canonical + 24 loadtest receipts reproduces every count |
| 3 | the two `stable=[…]` clauses byte-identical in 9/9 | **CONFIRMED, extended to 32/32** | 16 tweenproc + 16 animproc runs in 7 launch conditions, exactly one clause each, all byte-identical |
| 4 | the 9 pure/manual cells are launch-invariant | **CONFIRMED under quiet / 16 hogs / ff30 / ff60 / ff120 / ff120+16 hogs** (6 batches); the 2 manual cells in the `l32` subset also under **32 hogs** | `all_uniq=1` for those cells in every batch they appear in (14 reps each; tweenstep/animseek 16 incl. `l32`), byte-identical to the scout's canonical bytes |
| 5 | "frame-coupled counters are modes (`out_uniq=5–6`)" | **CONFIRMED; mechanism identified; the envelope is NOT bounded** | the cell value is `rate × Σ(process deltas)`; measured `after3proc` 1.5 … 10.09 (6.7×) vs the scout's 1.67 … 8.0; under `--fixed-fps` each mode cell collapses to **1 byte-stable value** |
| 6 | "a 0.1 s IDLE animation finishes after 16–17 process frames" | **FALSIFIED as a general law** | **4** frames at ff30, **7** at ff60, **13** at ff120, 16–17 at the default ~160 fps; law is `ceil(0.1/delta)+1` |
| 7 | manual clock (`pause()`+`custom_step`, MANUAL `advance`) is frame-independent | **CONFIRMED** incl. await-interleaved driving and 32 hogs | `manual_inv`: `paused=[2.5,2.5,5.0,5.0,10.0]`, `manual=[25,25,50,50,100]`, all `inv=true` — invariant tokens in all 16 runs; only the unpaused control varies |
| 8 | crossfade weight law `w_i=(i−1)/(N−1)` | **CONFIRMED + await-immune (new)** | `interleaved_eq_plain=true` in all 17 blend runs (10 manual steps with an awaited process frame between each reproduce the plain lattice byte-for-byte) |
| 9 | scout §3.2: "**the runtime tween clamps** (a tween's value never exceeds its endpoints)" | **FALSIFIED** | `BACK/EASE_IN_OUT` 1→10 at t=0.25 → **0.1029** (below the start value 1.0); `SPRING/EASE_OUT` 0→10 at t=0.5 → **10.5102** (above the end value 10.0) |
| 10 | DEFERRED queues method calls to the next frame | **CONFIRMED + one new route** | `after_adv=[]`, `next_proc=[7,8]`, `second_proc=[7,8]`; **`after_phys=[7,8]`** — a physics frame flushes too (all 16 deferred runs) |
| 11 | `play()` does not apply the pose | **CONFIRMED + off-by-one read law (new)** | `x1=0.0` in **258/258** runs; N awaited frames ⇒ N−1 applied steps (`pos10` = 9·delta exactly at ff30/60/120) |
| 12 | `--fixed-fps` as a harness variation | **NEW MODE: not benign — it is a *stabilizer* with a deterministic boot transient** | frame cells are byte-stable across reps **and** under 16 hogs at ff120 (`f120l == f120` byte-for-byte); but ff30's first six deltas are `0.025, 0.0333, 0.0417, 0.0292, 0.03, 0.0325` — not `1/30` |
| 13 | the scout's analyzer `stable_tokens` list is pin-safe | **FALSIFIED for `tweenproc.phys`** | `phys` takes 4 values across launch modes (`after3proc` 16.67/33.33/50/100, `after3phys` 50/66.67/83.33/133.33) while the scout's `analyze_r93.json` lists one as stable (their §6.2 rule 4 correctly says *don't pin* `phys` — the report text is safe, the derived list is not) |
| 14 | `mixer_updated=0`, `caches_delta=1`, `caches_total=11`, `frozen`, `inactive`, `is_playing=false`, `mixer_applied_10=10` | **CONFIRMED invariant in all 7 conditions** | 16 animproc + 16 frame runs; none of these tokens varies (incl. 32 hogs and ff120+load) |

---

## 2. Attack 1 — independent replication of the scout's receipts **[M]**

The scout's §8 lists "independent replication is missing" as its first open unknown. This
seat re-ran its frozen probe (sha256 `6a919ae04d4e7549…`, byte-verified before launch) in
its own lane under its own hogs, and compared whole files with `cmp`:

| cell | `q_` (mine) vs scout canonical | `l_` (mine, 16 hogs) vs scout loadtest |
|---|---|---|
| census, tweenval, tweenval_grid, animtrack, tweenstep, tweenchain, animseek, animmethod, animblend | **IDENTICAL** (whole file, banner included) | **IDENTICAL** |
| tweenproc, animproc | differs | differs |

**9/11 arms replicate byte-for-byte on a second seat, in a second window, under a different
hog count.** The two exceptions are the mode cells, and they are the *only* ones whose
payloads vary here at all (`all_uniq=11` each, across 16 runs). None of my 11 tweenproc or
11 animproc payloads coincides with any of the scout's 8/9 distinct payloads — the values are
continuous functions of the observed deltas, so a "mode set" is a window artifact, not a
recurring lattice (§3).

**The scout's own receipts check out at byte level** (this seat's re-hash, closing the
labrat's blocked check): canonical `out_uniq` = 1,1,1,1,1,1,1,1,1,**5**,**6** (11 cells, census
… animproc); loadtest `out_uniq` = 1,1,1,**3**,1,1,1,**3** (the 8 cells they ran under load);
`err_bytes=0` in all 78 receipts; `rc=0` in all 78; and the two `stable=[…]` clauses appear
verbatim, byte-identical, in 6/6 canonical + 3/3 loadtest reps of their cells. The scout's
§1 and §3.6/§3.11 statements are accurate.

---

## 3. Attack 2 — the frame-coupled cells: the mode law is `Σ deltas`, and `--fixed-fps` collapses it **[M]**

The scout's rule "frame-coupled counters are modes; pin only the `stable=[…]` clauses"
(§4.2, hazard 11) is **correct and now mechanised**. The unpaused-tween cell of `tweenproc`
(`0 → 60` over 1.0 s, value read after 3 awaited process frames) is exactly
`60 × Σ(process deltas applied)`, i.e. **2 applied steps** (off-by-one, §9), so:

| launch | `auto=[y0=0.0,after3proc=…]` | interpretation |
|---|---|---|
| ff60 | `2.0` | `60 × 2/60` — exact |
| ff120 | `1.5` | `60 × (2/120 + 1/120)` — the boot double-delta |
| ff30 | `3.5` | `60 × (0.025 + 0.03333)` — the first two boot deltas |
| my `q_` 3 reps | `5.175`, `3.681`, `2.038` | ambient deltas |
| my `l32` (32 hogs) | `10.086`, `5.0` | saturated host |
| scout canonical 6 reps | `1.667, 2.051, 2.0, 2.0, 2.275, 2.059` | their window |
| scout loadtest 3 reps | `8.0, 2.537, 4.0` | their 16-hog window |

So the scout's own "bimodal 16.67/33.33 px" reading of `phys` (§3.6) understates the
dispersion: the measured range across all conditions here is **1.5 … 10.09 (6.7×)**, and it
is *unbounded* in principle because it is a sum of deltas, not a discrete mode set.

**New: `--fixed-fps` makes the mode cells byte-stable.** `tweenproc`, `animproc`, `frame`,
`manual_inv`, `blend`, `deferred` each have `payload_uniq=1` inside every fixed-fps batch
(2/2 reps), and **`f120l` (ff120 + 16 hogs) is byte-identical to `f120` (quiet)** for all six
of them. This is the opposite polarity to the r91 nav finding: for *frame-coupled animation*,
`--fixed-fps` is a stabiliser, because it replaces the ambient delta sequence with a fixed
one. The corollary for the battery is exact: **a frame-coupled animation cell can be pinned
only under a fixed-fps launch — or not at all.**

**The stabiliser is not free** (§6): the fixed-fps *boot* frames are not `1/N`.

---

## 4. Attack 3 — the manual clock survives 32 hogs, await-interleaving and fixed-fps **[M]**

Three independent lanes agree with the scout's manual-clock law (§4.2) and extend it:

1. **Await-interleaved manual driving.** `manual_inv` steps a paused tween and a MANUAL
   player with awaited process *and* physics frames in between:
   `paused=[a=2.5,b=2.5,c=5.0,d=5.0,e=10.0]`, `manual=[f=25.0,g=25.0,h=50.0,k=50.0,m=100.0]`,
   `inv=[paused_proc=true,paused_phys=true,manual_proc=true,manual_phys=true]` — invariant
   tokens in **all 16 runs** (quiet, 16 hogs, 32 hogs, ff30/60/120, ff120+16 hogs). The
   unpaused control in the same arm *does* move (`o` 15.77 … 16.0, i.e. the frame path is
   live), so the invariance is not a vacuous probe.
2. **The crossfade lattice is await-immune.** `blend`'s 10×0.1 s lattice with one awaited
   process frame between steps equals the plain lattice byte-for-byte:
   `interleaved_eq_plain=true` in **16/16** runs, `interleaved == finished_010 ==
   [100.0,144.444…,188.888…,…,500.0]`.
3. **The scout's own manual cells replicate under saturation.** `tweenstep` and `animseek`
   (the two manual cells in the `l32` subset) are byte-identical to the scout's canonical
   bytes under 32 hogs on 32 cores (loadavg 75→121) as well as under ff120+16 hogs; the
   remaining manual cells (`tweenchain`, `animmethod`, `animblend`) are byte-identical across
   the other six batches.

**Extended claim (this seat): the manual clock is invariant across all seven conditions
tested; only frame-coupled reads move.**

---

## 5. Attack 4 — the "16–17 process frames" is a host-rate artifact **[A]**

Scout §3.11: *"A 0.1 s animation under IDLE finishes after 16–17 process frames (~100 ms at
~160 fps)"*. The qualifier was honest, but the frame count is not a property of the
subsystem:

| launch | `quick=[frames_to_finish, fin_frame]` (animproc) | `frame` arm `quick` |
|---|---|---|
| `--fixed-fps 30` | `4, 3` (2/2) | `frames=4, fin_frame=3` (2/2) |
| `--fixed-fps 60` | `7, 6` (2/2) | `frames=7, fin_frame=6` (2/2) |
| `--fixed-fps 120` | `13, 12` (2/2 quiet, 2/2 +16 hogs) | `frames=13, fin_frame=12` (2/2) |
| default (my windows) | 16 (7×), 17 (1×) | 16 (6×), 17 (1×), 15 (1×) |
| scout canonical/loadtest | 16 (6/6), 17 (3/3) | — |

The law is `frames = ceil(0.1 / process_delta) + 1`; the scout's 16–17 is simply
`delta ≈ 1/160`. Their own analyzer classified `quick` as a varying token and §6.2 says never
to pin frame counts — so no scout *pin* is wrong here, but the §3.11 sentence and any row
lifted from `stable_tokens` would be. **Pin the elapsed time, never the frame count.**

---

## 6. Attack 5 — `--fixed-fps` is a mode: a deterministic boot transient **[M]/[I]**

The `clock` arm's full delta vector is byte-stable across reps in each fixed-fps batch, and
the boot frames are **not** `1/N`:

```
ff30 : deltas=[0.025, 0.03333333333333, 0.04166666666667, 0.02916666666667, 0.03, 0.0325,
               0.03333333333333 × 14]        mean=0.03291666666667  (runs/f30_clock.rep1.out)
ff120: deltas=[0.01666666666667, 0.00833333333333 × 19]            (runs/f120_clock.rep1.out)
ff60 : deltas=[0.01666666666667 × 20]                              (runs/f60_clock.rep1.out)
```

- ff30's first six frames are `0.75×, 1×, 1.25×, 0.875×, 0.9×, 0.975×` of a frame — the
  engine's start-up compensation — and they are **reproducible to the byte** (`f30_clock.rep1`
  == `rep2`), which is why the ff30 frame cells are stable despite not being exactly `1/30`.
- ff120 carries one double-delta frame; ff60 is exactly `1/60` from frame 1.
- Consequence: a cell read in the **first frames** under ff30 inherits the transient
  (`f30_frame` `x5=13.4166669845581` instead of `13.333…`; `f30_tweenproc auto=3.5` instead
  of `4.0`), yet it is still byte-reproducible. **A fixed-fps pin is valid only if the
  whole delta vector is part of the pinned process** — which it is, since it is deterministic.
- `phys_per_proc` (process frames per physics tick) separates the launches: 2.05 (ff30),
  1.05 (ff60), 0.53 (ff120), 0.42–0.63 (default). Note ff120's 0.526 coincides with a
  default-window value while the frame cells differ — **the ratio is not the discriminator;
  the process delta is.**

**Saturation, for contrast** (`l32`, 32 hogs): `deltas=[0.093672, 0.006328, 0.000001,
0.001039, 0.005555…]` — a **1 µs** frame inside the same 20-frame window (min 1e-6, max
0.0937, mean 0.0102). Frame-counted animation under ambient load spans six orders of
magnitude of frame time; this is the whole reason the mode cells are modes.

---

## 7. Attack 6 — the runtime tween does NOT clamp: the scout's §3.2 parenthetical is falsified **[A]**

Scout §3.2: *"The **runtime** tween clamps (a tween's value never exceeds its endpoints in
the measured chains); the **static** function extrapolates."* Every *Tween* chain they
measured used the default `TRANS_LINEAR` transition, which never leaves the endpoint
interval — so the parenthetical was never tested. With an overshooting transition the
runtime leaves the endpoint interval on both sides:

```
overshoot=[back025=0.10286344587803,back050=5.5]
overshoot2=[spr050=10.510157585144,spr100=10.0,ela025=9.11611652374268]
```
(`runs/q_purity.rep1.out`; byte-identical in **all 16** purity runs across the 7 conditions)

- `tween_property(target, "scale:y", 10.0, 1.0).set_trans(TRANS_BACK).set_ease(EASE_IN_OUT)`
  stepped to t=0.25 yields **0.1029**, i.e. *below the start value* (the node's scale.y was
  1.0); at t=0.5 it is the midpoint 5.5.
- `TRANS_SPRING/EASE_OUT` on a fresh `0 → 10` tween at t=0.5 yields **10.5102**, i.e. *above
  the end value*; at t=1.0 it lands exactly on `10.0`.

**Correct statement:** the runtime tween reproduces `Tween.interpolate_value` on the same
curve to float32 precision (BACK: measured `0.10286344587803` vs static `0.102863446…`;
SPRING: `10.510157585144` vs the scout's grid `10.5101573467255`, ≈2e-7 relative) with **no
clamp**; the *endpoints* are only guaranteed at t=0 and t≥duration. A "bounded sampler"
assumption is wrong on both the static and the runtime path. The scout's own grid values
(`bac io` @0.25 = −0.9968·delta) already contained this fact; the §3.2 parenthetical
contradicts their own data.

---

## 8. Attack 7 — DEFERRED/IMMEDIATE callback timing (extension) **[M]**

`deferred` reproduces the scout's split and adds one route and a scheduler statement:

```
manual_def=[after_adv=[],next_proc=[7,8],second_proc=[7,8]]
manual_def_phys=[after_adv=[],after_phys=[7,8]]
two_adv=[after=[],flush=[7,8]]
immediate=[after_adv=[7,8],after_frame=[7,8]]
```
(`runs/q_deferred.rep1.out`; the four lattices are byte-identical in **all 16** runs)

- A MANUAL `advance(1.0)` executes the timeline but never the calls; they flush on the next
  **process frame** — *and also on a physics frame* (new; not in the scout's §3.8/§4.6).
- Two manual advances before any frame still produce nothing until the frame boundary
  (`two_adv`), so the queue is per-mixer, not per-advance.
- **The lag is one process frame, so its wall-clock size is launch-dependent.** In the
  frame-coupled variant the first DEFERRED call is observed at the first frame whose
  animation position has passed the key:

  | launch | `idle_lag` |
  |---|---|
  | ff120 | `first_at=6, first_pos=0.04166666666667` (key 0.04), `second_at=13, second_pos=0.1` (key 0.1, exact) |
  | default | `first_at=7, first_pos≈0.0411`, `second_at=16, second_pos≈0.1035` |
  | l32 | `first_at=8, first_pos≈0.0466` |

  i.e. the same "next frame" law costs 8.3 ms at ff120 and ~6.9 ms at the default rate —
  **the law is in frames; any timeout expressed in seconds is a mode.**

---

## 9. Attack 8 — off-by-one read law for frame-coupled cells (new) **[M]**

`x1=0.0` in **258/258** runs of the `frame` arm (all launches): after `play()`, the first
awaited process frame reads the *pre-play* value. Across the fixed-fps batches the pattern is
exact: `pos10 = 9 × delta` (0.3 at ff30, 0.15 at ff60, 0.075 at ff120); `x2/x3/x5` are exactly
1/2/4 applied steps at ff60 and ff120 (`1.667/3.333/6.667` and `0.833/1.667/3.333`) and
1/2/4 steps *including the ff30 boot transient* at ff30 (`3.333/7.5/13.417` — see §6). So:

**`await process_frame` N times ⇒ N−1 process steps have been applied.**

This sharpens the scout's hazard 5 ("`play()` does not apply the pose") into a counting rule
for any cell that reads values after awaits: **a frame-counted cell that assumes N awaits =
N steps is off by one, in every launch mode.** It also confirms the scout's §3.7
`manual_frames=[0.0,0.0]` (a MANUAL player never advances on awaits) — that cell is
byte-identical in all conditions.

---

## 10. Unstated modes and hazards (all with receipts)

1. **`custom_step` accepts a negative delta** without rewinding: `neg=0.0`,
   `neg_elapsed=-0.5` (`runs/q_purity.rep1.out`) — elapsed goes negative, the value does not.
2. **Extreme manual deltas are honoured**: `custom_step(1e-9)` → `1e-8` px; a single
   `custom_step(1e6)` completes the tween (`huge=10.0, huge_running=false`).
3. **1000 × 0.001 manual steps land exactly on 1.0** (`accum1000=1.0`) — the elapsed
   accumulator does not drift at this scale.
4. **`mixer_applied_10=10`** in every launch (1 per process frame) while `mixer_updated=0`
   in every launch — the scout's F13 holds under ff and 32 hogs, and the "40–42" counter in
   their §3.11 is just the number of frames their arm ran.
5. **`caches_total=11` and `caches_delta=1` are invariant in all 7 conditions** — the
   scout's §6.2 advice not to pin `caches_total` is conservative, not required, on this host;
   but it is a *count of frame-driven operations* in principle, so the advice stands.
6. **`--fixed-fps` does not disturb the physics side**: `phys=[y1=0.0,y2=0.0,y3=1.66666674613953,y6=6.66666698455811]`
   is byte-identical in **16/16** `frame` runs (incl. 32 hogs), and `phys_delta=0.01666666666667`
   everywhere. The *increments* per physics await are launch-invariant too: `tweenproc`'s
   `phys` pairs across all four observed launch values are `[16.667→50.0]`, `[33.333→66.667]`,
   `[50.0→83.333]`, `[100.0→133.333]` — every increment is exactly `+33.3333` (= 2 physics
   ticks × 1/60 × 1000), while the *base* is a mode. **Physics-tick values and their
   increments are pinnable; process-window accumulations are not.**
7. **Vacuous-receipt class**: a missing probe file yields rc=1 + 3 `ERROR:` lines + **no
   `PASS` line** (`runs/defect/`). The battery's PASS convention catches it; a
   timeout-only runner would not.
8. **The scout's analyzer `stable_tokens` is not a pin-safe list**: `tweenproc.phys` appears
   there as one value but takes 4 values across launch modes. Their §6.2 rule 4 ("never pin
   `phys`") is the correct reading; the derived list is not.

---

## 11. Remaining risks / not measured

- **Mechanism of the fixed-fps boot transient is [I]**: no engine source tree on this host;
  the observable (byte-reproducible non-`1/N` first frames) is solid, the "start-up
  compensation" reading is the best fit. The transient's *length* (6 frames at ff30, 1 at
  ff120, 0 at ff60) is measured, not explained.
- **The host was never idle** (loadavg 57–149, concurrent batteries). Every absolute value is
  host-conditioned; a quiet box would shrink the default-window dispersion but not the law.
- **Not re-litigated:** the census/enum surface, `tweenval_grid` beyond byte-identity,
  `animtrack` sampler values, `animblend`'s capture route (all byte-identical here, so the
  scout's canonical receipts stand unchallenged), plus the scout's own §8 unknowns
  (`UPDATE_DISCRETE`/`UPDATE_CAPTURE`, nested/animation tracks, audio tracks,
  `set_pause_mode`, negative `speed_scale`, `play_section`, threaded animation).
- **Not measured:** fixed-fps values other than 30/60/120; `Engine.max_fps`-capped launches;
  a genuinely quiet window; Windows/macOS portability.
- **No pin is proposed here.** This seat attacks claims; the 15 gating rows in
  `corpus/live/r93-scout/author-rows.py.txt` are not modified or endorsed, and the two mode
  cells' `stable=[…]` clauses are the only tokens this seat would consider pin-safe — which
  is what the scout's §6.2 already says.

---

## 12. Host cleanup

- **0 timeouts** (no rc=137); no godot process from this lane remains
  (`ps -eo pid,args | grep godot | grep -E 'r93b_anim|scout_anim_lattice'` → 0; a bare
  `pgrep -f` self-matches its own command line, so the `ps` form is the one recorded).
- The seat's own `yes r93b-hog` hogs were killed after every batch (`stop_load` + EXIT/INT/TERM
  traps); `my_hogs_after_stop=0` is recorded at every batch boundary in `runs/rc-summary.txt`.
  Other lanes' system-wide `yes` hogs (12–218 processes) were never touched — no `pkill -x yes`
  was ever issued.
- No tracked file written (`git status --porcelain`: only the pre-existing
  ` M corpus/fixtures/run_battery.py` and other lanes' untracked churn). No commit, no push.
- `manifest.sha256` covers every artefact under `corpus/live/r93-boundary/`.

---

## 13. Evidence index

All under `corpus/live/r93-boundary/`; `manifest.sha256` covers every artefact.

| artefact | path | notes |
|---|---|---|
| scout frozen probe (byte-copy) | `probes/scout_anim_lattice.gd` | sha256 `6a919ae04d4e7549…` |
| seat attack probe, 6 arms | `probes/r93b_anim.gd` | clock / manual_inv / frame / deferred / purity / blend |
| launch project | `proj/project.godot` | sha256 `8de8b3af9cc737ed…` (fixtures byte-copy) |
| driver (8 batch modes) | `run_matrix.sh` | `timeout -s KILL 25`; hog marker `r93b-hog` |
| analyzer → JSON + text | `analyze_r93b.py` → `runs/analyze_r93b.json`, `runs/analysis.txt` | |
| receipts | `runs/<tag><cell>.rep<N>.{out,err,rc,wall}` | 258 canonical runs |
| harness-defect receipt | `runs/defect/noscript.{out,err,rc}` | rc=1, 0 PASS lines, 3 ERROR lines |
| batch log + hog/loadavg census | `runs/rc-summary.txt`, `runs/matrix*.log` | loadavg per batch |
| batch/evidence table | `RECEIPTS.md` | |

Key verbatim receipts: `runs/q_frame.rep1.out` (default-rate lattice),
`runs/f30_frame.rep1.out` / `runs/f60_frame.rep1.out` / `runs/f120_frame.rep1.out`
(deterministic lattices), `runs/f120l_frame.rep1.out` (ff120+16 hogs == ff120 quiet),
`runs/f30_clock.rep1.out` (boot delta vector), `runs/l32_clock.rep1.out` (1 µs frame),
`runs/q_tweenproc.rep1.out` + `runs/f30_tweenproc.rep1.out` (mode vs fixed),
`runs/q_animproc.rep1.out` + `runs/f30_animproc.rep1.out` (16 frames vs 4),
`runs/l32_manual_inv.rep1.out` + `runs/f120l_manual_inv.rep1.out` (manual clock under
saturation), `runs/q_purity.rep1.out` (overshoot falsification), `runs/f120_deferred.rep1.out`
(one-frame lag at a fixed rate), `runs/f120_blend.rep1.out` (await-immune weight law),
`runs/q_census.rep1.out` (byte-identical replication).
