# game-dev-2d round 99 — scout (r99-scout): the headless in-engine audio surface; r88's "headless-null" verdict refuted; 18 rows verbatim-ready

Seat `SCOUT` (LEAF; frozen `probeParent` — one labrat dispatch, documentary, §1) | lane
`r99-scout` | round 99 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
`AudioServer.get_driver_name() == "Dummy"`, mix rate **44100**, 60 physics tps.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at session start **`2c4b1ff`**
(*r94 scout*), HEAD at session end **`e741cf8`** (*r94 boundary* — other lanes committed
while this seat ran; none of those commits touch this seat's artefacts). The launch
`project.godot` is the byte-copy of `corpus/fixtures/project.godot` (`8de8b3af…`).

**No git mutation, no tracked file written, no commit.** Writes are this report and
`corpus/live/r99-scout/**` only. The tracked modification in `git status`
(`corpus/fixtures/run_battery.py`, `M`) and the untracked `corpus/fixtures/rb_*.gd`,
`reports/round-96/` are **concurrent lanes'** and contain no r99/audio token.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server
installed; `definition`/`references`/`hover` were **unavailable for every file**. No
cross-file symbol work was required (the deliverable is one new self-contained probe plus
receipts), so no rename/reference risk exists; semantic carriers are fresh-process
execution receipts, runtime `AudioServer`/`ClassDB` introspection inside the probes, and
engine-emitted error text. Every `file:line` below is engine-emitted `at:` backtrace text,
never a source read; no engine source tree exists on this host, so mechanisms are marked
**[I]** and kept separate from measurements.

**Labrat disclosure.** The one permitted frozen-`probeParent` labrat was dispatched once
(bounded, read-only) to falsify H = "headless audio is not null; r88's null is a
0.1 s-stream/20-frame readback confound". It returned **H CONFIRMED on documentary
evidence** — quoting `run_battery.py:680` (`--headless` launch), the pinned
`audio_playback` row (`PASS audio_playback in_tree=true playing=true
position_advanced=true`), and the r12 receipts (`position_before=0.00580498855561
position_after=0.09868481010199`), plus r88 §3.15 verbatim — and reported honestly that
**its substrate exposes no shell/exec tool**, so it ran 0 godot launches. It also raised
the one caveat worth resolving empirically (r88 used `LOOP_FORWARD`): §3.4 measures that
caveat and resolves it (degenerate loop points ⇒ self-termination). No independent
replication exists from that seat; all values below rest on this seat's own receipts.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Assigned: the in-engine audio surface — `AudioStreamPlayer2D` / `AudioStreamPlayer`
(playback position, bus routing, attenuation readbacks), stream generators
(`AudioStreamGenerator` + playback push frames), polyphony (`max_polyphony`),
autoplay/`finished` timing — with r88's `audio_pos` verdict as the null baseline.**

Why it earns the round: r88 §3.15 concluded *"Under the Dummy driver no buffer advances
and `playing` clears … Only negative pins are authorable headless"* and the r88
adjudication folded a **headless-null-audio** row. The first probe refuted that verdict
on every axis: the Dummy driver runs a **real mix clock** (position advances, streams
finish, `finished` fires, bus peaks are live dB values, generator frames are consumed).
The tracked battery itself had always contradicted the verdict — `audio_playback.gd`
asserts `playing=true` + `position_advanced=true` **headless** and is captured green in 62 lesson receipts (§7 F1) — so this round's job was to measure *what is not null*, pin it, and locate the
r88 confound exactly. Two concrete confounds were found and pinned:

1. r88's stream was `LOOP_FORWARD` **with default loop points** (`loop_begin=loop_end=0`),
   which **terminates after one sample** (`playing=false`), not loops (§3.4);
2. `get_playback_position()` **reads 0.0000000 after finish/stop** (§3.3/§3.10), so
   r88's `pos=0.000` was the post-finish readback, and its `-200 dB` peaks were the
   *idle* readback (nothing playing), not a dead meter (§3.6).

What *is* null headless is now a short, exact list: `get_output_latency()==0.00`,
`get_bus_send(Master)==""`, the device lists are `["Default"]` only, bus peaks read
`-200.00` while silent, and `AudioStreamGeneratorPlayback.clear_buffer()` is **refused in
every state** (loud `ERROR`, §3.5).

Adjacents weighed and left: 3D audio (`AudioStreamPlayer3D`) is out of lane;
`AudioEffect` DSP semantics beyond bus readbacks and `AudioStreamMicrophone` capture were
not armed (no input device; `audio/driver/enable_input=false`).

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (8 arms) | census, position ladder, finish, generator push/pull, polyphony, bus, autoplay, 2D props | `runs/disc-*.{out,err}` |
| 2 | `probes/discover2.gd` (9 arms) | loop modes, pitch, pause, play() restart, mix clock, generator capacity, poly voices, free-drain ladder | `runs/d2-*` |
| 3 | `probes/discover3.gd` (6 arms) | 2D peak/attenuation, poly voice trace, clear_buffer hold, finish trace, stop position, block ladder | `runs/d3-*` |
| 4 | `probes/discover4.gd` (4 arms) | `finished`-signal wait, peak calibration, clear-after-stop, pause trace | `runs/d4-*` |
| 5 | `probes/discover5.gd` (4 arms) | first-readback ×4 processes, sine-vs-constant peak scale, skips growth, generator consumption | `runs/d5-*` |
| 6 | `probes/discover6.gd` (2 arms) | pan/attenuation lattice, generator-on-2D | `runs/d6-*` |
| 7 | `probes/discover7.gd` (3 arms) | loop trace (full + sub-range), pan knee | `runs/d7-*` |
| 8 | ad-hoc (`panknee*`, `loopdbg`, `p2dgen2`) | pan knee 0–100 px, max_distance/panning_strength independence, generator-on-2D live peak | stdout in §3 |
| 9 | `bash run_cells.sh` | **18 cells** (5 pure ×3, 13 block-bound ×6) = **93 runs** | `runs/r99_<cell>.rep<N>.{out,err,rc}` |
| 10 | `bash run_loadtest.sh` (16 own `yes` hogs, loadavg 95.95–115.07) | 18 cells ×3 = **54 runs** | `runs/loadtest/` |
| 11 | `python3 analyze_r99.py` | per-cell reps / out-uniq / err-uniq / rc / pinned-prefix uniq | `runs/analyze_r99.json` |
| 12 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 18 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |

**Canonical cell set: 147 receipts across 18 cells.** All `rc=0`; no cell crashed; no run
left running; **stderr 0 B on 17/18 cells** (the `gen` cell's 462 B are the two
deterministic refused-`clear_buffer()` ERROR lines + backtraces).

**Byte-stability: 18/18 cells have a `prefix_uniq=1` pinned prefix** across canonical +
loadtest reps (`runs/analyze_r99.json`: `UNSTABLE` lists only cells whose *tails* vary —
wall-clock block counters; `CRASH_CELLS=[]`). 10 cells are byte-identical **whole-line**
(including the pan-law and 2D-attenuation lattice); 8 carry a varying informational tail
after the ` | ` separator. **Load-stability:** all 54 loadtest receipts (loadavg
95.95–115.07) reproduce every pinned prefix byte-for-byte; `verify_rows.py` →
`ROWS 147/147 accepted`, `ROWS_PREFIX 147/147 accepted`, `rejected=[]`.

**Arm-dispatch integrity [O]:** every arm prints its own name on the `PASS` line
(`PASS r99_audio <arm> …`) and is parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan), so the r88 silent-fallback class
cannot recur.

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **Driver/bus/device census** | **PINNABLE** (Dummy, 44100, stereo, latency 0.00, 1 bus, `["Default"]` devices) | 6 | prefix uniq=1 |
| **Mix clock / position advance** | **PINNABLE law** — real clock: 128-frame quantum, 4096-frame block, ~92.88 ms period | 9 | prefix uniq=1 |
| **Finish + `finished` signal** | **PINNABLE law** — transition at stream end, signal same frame, position resets to 0 | 9 | prefix uniq=1 |
| **`LOOP_FORWARD` default loop points** | **PINNABLE hazard** — self-terminates after one sample | 9 | whole line uniq=1 |
| **Explicit loop points** | **PINNABLE law** — wraps exactly at `loop_end` | 9 | prefix uniq=1 |
| **`AudioStreamGenerator`** | **PINNABLE** — capacity `next_pow2(bl·rate)−1`, real consumption, skips on dry; `clear_buffer()` refused | 9 | prefix uniq=1 (2 expected ERROR lines) |
| **Generator output on Master** | **PINNABLE** — live peak, `−0.92 dB` for a 0.9 constant | 9 | whole line uniq=1 |
| **Generator output on 2D** | **PINNABLE** — live, obeys the 2D center pan (`−6.94 dB`) | 9 | prefix uniq=1 |
| **Polyphony** | **PINNABLE law** — each `play()` = new voice; readback tracks the newest; older voices keep advancing | 9 | prefix uniq=1 |
| **Bus routing/effects readbacks** | **PINNABLE** — incl. silent invalid-name fallback to Master | 6 | whole line uniq=1 |
| **Bus peaks** | **PINNABLE** — live dB while playing, `−200.00` idle; per-block, lags one block | 9 | prefix uniq=1 |
| **2D attenuation model** | **PINNABLE law** — linear `1−d/max_distance`, `−200` past `max_distance` | 9 | whole line uniq=1 |
| **2D pan model** | **PINNABLE law** — `pan = clamp(x/128, ±0.5)·panning_strength`, center = 0.5/channel | 9 | whole line uniq=1 |
| **Autoplay** | **PINNABLE** — starts on the first frame after `add_child` | 6 | whole line uniq=1 |
| **Pause / stop** | **PINNABLE laws** — pause freezes and reports `is_playing()==false`; stop zeroes the position | 9 / 6 | prefix uniq=1 / whole line |
| **r88 `audio_pos` verdict** | **REFUTED [A]** — the surface is not null; the confounds are pinned | — | — |

---

## 3. Measured laws, verbatim **[M]**

### 3.1 Census (`r99_audio_census`, 6 receipts)

```
PASS r99_audio census driver=Dummy mix_rate=44100 speaker_mode=0 output_latency=0.00
bus_count=1 bus_names=["Master"] bus0_vol=0.00 bus0_mute=false bus0_solo=false
bus0_send_empty=true bus0_effects=0 idle_peak=-200.00/-200.00 out_devices=["Default"]
in_devices=["Default"] enable_input=false max_fps=0 tps=60
```

- `speaker_mode=0` = `SPEAKER_MODE_STEREO`; `output_latency` is **0.00** (Dummy).
- `get_output_device_list()`/`get_input_device_list()` are `["Default"]` — no real device
  enumeration headless; `audio/driver/enable_input` is unset ⇒ `false`.
- Master's `get_bus_send(0)` returns the **empty string** (`bus0_send_empty=true`).
- `idle_peak` is the null the r88 report actually measured: **`−200.00/−200.00`** with
  nothing playing.

### 3.2 The mix clock — the headline law (`r99_audio_mixblock`, `r99_audio_advance`)

```
PASS r99_audio mixblock q_frames=128 jump_frames=4096 jump6=0.092880 first=0.002902494
first_is_q=true all_jumps_q=true block_jumps_ge6=true period_is_block=true
| jumps=8 block_jumps=8 jmin=0.092879802 jmax=0.092879832 wall_max=0.0968 frames=104

PASS r99_audio advance playing=true advanced=true pb_nonnull=true pos_multiple_q=true
pos_after_gt_before=true | before=0.0029025 after=0.2815419
```

- **The Dummy driver mixes in real time.** `get_playback_position()` advances while a
  stream plays; `is_playing()` stays true; `get_stream_playback()` is non-null
  (`pb_nonnull=true`).
- **Quantum = 128 frames** (`0.002902494 s` @44100): every non-looping position readback
  is `k·128` frames (`first_is_q=true`, `all_jumps_q=true`, `pos_multiple_q=true`).
- **Block = 4096 frames = `0.09287981859410431 s`** (`jump6=0.092880`): the readback
  advances in 4096-frame steps, `≥6` per 700 ms window (`block_jumps_ge6=true`), and
  `AudioServer.get_time_since_last_mix() + get_time_to_next_mix()` equals the same block
  period (`period_is_block=true`, tolerance 1e-5) — i.e. the **mix period is the block**.
- **The first readback after `play()` is exactly 128 frames** (`first=0.002902494`,
  `first_is_q=true`), stable in 4/4 fresh processes (`runs/d5-firstread*`), even when the
  read happens 25 µs after `play()`.
- **Wall pacing is real-time** (`wall_max=0.0968 s` per block jump in the 700 ms window);
  the position never advances faster than wall clock once the start burst settles.
- **Headless process frames are ~147 fps, not 60** (`runs/d2-mixclock.out`:
  `frames=119 wall=0.8077810 fps=147.317`). This is why every block-sensitive wait in the
  frozen probe is wall-time based, never a frame count.

### 3.3 Finish and the `finished` signal (`r99_audio_finish`, 9 receipts)

```
PASS r99_audio finish stopped=true playing_end=false pos_end=0.0000000 finished_seen=true
fin_frame_ge_1=true fin_same_frame=true played_gt_02=true
| transition_f=50 fin_frame=50 fin_us=331291 last_pos=0.2815419 frames=81
```

- A 0.3 s `AudioStreamWAV` stops at **296.8–358.9 ms** wall (`fin_us` mode spread across
  9 receipts; `transition_f` 44–54) — real-time paced with block quantization.
- **`finished` fires**, on the **same frame** the `playing→false` transition is observed
  (`fin_same_frame=true` in 9/9). The first measurement of "no signal" was a probe
  artifact: the arm `break`ed on the transition frame before the internal process emitted
  the signal (`runs/d3-finish2.out` `fin_frame=-1` vs `runs/d4-finwait.out`
  `transition_f=45 fin_frame=45 fin_us=296787`).
- After finish, `get_playback_position()` reads **`0.0000000`** and
  `is_processing_internal()` is `false`.
- **Hazard:** `is_playing()==false` does *not* mean "never started" — it means finished
  **or paused** (§3.10).

### 3.4 `LOOP_FORWARD` semantics — the r88 confound (`loop_degenerate`, `loop_pts`)

```
PASS r99_audio loop_degenerate playing_end=false pos_end=0.0000000 looped=false
maxpos_lt_001=true | maxpos=0.0000227 wraps=0 frames=75

PASS r99_audio loop_pts playing_end=true looped=true wraps_ge2=true maxpos_le_loop=true
| wraps=7 maxpos=0.0957823 frames=104
```

- **`loop_mode = LOOP_FORWARD` with default loop points (`loop_begin=loop_end=0`)
  terminates after one sample**: max position `0.0000227` (= 1/44100), `playing=false`
  by ~0.5 s, final position `0.0000000`, zero wraps. This is exactly r88's stream
  configuration, and it is why their 0.1 s "looping" stream read `playing=false, pos=0.000`.
- **With explicit loop points** (`loop_begin=0`, `loop_end=4410`) the stream loops: the
  position wraps at the loop length (`0.0957823 → 0.0886621 → …`, `wraps=7` in 700 ms,
  `maxpos ≤ loop_end`). Trace in `runs/d7-loop_trace.out` shows a 1.0 s loop wrapping
  `0.931700706 → 0.024580499` = `+0.092879818 − 1.0` exactly.
- For a loop shorter than the mix block the readback **decreases** by
  `(block − loop_len)` each block (0.1 s loop ⇒ −0.00712 s per block,
  `runs/d7-loop_short.out`) — a wrap is a *decrease*, not a reset to 0.

### 3.5 `AudioStreamGenerator` (`r99_audio_gen`, 9 receipts + 2 expected ERROR lines)

```
PASS r99_audio gen caps=["4095", "8191", "16383"] pushed=8191 avail_full=0 full_refused=true
clear_noop_active=true clear_noop_stopped=true skips_dry_gt0=true
| avail_after_refused=0 avail_stopped=512 avail_after_stop=512 skips_dry=96
```

- **Capacity = `next_pow2(buffer_length · mix_rate) − 1`**: `0.05 s → 4095`,
  `0.1 s → 8191`, `0.25 s → 16383` — *not* `bl·rate` (2205/4410/11025). `push_frame()`
  fills to exactly `8191` then refuses (`avail_full=0`, `full_refused=true`);
  `push_buffer(PackedVector2Array)` works (`runs/d2-gen2.out`: `push_buffer_1000=true`).
- **Frames are really consumed by the mixer**: a full 8191-frame buffer drains back to
  `avail=8191` within 200–300 ms (`runs/d5-genconsume.out`), and `get_skips()` grows when
  the buffer runs dry (`skips_dry=96…128` in 300 ms; `runs/d5-skips.out` 64/128/192/288
  at 200/400/600/800 ms).
- **`clear_buffer()` is unusable**: it is refused while playing *and* after `stop()`, both
  with the deterministic line
  `ERROR: Condition "active" is true.` /
  `at: clear_buffer (servers/audio/effects/audio_stream_generator.cpp:166)`
  (`clear_noop_active=true`, `clear_noop_stopped=true`; the two ERROR lines are the only
  stderr in the whole round and are declared in `EXPECTED_ERRORS`). Authors must manage
  the ring buffer by pushing, never by clearing.
- After `stop()`, `get_stream_playback()` returns `null` and a fresh call emits
  `ERROR: Player is inactive. Call play() before requesting get_stream_playback().`
  (`runs/d2-gen2.out`).

### 3.6 Peaks — live meters (`bus_peak`, `gen_peak`, `gen2d`, `peak_calib`)

```
PASS r99_audio bus_peak live_gt_neg20=true idle_is_minus200=true live_gt_idle=true
| live=-12.04 idle=-200.00 pos_live=0.2815419

PASS r99_audio gen_peak live_gt_neg10=true dry_is_minus200=true live_gt_dry=true
| pushed=8191 live=-0.92 dry=-200.00

PASS r99_audio gen2d pushed=8191 center_peak=-6.94/-6.94 center_half_pan=true advanced=true
| live_l=-6.9358 live_r=-6.9358 pos=0.0928798

PASS r99_audio peak_calib const8191_minus12=true sine8191_matches_const=true
const16384_minus6=true sine4096_minus18=true idle_after_minus200=true
| const_8191=-12.04 sine_8191=-12.04 sine_4096=-18.06 const_16384=-6.02
```

- **Bus peaks are live dB values while a stream plays** (`live=-12.04` for a 8191-amplitude
  sine on Master) and **`−200.00` when idle** — the value r88 reported. `runs/d4-peakcal.out`
  calibrates the scale exactly: constant 32767→`0.00`, 16384→`−6.02`, 8191→`−12.04`,
  4096→`−18.06` dB, i.e. `20·log10(level/32768)`.
- The generator's own output is mixed: a 0.9 constant reads `−0.92` on Master and
  **`−6.94` on a centered `AudioStreamPlayer2D`** (= 0.9 × center-pan 0.5, §3.9) — the 2D
  pan/attenuation chain applies to generator output too.
- **Peak readback is per-mix-block**: it updates once per ~92.9 ms block and lags a
  position/volume change by up to one block (`runs/d6-pan.out` early reads show the
  previous block's value). Wait ≥300 ms per step in author probes.

### 3.7 Bus routing readbacks (`r99_audio_bus`, 6 receipts)

```
PASS r99_audio bus added_name=r99_probe_bus added_vol=-6.00 send_empty=true effects=1
eff_class=AudioEffectAmplify eff_vol=-3.00 eff_enabled=true resolved_idx=1 invalid_idx=-1
invalid_readback=Master valid_readback=r99_probe_bus advanced=true removed_effects=0
bus_count_end=1
```

- `add_bus`/`set_bus_name`/`set_bus_volume_db`/`add_bus_effect` all read back exactly;
  `AudioServer.get_bus_index("r99_probe_bus") == 1`; an `AudioEffectAmplify`'s `volume_db`
  reads back `−3.00` and `is_bus_effect_enabled` is `true`.
- **An unknown bus name silently falls back to Master**: `get_bus_index("NoSuchBus")==−1`,
  but assigning it to `player.bus` leaves the property reading `Master`
  (`invalid_readback=Master`) and playback still advances — the same silent-fallback
  class the tracked `audio_bus_route_invalid_control` fixture asserts.
- Removal is clean: effect count 0, `bus_count` back to 1.

### 3.8 Polyphony (`r99_audio_poly`, 9 receipts)

```
PASS r99_audio poly voices=3 distinct=2 newest_tracked=true older_advanced=true
all_playing=true playing=true
| p1=0.2815420 p2=0.2815420 p3=0.3744218 p1b=0.5601814 p2b=0.6530612 p1c=0.9317007
  player_read=0.3744218
```

- With `max_polyphony=3`, each `play()` creates a **new playback object**
  (`distinct=2` over three voices) and **does not stop the older voices** — retained
  references keep advancing independently (`older_advanced=true`: `p1c > p2b > p3`).
- **`get_playback_position()` returns the newest voice** (`newest_tracked=true`), so a
  polyphonic player's position readback *resets* on each `play()` while the audio of the
  earlier voices continues — the author-relevant hazard of this cell.
- Default `max_polyphony=1`: `play()` while playing **restarts** the stream — the
  position immediately reads a fresh quantum (`runs/d2-playpos.out`:
  `before=0.0957823 imm_after_play=0.0029025 pb_same_before_imm=false`).

### 3.9 `AudioStreamPlayer2D` attenuation + pan laws (`p2d`, `pan_law`)

```
PASS r99_audio p2d attenuation=1.00 max_distance=2000.00 panning=1.00 area_mask=0 bus=Master
volume=0.00 pitch=1.00 listener_current=true advanced=true center_lr_equal=true
left_louder=true right_louder=true far_att_lt_center=true cutoff_2001=true cutoff_2500=true
diag_pan_saturated=true
| center=-18.06/-18.06 x400_diff=9.54 x-800=-18.98/-28.52 x800=-28.52/-18.98
  y-1500=-30.10 y-2001=-200.00 y-2500=-200.00 diag=-40.56/-31.02
  probe=["x-400=-16.48/-26.02","x-800=-18.98/-28.52","x800=-28.52/-18.98",
         "y-1500=-30.10/-30.10","y-2001=-200.00/-200.00","y-2500=-200.00/-200.00",
         "diag800-1500=-40.56/-31.02"]

PASS r99_audio pan_law center_zero=true x32_diff=4.44 x64_diff=9.54 x200_sat=true
maxd_independent=true ps_half=4.44 x_only=true
| d32=-4.4370 d64=-9.5424 d200=-9.5424 d64_4k=-9.5424 d64_half=-4.4370 d32_far=-4.4370
```

Measured model (source sine = `−12.04 dB`, all values are peak dB on Master):

| position (listener at origin) | L/R peaks | implied gain |
|---|---|---|
| (0, 0) | `−18.06/−18.06` | source × 0.5 (center pan), att 1.0 |
| (−800, 0) | `−18.98/−28.52` | att `1−800/2000=0.6` (`−4.44 dB`), pan `−0.5` |
| (800, 0) | `−28.52/−18.98` | mirrored |
| (0, −1500) | `−30.10/−30.10` | att `0.25` (`−12.04 dB`), pan 0 |
| (0, −1999) (`runs/d6-pan.out`) | `−84.08/−84.08` | att `0.0005` (`−66.02 dB`) |
| (0, −2001) / (0, −2500) | `−200.00` | **past `max_distance` ⇒ silence** |
| (800, −1500) | `−40.56/−31.02` | att `0.15` + pan saturated |

- **Attenuation is linear in distance**: `gain = max(0, 1 − d/max_distance)`, i.e.
  `dB = 20·log10(1 − d/max_distance)`; verified at d = 800 (−4.44), 1500 (−12.04),
  1999 (−66.02), and hard `−200` beyond `max_distance` (`cutoff_2001=true`,
  `cutoff_2500=true`). Not inverse-square, not exponential.
- **Pan**: `pan_eff = clamp(x/128, −0.5, +0.5) · panning_strength`, where `x` is the
  listener-relative x in px. Channel gains are `(1∓pan_eff)/2` of the attenuated signal:
  center → 0.5 each (−6.02 dB); x=32 → ±0.25 (`x32_diff=4.44`); x≥64 → ±0.5
  (`x64_diff=9.54` saturated, `x200_sat=true`).
  - **Independent of `max_distance`** (`maxd_independent=true`: identical at 1000/2000/4000),
    **halved by `panning_strength=0.5`** (`ps_half=4.44`), **x-only** (`x_only=true`: the
    (32,−1500) split equals the (32,0) split while the attenuation differs).
  - Practical consequence: beyond **64 px** of lateral offset the pan is fully saturated,
    so for a 2000-px `max_distance` the pan is effectively binary.
- `AudioListener2D.make_current()`/`is_current()` return `true`; `attenuation=1.00`,
  `max_distance=2000.00`, `panning_strength=1.00`, `area_mask=0`, `bus=Master`,
  `volume_db=0.00`, `pitch_scale=1.00` all read back.

### 3.10 Autoplay / pause / stop (`autoplay`, `pause`, `stoppos`)

```
PASS r99_audio autoplay pre=false at_add=false after1=true noauto=false manual=true

PASS r99_audio pause playing_while_paused=false frozen_400ms=true resumed_advanced=true
pos_gt_frozen=true | a=0.2815419 b=0.2931519 c=0.2931519 d=0.5717914

PASS r99_audio stoppos before_gt0=true imm_zero=true playing_after=false after_frame_zero=true
```

- **Autoplay starts on the first process frame after `add_child`** (`at_add=false`,
  `after1=true`); `autoplay=false` stays silent until `play()` (`noauto=false`,
  `manual=true`).
- **`stream_paused=true` makes `is_playing()` return `false`** while the stream is merely
  paused (`playing_while_paused=false` in 9/9) — do not use `is_playing()` as a
  "paused" test. The position advances by the in-flight block remainder (~0.0116 s in the
  measured case) then **freezes** (`frozen_400ms=true`); unpausing continues from the
  frozen position (`resumed_advanced=true`).
- **`stop()` zeroes the position immediately** (`imm_zero=true`) and `is_playing()` is
  false (`playing_after=false`) — the post-stop readback is `0.0000000`, the second half
  of the r88 confound.

---

### 3.11 Causal reproduction on r88's own probe (`runs/r88-repro-*`) **[M]**

The dead seat's probe survives at `corpus/live/r88-scout/proj/r88_probe.gd`; this seat
copied it (byte-identical except a `--fix-loop` switch) to
`proj/r88_audio_repro.gd` and ran its `audio_pos` arm with the r88 launch shape
(`godot --headless --path proj --arm audio_pos --script res://r88_audio_repro.gd`):

| arm | stdout (3/3 byte-identical) | stderr |
|---|---|---|
| **verbatim** (r88's `LOOP_FORWARD`, default loop points) | `R88 audio_pos playing=false pos=0.000 peaks_near=[-200.00,-200.00,-200.00,-200.00]` / `peaks_far=[-200.00,-200.00,-200.00,-200.00]` | 0 B |
| **one-line fix** (`wav.loop_end = 4410`) | `R88 audio_pos playing=true pos=0.096` + peaks leave `-200.00` (`-6.02` once a mix block lands) | 2 `ObjectDB … leaked at exit` WARNING lines (r88's probe never frees its nodes) |

The verbatim arm reproduces the r88-pinned battery row
(`PASS r88_surfaces audio_pos playing=false pos=0.000 peaks_near=[-200.00,…]`) byte-for-byte
3/3; the single `loop_end` line flips the identical probe to a live surface 6/6
(`playing=true pos=0.096`; the exact peak sample varies with mix-block phase, as §3.6
predicts). **r88's null is fully explained and causally attributed.**

---

## 4. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | r88: "under the Dummy driver no buffer advances and `playing` clears; only negative pins are authorable headless" | **REFUTED [A]** — position advances (`advance`), peaks are live (`bus_peak` `−12.04`), generator frames are consumed (`gen`), `finished` fires (`finish`); and the tracked `audio_playback` battery row has asserted `playing=true position_advanced=true` headless in 62 lesson receipts since r12 (`position_before=0.00580498855561 → 0.09868481010199`); **causal repro on r88's own probe** (§3.11): verbatim arm reproduces `playing=false pos=0.000 peaks=[-200.00×4]` 3/3, and adding `wav.loop_end = 4410` flips the identical probe to `playing=true pos=0.096` 6/6 |
| F2 | r88's `playing=false, pos=0.000` is the Dummy driver clearing playback | **REFUTED [A]** — it is (a) the degenerate `LOOP_FORWARD` default-loop-points termination (`maxpos=0.0000227`, `playing_end=false`) and (b) the post-finish position readback `0.0000000` |
| F3 | r88's `−200 dB` peaks mean the meter is dead headless | **REFUTED [A]** — `−200.00` is the *idle* readback; while playing the same bus reads `−12.04` (`live_gt_idle=true`) |
| F4 | `get_playback_position()` advances in 128-frame quanta only | **REFUTED [A]** — it advances in 4096-frame block steps (~92.88 ms) with 128-frame sub-steps; `block_jumps_ge6=true`, `period_is_block=true` |
| F5 | `LOOP_FORWARD` loops the stream | **REFUTED [A] with default loop points** (1-sample termination); **confirmed with explicit points** (`looped=true`, `wraps=7`) |
| F6 | `finished` never fires headless | **REFUTED [A]** — fires on the transition frame (`fin_same_frame=true` in 9/9); the earlier negative was a probe `break` artifact |
| F7 | `is_playing()==false` means the stream is stopped | **REFUTED [A]** — also true while `stream_paused=true` (`playing_while_paused=false`) |
| F8 | `clear_buffer()` clears the generator ring buffer | **REFUTED [A]** — refused in both states with `ERROR: Condition "active" is true.`; avail unchanged (`clear_noop_active/stopped=true`) |
| F9 | Generator capacity = `buffer_length · mix_rate` | **REFUTED [A]** — `next_pow2(...) − 1` (4095/8191/16383 vs 2205/4410/11025) |
| F10 | A polyphonic player's position readback is the oldest/current voice | **REFUTED [A]** — it is the **newest** voice (`newest_tracked=true`), older voices keep advancing |
| F11 | 2D distance attenuation is inverse-square/exponential | **REFUTED [A]** — linear `1−d/max_distance` (measured at 800/1500/1999 px to 0.01 dB) |
| F12 | 2D pan scales continuously with lateral offset | **REFUTED [A]** — saturates at ±0.5 for |x| ≥ 64 px, independent of `max_distance`, halved by `panning_strength` |
| F13 | 2D pan depends on the direction vector (normalized by distance) | **REFUTED [A]** — `x_only=true`: (32,−1500) and (32,0) give the identical split |
| F14 | Autoplay starts at `add_child` | **REFUTED [A]** — starts on the first process frame after it |
| F15 | A stopped/finished player keeps its last position | **REFUTED [A]** — reads `0.0000000` (`stoppos`, `finish`) |
| F16 | An unknown bus name is an error | **REFUTED [A]** — `get_bus_index` = −1 but the property silently reads `Master` and playback works |
| F17 | Peak readback is a max-hold across blocks | **REFUTED [A]** — per-block; a dry generator reads `−200.00` while an earlier fed block was `−0.92` |

---

## 5. Hazards recorded (for the author, boundary and battery seats)

1. **Never pin frame counts as time headless** — process frames run ~147 fps and vary with
   load; block-sensitive waits must be wall-time based (§3.2).
2. **`LOOP_FORWARD` with default loop points terminates after one sample** (§3.4) — set
   `loop_begin`/`loop_end` explicitly or the "looping" stream ends immediately.
3. **A finished/stopped player reads `pos=0.0000000`** (§3.3/§3.10) — `pos==0` is not
   evidence that audio never ran; read `playing` + the mix clock instead.
4. **`is_playing()==false` also means paused** (§3.10) — check `stream_paused` before
   concluding a stream ended.
5. **Polyphonic position readback tracks the newest voice** (§3.8) — the readback appears
   to "reset" on each `play()` while earlier voices are still audible; keep playback
   references if you need per-voice positions.
6. **`clear_buffer()` is refused in every state** (§3.5) — it emits a loud `ERROR` and is a
   no-op; budget `expected_errors` if a probe calls it (or never call it).
7. **Generator capacity is a power of two minus one** (§3.5) — do not size a push loop by
   `buffer_length * mix_rate`.
8. **Bus peaks are per-block and lag** (§3.6) — wait ≥300 ms after a position/volume
   change before reading a peak; a dry generator reads `−200.00` even after playing.
9. **2D pan saturates at 64 px** (§3.9) — beyond that, panning is effectively binary;
   `panning_strength` scales it.
10. **An invalid bus name silently falls back to Master** (§3.7) — assert
    `get_bus_index(name) >= 0` if the route matters.
11. **ObjectDB leak warnings**: freeing a player without draining frames leaves
    `WARNING: N ObjectDB instances were leaked at exit` on stderr (drain ≥2 frames after
    `free()`, measured `runs/drain-{0,2,5,20,60}`: only `drain=0` leaks). The battery's
    `classify_audio_process` rejects such a row outright.
12. **Probe discipline (this seat's own bug, caught by falsification):** GDScript lambdas
    **capture by value** — a `finished.connect(func(): fin_frame = PH)` handler silently
    never updates the outer variable. Use a bound method (this seat's `_on_finished`) and
    re-measure; the first `finish` arm's "no signal" was this artifact plus a
    break-before-emit.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (18, exec-checked)

`corpus/live/r99-scout/author-rows.py.txt` holds `ROWS`, `ROWS_PREFIX` and
`EXPECTED_ERRORS`; `python3 verify_rows.py` classifies every row against **every**
canonical + loadtest receipt with the production `classify_process` (AST-extracted from
`corpus/fixtures/run_battery.py`, segment sha256 `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`
— the same segment r89/r90/r91/r95 pinned):

- **`ROWS` (full-line for 10 stable cells, prefix for 8 tail-varying cells): 147/147
  receipts accepted, `rejected=[]`.**
- **`ROWS_PREFIX` (recommended): 147/147 accepted, `rejected=[]`.**
- `EXPECTED_ERRORS`: exactly one entry —
  `r99_audio_gen`: `('ERROR: Condition "active" is true.',)` (the two refused
  `clear_buffer()` calls; both ERROR lines match the exact allowlist entry).

```
r99_audio_census          PASS r99_audio census driver=Dummy mix_rate=44100 speaker_mode=0 … tps=60
r99_audio_bus             PASS r99_audio bus added_name=r99_probe_bus added_vol=-6.00 … bus_count_end=1
r99_audio_autoplay        PASS r99_audio autoplay pre=false at_add=false after1=true noauto=false manual=true
r99_audio_stoppos         PASS r99_audio stoppos before_gt0=true imm_zero=true playing_after=false after_frame_zero=true
r99_audio_peak_calib      PASS r99_audio peak_calib const8191_minus12=true … idle_after_minus200=true
r99_audio_mixblock        PASS r99_audio mixblock q_frames=128 jump_frames=4096 jump6=0.092880 first=0.002902494 … period_is_block=true
r99_audio_advance         PASS r99_audio advance playing=true advanced=true pb_nonnull=true pos_multiple_q=true pos_after_gt_before=true
r99_audio_finish          PASS r99_audio finish stopped=true playing_end=false pos_end=0.0000000 finished_seen=true … played_gt_02=true
r99_audio_loop_degenerate PASS r99_audio loop_degenerate playing_end=false pos_end=0.0000000 looped=false maxpos_lt_001=true
r99_audio_loop_pts        PASS r99_audio loop_pts playing_end=true looped=true wraps_ge2=true maxpos_le_loop=true
r99_audio_gen             PASS r99_audio gen caps=["4095", "8191", "16383"] pushed=8191 … skips_dry_gt0=true
r99_audio_gen_peak        PASS r99_audio gen_peak live_gt_neg10=true dry_is_minus200=true live_gt_dry=true
r99_audio_gen2d           PASS r99_audio gen2d pushed=8191 center_peak=-6.94/-6.94 center_half_pan=true advanced=true
r99_audio_poly            PASS r99_audio poly voices=3 distinct=2 newest_tracked=true older_advanced=true all_playing=true playing=true
r99_audio_bus_peak        PASS r99_audio bus_peak live_gt_neg20=true idle_is_minus200=true live_gt_idle=true
r99_audio_p2d             PASS r99_audio p2d attenuation=1.00 max_distance=2000.00 … diag_pan_saturated=true
r99_audio_pan_law         PASS r99_audio pan_law center_zero=true x32_diff=4.44 x64_diff=9.54 x200_sat=true maxd_independent=true ps_half=4.44 x_only=true
r99_audio_pause           PASS r99_audio pause playing_while_paused=false frozen_400ms=true resumed_advanced=true pos_gt_frozen=true
```
(Exact strings in `author-rows.py.txt`.)

Probe file lands at `corpus/fixtures/audio_lattice.gd` (sha256
`165571c410d506f14915326fd0806e9ff01e5056631620f565c9a7836a920baf`; self-contained
`SceneTree` script, battery `--arm=` convention). Insert the rows ahead of the crash/
descendant tail like prior blocks; **one `expected_errors` entry is required** (the `gen`
cell). No other fixture change is needed.

### 6.2 What to pin and what not to pin

1. **Pin the `PASS r99_audio …` prefix** — it carries the arm name, so the r88
   silent-fallback failure cannot recur.
2. **Prefer `ROWS_PREFIX`** for the 8 tail-varying cells (`mixblock`, `advance`, `finish`,
   `loop_pts`, `gen`, `poly`, `bus_peak`, `gen2d`): their tails carry wall-clock block
   counters that are modes, not laws. All 18 full-line rows are *also* load-clean today.
3. **Pin the laws, not just the values**: `q_frames=128`/`jump_frames=4096`/
   `first=0.002902494`; `looped=false` for the degenerate loop; `playing_while_paused=false`;
   `x32_diff=4.44`/`x64_diff=9.54`; `caps=["4095","8191","16383"]`.
4. **Do not pin** raw `transition_f`/`frames`/`jumps`/`skips_dry`/`wraps` (wall-clock
   modes), raw `pos_live`/`player_read` per-voice positions (block phase), or anything
   from a construction you did not freeze yourself.
5. **Pin `idle_peak=-200.00` and `live_gt_idle=true` together** — the pair is the r88
   refutation; either alone is ambiguous.
6. **No envelope is needed for any pinned prefix** — 18/18 are single-valued across 147
   canonical + load receipts (including at loadavg 95.95–115.07).

---

## 7. Remaining unknowns / not measured

- **Mechanism of the 128/4096 quantization** — the *values* are measured and stable, but
  *why* the first readback is exactly one 128-frame quantum and subsequent updates land
  every 4096 frames is **[I]** (no engine source on this host). The 147-fps main loop and
  the ~92.9 ms mix period are both measured.
- **`pitch_scale` ratio** — `runs/d2-pitch.out` shows `pitch=2.0` advancing faster and
  `pitch=0.5` slower, but the ratios measured (2.69 / 0.34 over the sampled window) are
  contaminated by the start burst; an exact ratio cell was not armed.
- **`stream_paused` + `seek`/`play(from_pos)`** — only the plain pause/resume path was
  measured.
- **`max_polyphony` > 3 and voice stealing** — only 3 voices; eviction order at the cap
  was not measured.
- **`Area2D`-driven audio buses** (`area_mask`, `AudioStreamPlayer2D` area overrides) —
  `area_mask=0` readback only.
- **`AudioEffect` DSP semantics** — add/readback/remove only; no effect response was
  measured (an Amplify's `−3.00` readback is a value pin, not a DSP claim).
- **`AudioStreamMicrophone` / input** — `enable_input=false`, no input device headless.
- **`AudioStreamPlayer3D`** — out of lane (g2d); its attenuation model is 3D-specific.
- **Non-Dummy drivers** — every value here is the Dummy driver; a real host
  (PulseAudio/ALSA) will differ in device lists, latency and possibly block size.
- **Portability**: all values are this host/build/`--headless`/Dummy/44100 Hz.

---

## 8. Host hygiene

- **207 bounded launches captured** (93 canonical cell runs + 54 loadtest + 55 discovery/
  smoke arms + 5 stdout-only ad-hoc probes), all `--headless`, all `timeout -s KILL`-bounded (40/60 s; none hit),
  no run left running (`pgrep -fa audio_lattice` → none; the only godot processes on the
  host during the session belong to other lanes).
- Loadtest hogs: 16 own `yes` processes started and **only their own PIDs killed**
  (own-PID array + trap; no `pkill` by name) — loadavg 95.95–115.07 during the run.
- **No tracked file written, no commit**: `git status --porcelain` shows the concurrent
  lane's `M corpus/fixtures/run_battery.py` (already modified before this session) plus
  other lanes' untracked `corpus/fixtures/rb_*.gd`, `reports/round-96/`; this seat's writes
  are `corpus/live/r99-scout/**` and this report only.
- `manifest.sha256` (586 lines) covers every artefact under `corpus/live/r99-scout/`.

---

## 9. Evidence index

All under `corpus/live/r99-scout/`; `manifest.sha256` covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| **frozen primary probe, 18 cells** | `probes/audio_lattice.gd` | `165571c410d506f1` |
| discovery probes (7) | `probes/discover*.gd` | see manifest |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| canonical driver (18 cells, 93 runs) | `run_cells.sh` | see manifest |
| loadtest driver (54 runs, load 95.95–115.07) | `run_loadtest.sh` | see manifest |
| analyzer → json | `analyze_r99.py` → `runs/analyze_r99.json` | see manifest |
| author rows + builder + verifier | `author-rows.py.txt`, `make_author_rows.py`, `verify_rows.py` | see manifest |
| per-cell receipts (93 × 3 files) | `runs/r99_*.{out,err,rc}` | `manifest.sha256` |
| loadtest receipts (54 × 3 files) | `runs/loadtest/` | `manifest.sha256` |
| discovery receipts | `runs/disc-*`, `runs/d2-*` … `runs/d7-*`, `runs/drain-*`, `runs/smoke-*` | `manifest.sha256` |
| **r88-probe causal repro (verbatim ×3 + `--fix-loop` ×3)** | `proj/r88_audio_repro.gd`, `runs/r88-repro-{verbatim,fixloop}.rep*` | `manifest.sha256` |

Reproduce: `bash run_cells.sh && bash run_loadtest.sh && python3 analyze_r99.py &&
python3 make_author_rows.py && python3 verify_rows.py` (expect every pinned prefix
`uniq=1`, `ROWS 147/147`, `ROWS_PREFIX 147/147`, `rejected=[]`).
