# Round 66 simplifier report — rejection-clause SURFACE map audit (host: devin)

Seat: simplifier (LEAF, audit-only — write scope is this report +
`corpus/live/r66-simplifier/`; tracked-file edits are author-owned).
Subject: the in-flight r66 author landing, audited as it landed —
`corpus/fixtures/descendant_pipe_probe.gd` (+65/−1) +
`corpus/fixtures/run_battery.py` (+500/−0), working-tree diff vs HEAD
`2efaae2`. Landed digests: `76d37ace…` (runner), `9ff5a9ae…` (fixture).
The fixture diff appeared mid-audit at 02:08 local, the runner block
(+500) at ~02:11; both audits below are against the final landed bytes.

## Verdict

**Minimal-expression bar MET.** All four new arms pin a distinct
clause-level fact; none duplicates the r65 flip mechanics. 34 new
discriminations: 32 keep, 2 borderline headline-restates — no true wash.
The r65-flagged `reparent_gate` trigger is now **fired at 6 copies** —
extraction is warranted and proven byte-identical end-to-end on this
host. One genuinely dead allowlist entry found (the census's blind spot):
`export_preset_missing` in the `expected_errors` map.

Deletions made: **none** (no tracked edit scope; shared tree carries only
the author's diff — verified `git status` shows exactly the two author
`M` entries plus seat scratch).

## Preserved contract — independently re-verified, not trust-relayed

- Own battery on the **landed** tree:
  `corpus/live/r66-simplifier/runs-author/20261014T051322328700Z/verdicts.json`
  → **PASS, 88 rows, 96 discriminations all True** (62 prior + 34 new);
  `battery-author-exit.txt` `EXIT=0`; stdout line
  `PASS error-clause surface meta`.
- Own battery on the **pre-author** tree (control):
  `runs/20261014T050503947994Z/verdicts.json` → PASS, 87 rows, 62
  discriminations all True, `EXIT=0`.
- Field-diff landed vs baseline (pid/stamp/ASLR/elapsed-normalized,
  `field-diff-author.txt`): **shared=87, new_only=[probe_error_clause_
  surface], base_only=[]**. Only two rows differ, both expected:
  - `crash_spontaneous_sigabrt.output` — ASLR load addresses (frame
    offsets identical).
  - `probe_descendant_error_spoof` genuine-arm records — the `push_error`
    backtrace `at:` citation moved `descendant_pipe_probe.gd:84` → `:125`
    because the +65 fixture grew above it. Provenance-only (the line is
    inside `provenance_only_line_diff`); all classification-visible
    fields and every verdict identical. Not a regression — inherent to
    any fixture edit above :84 and correctly classified provenance.

## Per-arm audit — distinct clause-level facts (the brief's bar)

| arm | clause fact pinned | dup of r65 flip? |
|---|---|---|
| `--spawn-allowforge` | (a) allowlist-as-preemptor: identical captured bytes reject under `()`, absorbed under the matching entry, rejected under a foreign entry | No — same reparent-gate chassis as errforge but asserts the *opposite* verdict modulo allowlist |
| `--spawn-splitforge` | (c) newline-split evasion: `ERR\n`+`OR:` bytes captured, zero lines contain `ERROR:`, merged scan accepts | No — new multi-write `printf` mechanic |
| `--spawn-seamforge` | (c) cross-stream fabrication: unterminated stdout tail + stderr head → merged line exists in neither stream | No — new seam mechanic |
| `--spawn-midlineforge` | dual-clause corruption: mid-signature splice fabricates the ERROR line AND destroys the signature substring; `write_ppid==godot_pid` (only pre-death provenance arm in the family) | No — live-spawn, not gated |

Measured on the author's own receipt
(`corpus/live/r66-author/runs/20261014T051140112142Z/verdicts.json`):
`allowforge inner=False` (bare), `splitforge inner=True` (evaded),
`seamforge inner=False` (fabricated), `midline inner=False` +
`write_ppid==godot_pid` + `signature_observed=False` — all four landed
as declared. `shape_matrix` 9 cells all expected.

## reparent_gate extraction — trigger fired, extraction WARRANTED

- **Count:** the `while read -r _ _ _ pp _ < /proc/self/stat … done; `
  gate literal is now **6 copies** (`descendant_pipe_probe.gd:134,141,
  145,148,151,154` landed numbering) — 3 old + allowforge + splitforge +
  seamforge. My r65 trigger was "a 4th reparent-gated arm → extract";
  the author's three gated arms blew past it.
- **Proof (engine-verified):** `argv_proof.gd` reconstructs old-literal
  and `reparent_gate + …` argv for all 8 gated-arm variants under real
  Godot 4.7.2 — **all 8 byte-identical** (`argv-proof.stdout`,
  `ARGV_PROOF PASS`, per-arm sha256 printed).
- **End-to-end on the pre-author tree:** shadow fixture with the 3-copy
  extraction, full battery `runs-extracted/20261014T050739566712Z` →
  PASS 87; normalized field-diff vs baseline — zero semantic drift
  (`field-diff-extracted-normalized.txt`: residual diffs are ASLR hex,
  pids, interleave ordering, float jitter only).
- **On the author's arms:** extracted shadow fixture smoke —
  `--spawn-seamforge` produced the fabricated seam line +
  `write_ppid=1573` post-death (`seamforge-extracted-smoke.stdout`);
  `--spawn-midlineforge` produced the mid-signature splice with
  `write_ppid==godot_pid` (`midline-extracted-smoke.stdout`).
- **Deliverable:** `reparent-gate-extraction.patch` (+2/−6 lines net,
  ~460 chars lighter, single gate authority). The midline arm's
  single-shot `read` (:159) is a different primitive — **excluded**, stays
  literal. Keep/drop: **extract the 6 while-gate copies now**; the
  greppability argument that deferred it at 3 copies does not survive 6.

## Deletion candidates found

1. **`expected_errors["export_preset_missing"]` (run_battery.py:441) —
   DEAD ENTRY, delete.** Structurally unreachable: `execute()` sets
   `passed` for `__godot_export_missing__` at :348 (via `classify_export`,
   whose allowlist is the inline `(evidence,)` at :346); the dict lookup
   only runs under `if passed is None` (:402) — never true for that row.
   Confirmed three ways: (a) control-flow: `passed` is a bool before the
   lookup; (b) the author's own `record["expected_errors"]` carry shows
   the row shipping `[]` in the captured receipt; (c) the author's census
   reports `rows_with_expected_errors: 39` while the map holds 40
   non-empty value-entries — the delta is exactly this ghost. It looks
   load-bearing (its entry text matches the row's error line) — that is
   precisely why it is a simplifier find: the output-level census cannot
   see an entry that is never consulted. Deleting it is zero-behavior:
   `.get("export_preset_missing")` is never issued. This is the one real
   dead-entry find of the round — recommend deleting the line, or a
   comment marking it inert if provenance is preferred.
2. **`surface_allowed_error` (author block) — verbatim mirror of the
   nested `allowed_error` inside `classify_process` (:163-173).**
   Whitespace-normalized bodies are byte-identical (AST-verified).
   Recommended consolidation: hoist `allowed_error` to `main()`-level
   sibling of `classify_process` (closure-free pure def — provably
   identical semantics), letting both the classifier and the census call
   the single real function — deletes ~14 mirror lines and the
   drift-risk. Keep/drop: **recommended candidate**; the mirror is
   defensible only as zero-churn on the pinned classifier, and the
   author's `census_bare_classifier_consistent` discrimination does
   re-verify verdicts through the real path — so deferring is also
   defensible this round.
3. **`surface_signature` (run_battery.py:1583) — 7th named copy of the
   marker literal.** `surface_signature = errforge_signature` (:1135,
   same scope, already defined) is a free alias — micro-candidate.
4. **r65 micro-carryover, status update:**
   - `hold_descendant_orphaned_alive`, `gate_error_axis_timing_split`
     wash discriminations — **now pinned, keep**: the new
     `prior_meta_rows_stable_29_discriminations` discrimination asserts
     `len(discriminations) == 29`; removing the two wash keys would break
     the new anchor. The stability anchor converted wash into
     load-bearing-by-count — noted as coupling, not a drop candidate.
   - `ERRFORGE_ERROR := "ERROR: " + ERRFORGE_ERROR_BODY` fold — still
     unapplied, still micro.
   - 3 explicit-empty `expected_errors` tuples (:424,:426,:430) —
     no-op keys; keep as documented "considered, empty" rows (their
     presence now makes the census's empty-vs-missing distinction
     visible in records).
   - Marker literal total: 7 occurrences; `errforge_signature` at :1135
     is itself a literal (not the `= gate_marker` alias my r65 report
     described — corrected).

## Keep/drop per remaining element

- **KEEP `surface_run` fork** (normalized similarity 0.748 vs
  `errforge_run`): second copy of the communicate-bound family — my r65
  consolidation trigger is third-copy; also the fork carries real deltas
  (parameterized `ppid_token`, `(record, text)` return, no
  banner/stripped fields). Same verdict for **`surface_split_run`**
  (0.653 vs `split_errforge_run`, second copy). Revisit if a third
  bounded-Popen or split runner lands.
- **KEEP all 34 discriminations** except the 2 borderline below; each
  pins a distinct clause-level fact — notably `splitforge_contiguous_
  twin_rejects` (sole-cause control: same bytes joined → rejects),
  `seamforge_line_in_neither_stream` (the fabrication proof),
  `midlineforge_counterfactual_defeated` (strip-error still rejects →
  dual-clause), `midlineforge_write_pre_death` (new provenance sign).
- **BORDERLINE `surface_verdicts_follow_merged_line_presence`** — pure
  re-conjunction of five sibling atoms (the claim expressed atomically,
  same status as r65's `gate_does_not_reject…`). Keep or drop loses
  nothing.
- **BORDERLINE `detached_control_row_still_passes`** — second in-file
  copy of the ef-block anchor (reuses the shared `detached` var);
  self-containedness vs duplication. Third copy would warrant a helper.
- **KEEP `expected_errors = ()` + `record["expected_errors"]`** (+2) —
  turns the per-row allowlist into carried data; required by the census
  and incidentally what exposes finding #1.
- **KEEP `prior_meta_rows_stable_29_discriminations`** — the declared
  "stable" requirement made a gated tripwire (see coupling note above).

## Evidence paths (all host-resolvable)

- `corpus/live/r66-simplifier/runs-author/20261014T051322328700Z/
  verdicts.json` (landed: PASS 88, 96 disc True), `runs/
  20261014T050503947994Z/` (baseline: PASS 87), `runs-extracted/
  20261014T050739566712Z/` (extraction: PASS 87).
- `battery*.stdout`, `battery*-exit.txt` (EXIT=0 ×3).
- `field-diff-author.txt`, `field-diff-extracted{,-normalized}.txt`,
  `argv-proof.stdout`, `reparent-gate-extraction.patch`,
  `seamforge-extracted-smoke.stdout`, `midline-extracted-smoke.stdout`.
- `allowlist-census.json`, `census-summary.txt` — independent census on
  my baseline run (0 output-level dead entries, 0 unadmitted error
  lines, shape histogram exact=33/comma-prefix=8/structured=0), agreeing
  with the author's in-run census (39 rows, dead=0).
- `pre-audit-sha256.txt` / `landed-sha256.txt` — before/after digests;
  `git status` shows only the author's two `M` files + seat scratch.
- Author receipt cross-checked: `corpus/live/r66-author/runs/
  20261014T051140112142Z/verdicts.json`.
- Caller analysis: no `lsp` device exists in this seat's surface and no
  language server answers these fixtures (Python/GDScript — same finding
  as r65-simplifier, r66-reviewer, r66-scout). Disclosed literal
  fallback: text search + AST extraction + runtime receipts; the
  `export_preset_missing` finding additionally carries a control-flow
  reachability proof, not grep absence.

## Tradeoffs

- Accepted the author's fork-of-fork structure (`surface_run`,
  `surface_split_run`): keeps r64/r65 pinned runners untouched; each is
  only the second of its family — consolidation is third-variant per my
  own standing trigger.
- Accepted the `allowed_error` mirror this round (zero classifier churn)
  while recommending the hoist — the integrity discriminations bound the
  drift risk to detectable.
- The `== 29` stability anchor now makes the two r65-wash discrimination
  keys load-bearing-by-count — cheapest to keep them; future ef-dict
  edits must update the anchor.
- The `export_preset_missing` ghost entry costs one line and a wrong
  mental model; deleting it tightens the map the author is building —
  the only deletion with a real upside this round.
- Stop rule hit: the next deletion would be the `surface_run` fork
  (~45 lines of plumbing) — that harms the pinned-record/audit axis for
  weight, so it stops here.
