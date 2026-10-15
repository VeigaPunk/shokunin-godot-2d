# game-dev-2d round 92 — boundary (r92-boundary): the 13 TileMapLayer rows under quiet / 12–32-hog load / `--fixed-fps` 1…600 / 120-tps project

Seat `BOUNDARY` (LEAF) | lane `r92-boundary` | round 92 | host **devin** (`plazir27`, 32 cores).
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
GodotPhysics2D. Repo `~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start
**`520ed6d`**, at write time **`e2cfb84`** (concurrent r93/r94/r95 lanes' folds). The only
tracked modification in the tree is a concurrent lane's `corpus/fixtures/run_battery.py`
(+74 lines); **no tracked file was written by this seat, no commit, no push.**

**Probe corpus.** The scout's frozen probe is carried as
`probes/scout_tilemap_lattice.gd` — byte-copy, sha256 `a699138945ec7c1c…` (identical to
`corpus/live/r92-scout/probes/tilemap_lattice.gd`); the launch projects `proj/` and
`proj_tps120/` are byte-copies of the scout's (`8de8b3af…` / `0b7c6491…`). Attack
instrument: `probes/r92b_probe.gd` (`sched`/`phys`/`nav`) and `probes/r92b_navmech.gd`
(`mech`/`cold`), plus the r91 scout's frozen `nav_lattice.gd` (`efb496e5…`) as the
positive control.

**Frozen probeParent disclosure.** Exactly **one** `ufo-labrat` (L2, read-only) was
dispatched with one bounded hypothesis ("at least one of the 13 rows is
scheduler-mode-sensitive"). It returned a static classification plus a ranked prediction
— top pick **`nav` `regions_f1` `1 → 0` under `--fixed-fps 30`** — and wrote nothing,
spawned nothing. Its prediction was **right in kind, wrong in mode**: `--fixed-fps 30`
is byte-identical (39/39); the flip is at `--fixed-fps ≥ 150`. Verbatim outcome in §7.

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host; every
`file:line` below is engine-emitted `at:` backtrace text. Probe authoring was direct file
writes (the fallback); no symbol-aware rename was needed.

**The host is shared.** Concurrent boundary lanes held the box at loadavg **56–150** with
32–112 `yes` hogs for the whole session. `quiet` below means **"no hogs added by this
seat"**, never an idle host. Seat hogs were killed after every load batch and no
orphaned `yes` (ppid≠1) remains; other lanes' hogs were left untouched.

**Legend:** **[M]** measured (fresh process); **[A]** ablation/refutation; **[I]** inference;
**[U]** unstable (payload differs).

---

## 0. What I ran

**667 fresh godot receipts, 20 batches, 0 timeouts, 0 watchdog FAILs, 639 rc sidecars all
`rc=0`.** Every run `timeout -s KILL 25`; max observed wall **2.51 s** (32-hog batch).
Full batch table, loadavg/hog accounting and replay commands: `corpus/live/r92-boundary/RECEIPTS.md`.

| condition family | `--fixed-fps` / project | idle:physics ratio (measured, in-situ) | runs |
|---|---|---|---|
| quiet 60 tps ×3 | default | 2.5–3, **irregular** (`[3,2,3,2…]`) | 39 |
| +12 seat hogs ×3 | default | 2.5–3 (physics is real-clock-driven) | 39 |
| +32 seat hogs ×2 (loadavg **145**) | default | ~0.5–3, irregular (`[0,0,0,0,1,2,1,3…]`) | 26 |
| repeat quiet ×2 | default | 2.5–3 | 26 |
| ×2 | `--fixed-fps 1` (extreme) | 1/60 | 16 (4 timing arms) |
| ×2 | `--fixed-fps 5` (extreme) | 1/12 | 16 (4 timing arms) |
| ×2 | `--fixed-fps 10` | 1/6 | 26 |
| ×2 | `--fixed-fps 20` | 1/3 | 26 |
| ×3 (+2 under load) | `--fixed-fps 30` | 1/2 | 39+26 |
| ×3 | `--fixed-fps 60` | 1 | 39 |
| ×3 (+2 under load) | `--fixed-fps 120` | 2 | 39+26 |
| ×2 each | `--fixed-fps` 150/180/200/210/240/300/400/480/600/900 | 2.5 / 3 / 3.3 / 3.5 / 4 / 5 / 6.7 / 8 / 10 / 15 | 20+20 (nav only) |
| ×3 | 120-tps project, default scheduler | ~0.5–1 | 39 |
| ×2 | 120-tps project × `--fixed-fps` 120/240/480 | 1 / 2 / 4 | 12 (nav only) |
| ×20/×20/×10/×10 | scout `nav` arm rate test (default / ff120 / ff150 / ff600) | — | 60 |

Plus the seat's own pollers (78 runs), a positive control on the r91 scout's `sync` arm
(9 runs), the mechanism probe (28 runs) and 16 extreme-scheduler runs. `await physics_frame`
was measured to be **exactly one physics step in every mode** (`phys_per_await=[1,…,1]`,
12/12 awaits, in every batch) — so the row payloads are physics-step-counted, not
wall-clock-counted, in all conditions tested.

---

## 1. Verdict table

| # | attack | verdict | one-line evidence |
|---|---|---|---|
| 1 | The 13 rows reproduce byte-identically in a fresh quiet window (3 reps each) | **CONFIRMED** | 39/39 `q60` + 26/26 `q60b` PASS lines byte-equal to the scout's canonical receipts |
| 2 | "No load-sensitive counter" — the scout's own claim, re-attacked with **≥12 seat hogs** | **CONFIRMED** | 39/39 `l60` + 26/26 `f120l` + 26/26 `f30l`, loadavg 64→93 |
| 3 | Same at **32 seat hogs** (2× oversubscription, loadavg **145.25**) | **CONFIRMED** | 26/26 `l32` identical; max wall 1.98 s |
| 4 | The 9 pure arms (census/atlas/cells/custom/terrain/pattern/encoding/fixinvalid/srcids) are scheduler-invariant | **CONFIRMED** | byte-identical under every `--fixed-fps` tested, **1 through 900**, and under both projects |
| 5 | `physics` / `timing` / `quadrant` (`_f1`/`_f2` lever lattice, incl. `travel=0.0000,1.9531`) are scheduler-invariant | **CONFIRMED** | 3 arms byte-identical in all 13 matrix conditions + ff1/ff5 extremes; independent poller reads `t_set=t_erase=t_dis=t_en=t_mv=t_notify=1` in **every** mode |
| 6 | `nav` is scheduler-invariant | **FALSIFIED [A]** | `regions_f1` **1 → 0** at `--fixed-fps ≥ 150` (idle:physics ≥ 2.5): ff150 **0/10**, ff600 **0/10**, default **20/20 = 1**, ff120 **20/20 = 1** |
| 7 | The scout's "60 ≡ 120 tps" clock-independence claim, **extended from 3 arms to all 13** | **CONFIRMED** | 39/39 `t120` identical (the scout had only run physics/timing/nav) |
| 8 | The one-physics-step law is *exactly* one physics step for the physics levers | **CONFIRMED** | frame pollers: `t_*=1` for all 6 levers, every mode (ff1…ff600, load, tps120) |
| 9 | `update_internals()` / `map_force_update()` are synchronous levers for the nav region | **REFUTED [A]** | same frame `n_force=0 n_upd=0`; **one `await process_frame` ⇒ `n_proc1=1`** — the registration lands on the idle/process path, not the physics path |
| 10 | The production classifier accepts the rows under every new condition | **CONFIRMED except nav/f600** | 416 gated receipts, `rejected=2` (both `f600_nav`), under both `ROWS` and `ROWS_PREFIX`; scout control 64/64 |
| 11 | This harness can see scheduler sensitivity at all (positive control) | **CONFIRMED** | r91 scout's frozen `sync` arm: `chg_settled` true 3/3 default vs **false 3/3** at ff120/ff30; `first_reach` 8/−1/−1 vs −1 3/3 |
| 12 | The labrat's prediction `nav regions_f1 1→0 under --fixed-fps 30` | **FALSIFIED as stated; correct in kind** | ff30 = 39/39 identical; the flip needs ratio ≥ 2.5, not ≥ 0.5 |

**Bottom line.** 12 of 13 rows are scheduler- and load-invariant across a wider matrix
than the scout ever ran (the scout varied only 60 tps, one 16-hog loadtest and a 120-tps
project). The **`r92_tilemap_nav` row is not**: its `regions_f1=1` key is a
phase-sensitive, idle-frame-driven read that flips to `0` as soon as the fixed-fps
scheduler runs more than two idle frames per physics step. Every other field of the nav
row — including `regions_f2=1` — is single-valued across all 126 nav receipts collected
here.

---

## 2. Positive controls — the attack was live

### 2.1 The scheduler really did change (seat's `sched` arm) **[M]**

```
default (quiet, loadavg 61)  phys_per_await=[1,1,1,1,1,1,1,1,1,1,1,1] proc_per_phys_await=[3,2,3,2,3,2,3,2,3,2,3,2] usec_per_phys_frame=16105.8
+32 hogs (loadavg 145)       phys_per_await=[1,…]                     proc_per_phys_await=[0,0,0,0,1,2,1,3,3,2,3,3] usec_per_phys_frame=9758.3
--fixed-fps 10               phys_per_await=[1,…]                     proc_per_phys_await=[0,0,0,0,1,0,0,0,0,0,1,0] usec_per_phys_frame=4.2
--fixed-fps 30               phys_per_await=[1,…]                     proc_per_phys_await=[1,0,1,0,1,0,1,0,1,0,1,0] usec_per_phys_frame=5.3
--fixed-fps 60               phys_per_await=[1,…]                     proc_per_phys_await=[1,1,1,1,1,1,1,1,1,1,1,1] usec_per_phys_frame=6.1
--fixed-fps 120              phys_per_await=[1,…]                     proc_per_phys_await=[2,2,2,2,2,2,2,2,2,2,2,2] usec_per_phys_frame=6.9
--fixed-fps 600              phys_per_await=[1,…]                     proc_per_phys_await=[10,10,10,10,10,10,10,10,10,10,10,10]
120-tps project (default)    phys_per_await=[1,…]                     proc_per_phys_await=[0,1,2,1,1,2,1,1,1,2,1,1] usec_per_phys_frame=7110.0
```

Two facts this pins: (a) `--fixed-fps` changes the idle:physics ratio from an
irregular, load-dependent 0.5–3 (default) to an exact constant — and makes the loop run
**~2500× faster than real time** (16.1 ms vs 4.2–6.9 µs per physics frame); (b)
`await physics_frame` remains **exactly one physics step** in every mode
(`phys_per_await` = twelve 1s in all 13 batches, both waves) — which is why 12 of the 13
rows survive.

### 2.2 The harness can see a scheduler-sensitive row (r91 control) **[M]**

The r91 scout's frozen `nav_lattice.gd --arm=sync` (sha256 `efb496e5…`) run through this
seat's launcher, `runs/control/`:

```
ctl_def   rep1  first_reach=8   chg_settled=true   dis_settled=false   first_reach_sync=1
ctl_def   rep2  first_reach=-1  chg_settled=true   dis_settled=false   first_reach_sync=1
ctl_def   rep3  first_reach=-1  chg_settled=true   dis_settled=false   first_reach_sync=1
ctl_ff120 rep1  first_reach=-1  chg_settled=false  dis_settled=false   first_reach_sync=-1
ctl_ff120 rep2  first_reach=-1  chg_settled=false  dis_settled=false   first_reach_sync=-1
ctl_ff120 rep3  first_reach=-1  chg_settled=false  dis_settled=false   first_reach_sync=-1
ctl_ff30  rep1  first_reach=-1  chg_settled=false  dis_settled=false   first_reach_sync=1
ctl_ff30  rep2  first_reach=-1  chg_settled=false  dis_settled=false   first_reach_sync=-1
ctl_ff30  rep3  first_reach=-1  chg_settled=false  dis_settled=false   first_reach_sync=1
```

The r91 row is **unstable even at 60 tps** on this host (`first_reach` 8/−1/−1) and
flips hard under `--fixed-fps` (`chg_settled` true→false). So the null result on the r92
rows in §3 is not a dead probe: the same harness, same launcher shape, same session
detects the r91 class of sensitivity immediately.

---

## 3. The 13 rows under all 13 matrix conditions **[M]**

Every cell below is the scout's `PASS tilemap_lattice <arm> …` line compared byte-for-byte
against the scout's own canonical receipt (`corpus/live/r92-scout/runs/r92_tm_<arm>.rep1.out`).
`OK` = identical in every rep of that condition. stderr is byte-identical too after
normalising only the probe filename inside engine backtraces
(`res://scout_tilemap_lattice.gd` → `res://tilemap_lattice.gd`; engine source paths and
line numbers unchanged).

```
arm         q60  l60  f30  f60  f120 f120l t120 q60b f10  f20  f600 f30l l32
census      OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
atlas       OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
cells       OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
custom      OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
terrain     OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
pattern     OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
encoding    OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
fixinvalid  OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
srcids      OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
physics     OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
timing      OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
quadrant    OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   OK   OK   OK
nav         OK   OK   OK   OK   OK   OK    OK   OK   OK   OK   DIFF OK   OK
```

The single `DIFF` (`runs/f600_nav.rep{1,2}.out`):

```
canonical:  PASS tilemap_lattice nav … regions_empty=0 regions_same_frame=0 regions_f1=1 regions_f2=1 …
ff600:      PASS tilemap_lattice nav … regions_empty=0 regions_same_frame=0 regions_f1=0 regions_f2=1 …
```

Aggregate: **432 scout-arm receipts outside the ratio scans, 2 mismatches** (both
`nav`/ff600); **126 nav receipts, 46 with `regions_f1=0`** and every other nav field
single-valued:

```
regions_f1 : 0 | 1            (bimodal)      regions_f2               : 1     (126/126)
regions_same_frame : 0        (126/126)      regions_after_plain_cell : 1     (126/126)
regions_disabled_same_frame : 1 (126/126)    regions_disabled_f1      : 0     (126/126)
regions_erased_same_frame   : 1 (126/126)    regions_reenabled        : 1     (126/126)
                                             regions_erased_f1        : 0     (126/126)
```

---

## 4. The nav falsification — where the row breaks, and why **[M]/[A]**

### 4.1 The flip is an idle:physics-ratio threshold, crossed with either knob

| scheduler | idle:physics | scout `nav` `regions_f1` | seat's own `nav` poller `t_reg_add` | receipts |
|---|---|---|---|---|
| default 60 tps | 2.5–3, **irregular** | **1** (20/20 rate test; 5 matrix reps) | 1 | `runs/reps/def20.*`, `q60_*` |
| `--fixed-fps 1`, `5`, `10`, `20`, `30`, `60` | 1/60 … 1 | **1** | 1 | `runs/extreme/`, `f10_*`…`f60_*` |
| `--fixed-fps 120` | 2 | **1** (20/20) | 1 | `runs/reps/ff120x20.*` |
| **`--fixed-fps 150`** | **2.5** | **0 (10/10)** | **2** | `runs/scan2/ff150_*`, `runs/reps/ff150x10.*` |
| ff180 / 200 / 210 / 240 / 300 / 400 / 480 / 600 / 900 | 3 … 15 | **0 (2/2 each)** | 2 | `runs/scan/`, `runs/scan2/` |
| 120-tps project, default | ~0.5–1 | **1** | 1 | `runs/scan2/t120_none_*` |
| 120-tps project × ff120 | 1 | **1** | 1 | `runs/scan2/t120_ff120_*` |
| 120-tps project × ff240 | 2 | **1** | 1 | `runs/scan2/t120_ff240_*` |
| **120-tps project × ff480** | **4** | **0 (2/2)** | **2** | `runs/scan2/t120_ff480_*` |

The cross-project rows are the discriminating control: the break tracks the **ratio**
(`fixed-fps ÷ physics_ticks_per_second`), not the fixed-fps value — ff240 at 60 tps
breaks (ratio 4) while ff240 at 120 tps is fine (ratio 2). The rate test is exact:

```
def20     reps=20 regions_f1: one=20 zero=0
ff120x20  reps=20 regions_f1: one=20 zero=0
ff150x10  reps=10 regions_f1: one=0 zero=10
ff600x10  reps=10 regions_f1: one=0 zero=10
```

So the scout's nav row is deterministic **inside** each mode and flips **between** modes.
It is not a row that can be pinned as a single-valued battery signature across a
fixed-fps harness.

### 4.2 The row's phase is the fragile part (cold write vs warm write) **[M]**

`probes/r92b_navmech.gd` reproduces the scout nav arm's phase exactly (`cold`: write the
first cell with **no prior physics step**) and contrasts it with a warm phase
(`mech`: 8 physics awaits first).

```
mode          cold  t_cold_add | warm  n_f1 | same-frame levers
default r1    cold  t=1        | mech  n_f1=1 | n_same=0 n_force=0 n_upd=0 n_proc1=1 n_proc2=1
default r2    cold  t=2        | mech  n_f1=1 | n_same=0 n_force=0 n_upd=0 n_proc1=1 n_proc2=1
ff120         cold  t=1        | mech  n_f1=1 | n_proc1=1
ff150         cold  t=2        | mech  n_f1=1 | n_proc1=1
ff240         cold  t=2        | mech  n_f1=1 | n_proc1=1
ff600         cold  t=2        | mech  n_f1=1 | n_proc1=1
t120_ff480    cold  t=2        | mech  n_f1=1 | n_proc1=1
```

- **Warm-phase writes register in exactly one physics step in every mode tested**, up to
  ratio 10 — the underlying registration path is not simply "ratio-broken".
- **Cold-phase writes (the scout's nav phase) take two physics steps at ratio ≥ 2.5.**
- `map_force_update(map)` and `layer.update_internals()` do **not** make the region
  visible in the write frame (`n_force=0`, `n_upd=0`), while **one `await process_frame`
  does** (`n_proc1=1` in every mode). The pending work is not in the server's queue yet;
  it is flushed on the idle/process pass — the same *class* of mechanism as the r91
  stall (server-synced state whose cadence is idle-frame-driven), not a wall-clock
  duration.
- Consequence for the scout's law: "a runtime write is applied at the next physics step"
  is exact for the **physics** levers and for **warm** nav writes, but the **cold** nav
  write is a *one-or-two* physics-step read whose value depends on how the idle passes
  interleave with the physics steps. The scout's own harness (60 tps, and a 120-tps
  project) only ever sampled ratio ≤ 2, where the cold value is 1.

Note the default-mode rep2 above: a structurally equivalent cold-write poller read **2**
at plain 60 tps on this host — i.e. even in the default harness the cold-phase latency
sits close enough to the flip point that a slightly different pre-write work profile
crosses it. The scout's own nav arm was 1 in all 28 default-mode receipts collected here
(3 quiet + 3 load + 2 repeat + 20 rate test), so the pinned value is *not* currently
flaky in the production shape — but it is not structurally guaranteed either.

### 4.3 What the scout could not have seen **[I]**

The scout varied (a) 60 tps, (b) a 16-hog loadtest, (c) a 120-tps *project* on 3 arms.
All three keep the idle:physics ratio ≤ 2 (the 120-tps project *lowers* it). The
`--fixed-fps` axis — which r91 proved is a different scheduler axis — was never run on
this surface, and it is exactly the axis that crosses the ratio-2.5 threshold. This is
the r91 lesson generalising: frame-counted rows are only as portable as the scheduler
that produced them, and a "no envelope needed" claim must name the scheduler regimes it
covers.

---

## 5. Independent re-gating with the production classifier **[M]**

`python3 verify_r92b.py` extracts `classify_process` verbatim (AST) from
`corpus/fixtures/run_battery.py` — segment sha256 **`749fa0607e7707e6`**, the same
segment r89/r90/r91/r92 pinned — and classifies every boundary scout-arm receipt
(stdout+stderr merged exactly like `run_process`, rc from the sidecar) against the
scout's `ROWS` and `ROWS_PREFIX`:

```
[BOUNDARY/ROWS(full-line)]             rows=13 receipts_checked=416 rejected=2
    q60 39/0  l60 39/0  f30 39/0  f60 39/0  f120 39/0  f120l 26/0  t120 39/0
    q60b 26/0 f10 26/0  f20 26/0  f600 26/2  f30l 26/0  l32 26/0
    REJECTED ('r92_tilemap_nav', 'f600', 'f600_nav.rep1.out')
    REJECTED ('r92_tilemap_nav', 'f600', 'f600_nav.rep2.out')
[BOUNDARY/ROWS_PREFIX(census-tail-cut)] rows=13 receipts_checked=416 rejected=2  (same two)
[SCOUT-CONTROL/ROWS]                    rows=13 receipts_checked=64  rejected=0
TOTAL rejected=4
```

The scout's own 64/64 acceptance reproduces; the boundary adds **416 gated receipts**
with **2 rejections**, both the ff600 nav receipts (the `regions_f1` flip). Note the
allowlists held everywhere else: the 9 error-emitting arms produce the same ERROR lines
under every scheduler, and no new `ERROR:`/`SCRIPT ERROR:`/`Parse Error:` appeared under
`--fixed-fps` (the only stderr deltas are the harness-local probe filename in backtraces).

---

## 6. Author directives (boundary-recommended, not a judgment)

1. **`r92_tilemap_nav` as written is not a portable row.** Either
   - pin **`regions_f2=1`** instead of (or in addition to) `regions_f1=1` — `regions_f2`
     is single-valued in all 126 nav receipts collected here, including every broken
     mode, and it is the settled form of the same claim; **or**
   - declare an **envelope** for `regions_f1` (`1` at idle:physics ≤ 2, `0` above) and
     record the scheduler regime with the row; **or**
   - keep the row but state that it is only valid for harnesses whose
     `fixed-fps ÷ physics_ticks_per_second ≤ 2` (which includes the scout's 60-tps and
     120-tps-project harnesses, and excludes any `--fixed-fps` battery ≥ 150).
2. **The other 12 rows need no envelope.** They survived ratio 1/60 … 15, loadavg 145,
   the 120-tps project and the probe's own 20 s watchdog, with byte-identical stdout
   *and* stderr.
3. **Pin the lever quartets, not single reads** (the scout's own §6.2.2) — confirmed
   here: the `_same_frame` / `_f1` / `_f2` quartets are what makes the physics/timing
   rows discriminating; a settled-only row would have lost the law.
4. **Do not use `update_internals()` or `map_force_update()` as a synchronous nav
   lever** — neither applies the region in the write frame (`n_force=0 n_upd=0`); one
   idle frame does.
5. **`travel=0.0000,1.9531`** (the only await-gated float in the row set) held
   byte-exactly in all 13 conditions and both projects — no envelope needed.
6. **Watchdog note:** the probe's 20 s timer is process-time based; under
   `--fixed-fps 1/5` the four timing-sensitive arms still complete (PASS, rc=0), so the
   watchdog is not a hazard in the regimes tested — but it is the first thing to check
   if a future fixed-fps battery reports `reason=watchdog` instead of a payload.

---

## 7. Falsification list (attacks and their outcome)

| id | hypothesis | result |
|---|---|---|
| F1 | The scout's 13 rows do not reproduce on a fresh host window | **REFUTED** — 65/65 quiet+repeat receipts byte-equal |
| F2 | ≥12 hogs expose a load-sensitive counter the scout's 16-hog loadtest missed | **REFUTED** — 91/91 load receipts identical (loadavg up to 145) |
| F3 | `--fixed-fps` breaks the TileMapLayer physics-lever lattice (the r91 pattern) | **REFUTED** — `physics`/`timing`/`quadrant` identical at ff1…ff900; pollers read `t=1` everywhere |
| F4 | `--fixed-fps` breaks the nav row | **CONFIRMED [A]** — `regions_f1 1→0` at ratio ≥ 2.5 (ff150+, and ff480 on the 120-tps project) |
| F5 | The nav break is a fixed-fps artifact (not a ratio effect) | **REFUTED** — ff240 is fine at 120 tps (ratio 2) and broken at 60 tps (ratio 4) |
| F6 | The nav cold/warm phase does not matter | **REFUTED** — warm `n_f1=1` at ratio 10; cold `t=2` at ratio ≥ 2.5 |
| F7 | `update_internals()` / `map_force_update()` close the nav same-frame window | **REFUTED** — `n_upd=0 n_force=0`; `await process_frame` ⇒ `n_proc1=1` |
| F8 | The 120-tps project claim only holds for the 3 arms the scout tested | **REFUTED** — extended to all 13, 39/39 identical |
| F9 | The rows are only accepted by the production classifier in the scout's own harness | **REFUTED except nav/f600** — 416 gated, 2 rejected |
| F10 | (labrat's ranked prediction) `nav regions_f1 1→0` under `--fixed-fps 30` | **FALSIFIED as stated** — ff30 identical 39/39; the mechanism it named (server-side, iteration-boundary read) is the right one |
| F11 | The r91 control row would reproduce identically in this harness (i.e. the harness is dead) | **REFUTED** — r91 `sync` row unstable in default (8/−1/−1) and flips `chg_settled` true→false under ff120/ff30 |
| F12 | The seat's own pollers are mode-insensitive (dead instrument) | **REFUTED** — `proc_per_phys_await` 0.167→15 across modes; `t_reg_add` 1→2 across the ratio-2.5 boundary |

---

## 8. Remaining unknowns

- **Exact engine ordering** of the nav-region flush relative to the physics step: the
  evidence pins *where* the pending work is (idle/process pass; `n_proc1=1`,
  `n_force=0`, `n_upd=0`) and *when* the value flips (ratio ≥ 2.5), not the precise
  call order inside `Main::iteration()`. No engine source tree on this host.
- **Other nav-polygon geometries**: one 4-vertex polygon on one cell only. Larger
  polygons / `TileMapLayer` navigation with `use_async_iterations` / multiple cells were
  not varied (the r91 async-bake axis is a different surface).
- **Threaded physics / Jolt**: default GodotPhysics2D only.
- **Default-scheduler ratio on a genuinely idle host**: this box never went below
  loadavg 56; a fast unloaded host would have a much higher default ratio (the loop is
  uncapped), which *could* cross the 2.5 threshold in plain 60-tps mode. Not measured
  (not available).
- **`--fixed-fps` with the rendering loop** (`--disable-render-loop` off, non-headless):
  not measured; every receipt here is `--headless`.
- **Portability**: every value is this host/build/`--headless`/GodotPhysics2D.

---

## 9. Host cleanup and evidence index

- 667 receipts, 639 rc sidecars, all `rc=0`; no run left running; no `timeout` kill
  fired; the seat's `yes` hogs were killed after every load batch (trap + explicit
  `kill`), and `ps` shows **no orphaned `yes`** (ppid≠1). Other lanes' hogs untouched.
- No tracked file written: `git status --porcelain` shows only the pre-existing
  ` M corpus/fixtures/run_battery.py` (concurrent lane) and untracked
  `corpus/live/r92-boundary/`; this report is a new untracked file.
- `corpus/live/r92-boundary/manifest.sha256` (2471 lines) covers every artefact under
  the lane directory.

| artefact | path |
|---|---|
| **this report** | `reports/round-92/r92-boundary.md` |
| frozen scout probe (byte-copy) | `corpus/live/r92-boundary/probes/scout_tilemap_lattice.gd` |
| attack pollers | `probes/r92b_probe.gd` (`sched`/`phys`/`nav`), `probes/r92b_navmech.gd` (`mech`/`cold`) |
| drivers | `run_matrix.sh`, `run_control.sh`, `run_nav_scan.sh`, `run_nav_scan2.sh`, `run_nav_reps.sh` |
| analyzers | `analyze_r92b.py` → `runs/analyze_r92b.json`; `verify_r92b.py` |
| matrix receipts | `runs/{q60,l60,f30,f60,f120,f120l,t120,q60b,f10,f20,f600,f30l,l32}_*.{out,err,rc,wall}` |
| ratio scans / rate test / mechanism / control / extremes | `runs/scan/`, `runs/scan2/`, `runs/reps/`, `runs/mech/`, `runs/control/`, `runs/extreme/` |
| batch log + loadavg accounting | `runs/rc-summary.txt`, `runs/matrix.log`, `runs/matrix2.log` |
| run inventory + replay + transcripts | `RECEIPTS.md` |
