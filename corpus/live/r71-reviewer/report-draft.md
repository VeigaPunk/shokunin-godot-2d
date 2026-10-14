# r71 reviewer — pygame 2.6.1 headless first contact (lane g2d, wave w11)

Seat: **reviewer** (LEAF, dispatched specialist; recommendation only). Host:
devin — CPython 3.14.7, `pygame 2.6.1 (SDL 2.32.72)`, `/usr/bin/python3`.
Lane repo: `~/Projects/shokunin/game-dev-2d-shokunin`.

Reviewed revisions (working tree; no commit landed this round):

| rev | probe sha256 | battery sha256 | state |
|---|---|---|---|
| 1 (14:28:17/14:28:54) | `1b48060bb886…` | `0a579819658e…` | **RED 35/36, exit 1** |
| 2 (14:30:18/14:30:24) | `4d426a3ba609…` | `f0630a9b1ca4…` | GREEN 36/36 (5 runs) |

Diff shape: two **new** files — `corpus/fixtures/pygame_probe.py` (242 lines)
and `corpus/fixtures/pygame_battery.py` (212 lines). No tracked file modified
(`git status`; `sha256sum -c` over 35 pre-landing fixture hashes all OK).

**`lsp` disclosure:** no `lsp` device on this host (`lsp`, `pyright`,
`basedpyright`, `pylsp`, `jedi-language-server`, `ruff-lsp` all absent from PATH
and not importable). Every reference/definition/usage claim below is a
**textual line-cited inspection**, not a semantic `references` proof — recorded
per seat card rather than presented as semantic evidence.

## Findings by severity

### R1 — MEDIUM (open): `whf_early_bytes` pin widened beyond need; strictly weaker

`pygame_battery.py:94` pins `withhold_fill|early_bytes` at `(65536, 200000)`.
The fixed accounting rule (`pygame_probe.py:141`) yields **126007
deterministically** (5/5 of my runs, idle and 32-hog loaded; the flush boundary
is structurally 14×9000 + 7-byte MARK-1). The pre-fix pin `(60000, 135000)`
**passes** with the fixed probe, so the widening was unnecessary — and it is
strictly weaker: it now **accepts the rev-1 misattribution value 191543**
(`126007 + 65536`), the exact failure the rule fix addressed. Independently
reproduced in my scratch:

| cell | probe | battery pin | result |
|---|---|---|---|
| A | rev-1 (`1b48060b…`) | rev-2 widened `(65536,200000)` | **36/36 PASS, observed 191543** — bug masked |
| B | rev-2 (`4d426a3b…`) | tight `(60000,135000)` | **36/36 PASS, observed 126007** — widening unneeded |

The pin's upper edge is also only **7 bytes** from `200007` (whole payload
flushed mid-run — the failure the arm exists to catch). Recommendation: restore
`(60000,135000)` or tighten to `(120000,140000)`; the fixed rule's value is
stable across load. Receipts: `cellA/runs/pygame-20261014T143209201208Z/`,
`cellB/runs/pygame-20261014T143217576014Z/`.

### R2 — MEDIUM (resolved in-round): rev-1 landed battery was red

First landed revision: `python3 corpus/fixtures/pygame_battery.py` → **FAIL
35/36, exit 1**, single row `whf_early_bytes` observed `191543` vs pinned
`(60000,135000)` — reproduced 2/2 by me, plus the author's own run
(`corpus/live/runs/pygame-20261014T142858275396Z/verdicts.json`) and 2/2 by the
simplifier seat. Deterministic, not flaky.

Root cause (measured, not inferred): the rev-1 rule
`early_bytes = sum(n for ms,n in chunks if 0 <= ms < mark2_ms)` attributes every
read before the MARK-2-completing read to the withholding window. The fill arm's
**exit burst is 74007 B**, which exceeds the 65536 B pipe capacity and therefore
arrives as two reads — `(205.36, 65536)` and `(205.41, 8471)`; the first is
counted "early": `126007 + 65536 = 191543`. My chunk timeline
(`corpus/live/r71-reviewer/`, fill child, 2/2): `[(105.23,65536),(105.26,60471),
(205.36,65536),(205.41,8471)]`; `withhold_small`/`withhold_big` escape because
their exit bursts are one read (9014 B / 7 B).

Fix (rev 2, 14:30): rule now keys off EOF —
`early_bytes = sum(n for ms,n in chunks if 0 <= ms < eof_ms - 25)`
(`pygame_probe.py:136-141`); with the same revision the pin was widened (R1).
Rev 2 verdict: **36/36 PASS, exit 0** — my runs:
`pg-runs/pygame-20261014T143034575334Z`, `…143118354542Z`, `…143126878900Z`,
plus 32-hog loaded `pg-runs-loaded/pygame-20261014T143102300395Z`.

### R3 — LOW-MEDIUM (open): the exact flush edge is not pinned

The brief's arm (b) says "measure the flush edge … pin measured bound". The
landed battery pins the interpreter constant `bufsize=131072`
(`pygame_battery.py:78`) and a coarse bracket — 9000 B withheld
(`whs_early_none=0`), 200000 B early (`whb_early_bytes`), cumulative fill early
(`whf_early_bytes`) — but **not the edge cells 131071/131072**. My independent
measurements pin it exactly:

- `consolidated-edge.txt` (text layer): single 131071 **withheld 3/3**, 131072
  **early 3/3**, 131073 **early 3/3**; 8192/65536 withheld 2/2; 132×1000
  withheld; 135×1000 early 126002; 16×8192 withheld; 17×8192 early 131074;
  buffered layer identical edge.
- Cross-seat agreement: boundary `w_128k_lo/eq/hi` 3/3
  (`corpus/live/r71-boundary/withhold-raw.stdout.txt:9-17`), scout
  `edge_128k_*` 3/3 (`corpus/live/r71-scout/withhold_probe.stdout.txt:13-21`),
  simplifier bisect + explicit `buffering=8192` control
  (`reports/round-71/r71-simplifier.md` §2).
- Source-level: `textio.c` chunk_size=8192 (v3.14.7); `io.DEFAULT_BUFFER_SIZE`
  = `128*1024` (`_iomodule.h:81` v3.14.7) vs `8*1024` (v3.13.0) — the frontier's
  "~8KB" is the ≤3.13 default.

A one-cell fix (payload `bufsize-1` withheld / `bufsize` early) would turn the
bracket into a discriminator; the explicit `buffering=` control is the cheapest
model-falsifier the simplifier demonstrated.

### R4 — LOW (open): coverage gaps in the landed battery

- `popen_buf` byte-exactness is emitted but unpinned: `popen_buf|l1`, `|l2`,
  `|rest_len` carry no assertion (`pygame_battery.py:75` pins only `l1_wait_ms`).
  Arm (c) claims byte-exactness for the Popen surface; the buffered child is the
  withholding case and its bytes are not asserted.
- `pump|nopump_total_ms` (the "cadence unaffected" witness, ~3216–3226 ms) is
  emitted but unpinned; `pump_needed` (`pygame_probe.py:235`) and
  `frames_nopump` (`:233`) are probe **literals** — assertion-carried, the same
  accepted pattern as `love_battery.py:54`'s `pump_not_needed` (the simplifier's
  LOVE deletion candidate). The measured half is `posted_survived=1`.
- 33 of 69 emitted keys are unpinned (simplifier census agrees); most are
  provenance echoes, but the three above are load-bearing.

### R5 — LOW (open): the `eof_ms - 25` margin is a heuristic

The rule assumes (a) the mid-run burst lands ≥100 ms before EOF — true by
construction (the child sleeps 100 ms after the mid-run write) — and (b) the
parent reads promptly. Under 32 `yes` hogs the pins held with unchanged values
(loaded receipt: `whs_held_to_exit` 213.04 ms, `early_bytes=0`; `whf` 126007;
`whb` 200007). Residual, not observed: a >75 ms parent stall between mid-run
flush and EOF would misattribute bytes to exit (flipping `whb/whf_early_bytes`),
and a >25 ms stall between `withhold_small`'s single read and its EOF read would
flip `whs_early_none` (the read pair is back-to-back in one select loop, so this
needs an extreme stall). Recorded as residual risk, not a defect.

### R6 — INFO: sibling conventions and byte-stability

- Arm grammar `PYGAME-ARM <arm> | k=v` matches the tracked frontier probe
  (`corpus/live/frontier-pygame/pygame_probe.py:3`); battery mirrors
  `love_battery.py` helpers/payload (`run_process`/`parse_arms`/`check`/`main`,
  payload keys modulo runtime names, `--runs` default `HERE.parent/"live"/"runs"`
  `pygame_battery.py:153`, run dirs `pygame-<stamp>` `:157`, exit 0/1 `:196-208`).
- `sha256sum -c corpus/live/r71-reviewer/pre-landing.sha256` → **all OK** (35
  files incl. `run_battery.py`, `love_battery.py`, `love_probe/*`, `*.gd`,
  `*.tscn`, `*.cfg`). `git status`: only the two new untracked fixtures (plus
  pre-existing `corpus/live/frontier-lovephysics/` dirt owned by another seat).
- LOVE battery post-landing: **19/19 PASS, exit 0**
  (`love-runs/love-20261014T143050643150Z/verdicts.json`).
- Godot battery **not re-run** by this seat (heavy; verifier's seat). Stability
  argued by hash + static `CASES` (`run_battery.py:18+`) + zero references to the
  new files. Residual gap, listed below.

### R7 — INFO: claim adjudication (brief claims vs measured)

- *"stdout withholding is a language-layer window bounded by buffer size"* —
  **CONFIRMED in shape, bound corrected**: the window is exit-bound below the
  buffer capacity and buffer-bound at it; measured edge **131072 B on this
  build**, not ~8KB. (`BUFSIZE = io.DEFAULT_BUFFER_SIZE`, `pygame_probe.py:55` —
  the fixture carries no stale constant; `whs_bufsize=131072` is a
  version-specific pin by design, documented in the battery docstring.)
- Declared falsifier *">8KB mid-run write surfacing early"* — **REFUTED on
  CPython 3.14.7** (9000/65536/131071 B all withheld; 131072+ early). The
  brief's falsifier is mis-parameterized for 3.14; the landed arms test the
  correct relation instead.
- Cadence (a): tick(60) **62.1–62.5 Hz, never 60** (my ref mean 16.058 ms;
  probe 16.053–16.063; 32-hog 16.051); `tick_busy_loop(60)` tighter tail;
  uncapped 4.5–7.2 MHz (probe, 1200 frames with per-frame perf_counter) vs
  24.9 MHz (my trivial 200k loop) — **loop-body-dependent**, so the battery's
  floor-only pin `(20000, 1e9)` (`:63`) is the honest shape; a tight MHz pin
  would be dishonest. Bounds held under 32 hogs.
- Popen (c): writer-bound + byte-exact confirmed (l2_wait 120.06–120.09 ≈ the
  child's own 120 ms sleep; `rest_len 0`; close ~1.5 ms) — **LOVE's shape**.
  `popen_buf` l1 held to child exit (124.9–132.7 ms).
- Pump (d): pump-free headless confirmed — 400 frames, zero event calls, posted
  USEREVENT survives; no error.

## Verification gaps (residual)

1. Godot battery replay on the post-landing tree — left to the verifier seat
   (hash-level stability is verified here).
2. Author's `r71-author.md` was not landed at review time; its claims are not
   checked here (the battery receipt and my replay cover the artifact).
3. Exact-edge cells are absent from the landed artifact (R3); my receipts cover
   them independently but they are not battery-enforced.
4. Rule-margin robustness beyond 32-hog load (R5) untested.
5. No `lsp` device → no semantic reference/definition checks; all claims are
   textual line-cited (recorded).

## Receipts (all in `corpus/live/r71-reviewer/` unless noted)

- Rev-1 red: `pg-runs/pygame-20261014T142915865093Z/`, `…142927721427Z/`
- Rev-2 green: `pg-runs/pygame-20261014T143034575334Z/`, `…143118354542Z/`,
  `…143126878900Z/`; loaded: `pg-runs-loaded/pygame-20261014T143102300395Z/`
- Cell A/B: `cellA/runs/pygame-20261014T143209201208Z/`,
  `cellB/runs/pygame-20261014T143217576014Z/`
- Edge: `consolidated-edge.{json,txt}`, `withhold_receipts.{json,txt}`,
  `flush_edge_matrix.{json,txt}`, `wh_pg_receipts.json`
- Probe lattice: `probe-run1.stdout.txt`, `probe-run2.stdout.txt` (+ stderr)
- Cadence/ref: `pygame_ref_probe.py` + run output in this report's shell log
- Hashes: `pre-landing.sha256`, `landed-hashes.txt`
- LOVE post-landing: `love-runs/love-20261014T143050643150Z/verdicts.json`
- Snapshots: `probe-snapshot-112817.py` (rev 1), `battery-snapshot-112854.py`
  (rev 1)

## Method (exact commands, from repo root)

```
python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r71-reviewer/pg-runs
python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r71-reviewer/pg-runs-loaded   # 32 yes hogs
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 \
    python3 -u corpus/fixtures/pygame_probe.py
python3 corpus/fixtures/love_battery.py --runs corpus/live/r71-reviewer/love-runs
sha256sum -c corpus/live/r71-reviewer/pre-landing.sha256
python3 corpus/live/r71-reviewer/consolidated_edge.py
```
