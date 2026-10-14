# game-dev-2d round 71 — author (seat: author; host: devin)

## Declared move (verbatim)

"MOVE (coverage): `corpus/fixtures/pygame_probe.py` + `pygame_battery.py`
sibling runner mirroring love_battery conventions. Arms: (a) cadence
bounds (tick(60) ~62Hz, uncapped MHz — bound-pinned); (b) withholding
window — measure the flush edge: unflushed line parent-invisible until
~8KB or exit; pin measured bound; (c) io.popen/Popen writer-bound +
byte-exact (confirm LOVE's shape); (d) pump-free headless. Claim to
test: 'stdout withholding is a language-layer window bounded by buffer
size' — falsifiable via a >8KB mid-run write surfacing early (scout left
this open). Sibling-only; Godot/LOVE rows byte-stable."

## Landed changes

- `corpus/fixtures/pygame_probe.py` (NEW): single-file pygame probe —
  no project dir exists to mirror, so the fixture carries its headless
  contract itself (conf.lua-analogous): `SDL_VIDEODRIVER=dummy`,
  `SDL_AUDIODRIVER=dummy`, `PYGAME_HIDE_SUPPORT_PROMPT=1` set via
  `os.environ.setdefault` **before** `import pygame`. Arms: viability /
  cadence60 / cadence0 / popen / popen_buf / withhold_small /
  withhold_big / withhold_fill / pump, emitted as `PYGAME-ARM <arm> |
  k=v` with `flush=True`, terminating `PYGAME_PROBE_DONE`.
- `corpus/fixtures/pygame_battery.py` (NEW sibling runner): mirrors
  `love_battery.py` structure exactly — one `python3 pygame_probe.py`
  run, `--version` preflight via the probe's own `--version` flag
  (analogue of `love --version`), ARM parser, 36 pinned cases (exact
  bytes where deterministic, bound tuples where jittered),
  `verdicts.json` under ignored `corpus/live/runs/pygame-*`.
  `run_battery.py` and `love_battery.py` untouched.
- The withhold children are **plain `python3 -c`, deliberately**: the
  claim is language-layer (Python stdio block-buffering), so the subject
  must not import pygame. `PYTHONUNBUFFERED` is stripped from child env
  so operator environment cannot quietly invalidate the buffered-pipe
  physics. Parent-side timing uses `select`+`os.read` on the raw fd —
  no parent-side stdio buffer pollutes the read-chunk timestamps.

## Measured result (36/36 PASS, 3 stable reps + 1 dev run)

Verdict on the claim — **form CONFIRMED, claimed bound FALSIFIED**:
the window *is* bounded by the language-layer buffer, but the bound on
this build is `io.DEFAULT_BUFFER_SIZE` = **131072** (Python 3.14),
**not ~8KB**:

- `withhold_small` (9000B mid-run write, which *exceeds* the claimed
  8192 edge): all 9014 bytes held to child exit — `first_read_ms`
  205.1–205.4 vs `eof_ms` ~206.8, `early_bytes=0`, 3/3 reps. The
  frontier's "~8KB or exit" is wrong on the number.
- `withhold_big` (200000B single mid-run write > 131072): 200007 bytes
  surfaced at ~105ms **while the child was still asleep**
  (`alive_at_first=True`, 3/3) — the withheld `MARK-1` (7 buffered
  bytes) rode the flush, fused delivery; the post-flush `MARK-2`
  re-buffered and was held to exit (`mark2_ms` 205.4–206.2). The
  falsifier fires — but only above the *measured* 128KiB bound, so the
  claim survives as "bounded by buffer size" with the buffer
  re-measured at 131072.
- `withhold_fill` (200×1000B cumulative crossing): mid-run flush at
  ~105ms of 126007 bytes (3/3 identical) — the edge is buffer-**fill**,
  not large-write bypass; granularity-independent.
- Cadence (a): `tick(60)` dt_mean 16.063–16.073ms, fps 62.1–62.5 —
  ~62Hz, never 60 (SDL_Delay ms-undershoot, as frontier measured).
  `tick()` uncapped: 6.5–6.9 MHz bare-Python spin, dt_mean 0.0ms.
- Popen (c): writer-bound + byte-exact, LOVE's shape confirmed —
  `l1_wait` 4.8–5.1ms (spawn floor), `l2_wait` 120.06–120.08ms = the
  flushing child's own 120ms sleep, `close_wait` 1.2–1.7ms,
  `rest_len=0`, `ret=0`. `popen_buf` (non-flushing child): `l1_wait`
  125.0–125.1ms — held to child exit, same withholding surface from
  the probe side.
- Pump-free (d): 400 frames, zero event calls, `posted_survived=1`,
  `pump_needed=false`.
- Viability: `init (5,0)`, `driver=dummy`, `PYGAME_PROBE_DONE`,
  exit 0.

## Evidence

- `python3 corpus/fixtures/pygame_battery.py` → `totals: cases=36
  pass=36 fail=0 launch_ok=True done_marker=True exit=0`, exit 0,
  ~9.5s wall. Receipts:
  `corpus/live/runs/pygame-20261014T143028666014Z/verdicts.json`,
  `...T143041126847Z`, `...T143049554160Z` — all 36/36, deterministic
  keys byte-identical across reps, bound keys mid-range.
- Scratch copies + pre-fixture flush-edge experiments:
  `corpus/live/r71-author/` (`withhold_{experiment,variants,big,huge,
  fill}.py`, `verdicts-run{1,2,3}.json`, `probe.stdout.txt`).
- Sibling byte-stability: `sha256sum` of `run_battery.py`,
  `love_battery.py`, `love_probe/{main,conf}.lua` == `corpus/live/
  r71-simplifier/preland-sha256.txt` exactly (diff clean);
  `git status --porcelain corpus/fixtures/` shows only the two new
  pygame files.
- LOVE regression check: `python3 corpus/fixtures/love_battery.py` →
  19/19 PASS (`corpus/live/runs/love-20261014T143116881482Z/`).
- Dev-time note (honest): first authored run scored 35/36 —
  `whf_early_bytes` exposed a bad metric (exit burst spans multiple
  64KiB pipe reads landing ~1ms apart; keying "early" off the MARK-2
  read misattributed 65536 exit bytes). Fixed the definition to
  `ms < eof_ms - 25` (bursts are ~100ms apart by construction);
  re-pinned; 3 clean reps after.

## Remaining unknowns / risks

- `whs_bufsize` pins `131072` exactly — correct for this
  `python3.14.7` build; older Pythons (8192) would fail that pin.
  That's an honest per-build lattice pin (same convention as LOVE's
  `ret_a=768`), flagged here so a future port reads it deliberately.
- `withhold_fill` early_bytes=126007 < bufsize — the flush delivers
  the *accumulated* buffer at the crossing write, not a full 131072;
  mechanism detail, pinned as a wide bound.
- `alive_at_first` race: exit-flushed bytes can be read while
  `proc.poll()` is still `None` (seen on `withhold_small`,
  `alive_at_first=True` at its exit read — emitted, unpinned). Only
  pinned where deterministic (big/fill mid-run flush).
- Uncapped `dt_max_ms` (0.007–0.009ms observed, pinned hi=50) and
  `c60_max` (16.2–16.8, pinned hi=30) could flake only under heavy
  host load — jitter bounds, not mis-pins.
- Mixer/audio semantics under `SDL_AUDIODRIVER=dummy` still unmeasured;
  event-queue overflow bound unmeasured (no spontaneous traffic
  headless).
