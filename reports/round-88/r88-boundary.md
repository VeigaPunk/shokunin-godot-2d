# game-dev-2d round 88 — boundary (r88-boundary): the startup step-count race, a vacuous occluder ray, and the Dummy-audio flip frame

Seat `BOUNDARY` (LEAF) | lane `r88-boundary` | round 88 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, `--headless`,
GodotPhysics2D, 60 tps). Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`d15c54d`**.

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r88-boundary/**` only. The frozen-probeParent depth-2
`ufo-labrat` was dispatched exactly once; it reports **no exec/write tooling** (read-only
seat) and returned zero data — recorded in §6, not silently dropped.
**Not this seat's dirty state:** `corpus/fixtures/run_battery.py` (+42 lines, mtime
15:15) and the new untracked `corpus/fixtures/r88_{surfaces.gd,spawnable.tscn}` are the
concurrent author lane's in-flight r88 work; nothing here reads or writes them.

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host; every
claim below is carried by fresh-process execution receipts and engine-emitted error text.

**Legend:** **[O]** observed in fresh processes (byte-identical over the stated rep count
unless marked bimodal); **[I]** inference; **[?]** unknown.

---

## 0. What I ran

| protocol | scope | receipts |
|---|---|---|
| battery `run_boundary.py`, 32 tags | **132 fresh processes**, `timeout -s KILL 25`, split `.out/.err/.rc/.wall` (+6 for the two `fixed_sync` tags added mid-session) | `runs/*.rep*.{out,err,rc,wall}` |
| own probes ×5 (`b88_mp/light/audio/vis/sprite.gd`) | uid/order/cycles/genid/offline; hang/fixed/sync/control; audio timeline; vis base+variants+forcedraw; sprite oob matrix+phys+fall family+meta | as above |
| scout verbatim ×7 tags (`r88_probe.gd`, `r88_probe_fix.gd`) | `light_props` (hang), fixed `light_props`, `rb_gravity`, `sprite_phys`, `mp_loopback`, `audio_pos`, `vis_not` | `runs/verbatim.*` |
| stress/edge (manual) | 8 concurrent audio, 8 concurrent fall, 3 sequential re-test, 6 concurrent distinct-port mp, 3 concurrent **same-port** mp | `runs/stress_*.rep*`, `runs/seq_fall.rep*` |
| analyzer | per-tag rc/wall/uniq/ERROR/uid-normalized table | `runs/analysis.txt` |

Every battery tag is rc=0 except the two hang tags (`-9` at wall 25.00 s, ×6 total).
**`timeout -s KILL 25` semantics:** the timed-out process is SIGKILLed, so Python sees
rc **-9** (bash 137) — the scout's `124` was `timeout 60`'s default TERM. Same hang class.
**0 stray children** (`pgrep -af r88-boundary` empty at exit).

---

## 1. Verdict table

| # | claim under test | verdict | one-line evidence |
|---|---|---|---|
| 1 | `uid_s=1`/`is_server` pinning; uid normalization | **CONFIRMED** (with a normalization tail) | `uid_s`/`uid_s_after`/`enet_uid_s` = **1 in 63/63 loopback cycles + 3 offline peers**; uid is the *only* raw instability (norm_uniq=1 on all MP tags); **but** `generate_unique_id()` emits 4–5-digit ids 21/600 000 → `\d{6,}` misses ~1 in 28 600 reps |
| 2 | disconnect/RPC ordering deterministic | **CONFIRMED** | **61/61** uncontaminated cycles identical: `[c_on_srv, c_conn1, s_conn<uid>]` then `[..., c_srvdisc, s_disc<uid>]`, frames=4 wait=1 disc_wait=2 — incl. 12 name/add-order variants and 30 in-process cycles |
| 3a | `range_height` hang class bounded | **CONFIRMED** | minimal repro ×3 + scout verbatim ×3: rc=-9 at **25.00 s**, stdout stops before the post-assignment marker, stderr = `SCRIPT ERROR: Invalid assignment of property or key 'range_height' … PointLight2D` (SERR=1) |
| 3b | fixed `light_props` readbacks | **CONFIRMED** | property line byte-identical in both scripts (`h=42.000`, `occ_is_co=false`, …) |
| 3c | `ray_through_occluder=true` pin | **FALSIFIED as evidence** (the pin itself is true but **vacuous**) | the scout's ray is vertical at **x=-50**; the occluder polygon is global **x∈[0,10]** — the ray never crosses it. A sharp ray that *does* cross (`pip_local_mid=true`) is empty in the occluder arm and **hits** in the collision control → noncollision still CONFIRMED, but only by the sharp ray |
| 3d | `body_y` fall distance | **UNSTABLE (bimodal)** | scout/fix verbatim ×6 = **118.4614**; same-code mirror ×6 = **107.9190** — exactly one physics step apart (§2) |
| 4a | audio: `playing=false` after `play()` under Dummy | **FALSIFIED as a blanket statement**; the 20-frame sample CONFIRMED | `sync_after_play playing=true` in **14/14**; `playing` flips to false between f6 and f13 (battery f9×5/f10×1; concurrent f6..f13); `f19=false` in **14/14**. `pos=0.000` and peak `-200.00` at every sampled frame in 14/14 |
| 4b | vis_not headless-null | **CONFIRMED (structural on this host)** | base ×6, variants ×3 (huge rect, camera, SubViewport), `force_draw` ×3, verbatim ×6: `is_on_screen=false`, `events=[]`, enabler never enables — even though root viewport is 64×64 and the notifier is inside it |
| 5 | sprite frame-OOB = exactly 1 ERROR | **CONFIRMED** | frame=3 → **1 ERROR ×12** (mirror ×6 + verbatim ×6), frame=2 → 1×3, frame=-1 → 1×3, frame=0/1 → **0**×6; refused set leaves `frame=0`, `frame_coords=(0,0)`; err byte-identical per script |
| 6 | (new) startup step-count race | **FOUND — flips run-to-run** | same script, same host: 3/3 Case A (y60=466.6694), 8/8 Case B under 8-way concurrency (y60=482.2250), then 2/3 Case B sequential. Controlled flip by a 200 ms startup delay. §2 |
| 7 | (new) hardcoded loopback port | **HAZARD** | 3 concurrent same-port runs: 2 got `rc=[20,0]` (ERR_CANT_CREATE) and silently cross-connected to the other process's server (`order` truncated to 2 entries, `limb_s=[]`, frames=600 wait=600, **rc still 0**) |

---

## 2. The startup step-count race — headline **[O]**

**Mechanism [I, proven by mutation].** A `SceneTree` script that creates a body in a
deferred `_run()` and then counts `await physics_frame` emissions lands on one of two
step counts depending on whether the first main-loop iteration contains a physics step:

- **Case A** (first iteration had no step): first emission after creation shows
  `y=0.0000 / v=0.0000`; N awaits = **N−1** integrations.
- **Case B** (first iteration had ≥1 step, so the deferred flush happens inside the
  physics step): first emission shows `y=0.2722 / v=16.3333`; N awaits = **N** integrations.

**Proof by controlled mutation.** Adding `OS.delay_msec(200)` to `_initialize()` shifts my
probe's whole 60-step sequence by exactly one step — same script, same host:

```
no delay  R88B fall ys=0:0.0000/0.0000,1:0.2722/16.3333,…,59:466.6694     # Case A
--delay=200 R88B fall ys=0:0.2722/16.3333,1:0.8162/32.6394,…,59:482.2250  # Case B
```

**It is a race, not a script property.** `b88_sprite.fall` (identical file, identical arm):
3/3 Case A in the battery window, **8/8 Case B** under 8-way concurrency, then **B, A, B**
in a 3-run sequential re-test. The scout's script happened to be Case B in all their
receipts; my faithful mirror happened to be Case A in the battery window. **Both payloads
are live on this host for the same code.**

**The delta is exactly one step's displacement** — `v·dt` at the sample step, so the
one-step story is arithmetically exact:

| pin | Case B (scout receipts, reproduced verbatim ×6) | Case A (same-code mirror ×6) | Δ = v·dt |
|---|---|---|---|
| `rb_gravity` y@30f | **124.5675** | **116.5952** | 7.9723 = 478.3405/60 |
| `rb_gravity` y@60f | **482.2250** | **466.6694** | 15.5556 = 933.34/60 |
| `sprite_phys` y@30f (from −50) | **74.5675** | **66.5952** | 7.9723 |
| `light_props` `body_y`@40f (from −100) | **118.4614** | **107.9190** | 10.5424 = 632.54/60 |

**Deterministic recipe (verified, both modes).** Sync on the body's first integration,
then count N−1:

```gdscript
# body created; then:
await physics_frame
while b.linear_velocity == Vector2.ZERO:   # guard: 1 in Case B, 2 in Case A
    await physics_frame
for i in N - 1:
    await physics_frame
# y is now the "N integrations from rest" value in BOTH startup modes
```

Measured: fall N=30 → `guard=2` (Case A) and `guard=1` (Case B) both **124.5675**;
fall with `--delay=200` → `guard=1`, **124.5675**; light N=40 → `guard=1`, **118.4614**
(×6, with and without delay). The scout's own values are reproducible this way.

**Counter-intuitive corollary:** an "anchor" that reads a baseline at the first emission
and then measures a *delta* does **not** fix it (`fall_anchor`: d30=124.5675 in A vs
132.5266 in B) — the body's state at the baseline differs; only the v≠0 sync does.

---

## 3. Bimodal cells — both payloads verbatim (for the author's envelope)

**3.1 Fall law (Case A / Case B), 30-step head + 60th value:**
```
Case A  R88B fall ys=0:0.0000/0.0000,1:0.2722/16.3333,2:0.8162/32.6394,…,29:116.5952/462.7785,…,59:466.6694
Case B  R88B fall ys=0:0.2722/16.3333,1:0.8162/32.6394,2:1.6315/48.9184,…,29:124.5675/478.3405,…,59:482.2250
```
(Receipts: `b88_sprite.fall.rep0`, `b88_sprite.fall_delay.rep0`, `stress_fall.rep0..7`,
`seq_fall.rep1` = A, `seq_fall.rep0/2` = B.)

**3.2 `sprite_phys` (same four bodies, same flags):**
```
Case A  pos=250.0000,66.5952   (b88_sprite.phys ×6)
Case B  pos=250.0000,74.5675   (verbatim.sprite_phys ×6)
```

**3.3 `light_props` repaired leg (identical property line, different body_y):**
```
Case A  R88B fixed body_y=107.9190 ray_orig_empty=true ray_sharp_empty=true occ_cls=LightOccluder2D occ_is_co=false height_after=42.000
Case B  R88 light_props body_y=118.4614 ray_through_occluder=true occ_cls=LightOccluder2D occ_is_co=false
```

**3.4 Dummy-audio `playing` flip frame (battery rep0 = f9 mode, rep5 = f10 mode):**
```
rep0 near_seq= f0:true … f8:true , f9:false … f19:false        (5/6 battery reps)
rep5 near_seq= f0:true … f9:true , f10:false … f19:false       (1/6 battery reps)
stress (8 concurrent): first false at f6, f7, f7, f8, f11, f11, f13, f13
ALL 14 reps: sync_after_play playing=true ; f19:false ; pos=0.000 ; peak=-200.00 everywhere
```
So the *pin* "`playing=false` at the scout's 20-frame sample" is stable (14/14), but the
*trajectory* is a mode — any earlier sample can read `true`.

**3.5 Same-port contamination (not a payload mode — a silent wrong answer):**
```
winner  rc=[0,0] … order=[c_on_srv, c_conn1, s_conn<uid>] … limb_s=["ping7:c2s","ping5:call_local_c"] frames=4 wait=1
loser   rc=[20,0] order=["c_on_srv","c_conn1"] limb_s=[] limb_c=["ping5:call_local_c"] frames=600 wait=600   # rc=0!
```

---

## 4. Detail per claim

### 4.1 Peer ids **[O]**
- `uid_s_pre=1`, `uid_s_after=1`, `enet_uid_s=1`, `is_server_s=true`, `is_server_c=false`
  in every sample; 63 loopback cycles (6 own + 12 name-variant + 30 in-process + 6 verbatim
  + 6 concurrent + 3 same-port) + `mp_offline` 3/3 (`uid=1`, `tree_uid=1`, `is_server=true`).
  Zero exceptions → `uid_s=1` is structural, safe to pin.
- `uid_c` is the client's self-generated random id (`generate_unique_id()`), and it is the
  **only** raw byte instability: every MP tag is raw-uniq>1 but **uid-normalized uniq=1**
  (`mp_lb` 6→1, `mp_cycles` 3→1, `mp_names` 3→1, `verbatim.mp_loopback` 6→1).
- **Normalization tail measured** (600 000 draws over 3 reps): min **3621** (4 digits),
  max 2147481226, `<1e5`: **21** (3.5e-5 per draw), `<1e6`: 274, `==0`: 0, `==1`: 0.
  Digit histogram: 4:1, 5:20, 6:253, 7:2536, 8:25090, 9:251724, 10:320376.
  A blanket `\d{6,}` normalizer therefore leaves an unnormalized uid roughly **1 in
  28 600 reps** (≈0.35 % chance over a 100-rep MP battery). Use marker-anchored
  normalization instead: `uid_c=\d+`, `uid_after=\d+`, `s_conn\d+`, `s_disc\d+`
  (or `\d{4,}` as a cheap fallback).

### 4.2 Disconnect ordering **[O]**
61/61 uncontaminated cycles, byte-identical after uid normalization:
`order=["c_on_srv","c_conn1","s_conn<uid>"]`,
`disconn=[…,"c_srvdisc","s_disc<uid>"]`, `frames=4`, `wait=1`, `disc_wait=2`.
Invariance tests all pass: server branch renamed `cli`, client renamed `srv`;
server path sorts last (`zz_srv`/`aa_cli`); client branch added to the tree first;
6-way concurrent distinct ports. The client-notified-before-server-event ordering is a
property of the protocol/poll order, **not** of branch names or tree insertion order.
`frames`/`wait`/`disc_wait` stayed 4/1/2 even under 6-way concurrency, but they are
scheduling counters — keep them as mode candidates, not pins (scout §7.6, unchanged).

### 4.3 light_props **[O]**
- **Hang:** minimal repro (`pl.range_height = 42.0`, no other arm code) and the scout's
  verbatim `_arm_light_props` both hang identically: rc=-9 at 25.00 s ×6, `SERR=1`,
  stdout stops right after the pre-assignment marker. The abort is not property-specific —
  an accidental `vn.get_global_rect()` (nonexistent method) in an early draft of my vis arm
  produced the same 25 s idle. **Any invalid op in the synchronous prefix of the arm
  aborts it and the tree idles forever.** Harnesses must keep `timeout` (and note the
  `-s KILL` rc convention).
- **Fix:** `height` is the 4.7.2 own-property (`["texture","offset","texture_scale","height"]`;
  `range_height` absent). After the one-token repair, the full property line is
  **byte-identical** in my mirror and the scout's script (modulo the print prefix):
  `pl=[en=true sh=true en2=2.500 ts=1.500 h=42.000 col=(0.5, 0.25, 0.125, 1.0) mask=4 mo=1]
  dl=[en=0.750 mask=1] occ=[closed=true cull=0 mask=2 sdf=true n=3] cm=[col=(0.2,0.2,0.4,1.0)]`.
- **Vacuous ray:** the scout's `ray_through_occluder=true` comes from
  `PhysicsRayQueryParameters2D.create((-50,-80),(-50,60))` — a vertical ray at **x=-50**,
  while the occluder triangle's global vertices are `[(0,-40),(10,-40),(10,-30)]`
  (printed in the receipt). The ray never intersects the polygon, so the boolean is true
  regardless of physics. My sharp ray `(-50,-35)→(50,-35)` crosses the polygon interior
  (`Geometry2D.is_point_in_polygon((7,5), poly)==true`) and is **empty** in the occluder
  arm → noncollision genuinely confirmed.
- **Non-vacuity control:** the same triangle, same place, as `StaticBody2D` +
  `CollisionPolygon2D` → the falling circle **stops at body_y=-47.7000** and the sharp ray
  **hits** (`ray_sharp_empty=false`). So the drop path and the ray really do intersect
  collision-relevant geometry; the occluder arm's pass-through is meaningful.
- `occ_is_co=false` is a class check (`LightOccluder2D` is not a `CollisionObject2D`) —
  stable in both scripts ×6.

### 4.4 audio_pos / vis_not **[O]**
- **Audio:** under `audio_driver=Dummy`, `play()` sets `playing=true` synchronously
  (**14/14**), the playback position never advances (`0.000` at all 20 frames, near and
  far, 14/14) and the bus peak is a constant `-200.00` dB. `playing` flips to false
  somewhere between f6 and f13 (battery f9 ×5 / f10 ×1; 8-way concurrent f6..f13) and is
  false at f19 in **14/14**. So: author the negative pin only with an explicit sample
  point ≥ the observed flip band (the scout's 20-frame sample is safe, 14/14); do **not**
  pin `playing` immediately after `play()` (it is `true`) or the exact flip frame
  (bimodal). The scout's own arm reproduces byte-identically ×6.
- **Visibility:** no positive reachable on this host. `is_on_screen()` false and
  `events=[]` in every configuration tried: base ×6, huge rect covering the 64×64 root
  viewport, `Camera2D` current, inside a `SubViewport`, `RenderingServer.force_draw()`
  (×3), and the scout's verbatim arm ×6. `VisibleOnScreenEnabler2D` never enables its
  target (`tgt_proc=false`). Negative pins only — confirmed.
  Caveat for authors: `VisibleOnScreenNotifier2D` has **no `get_global_rect()`**; calling
  it aborts the arm into the §4.3 hang.

### 4.5 sprite frame OOB **[O]**
| set | ERROR lines | readback |
|---|---|---|
| `frame=0` | 0 (×3) | `frame=0`, coords (0,0), rect unchanged |
| `frame=1` | 0 (×3) | `frame=1`, coords (1,0) |
| `frame=2` | **1** (×3) | refused → `frame=0` |
| `frame=3` | **1** (×12) | refused → `frame=0` |
| `frame=-1` | **1** (×3) | refused → `frame=0` (no wrap) |

The `sprite_phys` arm (frame=3 with hframes=2) therefore carries **exactly 1 ERROR per
process**, deterministic in count and byte-identical within a script (my mirror 248 B,
scout's 254 B — the only difference is the backtrace path/line; the ERROR text
`Index p_frame = 3 is out of bounds (vframes * hframes = 2).` is identical). The arm's
four-body payload stays internally consistent: sprite flags never perturb the motion, in
either startup mode.

---

## 5. Author directives

1. **Do not pin the fall-distance values as written.** `74.5675`, `118.4614`, `124.5675`,
   `482.2250` are Case-B realizations; the same code yields `66.5952`, `107.9190`,
   `116.5952`, `466.6694` in Case A, and the mode flips run-to-run under load. Either
   (a) use the §2 v≠0 sync recipe (verified deterministic in both modes), or
   (b) pin only the invariant shape (`d30>0`, ordering across gravity scales, `body_y` as
   a masked range), or (c) pin the mode with an explicit startup delay — but then the pin
   carries the delay's own load sensitivity.
2. **Normalize peer ids with marker-anchored `\d+`**, not a blanket `\d{6,}` (measured
   4–5-digit tail, 21/600 000). Pin `uid_s=1`/`is_server` freely — 63/63 loopback cycles
   and 3/3 offline peers.
3. **Keep the scout's 20-frame audio sample point** for `playing=false`; never pin the
   flip frame (f6..f13) or the post-`play()` value (true). `pos=0.000`/peak `-200.00`
   are stable negatives.
4. **vis_not: negative pins only** (`is_on_screen()==false`, `events==[]`,
   `enabler_proc==false`); no positive is reachable headless on this host.
5. **`light_props`:** keep the `height` fix and the property readbacks; replace the
   vertical x=-50 ray with a ray that actually crosses the polygon (e.g. y=-35, x −50→50)
   if the ray is meant to be evidence; keep `occ_is_co=false`; use the §2 sync recipe if
   `body_y` is pinned. The collision control (`StaticBody2D`+`CollisionPolygon2D` same
   triangle → stops at −47.7000, sharp ray hits) is the falsifiable counterpart.
6. **Budget exactly 1 ERROR for one OOB frame set** (0 for in-bounds; `frame=-1` also
   errors); the refused set leaves `frame=0`.
7. **MP arms must own their port.** Same-port concurrency produces rc=[0,0] +
   `rc_s=20` + cross-process contamination with a *different* payload and **no error** —
   serialize MP arms or give each its own port; consider asserting `frames<600` so the
   `frames=600 wait=600` contamination signature fails loudly.
8. **Any invalid op in an arm's synchronous prefix = 25 s hang, not a clean failure.**
   Keep the timeout wrapper; `timeout -s KILL` reports rc=-9/137 (not 124).

---

## 6. Remaining risks / unknowns **[?]**

- **Depth-2 labrat: zero data.** The one dispatched `ufo-labrat` reports it has only
  read/grep/glob — no exec, no write — so it could not run the assigned probes and created
  nothing. All MP replication and load stress above is this seat's own. (Per the frozen
  probeParent rule, exactly one child was dispatched and no other was attempted.)
- **Host load varies**: other lanes (r88-baseline, a 3d-repo critic) were running
  throughout; the Case A/B flip rates are *observations under changing load*, not a
  controlled load sweep. The mechanism is proven by the delay mutation; the exact
  load threshold was not mapped.
- **Port collision** was measured only for 3-way same-port concurrency (2/3 losers);
  cross-process contamination could in principle also occur with *different* ports if a
  client's connect races another lane's server on the same port — not measured.
- **Audio**: the flip frame band f6..f13 is bounded by my 20-frame sampling; what
  triggers the flip (dummy mixer thread cadence vs frame count) was not dissected.
  Peaks were sampled at **every** frame in my timeline (all `-200.00`, near and far).
- **vis_not positive**: unreachable on this host/build; a display-server host could open
  it — not tested.
- **`frames`/`wait`/`disc_wait`**: stable 4/1/2 in 61/61 cycles incl. 6-way concurrency,
  but still counters — a slower host could change them.
- Everything here is `--headless`, 60 tps, GodotPhysics2D, this host/build.

---

## 7. Evidence index

All under `corpus/live/r88-boundary/`; `manifest.sha256` covers every artefact (probes,
runner, analyzer, 163 receipt sidecars, `analysis.txt`, `RECEIPTS.md`, this report).

| artefact | path | what it carries |
|---|---|---|
| probe suite | `proj/b88_{mp,light,audio,vis,sprite}.gd` | all own arms |
| battery runner / analyzer | `run_boundary.py`, `analyze_boundary.py` | 132-run matrix, stability table |
| frozen stability table | `runs/analysis.txt` | rc/wall/uniq/ERROR/normalized-uid per tag + both payloads of every unstable tag |
| MP receipts | `runs/b88_mp.*`, `runs/verbatim.mp_loopback.*`, `runs/stress_mp_*` | §4.1, §4.2, §3.5 |
| light receipts | `runs/b88_light.*`, `runs/verbatim.light_props_*` | §4.3, §3.3 |
| audio receipts | `runs/b88_audio.timeline.*`, `runs/verbatim.audio_pos.*`, `runs/stress_audio.*` | §4.4, §3.4 |
| vis receipts | `runs/b88_vis.*`, `runs/verbatim.vis_not.*` | §4.4 |
| sprite receipts | `runs/b88_sprite.*`, `runs/verbatim.sprite_phys.*` | §4.5, §3.2 |
| race receipts | `runs/b88_sprite.fall*`, `runs/b88_sprite.fall_sync*`, `runs/verbatim.rb_gravity.*`, `runs/stress_fall.*`, `runs/seq_fall.*` | §2, §3.1 |
| command inventory | `RECEIPTS.md` | protocols, rc vectors, reproduce |

Reproduce: `cd corpus/live/r88-boundary && python3 run_boundary.py && python3 analyze_boundary.py`.
