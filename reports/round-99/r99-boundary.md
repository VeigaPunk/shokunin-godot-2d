# game-dev-2d round 99 — boundary (r99-boundary): the row lattice is quiet/load/paced-fps/thread-portable — but **`--fixed-fps` is unpaced** (100k–233k fps) and the frozen probe's frame caps collapse its wall windows there (14–16/18 cells break); `block_jumps_ge6` and `fin_same_frame` are **polling-rate-coupled observations, not laws**; the r88 causal repro replicates only at paced frame rates; no r95-style cycle found

Seat `BOUNDARY` (LEAF; frozen `probeParent` — one read-only `labrat` dispatch, §2) | lane
`r99-boundary` | round 99 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
audio driver `Dummy`, mix rate 44100, 60 physics tps. Repo
`~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start **`2db28ad7`** (r99 scout's
HEAD `2c4b1ff` had already moved), HEAD at session end **`23947df0`** — other lanes committed
while this seat ran; none of those commits touch this lane's artefacts.

Attack corpus: **732 fresh `rc`-bearing launches + 9 pre-freeze pilot launches = 741 fresh
processes**, 12 mode batches, **all `rc=0`, 0 timeouts (0 × rc=137)**. Frozen primary probe
byte-copy `probes/audio_lattice.gd` (sha256 `165571c410d506f1…`, identical to the scout's own
file); own mode/phase probe `probes/r99b_modes.gd` (sha256 `b680e6f297b7534d…`, 11 arms);
launch projects `proj/` (fixture byte-copy `8de8b3af9cc737ed…`) and `proj2d/` (same + the
threaded-physics setting, `eb2bda39ce82cd5a…`); drivers `run_matrix.sh` / `run_probes.sh` /
`run_r88.sh` / `run_ffslow.sh`; analyzer `analyze_r99b.py` (uses the production
`classify_process` AST-extracted from `corpus/fixtures/run_battery.py`, segment sha256
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` — the same segment
r89/r90/r91/r95/r97/r99 pinned).

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r99-boundary/**` only. `git status --porcelain` shows only the
pre-existing concurrent-lane ` M corpus/fixtures/run_battery.py` (present before this session)
plus untracked churn; `corpus/fixtures/` was never written by this seat (the probes were only
ever copied into this lane's own `proj/` and `proj2d/`).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on this
host; `definition`/`references`/`hover` were **unavailable for every file**. No
rename/symbol-level work was required (this is a behavioral attack); every mechanism statement
below is marked **[I]** and kept separate from the measurements. Probe source and the frozen
probe's line numbers were read directly.

**The host is shared.** Other lanes ran 48–80 `yes` hogs for the whole session (loadavg
59–139). `quiet` below means **"no hogs added by this seat"**, never an idle host. The `load`
batch added exactly **16 own `yes` hogs** (task floor ≥12), tracked by PID and killed by PID
(`own_hogs_killed=16`, `host_yes_after_kill=80` — other lanes' hogs untouched, never `pkill`).

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[A]** refutation/ablation; **[I]** inference; **[U]** phase-unstable payload (explained);
**[?]** unknown.

---

## 0. What I ran

| # | batch | flags / project | runs (receipts in the dir) | loadavg start→end | rows accepted |
|---|---|---|---|---|---|
| 1 | `quiet` | — | 54 cells ×3 + 18 probes + 4 r88 | 61.3 → (tail lost, §0.1) | **54/54** |
| 2 | `load` | + **16 seat `yes` hogs** | 54 ×3 + 18 | 59.9 → 83.3 | **54/54** |
| 3 | `ff30` | `--fixed-fps 30` | 54 ×3 + 18 + 4 r88 | 83.3 → 79.8 | **18/54** |
| 4 | `ff60` | `--fixed-fps 60` | 54 ×3 + 18 | 79.8 → 82.9 | **16/54** |
| 5 | `ff120` | `--fixed-fps 120` | 54 ×3 + 18 + 4 r88 | 82.0 → 83.3 | **14/54** |
| 6 | `ff1` | `--fixed-fps 1` | 36 ×2 + 18 | 92.9 → 74.1 | **30/36** |
| 7 | `maxfps30` | `--max-fps 30` (paced) | 36 ×2 + 18 + 4 r88 | 79.7 → 70.8 | **34/36** |
| 8 | `maxfps60` | `--max-fps 60` (paced) | 36 ×2 + 16 | 70.8 → 109.4 | **34/36** |
| 9 | `maxfps120` | `--max-fps 120` (paced) | 36 ×2 + 16 | 109.4 → 123.5 | **34/36** |
| 10 | `single` | `--single-threaded-scene` | 36 ×2 + 18 | 123.5 → 92.9 | **36/36** |
| 11 | `proj2d` | `physics/2d/run_on_separate_thread=true` | 36 ×2 + 18 | 139.1 → 92.9 | **36/36** |
| 12 | `ff30slow` | `--fixed-fps 30 --frame-delay 100` | 36 ×2 | 82.4 → 102.5 | **inert control, §2.3** |
| 13 | `pilot` | pre-freeze smoke | 9 | — | not part of the matrix |

Probe receipts are 8 arms ×2 reps (plus `firstlaw` ×2 in batches 1–7, 10–11). The 16 `r88`
receipts (4 modes × 2 variants × 2 reps) live inside `quiet/ff30/ff120/maxfps30` and are
counted in those rows. Batch totals: 76+72+76+72+76+54+58+52+52+54+54+36 = **732**
`rc`-bearing launches + 9 pilot = **741 fresh processes**.

Every launch is `timeout -s KILL 45`-bounded (never hit) and every receipt is
`runs/<mode>/r99b_<cell>.rep<N>.{out,err,rc}`. Probe receipts are
`runs/<mode>/r99b_probe_<arm>.rep<N>.{out,err,rc}` for
`modeinfo mixphase startphase peakphase mixfree finfree advfree splitcycle firstlaw`.
The `ff30slow`, `r88` and `firstlaw` receipts live in the same per-mode dirs.

### 0.1 Two process incidents (declared, receipts unaffected)

1. **Driver break.** `run_matrix.sh` was edited while the `quiet` batch was executing; bash
   re-reads a running script and aborted its **probe** phase (`line 75: ho: command not
   found`). All 18 quiet cells ×3 had already completed `rc=0` (verified: 18 logged `rc=[0 0 0]`
   lines, 54 `.out` files) and one `pause.rep3.rc` was left empty by the aborted write; the
   cell was re-run (`0 0 0`) and the quiet probe arms were re-run via `run_probes.sh quiet`.
   The quiet `rc-summary.txt` therefore lacks its `load_end` tail line. No other batch was
   affected — all later batches ran a frozen script. The one mid-flight edit that the running
   `load` batch did see (its `ARMS` list gained `splitcycle` between its cell phase and its
   probe phase) changed no cell receipt: all 54 load cell receipts completed `rc=0` before the
   edit and the probe phase simply ran the extra arm.
2. **Inert control.** `--frame-delay 100` is **ignored when `--fixed-fps` is active**
   (`--fixed-fps 30 --frame-delay 100` measures 112,982 fps; `--frame-delay 100` alone
   measures 9.9 fps). The intended `ff30slow` causal control therefore ran as a second ff30
   batch (§2.3) and is reported as a flag-interaction negative result, not as evidence.

---

## 1. Verdict table

| # | scout claim (`r99-scout.md`) | verdict | one-line evidence |
|---|---|---|---|
| 1 | §6.1 the 18 `ROWS`/`ROWS_PREFIX` are verbatim-ready: "147/147 receipts accepted, `rejected=[]`" | **CONFIRMED (own receipts) and reproduced by an independent replay [M]** | the frozen probe byte-copy replayed under the battery launch shape gives **54/54 quiet + 54/54 load** accepted with the production classifier; the labrat re-derived the scout's own claim independently: **147/147** signature hits, all `.rc`=`0`, only `gen` stderr non-empty (§10) |
| 2 | §5.1 "every block-sensitive wait in the frozen probe is wall-time based, **never a frame count**" | **REFUTED [A]** | the frozen probe's `_wait_ms(ms, cap=4000)` and its block loops are `wall AND frames < cap` (`audio_lattice.gd:74-79`, `:164` `frames<900`, `:239` `frames<3000`, `:276` `frames<800`, `:307` `frames<900`), and `_drain(30)` is frame-count-only. Under `--fixed-fps` the cap binds: 4000 frames = **17–40 ms** (§2) |
| 3 | §3.2 "headless process frames are ~147 fps" | **CONFIRMED in the default launch, but it is a mode fact, not a law [M]** | quiet/load/`single`/`proj2d` measure **148.9–149.8 fps**; `--fixed-fps 30/60/120` measure **102k–233k fps** (unpaced); `--max-fps 30/60/120` measure 34.7/64.9/124.8 fps; `--fixed-fps 1` 9.0k fps |
| 4 | §3.2 "the first readback after `play()` is exactly 128 frames (4/4 processes)" | **CONFIRMED and strengthened, with a scope note [M]** | 5 play/stop cycles × 2 reps × 11 modes: the immediate readback is always `0.0029025` (`imm_uniq=1`), even at 100k fps; **scope**: it is the LOOP_DISABLED / explicit-loop value — a `LOOP_FORWARD` stream with default points reads **1 sample** (`0.0000227`, `firstlaw`) |
| 5 | §3.2 "position advances in 4096-frame block steps; `block_jumps_ge6=true`" | **law CONFIRMED; the pinned `block_jumps_ge6` key REFUTED as a law [A]** | `advfree` `after=0.2815419` identical in **10/10** receipts across quiet/load/ff30/ff60/ff120; `period_is_block=true` 10/10. But `blocks_ge6` fails **cap-free** under unpaced modes: ff30 mixfree rep2 `hist={256:1,512:3,3584:3,3840:1,4096:4}` → `blocks=4` (§3) |
| 6 | §3.3 `finished` fires, "`fin_same_frame=true` in 9/9" | **law CONFIRMED; the pinned `fin_same_frame` key REFUTED as a law [A]** | `finfree` `stopped/finished_seen/played_gt_02` true 10/10 across modes, but `fin_same_frame=false` in 1/2 ff30 and 1/2 ff120 cap-free receipts (signal frame vs observed transition frame off by one at ~100k fps) |
| 7 | §3.4 `LOOP_FORWARD` default points self-terminate; explicit points wrap | **CONFIRMED; unpaced failures are cap-bound [M]** | quiet/load 3/3 each; under ff modes the 800/900-frame caps (= 8–9 ms) fire before any wrap: `playing_end=true pos_end=0.0000227` while `maxpos_lt_001=true` still holds |
| 8 | §3.5 generator capacity `next_pow2(bl·rate)−1`, `clear_buffer()` refused | **CONFIRMED in every mode [M]** | `caps=["4095","8191","16383"] pushed=8191 avail_full=0 full_refused=true clear_noop_active/stopped=true` are synchronous keys and hold in all 11 modes; only `skips_dry_gt0` moves (cap-bound: ff30 rep1 `skips_dry=0 avail_stopped=512`) |
| 9 | §3.6 peaks are live per block and lag one block; "wait ≥300 ms" | **CONFIRMED and sharpened to the mix boundary [M]** | `peakphase`: onset 6–100 ms (first mix boundary after `play()`), clear 66–100 ms after `stop()` (first boundary after stop) — in **every** mode; the meter **holds** the last block's value until the next mix, so the minimum wait is one block (~92.9 ms), not a fixed 300 ms |
| 10 | §3.7 bus routing / invalid-name fallback | **CONFIRMED in every mode [M]** | `bus` is accepted 3/3 (quiet/load/ff30/ff60/ff120) and 2/2 (paced/thread modes) — one of only 4 cells that survive `--fixed-fps` |
| 11 | §3.8 polyphony: new voice per `play()`, newest tracked, older advance | **law CONFIRMED quiet/load; unpaced flips are cap-bound [M]** | quiet/load 3/3; ff modes read `older_advanced=false` because the 300 ms waits collapse to ~40 ms (no block boundary between reads) — the tails show positions frozen at `0.0957823` |
| 12 | §3.9 2D attenuation `1−d/max_distance`, pan `clamp(x/128,±0.5)·ps` | **law CONFIRMED quiet/load; unpaced lattice is read early [M]** | quiet/load 3/3 each; ff modes flip the dB keys but `maxd_independent=true` holds everywhere — the lattice is intact, the 300/400 ms settling waits are truncated |
| 13 | §3.10 autoplay starts on the first frame; `stop()` zeroes the position | **CONFIRMED in every mode [M]** | `autoplay` and `stoppos` accepted 3/3 + 2/2 + 2/2 in all 11 modes (only `pause` moves, cap-bound) |
| 14 | §3.11 the r88 causal repro: verbatim reproduces the null, `loop_end=4410` flips it | **CONFIRMED at paced rates; REFUTED as mode-invariant [A]** | quiet: verbatim `playing=false pos=0.000 peaks=[-200×4]` / fixloop `playing=true pos=0.096 peaks=[-200,-6.02,…]`; maxfps30: same flip; **ff30/ff120: verbatim `playing=true pos=0.000`** (the 20-frame window is 0.2 ms — no mix yet) (§5) |
| 15 | §5.11 "freeing a player without draining frames leaks; drain ≥2 frames" | **REFUTED as a frame-count rule [A]** | quiet/load/paced/`single`/`proj2d`: 0 leak warnings; ff30/60/120: **31–32/54** receipts carry `WARNING: 2 ObjectDB instances were leaked at exit` with `_drain(30)` (= 0.3 ms there); ff1 20/36 |
| 16 | §5.1's advice "pin the laws, not just the values" (§6.2) | **CONFIRMED with a correction [M]** | `census`'s `max_fps=0` is a **mode-coupled** value: `--max-fps N` makes it `max_fps=30/60/120` (census 0/2 in all three paced batches); `--fixed-fps` does **not** touch it (census 3/3 in ff30/60/120) |
| 17 | (new) the row lattice under threaded physics / scene threading | **NO EFFECT — negative controls pass [M]** | `proj2d` (`physics/2d/run_on_separate_thread=true`, verified in-receipt) **36/36**; `--single-threaded-scene` **36/36**; both also keep `mix_period=0.092880` and `meas_fps≈149` |
| 18 | (new) an r95-style k(k−1) cycle in the audio lattice | **NO CYCLE FOUND [A]** | `splitcycle` (1.5 s window, every delta recorded): quiet/load/maxfps120/ff1 → 16–18 changes, **all exactly 4096**; ff30 → 21 changes with intermittent single splits (`1536+2560`, `256+3840`, `512+3584`) — every delta is a 128-multiple, every split sums to 4096, no periodic split point |

---

## 2. Headline 1 — `--fixed-fps` disables real-time synchronization, so the frozen probe's frame caps become the binding clock

### 2.1 The measurement

`godot --help` documents `--fixed-fps <fps>` as *"Force a fixed number of frames per second.
This setting **disables real-time synchronization**."* Measured with the `modeinfo` arm
(400 ms wall window):

| mode | `Engine.max_fps` | frames / 400 ms | measured fps | physics steps / frame |
|---|---|---|---|---|
| `quiet` | 0 | 60 | **149.8** | 2.40 |
| `load` (16 hogs) | 0 | 60 | **149.8** | 2.31 |
| `ff30` | 0 | 3999 | **112,603** | 0.50 |
| `ff60` | 0 | 3999 | **102,644** | 1.00 |
| `ff120` | 0 | 3999 | **110,622** | 2.00 |
| `ff1` | 0 | 3603 | **9,007** | 0.02 |
| `maxfps30` | 30 | 14 | 34.7 | 0.54 |
| `maxfps60` | 60 | 26 | 64.9 | 0.96 |
| `maxfps120` | 120 | 50 | 124.8 | 1.92 |
| `single` | 0 | 60 | 149.7 | 2.40 |
| `proj2d` | 0 | 60 | 148.9 | 2.40 |

So the `--fixed-fps` value is a **delta**, not a pace: the loop runs flat out (one rep reached
233,232 fps). `--max-fps` is the paced variant and *is* honored.

### 2.2 Consequence for the frozen probe

`_wait_ms(400, cap=4000)` returns after **~40 ms** under ff30 (not 400 ms); `_drain(30)` takes
**0.3 ms**; the block loops hit `frames=900` / `frames=3000` after 8–30 ms. Every cell whose
measurement needs wall time therefore reads a *pre-settled* world. Verbatim:

```
runs/ff30/r99b_mixblock.rep1.out:
PASS r99_audio mixblock q_frames=128 jump_frames=4096 jump6=0.092880 first=0.002902494
first_is_q=true all_jumps_q=true block_jumps_ge6=false period_is_block=true |
jumps=0 block_jumps=0 jmin=999.000000000 jmax=0.000000000 wall_max=0.0000 frames=900

runs/ff120/r99b_finish.rep1.out:
PASS r99_audio finish stopped=false playing_end=true pos_end=0.0029025 finished_seen=false
fin_frame_ge_1=false fin_same_frame=true played_gt_02=false |
transition_f=-1 fin_frame=-1 fin_us=-579882 last_pos=0.0029025 frames=3000

runs/ff30/r99b_bus_peak.rep1.out:
PASS r99_audio bus_peak live_gt_neg20=false idle_is_minus200=true live_gt_idle=false |
live=-200.00 idle=-12.04 pos_live=0.0957823        (live/idle inverted: both windows truncated)

runs/ff30/r99b_advance.rep1.out:
PASS r99_audio advance ... pos_after_gt_before=false | before=0.0029025 after=0.0029025
```

### 2.3 The failure set is a frame-budget race, not a semantic mode difference

The three controls that separate "unpaced" from "frame rate" and "law" from "budget":

1. **Cap-free re-implementations of the three worst-affected cells hold the laws in every
   mode** (own probe, wall-time bound only, no frame cap):

   | arm | quiet | load | ff30 | ff60 | ff120 |
   |---|---|---|---|---|---|
   | `mixfree` `first` / `all_jumps_q` / `period_is_block` | 128 / true / true | 128 / true / true | 128 / true / true | 128 / true / true | 128 / true / true |
   | `finfree` `stopped` / `finished_seen` / `played_gt_02` | true | true | true (2/2) | true | true |
   | `advfree` `after` (300 ms wall) | 0.2815419 | 0.2815419 | **0.2815419** | **0.2815419** | **0.2815419** |

   `advfree`'s `after` is **byte-identical in 10/10 receipts across five modes** — the
   position law is wall-clock exact; only the frozen probe's frame budget differs.

2. **The paced `--max-fps` modes pass everything except the census key.** `maxfps30/60/120`:
   **34/36** each; the only rejected row is `census` (`max_fps=30/60/120` vs the pinned
   `max_fps=0`). Same frame rates as `--fixed-fps 30/60/120`, same wall-time windows → all 17
   other cells hold. **The frame rate is not the variable; the lack of real-time
   synchronization is.**

3. **The failure count scales with the achieved frame rate.** `ff1` runs at 9,007–12,980 fps
   (its 4000-frame `_wait_ms` cap is 308–444 ms, just above the 300–400 ms wall bounds, so the
   wall windows survive) and fails exactly **3/18 cells** — and precisely the three whose
   tighter frame caps still bind: `mixblock` (`frames<900` = 69–100 ms), `finish`
   (`frames<3000` = 231–333 ms), `loop_pts` (`frames<900` = 69–100 ms). At 100k+ fps the same
   caps cover 8–36 ms and 14–16 cells break. A semantic change in the audio server would not
   produce this gradient.

4. **The `--fixed-fps` modes' failures are also rep-unstable** (`advance` 1/3, `gen` 2/3,
   `loop_degenerate` 1/3, `pause` 1–2/3) — a race signature, not a deterministic mode law.

The `ff30slow` control intended to prove this directly **failed as a control**:
`--frame-delay 100` is inert under `--fixed-fps` (112,982 fps measured; §0.1-2), and its 36
receipts are byte-indistinguishable from plain `ff30` in kind (`block_jumps_ge6=false`,
`frames=900`, truncated peaks). It is kept as the flag-interaction record.

---

## 3. Headline 2 — two pinned keys are polling-rate-coupled *observations*, not laws

### 3.1 `block_jumps_ge6` — the block update can be seen split in two

The position readback is an **asynchronously updated** value: a same-frame 3 ms busy-wait can
observe a full `+4096` between two reads (`mixphase` `intra=["0","0","4096","0","0"]`), and a
readback inside a block is constant (`trace=["1:128:60429",…,"6:128:88074","7:4224:2075",…]`:
128 frames held for a whole block, then +4096).

When the poll interval is µs-scale (unpaced modes), the update at one mix boundary can be
**observed as two sub-publishes** whose sizes are 128-multiples summing to 4096:

```
runs/ff30/r99b_probe_mixfree.rep1.out  hist={512:1,3584:1,4096:7}  blocks_ge6=true   frames=95467
runs/ff30/r99b_probe_mixfree.rep2.out  hist={256:1,512:3,3584:3,3840:1,4096:4}  blocks_ge6=false  frames=50242
runs/ff120/r99b_probe_mixfree.rep1.out hist={128:1,512:4,3584:4,3968:1,4096:3}  blocks_ge6=false
runs/ff60/r99b_probe_mixfree.rep2.out  hist={256:2,384:1,3712:1,3840:2,4096:5}  blocks_ge6=false
runs/quiet/r99b_probe_mixfree.rep1.out hist={4096:8}  blocks_ge6=true   (rep2 {4096:7}; load {4096:8} both reps)
```

- `all_jumps_q=true` in **10/10** cap-free receipts — every observed delta is a 128-multiple;
- the clean-4096 count is **3–8** cap-free under unpaced modes (3/10 receipts below the pinned
  threshold of 6: ff30 rep2=4, ff60 rep2=5, ff120 rep1=3) and **7–8** at every paced rate;
- the split point is not periodic (`splitcycle` ff30: `1536+2560`, `256+3840`, `512+3584`,
  `512+3584`, `512+3584` — 21 changes, no cycle; quiet/load/maxfps120/ff1: 16–18 changes, all
  exactly 4096).

**The law is "all updates are 128-multiples; the total advance is wall-paced". The pinned
`block_jumps_ge6=true` is a statement about the observer's frame rate, not about the clock.**

### 3.2 `fin_same_frame` — off by one when the poller is faster than the audio thread

`finfree` (cap-free, wall-bounded):

```
quiet  transition_f=51 fin_frame=51 fin_same_frame=true   fin_us=338183
load   transition_f=55 fin_frame=55 fin_same_frame=true   fin_us=365782
ff30   transition_f=24129 fin_frame=24128 fin_same_frame=false  fin_us=295813   <- off by one
ff120  transition_f=34887 fin_frame=34886 fin_same_frame=false  fin_us=370439   <- off by one
```

The `finished` signal and the `playing→false` flip land in *adjacent* frames when frames are
~10 µs apart; at 150 fps (and at every paced rate) they land in the same frame — which is why
the scout's 9/9 holds. The pinned key is again an observation statistic; the law (signal fires
at stream end, position resets to 0) is confirmed in 10/10 receipts.

### 3.3 Latent fragility of `period_is_block`

One `modeinfo` receipt read `mix_period=0.000000` under ff30 (`win_frames=3999`,
`meas_fps=233232`) — i.e. `get_time_since_last_mix()+get_time_to_next_mix()` returned 0.0 at
that instant, which would flip the pinned `period_is_block=true` to false if a `mixblock`
receipt ever sampled there. Not observed in any of the 54 mixblock receipts, but it is a
snapshot race worth knowing: the key compares a two-timestamp sum against the block period.

---

## 4. Mechanism measurements (own probe) — what the lattice's observables actually are

All of these are mode-invariant unless noted; receipts `runs/<mode>/r99b_probe_*`.

| arm | observation | quiet | ff30 | ff60 | ff120 | paced modes |
|---|---|---|---|---|---|---|
| `startphase` | immediate readback after `play()` ×5 cycles | `0.0029025` ×5 (`imm_uniq=1`) | same | same | same | same (all 11 modes) |
| `startphase` | one frame later | 128 | 128 | 128 | 128 | **load rep2: `0.0957823` twice** — a whole block can complete inside one frame under load |
| `firstlaw` | LOOP_DISABLED / `fwd0` / `fwd4410` immediate readback | `0.0029025` / `0.0000227` / `0.0029025` | same | same | same | same (all 9 modes) |
| `firstlaw` | same, after 150 ms | `0.1886621,true` / `0.0000000,false` / `0.0886621,true` | pre-mix values (window 0.2 ms) | pre-mix | pre-mix | same as quiet |
| `peakphase` | first live bus peak after `play()` | 28 ms / 6 ms | 69 / 18 ms | 38 / 78 ms | 41 / 45 ms | maxfps30 66 / 100 ms |
| `peakphase` | peak clears to −200 after `stop()` | 88 / 96 ms | 90 / 95 ms | 94 / 96 ms | 97 / 100 ms | maxfps30 99 / 66 ms |
| `splitcycle` | deltas over 1.5 s | 17×4096 | 21 changes, 5 splits | 17 changes, 1 split | 16×4096 | maxfps120 17×4096, ff1 18×4096 |

- The **128-frame first readback is set at `play()`** (immediate, even at 100k fps, and on the
  5th play/stop cycle in the same process) — but only for non-degenerate streams; a
  `LOOP_FORWARD` stream with default points reads **1 sample** (`0.0000227`, the same value
  the `loop_degenerate` cell pins as `maxpos`).
- The **bus peak is a held per-block value**: it turns live at the first mix boundary after
  `play()` (≤ one block) and stays live until the first boundary after `stop()` (≤ one block +
  margin) — 88–100 ms measured in every mode. The scout's "wait ≥300 ms" is safe; the floor is
  one block (~92.9 ms).
- **No cycle**: the position sequence is a block-periodic 4096 advance with occasional
  single splits; the split point does not repeat with any period observed (no r95-style
  k(k−1) pattern).

---

## 5. The r88 causal repro under modes — the null reproduces only when 20 frames span a mix block

The scout's own repro (`corpus/live/r99-scout/proj/r88_audio_repro.gd`, sha256
`ac2c672e10e94e89…`) re-run with the scout's launch shape (`--arm audio_pos` before
`--script`, `--fix-loop` as a user arg):

| mode | verbatim (default loop points) | `--fix-loop` (`loop_end=4410`) |
|---|---|---|
| `quiet` | `playing=false pos=0.000 peaks_near=[-200.00×4]` (r88's null, byte-for-byte) | `playing=true pos=0.096 peaks_near=[-200.00,-6.02,-6.02,-6.02]` (live) |
| `maxfps30` | `playing=false pos=0.000 peaks=[-200.00×4]` | `playing=true pos=0.060 peaks=[-6.02×4]` |
| `ff30` | **`playing=true pos=0.000 peaks=[-200.00×4]`** | `playing=true pos=0.003 peaks=[-200.00×4]` |
| `ff120` | **`playing=true pos=0.000 peaks=[-200.00×4]`** | `playing=true pos=0.003 peaks=[-200.00×4]` |

- **At paced rates the scout's causal attribution replicates** (independent seat, 2/2 each):
  the verbatim arm reproduces r88's exact null line, and the one-line `loop_end` fix flips the
  identical probe to a live surface. The peak sample in which the meter turns live varies with
  mix-block phase (exactly as the scout's §3.11 predicted).
- **Under `--fixed-fps` the repro loses its discriminating power**: its 20-frame window is
  0.2 ms, so *no* mix has happened and both variants print `playing=true`; the null signature
  (`playing=false`) is only reproducible when 20 frames ≥ one mix block (~92.9 ms), i.e. at
  ≤ ~215 fps. This bounds the repro's validity, it does not weaken the attribution.

---

## 6. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | "the frozen probe's block-sensitive waits are wall-time based, never a frame count" | **REFUTED [A]** — `_wait_ms(ms, cap=4000)` + `frames<900/3000/800` co-bounds; under `--fixed-fps` the cap binds (4000 frames = 17–40 ms) and 14–16/18 cells flip |
| F2 | "`block_jumps_ge6=true` is a law of the audio clock" | **REFUTED [A]** — cap-free unpaced receipts show 3–7 clean 4096-jumps in the same 700 ms (`blocks_ge6=false` in 3/10); the block update is observed split (`m·128 + (4096−m·128)`) when polls are µs-scale |
| F3 | "`fin_same_frame=true` is a law" | **REFUTED [A]** — off by one in 1/2 ff30 and 1/2 ff120 cap-free receipts; the law (signal at stream end, `pos→0`) holds 10/10 |
| F4 | "the 18 rows are launch-mode portable" | **REFUTED for `--fixed-fps` [A]** (18/54, 16/54, 14/54) — but the cause is the probe's frame budget, not the audio semantics; **CONFIRMED for quiet/load/paced `--max-fps`/`--single-threaded-scene`/threaded physics** (54/54, 54/54, 34/36 each, 36/36, 36/36) |
| F5 | "the census row pins a mode-invariant `max_fps=0`" | **REFUTED for `--max-fps N` [A]** — `Engine.max_fps` reads 30/60/120; census 0/2 in all three paced batches (`--fixed-fps` does not touch it) |
| F6 | "`_drain(≥2 frames)` prevents the ObjectDB leak warning" | **REFUTED as a frame-count rule [A]** — `_drain(30)` leaks 31–32/54 receipts under ff30/60/120 (0.3 ms) and 20/36 under ff1; 0 under every paced/thread mode |
| F7 | "the first readback after `play()` is 128 frames for every stream" | **REFUTED in scope [A]** — true for LOOP_DISABLED and explicit-loop streams (all 9 modes, 5 cycles each); a default-points `LOOP_FORWARD` stream reads `0.0000227` (1 sample) |
| F8 | "the r88 repro's verbatim arm reproduces the null in any launch mode" | **REFUTED [A]** — under ff30/ff120 both variants print `playing=true`; the repro is a paced-mode instrument |
| F9 | "an r95-style k(k−1) cycle exists in the position lattice" | **NOT FOUND [A]** — 1.5 s delta traces are block-periodic 4096 with intermittent single splits; no repeating split point (quiet/load/maxfps120/ff1: zero splits) |
| F10 | "`--frame-delay` slows the loop for a cap control" | **REFUTED [A]** — inert under `--fixed-fps` (112,982 fps); honored alone (9.9 fps) |

---

## 7. What this means for the author (additions to scout §5)

1. **The rows are correct where the battery runs** — `run_battery.py:730` launches
   `[godot, "--headless", "--path", scratch, "--script", …, "--", *flags]` with **no
   `--fixed-fps`/`--max-fps`**, i.e. the paced 149.8 fps regime where all 54 quiet + 54 load
   receipts pass. Do not "fix" the rows for `--fixed-fps`; record the scope instead.
2. **Do not treat `block_jumps_ge6` as a clock law.** If a future cell must be robust under
   arbitrary frame budgets, count *block boundaries* by wall time (e.g. `Δpos/4096` with a
   tolerance, or count changes that are multiples of 4096 within a wall window) rather than
   counting exact-4096 deltas at an unstated poll rate. The `all_jumps_q` key *is* a law.
3. **Do not treat `fin_same_frame` as a clock law.** The observable law is
   `finished_seen=true` + `pos_end=0` + `played_gt_02`; same-frame coincidence is an
   artifact of the 150 fps poll.
4. **`census.max_fps` mirrors `--max-fps`** — if a future launch shape adds `--max-fps`,
   the census row must not pin `max_fps=0` (pin the launch-shape fact explicitly, or drop the
   key).
5. **Drain/leak hygiene is wall-time coupled.** `_drain(N)` frames is not enough when frames
   are cheap; budget one mix block (~93 ms) before `free()`/exit, or accept the warning.
6. **Peak settling is one mix block, not 300 ms** — keep the scout's conservative waits in
   the frozen probe, but author probes can settle in ~100 ms.
7. **`--fixed-fps` is not a frame-rate axis.** Anyone repeating this attack should use
   `--max-fps` for "paced at N fps" and `--fixed-fps` for "unpaced fixed delta"; mixing them
   up produces a harness artifact, as `ff30slow` shows.

---

## 8. Remaining unknowns / not measured

- **Mechanism of the sub-publish split** (why one block update can appear as `m·128` then
  `(4096−m·128)`, µs apart) — measured, not explained; **[I]** (no engine source on this host).
- **`period_is_block`'s race window** — one `mix_period=0.000000` snapshot observed; the exact
  instant that produces it was not isolated.
- **`--fixed-fps` + `--frame-delay` interaction** — measured inert; the engine-side reason is
  **[I]** (likely `--fixed-fps` taking the timing path before the delay).
- **`pitch_scale` ratio, `max_polyphony` > 3 voice eviction, `Area2D` audio overrides,
  `AudioEffect` DSP response, non-Dummy drivers** — still unmeasured (scout §7 stands).
- **Paced modes below 30 fps** — `--frame-delay 100` alone (9.9 fps) was identified as the
  instrument but not run against the 18 cells (out of the assigned axis).
- **Windows/macOS hosts** — every value is this host/build/`--headless`/Dummy/44100 Hz.

---

## 9. Host hygiene

- **741 bounded launches** (732 with `.rc` + 9 pilot), all `--headless`, all
  `timeout -s KILL 45`-bounded (none hit), no run left running; this lane's own PIDs only.
- Loadtest hogs: 16 own `yes` processes started and **only their own PIDs killed** (PID array
  + trap; `own_hogs_killed=16`, `host_yes_after_kill=80`; never `pkill`).
- **No tracked file written, no commit**: `git status --porcelain` shows only the
  pre-existing concurrent-lane ` M corpus/fixtures/run_battery.py` plus untracked churn; all
  writes are under `corpus/live/r99-boundary/` and this report.
- `manifest.sha256` (2256 lines, `sha256sum -c` → 2256/2256 OK) covers every artefact under
  `corpus/live/r99-boundary/`.
- The lane's own `proj/` and `proj2d/` contain byte-copies of the fixture `project.godot`
  (`8de8b3af…`) and of the frozen scout probe (`165571c4…`); `proj2d` adds only the
  `[physics] 2d/run_on_separate_thread=true` line (`eb2bda39…`).

## 10. Delegated probe (frozen `probeParent`, one dispatch)

The one permitted read-only `ufo-labrat` was dispatched once with a bounded documentary
hypothesis: *"every one of the 18 `ROWS_PREFIX` signatures appears in ≥1 canonical and ≥1
loadtest receipt; every `.rc` is `0`; every `.err` is empty except `gen`'s, whose only ERROR
lines are `ERROR: Condition "active" is true.`"* It reported **H CONFIRMED** (no shell/exec in
its substrate; read/grep only): **147/147** signature hits (93 canonical + 54 loadtest, line 3
of every `.out`), 153 `.rc` files all exactly `0` (147 in scope + 6 out-of-scope r88-repro),
and the only in-scope non-empty stderr files are the 9 `gen` receipts — each 9 lines: two
`ERROR: Condition "active" is true.` lines plus `at: clear_buffer
(servers/audio/effects/audio_stream_generator.cpp:166)` and GDScript backtraces. Its one
nuance: the scout's phrase "the only line" is imprecise (the `.err` is 9 lines, not 1). This
is an independent re-derivation of the scout's 147/147 claim from the receipts on disk.

## 11. Blockers / caveats

- **No blockers.** The assigned attack (quiet + load + `--fixed-fps` 30/60/120 + threaded
  physics, multiple fresh processes) is complete and the lattice verdict is reproducible from
  the receipts with `python3 analyze_r99b.py`.
- **Caveat 1**: the quiet batch's driver was edited mid-run and aborted its probe phase; all
  54 cell receipts predate the break and are `rc=0`, the one empty `pause.rep3.rc` was
  re-run, and the quiet probe arms were re-run (`runs/quiet/probe-summary.txt`).
- **Caveat 2**: `ff30slow` is an inert control (`--frame-delay` under `--fixed-fps`), kept as
  the flag-interaction record; the causal claim rests on the cap-free arms, the paced modes,
  and the ff1 gradient.
- **Caveat 3**: `r99b_modes.gd` was extended additively during the session (mixfree hist
  instrumentation before the matrix; `splitcycle` before the quiet probe re-run; `firstlaw`
  after the matrix). No arm's behavior changed after its first canonical receipt; per-arm
  receipt availability is noted in §0.

---

## 12. Evidence index

All under `corpus/live/r99-boundary/`; `manifest.sha256` covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| frozen scout probe, byte-copy | `probes/audio_lattice.gd` (= `proj/audio_lattice.gd`) | `165571c410d506f1` |
| own mode/phase probe (11 arms) | `probes/r99b_modes.gd` | `b680e6f297b7534d` |
| launch project (fixture byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| threaded-physics launch project | `proj2d/project.godot` | `eb2bda39ce82cd5a` |
| matrix driver / probe driver | `run_matrix.sh` / `run_probes.sh` | `3235113522abd99e` / `0701606900ca285a` |
| r88 repro driver / inert-control driver | `run_r88.sh` / `run_ffslow.sh` | `cc56c2d1db94c543` / `ff2959e25d8065c2` |
| analyzer (production classifier, AST) | `analyze_r99b.py` → `runs/analyze_r99b.json` | `fe01c1ad9f9c8e1b` |
| r88 repro probe (scout's, byte-copy) | `proj/r88_audio_repro.gd` | `ac2c672e10e94e89` |
| per-mode cell receipts | `runs/<mode>/r99b_<cell>.rep*.{out,err,rc}` | `manifest.sha256` |
| per-mode probe receipts | `runs/<mode>/r99b_probe_<arm>.rep*.{out,err,rc}` | `manifest.sha256` |
| batch summaries | `runs/<mode>/rc-summary.txt`, `runs/<mode>/probe-summary.txt`, `runs/<mode>/r88-summary.txt` | `manifest.sha256` |
| logs | `runs/matrix.log`, `runs/extra.log`, `runs/control.log` | `manifest.sha256` |

Reproduce: `bash run_matrix.sh quiet 3 && bash run_matrix.sh load 3 &&
bash run_matrix.sh ff30 3 && bash run_matrix.sh ff60 3 && bash run_matrix.sh ff120 3 &&
bash run_probes.sh quiet 2 && … && python3 analyze_r99b.py` — expect
`quiet 54/54`, `load 54/54`, `ff30 18/54`, `ff60 16/54`, `ff120 14/54`,
`maxfps30/60/120 34/36`, `single 36/36`, `proj2d 36/36`, `ff1 30/36`,
`segment_sha=749fa060…`, and the `ff30slow`/`r88`/`firstlaw` receipts as described above.
