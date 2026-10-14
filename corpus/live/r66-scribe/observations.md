# r66-scribe observations — rejection-clause surface, independent derivation

Host: devin. Godot `4.7.2.stable.arch_linux.ed1daf0bf`, CPython 3.14.7,
Linux x86_64, `systemd --user` subreaper pid 1573.

## Commands run (exact)

```
mkdir -p corpus/live/r66-scribe/{raw,proj}
cp corpus/fixtures/project.godot corpus/fixtures/descendant_pipe_probe.gd \
   corpus/live/r66-scribe/proj/          # worktree bytes (r66 arms present)
python3 corpus/live/r66-scribe/drive_surface.py   # tee run-matrix.stdout
```

Driver: `ast.get_source_segment`-extracts `run_process`/`classify_process`/
`classify_streams`/`classify_audio_process` from BOTH the worktree
`run_battery.py` (sha256 `76d37ace4b0bbc3c…`, +500 r66 author diff present)
and the `HEAD:` blob (`cd4824cc1a01…`); exec'd the worktree segments.
Segment sha256 equality HEAD↔worktree: all four True — the classifiers the
arms measure are byte-identical to the committed verified blob
(`run_process 88728b23…`, `classify_process 749fa060…`, `classify_streams
a886968f…` per r66-reviewer).

## Measured (123 runs, real pipes, verbatim classifier)

Every arm 3/3 stable. Post-death provenance: `write_ppid=1573` (subreaper)
≠ child pid on every gated arm.

| arm | verdicts | note |
|---|---|---|
| syn_genuine ×3 | True | control |
| syn_self_error ×3 | False | genuine error control |
| syn_allowforge_exact ×3 | bare F / entry T / foreign F | exact-shape forged line verdict-inert iff entry given |
| syn_allowforge_exact_padded ×3 | same | strip() widens exact match — padded twin absorbed |
| syn_allowforge_twin ×3 | F/F/F | 1-char mutation (`JSON_PARSE_ERR0R`) rejects everywhere |
| syn_allowforge_comma_tail ×3 | F/T/F | `,`-prefix absorbs arbitrary tail (`…FILE_NOT_FOUND,forged_tail …`) |
| syn_allowforge_comma_dbl ×3 | F/F/F | second `ERROR:` in tail → count==2 → defeats absorption (conjunct breakable) |
| syn_allowforge_comma_atcomma ×3 | F/T/F | line ending AT the comma absorbed via the exact branch too |
| syn_allowforge_comma2_tail ×3 | F/T/F | button_activation entry, forged suffix absorbed |
| syn_allowforge_structured ×3 | F/T/F | `ERROR: chain incomplete collections=9 scene=SceneB:<Node#9> old_alive=false` absorbed |
| syn_allowforge_structured_missing ×3 | F/F/F | dropping `old_alive=false` defeats the structured entry |
| syn_script_forge ×3 | F | dormant `SCRIPT ERROR:` blob clause fires on forged write |
| syn_parse_forge ×3 | F | `Parse Error:` fires its clause; error_lines=0 — "Error:"≠"ERROR:" evades the LINE scan |
| syn_nlsplit_{lf,cr,vt} ×3 | True ×9 | `ERR<b>OR:` evades for b∈{\n,\r,\v}; forged bytes captured, no line trips |
| syn_nlsplit_script ×3 | True | `SCRIPT ERR\nOR:` evades the blob clause too (contiguity broken) |
| syn_nosplit_ctrl ×3 | False | contiguous control detects |
| syn_seam_inlife ×3 | False | fabricated `SEAM_ERROR:…` reject line in NEITHER stream; no descendant needed — merge-order artifact |
| syn_seam_postdeath_xfd ×3 | False | same fabrication, descendant stderr write post-death (wppid=1573) |
| syn_seam_postdeath_samefd ×3 | False | fabrication INSIDE stdout alone (same-fd continuation post-death) |
| syn_seam_sig_inlife ×3 | True | signature `…signa`+`ture` fabricated at concat seam — no process emitted it; accept-axis dual |
| syn_seam_sig_postdeath ×3 | True | post-death same-fd signature completion — forged PASS by byte splice |
| syn_seam_script ×3 | False | `TAIL_SCRIPT `+`ERROR:…` fabricates the `SCRIPT ERROR:` blob clause |
| syn_midline ×3 | False | pre-death splice (wppid==child): error line fabricated AND signature substring destroyed; stripped counterfactual still False |
| syn_decode_inlife ×3 | UnicodeDecodeError | `\xff\xfe` in-life — exception escapes run_process; NO verdict exists |
| syn_decode_postdeath ×3 | UnicodeDecodeError | same, post-death descendant write — a descendant can kill the verdict path entirely |
| syn_ce1a_parse_tail ×3 | F/F/F | comma-entry absorbs the line at scan level (startswith✓ count==1✓ — `Parse Error:` is case-distinct from `ERROR:`) yet `Parse Error:` blob conjunct vetoes — **the allowlist is NOT the clause's top preemptor** (critic CE-1a reproduced live) |
| syn_ce1b_parse_seam ×3 | False, errln=0 | `ends in Parse Err`+`or:…` seam → merged `Parse Error:` line with ZERO `ERROR:` lines — blob fabrication independent of the line scan (CE-1b reproduced live) |
| syn_ce2_scr_ipt ×3 | False | `SCR\nIPT ERROR:` leaves residual `IPT ERROR:` line — split inside `SCRIPT` prefix does NOT evade (CE-2 backstop) |
| syn_ce2_script_sp ×3 | False | `SCRIPT \nERROR:` residual `ERROR:` line rejects |
| syn_ce2_parse_split ×3 | True | `Parse Err\nor:` evades — `Error:` never matches case-sensitive `ERROR:` |
| syn_ce2_error_headsplit ×3 | False | `ERROR: head\nrest` — residual first line keeps `ERROR:` |
| syn_double_forge ×3 | bare F / SAVE-exact T / foreign F | ONE descendant post-death: real `ERR\nOR: real escaped error` EVADES + seam-fabricated `ERROR: SAVE EXPECTED…` phantom ABSORBED under the matching allowlist → record twice-forged, verdict PASS (critic attack-4 composite reproduced live) |
| g_genuine ×3 | True | real Godot control |
| g_errforge_release ×3 | False | r65 reground: post-death un-allowlisted error flips clean record |
| g_emit_errforge ×3 | False | genuine-error control, identical clause table to forged arm |
| g_allowforge ×3 | F/T/F | author's arm through my extraction: forged allowlisted line verdict-inert iff entry given |
| g_splitforge ×3 | True | newline-split evasion on real engine pipes |
| g_seamforge ×3 | False | `…tail ends in ERROR` + stderr `: SEAMFORGE phantom…` → fabricated merged line, absent in both streams |
| g_midlineforge ×3 | False | pre-death splice: sig destroyed + error fabricated (wppid==godot_pid) |

## Boundary units (verbatim classifier, synthetic)

- `ERR<b>OR:` evades for ALL 11 splitlines boundaries:
  `\n \r \r\n \x0b \x0c \x1c \x1d \x1e \x85 \u2028 \u2029` — verdict True,
  `halves_captured` True each.
- `\x1f` (unit separator): NOT a splitlines boundary but breaks `ERROR:`
  contiguity → single line, verdict True — evasion without a split.
- Blob-equivalence: `p in blob` == `any(p in line)` for newline-free
  `SCRIPT ERROR:`/`Parse Error:` — the blob clauses are line-equivalent
  by coincidence of pattern shape, not by construction.
- `"ERROR:" in "SCRIPT ERROR: x"` → True — a SCRIPT ERROR line trips BOTH
  the per-line scan and its blob clause; but the allowlist CANNOT preempt
  the blob clauses (allowlisted `SCRIPT ERROR:` line still → False).
- lowercase `error:`/`Error:` lines evade the case-sensitive `ERROR:` scan
  entirely (verdict True) and are un-allowlistable shapes.

## Dead-entry census (independent replay)

Receipt: `corpus/live/r66-author/runs/20261014T051301624764Z/verdicts.json`
(99 rows, PASS — the author's own full-flag run; records carry the new
`expected_errors` field). Verbatim `allowed_error` replayed per entry over
captured `output` lines:

- 39 rows carry non-empty allowlists; **every entry matched ≥1 captured
  line** → `dead_entries_in_run: []` — converges with the author's in-run
  census (`dead_entry_count: 0`) and my replay on the r65-baseline 97-row
  receipt (same result).
- Match-branch census: 33 hits via `exact`, 7 via `comma_prefix`.
  `save_process_missing`'s `,`-entry matched via the EXACT branch (real
  line ends at the comma) — its prefix arm is latent (absorbs `,X`
  forgeries; measured `syn_allowforge_comma_atcomma`+`_tail`).
- Consistency on all 39 rows: `any_entry_matched == bare_rejects` and
  `allowlisted_passes == (verdict==PASS)` — zero disagreement.
- Clause line counts across 99 rows: `SCRIPT ERROR:` 0, `Parse Error:` 0,
  `ERROR:`-lines 43, ObjectDB-leak 0 → the two blob clauses + the audio
  leak clause are dormant in-corpus; measured firing on forged writes.

### Static dead/unreachable surfaces the in-run census cannot see

- `expected_errors["export_preset_missing"]` (run_battery.py dict,
  ~:441 in worktree): **unreachable** — `__godot_export_missing__` rows
  bind `passed` in the `elif` branch (~:345-347, allowlist `(evidence,)`)
  before the `if passed is None:` dict is consulted; the author receipt
  shows the row's serialized `expected_errors=[]` while its output carries
  an `ERROR:` line absorbed by the elif's inline tuple. The dict entry is
  a dead duplicate — editing it would silently do nothing.
- `classify_mutant`'s generic arm `("ERROR: " + evidence,)` (~:367-368):
  computed then **overwritten** by the `mutant_broken_scene_route` /
  `mutant_level_collision_removed` overrides on every reachable name
  (only two mutants exist, :1549-1551) — dead store, live only for a
  hypothetical new mutant name without an override.
- `classify_streams`' `line_allowed` set-membership and `,`-prefix arms:
  sole call sites pass `allowed_stderr=()` (stream probe ~:1719/:2219) —
  the entry-matching machinery is dead under current callers; any
  non-empty stderr line rejects (the empty-allowlist behavior is live).
- `"SCRIPT ERROR:"/"Parse Error:" in output` re-check at ~:449-450:
  redundant second evaluation of conjuncts `classify_process` already ran
  on the same `output` — belt-and-suspenders, no distinct surface.
- 3 `()` dict keys (slider focus-restore rows): semantic placeholders,
  identical to the `.get(name, ())` default — documentation-only.
- `crash_self_sigkill`: deliberately no entry; captured output carries
  zero `ERROR:` lines (SIGKILL gives no handler text) — the no-allowlist
  path is exercised every run.

## Converge/diverge on the declared claim

Claim: "the rejection clause's verdict is a pure function of merged-output
line presence modulo the allowlist — forgeable in both directions (evasion
and fabrication) by a post-death descendant."

**CONVERGE — holds on this host, with three sharpenings:**

1. Both directions measured on real pipes; fabrication additionally shown
   WITHOUT any descendant (in-life concat seam) and on the accept axis
   (seam-fabricated signature → PASS) — the mechanism is merge-geometry,
   not provenance. "Pure function of merged bytes" cuts both ways.
2. Domain precondition: the function exists only where the merged bytes
   UTF-8-decode — a post-death `\xff` raises UnicodeDecodeError through
   `run_process`; no verdict is produced at all (third direction beyond
   evasion/fabrication: denial-of-verdict; scout-flagged, now live-measured
   through the verbatim function).
3. "Line presence" is exact for the `ERROR:` scan only; `SCRIPT ERROR:`/
   `Parse Error:`/`signature` are blob-substring tests — and they are
   **allowlist-immune** (measured: allowlisted `SCRIPT ERROR:` line still
   rejects; comma-absorbed line carrying `Parse Error:` tail still rejects
   → F/F/F under all allowlists). The true conjunct order is blob clauses
   → allowlist-gated line scan — convergent with critic CE-1a/CE-1b, both
   reproduced on real pipes. The full verdict also ANDs
   `code==expected_exit` and `error is None` — not output-derived (claim
   scoped to the rejection clause; noted).
4. Evasion is bounded to splits inside the token: residual `ERROR:`-bearing
   fragments still reject (`SCR\nIPT ERROR:`, `SCRIPT \nERROR:`, `ERROR:
   head\nrest` all → False; `Parse Err\nor:` → True by case asymmetry) —
   convergent with critic CE-2.

## Convergence vs sibling seats

- Author's in-run meta `probe_error_clause_surface`: PASS, 34/34
  discriminations (their receipt, 99 rows). My driver reproduces all four
  arm behaviors through an INDEPENDENT extraction + driver — same
  verdicts: allowforge F/T/F, splitforge True, seamforge False with
  per-stream absence, midlineforge False+sig-destroyed.
- r66-reviewer: `AUTHOR_ARMS_BEHAVE_AS_DECLARED` + 88/88 battery on the
  diff + 87→88 prior-row stability — convergent.
- r66-scout map: 22/22 synthetic discriminations + census claims —
  convergent where overlapping; my adds: all shapes on real pipes,
  decode-hole live-confirmed, census replay on the author receipt +
  static unreachability findings.
- Fixture byte convergence: my `proj/descendant_pipe_probe.gd` sha256
  `9ff5a9ae57579017…` == scout's reported `9ff5a9ae5757…` == reviewer's
  measured worktree bytes.

## Caveats / UNKNOWNs

- Single host/profile; timings vary, verdict directions do not.
- `syn_decode_postdeath` write_ppid not in-record (no record exists) —
  post-death-ness is by gate construction, not receipt-visible.
- sh-descendant arms simulate the same pipe mechanics; the Godot arms use
  the author's real fixture arms verbatim.
- The census's "reachable" claim is bounded to the fixtures as shipped;
  dead-code findings are static (file:line) + receipt-corroborated.
