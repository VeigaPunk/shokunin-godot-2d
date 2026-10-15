# game-dev-2d round 90 — boundary (r90-boundary): the RigidBody2D lattice under load, engine, tps and extreme-inertia stress

Seat `BOUNDARY` (LEAF) | lane `r90-boundary` | round 90 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, `--headless`),
GodotPhysics2D unless a cell says otherwise. Repo `~/Projects/shokunin/game-dev-2d-shokunin`,
HEAD at session start **`0628932`** (the r90 scout report itself is tracked at this HEAD).

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r90-boundary/**` only. The pre-existing dirty state
(` M corpus/fixtures/r88_surfaces.gd`, untracked `corpus/fixtures/__pycache__/…` and the
`corpus/live/r7x-*`/`r8x-*` lanes) pre-dates this seat and is untouched.
**Frozen probeParent:** this seat dispatched **zero** subagents — the assignment is a
single bounded stress sweep and the probe corpus is the seat's own; no `ufo-labrat` was
needed. (Recorded rather than silently omitted.)

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host;
every `file:line` below is engine-emitted `at:` backtrace text, never a source read.

**Legend:** **[M]** measured (fresh process, byte-identical over the stated rep count);
**[A]** ablation/refutation; **[I]** inference; **[U]** unstable (two payloads recorded);
**[?]** unknown.

---

## 0. What I ran

**281 receipted fresh godot runs** (299 launches: the dedicated 30 tps batch ran twice and
its identical second pass overwrote the first pass's 18 receipts; syntax-check smoke runs
were discarded). Every launch is `timeout -s KILL 25`-bounded, all rc=0, bound never hit,
0 stray children. Full batch table, load levels and reproduce commands: `RECEIPTS.md`.

| protocol | scope | receipts |
|---|---|---|
| `run_cells.sh all` | 8 batches: base/com/load1/load2/delay/dummy/t30/par | `runs/` |
| load tiers | L1 = 32 × `yes>/dev/null` system-wide (loadavg 20.10→25.91); L2 = godot `taskset -c 0,1` + 12 × `yes` pinned `-c 0-3`; `par` = 8-way/6-way concurrent godot | `.wall`, rc |
| starved-batch probe | in-process 300 ms `OS.delay_msec` at await 30, idle-context (`process_frame` lambda) and physics-context (inside the coroutine) | `b_stall_{none,idle,phys}` |
| startup-race positive control | `--delay=0/20/50/100/200/300` ms in the deferred `_run` | `d_order_d*` |
| 30 tps distribution | order ×9 + lag ×9, two passes | `t30_*` |
| engine split | `physics/2d/physics_engine` = DEFAULT / Dummy / `"Jolt Physics"` / `garbage_xyz` | `proj_*` |
| scout verbatim | **byte-copy** of `rb_lattice.gd` (sha256 `4f201e85…`) ×9 cells, baseline + L1 + L2 + par | `sv_*`, `l_sv_*`, `l2_sv_*`, `p_sv_*` |
| analyzer | per-cell rc/uniq/at-lines + claim checks + scout-pin equality | `analysis.txt`, `analyze_boundary.json` |

**Scout-pin reproduction [M]:** all 9 verbatim scout cells re-derived byte-exact at
baseline (`sv_order sv_damp sv_write sv_impulse sv_freezelock sv_contacts sv_gravity
sv_gravity_t120 sv_comrefuse`, 3/3 each) — and `sv_order`/`sv_freezelock`/`sv_contacts`
stayed **byte-identical across L1, L2 and 6-way concurrency** (one PASS hash per cell:
`764c523cd0c9…`, `3b6250190357…`, `0c9cecc3d1ee…`). **No scout pin is falsified.**

---

## 1. Verdict table

| # | attack | verdict | one-line evidence |
|---|---|---|---|
| 1 | `_integrate_forces` ordering law under CPU hogs / 120 tps | **CONFIRMED** (law); the `cb0≡f1` *pin* is **conditional on pairing** | 60/120 tps: `cb0_rel=obs0_rel=1`, `cb0≡f1` field-for-field, `ncb=pf_delta=frames`, per-await step `1:1`, byte-identical to baseline in **35/35** load+concurrency+delay runs at 60 tps (PASS hash `31c95133200e537a…` across baseline/L1/L2/par/delay) plus 3/3 at 120 tps; at 30 tps the pairing is `late_body` and the equality moves to `cb0≡f2` |
| 2 | damp oracle `0.1/0.0/0.5/0.6` stable across engines | **CONFIRMED on GodotPhysics2D; FALSIFIED as engine-portable** | same values at 60/120 tps and under load; under `physics_2d/physics_engine="Dummy"` the oracle reads **`-1.0000` (never written)**, `ncb=0`, no motion — the whole cell is vacuous; the only 2D engine names in the hint are `DEFAULT,GodotPhysics2D,Dummy`; unknown strings silently fall back to GodotPhysics2D |
| 3 | `8.1667 = 30·g·dt²` one-step-lag claim; tps 30/120 boundaries | **CONFIRMED** (formula, 30–240 tps); **UNSTABLE** (the `N` used at 30 tps) | closed form is `dy = n·g·dt²` with `n` = executed callbacks: 30 tps 32.6667/31.5778, 60 tps 8.1667/16.3333, 120 tps 2.0417/4.0833/8.1667, 240 tps 0.5104 — all exact; but at 30 tps `n` is **29 or 30 depending on the startup window** (both payloads in §4) |
| 4 | impulse at extreme inertia (`iI=0.031250`) — sign/precision flips | **CONFIRMED** (iI oracle, all signs); no sign flip found; **two adjacent typed refusals + oracle collapse at the extremes** | `inertia=-5` refused `:334` (stays auto, ω=+15); `mass<=0` refused `:324` (stays 1.0); `inertia=NaN/INF` accepted → `iI=0.000000`, ω=0.0000; `inertia=1e9` → `iI=0.000000` at 6 dp (row no longer self-checking); `inertia=1e-9` → ω=`480000016384.0000` (float32 rounding of 4.8e11) |
| 5 | `rigid_body_2d.cpp:376` the only COM error path; custom COM on static/frozen bodies | **CONFIRMED** | **18 scenarios × 3 reps**: every AUTO-mode set of a different value (incl. frozen STATIC, frozen KINEMATIC, out-of-tree, `set()`, NaN, mode 99/−1) emits exactly **1 ERROR at `:376`**; every CUSTOM-mode set (incl. frozen, out-of-tree, NaN) emits **0** and stores; no second COM path exists. (The file *does* carry `:324 set_mass` / `:334 set_inertia` refusals — different properties, §5.) |
| 6 | freeze/contact 120-frame window under load (starved batches) | **CONFIRMED** | rest is reached by **f60** and stable through f120 (≥2× margin: `n[y=-7.7000]` at f60/f90/f120), identical under L1/L2; `sv_freezelock`/`sv_contacts` byte-identical across all tiers; the 300 ms stall leaves `ncb=90/90`, `tick_dh=1:89` and the near-stall values **byte-equal to the no-stall control** |

---

## 2. Attack 1 — ordering law under load, concurrency and 120 tps **[M]**

**The invariant that survives every tier:** for each physics step `S`, the
`_integrate_forces` callback state equals the node state observed at the first
`await physics_frame` of that same step (`Engine.get_physics_frames()` matches:
`cb0_rel == obs0_rel`), and one await = one executed step (`ncb == pf_delta == frames`,
`tick_dh=1:(frames−1)`). Baseline at 60 tps, verbatim:

```
PASS rb90_boundary order ncb=60 cb0=st=0.016667 ty=0.2722 vy=16.3333 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb1=st=0.016667 ty=0.8162 vy=32.6394 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb2=st=0.016667 ty=1.6315 vy=48.9184 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb3=st=0.016667 ty=2.7177 vy=65.1702 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb4=st=0.016667 ty=4.0743 vy=81.3949 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cblast=st=0.016667 ty=482.2250 vy=933.3325 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 f1=y=0.2722,vy=16.3333 f2=y=0.8162,vy=32.6394 f3=y=1.6315,vy=48.9184 f60=y=482.2250,vy=933.3325 cb0_rel=1 obs0_rel=1 pf_delta=60 tick_dh=1:59 cbpf_dh=1:59
```

**Tier evidence (every 60 tps row's PASS line is byte-identical to the baseline above; the
120 tps rows are byte-identical to each other):**

| tier | runs | result |
|---|---|---|
| baseline 60 tps | 3 | `sync0`, `cb0≡f1`, 1:1 |
| L1 (32 hogs, loadavg→25.9) | 6 | identical |
| L2 (godot pinned 0,1; 12 hogs 0-3) | 3 | identical |
| 8-way concurrent processes | 8 | identical |
| `--delay=0/20/50/100/200/300` | 18 | identical — a startup delay does **not** flip the pairing at 60 tps |
| 120 tps (60 frames, 1.0 s wall) | 3 baseline + 3 L1 | `cb0=st=0.008333 ty=0.0681 vy=8.1667`, `cb0≡f1`, `ncb=pf_delta=60` |
| 30 tps | 3 + 9 | **`late_body`**: see below |

**30 tps alt payload (the one pairing that breaks the pin) [M]:**

```
PASS rb90_boundary order ncb=29 cb0=st=0.033333 ty=1.0889 vy=32.6667 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb1=st=0.033333 ty=3.2630 vy=65.2244 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb2=st=0.033333 ty=6.5188 vy=97.6737 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb3=st=0.033333 ty=10.8527 vy=130.0148 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb4=st=0.033333 ty=16.2609 vy=162.2481 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cblast=st=0.033333 ty=459.2563 vy=904.4226 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 f1=y=0.0000,vy=0.0000 f2=y=1.0889,vy=32.6667 f3=y=3.2630,vy=65.2244 f30=y=459.2563,vy=904.4226 cb0_rel=2 obs0_rel=1 pf_delta=30 tick_dh=1:29 cbpf_dh=1:28
```

At 30 tps the body is created **after** step 1's integration, so the first await
(`obs0_rel=1`) sees the un-integrated body (`f1=y=0.0000`) and the first callback is
step 2: `cb0 ≡ f2` (verified `cb0_eq_f2=True`, `cb0_ty=1.0889 == f2 y`), `ncb=29` for 30
awaits. The ordering law itself is intact (callback is post-integration; the state you
write lands next step); only the *pairing key* shifts. The scout's author rule
"`cb0` ≡ `f1`" is therefore **case-B-specific**: the robust row is
"callback at frame `F` ≡ node state at frame `F`", which needs `cb0_rel`/`obs0_rel`
(or a `pf_delta`-paired trace) to be checkable.

**Write-through under load** (`b_write`, L1 `l_write`): `wzero`/`whold` hold
(`y=0.0000` / `y=-50.0000`) and `wman` closes on `Σ_{k=0}^{n−1} k·g·dt²` in every tier
(`f30=wzero[y=0.0000,vy=0.0000]|whold[y=-50.0000,vy=0.0000]|wman[y=118.4167,vy=490.0001]`)
— identical baseline/L1.

---

## 3. Attack 2 — damp oracle across engines **[M]/[A]**

**On GodotPhysics2D the oracle is stable at both tps and under load.** `tld=` reads
`default=0.1000|rep0=0.0000|rep05=0.5000|comb05=0.6000` at 60 tps, at 120 tps
(`ncb=120`) and under L1 — byte-identical. The position recurrences close at both tps
(`default 482.2250` / `478.1452` at 1.0 s; `rep0 498.1666` / `494.0834`), matching the
scout's §3.11 split.

**The split is GodotPhysics2D vs Dummy — and Dummy makes the entire cell vacuous [A]:**

```
PASS rb90_boundary backend cfg2d=Dummy hint2d=DEFAULT,GodotPhysics2D,Dummy id2d=PhysicsServer2DDummy cls_exists=GodotPhysicsServer2D=false,Dummy=true dss2d=PhysicsDirectSpaceState2DDummy drop=y=-100.0000,vy=0.0000 ncb=0 tld=-1.0000 pf_delta=30 tick_dh=1:29
PASS rb90_boundary damp f30=default[y=0.0000,vy=0.0000]|rep0[y=0.0000,vy=0.0000]|rep05[y=0.0000,vy=0.0000]|comb05[y=0.0000,vy=0.0000] f60=default[y=0.0000,vy=0.0000]|rep0[y=0.0000,vy=0.0000]|rep05[y=0.0000,vy=0.0000]|comb05[y=0.0000,vy=0.0000] tld=default=-1.0000|rep0=-1.0000|rep05=-1.0000|comb05=-1.0000 ncb=0 pf_delta=60 tick_dh=1:59
```

Under Dummy: **no `_integrate_forces` callbacks ever** (`ncb=0`), no motion, the `tld`
oracle is never written (`-1.0000`), yet `await physics_frame` still resumes 1:1
(`pf_delta=60`, `tick_dh=1:59`). The scout's whole family (damp, order, write, impulse,
freeze, contacts) is therefore **engine-scoped**: every pin silently becomes vacuous
under a Dummy boot — **0 B stderr, no warning** (consistent with r86 B7). Verbatim
scout cells under Dummy:

```
PASS rb_lattice freezelock f30=f_normal[y=-100.0000,vy=0.0000,w=0.0000,fz=false]|f_static[y=-100.0000,vy=0.0000,w=0.0000,fz=true]|f_kin[y=-100.0000,vy=-30.0000,w=0.0000,fz=true]|f_kin2[y=-100.0000,vy=-30.0000,w=0.0000,fz=true]|f_lock[y=-100.0000,vy=0.0000,w=0.0000,fz=false] sleep=s_off[sl=false,y=-40.0000,vy=0.0000] s_on[sl=false,y=-40.0000,vy=0.0000]
PASS rb_lattice contacts rest=y=-40.0000,vy=0.0000 cb=count=-1 y=0.0000 pos=0.0000,0.0000 cvel=0.0000,0.0000 entered=0
```

(`count=-1` is the probe's never-written sentinel; `entered=0` — no contact ever.)

**"Another 2D engine" does not exist in this build.** The property hint is
`DEFAULT,GodotPhysics2D,Dummy`; the 3D-only name `"Jolt Physics"` and the garbage string
both **silently fall back to GodotPhysics2D** and behave like DEFAULT:

```
PASS rb90_boundary backend cfg2d=Jolt Physics hint2d=DEFAULT,GodotPhysics2D,Dummy id2d=PhysicsServer2D cls_exists=GodotPhysicsServer2D=true,Dummy=false dss2d=GodotPhysicsDirectSpaceState2D drop=y=24.5675,vy=478.3405 ncb=30 tld=0.1000 pf_delta=30 tick_dh=1:29
PASS rb90_boundary backend cfg2d=garbage_xyz hint2d=DEFAULT,GodotPhysics2D,Dummy id2d=PhysicsServer2D cls_exists=GodotPhysicsServer2D=true,Dummy=false dss2d=GodotPhysicsDirectSpaceState2D drop=y=24.5675,vy=478.3405 ncb=30 tld=0.1000 pf_delta=30 tick_dh=1:29
```

---

## 4. Attack 3 — the one-step-lag law at tps boundaries **[M]/[U]**

Closed forms verified against every cell: with `dt=1/tps`, `n` = executed callbacks,
`a` = built-in undamped, `b` = `custom_integrator` manual gravity:
`a_y = g·dt²·n(n+1)/2`, `b_y = g·dt²·n(n−1)/2`, `dy = a_y − b_y = n·g·dt²`,
`bpre = (n−1)·g·dt`, `bpost = n·g·dt`, node `b.vy = a.vy` (`dvy=0.0000`).

| tps | frames | `n` | `a_y` | `b_y` | `dy` | `n·g·dt²` | pairing |
|---|---|---|---|---|---|---|---|
| 30 | 30 | **29** | 473.6667 | 442.0890 | 31.5778 | 31.5778 | `late_body` |
| 30 | 30 | **30** | 506.3334 | 473.6667 | 32.6667 | 32.6667 | `sync0` |
| 30 | 60 | 60 | 1992.6665 | 1927.3333 | 65.3333 | 65.3333 | `sync0` |
| 60 | 30 | 30 | 126.5834 | 118.4167 | **8.1667** | 8.1667 | `sync0` |
| 60 | 60 | 60 | 498.1666 | 481.8333 | 16.3333 | 16.3333 | `sync0` |
| 120 | 30 | 30 | 31.6458 | 29.6042 | 2.0417 | 2.0417 | `sync0` |
| 120 | 60 | 60 | 124.5417 | 120.4583 | 4.0833 | 4.0833 | `sync0` |
| 120 | 120 | 120 | 494.0834 | 485.9167 | 8.1667 | 8.1667 | `sync0` |
| 240 | 30 | 30 | 7.9115 | 7.4010 | 0.5104 | 0.5104 | `sync0` |

**The `N` at 30 tps is bimodal across windows [U].** Same probe revision, same project:
in the `all` sweep (19:12–19:17Z) both 30 tps lag cells ran `sync0` with `n=30`
(`exp=N=30 exp_dy=32.6667`, `a_y=506.3334`); in the two dedicated `t30` passes
(19:18–19:19Z) the same cells ran `late_body` with `n=29`
(`exp=N=29 exp_dy=31.5778`, `a_y=473.6667`) — 9/9 in each pass (the second pass's
receipts are the ones on disk; the first pass's identical payloads were overwritten by
the rerun). Every observed 30 tps `order` run was `late_body` (**12/12** on disk plus
3/3 in the earlier window). Both payloads:

```
# sync0 (all sweep)
PASS rb90_boundary lag a=y=506.3334,vy=980.0002 b=y=473.6667,vy=980.0002 c=y=490.3922,vy=934.0746 d=dy=32.6667,dvy=0.0000 step=0.033333 gdt=32.6667 gdt2=1.088889 exp=N=30 exp_dy=32.6667 exp_dvy_gdt=32.6667 acc=an=30,bn=30,apre=980.0002,bpre=947.3336,bpost=980.0002 pf_delta=30 tick_dh=1:29
# late_body (t30 passes)
PASS rb90_boundary lag a=y=473.6667,vy=947.3336 b=y=442.0890,vy=947.3336 c=y=459.2563,vy=904.4226 d=dy=31.5778,dvy=0.0000 step=0.033333 gdt=32.6667 gdt2=1.088889 exp=N=29 exp_dy=31.5778 exp_dvy_gdt=32.6667 acc=an=29,bn=29,apre=947.3336,bpre=914.6669,bpost=947.3336 pf_delta=30 tick_dh=1:29
```

**Consequence for the author:** the *formula* `dy = n·g·dt²` is tps-robust (30→240 tps,
1-ulp float32 artifacts only), but a pinned literal must state tps **and** must derive
`n` from the callback count (`exp=N=…`), not from `--frames`. At 30 tps the same
`--frames=30` run legitimately yields either 31.5778 or 32.6667 depending on the
startup window. This is the r88 startup step-count race (Case A/B) reappearing at the
r90 surface — and it is **not** load-triggered here: L1/L2/par/`--delay` never flipped
the 60 tps pairing.

**Velocity nuance (scout §3.7 restated).** Node-vs-node `dvy=0.0000` — the `b` node
readback equals `a` (`490.0001` at 60 tps/30 f). The `16.3333 = g·dt` gap in the scout
report is the **callback pre-write vs post-write** gap: `bpre=473.6668` (=29·g·dt,
inside the callback) → `bpost=490.0001` (=30·g·dt, and the node value). So "the state
you write is next step's input" is exactly the callback's `pre`/`post` pair, not a
node-property lag.

---

## 5. Attack 4 — impulse family at inertia/mass extremes **[M]**

15 lanes in one process, gravity 0, both damps REPLACE 0 (verbatim `post=` payload in
`runs/b_impulse.rep1.out`; `l_impulse` identical under L1):

| lane | setup | live `iI` | live `im` | measured | closed form / note |
|---|---|---|---|---|---|
| `auto` | default | 0.031250 | 1.000000 | ω=+15.0000, v=(0,−60) | 480·iI ✓ (r=8/m=1) |
| `zero` | `inertia=0.0` | 0.031250 | 1.000000 | ω=+15.0000 | **0 means AUTO**, not zero-inertia |
| `tiny` | `inertia=1e-6` | 1000000.000000 | 1.000000 | ω=480000000.0000 | 480·iI ✓ |
| `nano` | `inertia=1e-9` | 1000000000.000000 | 1.000000 | ω=480000016384.0000 | float32 rounding of 4.8e11 (print-only) |
| `huge` | `inertia=1e9` | **0.000000** | 1.000000 | ω=0.0000 | **oracle collapse**: true iI≈1e-9 prints `0.000000` → the row is no longer self-checking |
| `neg` | `inertia=-5.0` | 0.031250 | 1.000000 | ω=+15.0000 | **refused** `:334`; readback stays 0.0000 (auto) — no sign flip |
| `m_small` | `mass=0.001` | 31.249998 | 999.999939 | ω=14999.9990, v=−59999.9961 | float32 at 6/4 dp |
| `m_large` | `mass=1e6` | 0.000000 | 0.000001 | ω=0.0000, v=−0.0001 | 4 dp cannot resolve 6e-5 |
| `mass0` | `mass=0.0` | 0.031250 | 1.000000 | ω=+15.0000 | **refused** `:324`; stays 1.0000 |
| `massneg` | `mass=-1.0` | 0.031250 | 1.000000 | ω=+15.0000 | **refused** `:324` |
| `nan_i` | `inertia=NAN` | 0.000000 | 1.000000 | ω=0.0000 | **accepted silently**; readback `nan` |
| `inf_i` | `inertia=INF` | 0.000000 | 1.000000 | ω=0.0000 | **accepted silently** |
| `s_tqneg` | torque −480 | 0.031250 | — | ω=−15.0000 | sign ✓ |
| `s_offneg` | impulse at (−8,0) | 0.031250 | — | ω=+15.0000 | sign flips vs scout `c_off` (−15) ✓ |
| `s_up` | central (0,+60) | 0.031250 | — | v=+60.0000 | sign ✓ |

**No sign flip exists at either extreme**: negative inertia and non-positive mass are
refused loudly and leave the body at its previous (auto) state; the ω sign tracks
`cross(r, J)·iI` and `J·iI` everywhere. **Two adjacent typed refusals found** (same
file, different lines — relevant to §6's "only error path" scope):

```
ERROR: Condition "p_inertia < 0" is true.
   at: set_inertia (scene/2d/physics/rigid_body_2d.cpp:334)
ERROR: Condition "p_mass <= 0" is true.
   at: set_mass (scene/2d/physics/rigid_body_2d.cpp:324)
```

**Precision boundaries for the author:** the scout's "every impulse row carries its own
oracle (`iI=`/`im=`)" holds in the *normal* band (default shapes, mass 0.001–1e6 scale
fine at 4 dp). At `inertia≥~1e9` the 6-dp `iI` and 4-dp ω both print `0.0000…` and the
row stops discriminating "no response" from "response below print precision"; at
`mass=1e6` the velocity pin prints `-0.0001` for a true 6e-5. Do not extend impulse
rows into those extremes without higher-precision printing.

---

## 6. Attack 5 — the COM refusal boundary, 18 scenarios **[M]**

One scenario per process, 3 reps each, all rc=0. `err` = ERROR-line count per run.

| scenario | body state at the set | `com` / `mode` after | err | `at:` |
|---|---|---|---|---|
| `intree_auto_diff` | in tree, AUTO | `0.0000,0.0000` / 0 | 1 | **:376** |
| `intree_auto_same` | in tree, AUTO, same value | `0.0000,0.0000` / 0 | 0 | — |
| `intree_custom_diff` | in tree, CUSTOM | `4.0000,0.0000` / 1 | 0 | — |
| `frozen_static_auto_diff` | `freeze=true` STATIC, AUTO | `0.0000,0.0000` / 0 (also after unfreeze) | 1 | **:376** |
| `frozen_kin_auto_diff` | `freeze=true` KINEMATIC, AUTO | `0.0000,0.0000` / 0 | 1 | **:376** |
| `frozen_static_custom_diff` | frozen STATIC, CUSTOM | `4.0000,0.0000` / 1 | 0 | — |
| `frozen_kin_custom_diff` | frozen KINEMATIC, CUSTOM | `4.0000,0.0000` / 1 | 0 | — |
| `nottree_auto_diff` | **not in tree**, AUTO | `0.0000,0.0000` / 0 (also after add) | 1 | **:376** |
| `nottree_custom_diff` | not in tree, CUSTOM | `4.0000,0.0000` / 1 | 0 | — |
| `set_via_set` | `b.set("center_of_mass", …)`, AUTO | `0.0000,0.0000` / 0 | 1 | **:376** |
| `mode_invalid` | `center_of_mass_mode=99` | mode reads **99** | 1 | **:376** |
| `mode_neg` | `center_of_mass_mode=-1` | mode reads **4294967295** (uint32 wrap) | 1 | **:376** |
| `custom_freeze_sequence` | CUSTOM → freeze → set(8,0) | `8.0000,0.0000` / 1 (also after unfreeze) | 0 | — |
| `auto_nan` | AUTO, `(NAN,NAN)` | `0.0000,0.0000` / 0 | 1 | **:376** |
| `custom_nan` | CUSTOM, `(NAN,NAN)` | `nan,nan` / 1 | 0 | — |
| `frozen_static_auto_then_mode` | frozen STATIC, AUTO set (1 err) then CUSTOM set | `4.0000,0.0000` / 1 | 1 | **:376** |
| `custom_back_auto_diff` | CUSTOM → AUTO → set(4,0) | `0.0000,0.0000` / 0 | 1 | **:376** |
| `custom_dupe` | CUSTOM, same then new value | `8.0000,0.0000` / 1 | 0 | — |

Verbatim refusal payload (identical stderr for every refusal case):

```
ERROR: Condition "center_of_mass_mode != CENTER_OF_MASS_MODE_CUSTOM" is true.
   at: set_center_of_mass (scene/2d/physics/rigid_body_2d.cpp:376)
```

**Verdict [M]: `:376` is the only COM error path — CONFIRMED.** Freeze (both modes) is
not special-cased, out-of-tree bodies take the same node-side guard, `Object.set()` takes
the same path, and the guard is value-gated (`auto_set0` silent) and comparison-based
(`NaN != 0` → refuse; `NaN` under CUSTOM stores `nan,nan`). Two boundary extras the
scout did not state: `center_of_mass_mode` accepts **99** and **−1** without validation
(−1 reads back as **4294967295**, a uint32 wrap) and both then refuse COM at `:376`.
The scout's single `expected_errors` entry needs no change for the row as authored
(the frozen/not-tree/NaN cases are *not* in the scout's row — see §8).

---

## 7. Attack 6 — freeze/contact window under starved batches **[M]**

**Window margin (`b_settle`, 120 frames, floor top 0):**

```
PASS rb90_boundary settle f30=n[y=-7.6969,vy=0.0000] c[y=-7.7000,cnt=1,ent=1] so[y=-7.7000,sl=false] sf[y=-7.7000,sl=false] f60=n[y=-7.7000,vy=0.0000] c[y=-7.7000,cnt=1,ent=1] so[y=-7.7000,sl=true] sf[y=-7.7000,sl=false] f90=n[y=-7.7000,vy=0.0000] c[y=-7.7000,cnt=1,ent=1] so[y=-7.7000,sl=true] sf[y=-7.7000,sl=false] f120=n[y=-7.7000,vy=0.0000] c[y=-7.7000,cnt=1,ent=1] so[y=-7.7000,sl=true] sf[y=-7.7000,sl=false] ncb=45 pf_delta=120 tick_dh=1:119
```

The falling body reaches rest (`-7.7000`) by **f60** and is unchanged at f90/f120 —
**≥60 frames of margin** inside the 120-frame window; the contact body rests from f30
(`cnt=1, ent=1`); `can_sleep=true` sleeps by f60, `can_sleep=false` never does. L1 and
L2 receipts are byte-identical (same PASS). The scout's `f_normal[y=-7.6969]` @30 awaits
is a **transient** (one step from rest) — pin it only with the pairing key from §2.

**Scout verbatim under load — byte-identical across all tiers** (`sv_freezelock` hash
`3b6250190357…` × 3 baseline + 6 L1 + 3 L2 + 6 concurrent; `sv_contacts` hash
`0c9cecc3d1ee…` × 3+6+3+6; `sv_order` `764c523cd0c9…` × 3+3+3+6).

**Injected stall (the r84 accumulator-clamp class) does not perturb step accounting:**

```
PASS rb90_boundary stall stall=idle stall_at=30 ncb=90 near=f29[y=124.5675,vy=478.3405]|f30[y=132.7988,vy=493.8766]|f31[y=141.2886,vy=509.3869]|f32[y=150.0364,vy=524.8712] fN=y=1061.5953,vy=1366.1176 pf_delta=90 tick_dh=1:89 cbpf_dh=1:89
PASS rb90_boundary stall stall=none stall_at=30 ncb=90 near=f29[y=124.5675,vy=478.3405]|f30[y=132.7988,vy=493.8766]|f31[y=141.2886,vy=509.3869]|f32[y=150.0364,vy=524.8712] fN=y=1061.5953,vy=1366.1176 pf_delta=90 tick_dh=1:89 cbpf_dh=1:89
```

A 300 ms `OS.delay_msec` at await 30 — idle-context (`process_frame` lambda, wall
+0.2 s) and physics-context (inside the coroutine) alike — leaves `ncb=90/90`,
`tick_dh=1:89` and **every near-stall value byte-equal to the no-stall control**. The
accumulator may clamp/drop *demand* (r84), but each executed step still emits one
`physics_frame` and resumes the coroutine exactly once, so a frame-counted window
remains step-exact under starvation. Under L1 (`l_stall_idle`) the same. **The
"starved physics batches" hazard class does not threaten the r90 pins; the only timing
hazard this surface has is the 30 tps startup pairing race (§2/§4).**

---

## 8. What the author should (and should not) pin

1. **Pin the ordering law with its pairing key.** Keep `cb0≡f1` *only* if the row also
   pins `cb0_rel=1 obs0_rel=1` (60/120 tps) — or re-word the law as "callback at frame
   `F` ≡ node at frame `F`". At 30 tps the same code is `late_body` (`cb0≡f2`,
   `ncb=29`); do not author a 30 tps row from the 60 tps literal.
2. **Every physics row states tps + engine.** The scout already states tps for the
   gravity split; extend that to the whole family: under `2d/physics_engine="Dummy"`
   every value in this family silently changes to "no motion / `ncb=0` / `tld=-1`" with
   0 B stderr. An engine guard (or at least a stated precondition) belongs on the rows.
3. **`rb_damp` is safe as authored** (tld + positions byte-stable at 60/120 tps and
   under load on GodotPhysics2D), but its evidence must name the engine.
4. **`rb_order`'s `cb0≡f1` needs the pairing key** (see 1); `rb_write` is safe
   (baseline = L1).
5. **Impulse rows are self-checking only in the normal inertia band.** Keep the scout's
   rows as authored; do **not** add extreme-inertia lanes to the pinned row without
   higher-precision printing — and if such a row is ever added, its `expected_errors`
   must carry `set_inertia … :334` / `set_mass … :324` refusals (a different error path
   than the COM row).
6. **`rb_comrefuse` needs no change** — `:376` is the only COM path, and the scout's
   row (one refusal + one silent no-op) is exactly reproducible. Optional hardening:
   the frozen/out-of-tree/NaN cases are *not* in the scout's row and all behave like the
   in-tree case, so nothing extra needs pinning.
7. **`rb_freezelock` (120 frames) and `rb_contacts` are load-proof as authored**;
   `f_normal=-7.6969` @30 awaits is a transient one step from rest — the stable rest pin
   is `-7.7000` at f60+.
8. **The `8.1667 = 30·g·dt²` decomposition is exact at 60 tps/30 f**; for other tps use
   `dy = n·g·dt²` with `n` from `exp=N=` (callbacks), never from `--frames` (30 tps is
   bimodal).

---

## 9. Host cleanup and provenance

- **281 receipted runs** (299 launches incl. the t30 rerun's overwritten receipts), all
  `--headless`, all `timeout -s KILL 25`-bounded, all rc=0 (bound never hit). No run left behind; `pgrep -fa '^yes$'` empty at exit (L1/L2 hogs
  killed in-batch, `load_stopped=1` in `runs/rc-summary.txt`).
- No tracked file written. At session start HEAD was `0628932` with a pre-existing
  ` M corpus/fixtures/r88_surfaces.gd` (other lane, left untouched); HEAD advanced
  mid-session to `fd59c11` by concurrent lanes' commits (r88 fold / r89 boundary / r91
  scout) — none touched this seat's receipts, which are probe/API measurements
  independent of those commits. At report time `git status --porcelain` shows **no
  modified tracked file**; this seat's additions are untracked
  (`corpus/live/r90-boundary/`, `reports/round-90/r90-boundary.md`).
- The host was concurrently loaded by other lanes throughout (loadavg 14–26); the
  baseline was taken under that same background, and the load tiers add their own
  hogs on top — every claimed invariance is *within-tier* byte-identity, so background
  load is covered rather than assumed away.
- `manifest.sha256` (1143 lines) covers every artefact under `corpus/live/r90-boundary/`
  except itself.

## 10. Evidence index

| artefact | path |
|---|---|
| boundary probe (9 arms) + forwarder | `corpus/live/r90-boundary/probes/b90.gd`, `b90_watch.gd` |
| scout verbatim byte-copies | `probes/scout_rb_lattice.gd` (`4f201e85…`), `probes/scout_rb_watch.gd` (`e349faa0…`) |
| driver (8 batches) | `run_cells.sh` |
| analyzer → json / text | `analyze_boundary.py` → `analyze_boundary.json`, `analysis.txt` |
| 281 receipts × 4 sidecars | `runs/*.rep*.{out,err,rc,wall}` |
| batch log + load state | `runs/rc-summary.txt` |
| batch/repro table | `RECEIPTS.md` |
| project variants | `proj/`, `proj_tps30/`, `proj_tps120/`, `proj_tps240/`, `proj_dummy/`, `proj_jolt2d/`, `proj_garbage/` |

Reproduce: `cd corpus/live/r90-boundary && bash run_cells.sh all && python3 analyze_boundary.py`
(expect every cell `rc=0`, `pass_uniq=1`, all `pins … all_ok=True`).
