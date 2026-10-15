# game-dev-2d round 100 — boundary (r100-boundary): the 14 GUI rows are **byte-portable across quiet / 16-hog load / `--fixed-fps` 30·60·120 / threaded physics** (356 fresh processes, 210/210 production-classifier accepts, byte-identical to the scout's committed receipts); the parse→cursor write is **FLUSH-GATED** (applied before the `process_frame` signal), the drag threshold is **|Σ relative| > 10** (the scout's "accumulated |relative|" wording **REFUTED**), and the rows are **single-cell-per-process only** (cursor + emulated-button state leak across cells even with cleanup)

Seat `BOUNDARY` (LEAF; frozen `probeParent` — one read-only `labrat` dispatch, §9) | lane
`r100-boundary` | round 100 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
`DisplayServer.get_name() == "headless"`, root viewport **64×64**, 60 tps, `RendererDummy`.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start **`3fd8512`** (*r97
boundary*); HEAD at session end **`caa43a5`** (*r96 boundary* — a concurrent lane committed
while this seat ran; that commit touches neither this seat's artefacts nor the frozen probe).

Attack corpus: **356 fresh Godot processes, 13 batches, all `rc=0`, 0 timeouts, 0 tracked
writes** (210 matrix runs on the frozen scout probe `r100_gui.gd` sha256 `dd826f6e…`, 143
artifact-probe runs on `r100b_phase.gd`/`r100b_seq.gd`, 3 one-off mode/state receipts).
Every matrix receipt is `timeout -s KILL 25`-bounded (the bound was never hit; slowest run
1504 ms). Writes are this report (new, untracked) and `corpus/live/r100-boundary/**` only;
`git status --porcelain` shows only the pre-existing ` M corpus/fixtures/run_battery.py`
(a concurrent lane's, present before this session) plus untracked churn. `git ls-files`
confirms `reports/round-100/r100-boundary.md` is not a tracked path and the receipts live
under the already-ignored `corpus/live/**/runs/` pattern (same as r95/r97).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on
this host; `definition`/`references`/`hover` were **unavailable for every file**. No
rename/symbol work was required — the attack is behavioral and every statement below is
grounded in receipt text or in probe source read directly. Mechanism statements are marked
**[I]** and kept separate from the measurements.

**The host is shared.** loadavg 57 → 83 for the whole session (other lanes' `yes` blocks:
**48 → 80 host hogs**). `quiet` below means **"no hogs added by this seat"**, never an idle
host. The `load` batches added exactly **16 own `yes` hogs** (task floor ≥ 12), tracked by
PID and killed by PID via the driver's EXIT trap: the host `yes` count was unchanged across
every load batch (64 → 64 and 80 → 80), i.e. no foreign process was ever killed (never
`pkill`).

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[A]** refutation/ablation; **[I]** inference; **[?]** unknown.

---

## 0. What I ran

| # | batch | conditions | runs | loadavg (start→end) |
|---|---|---|---|---|
| 1 | `quiet` | 60 tps, no seat hogs | 42 | 57.5 → 57.5 |
| 2 | `load` | 60 tps + **16 seat hogs** | 42 | 57.3 → 63.8 |
| 3 | `ff30` | `--fixed-fps 30` | 28 | 63.8 → 62.5 |
| 4 | `ff60` | `--fixed-fps 60` | 28 | 62.5 → 64.1 |
| 5 | `ff120` | `--fixed-fps 120` | 28 | 64.1 → 61.9 |
| 6 | `thr` | `physics/2d/run_on_separate_thread=true` (`proj_thr/`) | 28 | 61.9 → 59.1 |
| 7 | `ff1` | `--fixed-fps 1` (extra ratio extreme) | 14 | 59.1 → 61.2 |
| 8–13 | probe batches | arms below × {quiet 3 reps, other modes 2 reps} | 143 | 62.9 → 83.3 |
| 14 | meta/one-off | project-mode evidence + emulation state | 3 | — |

**Matrix = the scout's exact launch shape** (`godot --headless [--fixed-fps N] --path proj
--script res://r100_gui.gd -- --arm=<cell>`), 14 cells × fresh process per rep (quiet 3,
load 3, ff 2, ff1 1). The launched `r100_gui.gd` is the **byte-frozen scout probe**
(`dd826f6e7b74ba62fcfd175ab7a1cf0c40fd9712de4b33a18554930cf6dad073`); the launch
`project.godot` is the byte-copy of `corpus/fixtures/project.godot` (`8de8b3af…`).
`proj_thr/` is the same project plus `[physics] 2d/run_on_separate_thread=true`; a one-off
probe prints `META sep2d=true` there and `sep2d=false` on `proj` (`runs/probes/meta/`), so
the `thr` batch is self-documenting rather than assumed.

**Probe arms** (`probes/r100b_phase.gd`, hash in `RECEIPTS.md`) — one arm per process:
`cursorphase` (cursor write phase), `hoverphase` (hover pick phase), `dragphase` (threshold
accumulation model, same-frame vs cross-frame, relative vs position), `coalesce` (parsed
motion buffering), `velphase` (`Input.get_last_mouse_velocity` phases), `startup`
(frame-shape/startup state), `flushpos` (where the implicit flush sits in the frame),
`orderin` (interleaved `_input`/`_gui_input` order), `dblclick` (engine-computed
double-click?). Plus `probes/r100b_seq.gd` (built by `make_seq.py` from the frozen scout
probe: all 14 cells in one process, `--clean=0/1`) and two one-off probes
(`r100b_meta.gd`, `r100b_emul.gd`).

**Receipt census [M]:** every matrix cell is `out_uniq=1 err_uniq=1 rc=[0] pass_uniq=1`
within each mode and the payload is **byte-identical across all 7 modes** (§3). Every
artifact arm is byte-stable per mode and cross-mode identical except `startup`, which is
deliberately unstable (it prints wall-clock `t=` and frame counters); its *shape* tokens are
analyzed in §7. Matrix stderr is only `render`'s deterministic 246 B dummy-texture ERROR —
**byte-identical in all 7 modes** (sha `bdf7239f52edc2b3…` truncated). Probe stderr is
empty except the two `seq` arms (293/296 B: the same dummy-texture ERROR with the seq
script's own backtrace).

---

## 1. Verdict table

| # | scout claim (r100-scout.md) | verdict | one-line evidence |
|---|---|---|---|
| 1 | L1 STOP/IGNORE/PASS routing matrix + `set_input_as_handled` | **CONFIRMED, extended [M]** | `routing` payload byte-identical in 7 modes; `orderin` adds the unmeasured delivery order: `_input` runs **before** `_gui_input` for press/motion/key/touch, so a `_gui_input`-side `set_input_as_handled` cannot suppress the `_input` copy |
| 2 | L2 `push_input` is a scene-tree injection (no `Input` state, no cursor; does update hover) | **CONFIRMED, and the hover half is synchronous [M]** | `routing s10`/`motion m4`/`cursor` rows portable; `hoverphase h_imm=A ev=[in@0]` — the pick and `mouse_entered` fire inside the `push_input` call, not at a frame boundary |
| 3 | L3 the cursor is written only by `Input.parse_input_event`, from `global_position` | **OBSERVABLE CONFIRMED; MECHANISM REWORDED — the write is FLUSH-GATED [A]** | `cursorphase`: right after `parse_input_event` the cursor is still `(0,0)` and `held=0`; `Input.flush_buffered_events()` → `(20,20)`/`held=1`. `flushpos`: the `process_frame` listener sees the parsed value (`sig@1=(20,20)`) — the implicit flush runs **before** the signal (r97's pattern) |
| 4 | L4 `event.position` is control-local; `get_*_mouse_position()` helpers are cursor-derived | **CONFIRMED [M]** | `localpos` row byte-identical in 7 modes (`loc_c=-24.0,-12.0` stale under push; `6.0,2.0` after parse) |
| 5 | L5 hover is clipped to the viewport rect; button routing is not | **CONFIRMED [M]** | `clip` row byte-identical in 7 modes (half-open rect; `FA` reachable by press, never hovered) |
| 6 | L6 drag start = **accumulated `|relative|` > 10** on a motion whose own `button_mask` has LEFT | **REFUTED as worded [A]** | `dp_sign_same drag=0` (rel `+6` then `−6`: Σ|rel| = 12 but net = 0 → no drag) and `dp_rel_only drag=1` (rel 30 with the event's position unchanged) and `dp_pos_only drag=0` (position 40, rel 0): the threshold is **|Σ relative| > 10**; position fields are ignored; accumulation is per delivered event, not per frame (`dp_sameframe == dp_multiframe == [1:0 2:1 3:1]`) |
| 7 | L7 drop target = hover-picked; `can`/`drop` callback sequence | **CONFIRMED [M]** | `drag` row byte-identical in 7 modes |
| 8 | L8 touch is positional/tracked (`ScreenDrag` advances by `relative`) | **CONFIRMED, state machine added [M]** | `touch` row portable; one-off `r100b_emul`: parsed touch press → `held=1`, release → `held=0`, second press → `held=1` (emulated button state is set/cleared by parsed touches) |
| 9 | L9 both emulation directions work headless; touch→mouse on by default | **CONFIRMED [M]** | `touch`/`census` rows portable in 7 modes; `emul_mouse=1` in every mode |
| 10 | L10 SubViewports own their input state and are isolated from root `push_input` | **CONFIRMED [M]** | `subvp` row byte-identical in 7 modes |
| 11 | L11 warp APIs and the OS cursor are inert headless | **CONFIRMED [M]** | `warp` row byte-identical in 7 modes |
| 12 | L12 focus owns key delivery; `_gui_input` and `_input` both see the key | **CONFIRMED [M]** | `focus` row portable; `orderin key[i:…|g:…]` |
| 13 | L13 the render surface is headless-null (one allowlisted ERROR) | **CONFIRMED [M]** | `render` row portable; its stderr is byte-identical in all 7 modes |
| 14 | §6.1 the 14 rows are byte-stable ×6 canonical + ×2 load | **CONFIRMED and widened [M]** | **7 modes** (quiet/load16/ff30/ff60/ff120/thr/ff1) × reps: one distinct payload per cell across **all 210 matrix receipts**; production `classify_process` (segment sha `749fa060…`): **210/210 accepted, `rejected=[]`** |
| 15 | §7 the tracked battery is load-fragile at HEAD (5 row FAILs, 2 meta FAILs) | **NOT RE-ATTACKED** | outside this seat's row lattice (different artifact family: scene-transition/audio/overlap rows); left as the scout's open finding for the operator |
| 16 | §8 remaining unknowns (multi-touch, drag preview, `event_index`, stretch modes, nested SubViewports, `set_mouse_mode`, real display) | **UNCHANGED** | not measured here; §8 lists the boundary of this attack |
| 17 | (new) is any pinned payload a function of an unmodelled phase/startup coordinate (the r95/r97 hazard)? | **NO TICK-PHASE CYCLE FOUND [A]** | all 14 payloads are event-driven and byte-identical across 7 frame-shape regimes; the one phase coordinate that exists here (the input-flush boundary) is *before* the `process_frame` signal in every mode (§4) |
| 18 | (new) can the 14 cells be replayed in one process? | **REFUTED — single-cell-per-process only [A]** | `seq_clean` (tree cleanup between cells): **10/14** reproduce, first divergence `cursor` (`c0=(30.0,14.0)` vs `(0.0,0.0)`); `seq_noclean`: **5/14**, first divergence `hover` (`h0=P`). The tracked battery launches one fresh process per case, so the rows are safe — but any future batched probe must reset the cursor + emulated-button state (§8) |

---

## 2. Replay evidence: the frozen rows reproduce byte-for-byte

Every quiet rep1 receipt is **byte-identical (stdout *and* stderr)** to the scout's committed
receipt for the same cell (`corpus/live/r100-scout/runs/r100_gui_<cell>.rep1.out/.err`),
14/14 cells, `rc 0→0`. This is the strongest form of "the rows still hold": not merely
classifier-accepted, but the same bytes from a fresh process on a differently-loaded host.

```
replay census    stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay routing   stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay hover     stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay motion    stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay localpos  stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay cursor    stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay clip      stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay drag      stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay touch     stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay subvp     stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay warp      stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay focus     stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay render    stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
replay osmeta    stdout_eq=True stderr_eq=True pass_eq=True rc=0->0
```

(`runs/analyze_r100b.txt` §3; raw receipts `runs/quiet/r100b_gui_<cell>.rep{1..3}.{out,err,rc}`.)

---

## 3. The 14 rows are mode-portable (7 frame-shape regimes)

`runs/analyze_r100b.txt` §1/2: every mode reports `UNSTABLE=[]` and every cell
`portable=True pass_uniq=1` across `modes=7`. The full stdout — including the engine banner
— is identical across modes, not just the PASS line (`sha256` of
`runs/*/r100b_gui_census.rep1.out` → one distinct hash). The `render` stderr is likewise one
distinct hash across all 7 modes.

| mode | cells × reps | unstable | classifier accepts |
|---|---|---|---|
| quiet | 14 × 3 = 42 | `[]` | 42/42 |
| load (16 own hogs) | 14 × 3 = 42 | `[]` | 42/42 |
| ff30 | 14 × 2 = 28 | `[]` | 28/28 |
| ff60 | 14 × 2 = 28 | `[]` | 28/28 |
| ff120 | 14 × 2 = 28 | `[]` | 28/28 |
| thr (`sep2d=true`) | 14 × 2 = 28 | `[]` | 28/28 |
| ff1 | 14 × 1 = 14 | `[]` | 14/14 |

**No phase/startup-mode artifact reached any pinned payload.** The scout's §6.1 claim ("no
envelope/mode split is needed anywhere in this surface") is therefore confirmed *and
widened*: `--fixed-fps` 30/60/120/1, 16-hog load and threaded physics all leave the 14
payloads byte-identical, because the cells are event-driven (`push_input` dispatch is
synchronous) rather than frame-sampled.

---

## 4. Headline mechanism refutation: the parse→cursor write is **flush-gated**, and the flush sits **before** the `process_frame` signal

`runs/probes/quiet/r100b_cursorphase.rep1.out` (verbatim, identical in all 6 probe modes):

```
PASS r100b_phase cursorphase init=(0.0, 0.0) mm_imm=(0.0, 0.0) mm_flush=(20.0, 20.0)
mm_f1=(20.0, 20.0) mm_f2=(20.0, 20.0) mb_imm=(20.0, 20.0) held=0 mb_flush=(24.0, 24.0) held=1
mb_f1=(24.0, 24.0) held=1 push_imm=(24.0, 24.0) push_f1=(24.0, 24.0) gpos_imm=(24.0, 24.0)
gpos_f1=(52.0, 52.0) hovered=null
```

- `parse_input_event(motion)` does **not** write the cursor at the call: `mm_imm=(0,0)`.
  `Input.flush_buffered_events()` applies it: `mm_flush=(20,20)`.
- The same holds for the button state: `mb_imm held=0` → `mb_flush held=1`.
- `global_position` drives the applied value (`gpos_f1=(52,52)` while the event's `position`
  was `(70,70)`), confirming the scout's c5 — but *at the flush*, not at the parse.
- `push_input` never writes the cursor (`push_imm == push_f1 == (24,24)`), confirming L2.

`runs/probes/quiet/r100b_flushpos.rep1.out` localizes the implicit flush:

```
pre=(0.0, 0.0) pf=0 post_parse=(0.0, 0.0) after_await=(20.0, 20.0)
log=[sig@1=(20.0, 20.0)] post_parse2=(20.0, 20.0) after_await2=(44.0, 44.0)
log=[sig@1=(20.0, 20.0)|sig@2=(44.0, 44.0)] post_flush=(12.0, 12.0)
after_await3=(12.0, 12.0) log=[…|sig@3=(12.0, 12.0)]
```

The `process_frame` signal listener (connected *before* the parse and before the await
continuation) already sees the parsed value at the same frame (`sig@1=(20,20)`): **the
implicit input flush runs before the `process_frame` signal** — the same in-frame position
r97 measured for the deferred-call flush, now for the input queue. A probe that samples the
cursor between `parse_input_event` and the frame boundary (or inside an `_input` handler
that runs before the flush) sees the stale value; every pinned cell samples after
`await process_frame`, which is why the rows are stable.

**Consequence for authors [I]:** "`parse_input_event` moves the cursor" is the wrong mental
model; the correct one is "the parse enqueues, the frame's input flush applies" — and
because that flush precedes `process_frame`/`await process_frame`, one `await` is enough.

---

## 5. Drag threshold: **|Σ relative| > 10**, not "accumulated |relative|"

`runs/probes/quiet/r100b_dragphase.rep1.out` (identical in all 6 probe modes):

```
dp_multiframe[1:0 2:1 3:1 ] calls=1     dp_sameframe[1:0 2:1 3:1 ] calls=2
dp_sign_same drag=0 calls=0             dp_sign_multi mid=0 after=0 calls=0
dp_net16 drag=1 calls=1                 dp_10p5 drag=1 calls=1
dp_small3 drag=1 calls=1                dp_rel_only drag=1 calls=1
dp_pos_only drag=0 calls=0              dp_pos_thresh at10=0 at11=0 calls=0
```

- `dp_sign_same`: press at `(8,8)`, then `relative=(+6,0)` and `relative=(−6,0)` in one
  frame — **Σ|relative| = 12**, net displacement 0. Measured **no drag**. The scout's
  wording ("accumulated `|relative|`") predicts a drag; it is **[A] falsified**.
- `dp_rel_only`: a single motion with `relative=(30,0)` whose own `position` is still
  `(8,8)` → **drag starts**. `dp_pos_only`: `position=(40,8)` with `relative=(0,0)` → **no
  drag**; `dp_pos_thresh` (position-only 18 then 19) never starts. So the engine consumes
  the **`relative` stream**, not the event's `position`/`global_position`, for the threshold.
- The scout's own numbers are consistent with both models (their `d7` uses three `(4,4)`
  motions where Σ|rel| and |Σrel| both cross at the second step); my sign test separates
  them, and the correct law is **|Σ relative| > 10** (strict).
- Same-frame vs cross-frame accumulation is identical (`dp_sameframe == dp_multiframe`):
  the accumulator is per delivered event, not per frame — so a same-frame burst behaves
  exactly like one motion per frame.

Everything else in the drag row (mask requirement, press-focus source, drop target,
`force_drag`, `can_drop=false`) re-measured byte-identical across all 7 modes.

---

## 6. Ordering / buffering artifacts (new measurements)

**`orderin` — delivery order is `_input` → `_gui_input` [M].** For a press, a motion, a key,
a touch and two events in one frame, the interleaved log is always
`i:<ev>|g:<ev>`; a `_gui_input`-side `set_input_as_handled()` cannot suppress the `_input`
copy (it has already run), and two pushed events keep their order
(`two_in_frame[i:mm|g:mm|i:mb|g:mb]`). The pinned cells keep the two logs separate, so this
order was previously unmeasured.

**`coalesce` — the parse path coalesces motions at the flush; the push path does not [M].**

```
p2_imm n=0 rel=(0.0, 0.0) log=-      p2_flush n=1 rel=(20.0, 0.0)
p2_f1  n=1 rel=(20.0, 0.0) log=[S:mm(…pos=20.0,10.0…rel=20.0,0.0…)]
p2_sep imm n=1  p2_sep flush n=2 rel=(20.0, 0.0) log=[…pos=30.0…|…pos=40.0…]
push2 imm n=2 rel=(20.0, 0.0) log=[…pos=50.0…|…pos=60.0…]
```

Two parsed motions in one flush batch arrive as **one** event whose `relative` is the sum
and whose `position` is the last one; an explicit flush between them delivers two. Two
pushed motions arrive 1:1 immediately. Authors mixing `parse_input_event` with per-event
bookkeeping must expect coalescing (the pinned `motion` row uses the push path and is
unaffected).

**`dblclick` — the engine never computes `double_click` for synthetic events [M].** Two
parsed press/release pairs and a third press all deliver `dc=0`; pushed events carry only
the caller's flag (the scout's m3). No time-based double-click law exists here to be
mode-sensitive.

**`velphase` — `Input.get_last_mouse_velocity()` stays `(0.0, 0.0)` on both paths at every
sampled phase [M]** (`v0…v6`, including immediately after parse and after 1/2 frames). The
scout's "do not pin" warning refers to the `Input.warp_mouse` path (their `d2_cursor`:
`input_warp=(9.957696, 9.957696)`), which the pinned `warp` cell deliberately does not
print; the pinned `motion m4` zero is safe.

**`hoverphase` — hover is synchronous with `push_input` [M]**: `h_imm=A ev=[in@0]` before
any await; leaving clears it synchronously (`leave_imm=null`). No deferred-pick phase exists
for hover, unlike the cursor path.

---

## 7. Startup mode: frame shape is mode-coupled, the rows are not

`runs/probes/<mode>/r100b_startup.rep1.out` (pf/ph ladder; `t=` wall-clock is the only
unstable token):

| mode | pf/ph at `_initialize` | at `_run` | f1 | f2 | f3 | f4 | physics per idle frame |
|---|---|---|---|---|---|---|---|
| quiet | 0/0 | 0/1 | 0/1 | 1/2 | 2/2 | 3/3 | host-coupled (~0.5–0.75) |
| load | 0/0 | 0/1 | 0/1 | 1/2 | 2/2 | 3/3 | host-coupled |
| ff30 | 0/0 | 0/1 | 0/1 | 1/3 | 2/5 | 3/7 | **2.00** |
| ff60 | 0/0 | 0/1 | 0/1 | 1/2 | 2/3 | 3/4 | **1.00** |
| ff120 | 0/0 | 0/1 | 0/1 | 1/1 | 2/2 | 3/2 | **0.50** |
| thr | 0/0 | 0/1 | 0/1 | 1/2 | 2/3 | 3/3 | host-coupled |

- **The first `await process_frame` after `call_deferred("_run")` resumes at `pf=0` in every
  mode** — the deferred `_run` flush is in the same frame window as that signal, exactly the
  r97 law (deferred flush before the signal) re-observed at startup. A startup probe that
  counted "one await = next frame" would be off by one.
- The physics:frame ratio is the r97 mode table re-measured in a different probe
  (2.00/1.00/0.50 at ff30/ff60/ff120). **None of it reaches the rows**: the 14 payloads are
  identical in all these regimes.
- `shape … max_fps=0 tps=60 scale=1.00 vis=[P:(0,0),S:(64,64)] win=(64,64)` and the identity
  final transform are identical in every mode; **no control is hovered or focused at
  startup** (`h=null owner=null` at every sample) — so there is no startup-mode pick
  artifact to hunt.

---

## 8. The rows are **single-cell-per-process only** (contamination chain, exact)

`probes/r100b_seq.gd` runs all 14 cells in one process (frozen cell bodies), optionally with
the scout's own `_cleanup()` between cells. Compared against the fresh-process payloads
(`runs/analyze_r100b.txt` §6, identical in all 6 probe modes):

| variant | cells reproduced | first divergence | divergent cells |
|---|---|---|---|
| `seq_clean` (`--clean=1`) | **10/14** | `cursor` (`c0=(30.0,14.0)` vs `(0.0,0.0)`) | `cursor`, `warp`, `subvp`, `touch` |
| `seq_noclean` (`--clean=0`) | **5/14** | `hover` (`h0=P` vs `null`) | + `hover`, `motion`, `localpos`, `clip`, `drag` |

With cleanup the leaks are **singleton state, not the tree**:

- **Viewport cursor persists.** The `localpos` cell parses a press at `(30,14)` and never
  resets the cursor; the `cursor` cell then starts at `c0=(30.0,14.0)`, the `warp` cell at
  `w0 cursor=(20.0,4.0)` (set by `touch`'s t4 parse), and `subvp` reports
  `cursor_root=(20.0,4.0)`. `_cleanup()` frees nodes; it does not reset
  `Viewport.get_mouse_position()`.
- **Emulated mouse-button state persists.** One-off `runs/probes/meta/r100b_emul.rep1.out`:
  a parsed `ScreenTouch` press sets `Input.is_mouse_button_pressed(LEFT)=1`, a release
  clears it. The `cursor` cell parses a touch **press** (c6) and never a release, so in the
  sequence the `touch` cell's t3 parsed press cannot emit a *new* emulated
  `InputEventMouseButton` (measured: `a=[A:st(…)]`, no `mb`, vs the fresh process's
  `a=[A:mb(bm=1…)|A:st(…)]`). Mechanism of the suppression is **[I]** (already-held
  transition), the divergence is **[M]**.
- Without cleanup the tree leftovers dominate first (`hover`'s `h0=P` is routing's leftover
  control; `motion m1=[]` is the leftover `P` capture; `clip`'s `(90,4)` press lands on a
  leftover `ED`).

**Why this is a hazard note, not a row defect:** `run_battery.py`'s `execute()` launches one
fresh `godot --headless … --script res://<case> -- <flags>` process per case
(`corpus/fixtures/run_battery.py:712-733`, `subprocess.run` at `:586`), so the tracked
battery already has the property the rows need. Any future probe that batches cells must
reset the cursor (`Viewport.warp_mouse` is inert headless — no reset exists except a parsed
motion/press, or a fresh process) and the emulated button state (parse the matching release).

---

## 9. Independent probe (frozen `probeParent` dispatch) — read-only audit

The frozen `probeParent` dispatched **exactly one** read-only `ufo-labrat` (L2, advisory,
non-editing) with one bounded hypothesis: *"every
`runs/probes/<mode>/r100b_dragphase.rep*.out` exists and contains all ten `dp_*` tokens,
with `.rc=0` and empty `.err`"*.

**Result: REFUTED by non-existence — the labrat could not see the receipts.** Its
file-discovery substrate honors `.gitignore`, and the receipts live under
`corpus/live/r100-boundary/runs/`, matched by `corpus/live/.gitignore:1:runs/`; its report
lists only the script/probe files and finds zero `r100b_dragphase*` paths. The receipts **do
exist on disk** (356 `.out` files; `runs/probes/quiet/r100b_dragphase.rep{1,2,3}.{out,err,rc}`
present, all `.rc=0`, all `.err` 0 B) and every one is hashed in `manifest.sha256`. This is
the same *substrate-limitation* class the r95 scout's labrat recorded (null execution), now
for gitignored paths; **no second dispatch** was made (the probeParent budget is one). The
drag-model claim is therefore carried by the receipts + the manifest, not by the labrat.

---

## 10. Remaining unknowns / not measured

- **Multi-touch** (`index>0`, simultaneous touches), **drag preview**
  (`Control.set_drag_preview`), **`event_index` semantics 1..31**, **`in_local_coords=true`
  under non-identity content scale**, **nested SubViewports / CanvasLayer-offset input**,
  **`Input.set_mouse_mode` / `DisplayServer.warp_mouse`**, **real-display drag/drop** — all
  still unmeasured (the scout's §8 list stands; none is touched by this attack).
- **The tracked battery's load envelope** (scout §7: 5 row FAILs + 2 meta FAILs at
  loadavg 60–80) was **not re-attacked** here; this seat's row lattice is the 14 GUI cells.
  The scout's `negative_transition`/`overlap`/`audio_*` failures remain the operator's call.
- **`Input.warp_mouse`'s nonzero `get_last_mouse_velocity`** (the scout's d2 `9.957696`) is
  time-based and not pinned anywhere; it remains deliberately unpinned.
- **Mechanisms marked [I]:** the drag accumulator's storage, the emulated-press suppression
  rule, and the input-queue flush internals. No engine source tree exists on this host;
  all mechanism statements are separated from measurements.
- **Portability:** every value is this host/build/`--headless`/64×64 root viewport/identity
  transform; no off-host claim.

---

## 11. Host cleanup

- **Probe launches:** 210 matrix + 143 artifact-probe + 3 one-off = **356 fresh Godot
  processes**, all `timeout -s KILL 25`-bounded (0 hits), all `rc=0`, plus ~10 smoke launches.
- **Hogs:** exactly 16 own `yes` in each `load` batch, killed by PID via the driver trap;
  host `yes` counts unchanged (64→64, 80→80) — no foreign process touched, never `pkill`.
- **No stray processes:** `pgrep -fa 'r100b_|r100_gui'` empty; no run left running.
- **Writes:** `reports/round-100/r100-boundary.md`, `corpus/live/r100-boundary/**` (probes,
  drivers, analyzers, receipts, `RECEIPTS.md`, `manifest.sha256`). No tracked file written;
  no commit. The only `git status` tracked modification is the pre-existing
  ` M corpus/fixtures/run_battery.py` (a concurrent lane's, present before this session).

---

## 12. Evidence index

| path | content |
|---|---|
| `corpus/live/r100-boundary/proj/r100_gui.gd` | frozen scout probe (sha256 `dd826f6e…`), exact replay launch |
| `corpus/live/r100-boundary/probes/r100b_phase.gd` | 9 artifact arms (§4–§7) |
| `corpus/live/r100-boundary/probes/r100b_seq.gd` | 14 cells in one process (`--clean=0/1`, §8) |
| `corpus/live/r100-boundary/probes/r100b_meta.gd`, `r100b_emul.gd` | mode evidence (`sep2d`) + emulation state machine |
| `corpus/live/r100-boundary/run_matrix.sh`, `run_probes.sh` | drivers (hog PID discipline, `timeout -s KILL 25`) |
| `corpus/live/r100-boundary/analyze_r100b.py` | census + portability + replay + classifier + probes + seq |
| `corpus/live/r100-boundary/runs/<mode>/r100b_gui_<cell>.rep*` | 210 matrix receipts (7 modes) |
| `corpus/live/r100-boundary/runs/probes/<mode>/` | 143 artifact receipts (6 modes) + meta/one-off |
| `corpus/live/r100-boundary/runs/analyze_r100b.{json,txt}` | the analysis quoted above |
| `corpus/live/r100-boundary/manifest.sha256` | sha256 of every receipt/probe/driver + this report |
| `corpus/live/r100-boundary/RECEIPTS.md` | hash summary |
| `corpus/live/r100-scout/runs/r100_gui_<cell>.rep1.{out,err}` | replay reference (committed) |
