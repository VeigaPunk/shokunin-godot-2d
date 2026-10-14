# r71 verifier — pygame 2.6.1 headless first-contact battery (lane g2d)

Post-landing verification of committed tree at `a993cbe` ("r71: pygame
2.6.1 headless first contact — withholding window = io.DEFAULT_BUFFER_SIZE
(131072 on 3.14, frontier's 8KB falsified); compound 2-layer edge; 36/36")
plus report-last `44127af`. Commit content confirmed via
`git show --name-only a993cbe`: only `corpus/fixtures/pygame_probe.py`,
`corpus/fixtures/pygame_battery.py`, and seat reports — **zero** `.gd` /
`.tscn` / `run_battery.py` / `love_*` paths touched. `git status` on
`corpus/fixtures/` vs HEAD: clean (verified the committed tree, not a
working-tree delta). Waited ~15 min polling `git log` before landing at
11:33 (author commit) / 11:34 (report-last).

Host surface: `python3` 3.14.7, `io.DEFAULT_BUFFER_SIZE=131072`,
`pygame 2.6.1 (SDL 2.32.72)`, `PYTHONUNBUFFERED` unset on this host
(measured). 32 cores.

## Item 1 — `python3 corpus/fixtures/pygame_battery.py` → PASS (36/36, 4 idle reps + 1 loaded)

Run from repo root with `--runs corpus/live/r71-verifier/runs`. All 4 idle
runs: `totals: cases=36 pass=36 fail=0 launch_ok=True done_marker=True
exit=0`, exit 0, ~8.4s wall. A 5th run under 64×`yes` on 32 cores (2×
oversubscription, critic F3's load shape): **36/36 PASS**, elapsed 8.7s.

Receipts (all `verdicts.json` + `probe.stdout.txt`/`probe.stderr.txt`):
- `corpus/live/r71-verifier/runs/pygame-20261014T143451109406Z/`
- `corpus/live/r71-verifier/runs/pygame-20261014T143504742083Z/`
- `corpus/live/r71-verifier/runs/pygame-20261014T143513235942Z/`
- `corpus/live/r71-verifier/runs/pygame-20261014T143521690251Z/`
- `corpus/live/r71-verifier/runs/pygame-20261014T143824501908Z/` (loaded)

Bound-pinned observed values (idle min–max across 4 reps; loaded value):

| case | pinned | observed idle | loaded |
|---|---|---|---|
| c60_mean_undershoot | 15.5–16.66 | 16.056–16.061 | — |
| c60_fps_over60 | 60.5–64.0 | 62.11–62.5 | — |
| c0_hz_uncapped | 20000–1e9 | 6.88M–8.86M | — |
| popen_l1_wait_fast | 0.2–30.0 | 4.95–5.36 | 15.01 |
| popen_l2_wait_writer | 110–140 | 120.07–120.08 | 120.94 |
| popen_close_fast | 0.0–5.0 | 1.32–1.69 | **4.66** |
| popenbuf_l1_held | 110–180 | 124.88–125.47 | 136.23 |
| whs_held_to_exit | 180–3000 | 205.42–206.06 | 217.63 |
| whb_first_early | 60–190 | 105.22–105.55 | 115.74 |
| whb_early_bytes | 100000–210000 | 200007 (all 4) | — |
| whf_early_bytes | 60000–135000 | 126007 (all 4) | — |

Deterministic keys (`init_fail=0`, `driver=dummy`, `n`, `bufsize=131072`,
markers, `rest_len=0`, `early_bytes` figures, `alive_at_first=True`,
`frames_nopump=400`, `posted_survived=1`): byte-identical across reps.

**Verdict: AGREE.** Bound pins hold mid-range; deterministic keys stable.

## Item 2 — arm (b) withholding claim: author's corrected bound CONFIRMED, frontier's ~8KB FALSIFIED

The declared claim under test: "stdout withholding is a language-layer
window bounded by buffer size", falsifiable via a >8KB mid-run write
surfacing early. The author lands "**form CONFIRMED, claimed bound
FALSIFIED** — the bound is `io.DEFAULT_BUFFER_SIZE`=131072, not ~8KB".

Independent check — my own harness `corpus/live/r71-verifier/edge_scan.py`
(select+os.read on raw fd, buffered `python3 -c` child writing k bytes
mid-run, MARK-1 7B pending before the write). Receipts:
`edge_scan.out.txt`, `edge_fine.out.txt`. Measured:

| k | pending+k vs 131072 | first parent-visible |
|---|---|---|
| 4096 / 8192 / 8193 / 9000 / 65536 | ≤ B | exit-batched (~205ms on a ~207ms child) |
| 131064 (= B−8) | 131071 ≤ B | exit-batched |
| 131065 (= B−7) | 131072 = B | exit-batched |
| 131066 (= B−6) | 131073 > B | **105.1ms early** |
| 131071/131072/131073/200000 | > B | ~105.3ms early |

So the flush fires exactly when `pending + incoming >
io.DEFAULT_BUFFER_SIZE` — a strict inequality at 131072 on this build.
The author's lattice is confirmed cell-for-cell by an independent
harness: 9KB does NOT surface early (frontier's ~8KB figure falsified —
it is the text layer's staging chunk, never the release edge); ≥131072
does. The battery pins the right cells: `whs_*` (9000 held, early_bytes=0),
`whb_*` (200007B fused early delivery while `alive_at_first=True`,
MARK-1's 7B riding the flush), `whf_*` (126007B cumulative-fill flush —
granularity-independent, edge is buffer-fill not large-write bypass).

**Verdict: AGREE** — including the author's verdict *on* the claim
(corrected bound, not claim rejection). The frontier's mechanism
(writer-flush-bound, block buffering) was right; its number was the
pre-3.14 buffer size.

## Item 3 — arm (c) popen writer-bound + byte-exact → AGREE

`popen`: `l1`/`l2` byte-exact (`CHILD-MARK-1/2`), `l1_wait` ~5ms spawn
floor, `l2_wait` 120.07–120.08ms = the flushing child's own 120ms sleep,
`close_wait` 1.3–1.7ms, `rest_len=0`, `ret=0` — LOVE's shape confirmed,
no engine-layer fabrication seam (pygame contributes zero pipe
plumbing). `popen_buf` (non-flushing child): `l1_wait` 124.9–125.5ms —
withheld to child exit, the same surface seen from the probe side.

## Item 4 — arm (d) pump-free headless + viability → AGREE

400 frames, zero event calls, cadence unaffected, posted USEREVENT
survives (`posted_survived=1`), `pump_needed=false`; `init_fail=0`,
`driver=dummy`, `PYGAME_PROBE_DONE` every run. The probe pins the
headless contract in-fixture via `os.environ.setdefault` *before*
`import pygame` (pygame_probe.py:49-53) and the battery overrides it
explicitly (`PROBE_ENV`, pygame_battery.py:42-46) — deterministic under
the harness on this compositor host.

## Item 5 — prior batteries on the committed tree → AGREE

- `python3 corpus/fixtures/love_battery.py` → **19/19 PASS**, exit 0.
  Receipt: `corpus/live/r71-verifier/runs/love-20261014T143539777913Z/`.
- `python3 corpus/fixtures/run_battery.py` (Godot) → **PASS**, exit 0
  (128 PASS verdict rows incl. all negative controls + metas).
  Receipt: `corpus/live/r71-verifier/runs/20261014T143549785922Z/`.
- `git diff d9ae207..HEAD -- corpus/fixtures/` adds **only** the two
  pygame files; every other path in the r71 delta is seat scratch
  (`corpus/live/r71-*/`) or reports. Sibling-only confirmed.

## Item 6 — DEFECT (reproduced 2/2): `popen_buf` still inherits `PYTHONUNBUFFERED` — critic F4 only partially folded

The author strips `PYTHONUNBUFFERED` via `CHILD_ENV` — but only passes it
to the **withhold** children (pygame_probe.py:59,105). `popen_arm`
(pygame_probe.py:73-86) passes no `env`, so `popen`/`popen_buf` children
inherit the operator environment through the battery's
`env.update(PROBE_ENV)` path (PROBE_ENV pins SDL/pygame vars only,
pygame_battery.py:42-46).

Measured: `PYTHONUNBUFFERED=1 python3 corpus/fixtures/pygame_battery.py
--runs corpus/live/r71-verifier/runs` → **35/36, FAIL battery**, exit 1:

```
FAIL  popenbuf_l1_held  popen_buf|l1_wait_ms  '4.9' outside pinned bound (110.0, 180.0)
```

Receipts: `corpus/live/r71-verifier/runs/pygame-20261014T143756251353Z/`,
`...T143807142906Z/` (2/2 repro). The unbuffered child's l1 surfaces at
~5ms — the exit-batch shape the case exists to pin disappears, so the
battery fails for env-provenance, not runtime physics. Exactly critic
F4's flagged trap on the exact arm the critic named; the landed fix
covered the new withhold arms but not `popen_buf`. This host is clean
(`PYTHONUNBUFFERED` unset) so landed evidence stands — the defect is
portability (CI images commonly export it).

Smallest safe correction (per critic F4): pass `env=CHILD_ENV` in
`popen_arm`'s `subprocess.Popen` call — one argument.

**Verdict: PARTIAL** on env-robustness — real, reproducible,
single-argument fix.

## Overall

| item | verdict |
|---|---|
| 1. pygame_battery 36/36 committed tree | AGREE (4 idle + 1 loaded rep) |
| 2. withholding claim verdict + corrected bound | AGREE (independent edge scan, cell-for-cell) |
| 3. popen writer-bound + byte-exact | AGREE |
| 4. pump-free headless + viability | AGREE |
| 5. sibling byte-stability + prior batteries green | AGREE (LOVE 19/19, Godot PASS) |
| 6. PYTHONUNBUFFERED trap on popen_buf | PARTIAL — F4 half-folded, 2/2 repro FAIL |

## Remaining risks

- `popen_close_fast` (pin hi=5.0): idle 1.32–1.69ms, loaded-2× **4.66ms**
  — 0.34ms headroom. The critic measured 5.12ms (over-cap) on the same
  pin shape in the scout draft under the same load and recommended
  (0,20); the author kept 5.0. Passes today; it is the single
  near-edge bound in the battery and the most likely flake source.
- `whs_bufsize` pins `131072` exactly — interpreter-version-dependent
  (8192 on CPython ≤3.13). Author flagged it himself; honest per-build
  pin, intended pin behavior on a port.
- `popen_l2_wait_writer` (110,140): critic measured 136.5 under load on
  the scout equivalent; my loaded run saw 120.94 — margin holds but is
  thinner than the pin suggests.

## Receipts

- `corpus/live/r71-verifier/runs/pygame-*/verdicts.json` (4 idle PASS,
  2 PYTHONUNBUFFERED FAIL, 1 loaded PASS)
- `corpus/live/r71-verifier/runs/love-20261014T143539777913Z/verdicts.json`
- `corpus/live/r71-verifier/runs/20261014T143549785922Z/verdicts.json` (Godot)
- `corpus/live/r71-verifier/edge_scan.py` + `edge_scan.out.txt` +
  `edge_fine.out.txt` (independent flush-edge measurement)
