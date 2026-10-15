# game-dev-2d round 94 — scout (r94-scout): the CPUParticles2D + GPUParticles2D emission lattice, pre-measured; 19 rows verbatim-ready

Seat `SCOUT` (LEAF; frozen `probeParent` — one labrat dispatch, inconclusive, §9) | lane
`r94-scout` | round 94 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
default 60 physics ticks/s, `RendererDummy` (headless has no rendering server).
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at session start **`520ed6d`**
(*r90 boundary*); the only tracked modification in `git status` is the concurrent lane's
`corpus/fixtures/run_battery.py` edit (read-only for this seat — it was already `M` before
the session and is untouched by me).

**No git mutation, no tracked file written, no commit.** Writes are this report and
`corpus/live/r94-scout/**` only. The launch `project.godot` is the byte-copy of
`corpus/fixtures/project.godot` (`8de8b3af…`).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on
this host; `definition`/`references`/`hover` were **unavailable for every file**. All
symbol/API knowledge below comes from runtime `ClassDB` introspection inside the probes
(`census`/`sig` arms) and from the engine's own error text — never from engine source.
One mechanism note in §5 item 12 cites the upstream `master` `cpu_particles_2d.cpp` fetched
over the network as **[I]** (this build's source is not on the host and the master revision
does not match this build exactly — behaviour, not source, is the evidence).

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Primary: the 2D particle-emission lattice** — `CPUParticles2D` (emission timing,
lifetime/one-shot/explosiveness/preprocess/speed_scale/fixed_fps, restart and re-trigger
semantics, `emitting=false` timing, pause levers, mid-flight parameter changes,
`request_particles_process`), `GPUParticles2D` (headless behaviour, `emit_particle`,
`capture_rect`, `amount_ratio`, `sub_emitter`, trails, collision) and
`ParticleProcessMaterial` (parameter/flag/sub-emitter/collision API + defaults), plus the
GPU↔CPU `convert_from_particles` bridge. This is the brief's surface verbatim.

Why it earns the round: `grep -rin "particle" corpus/knowledge corpus/lessons` finds
**zero** prior particle knowledge and the battery CASES list has **no particle row** (the
only particle mentions anywhere in `corpus/fixtures` are none) — the family is an
uncovered blind spot, and the first probe immediately refuted the naive author model
(§7 F1/F4/F9): `finished` is not a frame counter, `emitting=false` does not
stop particles, and `GPUParticles2D` is completely inert headless. Every law below is
reachable from GDScript with `--headless` (no rendering server needed), so the whole
lattice is battery-authorable.

Adjacents weighed: TileMapLayer/r92, AnimationPlayer+Tween/r93 and
PhysicsDirectSpaceState2D/r95 are already dispatched to sibling scout seats this wave —
no overlap was taken.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (14 arms) | API census, one-shot timing ladder, stop/hide/detach/restart/gpu | `runs/disc-*` |
| 2 | `probes/discover2..7.gd` (40 arms) | fine traces: same-frame restart, request isolation, GPU flip, contamination, setters | `runs/disc2-*` … `runs/disc7-*` |
| 3 | `bash run_cells.sh` | **19 cells** (3 pure ×3, 16 timing ×6) = **105 runs** | `runs/r94_particles_*.{out,err,rc}` |
| 4 | `python3 analyze_r94.py` | per-cell reps / out_uniq / err_uniq / rc / common prefix | `runs/analyze_r94.json`, `runs/analyze_r94.txt` |
| 5 | `HOGS=8 REPS=2 bash run_loadtest.sh` | **38 runs** under deliberate load | `runs/loadtest/` |
| 6 | `python3 make_author_rows.py` → `verify_rows.py` | 19 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |

**213 receipted launches** (105 canonical + 38 loadtest + 54 discovery + 16 smoke) plus
~15 unrecorded one-off scratch launches. Every run `timeout -s KILL`-bounded (30 s; none
hit). **All rc=0, and every one of the 143 canonical+loadtest receipts has 0 B stderr** —
no ERROR, no WARNING, no `SCRIPT ERROR`, no leak message anywhere in the primary probe
(`err_uniq=1`, `err_bytes=[0]` for all 19 cells).

**Byte-stability:** 12 of 19 cells are single-valued across 6 canonical reps; the other 7
differ only in a ±1-tick measured tail, and every one of the 7 keeps a byte-stable
boolean prefix before the `" | "` separator. The loadtest (loadavg **110.2/93.2/61.6**,
8 own + ~80 host `yes` hogs from concurrent lanes) reproduced all 19 gating prefixes —
`ROWS_PREFIX` rejected **0 of 143** receipts.

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| Class/enum/default census (CPU, GPU, PPM) | **PINNABLE** (one 8.6 KB (8785 B) line) | 3 | uniq=1 |
| PPM param/flag/sub-emitter/collision API | **PINNABLE** | 3 | uniq=1 |
| `convert_from_particles` GPU↔CPU | **PINNABLE** (full transfer, both directions) | 3 | uniq=1 |
| One-shot timing ladder (lifetime, explosiveness, speed_scale, preprocess, fixed_fps) | **PINNABLE law; exact tick is a ±1 mode** | 6 × 3 cells | prefix stable |
| `emitting=false` / `one_shot=false` timing | **PINNABLE law** | 6 × 2 cells | uniq=1 |
| Pause levers (own/inherited visibility, tree, process_mode, time_scale) | **PINNABLE law** | 6 | prefix stable |
| restart / re-trigger semantics | **PINNABLE law** | 6 × 2 cells | prefix stable |
| Mid-flight `lifetime`/`speed_scale` | **PINNABLE law** | 6 × 2 cells | uniq=1 |
| Mid-flight `amount` | **PINNABLE hazard** (spurious `finished`) | 6 | uniq=1 |
| `request_particles_process` clock-free lattice | **PINNABLE exact** (integer call index) | 6 | uniq=1 |
| `GPUParticles2D` headless | **PINNABLE inertness** (no `finished`, no readback) | 6 | prefix stable |
| Particle positions/colors/velocities | **NOT OBSERVABLE** headless (no per-particle readback API) | — | — |
| GPU collision / sub-emitters / trails / turbulence | **NOT MEASURABLE** headless (readback only) | — | — |

---

## 3. Measured values, verbatim

All lines are the canonical `runs/r94_particles_*.rep1.out` unless noted; the full set of
unique lines per cell is `runs/canonical-lines.txt`.

### 3.1 Census (`census`) — [M], 3/3 identical

`PASS particles_lattice census cpu_consts=…` (the full 8.6 KB (8785 B) line is the row; quoted
here only in the parts that matter):

- **Enums (CPU):** `DRAW_ORDER_INDEX=0,DRAW_ORDER_LIFETIME=1`; `PARAM_*` 0..11,
  `PARAM_MAX=12`; `PARTICLE_FLAG_ALIGN_Y_TO_VELOCITY=0,ROTATE_Y=1,DISABLE_Z=2,MAX=3`;
  `EMISSION_SHAPE_POINT=0,SPHERE=1,SPHERE_SURFACE=2,RECTANGLE=3,POINTS=4,DIRECTED_POINTS=5,RING=6,MAX=7`.
- **Enums (GPU):** `DRAW_ORDER_INDEX=0,LIFETIME=1,REVERSE_LIFETIME=2`;
  `EMIT_FLAG_POSITION=1,ROTATION_SCALE=2,VELOCITY=4,COLOR=8,CUSTOM=16`.
- **Enums (PPM):** `PARAM_*` 0..11 plus `PARAM_RADIAL_VELOCITY=15,DIRECTIONAL_VELOCITY=16,SCALE_OVER_VELOCITY=17,PARAM_MAX=18`,
  `PARAM_TURB_INFLUENCE_OVER_LIFE=12,TURB_VEL_INFLUENCE=13,TURB_INIT_DISPLACEMENT=14`;
  `PARTICLE_FLAG_DAMPING_AS_FRICTION=3,INHERIT_EMITTER_SCALE=4`;
  `SUB_EMITTER_DISABLED=0,CONSTANT=1,AT_END=2,AT_COLLISION=3,AT_START=4,MAX=5`;
  `COLLISION_DISABLED=0,RIGID=1,HIDE_ON_CONTACT=2,MAX=3`; `EMISSION_SHAPE_BOX=3`.
- **CPU defaults:** `amount=8 lifetime=1.0 one_shot=false preprocess=0 speed_scale=1 explosiveness=0 randomness=0
  use_fixed_seed=false lifetime_randomness=0 fixed_fps=0 fract_delta=true local_coords=false draw_order=0
  emission_shape=0 emission_sphere_radius=1.0 emission_rect_extents=(1,1) emission_ring_radius=1.0
  emission_ring_inner_radius=0.8 direction=(1,0) spread=45 gravity=(0,980) initial_velocity 0..0
  angular 0..0 damping 0..0 angle 0..0 scale_amount 1..1 color 1/1/1/1 hue 0..0 anim 0..0`.
- **GPU defaults:** `amount=8 amount_ratio=1.0 sub_emitter="" lifetime=1.0 interp_to_end=0 one_shot=false
  preprocess=0 speed_scale=1 explosiveness=0 randomness=0 use_fixed_seed=false fixed_fps=30 (!) interpolate=true
  fract_delta=true collision_base_size=1.0 visibility_rect=[P: (-100,-100), S: (200,200)] local_coords=false
  draw_order=1 trail_enabled=false trail_lifetime=0.3 trail_sections=8 trail_section_subdivisions=4 process_material=null`.
- **PPM defaults:** `emission_point_count=1 emission_box_extents=(1,1,1) direction=(1,0,0) spread=45 flatness=0
  gravity=(0,-9.8,0) directional_velocity=(1,1) min=max=1 scale 1..1 color white turbulence_enabled=false
  turbulence_noise_strength=1 turbulence_noise_scale=9 turbulence_noise_speed=(0,0,0) turbulence_noise_speed_random=0.2
  attractor_interaction_enabled=true use_rotation_3d=false`.
- **`ppm_curve_types`** — every `*_curve` property is **`Texture2D` (type 24), not `Curve`**
  (`damping:24,alpha:24,emission:24,scale:24,angle:24,…`).
- **Signatures:** `CPUParticles2D.restart(keep_seed:1)->0`,
  `CPUParticles2D.request_particles_process(process_time:3,process_time_residual:3)->0`,
  `CPUParticles2D.is_emitting()->1`, `CPUParticles2D.convert_from_particles(particles:24)->0`;
  `GPUParticles2D.emit_particle(xform:11,velocity:5,color:20,custom:20,flags:2)->0`,
  `GPUParticles2D.capture_rect()->7` (Rect2), `restart`/`request`/`is_emitting`/`convert` as CPU.
- **`seed` is excluded from the row**: its ClassDB default is 0 but the instance value is
  **randomized per instantiation** (`cpu=[3554215384,610307821]`, `gpu=[1597799548,1328438430]`
  in one process; different again in the next) — a non-pinnable default **[M]**.

### 3.2 PPM API (`ppm`) — [M], 3/3 identical

```
PASS particles_lattice ppm iv_min=7.0000 iv_max=9.0000 scale=(2.0000,3.0000) tex_same=true curve_same=true flags=truetrue sub_mode=3 sub_amt=3 coll=2 turb=true turb_n=1
```
`set_param/set_param_min/set_param_max/set_param_texture` + the property aliases round-trip
identically (texture identity and `damping_curve` identity preserved); `set_particle_flag`
and the `sub_emitter_*`/`collision_mode` enums read back as set.

### 3.3 GPU→CPU convert (`convert`) — [M], 3/3 identical

```
PASS particles_lattice convert g2c[amount=12 lifetime=0.7000 os=true expl=0.2500 rand=0.5000 ss=2.0000 ffps=0 pre=0.1250 local=true draw=2] g2c_dir=(0.5000,0.5000) spread=30.0000 grav=(0.0000,98.0000) iv=10.0000..20.0000 scale=2.0000..3.0000 g2c_col=0.250/0.500/0.750/0.500 shape=1 sph=5.0000 c2g[amount=5 lifetime=0.4000 os=false expl=0.5000 pm_null=false dir=(0.0000,-1.0000,0.0000) spread=10.0000 grav=(0.0000,30.0000,0.0000) iv=3.0000..4.0000 col=0.100/0.200/0.300/0.400]
```
Both directions transfer the full timing + parameter set. **Hazard:** a GPU
`draw_order=2` (REVERSE_LIFETIME) converts to CPU `draw_order=2`, which is outside the
CPU enum (0/1) — the CPU node accepts the out-of-range value silently **[M]**.

### 3.4 Timing ladders (canonical uniques, `runs/canonical-lines.txt`)

```
cpu_lifetime ok=true l01_ok=true l025_ok=true l05_ok=true l1_ok=true | l01[delta=6|7|8] l025[delta=14|15] l05[delta=29|30] l1[delta=59|60]
cpu_expl     ok=true e1_ok=true e05_ok=true e0_ok=true          | e1[delta=29|30] e05[delta=42|43] e0[delta=56|57]
cpu_speed_pre ok=true ss2_ok=true ss05_ok=true pre25_ok=true ff30_ok=true | ss2[delta=15] ss05[delta=59|60] pre25[delta=14|15] ff30[delta=31]
cpu_stop     ok=true stop10_ok=true stop40_ok=true | stop10[fin_after=20] stop40[fin_after=19|20]
cpu_pause    ok=true vis_ok=true vis_parent_ok=true pm_disabled_ok=true ts0_ok=true | vis[5] vis_parent[4|5] pm_disabled[4|5] ts0[19|20]
cpu_restart  ok=true first_ok=true second_ok=true first_em=false first_ise=false em_after_restart=true ise_after_restart=true em_after=false | first_delta=15 second_after=14|15 n_fin=2
```
Cross-check with wall clock (discovery receipts, `runs/disc-cpu_*`): `l05` finished at
`fin_ms=497`, `l1` at `994`, `l025` at `241`, `l01` at `90`; `ss2` at `249`; `ss05` at
`987`; `pre25` at `256` — the tick count is the physics clock, the ms is the simulated
time, and both scale with `lifetime` **[M]**.

### 3.5 Stable single-value cells

```
cpu_never         ok=true never_fired=true n_fin=0 | fin_delta=-1 em_after=false ph_total=60
cpu_contam        ok=true n_never=2 | never1[fin_delta=0 n=1] never2[fin_delta=0 n=1]
cpu_oneshot_off   ok=true fin_ok=true em_after=false os_after=true | fin_after_off=50 n_fin=1 em_fin=false
cpu_oneshot_flag  ok=true never_fired=true em_after=true os_after=false | fin_after_flag=-1 n_fin=0
cpu_retrigger     ok=true first_ok=true second_ok=true em_set=true ise_set=true | first_delta=15 second_after=14 n_fin=2 em_after=false
cpu_lt_mid        ok=true fin_ok=true em_after=false | fin_after_set=2 n_fin=1 em_fin=false
cpu_speed_mid     ok=true fin_ok=true em_after=false | fin_after_set=12 n_fin=1
cpu_amount_mid    ok=true em_at_set=true spurious_finish=true | fin_after_set=0 n_fin=1 em_fin=true ise_fin=true em_at_end=false
cpu_request       ok=true step010_ok=true step005_ok=true | step0.10[fin_call1=6 fin_call_raw=4 expected=6 ok=true n_fin=1] step0.05[fin_call1=11 fin_call_raw=9 expected=11 ok=true n_fin=1]
gpu_headless      ok=true os_ok=true cont_ok=true manual_ok=true capture_ok=true | os[fin_delta=-1 n=0 flip_after=3|4|5|7 em_after=false ise_after=false] cont[fin_delta=-1 n=0 flip_after=-1 em_after=true ise_after=true] manual[fin_delta=-1 n=0 em_after=false] capture[rect=(0.0000,0.0000,0.0000,0.0000) em_after=false]
```

---

## 4. Laws (each pinned by ≥3 canonical reps + loadtest)

1. **One-shot, `explosiveness=1`: `finished` fires when the cycle clock reaches `lifetime`**
   — `L=0.1/0.25/0.5/1.0` → `6/15/30/60` physics ticks (±1), i.e. `round(L*60)` ticks and
   `≈L*1000` ms. It is **not** a fixed frame count and it is not `L+1` frames.
2. **Streamed emission (`explosiveness=e`) finishes at `L + L*(1-e)*(amount-1)/amount`** —
   `e=0` → `56` ticks (model `56.25`), `e=0.5` → `42–43` (model `43.125`), `e=1` → `30`.
   The `(amount-1)/amount` term is the last particle's emission slot
   (`restart_phase = i/amount`).
3. **`speed_scale` divides the particle clock**: `ss=2` → `15` ticks, `ss=0.5` → `59–60`
   (L=0.5). **`preprocess=0.25` (e=1) removes 0.25 s** → `14–15` ticks. **`fixed_fps=30`**
   quantizes the internal step but does not move the end time (`31` ticks; `fract_delta`
   false identical in discovery).
4. **`emitting=false` never kills live particles.** A continuous emitter stopped at tick
   10 finishes at tick 30 (the last batch's lifetime); stopped at 40 it finishes at
   59–60; a one-shot with `emitting=false` at tick 10 (L=1.0) still finishes at its
   natural tick 60 (`fin_after_off=50`). `finished` never fires while `one_shot=false`
   (mid-cycle flag flip → nothing in 70 ticks; continuous while emitting → never).
5. **`finished` requires an emission to have happened**: an emitter that was
   `emitting=false` from tick 0 never fires it (60 ticks, `n_fin=0`) — *provided it is the
   first emitter of the process* (see law 12).
6. **The particle clock is frozen by every pause lever** — own `visible=false`, inherited
   visibility (hidden parent), `process_mode=PROCESS_MODE_DISABLED`, removal from the
   tree, and `Engine.time_scale=0`. On resume the emitter continues with the *remaining*
   lifetime: hidden at 10 / shown at 40 with `L=0.25` finishes at 45 (`+5`), the same for
   the parent case, process_mode and time_scale (L=0.5, 10 ticks elapsed → `+19/20`).
7. **`restart()` starts a fresh cycle**: after the first finish (tick 15) `restart()` sets
   `emitting=true`/`is_emitting()=true` and the second finish lands `+14/15` ticks later;
   `n_fin=2`. After a one-shot finish, `emitting` reads `false` and `one_shot` stays
   `true`; a later `emitting=true` re-runs the cycle (second finish `+14`).
8. **`lifetime` is read live**: one-shot `L=1.0`, set to `0.2` at tick 10 → finish at
   `+2` (the cycle ends at the first tick where elapsed ≥ new lifetime).
9. **`speed_scale` is read live**: `L=1.0`, set to `4` at tick 10 (0.166 s elapsed) →
   finish `+12` (`0.166 + 0.833/4 ≈ 0.375 s`).
10. **`request_particles_process(step)` with `Engine.time_scale=0` is a clock-free
    deterministic lattice**: `step=0.1` → `finished` during call **6**; `step=0.05` →
    call **11** — i.e. `round(lifetime/step)+1` (the extra call is the
    deactivate-before-advance check). 6/6 reps + 2 load reps identical. The second
    argument (`process_time_residual`) changes the arithmetic (4 measured variants in
    `runs/disc4-request_args`), and the streamed path (`e=0`) **never** finishes under
    request-only time (300 calls, `runs/disc4-request_e0`).
11. **`GPUParticles2D` is headless-inert**: `finished` never fires (one-shot, continuous,
    manual `emit_particle`, 40 ticks each); a one-shot clears `emitting`/`is_emitting()`
    within `3–7` ticks of entering the tree; a continuous emitter keeps both `true`;
    `capture_rect()` returns `Rect2(0,0,0,0)`; `request_particles_process` is a no-op.
    `GPUParticles3D` behaves identically (control, `runs/disc2-gpu_trace`). CPU particle
    timing is dimension-agnostic: `CPUParticles3D` L=0.25 finishes at tick 15 too.
12. **CPUParticles2D has process-global contamination** [M][A]: once *any* emitter has run
    in the process (even 5 ticks, even if it is still in the tree or was freed), a
    never-emitting emitter fires `finished` on its **first update** (`fin_delta=0`), and
    so does the next one (`cpu_contam`: `never1` and `never2` both `fin_delta=0 n=1`).
    The first emitter of a process is clean (`cpu_never`). Probe design must therefore
    isolate never-emitting cells in their own process — the primary probe does.
13. **Mid-cycle `amount` emits a spurious `finished`** [M][A]: setting `amount` (up, down,
    or to the same value) on a one-shot emits `finished` on the set tick with
    `emitting`/`is_emitting()` still `true` (`fin_after_set=0 n_fin=1 em_fin=true
    ise_fin=true`), and the genuine end-of-cycle `finished` is suppressed (`em_at_end=false`;
    emitting clears silently at the natural end — `runs/disc6-amount_long`). Not before
    emission starts, not for continuous emitters, and not for `randomness`/`draw_order`/
    `scale_amount` setters (controls, `runs/disc5-*`, `runs/disc6-amount_pre_start`).
14. **`convert_from_particles` is a lossless timing+param bridge in both directions**
    (law/pin in §3.3), including the GPU→CPU `draw_order` out-of-range leak.
15. **`ParticleProcessMaterial` curve levers are `Texture2D`-typed in this build** — a
    `Curve` resource cannot be assigned (`Parse Error: Value of type "Curve" cannot be
    assigned to a variable of type "Texture2D"`, discovery) and all `*_curve` properties
    report type 24. `set_param_curve`/`get_param_curve` do not exist; only
    `set_param*`/`set_param_texture`.
16. **`seed` default is random per instantiation** (ClassDB default 0) — exclude it from
    any pin; `use_fixed_seed=false` by default. Defaults worth noting: CPU `fixed_fps=0`
    vs **GPU `fixed_fps=30`**, GPU `draw_order=LIFETIME(1)` vs CPU `INDEX(0)`, CPU
    `gravity=(0,980)` (2D down) vs PPM `gravity=(0,-9.8,0)` (3D), PPM
    `directional_velocity=(1,1)` min=max=1, CPU `emission_ring_inner_radius=0.8` (PPM
    `0.0`).

---

## 5. Hazards for the author and the boundary seat

1. **`GPUParticles2D` is a headless no-op** — never author a row that expects a GPU
   particle signal, count, rect or readback in `--headless`; the only pinnable GPU facts
   are inertness and resource/param readback.
2. **`finished` is a mode, not an integer** (±1 tick). Pin the boolean block, or pin the
   tick count only in a quiet window (the `ROWS`/`ROWS_PREFIX` split in §6).
3. **`amount` setter ⇒ spurious `finished`** (law 13) — any emitter whose `amount` is
   driven by gameplay will fire `finished` spuriously; do not treat `finished` as
   "cycle completed" when `amount` is animated.
4. **Process-global contamination** (law 12) — never-emitting emitters are only clean as
   the *first* emitter of a process; multi-emitter probes must keep them isolated. The
   first draft of this probe hit it (a `stop0` sub-case after two live emitters fired
   immediately; the frozen probe isolates it as `cpu_never` and pins the positive control
   as `cpu_contam` — `runs/r94_particles_cpu_contam.rep{1..6}.out`).
5. **Pause levers are not a `finished` substitute** — visibility/process_mode/time_scale
   freeze the clock silently; an emitter hidden at the wrong time never finishes.
6. **`restart()` vs `emitting=true`**: `restart()` is safe on a finished emitter;
   `emitting=true` on a *running* emitter is a no-op (`if (emitting == p_emitting) return`).
   `one_shot` is not cleared by the finish — re-trigger by `emitting=true` or `restart()`.
7. **`request_particles_process` is a foot-gun**: it *sets* `emitting=true` internally
   while processing the requested time and the residual argument flips it back (measured
   `emitting` state after a request run can read `true` even though the cycle finished);
   never pin `emitting` immediately after a request call — pin the call index and the
   `finished` count.
8. **CPU `draw_order` accepts the GPU-only value 2** after conversion (out-of-enum) —
   an author switching emitters should normalize `draw_order`.
9. **`*_curve` is a texture** in this build (law 15) — assigning a `Curve` is a parse
   error, and `set_param_curve` does not exist.
10. **`seed` is randomized per instance** — never pin it; if determinism is needed set
    `use_fixed_seed=true` and an explicit `seed` (not measured here: whether
    `use_fixed_seed` actually makes the emission deterministic is unobservable headless
    — no per-particle readback).
11. **`census` is an 8.6 KB (8785 B) signature** — the whole defaults table is one row. If the
    battery prefers leaner signatures, cut the row at `ppm_curve_types=` or keep only
    `*_consts` (the full line is still in `runs/canonical-lines.txt`).
12. **Mechanism caveat [I]**: upstream `master` `cpu_particles_2d.cpp` (fetched, not this
    build) explains law 12/13 with per-instance `active`/`time` plus
    `if (!Math::is_equal_approx(time, 0.0) && active && !should_be_active) emit finished`
    — this build's behaviour matches that shape but the exact flag ownership
    (instance vs process-global) was **not** verified against this build's source; the
    laws above are the empirical contract.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (19, exec-checked)

`corpus/live/r94-scout/author-rows.py.txt` holds `ROWS` (full lines) and `ROWS_PREFIX`
(gating prefixes) plus an empty `EXPECTED_ERRORS` (0 B stderr on all 143 receipts).

- **`ROWS_PREFIX` (recommended, gating): 143/143 receipts accepted, `rejected=[]`** —
  verified against every canonical rep **and** every loadtest rep with the production
  `classify_process` (segment sha256 `749fa060…`):

```
r94_particles_census        PASS particles_lattice census cpu_consts=… (full 8.6 KB (8785 B) line)
r94_particles_ppm           PASS particles_lattice ppm iv_min=7.0000 iv_max=9.0000 scale=(2.0000,3.0000) tex_same=true curve_same=true flags=truetrue sub_mode=3 sub_amt=3 coll=2 turb=true turb_n=1
r94_particles_convert       PASS particles_lattice convert g2c[amount=12 … col=0.100/0.200/0.300/0.400]
r94_particles_cpu_lifetime  PASS particles_lattice cpu_lifetime ok=true l01_ok=true l025_ok=true l05_ok=true l1_ok=true
r94_particles_cpu_expl      PASS particles_lattice cpu_expl ok=true e1_ok=true e05_ok=true e0_ok=true
r94_particles_cpu_speed_pre PASS particles_lattice cpu_speed_pre ok=true ss2_ok=true ss05_ok=true pre25_ok=true ff30_ok=true
r94_particles_cpu_stop      PASS particles_lattice cpu_stop ok=true stop10_ok=true stop40_ok=true
r94_particles_cpu_never     PASS particles_lattice cpu_never ok=true never_fired=true n_fin=0
r94_particles_cpu_contam    PASS particles_lattice cpu_contam ok=true n_never=2
r94_particles_cpu_oneshot_off  PASS particles_lattice cpu_oneshot_off ok=true fin_ok=true em_after=false os_after=true
r94_particles_cpu_oneshot_flag PASS particles_lattice cpu_oneshot_flag ok=true never_fired=true em_after=true os_after=false
r94_particles_cpu_pause     PASS particles_lattice cpu_pause ok=true vis_ok=true vis_parent_ok=true pm_disabled_ok=true ts0_ok=true
r94_particles_cpu_restart   PASS particles_lattice cpu_restart ok=true first_ok=true second_ok=true first_em=false first_ise=false em_after_restart=true ise_after_restart=true em_after=false
r94_particles_cpu_retrigger PASS particles_lattice cpu_retrigger ok=true first_ok=true second_ok=true em_set=true ise_set=true
r94_particles_cpu_lt_mid    PASS particles_lattice cpu_lt_mid ok=true fin_ok=true em_after=false
r94_particles_cpu_speed_mid PASS particles_lattice cpu_speed_mid ok=true fin_ok=true em_after=false
r94_particles_cpu_amount_mid PASS particles_lattice cpu_amount_mid ok=true em_at_set=true spurious_finish=true
r94_particles_cpu_request   PASS particles_lattice cpu_request ok=true step010_ok=true step005_ok=true
r94_particles_gpu_headless  PASS particles_lattice gpu_headless ok=true os_ok=true cont_ok=true manual_ok=true capture_ok=true
```
  (Exact strings in `author-rows.py.txt`; the `…` above is elision only.)
- **`ROWS` (full-line, informational): 30 loadtest/canonical rejections** across the 7
  cells with a ±1-tick tail (`cpu_lifetime` 7, `cpu_expl` 2, `cpu_speed_pre` 3,
  `cpu_stop` 5, `cpu_pause` 6, `cpu_restart` 2, `gpu_headless` 5) — use these only in a
  quiet window or as mode envelopes; the values are in `runs/canonical-lines.txt`.

Every cell is `ERROR:`-clean with 0 B stderr (measured on all 143 receipts).

Probe file lands at `corpus/fixtures/particles_lattice.gd` (self-contained `SceneTree`
script, battery `--arm=` convention, 19 arms). Insert the rows ahead of the crash/
descendant tail like prior blocks; no other fixture change is needed.

### 6.2 What to pin and what not to pin

1. **Pin the boolean block before `" | "`** for every timing cell — it encodes the law and
   is load-proof at loadavg 110.
2. **Pin the exact integers only where they are byte-stable** (12 cells, §2) — never for
   the 7 ±1-tick cells (use the `ROWS` line as a mode envelope instead).
3. **Do not pin** `seed`, particle positions/colors, RIDs, `flip_after` on the GPU cell
   (3–7 ticks), or `emitting` immediately after a `request_particles_process` call.
4. **Pin `fin_call1`** for the request cell (`6` and `11`) — it is a pure integer of the
   clock-free lattice and was stable over 6 canonical + 2 loadtest reps.
5. **Pin `fin_after_set=0` + `em_fin=true`** for the amount hazard — that pair *is* the
   spurious-finish law.
6. **Keep one emitter per process** for never-emitting cells (`cpu_never`), and keep
   `cpu_contam` as the positive control for law 12.

---

## 7. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | `finished` fires after a fixed number of frames independent of `lifetime` | **REFUTED [A]** — 6/15/30/60 ticks for L=0.1/0.25/0.5/1.0; ms scale with L |
| F2 | `explosiveness=0` finishes at `lifetime` (all particles born at t=0) | **REFUTED [A]** — 56 ticks (1.875·L); the emission window is streamed |
| F3 | `explosiveness=0` finishes at `2·lifetime` (last particle at the end of the window) | **REFUTED [A]** — the last slot is `(amount-1)/amount` of the window |
| F4 | `emitting=false` kills live particles | **REFUTED [A]** — continuous stop@10 finishes at 30; one-shot off@10 finishes at 60 |
| F5 | `emitting=false` from tick 0 still emits `finished` | **REFUTED [A]** — no finish in 60 ticks (first-emitter process) |
| F6 | `finished` fires while `one_shot=false` (continuous) | **REFUTED [A]** — never, including after a mid-cycle flag flip |
| F7 | a hidden emitter keeps simulating | **REFUTED [A]** — clock frozen; resumes with the remaining lifetime |
| F8 | removal from the tree kills/stops the emitter permanently | **REFUTED [A]** — detach@5 re-add@20 finishes at 45 (paused, not reset) |
| F9 | `GPUParticles2D` emits `finished` headless | **REFUTED [A]** — never, one-shot/continuous/manual; `emitting` clears silently |
| F10 | GPU and CPU particles share timing semantics headless | **REFUTED [A]** — CPU finishes at 15 ticks, GPU never |
| F11 | `restart()` on a finished one-shot re-emits immediately | **REFUTED [A]** — second finish `+14/15` ticks, `emitting=true` again |
| F12 | a finished one-shot cannot be re-triggered (`emitting=true` is ignored) | **REFUTED [A]** — second finish `+14`; `one_shot` stays true |
| F13 | `lifetime` is latched per particle at birth | **REFUTED [A]** — lowering it to 0.2 at tick 10 finishes at `+2` |
| F14 | `speed_scale` is latched per cycle | **REFUTED [A]** — raising it to 4 mid-cycle finishes at `+12` |
| F15 | changing `amount` mid-cycle is timing-neutral | **REFUTED [A]** — spurious `finished` on the set tick, real one suppressed |
| F16 | any setter mid-cycle emits `finished` | **REFUTED [A]** — `randomness`/`draw_order`/`scale_amount` controls do not |
| F17 | the spurious `finished` also fires for continuous emitters | **REFUTED [A]** — continuous amount change: `n_fin=0` |
| F18 | a never-emitting emitter never fires `finished` (unconditionally) | **REFUTED [A]** — after any emitter has run it fires at `delta=0` (process-global state) |
| F19 | `request_particles_process` is a wall-clock-dependent hint | **REFUTED [A]** — `time_scale=0` + step 0.1 → finish during call 6, step 0.05 → call 11, 6/6 reps |
| F20 | `request_particles_process` works for streamed emission too | **REFUTED [A]** — `e=0`, 300 calls, never finishes |
| F21 | PPM curves are `Curve` resources | **REFUTED [A]** — all `*_curve` props are `Texture2D` (type 24); `set_param_curve` absent |
| F22 | `capture_rect()` needs a real renderer but returns *something* | **REFUTED [A]** — zero rect headless |
| F23 | GPU→CPU conversion drops timing/params | **REFUTED [A]** — full transfer both directions (incl. the out-of-enum `draw_order=2`) |
| F24 | `seed` is a stable default | **REFUTED [A]** — random per instantiation |

---

## 8. Remaining unknowns / not measured

- **No per-particle observables**: positions, colors, velocities, scales are not readable
  from GDScript (no API) — every law here is node-level timing/readback. `capture_rect`
  would expose particles on a real renderer; headless it is a zero rect.
- **GPU-only features are unmeasurable headless**: collision (`collision_mode`,
  `collision_base_size`), sub-emitters (`sub_emitter`, `sub_emitter_*`), trails
  (`trail_*`), turbulence, attractors. Only enum/param readback is pinnable (§3.1/3.2).
- **tps dependence**: all timing cells are 60 tps; a 120 tps variant was **not** run
  (the independent labrat probe that would have covered it could not execute, §9). The
  clock-free request lattice is tps-independent by construction.
- **`use_fixed_seed=true` + explicit `seed` determinism** — not observable headless.
- **`fixed_fps` edge values** (`1`, `1000`, `fract_delta` interaction under load) — only
  `30` measured.
- **`amount_ratio`** (GPU-only property) and `interp_to_end`/`interpolate` — readback
  only; no headless behaviour.
- **`convert_from_particles` loss matrix** — only two parameter sets measured; unusual
  shapes (ring, directed points, `emission_points` arrays, texture-based curves) not
  exercised.
- **`CPUParticles2D` + `CanvasItemMaterial` particles animation** (the
  `get_configuration_warnings` path) — not measured.
- **Particle-process behaviour at 120 tps / under `--fixed-fps`** and **`PhysicsServer`
  interaction** — out of scope this round.
- **Portability**: every value is this host/build/`--headless`/60 tps.

---

## 9. Independent probe (frozen `probeParent` dispatch) — INCONCLUSIVE

Exactly one `ufo-labrat` dispatch was made (bounded depth-2, read-only) to independently
falsify the three load-bearing laws (one-shot tick scaling, the streamed-emission
formula, GPU inertness). **The seat returned INCONCLUSIVE with no receipts**: its
substrate exposed only `read`/`grep`/`glob` tools — no shell, no file write — so it could
not launch `godot` or create `corpus/live/r94-labrat/`. Nothing was written by that
dispatch and no claim above rests on it. The falsification set in §7 is therefore
single-seat evidence; an independent replication of F1/F2/F9 remains an open item for the
verifier seat.

---

## 10. Host cleanup

- **213 receipted launches** (105 canonical + 38 loadtest + 54 discovery + 16 smoke) plus
  ~15 one-off scratch launches, all `--headless`, all `timeout -s KILL 30`-bounded (none
  hit), no run left running from this seat (`pgrep -fa "r94-scout"` shows only the grep
  itself; concurrent lanes' godot processes are untouched).
- The loadtest `yes` hogs were started and killed by PID (8 own). `pgrep -c -x yes`
  read 64 before the block, 88 during it (8 own + ~80 from concurrent lanes) and 16
  after it — none of the remaining hogs are mine, and no other lane's process was
  signalled.
- No tracked file written: `git status --porcelain` shows only the concurrent lane's
  pre-existing ` M corpus/fixtures/run_battery.py` (read-only for this seat).
- `manifest.sha256` (598 lines) covers every artefact under `corpus/live/r94-scout/`.

---

## 11. Evidence index

All under `corpus/live/r94-scout/`; `manifest.sha256` (598 lines) covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| **frozen primary probe, 19 arms** | `probes/particles_lattice.gd` | `e6a2e0f55c6bbeaa` |
| discovery probes (7 files) | `probes/discover*.gd` | `manifest.sha256` |
| launch project (fixtures byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| driver (19 cells, 105 runs) | `run_cells.sh` | `f70566f1d2075202` |
| loadtest driver (38 runs) | `run_loadtest.sh` | `5231a4f26f236900` |
| analyzer → json | `analyze_r94.py` → `runs/analyze_r94.json` | `947dd72575f9ad3b` / `201d4438a5b89ec8` |
| author rows + builder + verifier | `author-rows.py.txt`, `make_author_rows.py`, `verify_rows.py` | `29fa7da8c6c75599` / `d91b54d0bd6c5e3e` / `68c5a6bb025743a7` |
| per-cell receipts (105 × 3 files) | `runs/r94_particles_*.{out,err,rc}` | `manifest.sha256` |
| loadtest receipts (38 × 3 files + summary) | `runs/loadtest/` | `manifest.sha256` |
| discovery/smoke receipts (70 × 2 files) | `runs/disc*.{out,err}`, `runs/smoke*.{out,err}` | `manifest.sha256` |
| unique canonical lines per cell | `runs/canonical-lines.txt` | `manifest.sha256` |
| receipts index | `RECEIPTS.md` | `manifest.sha256` |

Reproduce: `bash run_cells.sh && python3 analyze_r94.py && python3 make_author_rows.py &&
python3 verify_rows.py` (expect `ROWS_PREFIX … rejected=[]`,
`full_line_rejections=30`), then `HOGS=8 REPS=2 bash run_loadtest.sh` and re-verify.
