# game-dev-2d round 90 — scout (r90-scout): the RigidBody2D authorability lattice, pre-measured; 10 rows verbatim-ready

Seat `SCOUT` (LEAF) | lane `r90-scout` | round 90 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps default (plus a generated 120 tps project variant), GodotPhysics2D.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at session start **`00a1416`**
(*r87 boundary: just_\* one-physics-step pulse law solved*); HEAD moved to **`1ecca1b`**
mid-session (a concurrent lane's SCORECARD backfill commit, no probe-relevant file). All
measurements here are probe/API receipts independent of that commit; the launch `project.godot`
is pinned in `manifest.sha256` (`8de8b3af…`, byte-copy of `corpus/fixtures/project.godot`).

**No git mutation, no tracked file written, no subagent, no commit.** Writes are this report and
`corpus/live/r90-scout/**` only. `git status --porcelain` shows no modified tracked file; the
pre-existing modified `corpus/fixtures/run_battery.py` and the untracked `corpus/fixtures/*`
leftovers (r87 lane) pre-date this session and are untouched.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server installed;
`definition`/`references`/`hover` were **unavailable for every file touched**. Semantic carriers:
fresh-process execution receipts, `ClassDB`/`ProjectSettings` runtime introspection inside the
probe, and engine-emitted error text. Every `file:line` below is engine-emitted `at:` backtrace
text, never a source read.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Primary: the RigidBody2D authorability lattice** — `gravity_scale` (incl. 0/negative/fractional
and `constant_force` equivalence), `center_of_mass` AUTO/CUSTOM + the refusal boundary, the
`inertia` write-override, `_integrate_forces` ordering/`custom_integrator` write-through, the
impulse family on known shapes, plus the adjacent unmeasured extras (`freeze`/`freeze_mode`,
`lock_rotation`, `can_sleep`/`sleeping`, the contact instrument, and the damping lattice that the
r88 census tripped over). This is the **census's top-ranked REMAINING PINNABLE family**: r88 §2
orders the surfaces Geometry2D → geometry bridge → **RigidBody2D gravity/COM/integrator** →
multiplayer → spawner → sprite → lights → audio/vis nulls; r89 §7 explicitly hands the
"RigidBody2D extras" family to r90+ as the first untouched PINNABLE block, and the census's own
§8 names the `custom_integrator` Δ (c vs a) as the one dissection it left open **[I]** — this
round closes it (§4). Two facts justify the pick beyond rank: the family is **physics-await**
territory, exactly where r89's "duration pin" lesson and r87's frame-stamp hazards live, so it is
the highest-information surface to pre-measure for flakiness; and its pins are **analytic** —
every value below is checked against closed-form semi-implicit-Euler arithmetic, which no
previous surface allowed. **r87 leftovers weighed, not taken:** `event_index 1..31` is already
*measured* (r87 §4: `1..31` silent no-op, `≥32` refused with `input.cpp:1010`; the open part is
what the field is *for*, which needs upstream source absent on this host), and the SubViewport
cursor needs a display server / frame-sequenced probe (r89 §7 declined it for the same reason);
neither appears anywhere in the census ranking, so neither displaces the ranked family **[O]**.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `bash run_cells.sh` | 12 cells (3 pure ×3, 7 physics-await ×6, 2 tps-split ×3) = 57 runs | `runs/` |
| 2 | `python3 analyze_r90.py` | per-cell reps / out-uniq / err-uniq / rc vectors | `analyze_r90.json` |
| 3 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 10 verbatim CASES rows, classified with the production `classify_process` | `author-rows.py.txt` |

**Canonical cell set: 57 runs across 12 cells** — 3 cells × 3 reps (pure readback: `props`,
`comread`, `comrefuse`) and 7 cells × 6 reps (every physics-await/lifecycle cell: `gravity`,
`damp`, `order`, `write`, `impulse`, `freezelock` @`--frames=120`, `contacts`), plus 2 tps-split
cells × 3 reps (`gravity` @120 tps, 120 and 60 frames). 71 godot launches in total (57 canonical
+ 14 smoke launches, 10 surviving receipts under `runs/smoke/`, from the probe revision).

**Byte-stability: 12 of 12 cells are `out_uniq=1` `err_uniq=1` with a constant rc vector.**
`analyze_r90.py` prints `UNSTABLE=[]` and `CRASH_CELLS=[]`. **No bimodal cell exists in this
surface — no envelope or mode-distribution is needed for any row below.** rc vectors all `0`;
one ERROR-carrying cell (`rb_comrefuse`, deterministic 286 B stderr, §3.3).

**Arm-dispatch integrity [O]:** every arm prints its own name on its `PASS` line, so the 12
signatures are pairwise distinct and a silent `_:` fallback (the r88 dead-seat failure) is
impossible to miss. `arm` is parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan), not the inverted pair that killed r88.

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **`gravity_scale` lattice** (0/0.5/1/2/−1, zero-g + v0, `constant_force`) | **PINNABLE**, exact linearity + census reproduction | 6 | uniq=1 |
| **damping lattice + live `total_linear_damp` oracle** | **PINNABLE** — explains the census's non-round 478.3405 | 6 | uniq=1 |
| **`_integrate_forces` ordering** (callback vs integration) | **PINNABLE** — callback is **post-integration** | 6 | uniq=1 |
| **`custom_integrator` write-through** (v=0 hold, transform hold, manual gravity) | **PINNABLE** — write is authoritative, one step late | 6 | uniq=1 |
| **impulse family on known shapes** | **PINNABLE** — analytic-exact ω = ±J·r·inv_I | 6 | uniq=1 |
| **`freeze`/`freeze_mode`/`lock_rotation`/sleep** | **PINNABLE** — incl. KINEMATIC freeze does **not** integrate velocity | 6 | uniq=1 |
| **contact instrument** (count/pos/velocity/signal) | **PINNABLE** | 6 | uniq=1 |
| **`center_of_mass` modes + `inertia` override** | **PINNABLE**; `center_of_mass_local` **does not exist** | 3 | uniq=1 |
| **`center_of_mass` refusal under AUTO** | **PINNABLE**, loud ERROR + silent same-value no-op | 3 | uniq=1 (1 ERROR) |
| **RigidBody2D property/API census** | **PINNABLE** (88 props, defaults, engine damp oracles) | 3 | uniq=1 |
| **tps split of the gravity fall** | measured: the pin is **tps-dependent at equal duration** with damp on | 3+3 | uniq=1 |

---

## 3. Measured values, verbatim

### 3.1 Property/API census (`props`) — [M]

```
PASS rb_lattice props nprops=88 props=[mass|physics_material_override|gravity_scale|Mass Distribution|center_of_mass_mode|center_of_mass|inertia|Deactivation|sleeping|can_sleep|lock_rotation|freeze|freeze_mode|Solver|custom_integrator|continuous_cd|contact_monitor|max_contacts_reported|Linear|linear_velocity|linear_damp_mode|linear_damp|Angular|angular_velocity|angular_damp_mode|angular_damp|Constant Forces|constant_force|constant_torque|disable_mode|Collision|…|editor_description] u_center_of_mass=6 u_center_of_mass_local=-1 u_inertia=6 u_linear_damp=6 u_angular_damp=6 u_constant_force=6 u_constant_torque=6 u_freeze_mode=6 u_sleeping=6 methods=[_edit_get_state|_edit_set_state|_integrate_forces|add_constant_central_force|add_constant_force|add_constant_torque|apply_central_force|apply_central_impulse|apply_force|apply_impulse|apply_torque|apply_torque_impulse|force_update_transform|get_angular_damp|get_angular_damp_mode|get_constant_force|get_constant_torque|get_gravity|get_gravity_scale|get_linear_damp|get_linear_damp_mode|set_angular_damp|set_angular_damp_mode|set_constant_force|set_constant_torque|set_gravity_scale|set_linear_damp|set_linear_damp_mode] enum=COM_AUTO=0,COM_CUSTOM=1,FM_STATIC=0,FM_KINEMATIC=1,CCD_OFF=0,CCD_RAY=1,CCD_SHAPE=2,DAMP_COMBINE=0,DAMP_REPLACE=1 ps_gravity=980.0000 ps_ldamp=0.1000 ps_adamp=1.0000 ps_tps=60 d_mass=1.0000 d_inertia=0.0000 d_center_of_mass=0.0000,0.0000 d_center_of_mass_local=<null> d_center_of_mass_mode=0 d_gravity_scale=1.0000 d_custom_integrator=false d_freeze=false d_freeze_mode=0 d_lock_rotation=false d_can_sleep=true d_sleeping=false d_continuous_cd=0 d_max_contacts_reported=0 d_contact_monitor=false d_linear_damp=0.0000 d_linear_damp_mode=0 d_angular_damp=0.0000 d_angular_damp_mode=0 d_constant_force=0.0000,0.0000 d_constant_torque=0.0000
```
(Prop list abridged at `…` only in this report; the `PASS` line is the full 88-entry pin.)

- **`center_of_mass_local` is not a property on this build** — `u_center_of_mass_local=-1`,
  `d_center_of_mass_local=<null>` **[M]**. The r88 census's "`center_of_mass` reads back the set
  value under CUSTOM" stands; there is no second COM property to cross-check against.
- **Engine damp oracles:** `physics/2d/default_gravity=980`, `default_linear_damp=0.1`,
  `default_angular_damp=1.0`, `physics_ticks_per_second=60` **[M]**. This is the missing input
  that made the census's `478.3405` look arbitrary (see §4.2).
- **Defaults:** body `linear_damp`/`angular_damp` read `0.0000` while the *effective* defaults
  are 0.1/1.0 — the r86 `linear_damp`-reads-0.0 write-override class, now confirmed for both
  damp axes **[M]**. `inertia` reads `0.0000` (auto-override, §3.2).
- `get_gravity()` exists on RigidBody2D (`methods` list); its callability/semantics were **not**
  measured (it is not the `_integrate_forces` state's `total_gravity`, which is measured).

### 3.2 `center_of_mass` modes + `inertia` override (`comread`) — [M]

```
PASS rb_lattice comread auto_com=0.0000,0.0000 auto_mode=0 coml_prop=<null> custom_mode=1 custom_com=4.0000,0.0000 rot_com=4.0000,0.0000 inertia5=5.0000 inertia0=0.0000 inertia33_mass4=33.0000 inertia33_mass1=33.0000 gscale_neg=-1.5000 gscale0=0.0000
```

- AUTO reads `(0,0)`; CUSTOM reads back the set `(4,0)`; a body rotated `PI/2` reads back the
  set `(4,0)` **unchanged** (no frame transform is applied to the stored value) **[M]**.
- **`inertia` is a pure write-override**: `5.0→5.0`, `0.0→0.0`, `33.0` survives both a mass
  change to 4 and back to 1 (`33.0000` both) **[M]**. Effective inertia is only visible in
  `_integrate_forces` (`state.inverse_inertia`, §3.6).

### 3.3 `center_of_mass` refusal boundary (`comrefuse`, ERROR-carrying) — [M]

```
PASS rb_lattice comrefuse auto_set4=com=0.0000,0.0000 mode=0 auto_set0=com=0.0000,0.0000 mode=0 custom_set4=com=4.0000,0.0000 mode=1 custom_set0=com=0.0000,0.0000 mode=1 back_auto=com=0.0000,0.0000 mode=0
```
stderr (deterministic, 286 B, exactly **one** ERROR):
```
ERROR: Condition "center_of_mass_mode != CENTER_OF_MASS_MODE_CUSTOM" is true.
   at: set_center_of_mass (scene/2d/physics/rigid_body_2d.cpp:376)
```

- Setting a **different** COM while mode is AUTO is **refused loudly** (`com` stays `(0,0)`,
  mode stays 0) **[M]**.
- Setting the **same** value while AUTO is a **silent no-op** — no second ERROR line **[M]**;
  the guard is value-gated. (Author it as one `expected_errors` entry; both branches are in the
  same row.)
- Switching back to AUTO resets the readback to the computed `(0,0)` **[M]**.

### 3.4 `gravity_scale` lattice (`gravity`) — [M], census §3.6 reproduced byte-exact

```
PASS rb_lattice gravity f30=g0[y=0.0000,vy=0.0000]|g05[y=62.2838,vy=239.1703]|g1[y=124.5675,vy=478.3405]|g2[y=249.1351,vy=956.6811]|gm1[y=-124.5675,vy=-478.3405]|zv[y=-14.6187,vy=-28.5357]|zv0[y=-15.0000,vy=-30.0000]|cf[y=124.5675,vy=478.3405] f60=g0[y=0.0000,vy=0.0000]|g05[y=241.1125,vy=466.6662]|g1[y=482.2250,vy=933.3325]|g2[y=964.4500,vy=1866.6649]|gm1[y=-482.2250,vy=-933.3325]|zv[y=-28.5238,vy=-27.1429]|zv0[y=-30.0000,vy=-30.0000]|cf[y=482.2250,vy=933.3325]
```

- `g1`/`g2`/`gm1`/`g0` equal the census's §3.6 values at both sample frames **[M]**; the
  lattice is exactly linear (`g05 = g1/2`, `g2 = 2×g1`, `gm1 = −g1`).
- **`zv0` (gravity 0, damp REPLACE 0, v0=(0,−30)) is exact linear motion**: `y=−15.0000`,
  `vy=−30.0000` @30f and `y=−30.0000`, `vy=−30.0000` @60f — `gravity_scale=0` removes gravity
  **and nothing else** **[M]**.
- **`zv` (same, default damp) is not linear**: `−14.6187/−28.5357` @30f — the 0.1 default damp
  acts on non-gravity motion too **[M]**. This is a one-line trap for authors.
- **`cf` (`constant_force=(0,+980)`, gravity 0) is field-identical to `g1`** at both frames
  **[M]**: a constant force of 980 on mass 1 is exactly `gravity_scale=1`, damping included.

### 3.5 Damping lattice + live oracle (`damp`) — [M]

```
PASS rb_lattice damp f30=default[y=124.5675,vy=478.3405]|rep0[y=126.5834,vy=490.0001]|rep05[y=116.9554,vy=435.1487]|comb05[y=115.1592,vy=425.1562] f60=default[y=482.2250,vy=933.3325]|rep0[y=498.1666,vy=979.9996]|rep05[y=425.5192,vy=773.6876]|comb05[y=412.9205,vy=739.6441] tld=default=0.1000|rep0=0.0000|rep05=0.5000|comb05=0.6000
```

- `state.total_linear_damp` inside `_integrate_forces` is the live oracle: **default body
  = 0.1000** (from `ProjectSettings`, not the property), REPLACE 0.0 → 0.0000, REPLACE 0.5 →
  0.5000, COMBINE 0.5 → **0.6000** (0.1 + 0.5) **[M]**.
- `rep0` (`linear_damp_mode=REPLACE, linear_damp=0.0`) is **undamped semi-implicit Euler**:
  measured `126.5834 / 490.0001` vs closed-form `465·g·dt² = 126.5833` / `30·g·dt = 490.0000`
  — a 1-ulp 4-dp float artifact, not a semantic gap **[M]**.

### 3.6 `_integrate_forces` ordering (`order`) — [M], the core law

```
PASS rb_lattice order ncb=60 cb0=st=0.016667 ty=0.2722 vy=16.3333 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb1=st=0.016667 ty=0.8162 vy=32.6394 … cb4=st=0.016667 ty=4.0743 vy=81.3949 … cblast=st=0.016667 ty=482.2250 vy=933.3325 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 f1=y=0.2722,vy=16.3333 f2=y=0.8162,vy=32.6394 f3=y=1.6315,vy=48.9184 f60=y=482.2250,vy=933.3325
```

- `ncb=60` for 60 awaited frames — exactly one callback per step **[M]**.
- **`cb0` equals `f1` field-for-field** (`ty=0.2722`, `vy=16.3333`): the callback sees the
  **post-integration** state of that step, i.e. `_integrate_forces` runs **after** the built-in
  gravity+damp velocity update and position update **[M]**. A velocity/transform write in the
  callback is therefore integrated on the **next** step (one-step lag).
- Live state values at every callback: `step=0.016667`, `total_gravity=980.0000`,
  `total_linear_damp=0.1000`, `inverse_mass=1.0000`, **`inverse_inertia=0.031250` = 1/32** —
  the exact analytic inertia of a radius-8 circle at mass 1 (`I = ½mr² = 32`) **[M]**.

### 3.7 `custom_integrator` write-through (`write`) — [M], census §3.8 arm c reproduced

```
PASS rb_lattice write step=0.016667 f30=wzero[y=0.0000,vy=0.0000]|whold[y=-50.0000,vy=0.0000]|wman[y=118.4167,vy=490.0001] f60=wzero[y=0.0000,vy=0.0000]|whold[y=-50.0000,vy=0.0000]|wman[y=481.8333,vy=979.9996]
```

- `wzero` (callback writes `linear_velocity=0` each step) stays at `y=0.0000, vy=0.0000`
  forever; `whold` (callback writes `transform.origin=(200,−50)`) stays at `y=−50.0000` —
  **the callback's state is authoritative** **[M]**.
- `wman` (manual `v += g·step`) reproduces the census's §3.8 arm-c **y** exactly
  (`118.4167` @30f) and adds the closed form: `118.4167 = Σ_{k=0}^{29} k·g·dt²`,
  `481.8333 = Σ_{k=0}^{59} k·g·dt²` @60f **[M]**. The engine applies **no** gravity and **no**
  damping in custom mode — otherwise these sums would not close.
- **One-step-lag arithmetic:** undamped built-in `126.5833` − manual `118.4167` = **8.1667 =
  30·g·dt²**; velocity `490.0000` − `473.6668` (census arm c) = **16.3333 = g·dt** **[M]**.
  The census sampled arm c's `linear_velocity` one step earlier than its `y` (its `v` is
  `29·g·dt`, its `y` is the 30-step position sum) — **[I]**, consistent with a callback-state
  read; this probe reads both from the node after the same await.

### 3.8 Impulse family on known shapes (`impulse`) — [M], analytic-exact

```
PASS rb_lattice impulse post=c_central[v=0.0000,-60.0000,w=0.0000,iI=0.031250,im=1.0000]|c_off[v=0.0000,-60.0000,w=-15.0000,iI=0.031250,im=1.0000]|c_tq[v=0.0000,0.0000,w=15.0000,iI=0.031250,im=1.0000]|r_tq[v=0.0000,0.0000,w=11.5200,iI=0.024000,im=1.0000]|r_off[v=0.0000,-60.0000,w=-11.5200,iI=0.024000,im=1.0000]
```

With gravity and both damps REPLACE-0, so the impulse is the only velocity change:

| lane | call | measured | closed form |
|---|---|---|---|
| `c_central` | `apply_central_impulse((0,−60))` | `v=(0,−60.0000)`, `ω=0` | `v=J/m` ✓ |
| `c_off` | `apply_impulse((0,−60),(8,0))` | `ω=−15.0000` | `−480·inv_I = −480/32` ✓ |
| `c_tq` | `apply_torque_impulse(480)` | `ω=+15.0000` | `480·inv_I` ✓ |
| `r_tq` | rect 20×10, torque 480 | `ω=11.5200` | `I=m(w²+h²)/12=41.6667`, `inv_I=0.024` ✓ |
| `r_off` | rect, off-center impulse | `ω=−11.5200` | ✓ |

`inv_I` is read live from `state.inverse_inertia` in the callback, so **every row carries its own
oracle** **[M]**. (The census's §3.7 `−12.6794/−4.2265/−3.1699` used an unstated shape; these
values are shape-annotated and analytically closed.)

### 3.9 `freeze` / `lock_rotation` / sleep (`freezelock`, 120 frames) — [M]

```
PASS rb_lattice freezelock f30=f_normal[y=-7.6969,vy=0.0000,w=0.0000,fz=false]|f_static[y=-100.0000,vy=0.0000,w=0.0000,fz=true]|f_kin[y=-100.0000,vy=-30.0000,w=0.0000,fz=true]|f_kin2[y=-100.0000,vy=-30.0000,w=0.0000,fz=true]|f_lock[y=-128.0000,vy=-60.0000,w=0.0000,fz=false] sleep=s_off[sl=false,y=-7.7000,vy=0.0000] s_on[sl=true,y=-7.7000,vy=0.0000]
```

- `f_normal` settles to the same solver-margin rest as the census bridge: `−7.6969` @30f,
  `−7.7000` @120f (ideal contact −8.0; the 0.3 px margin matches `82.3000` vs 82.0) **[M]**.
- `f_static` holds `−100.0000` — STATIC freeze is a true hold **[M]**.
- **`f_kin` and `f_kin2` both hold `−100.0000` with `vy=−30.0000` reported** — `FREEZE_MODE_
  KINEMATIC` does **not** integrate `linear_velocity` on this build, whether the velocity is set
  before the first step or after one step **[M]**. The velocity is stored/read back but never
  moves the transform (a documented-expectation trap; [I] for the intent, [M] for the behavior).
- `f_lock` (gravity 0, damps REPLACE 0, `lock_rotation`, off-center impulse): `y=−128.0000`,
  `vy=−60.0000` (= 28 steps × 1 px/step), `ω=0.0000` — `lock_rotation` fully suppresses the
  angular response **[M]**.
- Sleep: with `can_sleep=false` → `sleeping=false`; with `can_sleep=true` → `sleeping=true`,
  both resting at `−7.7000` after 120 frames **[M]**.

### 3.10 Contact instrument (`contacts`) — [M]

```
PASS rb_lattice contacts rest=y=-7.7000,vy=0.0000 cb=count=1 y=-7.7000 pos=0.0000,0.3000 cvel=0.0000,16.3333 entered=1
```

`contact_monitor=true`, `max_contacts_reported=4`: at rest the callback reads **one** contact at
`(0, 0.3000)` — the solver margin is visible *in the contact point* — with a pre-solve contact
velocity `(0, 16.3333)` (= `g·dt`, the last approach step's velocity), and `body_entered` fired
**once** **[M]**.

### 3.11 Runtime split: the gravity pin is tps-dependent with damp on — [M]

```
rb_tps120_f120 (120 tps, 120 frames = 1.0 s):  g1[y=478.1452,vy=932.9641]  zv0[y=-30.0000,vy=-30.0000]
rb_tps120_f60  (120 tps,  60 frames = 0.5 s):  g1[y=122.5250,vy=478.1458]  zv0[y=-15.0000,vy=-30.0000]
60 tps, 60 frames = 1.0 s (rb_gravity):        g1[y=482.2250,vy=933.3325]  zv0[y=-30.0000,vy=-30.0000]
```

- **Undamped motion is duration-exact and tps-invariant** (`zv0` identical at both tps) — the
  r89 bridge-style "duration pin" law holds here **[M]**.
- **Damped gravity fall is not tps-invariant at equal duration**: `482.2250` (60 tps) vs
  `478.1452` (120 tps) at 1.0 s — **0.85 % apart**, because the 0.1/s damp is discretized per
  step **[M]**. Closed-form recurrence `v←v(1−0.1·dt)+g·dt, y←y+v·dt` reproduces both
  (`482.2251`/`478.1449` @4 dp) **[M]**.
- Consequence: a frame-counted gravity row must state its tps **and** its damp config; the two
  tps cells are receipts, not portable rows (§6.3).

---

## 4. Laws (the two dissections the census left open)

### 4.1 Integrator ordering — [M]

**Built-in step order (GodotPhysics2D, 4.7.2):** velocity update (`v ← v·(1−damp·dt) + g·dt`),
then position update (`y ← y + v·dt`), **then** the script callback `_integrate_forces` with the
post-step state. Evidence: `cb0` ≡ `f1` field-for-field (§3.6); undamped `rep0` closes on
`Σ k·g·dt²` (§3.5); manual-gravity `wman` closes on `Σ_{k=0}^{n−1} k·g·dt²` with its velocity
write landing one step late (§3.7). **Author rule: in `_integrate_forces`, the state you read is
this step's result; the state you write is next step's input.**

### 4.2 The census `custom_integrator` Δ, decomposed — [M]

The r88 census's Δ (arm c `118.4167 / 473.6668` vs arm a `124.5675 / 478.3405`) is **two
effects, both now exact**:

1. **Damping.** Arm a runs with the engine default `linear_damp=0.1` (readable only via
   `ProjectSettings`/`state.total_linear_damp`, never the body property). Arm c's
   `custom_integrator=true` skips gravity **and** damping. Removing damping from the built-in
   (REPLACE 0) gives `126.5834 / 490.0001` (§3.5).
2. **One-step lag.** `126.5834 − 118.4167 = 8.1667 = 30·g·dt²` and `490.0000 − 473.6668 =
   16.3333 = g·dt` (§3.7). Arm c is the *same* integrator, one step behind.

A script-side manual gravity can therefore reproduce the built-in fall **exactly** by using
`v ← v + g·step` with `linear_damp_mode=REPLACE, linear_damp=0` on the body — at the cost of the
one-step phase offset.

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **`_integrate_forces` is post-integration** (§4.1) — an author who expects pre-step state (the
   intuitive model) writes a body that lags one step; pins must be written from these receipts.
2. **The default damp is invisible in the property** (`d_linear_damp=0.0000`, effective 0.1;
   angular 0.0 vs 1.0) **[M]**. Any body whose velocity should be analytic needs
   `DAMP_MODE_REPLACE, 0.0` on both axes — otherwise impulses decay ~0.17 %/frame linearly and
   ~1.7 %/frame angularly (measured: `−15.0000 → −14.5042` over two frames, §3.8 pre-fix).
3. **`gravity_scale=0` does not freeze motion** — the default damp still decays it
   (`zv` vs `zv0`, §3.4). Pin `zv0` for the clean law.
4. **`center_of_mass` under AUTO**: a *different* value is refused with a deterministic ERROR
   (`rigid_body_2d.cpp:376`), the *same* value is a silent no-op; `center_of_mass_local` does not
   exist **[M]**. Set the mode first.
5. **`FREEZE_MODE_KINEMATIC` does not integrate `linear_velocity`** on this build (§3.9) —
   do not author a moving-platform pin from it without a positive control; the transform holds.
6. **The gravity fall is tps-dependent when damp is on** (§3.11) — state tps+damp in any
   trajectory row; equal *duration* is not sufficient for byte-equal values at different tps.
7. **Solver margin is part of every rest pin**: `−7.7000` (not −8.0) and contact point `0.3000`
   above the floor top; the census's `82.3000` is the same class **[M]**.
8. **`inertia` reads `0.0000` when auto** and is a write-override; the live oracle is
   `state.inverse_inertia` (`0.031250` for r=8/m=1) **[M]**.
9. **`props` list contains property *group headers*** (`Mass Distribution`, `Solver`, `Linear`,
   `Angular`, `Constant Forces`, `Collision`, …) — a naive consumer of the 88-entry list will
   see them; they are editor groups, not properties **[O]**.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (10, exec-checked)

`corpus/live/r90-scout/author-rows.py.txt` holds the exact 5-tuples, and
`python3 verify_rows.py` classifies all 10 with the production `classify_process` (AST-extracted
verbatim from `corpus/fixtures/run_battery.py`, segment sha256 `749fa060…`) →
**`rows=10 rejected=[]`**.

```
rb_lattice_{props,comread,comrefuse,gravity,damp,order,write,impulse,freezelock,contacts}
```

Probe files land at `corpus/fixtures/rb_lattice.gd` (sha256 `4f201e85…`) and
`corpus/fixtures/rb_watch.gd` (sha256 `e349faa0…`, the `_integrate_forces` forwarder — **both
files are required**). `rb_lattice_freezelock` carries the two flags
`["--arm=freezelock", "--frames=120"]`; every other row is a single `--arm=` flag. Insert the
rows ahead of the crash/descendant tail like prior blocks; no other fixture change is needed.

**Not rows** (receipts only, do not author): `rb_tps120_f120` / `rb_tps120_f60` (need a 120 tps
project — only reachable via the r86 nested-boot pattern; they are the tps-dependence evidence,
§3.11).

### 6.2 `expected_errors` addition (dict in `run_battery.py`, keyed by case name)

```python
'rb_lattice_comrefuse': (
    'ERROR: Condition "center_of_mass_mode != CENTER_OF_MASS_MODE_CUSTOM" is true.',
),
```

Every other row is `ERROR:`-clean with **0 B stderr** (measured).

### 6.3 What to pin and what not to pin

1. **Pin the full `PASS rb_lattice …` line as the row signature** — it carries the arm name, so
   the row is arm-verified and the r88 silent-fallback failure cannot recur.
2. **Pin `tld=` in `rb_damp`** — it is the only place the effective (combined) damp is visible;
   the body property is a write-override and reads 0.
3. **Pin `iI=`/`im=` in `rb_impulse`** — each impulse row carries its own inertia oracle, so the
   ω pins are self-checking, not shape-assumed.
4. **Pin `cb0`≡`f1` in `rb_order`** — that equality *is* the ordering law; do not pin only the
   final frame.
5. **Do not pin ideal contact geometry** — pin `−7.7000` / `0.3000` / `−7.6969` as measured.
6. **Do not author a frame-counted gravity row without stating tps+damp** (§5.6).
7. **No envelope/mode-distribution is needed anywhere in this surface** — 12/12 cells are
   single-valued across 3–6 reps. If a future cell pairs `_integrate_forces` callbacks with
   frame-indexed counts, re-check against the r87 lesson before pinning.

---

## 7. Remaining unknowns / not measured

- **`get_gravity()`** on RigidBody2D is listed by `ClassDB` but was not called; its relation to
  `state.total_gravity` (and whether it works outside the callback) is untested.
- **KINEMATIC-freeze intent**: the transform holds under `linear_velocity` writes; whether
  `move_and_collide`-style server-side motion or a `PhysicsServer2D` state write moves it was
  not probed (only the node-side velocity was).
- **`center_of_mass` axis semantics**: the stored value reads back unchanged under a `PI/2`
  rotation; whether it is interpreted in global or local axes at integration time was not
  discriminated (no second property exists; the off-center-impulse ω was measured only with
  AUTO COM).
- **`continuous_cd`** modes read back (0/1/2) but their tunneling behavior was not measured
  (r80 covered CCD separately in `phys2d_motion`).
- **`max_contacts_reported` > 1** (multi-contact stacks) and `contact_monitor` with several
  bodies were not measured; only the single-resting-contact case.
- **Solver internals**: the 0.3 px margin's dependence on mass/radius/iterations is unmeasured
  (same open item r89 left).
- **`constant_force`/`constant_torque` accumulation semantics** (`add_constant_*` methods,
  per-frame vs persistent) were not split; only the static equivalence to `gravity_scale=1`
  was measured.
- **The census's `rb_com` shape**: its `−12.6794` cannot be recomputed without the probe's
  shape; this round's values are shape-annotated (§3.8), so the census values are superseded as
  pins.
- **`event_index 1..31` and SubViewport cursor** (r87 leftovers): unchanged, and still not
  reachable from this surface (§0).
- **Portability**: every value is this host/build/`--headless`/GodotPhysics2D; `DisplayServer`
  is headless in every receipt; 60 tps unless the cell name says `tps120`.
- **`lsp` absent**: all `file:line` citations are engine-emitted `at:` text.

---

## 8. Host cleanup

- 71 godot launches total = **57 canonical cell runs** + 14 smoke launches (10 surviving receipts:
  9 first-pass arms + the first `comrefuse` run; 4 files overwritten by the re-smoke) — **all
  `--headless`, all `timeout 25`-bounded** (bound never hit; all rc=0), no run left running.
- `pgrep -fa godot` at report time lists only concurrent lanes' processes (g3d
  `r100-scout`/`fe` runs; this repo's `r87-simplifier`/`r87-reviewer` runs) — **none from this
  seat**.
- No tracked file written: `git status --porcelain` shows no modified tracked file and no
  `corpus/fixtures/` addition from this seat.
- `manifest.sha256` (208 lines) covers every artefact under `corpus/live/r90-scout/`.

---

## 9. Evidence index

All under `corpus/live/r90-scout/`; `manifest.sha256` (208 lines) covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| primary probe, 10 arms | `probes/rb_lattice.gd` | `4f201e85e569c737` |
| `_integrate_forces` forwarder (required) | `probes/rb_watch.gd` | `e349faa0715421d7` |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| 120 tps variant project | `proj_tps120/project.godot` | `1bcaeba7d52c27ee` |
| driver (12 cells, 57 runs) | `run_cells.sh` | `2bccba5a944aa181` |
| analyzer → json | `analyze_r90.py` → `analyze_r90.json` | `ef96175becc59957` |
| author rows + verifier | `author-rows.py.txt`, `verify_rows.py` | see `manifest.sha256` |
| per-cell receipts (57 runs × 3 files) | `runs/` | `manifest.sha256` |
| superseded smoke receipts | `runs/smoke/` | `manifest.sha256` |

Reproduce: `bash run_cells.sh && python3 analyze_r90.py && python3 make_author_rows.py &&
python3 verify_rows.py` (expect `UNSTABLE=[]`, `CRASH_CELLS=[]`, `rows=10 rejected=[]`).
