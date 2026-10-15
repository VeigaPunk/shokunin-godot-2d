# Round 71 scribe — pygame 2.6.1 headless first contact (third runtime): withholding edge re-measured at 131072 B (frontier ~8KB falsified); 36/36 battery; verifier PARTIAL on env trap

Seat: g2d scribe (LEAF, report+scratch only). Host: devin — CPython 3.14.7,
`pygame 2.6.1 (SDL 2.32.72)` at `/usr/bin/python3`, 32 cores, compositor
present (Hyprland/Wayland). Lane repo
`~/Projects/shokunin/game-dev-2d-shokunin`. Write scope honored: this report +
`corpus/live/r71-scribe/` only. No tracked edits, no git mutations, no
subagent dispatch, no rerun of the round's batteries — every execution claim
below is seat-run with a receipt path + sha256; the independent post-landing
replay is the verifier's. Provenance pins: `corpus/live/r71-scribe/provenance.json`.

## Landing status (report time 2026-10-14T14:41Z)

- HEAD `44127af` — "r71 report-last: adjudicator + LOG + SCORECARD + landed
  seat reports" (14:33:49Z); work commit `a993cbe` — "r71: pygame 2.6.1
  headless first contact — withholding window = io.DEFAULT_BUFFER_SIZE
  (131072 on 3.14, frontier's 8KB falsified); compound 2-layer edge; 36/36"
  (14:33:33Z).
- `git show --stat a993cbe` → `corpus/fixtures/pygame_probe.py` (242 lines),
  `corpus/fixtures/pygame_battery.py` (212 lines) + 8 seat reports;
  `git show --name-only a993cbe | grep -cE 'run_battery|\.gd$|\.tscn$|love_'`
  → **0**. `git diff --stat d9ae207..HEAD -- corpus/fixtures/` → only the two
  new pygame files (+454). Sibling-only confirmed.
- Fixture hashes (my `sha256sum` at report time): probe
  `4d426a3ba6098186c8ef4d6c6cdf6e4e8ecd17dc7af3828ceb91ccb510bb4738`, battery
  `0a579819658ee9be9dbd3e6fb81414a036f712a5d03358c7b57a8481a2cec47f` (= the
  reviewer's rev-3 "current at write time").
- Untracked/uncommitted at report time (operator-owned commit):
  `reports/round-71/r71-reviewer.md`, `reports/round-71/r71-verifier.md`,
  `corpus/live/r71-verifier/`.
- Round timeline (my watcher, `corpus/live/r71-scribe/watch.log`, frozen at
  sha256 `f759285e…`, 26 lines): scout scratch 14:19:40Z → author scratch
  14:22:26Z → `reports/round-71` first file 14:24:11Z → fixtures present
  14:28:27Z → HEAD `44127af` + verifier scratch 14:35:58Z.

## Claim adjudication (the round's verdict)

Claim under test: *"stdout withholding is a language-layer window bounded by
buffer size"* — frontier bound ~8KB, falsifiable via a >8KB mid-run write
surfacing early (`fa-pygame.md:76-84,119`).

- **Form CONFIRMED — language layer, not SDL/pygame.** Identical edge with
  pygame fully initialized (`r71-baseline` `--wh-init` cells) and with a plain
  `python3 -c` child (landed probe's withhold children import no pygame);
  scout `small_pg` withheld / `big_200k_pg` early = plain-Python cells.
  pygame contributes zero pipe plumbing.
- **Constant FALSIFIED.** The parent-visible release edge on this build is
  `io.DEFAULT_BUFFER_SIZE` = **131072 B** (CPython 3.14.7; GH-118144 raised it
  from 8192 in 3.14; ≤3.13 carries 8192). The frontier's "~8KB" is the text
  layer's `chunk_size` staging threshold, never the release edge.
  Exact edge, independently reproduced: **131071 withheld / 131072 early**
  (boundary 3/3, scout 3/3, reviewer 3/3, simplifier bisect 3/3; verifier's
  own scan narrows it to a strict inequality — `pending + incoming > 131072`
  fires, 131065 exit-batched / 131066 early).
- **Declared falsifier REFUTED on this build (mis-parameterized).** A single
  9000 B mid-run write does **not** surface early — `withhold_small` 9014 B
  held to exit, `early_bytes=0` 3/3; 65536/131071 also held (seats' scans).
  Early release fires only at a single write ≥131072 (raw write-through), on
  overflow of the buffered prefix, or on `flush`/`-u`. The landed battery
  therefore tests the correct relation (9 KB held vs 200 KB early vs
  cumulative-fill crossing) rather than the brief's 8 KB cell.
- **Two-layer compound semantics** (boundary, 2–3 reps/cell): textio pending
  8192 (staging) + BufferedWriter 131072 (visibility); an exactly-full buffer
  does **not** flush (`16×8192`, `65536+65536`, `131071+1` all withheld);
  compound window = **139263 B fully invisible**, the 139264th byte surfaces
  the buffered 131072; granularity-conditional (a single 139263 B write is
  fully early). Verifier's item 2, reviewer R7, adjudicator, author all agree.

Landed battery: **36/36 PASS, exit 0** on 3 author reps, 4 verifier idle reps,
1 verifier loaded rep (64×`yes` on 32 cores, 2× oversubscription), reviewer
idle + loaded-32 — deterministic keys byte-identical; bound keys mid-range.

## Evidence ledger (commands, outcomes, receipts)

### author (fixtures + self-verify)
- `python3 corpus/fixtures/pygame_battery.py` → `totals: cases=36 pass=36
  fail=0 launch_ok=True done_marker=True exit=0`, ~9.5 s wall. Receipts:
  `corpus/live/runs/pygame-20261014T143028666014Z|…143041126847Z|…143049554160Z`
  (sha256 `8ff37f2c…`, `b8915b7e…`, `ec40f866…`); `probe_exit=0`,
  `probe_error=None`.
- Measured cells (author + verifier): `tick(60)` dt_mean 16.056–16.073 ms,
  fps 62.11–62.5 (~62 Hz, never 60; `int(1000/fps)` SDL_Delay undershoot);
  `tick()` uncapped 6.5–8.9 MHz spin, dt_mean 0.0 ms; `popen` l1 4.95–5.36 ms,
  l2 120.06–120.08 ms (= flushing child's own 120 ms sleep), close 1.3–1.7 ms,
  `rest_len=0` — **LOVE's writer-bound shape**; `popen_buf` l1 124.9–125.5 ms
  held to exit; pump-free: 400 frames, zero event calls, `posted_survived=1`.
- Dev-time honesty (recorded by the author): first authored run scored 35/36 —
  `whf_early_bytes` metric misattributed the exit burst (191543 vs 126007);
  rule fixed to `ms < eof_ms - 25`, re-pinned (`r71-author.md:93-98`).

### verifier (post-landing, committed tree `a993cbe`+`44127af`)
- 4 idle + 1 loaded (2× oversubscription) runs → **36/36 PASS** each. Receipts
  `corpus/live/r71-verifier/runs/pygame-20261014T143451109406Z` (`7267a63f…`),
  `…143504742083Z`, `…143513235942Z`, `…143521690251Z`, loaded
  `…143824501908Z` (`239a7574…`).
- Independent edge scan (`edge_scan.py`, `edge_scan.out.txt`,
  `edge_fine.out.txt`): 4096/8192/9000/65536/131064/131065 exit-batched;
  131066…200000 early at ~105 ms — strict inequality at 131072.
- Prior batteries on the committed tree: LOVE **19/19** (`love-…143539777913Z`,
  `ad550fd9…`), Godot **PASS** (`…143549785922Z`, `c3257efd…`).
- **PARTIAL (item 6)** — see conflict 1 below: `PYTHONUNBUFFERED=1` run →
  35/36, exit 1, 2/2 repro (`…143756251353Z`, `d87b26ed…`).

### baseline (independent second implementation, scratch-only)
- `54/54 ×3` + LOVE 19/19 + Godot 88/88 flagless replays; scratch
  `corpus/live/r71-baseline/` (promotion-ready, not promoted — write scope).

### scout (prototype, handoff)
- Prototype battery **83/83 ×3** incl. a stress rep; full edge matrix
  (`withhold_probe.stdout.txt`), landing notes; edge relations
  `bufsize−1/bufsize/bufsize+1` exist in the prototype
  (`corpus/live/r71-scout/pygame_battery.py:115-126`).

### boundary / critic / reviewer / simplifier (independent measurement seats)
- boundary: two-layer lattice + R1–R5 visibility rules, event queue cap
  **exactly 65535** (post #65536 raises `pygame.error`), cadence knife-edges
  (fps 1000 sleeps 1 ms / fps 1001 spins), stderr line-buffered edges.
- critic: pre-landing attack; scout prototype `75/75` idle, **`73/75` at
  64-hog** load (`popen_close_fast` 5.12 ms vs `(0,5)`; `withhold_seg_over_partial`);
  F1–F7 including the 128 KiB mechanism trace and the F4 `PYTHONUNBUFFERED` trap.
- reviewer: rev-1 red 35/36 → rev-2/3 green; **36/36 idle + 36/36 loaded-32**
  on the final artifact; `sha256sum -c pre-landing.sha256` 37 paths OK; LOVE
  19/19 post-landing; findings R1–R7.
- simplifier: LOVE **19/19** (`corpus/live/r71-simplifier/runs-love/love-20261014T142144814250Z/verdicts.json`,
  `9b61da0c…`); flush-edge bisect + explicit `buffering=` control (edge moves
  with the declared buffer); deletion candidates found but **not applied**
  (byte-stability axis is the round's stop condition).

### adjudicator (report-last)
- `ADMIT-with-correction` (`r71-adjudicator.md:45-50`): bound corrected
  (8192 → `io.DEFAULT_BUFFER_SIZE`=131072 as a host-provenance row), window
  form + language-layer attribution confirmed; additive sibling, LOVE/Godot
  untouched.

## Conflicts for the canonical judge (verbatim, with refs)

1. **`PYTHONUNBUFFERED` scope — author/adjudicator overstate, verifier right.**
   Author `r71-author.md:32-34`: "`PYTHONUNBUFFERED` is stripped from child env
   so operator environment cannot quietly invalidate the buffered-pipe
   physics." Adjudicator `r71-adjudicator.md:23-24`: "`PYTHONUNBUFFERED`
   pinned per-child." Verifier `r71-verifier.md:119-148`: "`popen_arm`
   (pygame_probe.py:73-86) passes no `env` … **35/36, FAIL battery**, exit 1 …
   **Verdict: PARTIAL** on env-robustness — real, reproducible,
   single-argument fix." My own read confirms: `CHILD_ENV` exists
   (`pygame_probe.py:59`) but is passed only in `withhold_arm`
   (`pygame_probe.py:105`); `popen_arm` passes none. On this host
   (`PYTHONUNBUFFERED` unset) the landed evidence stands; the defect is
   portability.
2. **Exact-edge pins — adjudicator line vs landed artifact + reviewer R3.**
   Adjudicator `r71-adjudicator.md:22-24`: "pins re-derived to relations
   (bufsize−1/bufsize/bufsize+1)". Reviewer R3 `r71-reviewer.md:89-115`: "the
   exact flush edge is not pinned … R3 — LOW-MEDIUM (open)". My read of the
   landed CASES agrees with the reviewer: the relations live in the scout
   prototype (`r71-scout/pygame_battery.py:115-126`), while the landed battery
   pins `whs_bufsize = "131072"` exactly plus bracket arms (9000 held /
   200000 early / 200×1000 fill). The landed artifact is the authority; R3 is
   open (suggested two-cell fix: payload `bufsize−1` withheld / `bufsize` early).
3. **Doc drift.** Reviewer R1b `r71-reviewer.md:60-62`: `r71-author.md:108`
   ("pinned as a wide bound") is stale vs the final tight pin
   `whf_early_bytes (60000,135000)`. Artifact is the authority.
4. **Near-edge bound (open).** Critic F3 `r71-critic.md:122-137`: scout
   `popen_close_fast` measured 5.12 ms vs `(0,5)` under 64 hogs, recommended
   `(0,20)`; author kept `(0,5)`. Verifier `r71-verifier.md:163-167`: loaded-2×
   observed 4.66 ms — **0.34 ms headroom**, "the most likely flake source".
5. **Scout control anomaly (unattributed).** Simplifier `r71-simplifier.md:215-222`:
   scout pygame-parity cells `small_pg`/`big_200k_pg` recorded `rc=2`,
   `total_bytes=0`, `integrity=0` 3/3; the same child invocation reproduces
   clean (`rc=0`) in the simplifier's harness — cause not attributed; the
   pygame-child edge is pinned by the simplifier/boundary controls instead.
6. **Seat accounting timing.** Adjudicator `r71-adjudicator.md:38-43` ("Reviewer
   not yet landed; verifier dispatched for committed tree") was written before
   the reviewer landed (14:34Z) and before the verifier replay (14:35–14:39Z);
   both are now present. This scribe report is the last r71 seat artifact.

## Sibling byte-stability / provenance

- Godot/LOVE rows byte-stable by construction and verified: `a993cbe` touches
  zero `.gd`/`.tscn`/`run_battery.py`/`love_*` paths (grep count 0);
  `git diff --stat d9ae207..HEAD -- corpus/fixtures/` = the 2 new files only;
  LOVE 19/19 (verifier `ad550fd9…`, simplifier `9b61da0c…`, reviewer
  `love-…143050643150Z`); Godot PASS (verifier `c3257efd…`).
- Frontier provenance pinned by this seat: `reports/frontier/fa-pygame.md`
  sha256 `c3ee826b…` (falsified ~8KB at `:78-79`; open question `:119`);
  scratch `pygame_probe.py b8f95df2…`, `capture_probe.py f3da63d3…`,
  `run.stdout.txt c283bbfb…`, `run.stderr.txt 5ebca6a8…`,
  `env-matrix.txt 381eeeba…`, `capture.stdout.txt 05864650…`.
- Frontier mechanism claims that survived: writer-flush-bound pipes (no
  Godot-style splice seam), no pump needed headless, banner/env requirements
  (`SDL_VIDEODRIVER=dummy` hard requirement; `PYGAME_HIDE_SUPPORT_PROMPT=1`;
  avx2 `RuntimeWarning` on stderr), `get_wm_info` SIGSEGV on the wayland path
  (fixtures must not call it). Its number did not survive: 8 KiB → 131072 B.

## Known limits / out of scope

- This seat re-executed nothing (no decoration reruns); execution evidence is
  seat-run receipts + hashes above; the independent post-landing replay is the
  verifier's (AGREE ×5, PARTIAL ×1).
- Open items carried: `PYTHONUNBUFFERED` trap on `popen_buf` (single-arg
  `env=CHILD_ENV` fix per verifier); exact-edge cells not battery-enforced
  (reviewer R3); `whs_bufsize=131072` is per-build (8192 on CPython ≤3.13 —
  intended pin behavior on a port); `popen_close_fast` 0.34 ms headroom;
  mixer/audio semantics under `SDL_AUDIODRIVER=dummy` unmeasured; event-queue
  cap 65535 measured (boundary) but not pinned; no LSP device on this host
  (all seat call-graph claims are textual/AST, disclosed by the seats).
- r72 seat scratch dirs were already present at report time (next round in
  flight) — outside r71 scope. Commit/push are operator-owned; this seat made
  no git mutations.
- `corpus/live/r71-scribe/watch.log` is tracked (committed by the operator's
  report-last `44127af`) and frozen at sha256 `f759285e…` (watcher killed at
  report time).

## Artifact paths

- Report: `reports/round-71/r71-scribe.md`
- Scratch: `corpus/live/r71-scribe/provenance.json`, `watch.sh`, `watch.log`
- Landed: `corpus/fixtures/pygame_probe.py`, `corpus/fixtures/pygame_battery.py`
  (commits `a993cbe`, `44127af`)
- Receipts: `corpus/live/runs/pygame-20261014T143028666014Z|…143041126847Z|…143049554160Z/`,
  `corpus/live/r71-verifier/runs/pygame-*/`, `…/love-20261014T143539777913Z/`,
  `…/20261014T143549785922Z/`
- Seat reports: `reports/round-71/r71-{author,scout,baseline,boundary,critic,reviewer,simplifier,verifier,adjudicator}.md`
