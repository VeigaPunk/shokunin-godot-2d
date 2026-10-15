# game-dev-2d round 81 — boundary (g2d): the joint/layer lattice at its edges — 11 named classes, one engine abort, four cells touched

Seat `BOUNDARY` (LEAF) | lane `g2d` | round 81 | host **devin** (wave id not carried by this
seat's brief; r79/r80 headers record `shokunin-train-20261101-w19`).
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, sha256-addressed by
`--version` only), Python 3.14.7, 32 cores.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`27f465c`** (*r80 LOG: ADMIT-corr*) +
the r81 dirty landing (` M corpus/fixtures/run_battery.py`, `?? corpus/fixtures/phys2d_joints.gd`,
both untouched by this seat).

**READ-ONLY on tracked files. No commit. No tracked file read-modified.** Writes are this
report and `corpus/live/r81-boundary/**` only. The prior boundary seat died on a rate limit
mid-probe; its probe (`corpus/live/r81-boundary/proj/phys2d_jb.gd`, sha256 `0841a70b…`) and
its 9 receipt tags are inherited here, and every inherited arm is **re-measured** in this
seat's own 3-rep set rather than cited on trust (§0).

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this session and no
GDScript/Python language server is installed; `lsp status` is unavailable, so no definition/
reference/hover trace was possible and none is claimed. Semantic carriers are (a) fresh-process
execution receipts, (b) the engine's own line-exact error anchors, (c) controls that move one
variable at a time. Text `grep` was used **only** as a literal fallback to locate the landed
`phys2d_joints_*` rows and to count `RID()` occurrences in the landed fixture (§12) — recorded
here as literal search, never as semantic proof. No cold-start empty result is recorded as
absence.

**Legend.** **[M]** measured (fresh process, ×3 reps; stdout byte-stable unless stated);
**[I]** inference; **[A]** ablation/control (the claim was shown to move when one variable moved).

---

## 0. What I ran

One probe, one arm per process, the battery's exact launch shape —
`godot --headless --path corpus/live/r81-boundary/proj --script res://phys2d_jb.gd -- --arm=<name>`
— 8 s bound, merged stdout+stderr, per-rep raw files under `cells/<tag>.<arm>.rep<N>.{stdout,stderr}.txt`.

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `python3 -B corpus/live/r81-boundary/run_arms.py --reps 3 --tag final2` — **42 arms × 3 reps = 126 fresh Godot processes** | 0 | `arms-final2.json` (one row per arm: rc ×3, PASS line ×3, merged sha256 ×3, stderr errors) |
| 2 | `python3 -B corpus/live/r81-boundary/stability.py final2` | 0 | `stability-final2.txt` — per-row stream-stability breakdown (stdout bytes / stderr bytes / stderr multiset) |
| 3 | `godot --headless --path … --check-only --script res://phys2d_jb.gd` | 0 | parse gate before every run |
| 4 | inherited tags `smoke, iso, fix, fix2, fix3, bisect, combo, wnull, r81b` (prior seat) | — | `arms-*.json` + `cells/*` — superseded by `final2` for every arm it re-measures |

**Backend scope (restated per arm header, unchanged from r80/r81):** `physics/2d/physics_engine =
DEFAULT`, `run_on_separate_thread = false`, `physics_ticks_per_second = 60`, `default_gravity =
980`. Every row below is **GodotPhysics2D**; nothing here claims a Jolt-2D measurement.

**Stream stability (measured, `stability-final2.txt`).** All **42/42 rows' stdout is
byte-stable across the 3 reps**; stderr is byte-stable for **28/42**. Seven rows
(`spring_negative`, `spring_nonfinite`, `groove_zero`, `groove_nonfinite`, `pin_soft_ext`,
`motor_huge`, `joint_bias_env`) have a **stderr line multiset that is identical but whose line
order moves** — class B10, and it is *probabilistic per run*, not deterministic: `motor_huge`
was byte-stable in the earlier `final` 3-rep set and unstable in `final2` with identical
stdout. Seven rows (`world_null_b:d`, `null_b_kind:pin_b`, `null_b_kind:pin_b_char`,
`null_b_phase:{one_frame,step40,nofree,vel0}`) are `rc=-6` crash rows whose stderr is a crash
backtrace with an ASLR load address — **never byte-stable, and therefore never `CASES`-able**
(a row's `expected_exit=0` cannot be met by an abort).

---

## 1. Class `B1 NULLB-ABORT` — `joint_make_pin` with a non-static `body_a` and a null `body_b` aborts the process on the first physics step **[M]**

Not in the brief; found while extending the prior seat's self-joint/nulls bisection, then
reduced to a phase table and a kind table. **No r81 cell is threatened by this class** (§12) —
but it is the family's one input shape with neither a refusal nor a safe behavior.

**Phase isolation** (one process per lane, `--lanes=`, all with `body_a = RigidBody2D`,
`body_b = RID()`):

| lane | what runs | rc | witness |
|---|---|---|---|
| `mk_only` | make, **no step**, teardown | **0** | `PASS … sel=mk_only type=0 pos=(200.00,0.00)` — make + teardown safe |
| `one_frame` | make + **1** step | **-6** | crash |
| `step40` | make + 40 steps | **-6** | crash |
| `nofree` | 40 steps, PASS printed, **no teardown** (`quit(0)`) | **-6** | crash ⇒ **the abort is in the step, not in teardown** |
| `vel0` | 40 steps, body velocity forced to zero | **-6** | crash ⇒ motion is not required |
| `static_a` | `body_a = StaticBody2D`, null `body_b`, 40 steps | **0** | `type=0` — **silently accepted** |

**Kind / body-type table** (40 steps each; `A` = null `body_a`, `B` = null `body_b`):

| lane | call | rc | refusal text | type |
|---|---|---|---|---|
| `pin_a` | `joint_make_pin(RID(), dyn_b)` | 0 | `Parameter "A" is null.` | 3 (unmade) |
| `pin_b` | `joint_make_pin(dyn_a, RID())` | **-6** | **none emitted** | — |
| `pin_b_frozen` | same, `body_a.freeze = true` | 0 | none | 0 (silent) |
| `pin_b_char` | `body_a = CharacterBody2D` | **-6** | none | — |
| `spring_b` | `joint_make_damped_spring(dyn_a, RID())` | 0 | `Parameter "B" is null.` | 3 |
| `groove_b` | `joint_make_groove(dyn_a, RID())` | 0 | `Parameter "B" is null.` | 3 |
| `spring_a` / `groove_a` | null `body_a` | 0 | `Parameter "A" is null.` | 3 |

Crash marker, verbatim (stderr, all seven crash rows, ×3 reps):
`ERROR: /root: The caller thread can't call the function \`propagate_notification()\` on this
node. Use \`call_deferred()\` or \`call_deferred_thread_group()\` instead.` at
`propagate_notification (scene/main/node.cpp:2578)`, then
`handle_crash: Program crashed with signal 11` with frames
`godot+0x1d35c40`, `+0x68a27b8`, `+0x68a2eac`, `+0x61d317d`, `+0x6b403339`
(offsets constant per build; only the load address varies). `rc=-6` is the engine's crash
handler aborting after the SIGSEGV.

**Class statement [M]:** the abort condition is **`joint_make_pin` ∧ `body_b` is the null RID ∧
`body_a` is a simulated body (RigidBody2D with `freeze=false`, or a CharacterBody2D)**. Static
and frozen `body_a` are accepted silently (`type=0`); every other joint kind and every other
null position refuses with a typed `Parameter "A"/"B" is null.` line and leaves the joint at
`JOINT_TYPE_MAX` (3). **The pin joint's null-`body_b` guard is missing where the other three
guards exist.** Cause is **[I]**: the stripped binary (no `.debug` file, no symbol package, no
Godot source tree on this host — checked) leaves the crash frames unresolved; the recorded
hypothesis is a null dereference of `body_b` in the pin solver's simulated-body path.

**Why this matters for the family:** a cell author who wants a "world anchor" pin
(`joint_make_pin(j, anchor, dyn_body, RID())`) — a natural shape, and the shape the engine
accepts for a static `body_a` — gets a process abort instead of an error line. The landed r81
fixture contains **zero** `RID()` literals (literal grep, §12), so no landed cell is exposed.

---

## 2. Class `B2 AREA-CB-GATE` — in-callback layer/mask writes are accepted and re-evaluated at the next step; `monitoring` alone is gated **[M]** (the brief's headline edge)

`area_mask_cb`, 9 lanes, one PASS line, ×3 byte-stable (stdout and stderr):
a body flies through an 80×400 `Area2D` (entry at f31, control exit at f53) or an area slides
through another (entry f24, control exit f57); the write is issued **inside** the entered
callback.

| lane | write (in-cb) | `in_cb` readback | `after_def` | `ext_f` | verdict |
|---|---|---|---|---|---|
| `ctl` | none | 1.0 | — | 53 | control |
| `direct_mask` | `zone.collision_mask = 0` | **0.0** | — | **32** | accepted; overlap drops next step |
| `deferred_mask` | `set_deferred`-style via `call_deferred` | 1.0 (not yet) | **0.0** | **32** | accepted; **same frame as direct** |
| `direct_layer` | `body.collision_layer = 0` (body side) | **0.0** | — | **32** | accepted; overlap drops |
| `direct_mon` | `zone.monitoring = false` | **1.0** | — | 53 | **REFUSED** — write never lands |
| `deferred_mon` | `set_deferred("monitoring", false)` | 1.0 | 1.0¹ | **32** | accepted; lands within one idle frame (`end_mon=0.0`) |
| `pair_ctl` | none (area↔area) | 1.0 | — | 57 | control |
| `pair_mask` | watcher `collision_mask = 0` | **0.0** | — | **25** | accepted; drops next step |
| `pair_layer` | target `collision_layer = 0` | 1.0 | **0.0** | **25** | accepted; drops next step |

¹ probe artifact: the readback is taken immediately after the nested deferral is *scheduled*;
`end_mon=0.0` proves the write landed.

Typed refusal, verbatim (stderr, ×3 reps):
`ERROR: Function blocked during in/out signal. Use set_deferred("monitoring", true/false).`

**Class statement [M]:** (a) the `Area2D` overlap gate **re-evaluates the pair every physics
step**, so a mask/layer write inside the callback — direct *or* deferred — takes effect at the
next step; the direct/deferred distinction is visible **only** in the in-callback readback
(`in_cb=0.0` vs `in_cb=1.0, after_def=0.0`), exactly the shape r81's `layer_flip_cb` pinned for
the contact surface; (b) the `monitoring` setter is the one **gated** in-callback write: it is
refused with a typed error and the readback proves it never landed (`in_cb=1.0`, `end_mon=1.0`,
exit at the control frame 53), while the deferred form works. **The r81 `layer_flip_cb` claim
("in-callback flips are accepted, not gated") therefore holds for `collision_mask`/
`collision_layer` and fails for `Area2D.monitoring`** — a wording boundary, not a byte
falsification (§12, cell 17).

**Cross-surface contrast [M]:** on the *contact* surface r81 measured that a mask flip alone
never drops the contact (a velocity write is also required, `layer_flip_mid`), while here the
area overlap drops on the very next step from the flip alone. The re-evaluation rule is
**surface-dependent**, so neither cell's rule may be lifted to the other surface.

---

## 3. Class `B3 MOTOR-UNBOUNDED` — `motor_target_velocity` is an unclamped solver input; ±INF saturates to a huge finite ω, NaN propagates **[M]** (brief item 7)

`motor_huge`, 10 lanes (anchor at the body's centre, static body 200 px away ⇒ pure spin),
**×3 stdout-byte-stable** (its stderr carries the B10 warning-order flake from the `m_nan`
lane). `av` = angular velocity at f40, `rb_mtv` = readback.

| lane | target | rot@f40 | av@f40 | NaN | note |
|---|---|---|---|---|---|
| `m_pos` | 3.0 | **1.7255** | 2.8276 | no | **byte-identical to r81-scout §1.1 row 9's server motor** (same 40-frame shape) — cross-check |
| `m_neg` | -3.0 | -1.7255 | -2.8276 | no | exact mirror |
| `m_1e3` | 1e3 | -2.8945 | 942.5439 | no | av ≈ 0.9425 × target |
| `m_1e6` | 1e6 | 2.0182 | 942543.8125 | no | av ≈ 0.9425 × target |
| `m_1e9` | 1e9 | 2.1746 | 942543680.0 | no | av ≈ 0.9425 × target |
| `m_inf` | INF | 0.6020 | **6.6252e32** | no | **finite, not NaN** |
| `m_neginf` | -INF | -0.6020 | -6.6252e32 | no | mirror |
| `m_nan` | NAN | nan | nan | **yes** | NaN propagates to rot/av |
| `n_1e9` | 1e9 (node tier) | 2.1746 | 942543680.0 | no | **byte-identical to `m_1e9`** |
| `n_inf` | INF (node tier) | 0.6020 | 6.6252e32 | no | **byte-identical to `m_inf`** |

**Class statement [M]:** the motor is a velocity target with **no upper clamp** — the measured
angular velocity tracks the target linearly (≈0.9425×) up to 1e9 rad/s, ±INF does not produce
NaN but a **huge finite** ω (6.6e32 rad/s), and NAN propagates into both `rot` and `av`.
r81's `joint_pin_params` pinned only ±3.0; the whole extreme is new. The node and server tiers
agree byte-for-byte on this path (also class B11).

---

## 4. Class `B4 LIMIT-VELOCITY-BRAKE` — the angular limit is a velocity-level correction (gain ≈ 104.6 s⁻¹), band-irrelevant while inside, energy-injecting outside, and branch-cut-crossing at ±π **[M]** (brief item 8)

`limit_pi`, 10 lanes (pure spin, anchor at the body's centre), ×3 byte-stable.

| lane | limit | ω₀ | rot @f40/80/150 | av@f150 | verdict |
|---|---|---|---|---|---|
| `no_limit` **[A]** | flag **off** | 3.0 | 1.4439 / 2.1811 / 2.7129 | 0.2411 | **free spin** (only the project's default angular damp) — the control that attributes the stop |
| `no_limit_av0` | off, ω₀=0 | 0 | 0 / 0 / 0 | 0 | rest |
| `pi_band` | ±π | 3.0 | **0.1694** ×3 | **0.0** | stopped inside the band, never reaches π |
| `pi_wide` | ±4 | 3.0 | **0.1694** ×3 | 0.0 | **byte-identical to ±π** |
| `two_pi` | ±2π | 3.0 | **0.1694** ×3 | 0.0 | **byte-identical again** |
| `pi_neg` | ±π | -3.0 | -0.1694 ×3 | 0.0 | mirror |
| `pi_start3` | ±π, **initial rotation 3.0** | 3.0 | **-3.1138** ×3 | 0.0 | **crossed +π and parked on the negative side of the cut** |
| `pi_exact` | lower=upper=π | 0 | -0.4945 / -1.2791 / -1.0803 | **328.6914** | unreachable band ⇒ **energy injected** |
| `pi_exact_spin` | lower=upper=π | 3.0 | -0.3251 / -1.1097 / -0.9109 | **328.6914** | same |
| `neg_band` | [-4,-3] | -3.0 | 3.0816 / 1.1758 / -0.5894 | **-313.8774** | current angle outside the band ⇒ energy injected |

**Class statement [M].** The limit is implemented as a **velocity-level** correction, not a
position clamp:
1. **Inside the band it kills free spin within ~3 frames** (3 rad/s → 0.1694 rad total travel,
   then `av=0.0` forever) — and the stop value is **byte-identical for ±0.5 (the landed
   `joint_pin_params` lane), (0,0) (this probe's `pin_angular` `locked` lane), ±π, ±4 and
   ±2π**, i.e. the band *width* is irrelevant while the current angle is inside. r81's "a brake, not a hard clamp" is confirmed **and its implicit
   attribution to the ±0.5 band is not witnessed** (§12, cell 9).
2. **Outside the band the correction is an injected velocity proportional to the violation**:
   `328.6914 / π = 104.62`, `313.8774 / 3 = 104.63` ⇒ gain ≈ **104.6 s⁻¹** — a π-sized
   violation injects 328 rad/s (unbounded, no clamp, no refusal).
3. **Crossing +π with the limit enabled snaps the body across the branch cut**: starting at
   +3.0 rad and spinning +3 rad/s, the body ends at **-3.1138 rad** (constant from f40) — it
   reverses through zero and parks just inside the *negative* edge rather than clamping at +π.
   The `no_limit` control shows the same lane would otherwise keep spinning (2.7129 at f150).

---

## 5. Class `B5 SOFTNESS-UNBOUNDED-SCALE` — pin `softness` is an unnormalized, unbounded scale: full pin at ≤1e-9, no constraint at ≥1e7 **[M]** (brief item 3)

`pin_soft_sweep` (14 lanes, ×3 byte-stable) + `soft_vs_free` (matched controls, ×3 byte-stable).
`dist` = distance from the anchor after 40 frames; the body is launched at 300 px/s from a
200 px offset (free flight ≈ 278.15 px, full pin ≈ 200.27 px).

| softness | dist | | softness | dist |
|---|---|---|---|---|
| 0 | 200.2710 | | 1e4 | 277.6529 |
| 1e-9 | 200.2708 | | 1e5 | 278.0676 |
| 1e-3 | 200.2714 | | 1e6 | 278.1406 |
| 1 | 200.8061 | | **1e7** | **278.1555** |
| 10 | 204.8865 | | **1e8** | **278.1555** |
| 100 | 251.6092 | | **1e9** | **278.1555** |
| 1000 | 274.7501 | | NAN | **nan** |

Matched-control lane (`soft_vs_free`, same shape, adjacent y):
`full_s0_y0=200.2710`, `soft1e9_y2k=278.1540`, `nojoint_y4k=278.1541`,
`soft1e9_y6k=278.1541`, `soft1e7_y8k=278.1534`, `nojoint_y10k=278.1562`
⇒ softness ≥ 1e7 is **within 1e-4…3e-3 of the no-joint control** (the y-gradient scale, class
B11) while the full pin is **78 px** away. `pin_soft_ext` adds the refusal surface: softness
`-1`, `+INF`, `-INF` → NaN trajectory, plus `ERROR: Condition "det == 0" is true.` at
`affine_invert (core/math/transform_2d.cpp:51)`.

**Class statement [M]:** the pin's constraint strength is a monotone but **unnormalized** scale
with a useful range of roughly 0…1e2; softness ≤1e-3 leaves the pin fully engaged
(200.2708…200.2714 vs 200.2710 at y=0 — inside the y-gradient), and ≥1e7 is
indistinguishable from *no joint at all*, while negative/±INF softness produces NaN. r81's
`joint_pin_params` pinned 0/1/4 (all inside the live range) — the no-op edge and the NaN edge
are new.

---

## 6. Classes `B6 SPRING-NONFINITE-RUNAWAY` and `B7 GROOVE-DEGENERATE-NAN` — degenerate scalars are accepted, never clamped **[M]** (brief items 1–2)

`spring_negative` (12 lanes) and `spring_nonfinite` (9 lanes), both ×3 stdout-stable:

| lane | rest / stiffness / damping | result |
|---|---|---|
| `ctl` | 50 / 20 / 0 | `d0=62.3784` |
| `nojoint` **[A]** | — | `d=126.4086` (free flight) |
| `auto` | *not written* (only `joint_make_damped_spring`) | `rb=[100.0000, 20.0000, 1.5000]`, `d=104.3490` ⇒ the maker **auto-sets rest = anchor distance** (100 here, 200 in r81's census) and stiffness 20 / damping 1.5 |
| `sneg` | 50 / **-20** / 0 | `d0=589.4596`, `vel=(2167.00,-750.77)` — the spring **pushes** |
| `snegd` | 50 / **-20** / 4 | `d0=119.9880` — damping tames it |
| `dneg` | 50 / 20 / **-4** | `pos=(14855176.00,-10676994.00)`, `vel=(3.6e8,-2.6e8)` — runaway |
| `rzero` / `rneg` | **0** / **-50** rest | `d0=95.9936` / `62.1159` — accepted |
| `shuge` | 50 / **1e6** / 0 | **NaN** |
| `stiff_inf` / `stiff_nan` | INF / NAN stiffness | **NaN** trajectory, readback `inf`/`nan` |
| `damp_inf` | INF damping | **finite**, `d=100.7400` ≈ undamped — accepted, no NaN |
| `damp_nan` | NAN damping | **NaN** |
| `rest_inf` / `rest_nan` | INF / NAN rest | **NaN** |
| `s256`/`s1024`/`s8192` | 256/1024/8192 | finite, non-monotone (`78.00`/`30.75`/`77.76`) |

Grooves (`groove_zero` 6 lanes + `groove_nonfinite` 6 lanes): server zero-length segment
(`groove1 == groove2`) → **NaN**; node `length = 0` → **NaN**; node `length = -50` → finite
(`27.90,64.99`, the segment runs reversed); reversed server segment → finite
(`-54.15,147.24`); `initial_offset = ±40` → finite (`50.00,50.00` / `37.66,-55.14`); a normal
100-length groove → finite (`-44.04,45.02`); **INF and NAN lengths (server *and* node) → NaN**.

**Class statement [M]:** the damped spring and the groove accept every non-finite and
negative scalar without a refusal; the failure mode is either NaN (stiffness/damping/rest
INF·NAN, groove length 0·INF·NAN) or an unbounded runaway (negative stiffness/damping,
millions of pixels in 40 frames) — never a typed error. The only degenerate value with a
*benign* outcome is negative damping *with* a finite spring (`snegd`) and `damp_inf`.

---

## 7. Class `B8 SELF-JOINT-INERT` — `body_a == body_b` is accepted, and the self-pin constrains nothing **[M]** (brief item 4)

| arm | call | witness |
|---|---|---|
| `self_pin_dyn` | pin, dyn body vs itself | `type=0 pos=(200.00,193.31) dist=278.1541` — **byte-identical to free flight** (the pin is inert) |
| `self_pin_static` | pin, static body vs itself | `type=0` (no error, no motion to observe) |
| `self_spring` | spring, dyn body vs itself | `type=2 rb=[100.0, 20.0] pos=(200.00,0.00)` — rest 100 = the maker's auto-rest; body unmoved |
| `self_groove` | groove, dyn body vs itself (+ a normal groove twin) | `types=1,1 pos=(-44.04,45.02)` — the body **does** move (the self-groove is live) |

**Class statement [M]:** a self-joint is accepted by every maker (`type` = 0/1/2, no error
line) and never refuses; the pin and spring degenerate to no-ops while the groove remains
live. Note this is a *distinct* class from B1: the self-pin passes the same null-guard path
with both bodies present.

---

## 8. Class `B9 RID-NO-RECYCLE / STALE-BODY-SILENT-INERT` — freed joint RIDs are not recycled within 64 allocations; a stale *body* RID is accepted silently and constrains nothing **[M]** (brief item 5)

`joint_realloc` (×3 byte-stable): `recycled=false id1=141733920768 id2=146028888064`
(`id2 = id1 + 2³²`) `reused_at=-1 n_ids=64` — **64 subsequent `joint_create()` calls never
return the freed id**. A `joint_make_pin` through the stale handle refuses
(`ERROR: Parameter "prev_joint" is null.`) and leaves the live joint untouched
(`t_after_stale_make=2`, `type_end_new=2`, `d_b2=0.0000`), while its intended target flies free
(`d_b3=247.7310` = the free-flight `146.1870` plus its 200 px start offset). **[A]** the
same-shaped free control (`d_ctl=146.1870`) is in the row.

`stale_reuse_ctl` (×3 byte-stable) — the prior seat's ambiguous `victim_drift=98.2684` is
resolved by controls: `reuse[type=0 drift=98.2682]` is **byte-identical to
free_ctl[drift=98.2682]** (a recycled victim is *not* constrained), while
`live_ctl[type=0 drift=0.0000]` shows what a live pin does. `joint_stale_body`'s
`stale_make[node_valid=false type=0 soft_rb=0.0000]` emits **no error line** at all.

**Class statement [M]:** (a) a freed joint RID is not reused in this window, so the r81
`joint_freed_rid` sentinels cannot be aliased by a later allocation — the cell is *robust*, not
merely true; (b) a freed **body** RID passed to `joint_make_pin` produces a joint that reports
`type=0` with **no refusal** and **no constraint** — a silent no-op, the opposite failure shape
from the joint-RID case, and the one a caller gets when it reuses a handle to a body that has
already been freed.

---

## 9. Class `B10 WARN-ANCHOR-INTERLEAVE` — the NaN lanes' warning text and its `at:` anchor are two writes whose order moves across reps (harness class) **[M]**

Measured on `final` and `final2` (identical stdout, byte-identical PASS line, ×3):
7 rows emit `WARNING: Vector2 cannot be normalized, the elements must be finite. Making (0, 0)
as a fallback.` followed by `at: normalize (core/math/vector2.cpp:55)` — 4 pairs
(`spring_negative`, `motor_huge`'s `m_nan` lane), 6 (`pin_soft_ext`), 16 (`groove_zero`), 21
(`joint_bias_env`), 24 (`spring_nonfinite`), 184 (`groove_nonfinite`). The **line multiset is
identical across reps** (same bytes, same lines) but the **interleaving of the message lines
with their anchors differs**, so a merged-stream byte comparison reports the row unstable.

**The instability is probabilistic, not deterministic** [M]: `motor_huge` was byte-stable in
`final`'s three reps and unstable in `final2`'s three reps with *identical stdout* — i.e. this
is a latent flake in any byte-criterion applied to these rows, not a fixed property of the row.
`pin_soft_ext` additionally emits `ERROR: Condition "det == 0" is true.` at
`affine_invert (core/math/transform_2d.cpp:51)` (once, stable position).

**Consequence [M]:** any cell in this family whose lane enters a NaN/runaway state cannot be
pinned by a merged-stream `stable_bytes` criterion, even though its numeric payload is
byte-stable. The battery's own `classify_process` is line-based and unaffected **provided** the
signature is on stdout and no `expected_errors` entry matches the warning text. This is also
why the r81 scout's "20/20 `stable_bytes=true`" is not contradicted here: none of its 20 lanes
reaches a NaN state.

---

## 10. Class `B11 TIER-AGREE-MOTOR` (cross-check) and the y-gradient **[M]/[I]**

- The node and server tiers are **byte-identical** on the motor path at both extremes
  (`n_1e9` ≡ `m_1e9`, `n_inf` ≡ `m_inf`).
- `m_pos` (server, 40 frames, anchor at the body's centre) = **1.7255** — byte-identical to the
  r81-scout §1.1 row 9 server motor; the landed `pin_angular` **node** motor reads **1.9611**
  on a 45-frame arm (5 + 40). **[I]** that difference is the 5 extra frames at the measured
  approach rate (2.8276 rad/s × 5/60 = 0.236 ≈ 1.9611 − 1.7255), i.e. a frame-count effect,
  not a tier effect.
- My own lanes show the same **last-digit float gradient in absolute y** the critic attributed
  to the r81 `joint_pin_tiers` split: the *identical pin geometry* reads `200.2710` at y=0 and
  `200.2708` at y=2000 — the very two y values that cell's node/server lanes sit at — while the
  *free-flight* distance drifts `278.1540` (y=2000) → `278.1541` (y=4000) → `278.1562`
  (y=10000). This **corroborates critic C1** and is the reason every "free flight" claim above
  is stated against an adjacent-y control.

---

## 11. Falsification list — what would kill each class, and the control that already moved

| class | falsified by | control already run |
|---|---|---|
| `B1 NULLB-ABORT` | a build/host where `pin_b` completes a step; or a crash in `static_a`/`pin_b_frozen` (then the class is not about the dynamic `body_a`) | `static_a`, `pin_b_frozen`, `mk_only` all rc=0; `one_frame`/`nofree`/`vel0` all rc=-6 |
| `B2 AREA-CB-GATE` | an in-cb mask write that leaves `ext_f` at the control frame (53/57); or a *direct* `monitoring` write that lands | `ctl` (53), `pair_ctl` (57), `direct_mon` (refused, 53) |
| `B3 MOTOR-UNBOUNDED` | a target ≥1e3 whose `av` saturates or NaNs; or a clamped ±INF | `m_1e3/1e6/1e9` linear (0.9425×), `m_inf` finite 6.6e32, `m_nan` NaN |
| `B4 LIMIT-VELOCITY-BRAKE` | a band whose stop value differs from 0.1694 (±π stopping at π); or a crossing lane clamping at +π | `no_limit` (free spin), `pi_wide`/`two_pi` (0.1694, byte-identical) |
| `B5 SOFTNESS-UNBOUNDED-SCALE` | a softness ≥1e7 lane that stays pinned (≈200) | matched no-joint controls at adjacent y (278.1541/278.1562 vs 278.1555) |
| `B6 SPRING-NONFINITE-RUNAWAY` | a negative-stiffness or INF-stiffness lane that stays bounded | `ctl`/`nojoint`/`auto` controls in the same row |
| `B7 GROOVE-DEGENERATE-NAN` | a zero/INF/NAN-length groove that stays finite | `srv100` (finite) in the same row; `gz_rev`/`gz_nodeneg` finite |
| `B8 SELF-JOINT-INERT` | a self-pin that arrests the body (dist < free flight) | `self_pin_dyn dist=278.1541` = free flight; `self_groove` moves (the maker is live) |
| `B9 RID-NO-RECYCLE` | an id equal to `id1` among the 64 later allocations, on any build | `reused_at=-1`; free-flight control for the target body |
| `B9 STALE-BODY-SILENT-INERT` | a stale-body joint whose victim drift ≠ the free control | `reuse 98.2682` ≡ `free_ctl 98.2682`, `live_ctl 0.0000` |
| `B10 WARN-ANCHOR-INTERLEAVE` | byte-identical stderr across reps for a NaN lane **in every run** (the class is probabilistic — one stable run does not falsify it, one unstable run does not prove it permanent) | 7 rows × 3 reps in `final2`, plus `motor_huge` stable-in-`final`/unstable-in-`final2` with identical stdout |
| `B11 TIER-AGREE-MOTOR` | a same-y same-frame node/server pair whose bytes differ | `m_1e9 ≡ n_1e9`, `m_inf ≡ n_inf` |

**What would falsify this report as a whole:** a different Godot build (4.7.x ≠ 4.7.2) or a
different `physics/2d` backend (Jolt-2D) — every number here is GodotPhysics2D on
`4.7.2.stable.arch_linux.ed1daf0bf`, 60 tps, `run_on_separate_thread=false`; and a host whose
RID allocator recycles differently (B9 is explicitly window-bounded to 64 allocations).

---

## 12. Cells threatened — the 20 landed `phys2d_joints_*` rows

| # | cell | status | why |
|---|---|---|---|
| 1 | `joint_census` | **safe** | only more of the same surface is read; no contradiction |
| 2 | `joint_unset_refusal` | **safe / extended** | the null-body refusals (`Parameter "A"/"B" is null.`) belong to the same refusal surface; the cell's own rows unchanged |
| 3 | `joint_pin_tiers` | **threatened (pre-existing C1, corroborated)** | the node/server last-digit split tracks absolute y (my B11 gradient is an independent instance); the same-y server lane has not been measured by anyone yet |
| 4 | `joint_pin_clear` | **safe** | — |
| 5 | `joint_node_clear` | **safe** | C4's unwitnessed-nudge finding stands, unchanged by this seat |
| 6 | `joint_freed_rid` | **strengthened** | B9: no recycling within 64 allocations ⇒ the sentinels cannot be aliased; C6's freed-vs-never-valid reword still stands |
| 7 | `joint_node_freed_rid` | **safe** | — |
| 8 | `joint_spring_env` | **safe / extended** | negative, zero-rest and non-finite scalars are outside its envelope; the `auto` defaults match its census |
| 9 | `joint_pin_params` | **threatened (attribution only)** | the softness ladder is fine, but the cell's angular-limit lane attributes the 0.1694 stop to the ±0.5 band; B4 shows the same stop for ±π/±4/±2π, and the boundary probe's `locked` lane shows it for the degenerate (0,0) band ⇒ the band is not the cause. Bytes unchanged; the *claim* over-specifies |
| 10 | `joint_node_anchor` | **safe** | C2 stands |
| 11 | `joint_groove` | **safe / extended** | B7 adds the INF/NAN and zero-length NaN class; the chaotic-lane bytes are untouched |
| 12 | `joint_disable_coll` | **safe** | — |
| 13–15 | `layer_or_table`, `layer_zero_table`, `layer_dyn_pair` | **safe** | untouched surfaces |
| 16 | `layer_flip_mid` | **safe** | C7 stands; B2 is a *different* surface (area overlap, not contact) and is not lifted onto it |
| 17 | `layer_flip_cb` | **threatened (wording only)** | "in-callback flips are accepted, not gated" is true for `collision_mask`/`collision_layer` and **false for `Area2D.monitoring`** (B2: typed refusal, write never lands). The cell's own bytes are untouched; the claim needs the qualifier, and its "neither releases the contact" must not be lifted to the area surface (where the flip *does* release at the next step) |
| 18 | `area_lattice` | **safe / extended** | B2's pair lanes reproduce the per-side gate; frame-exact entry/exit witnesses are offered as a candidate pin for C8's timing gap |
| 19 | `area_body_gate` | **safe** | — |
| 20 | `area_entry_order` | **safe** | untouched |

**No cell is falsified by any measurement in this report.** Three cells carry claim-level
threats (3 via the pre-existing critic C1; 9 and 17 by attribution/wording), four are extended
(2, 8, 11, 18) and one is strengthened (6). The B1 abort threatens **no landed cell**: a literal
`grep -c "RID()"` over `corpus/fixtures/phys2d_joints.gd` returns **0** — literal search, not
semantic proof, but sufficient to show no landed lane constructs a null body.

**Landing note for a future author:** the value-edge classes (B4, B5, B6, B7, B8, B9) are all
expressible as `expected_exit=0` cells — their lanes complete; only the *values* are extreme —
but **B10 means the NaN-bearing ones cannot be pinned with a merged-stream byte criterion**
(their stdout signatures are stable, so a `CASES` row carrying a stdout signature is fine,
while a `stable_bytes`-style ablation over the same row is not). Class B1's **non-crash** lanes
(`pin_a`, `pin_b_frozen`, `spring_b`, `groove_b`, `spring_a`, `groove_a`, `static_a`) are
cell-able as typed-refusal cells (the first six carry `Parameter "A"/"B" is null.`); its four
**crash** lanes (`pin_b`, `pin_b_char`, and the phase lanes) are **never** `CASES`-able — an
abort cannot satisfy `expected_exit=0`.

---

## 13. Remaining unknowns

1. **B1's crash mechanism.** The binary is stripped, no `.debug`/symbol package and no Godot
   source tree exists on this host (checked); the five backtrace offsets are recorded
   (`+0x1d35c40, +0x68a27b8, +0x68a2eac, +0x61d317d, +0x6b403339`) but unresolved. Whether the
   same abort occurs with a *second* joint on the same pair, inside a callback, or on a
   non-Linux platform is unmeasured.
2. **B4's gain law.** 104.6 s⁻¹ is measured from two lanes (π and 3.0 violations); whether the
   gain is exactly `k/dt` or `k·bias` and whether it is tunable via `bias`/`max_bias` on the
   pin joint is not measured (the limit path may not read those params).
3. **B4 wrap semantics beyond one crossing.** One +π crossing was measured (parking at
   -3.1138). Multi-turn crossings (e.g. 2 full turns before the check) and the exact wrap
   predicate (`atan2` difference vs accumulated rotation) are unresolved.
4. **B9's allocator window.** "No recycling in 64 allocations" is a bounded claim; the
   long-horizon behavior (thousands of joints, other object types interleaved) is unmeasured.
5. **B5's threshold law.** The curve is monotone with a live range ≈0…1e2 and a dead range
   ≥1e7, but the exact functional form (1/(softness+Σinv_mass)?) and its mass dependence
   (a light body vs a heavy one) are unmeasured.
6. **B10's cause.** The message/anchor split is measured as an output-ordering fact; whether
   the two lines come from different sinks or a buffered writer is not established.
7. **Cross-backend.** Every class above is GodotPhysics2D-only; no Jolt-2D backend exists in
   this build, so no cross-backend claim is made.

---

## 14. Receipts (`corpus/live/r81-boundary/`)

| artifact | path |
|---|---|
| probe (current revision) | `proj/phys2d_jb.gd` — sha256 `6785cd3e8e15e85c756978924ccf23525339d672ae69c0ae6b3709d220261430`, 1522 lines, 30 `match` arms (42 runnable rows once the `null_b_phase` ×6 and `null_b_kind` ×8 lane sets are counted) |
| runner | `run_arms.py` — sha256 `186cec5d71e32dc7cb00736f00a677897431fc4fc723c96067da65984a916b7d`; its default `ARMS` list is the canonical 42-row set, so `run_arms.py --reps 3 --tag final2` reproduces the receipt below |
| **canonical 42-arm × 3-rep receipt** | `arms-final2.json` (+ `cells/final2.<arm>.rep<N>.{stdout,stderr}.txt`, 252 files) |
| superseded 41-arm × 3-rep receipt (same probe minus `soft_vs_free`) | `arms-final.json` |
| matched softness controls | `arms-softfree.json` (+ `cells/softfree.*`) |
| stream-stability analysis + tables | `stability.py` (tag argument), `stability-final2.txt` (canonical), `stability-final.txt` (earlier set) |
| consolidated human-readable summary | `final-summary.txt` |
| crash phase/kind isolation receipts | `arms-s2phase.json`, `arms-s2kind.json`, `arms-s2kind2.json` (+ `cells/s2*`) |
| probe-construction iterations | `arms-s2smoke{,2,3}.json` (+ `cells/s2smoke*`) |
| inherited prior-seat receipts (superseded where re-measured) | `arms-{smoke,iso,fix,fix2,fix3,bisect,combo,wnull,r81b}.json` |

**Provenance of every quoted number:** `final2` (42 rows × 3 reps, 126 fresh Godot processes,
probe sha `6785cd3e…`), plus `softfree`/`s2phase`/`s2kind*` for the arms added after the first
consolidation. Nothing in this report is quoted from the prior seat's tags without being
re-measured in `final2`; where the prior seat's numbers are cited (`joint_stale_body`,
`victim_drift=98.2684`) they are quoted **as re-measured in `final2`** and the ambiguity is
resolved by this seat's controls.
