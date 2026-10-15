# Round 67 — boundary recon: per-channel divergence surface edges

## Scope and method

LEAF boundary seat, scratch-only and report-only. I wrote only this report
and `corpus/live/r67-boundary/`. No tracked fixture, runner, CASES row,
lesson, LOG, or SCORECARD entry touched; no subagent dispatch; no git
mutation.

Assignment (lane brief, verbatim edges): (1) per-stream seam positions
**both** directions (stdout-tail+stderr-head AND stderr-tail+stdout-head);
(2) splitlines boundary table on the per-stream path; (3) allowlist shapes
under `classify_streams`; (4) unicode/`ÿ` on the per-stream path (r66's
DoV class — does it hit `classify_streams` identically?); (5) drain-order
sensitivity — does `Popen.communicate()` ordering change which seam
fabricates?

**Provenance.** The author's r67 diff landed mid-session (r66 pattern
repeated): at probe start the tree was clean at `4a4def9` (runner sha256
`76d37ace…`, 2506 lines); the author then wrote the working-tree diff
(runner `3d5b0721…`, 2769 lines; fixture `97143ad3…` → `dc0b0d5c…`,
67 lines) and committed it as HEAD `d44ba86` while I measured. All my
post-landing numbers are on the committed content: `git show
HEAD:corpus/fixtures/run_battery.py` sha256 == working-tree sha256 ==
`3d5b0721…`; `git status corpus/fixtures/` clean.

Method: `ast.get_source_segment`-extract `run_process`, `classify_process`,
`classify_streams`, `classify_audio_process`, `pid_alive`, `kernel_ppid`
from the landed runner and `exec` them — sha-pinned per segment
(`boundary-verdicts.json → function_shas`; all six byte-identical to
HEAD). All verdicts are verbatim-function outputs; unit-string cells are
disclosed as such. Replay anchor: every replayable row of the r67 frozen
baseline receipt and the author's flagless receipt re-classified through
the verbatim functions under each case's own classification convention
(audio → `classify_audio_process`; export rows → their
`classify_export`-equivalent signature/allowlist; mutants → the
`classify_mutant` arm logic): **81 + 83 rows, 0 mismatches**.
Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Linux x86_64,
CPython 3.14.7.

## Author-claim verification (independent reproduction)

- Author flagless receipt `corpus/live/r67-author/runs/
  20261014T095753034446Z/verdicts.json` (sha256 `2726c7b2…`): **88 rows,
  all PASS**; surface meta 34/34.
- Author full-flag receipt `…/20261014T095910487678Z/verdicts.json`: **99
  rows PASS**; `stream-attribution-verdicts.json` (sha256 `d65608f9…`)
  `probe_stream_attribution` PASS, **20/20 discriminations True**;
  divergence table exactly the declared 9-row set (7 divergent, 2
  concordant).
- MY own flagless battery on the landed tree: `python3
  corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
  corpus/live/r67-boundary/runs` → exit 0, `runs/20261014T101324429639Z/
  verdicts.json` (sha `69af8243…`) — **88 rows, all PASS; surface
  34/34**. "88/88 + surface 34/34 stays green" holds: the arm lives
  entirely inside `if args.probe_stream_attribution:` (`:2199-2551`),
  the flagless path is byte-untouched.
- MY own `--probe-stream-attribution` battery: `runs/
  20261014T101440531775Z/verdicts.json` (sha `92811059…`) — **89 rows,
  all PASS**; the stream row PASSes with **20/20 discriminations** on my
  independent capture. Independent reproduction of the author's probe
  verdict confirmed.
- Landed arms independently re-driven per-stream through verbatim
  classifiers (`drive_boundary.py → edge1_seams.landed_redrive`), each
  arm bare AND under the author's pinned allowlists — all nine cells
  reproduce the author's table exactly (incl. `seam_error`/
  `seam_script` bare=False/False vs head-allowlisted False/True).

## Edge 1 — per-stream seam positions: the cross-channel seam is a ONE-position space

Real-pipe captures through verbatim classifiers (`edge1_seams`):

| arm | merged | streams | reading |
|---|---|---|---|
| `seam_A_synth` — stdout tail `BOUNDARY seam tail ends in ERROR` (unterminated) + stderr head `: BOUNDARY seam phantom merged-only` | bare False | bare False | the phantom `…ERROR: BOUNDARY seam phantom merged-only` is in `merged.splitlines()` and in **neither** stream's line set |
| same capture, stderr head allowlisted | **False** | **True** | the fabricated veto is merged-only; streams absorbs the (real) stderr fragment and stdout is never line-scanned |
| same capture, merged allowlist = **the phantom line itself** | **True** | False | the merged allowlist preempts a line that exists in neither stream — a fabricated reject line is a first-class allowlist target |
| `seam_B_synth` — stdout head `: BOUNDARY rev head fragment` + stderr tail `BOUNDARY rev tail ends in ERROR` (unterminated) | **True** | **False** | **direction B cannot fabricate**: concat order is `stdout+stderr`, so the fragments sit at the blob's opposite ends; `any_merged_line_with_error == []` — the `ERROR:` token never exists for merged. Streams rejects on the stderr tail's mere presence (strictness), not on any error content |
| `seam_B_postdeath` — same B shape, stderr tail written by a reparenting-gated descendant after child exit | True | False | post-death writes only ever extend a stream's **tail** (pipe append) — they can never reach stdout head; direction B stays unfabricatable post-death |
| `seam_B_sig` — signature head on stderr tail, tail on stdout head | False | False | the signature never becomes contiguous anywhere — direction B cannot fabricate the accept axis either |
| `seam_intrastream_postdeath_sig` — child leaves unterminated stdout `STREAM_STDOUT: expected attribution `, descendant prints `marker` post-exit on the SAME fd | True | True | **intra-stream seam**: the signature fabricates inside stdout alone; `classify_streams`' stdout signature check is satisfied by bytes no single process completed — stream-channel separation is not required for signature forgery |
| `seamforge_postdeath_perstream` — shipped r66 `--spawn-seamforge` arm captured per-stream | False | False | concordant reject, different mechanisms: merged on the phantom line, streams on the unallowlisted stderr head |
| landed `--seam-error` / `--seam-script` / `--seam-sig` (author arms, in-life writes) | F/F bare, F/T allowlisted; F/T | matches author's pins |

The seam space is a single position — `stdout-tail|stderr-head` — and it
is created by the *runner's concat order*, not by stream semantics.
`classify_streams` is seam-immune by construction (no concat), which is
why the author's seam arms diverge exactly as declared. New cells beyond
the landed map: direction-B de-fabrication (merged can't assemble the
token at all), the merged allowlist absorbing a nonexistent phantom line,
and the intra-stream signature seam that fools BOTH classifiers.

## Edge 2 — splitlines boundary table on the per-stream path

`stderr.splitlines()` (`:189`) vs `output.splitlines()` (`:161`) — the
SAME `str.splitlines`; the boundary set is identical on both paths.
Measured per boundary char (`edge2_splitlines.boundary_table`), stderr
payloads `ENTRY+ch`, `ENTRY+ch+rest`, `ERR+ch+OR: tail`:

| char | splits? | strip()s trailing? | tail cell (str/mrg) | frag cell (str/mrg) |
|---|---|---|---|---|
| `\n \r \r\n \v \f \x1c \x1d \x1e` | yes | yes | True/True | False/True |
| `\x85` NEL (as c2 85) | yes | yes | True/True | False/True |
| `\u2028`/`\u2029` | yes | yes | True/True | False/True |
| `\x1f` | **no** | **yes** | True/True | False/False |
| `ÿ` (U+00FF) | no | no | False/False | False/False |

Readings:

- **Evasion is a merged-only property for stderr-carried bytes.** Every
  split that erases the `ERROR:` line from merged leaves fragments that
  are themselves rejecting lines under streams' every-nonblank-line
  audit — `ERR\x85OR: tail` on stderr: merged True (evaded), streams
  False (`ERR` unallowlisted). Real-pipe confirmations
  (`nel_split_stderr`, `vt_split_stderr`, `fs_nosplit_stderr`,
  `yuml_noise_stderr`): all streams=False; merged=True except `\x1f`
  (no split → real `ERROR:`-less line → merged still True; streams False
  either way).
- `\x1f` is the asymmetric control: `str.splitlines()` does NOT split it
  (FS/GS/RS split, US doesn't), but `str.strip()` removes it — so
  `ENTRY\x1f` still exact-matches and absorbs (both paths True).
- `ÿ` neither splits nor strips → `ENTRYÿ` escapes exact match on both
  paths.
- A boundary at the END of an allowlisted line is absorbed on both
  (the trailing fragment is empty/`strip`-skipped).
- `blob_split_stdout`: `SCRIPT ERR\n` + `OR: …` on stdout evades the
  blob substring check **identically in both classifiers** (streams's
  blob checks are `in stdout`/`in stderr` substring tests, equally
  line-naive) — streams=True, merged=True.

## Edge 3 — allowlist shapes under `classify_streams`

Unit matrix over stderr lines (`edge3_allowlist.shape_matrix`,
`streams/merged` under the same entries), plus stdout-side cells:

- `exact` / `,`-prefix+`count==1` shapes behave identically in both on
  stderr: `exact_absorbs` T/T, `comma_tail_absorbs` T/T, escapes
  (suffix/prefix/count==2/no-comma) F/F both.
- **`structured` is merged-only** (the author's pin (c), confirmed):
  `structured_canonical` **False/True**; `structured_reordered`
  (order-free `in` checks) **False/True**. `line_allowed` (`:192-198`)
  has exact + `,`-prefix only. The **exact-match backdoor** survives:
  `structured_bare_entry_as_line` True/True — the bare entry string as a
  stderr line absorbs via `stripped in allowed`.
- **Streams' allowlist is a general stderr whitelist, not an error
  preemptor**: `nonerror_chatter_allowlisted` T/T and
  `warning_line_allowlisted` T/T — a streams entry can absorb
  `WARNING:`/chatter lines that veto it; merged needs no entry for them
  (they're invisible: `nonerror_chatter_bare` F/**T**). Scope inversion:
  entries merged never needs are load-bearing for streams.
- `comma_entry_on_nonerror_line` F/T: the `,` shape stays error-scoped
  even in streams (`count("ERROR:")==1` conjunct fails on chatter).
- `foreign_entry` F/F: per-call scope on both.
- stdout side: `error_line_on_stdout_bare` **True/False** (the headline
  — stdout never error-scanned; the streams entry is unreachable dead
  weight on stdout). `script_blob_on_stdout` F/F and
  `parse_blob_on_stderr`-with-entry F/F: **the blob vetoes scan both
  streams and are allowlist-proof** — `self_neutralizing_entry`
  (entry = `SCRIPT ERROR: x`) absorbs the line from the audit yet the
  blob veto stands: F/F. An allowlist entry can never preempt a blob
  clause on either path.

## Edge 4 — unicode/`ÿ` per-stream: the DoV class hits identically

`run_process_streams` (`:2200`) is the same `subprocess.run(…,
capture_output=True, text=True)` shape as `run_process` — strict decode
per pipe. Real-pipe arms (`edge4_unicode`):

| arm | outcome |
|---|---|
| `ff_stdout` (raw `\xff` on stdout) | `UnicodeDecodeError` at stdout offset 43 — **no verdict exists** |
| `ff_stderr` (raw `\xff` on stderr) | `UnicodeDecodeError` at stderr offset 0 — **no verdict** |
| `ff_both` | `UnicodeDecodeError` — **no verdict** |
| `raw85_stderr` (raw `0x85`, invalid UTF-8) | `UnicodeDecodeError` — **no verdict** |
| `nel_stderr` (encoded NEL c2 85) | decodes; NEL splits → merged True / streams False |
| `yuml_stdout_noise` (`noise ÿ` on stdout) | decodes; T/T (invisible to both) |
| `yuml_stdout_errorline` (`ERROR: … ÿ` on stdout) | **T/F** — the headline asymmetry carries `ÿ`-carrying bytes too |
| `yuml_stderr_noise` | **F/T** — chatter veto |
| `yuml_stderr_errorline` | F/F — reject under both |
| `ff_then_hold` (write `\xff`, hold pipes >2s) | `TimeoutExpired` — `exc.stdout` arrives as **bytes**, the runner's timeout path decodes `errors="replace"` → `\ufffd` in the recovered output — **a verdict EXISTS** (both classifiers then reject on `error is not None`) |

So r66's denial-of-verdict class hits the per-stream path **identically**
— either stream's undecodable byte crashes before any classifier runs,
stdout or stderr. The measured asymmetry is lifecycle-path, not
channel-path: **DoV is completion-path-only** — the same `\xff` under a
pipe-hold timeout yields a recoverable `\ufffd` record, because the
`TimeoutExpired` buffers are undecoded bytes and the runner decodes them
with `errors="replace"`.

## Edge 5 — drain-order sensitivity: none; the seam is concat-positional

`communicate()` returns `(stdout, stderr)`; the merge is `stdout +
stderr` regardless of when bytes arrived. Arms ×3 reps each
(`edge5_drain`):

| arm | phantom in merged | streams | merged |
|---|---|---|---|
| `stderr_first_then_stdout` (stderr head written, 300ms, then stdout tail) | yes (3/3) | True | False |
| `stdout_tail_then_stderr` (reverse temporal order) | yes (3/3) | True | False |
| `interleaved` (a `pre\n` stderr line occupies the head slot) | no (3/3) | False | True |
| `postdeath_stderr_head` (head written by reparenting-gated descendant after exit) | yes | F bare / T allowlisted | False |
| `bulk_drain_64k` (200KB stdout + 150KB stderr — real concurrent drain) | yes | True | False |

Temporal order across the two fds is invisible to the verdicts — the
only ordering that matters is **intra-stream byte order** (which bytes
are the tail of stdout and the head of stderr — `interleaved` shows a
competing stderr head defeats the seam). Pipe-capacity interleaving
(>64KiB on both fds, real selector-driven drain) changes nothing.
Post-death provenance changes nothing.

## Verdict on the declared falsifiable claim

"classify_streams verdicts diverge from classify_process on exactly the
stream-attribution axis — a stdout-carried `ERROR:` is ABSORBED
(PASS-shaped) where merged rejects, while stderr-carried bytes behave
differently" — **CONFIRMED** on the headline and the author's four-
mechanism refinement (attribution + stderr-strictness + allowlist-shape
+ seam immunity) independently reproduced: my landed re-drive matches
all 9 table rows; my own probe battery reproduces 20/20 discriminations.
My edges add five cells the author's map doesn't pin:

1. Direction-B seams cannot fabricate in merged at all — the
   concat-order pins the cross-channel seam to exactly one position
   (stdout-tail|stderr-head); post-death writes can't reach a head.
2. The phantom seam line is itself a merged-allowlist target —
   allowlisting a line in neither stream absorbs the fabricated veto.
3. The signature axis fabricates intra-stream (one fd, post-death
   completion) — fooling both classifiers; channel separation isn't
   required.
4. splitlines evasion is impossible on streams' stderr — every fragment
   is a rejecting line; the boundary table is identical on both paths.
5. DoV hits both streams identically (per-pipe strict decode) and is
   completion-path-only — the timeout path recovers `\ufffd` and a
   verdict exists.

## Divergences / sharpenings beyond the landed map

- Streams' allowlist is a general stderr whitelist (absorbs non-`ERROR:`
  chatter/`WARNING:`), while merged's preemptor only ever meets
  `ERROR:`-carrying lines — same grammar, different scope class. The
  `,`-prefix shape stays error-scoped in both (`count("ERROR:")==1`).
- Blob clauses (`SCRIPT ERROR:`/`Parse Error:`) are the only stdout
  content `classify_streams` audits — and they are allowlist-proof on
  both paths (self-neutralizing entries absorb the line but not the
  veto).
- `interleaved` stderr content: any non-allowlisted stderr line ahead of
  the head slot both defeats the merged seam AND vetoes streams — a
  single chatter line flips the verdict the opposite way per classifier.

## UNKNOWNs / retained caveats

- Single host (godot 4.7.2 headless, CPython 3.14.7): timings slide,
  verdict directions do not.
- My synthetic arms use `python3`/`sh` children through the same
  `subprocess` capture shapes the runner uses; the landed Godot arms are
  the author's fixture bytes re-captured live. Direction-B on real Godot
  bytes is unrealizable in-tree (no fixture can emit an unterminated
  stderr tail or a post-death stdout head — pipe writes append); it was
  measured on synthetic bytes, which suffices because the seam is a
  runner-concat property, not an engine property.
- `record_dual` binds `expected_exit` to the observed exit so the
  verdict pair isolates the stream axis; the exit axis is not exercised
  by these cells (all arms exit 0 clean anyway).
- `pidfd`/non-POSIX/exported-build/`OS.execute` paths unprobed (carried
  forward).
- Sibling lanes ran concurrent live batteries on this host during
  measurement; my runs are independent receipts.

## Artifact inventory (`corpus/live/r67-boundary/`)

- `drive_boundary.py` — verbatim-extraction edge driver (replay anchor,
  landed re-drive, seam positions, splitlines table, allowlist matrix,
  unicode arms, drain arms).
- `boundary-verdicts.json` — all phase outputs on runner sha
  `3d5b0721…` @ HEAD `d44ba86`.
- `drive.stdout` — driver stdout.
- `proj/` — scratch fixture copy used for the real-Godot re-drive.
- `raw/` — per-stream captures (`landed_*.stdout/.stderr`).
- `runs/20261014T101324429639Z/` — flagless battery receipt on the
  landed tree (88 rows PASS, surface 34/34).
- `runs/20261014T101440531775Z/` — `--probe-stream-attribution` battery
  receipt (89 rows PASS; stream row PASS, 20/20 discriminations).
- `battery.stdout`, `battery.stderr`, `battery-stream.stdout`,
  `battery-stream.stderr`, `pre-landing-shas.txt`.

No commit, no tracked mutation, no LOG/SCORECARD write; descendant
probes were `sh` subshells gated on their own parent's pid
(`/proc/self/stat` ppid-flip), self-exiting within ~0.5s; post-run
process scan clean.
