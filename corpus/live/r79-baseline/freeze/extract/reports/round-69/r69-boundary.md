# Round 69 — boundary recon: fabrication-window REFERENT knife-edges + merged-sha coverage edges

## Scope and method

LEAF boundary seat, scratch-only and report-only. I wrote only this report
and `corpus/live/r69-boundary/`. No tracked fixture, runner, CASES row,
lesson, LOG, or SCORECARD entry touched; no subagent dispatch; no git
mutation. `corpus/fixtures/__pycache__/` is the battery's own by-product.

Assignment (lane brief, verbatim edges): (1) gap below the spawn-overhead
floor (~<2ms — can the write ever win?); (2) gap == offset (80,80 —
degenerate cell); (3) offset>gap cells (240/100 — write lands post-tail by
construction); (4) does the r68 timeout/drain nondeterminism interact with
longer gaps (800ms)?

**Provenance.** The author's diff was NOT in the tree when my probe window
opened: tracked `descendant_pipe_probe.gd` was sha256 `5c5c629a…` (r68
bytes), `run_battery.py` `55314bb5…`. I emulated the declared axis-move on a
scratch copy (`proj/descendant_pipe_probe.gd` sha `bfd68d76…`) — the same
opt-in `--midline-gap-ms=N` flag (default 200) feeding the banner field and
`OS.delay_msec`, matching the author's briefed grammar. The diff then landed
mid-session and the runner was still being amended at report time (observed
`55314bb5…` → `5602566c…` → `56adf7cb…`); the fixture is stable at
`c86bda84…` — the bytes I re-drove — with both files ` M` uncommitted. `diff` of my scratch copy vs the landed fixture: **comment
lines only — executable semantics identical** (verified; FIXTURE_DIFF shows
banner/`--midline-gap-ms` parse/`OS.delay_msec(midline_gap_ms)` all equal).
Every key edge cell was then RE-DRIVEN on the landed bytes via
`proj-landed/` (`landed-verify.json`) — results transfer exactly. Environment:
Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Linux x86_64, CPython 3.14.7.

## Detector baseline (pristine bytes)

`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
corpus/live/r69-boundary/runs` (pre-landing runner `55314bb5…`) → exit 0,
`runs/20261014T120916771622Z/verdicts.json` — **88/88 PASS**;
`probe_error_clause_surface` **34/34** discriminations.

## Edge results

### P1 — declared crossed ladder, emulated (off=80 fixed)

gap {50,100,200,400,800}: **missed at 50 only** (0/3); fabricated 3/3 at
100/200/400/800. Matches the predicted set; no persistence below, no
failure above → the gap-relative reading survives the declared granularity.

### Edge 1 — below the spawn-overhead floor: the write can never win

| cell | outcome |
|---|---|
| off=80 @ gap {0,1,2,3,5,10} | **all missed** (0/3 each) — write arrives ~82.5ms, hopeless |
| off=0 @ gap {0,1,2,3} | all missed; **gap=5 MIXED (1/3)** — jitter-split |
| off=−50 (malformed `sleep 0.-50` → immediate write ~2ms) @ gap {0,2,5} | all missed 0/3 |
| landed-bytes recheck off=0 | gap=2 **MIXED 2/3** (earliest write ~1.9–2.2ms CAN win a 2ms gap); gap=5 fabricated 4/4 |

The window has an **absolute achievability floor ≈1–2ms** on this host:
below it no descendant write can outrun the tail flush at ANY offset —
the gap-relative bound is bounded below by spawn+exec+sleep latency.
Floor jitter cell sits at gap≈2–5ms, not a hard zero.

### Edge 2 — degenerate (80,80) + the referent knife-edge

- gap=80 = offset: **missed 0/6** (landed: 0/4) — equality is outside the window.
- **Referent pinned at 1ms granularity** (off=80): gap ≤81 all miss; **gap=82
  MIXED** (scratch 2/3, landed 2/4); gap ≥83 all fabricate. Nominal
  `offset<gap` predicts fabrication for every gap>80 — falsified at gap=81:
  the bound's referent is the write's **arrival position vs tail flush**
  (`offset + ~2.5ms spawn latency < gap`), not the nominal offset vs gap.
  The declared claim's stated semantics — "fabrication iff the write lands
  before the tail flush AT ANY gap size" — is **CONFIRMED** (it is
  gap-relative, never absolute: fabrication at 800ms proves the write
  position, not the gap width, is the bound); its shorthand `offset<gap`
  form is off by the ~2.5ms spawn-latency constant, exposed exactly at the
  81–82ms knife-edge.

### Edge 3 — offset>gap (post-tail by construction)

| (off,gap) | outcome | provenance |
|---|---|---|
| (240,100) | missed 0/3 | **write_ppid≠godot_pid all reps → post-death** (reparented; child long gone at ~242ms write) |
| (160,50) | missed 0/3 | post-death all reps |
| (120,100) | missed 0/3 | pre-death — write lands post-tail but pre-exit (teardown outlives tail ~20ms+) |
| (100,100) | missed 0/3 | pre-death; arrival ~102.5ms past the 100ms tail |
| (95,100) | **fabricated 3/3** | arrival ~97.5ms inside the gap — the offset-axis knife-edge mirror |

offset>gap cells are all misses as constructed, but the pre-death
invariant silently flips: writes ~140ms+ past the tail are post-death
(ppid reparented), so "provably pre-death" cells exist only in a band
between tail-flush and child teardown — roughly (+0,+140ms) on this host.

### Edge 4 — drain×timeout vs long gaps: OFF at 800ms, ON at the bound

- **gap=800: zero interaction.** 8/8 fabricated, all clean exit-0, all
  pre-death, elapsed ~1.2–1.5s vs the 3.0s surface bound — the record
  shape is identical every rep. The r68 drain nondeterminism lives in
  TIMEOUT truncation; nothing truncates here.
- **Onset ≈ gap 2350–2450ms** (= bound − child lifetime ~0.55–0.66s).
  off=80 @ gap {2050,2250}: clean, fabricated, elapsed 2.72/2.89s.
  @ gap {2450,2750}: **TIMEOUT record still carrying the fabrication** —
  the write (landed ~82ms) is in the captured prefix, the tail never
  arrives (child mid-delay at deadline: `child_exit_at_timeout=None`),
  yet `write_ppid==godot_pid` — a TIMEOUT record with pre-death provenance.
- **Deadline-race cells @ gap=2450** (the interaction's real teeth —
  `deadline-race*.json`, `raw/deadline2_*`):
  - off ≤2400: splice lands pre-deadline → fabricated in the prefix;
    TIMEOUT itself is jitter-split (off 2350/2400 mixed clean/timeout at
    the SAME nominal cell).
  - off 2450–2500: write lands post-tail but pre-deadline → intact
    signature + standalone ERROR + TIMEOUT.
  - **off=2550 knife-edge, same nominal cell, three record shapes:**
    write in-capture (post-death, `write_ppid=1573`), write evaporated
    post-capture (intact signature only), and a clean exit-0 return —
    fabrication presence is drain-timing nondeterministic.
  - off ≥2850: write always post-deadline, never captured; signature
    presence itself flip-flops (tail races the deadline — 2850 rep3
    `signature_observed=False` vs True on siblings).
- **New record shape surfaced:** TIMEOUT with `actual_exit` never set,
  child `poll()==0` at deadline, and the COMPLETE intact signature in the
  prefix — caused purely by the not-yet-fired descendant holding the pipe
  write-end open past the bound. The r62 pipe-EOF misattribution class
  manufactured by the crossed ladder alone — no hold arm needed. All such
  records still classify False (error clause) — **verdict-stable,
  content-unstable.**

### Receipt-upgrade edge — `sha256(merged)` coverage is stream-count-bound

Across all 118 captured records (`boundary-verdicts.json → p6`):
`sha256(so+se) != sha256(se+so)` on exactly **9** — all the off=−50 cells
where the malformed `sleep 0.-50` writes `sleep: invalid time interval`
(82B) to stderr. Every other midline cell has **empty stderr**, and
`order_blind_when_stderr_empty` held for all 109: `sha(so+"")==sha(""+so)`.
The merged digest catches concat-order drift **only on records where both
streams carry bytes** — on the midlineforge arm family (stdout-only
writes) it is informationally redundant with `raw_stdout_sha256`. Its
discriminating power lives on the stderr-carrying arms (seam/splitforge,
error-surface records). Correct additive field; coverage edge is real.

## Verdict on the declared falsifiable claim

"the window follows `offset<gap` (gap-relative — fabrication iff the write
lands before the tail flush AT ANY gap size)" — **CONFIRMED in stated
semantics, sharpened to the arrival referent**: fabrication iff the write's
pipe-arrival lands inside `(head_flush, tail_flush)`, at any gap above the
~2ms achievability floor; the nominal `offset<gap` shorthand misses by
~2.5ms spawn latency (knife-edge: miss at gap=81, mixed 82, fabricate ≥83,
on both scratch and landed bytes). Neither falsifier fired: no persistence
at gap<<80 (miss at 50; no write wins ≤2ms at any offset) and no failure
at gap>>80 (8/8 at 800). Additional bounds surfaced: post-death crossover
inside offset>gap cells, and a drain×deadline nondeterminism band at
gap ≈ bound − ~0.6s (≈2350–2550ms) producing three record shapes at one
nominal cell plus a clean-signature TIMEOUT misattribution.

## UNKNOWNs / retained caveats

- Single host; the author's diff landed mid-session (uncommitted ` M`).
  Scratch cells measured pre-landing bytes + my emulation; all key cells
  re-verified on landed bytes `c86bda84…` (`landed-verify.json`) — if the
  working tree is amended pre-commit, landed figures refer to that sha.
- Sibling lanes ran concurrent live batteries during measurement (r69-
  reviewer battery observed); jitter-cell positions are load-sensitive —
  the knife-edge locations (82ms, 2550ms, gap-onset ~2350–2450) are this
  host's data, the existence of each edge is the finding.
- `merged_sha` census ran on midline cells only; the stderr-carrying arm
  families' order-sensitivity is asserted structurally (nonempty both
  streams ⇒ `so+se ≠ se+so` for non-commuting content), not re-measured.

## Artifact inventory (`corpus/live/r69-boundary/`)

- `drive_boundary.py`, `boundary-verdicts.json` — 118-record edge driver:
  declared-ladder bridge, floor cells, knife-edge, offset>gap, long-gap,
  timeout-onset bracket, merged-sha census. Sha pins: runner `55314bb5…`
  (probe-time), tracked fixture `5c5c629a…` (probe-time), scratch fixture
  `bfd68d76…`, `classify_process` segment sha pinned in-file.
- `deadline-race.json`, `deadline-race2.json` — gap=2450 write-vs-deadline
  sweeps (off 2300–3060): the nondeterministic band.
- `landed-verify.json` — 11 edge cells re-driven on the landed fixture
  `c86bda84…` (`proj-landed/`): identical verdicts incl. gap=81 miss,
  gap=82 mixed 2/4, off=0/gap=2 mixed 2/3.
- `proj/`, `proj-landed/` — scratch + landed-byte projects.
- `raw/` — per-stream captures for every run (incl. `deadline2_*` timeout
  prefixes).
- `runs/20261014T120916771622Z/` — flagless battery on pristine tree
  (88/88, surface 34/34) + `battery.stdout/.stderr`.

No commit, no tracked mutation, no LOG/SCORECARD write; all descendants
were `sh` subshells self-exiting after their write — post-run process scan
clean (only a sibling lane's battery was live).
