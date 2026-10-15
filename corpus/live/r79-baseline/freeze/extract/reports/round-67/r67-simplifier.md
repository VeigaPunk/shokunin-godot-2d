# Round 67 simplifier report — per-channel divergence map audit (host: devin)

Seat: simplifier (LEAF, audit-only — write scope is this report +
`corpus/live/r67-simplifier/`; tracked-file edits are author-owned).
Subject: the landed r67 diff, commit `d44ba86` —
`corpus/fixtures/stream_attribution_probe.gd` (+58/−1) and
`corpus/fixtures/run_battery.py` (+265/−1), all inside the existing opt-in
`if args.probe_stream_attribution:` block (:2199). Landed digests:
runner sha256 `3d5b0721d582…`, fixture sha256 `dc0b0d5c5f44…`
(`landed-sha256.txt`). Pre-land runner sha was `76d37ace…`-era content
(md5 `0b2897bf…`, snapshot `run_battery.pre-author.py`).

## Verdict

**Minimal-expression bar MET.** All 7 new fixture arms and all 20 new
discriminations are load-bearing — each pins a distinct clause-level or
sole-cause fact; zero wash. The harness is minimal: it reuses the
in-block `run_process_streams` (no 4th split-runner fork) and the r66
record conventions without copying the r66 runners. One dead binding
found: `sd_sig_head` (run_battery.py:2278) — never referenced;
delete-and-measure receipt proves byte-identical behavior.

Deletions made: **none** (no tracked edit scope; shared tree carries only
the author's commit — `git status` shows seat scratch + `reports/`
untracked dirs only, zero `M`/`D` rows).

## Preserved contract — independently re-verified on the landed tree

- Flagless battery (mine):
  `python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
  corpus/live/r67-simplifier/runs-landed` → **exit 0**
  (`battery-landed-exit.txt`), `runs-landed/20261014T100135501917Z/
  verdicts.json` **PASS 88/88**; `probe_error_clause_surface` row still
  carries **34 discriminations, all True** — the claim's "88/88 + 34/34
  green" conditions hold on the landed bytes.
- Opt-in leg (mine): same command + `--probe-stream-attribution` →
  **exit 0**, `runs-landed/20261014T100512403308Z/verdicts.json`
  **PASS 89/89** (88 + `probe_stream_attribution`), payload
  `stream-attribution-verdicts.json` verdict **PASS**, **20/20
  discriminations True**, divergence table 9 rows: 7 divergent + 2
  concordant, exactly the set `divergence_rows_match_expectation` pins.
- Cross-receipt byte equality vs author's own flagged run
  (`corpus/live/r67-author/runs/20261014T095910487678Z/`): all 7 arms'
  `raw_stdout`/`raw_stderr` are **byte-identical** to my independent
  captures; discrimination dicts and divergence tables identical.
  Deterministic byte placement as bounded_claimed.
- Field-diff landed-vs-baseline (`field_diff.py` on r67-baseline
  `20261014T094859374505Z` vs my landed run; `field-diff-landed.txt`):
  **shared=88, new_only=[], base_only=[], verdict_diffs=[]**. Residual
  field diffs are provenance only — `command[3]` scratch paths (frozen
  vs live seed dir) and `crash_spontaneous_sigabrt` ASLR load addresses
  (frame offsets identical). No semantic drift.
- Pre-land reference measurement (independent of the author's arm):
  `divergence_truth.py` execs `classify_process`/`classify_streams`
  extracted verbatim via AST from the landed file, 20 synthetic stream
  pairs (`divergence-truth-preland.json`) — predicted every divergent
  cell the arm later measured, plus the stderr-strictness and
  structured-entry cells the critic falsification named. The author's
  table matches it cell-for-cell.

## Per-arm audit — each arm pins a distinct fact (the brief's bar)

| arm (fixture flag) | measured (mine) | fact pinned | load-bearing? |
|---|---|---|---|
| `--stdout-error` | merged=F, streams=T | **headline**: stdout ERROR: absorbed — stdout is never error-scanned | yes — declared claim core |
| `--stderr-error` | F/F bare; T/T exact entry; F/F foreign | concordant control: same bytes on stderr reject both; entry absorbs symmetric — isolates channel placement as the axis | yes — the claim's "stderr behaves differently" control |
| `--stderr-structured` | merged=T, streams=F under `"ERROR: chain incomplete"` | allowlist's per-stream match asymmetry: structured matcher exists only in merged `allowed_error` (:168-171), not in `line_allowed` (:192-198) | yes — declared "allowlist's per-stream match" pin |
| `--sig-on-stderr` | merged=T, streams=F | signature channel: merged accepts anywhere, streams requires stdout | yes — declared signature-axis pin |
| `--seam-error` | merged=F, streams=T (head allowlisted) | ERROR: seam fabrication is merged-only; streams absorbs iff stderr head allowlisted | yes — declared "per-stream seam positions" |
| `--seam-script` | merged=F, streams=T | blob clause (`SCRIPT ERROR:`) seam-fabrication — a third clause on the same seam | yes — extends beyond literal ERROR:/signature text but maps the documented surface (critic row J); dropping it leaves the blob-clause seam unmapped |
| `--seam-sig` | merged=T, streams=F | signature seam: contiguous only in merged | yes — declared seam + signature pins |

Plus 2 zero-cost rows: `dual_classify` re-runs on the pre-existing
`stream_accept`/`stream_reject` captures — `stream_reject` turns out
divergent (non-`ERROR:` stderr line is invisible to merged, rejected by
the streams sweep) at no extra Godot run. Free coverage, keep.

## Delete-and-measure — every discrimination

20 discriminations (`sd_discriminations`, :2385-2502), each verified True
in my run. Semantic load-bearing check — removing each loses a fact no
sibling asserts:

- Sole-cause controls that make other pins attributional, not
  correlational: `stderr_error_foreign_entry_rejects_both` (absorption is
  entry-specific), `structured_bare_rejects_both` + `structured_exact_
  line_absorbs_both` (the entry shape, not the line, diverges),
  `sig_on_stderr_streams_rejects_solely_on_signature` (stderr fully
  allowlisted yet still FAIL → signature clause is the sole cause),
  `seam_error_streams_bare_rejects_stderr_strictness` (absorption came
  from the allowlisted head, not seam-invisibility).
- Evidence pins: `stdout_error_line_only_on_stdout`,
  `seam_error_line_in_neither_stream` (fabricated line absent from both
  streams — the fabrication proof).
- Map integrity: `divergence_rows_match_expectation` (set-exactness: the
  map IS these 7 divergent + 2 concordant rows), `accept_arm_concordant`
  (concordant baseline on a free row — weakest key but anchors the
  PASS/PASS cell and guards verdict drift; keep).
- Hygiene/binding: `all_divergence_arms_exit0_clean`,
  `all_divergence_arms_same_script` — standard battery convention.

Delete-and-measure consequence map: removing any arm unmaps its
discriminations and shrinks the exact-set pin; removing any
discrimination drops a distinct sole-cause or evidence pin. **0 of 20 are
wash.** The runtime deletion test below confirms the one true candidate.

## Harness minimality vs the r66 surface code

- **No new runner.** `streamdiv_arm` (:2294) calls the in-block
  `run_process_streams` (:2200) — the only primitive returning raw
  `(stdout, stderr, code, error)` — instead of forking a 4th
  separate-PIPE capture (`split_errforge_run` :1350, `surface_split_run`
  :1662 already exist as lines-only record builders).
- **Byte-level proof the lines-only records could not substitute**
  (this is the reuse question the brief asks): reconstructing
  `"\n".join(raw_stdout_lines)` re-terminates the unterminated stdout
  tail. On the real captured bytes —
  `seam_error`: merged F→**T** (fabricated line never forms);
  `seam_script`: F→**T**; `seam_sig`: T→**F** (fabricated signature
  never forms). `surface_split_run`/`split_errforge_run` keep only
  `*.splitlines()`, so reuse would silently falsify all three seam
  verdicts. `streamdiv_arm`'s raw-string fields are load-bearing, not
  duplication.
- **`dual_classify`** (:2281) is itself the consolidation — one
  12-line wrapper serving 15 call sites (2 pair reclass + 7 arms +
  6 allowlist reclass cells). No second convention created.
- Constants mirrored between `.gd` and the runner are cross-language
  assertion anchors (same convention as `STDOUT_MARKER`/`stdout_sig`) —
  necessary, not driftable-copy weight.
- Verdict wiring is a single-token edit (`meta_pass and sd_meta_ok`,
  :2536) — additive to the existing row; the diff's only deletion is
  that one line's old form. No new battery row, hence 88/88 flagless
  preserved by construction.
- Dead-name census over the new block: every `sd_*` binding has ≥2
  textual references except `sd_sig_head` (1 = its definition). Fixture
  side: all 8 `STREAMDIV_*` constants and all 7 flags are consumed.
- Revival note (weight-reducing, not weight-adding): `line_allowed`'s
  exact/`,`-prefix matcher (:192-198) was dead machinery under the sole
  pre-r67 caller (`allowed_stderr=()`, r66-scribe census finding) — the
  new arms now exercise it for real, resolving that dead-code entry by
  *use* rather than by new parallel machinery.

## Deletion candidates found

1. **`sd_sig_head` (run_battery.py:2278) — DEAD BINDING, delete.**
   Defined, never referenced (whole-file scan: 1 hit). Scope is a
   block-local variable; the file has no `getattr`/`locals()`/`exec`/
   `eval`, so the literal scan is exhaustive for it. Context suggests
   intent: sd5 pins its seam position via `stdout_tail_line ==
   sd_seam_tail and stderr_head_line == sd_seam_head`, but sd7's
   discrimination set never pins its seam positions — a naive
   `stdout_tail_line == sd_sig_head` pin would in fact be FALSE, because
   `stdout_tail_line` is `.strip()`ed (:2307) while `sd_sig_head` ends
   in the seam-significant trailing space. Byte-demonstrated on real
   captured bytes (`del-measure` + probe output): the correct pin would
   be `raw_stdout.endswith(sd_sig_head)` (True) with
   `stderr_head_line == sd_sig_tail` (True).
   **Delete-and-measure receipt:** scratch copy `del-measure/fixtures/
   run_battery.py` = landed bytes minus line 2278; full battery +
   `--probe-stream-attribution` → `del-measure/runs/
   20261014T101048333340Z/` **EXIT=0, 89/89 PASS**, probe payload
   byte-identical in every verdict field: same 20 discriminations all
   True, same 9-row divergence table, 0 row-verdict diffs vs the landed
   run. Deletion is provably zero-behavior.
   Alternative (author's call, not a weight issue): keep the constant
   and complete sd7's seam-position pin with the endswith form —
   symmetric with sd5. Either is admissible; as simplifier I recommend
   the deletion since `signature_in_*` flags already pin the mechanism.
2. **No other candidates.** Checked: `expected_exit`/`flags` record
   fields (provenance convention, carried by every sibling record);
   `sd_script_tail`/`sd_script_head` (consumed by `sd6_fabricated` +
   allowlist); `sd_pair_dual` (consumed by table + 3 discriminations);
   the `.gd` doc comment (lane convention, matches r66's arm-header
   style). The `elif` chain for `--seam-sig`/`--sig-on-stderr` is the
   minimal correct structure (both arms must suppress the plain
   `print(STDOUT_MARKER)`).

## Consolidation verdict

None warranted. The only forkable surfaces (`run_process_streams`,
`dual_classify`) were already reused/singular. A `streamdiv_arm` /
`surface_split_run` merge is disproven byte-level above. The declared
stop rule: the next deletion would be a discrimination or arm — every
one is load-bearing — so it stops at the one dead binding.

## Evidence paths (all host-resolvable)

- `corpus/live/r67-simplifier/runs-landed/20261014T100135501917Z/
  verdicts.json` — flagless landed PASS 88/88; surface row 34/34.
- `corpus/live/r67-simplifier/runs-landed/20261014T100512403308Z/` —
  flagged landed PASS 89/89 + `stream-attribution-verdicts.json`
  (20/20 discriminations, 9-row table).
- `corpus/live/r67-simplifier/battery-landed{,-stream}.stdout`,
  `*-exit.txt` — EXIT=0 ×2.
- `corpus/live/r67-simplifier/del-measure/` — sd_sig_head-deleted
  runner + `runs/20261014T101048333340Z/` receipts (89/89, identical
  payload semantics).
- `corpus/live/r67-simplifier/divergence_truth.py` +
  `divergence-truth-preland.json` — independent AST-extracted
  classifier truth table (pre-land prediction matching the landed arm).
- `corpus/live/r67-simplifier/field_diff.py` + `field-diff-landed.txt`,
  `landed-runner.diff`, `landed-fixture.diff`, `landed-sha256.txt`,
  `run_battery.pre-author.py` (pre-land snapshot, md5 `0b2897bf…`).
- Author receipts cross-checked:
  `corpus/live/r67-author/runs/20261014T095753034446Z/` (88/88),
  `…/20261014T095910487678Z/` (99/99 + artifact sha `d65608f9…`).
- Caller analysis: no `lsp` device in this seat's surface and no Python
  or GDScript language server answers on this host (clangd only;
  pyright/pylsp absent — same finding as r66 seats). Disclosed literal
  fallback: whole-file textual scan + AST name census; for the sole
  deletion candidate the scope is a single block-local variable and the
  file carries no dynamic name access, so the textual count is
  exhaustive in fact, not just in practice.

## Tradeoffs

- Accepted `seam_script` as beyond-literal-claim coverage: it pins the
  blob clause at the seam — part of the mapped surface the claim opens
  ("the divergence is documented but its contract is unmapped") and the
  critic's measured row J. Deleting it would unmap a real mechanism for
  ~8 lines of weight — wrong trade.
- Accepted 20 discrimination keys including the concordance anchors:
  the map's claim is exactness of the divergent SET, which needs both
  poles pinned.
- The one real residue is `sd_sig_head`: delete (1 line, proven
  zero-behavior) or complete the sd7 seam pin (symmetric coverage).
  Flagged for the author; either resolution is Pareto-fine.
