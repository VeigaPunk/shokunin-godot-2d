# game-dev-2d round 94 — boundary (r94-boundary): the CPUParticles2D lattice under quiet / 16-hog load / `--fixed-fps` 30·60·120 / tps 30·120

Seat `BOUNDARY` (LEAF; frozen `probeParent` — one labrat dispatch, §9) | lane
`r94-boundary` | round 94 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
default 60 physics ticks/s. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at
session start **`2c4b1ff`** (r94 scout).
Probe corpus: byte-copy of the scout's frozen primary probe as
`probes/scout_particles_lattice.gd` (sha256 `e6a2e0f5…b930` = their committed file), the
scout's `discover6.gd` as `probes/scout_discover6.gd` (sha256 `213d4cb1…`), and this
seat's `probes/r94b_particles.gd` (24 arms + 4 bisect arms).

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r94-boundary/**` only. `git status --porcelain` still shows
only the pre-existing ` M corpus/fixtures/run_battery.py` and other lanes' untracked
churn.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on
this host; no symbol-aware rename was needed (probe authoring is direct file writes).
The scout's `author-rows.py.txt` and `classify_process` were consumed as data
(AST-extracted, segment sha256 `749fa0607e7707e6…` — identical to the scout's).

**The host is shared.** Concurrent lanes held the box at **loadavg 69–147** for the whole
session. `quiet` below means **"no hogs added by this seat"**, never an idle host. Every
batch records `loadavg_start/end` in `runs/rc-summary.txt`; this seat's 16 `yes` hogs were
killed by the batch EXIT trap after each load batch.

**Legend:** **[M]** measured (fresh process, this seat); **[A]** ablation/refutation;
**[I]** inference; **[U]** unstable across conditions; **[?]** mechanism unknown.

---

## 0. What I ran

**734 fresh godot launches, 8 batches, 0 timeouts** (683 matrix + 51 reprobe; 25 further
smoke runs). All `timeout -s KILL 25`-bounded, stdout/stderr split into per-cell sidecars
plus `.rc`/`.wall`. **0 non-zero rc, 0 B stderr on every matrix+reprobe receipt** [M].

| batch | conditions | runs | loadavg start→end |
|---|---|---|---|
| `quiet` | 60 tps, no seat hogs | 138 | 69.4 → 125.7 |
| `load` | 60 tps + **16 seat hogs** | 114 | 125.7 → 118.2 (system-wide `yes` count 128 during) |
| `ff30` | `--fixed-fps 30` | 111 | 118.2 → 98.1 |
| `ff60` | `--fixed-fps 60` (ratio control, 1 idle : 1 physics) | 111 | 98.1 → 112.5 |
| `ff120` | `--fixed-fps 120` | 111 | 112.5 → 93.9 |
| `ff120load` | `--fixed-fps 120` + 16 hogs | 62 | 93.9 → 104.1 |
| `ab` | paired, interleaved default vs ff30/ff60/ff120 | 36 | 104.1 → 93.3 |
| `reprobe` | final probe revision: contamination matrix + amount bisect | 51 | 89.1 |

Cells per batch: the scout's **19 frozen cells** (byte-copy probe, 3 reps) + **24 attack
arms** (2–3 reps) + the scout's own `discover6` amount arms (2–3 reps). Full replay:
`RECEIPTS.md`; machine summary: `runs/analyze_r94b.json` + `runs/analysis.txt`.

---

## 1. Verdict table

| # | attack | verdict | one-line evidence |
|---|---|---|---|
| 1 | **Evidence integrity of the scout's "143/143"** | **DEFECT (provenance)** | the frozen probe was written at **16:51:26**; **135 of the 143 receipts predate it** (only `cpu_request` 6+2 were re-run on the frozen revision); `RECEIPTS.md` cites sha `09dd77238668b315…` while `manifest.sha256`/report cite `e6a2e0f5…`; the pre-freeze revision is unrecoverable (receipts gitignored, single commit) — §2 |
| 2 | one-shot ladder `round(L·60)` ticks | **CONFIRMED at 60 tps in all 6 conditions; FALSIFIED as a general law** | `ok=true` for `cpu_lifetime`/`cpu_expl`/`cpu_speed_pre` in quiet, load, ff30, ff60, ff120, ff120load; but at `Engine.physics_ticks_per_second=30` L=0.5 finishes at **15** ticks and at 120 at **60** ticks — the "×60" is the host tps, not a particle law — §3 |
| 3 | "the tick count is the physics clock, the ms is the simulated time" | **CONFIRMED with the mechanism named** | the clock is a **process-delta time accumulator**: L=0.5 → `proc_ms=495–500` in every condition while `fin_ph` = 30 (quiet/ff60), **28** (ff30), 29 (ff120), 60 (tps120), 15 (tps30); process:physics ratio is **2.1–2.5:1** at 60 tps here, 0.50 at ff30, 1.98 at ff120 — §3 |
| 4 | `--fixed-fps` is a benign harness variation | **NEW MODE: it is not** | at ff30 the ladder is deterministically **2 ticks low** in all 3 interleaved pairs (l01=7, l025=12, l05=28, l1=58) and **`cpu_pause` rejects its pinned row 3/3** (`vis_parent_ok=false`, `pm_disabled_ok=false`); ff60/ff120 stay inside the ±1 tail — §4 |
| 5 | engine `fixed_fps` "quantizes but does not move the end time" | **PARTLY FALSIFIED + new stall mode** | the end moves by up to one quantum: `ff5`→35 ticks (0.586 s), `ff30`→31, `ff60`→30, `ff1000`→30; **`fixed_fps=1` never finishes** (240 ticks / **3.99 s**, n_fin=0) in quiet, ff30, ff60 and ff120 — §5 |
| 6 | request lattice = `round(lifetime/step)+1` | **FALSIFIED (closed form wrong)** | 7-step table: 0.05→11, 0.1→6, 0.15→4, 0.2→**3** (round predicts 4), 0.25→3, 0.3→**2** (predicts 3), 0.4→2 — all 7 fit **`floor(L/step)+1`**; tps-invariant (tps120 reproduces 6 and 3) and identical under load and ff120 — §6 |
| 7 | amount-setter spurious `finished` "on the set tick" | **CONFIRMED for `one_shot=true`; mechanism corrected** | `cpu_amount_mid` is byte-identical (`fin_after_set=0 n_fin=1 em_fin=true ise_fin=true em_at_end=false`) in **all 6 conditions**; but the signal is **not** synchronous (`sync=0`): it is emitted by the node's next `_process`, **same process frame** (`frames_to_fire=1 d_pf=0`) — §7 |
| 8 | F17 "continuous emitters do not fire" | **UNSTABLE [U] — not a law** | the scout's own `discover6.amount_cont` re-run: quiet 0, load 0, ff30 0, **ff60 1**, ff120 0; this seat's equivalent arms fire at t=10 (first node) but not t=30, while the 5th node fires at t=30 — §7.3 |
| 9 | law 12 "process-global contamination" | **FALSIFIED as framed** | a **single** never-emitting emitter with **nothing before it** fires `finished` on its first update if it is added at `PF≥1` (`contam_j`: `pre=none_wait2` → `fin_delta=0 n=1 add_pf=1`), while the same arm added in the first frame is clean (`contam_g` `add_pf=0` → `-1`); `add_pf=0` → clean 6/6 receipts, `add_pf≥1` → fires 24/24 receipts; no global state is needed — §8 |
| 10 | `GPUParticles2D` headless inertness | **CONFIRMED in every condition; the flip range is wider** | `gpu_headless ok=true` in all 6 conditions; `flip_after` measured **1** (quiet, ff120), 3, 4, 5, 6, 7 — the scout's "3–7" is really **[1,7]**; `capture_rect` zero everywhere — §9 |
| 11 | pause levers freeze the clock | **CONFIRMED at 60 tps (quiet+load), REJECTS at ff30** | `cpu_pause ok=true` in quiet/load/ff60/ff120/ff120load; `ok=false` 3/3 at ff30 (`vis_parent[fin_after_show=2]`, `pm_disabled[fin_after_enable=2]`, expected 4–7) — §4.2 |
| 12 | 19 gating rows (`ROWS_PREFIX`) portable | **18/19 portable; `cpu_pause` is not** | on the **frozen** probe: quiet 0/57 rejected, load 0/57, ff30 **3/57**, ff60 0/57, ff120 0/57, ff120load 0/38 — §10 |
| 13 | the scout's 143/143 verification is reproducible | **CONFIRMED (on their receipts)** | this seat's classifier run over `../r94-scout/runs{,/loadtest}`: `ROWS_PREFIX rejected=0` (105+38), `ROWS rejected=20+10=30` — matching their numbers, same `classify_process` segment sha — §2 |
| 14 | scout §8 open items: tps dependence, `fixed_fps` edges, continuous-amount | **MEASURED** | tps 30/120 done (attack 2), `fixed_fps` 1/5/30/60/1000 × `fract_delta` done (attack 5), continuous-amount done (attack 8) — §11 |

---

## 2. Evidence integrity — the "143/143" rests on two probe revisions [M]

This is a provenance finding, not a behaviour finding, and it is the reason this seat
re-ran the frozen probe from scratch.

- The committed probe `corpus/live/r94-scout/probes/particles_lattice.gd` (sha256
  `e6a2e0f5…b930`, 741 lines) has mtime **2026-10-15 16:51:26**; `proj/particles_lattice.gd`
  is the same byte-copy (16:51:26).
- Of the 143 receipts the headline cites, **only 8** (`runs/r94_particles_cpu_request.rep1..6`
  at 16:51:26–16:51:30 and `runs/loadtest/r94_particles_cpu_request.rep1..2` at 16:51:34–35)
  were written at or after that freeze. **135 receipts (99 canonical + 36 loadtest) predate
  it** (canonical cells 16:42–16:44, loadtest 16:48–16:49).
- `RECEIPTS.md` line 13 names the frozen probe as `sha256 09dd77238668b315…`; `manifest.sha256`
  lines 11/19 and report §11 name it `e6a2e0f55c6bbeaa…`. **The same commit carries two
  different hashes for one file.** A second, independent read-only reader (the labrat, §9)
  confirmed this contradiction from the files alone.
- The pre-freeze revision is **not recoverable**: `corpus/live/.gitignore` ignores `runs/`,
  so no receipt is in git history, and `git log --all -- corpus/live/r94-scout/probes/particles_lattice.gd`
  shows the single r94 commit — the old revision exists nowhere in the tree.
- **Consequence.** "ROWS_PREFIX rejected 0 of 143" was computed over a receipt set that mixes
  two probe revisions, 135 of which cannot be tied to the frozen artifact. The claim is
  *reproducible* (this seat re-ran the classifier over those same receipts: `rejected=0`,
  `ROWS` full-line `20+10=30`, identical segment sha — attack 13), but it is not
  *evidence for the frozen probe*. **This seat's matrix is the missing evidence**: all 19
  cells re-run on the frozen revision under 6 conditions (§10).
- Minor, same family: the scout's `analyze_r94.py` prints
  `loadtest_prefix_violations = ['particles_cpu_speed_pre']` while report §1 says the loadtest
  "reproduced all 19 gating prefixes". Both are true under different definitions — the
  analyzer's `common_prefix` is the byte-common prefix *across canonical reps* (it runs into
  the measured tail, `ss05[delta=60`), while `ROWS_PREFIX` is the boolean block before `" | "`.
  Author-facing note: **"gating prefix" must mean the boolean block**; the analyzer's word
  "prefix" is a different object.

---

## 3. Attack 1 — the ladder is a *time* law wearing a 60-tps alias [M]

**The clock is a process-delta time accumulator.** `r94b_clock_unit` measures the same
one-shot (`e=1, amount=8`) in three units at once (physics ticks, process frames,
accumulated process delta):

```
quiet (3 reps) L0.25[fin_ph=15 fin_pf=32..37 proc_ms=250.5..255.8]  L0.50[fin_ph=29..30 fin_pf=71..72 proc_ms=493.9..499.7]  L1.00[fin_ph=59 fin_pf=143 proc_ms=993.6..999.8]
ff30  (2 reps) L0.25[fin_ph=15 fin_pf= 8         proc_ms=258.3]       L0.50[fin_ph=28     fin_pf=14     proc_ms=500.0]       L1.00[fin_ph=58 fin_pf= 29 proc_ms=1000.0]
ff120 (2 reps) L0.25[fin_ph=15 fin_pf=30         proc_ms=258.3]       L0.50[fin_ph=29     fin_pf=59     proc_ms=500.0]       L1.00[fin_ph=59 fin_pf=119 proc_ms=1000.0]
```
(`runs/quiet/r94b_clock_unit.rep{1,2,3}.out`, `runs/ff30/…rep{1,2}.out`, `runs/ff120/…rep{1,2}.out`)

`proc_ms` is **exact** (L×1000 ±5 ms) in every condition; the *process-frame* count changes
by the mode (32 vs 8 vs 30 for L=0.25); the *tick* count changes only where the frame
quantization forces it (§4). The scheduler is characterised by `r94b_frame_ratio`:

```
quiet   proc_frames=89 phys_frames=36..42  proc_per_phys=2.12..2.47  last_proc_delta=0.00694  last_phys_delta=0.016667
load    (same shape, ±1 frame)                                    last_proc_delta=0.0069
ff30    proc_frames=89 phys_frames=179     proc_per_phys=0.497     last_proc_delta=0.033333
ff60    proc_frames=89 phys_frames=90      proc_per_phys=0.989     last_proc_delta=0.016667
ff120   proc_frames=89 phys_frames=45      proc_per_phys=1.978     last_proc_delta=0.008333
```
**At 60 tps on this host the main loop runs 2.1–2.5 idle frames per physics step** (the
scout's canonical window evidently ran ~1:1; r91 measured 1.0–2.5 for nav). The particle
node is driven by the idle delta, so the ratio cancels out and the tick ladder survives —
which is exactly why the scout's ±1 tails looked benign.

**The tps arms (the scout's own §8 gap) decide the question** — `Engine.physics_ticks_per_second`
changed at runtime, same probe, same process shape:

| condition | L=0.5 `fin_ph` at tps 60 | at tps 30 | at tps 120 | `proc_ms` |
|---|---|---|---|---|
| quiet | 30 | **15** (`runs/quiet/r94b_tps30.rep*`) | **60** (`…tps120…`) | 502 / 505 |
| load | 30 | **15** | **60** | 502 / 506 |
| ff120 (harness) | 29 | **14** | **61** | 492 / 508 |

So **`round(L·60)` is `round(L·tps)`**: the ladder numbers are host-tps artifacts and the
scout's `_okb` windows (`l025 ∈ [12,18]`, `l05 ∈ [27,33]`, `l1 ∈ [57,63]`) **reject at 30 tps**
(L=0.25 → 7 ticks, L=1.0 → 30). A battery cell that changes tps (or a project whose
`physics/common/physics_ticks_per_second` is not 60) will fail the ladder rows; the pinned
`ok=true` block does *not* protect them, because `_okb` is the thing that fails.
**Author rule: pin the *time* (or the boolean `n_fin`/`em_after` state), never the tick
count, unless the tps is pinned by the launch project.**

---

## 4. Attack 2 — `--fixed-fps` as a mode [M]/[A]

### 4.1 The paired, interleaved window (`ab`)

3 pairs, each running default → ff30 → ff60 → ff120 back to back in the same window
(`runs/ab/ab{1,2,3}_{def,f30,f60,f120}_cpu_lifetime.rep1.out`):

| pair | mode | l01 | l025 | l05 | l1 |
|---|---|---|---|---|---|
| 1 | `def` | 6 | 15 | 30 | 59 |
| 1 | **`f30`** | 7 | **12** | **28** | **58** |
| 1 | `f60` | 7 | 14 | 29 | 59 |
| 1 | `f120` | 6 | 14 | 29 | 59 |
| 2 | `def` | 6 | 13 | 29 | 59 |
| 2 | **`f30`** | 7 | **12** | **28** | **58** |
| 2 | `f60` | 7 | 14 | 29 | 59 |
| 2 | `f120` | 6 | 14 | 29 | 59 |
| 3 | `def` | 6 | 14 | 29 | 60 |
| 3 | **`f30`** | 7 | **12** | **28** | **58** |
| 3 | `f60` | 7 | 14 | 29 | 59 |
| 3 | `f120` | 6 | 14 | 29 | 59 |

`def` varies by ±1 (the known tail); **ff30 is identical in all three pairs and 2 ticks
low**; ff60 (the 1:1 ratio control) and ff120 sit inside the default tail. The shift tracks
the **fixed-fps ratio** (2 physics steps per idle frame at ff30), not the flag as such: at
ff30 the finish can only be observed on an idle frame, so a 30-tick (0.5 s) cycle is
reported at 28 ticks = 14 frames × 2 steps. Same effect in `r94b_ffprop` (`ff30_frt` →
31 ticks quiet, 28 ticks under the ff30 harness).

### 4.2 The one row that breaks — `cpu_pause` rejects 3/3 at ff30 [A]

```
runs/ff30/r94_particles_cpu_pause.rep{1,2,3}.out
PASS particles_lattice cpu_pause ok=false vis_ok=true vis_parent_ok=false pm_disabled_ok=false ts0_ok=true
 | vis[fin_after_show=4 n=1] vis_parent[fin_after_show=2 n=1] pm_disabled[fin_after_enable=2 n=1] ts0[fin_after_restore=18 n=1]
```
The same cell is `ok=true` in quiet, load, ff60, ff120 and ff120load (e.g.
`runs/ff120/r94_particles_cpu_pause.rep1.out`: `vis_parent[fin_after_show=4]`,
`pm_disabled[fin_after_enable=4]`). The scout's window is `_okb(…, 4, 7)` for the three
"resume with the remaining lifetime" levers; at ff30 the parent-visibility and
process_mode lanes land on **2**. The `vis` and `ts0` lanes still pass.
**This is the only `ROWS_PREFIX` rejection in the whole 6-condition matrix (3 of 323
classifier checks).**

---

## 5. Attack 3 — the engine `fixed_fps` *property* (scout §8 gap) [M]/[A]

`r94b_ffprop` (fresh one-shot L=0.5 e=1 per config, same process; `fract_delta` = `fr`):

```
quiet   ff1_frt[fin_ph=-1  proc_ms=1327..1330 n=0]  ff1_frf[fin_ph=-1 n=0]
        ff5_fr{t,f}[34..35]  ff30_fr{t,f}[31..32]  ff60_frt[30]  ff1000_frt[30]
ff30    ff1_fr{t,f}: never (proc_ms=1325/1333)   ff5[32]  ff30[28]  ff60[28]  ff1000[28]   (2/2 reps)
ff120   ff1_fr{t,f}: never (proc_ms=1325/1333)   ff5[35]  ff30[30]  ff60[30]  ff1000[30]   (2/2 reps)
```
(`runs/quiet/r94b_ffprop.rep{1,2,3}.out`, `runs/ff30/…`, `runs/ff120/…`)

- **`fixed_fps=1` never emits `finished`**: a dedicated 240-tick (4 s) arm confirms it in
  **every** condition — `runs/quiet/r94b_ff1_long.rep{1,2,3}.out` (`fin_ph=-1 fin_pf=-1
  proc_ms=3998.1 ph_total=240 n_fin=0`), `runs/ff30/…`, `runs/ff60/…`, `runs/ff120/…`
  (`proc_ms=3991.7 ph_total=240 n_fin=0`). The emitter accumulates 4 s of process time and
  the cycle never ends. **[?] mechanism** — a lossless accumulator with a 1 s quantum would
  have ended by ≤1.5 s, so the low-quantum path is not a plain accumulator; not resolved
  here (no engine source on this host).
- **The end time *does* move** — by up to one quantum: `ff5` → 0.586 s (+0.086 s, quantum
  0.2 s), `ff30` → 0.516 s (+0.016 s, quantum 0.033 s), `ff1000` → 0.497 s. So the scout's
  law-3 phrasing ("does not move the end time") is true only for `fixed_fps ≥ 60`.
- **`fract_delta` does not change the end time materially** (±1 tick in the quiet window,
  identical under ff30/ff120) — and `fract_delta=false` does **not** rescue `fixed_fps=1`
  (`ff1_frf` stalls too).
- **Author rule: never author `fixed_fps` ≤ 5; `fixed_fps=1` is a hang, not a slow cycle.**

---

## 6. Attack 4 — `request_particles_process`: the closed form is `floor(L/step)+1` [A]

`r94b_req_var` (Engine.time_scale=0, L=0.5), identical in **quiet, load and ff120**
(`runs/quiet/r94b_req_var.rep*.out`, `runs/load/…`, `runs/ff120/…`):

| step | measured `fin_call1` | scout's `round(L/step)+1` | `floor(L/step)+1` |
|---|---|---|---|
| 0.05 | 11 | 11 ✓ | 11 ✓ |
| 0.10 | 6 | 6 ✓ | 6 ✓ |
| 0.15 | 4 | 4 ✓ | 4 ✓ |
| **0.20** | **3** | 4 ✗ | 3 ✓ |
| 0.25 | 3 | 3 ✓ | 3 ✓ |
| **0.30** | **2** | 3 ✗ | 2 ✓ |
| 0.40 | 2 | 2 ✓ | 2 ✓ |

The scout fitted two integer ratios (0.1, 0.05) where the two formulas coincide; the
non-integer steps falsify `round`. `floor(L/step)+1` fits all seven. Also measured:
the residual argument **does** change the arithmetic (`step 0.10 res 0.02` → **5** instead of
6), and the lattice is **tps-invariant** (tps120 reproduces 6 and 3 exactly) and
**load/ff-invariant** — the "clock-free by construction" claim survives everything.
**Author rule: pin `fin_call1` only for integer `L/step` ratios, or restate the row with
`floor`.**

---

## 7. Attack 5 — the amount-setter hazard [M]/[A]/[U]

### 7.1 The `one_shot=true` hazard is rock-solid and its mechanism is not what was written

`cpu_amount_mid` is **byte-identical in all 6 conditions** (`fin_after_set=0 n_fin=1
em_fin=true ise_fin=true em_at_end=false`) — the spurious finish, the still-true
`emitting`/`is_emitting()` at the signal, and the suppressed genuine finish all reproduce.

But the mechanism note is wrong in two ways:

- **The signal is not synchronous in the setter.** `r94b_amount_sync` reads `n_fin` with no
  `await` after the assignment: `n_fin_sync=0 sync_fired=false n_fin_after_frame=1`
  (`runs/quiet/…`, `runs/load/…`, 6/6). The setter only arms it.
- **It fires on the node's next `_process`, in the same idle frame** —
  `r94b_amount_attr`: `sync_n_fin=0 frames_to_fire=1 d_ph=0 d_pf=0` (3/3 quiet, 2/2 load).
  `fin_after_set=0` is therefore a *frame-order* fact (the probe resumes from
  `await process_frame` before node processing, so the setter and the update share a frame),
  which is why it is stable across tps and `--fixed-fps`.
- **A second set does not fire again**: `second_n_fin=1 second_sync_fired=false` — only the
  first `amount` write of a cycle is armed.
- **Setting `amount` before emission starts does not fire** — `r94b_amount_pre`
  `never_emitting_n_fin=0` (the node must be explicitly `emitting=false`; the class default
  is `emitting=true`, and the scout's `discover6.amount_pre_start` receipt that shows
  `n_fin=1` is the *natural* end at tick 30, not a spurious fire).

### 7.2 `cpu_amount_mid` is the one row that survived every mode — including ff30

`fin_after_set=0` holds at ff30/ff60/ff120 despite the frame-ratio change, so the pinned pair
(`fin_after_set=0` + `em_fin=true`) is portable as long as the probe keeps the
"resume-then-set" shape.

### 7.3 The continuous-emitter claim (scout F17) is **unstable [U]**

The scout's F17 refuted "the spurious finished also fires for continuous emitters" with a
single `one_shot=false` control. Re-running **their own frozen arm**
(`scout_discover6.gd`, byte-copy) in this seat's conditions:

| condition | `disc6 amount_cont` (`set_ph=30`) |
|---|---|
| quiet (3/3) | `n_fin=0` |
| load (3/3) | `n_fin=0` |
| ff30 | `n_fin=0` |
| **ff60** | **`n_fin=1`** |
| ff120 | `n_fin=0` |

and this seat's bisect arms (each the **first** node of its own process, so node order
cannot confound; `runs/reprobe/r94b_amount_b{1..4}.rep*.out`, 3/3 identical each):

| arm | config | set tick | result |
|---|---|---|---|
| `b1` | scout-exact (direct assignment, plain counter) | 30 | `at_set=0 total=0` |
| `b2` | scout-exact | **10** | `at_set=1 total=1` |
| `b3` | scout-exact + this seat's `_watch` handler | 30 | `at_set=0 total=0` |
| `b4` | scout-exact via `Object.set()` | 30 | `at_set=0 total=0` |

So the handler and the property-API are *not* the difference — the **set tick** is, and
node order matters too: `r94b_amount_phase` (8 sequential continuous nodes, 5th node at
t=30) fires at t=10, 20, 29, 30, 31, 45, 60 and not at t=5 in one window (in the quiet
window it fired at t=5 as well: `t5[fire=1]`).
**Verdict: the amount→`finished` coupling for `one_shot=false` emitters is not a law; it is
a phase/order-dependent effect that can appear or vanish with the same artifact. Author
rule: pin the amount hazard for `one_shot=true` only; never build a battery row on
"continuous emitters are immune".**

---

## 8. Attack 6 — law 12 is not "process-global" [A]

The scout's law 12 (and report hazard 4, and F18) says a never-emitting emitter fires
`finished` on its first update *because any emitter has run in the process*. That framing is
wrong; there is no global state. The reprobe matrix (final probe, `sync=`/`add_pf=`
instrumented, 3/3 identical *outcome* each; `runs/reprobe/r94b_contam_*.rep*.out`):

| arm | prior state | never-node `add_pf` (3 reps) | never-node result |
|---|---|---|---|
| `contam_g` | **nothing** (created in `_initialize`) | **0** | **clean** `fin_delta=-1 n=0` |
| `contam_f` | prior node added + freed in frame 0 | **0** | **clean** `-1 / 0` |
| `contam_j` | **nothing**, then `await _wait_ph(2)` | 1 | **fires** `fin_delta=0 n=1` |
| `contam_k` | parentless instance, freed, wait | 1 | fires |
| `contam_d` | parentless instance (`emitting=true`), freed, wait | 1 | fires |
| `contam_h` | a **never-emitting** node live 3 ticks | 1..3 | fires |
| `contam_a` | scout-exact: emitter 5 ticks, freed | 4..8 | fires |
| `contam_b` | node **updated 5 ticks, never emitting**, freed | 5..9 | fires |
| `contam_c` | emitter live | 2..6 | fires |
| `contam_e` | prior **CPUParticles3D** emitter | 4..6 | fires |

**`add_pf=0` → clean (6/6 receipts: `contam_f`+`contam_g` × 3 reps, all `add_pf=0`);
`add_pf≥1` → fires (24/24 receipts: `contam_a/b/c/d/e/h/j/k` × 3 reps, every one
`add_pf≥1`)** — the exact `add_pf` value varies with the window (4–8 for the 5-tick arms),
the 0/non-zero boundary does not. `sync=0` in every row, so the signal is not produced by
the `emitting=false` setter. `contam_first` proves it inside a single process: the node
added in frame 0 is clean while the node added later fires
(`frame0_never[fin_delta=-1 n=0] late_never[fin_delta=0 n=1]`, 3/3 quiet).

**Reframed law (this seat's):** *a never-emitting CPUParticles2D emits `finished` on its
first update unless it was added to the tree before the process's first idle frame.* The
scout's positive control (`cpu_contam`, `never1/never2` both `fin_delta=0`) is still
reproduced — but it is reproduced by *any* later-added node, not by the prior emitter.
**Author rule: a "never emits ⇒ no `finished`" cell is only valid if the node is created in
the probe's first frame (as `cpu_never` does); "one emitter per process" is neither
necessary nor sufficient.**

---

## 9. Attack 7 — GPU inertness, and the labrat dispatch

- `gpu_headless ok=true` in **all 6 conditions** (0/57 rejections everywhere): no `finished`
  (one-shot/continuous/manual), one-shot clears `emitting` silently, continuous keeps both
  flags, `capture_rect()` is a zero rect, `request_particles_process` is a no-op.
- **`flip_after` is wider than "3–7"**: measured values across the matrix are
  **1** (quiet `runs/quiet/r94_particles_gpu_headless.rep*.out`, ff120), 3, 4, 5, 6, 7
  (+`-1` for the continuous lane). The scout's own §6.2 says "do not pin `flip_after`" —
  that guidance is right; the range quoted in the report is not.
- **Frozen `probeParent` dispatch (one labrat, L2, read-only).** One dispatch was made with
  a bounded, read-only-falsifiable hypothesis (all 143 receipts postdate the frozen probe;
  the corpus agrees on one probe hash). The seat returned **INCONCLUSIVE with no receipts**:
  its substrate exposed only `find_file_by_name`/`grep`/`read` — no shell, no `stat`, no
  `git`, no `python3`. It did, however, independently **confirm the sha256 contradiction**
  (`RECEIPTS.md` `09dd7723…` vs `manifest.sha256` `e6a2e0f5…`) from the files alone, and
  confirmed the receipts are gitignored. The mtime/verifier half of the hypothesis was then
  run by this seat (§2). No second dispatch was made; the labrat wrote nothing.

---

## 10. Row-portability verdict for the author (the deliverable)

`ROWS_PREFIX` (the 19 boolean-block signatures, loaded read-only from
`../r94-scout/author-rows.py.txt`) classified by the production `classify_process`
(segment sha `749fa0607e7707e6…`) over **this seat's receipts on the frozen probe**:

| condition | checks | rejected | which |
|---|---|---|---|
| quiet | 57 | **0** | — |
| load (16 hogs, loadavg 118–126) | 57 | **0** | — |
| **ff30** | 57 | **3** | `r94_particles_cpu_pause` ×3 (`ok=false`) |
| ff60 | 57 | **0** | — |
| ff120 | 57 | **0** | — |
| ff120load | 38 | **0** | — |
| **total** | **323** | **3** | |

- **The 19 rows are re-established on the frozen revision** (they had never been verified
  against it — §2). All 19 pass under quiet and under 16-hog load.
- **`r94_particles_cpu_pause` must not be shipped as-is**: it rejects under `--fixed-fps 30`
  (3/3). Either drop the three `fin_after_*` tick windows from the gate (keep
  `vis_ok/ts0_ok`, or widen to 1–7), or pin only `n=1`/`ok` booleans.
- **Full-line (`ROWS`) rejections** on the frozen probe: 17 quiet, 12 load, 27 ff30, 30 ff60,
  21 ff120 — i.e. the scout's "use `ROWS` only in a quiet window or as an envelope" rule is
  correct, and the ±1 tail widens to **±2** under ff30 (and ±1 under load/ff60/ff120).
- **Every other boolean gate is scheduler-proof**: `cpu_lifetime`/`cpu_expl`/`cpu_speed_pre`
  (the ladder and streamed formula), `cpu_stop`, `cpu_never`, `cpu_contam`,
  `cpu_oneshot_off/flag`, `cpu_restart`, `cpu_retrigger`, `cpu_lt_mid`, `cpu_speed_mid`,
  `cpu_amount_mid`, `cpu_request`, `gpu_headless`, and the 3 pure cells.
- **tps fragility (not covered by any of the 6 conditions):** the ladder rows' `_okb` windows
  are 60-tps-only (§3). A battery cell that changes `Engine.physics_ticks_per_second` will
  reject `cpu_lifetime`/`cpu_expl`/`cpu_speed_pre` regardless of the boolean gate.

---

## 11. Remaining risks / not measured

- **Mechanism of the `fixed_fps=1` stall is [?]** (no engine source on this host). The
  observable (4 s, no `finished`, every condition) is solid; the "quantum-truncated delta"
  explanation does not fit the `fixed_fps=5/30` rows, which do advance.
- **Mechanism of the `add_pf` rule is [?]**: "added before the first idle frame ⇒ clean" is
  an empirical rule over 11 arms × 3 reps; the engine-side flag was not read. The candidate
  "first-frame delta == 0" explanation is **refuted** — `contam_first` measured the frame-0
  probe's first delta at **0.0317–0.0779 s**, not 0.
- **The amount hazard for continuous emitters is [U]** (§7.3): set tick, node order and
  `--fixed-fps` all flip it. Not resolved to a rule; do not pin.
- **Host was never idle** (loadavg 69–147, concurrent batteries). Every "quiet" number is
  host-conditioned; the process:physics ratio here (2.1–2.5:1 at 60 tps) differs from the
  scout's canonical window (which behaved ~1:1) and from r91's 1.0–2.5.
- **Not re-tested / not measured**: per-particle observables (still no API), GPU collision /
  sub-emitters / trails / turbulence / attractors (still readback-only headless),
  `use_fixed_seed` determinism, `amount_ratio`/`interp_to_end`/`interpolate`, the
  `convert_from_particles` loss matrix beyond the two parameter sets, `CPUParticles2D` +
  `CanvasItemMaterial`, 120-tps *streamed* (e≠1) ladders, `fixed_fps` values between 1 and 5.
- **`--fixed-fps` is a harness mode**, not a shipping config — but a battery cell booted with
  it (r86 nested-boot pattern) will reject `cpu_pause` and read the ladder 2 ticks low.

---

## 12. Host cleanup

- **0 timeouts** (no rc=137 in 683+51 receipts); no godot process from this lane remains
  (`pgrep -fa 'r94b_particles|scout_particles_lattice|scout_discover6'` → only the grep
  itself); the 3 system-wide godot processes are other lanes'.
- This seat's own `yes` hogs were killed by `stop_load` + the batch EXIT trap after every
  load batch (16 each in `load`, `ff120load`); the system-wide `yes` count (48 at session
  start, 64–128 during, other lanes') was never touched by this seat beyond its own PIDs.
- **0 B stderr** on every matrix + reprobe receipt; **0 non-zero rc**.
- No tracked file written: `git status --porcelain` shows only the pre-existing
  ` M corpus/fixtures/run_battery.py` and other lanes' untracked churn. No `.godot/` cache
  was created in any project dir (checked).
- `manifest.sha256` covers every artefact under `corpus/live/r94-boundary/`.

---

## 13. Evidence index

All under `corpus/live/r94-boundary/`; `manifest.sha256` covers every artefact.

| artefact | path | notes |
|---|---|---|
| scout frozen probe (byte-copy) | `probes/scout_particles_lattice.gd` | sha256 `e6a2e0f5…b930` = the committed r94 scout file |
| scout discover-6 (byte-copy) | `probes/scout_discover6.gd` | sha256 `213d4cb1…` |
| seat attack probe (28 arms) | `probes/r94b_particles.gd` | frame_ratio, clock_unit, tps30/120, ffprop, ff1_long, amount_{sync,attr,pre,cont,phase,b1..b4}, contam_{a..k,first}, gpu_probe, req_var |
| launch project | `proj/project.godot` | sha256 `8de8b3af…` = `corpus/fixtures/project.godot` |
| driver (7 batches) | `run_matrix.sh` | `timeout -s KILL 25` |
| reprobe driver | `run_reprobe.sh` | final-revision contamination + bisect |
| analyzer → JSON + text | `analyze_r94b.py` → `runs/analyze_r94b.json`, `runs/analysis.txt` | classifier + envelopes + arm payloads |
| receipts | `runs/{quiet,load,ff30,ff60,ff120,ff120load,ab,reprobe}/*.{out,err,rc,wall}` | 734 runs |
| batch log | `runs/rc-summary.txt` | loadavg per batch, hog counts, timeout check |
| key receipts | `runs/ff30/r94_particles_cpu_pause.rep{1,2,3}.out` (the rejection) · `runs/ab/ab*_f30_cpu_lifetime.rep1.out` (ladder shift) · `runs/quiet/r94b_clock_unit.rep1.out` (time clock) · `runs/quiet/r94b_tps{30,120}.rep1.out` (tps) · `runs/quiet/r94b_ff1_long.rep1.out` (stall) · `runs/quiet/r94b_req_var.rep1.out` (floor lattice) · `runs/reprobe/r94b_contam_{g,j,first}.rep1.out` (add_pf rule) · `runs/reprobe/r94b_amount_b{1..4}.rep1.out` (bisect) · `runs/ff60/r94b_disc6_amount_cont.rep1.out` (F17 flip) | |
| receipts index | `RECEIPTS.md` | batch table + replay commands |

Reproduce: `bash run_matrix.sh all && bash run_reprobe.sh && python3 analyze_r94b.py`
(expect `ROWS_PREFIX rejected=3` — all three `cpu_pause` at ff30 — and 0 elsewhere).
