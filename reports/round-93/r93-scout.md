# game-dev-2d round 93 — scout (r93-scout): the AnimationPlayer + Tween authorability lattice, pre-measured; 15 rows verbatim-ready

Seat `SCOUT` (LEAF) | lane `r93-scout` | round 93 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps default, GodotPhysics2D. Repo `~/Projects/shokunin/game-dev-2d-shokunin`,
HEAD at session start **`c97424b`** (*r92 scout*). The one modified tracked file,
`corpus/fixtures/run_battery.py` (82 insertions), is the **concurrent r89 geo2d/input
fold lane's** edit (its diff adds `geo2d_lattice.gd`/`input89_edges.gd` rows; nothing
animation- or tween-related) — not this seat's. The launch `project.godot` is the
byte-copy of `corpus/fixtures/project.godot` (`8de8b3af…`).

**No git mutation, no tracked file written, no commit.** Writes are this report and
`corpus/live/r93-scout/**` only.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server
installed; `definition`/`references`/`hover` were **unavailable for every file touched**.
This round needed no cross-file symbol work: the deliverable is a new self-contained
probe plus receipts, so semantic carriers are fresh-process execution receipts, engine
`ClassDB`/runtime introspection inside the probes, and engine-emitted error text. Every
`file:line` below is engine-emitted `at:` backtrace text, never a source read.

**Labrat disclosure (blocker).** The one permitted frozen-`probeParent` labrat was
dispatched; it returned **INCONCLUSIVE for all three hypotheses because that seat's
substrate exposes no command-execution tool** (read/grep/glob only) — zero Godot
launches, no receipts. No independent replication exists from that seat; §8 records the
open verification need. The claims below rest on this seat's own fresh-process receipts.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Assigned: the AnimationPlayer runtime + Tween authorability lattice.** The r91 scout
weighed this surface but measured only three `Tween.interpolate_value` discovery values
(`linear@0.25=2.5`, `quad/EASE_IN_OUT@0.25=1.25`, `expo/EASE_OUT@0.5=9.69718754291534`,
`corpus/live/r91-scout/runs/disc-tweenval.out`) and left the timing half explicitly
unprobed. This round **verifies that receipt byte-for-byte and extends it into a full
authoring lattice** [M] (§3.2, §7 F1).

Why it is falsifiable and cheap:

- **Both halves have a manual clock.** `Tween.custom_step(delta)` and
  `AnimationPlayer.advance(delta)`/`seek()` turn frame-coupled animation into exact,
  frame-independent stepping — so the interesting cells are *pinnable* rather than
  envelope-only (the r87 lesson that timing cells become modes applies only to the
  frame-coupled residue; §3.6/§3.11 mark exactly those fields) [M].
- **The subsystem is a trap field.** A first probe pass immediately refuted four naive
  models (expo curve, time clamping, same-name replay, `play()` applying the pose) —
  §7 [A].
- **No battery overlap.** `grep -rin "tween\|AnimationPlayer" corpus/fixtures/*.gd` finds
  only r5 `animation_property.gd` (MANUAL-free `advance(0.5)` → x=60) and r13
  `tween_flash.gd` (modulate excursion/return). No track-type, method-callback, blend,
  seek, process-mode, cache or interpolation-sampler rows exist [O].

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (10 arms, fresh process) | API census, interpolate_value grid, expo reverse-engineering, custom_step, MANUAL advance/seek, method tracks, track sampler, blend, process modes, frame clock | `runs/disc-*.{out,err,rc}` |
| 2 | `probes/discover2.gd` (7 arms) | loose ends: same-name replay, Tween.stop, node-free, blend step lattice, delay/from/relative, pingpong, infinite loops | `runs/disc2-*.{out,err,rc}` |
| 3 | `bash run_cells.sh` | **11 cells** (4 pure ×3, 7 runtime ×6) = **54 runs** | `runs/r93_*.{out,err,rc}` |
| 4 | `bash run_loadtest.sh` (16 `yes` hogs) | 8 cells ×3 = **24 runs** at load avg 104–118 | `runs/loadtest/` |
| 5 | `python3 analyze_r93.py` | per-cell reps / out-uniq / err-uniq / rc vectors + varying-token census | `runs/analyze_r93.json` |
| 6 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 15 gating + 2 informational rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |
| 7 | `python3 audit_claims.py` | recomputes every headline numeric law from the raw receipts (r91 receipt, expo closed forms, crossfade weight law, running-source formula, stable clauses, byte-identity) — **AUDIT PASS, 0 mismatches** | stdout |

**Canonical cell set: 54 runs across 11 cells** — `census`/`tweenval`/`tweenval_grid`/
`animtrack` ×3 (pure/readback), `tweenstep`/`tweenchain`/`tweenproc`/`animseek`/
`animmethod`/`animblend`/`animproc` ×6 (runtime/lifecycle). All rc=0; canonical stderr
**0 B in 54/54 reps**; no run crashed; no run left running.

**Byte-stability: 9 of 11 cells are `out_uniq=1 err_uniq=1`** (`runs/analyze_r93.json`):
census, tweenval, tweenval_grid, animtrack, tweenstep, tweenchain, animseek, animmethod,
animblend. **Two mode cells:** `tweenproc` (`out_uniq=5`) and `animproc` (`out_uniq=6`);
both carry a trailing `stable=[…]` boolean clause that is byte-identical in **9/9**
canonical+loadtest reps (§3.6, §3.11).

**Arm-dispatch integrity [O]:** every arm prints its own name on its `PASS` line
(`PASS anim_lattice <arm> …`), parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan), so a silent `_:` fallback (the r88
dead-seat failure) cannot recur.

**Load discipline:** under load avg **104–118**, all 8 loadtest cells stayed rc=0 with
0 B stderr and the six non-frame-coupled cells (tweenstep, tweenchain, animseek,
animmethod, animblend, tweenval) remained **byte-identical**; only the frame-coupled mode
cells varied (§3.6, §3.11). This is the strongest statement available for these cells: a
`MANUAL`/`custom_step` clock makes the receipt load-immune, while frame-count cells are
modes.

**Frame clock [M]** (`runs/disc-clock.out`): `proc_delta_us=6225.6` (≈160.6 process
frames/s — headless process frames are **not** 60 fps; `engine_max_fps=0`),
`phys_delta_us=16560.3` (60.4 physics ticks/s). This is why frame-counted animation
cells are modes and why the manual clocks are the authoring path.

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **Class/enum/default census** (Animation, AnimationMixer, AnimationPlayer, Tween) | **PINNABLE** | 3 | uniq=1 |
| **`Tween.interpolate_value`** (r91 receipt + 12×4 grid + clamps + Variant kinds) | **PINNABLE** pure function; expo carries a measured 0.001 quirk | 3 canonical (+3 loadtest on tweenval) | uniq=1 |
| **`Tween` manual stepper** (`pause`+`custom_step`, completion signals, loops) | **PINNABLE** | 6 | uniq=1 |
| **`Tween` chains** (sequential/parallel/interval/callback/method/kill/owner-free) | **PINNABLE** | 6 | uniq=1 |
| **`Tween` process-mode coupling** | **mode** (frame-coupled); structural clause PINNABLE | 6 | uniq=5 (stable clause 9/9) |
| **`AnimationPlayer` MANUAL clock** (play/advance/seek/pause/stop/speed/loop/replay) | **PINNABLE** | 6 | uniq=1 |
| **Method-track callbacks** (DEFERRED vs IMMEDIATE, disabled track, signals) | **PINNABLE** | 6 | uniq=1 |
| **Track sampling** (`value_track_interpolate` NEAREST/LINEAR/CUBIC, bezier) | **PINNABLE** pure sampler | 3 | uniq=1 |
| **Blending** (`blend_times`, default blend, hard switch, `play_with_capture`) | **PINNABLE** under a uniform manual step; weight is step-granularity dependent | 6 | uniq=1 |
| **Process modes / caches / mixer signals** | structural clause PINNABLE; frame counters **mode** | 6 | uniq=6 (stable clause 9/9) |

---

## 3. Measured values, verbatim

All payloads are `runs/r93_<cell>.rep1.out`; `%.4f` only where noted, otherwise Godot's
default `str(float)` (float32-precision prints).

### 3.1 Census (`census`) — [M]

```
PASS anim_lattice census ap_is_mixer=true ap_is_node=true tw_is_ref=true anim_is_res=true
 anim_consts=[TYPE_VALUE=0,TYPE_POSITION_3D=1,TYPE_ROTATION_3D=2,TYPE_SCALE_3D=3,TYPE_BLEND_SHAPE=4,
   TYPE_METHOD=5,TYPE_BEZIER=6,TYPE_AUDIO=7,TYPE_ANIMATION=8,INTERPOLATION_NEAREST=0,
   INTERPOLATION_LINEAR=1,INTERPOLATION_CUBIC=2,INTERPOLATION_LINEAR_ANGLE=3,INTERPOLATION_CUBIC_ANGLE=4,
   UPDATE_CONTINUOUS=0,UPDATE_DISCRETE=1,UPDATE_CAPTURE=2,LOOP_NONE=0,LOOP_LINEAR=1,LOOP_PINGPONG=2,
   LOOPED_FLAG_NONE=0,LOOPED_FLAG_END=1,LOOPED_FLAG_START=2,FIND_MODE_NEAREST=0,FIND_MODE_APPROX=1,FIND_MODE_EXACT=2]
 mixer_consts=[ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS=0,ANIMATION_CALLBACK_MODE_PROCESS_IDLE=1,
   ANIMATION_CALLBACK_MODE_PROCESS_MANUAL=2,ANIMATION_CALLBACK_MODE_METHOD_DEFERRED=0,
   ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE=1,ANIMATION_CALLBACK_MODE_DISCRETE_DOMINANT=0,
   ANIMATION_CALLBACK_MODE_DISCRETE_RECESSIVE=1,ANIMATION_CALLBACK_MODE_DISCRETE_FORCE_CONTINUOUS=2]
 player_consts=[ANIMATION_PROCESS_PHYSICS=0,ANIMATION_PROCESS_IDLE=1,ANIMATION_PROCESS_MANUAL=2,
   ANIMATION_METHOD_CALL_DEFERRED=0,ANIMATION_METHOD_CALL_IMMEDIATE=1]
 tween_consts=[TWEEN_PROCESS_PHYSICS=0,TWEEN_PROCESS_IDLE=1,TWEEN_PAUSE_BOUND=0,TWEEN_PAUSE_STOP=1,
   TWEEN_PAUSE_PROCESS=2,TRANS_LINEAR=0,TRANS_SINE=1,TRANS_QUINT=2,TRANS_QUART=3,TRANS_QUAD=4,TRANS_EXPO=5,
   TRANS_ELASTIC=6,TRANS_CUBIC=7,TRANS_CIRC=8,TRANS_BOUNCE=9,TRANS_BACK=10,TRANS_SPRING=11,
   EASE_IN=0,EASE_OUT=1,EASE_IN_OUT=2,EASE_OUT_IN=3]
 ap_defaults=[proc=1,cbm=0,cbp=1,cbd=1,root=..,active=true,speed=1.0,default_blend=0.0,auto_capture=true]
 anim_defaults=[len=1.0,loop=0,step=0.0333333350718,tracks=0]
 ap_signals=[script_changed,property_list_changed,ready,renamed,tree_entered,tree_exiting,tree_exited,
   child_entered_tree,child_exiting_tree,child_order_changed,replacing_by,editor_description_changed,
   editor_state_changed,animation_list_changed,animation_libraries_updated,animation_finished,animation_started,
   caches_cleared,mixer_applied,mixer_updated,current_animation_changed,animation_changed]
 tw_signals=[script_changed,property_list_changed,step_finished,loop_finished,finished]
 an_m_count=177 tw_m_count=94 ap_m_count=293
 cache_methods=[clear_caches]
 capture_methods=[set_auto_capture,is_auto_capture,set_auto_capture_duration,get_auto_capture_duration,
   set_auto_capture_transition_type,get_auto_capture_transition_type,set_auto_capture_ease_type,
   get_auto_capture_ease_type,play_with_capture,capture]
 blend_methods=[set_blend_time,get_blend_time,set_default_blend_time,get_default_blend_time]
 an_sample_methods=[position_track_interpolate,rotation_track_interpolate,scale_track_interpolate,
   blend_shape_track_interpolate,value_track_interpolate,bezier_track_interpolate]
 tw_step_methods=[custom_step]
```
(the exact one-line receipt is `runs/r93_census.rep1.out`; line wrapped here for print)

- **`Animation.TYPE_*` order is not the "value first, method last" guess**: VALUE=0,
  POSITION_3D=1, ROTATION_3D=2, SCALE_3D=3, BLEND_SHAPE=4, **METHOD=5, BEZIER=6, AUDIO=7,
  ANIMATION=8** [M].
- **Defaults:** `AnimationPlayer` is `AnimationMixer` is `Node` (`ap_is_mixer=true`,
  `ap_is_node=true`); `Tween` is `RefCounted` (`tw_is_ref=true`) and **cannot be
  constructed directly** (`Tween.new()` → `ERROR: Tween can't be created directly. Use
  create_tween() method.`, `runs/disc-census.err`) [M].
- `ap_defaults`: process mode IDLE(1), method callback DEFERRED(0), process callback
  IDLE(1), discrete RECESSIVE(1), **root `..`** (the parent node — that is why the r5
  `.:position:x` track targets the player's parent), active=true, speed 1.0, blend 0.0,
  **auto_capture=true** [M].
- `Animation` defaults: length **1.0** (not 0), loop NONE, step 1/30, 0 tracks [M].
- Cache/capture surface is thin but real: `clear_caches()` + `caches_cleared` signal;
  `set_auto_capture*`/`play_with_capture`/`capture`; there is **no public per-property
  cache readback** — the cache is only observable through `caches_cleared` and behaviour
  [M].

### 3.2 `Tween.interpolate_value` (`tweenval`) — [M], the r91 receipt + quirk

```
PASS anim_lattice tweenval r91_exact=9.69718754291534 expo_in_05=0.30249999836087
 expo_in_10=9.99000012874603 expo_out_05=9.69718754291534 expo_out_10=10.0
 clamp_neg=-5.0 clamp_over=15.0 int_025=3 int_050=5 int_075=8 vec_025=(2.0, 4.0)
 color_050=(0.5, 0.25, 0.0, 1.0) form_in_err=0.00000000016391 form_out_err=0.00000000429153
```

- **The r91 discovery receipt reproduces byte-for-byte** in 3/3 canonical and 3/3
  loadtest reps: `interpolate_value(0.0, 10.0, 0.5, 1.0, TRANS_EXPO, EASE_OUT)` =
  `9.69718754291534` [M].
- **Time is NOT clamped** [M]: `elapsed=-0.5` → `-5.0`; `elapsed=1.5` → `15.0`
  (linear). The *runtime* tween clamps (a tween's value never exceeds its endpoints in
  the measured chains); the *static* function extrapolates. Author trap: do not use
  `interpolate_value` as a safety-clamped sampler.
- **Integer deltas round** [M]: `0,10` at 0.25/0.5/0.75 → `3, 5, 8` (2.5→3, 7.5→8).
- `Vector2` and `Color` deltas interpolate componentwise [M].

**The expo quirk [M].** The expo curve is *not* the textbook `1−2^(−10t)`:

- `EASE_IN(t) = 2^(10(t−1)) − 0.001` (measured float32 residual `form_in_err=1.6391e-10`
  at t=0.5), so **at t=1.0 it yields 0.999, not 1.0**: with delta 10 the endpoint is
  `9.99000012874603` [M].
- `EASE_OUT(t) = 1.001·(1 − 2^(−10t))` (residual `form_out_err=4.29153e-9` at t=0.5),
  with `t=1.0` special-cased to exactly `10.0` [M].
- Both formulas match every sampled point (t = 0.05…0.95) to float32 precision
  (`runs/disc-expo.out`); the 0.001 offset is structural, not rounding (at t=0.1 the
  measured 0.00095312501071 differs from `2^-9` by exactly 0.001) [M].

### 3.3 The 12×4 grid (`tweenval_grid`) — [M]

Expo row verbatim (the other 11 rows are in `runs/r93_tweenval_grid.rep1.out`):

```
expo in=0.0,0.04524271469563,0.30249999836087,1.75776690244675,9.99000012874603
     out=0.0,8.24046492576599,9.69718754291534,9.95470225811005,10.0
     io=0.0,0.15124999918044,5.00249981880188,9.84867215156555,10.0
     oi=0.0,4.84859377145767,5.0,5.15124976634979,9.99499976634979
```

Spot values (t = 0.25/0.5/0.75/1.0, delta 10) [M]: `lin` 2.5/5.0/7.5/10.0 for all four
eases; `qad in` 0.625/2.5/5.625/10.0; `qad out` 4.375/7.5/9.375/10.0; `qui out`
7.626953125/9.6875/9.990234375/10.0; `sin io` 1.46446615457535/5.0/8.53553414344788/10.0;
`bac io` −0.99681839346886/5.0/10.9968185424805/10.0; `spr out`
6.6333669424057/10.5101573467255/9.86345112323761/10.0. The
sin/quad/quint/quart/cubic/circ/bounce rows match their standard closed forms at the
sampled points (e.g. `sin out`@0.25 = sin(π/8) = 0.38268343…, `qui out`@0.25 =
1−0.75⁵ = 0.7626953125); **expo alone carries the 0.001 offset**; `ela`/`bac`/`spr`
overshoot/undershoot as designed (a pin must expect out-of-range values) [M].

### 3.4 Tween manual stepper (`tweenstep`) — [M]

```
PASS anim_lattice tweenstep created=[true,true,0.0,0.0] step05=[5.0,true,0.5,0,0]
 step10=[10.0,false,1.0,1,1] step_again=[10.0,false,1.0,1,1]
 paused=[5.0,false,true,0.25,0] paused_done=[20.0,false,1.0,1]
 loop1=[2.0,1,0,1] loop2=[2.0,0,1,1]
```
(fields: created=[running,valid,x,elapsed]; stepN=[x,running,elapsed,finished,step_finished];
paused=[y,running,valid,elapsed,finished]; loopN=[scale_x,loops_left,finished,loop_finished])

- `custom_step(0.5)` on a 0→10 / 1.0 s property tween yields exactly `5.0`; a second
  `custom_step(0.5)` yields `10.0`, `running=false`, and **`finished` + `step_finished`
  fire synchronously inside the call**; a third step is inert (idempotent completion) [M].
- **`pause()` + `custom_step` is the deterministic recipe**: a paused tween reports
  `running=false` but `valid=true`, does not auto-advance across frames, and still steps
  exactly (`y=5.0` at 0.25; `20.0` at completion) [M].
- `set_loops(2)` on a 0.5 s leg: after one step `scale_x=2.0`, `loops_left=1`,
  `loop_finished=1`; after the second, `loops_left=0`, `finished=1` [M]. `set_loops(0)`
  is infinite (`get_loops_left()=-1`, never finishes; `runs/disc2-inf.out`) [M].

### 3.5 Tween chains (`tweenchain`) — [M]

```
PASS anim_lattice tweenchain seq=[20.0,30.0,40.0] par=[30.0,2.0]
 interval=[cb_at_050=0,mvals_at_050=[],cb_at_100=1,mvals_at_100=[5.0],cb_after_extra=1]
 node_free=[before=[true,true],right_after=[true,true],stepped_after_free=[true,true],after_frame=[false,true]]
 kill=[before=[true,false],after=[false,false]]
```

- **Sequential legs are exact at the boundary**: a 0→20/0.5 s leg followed by a
  20→40/0.5 s leg gives `[20.0, 30.0, 40.0]` after steps 0.5/0.25/0.25 — the second leg
  starts only on the step *after* the first completes [M].
- `set_parallel(true)`: `[30.0, 2.0]` after one 0.5 step (y 0→60 and scale_x 1→3 both at
  50%) [M].
- **Interval + callback ordering**: after the 0.5 s interval step the callback has *not*
  fired (`cb_at_050=0`); it fires on the following step (`cb_at_100=1`) together with the
  first `tween_method` value (`mvals=[5.0]` — the method tween's own 50% point) [M].
- **Owner-free is lazy**: after `n.free()` the bound tween still reports
  `is_valid=true` and `custom_step` still runs (`stepped_after_free=[true,true]`);
  `is_valid` flips to `false` only at the next processing pass (`after_frame=[false,true]`)
  while `is_running` stays `true` [M]. `kill()` is immediate:
  `[true,false] → [false,false]` [M]. `Tween.stop()` resets `elapsed` to 0 but keeps the
  tween valid, and a following `custom_step` continues from the current property value
  (`runs/disc2-stopstep.out`: mid 5.0 → stop(elapsed 0) → step 0.25 → 6.25) [M].

### 3.6 Tween process-mode coupling (`tweenproc`) — mode + structural clause

```
PASS anim_lattice tweenproc auto=[y0=0.0,after3proc=1.66666662693024]
 paused=[at_pause=1.66666662693024,after3frames=1.66666662693024,running=false]
 phys=[x0=0.0,after3proc=16.6666679382324,after3phys=50.0]
 phys_manual=[before=1.0,after_step025=2.0]
 stable=[auto_advanced=true,paused_frozen=true,phys_advanced=true,manual_exact=true]
```

- An **unpaused** tween auto-advances on process frames (`auto_advanced=true`); a
  **paused** tween does not (`paused_frozen=true`, `running=false`) [M].
- A `TWEEN_PROCESS_PHYSICS` tween advances in *both* windows in the measured frame
  interleave (`after3proc` is bimodal 16.67/33.33 px = 1–2 physics ticks landing inside
  the process-frame window; `out_uniq=5`), i.e. the process/physics counters are a
  **mode** — but the manual step on a paused physics-mode tween is exact
  (`phys_manual` 1.0 → 2.0) [M].
- The `stable=[…]` quartet is byte-identical in **9/9** canonical+loadtest reps [M].

### 3.7 AnimationPlayer MANUAL clock (`animseek`) — [M]

```
PASS anim_lattice animseek at_play=[7.0,true,0.0,move] adv025=[25.0,0.25] seek_up=[75.0,0.75]
 seek_noup=[75.0,0.5] cross=[100.0,1.0,false,1] after_frame=[100.0,1] before_stop=50.0
 after_stop=[0.0,false,,move] speed2=[50.0,0.5] speed0=[50.0,0.5] replay_before=[50.0,0.5]
 replay_same=[50.0,0.5] play_other=[50.0,0.0,loop] back_other=[50.0,0.0] paused_adv=[50.0,false]
 looped=[25.0,0.25,0] seek_over=[100.0,1.0,true] manual_frames=[0.0,0.0]
```

- **`play()` does not apply the pose**: with the property pre-set to 7.0, `play("move")`
  leaves x=7.0 (`at_play`); the first `advance` applies the animation
  (`adv025=[25.0,0.25]`) [M].
- `seek(0.75, true)` applies x=75 immediately; `seek(0.5, false)` moves the position to
  0.5 **without** applying the value (x stays 75) [M].
- `advance` past the end clamps position to 1.0, stops, applies the last key (100.0) and
  **fires `animation_finished` synchronously inside `advance`** (`cross` finished=1) [M].
- **`stop()` resets the property to the animation's t=0 value**, not the pre-play value:
  x 7.0 → play → advance(0.5) → 50.0 → stop → **0.0** (`after_stop`); `current_animation`
  becomes `""` while `assigned_animation` stays `"move"` [M].
- `speed_scale=2` doubles the step (advance 0.25 → pos 0.5, x=50); `speed_scale=0`
  **freezes** `advance` (pos stays 0.5) [M].
- **Replaying the same animation name is a no-op** (`replay_same=[50.0,0.5]`), while
  playing a *different* name resets position to 0.0 without applying its value
  (`play_other=[50.0,0.0,loop]`) [M].
- `pause()` then `advance(0.5)` still steps exactly (`paused_adv=[50.0,false]`) [M].
- `LOOP_LINEAR` at 0.75 on a 0.5 s loop wraps to pos 0.25, x=25, **no** finished signal;
  `LOOP_PINGPONG` cycles 0→0.5→0 (`runs/disc2-pingpong.out`: 0.75→pos 0.25, 1.25→0.25,
  1.75→0.25, never finishes) [M].
- `seek(2.0, true)` beyond length clamps to 1.0 and **keeps playing** [M].
- A MANUAL player **does not advance on awaited frames** (`manual_frames=[0.0,0.0]`) [M].

### 3.8 Method-track callbacks (`animmethod`) — [M]

```
PASS anim_lattice animmethod sig_at_play=[1,0,1] deferred_adv=[] deferred_frame=[7,8]
 sig_after_frame=[1,0,2] immediate_adv=[7,8] immediate_frame=[7,8] disabled_track=[]
 started_names=[m,m,m] changed=[] cur_changed=[m,,,,,]
```

- Keys at t=0.2 → `notify(7)` and t=0.5 → `notify(8)`; with the default
  `callback_mode_method=DEFERRED` a manual `advance(1.0)` produces **no calls**
  (`deferred_adv=[]`); they flush on the next `await process_frame` (`deferred_frame=[7,8]`)
  [M].
- `ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE` calls both **synchronously inside
  `advance(1.0)`** (`immediate_adv=[7,8]`) [M].
- `track_set_enabled(false)` suppresses calls entirely (`disabled_track=[]`) [M].
- `animation_started` fires once per `play()` (3 plays → `started_names=[m,m,m]`);
  `animation_changed` never fired in this arm; `current_animation_changed` fires with the
  name on play and with `""` on stop [M].

### 3.9 Track sampling (`animtrack`) — [M], pure

```
PASS anim_lattice animtrack
 two_key=[it0=[t05=0.0,t09=0.0,t10=10.0],it1=[t05=5.0,t09=8.99999976158142,t10=10.0],
          it2=[t05=5.0,t09=9.71999987125395,t10=10.0]]
 three_key=[it0=[t025=0.0,t075=10.0],it1=[t025=5.0,t075=5.0],it2=[t025=5.0,t075=5.0]]
 two_default_interp=1 three_key_count=3 k0=0.0 kt1=0.5 k1=10.0
 bezier=[1.05892944335938,5.0,8.94107055664062] bezier_key_count=2
 track_enabled=true track_type=0 track_path=.:position:x
```

- `Animation.value_track_interpolate(track, time)` exists and is a pure sampler [M].
- **NEAREST holds the previous key** (t=0.5 and 0.9 → 0.0; t=1.0 → 10.0; on the
  three-key triangle 0.25→0.0, 0.75→10.0) [M].
- LINEAR and CUBIC agree at midpoints of symmetric layouts; with only two keys CUBIC is a
  different curve (0.9 → 9.71999987 vs linear 8.99999976) [M].
- Default interpolation type is **LINEAR(1)**; a bezier track with asymmetric handles
  samples `1.05892944 / 5.0 / 8.94107056` at 0.25/0.5/0.75 [M].

### 3.10 Blending (`animblend`) — [M], the crossfade weight law

`a`: x 0→100 over 1.0 s; `b`: constant 500; blend time a→b = 1.0 s; MANUAL clock.

```
finished_010=[100.0,144.444442749023,188.888900756836,233.333343505859,277.777801513672,
              322.222229003906,366.666687011719,411.111114501953,455.555572509766,500.0]
finished_005=[100.0,121.052627563477,…,478.947357177734,500.0]      (20 × 0.05 s steps)
finished_020=[100.0,200.0,300.0,400.0,500.0]                        (5 × 0.2 s steps)
running_from_50=[60.0000038146973,117.777778625488,173.333343505859,226.66667175293,
                 277.777801513672,322.222229003906,366.666687011719,411.111114501953,
                 455.555572509766,500.0]
hard=[at_play=100.0,after_025=500.0]  default_blend_mid=100.0
capture=[before=50.0,seq=60.0000038146973,117.777778625488,…]
```

- **Law: with N uniform manual steps of dt = blend_time/N, the crossfade weight at step
  i is `w_i = (i−1)/(N−1)`** — w=0 on the first step and w=1 exactly at
  t = blend_time. Verified across dt = 0.05 (N=20, increments 21.0526 px),
  0.1 (N=10, 44.4444), 0.2 (N=5, 100.0), 0.25 (N=4, 133.33) [M].
  Equivalently `w(t) = (t−dt)/(blend_time−dt)` — **the mid-blend value depends on the
  step granularity** (at t=0.6: 322.22 at dt=0.1 vs 300.0 at dt=0.2 vs 331.58 at dt=0.05),
  so mid-blend values are a **mode**, not a pure function of wall time [M].
- Crossfading from a *running* animation blends the still-playing `a` against `b`:
  the sequence matches `w_i·500 + (1−w_i)·a(t_i)` exactly (60.0, 117.78, 173.33, 226.67,
  277.78, …) [M].
- **Hard switch** `play("b", 0.0)` leaves the old value at play time (100.0) and applies
  the new animation on the next advance (500.0) [M].
- `set_default_blend_time(1.0)` is used by a plain `play("b")` (single 0.5 s step → w=0 →
  100.0) [M].
- `play_with_capture("b", 1.0)` from a running `a` (x=50) reproduces the running-crossfade
  sequence **identically** (`capture.seq == running_from_50`) [M].

### 3.11 Process modes / caches / signals (`animproc`) — mode + structural clause

```
PASS anim_lattice animproc
 idle=[x0=0.0,after3proc=0.38723334670067,after3phys=6.05586671829224,pos=0.1]
 phys=[x0=0.0,after3proc=1.66666674613953,after3phys=5.0]
 manual=[x=25.0,after3frames=25.0] frozen=[0.0,true,0.0] inactive=[50.0,true]
 quick=[frames_to_finish=17,fin_frame=16,x=5.0] caches_delta=1 caches_total=11
 mixer_updated=0 mixer_applied=42 is_playing=false
 stable=[manual_frame_frozen=true,manual_exact=true,speed0_frozen=true,inactive_advance=true,
         fin_fired=true,caches_once=true,mixer_updated_zero=true]
```

- IDLE advances on process frames; PHYSICS on physics ticks — but the *counters* are
  bimodal/phase-dependent (`after3proc` 0.0–1.7 across reps; `out_uniq=6`), so only the
  structural clause is pinnable [M].
- `speed_scale=0` freezes (`frozen=[0.0,true,0.0]`: x and pos unchanged, still playing);
  `active=false` **does not stop `advance()`** (`inactive=[50.0,true]`) [M].
- A 0.1 s animation under IDLE finishes after 16–17 process frames (~100 ms at ~160 fps)
  [M].
- `clear_caches()` emits `caches_cleared` exactly once (`caches_delta=1`) but the signal
  also fires from other operations (11 total across the arm) [M].
- `mixer_updated` **never fired** in this arm (0); `mixer_applied` fires per applied step
  (40–42, mode) [M].
- The `stable=[…]` septet is byte-identical in **9/9** canonical+loadtest reps [M].

---

## 4. Laws

### 4.1 The pure-function law [M]
`Tween.interpolate_value` is a deterministic, process-stable pure function (byte-identical
across reps and under load avg 118). It **extrapolates** outside [0, duration]; integer
deltas **round to nearest**; `Vector2`/`Color` interpolate componentwise. Eleven
transitions are textbook curves; `expo` is offset by exactly 0.001 (in: `−0.001`, so the
endpoint is 0.999·delta; out: `×1.001`, endpoint special-cased to delta).

### 4.2 The manual-clock law [M]
`Tween.pause()` + `Tween.custom_step(delta)` and
`AnimationPlayer.playback_process_mode=MANUAL` + `advance(delta)`/`seek()` are exact,
frame-independent clocks: identical bytes across 3–6 reps and under load avg 104–118.
**Author rule: pin animated values from a manual clock; never from a frame count.**
Frame-coupled progression (IDLE/PHYSICS, unpaused tweens) is a mode.

### 4.3 The completion-signal law [M]
`Tween.finished`/`step_finished`/`loop_finished` fire **synchronously inside
`custom_step`**; `AnimationPlayer.animation_finished` fires **synchronously inside
`advance`** (including the step that crosses the end); a MANUAL player's awaited frames
advance nothing. Method-track callbacks obey a different rule (4.6).

### 4.4 The play/stop semantics law [M]
`play()` does not apply a pose (the first advance/seek/process does); replaying the
**same name is a no-op** while a different name restarts at 0; `stop()` resets the
animated property to the animation's t=0 value (clobbering the pre-play value) and clears
`current_animation` but keeps `assigned_animation`; `seek(t, false)` moves the position
without applying; `seek` beyond length clamps and keeps playing; `speed_scale` scales the
manual step and 0 freezes it.

### 4.5 The crossfade law [M]
With N uniform steps of dt = blend_time/N the weight is `w_i=(i−1)/(N−1)` (0 on the
first step, 1 at t=blend_time); the running-source crossfade blends the still-playing
source against the target; a hard switch (`custom_blend=0`) applies on the next step;
`play_with_capture` ≡ running crossfade under the manual clock. **Mid-blend values are
step-granularity dependent — never pin them.**

### 4.6 The method-callback law [M]
`callback_mode_method=DEFERRED` (default) queues method-track calls to the end of the
**next** frame — a manual `advance()` executes the timeline but not the calls;
`IMMEDIATE` calls them inside `advance()`; a disabled track calls nothing;
`animation_started` fires once per `play()`.

### 4.7 The track-sampling law [M]
`Animation.value_track_interpolate` is a pure sampler: NEAREST holds the previous key
until the next key time; LINEAR interpolates; CUBIC uses tangents (differs from LINEAR
with 2 keys); default interpolation is LINEAR; bezier tracks sample their handles.

### 4.8 The lifetime law [M]
`Tween.new()` is refused (hard `ERROR`; use `create_tween()`); a node-bound tween is
invalidated **lazily** — `is_valid()` stays true through owner free and manual stepping
and flips false at the next processing pass while `is_running()` stays true; `kill()` is
immediate; `stop()` resets elapsed but keeps the tween valid and re-bases on the current
value.

### 4.9 The cache/capture law [M]
`clear_caches()` + `caches_cleared` is the only cache surface (one emission per explicit
call, but other operations also emit it); `auto_capture=true` by default;
`play_with_capture`/`capture` blend from the current pose; `mixer_updated` was never
observed firing while `mixer_applied` fires per applied step.

### 4.10 The authorability recipe [M]
For a pinnable animation/tween cell: build the scene, `await process_frame` once (tree
state is not live before), set `MANUAL`/`pause()`, drive with `advance`/`seek`/
`custom_step`, and read properties/positions after each step. Completion signals are
available synchronously at the crossing step.

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **`Tween.new()` is a hard error** (`runs/disc-census.err`) — only `create_tween()`
   (Node or SceneTree) yields a usable instance [M].
2. **`interpolate_value` does not clamp** (§3.2) — it extrapolates; the runtime tween
   clamps. Do not use it as a bounded sampler [M].
3. **The expo curve is offset** (§3.2) — an expo/EASE_IN tween does not reach its delta
   endpoint (0.999·delta), and expo/EASE_OUT is scaled 1.001 [M].
4. **Integer deltas round** (§3.2) — 2.5→3, 7.5→8 [M].
5. **`play()` does not apply the pose** (§3.7) — a cell that reads the property right
   after `play()` reads the *old* value [M].
6. **Replaying the same animation name is a no-op** (§3.7) — a "restart" cell must
   `stop()` first or play a different name [M].
7. **`stop()` clobbers the animated property with the animation's t=0 value** (§3.7) —
   pre-play values are not restored [M].
8. **DEFERRED method-track calls lag a frame** (§3.8) — pinning "calls during advance"
   requires IMMEDIATE [M].
9. **Crossfade mid-values are step-granularity dependent** (§3.10) — pin only the
   endpoints (w=0 first step, w=1 at t=blend_time) or hard-switch [M].
10. **`is_valid()` on a freed owner is stale for one processing pass** (§3.5) [M].
11. **Frame-coupled counters are modes** (§3.6/§3.11) — `out_uniq=5–6`; pin only the
    trailing `stable=[…]` clauses or the endpoints [M].
12. **A second `AnimationLibrary` under the same name errors**
    (`ERROR: Can't add animation library twice with name:`, `runs/disc-animproc.err`) —
    put all animations in one library [M].
13. **An `AnimationPlayer` that is never added to the tree leaks an ObjectDB instance at
    exit** (WARNING) unless freed — the census arm frees it; a fixture that forgets will
    carry a warning [M].
14. **`position:z_index` is not a valid property path** for `tween_property` (the
    `z_index` int lives on the node, not under `position`) — the engine emits
    `ERROR: The tweened property "position:z_index" does not exist…` and the tween starts
    with no tweeners [M] (discovery).
15. **`mixer_updated` may be dead for script observation** on this build (0 fires across
    the whole arm) — do not build a row on it [M].

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (15 gating, exec-checked)

`corpus/live/r93-scout/author-rows.py.txt` holds `ROWS` (gating), `ROWS_FULL`
(informational) and `EXPECTED_ERRORS`; `python3 verify_rows.py` classifies every row
against every canonical + loadtest receipt with the production `classify_process`
(AST-extracted, segment sha256 `749fa060…` — the same segment r89–r92 pinned):

- **`ROWS` (recommended, gating): 108 receipt checks, `rejected=[]`.**

| case | arm | signature (see file for the exact string) |
|---|---|---|
| `r93_tween_census` | census | full census line (enums/defaults/signals/method counts/cache+capture surface) |
| `r93_tween_interp_value` | tweenval | full line (r91_exact, expo quirk endpoints, clamps, int/vec/color, formula residuals) |
| `r93_tween_interp_grid_a` | tweenval_grid | `PASS … lin … sin … qui … qua … qad …` (5 transitions ×4 eases ×5 t) |
| `r93_tween_interp_grid_b` | tweenval_grid | `expo … ela … cub … cir … bou … bac … spr …` (7 transitions ×4 eases ×5 t) |
| `r93_anim_track_interp` | animtrack | full line (NEAREST/LINEAR/CUBIC two- and three-key, default interp, bezier) |
| `r93_tween_manual_step` | tweenstep | full line (custom_step exactness, completion signals, paused stepper, loops) |
| `r93_tween_chain` | tweenchain | full line (sequential/parallel/interval/callback/method, owner-free, kill) |
| `r93_tween_process_stable` | tweenproc | `stable=[auto_advanced=true,paused_frozen=true,phys_advanced=true,manual_exact=true]` |
| `r93_tween_phys_manual_step` | tweenproc | `phys_manual=[before=1.0,after_step025=2.0]` |
| `r93_anim_seek` | animseek | full line (play/advance/seek/pause/stop/speed/replay/loop/manual-frames) |
| `r93_anim_method_callback` | animmethod | full line (DEFERRED vs IMMEDIATE, disabled track, started/current signals) |
| `r93_anim_blend_finished` | animblend | `finished_010/005/020` lattice (three step granularities) |
| `r93_anim_blend_running` | animblend | `running_from_50 … hard … default_blend_mid … capture` |
| `r93_anim_process_manual` | animproc | `manual=[x=25.0,after3frames=25.0] frozen=[0.0,true,0.0] inactive=[50.0,true]` |
| `r93_anim_process_stable` | animproc | `stable=[manual_frame_frozen=true,…,mixer_updated_zero=true]` |

- **`ROWS_FULL` (informational):** the two full mode-cell lines
  (`r93_tween_process_full`, `r93_anim_process_full`) reject **16/18** — the load-fragile
  frame counters. Use them only in a quiet window or as mode envelopes.

`expected_errors` additions: **none** — every gating arm is `ERROR:`-clean with 0 B
stderr (54/54 canonical, 24/24 loadtest).

Probe file lands at `corpus/fixtures/anim_lattice.gd` (sha256
`6a919ae04d4e7549…`, 689 lines, self-contained `SceneTree` script, battery `--arm=`
convention). Insert the rows ahead of the crash/descendant tail like prior blocks; no
other fixture change is needed.

### 6.2 What to pin and what not to pin

1. **Pin the `PASS anim_lattice …` line (or its stable prefix)** — it carries the arm
   name, so the r88 silent-fallback failure cannot recur.
2. **Pin the pure cells full-line** (census, tweenval, grid, animtrack) — single-valued
   across reps and load.
3. **Pin the manual-clock cells full-line** (tweenstep, tweenchain, animseek, animmethod,
   animblend) — byte-identical under load avg 118.
4. **For the two mode cells, pin the trailing `stable=[…]` boolean clauses** — never the
   frame counters (`idle`/`phys`/`quick`/`mixer_applied`/`auto`/`paused`).
5. **Never pin** mid-blend values, frame counts, `mixer_applied` counts, or
   `caches_total`; pin `caches_delta` (exactly 1 per explicit `clear_caches()`).
6. **Do not pin the r91 receipt without the quirk**: `9.69718754291534` is stable, but a
   pin that assumes `expo = 1−2^(−10t)` is wrong by design (§3.2).

---

## 7. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | the r91 Tween receipt does not reproduce on a fresh process | **REFUTED [A]** — `9.69718754291534` byte-identical 6/6 reps (3 canonical + 3 loadtest) |
| F2 | the expo curve is the textbook `1−2^(−10t)` | **REFUTED [A]** — EASE_IN = `2^(10(t−1))−0.001` (t=1 → 0.999), EASE_OUT = `1.001(1−2^(−10t))` |
| F3 | `interpolate_value` clamps elapsed to [0, duration] | **REFUTED [A]** — `-5.0` at t=−0.5, `15.0` at t=1.5 |
| F4 | integer deltas truncate | **REFUTED [A]** — 2.5→3, 7.5→8 (round) |
| F5 | a paused tween cannot be stepped manually | **REFUTED [A]** — `pause()` + `custom_step` is the exact recipe |
| F6 | `play()` applies the first pose | **REFUTED [A]** — x stays 7.0 until the first advance |
| F7 | replaying the same animation name restarts it | **REFUTED [A]** — `replay_same=[50.0,0.5]`; only a different name restarts |
| F8 | `stop()` restores the pre-play property value | **REFUTED [A]** — resets to the animation's t=0 value (7.0 → 50.0 → 0.0) |
| F9 | method-track calls fire during manual advance by default | **REFUTED [A]** — DEFERRED queues to the next frame; IMMEDIATE fires inside advance |
| F10 | freeing a tween's owner invalidates it immediately | **REFUTED [A]** — `is_valid` true through free + manual step; false at the next processing pass |
| F11 | crossfade mid-values are a pure function of wall time | **REFUTED [A]** — weight `(i−1)/(N−1)`; dt=0.1 vs 0.2 give different mid-values at the same t |
| F12 | `active=false` stops `advance()` | **REFUTED [A]** — `inactive=[50.0,true]` (advance still applies) |
| F13 | `mixer_updated` fires on manual advance | **REFUTED [A]** — 0 fires; `mixer_applied` fires per applied step |
| F14 | `Tween.new()` is constructible | **REFUTED [A]** — hard `ERROR: Tween can't be created directly` |
| F15 | `caches_cleared` is exclusive to `clear_caches()` | **REFUTED [A]** — 1 per explicit call but 11 total across the arm |
| F16 | a MANUAL player still advances on awaited frames | **REFUTED [A]** — `manual_frames=[0.0,0.0]` |
| F17 | a second `AnimationLibrary` with the same name can be added | **REFUTED [A]** — `ERROR: Can't add animation library twice with name:` |
| F18 | `seek(t)` beyond length stops playback | **REFUTED [A]** — clamps to 1.0 and keeps playing |
| F19 | `set_loops(0)` means zero loops | **REFUTED [A]** — infinite (`get_loops_left()=-1`) |

---

## 8. Remaining unknowns / not measured

- **Independent replication is missing.** The one permitted labrat returned
  INCONCLUSIVE (no exec tool in its substrate) — no second seat has reproduced the expo
  law, the crossfade weight law, or the deferred-callback timing. Recommend a verifier
  seat with shell access before any row is admitted.
- **Audio tracks** (`Animation.TYPE_AUDIO`) were not measured; r88 already showed the
  headless Dummy driver is null (`playing=false`), so an audio-track cell is likely
  vacuous.
- **`TYPE_ANIMATION` (nested animation) and `TYPE_BLEND_SHAPE`/3D track types** were not
  exercised (out of the 2D authoring scope).
- **`UPDATE_DISCRETE`/`UPDATE_CAPTURE` and `callback_mode_discrete`** were not latticed
  (only `callback_mode_method`); the discrete path may hold a second timing law.
- **`AnimationMixer.root_node` overrides, `set_audio_max_polyphony`, library
  add/remove/rename edges** were not measured.
- **`Tween.set_pause_mode`/`TWEEN_PAUSE_PROCESS` semantics** were not split (only
  `pause()`/`play()` behaviour).
- **`tween_property(...).set_delay()` interaction with `get_total_elapsed_time`** was
  measured in discovery only (delay consumes time; elapsed includes it; `.from()`
  overrides the start value; `.as_relative()` adds to the current value —
  `runs/disc2-delay.out`) and is not in a frozen row.
- **`AnimationPlayer.speed_scale` negative / `from_end=true` play and
  `play_section`/`play_section_with_markers`** were not measured.
- **Threaded/`run_on_separate_thread`** animation was not tested.
- **Portability**: every value is this host/build/`--headless`/60 tps/GodotPhysics2D;
  the expo/crossfade laws are float32-of-this-build claims.

---

## 9. Host cleanup

- **54 canonical + 24 loadtest + 17 discovery runs (95 Godot launches)**, all
  `--headless`, all `timeout -s KILL`-bounded (30 s bound; none hit), no run left
  running from this seat (the `pgrep` tail in `runs/run_cells.log` shows only concurrent
  lanes: g2d r92/r94/r95 scouts, r89 fold, g3d r92–r100 — none from this seat).
- The loadtest `yes` hogs were cleared (`pkill -x yes`; `load_after` recorded in
  `runs/loadtest/summary.txt`).
- No tracked file written: `git status --porcelain` shows only the concurrent r89-fold
  lane's `corpus/fixtures/run_battery.py` edit and untracked `corpus/live/*` churn.
- `manifest.sha256` (303 lines) covers every artefact under `corpus/live/r93-scout/`.

---

## 10. Evidence index

All under `corpus/live/r93-scout/`; `manifest.sha256` (303 lines) covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| **frozen primary probe, 11 arms** | `probes/anim_lattice.gd` | `6a919ae04d4e7549` |
| discovery micro-probe (10 arms) | `probes/discover.gd` | `f3dee40d294e245f` |
| discovery #2 (7 arms) | `probes/discover2.gd` | `642ff10a4562d846` |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| driver (11 cells, 54 runs) | `run_cells.sh` | in manifest |
| loadtest driver (8 cells, 24 runs, load 104–118) | `run_loadtest.sh` | in manifest |
| analyzer → json | `analyze_r93.py` → `runs/analyze_r93.json` | in manifest |
| author rows + verifier | `author-rows.py.txt`, `make_author_rows.py`, `verify_rows.py` | `07abf597a9c98d6c` / in manifest |
| claim audit (recomputes every headline law) | `audit_claims.py` | in manifest |
| per-cell receipts (54 × 3 files) | `runs/r93_*.{out,err,rc}` | `manifest.sha256` |
| loadtest receipts (24 × 3 files) | `runs/loadtest/` | `manifest.sha256` |
| discovery receipts (17 × 3 files) | `runs/disc-*.{out,err,rc}`, `runs/disc2-*.{out,err,rc}` | `manifest.sha256` |
| receipts summary | `RECEIPTS.md` | in manifest |
