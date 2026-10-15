# Round 66 critic report — rejection-clause surface map (host: devin)

Seat: critic, lane `game-dev-2d`. Target: the author's uncommitted +565/−0
diff in `~/Projects/shokunin/game-dev-2d-shokunin` (`corpus/fixtures/
run_battery.py` +500, `corpus/fixtures/descendant_pipe_probe.gd` +65/−1 —
four new meta arms + shape matrix + census). Attacked the landed working-tree
diff directly; all commands resolve on this host. My own probe copies/exec'd
the classifiers VERBATIM from the diff (`clause_probe.py` regex+dedent+exec),
so no re-implementation drift.

## Verdict on the declared claim — mechanism CONFIRMED, literal claim
## FALSIFIED at the clause boundary (fixable wording defect)

"the rejection clause's verdict is a pure function of merged-output line
presence modulo the allowlist" — the line-scan half is confirmed (all 34
author discriminations reproduce independently, below), but the clause has
two **whole-blob conjuncts** (`"SCRIPT ERROR:" not in output`,
`"Parse Error:" not in output`, run_battery.py:177) that consult neither
line presence nor the allowlist. They preempt the allowlist, and they
fabricate without any `ERROR:` line existing. Both measured on the
verbatim classifier:

- **CE-1a (blob clause preempts the allowlist):** line
  `ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected
  signature=FILE_NOT_FOUND, tail embeds Parse Error: injected` under the
  matching `,`-prefix entry: line-scan absorbs it (`startswith` ✓,
  `count("ERROR:")==1` ✓ — `Parse Error:` is case-distinct), so
  line-presence-mod-allowlist predicts PASS. Observed verdict: **FAIL**
  — the `Parse Error:` blob conjunct rejects anyway. The allowlist is not
  the clause's top preemptor; the true order is blob clauses (allowlist-
  immune) → per-line `ERROR:` scan (allowlist-gated). Attack (a)'s framing
  "the allowlist acts as the rejection clause's preemptor row" is wrong in
  ordering for the blob half of the clause.
- **CE-1b (fabrication without any error line):** seam splice
  `ends in Parse Err` (stdout tail) + `or: spliced\n` (stderr head) →
  merged contains zero `ERROR:` lines (`error_lines == []`) yet verdict
  **FAIL** — the blob clause fabricates independently of the line scan.
  The author's `seamforge` maps the `ERROR:`-line phantom only; the same
  concat seam fabricates the blob-substring phantoms too — a second
  fabrication channel "line presence" does not express.

Smallest safe correction: amend the claim to "a pure function of the merged
output's line-set modulo the allowlist, **plus two allowlist-immune
blob-substring conjuncts** (`SCRIPT ERROR:`, `Parse Error:`)". Optionally
one discrimination pinning blob-preemption
(`absorbed_line + ' Parse Error: tail' → False`). No mechanism change; not
a judge-reject — same class as r65's capture-precondition omission.

## CE-2 — the granularity note overgeneralizes split evasion (measured)

Author's `clause_granularity` field: "a newline-split SCRIPT/parse token
evades entirely". My matrix through the verbatim classifier (all outputs =
banner + signature + body):

| split shape | verdict |
|---|---|
| `ERR\nOR: x` / `ERROR\n: x` / `ERRO\nR: x` | evade (PASS) |
| `ERROR: head\ncontinued` / `prefix\nERROR: x` | **reject** — residual line keeps `ERROR:` |
| `SCRIPT ERR\nOR: x` (inside `ERROR:`) | evade |
| `SCR\nIPT ERROR: x` (inside `SCRIPT`) | **reject** — `IPT ERROR:` residual trips line clause |
| `SCRIPT \nERROR: x` | **reject** — same |
| `SCRIPT ERROR\n: x` | evade |
| `Parse Err\nor:` / `Par\nse Error:` / `Parse \nError:` | evade — `Error:` never matches case-sensitive `ERROR:` |

So a `SCRIPT ERROR:` emission split inside the `SCRIPT ` prefix still
rejects via the surviving `ERROR:` fragment; only splitting inside the
`ERROR:` token itself evades — while `Parse Error:` evades when split
anywhere that breaks `Error:` (case-sensitivity asymmetry). The note is
correct only for splits inside the reject token. Fixable: one clause in
the note, or two shape-matrix rows (`SCR\nIPT ERROR:` → False;
`Par\nse Error:` → True).

## Brief attacks (1)–(5), resolved against the landed diff

1. **Absorption is verdict-inert AND record-faithful** — the author's own
   `allowforge_forged_error_captured` asserts `error_lines ==
   [allowforge_error]`; my runs confirm the absorbed line remains in
   `error_lines` and `output_lines` (cls under `()`=False, under matching
   entry=True, under foreign=False, 3/3). The forged emission stays
   auditable in the record. No defect — "absorbed" is verdict-level only.
2. Evasion is **not total** — see CE-2 matrix (residual-fragment backstop).
3. **Fabrication needs no child cooperation** — author's `seamforge` and
   my independent real-pipe arm both fabricate with BOTH halves authored
   post-death by one descendant holding both fds (`write_ppid=1573` =
   subreaper ≠ `godot_pid`, child output line-clean, 3/3). Confirmed.
   Methodological nit: author's `seamforge_line_in_neither_stream`
   evidence is a **second invocation** (`surface_split_run`); my harness
   captures stdout/stderr/merged on one run — stream-faithfulness on the
   same capture is tighter (same-write determinism makes this cosmetic).
4. **Double-sided batching composes in one record** (unmapped edge, not a
   falsification — the claim is existential per-direction). Measured: one
   post-death descendant writes `ERR\nOR: real` (evades) while splicing an
   un-allowlisted phantom (record FAILs on the phantom while the real
   emission is invisible), **or** splices an allowlist-shaped phantom —
   `stdout "ERROR"` + `stderr ": SAVE EXPECTED NEGATIVE…"` → verdict
   **PASS** with a real error emission escaped AND a fabricated line
   absorbed. Verdict-neutral double-forge: the record is twice-forged and
   the verdict agrees with a clean record.
5. **Census is per-run emission-presence, honestly named `dead_in_run`**
   — but that is not the declared axis-move's "no reachable child output
   can trip". My reachability runs (real Godot invocations): all 6
   grep-absent allowlist entries ARE emitted verbatim — `Can't change to
   a null scene…` and `Invalid export preset name: Missing preset.` are
   **engine-emitted**; the four camera entries are **format-constructed**
   (`"...within %s boundary"`). `SCRIPT ERROR:` fires on a runtime error
   (`SCRIPT ERROR: Invalid call. Nonexistent function … in base 'Nil'.`);
   `Parse Error:` fires on a syntax error (`SCRIPT ERROR: Parse Error:
   Unexpected "Indent" in class body.` + `ERROR: Failed to load script…`).
   So grep-absence is invalid deadness evidence and per-run absence is
   weaker still — reachable-but-untriggered. Author's run: `dead_entry_
   count=0`, blob clauses at 0 occurrences — consistent. Defect is only
   latent if the report/scorecard upgrades `dead_in_run` to "unreachable".

## Independent reproduction (not trusted from author receipts)

- Row stability: 8-field tuple diff (case/script/flags/expected_exit/
  actual_exit/signature/verdict/error) of author's run
  `corpus/live/r66-author/runs/20261014T051140112142Z/verdicts.json` (88
  rows) vs r66-baseline receipt `corpus/live/r66-baseline/runs/
  20261014T050234068765Z/verdicts.json` (87 rows) → **87 common, 0
  mismatches, 1 new row** (`probe_error_clause_surface` PASS).
- Author's own run `…T051301624764Z` (99 rows): surface probe PASS,
  **34/34 discriminations True**, error_spoof 29/29 (HEAD already carried
  29 — r65 boundary added one; the diff leaves `ef_discriminations`
  untouched).
- My re-run of all four fixture arms through verbatim-extracted
  `classify_process` + own bounded Popens, 3 reps each
  (`author-arms-results.json`): allowforge rejects()/foreign, absorbs
  matching; splitforge evades (`error_lines=[]`, cls True); seamforge
  fabricates post-death (`wppid=1573≠gpid`, `stdout_tail` unterminated,
  `stderr_head` `:`-led, same-run streams); midlineforge splices mid-
  signature pre-death (`wppid==gpid`, signature destroyed, cls False).
- My parallel fixture (`critic_surface_probe.gd`) adds the same-run
  descendant-only splice (3/3) and the allowlisted-phantom splice:
  `cls()`=False vs `cls(SAVE_ALLOW)`=**True** on real pipes — fabricated
  AND verdict-inert (`realpipe-results.json`).

## Minor observations (non-blocking)

- `surface_allowed_error` is a hand-mirrored copy of the nested
  `allowed_error` — self-flagged in a comment, verdicts re-derived via the
  real classifier; still a drift point if the nested fn ever changes.
- `midlineforge` is timing-shaped: descendant writes ~80ms into a 200ms
  signature gap (~120ms margin); a loaded host could push the splice past
  the gap → discrimination flake. `write_ppid==godot_pid` has a µs TOCTOU
  (stat read precedes write); the destroyed signature corroborates
  mid-gap timing anyway.
- The two blob clauses are **shadowed** by the line clause for
  `SCRIPT ERROR:` (any occurrence contains `ERROR:`) but **independent**
  for `Parse Error:` (case-distinct) — that's exactly why CE-1a/b use the
  Parse channel. Under the current allowlist map, no entry contains either
  blob token, so the clauses never rescue — they only independently reject.
- `record["expected_errors"]` added to every CASES row is additive; the
  r65 7/8-field stability tuples don't cover it (fine — additive schema).

## Fixable defect vs tradeoff

All 34 discriminations reproduce; the mechanism and its measured edges are
sound. Defects are claim/map precision: (CE-1) the falsifiable claim omits
the two blob conjuncts that bypass both line-presence and the allowlist;
(CE-2) the granularity note overstates which splits evade; (attack-4
composition edge and census-reachability scoping are unmapped/unstated, not
false). **Smallest safe correction:** reword the bounded_claim + granularity
note as above; optionally add three discrimination cells
(`Parse Error:`-tail-on-absorbed-line → False, seam `Parse Err`+`or:` →
False, `SCR\nIPT ERROR:` → False). Nothing here is judge-reject material.

## Files written (inside brief scope only)

- report: `reports/round-66/r66-critic.md` (this file)
- scratch: `corpus/live/r66-critic/{clause_probe.py, clause-probe-results.json,
  realpipe_probe.py, realpipe-results.json, author_arms_probe.py,
  author-arms-results.json, reachability_probe.py, reachability-results.json,
  proj/{project.godot, critic_surface_probe.gd}, author_proj/, reach_proj/,
  reach_missing/, xdg/}`
