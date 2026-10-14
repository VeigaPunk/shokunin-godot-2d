# Round 66 author report — rejection-clause SURFACE map (host: devin)

Seat: author (ONLY tracked-file writer), lane `game-dev-2d`, declared
axis-move (verbatim brief): pin the rejection-clause SURFACE map — the r65
critic/boundary measured edges that never became tracked: (a) the per-case
allowlist acts as the rejection clause's preemptor row — a forged error
matching the allowlist is verdict-inert (absorbed) while an un-allowlisted
twin rejects; (b) the `count("ERROR:")==1` conjunct / allowlist match
shapes are breakable gates (hcom-shaped: exact vs `,`-prefix vs structured
forms); (c) line-faithfulness: `ERR\n`+`OR:` newline-split EVADES the
line-local scan, an interleaved splice can FABRICATE a reject line present
in neither stream; (d) a dead-entry census — allowlist entries or scan
clauses that no reachable child output can trip. Declared falsifiable
claim: the rejection clause's verdict is a pure function of merged-output
line presence modulo the allowlist — forgeable in both directions (evasion
and fabrication) by a post-death descendant.

## Outcome — claim CONFIRMED (measured, all four surfaces live)

`classify_process`'s error clause is a per-line `ERROR:` presence scan over
the merged `stdout + stderr` concat, modulo the per-case allowlist. All
four declared surfaces measured live through the REAL classifier on real
captured pipe bytes — no clause, classifier, or CASES row touched:

- **(a) allowlist-as-preemptor** (`--spawn-allowforge`): reparenting-gated
  descendant echoes `save_corrupt_negative`'s byte-exact allowlisted error
  post-death (`write_ppid=1573 ≠ godot_pid`). Same captured bytes:
  `classify(())` **False** (un-allowlisted twin rejects),
  `classify((entry,))` **True** (absorbed — verdict-inert),
  `classify((foreign,))` **False**. The allowlist checks string equality,
  never origin/timing — an expected-negative row's own allowlist would
  admit a descendant-forged duplicate of its expected error.
- **(b) hcom-shaped gates** — 9-cell shape matrix through the real
  classifier, all landing as declared: exact entry absorbs exact line /
  rejects suffixed twin; `,`-prefix entry absorbs anchored prefix line,
  rejects `count("ERROR:")==2` tail-forge and unanchored lines;
  `,`-entry does NOT absorb an exact-shaped line (entry-shape mismatch,
  measured on real allowforge bytes); structured `chain incomplete` entry
  requires all three conjuncts + count==1.
- **(c) line-faithfulness, both directions:**
  - **Evasion** (`--spawn-splitforge`): post-death `ERR\n` + `OR: ...` —
    forged bytes captured, `error_lines == []` → merged scan **accepts**
    (`inner_classification` True). Contiguous twin (`ERR\nOR:` → `ERROR:`)
    rejects. Line-locality measured, not inferred.
  - **Fabrication, seam** (`--spawn-seamforge`): descendant leaves
    unterminated `...tail ends in ERROR` as the last stdout bytes and
    `: SEAMFORGE phantom fabricated line` as the first stderr bytes →
    merged concat carries `...ERROR: SEAMFORGE phantom fabricated line` —
    a reject line **present in neither stream's line set** (paired
    split-PIPE run: `stdout_tail_line` == tail, `stderr_head_line` ==
    head, fabricated line absent from both) → merged classify **False**.
  - **Fabrication, mid-signature splice** (`--spawn-midlineforge`):
    descendant spawned while child alive (fixed 80ms offset,
    `write_ppid=2050449 == godot_pid=2050449` — provably pre-death) writes
    into the 200ms gap between the signature's two printraw halves →
    `DESCENDANT_PIPE_PROBE: expected ERROR: DESCENDANT_PIPE_MIDLINE forged
    splice`: the ERROR: line is fabricated AND the signature substring is
    destroyed → dual-clause reject; the r65 stripped counterfactual is
    defeated (`mid_stripped` still rejects on the signature axis — the
    error is not sole-isolable).
- **(d) dead-entry census — carried as data:** 39 CASES rows carry
  `expected_errors`; **0 dead entries** this run (every allowlist entry
  was tripped by its row's captured output — each negative control emits
  its allowlisted line). Scan-clause census across all captured CASES
  outputs: `SCRIPT ERROR:` **0 lines**, `Parse Error:` **0 lines** → both
  whole-blob clauses are dead clauses in-run (plus the audio ObjectDB-leak
  clause, 0 lines); `ERROR:`-per-line lines seen: 41. Self-validated:
  `bare_classification_rejects == any_entry_matched` on all 39 rows and
  `allowlisted_classification == verdict` on all 39 rows (real classifier
  re-derivation, not the replica).

## Labrat spike (dispatched, bounded, read-only)

One `ufo-labrat` probe dispatched pre-landing with the 14-arm synthetic
matrix against the verbatim clause. Its tool surface resolved
read/grep/glob only (no exec/write) — it returned the full matrix as
answer text: **14/14 arms matched expectation** by strict static
evaluation of the verbatim source, plus one adjacent finding (the
`ERROR:`-per-line vs `SCRIPT ERROR:`/`Parse Error:`-whole-blob granularity
asymmetry — carried into the census as `clause_granularity`). I persisted
its receipt at `corpus/live/r66-author/labrat/clause-matrix.json` and
corroborated 7/7 spot arms on a real interpreter via
`ast.get_source_segment`+exec of the same clause; the live probe then
measured all shapes end-to-end.

## Landed diff (additive — +565/−1 across two tracked files)

- `corpus/fixtures/descendant_pipe_probe.gd` — sha256
  `37cf5015…` → `9ff5a9ae575790173412b7a78a8e5af02b7f0e593d84bcd9d9c7166b703dbdc1`,
  **+65/−1**: four arm blocks + constants + banner; the single changed
  line is `else: print(MARKER)` → `elif not midline_forge: print(MARKER)`
  (midline emits the marker as halves at the end so the splice gap has no
  intervening child line; all existing arms unchanged). Post-death arms
  reuse the r63 reparenting gate verbatim; midline uses the
  boundary-proven fixed-offset (80ms write vs 200ms gap) shape.
- `corpus/fixtures/run_battery.py` — sha256
  `cd4824cc…` → `76d37ace4b0bbc3c92b83baf431bf6046cdfe4fa88f4bf3cd833dee99269b1ed`,
  **+500/−0**: two additive lines in `execute()`
  (`expected_errors = ()` hoist + `record["expected_errors"]` field) plus
  one block (`probe_error_clause_surface`) between the r65 error-spoof
  print and `if args.probe_failing:`. New row carries `surface_run`
  (bounded-Popen CASES-shape records), `surface_split_run` (separate
  PIPEs), 4 arms + 1 split run, 9-cell shape matrix, dead-entry census,
  **34 discriminations, all True**, SIGKILL orphan hygiene (ungated).

`classify_process`, `classify_streams`, `classify_audio_process`,
`allowed_error`, `gated_signature_run`, CASES, and every existing meta row
untouched (the only `-` in the runner diff is the `---` header line).

## Landed per-arm measurements

(`runs/20261014T051301624764Z/verdicts.json` → `results` →
`probe_error_clause_surface`)

| arm | exit | error | sig | ERROR: lines | wppid | inner cls |
|---|---|---|---|---|---|---|
| allowforge | 0 | None (0.591s) | True | `[allowlist string]` | 1573≠godot | False bare / **True** under entry / False under foreign |
| splitforge | 0 | None (0.600s) | True | `[]` | 1573≠godot | **True** (evades) |
| seamforge | 0 | None (0.572s) | True | `[fabricated]` | 1573≠godot | False |
| midlineforge | 0 | None (0.677s) | **False** | `[spliced]` | **==godot** | False |

Smoke (pre-battery, `corpus/live/r66-author/smoke/`): all four arms
produced the designed merged shapes; seam verified under separate PIPEs
(stdout unterminated tail, stderr `: ` head, fabricated line absent from
both, present in `stdout+stderr` concat).

## Exact evidence

Flagless battery (canonical repo root `~/Projects/shokunin/game-dev-2d-shokunin`):
`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
corpus/live/r66-author/runs` → **exit 0**,
`runs/20261014T051140112142Z/verdicts.json` **PASS 88/88 rows** (sha256
`c62c1bec739b0d55d4ea6e7aab583bc8f14344002f5ef9f3e087861df9f8aadf`) —
87 prior rows + `probe_error_clause_surface`; stdout
`corpus/live/r66-author/battery.stdout`.

Mandated seven-flag battery (exact invocation):
`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
corpus/live/r66-author/runs --probe-failing --probe-unrelated-error
--probe-export-launch --probe-godot-error --probe-stream-attribution
--probe-crash-exit --probe-timeout` → **exit 0**,
`runs/20261014T051301624764Z/verdicts.json` **PASS 99/99 rows** (sha256
`ff4bee33fabed874e6bc96480c067d98d9b8df460d2c849e67b822231bcbd617`);
stdout `corpus/live/r66-author/battery-full.stdout`. Row arithmetic: 81
CASES + 2 mutants + 4 unrelated-error + 12 meta/probe rows (7
unconditional: save-process, crash, pipe-EOF, signature-spoof,
while-live-gate, error-spoof, **error-clause-surface**; 5 opt-in). The two
designed inner `FAIL` lines (`godot_error_unrelated`, `stream_reject`)
unchanged.

Prior-row stability — 7-field diff `(script, flags, expected_exit,
actual_exit, signature, verdict, error)`:

- vs **same-session pretree** run: HEAD tracked tree materialized
  read-only via `git archive HEAD corpus/fixtures | tar -x` into
  `corpus/live/r66-author/pretree/` (runner sha `cd4824cc…`, fixture
  `37cf5015…`, both == `git show HEAD:` digests), same 7 flags →
  `pretree-runs/20261014T051443586564Z/verdicts.json` **PASS 98/98**
  (sha256 `537ffd945c28438bdd0f015dd7f291ca683f1929a337cde1fa084afafd3e493b`):
  **98 common rows, 0 mismatches**; new-only
  `{probe_error_clause_surface}`; pretree-not-in-new `[]`.
- vs r65 **named baseline receipt**
  `corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json`:
  **97 common rows, 0 mismatches**; new-only
  `{probe_descendant_error_spoof, probe_error_clause_surface}`. The r63
  accepting-forgery row `descendant_pipe_forged_signature_release` stays
  `PASS exit=0`; `probe_descendant_error_spoof` carries all **29**
  discriminations True (in-run discrimination
  `prior_meta_rows_stable_29_discriminations`).

Separate leg: `--fault-injection` → **exit 0**,
`fault-runs/20261014T051447319929Z/fault-verdicts.json` outer **PASS**
(sha256 `cc50beaf84dfdc2010358eafda5dbb50e217ed6327d8e39fd7b3538cc612fd8f`),
designed inner `fault_hang`/`fault_unrelated_error` FAILs unchanged.

No LSP server answers either file (only clangd installed; no Python or
GDScript language server configured) — text edit was the only path; the
change is additive blocks with no cross-file rename.

## Files written (inside brief scope only)

- tracked: `corpus/fixtures/descendant_pipe_probe.gd` (+65/−1),
  `corpus/fixtures/run_battery.py` (+500/−0)
- report: `reports/round-66/r66-author.md` (this file)
- scratch: `corpus/live/r66-author/{labrat/clause-matrix.json,
  smoke/, pretree/, pretree-runs/, pretree-battery.stdout, runs/,
  battery.stdout, battery-full.stdout, fault-runs/, fault.stdout}`

## Remaining risks / blockers

- **Midline timing (bounded, declared):** the splice relies on the
  descendant's 80ms fixed offset landing inside the child's 200ms
  printraw gap (boundary-proven shape). Under >120ms scheduler stall the
  write lands after half2 → marker intact + separate error line →
  `midlineforge_error_spliced_into_signature` flips FAIL (declared
  falsification surface; the splice landed mid-gap in both battery
  runs on this host).
- **Census is run-scoped data:** `dead_in_run` labels entries untripped
  by THIS battery's outputs — 0 dead this run; it is evidence about
  reachable output, not a proof the entry is forever dead. The census
  covers CASES `expected_errors`; opt-in probe allowlists are listed
  under `allowlists_outside_expected_errors`, not censused (they execute
  after the meta block).
- **Allowforge allowlist choice:** the absorbed entry is
  `save_corrupt_negative`'s exact-shaped string — absorption is
  entry-shape-specific; the `,`-prefix entry measured on the same bytes
  does NOT absorb (entry-shape mismatch). Other rows' entries untested
  for cross-forgery (each is a per-case preemptor by construction).
- **`surface_allowed_error` is a disclosed replica** for per-entry match
  attribution only; verdict-level liveness is re-derived through the
  real `classify_process` (`bare`/`allowlisted` columns + consistency
  discriminations) — replica drift would surface as a census
  inconsistency FAIL, not a silent mislabel.
- **Stream-merge ordering:** the seam fabrication relies on the runner's
  fixed `stdout + stderr` concat order — measured and pinned; a consumer
  concatenating stderr+stdout would fabricate a different phantom.
- No blockers. Commit/push left to operator per seat rules.
