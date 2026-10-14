# Round 71 scout report — pygame first contact: withholding-window edge measured (buffer = 131072, NOT ~8KB) + coverage-move handoff

Seat: scout, lane `game-dev-2d`, round r71, wave `shokunin-train-20261101-w11`.
Host: devin. Repo: `~/Projects/shokunin/game-dev-2d-shokunin` at HEAD `d9ae207`
(no tracked file touched by this seat; all receipts under
`corpus/live/r71-scout/`, `runs/` gitignored via `corpus/live/.gitignore:1`).
Concurrent r71 seats active (author/baseline/boundary/critic/reviewer/
simplifier scratch dirs observed; the critic appears to have run the scout
battery prototype under idle and loaded64 conditions into
`corpus/live/r71-critic/scout-battery-{idle,loaded64}/pygame-*` — observed,
not reviewed; that load temporally overlaps this seat's v1 battery run 3,
see §4). No `lsp` device is exposed in this seat's toolset: the
convention traces below are **text reads** of `corpus/fixtures/love_battery.py`
(literal fallback, recorded; not presented as semantic proof).

**The assigned unknown is resolved: the frontier's `~8KB` withholding bound
is falsified 16× on this host.** The measured edge is **131072 bytes**
(CPython 3.14.7 `io.DEFAULT_BUFFER_SIZE`, raised from 8192 by CPython
gh-117151/GH-118144). The claim *shape* — "stdout withholding is a
language-layer window bounded by buffer size" — survives with the corrected
constant. Full matrix, edge semantics, and a load-validated sibling battery
prototype are below; **landing into `corpus/fixtures/` is outside this
seat's write scope** (scratch prototypes are copy-ready).

## 1. Headline — withholding edge (the open falsifier)

Claim under test (frontier `fa-pygame.md` remaining unknown): unflushed piped
stdout is parent-invisible until buffer-fill *or* exit; falsifiable via a
>8KB mid-run write surfacing early.

Outcome (standalone probe, 3 reps/case, `withhold_probe.stdout.txt` +
`withhold_receipt.json`; child = plain `python3 withhold_child.py`, binary
pipe, no text layer; `first_vis_ms` = parent-visible latency of byte 1):

| case | ops | verdict | first_vis_ms (3 reps) | vis_mid@300ms | exit_ms | bytes |
|---|---|---|---|---|---|---|
| small | w100, s600 | **withheld → exit** | 608.7 / 609.0 / 609.9 | 0 | 611.1–612.0 | 100 |
| small_pg | same + `import pygame` | **withheld → exit** | 645.2 / 645.8 / 647.4 | 0 | 654.7–656.3 | 100 |
| edge_8192 | w8192, s600 | **withheld → exit** | 608.9–609.3 | 0 | 611.0–611.6 | 8192 |
| edge_65536 | w65536, s600 | **withheld → exit** | 608.6–609.0 | 0 | 610.7–611.1 | 65536 |
| edge_128k_lo | w131071, s600 | **withheld → exit** | 608.9–609.2 | 0 | 611.1–611.5 | 131071 |
| edge_128k_eq | w131072, s600 | **EARLY** | 8.9–9.8 | 131072 | 611.1–611.9 | 131072 |
| edge_128k_hi | w131073, s600 | **EARLY** | 9.0–9.6 | 131073 | 611.2–612.0 | 131073 |
| big_200k | w200000, s600 | **EARLY** | 9.0–9.8 | 200000 | 611.5–612.1 | 200000 |
| big_200k_pg | same + `import pygame` | **EARLY** | 43.1–45.3 | 200000 | 652.2–655.8 | 200000 |
| seg_64k_64k | w65536, s250, w65536, s350 | **withheld → exit** (sums to exactly 131072) | 609.3–609.8 | 0 | 611.2–612.0 | 131072 |
| seg_70k_70k | w70000, s250, w70000, s350 | **PARTIAL** (70000 early @ ~259ms, 70000 at exit) | 258.7–260.1 | 70000 | 610.8–612.4 | 140000 |
| seg_131072_100 | w131072, s250, w100, s350 | first 131072 early; 100 at exit | 8.8–9.3 | 131072 | 611.0–612.1 | 131172 |
| flush_control | w100, s200, **flush**, s300 | surfaces at flush (209ms) | 209.2–209.8 | 200 | 511.3–512.2 | 200 |
| unbuf_control | w100, s600, child `-u` | **EARLY** | 8.7–9.3 | 100 | 610.8–611.3 | 100 |

`integrity=1` (byte-exact content), `rc=0` on all 42 reps. Read-event
timeline for `seg_70k_70k` rep0 (`[[258.8,65536],[258.8,4464],[608.9,65536],
[608.9,4464]]`) is the clean partial-visibility proof: the first 70000 bytes
land mid-life, the remainder only at exit. 64KiB read chunks are the kernel
pipe capacity, not a write-side effect.

**Edge semantics (observed):**
- single unflushed write with `len >= io.DEFAULT_BUFFER_SIZE` on an empty
  buffer → bypasses the buffer, early (exact-equality case measured: 131072
  is early, 3/3);
- accumulated writes that reach *exactly* the buffer size do **not** flush
  (`seg_64k_64k` withheld, 3/3) — "buffer full" alone is not a flush edge;
- overflow (`len > available`) flushes the existing buffer first, then
  buffers the new data if it fits (`seg_70k_70k`, `seg_131072_100`);
- explicit `flush()` and `-u`/`PYTHONUNBUFFERED` surface immediately;
- `import pygame` does not move the edge (`small_pg` withheld,
  `big_200k_pg` early) → **language layer (Python stdio), not pygame/SDL**.

Mechanism is **inference** (black-box behavior consistent with CPython
`_io.BufferedWriter`; the C-source branch condition was not read this round).
Buffer-size provenance is **observed + external**: `io.DEFAULT_BUFFER_SIZE`
= 131072 on this interpreter, measured edge == 131072, change landed via
CPython gh-117151 (GH-118144).

## 2. Surface lattice re-measured (prototype fixture, 4 runs incl. stress)

`pygame_probe.py` (scratch prototype of `corpus/fixtures/pygame_probe.py`),
run under `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
PYGAME_HIDE_SUPPORT_PROMPT=1`, probe wall ~20.0–20.5s, exit 0,
`PYGAME_PROBE_DONE`, stderr = the avx2 `RuntimeWarning` only. Ranges across
3 clean battery runs + 1 run under 16 extra CPU burners:

- viability: `driver=dummy`, `init_fail=0`, `surf=320x240`, flags `0x1000000`.
- `cadence60` (tick(60) ×240): dt_mean 16.052–16.064ms, dt_min 16.008–16.048,
  dt_max 16.06–17.03, fps 62.11–62.5, tick ret 16 → **~62Hz, never 60.00**
  (SDL_Delay ms-granular undershoot). Frontier's wider min/max spread
  (15.05/16.87) still fits the proposed bounds.
- `cadence120` ×240: mean 8.051–8.059ms, fps 123.46–125.0.
- `cadence0` (tick() ×1200): hz 6.9–9.7 MHz, dt_mean 0.0, ret 0 (uncapped
  bare-loop spin; unbounded CPU).
- `cadencebusy` ×120: mean 15.993–15.998, max ≤16.002 (tighter tail).
- `popen` (flushing child, `-u`): l1_wait 4.85–6.4ms, **l2_wait
  120.07–120.09ms = the child's own sleep**, close 1.23–1.81, total
  126.37–128.31, rest_len 0 → **writer-bound pipe, LOVE's shape confirmed**;
  no pygame-side plumbing/seam at this layer.
- `popen_buf` (unflushed child): l1_wait 125.12–126.26 (exit-batched),
  l2_wait 0.0 — the small-scale withholding demo.
- `pump`: 400 frames with zero event calls, total 3213.4–3216.0ms,
  queued_after_nopump 9 (one-time SDL events), posted USEREVENT survived,
  found at end True; `pump2` (with pump) total 3221.4–3227.0,
  queued_after_pump 0 → **pump-free headless confirmed**; exit is
  self-imposed (no spontaneous QUIT).
- `flip`: mean 0.001ms (no-op headless).

In-probe withholding arm (child = same file via `--io-child`, so it pays the
pygame import): small first_vis 646–659ms / exit 655–670 (withheld);
edge_eq first_vis 47–58ms (early); seg_over first_vis 297–309ms,
vis_pre_exit 70000 (partial); unbuf first_vis 47–60ms. Same lattice as the
standalone probe.

## 3. Coverage-move handoff (prototypes; author lands)

Scratch prototypes, copy-ready (sha256 prefixes):

| scratch file | sha256 | lands as |
|---|---|---|
| `corpus/live/r71-scout/pygame_probe.py` | `f85e28bc205ae3a9` | `corpus/fixtures/pygame_probe.py` |
| `corpus/live/r71-scout/pygame_battery.py` | `98ced2932ccdc2da` | `corpus/fixtures/pygame_battery.py` |
| `corpus/live/r71-scout/withhold_child.py` | `c6792093f116d115` | standalone 3-rep edge probe (scratch-only) |
| `corpus/live/r71-scout/withhold_probe.py` | `e5039a858e0d77a7` | standalone 3-rep edge probe (scratch-only) |

`pygame_battery.py` mirrors `love_battery.py` convention-for-convention:
`CASES` model (`love_battery.py:38`), `ARM_LINE` (`:58`), `run_process`
(`:88`), `parse_arms` (`:104`, kv split on whitespace `:111` — **values must
be space-free**; the frontier probe's `surf=(320, 240)` would parse broken,
prototype emits `surf=320x240`), `check` exact-or-bound (`:116`),
`run_dir`/`verdicts.json` (`:142`, `:194-204`), PASS iff
`failed==0 and launch_ok and done_marker`.

Validated end-to-end: **83/83 cases PASS ×3 clean runs** (`battery.v2.run{1,2,3}.txt`,
83 = 72 pins + 11 cross-key relations) **+ 83/83 under 16 CPU burners**
(`battery.stress.txt`), exit 0, ~20s wall. Case rows: viability 3, stdio 1,
cadence 15, popen 12, pump 7, flip 1, withhold 33, relations 11.

Landing deltas (only these differ from the scratch prototype):
1. `--runs` default → `HERE.parent / "live" / "runs"` (love_battery.py:138
   shape; prototype defaults scratch-local to respect this seat's scope).
2. `TIMEOUT_S = 45` (probe is ~20s; love's 30 is too tight under load).
3. Buffer-size pins: exact `131072` rows are **host/Python-version scoped**;
   the self-describing relations (`withhold_edge_eq.n ==
   stdio.default_buffer_size`, ±1) are the load-bearing pins and survive a
   default-buffer change. Keep both, document the bound.
4. Keep the child-env scrub of `PYTHONUNBUFFERED` (probe does) — otherwise
   the withhold arm is defeated whenever the battery env carries it.
5. Don't call `display.get_wm_info()` (wayland-path SIGSEGV, frontier);
   probe forces the dummy trio before `import pygame` (fixture owns its
   headless profile, like `love_probe/conf.lua`).

Run shape: `python3 corpus/fixtures/pygame_battery.py` →
`corpus/live/runs/pygame-<stamp>/verdicts.json` (+ probe stdout/stderr),
exit 0 on PASS. Sibling-only: `run_battery.py` / `love_battery.py` untouched,
Godot/LOVE rows byte-stable by construction.

## 4. Falsification ledger (honest)

- Frontier's `~8KB` withholding bound: **falsified** (edge = 131072 here;
  8192/65536/131071 all withheld 3/3). The frontier measured only <8KB
  cases, consistent with any buffer ≥ 8KB — the number was an assumption.
- My own v1 battery design: fixed 300ms mid-sample **failed once under load**
  (`battery.run3.txt`: `withhold_seg_over vis_mid_bytes=0`, 74/75 — child
  startup jitter pushed the overflow flush past the sample). Fixed by the
  adaptive `vis_pre_exit_bytes` metric (bytes readable ≥200ms before exit);
  the failing run dir `runs/pygame-20261014T142344407705Z/verdicts.json` is
  retained. A first `--import-pygame` control run was lost to an argv-order
  bug in my harness (`withhold_probe.stdout.v1-argvbug.txt`); fixed and
  re-run.
- Claim held: >8KB writes do **not** surface early; ≥128KiB writes do.

## 5. Receipts index (all under `corpus/live/r71-scout/`)

- Edge matrix: `withhold_probe.py` + `withhold_child.py` →
  `withhold_probe.stdout.txt`, `withhold_receipt.json` (3 reps × 14 cases,
  full timelines).
- Prototype fixture: `pygame_probe.py` → `probe.rep1.{stdout,stderr}.txt`,
  `probe.u.stdout.txt` (`python3 -u` parent control).
- Prototype battery: `pygame_battery.py` → `battery.v2.run{1,2,3}.txt`,
  `battery.stress.txt`, `battery.run{1,2,3}.txt` (v1),
  `runs/pygame-*/{probe.stdout.txt,probe.stderr.txt,verdicts.json}` (8 dirs).

## 6. Confidence / remaining unknowns

- **High**: withholding edge location and semantics (42-rep matrix +
  in-probe + stress), writer-bound popen shape, pump-free headless, cadence
  lattice (own 3 reps + frontier 4), battery executability (8 runs).
- **Moderate**: `vis_pre_exit_bytes` margin choice (200ms) — structural for
  this case set (all writes ≥250ms before exit), not re-derived per load
  level; buffer-size *pin policy* (exact vs relation) left to the author.
- **Unresolved / not measured by this seat**: exact CPython source branch
  condition; binary-vs-text write parity (text measured only); buffer
  behavior for `PYTHONUNBUFFERED` inherited via env (scrubbed, not
  measured); mixer determinism and pygame-ce divergence (frontier unknowns
  stand); whether the landed fixture should keep `cadencebusy`/`flip`
  (measured, cheap, kept in the prototype).
- Bounded: CPython 3.14.7 / pygame 2.6.1 / SDL 2.32.72, this host;
  the referent (buffer-bounded withholding, writer-bound pipes) is portable,
  the 131072 constant is Python-version-scoped.
