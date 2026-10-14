# Round 68 — boundary recon: fabrication-window edges + receipt-shape edge cells

## Scope and method

LEAF boundary seat, scratch-only and report-only. I wrote only this report
and `corpus/live/r68-boundary/`. No tracked fixture, runner, CASES row,
lesson, LOG, or SCORECARD entry touched; no subagent dispatch; no git
mutation. The `corpus/fixtures/__pycache__/` untracked dir is the author's
battery by-product, not mine.

Assignment (lane brief, verbatim edges): (1) offsets beyond the ladder —
negative/jitter/duplicate writes mid-gap; (2) does drain scheduling actually
interact with timeout truncation (the w7 xconnector-flagged cell); (3)
`divergent_clause` collisions — two distinct mechanisms mapping to the same
signature?; (4) same-input sha256 under stream-capture edge cases (empty
stream, binary bytes).

**Provenance.** Probed AFTER the author's diff landed in the working tree:
`run_battery.py` sha256 `7c421436…` (was `8d7e4d94…` at r68-baseline freeze),
`descendant_pipe_probe.gd` sha256 `5c5c629a…` (was `92a40d70…`). Tree was
uncommitted-modified throughout my measurement window (author report lands
separately as `reports/round-68/r68-author.md`). All classifier/attribution
verdicts are `ast.get_source_segment` extracts of the landed runner, sha-pinned
per segment in `landed-verdicts.json → function_shas`. Environment: Godot
`4.7.2.stable.arch_linux.ed1daf0bf`, Linux x86_64, CPython 3.14.7.

## Author-claim verification (independent reproduction)

- MY flagless battery on the landed tree: `python3
  corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
  corpus/live/r68-boundary/runs` → exit 0, `runs/20261014T112024124494Z/
  verdicts.json` — **88/88 PASS**; `probe_error_clause_surface` **34/34**
  discriminations, keyset AND values identical to the r68-baseline frozen
  replay. Prior-row byte-stability vs
  `corpus/live/r68-baseline/runs/20261014T104854073132Z/verdicts.json` on the
  7-field tuple: **88 common, 0 mismatched, 0 new-only, 0 old-only**.
- MY probes battery: `… --runs corpus/live/r68-boundary/runs2
  --probe-midlineforge-ladder --probe-stream-attribution` → exit 0,
  `runs2/20261014T112024144893Z/verdicts.json` — **90/90 PASS**;
  `probe_midlineforge_ladder` PASS with all 8 discriminations;
  `probe_stream_attribution` PASS.
- Landed ladder artifact (`midlineforge-ladder-verdicts.json`): landed
  {0,40,80,120,160}, missed {240}, mixed [], `lo_edge_ms=0`, `hi_edge_ms=240`
  — reproduces the author's table exactly on my own runs; every rep
  pre-death (`write_ppid==godot_pid`), every rep rejects.
- Landed `stream-attribution-verdicts.json`: divergence_table carries
  `divergent_clause` per row + `raw_stdout_sha256`/`raw_stderr_sha256` on
  every dual record; all sha fields re-verify against the recorded
  `raw_*` text (arm rows) and against their source arm's digests
  (allowlist reclassifications — the same-input gate holds).

## Edge 1 — offsets beyond the ladder

Landed arm `--midline-offset-ms=N` driven at offsets the author ladder
doesn't reach (`landed-verdicts.json → p3a_landed_edges`), plus a
parallel scratch fixture (`proj/boundary_midline_probe.gd`, same halved-
signature mechanism) for shapes the landed flag grammar can't express:

| probe | outcome |
|---|---|
| landed `--midline-offset-ms={-500,-50,-1,0,20}` | **all splice** (3/3 each) — negative offsets produce a malformed `sleep 0.-0NN` arg → sleep errors → the write lands ~2ms after the head anyway. **The nominal-offset window is downward-unbounded**: `lo_edge_ms=0` in the author's `measured_window` is a ladder-domain artifact, not a real edge — spawn/exec latency ≥ ~2ms means no achievable offset lands the write before the head flush. The true lower bound is the head flush itself. |
| scratch `--pre-head` (child delays 150ms before `printraw(head)`; descendant writes immediately) | `before_head` 3/3 — a provably pre-gap write exists: signature intact, standalone ERROR line, merged=False, **streams=True** (the stdout-carried ERROR: is streams-invisible — the pre-gap miss is a *divergent* miss, not just a signature save). |
| landed edge sweep 160–205 (1–5ms granularity) | splice at 195–197 (3/3); **198 = MIXED cell (1 miss / 2 splices)** — the jitter-split cell the author's 6-point ladder skipped; 199–205 all miss. The nominal hi edge measured here ≈ **198ms** (write lands at offset + ~2.5ms → gap-relative ≈ 200.5ms, just over the 200–201ms gap). |
| landed {240,300,800} | all miss, signature intact — and **post-death crossover**: `write_ppid==godot_pid` at ≤240, but `write_ppid=1573` (reparented) at 300/800 (my scratch copy: crossover between 240 and 260ms). Past ~250ms nominal the arm silently stops being "provably pre-death" — the ladder's 240 cell keeps the provenance pin but sits ~40ms from the crossover on this host. |
| scratch `--dup=40,140` / `--dup=80,260` / `--dup=10,10` | **every in-window write splices independently**: `n_err=2` — first write destroys the signature, subsequent writes add standalone ERROR lines (the second at 260 lands post-tail). Side-effect: `count("ERROR:")==2` kills the `,`-prefix allowlist shape — a double-spliced line is unabsorbable where a single splice under a `,`-entry is not. |
| scratch `--jitter=80,40` (RANDOM%40ms) | 6/6 splice — interior is robust to ±20ms jitter. |
| scratch `--gap={60,120,400}` at off=80 | miss at gap=60 (write lands after tail), splice at 120/400 — **the window tracks `OS.delay_msec(G)`, not the nominal offset** — the bound is the pipe-arrival interval (head-flush, tail-flush), exactly as the author's `bound_semantics` says. |
| scratch `--payload=~` (bare `\n`), `--payload=: BARE CORRUPT~`, `--payload=gluedbytes` | ERROR-free mid-gap writes: the `\n` write splits the marker into two lines with **zero error bytes** — merged rejects on the signature clause alone (pure signature-axis corruption, isolable). `: BARE CORRUPT`/`gluedbytes` splice non-error bytes mid-line — same signature destruction, clean error scan. |

## Edge 2 — drain scheduling × TIMEOUT truncation (the flagged cell): CONFIRMED

The w7-xconnector cell was: per-fd capture means drain order can't alter
stream bytes — *but* it should interact with timeout truncation. Measured
(`boundary-verdicts.json → p2_drain_timeout`, `raw/p2_*`):

- **Captured-prefix length at TIMEOUT is nondeterministic.** `--hold-flood`
  (descendant floods stderr at 20ms cadence, holds pipes 5s; bound 1.5s):
  10/10 reps TIMEOUT; captured stderr tail index spread **44..56** (~240ms
  of write schedule) — the drain loop's phase at deadline decides which
  writes are in `exc.stderr`. Stdout (child's early writes) was stable at 5
  lines every rep — the nondeterminism lives in the in-flight stream only.
- **A TIMEOUT record can carry a seam-fabricated line.** `--hold-seam`
  (child leaves unterminated `…ends in ERROR` stdout tail; reparented
  descendant writes `: TRUNC phantom…` stderr head, holds pipes): at
  `sched=500` the phantom `BOUNDARY trunc tail ends in ERROR: TRUNC phantom
  fabricated line` appears in the recovered merged text 3/3; at `sched=1500`
  it flip-flops **1/3** — whether the fabrication lands in the timeout
  record is drain-timing-dependent; at ≥1900 it never lands (writes post-
  deadline aren't in `exc.stderr`). The stderr payload was a *post-death*
  write (`write_ppid=1573`) captured via held pipes.
- **Truncation is byte-granular**: a 400KB unterminated write captured
  400,009 bytes ending mid-line (`b'EEEEEEEEEEEE'` tail, no newline) — a
  timeout record's stdout tail can end unterminated, which is precisely the
  seam precondition.

So: drain scheduling is content-invisible on the completion path (r67
result holds) but **material under truncation** — it decides which in-flight
writes land in the partial buffers, hence whether a fabrication exists in
the recovered text at all. Both outcomes still classify FAIL (`error` set),
but the *content* of a TIMEOUT record is not replay-stable.

## Edge 3 — `divergent_clause` collisions: confirmed, three classes

Synthetic (so,se) cells through the VERBATIM landed `divergent_clause`
(`:2462-2516`) + both real classifiers
(`landed-verdicts.json → p3b_*`; synthetic cells disclosed as such):

1. **Mechanism collision (by design, now measured):** the landed table
   itself maps three distinct mechanisms to `["error_scan"]` —
   `streamdiv_stdout_error` (real stdout ERROR: absorbed: stdout never
   scanned), `streamdiv_seam_error` (phantom line existing in neither
   stream), `stream_reject` (non-ERROR: stderr strictness). And two
   mechanisms map to `["signature"]` — `streamdiv_sig_on_stderr`
   (wrong channel) vs `streamdiv_seam_sig` (seam-split). The label set is
   clause-granular, not mechanism-granular: same signature ≠ same
   mechanism.
2. **Masked clause:** `x_masked_allowlist` — stderr = structured-line
   (merged absorbs via the structured entry; streams rejects) + plain
   chatter line → merged=T/streams=F, and BOTH an allowlist-shape and an
   error-coverage divergence are live. Landed output: `["error_scan"]`
   only — the `all(stream_rejects are merged-absorbable ERROR: lines)`
   gate erases the `allowlist_shape` signal whenever one non-absorbable
   line coexists. Multi-mechanism rows under-report.
3. **Token-dependent label cardinality:** identical seam mechanism gives
   `["blob","error_scan"]` for `SCRIPT ERROR:` (phantom contains the
   `ERROR:` substring → trips the per-line scan too — matches the landed
   `streamdiv_seam_script` row) but `["blob"]` for `Parse Error:` (no
   `ERROR:` substring). Same mechanism, different signature width.

Additional pins: `x_sig_stderr_bare` → `["signature","error_scan"]` (the
unallowlisted signature line is *also* a stderr-audit reject — matches the
landed `sig_on_stderr__bare` reclass row); `x_concordant_with_clause_diffs`
(sig on stderr + stdout ERROR:) → `divergent=False` **with nonempty**
`divergent_clause=["signature"]` — the column measures clause-level diffs,
not verdict divergence: a "non-divergent" row can carry a non-empty clause
signature (and `seam_error__bare` shows the symmetric cell — concordant F/F
with `[]` where the two rejections have different grounds). `exit` is a
structurally dead label — `(code==0 and error is None) != (same)` is
self-comparison `X != X`; the taxonomy advertises a clause that cannot
diverge under same-input reclassification (error is equally dead — both
classifiers see the same value). Mislabels not found: every emitted label
was a genuinely differing clause; the gaps are masked multi-clause rows and
mechanism aliasing, not wrong attribution.

## Edge 4 — same-input sha256 gate: binds decoded text, not raw bytes

Landed implementation (`:2532-2535`): `hashlib.sha256(so.encode())` /
`se.encode()` — default utf-8 over the **decoded str**. Edge cells
(`p3c_sha256_edges`):

- **Empty vs absent stream collide**: empty stderr → `e3b0c442…`; an absent
  stdout (OSError path returns `""`) → same `e3b0c442…`. The gate cannot
  distinguish "captured empty" from "never captured".
- **Decode-replace collision**: distinct raw bytes `b"prefix \xff tail\n"`
  vs `b"prefix \xfe tail\n"` decode under `errors="replace"` (the runner's
  TimeoutExpired recovery path) to the identical str `\ufffd` → identical
  recorded sha256 `915e4135…`. The field name says `raw_stdout_sha256` but
  hashes post-decode text: byte-level divergence that decode erases is
  invisible to the same-input gate. On the *strict* completion path it's
  moot — invalid UTF-8 raises `UnicodeDecodeError` before any record exists
  (the r66 DoV class, still live: `run_process_streams` catches
  TimeoutExpired/OSError only).
- **Not reachable**: surrogate-carrying strs (`surrogateescape`) would make
  `so.encode()` raise `UnicodeEncodeError`, but neither decode path can
  produce one.
- Positive pin: on the landed artifact every arm's sha pair re-derives from
  its `raw_stdout`/`raw_stderr` fields, and all six `allowlist_reclassifications`
  carry their source arm's digests — the gate does prove same-text input
  between classifiers and across reclassifications.

## Verdict on the declared falsifiable claim

"the fabrication window has a strict measured bound [lo,hi) inside the
signature gap, and the r66 seam fabrication holds exactly within it" —
**CONFIRMED in substance, sharpened at both edges**:

- The bound is real and strict, but it is a bound on **write arrival
  position** `(head_flush, tail_flush)`, not on the nominal offset. The
  nominal-offset domain has **no lower edge** — every offset from -500ms up
  splices (spawn latency guarantees post-head arrival); `lo_edge_ms=0` is
  the smallest tested value, not a measured boundary.
- The hi edge measured tighter than the author's (160,240] bracket: nominal
  **198ms is the mixed cell** (1/3 miss), 199+ never splices → nominal hi ≈
  198–199ms on this host, agreeing with the author's instrumented
  ~197–198ms spike.
- Within the window the fabrication holds exactly (every in-window write —
  single, duplicate, jittered — lands its splice); outside it the write
  lands post-tail as a standalone ERROR: line (still rejects via
  error_scan), and past ~250ms nominal the write silently flips to
  **post-death** provenance (`write_ppid=1573`) — the pre-death property
  the ladder discriminates is itself timing-bounded.
- Receipt upgrades verified: `divergent_clause` labels are clause-accurate
  but mechanism-ambiguous (3 mechanisms → `["error_scan"]`, 2 →
  `["signature"]`) and can mask a co-diverging `allowlist_shape`; sha256
  fields gate same-*text* input, blind to byte-level divergence erased by
  `errors="replace"` decode and to empty-vs-absent streams.

## UNKNOWNs / retained caveats

- Single host (Godot 4.7.2 headless, CPython 3.14.7): absolute ms figures
  slide; the (head,tail) window semantics, collision classes, and
  truncation nondeterminism are structural.
- My mechanism-edge probes run a scratch fixture mirroring the landed arm
  byte-for-byte in mechanism (halved printraw signature, 200ms
  `OS.delay_msec`, descendant `sh -c` inherited pipes); the landed arm was
  re-driven verbatim for the offset cells. Working tree was
  uncommitted-modified at probe time — if the diff is amended before
  commit, shas shift; the extracted functions were sha-pinned to the
  working bytes I measured.
- Drain×timeout probes used my fixture's `sh` descendants (same POSIX pipe
  semantics the r62 hold arm relies on); scheduler-dependent numbers are
  host data, the *existence* of nondeterminism is the finding.
- Sibling lanes ran concurrent live batteries on this host during
  measurement; runs are independent receipts.

## Artifact inventory (`corpus/live/r68-boundary/`)

- `drive_boundary.py`, `boundary-verdicts.json` — phase 1/2 driver +
  results (offset edges, payloads, jitter/dup/gap, drain×timeout cells) on
  pre-landing runner sha `8d7e4d94…` for mechanism edges.
- `drive_landed.py`, `landed-verdicts.json` — post-landing driver: landed
  `--midline-offset-ms` sweep {-500..800}, verbatim `divergent_clause`
  collision cells, sha256 edge cells; function sha pins; runner sha
  `7c421436…`, fixture `5c5c629a…`.
- `proj/` — scratch project (`project.godot`, landed
  `descendant_pipe_probe.gd` copy, `boundary_midline_probe.gd`).
- `raw/` — per-stream captures for every probed run.
- `runs/20261014T112024124494Z/` — flagless battery on landed tree (88/88).
- `runs2/20261014T112024144893Z/` — `--probe-midlineforge-ladder
  --probe-stream-attribution` battery (90/90) + both artifacts.
- `battery.stdout/.stderr`, `battery-probes.stdout/.stderr`,
  `drive.stdout`, `drive.stderr`.

No commit, no tracked mutation, no LOG/SCORECARD write; descendants were
`sh` subshells self-exiting ≤10s (hold arms) — post-run process scan clean.
