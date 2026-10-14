# Round 65 — boundary recon: forged-REJECTION edge probes

## Scope and method

LEAF boundary/revenger seat, scratch-only and report-only. I wrote only this
report and `.shokunin/game-dev-2d/corpus/live/r65-boundary/`. No tracked
fixture, runner, CASES row, lesson, LOG, or SCORECARD entry was touched; no
subagent dispatch; no git mutation.

Assignment (lane brief): probe the edges of the landed forged-REJECTION dual
(`probe_descendant_error_spoof` + the `--spawn-errforge-*` fixture arms):
(1) does the forged error flip survive the r64 while-live gate's observation
path; (2) error-marker partial writes / interleaving with the signature
bytes; (3) error flood — any cap; (4) forge inside a timeout-held arm —
which axis rejects first; (5) pipe-full blocking post-death — who drains,
does it block forever.

**Provenance note — mid-flight commit.** At probe start the working tree
carried the r65 author diff uncommitted (runner sha256 `1acbc73d…`,
fixture `37cf5015…`). During my run the operator committed `414eb8e`
(r65 landing + all seats' scratch/reports sweep). I verified the committed
runner (sha `cd4824cc…`, 2006 lines vs probed 2002) differs from the probed
pre-commit file by **exactly +4 lines**: one added discrimination
`"hold_timeout_alone_rejects": ef_hold["stripped_classification"] is False`
inside the meta dict — every function I extracted and executed
(`run_process`, `classify_process`, `classify_streams`, `pid_alive`,
`kernel_ppid`, `gated_signature_run`) is byte-identical between the two.
Reconstruction proof: `corpus/live/r65-simplifier/tracked-diff.patch`
applied to `61ec1c0:run_battery.py` reproduces sha `1acbc73d…` exactly
(`diff` vs HEAD shows only that entry). Committed fixture ==
probed `proj_stock` (`37cf5015…` both). All measurements below therefore
characterize the committed artifact. An earlier attempt of this driver
(`drive_edges.py`, `raw/`, `drive.stdout`, 2026-10-13 23:43) died mid-run
at the unbounded-pump gate row — root cause measured this run (edge 5).

Method: `ast.get_source_segment`-extract the six production functions from
the working-tree runner and `exec` them — rows tagged `vg_*`/`comm_*`/
`st_*` run production code verbatim. `timed_probe` is an instrumented
gate-shaped replica (per-event `(t, stream, alive_before, n)` ledger,
marker + first-`ERROR:`-byte observation stamps, `/proc` wchan/syscall
descendant sampling — corroborating, disclosed). Per-clause truth tables
(`clauses` field in `edge-verdicts.json`) explode the landed
`classify_process` conjunction so "which axis rejects" is read off, not
inferred. All Godot runs sequential. Fixture copies: `proj_stock/`
byte-identical (`37cf5015…`); `proj_edge/` (`dded5056…`) adds scratch-only
arms disclosed in-file. Reaper safety: this run kills only the pid the
run's own capture printed AND only when `/proc/<pid>/cmdline` carries the
scratch fixture's unique `FORGED_DESCENDANT_ERROR` token (edge) /
`DESCENDANT_PIPE_ERRFORGE` (stock) — a generic `DESCENDANT_PIPE` match was
deliberately narrowed because an r65-critic battery ran the same stock
fixture concurrently on this host.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Linux x86_64,
CPython 3.14.7, 32 CPUs, pipe buffer `F_GETPIPE_SZ=65536` on both captured
fds, subreaper pid 1573 (`systemd --user`).

## Author-claim verification (independent reproduction)

- Author battery receipt `corpus/live/r65-author/runs/20261014T023015140150Z/verdicts.json`:
  `probe_descendant_error_spoof` **PASS**, all 28 discriminations True
  (29 in committed HEAD — the added `hold_timeout_alone_rejects` also True
  in the critic battery's rerun,
  `corpus/live/r65-critic/runs/20261014T041531981734Z/verdicts.json`).
- My verbatim-path reruns reproduce the claim on the stock fixture:
  `comm_stock_release` — exit 0, `error=None`, signature present, forged
  error line captured post-death, `verdict=False` (only
  `no_unrelated_errors` fails); `comm_stock_genuine` — identical
  classification-visible shape (byte-identical ERROR line via child
  `push_error`); `comm_stock_hold_b3` — TIMEOUT record carrying the forged
  error + `write_ppid=1573`. Confirmed.
- Prior-row stability: 97 common rows vs
  `corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json` —
  **0 mismatches** on verdict-bearing fields (`verdict`, `actual_exit`,
  `error`, `expected_exit`, `signature`). 8 rows differ only in volatile
  output bytes (pids, run-stamp paths, load addresses, tween floats); every
  verdict identical. "Byte-stable" holds on classification-visible fields.

## Edge 1 — the forged error under the while-live gate: gate-invisible, but observable

| arm (verbatim `gated_signature_run`) | gate sig | inner cls | dead@ | sig@ | notes |
|---|---|---|---|---|---|
| `vg_err_release_r0/r1/r2` | **accept** (True) | **False** | 0.384/0.411/0.410 | 0.313/0.339/0.339 | forged error INSIDE gate's captured bytes |
| `vg_err_stderr_r0/r1` | accept | False | 0.375/0.384 | 0.303/0.313 | fd-2 routed forge — same |
| `vg_err_hold` | accept | False | 0.382 | 0.311 | error lands inside TIMEOUT record |
| `vg_err_genuine` | accept | False | 0.370 | 0.304 | child-authored control |
| `vg_default_control` | accept | **True** | 0.391 | 0.324 | clean baseline |
| `vg_sigforge_release_control` | **reject** (False) | **True** | 0.396 | 0.428 post-death | r63/r64 boundary intact |

The forged error bytes ARE in the gate's own captured stream
(`output_lines` carry `ERROR: FORGED_DESCENDANT_ERROR injected diagnostic`;
instrumented `tp_err_release_r0` reads the 92-byte error chunk at
t=0.4139s with `alive=False`, ~37ms after death first observed at
0.3769s) — but the gate's accept criterion is the signature marker only, so
the arm is gate-ACCEPTED while the same bytes classify FAIL. **The flip
does not survive the gate's verdict path**: a consumer that used
while-live-signature as the accept authority would pass this record.
Rejection lives entirely in the un-gated merged scan — matching the
author's claim ("gate-invisible; rejection stays in the un-gated
classifier"), and the committed meta's dual-marker runner measures the
error arriving post-death every rep.

Timing corollary (`tp_*` instrumented runs): the error-axis timing split
the r64 gate exploited on signatures exists identically on errors —
forged post-death errors observed at `alive=False` in every rep
(`tp_err_release_*`, `tp_err_stderr`, `tp_err_hold`), while the pre-death
forge (`tp_err_predeath`, fixed 20ms offset, `write_ppid==godot_pid`)
arrives at `alive=True` (0.339 < death 0.386) and the genuine
`push_error` lands while-live. An error-axis gate would discriminate the
same way — and would be racable by a pre-death-scheduled forge, the same
declared scope limit as the signature gate.

## Edge 2 — partial writes / interleaving: two evasions and one dual-axis corruption

The error clause is a **line-local** substring scan (`"ERROR:" in line`
over `output.splitlines()`, `run_battery.py:174-176`); the signature clause
is a whole-blob substring. Measured against live post-death writes:

| shape | arm | result | mechanism |
|---|---|---|---|
| token split, **no newline** (`printf 'ERR'` … `'OR: …'`) | `--spawn-errforge-split` | **detected** (`comm_err_split` False) | byte stream reassembles `ERROR:` contiguously in-pipe |
| token split **across newline** (`'ERR\n'` then `'OR: …'`) | `--spawn-errforge-newlinesplit` | **EVADES** (`comm_err_newlinesplit` **True**, `vg_err_newlinesplit` inner True, `tp_err_newlinesplit` `err_at=None`) | no captured line contains `ERROR:` — the forged bytes are in the record yet invisible to the clause |
| error glued onto unterminated child tail | `--spawn-errforge-glue` | detected (`…TAIL_OPENERROR: FORGED…` line contains `ERROR:`) | substring is not line-anchored |
| error injected **mid-signature-line** (child emits marker in two `printraw` halves, descendant splices the gap) | `--spawn-errforge-midline` | FAIL via **two** clauses (`signature_present=False` AND `no_unrelated_errors=False`; `vg_err_midline` `sig_ok=False`, marker never completes) | the splice destroys the signature substring AND adds the error line — the flip is no longer solely the error; the author's `stripped_classification` counterfactual cannot isolate it (stripping the ERROR line removes half the marker fragments too) |
| forged error on fd 2 | `--spawn-errforge-stderr-release` | detected under merged consumer (`comm_err_stderr` False) | post-merge stream origin is invisible |
| same under `classify_streams` | `st_err_stdout` vs `st_err_stderr` | **stdout-carried forged error EVADES** (`streams_classification=True` on `st_err_stdout`/`st_stock_release` while `merged_classification=False`; stderr-carried rejects) | `classify_streams` only audits stderr lines (`run_battery.py:200-208`) — a descendant `echo` on stdout is outside its scan entirely |

Synthetic units (`edge-verdicts.json → synthetic_classifier_units`) pin the
clause geometry: `err_newline_split`, `lowercase_error`, `err_no_colon` all
**admit**; `err_on_sig_line`, `err_inside_sig`, `err_glued_tail`,
`err_prefix_of_allowed` (allowlisted line + glued `ERROR:` → `count==2`
guard fires) all reject; `SCRIPT ERROR:`/`Parse Error:` anywhere reject.

**Allowlist is origin-blind**: `--spawn-errforge-allowlisted` writes
`save_corrupt_negative`'s allowlisted line post-death — without the
allowlist the record rejects (`comm_err_allowlisted` False); classified
with that allowlist entry it **passes** (`comm_err_allowlisted_allowed`
**True**). On an expected-negative row, a descendant could forge the row's
*own* expected error text and be admitted — the allowlist checks string
equality, never origin or timing.

## Edge 3 — flood: no cap, no block

`--spawn-errforge-flood` post-death (`comm_flood_*`): N=20/500/2000
identical lines and N=200/2000 distinct lines — `err_lines` count is
exactly N, output bytes scale linearly (~51 B/line), elapsed ~0.4 s,
verdict False every time. No cap anywhere: `communicate` drains to EOF,
the scan sees every line, one suffices for rejection. Under the verbatim
gate (`vg_flood_2000`, 2000 lines in one burst): gate still accepts the
while-live signature, inner classification still False.

## Edge 4 — forge inside the timeout-held arm: the conjunction has no "first"; the bound decides which clauses fire

`classify_process` is a six-conjunct AND, not an ordered axis sequence —
the honest answer is the per-clause table (`edge-verdicts.json`):

| record | bound | code_eq | error_none | sig | no_unrelated | verdict |
|---|---|---|---|---|---|---|
| `comm_err_hold_b4` (error+hold) | 4s < 6s hold | **F** (exit None) | **F** (TIMEOUT) | T | **F** | False |
| `comm_err_hold_b8` same arm | 8s CASES bound | T | **T** | T | **F** | False |
| `comm_stock_hold_b8` (author arm) | 8s | T | T | T | **F** | False |
| `comm_combo_hold_b8` (forged sig + forged error + hold) | 8s | T | T | T (forged sig **accepted**) | **F** | False |
| `comm_combo_release` (forged sig + error, pipes released) | 8s | T | T | T | **F** | False |

Measured: the ~6s pipe hold **releases inside the production 8s CASES
bound** — `comm_err_hold_b8`/`comm_combo_hold_b8` return clean exit-0 +
`error=None` records at ~6.45s elapsed. The timeout axis vanishes and the
forged error is the **sole** rejection — the author's meta only ran the
hold at the 3s bound where three clauses fail together. On combo arms the
forged *signature* is present and accepted by the origin-blind clause — so
on a CASES-bound record the error axis alone does all the rejecting. Under
the verbatim gate the same combo records invert: `vg_combo_hold` /
`vg_combo_release` have `sig_ok=False` (forged signature observed
post-death, gate rejects) while the error is gate-invisible — the two
consumers reject the same arm on different axes.

## Edge 5 — pipe-full post-death: nobody drains but the reader; the writer blocks, then dies by SIGPIPE; unbounded pump is a memory-exhaustion surface

Pipe capacity measured `F_GETPIPE_SZ=65536` on both fds. Arms:
`--spawn-errforge-pipefull` (bounded `yes | head -c K`) and
`--spawn-errforge-pipefull-hold` (unbounded `exec yes`).

- **Bounded pump under `run_process`/`communicate`** (`pf_comm_256k`,
  `pf_comm_512k`): all 262398/524542 bytes captured, elapsed ~0.45 s,
  verdict False (every line is an error line). communicate drains both
  pipes concurrently — a finite >64K post-death write never blocks.
- **Stalled reader** (`pf_stall_then_drain`, 1.5 s pre-read stall, `/proc`
  sampling): the descendant family is caught blocked — `yes` pid in
  `wchan=pipe_wait_writable`, `head` in `anon_pipe_write`, parent `sh` in
  `do_wait`. Nobody drains while the reader stalls; on resume the full
  256 KiB lands (total elapsed 1.516 s). The only drainer is the reader.
- **Stall then close** (`pf_stall_then_close`, unbounded `yes`): child
  already `exit=0` at stall end; descendant sampled blocked in
  `pipe_wait_writable`; after the driver closes the read ends the
  descendant is **gone** (SIGPIPE) — closing the pipes is the kill
  mechanism, not a wait.
- **Unbounded pump under the gate-shaped read** (`pf_gate_bounded_read`,
  3 s bound, storage capped at 8 MiB — counters exact): **983,168 read
  events, 64,432,422,791 bytes drained in 3.0 s** (~21 GB/s — `yes` runs
  at memory bandwidth when the reader drains continuously). The loop never
  blocks; the deadline fires (`timed_out=True`), streams close, descendant
  SIGPIPEs (`desc_alive=False`).
- **Same unbounded pump under the VERBATIM gate** (`vg_pipefull_hold_guarded`,
  run in a subprocess under `RLIMIT_AS=5 GiB`):
  **`MemoryError`** inside `gated_signature_run` — its `captured`
  bytearray is uncapped, so an unbounded post-death pump converts the
  gate's read loop into a memory-exhaustion surface long before the bound
  (at ~21 GB/s it hits 5 GiB in ~0.25 s). This is the measured root cause
  of the first attempt's death at exactly this row. Under `communicate`
  the same unbounded pump hits the timeout bound first (bounded reader
  path), so the CASES consumer survives it — the hazard is specific to
  consumers that accumulate uncapped bytes while draining.

So: a >64K post-death write does not block any of the three consumers
(bounded drains at full speed; held pipes hit the deadline; closed pipes
SIGPIPE the writer). The real edge is **reader-side resource exhaustion**
on the uncapped-capture gate, plus the standing orphan mechanics already
pinned at r62–r64.

## Divergences / sharpenings vs the author's record

1. Author's `bounded_claim` "rejection axis as origin-blind as the
   signature axis" — **confirmed, and in fact blinder**: no while-live
   gate exists on the error axis, the scan is stream-blind post-merge,
   and the allowlist admits any origin/timing that string-matches.
2. "Gate-invisible" is precise about *verdict input*: the forged error
   bytes are inside the gate's captured stream every rep — observable,
   unused. A hypothetical gate-authored verdict would ACCEPT the
   forged-error arm.
3. New edges the arm-level claim does not cover (all measured live):
   newline-split token **evades** the line-local scan entirely (record
   PASSES with the forged bytes in-capture); stdout-carried forged error
   **evades** `classify_streams`; a forged *allowlisted* error is
   **admitted** under the matching allowlist; a mid-signature splice
   corrupts BOTH axes (defeats sole-cause isolation); the uncapped gate
   capture is a memory-exhaustion surface under an unbounded post-death
   pump.
4. CASES-bound nuance: the ~6s hold releases inside the 8s CASES bound —
   the hold arm is only a "double-axis rejection" at the 3s meta bound;
   at the production bound it is a pure error-axis FAIL on a clean exit-0
   record (committed meta's `hold_timeout_alone_rejects` documents the
   reverse direction at 3s).
5. Cosmetic: `descendant_alive_at_return=True` on release arms is a
   zombie-sampling artifact of `pid_alive` under the subreaper — verified
   directly (post-`communicate` the release descendant is already gone
   at +0.00 s; `kill(pid,0)` satisfies the briefly-unreaped zombie). The
   author's records inherit the same ambiguity on the same field.

## Recommended next-round surfaces (report-only)

1. Track the evasion shapes as a lesson/meta row: the rejection clause is
   `ERROR:`-substring-per-line — newline-split and stdout-under-
   `classify_streams` both defeat it on real pipe writes.
2. Pin the allowlist origin-blindness: a forged allowlisted error admits
   on expected-negative rows — the forgery dual of the positive-marker
   spoof.
3. Cap or document the gated reader's uncapped `captured` (one-line
   resource bound); the unbounded-pump shape OOMs the *reader* while the
   harness correctly bounds the child.
4. If an error-axis gate is ever proposed, the `gated_errforge_run`
   dual-marker timing split already shows it discriminates — and the
   `err_predeath` arm shows it is racable pre-death, same scope limit as
   the signature gate.

## UNKNOWNs / retained caveats

- Single host (godot 4.7.2 headless, CPython 3.14.7, 32 CPU): absolute
  timings (~35–60 ms post-death error lag, ~6.45 s hold-release) slide
  with load; the clause-level and directional results do not.
- `timed_probe` is an instrumented replica of the gate loop; verdict-path
  evidence is the verbatim-extracted functions (`vg_*`, `comm_*`,
  `st_*`, `pf_comm_*`) plus the author's/critic's own battery receipts.
- The newline-split evasion is demonstrated for the *merged* consumer;
  byte-interleaving across the two pipes (stdout/stderr ordering in the
  `communicate` concatenation) is nondeterministic but clause-irrelevant.
- `vg_*` records show `write_ppid=None` on errforge arms — the verbatim
  r64 gate only parses the FORGE regex; provenance was captured via the
  comm/timed runs' generic `write_ppid=` match (`=1573` post-orphan,
  `==godot_pid` on `err_predeath`/`err_midline` pre-death arms).
- Byte-exactness claim scope: my byte-stability check covers
  verdict-bearing fields; raw `output` lines differ in volatile values
  (pids/paths/addresses/floats) — same convention as the author's
  7-field diff.
- `pidfd`, non-POSIX, exported-build, `OS.execute` paths unprobed
  (carried from r61–r64).

## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r65-boundary/`)

- `drive_edges2.py` sha256 `4cde1257…` — verbatim-extraction + replica
  edge driver v2 (48 bounded runs + 16 unit probes, 7 phases; token-
  scoped reaper; memory-guarded unbounded-pump subprocess).
- `edge-verdicts.json` sha256 `7d97b9e8…` — per-run records incl.
  per-clause tables, event ledgers, `/proc` samples, unit matrix.
- `drive_edges.py`, `drive.stdout`, `raw/` — first attempt (died at the
  unbounded-pump gate row; retained as corroborating Phase-A receipts —
  its 15 `vg_*` rows agree with this run's).
- `raw2/` — merged captured bytes per run (this run).
- `proj_stock/` — byte-identical copy of tracked fixture (`37cf5015…`)
  + `project.godot` (`8de8b3af…`).
- `proj_edge/descendant_pipe_probe.gd` sha256 `dded5056…` — scratch-only
  edge fixture (stderr/predeath/split/newlinesplit/allowlisted/glue/
  midline/flood/combo/pipefull arms); tracked file untouched.

No commit, no tracked mutation, no LOG/SCORECARD write; descendants
SIGKILLed only when both the run's own printed pid and the fixture-unique
cmdline token matched; post-run `/proc` scan clean; zero stray fixture
processes.
