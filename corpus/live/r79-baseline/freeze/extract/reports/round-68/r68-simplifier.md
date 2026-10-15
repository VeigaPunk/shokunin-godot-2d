# Round 68 simplifier report — midlineforge ladder + receipt-upgrade audit (host: devin)

Seat: simplifier (LEAF, audit-only — write scope is this report +
`corpus/live/r68-simplifier/`; tracked-file edits are author-owned, none
made). Subject: the landed r68 diff, integrated as commit `f754546` —
`corpus/fixtures/descendant_pipe_probe.gd` (+17/−4) and
`corpus/fixtures/run_battery.py` (+302/−2), both inside opt-in paths plus
one fixture flag parse. Audited digests: runner sha256
`7c4214360970860dff5d69b47f3e5aad3dc707e212652984b871186fd431c214`,
fixture sha256 `5c5c629ac187b11832c825c3f510baeab98e81517e01b65491426840f4a39d1f`
(`landed-sha256.txt`); `git show f754546:` blobs match both. Pre-land
snapshots `run_battery.pre-author.py` / `descendant_pipe_probe.pre-author.gd`
verified byte-identical to `1101cb3` blobs (runner `8d7e4d94…`, fixture
`92a40d70…`).

## Verdict

**Minimal-expression bar MET.** All 6 ladder rungs, all 12 new
discriminations (8 ladder + 4 receipt-shape), both mirror matchers, and all
new record fields are load-bearing or honest claim carriers — no
`sd_sig_head`-class dead binding this round (full new-name census below).
Two zero-behavior items found and proven byte-identically by
delete-and-measure: one dead tautological conditional (`exit` clause,
2 lines) and one duplicated payload key (`signature_gap_ms`, 1 line). One
optional extraction demonstrated: the 4-line spliced-line finder idiom now
exists twice (net −4 lines). None of the three change any verdict or
discrimination.

Deletions made: **none** (no tracked edit scope; `git status` on tracked
paths shows zero `M`/`D` rows after `f754546` — only sibling r68 scratch +
`reports/` untracked dirs).

## Preserved contract — independently re-verified on the landed tree

- Flagless battery (mine, post-land bytes):
  `python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
  corpus/live/r68-simplifier/runs-landed` → **exit 0**
  (`battery-landed-exit.txt`), `runs-landed/20261014T112132992259Z/
  verdicts.json` **PASS 88/88** — no ladder/stream rows flagless, as
  declared opt-in.
- Surface meta byte-stable: `probe_error_clause_surface` discriminations
  dict **byte-equal** to the pre-land baseline run
  (`r68-baseline/runs/20261014T104854073132Z`) — 34/34 keys, all True;
  `midline_spliced_line` identical (`…expected ERROR: DESCENDANT_PIPE_MIDLINE
  forged splice`); the default-offset `surface_midlineforge` arm still
  fabricates with `write_ppid==godot_pid` — the r66 point-sample path is
  unchanged by the parameterization (default 80 → `sleep 0.080`, same
  observable bytes).
- Flagless field-diff vs baseline (`field-diff-flagless.txt`):
  `shared=88, new_only=[], base_only=[], verdict_diffs=[]`; residual keys
  identical to the r67 precedent profile (run-local `command`/`output`/
  `xdg_data_home` paths and pid-bearing arm records only).
- Flagged field-diff vs baseline's pre-land `--probe-stream-attribution`
  run (`field-diff-flagged.txt`): `shared=89, new_only=
  [probe_midlineforge_ladder], verdict_diffs=[]`.
- Combined opt-in leg (mine): `… --probe-stream-attribution
  --probe-midlineforge-ladder` → **exit 0**, `runs-landed/
  20261014T112415928385Z/verdicts.json` **PASS 90/90**; ladder payload
  verdict PASS, measured window `landed=[0,40,80,120,160] missed=[240]
  mixed=[]`, 8/8 discriminations True; stream-attribution payload 24/24
  discriminations True, clause map measured exactly:
  `seam_script` → `("blob","error_scan")` (the one multi-clause row),
  `*_sig*` → `("signature",)`, stderr_structured → `("allowlist_shape",)`,
  error-scan rows → `("error_scan",)`, concordant rows → `()`.
- Artifact-level byte-stability, sharpest form
  (`stream-artifact-stability.txt`): deleting ONLY the declared-upgrade
  fields (`divergent_clause`, `raw_stdout_sha256`, `raw_stderr_sha256`,
  the 4 new discrimination keys) from the landed stream-attribution
  artifact makes it **equal** to baseline's pre-land artifact modulo
  volatile fields (pids/paths/elapsed); all 20 pre-existing discrimination
  keys identical and True. The upgrade is surgically additive.

## Load-bearing audit — every element measured

### Ladder rungs {0,40,80,120,160,240} ×3 reps

Each rung is a distinct measurement role: `0` proves downward-closure to
the lowest reachable nominal offset (spawn latency already lands the write
inside the gap — `lo_edge_ms=0`); `40`/`120` are the contiguity witnesses —
without them the claim "[lo,hi) interval" rests on edge samples alone and
an undetected interior hole would still satisfy `window_is_strict_threshold`;
`80` is the r66 replication pin (`point_sample_80ms_still_fabricates`);
`160` is the last-landed rung (hi-edge lower bound); `240` is the sole
missed rung (hi-edge upper bound). Removing any rung shrinks the measured
bound's resolution — 40/120 are not individually pinned by a gate (the
gates survive their removal), but the verbatim declared sweep and the
interval contiguity claim require them. **Keep all 6.** Reps=3 is the
minimal count that can express a `mixed` (jitter-split) cell with majority
semantics; reps=2 splits are ambiguous. Keep.

### Ladder discriminations (8/8 True on my run + all three variant runs)

- `ladder_all_reps_clean_exit0` / `ladder_all_writes_pre_death` —
  confound + provenance guards: a crash/timeout or post-death write would
  silently corrupt cell semantics. Load-bearing.
- `ladder_all_reps_reject` — subtle and load-bearing: a *missed* write
  still rejects via its standalone `ERROR:` line, pinning that the ladder
  measures splice *placement*, not verdict flips. Without it the
  fabrication-window claim conflates "missed gap" with "accepted".
- `point_sample_80ms_still_fabricates` — declared continuity anchor.
- `window_is_strict_threshold` — the bound claim itself
  (downward-closed; mixed cells only inside the band).
- `fabrication_iff_signature_destroyed` — the dual-clause coupling per
  rep (fabrication ≡ signature destroyed).
- `spliced_line_is_head_error_fusion` — byte-exactness of the fabricated
  line (head+ERROR fusion, not adjacent-line coincidence).
- `over_gap_240ms_never_fabricates` — **weakest key**: logically implied
  by `window_is_strict_threshold` (whose nonempty-missed conjunct only
  240 can satisfy). Same class as r67's `accept_arm_concordant` — a named
  semantic anchor for the declared over-gap claim; keep per convention,
  flag noted.

### Receipt-shape upgrades

- `divergent_clause` (run_battery.py:2462-2516) — load-bearing, pinned by
  `divergent_clause_map_exact` (set-exact per-case tuples). Because the
  value is *computed* through the mirrors rather than asserted, the exact
  map pin is a measurement: deleting a clause check or a mirror arm
  falsifies the map, not just the receipt.
- `raw_stdout_sha256`/`raw_stderr_sha256` — load-bearing via
  `dual_records_same_input_digests`: pair rows digest the accept/reject
  captures and each reclassification digests its source arm's bytes —
  the same-input gate is the cross-record digest equality. (The per-arm
  `sha == sha256(own_raw)` sub-check is construction-true — it catches a
  wrong-field-wiring bug, nothing more; cheap, keep.)
- `divergent_clause_nonempty_iff_divergent` /
  `divergent_clause_taxonomy_bounded` — completeness + bounded-taxonomy
  pins; each fails on real regression shapes the map pin alone would
  misreport. Keep.
- `sd_clause_taxonomy` (2 refs), both mirrors (3/2 refs), `divergent_clause`
  (8 refs) — census clean; no dead name.

### Mirror fidelity — verified, not assumed

`sd_merged_line_allowed` mirrors `allowed_error` (nested in
`classify_process` :163-173); `sd_stream_line_allowed` mirrors
`line_allowed` (nested in `classify_streams` :192-198). Both are
line-for-line faithful; AST-extraction truth table
(`mirror_truth.py` / `mirror-truth.txt`): **66/66 merged cells + 66/66
stream cells identical** to the real matchers over a (entry,line) matrix
covering exact/comma-prefix/structured/none entries and exact/suffixed/
foreign/blank/non-ERROR lines — **0 mismatches**. The mirrors attribute,
the real classifiers decide: the alternative (hoisting the nested matchers
into shared scope) would edit audited classifier internals for zero gain.
Mirrors are the minimal-risk expression; hoisting to shared helpers would
be the *larger* change.

## Deletion candidates found — all demonstrated byte-identically

Scratch fixtures copies under `corpus/live/r68-simplifier/del-measure/`
(`fixtures/` = pristine landed control; `vA`/`vB`/`vC` = variants), each
run `… --probe-stream-attribution --probe-midlineforge-ladder` → all
**exit 0, 90/90 PASS, all row verdicts identical to landed, 8/8 ladder
discriminations, identical measured windows**
(`del-measure/variant-verdicts.txt`):

1. **Dead `exit` tautology — `run_battery.py:2480-2481`** (landed):
   ```python
   if (code == 0 and error is None) != (code == 0 and error is None):
       diffs.append("exit")
   ```
   `X != X` is always False — the append is unreachable; "exit" is already
   carried for completeness by `sd_clause_taxonomy` and the docstring. vA
   (`vA-fixtures/`, deleted): stream-attribution artifact **byte-identical
   modulo run paths**; ladder artifact identical modulo volatile
   (pids/elapsed). Provably zero-behavior. **Recommend delete** — the
   docstring sentence already documents the taxonomy slot; the dead
   conditional is theatrical weight.
2. **`signature_gap_ms` (run_battery.py:2157)** — payload-top duplicate of
   `measured_window.nominal_gap_ms`; the results row carries
   `measured_window` (with the gap) but not the top-level key, so the
   top-level key is the redundant one. vB (=vA+this deletion): the ONLY
   structural artifact diff is `signature_gap_ms only-in-landed`;
   verdicts/discriminations identical. **Recommend delete** (or rename
   `nominal_gap_ms` for symmetry — author's pick; both are 1-line).
3. **Spliced-line finder idiom ×2** — the 4-line `next(line.strip() …)`
   comprehension exists at :1726 (surface meta `midline_spliced`) and
   :2067 (ladder `lad_rec["spliced_line"]`) verbatim modulo input name.
   vC demonstrates a `find_spliced_midline(text)` helper defined beside
   `midline_error` (net −4 lines): artifacts identical modulo volatile.
   **Optional** — a two-site idiom is borderline under the r67 bar; shown
   only because it's now duplicated where it wasn't before r68.

## Not deletions — audit negatives (checked, keep)

- No new runner: the ladder reuses `surface_run` verbatim (bounded-Popen
  record shape shared with the r66 surface arms); the only new fixture
  surface is the `--midline-offset-ms=N` parse (4 lines, GDScript
  `get_slice("=",1).to_int()`, default 80).
- `measured_window` incl. `lo_edge_ms`/`hi_edge_ms`/`bound_semantics` is
  the claim carrier (the measured bound IS the payload); per-rep records
  are the evidence rows. Convention, keep.
- `mixed_offsets`/`reps_landed` are consumed by the strict-threshold gate;
  not decoration.
- Fixture doc comment matches the r66 arm-header convention.
- Malformed-offset behavior noted as data: `--midline-offset-ms=abc` →
  `to_int()` → 0 → fabricates (cannot fake a *miss*); a negative offset →
  malformed `sleep` → no write → a missed cell with `write_ppid=None`,
  which `ladder_all_writes_pre_death` would flag. Fail-closed against the
  fabrication claim either way. Unreachable from the declared ladder.
- Resolution note (not a defect): the declared ladder omits 200ms, so the
  tracked `hi_edge_ms` reads 240 while the author's instrumented spike
  places the edge at ~197-198ms nominal (`bound_semantics` discloses the
  ~2.5ms spawn-latency offset). The declared sweep is verbatim; a 200 rung
  is a follow-up refinement, not missing machinery.

## Evidence paths (all host-resolvable)

- `corpus/live/r68-simplifier/runs-landed/20261014T112132992259Z/` —
  flagless landed PASS 88/88; surface row 34/34.
- `corpus/live/r68-simplifier/runs-landed/20261014T112415928385Z/` —
  both-flag landed PASS 90/90 + `midlineforge-ladder-verdicts.json` +
  `stream-attribution-verdicts.json` (24/24 discriminations, clause map
  as above).
- `corpus/live/r68-simplifier/battery-landed{,-flagged}.stdout`,
  `*-exit.txt` — EXIT=0 ×2.
- `corpus/live/r68-simplifier/field-diff-{flagless,flagged}.txt` —
  field_diff.py vs `r68-baseline` runs `20261014T104854073132Z` /
  `20261014T105014927352Z` (pre-land bytes, sha-matched HEAD blobs).
- `corpus/live/r68-simplifier/stream-artifact-stability.txt` —
  post-strip artifact equality vs baseline.
- `corpus/live/r68-simplifier/mirror_truth.py` + `mirror-truth.txt` —
  AST-extracted matcher fidelity, 0/132 mismatches.
- `corpus/live/r68-simplifier/del-measure/` — vA/vB/vC variant fixtures +
  `v?-runs/` receipts + `variant-verdicts.txt` (all 90/90, identical
  windows, single-key structural diff for vB only).
- `corpus/live/r68-simplifier/{run_battery.pre-author.py,
  descendant_pipe_probe.pre-author.gd, pre-author-sha256.txt,
  landed-sha256.txt, landed-runner.diff, landed-fixture.diff}` —
  pre/post snapshots (pre == `1101cb3` blobs; landed == `f754546` blobs).
- Caller analysis: no `lsp` device in this seat's surface and no Python
  language server on this host (clangd only — same as r66/r67 seats);
  disclosed literal fallback: whole-file textual census + AST extraction.
  For the two code-level candidates the scopes are block-local (a dead
  conditional inside `divergent_clause`; a dict key inside
  `ladder_payload`) and the file carries no dynamic name access
  (`getattr`/`locals`/`exec`/`eval` absent), so the textual count is
  exhaustive.

## Tradeoffs

- Accepted `reps=3` and all six rungs as the declared sweep; noted that
  only the gates' *edges* (0/240) and continuity (80) are gate-pinned —
  40/120/160 are the contiguity witnesses that make "[lo,hi)" a measured
  interval rather than two edge samples. Deleting them would be a spec
  regression, not a weight win.
- Accepted the mirror pair as the smallest faithful attribution path —
  byte-fidelity proven against the real matchers rather than assumed from
  reading.
- The two deletion flags are genuinely zero-weight (3 lines total); both
  are Pareto-fine either way — the `exit` tautology arguably reads as
  executable documentation of "cannot diverge", and `signature_gap_ms`
  is self-describing payload convention. Recommended, not required.
- The one real residue worth the author's call is the dead conditional:
  tracked unreachable code inside a measurement function.
