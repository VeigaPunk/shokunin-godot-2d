# r66 verifier — NON-AUTHOR verification of cb84d0a

Commit under test: `cb84d0a6f1706e2604190c988162aa59c70266c7`
("r66: rejection-clause surface map — allowlist preemptor, evasion, fabrication")
Verifier run dir: `corpus/live/r66-verifier/runs/20261014T092653605430Z/`
Godot: `/usr/bin/godot` = `4.7.2.stable.arch_linux.ed1daf0bf`
Note: a prior verifier instance died mid-run; its completed `battery.stdout`
(89 lines, all PASS, pointing at `corpus/live/runs/20261014T053603255626Z`)
was left in `corpus/live/r66-verifier/` and is used below as a comparison
receipt. The tree has unrelated dirty files under `corpus/live/r66-scribe/`
(other seat's scratch); `corpus/fixtures/` is clean vs HEAD — the two files
under test hash-identical to `git show cb84d0a:` (see seed digests).

## Command-level evidence

Independent battery (absolute --runs path, as instructed):

    python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
      --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r66-verifier/runs
    -> exit 0; stderr empty; stdout 89 lines, final line
       "PASS battery: .../r66-verifier/runs/20261014T092653605430Z/verdicts.json"

- `verdicts.json`: outer verdict PASS, `len(results) == 88`, zero non-PASS rows.
- `probe_error_clause_surface` row: verdict PASS, `len(discriminations) == 34`,
  `all(...) == True` (printed all 34 keys; none False).
- Row ordering in my stdout byte-identical (post-`cut -d:`) to the prior
  verifier's `battery.stdout` — 89/89 lines.
- Verdict diffs (per-case `verdict` field):
  - vs prior verifier run `runs/20261014T053603255626Z`: 88 common, 0 mismatches.
  - vs author's committed flagless run `r66-author/runs/20261014T051140112142Z`:
    same 88-case set both directions, 0 mismatches.
  - vs r65 named baseline `r65-baseline/runs/20261014T022523005280Z`:
    86 common rows, 0 mismatches; new-only
    `{probe_descendant_error_spoof, probe_error_clause_surface}`
    (86 < author's 97 because flagless omits the 11 opt-in probe rows — expected).

## Per-claim verdicts

### Claim 1 — four new fixture arms: AGREE

`git show cb84d0a -- corpus/fixtures/descendant_pipe_probe.gd` shows all four
arms added (+70/−4): `--spawn-allowforge`, `--spawn-splitforge`,
`--spawn-seamforge`, `--spawn-midlineforge`, with constants
`ALLOWFORGE_ERROR`/`SPLITFORGE_*`/`SEAMFORGE_*`/`MIDLINE_*` and the `elif not
midline_forge: print(MARKER)` guard for the halved-signature arm.

Live evidence from my run's `results -> probe_error_clause_surface -> arms`
(all `actual_exit=0`, `error=None`, `elapsed≈0.4–0.7s`):

- `surface_allowforge`: `signature_observed=True`, `error_lines ==
  ["ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected
  signature=JSON_PARSE_ERROR"]` (byte-exact allowlisted save_corrupt_negative
  string), `write_ppid=1573 != godot_pid=2457101` (post-orphan write).
- `surface_splitforge`: captured lines `'ERR'` then `'OR:
  DESCENDANT_PIPE_SPLITFORGE newline-split diagnostic'` — `error_lines == []`;
  `inner_classification=True` (evaded); `write_ppid=1573 != godot_pid`.
- `surface_seamforge`: merged `error_lines == ["DESCENDANT_PIPE_SEAMFORGE tail
  ends in ERROR: SEAMFORGE phantom fabricated line"]`; the paired split-PIPE
  run shows raw stdout last line `'...tail ends in ERROR'` (unterminated) and
  raw stderr first line `': SEAMFORGE phantom fabricated line'` — the
  reject-triggering line is in neither stream; `write_ppid != godot_pid`.
- `surface_midlineforge`: `signature_observed=False`; spliced line
  `'DESCENDANT_PIPE_PROBE: expected ERROR: DESCENDANT_PIPE_MIDLINE forged
  splice'` captured verbatim (`midline_spliced_line` field);
  `write_ppid=2457225 == godot_pid=2457225` — pre-death write, exactly as
  claimed; `inner_classification=False`.

### Claim 2 — surface meta probe, reparent_gate extraction, 88/88, 34/34: AGREE

- `run_battery.py` diff is exactly +500/−0 (numstat), containing
  `probe_error_clause_surface` between the r65 error-spoof print and
  `if args.probe_failing:` — surface_run/surface_split_run bounded-Popen
  records, 9-cell `shape_matrix`, `census` block, 34-key `sf_discriminations`.
- Battery: 88/88 PASS in my run (see evidence above); surface meta PASS,
  34/34 discriminations True — matches claim.
- `reparent_gate` extraction is real but lives in
  `descendant_pipe_probe.gd` (`var reparent_gate := ("while read -r _ _ _ pp _
  < /proc/self/stat ...`)` consumed at 6 `OS.create_process` sites covering 8
  flag arms: hold, forge-hold/release, errforge-hold/release, allowforge,
  splitforge, seamforge). The claim's phrasing attaches it to run_battery.py —
  loose wording only; the extraction itself is verified and the pre-change
  file carried 3 inline copies (3 replaced + 3 new-arm uses = 6 sites).

### Claim 3 — rejection is not pure line-presence: AGREE

Code-verified at `run_battery.py:160-178` and demonstrated live:

- Blob clauses: `"SCRIPT ERROR:" not in output and "Parse Error:" not in
  output` — whole-blob substring conjuncts that no allowlist entry can
  preempt (the allowlist only filters the per-line `unrelated_errors` list).
  Census corroborates: `SCRIPT ERROR: 0`, `Parse Error: 0` lines in-run.
- Allowlist preempts only the generic `ERROR:`-in-line clause: allowforge's
  identical captured bytes classify False under `()`, True under the
  matching entry, False under a foreign entry
  (`allowforge_rejects_without_allowlist`,
  `allowforge_absorbed_by_matching_allowlist`,
  `allowforge_rejects_under_foreign_allowlist` — all True in-run).
- Newline evasion token-sensitive: `'ERR'`/`'OR: ...'` lines captured,
  `error_lines == []`, inner classification True; synthetic contiguous twin
  `ERR\nOR:`→`ERROR:` rejects (`splitforge_contiguous_twin_rejects`).
- Seam fabrication: reject-triggering line `'...ends in ERROR: SEAMFORGE
  phantom fabricated line'` exists only in the `stdout+stderr` concat —
  absent from both raw streams in the split run; both merged and
  split-then-merged classifications reject.

### Claim 4 — prior rows 0 mismatches: AGREE

Three independent comparisons above: 0 mismatches vs r65 baseline receipt
(86 common), vs author's committed r66 flagless run (88 common), vs the dead
prior verifier's run (88 common). The r63 accepting-forgery row
`descendant_pipe_forged_signature_release` remains `PASS exit=0`, and the
in-run anchor `prior_meta_rows_stable_29_discriminations` is True.

### Claim 5 — classify_process vs classify_streams divergence: AGREE

Real at `run_battery.py:160` vs `:179`:

- `classify_process`: signature is a blob substring of `stdout+stderr`;
  `ERROR:` rejection is a per-line scan over the merged text; `SCRIPT
  ERROR:`/`Parse Error:` are merged-blob conjuncts — hence the seam
  fabrication and split-token evasion this round measures.
- `classify_streams` (sole call site `:2219`, opt-in
  `--probe-stream-attribution` probe): signature must be in **stdout**;
  SCRIPT/parse conjuncts checked per-stream (no seam possible); the error
  scan is **stderr-only and stricter** — every nonblank stderr line must be
  allowlisted, not just `ERROR:` lines — while `ERROR:` on stdout is
  invisible to it. Divergence is bidirectional and exactly as documented.

### Seed digests unchanged: CONFIRMED

`git diff 4d938b2..cb84d0a -- corpus/fixtures/` touches only the two files.
Working-tree digests equal `git show cb84d0a:` digests:

- `run_battery.py` = `76d37ace4b0bbc3c92b83baf431bf6046cdfe4fa88f4bf3cd833dee99269b1ed`
  (matches author report's post-change digest).
- `descendant_pipe_probe.gd` = `92a40d70e31daa5048a4c49864d4ece276fbfbac8cb93f2cc6751c6c798caa91`;
  pre-image at 4d938b2 = `37cf5015…` (matches author report's old digest).

## Findings (severity-ordered)

1. **Minor (report staleness, not code)**: `r66-author.md` records the
   post-change `descendant_pipe_probe.gd` digest as `9ff5a9ae…` and the diff
   shape as `+65/−1`; the committed file is `92a40d70…` at `+70/−4`. The
   delta (+5/−3) is consistent with the `reparent_gate` extraction landing
   after the report's digest was computed (the commit message itself credits
   it: "reparent_gate extraction applied (simplifier-warranted…)"). Code is
   correct and battery-verified; only the report's pinned digest/stat is
   stale.
2. **Nit (claim wording)**: claim 2 attributes the `reparent_gate`
   extraction to run_battery.py; it is in the fixture file. And "6
   byte-identical copies" counts post-extraction use sites — 3 copies
   pre-existed; the other 3 are new arms.

## Residual risk / gaps

- `midlineforge` is timing-shaped (80ms write vs 200ms gap); observed
  deterministic across author + prior verifier + my run (3/3), but a
  heavily loaded host could plausibly shift the splice. The discrimination
  set would catch it as a FAIL, not a silent pass.
- `classify_streams` divergence was verified by code read plus its existing
  opt-in probe design; I ran the flagless battery (per instructions), so
  the stream-attribution probe's live verdict was not re-measured this
  round — its semantics are unaffected by this diff.
- Dirty `corpus/live/r66-scribe/` files exist in the working tree; they are
  outside the battery's inputs (scratch is seeded exclusively from
  `corpus/fixtures/`, confirmed at `run_battery.py:128-138`).

All five claims verify on the committed tree. Verifier recommendation: AGREE.
