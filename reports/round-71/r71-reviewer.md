# r71 reviewer — pygame 2.6.1 headless first contact (lane g2d, wave w11)

Seat: **reviewer** (LEAF, dispatched specialist; recommendation only — the
canonical runtime is the sole judge). Host: devin — CPython 3.14.7,
`pygame 2.6.1 (SDL 2.32.72)`, `/usr/bin/python3`. Lane repo:
`~/Projects/shokunin/game-dev-2d-shokunin`. Write scope: this report +
`corpus/live/r71-reviewer/` only; no tracked edits, no git mutations.

Reviewed artifact (working tree; **no commit landed this round**): three
revisions of `corpus/fixtures/pygame_probe.py` + `pygame_battery.py`.

| rev | time (local) | probe sha256 | battery sha256 | state |
|---|---|---|---|---|
| 1 | 11:28:17 / 11:28:54 | `1b48060bb886…` | `0a579819658e…` | **RED 35/36, exit 1** |
| 2 | 11:30:18 / 11:30:24 | `4d426a3ba609…` | `f0630a9b1ca4…` | GREEN (rule fixed, pin widened) |
| 3 | 11:32:55 (battery only) | `4d426a3ba609…` | `0a579819658e…` | GREEN, **current at write time** |

Rev 3 = rev-2 probe + rev-1 battery (battery byte-identical to rev 1,
`diff -q` clean): the pin widening of rev 2 was reverted; the tight pin is
restored. Verified green 36/36 idle and under 32-hog load (receipts below).

Diff shape: two **new** files — `corpus/fixtures/pygame_probe.py` (242 lines)
and `corpus/fixtures/pygame_battery.py` (212 lines). No tracked file modified.

**`lsp` disclosure:** no `lsp` device on this host (`lsp`, `pyright`,
`basedpyright`, `pylsp`, `jedi-language-server`, `ruff-lsp` all absent from PATH
and not importable). Every reference/definition/usage claim below is a textual,
line-cited inspection — not a semantic `references` proof — recorded per seat
card rather than presented as semantic evidence.

## Findings by severity

### R1 — MEDIUM (raised, resolved in-round): pin widening was unnecessary and strictly weaker

Rev 2 widened `withhold_fill|early_bytes` from `(60000, 135000)` to
`(65536, 200000)` (`pygame_battery.py:94`). The fixed rule
(`pygame_probe.py:141`) yields **126007 deterministically** (structurally
14×9000 + 7-byte MARK-1; observed in 7 of my battery runs: 5 idle + 2 under
32-hog load), which the
**old** pin already contains — so the widening was not needed. It is strictly
weaker: it **accepts the rev-1 misattribution value 191543** (the exact defect
the rule fix addressed) and its upper edge is only **7 bytes** from `200007`
(the "whole payload flushed mid-run" value the arm exists to reject).
Independently demonstrated in my scratch:

| cell | probe | battery pin | result |
|---|---|---|---|
| A | rev-1 (`1b48060b…`) | rev-2 widened `(65536,200000)` | **36/36 PASS, observed 191543** — bug masked |
| B | rev-2 (`4d426a3b…`) | tight `(60000,135000)` | **36/36 PASS, observed 126007** — widening unneeded |

The author restored the tight pin at 11:32:55 (rev 3); I re-ran the tracked
artifact: **36/36 PASS** idle (`pg-runs/pygame-20261014T143329679841Z`) and
**36/36 PASS** under 32 `yes` hogs (`pg-runs-loaded/pygame-20261014T143343171499Z`,
`whf_early_bytes` observed 126007). The simplifier seat reached the same
conclusion independently (`reports/round-71/r71-simplifier.md` §9.4: "widened a
pin … without need … strictly reduces that row's discriminating power").
Receipts: `cellA/runs/pygame-20261014T143209201208Z/`,
`cellB/runs/pygame-20261014T143217576014Z/`.

Residual nit (R1b): `r71-author.md:108` still describes the value as "pinned as
a wide bound", which is stale relative to the final battery (tight pin). Report
text vs artifact drift; the artifact is the authority.

### R2 — MEDIUM (raised, resolved in-round): rev-1 landed battery was red

First landed revision: `python3 corpus/fixtures/pygame_battery.py` → **FAIL
35/36, exit 1**, single row `whf_early_bytes` observed `191543` vs pinned
`(60000,135000)` — deterministic: my 2/2
(`pg-runs/pygame-20261014T142915865093Z`, `…142927721427Z`), the author's own run
(`corpus/live/runs/pygame-20261014T142858275396Z/verdicts.json`), simplifier 2/2.

Root cause, measured: the rev-1 rule
`early_bytes = sum(n for ms,n in chunks if 0 <= ms < mark2_ms)` attributes every
read before the MARK-2-completing read to the withholding window. The fill arm's
**exit burst is 74007 B**, exceeding the 65536 B pipe capacity, so it arrives as
two reads; the first (`(205.36, 65536)` vs MARK-2 read `(205.41, 8471)`) is
counted "early": `126007 + 65536 = 191543`. My chunk timeline for the arm's
child (2/2): `[(105.23,65536),(105.26,60471),(205.36,65536),(205.41,8471)]`.
`withhold_small` (single 9014 B read) and `withhold_big` (7 B exit burst) escape
the bug by construction.

Fix (rev 2, 11:30): rule keys off EOF —
`early_bytes = sum(n for ms,n in chunks if 0 <= ms < eof_ms - 25)`
(`pygame_probe.py:136-141`). Author's own report documents this honestly
(`r71-author.md:93-98`). Rev 2/3 verdicts: **36/36 PASS** on all my runs
(idle `…143034575334Z`, `…143118354542Z`, `…143126878900Z`, `…143329679841Z`;
loaded `…143102300395Z` rev 2, `…143343171499Z` rev 3).

### R3 — LOW-MEDIUM (open): the exact flush edge is not pinned

The brief's arm (b) says "measure the flush edge … pin measured bound". The
landed battery pins the interpreter constant `bufsize=131072`
(`pygame_battery.py:78`) and a coarse bracket — 9000 B withheld
(`whs_early_none=0`), 200000 B early (`whb_early_bytes`), cumulative fill early
(`whf_early_bytes`) — but **not the edge cells 131071/131072**. My independent
measurements pin it exactly:

- `consolidated-edge.txt`: text layer — single 131071 **withheld 3/3**, 131072
  **early 3/3**, 131073 **early 3/3**; 8192/65536 withheld 2/2; 132×1000
  withheld 2/2; 135×1000 early 126002 2/2; 16×8192 withheld 2/2; 17×8192 early
  131074 2/2; buffered layer identical edge (131071 withheld, 131072 early).
- Cross-seat agreement: boundary `w_128k_lo/eq/hi` 3/3
  (`corpus/live/r71-boundary/withhold-raw.stdout.txt:9-17`); scout
  `edge_128k_*` 3/3 (`corpus/live/r71-scout/withhold_probe.stdout.txt:13-21`);
  simplifier bisect + explicit `buffering=8192` control
  (`reports/round-71/r71-simplifier.md` §2).
- Source-level: `textio.c` `chunk_size = 8192` (v3.14.7);
  `io.DEFAULT_BUFFER_SIZE = 128*1024` (`Modules/_io/_iomodule.h:81` v3.14.7) vs
  `8*1024` (v3.13.0) — the frontier's "~8KB" is the ≤3.13 default.

A two-cell fix (payload `bufsize-1` withheld / `bufsize` early) would convert the
bracket into a discriminator; the explicit `buffering=` control is the cheapest
model-falsifier. The landed fixture does derive the bound from the interpreter
(`BUFSIZE = io.DEFAULT_BUFFER_SIZE`, `pygame_probe.py:55`), so no stale constant
is baked in.

### R4 — LOW (open): coverage gaps in the landed battery

- `popen_buf` byte-exactness emitted but unpinned: `popen_buf|l1`, `|l2`,
  `|rest_len` carry no assertion (`pygame_battery.py:75` pins only `l1_wait_ms`).
  Arm (c)'s byte-exactness claim is asserted for the flushing child but not the
  buffered one.
- `pump|nopump_total_ms` (the "cadence unaffected" witness, ~3216–3226 ms) is
  emitted but unpinned; `pump_needed` (`pygame_probe.py:235`) and `frames_nopump`
  (`:233`) are probe **literals** — assertion-carried, the same accepted pattern
  as `love_battery.py:54`'s `pump_not_needed` (the simplifier's LOVE deletion
  candidate). The measured half is `posted_survived=1`.
- 33 of 69 emitted keys unpinned (simplifier census agrees); most are provenance
  echoes, the three above are load-bearing.

### R5 — LOW (open, residual): the `eof_ms - 25` margin is a heuristic

The rule assumes the mid-run burst lands ≥100 ms before EOF — true by
construction (the child sleeps 100 ms after the mid-run write) — and that the
parent reads promptly. Under 32 `yes` hogs the pins held with unchanged values
(loaded receipts: `whs_held_to_exit` 213.04 ms / `early_bytes=0`; `whf` 126007;
`whb` 200007). Not observed, recorded: a >75 ms parent stall between mid-run
flush and EOF would misattribute bytes to exit (flipping `whb/whf_early_bytes`);
a >25 ms stall between `withhold_small`'s single read and its EOF read would flip
`whs_early_none` (those reads are back-to-back in one select loop, so this needs
an extreme stall).

### R6 — INFO: sibling conventions, byte-stability, env

- Arm grammar `PYGAME-ARM <arm> | k=v` matches the tracked frontier probe
  (`corpus/live/frontier-pygame/pygame_probe.py:3`); the battery mirrors
  `love_battery.py` (`run_process`/`parse_arms`/`check`/`main`, payload keys
  modulo runtime names, `--runs` default `HERE.parent/"live"/"runs"`
  `pygame_battery.py:153`, run dirs `pygame-<stamp>` `:157`, PASS/FAIL exit
  `:196-208`).
- `sha256sum -c corpus/live/r71-reviewer/pre-landing.sha256` → **all OK** (37
  hashed paths: 35 lane fixtures incl. `run_battery.py`, `love_battery.py`,
  `love_probe/*`, `*.gd`, `*.tscn`, `*.cfg`, plus the 2 frontier-pygame probes).
  `git status`: only the two new untracked fixtures (plus
  pre-existing `corpus/live/frontier-lovephysics/` dirt owned by another seat).
- LOVE battery post-landing: **19/19 PASS, exit 0**
  (`love-runs/love-20261014T143050643150Z/verdicts.json`).
- Godot battery **not re-run** by this seat (heavy; verifier's seat). Stability
  argued by hash + static `CASES` (`run_battery.py:18+`) + zero references to the
  new files. Listed as a residual gap.
- Env: the probe pins `SDL_VIDEODRIVER=dummy`/`SDL_AUDIODRIVER=dummy`/
  `PYGAME_HIDE_SUPPORT_PROMPT=1` via `setdefault` before `import pygame`
  (`pygame_probe.py:49-53`); the battery **overrides** via `PROBE_ENV`
  (`pygame_battery.py:42-46`), and `viability|driver=dummy` is pinned, so a
  mis-env run fails loudly rather than silently binding a real window. Children
  strip `PYTHONUNBUFFERED` (`pygame_probe.py:59`) so the withholding physics
  cannot be silently invalidated.

### R7 — INFO: claim adjudication (brief claims vs measured)

- *"stdout withholding is a language-layer window bounded by buffer size"* —
  **CONFIRMED in form, bound corrected**: exit-bound below capacity, buffer-bound
  at it; measured edge **131072 B on this build**, not ~8KB. Author's report
  reaches the same verdict (`r71-author.md:41-57`).
- Declared falsifier *">8KB mid-run write surfacing early"* — **REFUTED on
  CPython 3.14.7**: 9000/65536/131071 B all withheld (my receipts); 131072+ early.
  The brief's falsifier is mis-parameterized for 3.14; the landed arms test the
  correct relation instead.
- Cadence (a): tick(60) **62.1–62.5 Hz, never 60** (my ref mean 16.058 ms; probe
  16.053–16.063; 32-hog 16.051; min 15.05 observed); `tick_busy_loop(60)` tighter
  tail; uncapped 4.5–7.2 MHz (probe, per-frame `perf_counter`) vs 24.9 MHz (my
  trivial 200k loop) — **loop-body-dependent**, so the battery's floor-only pin
  `(20000, 1e9)` (`pygame_battery.py:63`) is the honest shape; a tight MHz pin
  would be dishonest. Bound pins held under 32 hogs.
- Popen (c): writer-bound + byte-exact confirmed — `l2_wait` 120.06–120.09 ms ≈
  the child's own 120 ms sleep, `rest_len=0`, close ~1.5 ms — **LOVE's shape**.
  `popen_buf` l1 held to child exit (124.9–132.7 ms).
- Pump (d): pump-free headless confirmed — 400 frames, zero event calls, posted
  USEREVENT survives, no error.
- Viability: `init (5,0)`, `driver=dummy`, `flags=0x1000000`,
  `PYGAME_PROBE_DONE`, exit 0.

## Verification gaps (residual)

1. Godot battery replay on the post-landing tree — left to the verifier seat
   (hash-level stability verified here).
2. Exact-edge cells absent from the landed artifact (R3); my receipts cover them
   independently but they are not battery-enforced.
3. Rule-margin robustness beyond 32-hog load (R5) untested.
4. `r71-author.md:108` ("pinned as a wide bound") is stale vs the final tight pin
   (R1b) — doc drift only.
5. No `lsp` device → no semantic reference/definition checks; all claims textual.

## Receipts (all under `corpus/live/r71-reviewer/` unless noted)

- Rev-1 red: `pg-runs/pygame-20261014T142915865093Z/`, `…142927721427Z/`
- Rev-2 green: `pg-runs/pygame-20261014T143034575334Z/`, `…143118354542Z/`,
  `…143126878900Z/`; loaded `pg-runs-loaded/pygame-20261014T143102300395Z/`
- Rev-3 (final) green: `pg-runs/pygame-20261014T143329679841Z/`; loaded
  `pg-runs-loaded/pygame-20261014T143343171499Z/` (whf 126007 vs tight pin)
- Cells A/B: `cellA/runs/pygame-20261014T143209201208Z/`,
  `cellB/runs/pygame-20261014T143217576014Z/`
- Edge: `consolidated-edge.{json,txt}`, `withhold_receipts.{json,txt}`,
  `flush_edge_matrix.{json,txt}`, `wh_pg_receipts.json`
- Probe lattice: `probe-run1.stdout.txt`, `probe-run2.stdout.txt` (+ stderr)
- Cadence/ref: `pygame_ref_probe.py` (run output in shell log)
- Hashes: `pre-landing.sha256`, `landed-hashes.txt`; snapshots
  `probe-snapshot-112817.py` (rev 1), `battery-snapshot-112854.py` (rev 1)
- LOVE post-landing: `love-runs/love-20261014T143050643150Z/verdicts.json`
- Cross-seat: `corpus/live/r71-boundary/withhold-raw.stdout.txt`,
  `corpus/live/r71-scout/withhold_probe.stdout.txt`,
  `reports/round-71/r71-simplifier.md` §2/§9.4

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
