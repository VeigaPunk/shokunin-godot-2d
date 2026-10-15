# Round 67 scout report — classify_streams per-channel divergence map

Seat: scout, lane `game-dev-2d`. Canonical repo `~/Projects/shokunin/game-dev-2d-shokunin`
(brief's worktree path resolves via `.shokunin/game-dev-2d` symlink). All commands ran on
this host (devin). Scratch + receipts: `corpus/live/r67-scout/`.

## Landed-state caveat (concurrency, not a blocker)

The r67 author diff landed **while I was scouting** — `corpus/fixtures/run_battery.py`
grew 2506→2769 lines mid-session (working-tree sha256 now
`3d5b0721d582a0b9f00b601b1ede5f6c313b700a0a5e9a15d8e09104c7370e7c`; `git status` shows
uncommitted `M run_battery.py` +265, `M stream_attribution_probe.gd` +58, and
`corpus/live/r67-author/` exists). The critic report (`reports/round-67/r67-critic.md`)
attacked the pre-land committed classifiers (file sha `76d37ace…`, HEAD `4a4def9`).
I measured **both** the committed classifiers AND the in-flight arm; line refs below
are current working-tree numbers. My map therefore covers (a) the clause-level diff,
(b) the falsification space, (c) the arm shape the author actually chose, and (d)
independent corroboration of every verdict pair their discriminations expect.

## (1) The two classifiers, line-by-line

`classify_process(code, error, output, expected_exit, signature, allowed_errors=())`
— `run_battery.py:160-177`. Input `output` is the merged blob produced by
`run_process` at `:152`: literal `proc.stdout + proc.stderr` (stdout block first,
exactly one concat seam at byte `len(stdout)`, zero interleave provenance —
r65/r66 seamforge pinned this).

`classify_streams(code, error, stdout, stderr, expected_exit, signature, allowed_stderr=())`
— `:179-208`. **Sole callsite is `:2219` inside opt-in `--probe-stream-attribution`
with `allowed_stderr=()`; no CASES row, export branch, or mutant path uses it** —
it is a meta-only classifier.

| clause | merged (`classify_process`) | per-stream (`classify_streams`) |
|---|---|---|
| exit / runner error | `code == expected_exit and error is None` (:176) | identical (:181) — **no divergence** |
| signature | `signature in output` — anywhere in the concat, incl. wholly on stderr or straddling the seam | `signature in stdout` (:183) — **stdout-bound only** |
| `SCRIPT ERROR:` / `Parse Error:` | whole-blob substring of concat (:177) — a token split across the seam still matches | `in stdout or in stderr` (:185-188) — seam-split token **evades** |
| `ERROR:` scan | per-line over merged lines, modulo `allowed_errors` (:174-175); non-`ERROR:` lines inert | **stdout never scanned at all**; every non-empty stderr line must satisfy `line_allowed` (:200-207) — incl. lines with no `ERROR:` token |
| allowlist shapes | 3: exact / `,`-prefix+`count("ERROR:")==1` / structured `"ERROR: chain incomplete"` conjuncts (:162-172) | 2: exact / `,`-prefix+count==1 (:192-198) — **structured shape absent** |
| seam fabrication | `stdout+stderr` concat fabricates reject lines present in neither stream (r66 seamforge) | no concat → phantom impossible; but the stderr head line itself trips the sweep unless allowlisted |

Measured on real captured bytes (`stream_divergence_probe.py` →
`stream-divergence.json`; classifiers exec'd **verbatim** via
`ast.get_source_segment`, r66-author precedent):

- `--spawn-errforge-release` (descendant `echo` → stdout; stderr **empty**):
  merged `False`, streams `True` — the claimed headline absorption, confirmed.
- `--emit-errforge` (`push_error` → stderr, **4 lines**: error +
  `   at: push_error (core/variant/variant_utility.cpp:1023)` +
  `   GDScript backtrace…` + `       [0] _initialize (res://…:125)`):
  merged `False`; under `(ERRFORGE_ERROR,)` merged `True` / streams **`False`** —
  the allowlist rescues merged but **cannot rescue streams**, because the
  accompanying engine context lines are unallowlistable dynamic text. (Also
  measured independently by the critic's `e2e_results.json`.)
- `--spawn-seamforge`: merged `False` (fabricated line), streams `False` — same
  verdict, different clause (streams rejects on the un-allowlisted `": SEAMFORGE…"`
  + `write_ppid=` stderr lines; the phantom itself is un-fabricatable).
- `--stderr-unrelated` (existing reject arm): merged **`True`**, streams `False` —
  opposite-direction divergence: a non-`ERROR:` stderr line is invisible to the
  merged scan but trips the whole-stderr sweep.

Synthetic cells through the verbatim classifiers (14 cells in the JSON): divergent
on `stdout_ERROR_stderr_clean` (F/T), `stderr_nonerror_noise` (T/F),
`signature_on_stderr` (T/F), `signature_straddles_seam` (T/F),
`seam_phantom_head_allowlisted` (F/T), `structured_entry_stderr` (T/F);
concordant-but-different-clause on `seam_phantom_fabricated` and
`script_error_seam_split` (both F — merged via fabricated `SCRIPT ERROR:` blob,
streams via the stderr sweep).

## (2) Falsification space — enumerated and mostly already measured

Six distinct clause-level mechanisms diverge (the declared claim's "exactly the
stream-attribution axis" is a superset-in-disguise — the critic's falsification of
"exactly" stands; mechanism list matches theirs):

1. **stdout `ERROR:` invisibility** (claimed) — absorbed unconditionally; no
   `allowed_stderr` value can make streams see it.
2. **signature stdout-binding** — stderr-carried or seam-straddled signature:
   merged PASS / streams FAIL.
3. **whole-stderr sweep** — any non-empty un-allowlisted stderr line rejects
   (`WARNING:`, `at:`, backtrace, `STREAM_STDERR:` diag) — strictness, not
   error-placement.
4. **allowlist matcher parity** — `"ERROR: chain incomplete"` structured entry is
   merged-only; same bytes + same entry → merged absorbs / streams rejects.
5. **seam concat artifacts** — `ERROR:`, `SCRIPT ERROR:` (and symmetrically
   `Parse Error:`), and signature text fabricated at `len(stdout)` exist only in
   merged; per-stream checks are seam-immune *when the stderr head is
   allowlisted* (else the sweep still rejects — clause attribution differs).
6. **scoped allowlists** — `allowed_errors` vs `allowed_stderr` are separate
   tuples; divergence between them is only observable under *asymmetric* tuples.

Scope facts that bound the map: `expected_errors` table (:399-446) contains **no**
structured `chain incomplete` entry — that shape lives only in `classify_mutant`
(:371), so mechanism 4 has zero CASES-row exposure today. `classify_streams` has
no `classify_audio_process` counterpart (the ObjectDB-leak clause :210-217 is
merged-only) — moot while streams stays meta-only.

## (3) Cheapest discriminating arm shape — and what the author actually landed

Cheapest I mapped: replay the **already-captured** split bytes —
`split_errforge_run` records (`:1350`, raw_stdout/raw_stderr lines + merged cls),
`surface_split_run` (`:1662`, seam tail/head pins), and the stream-attribution
pair's raw texts — through `classify_streams`; zero new Godot runs. (`surface_run`
records discard per-stream locals `sf_out`/`sf_err` — not replayable without
re-run or +2 fields; CASES records are unreplayable: `run_process` merges at
capture, `:152`.)

The author's in-flight diff chose a cleaner variant with the same cost class:
**inside** the existing `--probe-stream-attribution` block (`:2262-2549`), 7 new
fixture flags on `stream_attribution_probe.gd` (`--stdout-error`,
`--stderr-error`, `--stderr-structured`, `--sig-on-stderr`, `--seam-error`,
`--seam-script`, `--seam-sig` — single-process `print`/`printerr`/`printraw`
steering, no descendants, no timing hazards) → `streamdiv_arm` records
(raw_stdout/raw_stderr + lines, `stdout_tail_line`/`stderr_head_line` seam
positions, per-stream + merged `error_lines`, `signature_in_{stdout,stderr,merged}`,
`script_error_in_{*}`) + `dual_classify` (both classifiers on the same captured
pair + `divergent` flag) + 6 allowlist reclassification cells + 20
`sd_discriminations` + a closed-set `divergence_table` expectation pin. Verdict
**folds into the existing `probe_stream_attribution` row** (`meta_pass and
sd_meta_ok`, `:2536`) — zero new `results` rows: flagless battery stays 88/88 by
construction (opt-in flag never runs), mandated-flag run stays 99 rows; the r66
surface's 34 discriminations are a different row, untouched.

Independent corroboration (`author-arms-corroboration.json`, verbatim classifiers,
real godot 4.7.2 runs of the modified fixture): **all 7 arms + 4 reclass cells
land exactly as their discriminations expect** —

| arm | merged | streams | divergent |
|---|---|---|---|
| stdout_error | F | T | ✓ headline |
| stderr_error | F | F | concordant; exact-entry T/T, foreign F/F |
| stderr_structured (entry=`"ERROR: chain incomplete"` both tuples) | T | F | ✓ mechanism 4 |
| sig_on_stderr (stderr allowlisted with the sig itself) | T | F | ✓ mechanism 2 |
| seam_error (head allowlisted streams-side only) | F | T | ✓ mechanism 5 |
| seam_script (head allowlisted) | F | T | ✓ blob-clause seam immunity |
| seam_sig | T | F | ✓ seam-straddled signature |

plus `stream_reject` T/F (mechanism 3) and `stream_accept` T/T — matching the
closed-set expectation `{7 divergent, 2 concordant}` exactly. Confidence:
**high** — the arm as written will land green under the mandated seven-flag run.

## (4) Replayable r66 surface records

- `ef_release_split`/`ef_genuine_split` (`split_errforge_run` records):
  `raw_stdout_lines`/`raw_stderr_lines`/`error_on_{stdout,stderr}`/
  `merged_classification` — streams verdict replayable via `"\n".join` (no
  unterminated tails in these arms; strip/split is verdict-inert for
  `classify_streams`'s substring+line-set reads). I did exactly this on fresh
  captures — same verdicts.
- `sf_seam_split` (`surface_split_run`): raw line sets + `stdout_tail_line`/
  `stderr_head_line` seam pins + `merged_classification`; streams replay needs
  stderr allowlisting the head — the `write_ppid=` line is dynamic and
  unallowlistable, so seamforge can **never** PASS under streams as written
  (pin = same verdict / different clause).
- Stream-attribution pair records already carry raw texts — the author replays
  them directly (`sd_pair_dual`).
- `surface_run` records (allowforge/splitforge/seamforge/midlineforge): merged
  text only; per-stream bytes discarded. Replayable only by re-running or by
  adding `raw_stdout`/`raw_stderr` fields (+2 lines at `:1610-1620`).

## Remaining unknowns / gaps (for author/verifier)

1. **`push_error` defeats `allowed_stderr`** — measured (my `--emit-errforge`
   run + critic's): a real engine diagnostic's `at:`/backtrace context lines are
   unallowlistable, so under streams even a fully-allowlisted genuine error
   rejects. The author's arms all use `printerr` (single clean line) — the map
   does not pin this edge. Smallest fix: one `--emit-errforge`-style reclass row,
   or document `allowed_stderr` as exact-text-only by contract.
2. **`Parse Error:` seam variant** unpinned (symmetric to `seam_script`; trivial).
3. **`,`-prefix entry per-stream**: both classifiers share the shape → my cell
   shows agree (T/T); no dedicated pin in the arm — no divergence expected.
4. **Asymmetric-allowlist scoping** (critic's P/Q): partially exercised by
   sd4-sd7 (streams-only allowlists) but no pin holds one tuple empty while the
   other carries the matching entry for the *same* channel.
5. **CASES-row exposure unknowable from current records** — `run_process` merges
   at capture; whether any real battery row would flip under per-stream
   classification is unmeasurable without changing `run_process` (out of scope;
   streams is meta-only anyway).
6. **Provenance caveat** (critic, correct): seam-position pins are concat
   offsets, not emission timing — the author's `stdout_tail_line`/
   `stderr_head_line` fields are the honest shape; do not present them as
   ordering evidence.

No LSP server answers either file (only clangd installed; no Python/GDScript
server) — text grep + verbatim AST-exec were the semantic paths; recorded per
seat rule.

## Evidence index

- `corpus/live/r67-scout/stream_divergence_probe.py` → `stream-divergence.json`
  (7 real Godot arm captures + 14 synthetic cells; `python3 stream_divergence_probe.py` exit 0)
- `corpus/live/r67-scout/author-arms-corroboration.json` (7 new-flag arms +
  reclass cells, verbatim classifiers, exit 0)
- `corpus/live/r67-scout/proj/` (project.godot + both probe fixtures)
- Clause refs: `run_battery.py` :152 (merge), :160-177, :179-208, :210-217,
  :1350 (`split_errforge_run`), :1587/:1662 (`surface_run`/`surface_split_run`),
  :2199-2549 (stream-attribution block incl. in-flight r67 arm), :399-446
  (`expected_errors`), :371 (structured entry's only non-meta consumer)

Stop — assigned question answered; admissibility is the judge's call.
