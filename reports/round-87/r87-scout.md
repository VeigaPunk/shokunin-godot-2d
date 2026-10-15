# game-dev-2d round 87 — scout (r87-scout): the input event/action lattice, measured; 3 arms bimodal

Seat `SCOUT-FINISHER` (LEAF) | lane `r87-scout` | round 87 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless),
Python 3.14.7, 32 CPUs. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD
**`7ae7083`** (*r86 backend-select lattice*). `DisplayServer` is headless in every
receipt; `physics_ticks_per_second=60`, `Input.use_accumulated_input` defaults
**true**.

**No git mutation, no tracked file written, no subagent, no commit.** Writes are
this report and `corpus/live/r87-scout/**` only.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this
session and no GDScript/Python language server is installed, so
`definition`/`references`/`hover` were **unavailable for every file touched**.
Semantic carriers are fresh-process execution receipts and `get_method_list()`/
`get_property_list()` runtime introspection; engine file:line citations are
engine-emitted stderr text, not source reads.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless
marked); **[I]** inference; **[A]** ablation.

---

## 0. Prior-seat scratch audit — what the dead scout built and measured

A previous r87 scout died after completing the *evidence* pipeline but before
any analysis or report. Its scratch (`corpus/live/r87-scout/`, mtimes 10:43–10:45)
contains:

| artefact | verdict |
|---|---|
| `proj/` — byte-copy of `corpus/fixtures/` minus `run_battery.py`, plus `input_lattice.gd` | **sound**; `diff -rq` confirms the copy is exact |
| `proj/input_lattice.gd` (854 lines, 23 arms, sha256 `2b68531d…`) | **byte-identical to `corpus/live/r83-scout/proj/input_lattice.gd`** — the orphaned r83 lane's probe, adopted verbatim; still prints `R83 arm=…` headers (cosmetic, not part of pinned signatures) |
| `run_arms.py` (`fad1d03f…`) | **sound** — each arm = one fresh `godot --headless --path proj --script res://input_lattice.gd -- --arm=<n>` under the battery's 8 s bound, judged by the production `classify_process` extracted verbatim from `corpus/fixtures/run_battery.py` lines 386–404 (sha256 `615d332e…`) |
| `arms-discover.json` → `gen_pins.py` → `pins.json` | **sound method** — discover froze a *single sample* per arm into pins |
| `arms-verify.json` (23 arms × 3 reps) | **verdict FAIL, `bad=[press_phys, ui_ns]`** — the seat died having found nondeterminism but never characterised it |

Preserved verbatim under `corpus/live/r87-scout/inherited/`; this seat's reruns
write new files rather than overwriting the dead seat's receipts.

**What it measured and did not finish:** all 23 arms PASS in discover; verify
×3 froze `press_phys` (2 FAIL) and `ui_ns` (1 FAIL). My rerun of the identical
pipeline (§1) flaked `press_phys` **and `release_edge`** but not `ui_ns` — i.e.
the unstable set itself is unstable. The remainder of this report finishes that
characterisation.

---

## 1. What I ran (this seat)

| # | command (cwd = `corpus/live/r87-scout`) | receipts |
|---|---|---|
| 1 | `python3 run_arms.py --mode verify --reps 3` (×2 sessions) | `arms-verify-finisher-r3.json`, `arms-verify-finisher2-r3.json` — reproduction on host |
| 2 | `python3 run_arms.py --mode verify --reps 10 --arms press_phys,release_edge,ui_ns,press_idle,acc_off,acc_flush,burst` | `arms-flaky-r10.json` — mode frequencies |
| 3 | `godot --headless --path proj --script res://r87_edge.gd -- --arm=jpbe` ×3 | `runs/jpbe.rep{1..3}.{out,err}` — adjacent edge, byte-identical ×3 |
| 4 | `godot --headless --path proj --script res://r87_edge.gd -- --arm=jmode` ×3 | `runs/jmode.rep{1..3}.{out,err}` — in-process instability census |
| 5 | `godot … res://ei_bound.gd` ×3 (+ 1 micro-repro `ei_test.gd`) | `runs/ei_bound.rep{1..3}.{out,err}` — `event_index` refusal boundary, byte-identical ×3 |
| 6 | `python3 make_author_rows.py` | `author-rows.py.txt` — 20 verbatim CASES rows + `expected_errors`, exec-checked |

Cumulative verdicts across **all** sessions (dead + this seat), 19 reps/arm max:

```
press_idle 19/19   acc_off 19/19   acc_flush 19/19   burst 19/19
census 9/9  pre_frame 9/9  api_press 9/9  dz_ladder 9/9  joy_axis 9/9
echo_edge 9/9  key_map 9/9  imap_erase 9/9  imap_mid_cb 9/9  conflict 9/9
dev_joy 9/9  mouse_hdls 9/9  null_edge 9/9  dispatch_order 9/9
reentrant 9/9  phys_peer 9/9
press_phys   9/19   release_edge  7/19   ui_ns 11/19      <-- BIMODAL
```

Every bimodal arm produced **exactly two distinct payloads** across all 19
reps; every clean arm produced one. Ablations are load-bearing throughout
(`signature_dropped`/`exit_flipped`/`errors_dropped` all flip the verdict on
the reference rep — `errors_dropped` fails only on `null_edge`, which is the
only error-carrying row).

---

## 2. The input lattice — measured laws (the 20 stable arms)

All values below are pinned bytes from `pins.json`, re-verified on host.

### 2.1 Dispatch family and order **[M]**

Per-event receipt sets (four sink handlers `_input`/`_shortcut_input`/
`_unhandled_key_input`/`_unhandled_input` = `in`/`sc`/`uk`/`uh`):

| event class | receipts | arms |
|---|---|---|
| `InputEventAction` | `in`, `uh` (2) | press_idle, burst, release_edge, … |
| `InputEventKey` | `in`, `sc`, `uk`, `uh` (4) | echo_edge, key_map, ui_ns, … |
| `InputEventJoypadButton` | `in`, `sc`, `uh` (3) | dev_joy |
| `InputEventMouseButton`/`Motion` | `in`, `uh` (2) | mouse_hdls |
| `InputEventShortcut` (bare) | `in`, `sc`, `uh` (3) | null_edge |

`dispatch_order` pins the intra-phase order: `_input` runs **reverse creation
order** (`s1` before `s0`), then `_shortcut_input`, `_unhandled_key_input`,
`_unhandled_input`, each reverse-ordered. `root.set_input_as_handled()` inside a
later `_input` suppresses only the **subsequent phases** of that event — the
earlier-positioned `_input` calls already ran (they are not retroactively
blocked), and the same holds for the next parsed event.

### 2.2 Buffering and timing **[M]**

- `acc=true` (default headless): `parse_input_event` **buffers** — `imm[]`
  reads the pre-state, state applies and events deliver at the next frame
  boundary (`recv @pr+0` when parsed in an idle resume).
- `Input.use_accumulated_input = false`: `parse_input_event` delivers **inline
  inside the call** (`inline_receipts=2` before returning) and applies state
  immediately (`imm[1/1.00/1/0]`). The property write is honoured
  (`census` sets `acc=false` and reads back `false`).
- `Input.flush_buffered_events()` forces mid-frame delivery of everything
  pending (`mid_len=0 → post_len=2`, post state applied).
- `ProjectSettings` asymmetry: `input_devices/buffering/agile_event_flushing`
  exists (`ps_agile=false`) but `…/use_accumulated_input` is **absent**
  (`ps_acc=<missing>`) — the property lives only on the `Input` singleton.
- `pre_frame`: a parse before the first frame is buffered and delivered at
  `pr+1` to a sink created afterwards — no event loss.
- `reentrant`: a `parse_input_event` issued **inside** `_input` queues under
  `acc=true` (inner event delivered after the outer event's handler chain:
  `ra in,uh` then `rb in,uh`); under `acc=false` it dispatches **inline,
  mid-callback** (`ins0:rb` lands between `ins0:ra` and `uhs0:ra`).
- `phys_peer`: a buffered press parsed *inside* a physics step is recorded as
  delivered in the same step (`ev_step_delta=0`), `same_tick` poll still reads
  0, and both peers observe `pressed=1` from `d+1` — the buffered state lands
  at the next physics boundary.

### 2.3 Action state semantics **[M]**

- `just_pressed` lives exactly one frame in the phase that reads it
  (`api_press`: `pr0{…/1/0} → pr1{…/0/0}` in idle, `ph1{…/1/·} → ph2{…/0/·}`
  in physics); `just_released` reads 1 at the release-edge tick — its decay
  edge is not separately sampled by these arms.
- `Input.action_press`/`action_release` apply state **immediately with no event
  dispatch** (`recv=[]`), honor `strength` (`get_action_strength` and
  `get_action_raw_strength` both `0.70`), and bypass the action deadzone
  (`api50`: even `s0.00` presses with `jp=1`).
- `dz_ladder`/`joy_axis`: the action deadzone gates **device-event matching
  only**. `InputEventAction.strength` ignores it entirely (dz50 and dz20
  columns identical — `s0.00` still presses). Real `InputEventJoypadMotion`
  matching is **inclusive at the edge** (`|v|=dz` presses with strength 0) with
  `strength = (|v| − dz)/(1 − dz)` beyond it (`v0.51→0.02`, `v0.70→0.40`,
  `v1.00→1.00` at dz 0.5); `raw_strength` stays `|v|`. Axis sign selects the
  binding direction.
- `echo_edge`: an `echo=1` key event matches its action but does **not**
  re-trigger `just_pressed` (`m[ek:0/0|I1/0/0]`). An echo event arriving as the
  action's *first* event still presses (`first_echo[1/1.00/0/0]` — `pressed=1`
  with `just_pressed=0`).
- `key_map`: keycode-bound and physical-keycode-bound actions are consulted
  **independently** — one event carrying `keycode=Q + physical=W` fires both
  `ka` and `kp`; releases match per-field (a `kc=0/ph=W` release releases `kp`
  only).
- `imap_erase`: `InputMap.erase_action` on a pressed action drops it from the
  pressed enumeration immediately (`has=false`, `pl=[]`); raw key events bound
  to it still dispatch as unmapped `InputEventKey`s (4 receipts); re-add+rebind
  rearms cleanly.
- `imap_mid_cb`: `erase_action` **inside an `_input` callback** is honoured for
  action matching — a buffered event for the erased action still delivers to
  handlers but sets no state; the action can be re-added and re-armed mid-run.
- `ui_ns`: one Enter press fires **the custom action and three more builtins at
  once** — `pl=["cx","ui_accept","ui_text_completion_accept","ui_text_newline",
  "ui_text_submit"]`. `erase_action("ui_accept")` makes later receipts read
  `ui_accept:gone|Igone` while `cx` keeps matching.
- `conflict`: two actions bound to the same key both press; `shift+W` only
  fires the shift-bound action; `is_action_pressed(a, exact_match)` reads
  accumulated state (a pressed action stays pressed regardless of the probe's
  modifier).
- `dev_joy` (`joys=0` headless): synthetic `device=5` button events set
  `is_joy_button_pressed(5)` **device state** but do not fire a `device=0`-bound
  action; `device=-1` events set nothing anywhere. Binding device filters the
  action; the device-state bank accepts any device id.
- `mouse_hdls`: parsed `InputEventMouseButton` sets
  `is_mouse_button_pressed(1)=1` and delivers, but `root.get_mouse_position()`
  stays `(0,0)` — the event's `position` does not move the viewport cursor.
- `null_edge` (4 whitelisted ERRORs, rc=0): release-before-press still delivers
  and is a no-op on state; `parse_input_event(null)` → `ERROR: Required object
  "rp_event" is null.`; `is_action_pressed`/`is_action_just_pressed`/
  `action_press` on never-registered actions each emit
  `ERROR: The InputMap action "<name>" doesn't exist.` and return false/no-op.
- `census`: `InputEventAction` carries exactly `[device, action, pressed,
  strength, event_index]` — **`action_index` does not exist** (receipts print
  `ai=<null>`); `InputEventKey` adds `window_id`, `key_label`, `location`,
  `command_or_control_autoremap`. 91 `ui_*` builtins ship;
  `ui_accept` = `[K4194309 (Enter), K4194310 (KP Enter), K32 (Space)]`,
  `dz_ui=0.50`. `eng=0/1` — sampled at deferred-`_run` start, before any arm
  await: `Engine.get_process_frames()=0` while `get_physics_frames()=1`.

**Measured quirk, mechanism unexplained [M/I]:** the first *physics-phase*
sample after an API-press (`api_press` `ph1{ap=1/0.70/1/1}`) or a
physics-resume buffered press (`phys_peer` `d+1{…=1/1.00/1/1}`) reads
`just_released=1` alongside `just_pressed=1` — while the idle-flushed press
(`press_idle` `ph+0{pi=1/1.00/1/0}`) and the inline unbuffered press
(`acc_off` `ph+0{ao=1/1.00/1/0}`) read `jr=0`. Both readings are byte-stable
×9; which path seeds the physics-phase `just_released` flag was not determined.
Author-facing: pin it as measured, don't explain it.

---

## 3. The instability — three flake shapes, one root cause

Headless, the idle loop iterates faster than the 60 Hz physics step, and **how
many physics steps land inside a span of N idle frames is wall-clock
dependent** (`jmode` shape A: `{4:14, 5:2}` ph-ticks per 10 idle frames on this
host/session — the distribution itself is a mode, not a pin). Three arms carry
pinned bytes that depend on that ratio:

| arm | fails | mode A (pinned) | mode B | shape |
|---|---|---|---|---|
| `press_phys` | 10/19 | `post_ph` has **3** entries | `post_ph` has **2** entries | **ph-count** — number of physics ticks inside `await process_frame×10` after a physics-resume parse |
| `release_edge` | 12/19 | `ph+0{re=0/0.00/1/1}` (`jp=1`) | `ph+0{re=0/0.00/0/1}` (`jp=0`) | **semantic flag** — whether a physics step interposed inside the 2-idle-frame press→release gap |
| `ui_ns` | 8/19 | release receipts `@ph+0` | release receipts `@ph+1` | **ph-delta** — a physics boundary crossed between `_mark()` and the buffered release's delivery |

`press_phys`/`ui_ns` differ only in *timing counters*; `release_edge` is the
important one — a **semantic** payload difference: `is_action_just_pressed`
reads 1 or 0 at the same nominal tick.

**Mechanism, measured in-process [M]:** `jmode` shape C reproduces the
`release_edge` structure 16× in one process and records, per trial, the physics
ticks that landed inside the gap (`gap`) and the `just_pressed` read at the
first post-release physics tick (`jp`). Result, byte-identical ×3 on this host:

```
flag[gap/jp] = { "1/jp0": 12, "0/jp1": 4 }    gap = { 1: 12, 0: 4 }
```

**Perfect correlation**: when a physics step interposes inside the gap
(`gap=1`), it consumes the press's physics-phase `just_pressed` before the
release lands → `jp=0` at `ph+0`; when none does (`gap=0`), press and release
flush inside the same physics step and `ph+0` shows `jp=1, jr=1`. The pinned
signature happens to be the `gap=0` branch — a ~25–40% mode on this host, i.e.
**discover froze a coin-flip outcome**. The same logic explains `ui_ns`
(`gap` events between mark and release-parse shift the receipt's recorded
`phys_no`) and `press_phys` (count of interposed ticks).

**Structural rule for authors:** a pinned byte is safe only if (a) the value is
sampled in-resume with no await between the operations it relates, or (b) every
tick index in it is anchored by a `physics_frame`-phase await, or (c) physics
deltas are masked out (`_fmt_recv(true)` prints `ph~`). `release_edge` already
masks its `recv` ph-deltas and *still* flaked — masking deltas is necessary but
not sufficient when `just_*` flags are sampled across an idle-window gap.

`pre_frame` (9/9 clean) carries the latent `press_phys` shape — its `post_ph`
list length depends on ph-ticks inside a 3-frame idle window — flagged, not
counted against it.

---

## 4. Adjacent edge (r87_edge.gd) — the by_event API family + `event_index`

`is_action_just_pressed_by_event` / `is_action_just_released_by_event` and
`InputMap.event_is_action` are census-listed but were exercised by no arm. One
new probe (`proj/r87_edge.gd`, `jpbe` arm) measured **[M, ×3 byte-identical]**:

- `is_action_just_pressed_by_event` while `just_pressed` is live: `1` for the
  bound key event, `0` for a wrong-key event, `0` queried against a different
  action, `0` for a *released* event against a pressed action, `1` with
  `exact_match=true` on the identical event.
- `is_action_just_released_by_event`: `1` **only for the event instance that
  carried the transition** — a redundant second release event returns `0`
  while `is_action_just_released` reads `1`.
- `InputMap.event_is_action(ev, action, exact_match)`: matching event `1`,
  wrong action `0`; modifier semantics measured — a `shift+W` event matches a
  `shift+W` binding under both `exact_match` values (`s_ex=1 s_plain=1`) while
  a plain `W` event matches it under **neither** (`p_ex=0 p_plain=0`):
  `exact_match=false` does not widen to modifier-free matching on this build.
- `InputEventAction` participates fully in the by_event/eia path (`jpbe=1`,
  `eia=1`); `parse_input_event` **never writes** `event_index` (stays −1) and
  `action_index` reads `<null>` (absent property, census-confirmed).

**`event_index` refusal boundary [M, ×3 byte-identical], `ei_bound.gd`:** for a
parsed `InputEventAction`, `event_index ≤ 0` (`-2,-1,0`) applies the press;
`1 ≤ ei ≤ 31` is a **silent no-op** (`pressed=0`, no error line);
`ei ≥ 32` is a no-op **plus** one typed error:

```
ERROR: Input singleton does not support more than 32 events assigned to an action.
   at: _parse_input_event_impl (core/input/input.cpp:1010)
```

This is a deterministic, pinnable refusal cell if the author wants it
(values −2/−1/0/1/31/32/33/42/100 measured; rc=0 throughout).

---

## 5. Authorability

- **20 rows are verbatim-ready** in `corpus/live/r87-scout/author-rows.py.txt`
  (repr-quoted, exec-checked: 20 five-tuples whose signatures are byte-equal to
  the pinned `PASS` lines). Naming follows the `input_lattice_<arm>`
  convention; insert ahead of the crash/descendant tail like prior blocks.
- **`expected_errors`: only `input_lattice_null_edge` needs an entry** — its
  four lines, verbatim (§2.3). All other rows are `ERROR:`-clean; do not add
  entries for them.
- **Do not author `press_phys`, `release_edge`, or `ui_ns` as written.** Each
  is bimodal with both payloads enumerated in `arms-flaky-r10.json`. If their
  laws are wanted, restructure: anchor windows to `physics_frame` awaits, mask
  `ph` deltas/counts, or split the `just_*` flag read into a mode cell.
- **`pre_frame` caveat:** clean ×9 but latently shaped like `press_phys`; either
  re-cut to anchor `post_ph` or accept the flake risk knowingly.
- New pinnable cells available beyond the adopted lattice, both deterministic
  ×3: the **`event_index` refusal boundary** (§4, needs 1 whitelisted ERROR at
  `core/input/input.cpp:1010` for the `ei≥32` cases) and the **by_event /
  event_is_action / modifier matrix** (`r87_edge jpbe` signature in
  `runs/jpbe.rep1.out`).
- If authored, the probe file lands at `corpus/fixtures/input_lattice.gd`; the
  scratch `proj/` is already byte-identical to fixtures+probe, so no other
  fixture changes are needed. Cosmetic: the probe still prints `R83 arm=…`
  banners (upstream of the `PASS` line; harmless to the classifier).

## 6. Hazards / nondeterminism (mode candidates — never deterministic pins)

1. **ph-count in an idle window** (`press_phys` shape): any emitted list whose
   length counts physics ticks inside `process_frame` awaits. Mode frequencies
   observed: pin mode 9/19.
2. **ph-delta on buffered receipts** (`ui_ns` shape): any `ph+N` printed for an
   event whose parse→delivery spans idle awaits. Pin mode 11/19.
3. **`just_*` flags across a two-event idle gap** (`release_edge` shape):
   semantic 0/1 bimodality driven by physics-step interposition — proven by
   `jmode` (`gap/jp` correlation `{1→0:12, 0→1:4}`). Pin mode 7/19 (minority).
4. **Latent**: `pre_frame` (shape 1, clean ×9); any future arm pairing an
   idle-window gap with ph-indexed output or a `just_*` sample.
5. The headless `ph:pr` interleave ratio itself (~4–5 physics steps per 10 idle
   iterations this session) is load/timing-dependent — never pin it.
6. `jpbe`/`jmode`/`ei_bound` histograms and matrices are this-host,
   this-build, `--headless`, 60 tps measurements.

## 7. Remaining unknowns

- **`just_released=1` on first physics-phase read of an API/physics-resume
  press** (§2.3 quirk) — measured stable, mechanism unexplained.
- **`event_index` semantics for `1..31`** — silent drop is measured; what the
  field is *for* (pressed-event slot indexing per upstream docs) is untested
  beyond the boundary map.
- **`is_action_pressed(a, exact_match)` granularity** — `conflict` shows it
  reads accumulated state; whether exactness ever changes a polled answer
  (mixed exact+inexact bindings held simultaneously) was not isolated.
- **Mouse `position` vs viewport cursor** — measured for the root Window only;
  SubViewport/`warp_mouse` untested.
- The **joypad `device` filter** was tested only for `JOY_BUTTON_A` with no
  real device connected (`joys=0`); analog-axis device filtering untested.
- `arms-discover.json`'s single-sample pins mean the 20 "stable" arms carry
  ordinary residual flake risk (9–19 clean reps each, not proof of
  determinism); `pre_frame` is named explicitly.

## 8. Host cleanup

- All Godot runs were bounded (`timeout 15` shell bound + harness `timeout=8`
  per rep); every process exited `rc=0` — **no leaks, no stray processes**.
  `pgrep godot` at report time shows only an unrelated `game-dev-3d-shokunin`
  r91-author lane process — not this seat's, left untouched.
- `/tmp/r87edge/` (micro-repro scratch used before promoting the probes into
  `proj/`) was deleted.
- `git status --porcelain` shows three modified tracked files —
  `SCORECARD.md` (mtime 01:47, pre-dates this session),
  `corpus/fixtures/run_battery.py` and `corpus/fixtures/phys2d_backends.gd`
  (mtime 13:02). **None are this seat's** — nothing here writes tracked
  files; the fixture edits are a concurrent lane's in-flight work, left
  untouched. Scratch writes are confined to `corpus/live/r87-scout/**` plus
  this report.

## 9. Evidence index (`corpus/live/r87-scout/`, `MANIFEST.sha256` covers all)

| artefact | note |
|---|---|
| `proj/input_lattice.gd` | the adopted r83 probe, sha256 `2b68531d…` (unchanged) |
| `proj/r87_edge.gd` | this seat's edge probe (`jpbe`, `jmode`) |
| `proj/ei_test.gd`, `proj/ei_bound.gd` | `event_index` refusal isolation + boundary map |
| `run_arms.py`, `gen_pins.py`, `pins.json` | dead seat's harness + frozen pins (unchanged) |
| `inherited/{arms-discover,arms-verify,pins}.json` | dead seat's receipts, preserved verbatim |
| `arms-discover.json` | dead seat's discover output (23/23 PASS lines) |
| `arms-verify-finisher-r3.json`, `arms-verify-finisher2-r3.json` | this seat's two full ×3 verifies (bad = {press_phys,release_edge} then {press_phys,release_edge,ui_ns}) |
| `arms-flaky-r10.json` | ×10 mode census on the 3 flagged + 4 latent-risk arms |
| `runs/{jpbe,jmode,ei_bound}.rep{1..3}.{out,err}` | edge-probe receipts, byte-identical ×3 |
| `author-rows.py.txt` + `make_author_rows.py` | 20 verbatim CASES rows + `null_edge` whitelist, exec-checked |

Reproduce: `python3 run_arms.py --mode verify --reps 3` (expect `bad` ⊆
{press_phys, release_edge, ui_ns}, membership varies); edge arms via
`godot --headless --path proj --script res://r87_edge.gd -- --arm=<jpbe|jmode>`.
