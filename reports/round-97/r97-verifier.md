# r97 verifier — independent non-author verification of `f67094bb`

**VERDICT: VERIFIED** — the committed r97 landing clears the wave-B gate on
every axis this seat can test. My own full battery runs on the pinned
`git archive f67094bb` bytes are **438/438 PASS twice** (one on a fresh `/tmp`
checkout, one on the pinned tree) with all 12 `stree_lattice_*` rows green, the
r97 floor gate `True`, `dead_entry_count = 0`, and all 71 allowlist-bearing
rows of the earlier rounds live-matched; the signature gate is proven
load-bearing by an in-harness dead-entry mutant (gate flips `False`, exactly
one discrimination flips); forgery/mutation sensitivity rejects every tamper
(540/540 executed mutations, plus 4/4 fixture-level behavioural mutants);
300/300 frozen scout+boundary receipts accept the committed signatures as
byte-exact lines; and 97/97 laws re-derive from the committed signature bytes
alone. Findings §8 are report-prose discrepancies and declared properties, not
reservations about correctness.

Seat `VERIFIER` (g2d lane r97, independent non-author) | host **devin** |
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`,
default 60 tps), Python 3.14, `timeout 2400` bound on each battery run (8 s
per-case bound internal to the harness). Target:
`f67094bb9cbf665242f85499c59e8b2f59cd5531` (*r97 author: SceneTree
groups/signal-flags/call_deferred lattice* — 12 `stree_lattice_*` rows,
*420→432 CASES* as the commit message puts it — **measured 419→431**, see F1 —
438 battery rows, +65/−0 insertion-only, `+ stree_lattice.gd` + 3 scene
fixtures). Parent commit `d5c05ff8` (r96 adjudication). Receipts:
`corpus/live/r97-verifier/` (untracked evidence space). Author report
`reports/round-97/r97-author.md`; sibling receipts `corpus/live/r97-{scout,
boundary,critic,reviewer,scribe,simplifier}/` (corroboration only — every
load-bearing claim below is re-derived on this seat's own runs and bytes).

**`lsp` disclosure.** No `lsp` device / no GDScript language server on this
host (unchanged lane state r89–r97); all semantic validation is fresh-process
execution plus static reads of the committed bytes — the recorded fallback.
The change is new fixtures plus an insertion-only harness block (no renames, no
symbol moves), so no symbol-aware operation was possible or required.

**Frozen probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2,
agent `61ba8448`) was dispatched with one bounded four-clause hypothesis over
the committed CASES tuples × this seat's `runs-v` verdicts: (a) 12/12 r97 rows
PASS/exit 0/error null — **CONFIRMED**; (b) the committed signature is a
substring of each row's joined output — **CONFIRMED**; (c) it is a whole
byte-exact output line — **CONFIRMED**; (d) all 12 rows carry
`expected_errors: []`, `probe_error_clause_surface` is PASS with
`discriminations.r97_expected_errors_all_matched is True` and
`census.dead_entry_count == 0` — **CONFIRMED**. Advisory only; it wrote
nothing (its own report: "read-only probe, zero writes").

**Concurrent-worktree disclosure.** The shared worktree's tracked files were
clean at pass start and at report time (`git status --porcelain` has no ` M` /
` M`-class entry). The target is the **r97 landing commit** `f67094bb` (the
wave-B gate object named by this task); HEAD moved under this seat while it ran
(`2dcbb6f6` r100 author at pass start → `9ede7c50` *r97–r100 integration fix:
dedupe crash sentinel CASES rows (509/509 unique)* → `619ad7e0` pyc refresh).
The r97 bytes are untouched by all of that: the four r97 fixture files are
**unchanged** `f67094bb → HEAD` (`git diff --stat` on them is empty) and the 12
r97 CASES tuples are **byte-identical** at HEAD (AST-extracted tuple equality),
still contiguous at indices 415–426 — the later harness deltas are later
rounds' inserted blocks plus the crash-sentinel dedupe (which touched the
crash/descendant tail rows, not r97). The host was heavily oversubscribed by
sibling lanes (~19 concurrent full batteries at pass start, 54 by mid-pass;
loadavg 10–16): my first `rep2` attempt was **killed by the environment at
288/438 rows** (disclosed, kept as
`runs-v/20261016T093008638858Z.killed-at-288-rows`) and relaunched detached as
`rep2b`. Zero tracked writes by this seat; every artifact below ran the pinned
`tree/` extraction or the byte-identical `/tmp` checkout.

---

## 1. Method — pinned committed tree + fresh `/tmp` checkout

- `git archive f67094bb | tar -x -C corpus/live/r97-verifier/tree/` —
  **whole-commit** pin (not a fixtures-only slice), 2.1 GB.
- **Blob identity**: every `git ls-tree -r f67094bb` entry hashed as a git
  object against the extracted bytes — **125,147/125,147 regular-file blobs
  match (sha1), 68/68 symlinks match** (hashed as link text); 125,215/125,215
  paths, **0 real mismatches**.
- **Fresh `/tmp` checkout**: `git archive f67094bb corpus/fixtures
  corpus/lessons corpus/knowledge README.md LOG.md SCORECARD.md PROVINCE.md
  SHONEN.md | tar -x -C /tmp/r97v-20261016T092236Z/tree` (9.4 MB) — a pristine
  non-repo extraction of every byte the battery reads (`HERE` =
  `corpus/fixtures`; the only parent-dir reads in the harness are
  `../live` (default `--runs`, overridden) and `../lessons`, which is only
  touched by the opt-in `--probe-audio-warning` branch). The 297
  `corpus/fixtures` + `corpus/lessons` files there are **byte-identical to the
  pinned tree** (sha256 manifest `diff` = empty). **rep1 ran there**;
  **rep2b ran on the pinned tree** — the same bytes, two extraction paths.
- **Fixture pins** (sha256, computed here) match the author report exactly:
  `stree_lattice.gd` `61954f87f453762e5291a01422ff55e858d51d7ca0ce2a909a29f9115d33c528`
  (941 lines), `r97_scene_a.tscn` `c86d5674…b23046`,
  `r97_scene_b.tscn` `7c153f7f…6a79b50f`, `r97_scene_marker.gd`
  `39763310044aaac40fa69a1e57c435c6969ad9d9877c9f340ddb820bc2810b1a`;
  `run_battery.py` `a6a0f9651a69d5166b9c646e1ef8054749b1458eb9a559d9e3573786646de3ab`
  (4898 lines).
- **Commit scope** (`git show --stat`): 6 paths — the 4 fixtures, the harness,
  the author report; 1199 insertions / 0 deletions. `project.godot` untouched.
- **Source-level fold check** (`probes/fold_check.py`, §7): the frozen scout
  probe `corpus/live/r97-scout/probes/stree_lattice.gd`
  `4dd18e10e84f0da289688ea384f4029056cd2da7eeed32eeaa5d11f6e34a2c45`
  (896 lines) and the **boundary's** copy
  `corpus/live/r97-boundary/proj/stree_lattice.gd` are the *same* revision
  (byte-identical), so all 300 receipts below are one frozen probe revision.

## 2. Harness delta `d5c05ff8 → f67094bb` — insertion-only, independently re-derived

- `git diff --numstat` = **65 insertions / 0 deletions** on
  `corpus/fixtures/run_battery.py`.
- Tuple-level pure-insertion proof over AST-parsed CASES: **419 → 431**
  tuples; the 12 r97 rows are contiguous at indices **415–426**, preceded by
  `r96b_seed_seedcheck`, followed by the byte-identical crash/descendant tail
  (`crash_spontaneous_sigabrt`, `crash_self_sigkill`,
  `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`);
  the parent tuple list equals the child list minus that slice (both by name
  and by full tuple), and the parent contains **0** r97 tokens. **0 duplicate**
  case names.
- `expected_errors` += **0 entries**: 75 keys / 107 strings in both parent and
  target; `set(child) − set(parent)` is empty.
- Floor gate `r97_expected_errors_all_matched` present, predicate
  `r["case"].startswith("stree_lattice_")` — the same named-by-round /
  covers-round-prefixes shape as r87–r96 (12 round gates total in the
  committed harness).
- Every r97 row: `expected_exit == 0`, flags are exactly one `--arm=<arm>`
  token (plus `--rev` on the second `group_order` row), 12/12 signatures are
  plain `str` starting `PASS stree_lattice ` (no tuple signatures, no
  substring-only rows). Every arm resolves in the fixture's dispatch — proven
  behaviourally by §4 (the probe dies `_fail("unknown_arm")` without the flag).
- **Provenance vs the scout's frozen rows**: AST-extracting `ROWS` from
  `corpus/live/r97-scout/author-rows.py.txt` gives 12/12 **identical
  signatures**, identical `script` and `expected_exit`; the only difference is
  the flags column, where every committed row adds the `--arm=<arm>` token the
  scout's list omitted (the author's documented correction — the probe cannot
  run without it). Every committed signature is also a superstring of the
  scout's `ROWS_PREFIX` alternative (12/12).

## 3. Battery on the committed bytes — my runs

| rep | tree | run dir | verdict | rows | r97 rows | r97 gate | dead entries |
|---|---|---|---|---|---|---|---|
| rep1 | fresh `/tmp` checkout | `runs-v/20261016T092242628777Z/` | **PASS** | **438/438** | **12/12 PASS** | **True** | **0** |
| rep2b | pinned `tree/` | `runs-v/20261016T093732039299Z/` | **PASS** | **438/438** | **12/12 PASS** | **True** | **0** |

- Both runs: all 7 meta rows PASS (incl. `probe_error_clause_surface`,
  `probe_while_live_signature_gate`, `probe_descendant_signature_spoof`), all
  other surface discriminations `true`, **zero FAIL rows**, no flake.
- r97 rows: `actual_exit == 0`, `error is None`, `expected_errors == []`,
  contiguous at indices 415–426, flanked exactly as in §2.
- **Allowlist live-match**: `rows_with_expected_errors = 71` (r87–r96 rows),
  `dead_entry_count = 0`, `dead_entries = []` in both runs — every earlier
  round's entry fired in-run. The r97 block contributes **0** census rows
  (the census only collects rows that carry entries), so its gate is
  vacuously true today — §5 proves the gate mechanism still bites.
- **Author runs re-verified** (`corpus/live/r97-author/runs/`, all 7 present):
  `082702`, `083244`, `084924`, `090413`, `091032` = **PASS 438/438**;
  `084014` = FAIL on `negative_transition` + its documented
  `probe_error_clause_surface` knock-on; `085730` = FAIL on
  `nav_lattice_region`. **All 12 r97 rows PASS in all 7 runs** (84/84
  row-instances); **all 12 `*_expected_errors_all_matched` gates are true in
  all 7 runs**, and the only other flipped discrimination anywhere is
  `census_bare_classifier_consistent` in the `084014` flake run — exactly the
  knock-on the author describes (that row died differently, so its
  whitelisted `ERROR:` lines never fired). The *438/438 ×3 consecutive on final
  bytes* claim holds.
- **Cross-run byte stability**: 10 runs × 12 rows = **120 row-instances**
  (7 author + my rep1 + my rep2b + the §5 mutant run) — **no row has more than
  one distinct output** (`out_uniq = 1` per row), and the committed signature
  is present in every one.

## 4. Fresh arms — 12/12 clean on the pinned fixtures

`probes/fresh_arms.py` (harness-exact launcher: scratch copy + project-name
munging + `pickup.tscn` staging + the `causal_chain` readiness fix, pointed at
`tree/corpus/fixtures`; receipts `arms/tree-rep1/<case>.{out,err,rc}` +
`summary.json`):

- **12/12 launches rc=0, 12/12 classified PASS** under the production
  `classify_process` (AST-extracted from the pinned harness) with the committed
  `expected_errors`.
- **12/12 emit the signature as a whole line** (`signature_exact_line`), and
  **12/12 also PASS with the allowlist removed** (`bare_verdict = PASS`) —
  correct: the r97 block needs no allowlist.
- stderr **0 B for 12/12**; 0 unclaimed `ERROR:` lines.
- Slowest arm 0.727 s (`scene_probe`) vs the 8 s bound — >10× headroom.

## 5. Forgery / mutation sensitivity — the signature gate is load-bearing

`probes/discriminate.py` over the fresh receipts (re-classified with the
production `classify_process` + committed allowlist):

- **540/540 executed mutations rejected, 0 gaps**:
  - 60 global-axis mutations (per row: rc flip, injected unrelated `ERROR:`,
    injected `SCRIPT ERROR:`, injected `Parse Error:`, signature deletion) —
    60/60 reject;
  - **348 in-signature token mutations** (bool flips, int ±1, float
    last-digit, bracketed-vector element ±1 and element swaps, word last-char)
    — 348/348 reject; 5 further candidates were no-op rewrites and are counted
    as skipped, not as passes;
  - **132 cross-row signature swaps** (each row's PASS line replaced by one of
    the other 11 rows') — 132/132 reject.
- **Tail control**: junk appended *after* the signature is admitted **12/12** —
  the documented `signature in output` substring semantics, measured rather
  than assumed.

**Fixture-level falsifiability** (`probes/fixture_mutants.py`): four targeted
behavioural mutations of the committed fixture, each run fresh against the
committed signature — `group_order` `move_child(a, end→0)`,
`signal_flags` dropping `CONNECT_ONE_SHOT`, `scene_probe` swapping
`r97_scene_a.tscn → r97_scene_b.tscn`, `defer_ladder` removing the nested
`call_deferred("inner")`: **4/4 rejected with the emitted payload changed**,
while **4/4 unmutated controls PASS**. The pinned payloads are falsifiable by
real behaviour change, not tautologies.

**Gate-mutant battery** (`probes/make_mutant.py` → `mutant/fixtures/` = the
committed harness + **3 inserted lines**: one deliberately dead allowlist entry
on `stree_lattice_census`; diff is exactly that insertion; full 438-row run
`runs-mutant/20261016T093008686985Z/`):

- battery verdict **FAIL**, with exactly one failing row:
  `probe_error_clause_surface`;
- `r97_expected_errors_all_matched` = **False** — the **only** flipped
  discrimination (r96's gate and every other discrimination stayed `true`);
- `dead_entry_count = 1`, the injected entry named with `matched_lines = 0`,
  `dead_in_run = true`;
- `stree_lattice_census` itself still **PASSes** and **12/12 r97 rows still
  PASS** — the gate, not the row, is what fails. A dead r97 allowlist entry
  therefore cannot pass silently, even though the block carries none today.

## 6. Receipt coverage over the frozen receipts

`probes/receipt_coverage.py` over the scout canonical (48), scout loadtest (36)
and boundary-mode (216) receipts of the **same frozen probe revision** —
**300/300 accepted**:

- 300/300: committed signature present, **byte-exact whole line**,
  `rc = 0`, stderr **0 B**;
- 300/300 accepted by the production classifier with the committed
  `expected_errors` (and 300/300 also bare-accepted — no allowlist needed);
- **exactly one distinct `PASS stree_lattice …` line per row** across all its
  receipts (byte-stability over 48 canonical + 36 loadtest + 216 boundary-mode
  receipts, matching the author's claim);
- per-row counts: 24 receipts for the 3-rep cells, 27 for the 6-rep cells.

## 7. Laws and the fold re-derived from the committed bytes

- `probes/verify_laws.py` — **97/97 boolean checks true**, each parsing tokens
  out of the 12 committed signature strings themselves (no trust in report
  prose): group API/flag census (10 methods, 6 signatures, both flag blocks as
  distinct powers of two, `ticks=60`, `SceneTree`/`Window`); L1 tree-order view
  (t0 == DFS members, `rep1 == rep2 == after_move_child`, nested child member
  absent from the root's child list, dup-add idempotent, double-remove
  idempotent, re-add restores tree position, unknown group empty); the rev row
  (only `add_order` + `rev` differ — add-order independence); deferred capture
  (queue-time members called, leaver still called, joiner not, `REVERSE`
  reverses the *queue* list, UNIQUE epoch dedup vs no direct dedup, plain
  DEFERRED no dedup, FIFO across groups); lifecycle (stale snapshot, no
  cascade, `free()` instant vs `queue_free` next frame, root Window groups,
  `/`+`.` names verbatim); setters (real property writes, deferred flush
  point, non-property/unknown-group silent); signal order (connect order,
  disconnect, reconnect-to-END, by-name identity, bind, await-at-emit);
  signal flags (deferred at flush, FIFO, survives disconnect, ONE_SHOT severs
  at emit while the queued call still runs, REFERENCE_COUNTED needs N
  disconnects, PERSIST == `connect_flags` PERSIST, one global FIFO across
  objects); deferred ladder/slots/order (same-frame landing with and without
  await, physics continuation, nested same-flush, freed target dropped,
  detached still called, `queue_free` then gone, per-object FIFO, the
  signal-queued call not at emit but in-window); scene probe (file ≈2–5
  frames, packed 1 frame, node ≤2 frames, `reload_current_scene` exists).
  Cross-row: `rev=false` in the 10 rows that carry the key, `rev=true` only in
  the rev row, arm token matches flags, all 12 signatures distinct.
- `probes/fold_check.py` — the fixture is a **comment-only + namespace fold**
  of the frozen scout probe: **941 vs 896 lines (net +45)** and the **only**
  changed non-comment lines are the two declared `res://` renames; the marker
  script is **byte-identical** to the scout's; each `.tscn` differs by exactly
  one `ext_resource` path line; the mint-era `scene_a.tscn`/`scene_b.tscn`/
  `scene_marker.gd` family (root `Node` + `marker=`, load-bearing for
  `controls/scene_transition_probe.gd`) still exists untouched, so the
  `r97_scene_*` namespace keeps both families coexisting.

## 8. Findings / observations (ranked)

- **F1 (INFO — report prose, not bytes).** The author report (and the commit
  message) state *CASES 420 → 432*. The committed harness has **419 → 431**
  tuples (the *results rows 426 → 438 incl. meta* figure is correct; 431 + 7
  meta = 438). The off-by-one is in the prose only — the shipped tuples are
  exactly the 12 new rows, and the parent tuple list is a pure prefix/suffix
  split of the child (§2).
- **F2 (LOW — report prose, stale pre-fix counts).** The author report lists
  `stree_lattice.gd` as *937 lines* and *+41* vs the 896-line scout probe. The
  committed file is **941 lines**, delta **+45** — consistent with the
  session's own comment-level fix (the sha256 in the same report,
  `61954f87…`, matches the committed bytes exactly). Hash and behaviour are
  right; the line arithmetic predates the final comment fix.
- **F3 (INFO — declared, now proven).** The r97 floor gate is **vacuously
  true** on committed bytes: the r97 block carries zero allowlist entries and
  the census only collects rows *with* entries (0 r97 census rows). §5's
  injected dead entry flips it to `False` while the row itself still passes —
  the gate is a real tripwire for a future entry, not decoration.
- **F4 (INFO — engineering property, verified).** The `r97_scene_*`
  namespacing is behaviour-neutral: the commit touches 6 paths, the mint-era
  scene family is untouched, and the fold's only executable changes are the two
  `res://` renames (§7). The battery's pre-existing scene rows stay green in
  both of my runs.
- **F5 (INFO — host, disclosed).** The host ran ~19 → 54 concurrent full
  batteries from sibling lanes; my first `rep2` was killed by the environment
  at 288/438 rows (no FAIL rows at the time) and was relaunched detached as
  `rep2b`, which passed 438/438. No flake appeared in any completed run of
  mine. The author's two flake events (`negative_transition` + knock-on,
  `nav_lattice_region`) are the r89-documented wall-clock classes, reproduce in
  their own receipts, and touched no r97 row (12/12 green in those runs too).
- **F6 (INFO — lane property).** No GDScript language server exists on this
  host, so symbol-aware validation was unavailable (recorded fallback); the
  change required none.
- **Blockers: none.**

## 9. Remaining risks (stated, not reservations)

- The r97 signatures are **full-line order vectors** — deliberately stricter
  than the measured-equivalent `ROWS_PREFIX` form. A future engine bump must
  re-verify before any relaxation; silently weakening the form would drop the
  order laws this round pins (§7 shows the vectors *are* the laws).
- The r97 gate becomes live only when a future round adds r97 allowlist
  entries (F3); until then its protection is the harness census plus the
  per-row signature gate, both proven biting in §5.
- The pre-existing flake classes are host-load-coupled and unrelated to r97;
  the two documented events are reproduced and attributed in §3.

## 10. Evidence index

| artifact | path |
|---|---|
| pinned tree (125,215 blob-identical entries) | `corpus/live/r97-verifier/tree/` |
| fresh `/tmp` checkout (rep1 tree) | `/tmp/r97v-20261016T092236Z/tree/` |
| rep1 battery (PASS 438/438) | `corpus/live/r97-verifier/runs-v/20261016T092242628777Z/verdicts.json` |
| rep2b battery (PASS 438/438) | `corpus/live/r97-verifier/runs-v/20261016T093732039299Z/verdicts.json` |
| killed first rep2 attempt (disclosed) | `corpus/live/r97-verifier/runs-v/20261016T093008638858Z.killed-at-288-rows/` |
| gate-mutant battery (gate False as designed) | `corpus/live/r97-verifier/runs-mutant/20261016T093008686985Z/verdicts.json` |
| mutant harness (3 inserted lines) | `corpus/live/r97-verifier/mutant/fixtures/run_battery.py` |
| fresh arms on tree (12/12) | `corpus/live/r97-verifier/arms/tree-rep1/` (+`summary.json`) |
| fixture-level mutants (4/4 rejected) | `corpus/live/r97-verifier/fixture-mutants/summary.json` |
| laws re-derivation (97/97) | `corpus/live/r97-verifier/probes/laws.{txt,json}` |
| fold check (source-level) | `corpus/live/r97-verifier/probes/fold-check.{txt,json}` |
| discrimination (540/540) | `corpus/live/r97-verifier/probes/discrimination.{txt,json}` |
| receipt coverage (300/300) | `corpus/live/r97-verifier/probes/receipt-coverage.{txt,json}` |
| static harness census | `corpus/live/r97-verifier/probes/static-check.{txt,json}` |
| probe sources | `corpus/live/r97-verifier/probes/*.py` |
| battery logs | `corpus/live/r97-verifier/probes/battery-{tmp-rep1,tree-rep2,tree-rep2b,mutant}.log` |
| corroboration (sibling seats) | `corpus/live/r97-{scout,boundary,critic,reviewer,scribe,simplifier}/` |

Tracked writes: **zero** (this report is a new untracked file; `corpus/live/`
is the lane's evidence space and `corpus/live/**/*tree*/` is gitignored; no
tracked file was modified — `git status --porcelain` carries no ` M` entry at
report time).
