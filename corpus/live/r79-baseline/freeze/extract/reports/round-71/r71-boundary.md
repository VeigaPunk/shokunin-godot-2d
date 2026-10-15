# Round 71 — boundary: pygame stdout withholding edge is TWO-layer (8192 textio + 131072 BufferedWriter), not ~8KB

Seat: boundary (LEAF) | Lane: g2d | Round: 71 | Host: devin |
Python **3.14.7**, `pygame 2.6.1 (SDL 2.32.72)` at `/usr/bin/python3`.

## Scope and method

Scratch-only + report-only. I wrote only this report and
`corpus/live/r71-boundary/`. No tracked fixture, runner, CASES row, LOG,
or SCORECARD entry touched; no subagent dispatch; no git mutation.

The lane's tracked fixture (`corpus/fixtures/pygame_probe.py` +
`pygame_battery.py`) had **not landed at probe time** (`git status`:
absent; the author seat owns it). Every cell below is scratch-driven.
Probe design: the child emits `TRACE` lines on raw fd2 via `os.write`
(never buffered by Python) so the parent can timestamp the exact moment
of each stdout write **without perturbing the stdout buffer under
test**; the parent timestamps every byte chunk with `select` + `os.read`.
Byte-level visibility and `readline`-level visibility are measured by
separate drivers (`--reader raw|lines`).

All probes run under `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
PYGAME_HIDE_SUPPORT_PROMPT=1`; all exits 0 unless stated.

## Headline — the claim, tested

Claim to test (brief): *"stdout withholding is a language-layer window
bounded by buffer size"*, falsifiable via a >8KB mid-run write surfacing
early; frontier bound `~8KB/exit flush`.

**Measured verdict: CONFIRMED as a language layer (CPython stdio, not
SDL/pygame) — and the frontier's `~8KB` edge is FALSIFIED on this
build.** The parent-visible edge is **two-layer**:

- textio pending threshold: **8192 B** (`TextIOWrapper.chunk_size`,
  default 8192 — `Modules/_io/textio.c:1202` in v3.14.0),
- BufferedWriter buffer: **131072 B** — `io.DEFAULT_BUFFER_SIZE` is
  **131072** on this host, not 8192. GH-118144 raised it from 8 KiB in
  Python 3.14 (verified from CPython tags: `_iomodule.h` has
  `8 * 1024` in v3.12.0/v3.13.0, `128 * 1024` in v3.14.0).

Exact measured edges (byte-deterministic, 2–3 reps each; receipts
`withhold-raw.json`, `withhold-edge2.json`, `withhold-edge3.json`):

| cell (unflushed writes, text layer) | total B | parent-visible early | withheld to exit |
|---|---|---|---|
| single 1000 / 8191 / **8192** / 8193 | … | **0** | all |
| single 65536 | 65536 | 0 | 65536 |
| single **131071** | 131071 | 0 | 131071 (3/3) |
| single **131072** | 131072 | **131072** @ ~17.7–19.6 ms | 0 (3/3) |
| single **131073** / 196608 / 262145 | … | all | 0 (3/3) |
| 4096+4096 | 8192 | 0 | 8192 |
| 65536+65536 | 131072 | 0 | 131072 |
| 16×8192 | 131072 | 0 | 131072 |
| 16×8192+1 | 131073 | 0 | 131073 |
| 17×8192 | 139264 | **131072** @ 979 ms | 8192 (2/2) |
| **16×8192+8191** | **139263** | **0** | **139263 (2/2)** |
| **16×8192+8191+1** | **139264** | **131072** @ ~359 ms | 8192 (2/2) |
| 18×8192 | 147456 | 131072 | 16384 |
| 65536+65537 | 131073 | 65536 @ 79 ms | 65537 |
| 8192+122881 | 131073 | 8192 | 122881 |
| 8193+122880 | 131073 | 8193 | 122880 |
| 131071+1 | 131072 | 0 | 131072 |
| 131072+1 | 131073 | 131072 | 1 |
| 100+131072 | 131172 | 131172 | 0 |
| 131071+131072 | 262143 | 262143 | 0 |
| 131072+131071 | 262143 | 131072 | 131071 |

**Falsifier result:** a *single* >8KB mid-run write does **not** surface
early (8193, 65536, 131071 all withheld; binary-layer
`sys.stdout.buffer.write` identical). It surfaces early only at
**>= 131072 bytes in one write** (raw write-through), or when a chunked
write lands with `len > remaining buffer space` (then the buffered
prefix surfaces, the remainder re-buffers). The exact compound window is
**131072 + 8191 = 139263 B fully invisible; the 139264th byte surfaces
the buffered 131072** — measured 2/2 both sides.

**The window is a function of write granularity, not total size:** a
single 139263-byte write is *fully visible* (`e_single_139263`), while
139263 bytes accumulated in small chunks are *fully invisible*
(`e_16x8k_then_8191`). "Bounded by buffer size" holds per layer; the
parent-visible edge is chunk-conditional.

**Concurrent independent corroboration (read-only cross-check):** the
scout's scratch battery independently pins the same edge
(`corpus/live/r71-scout/battery.stress.txt` — `withhold_edge_eq/lo/hi`
against `stdio.default_buffer_size`, 83/83 PASS), and the author's
scratch targets the same 131072 crossing
(`corpus/live/r71-author/withhold_fill.py`). Three independent probe
families agree on the 131072 bound.

### Measured visibility rules

- **R1** single write `< 131072` → buffered, invisible until exit
  (flush at interpreter shutdown; bytes arrive ~3.4 ms before exit, EOF
  ~0.1 ms after last byte).
- **R2** single write `>= 131072` → written straight to the fd, visible
  immediately (~18 ms = spawn+write; chunked 65536+65536+1 by pipe
  capacity on read side).
- **R3** accumulation: a flush of the buffered prefix happens only when
  a chunk arrives with `len > avail` (`avail = 131072 − buffered`).
  `len == avail` does **not** flush (65536+65536, 131071+1, 16×8192 all
  withheld) — the buffer can be exactly full and invisible.
- **R4** textio pending holds the tail: writes of `< 8192` B accumulate
  in `TextIOWrapper` pending and never touch the BufferedWriter; pending
  is pushed to the buffer only when it reaches `>= 8192` (or on
  line-buffering/`write_through` triggers). This is why 16×8192+1 does
  **not** flush even though the buffer is exactly full: the +1 byte
  stays in pending (`e_16x8k_then_8191_then_1` crosses at the *next*
  byte).
- **R5** explicit `flush=True` → immediate (early at 18.1 ms);
  `python3 -u` / `PYTHONUNBUFFERED=1` → `write_through=True` (measured
  attrs) → immediate even without newline (`c_u_nonl`, `c_env_nonl`).

### Mechanism (source-traced + reproduced on a constructed writer)

- `textio.c` (v3.14.0): write pre-flushes pending when
  `bytes_len >= chunk_size` (:1739) and pushes pending to the buffer
  when `pending_bytes_count >= chunk_size` (:1780); `chunk_size` default
  8192 (:1202).
- `bufferedio.c` `_io_BufferedWriter_write_impl`: fast path buffers
  without flushing iff `len <= avail && len < buffer_size`; otherwise
  flush buffer → raw-write in `buffer_size` quanta → buffer remainder.
- Cross-check on a constructed writer (`bw_micro.py`, exit 0):
  `B=131072: 131072-then-1` → 131072 visible immediately, 1 byte at
  flush; `65536-then-65537` → 65536 visible at the 2nd write;
  `131071-then-1` → all at flush; `B=8192: 8192-then-1` → 8192 visible
  immediately, 1 at flush; `8191-then-1` → all at flush. Same rules.

### readline-level (line) visibility (`withhold-lines.json`)

| cell | line first visible |
|---|---|
| 100 B + `\n` unflushed | exit (~368 ms) |
| 100 B, no newline | exit (~372 ms) |
| single 131073 B + `\n` | **~19 ms** (raw write-through carries the newline) |
| 16×8192 + `\n` (131074 B line) | exit (~1330 ms) |
| 17×8192+1 + `\n` | exit |
| 2×4096 + `\n` | exit (~428 ms) |

For a line-oriented parent, an unflushed line is exit-batched **unless a
single >= 131072 B write carries its newline**; newline alone never
flushes when piped (`line_buffering=False`).

### stderr edges (same two-layer BufferedWriter, `line_buffering=True`)

- 100 B + `\n` → visible ~18.8 ms (line-buffered flush).
- 100 B / 9000 B without `\n` → withheld to exit.
- 131072 B no `\n` → visible immediately (== buffer_size, raw).
  (stderr totals in receipts include coalesced TRACE bytes; attribution
  by chunk.)
- A battery reading stderr separately sees the per-import avx2
  `RuntimeWarning` promptly (it ends with a newline) — good.

### pygame-process cells

- `p_plain` (pygame dummy, 100 B unflushed): withheld to exit
  (first_out 910/927 ms, exit 950/966 ms) — same physics inside a
  pygame process.
- `p_banner` (banner not hidden): banner+line = 214 B co-withheld to
  exit → fixture must set `PYGAME_HIDE_SUPPORT_PROMPT=1`.
- `p_128k_hi` (single 131073 B in a pygame process): visible early
  (131073) — matches plain Python.

## (a) cadence knife-edges (`cadence.stdout.txt`)

Pacing law measured: `tick(fps)` sleeps `int(1000/fps)` ms — every
nominal fps is really a *bound*, and the truncation is visible:

| fps | dt_mean ms | effective Hz | tick rets |
|---|---|---|---|
| 30 | 33.04 | 30.26 | 33 (57/60) |
| 59.94 | 16.06 | 62.26 | 16/17 |
| 60 (3 reps) | 16.060–16.100 | 62.11–62.27 | 16 ×139–141, 17 ×9–10 |
| 100 | 10.06 | 99.38 | 10/11 |
| 120 | 8.06 | 124.04 | 8/9 |
| 144 | **6.06** | **165.07** | 6/7 |
| 240 | 4.06 | 246.3 | 4/5 |
| 500 | 2.06 | 485.1 | 2/3 |
| 999 | 1.05 | 951.5 | 1/2 |
| 1000 | 1.047 | 955.3 | 1/2 (min dt 0.0004 — occasional no-sleep) |
| **1001** | **0.0004** | **2.2 MHz spin** | 0 (all) |
| 2000 | 0.0003 | 3.7 MHz spin | 0 |
| 0 / −1 / no-arg | 0.0001–0.0003 | 3.2–13.6 MHz spin | 0 |
| busy_loop(60) | 15.997 | 62.51 | 16 (150/150) |
| busy_loop(1000) | 0.9998 | 1000.2 | 1 (300/300) |

**Cutoff knife-edge: fps 1000 sleeps 1 ms; fps 1001 → delay 0 → bare
Python loop.** `tick(0)`, `tick(-1)`, `tick()` all spin uncapped
(`get_fps=inf`). `pygame.time.get_ticks()` is int ms (50 distinct values
in 50 ms).

Loaded rep (32 busy loops on 32 cores, `cadence_loaded.stdout.txt`):
tick(60) dt_mean 16.007 / 16.077 — mean stable; min dipped 10.07, max
17.75 → pin the mean, not min/max. Idle max already spikes to 18.96 in
one rep.

## (c) io arm — pygame parent → grandchild (`io.stdout.txt`)

LOVE r70 shape **confirmed** (writer-bound, byte-exact):

| arm | l1_wait | l2_wait | EOF | bytes |
|---|---|---|---|---|
| grandchild `python3 -u` | 5.03–5.12 ms | 125.1–125.2 ms (= its 0.12 s sleep) | ~0.02 ms | 13 B lines exact |
| grandchild plain (no `-u`) | 125.24 ms | 126.53 ms | — | 26 B in one chunk at exit |
| grandchild single 9000 B write | withheld to exit (305 ms) | | | 9001 B |
| grandchild single 131073 B write | visible at 5.1 ms | | | 131073 B |

So the parent's read latency tracks the *writer's* flush state; the
grandchild's own stdio adds the same two-layer withholding (9000 B <
131072 → invisible until exit).

## (d) pump arm (`pump.stdout.txt`)

- **Pump-free headless confirmed:** 300 frames `tick(120)` = 2417.5 ms
  with zero event calls; 8 queued SDL init events; a posted `USEREVENT`
  is retrievable via `event.get()` with no pump.
- **Queue cap (new bound):** exactly **65535** events; post #65536
  **raises** `pygame.error: Event queue is full (65535 events)` (it does
  not return `False`); drain retrieves all 65535; posting works again
  after drain. 65535 posts in 21 ms.

## Suggested pins for the author's battery (measured bounds)

- **withholding arm** — pin exact cells: 8191/8192/8193 withheld;
  131071 withheld vs 131072/131073 early; 139263 withheld vs 139264
  (early=131072, withheld=8192); 65536+65537 (early=65536);
  131072+1 (early=131072, withheld=1); 16×8192+1 withheld. These are
  byte-deterministic; no jitter observed.
- **cadence arm** — tick60 `dt_mean_ms` ∈ (16.0, 16.2) (idle
  16.06–16.10; loaded 16.01–16.08), `hz` ∈ (61.5, 62.6); tick120
  `dt_mean_ms` ∈ (8.0, 8.2); tick1000 ∈ (0.9, 1.1); tick1001/uncapped
  ∈ (0.0, 0.01). Do not pin min/max (loaded min 10.07, idle max 18.96).
- **io arm** — mirror LOVE: l1_wait (0.2, 30), l2_wait (110, 140),
  close_wait (0, 5), total (115, 170), rest_len 0, byte-exact marks.
- **fixture correctness** — ARM lines must be `flush=True` (or run
  `python3 -u`); set `PYGAME_HIDE_SUPPORT_PROMPT=1`; never rely on
  newline-flush on a pipe.

## UNKNOWNs / retained caveats

- Author fixture not landed at probe time; if its bytes/grammar differ
  from my scratch pattern, re-drive the edge cells on landed bytes.
- Single host. Withholding cells are byte-deterministic (no jitter across
  reps); cadence numbers are this host's (loaded rep only for tick60).
- The 131072 bound is **Python-version-conditional**: on <= 3.13 the
  BufferedWriter is 8192 B, where a full-buffer pending flush goes raw
  immediately — i.e. the frontier's `~8KB` intuition would hold there,
  not here (source-inferred from v3.12/v3.13 tags; not measured on a
  3.13 host).
- Unmeasured: mixer semantics; pygame-ce; the pipe-capacity chunking
  (64 KiB) only affects parent read sizes, not visibility edges.

## Reproduce

```
cd corpus/live/r71-boundary
python3 wprobe_parent.py --reader raw --json withhold-raw.json       # exit 0
python3 wprobe_parent.py --reader raw --suite edge2 --json withhold-edge2.json
python3 wprobe_parent.py --reader raw --suite edge3 --json withhold-edge3.json
python3 wprobe_parent.py --reader lines --suite lines --json withhold-lines.json
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 \
    python3 cadence_probe.py                                          # exit 0
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 \
    python3 io_probe.py                                               # exit 0
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 \
    python3 pump_probe.py                                             # exit 0
python3 bw_micro.py                                                   # exit 0
```

## Artifact inventory (`corpus/live/r71-boundary/`)

- `wprobe_child.py`, `wprobe_parent.py` — withholding driver (suites
  raw/lines/edge2/edge3; TRACE-on-fd2 design).
- `withhold-raw.json` + `.stdout.txt`, `withhold-edge2.json` +
  `.stdout.txt`, `withhold-edge3.json` + `.stdout.txt`,
  `withhold-lines.json` + `.stdout.txt` — per-chunk receipts.
- `bw_micro.py` — constructed-BufferedWriter cross-check.
- `edge_manual.py`, `edge_reader.py` — minimal manual reproduction of the
  16×8192+1 anomaly.
- `cadence_probe.py` + `cadence.stdout.txt`/`cadence.stderr.txt`,
  `cadence_loaded.py` + `cadence_loaded.stdout.txt`.
- `io_probe.py` + `io.stdout.txt`/`io.stderr.txt`.
- `pump_probe.py` + `pump.stdout.txt`/`pump.stderr.txt`.

No commit, no tracked mutation, no LOG/SCORECARD write. `git status`
shows only the concurrent frontier-lovephysics lane's scratch (not
mine); Godot/LOVE fixture rows untouched and byte-stable by non-touch.
