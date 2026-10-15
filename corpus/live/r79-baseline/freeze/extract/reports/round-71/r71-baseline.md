# Round 71 baseline report — pygame first contact (host: devin)

Seat: g2d baseline (LEAF). No tracked-file edits, no commits. All work
under `corpus/live/r71-baseline/` + this report. Frontier evidence read
first: `reports/frontier/fa-pygame.md` + `corpus/live/frontier-pygame/`.

**Scope note.** The MOVE names `corpus/fixtures/pygame_probe.py` +
`pygame_battery.py`, but this seat's write scope is the report + scratch
dir only — so both files are built, calibrated and thrice-verified at
`corpus/live/r71-baseline/` (promotion-ready; executor seat owns
fixtures/). A sibling-authored `corpus/fixtures/pygame_probe.py`
(untracked, 9524B, different withhold-payload choices: 9000/200000/
200×1000) appeared mid-round — left untouched; its bounds are
consistent with the edge measured below.

## Declared claim — measured outcome

> "stdout withholding is a language-layer window bounded by buffer
> size", falsifiable via a >8KB mid-run write surfacing early.

**Confirmed, with the bound corrected to 131072 bytes** — the frontier's
"~8KB" was wrong on this interpreter. `io.DEFAULT_BUFFER_SIZE` =
**131072** on Python 3.14.7 (the classic 8192 was 16× smaller). The
>8KB falsification cell did *not* fire — an 8192B mid-run write stayed
withheld to exit — but a write crossing 131072 releases pending
mid-run, exactly at the byte bound. Language-layer confirmed: identical
edge with pygame fully initialized (`--wh-init`) and without pygame at
all; SDL contributes zero pipe plumbing.

## Artifacts

- `corpus/live/r71-baseline/pygame_probe.py` (259 lines, sha256
  `0a98c1cd…`) — emits `PYGAME-ARM <arm> | k=v` lines (flush=True;
  timings measured in-process via perf_counter, so parent-side delivery
  never distorts them — love_probe convention). Arms: viability,
  cadence60/cadence0/cadencebusy, popen, popen_buf, pump, pump2,
  quitpoll, flip. Battery modes (selected before `import pygame`):
  `--io-child buf|flush`, `--wh-child N [--wh-init]` (line1@0ms, N-byte
  payload@200ms, line3@400ms, exit@600ms — all unflushed),
  `--wh-drip CHUNK,NCH,MS [--wh-init]`.
- `corpus/live/r71-baseline/pygame_battery.py` (415 lines, sha256
  `e69c3a82…`) — sibling runner mirroring `love_battery.py`
  conventions: CASES pin exact/(lo,hi) on arm keys; WH_CELLS spawn
  pipe-traced wh-children (class = `early` if bytes surface ≥200ms
  before EOF, `withheld` if within 100ms); IO_CELLS per-line writer-
  bound waits; `verdicts.json` + per-cell trace receipts per run.
- `edge_scan.py`, `edge_scan2.py` — the calibration ladders (scratch,
  not battery).

## Exact invocations

```
python3 corpus/live/r71-baseline/pygame_battery.py \
    --runs corpus/live/r71-baseline/runs        # ×3, all PASS 54/54
python3 corpus/fixtures/love_battery.py \
    --runs corpus/live/r71-baseline/love-runs   # PASS 19/19
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --runs corpus/live/r71-baseline/godot-runs  # PASS 88/88 flagless
```

Receipts: `runs/pygame-20261014T142532741745Z/verdicts.json` (sha256
`8f16a5eb…`), `…142558552392Z` (`589e4e1f…`), `…142623646451Z`
(`bf202a59…`) — 54/54 each; `love-runs/love-20261014T142608582031Z`
(`98f504bd…`) 19/19; `godot-runs/20261014T142633675793Z`
(`510beb9c…`) 88/88. Probe run elapsed ~13.5s; stderr = 334B avx2
RuntimeWarning only (known preamble).

## Measured lattice (54 cases, 3/3 stable)

**(a) cadence — bound-pinned:** `tick(60)` ×240: dt_mean 16.057ms, min
15.069, max 16.364, eff_hz 62.28, `get_fps()` 62.11 — ~62Hz, never
60.00 (SDL_Delay ms-undershoot). `tick()` ×1200 uncapped: dt_mean
0.000ms, max 0.005ms, **7.02 MHz** bare loop, fps=inf, ret 0.
`tick_busy_loop(60)`: mean 15.996, max 16.013 — tighter tail.

**(b) withholding window — the flush edge, measured:**
child schedule line1(12B)@0 → payload N@200ms → line3(12B)@400 →
exit@~615ms. First parent-visible byte:

| cell | observed | verdict |
|---|---|---|
| N=8192 / 65536 | nothing until exit (~614ms), early_bytes=0 | withheld |
| N=131048 / 131060 | all withheld to exit (pending ≤131072 fits) | withheld |
| N=131061 | pending 12B released @214ms; payload re-buffered to exit | early |
| N=131072 | 131084B stream @213ms; line3 still withheld to exit | early |
| N=1048576 | 1048588B streamed @214ms; 12B tail at exit | early |
| N=131060 `--wh-init` | withheld (fb 1034ms = init-shifted exit) | withheld |
| N=131072 `--wh-init` | early @651ms, 131084B — SDL loaded, same edge | early |
| drip 16384×10@30 | tip @374ms, flushed **114700** = 12+16384×7 | early |
| drip 8192×17@15 | tip @390ms, flushed **122892** = 12+8192×15 | early |

Measured semantics: buffer capacity 131072; a write that fits remaining
space is withheld; a write exceeding it flushes pending to the pipe
(the overflow point lands exactly on the write grid — flushed pendings
observed: 114700, 120012, 122892); a write ≥ capacity streams through.
**Tail nuance:** small writes are absorbed *past* capacity — line3's
12B never flushed a full buffer (N=131060/131061/131072 all withheld
their trailing 12B to exit); the overflow release fires at write time
for large writes only. Pipe capacity F_GETPIPE_SZ = 65536 caps the
parent's first read, so flush volume is measured as `early_bytes`
(≥100ms before EOF), not first-read size.

**(c) Popen — LOVE's shape confirmed:** flushing child l1_wait 5.58ms
(spawn floor), l2_wait 120.11ms = child's own 120ms sleep (writer-
bound, no hidden buffering), byte-exact `CHILD-MARK-1/2`, close 1.64ms,
rest_len 0. Non-flushing child: l1_wait 125.04ms (both lines at exit),
l2_wait 0.00ms — direction-1 withholding reproduced. Direction-2
iochild: flush mode 13.9ms/213.8ms (writer's clock); buf mode both
~214-216ms (exit burst).

**(d) pump-free headless:** 400 frames @tick(120) zero event calls =
3215.0ms (vs 3222.4 with pump); pre-posted USEREVENT survived
(`get()` pumps implicitly; 9 init-time SDL events queued, no growth);
`quitpoll` 600ms → 0 spontaneous QUIT — termination must be
self-imposed. `display.flip()` 0.000ms no-op.

## Sibling byte-stability — ZERO drift

Godot flagless 88/88 PASS (sha256 `510beb9c…`), LOVE 19/19 PASS
(`98f504bd…`). `git status` shows no tracked modifications from this
seat — only sibling untracked dirs (r71-*, frontier-lovephysics edits,
`corpus/fixtures/pygame_probe.py`).

## UNKNOWNs / caveats

- First calibration run kept at `runs/pygame-20261014T142434840977Z`
  (52/54 — two drip pins pre-fix; provenance, not a lattice failure).
- Grow-vs-flush threshold for *small* non-fitting writes sits between
  12B (absorbed) and 8192-grid writes (coalesce, flush at overflow) —
  not fully resolved; battery pins behavior, not mechanism.
- Buffer bound 131072 is this-interpreter (3.14.7); older Pythons ship
  8192 — the battery's bound pins are host-conditional by design.
- Not probed: mixer under AUDIODRIVER=dummy, event-queue overflow,
  pygame-ce divergence, >1 descendant depth.
