# Round 66 scribe — rejection-clause SURFACE lesson entry + LOG draft (host: devin)

Report+scratch seat. LEAF: no subagent dispatch, no tracked edits, no
commit/push/merge/rebase/stash/checkout, no delegation. Write scope honored:
this report + `corpus/live/r66-scribe/` only. Per dispatch instruction a
prior instance of this seat died mid-run; I **verified and extended** the
existing scratch rather than restarting — the 123-run matrix, driver, and
raw captures were complete at takeover; my work this pass was
re-derivation/audit of every reported number against the artifacts plus
source file:line re-verification on the now-committed tree (the r66 author
commit `cb84d0a` landed between scratch passes — see provenance).

**Scratch inventory** (all under `corpus/live/r66-scribe/`):

- `drive_surface.py` — sha256 `87ea0e50e217…`; `ast.get_source_segment`-
  extracts `run_process`/`classify_process`/`classify_streams`/
  `classify_audio_process` verbatim from BOTH the worktree
  `corpus/fixtures/run_battery.py` and the `HEAD:` blob, execs the
  worktree segments, runs 41 arms ×3 reps on real pipes.
- `surface-verdicts.json` — sha256 `77c45152543b…`; 123 records + boundary
  units + census payload (machine receipt for every claim below).
- `observations.md` — sha256 `84583b874088…`; commands + tables.
- `run-matrix.stdout` — sha256 `86d5e59c6eaa…`; all 123 per-rep lines.
- `desc/` 28 ppid-gated descendant scripts (shas recorded in payload);
  `raw/` 123 per-run merged captures; `proj/` fixture copy sha
  `9ff5a9ae5757…` (pre-commit worktree bytes — what the `g_*` Godot arms
  ran); `proj_committed/` copy sha `92a40d70e31d…` (= committed fixture at
  `cb84d0a`; diff vs `proj/` is ONLY the simplifier's `reparent_gate`
  extraction — gate string deduped into a var, emitted argv unchanged;
  verified by direct diff this pass).

**Verdict on the declared claim — CONVERGE on the mechanism; the literal
wording needs the critic's fix.** Claim: "the rejection clause's verdict
is a pure function of merged-output line presence modulo the allowlist —
forgeable in both directions (evasion and fabrication) by a post-death
descendant." Measured independently through the verbatim classifier on
real captured pipe bytes: both directions confirmed (evasion via
token-split, fabrication via concat-seam, each in-life AND post-death),
BUT "modulo the allowlist" is wrong scoping — the clause's two whole-blob
conjuncts (`"SCRIPT ERROR:" not in output`, `"Parse Error:" not in
output`, run_battery.py:177) are **allowlist-immune and preempt the
allowlist** (r66-critic CE-1a/CE-1b, reproduced by me on real pipes:
`syn_ce1a_parse_tail` → False under bare/matching/foreign allowlists;
`syn_ce1b_parse_seam` → False with `error_lines==0`). Corrected
formulation my data supports: *the verdict's output-derived conjuncts are
a pure function of merged captured BYTES — blob-substring tests first
(allowlist-immune), then the allowlist-gated per-line `ERROR:` scan —
forgeable in both directions at the merge seam, plus a third direction,
denial-of-verdict, via undecodable bytes.* "Post-death descendant" is
sufficient but not necessary: identical fabrication occurs on an in-life
stdout→stderr concat seam (`syn_seam_inlife`, `syn_seam_sig_inlife`) —
the mechanism is merge-geometry, not provenance.

## Baseline + mechanism read (extraction verified this pass)

- `corpus/fixtures/run_battery.py` sha256 `76d37ace4b0b…` — identical
  bytes in worktree and `HEAD:` blob at `cb84d0a` (pre-r66 blob at
  `414eb8e` was `cd4824cc1a01…`). Extracted segment sha256, HEAD↔worktree
  all equal: `run_process 88728b2303f6`, `classify_process 749fa0607e77`,
  `classify_streams a886968fd3ac`, `classify_audio_process 3a6bc0e831a7`
  — the classifiers measured are byte-identical to the r65-verified blob.
- Clause inventory (`classify_process` :160–177): conjunction of
  `code==expected_exit` ∧ `error is None` ∧ `signature in output` ∧
  `not unrelated_errors` ∧ `"SCRIPT ERROR:" not in output` ∧
  `"Parse Error:" not in output`. `unrelated_errors` = any splitline
  containing `ERROR:` after per-line `allowed_error` filtering (exact /
  `,`-prefix+`count("ERROR:")==1` / structured `chain incomplete` forms,
  :168–171). The blob tests are whole-string `in` checks — no line
  structure, no allowlist consultation.
- `run_process` (:149–158): single `subprocess.run(capture_output=True,
  text=True)` — merged verdict input is `stdout + stderr` concat
  (classifier reads one string); `UnicodeDecodeError` propagates.
- Descendant provenance: every gated forged write carried
  `write_ppid=1573` (this host's `systemd --user` subreaper,
  `/proc/1573/comm` = `systemd` — re-verified) ≠ child pid.

## Measured (123 runs, real pipes, verbatim classifier — every arm 3/3 stable)

| arm | verdicts (bare / matching / foreign) | finding |
|---|---|---|
| syn_genuine | True | control |
| syn_self_error | False | genuine-error control |
| syn_allowforge_exact, _exact_padded, _comma_tail, _comma_atcomma, _comma2_tail, _structured | F / **T** / F | forged post-death `ERROR:` line verdict-inert iff its entry shape matches — allowlist = preemptor row for the line scan (a) |
| syn_allowforge_twin, _comma_dbl, _structured_missing | F / F / F | 1-char twin, `count==2` tail-forge, dropped conjunct all defeat absorption (b) |
| syn_script_forge, syn_parse_forge | F | dormant blob clauses fire on forged writes; `Parse Error:` line trips blob clause while evading the `ERROR:` line scan (case asymmetry) |
| syn_nlsplit_{lf,cr,vt,script} | True | `ERR<b>OR:` evades — forged bytes captured, no line trips (c-evade) |
| syn_nosplit_ctrl | False | contiguous control detects |
| syn_seam_inlife | False | `SEAM_ERROR:…` fabricated in merged output, present in NEITHER stream (`stdout_err=[]`, `stderr_err=[]`, merged=1) — no descendant needed |
| syn_seam_postdeath_{xfd,samefd} | False | same fabrication, gated post-death writes, `wppid=1573` |
| syn_seam_sig_{inlife,postdeath} | **True** | accept-axis dual: signature substring fabricated at the seam (`sig_in_stdout=False`,`sig_in_stderr=False`,`sig_in_merged=True`) — forged PASS no process emitted |
| syn_seam_script | False | `TAIL_SCRIPT `+`ERROR:…` fabricates the `SCRIPT ERROR:` blob clause at the seam |
| syn_midline | False (+sig destroyed) | pre-death splice corrupts BOTH clauses; stripped counterfactual still False |
| syn_decode_{inlife,postdeath} | **UnicodeDecodeError escapes** | `\xff\xfe` write → no verdict produced at all — denial-of-verdict |
| syn_ce1a_parse_tail | F / F / F | comma-entry absorbs line at scan level yet `Parse Error:` blob conjunct vetoes — allowlist NOT the clause's top preemptor (CE-1a reproduced live) |
| syn_ce1b_parse_seam | False, errln=0 | seam-fabricated `Parse Error:` rejects with ZERO `ERROR:` lines — blob channel independent of line scan (CE-1b reproduced live) |
| syn_ce2_{scr_ipt,script_sp,error_headsplit} | False | residual `ERROR:`-bearing fragments still reject — evasion bounded (CE-2 backstop) |
| syn_ce2_parse_split | True | `Parse Err\nor:` evades — `Error:` case-distinct from `ERROR:` |
| syn_double_forge | F / **T** / F | ONE post-death descendant: real `ERR\nOR:` evades + seam-fabricated allowlist-shaped phantom absorbs → record twice-forged, verdict PASS under matching entry (critic attack-4 reproduced live) |
| g_genuine | True | real Godot 4.7.2 headless control |
| g_errforge_release | False | r65 reground: post-death un-allowlisted error flips clean record |
| g_emit_errforge | False | genuine-error control (engine `push_error` path) |
| g_allowforge | F / **T** / F | author's arm through my independent extraction — same three-way verdict |
| g_splitforge | True | newline-split evasion on real engine pipes |
| g_seamforge | False | merged `…tail ends in ERROR: SEAMFORGE phantom…` line absent from BOTH streams (per-stream captures empty of it) |
| g_midlineforge | False (+sig destroyed) | pre-death mid-signature splice, `wppid==godot_pid` |

### Boundary units (verbatim classifier, synthetic text)

- `ERR<b>OR:` evades for ALL 11 `splitlines` boundaries (`\n \r \r\n \v
  \f \x1c \x1d \x1e \x85 \u2028 \u2029`), halves captured each.
- `\x1f` (unit separator): NOT a splitlines boundary, still breaks
  `ERROR:` contiguity → single line, True — evasion without a split.
- Blob-equivalence: `p in blob` ≡ `any(p in line)` for newline-free
  `SCRIPT ERROR:`/`Parse Error:` — line-equivalent by coincidence of
  pattern shape, not construction; but only the line scan is
  allowlist-gated, so the equivalence is verdict-asymmetric.
- `"ERROR:" in "SCRIPT ERROR: x"` → True: a SCRIPT ERROR line trips the
  line scan AND its blob clause; the allowlist can clear the line-scan
  hit but never the blob hit.
- lowercase `error:`/`Error:` lines evade the case-sensitive scan
  entirely and are un-allowlistable shapes.

### Dead-entry census (independent replay, receipt-corroborated)

Replayed verbatim `allowed_error` over the author's own 99-row PASS
receipt `corpus/live/r66-author/runs/20261014T051301624764Z/
verdicts.json` (rows now carry `expected_errors`):

- 39 rows carry non-empty allowlists, **40 entries total** (32 exact, 8
  `,`-prefix); every entry matched ≥1 captured line →
  `dead_entries_in_run: []` — converges with the author's in-run census
  (`dead_entry_count: 0`).
- Match-branch census: 33 hits via `exact`, 7 via `comma_prefix`.
  `save_process_missing`'s `,`-entry matched via the EXACT branch (real
  line ends at the comma) — its prefix arm is **latent**: absorbs `,X`
  forgeries, measured by `syn_allowforge_comma_{atcomma,tail}`.
- Consistency on all 39 rows: `any_entry_matched == bare_rejects` and
  `allowlisted_passes == (verdict==PASS)` — zero disagreement.
- Clause hit counts across 99 rows: `SCRIPT ERROR:` 0, `Parse Error:` 0,
  `ERROR:`-lines 43, ObjectDB-leak 0 → the two blob clauses + audio leak
  clause are dormant in-corpus (firing measured on forged writes).

**Static dead/unreachable surfaces the in-run census cannot see**
(re-verified file:line this pass on committed `cb84d0a` bytes):

- `expected_errors["export_preset_missing"]` (:441) **unreachable** —
  `__godot_export_missing__` binds `passed` in the `elif` at :342–347
  (inline `(evidence,)` allowlist) before `if passed is None:` consults
  the dict; receipt shows the row's serialized `expected_errors=[]` while
  its output carries an `ERROR:` line absorbed by the elif's tuple.
- `classify_mutant`'s generic arm `("ERROR: " + evidence,)` (:368):
  computed then overwritten by the `mutant_broken_scene_route` /
  `mutant_level_collision_removed` overrides (:370/:374) on every
  reachable name — only two mutants are executed (:2047–2048). Dead store.
- `classify_streams`' entry-matching arms (`line_allowed` exact /
  `,`-prefix at :191–198): **sole call site** `run_battery.py:2219` passes
  `allowed_stderr=()` — the matching machinery is dead under current
  callers (the empty-allowlist reject-any-stderr-line behavior is live).
- `"SCRIPT ERROR:"/"Parse Error:" in output` re-check at :450: redundant
  second evaluation of conjuncts `classify_process` already ran on the
  same `output` — belt-and-suspenders, no distinct surface.
- 3 `()` dict keys (:424, :426, :430 — slider focus-restore rows):
  semantic placeholders, identical to `.get(name, ())` default.
- `crash_self_sigkill` (:97): deliberately no entry; SIGKILL yields no
  handler text — no-allowlist path exercised every run.

## Converge/diverge vs sibling seats

- **Author** (`cb84d0a` landed; receipt `20261014T051301624764Z`, 99 rows
  PASS): their `probe_error_clause_surface` reports 34/34
  discriminations; my independent driver reproduces all four arm
  behaviors through a SEPARATE extraction — allowforge F/T/F, splitforge
  True, seamforge False with per-stream absence, midlineforge
  False+sig-destroyed. CONVERGE.
- **Critic**: mechanism confirmed, literal wording falsified (blob
  conjuncts preempt allowlist) — I reproduce CE-1a and CE-1b live on real
  pipes, plus CE-2 residual-fragment backstops and attack-4 composite.
  CONVERGE (incl. the falsification — my verdict adopts it).
- **Reviewer**: `AUTHOR_ARMS_BEHAVE_AS_DECLARED`, 88/88 on the diff,
  34/34 meta, 87-prior-rows 0-mismatch; same segment shas. CONVERGE.
- **Boundary/scout**: overlap consistent (boundary ran the landed
  worktree diff; scout's map predicted the arm shapes verbatim). My adds:
  every shape on real pipes incl. accept-axis seam fabrication, decode
  hole live-fired through `run_process`, census replay on the author
  receipt + static unreachability findings.
- **Simplifier**: minimal-expression bar MET; the `reparent_gate`
  extraction it warranted is the ONLY diff between my measured fixture
  (`9ff5a9ae`) and committed (`92a40d70`) — verified argv-equivalent.
- Fixture byte convergence: `9ff5a9ae5757…` reported identically by
  scout and reviewer.

## Errata found in my own scratch notes (reported verbatim, not softened)

- `observations.md` cites "only two mutants exist (:1549-1551)" — actual
  execute sites are `:2047-2048` (overrides at `:370/:374`); :1549 sits
  inside the probe comment block.
- `observations.md` cites `classify_streams` call sites "~:1719/:2219" —
  sole call site is `:2219`; :1719 is `surface_classify` inside the meta
  probe (a `classify_process` wrapper, not a `classify_streams` call).
- `observations.md` describes the HEAD blob as `cd4824cc1a01…` — true for
  the pre-commit pass (vs `414eb8e`); the final run-matrix/JSON correctly
  records HEAD blob == worktree == `76d37ace…` post-`cb84d0a`. Both
  statements are consistent with the two-pass timeline.

---

## Draft A — lesson entry (proposed slot `corpus/lessons/r66-rejection-clause-surface.md`; final name/placement is parent's call)

````markdown
# R66 — rejection-clause SURFACE map: allowlist preemptor row, line-faithfulness gaps, dead-entry census (Godot 4.7.2 headless)

Sources: `reports/round-66/r66-{scout,author,critic,reviewer,simplifier,
boundary,baseline,scribe}.md`; `corpus/fixtures/run_battery.py` meta
`probe_error_clause_surface` + `corpus/fixtures/descendant_pipe_probe.gd`
`--spawn-{allowforge,splitforge,seamforge,midlineforge}` arms (work commit
`cb84d0a`; runner sha256 `76d37ace4b0b…`, committed fixture `92a40d70e31d…`);
author receipt `corpus/live/r66-author/runs/20261014T051301624764Z/
verdicts.json` (99 rows, PASS); scribe independent measurement
`corpus/live/r66-scribe/surface-verdicts.json` (sha256 `77c45152543b…`,
123 real-pipe runs + boundary units + census replay, driver
`87ea0e50e217…`, measured fixture `9ff5a9ae5757…` = committed modulo the
simplifier's `reparent_gate` extraction); report-last commit `[pending]`,
non-author verifier receipt `[pending]`.
Prior lessons this extends: `r63-signature-spoof-boundary.md` (accept-axis
origin-blindness), `r65-forged-rejection-dual.md` (reject-axis dual).

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python
`3.14.7`, Linux x86_64, `systemd --user` subreaper pid 1573; classifier
segments byte-identical HEAD↔worktree (`run_process 88728b23`,
`classify_process 749fa060`, `classify_streams a886968f`,
`classify_audio_process 3a6bc0e8`); verdicts driven through
`ast.get_source_segment`-extracted production functions on real captured
pipe bytes — never fed strings.

## Clause inventory (run_battery.py:160–177, :149–158)

`classify_process` ANDs six conjuncts over one merged `stdout + stderr`
string: `code==expected_exit` ∧ `error is None` ∧ `signature in output` ∧
`not unrelated_errors` ∧ `"SCRIPT ERROR:" not in output` ∧ `"Parse
Error:" not in output`. Only the middle three read output bytes. Two
channel shapes: (i) per-LINE `ERROR:` presence scan over
`output.splitlines()` with per-line allowlist exemption (`allowed_error`
forms: exact / `,`-prefix+`count("ERROR:")==1` / structured
`chain incomplete`, :168–171); (ii) whole-BLOB substring tests for
`SCRIPT ERROR:` and `Parse Error:` — line-agnostic AND allowlist-immune.
Evaluation order in effect: blob clauses → allowlist-gated line scan.
`run_process` is a single `capture_output=True` run; `UnicodeDecodeError`
propagates out of the verdict path entirely.

## Allowlist-as-preemptor row — measured, and bounded

A post-death descendant echoing a byte-exact allowlisted error is
VERDICT-INERT under the matching entry, rejected under `()` and under a
foreign entry (F/T/F, all entry shapes, syn + godot arms, `wppid=1573`).
The allowlist checks string equality, never origin or timing. Match-shape
gate geometry: `strip()` widens exact matching (padded twin absorbed);
`,`-prefix absorbs arbitrary tails AND a line ending AT the comma via the
exact branch; a second `ERROR:` in the tail defeats absorption
(`count==1` breakable); the structured form needs all conjuncts.
BOUND: the allowlist is the preemptor of the LINE SCAN ONLY — the two
blob conjuncts preempt the allowlist itself (allowlisted line carrying a
`Parse Error:` tail still rejects; allowlisted `SCRIPT ERROR:` line still
rejects; seam-fabricated `Parse Error:` rejects with ZERO `ERROR:`
lines). The r66 declared wording "the allowlist acts as the rejection
clause's preemptor row" is true of the line scan, false of the clause.

## Line-faithfulness gaps — both directions, plus a third

- EVASION: `ERR<b>OR:` evades the line-local scan for every `splitlines`
  boundary (`\n \r \r\n \v \f \x1c \x1d \x1e \x85 \u2028 \u2029`) and for
  `\x1f` without splitting at all; case variants (`Error:`/`error:`)
  evade unconditionally. Bounded by residuals: splits leaving an
  `ERROR:`-bearing fragment still reject (`SCR\nIPT ERROR:`,
  `SCRIPT \nERROR:`, `ERROR: head\nrest`); `SCRIPT ERR\nOR:` evades the
  blob clause; `Parse Err\nor:` evades by case asymmetry.
- FABRICATION: a stdout tail + stderr head (or same-fd post-death
  continuation) splices a reject line present in NEITHER stream —
  in-life (`SEAM_ERROR:…`, no descendant) and post-death
  (`wppid=1573`), incl. the blob clauses (`TAIL_SCRIPT `+`ERROR:…`) and
  `Parse Error:` (zero `ERROR:` lines). ACCEPT-AXIS DUAL: the signature
  substring fabricates identically at a seam — forged PASS no process
  emitted (`sig_in_stdout=False`, `sig_in_stderr=False`,
  `sig_in_merged=True`, verdict True). Mechanism is concat-seam
  geometry; post-death provenance is sufficient, not necessary.
- DENIAL-OF-VERDICT (third direction): a `\xff` write in-life or
  post-death raises `UnicodeDecodeError` through `run_process` — a
  descendant can prevent any verdict from existing.
- COMPOSITE (attack-4, measured): ONE post-death descendant splits a real
  error (`ERR\nOR:` evades) AND seam-fabricates an allowlist-shaped
  phantom (absorbed) — record twice-forged, verdict PASS under the
  matching entry.
- A pre-death mid-signature splice corrupts BOTH clauses at once
  (fabricated error line + destroyed signature substring).

## Dead-entry census

In-run (author receipt, replayed independently): 39 rows / 40
`expected_errors` entries; **zero dead in-run** — every entry matched a
captured line (33 exact-branch, 7 comma-prefix-branch hits;
`save_process_missing`'s `,` entry matched via exact — prefix arm latent
but live-measured to absorb `,X` forgeries). Clause counts over 99 rows:
`SCRIPT ERROR:` 0, `Parse Error:` 0, `ERROR:`-lines 43, ObjectDB-leak 0 —
blob clauses dormant in-corpus, fire only on forged writes.
Static dead surfaces (file:line, committed `cb84d0a`):
`expected_errors["export_preset_missing"]` :441 unreachable (elif :342
binds `passed` first); `classify_mutant` generic arm :368 dead store
(overridden :370/:374 for both executed mutants :2047–2048);
`classify_streams` entry-matching dead under sole caller
`allowed_stderr=()` (:2219); blob re-check :450 redundant; 3 `()` dict
placeholders (:424/:426/:430).

## Recheck conditions

(1) Any `run_process`/`classify_process` rewrite — merged concat +
presence scans are the whole mechanism. (2) If capture becomes
per-stream/per-writer, the merge gains a separator, or the scan gains
provenance/liveness. (3) If the allowlist match shapes or the
`count("ERROR:")==1` conjunct changes — every shape arm re-measures
cheaply. (4) If decoding changes (`text=True` errors policy) — the
denial-of-verdict hole is decode-bound. (5) Census drift: new CASES rows
with `expected_errors`, new mutants, any `export_preset_missing` reroute
— dead surfaces flip live silently. (6) Off this host/profile —
reparent target, pipe scheduling, splitlines table.

## Not established / retained UNKNOWNs

- Single host/profile; timings vary, verdict directions do not.
- `syn_decode_postdeath` write_ppid is not receipt-visible (no record
  exists) — post-death-ness is by gate construction.
- sh-descendant arms simulate pipe mechanics; Godot arms are the author's
  fixture arms verbatim.
- Census "reachable" is bounded to shipped fixtures; dead-code findings
  are static + receipt-corroborated, not execution-proof of
  unreachability under future callers.
- Whether any real engine emission can produce the `,`-prefix-tail or
  structured shapes organically is unmeasured — forgery value is
  symmetric either way.
````

---

## Draft B — LOG.md round-66 entry (draft; `[pending]` = fill from settled raw before commit)

```markdown
## Round 66 — devin host — depth: rejection-clause SURFACE map (allowlist preemptor, seam fabrication, dead-entry census)

- Declared: pin the r65 critic/boundary measured edges into tracked meta — allowlist-as-preemptor, breakable match shapes/count==1, newline-split evasion + splice fabrication, dead-entry census. Claim: rejection verdict = pure function of merged-output line presence modulo allowlist, forgeable both directions post-death.
- Wave `shokunin-train-20261014-w6`: reports `reports/round-66/r66-{baseline,scout,author,critic,reviewer,simplifier,boundary,scribe}.md` (+ verifier `[pending]`).
- Author `reports/round-66/r66-author.md`: fixture arms `--spawn-{allowforge,splitforge,seamforge,midlineforge}` + meta `probe_error_clause_surface` (34 discriminations); runner +500/−0, fixture +65/−1 then reparent_gate extraction; work commit `cb84d0a`; 88/88 battery incl. new meta, 87 prior rows 0-mismatch (reviewer).
- Measured (author 99-row PASS receipt + scribe 123-run independent real-pipe replay): allowlisted forged error verdict-inert F/T/F across all entry shapes; `ERR\nOR:` evades all 11 splitlines boundaries + `\x1f` unsplit; concat-seam fabricates reject lines present in neither stream — reject AND accept axes, in-life AND post-death; `\xff` write denies the verdict outright; dead-entry census 0/40 in-run + static dead surfaces (`export_preset_missing` dict entry unreachable, `classify_mutant` generic arm dead store, `classify_streams` allowlist machinery dead under `allowed_stderr=()`).
- Critic refinement absorbed (and reproduced by scribe): blob conjuncts `SCRIPT ERROR:`/`Parse Error:` preempt the allowlist and fabricate without any `ERROR:` line — literal claim wording falsified, mechanism confirmed; true order = blob clauses → allowlist-gated line scan.
- Per-axis verdicts `[pending adjudicator]`. Bounded: merge-geometry not provenance (in-life suffices); decode hole is denial-of-verdict; dead surfaces re-flip on future callers.
```

## Seat notes

- Exact commands + per-run evidence: `corpus/live/r66-scribe/observations.md`,
  `run-matrix.stdout`, `surface-verdicts.json`, `raw/` captures, `desc/` scripts.
- Provenance chain re-verified this pass: runner `76d37ace` (worktree == HEAD
  `cb84d0a` == measured), pre-r66 blob `cd4824cc` at `414eb8e`; measured
  fixture `9ff5a9ae` vs committed `92a40d70` differ ONLY by the simplifier's
  `reparent_gate` dedup (diff inspected directly; gate argv unchanged).
- Prior-instance state at takeover: driver + JSON + observations + all raw
  captures complete; `git status` shows the scratch partially swept into
  `cb84d0a` (tracked `desc/` + older `raw/` + driver, now `M`/added `??`) —
  normal scratch evolution, nothing rebased or rewritten by me.
- Orphan hygiene: token-scoped reaper SIGKILLs `R66S_`/`DESCENDANT_PIPE`
  tagged descendants at return; bounded `sleep` self-exits otherwise.
- Out of scope (untouched): tracked fixtures/runner/CASES/lessons/LOG/
  SCORECARD, all git mutations, sibling lanes, the `prymeagnt` worktree
  (read-only provenance check), any user/maintainer-visible action.
