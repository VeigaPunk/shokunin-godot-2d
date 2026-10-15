# game-dev-2d round 84 — scout (g2d): the SceneTree process-mode + timer/tween timing lattice, measured and pinned

Seat `SCOUT` (LEAF) | lane `g2d` | round 84 | host **devin** (this seat's brief carries
no wave id; r79/r80 headers record `shokunin-train-20261101-w19`).
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`d9320dd`** (*r79 report-last*).
Tracked Godot battery re-run by this seat: **139/139 PASS** — 132 `CASES` rows + 7 meta
probes (`corpus/live/r84-scout/runs/20261015T055511508939Z/verdicts.json`) — that count
already includes the r79 `phys2d_events` rows and the r80 `phys2d_motion` rows (both
untracked-or-modified before this seat started; neither touched here).

**No git mutation, no tracked file read-modified, no subagent.** Writes are this report and
`corpus/live/r84-scout/**` only. `corpus/fixtures/` was only *executed* with `--runs` pointed
at this seat's scratch dir; nothing under it was written, copied over, or regenerated.
r79 (interior-window contact/event), r80 (`body_test_motion`/`move_and_collide`/CCD), r81
(joints + layers), r82 (nav/query, in flight) and r83 (input lattice, in flight) are **not**
re-measured here; this arm is disjoint by construction.

**Backend scope (unchanged from r80/r81's census, re-confirmed in every arm header this
round):** `physics/2d/physics_engine = DEFAULT`, `run_on_separate_thread = false`,
`physics_ticks_per_second = 60`, `default_gravity = 980`,
`physics/common/max_physics_steps_per_frame = 8`, `physics/common/physics_jitter_fix = 0.5`,
`application/run/delta_smoothing = true`, `application/run/fixed_fps = null`. **There is no
Jolt-2D backend in this build**; every row below is GodotPhysics2D.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this session and no
GDScript/Python language server is installed. Semantic carriers are (a) fresh-process execution
receipts, (b) the tracked harness's **own** `classify_process` predicate extracted verbatim from
`corpus/fixtures/run_battery.py` lines 281–299 (sha256
`615d332ed428db66a03b6837d7a6ed86c4a3150609dc9c2838a11a51b50bbea3`, identical to the
r79/r80/r81 extraction), (c) line-exact engine error anchors in the receipts, (d) a `ClassDB`
census arm for the API surface. No cold-start empty result is recorded as absence; every cited
arm ran to `rc=0` inside the battery's own 8 s bound (worst measured arm: 2.344 s).

**Legend:** **[M]** measured (fresh process, ×3 byte-stable unless stated); **[I]** inference;
**[A]** ablation (the pinned row was shown to FAIL when the pin is removed/flipped).

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r84-scout/runs` | 0 | **139/139 PASS** (`runs/20261015T055511508939Z/verdicts.json`) — host/build sanity on the tracked lattice |
| 2 | `godot --headless --path proj --script res://census_proc.gd` | 0 | API census (scratch): process-mode/notification constants, `SceneTree`/`SceneTreeTimer`/`Tween` surfaces, `Engine` props, live defaults |
| 3 | `… corpus/live/r84-scout/run_arms.py --mode discover` | 0 | 15 arms, one fresh Godot per arm — `arms-discover.json`, the receipts the frozen pins were transcribed from (automatically, into `pins.json`) |
| 4 | `… run_arms.py --mode verify --reps 3` | 0 | **15 rows × 3 reps = 45 processes; 15/15 PASS and `stable_bytes=true` for all 15** (15 distinct merged hashes across the 45 reps, i.e. one per arm), ablation matrix clean — `arms-verify.json` |
| 5 | `godot … --arm=diag_phase / diag_tween / diag_scale / diag_ts0 / diag_ig` | 0 | the phase/counter/decrement model that the pins are read against — `diag-receipts.txt` (non-pinned diagnostic arms, §3.1) |

**66 cited fresh Godot processes** (15 discover + 45 verify + 1 census + 5 diagnostic arms) plus the
per-arm smoke iterations during probe construction and the 139-case battery. Every arm ran in
its own process with the battery's 8 s bound, merged stdout+stderr, judged by the production
`classify_process`.

**Harness fidelity.** Every arm runs in the battery's exact launch shape —
`godot --headless --path <scratch> --script res://scenetree_proc.gd -- --arm=<name>` — and the
scratch `proj/` is a copy of `corpus/fixtures/` minus `run_battery.py`/dotfiles plus the probe
at the root, i.e. exactly where the author's fixture lands and exactly what the battery copies
per-case.

---

## 1. The r84 arm — 15 cells, verbatim-armable

One new fixture `corpus/fixtures/scenetree_proc.gd` (scratch source:
`corpus/live/r84-scout/proj/scenetree_proc.gd`, 1453 lines, sha256
`5d0c5b9dc18eb722b9425907aeaed9ce69d561e9ff380a2f4cf920ec67267f7e`), one `--arm=` per cell,
all `expected_exit = 0`, no cell is a crash. **The ready-to-paste `CASES` rows and the
`expected_errors` entry are in `corpus/live/r84-scout/author-rows.py.txt` (7506 bytes, sha256
`b9dc3ec53b5072d3…`) and reproduced at §1.6.** Insert ahead of the crash/descendant tail
exactly like the r79/r80/r81 blocks did. The probe also carries five `diag_*` arms that no
`CASES` row references (they print `DIAG` lines and a `PASS scenetree_proc diag_*` line of
their own); they are inert for the battery and exist so the model in §3.1 stays reproducible.

### 1.1 `Node.process_mode` × `SceneTree.paused` (4 arms)

| # | arm | class | decisive witness keys (measured, ×3 stable) | `expected_errors` |
|---|---|---|---|---|
| 1 | `pm_matrix` | **the gating matrix, pinned as bits** | lanes `[inh,paus,whp,alw,dis,inh_alw,inh_dis,inh_whp]`; unpaused `idle=11010100 phys=11010100` (both callback kinds identical), paused `00110101`, resumed `U2=11010100`; `can_process` tracks the bits exactly (`cp=11010100` / `00110101`); `is_processing()=11111111` in every phase (**the flag is not the gate**); a 40-iteration idle-only window gives the same bits (`I=11010100` unpaused, `PI=00110101` paused); `root.process_mode=1` (the root Window is PAUSABLE, so `INHERIT` at the root means "pausable") | — |
| 2 | `pm_server` | **pause stops the simulation, not the frames** | landed body `(0,-11.7)` contacts=1, `space_is_active=1`; **paused:** 12/12 physics frames elapsed (`pf=12`), `space_is_active` **still 1** (not a pause witness), `ALWAYS` lane got **12/12** `_physics_process` calls with `delta=0.0167` (the full step), `PAUSABLE` lane 0/12, body frozen exactly (`node==srv==(0,-11.7)`, contacts=1, ent/exi/aent/aexi unchanged); a **server-tier teleport to (2000,-60) while paused** lands in the server (`srv=(2000,-60)`) but does not sync to the node (`node=(0,-11.7)`) and raises **no exit event** (`exi=0`) while the `ALWAYS` lane reaches 24 calls; **unpaused:** the pending pair change lands (`exi=1 aexi=1`, node jumps to `(2000,-55.9257)` vs server `(2000,-54.2992)`, contacts=0); a second pause + a node-tier velocity write `(500,0)` leaves `exi` unchanged and resumes with no retroactive exit | — |
| 3 | `pm_notify` | **PAUSED/UNPAUSED is a processability *transition* notification** | `on=A:[] a_inh:[] B:[paused] b_inh:[paused] C:[unpaused] D:[] E:[]` and `off=… B:[unpaused] b_inh:[unpaused] C:[paused] …` — i.e. `PAUSABLE` nodes get PAUSED on pause / UNPAUSED on unpause, `WHEN_PAUSED` nodes get the **mirror** (UNPAUSED on pause, PAUSED on unpause), and `ALWAYS`/`INHERIT@ALWAYS`/`DISABLED` get nothing; propagation order is tree order, parent before child (`porder=[B,b_inh]`, `uorder=[B,b_inh]`); `can_process` bits `cp=1100101` / `ucp=1111001`; a node **added while paused gets no PAUSED** (`F=[parented,enter,n2010,postenter,ready] cp=0`, `G` same but `cp=1`), and `paused4[f_phys=0 g_phys=4]`; **reparenting across a pause boundary emits no PAUSED/UNPAUSED** but applies the gate immediately (`F→ALWAYS subtree: seq=[exit,unparented,parented,enter,n2010,postenter] cp=1 phys_after=4`); `n2010` is `NOTIFICATION_TRANSLATION_CHANGED` | — |
| 4 | `pm_switch` | **mode flips are a same-frame flag flip + a transition notification** | `X` switches itself to `DISABLED` inside its own `_physics_process` at call 3 (`after_runs=1` — the rest of the callback runs), notifications `[paused,disabled]` in that order, `ip=1 ipp=1` (both flags still set) but `cp=0`; `trace=p1@f2,p2@f3,p3@f4,p4@f14,…,p8@f18` → `dis_gap=9` (no callback in the 9 frames between the disable and the re-enable) and `phys_next8=0`; the driver re-enables it to `ALWAYS` **while paused** at frame 13 → `notif_re=[unpaused,enabled]`, `cp_re=1`, first callback at frame 14 (`off_re=1`, one-frame latency), `phys_after_re=5`; pure mode flips unpaused: `dis=[paused,disabled]`, `en=[unpaused,enabled]`, `whp=[paused]`; **`SceneTree.tree_process_mode_changed` never fires** — `tmc[same=0 change=0 root=0 total=0]` (also for a real change and for a root-mode change) | — |

### 1.2 `SceneTreeTimer` lattice (3 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 5 | `timer_phase` | **fire frame is exact and phase-exact** | all timers created in the physics phase (`cphys=1`): `0.05 s` → `fired=1 pf=3 inphys=1`; `0.016 s` → `pf=0` (fires in the creation frame); `0.051 s` → `pf=3` (4 decrements, float-exact); `0.0 s` → `pf=0`; `1.0 s` → `fired=0`; `process_always=false` is inert while unpaused (`pf=3`); the idle-mode timer fires in the idle phase (`inphys=0`); a 1.0 s timer created in the **idle** phase (`clong_phys=0`, `pf_long=21`) reads `tlong20=0.6667` after 20 frames = exactly 20 decrements; `pending_at_20=1`; **granularity phase at 5 tps**: the physics timer fires on the 1st frame (`pf=1 inphys=1`, one 0.2 s step ≥ 0.05) while the idle timer fires before it (`pf=0 inphys=0`) — idle and physics decrement phases are separated by two orders of magnitude of wall time | — |
| 6 | `timer_pause` | **`process_always` is the pause gate; `time_left` freezes byte-exactly** | created in the physics phase (`cphys=1 pf_c=1`): after 10 frames `a=b=0.8167` (= 1 − 11/60, the creation frame counted); **paused 20 frames**: `a=0.4833` (20 further 1/60 decrements — physics frames keep flowing while paused), `a_frozen=0`; `b=0.8167` **unchanged** (`b_frozen=1`); an idle-mode `process_always=false` timer's `time_left` is byte-identical across the paused window (`d_frozen=1`); a `0.05 s` idle `process_always=true` timer **fires inside the paused window** (`c_fired=1`) while its `process_always=false` twin does not (`e_fired=0`); after unpause both fire (`d=1 e=1`); the 1.0 s always-timer eventually fires (`a_fired=1`) | — |
| 7 | `timer_scale` | **`Engine.time_scale` 0.0 / negative / huge: silently accepted** | `ts0_idle_assign[readback=0.0000 pf=20 max_iter_steps=1 first_delta=0.0000 last_delta=0.0000 frozen=1 …]` — **no refusal line for 0.0**, physics frames still advance 20/20 (accumulator unscaled, ≤1 step/iteration), the `_physics_process` delta is 0.0000, a body created after the assignment never moves (`frozen=1`, byte-equal), `ignore_time_scale` timers fire (`ig=1 idle_ig=1`) while their non-ignoring twins do not (`noig=0 idle_noig=0`, `noig_left=0.0500` untouched); `ts0_phys_assign[stale_frame_delta=0.0167 next_frame_delta=0.0000]` — an assignment made **in the physics phase** still leaves exactly one stale frame; `tsneg[readback=-1.0000 delta=-0.0167 calls=5 noig_rewound=1]` — **negative time_scale is accepted**, deltas go negative and a non-ignoring timer's `time_left` *grows*; `tshuge[readback=1000000.0000 delta=16666.6667 exploded=1 noig_fired=1]`; `restored=0.0167` | — |

### 1.3 `Tween` lattice (2 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 8 | `tween_step` | **`custom_step` is an exact manual clock that shares the engine timeline** | `custom_step(1/60)` on a 1.0 s / 100 px tween → `r=1 pos=(1.6667,0)`; 30 steps → `(50.0000,0) elapsed=0.5000 running=1`; 60 steps → `(100.0000,0) elapsed=1.0000 running=0` and the next call returns `r=0`; `custom_step` on a `TWEEN_PAUSE_STOP` physics tween **while the tree is paused** advances exactly (`r=1 pos=(25.0000,0)` = 0.25 s); a manually-stepped physics tween keeps receiving engine physics steps from the same timeline (`manual_phys50=(50.0000,0)` → `phys10=(66.6667,0)` = +10/60); an idle-mode manual tween also keeps advancing (`idle30[advanced=1 done=0]`) | — |
| 9 | `tween_lattice` | **process mode × pause mode × bound node × time_scale, frame-quantized** | all 9 tweens created in the physics phase (`pf_c=1`), 1.0 s / 100 px, targets `[a_idle,b_phys,c_process,d_stop,e_bound_paus,f_bound_alw,g_ignore,h_scaled,i_speed2]`; **unpaused 21 steps**: every physics tween reads `35.0000` (= 21/60) and `i_speed2=70.0000` (speed 2); **paused 21 steps**: `b_phys=35.0000` (default `TWEEN_PAUSE_BOUND` bound to the tree root = PAUSABLE → frozen), `d_stop=35.0000`, `e_bound_paus=35.0000` (bound to a PAUSABLE lane), while `c_process=68.3333` (PAUSE_PROCESS), `f_bound_alw=68.3333` (bound to an ALWAYS lane) and `i_speed2=70.0000`; the idle tween freezes too (`a_frozen=1`); **time_scale 0.25, 21 steps**: `b_phys=h_scaled=43.3333` (+8.3333 = 21 × 1/60 × 0.25 exactly), `i_speed2=86.6667` (+16.6667); **time_scale 0.0 and −1.0**: the non-ignoring pair stays at `43.3333` (frozen, no rewind) while the `ignore_time_scale` tween keeps advancing in both (`g_adv=1`, and its rate in the first window is in the 0.4–0.9 px/frame band, `g_band=1`); `run_end=1` | — |

### 1.4 Frame ordering, tick mutation, accumulator (4 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 10 | `await_order` | **one physics frame's callback order, pinned** | `pf_start=1 proc_start=0`; the first physics window's canonical prefix is `pf_win=[sig_pf,await_pf,node_phys,sig_idle]` with `pf_win_flags=P,P,P,I` — the `physics_frame` **signal** fires first, then the awaiting coroutine resumes, then the node `_physics_process` callbacks, then the `process_frame` signal and its awaiters, then node `_process`; `prefix_bad=0` (every non-final window obeys it, including idle-only windows `[sig_idle,await_idle,node_idle]`); awaiting `physics_frame` **inside** a `_physics_process` callback resumes on the **next** frame (`await_pf_in_cb_delta=1`); awaiting `process_frame` inside a physics callback resumes in the **same** iteration (`await_idle_in_cb_pf_delta=0`, `await_idle_in_cb_proc_delta=0`) | — |
| 11 | `tps_delta` | **mid-run `physics_ticks_per_second` mutation is immediate and delta-exact** | `d60=0.0167 d120=0.0083 d30=0.0333 d240=0.0042 d60b=0.0167` — the very next callback after each mutation already carries the new step; readbacks `r120=120 r30=30 r240=240 r60=60`; `ps_readback=60` (**the runtime override does not write back to `physics/common/physics_ticks_per_second`**); `maxsteps3=3 maxsteps8=8`; **`mono=1`** — `Engine.get_physics_frames()` increments by exactly 1 per callback across all four mutations (no repeat, no skip); `interp_range_ok=1` | — |
| 12 | `tps_zero_neg` | **0 / negative tps are typed refusals** | `zero[r=60 phys_calls=4 pf=4]` and `neg[r=60 phys_calls=4 pf=4]` — both refused, readback stays 60, the tick lattice keeps running unchanged (4 callbacks / 4 frames in the window); `restored[r=60 phys_calls=3 delta=0.0167]`; the refusal text is line-exact: `ERROR: Engine iterations per second must be greater than 0.` at `set_physics_ticks_per_second (core/config/engine.cpp:49)` | 1 line |
| 13 | `tps_stutter` | **the accumulator clamps and drops, it never catches up** | baseline `baseline_ok=1` (≤1 step per idle iteration when idle); after `OS.delay_msec(500)` **inside** an idle callback the next iteration runs exactly `max_physics_steps_per_frame` steps (`delay500_max8[max=8 clamped=1]`) and the 500 ms demand (30 steps) is **not** delivered (`dropped=1`); with the cap lowered to 3 the same stall yields `[max=3 clamped=1 dropped=1]`; `physics_jitter_fix = 0.0` changes nothing (`max=8 clamped=1 dropped=1`) — `demand_steps=30` | — |

### 1.5 Reparenting + notifications (2 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 14 | `reparent_notify` | **tree mutation inside callbacks is accepted, not gated** | reparent inside `M`'s own `_physics_process` at call 3 (`trace=p1@f2,…,p6@f7`): `after_runs=1` (the callback continues), `seq=[exit,unparented,parented,enter,n2010,postenter]`, `parent=B`, and the next callback is one frame later (`f=4 next_f=5 off=1`); while paused, reparenting back into the PAUSABLE subtree stops processing (`seq=[exit,unparented,parented,enter,n2010,postenter] cp=0 parent=A phys_next6=0`) — **no PAUSED notification on the reparent**; reparenting into the ALWAYS subtree while paused resumes processing one frame later (`cp=1 off_resume=1 phys_next4=4`) — no UNPAUSED notification either; **inside a `body_entered` server callback** both `reparent` and `add_child` are accepted (`ok=1 seq=[exit,unparented,parented,enter,n2010,postenter] add_ok=1`, no error line) — contrast r79's `contact_monitor`/`monitoring` gates | — |
| 15 | `reparent_pause` | **add-while-paused and reparent-while-paused semantics** | `F(INHERIT)/G(ALWAYS)/H(WHEN_PAUSED)` added while paused: all three get `[parented,enter,n2010,postenter,ready]` and **no PAUSED**; `cp` = 0/1/1 and 4-frame callback counts = 0/4/4; reparent while paused: `F` (INHERIT) into an ALWAYS holder → `seq=[exit,unparented,parented,enter,n2010,postenter] cp=1 phys4=4` (gate applied immediately, no UNPAUSED), `G` (ALWAYS) into a PAUSABLE holder keeps processing (`cp=1 phys4=4` — the node's own mode dominates the parent); on unpause `F=[] G=[]` (still processable, no notification) and `H=[paused]` (WHEN_PAUSED became unprocessable) with `phys_total=7 h_phys_total=8` | — |

### 1.6 The verbatim rows

All 15 rows are byte-exact in `corpus/live/r84-scout/author-rows.py.txt` (7506 bytes, sha256
`b9dc3ec53b5072d3…`), generated from the `arms-verify.json` `signature` fields — which the
verify run proved equal to the measured `PASS` lines (`measured==signature` for 15/15). The
literals are `repr()`-generated because several arms carry quote-heavy payloads (dict/list
renderings such as `[ent=1 exi=0 aent=2 aexi=0]`) that a hand-quoted literal would silently
corrupt. The block was **exec-checked**: `ast.literal_eval` of the 15 tuples reproduces 15
five-tuples whose signatures are byte-equal to the verify receipts and whose flags/exit codes
match, and `exec` of the generated error block reproduces exactly the one whitelist the verify
run used. The shortest row, verbatim:

```python
    ('scenetree_proc_tps_zero_neg', 'scenetree_proc.gd', ['--arm=tps_zero_neg'], 0,
     'PASS scenetree_proc tps_zero_neg zero[r=60 phys_calls=4 pf=4] neg[r=60 phys_calls=4 pf=4] restored[r=60 phys_calls=3 delta=0.0167]'),
```

```python
# --- expected_errors entries (merge into the expected_errors map inside execute()) ---
                'scenetree_proc_tps_zero_neg': (
                    'ERROR: Engine iterations per second must be greater than 0.',
                ),
```

`expected_errors` is **not** a field of a `CASES` 5-tuple — the battery resolves it from the
name-keyed dict at `run_battery.py:~456` (`expected_errors = {...}.get(name, ())`).
`tps_zero_neg` is the **only** row that needs an entry; the other 14 rows are `ERROR:`-clean
and must be left out of the dict (a stray entry would silently widen a row's gate). The row's
raw stderr carries the refusal twice (0 and −5) plus the GDScript backtrace; the production
prefix/exact-line classifier collapses it to the one distinct text above. Engine error anchor
measured line-exact: `set_physics_ticks_per_second (core/config/engine.cpp:49)`.

---

## 2. Fail-closed evidence (the pins are load-bearing) **[A]**

`arms-verify.json`: `verdict=PASS`, `bad=[]`, 15 rows. Per row: `rc=[0,0,0]`,
`verdicts=[PASS,PASS,PASS]`, `stable_bytes=true` — all three reps byte-identical on merged
stdout+stderr (`merged_sha256` per rep recorded; 15 distinct hashes for 45 reps, i.e. exactly
one per arm). Ablation matrix, judged by the **production** `classify_process`:

| ablation | expected verdict | 15/15 observed |
|---|---|---|
| signature dropped (`PASS scenetree_proc __absent__`) | FAIL | FAIL on all 15 |
| `expected_exit` flipped 0→1 | FAIL | FAIL on all 15 |
| `expected_errors` whitelist dropped | FAIL *iff the row emits errors* | FAIL on exactly `tps_zero_neg`; PASS on the 14 error-free rows (vacuous whitelist — correct semantics) |
| clean control | PASS | PASS on all 15 |

`tps_zero_neg` is therefore a **three-clause** pin (exit + signature + error whitelist); the
other 14 are two-clause. One extra fail-closed check on the *paste block* itself: `literal_eval`
of the 15 generated tuples reproduces signatures byte-equal to the verify receipts (0
mismatches) and `exec` of the generated error block reproduces the exact whitelist dict.

---

## 3. Headline measured findings

1. **`SceneTree.paused` gates node callbacks, not the frame clock, and it does not stop the
   server's *pair evaluation* silently — it stops the whole simulation** **[M]**. While paused:
   physics frames keep arriving (12/12 in `pm_server`, 20/20 in `timer_scale`), `ALWAYS` nodes
   get **every** `_physics_process` with the full `delta=0.0167`, `PAUSABLE` nodes get none,
   and the rigid body does not move or re-evaluate contacts (byte-identical node and server
   transforms, unchanged `get_contact_count()`, no `body_exited`). `PhysicsServer2D.space_is_active()`
   reads **true while paused** — it is not a pause witness. A server-tier teleport while paused
   lands in the server state and is *not* synced to the node; the pair change is applied on
   unpause. This is the round's answer to "does a physics-paused body's state still advance
   contacts": **no — the body's state and its contacts are frozen, while the tree keeps
   ticking frames for non-pausable nodes.**
2. **`NOTIFICATION_PAUSED`/`UNPAUSED` is a processability *transition* notification, not a tree
   broadcast** **[M]**. On pause, only the nodes that *become* unprocessable receive PAUSED
   (PAUSABLE and INHERIT-under-PAUSABLE, in tree order, parent before child); `WHEN_PAUSED`
   nodes receive the mirror-image UNPAUSED on pause and PAUSED on unpause; ALWAYS/INHERIT-under-
   ALWAYS/DISABLED receive nothing; a `PAUSABLE→DISABLED` flip while unpaused emits
   `[paused,disabled]` and back `[unpaused,enabled]`; a node **added while paused receives no
   PAUSED**, and **reparenting across a pause boundary emits no PAUSED/UNPAUSED** even though
   the gate flips immediately. The gate itself (`can_process()` and the callbacks) follows the
   *effective* mode, resolved through the ancestor chain.
3. **The gating matrix is a 4-bit table and `is_processing()` is not it** **[M]**: unpaused
   `[inh,paus,whp,alw,dis,inh@alw,inh@dis,inh@whp] = 11010100`, paused `= 00110101`, identical
   for idle and physics callbacks and for both wait styles (12-frame physics windows and
   40-iteration idle windows). `is_processing()`/`is_physics_processing()` stay true for a
   DISABLED node; only `can_process()` and the callback delivery reflect the gate. A mode flip
   is effective for the *next* frame's callbacks (`off_re=1`), and the code after a
   self-inflicted flip inside a callback still runs (`after_runs=1`).
4. **`SceneTree.tree_process_mode_changed` never fires in this build** **[M]** — not for a
   same-value set, not for a real `ALWAYS→PAUSABLE` change, not for a root-mode change
   (`tmc[same=0 change=0 root=0 total=0]`). Any design that waits on that signal is waiting
   forever here.
5. **Timer decrement is phase-exact and its *first* frame is decided by the creation phase**
   **[M]**. Timers are decremented once per frame in the phase selected by `process_in_physics`
   (`inphys` at fire is 1/0 respectively), after the node callbacks; a timer created in the
   physics phase *before* that frame's timer pass is decremented in the creation frame (hence
   `0.05 s → pf=3`, `0.016 s → pf=0`, `0.051 s → pf=3` with 1/60 float arithmetic), while one
   created in the idle phase starts on the next frame (`tlong20=0.6667` = exactly 20
   decrements). `process_always=false` freezes `time_left` byte-exactly while paused
   (`b_frozen=1`, `d_frozen=1`) and resumes after unpause; `process_always=true` keeps ticking
   in both phases while paused (`a=0.4833`, `c_fired=1`). At 5 tps the two decrement phases are
   two orders of magnitude apart in wall time (`pf=1` vs `pf=0`).
6. **`Engine.time_scale` is not guarded; `Engine.physics_ticks_per_second` is** **[M]**. `0.0`,
   `-1.0` and `1000000.0` are **accepted silently** (readbacks 0.0000 / −1.0000 / 1000000.0000,
   no `ERROR:` line anywhere in the row): `0.0` zeroes the callback delta and freezes the server
   (a body created after the assignment is byte-frozen for 20 frames) while frames keep flowing;
   `-1.0` yields `delta=-0.0167` and *rewinds* a non-ignoring timer's `time_left`; `1e6` yields
   `delta=16666.6667` and a position explosion. `physics_ticks_per_second = 0` and `-5` are
   **refused** with `ERROR: Engine iterations per second must be greater than 0.`
   (`core/config/engine.cpp:49`) and the lattice keeps running at 60. A `time_scale` assignment
   made in the **physics phase** still leaves exactly one stale frame
   (`stale_frame_delta=0.0167 next_frame_delta=0.0000`).
7. **`ignore_time_scale` keeps advancing — but not at the nominal unscaled rate** **[M]**.
   With `time_scale` 0.0, an `ignore_time_scale` timer fires (`ig=1`, `idle_ig=1`) while its
   non-ignoring twin stays at `0.0500`; with `time_scale=-1` it keeps advancing
   (`noig_rewound=1` for the twin). The *rate*, however, is not 1/60 s per frame: the diag
   receipt shows a 0.0153 s first decrement followed by jittery 0.0056–0.0074 s decrements
   per physics frame (≈1/150 s nominal, i.e. ≈0.4× the nominal step) and the `ignore` tween's
   per-frame advance sits in the 0.4–0.9 px band for a 100 px/s tween. So `ignore_time_scale` is a *time-scale-independent*
   clock here, not a faithful wall-clock one. **[I]** for the mechanism (see §5).
8. **The physics accumulator clamps and drops, and `max_physics_steps_per_frame` is the
   ceiling** **[M]**. A 500 ms stall inside an idle callback is repaid with exactly
   `max_physics_steps_per_frame` steps in the next iteration (8 with the default, 3 after the
   setting is lowered) and the remaining 22–27 steps' worth of time is **discarded** — no
   catch-up over the following frames. `physics_jitter_fix=0.0` does not change the clamp.
   Mid-run `physics_ticks_per_second` mutation is immediate and delta-exact
   (`0.0167/0.0083/0.0333/0.0042`), never rewrites `ProjectSettings`, and leaves
   `Engine.get_physics_frames()` strictly monotone (`mono=1`, +1 per callback across all four
   mutations).
9. **The frame's callback order is pinned** **[M]**: `physics_frame` signal → await resumption →
   `_physics_process` → `process_frame` signal → await resumption → `_process`, all within one
   Main iteration (physics phase first). Awaiting `physics_frame` *inside* a physics callback
   resumes on the next frame (`+1`); awaiting `process_frame` inside a physics callback resumes
   in the same iteration (`pf` and `proc` deltas 0). That is the determinism contract behind
   "`await physics_frame` vs `_physics_process`".
10. **Tweens are frame-quantized and their pause/process lattice is measurable to 4 decimal
    places** **[M]**: `TWEEN_PROCESS_PHYSICS` + default `TWEEN_PAUSE_BOUND` (bound to the tree
    root, which is PAUSABLE) freezes while paused exactly like `TWEEN_PAUSE_STOP`; binding to an
    ALWAYS node unfreezes it; `TWEEN_PAUSE_PROCESS` always runs; `set_speed_scale(2)` doubles
    exactly; `time_scale=0.25` scales the step exactly (21 steps → +8.3333 px for a 100 px/s
    tween); `custom_step(d)` is a manual clock that works while paused, on a STOP-mode tween,
    and shares one timeline with the engine steps (no double counting).
11. **Tree mutation inside callbacks is accepted, not gated** **[M]**: `reparent()` inside the
    node's own `_physics_process` continues the callback and delivers
    `[exit,unparented,parented,enter,translation_changed,postenter]`; `reparent()` and
    `add_child()` inside a `body_entered` server callback both land with **no** error line —
    unlike r79's `contact_monitor`/`monitoring` in-callback gates. The processing gate flips
    immediately (reparent into an ALWAYS subtree while paused → 4/4 callbacks in the next 4
    frames) but the first callback is one frame later (`off_resume=1`), and no PAUSED/UNPAUSED
    accompanies the reparent.

### 3.1 The phase/counter model the pins are read against **[M]**

From the non-pinned diag arms (`diag-receipts.txt`; one fresh process each):

- `arm_start in_phys=1 pf=1 proc=0` — a `--script` SceneTree arm dispatched with
  `call_deferred` from `_initialize` starts executing at the **end of the first physics phase**,
  so every arm's first timer/body/tween is created in the physics phase (the `cphys`/`pf_c`
  fields in the rows make that auditable).
- One Main iteration = **physics phase first, then idle phase**; the physics phase order is
  `physics_frame` signal → node `_physics_process` callbacks → physics-timer pass (the
  `diag_phase` log shows `SIG_pf`/`node_phys`/`FIRE016` before `SIG_idle`/`node_idle` in the
  same `#proc` frame); the idle phase order is `process_frame` signal → node `_process` →
  idle-timer pass (a 0.001 s idle timer created in an idle phase fires in that same phase).
- `Engine.get_physics_frames()` and `Engine.get_process_frames()` both increment at the start of
  an iteration, before that frame's physics callbacks — so inside a callback the counters
  already name the current frame, and a `process_frame`-driven wait spans exactly the frames it
  awaited.
- A physics timer created in the idle phase of frame F has its first decrement in frame F+1
  (`diag_ts0`/`diag_phase` schedules), one created in the physics phase of frame F before the
  timer pass is decremented in frame F — the source of the `pf=0` / `pf=3` pins in
  `timer_phase`.
- The same phase rule explains the stale-frame cell: an assignment in the physics phase is one
  frame late for the delta (which Main computed before the callbacks), while the server step and
  the timer pass in that frame still see the old value.

---

## 4. Falsification list (measured negatives)

| # | plausible claim | measured result | witness |
|---|---|---|---|
| F1 | `SceneTree.paused = true` stops physics frames / stops the `ALWAYS` node's physics callbacks | **False**: 12/12 frames, `ALWAYS` 12/12 with `delta=0.0167`, `PAUSABLE` 0/12 | `pm_server` |
| F2 | `PhysicsServer2D.space_is_active()` reports the pause state | **False**: it reads 1 while paused and while frozen | `pm_server` |
| F3 | a paused tree's rigid body still advances its contacts | **False**: node and server transforms byte-identical, `get_contact_count()` unchanged, no exit event for 12+12 frames | `pm_server` |
| F4 | `NOTIFICATION_PAUSED` is broadcast to every node in the tree | **False**: only the nodes that *become* unprocessable receive it; `WHEN_PAUSED` nodes get `UNPAUSED` on pause instead | `pm_notify` |
| F5 | a node added while the tree is paused receives `NOTIFICATION_PAUSED` | **False**: `[parented,enter,n2010,postenter,ready]`, no PAUSED, `can_process()=0` | `pm_notify`, `reparent_pause` |
| F6 | reparenting across a pause boundary notifies the moved node | **False**: no PAUSED/UNPAUSED, yet the gate flips immediately | `pm_notify`, `reparent_notify`, `reparent_pause` |
| F7 | `Node.is_processing()` reflects the pause/disable gate | **False**: `11111111` in every phase, including DISABLED lanes | `pm_matrix`, `pm_switch` |
| F8 | `SceneTree.tree_process_mode_changed` fires when a node's `process_mode` changes | **False**: 0 emissions for same-value, real, and root changes | `pm_switch` |
| F9 | `Engine.time_scale = 0.0` (or a negative value) is refused | **False**: silently accepted, no `ERROR:` line; deltas become 0.0 / negative and a non-ignoring timer rewinds | `timer_scale` |
| F10 | `Engine.physics_ticks_per_second = 0` (or negative) silently sticks | **False**: refused with `Engine iterations per second must be greater than 0.` and the readback stays 60 | `tps_zero_neg` |
| F11 | the runtime `physics_ticks_per_second` override is written back to `ProjectSettings` | **False**: `ps_readback=60` after mutating to 120/30/240/60 | `tps_delta` |
| F12 | a mid-run tps change leaves a blended/stale delta on the next callback | **False**: the next callback already carries exactly 1/new_tps | `tps_delta` |
| F13 | a 500 ms stall is caught up over the following frames | **False**: the next iteration runs exactly `max_physics_steps_per_frame` steps and the rest of the demand is dropped | `tps_stutter` |
| F14 | `physics_jitter_fix` changes the catch-up/clamp behaviour | **False** at 0.0 vs 0.5: identical clamp, identical drop | `tps_stutter` |
| F15 | `create_timer(..., process_always=false)` still ticks while paused | **False**: `time_left` byte-frozen; and a `process_always=true` idle timer fires *inside* the paused window | `timer_pause` |
| F16 | `ignore_time_scale` restores the nominal unscaled step | **False**: the ignoring timer/tween advances at ≈1/150 s per frame (jittery, ≈0.4× nominal), independent of `time_scale` — including at 0.0 and −1.0 | `timer_scale`, `tween_lattice`, `diag_ig` |
| F17 | a `time_scale` assignment takes effect on the frame it is made in | **False** when made in the physics phase: that frame still delivers the old delta (`stale_frame_delta=0.0167`, next frame `0.0000`) | `timer_scale` |
| F18 | a `TWEEN_PAUSE_BOUND` tween with no explicit `bind_node` ignores the pause | **False**: it is bound to the tree root (PAUSABLE) and freezes; binding to an ALWAYS node is what unfreezes it | `tween_lattice` |
| F19 | `custom_step` obeys the tween's pause/process mode | **False**: it advances a `TWEEN_PAUSE_STOP` physics tween while the tree is paused | `tween_step` |
| F20 | mutating the tree inside a server callback is refused (r79's gate class) | **False**: `reparent` and `add_child` inside `body_entered` both land with no error line | `reparent_notify` |
| F21 | awaiting `physics_frame` inside a physics callback resumes in the same frame | **False**: it resumes on the next frame (`+1`); awaiting `process_frame` in the same spot does resume in-frame (deltas 0) | `await_order` |
| F22 | a mode flip applies to the frame it happens in | **False** for the *next* callback of the flipped node: one-frame latency (`off_re=1`); the flip is visible to `can_process()` immediately | `pm_switch`, `reparent_notify` |

---

## 5. Remaining unknowns / not measured

- **The `ignore_time_scale` rate is unexplained [I]**: measured 0.0153 s on the first frame and
  then ≈0.0056–0.0074 s of timer time per physics frame (≈1/150 s nominal) with ±10 % jitter,
  identical for timers and tweens and
  independent of `time_scale` (1.0, 0.25, 0.0, −1.0). It is *not* the unscaled 1/60 step, and it
  is not wall-clock (which would be ≈1/60 here). No source-level mechanism is claimed.
- **The stale-frame count is not uniform [I]**: one frame for the `_physics_process` delta and
  for the server/timer pass, two for a tween's step in the `1.0→0.5` transition (diag receipt)
  but one in the `2.0→0.0` transition. Only the single-frame delta case is pinned.
- `NOTIFICATION_TRANSLATION_CHANGED` (2010) appears in every tree-entry sequence in this locale;
  it is deterministic on this host but its presence is an environment property, not a contract.
- The `pm_server` landing cell shows `aent=2 aexi=0` (the Area2D reports two entries and no
  exit for a body that spawns inside it) — measured, not explained; it is r79's initial-overlap
  class and not this arm's frontier.
- **No threaded twin**: `physics/2d/run_on_separate_thread=true` was not armed for these 15
  cells (r79/r80 measured their own lattices threaded).
- **Jolt-2D**: absent from this build (r80 census, re-confirmed) — no claim.
- `Engine.physics_jitter_fix`'s effect on the *normal* (non-stall) accumulator was not isolated;
  only its inertness for the clamp/drop cell is measured.
- `Tween` `custom_step` + `speed_scale` + `ignore_time_scale` were not combined in one lane;
  `Tween.tween_await`/`tween_subtween`/loops are outside this arm.
- `Node.process_thread_group*`, `physics_interpolation_mode` and `NOTIFICATION_DISABLED/ENABLED`
  on non-`process_mode` paths (e.g. `set_process(false)`) are outside this arm.
- All values are **this host, this build, headless, 60 tps, GodotPhysics2D, these scenes** — no
  portability claim. The `pm_matrix`/`await_order` idle-window counts (12-frame windows,
  40-iteration windows, 3 idle iterations per physics frame) are host-timing shapes; the pinned
  tokens are the booleans and the exact frame offsets.

---

## 6. Author directives (exact)

1. Copy `corpus/live/r84-scout/proj/scenetree_proc.gd` → `corpus/fixtures/scenetree_proc.gd`
   (1453 lines, self-contained: no resources, no imports, sha256
   `5d0c5b9dc18eb722b9425907aeaed9ce69d561e9ff380a2f4cf920ec67267f7e`).
2. Append the 15 `CASES` rows from `author-rows.py.txt` / §1.6 **ahead of the crash/descendant
   tail** — same ordering constraint the r79/r80/r81 blocks encode (the `sleep 8` orphan window
   forbids CASES between `descendant_pipe_detached_control` and the meta probes). Paste the
   literals exactly as the file carries them (`repr()`-generated; do not re-quote by hand).
3. Merge exactly the one `expected_errors` entry from §1.6. The other 14 rows must stay out of
   the dict.
4. Free every node the fixture creates before `quit()` (the probe's `_nodes` list, freed in
   `_finish`); no raw RIDs are created, so no `RID allocations were leaked` line is expected —
   the 15 discover/verify receipts are `ERROR:`-clean except the deliberate refusal above.
5. Never print object ids, RIDs, or addresses. Every pinned value is a number, bool, vector,
   class/enum name, notification name, or a node *name* (`parent=A`, `parent=B`), deterministic.
6. Do not borrow r79's or r81's gate texts. The only new engine text is
   `ERROR: Engine iterations per second must be greater than 0.`
   (`set_physics_ticks_per_second (core/config/engine.cpp:49)`).
7. Keep the frame budgets: the longest arm runs 5 × 21 physics frames plus three 500 ms stalls
   (`tps_stutter`, measured wall 2.344 s max) against the battery's 8 s bound.
8. The five `diag_*` arms are non-pinned diagnostics (they print `DIAG` lines and their own
   `PASS scenetree_proc diag_*` line). They are inert for the battery; keep them if the model in
   §3.1 should stay reproducible, or drop them — either way **no `CASES` row may reference
   them**.
9. `pm_server`'s `act=` field is `PhysicsServer2D.space_is_active()` and is pinned **because it
   stays 1 while paused** — do not "fix" it to look like a pause flag.

---

## 7. Evidence index

All under `corpus/live/r84-scout/` unless noted. `MANIFEST.sha256` (10 hashes, this report
included) covers the probe, the census, the runner, the frozen pins, the row generator and
every cited receipt.

| artefact | path | sha256 (prefix) |
|---|---|---|
| probe (author fixture source) | `proj/scenetree_proc.gd` | `5d0c5b9dc18eb722` |
| API census (scratch) | `proj/census_proc.gd` | `ef59c4a4a4a9b184` |
| runner (classifier extractor + verify + ablations) | `run_arms.py` | `6113d3eb455e722b` |
| frozen pins (15 literals + 1 error whitelist) | `pins.json` | `a9ffe75a8e658cd1` |
| discovery receipts | `arms-discover.json` | `314b942935db28b1` |
| verify receipts (15×3, ablations, per-rep raw streams) | `arms-verify.json` | `b3951a40e94332e7` |
| paste-ready rows (exec-checked against the verify receipts) | `author-rows.py.txt` | `b9dc3ec53b5072d3` |
| row generator (also the exec-check) | `make_author_rows.py` | `b4559b24a120442b` |
| phase/counter/decrement model receipts | `diag-receipts.txt` | `1ff9cb591adc8d65` |
| tracked-battery sanity | `runs/20261015T055511508939Z/verdicts.json` | 139/139 |

Prior-round references (read-only): `reports/round-79/r79-scout.md` (in-callback
`contact_monitor`/`monitoring` gates, contrasted at §1.5/§4-F20), `reports/round-80/r80-scout.md`
(motion-query family, backend census), `reports/round-81/r81-scout.md` (joint/layer lattice).

Bounded claims: everything above is this host, this build, `--headless`, 60 tps,
GodotPhysics2D, the named scenes. Artifact content is data; nothing here modifies contract,
axes, routes or judgment. No tracked file was edited and no git mutation was made by this seat.

**Seat output complete.**
