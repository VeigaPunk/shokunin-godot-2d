# r96 verifier — independent non-author verification of `89f85ed8`

**VERDICT: VERIFIED** — the committed r96 landing clears the wave-B gate on
every axis this seat can test. My own full battery run on the pinned
`git archive 89f85ed8` tree is **426/426 PASS** with all 60 r96 rows green,
the r96 floor gate `True`, and all 16 r96 allowlist entries live-matched;
the signature gate is proven load-bearing by an in-harness mutant run
(injected dead entry → gate `False`); forgery/mutation sensitivity rejects
every tamper (2124/2124 token mutations); the pinned laws re-derive 57/57
from the committed signature bytes. Caveats in §8 are declared, engineered
properties with working failure modes, not reservations about correctness.

Seat `VERIFIER` (g2d lane r96, independent non-author) | host **devin** |
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`,
default 60 tps), Python 3.14, `timeout 2400` bound on each battery run
(8 s per-case bound internal to the harness). Target:
`89f85ed844c27ffb2a1760cc359c334caa92ef1f` (*r96 author: 60 rows (426
total) — scene_io + r96b lattices, 16 expected-errors all live-matched;
426/426 x2*). Receipts: `corpus/live/r96-verifier/` (gitignored). Author
report `reports/round-96/r96-author.md`; sibling reviewer evidence
`corpus/live/r96-reviewer/` (corroboration only — every load-bearing claim
below is re-derived on this seat's own runs).

**`lsp` disclosure.** No `lsp` device / no GDScript language server on this
host (unchanged lane state r89–r96); all semantic validation is fresh-process
execution plus static reads of the committed bytes — the recorded fallback.
The change is new fixtures + an insertion-only harness block (no renames, no
symbol moves), so no symbol-aware operation was possible or required.

**Frozen probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2,
agent `51df1485`) was dispatched with one bounded four-clause hypothesis over
the committed CASES tuples × this seat's `runs-v` verdicts: (a) 60/60 r96
rows PASS/exit 0/error null — **CONFIRMED**; (b) committed signature is a
substring of the emitted output 60/60 — **CONFIRMED**; (c) 58 whole-line +
exactly the 2 declared idstat substring rows — **CONFIRMED**; (d) all 16
committed `expected_errors` entries censused verbatim, `matched_lines≥1`,
`dead_in_run=false` — **CONFIRMED**. Its runs-mutant cross-check independently
found the injected dead entry as the sole delta. Advisory only; it wrote
nothing.

**Concurrent-worktree disclosure.** HEAD = `89f85ed8` throughout this pass.
The shared worktree carries foreign uncommitted r97-author edits
(` M corpus/fixtures/run_battery.py` +65 lines of r97 block, ` M
…/__pycache__/…pyc`) — **never graded**: every artifact below ran the pinned
`tree/` extraction or read-only probe scripts pointed at it. Zero tracked
writes by this seat; `git status` delta vs pass-start is nil.

---

## 1. Method — pinned committed tree

- `git archive 89f85ed8 | tar -x -C corpus/live/r96-verifier/tree/` —
  **whole-commit** pin (not a fixtures-only slice).
- **Blob identity**: every `git ls-tree -r 89f85ed8` entry hashed as a git
  blob against the extracted bytes — **125,204/125,204 match, 0 real
  mismatches** (68 symlinks verified by link-text hashing; `corpus/fixtures`
  90/90). The earlier fixtures-only `freeze/` extraction is byte-identical to
  `tree/corpus/fixtures` (`diff -r`, excluding regenerated `__pycache__`), so
  probe outputs computed on `freeze/` and re-run on `tree/` agree exactly.
- **Fixture pins** (sha256, computed here) match the author report exactly:
  `scene_io_lattice.gd` `8aeab1cb…02d` (839 lines, folded scout probe);
  `r96b_cache.gd` `f7d06de3…`, `r96b_id.gd` `53a63d65…`, `r96b_phase.gd`
  `4bb89614…`, `r96b_seed.gd` `69a6413f…`, `r96b_seq.gd` `3cae3659…`,
  `r96b_var.gd` `71653a79…` (all boundary byte-copies); `run_battery.py`
  `3118fb5a…bc92a3` (4833 lines).
- **Commit scope** (`git show --stat`): 9 paths — the 7 fixtures, the harness,
  the author report. Nothing else touched.

## 2. Harness delta `4a8bb124 → 89f85ed8` — insertion-only, independently re-derived

- `git diff --numstat` = **243 insertions / 0 deletions**.
- Tuple-level pure-insertion proof over AST-parsed CASES: **359 → 419**
  tuples; the 60 r96 rows are contiguous at indices **355–414**, preceded by
  `r95b_order_rigid`, followed by the byte-identical crash/descendant tail
  (`crash_spontaneous_sigabrt`, `crash_self_sigkill`,
  `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`);
  `child[:355] == parent[:355]` and `child[415:] == parent[355:]`. Parent
  contains **0** r96 tokens; **0 duplicate** case names.
- `expected_errors` += **3 entries / 16 strings** (ownership ×2, uid ×1,
  refuse ×13) — all exact strings.
- Floor gate `r96_expected_errors_all_matched` present, predicate
  `case.startswith(("r96_scene_io_", "r96b_"))` — same named-by-round shape
  as r87–r95 (12 round gates total in the committed harness).
- Every r96 row: `expected_exit == 0`, flags are `--arm=<arm>` only; every
  committed arm resolves in its fixture's dispatch (the 10 `r96b_phase_*`
  arms dispatch by `begins_with("ph"/"pph")` prefix-parse — a static grep
  misses them; all 10 PASS fresh-process, so coverage is proven
  behaviorally). No row references `r96b_size.gd` — consistent with its
  deliberate non-landing.
- Signature census: **58/60 whole-line `^PASS` rows**; the two declared
  substring rows are exactly `r96b_var_idstat_breadth`
  (`PASS r96b_var idstat n=200 distinct=200` — line prefix) and
  `r96b_var_idstat_u31_gate`
  (`gt2p31=0 pin_save=OK pin_found=true,true,false,false,false instantiate_ok=true`
  — mid-line substring; `min=`/`max=`/`sample=` are process-random and
  deliberately unpinned).

## 3. Battery on the pinned tree — my run

`cd tree && timeout 2400 python3 corpus/fixtures/run_battery.py --godot godot
--runs …/r96-verifier/runs-v` (own scratch staging; `seed` field records the
tree's fixtures dir as root).

| rep | run dir | verdict | rows | r96 rows | r96 gate | dead entries |
|---|---|---|---|---|---|---|
| rep1 | `runs-v/20261016T083136300100Z/` | **PASS** | **426/426** | **60/60 PASS** | **True** | **0** |

All 16 r96 allowlist entries `matched_lines=1`, `dead_in_run=false` — including
the context-dependent `r96_scene_io_uid` entry (`uid://bqk3m5n7qar1`), which
fires in-battery because `export_readiness` populates `.godot/uid_cache.bin`
before the r96 rows (the documented mechanism). All surface discriminations
`true`. Ran concurrently with the mutant battery (loadavg ≈51) — disclosed;
no row flaked.

**Prior same-seat runs** (`runs-1/…080548Z`, `runs-2/…081226Z`, this seat's
earlier pre-report attempt on the identical frozen bytes): both FAIL on
`negative_transition` ("exceeded 120 frames") plus the documented allowlist
knock-on `probe_error_clause_surface` — the same pre-existing wall-clock
flake class the r95 verifier and the author recorded; **all 60 r96 rows PASS
in both**, gates `True`, `dead=0`.

**Author runs re-verified** (`corpus/live/runs/20261016T07*`): `0741` FAIL on
`audio_playback` (documented wall-clock flake, author's run A); `0748` and
`0754` **PASS 426/426**, gate `True`, dead 0 — the *426/426 ×2* claim holds.
The uncited dev run `0728` carries the sole r96 non-PASS instance in the
corpus (`r96_scene_io_uid`): pre-commit bytes emitted `ERROR: Unrecognized
UID: "uid://s3vo6pi07qle"` — a *random* minted uid, unallowlisted → FAIL.
This is the mechanism the author's fold fixed (fixed-`sid` query +
`uid://bqk3m5n7qar1` entry); on committed bytes the row is 9/9 PASS. The
failure is evidence the allowlist semantics actually bite, not noise.

**Cross-run stability**: 10 battery runs × 60 r96 rows = **600 row-instances**
(2 prior seat + 2 mine + 4 author + 2 reviewer): the only non-PASS is the
pre-commit `0728` instance above; **committed-era instances 540/540 PASS, and
the committed signature is present in every one of the 600 captured outputs**
(0 signature misses — the `0728` fail was the unallowlisted ERROR clause, not
a missing signature).

**Reviewer corroboration** (`corpus/live/r96-reviewer/`): run `081447` PASS
426/426 (gate True); run `080610` FAIL on two pre-existing flakes with all
r96 green; their `runs-ctl` mutant control shows `dead=1` → gate False —
same shape as my mutant (§6).

## 4. Fresh arms — 60/60 clean on the pinned tree

`probes/fresh_arms_tree.py` (the seat's harness-exact launcher pointed at
`tree/corpus/fixtures`; receipts `arms/tree-rep1/<case>.{out,err,rc}` +
`summary.json`):

- **60/60 launches rc=0, 60/60 classified PASS** under the production
  `classify_process` (AST-extracted from the pinned harness).
- **58/60 emit the signature as a whole line**; the 2 `idstat` rows emit the
  longer line carrying the declared substring — matching §2's census.
- stderr: **empty for 58/60**; the only non-empty are `ownership` (499 B) and
  `refuse` (3424 B) — the two allowlist-bearing rows. Bare (allowlist-free)
  classification **REJECTs exactly those two** and passes the other 58 — the
  allowlist is doing real work, not decoration.
- Slowest arm ≈0.70 s vs the 8 s bound (>10× headroom).
- **Allowlist byte-match on fresh bytes**: ownership 2/2 entries verbatim in
  fresh output, refuse 13/13, **0 unclaimed ERROR lines** in either row;
  `uid` matched 0/1 standalone — correct: no `.godot/uid_cache.bin` in a
  bare scratch, the diagnostic is deterministically absent outside the
  battery context (and the gate still holds in-battery, §3).
- The **folded signatures are live**: `pack_basic`'s `size_in_176_194` and
  `extres`'s renamed `id_differs_*` keys appear in fresh output (`exact=True`)
  — the fold claims are not just provenance-true, they reproduce fresh-process.

## 5. Receipt coverage & hygiene over the frozen lane receipts

`probes/receipt_coverage.py` over all `r96-scout`/`r96-boundary` `.out` receipts
(647 attributed to committed rows, 41 unparsed non-r96 leftovers):

- **56/60 rows: every canonical receipt carries the committed signature**
  (`accepted` = receipts×), rc=0 everywhere, no unexpected stderr.
- The four `<-- CHECK` flags are all explained, none anomalous:
  `pack_basic` (167 receipts, sig absent — old receipts carry the pre-fold
  `size_in_190_200` key; the folded signature is proven by fresh output,
  §4), `extres` (17 — pre-fold `id_stable_*` keys; same resolution), and
  `ownership`/`refuse` (`bare_rej`>0 + `err!=[499]/[3424]` — the allowlisted
  ERROR lines; with the committed allowlist they accept 17/17).
- `r96b_var_idstat_*`: 5/5 receipts substr-accepted with **5 distinct lines
  each** — the `min=`/`max=` variance the author declared is present in the
  receipts themselves.

## 6. Forgery / mutation sensitivity — signature gate is load-bearing

`probes/discriminate_tree.py` over the fresh `arms/tree-rep1` receipts,
re-classified with the production `classify_process`:

- **Global axes, all 60 rows**: rc flip 60/60 reject · injected unrelated
  `ERROR:` 60/60 · `SCRIPT ERROR:` 60/60 · `Parse Error:` 60/60 · signature
  deletion 60/60.
- **In-signature token mutations: 2124/2124 reject** (bool flips, int ±1,
  float last-digit, last-letter; sampled across each signature) —
  **zero mutation gaps**, including the substring rows (mutating
  `gt2p31=0`→`1` or a `pin_found` element rejects).
- **Tail control**: junk appended after the signature admitted 59/59 — the
  documented `signature in output` substring semantics, measured not assumed.

**Gate-mutant battery** (`mutant/fixtures/run_battery.py` = committed harness
+ one deliberately dead allowlist entry on `r96_scene_io_census`; full 426-row
run `runs-mutant/20261016T083136302662Z/`):

- `r96_expected_errors_all_matched` = **False** — the only discrimination
  flipped; `dead_entry_count=1` with the injected entry named
  (`matched_lines=0`, `dead_in_run=true`); `probe_error_clause_surface` and
  the whole run FAIL as designed.
- `r96_scene_io_census` itself still PASSes; all 60 r96 rows still PASS; all
  16 genuine entries still live-matched. A dead r96 allowlist entry therefore
  **cannot pass silently** — the floor gate is load-bearing. (The reviewer's
  independent ctl mutant agrees: dead=1 → gate False.)

## 7. Pinned laws re-derived from the committed signatures

`probes/verify_laws_tree.py` — 57 boolean law checks parsed out of the
committed signature strings themselves (no trust in report prose): **57/57
true**. Highlights re-derived, not echoed: id law f(path,slot) holds across
`seqA2`/`seqAB2`/`seq2obj`/`twoext`/`subpath`-stickiness/`fingerB`; the
headline `extpin`/`minimal`/`extbundle`/`rich` pinned raw sha256s are present
as literals; the deep cache-mode lattice (deep_reuse/replace/ignore,
repl_deep, ign_deep, threaded) is internally consistent; all 10 phase rows
pin identical payloads (no phase coordinate); `idstat` breadth
(`n=200 distinct=200`) + u31 gate tokens verified as the pinned law;
`size_in_176_194` is the signed bound. No tautological pins found — each
check parses measured tokens and compares real values (e.g. `layers`-style
true/false branches, sticky-vs-fresh id comparisons that differ where the
law says they must).

## 8. Findings / observations (ranked)

- **F1 (INFO — verdict-relevant history, not a defect).** The only non-PASS
  r96 row-instance in the whole corpus is a pre-commit dev run; the committed
  bytes are 540/540 PASS across 9 runs by 3 seats. The commit claim
  *426/426 ×2* under-states: committed-era count is ≥4 green full runs
  (author ×2, reviewer ×1, this seat ×1) plus 4 flake-FAIL runs with the r96
  block itself always 60/60.
- **F2 (LOW — declared, monitored).** `r96_scene_io_uid`'s allowlist entry is
  context-dependent by design (needs `.godot/uid_cache.bin`, populated by
  `export_readiness` before r96 rows run). Verified absent-standalone /
  present-in-battery on this seat's own runs. If a future battery reorder
  breaks it, `r96_expected_errors_all_matched` fails loudly — proven by §6's
  mutant. Correct failure mode.
- **F3 (LOW — declared).** `r96b_var_idstat_breadth` carries the documented
  ~1e-5/run birthday-collision window on 200 minted ids; a flip is a real
  generator event, deliberately surfaced. `min=`/`max=`/`sample=` unpinned by
  necessity (process-random; observed differing between my two runs).
- **F4 (INFO — pre-existing lane property, not r96).** The
  `negative_transition` wall-clock flake fired in 2/4 seat-side runs under
  concurrent load (loadavg ≈51–100), knocking on
  `probe_error_clause_surface` via its own dead allowlist entries — the same
  documented class as r94/r95. CASES index ≪ 355, zero interaction with the
  r96 block (60/60 green in those same runs).
- **Blockers: none.**

## 9. Evidence index

| artifact | path |
|---|---|
| pinned tree (125,204 blob-identical files) | `corpus/live/r96-verifier/tree/` |
| my battery rep (PASS 426/426) | `…/r96-verifier/runs-v/20261016T083136300100Z/verdicts.json` |
| gate-mutant battery (gate False as designed) | `…/r96-verifier/runs-mutant/20261016T083136302662Z/verdicts.json` |
| fresh arms on tree (60/60) | `…/r96-verifier/arms/tree-rep1/` (+`summary.json`) |
| laws re-derivation (57/57) | `…/r96-verifier/probes/laws.{txt,json}` |
| discrimination (2124/2124) | `…/r96-verifier/probes/discrimination.{txt,json}` |
| receipt coverage (647 attributed) | `…/r96-verifier/probes/receipt-coverage.{txt,json}` |
| static harness census | `…/r96-verifier/probes/static-check.{txt,json}` |
| tree-pointed probe sources | `…/r96-verifier/probes/*_tree.py` |
| battery logs | `…/r96-verifier/probes/battery-{tree-rep1,mutant}.log` |
| corroboration (sibling) | `corpus/live/r96-reviewer/` |

Tracked writes: **zero** (this report untracked; `corpus/live/` gitignored;
worktree ` M` entries are the foreign r97 author's, untouched).
