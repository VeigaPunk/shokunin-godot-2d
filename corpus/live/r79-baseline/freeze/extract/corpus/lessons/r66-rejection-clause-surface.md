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
simplifier's `reparent_gate` extraction); non-author verifier `reports/round-66/r66-verifier.md`; report-last commit follows adjudication.
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
