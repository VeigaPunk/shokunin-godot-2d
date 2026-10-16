# game-dev-2d round 91 — simplifier (r91-simplifier): the r91 nav_lattice landing is audited clean (11 rows ↔ 11 arms, zero dead harness keys, zero dead gates, every pin a byte-exact prefix of its emission, pins byte-stable across 6 independent receipts per row, all four boundary folds re-verified on the landed bytes) — with **two provable YAGNI deletions** (−3 lines: a dead `SETTLE` const and the two append-only `hits` sinks in the teardown arms) proposed as a patch, **not applied** (zero tracked writes)

Seat `SIMPLIFIER` (LEAF) | lane `r91` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Work commit **`77d2f7e`** (r91 author: `corpus/fixtures/nav_lattice.gd` +
`corpus/fixtures/run_battery.py` +88/−0 + author report, 258 rows). HEAD moved
mid-session under the sibling wave-B seats (`e3fd799` scribe → `7330589`
reviewer → **`645fd8e`** critic); the **landing bytes are unchanged at HEAD** —
`git show 645fd8e:corpus/fixtures/{nav_lattice.gd,run_battery.py}` are
byte-identical to `77d2f7e` (`088843399…`, `f5725ca4…`), so every receipt below
is valid for HEAD as well. **No tracked file written, no commit, no git
mutation by this seat.** Writes are this report and
`corpus/live/r91-simplifier/**` only. All receipts are against the byte-exact
`77d2f7e` snapshot in `corpus/live/r91-simplifier/committed-fixtures/`
(`nav_lattice.gd` `088843399ce37eb272dfb8cbf7e2a115f1b9af01a44859ea05610297875e3796`,
`run_battery.py` `f5725ca441565b8c9903b5e98aeb1112ea5c56a11a1f422b6feb46f904953220`).
Host ran under heavy foreign oversubscription throughout (load 65 → 80 on 32
cores; 7 concurrent `godot` processes seen — not mine).

**`lsp` disclosure.** No `lsp` device is exposed in this dispatch and no
GDScript/Python language server exists on this host (`gdlint`/`gdformat`/
`gdscript-lsp`/`gdtoolkit` absent — same finding as the r89/r90 seats).
Symbol-aware `references`/`definition`/rename were therefore **unavailable**;
no cold result is recorded as absence. Every caller/consumer claim below rests
on (a) a complete textual enumeration, (b) a scope-aware write-only-store scan,
(c) a pin↔emission prefix census over the real run, and (d) fresh-process byte
comparison.

**Frozen probeParent.** Exactly **one** read-only `ufo-labrat` was dispatched
(bounded, 4 falsifiable static hypotheses: pin/emission prefix law; scheduler
fields strictly post-pin; dead-weight census; teardown-arm shape). It returned
**H1 CONSISTENT** (every signature's token sequence is emitted in order, ending
at the declared last pinned token, tails after), **H2 CONSISTENT** (no
scheduler/race field printed inside any pinned block), **H4 CONSISTENT**
(crash arm registers a live callback, never clears it, prints no PASS line;
clean arm clears + ≥1 frame + frees), and **H3 refuted on one point: `const
SETTLE := 10` (line 56) has zero reads** — the same finding this seat then
proved by execution. Its H3(d) print-count mismatch was a wording ambiguity
(11 arms = 10 PASS lines + 1 marker + STALE + unknown-arm fallback = 13 sites;
`_arm_teardown_crash` legitimately prints no PASS line). The probe had no shell
(its own exec gap, as in r90), so every empirical number below is this seat's
own fresh-process receipt. No other descendant was spawned.

---

## 1. Method and proof artefacts

`corpus/live/r91-simplifier/` (`MANIFEST.sha256`, **589 files**, sha
`d251b2f982c46c37d0f98b672f0f3e6bd76adb6a35ed38b98e69f35f747bcc5a`; scratch/run
snapshot trees excluded per r90 precedent — the manifest covers the scripts,
receipts, the committed snapshot and the folded proposal tree):

| artefact | content |
|---|---|
| `committed-fixtures/` | byte-exact `git show 77d2f7e:` snapshot of `nav_lattice.gd` (`088843399…`) and `run_battery.py` (`f5725ca4…`); every audit below re-run against this snapshot |
| `runs-control/20261015T224739373652Z/` | full battery on the **committed** tree: **258/258 PASS**, `r91_expected_errors_all_matched=true`, `dead_entry_count=0`; launch snapshot proven committed (`scratch/nav_lattice.gd` = `088843399…`) |
| `control-battery.stdout` | the run's per-row verdict log |
| `committed-audit.txt` | arm↔row bijection, function/call-site census, print-site census, CLI-knob census, tail-marker scan |
| `deadstore-scan.txt` | scope-aware write-only-store scan (file scope + per function) → exactly **1** write-only store (`SETTLE`), plus the append-only sinks |
| `committed-key_and_pin_census.txt` | pin↔emission prefix census per row + allowlist/dead-entry census + all gate values |
| `committed-cross_session_pins.txt` | pinned block vs the author's 3 fresh reps × 11 arms + both author green runs → **TOTAL_MISMATCHES=0** |
| `committed-vs-author_runs.txt` | full-battery row identity vs the author's `runs1`/`runs2`: 258/258 common, 0 verdict diffs, 0 exit diffs |
| `committed-tail_variance.txt` | tail-field variance census (the fold's load-bearing proof) |
| `committed-gates.txt`, `committed-required_stderr_liveness.txt` | gate table; production-classifier liveness proof for the `required_stderr` pin |
| `fold-experiments-main.txt`, `fold-main-summary.txt`, `runs-fold-main/` | control vs `foldA` (SETTLE) vs `foldB` (sinks): 11 arms × 3 reps each |
| `fold-experiments-teardown.txt`, `fold-teardown-summary.txt`, `runs-fold-teardown/` | teardown-arm focus: raw-byte-identical 3/3 per arm per variant, plus the callback-hit probe |
| `fold-stale.txt`, `runs-fold-stale/` | `SYNC_BOUND := 1` gate-exhaustion probe (loud-failure fold) |
| `folded-battery-summary.txt`, `runs-fold-battery{,2}/` | full 258-row battery on the **folded** fixture, twice |
| `control2-summary.txt`, `runs-control2/` | a third full battery under the same load: working tree then = committed 258 rows + 14 uncommitted foreign r92 tilemap rows = **272 rows, 272/272 PASS** |
| `hits-probe.txt` | does the callback body execute in the teardown arms? (2 hits/arm) |
| `fold-proposal.diff`, `fold-battery-project/` | the −3-line patch and the folded tree it was measured on (`b23887e5…`, 880 lines) |
| `*.py` | the audit/experiment scripts (re-runnable) |

## 2. Verdict and findings (ranked)

**Verdict: PASS — the landing is audited clean, and the only removable weight
is two provable YAGNI deletions (−3 lines) proposed as a patch, not applied.**
No dead arm, no dead row, no dead allowlist entry, no dead gate, no dead CLI
knob, no unpinned emission, no pinned-but-unemitted field. All four boundary
folds hold on the landed bytes. 0 blockers.

| # | finding | severity | evidence |
|---|---|---|---|
| F1 | **Two YAGNI deletions are provable and byte-neutral** (§6): `const SETTLE := 10` (`nav_lattice.gd:56`, zero reads in the landed fixture *and* in the scout probe it came from — **corroborating the committed reviewer's F4**, which refers it to this seat) and the append-only `hits` sinks in `_arm_teardown_crash`/`_arm_teardown_clean` (`:851/:871` + their lambda bodies). Patch attached; **not applied** (this seat writes no tracked file) | low (clean-up; −3 lines) | `deadstore-scan.txt`, `fold-proposal.diff`, `fold-main-summary.txt` (masked-identical **3/3 for all 11 arms × both variants**), `folded-battery-summary.txt` (nav 11/11 twice) |
| F2 | **The two teardown sinks are executed, not unreachable** — the live callback fires **2×** inside the arm's 3-frame window in both arms. So the correct disposition is "write-only store", not "dead code"; the crash is bound to the *registered* Callable, not to the body | info | `hits-probe.txt` (`R91S_HITS_CRASH 2` / `R91S_HITS_CLEAN 2`, 2/2 reps) |
| F3 | **The `sync` arm's gate cannot exhaust** — its 10-frame ladder pre-syncs the map, so with `SYNC_BOUND := 1` `sync` still PASSes while the other 7 gated arms **and** `agent` (own loop) go `STALE`+exit 2. Not a defect (the loud path exists and is reachable; nothing is mis-PASSed) but it means that arm's effective bound is ladder(10)+bound(48)=58 frames, not 48 | info (recorded for critic/verifier) | `fold-stale.txt` (`sync rc=0 pass_line=True`; `path/query/region/avoid/bake/link/agent rc=2 stale_line=True pass_line=False`) |
| F4 | **The boundary fold was load-bearing, measured**: tails really do vary — `region settle` 4↔5, `agent first_reachable` 4↔5, `avoid seq_a/seq_b/vel_a/vel_b` 4 distinct values, `avoid sum_max` ∈ {19.8402, 19.8426, 20.0000}. Had any of them stayed pinned the row would flake | info (fold verification) | `committed-tail_variance.txt` |
| F5 | **The `required_stderr` pin is a live discrimination instrument, and deleting it would be invisible on the happy path**: happy path PASS; the same `rc=-6` with a non-glibc stderr **FAILs** only through this clause; deleting the entry leaves the row PASSing (so no gate would catch the deletion) | info (keep, audited) | `committed-required_stderr_liveness.txt` (Q1 PASS / Q2 FAIL / Q3 PASS, production `classify_process` AST-extracted from the committed harness) |
| F6 | **Harness insertion is insertion-only** (+88/−0), the r91 floor gate is **non-redundant** (no other gate's prefixes cover `nav_lattice_`), both allowlist entries matched **exactly once** with `bare_rejects=True`, `dead_entry_count=0`, all gates true | info | `committed-audit.txt`, `committed-key_and_pin_census.txt`, `committed-gates.txt` |
| F7 | **Custody**: a foreign in-flight edit appeared in the working tree at 20:24–20:25 local (an r92 `tilemap_lattice` lane: `run_battery.py` +161 lines, new `tilemap_lattice.gd`). All this seat's r91 receipts are against the committed bytes — proven by the control run's launch snapshot (`scratch/nav_lattice.gd` = `088843399…`) and by re-running every audit against `committed-fixtures/`. The third battery run necessarily exercised the foreign harness (272 rows incl. 14 tilemap rows); it is reported as such, and no r91 claim rests on it | info | `committed-fixtures/`, `runs-control/*/scratch/nav_lattice.gd`, `control2-summary.txt` |

## 3. The fold question — candidates audited

Method: (a) scope-aware **write-only-store** scan over every `var`/`const`
(file scope + per function, assignment-target aware); (b) **arm↔row bijection**
+ **function/call-site** census; (c) **pin↔emission** prefix census on the real
run; (d) direct reading of every statement that writes node/server state, asking
"can this change any pinned byte?"; (e) execution for every candidate that
survives (a)–(d).

| # | candidate | verdict | proof / reason |
|---|---|---|---|
| SP1 | `const SETTLE := 10` `:56` (−1 line) | **FOLD PROPOSED** | Zero reads file-wide **and** zero reads in the scout probe it was inherited from (`corpus/live/r91-scout/probes/nav_lattice.gd:21`) — the orphan of the settle-counting design that the boundary fold replaced with the `iteration_id >= 2 AND reach` gate (`SYNC_BOUND`). **Independently found, not new**: the committed reviewer's F4 (`reports/round-91/r91-reviewer.md:208-210`, commit `7330589`) records the same dead const and refers it to this seat. My added value is the executed byte-neutrality proof the reviewer did not run: `foldA` vs control **masked-identical 3/3 for all 11 arms**, and the full battery on the folded bytes is nav 11/11 twice (§6) |
| SP2 | append-only `hits` sinks in the two teardown arms `:851`/`:854-855` and `:871`/`:874-875` (−2 lines) | **FOLD PROPOSED** | The arrays are never value-read (only `append`); the callback still fires (F2) and the crash is bound to the registration: `foldB` receipts are **raw-byte-identical 3/3** for both arms — same marker stdout, same `double free or corruption (!prev)` stderr, same `rc=-6`/`rc=0` (§6) |
| SP3 | `_arm_sync` async=false sub-block `:276-284` + `:308-309` (−~10 lines, only product is the `first_reach_sync` tail field) | **rejected** | It is the **sole in-fixture instrument** behind boundary §2.2 (`r91-boundary.md:144-157`: "`use_async_iterations=false` is not a 'f1' guarantee", measured 26–≥40 frames at ff120) and is cited in `r91-scribe.md:156`; deleting it unbacks a cited, already-falsified claim (r90-SP2/SP3 class) |
| SP4 | `NavigationPolygon.new().get_method_list().size()` `:164` — a second instance where `poly` (`:158`) already exists | **rejected** | Provably identical (class-level method list) but **not a deletion**: 0 lines saved, 0 battery bytes, and it stales the probe sha cited by two tracked files (r90-SP7 "refactor with zero byte gain" class) |
| SP5 | unknown-arm fallback `:152-153` (prints a PASS-shaped line, exits 0) | **rejected** | Defensive loudness class (r89-SP7). Audited note: a mistyped `--arm` produces `PASS nav_lattice unknown arm=…`, which satisfies **no** row signature (all pins start `PASS nav_lattice <arm> `), so the battery still rejects it loudly |
| SP6 | Every other emitted field (all `settle/iter/ladder/first_reach*/gate/chg_iter_*/dis_same/fwd_disabled_same/walk_steps/reached_at/first_reachable/iter_b/link_iter/seq_*/vel_*/sum_max`) | **rejected** | These are the boundary fold's measurement surface, cited by the scribe's tail table and by boundary §2/§3/§6; and they are the fields that measurably vary (F4). Deleting diagnostics is not a YAGNI deletion — it removes evidence (r90-SP9 class) |
| SP7 | r91 CASES rows, `expected_errors` entries, `required_stderr` entry, `r91_expected_errors_all_matched` gate | **rejected** | All live: 11/11 rows PASS; both entries `matched_lines=1`, `dead_in_run=false`, `bare_rejects=True`; the `required_stderr` entry flips a cause-counterfactual to FAIL (F5); no other gate covers the `nav_lattice_` prefix (F6) |
| SP8 | CLI knobs: `_arg("arm", …)` is the only knob read; all 11 rows pass `['--arm=…']` only | **rejected (nothing dead)** | No `--frames`/`--fixed-fps` dependency inside any r91 pin; `_arg`'s default parameter is exercised by `_arg("arm", "census")` |
| SP9 | Defensive/default tails in helpers (`_arg` default, `_v`/`_path`/`_ps`/`_pia` formatting, `_reach`'s `size()>0` guard) | **rejected** | All reachable/live: every helper has ≥1 call site (`committed-audit.txt`); `_initialize` is the engine lifecycle entry (0 textual call sites, as in r90) |

**Conclusion.** The probe was written to the conventions the r89/r90 simplifiers
already pruned: no dead store other than SP1/SP2, no dead key, no dead gate, no
unreachable row path, and every line that *could* be deleted without proof turns
out to be an instrument (SP3), a family/coverage clause (SP7), or evidence
(SP6). The honest simplifier output is: **no fold beyond SP1+SP2**, and those two
are byte-neutral.

## 4. Landing integrity — the narrow check, on the committed bytes

- **Control battery** (committed bytes, `runs-control/20261015T224739373652Z`):
  **258/258 PASS**, zero flakes, `r91_expected_errors_all_matched=true`,
  `census_allowlisted_reproduces_verdicts=true`, `dead_entry_count=0`, all
  r87–r91/phys2d gates true.
- **Row identity vs the author's two green runs**: 258/258 common rows, **0
  verdict diffs, 0 exit diffs** in both comparisons; 11/11 nav rows identical.
- **Pin↔emission prefix census** (`committed-key_and_pin_census.txt`): for all
  11 rows the pinned signature is a **byte-exact prefix** of the emitted line,
  and everything after it is a declared diagnostic tail field →
  `ALL_PINS_ARE_BYTE_EXACT_PREFIXES_OF_EMISSION=True`; **0 unpinned emissions,
  0 pinned-but-unemitted fields**.
- **Cross-session pin identity**: each row's masked pinned block equals the
  author's 3 fresh reps **and** both author green runs → `TOTAL_MISMATCHES=0`
  (6 independent receipts per row).
- **Mechanical census**: 11 rows ↔ 11 dispatch arms (no orphan row, no orphan
  arm, no duplicate case, no non-nav row using `nav_lattice.gd`); all 26
  functions accounted for; 13 print sites = 10 PASS lines + 1 crash marker +
  1 STALE + 1 unknown-arm fallback; the fixture's only knob is `--arm`.
- **Write-only-store scan**: exactly **1** file-scope store (`SETTLE`) and the
  two append-only sinks; every other `var`/`const` is read.
- **Allowlist / gate liveness**: `nav_lattice_sync` and `nav_lattice_bake`
  entries matched exactly once each, both rows `bare_classification_rejects=true`
  and `allowlisted_classification_passes=true`; `dead_entry_count=0`;
  `r91_expected_errors_all_matched` is the only gate covering the prefix.
- **Substring-artifact note** (`pre_iter=` vs `iter=`): the committed reviewer's
  F5 (`r91-reviewer.md:213-220`) and the labrat's independent scan both flagged
  the pinned `pre_iter=0` as textually containing the token `iter=`. It is not a
  scheduler field — a pre-sync read taken before the first physics frame
  (structurally 0, measured 0 in 61/61 boundary gate runs) — and this seat's
  census/audit match tail-field names with a word boundary, so it is not counted
  as a tail field inside a pin.

## 5. Boundary folds re-verified on the landed bytes

| fold | claim | receipt |
|---|---|---|
| 1 | scheduler/rate fields are **never** inside a pin; every pinned token is a prefix and the tail is last | static (labrat H1/H2 + prefix census) **and** dynamic: pins identical across 6 receipts/row while tails vary (`region settle` 4↔5, `agent first_reachable` 4↔5, `avoid seq_*/vel_*` 4 distinct) — `committed-tail_variance.txt`, `committed-cross_session_pins.txt` |
| 2 | sync-gate exhaustion is a **loud** failure, never a PASS-shaped payload off an unsynced map | `SYNC_BOUND := 1` probe: `path/query/region/avoid/bake/link/agent` → `STALE nav_lattice <arm> sync_bound_exhausted bound=1` + **exit 2**, **no PASS line** (2/2 reps each); the gate code is `iteration_id >= 2 AND reach` with the bound as a failure surface (`_stale()` sets `_exit_code=2`). Caveat F3: the `sync` arm pre-syncs via its 10-frame ladder, so it is not exhaustible at bound=1 (its loud path still exists at bound=48) |
| 3 | same-frame OLD-answer reads (`dis_same`, `fwd_disabled_same`) are race fields, unpinned | prefix census shows both only in tails; `chg_same=false` stays pinned |
| 4 | `is_navigation_finished()` is read **before** `is_target_reached()` every frame | source `:561-568` (`fin_now = ag.is_navigation_finished()` then `if reached_at < 0 and ag.is_target_reached()`); `reached_at`/`walk_steps` remain tails; the pin carries only the order-independent final state (`fin=true reached=true reachable=true`) |
| 5 | avoidance invariants are asserted probe-side, split digits unpinned | pin carries `sum_bound_ok=true dirs_ok=true`; `seq_*`/`vel_*`/`sum_max` are tails; measured `sum_max` ∈ {19.8402, 19.8426, **20.0000**} — at the ORCA bound, below the 20.001 assertion (1e-3 slack) |
| 6 | teardown crash arm + `required_stderr` on `rc=-6` | control run: row `actual_exit=-6`, stdout marker present, stderr `double free or corruption (!prev)`; production-classifier liveness Q1 PASS / Q2 FAIL / Q3 PASS; `teardown_clean` discipline control `survived=true has_cb=false` exit 0 |

## 6. The proposed fold (SP1+SP2) — patch, proof, cost

`fold-proposal.diff` (also `fold-battery-project/nav_lattice.gd`, 880 lines,
sha `b23887e5b05d830629689010baf8bf5ed044e32548831945fe134983cd07450e`); the
exact unified diff is in the receipt — abridged here (`…` = elided context):

```
--- a/corpus/fixtures/nav_lattice.gd
+++ b/corpus/fixtures/nav_lattice.gd
@@ -53,7 +53,6 @@
 #  - map_get_random_point() is random per call (not pinnable).
 
-const SETTLE := 10
 const SYNC_BOUND := 48
@@ -848,11 +847,10 @@ func _arm_teardown_crash() -> void:
 	var a := NavigationServer2D.agent_create()
-	var hits: Array[Vector2] = []
 	...
-	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
-		hits.append(v))
+	NavigationServer2D.agent_set_avoidance_callback(a, func(_v: Vector2) -> void:
+		pass)
@@ (same 2-line change in _arm_teardown_clean)
```

**Proof of byte-neutrality (executed, not argued):**

- `foldA`/`foldB` vs control, battery launch shape, 11 arms × 3 reps each:
  **MISMATCHES=0** with declared tails masked — masked-identical **3/3 for every
  arm × variant**; 32/66 receipts raw-byte-identical, the rest differ only in
  declared tails or in the GDScript **backtrace line numbers** that any deleted
  line shifts (`nav_lattice.gd:234` → `:233`). No signature, `expected_errors`
  entry or `required_stderr` fragment references a line number (the two ERROR
  entries are exact sentences; the crash fragment is a glibc string), so the
  harness cannot see it.
- Teardown arms specifically: `foldB` raw-byte-identical **3/3** — same stdout
  marker, same stderr, same `rc=-6`; `teardown_clean` raw-identical 3/3 with
  `has_cb=false` and exit 0.
- **Full 258-row battery on the folded bytes, twice**: `nav_lattice` **11/11
  PASS both runs**, `r91_expected_errors_all_matched=true` both runs. The
  full-battery verdict flipped only on the **documented volatile classes**
  (`audio_bus_route` in run 1; `negative_transition` + its `probe_error_clause_surface`
  cascade in run 2 — the same two dead entries r90 recorded), rows that execute
  other fixtures and never load `nav_lattice.gd`. Under the same (rising) load,
  a later battery run — working tree then holding the committed 258 rows **plus
  14 uncommitted foreign r92 tilemap rows**, 272 rows — was **272/272 PASS**
  (`control2-summary.txt`), i.e. the volatile classes appear and disappear
  independently of this fold.

**Cost (honest accounting).** −3 lines; the landed fixture sha `088843399…`
becomes `b23887e5…`, which stales the sha quoted in `reports/round-91/r91-author.md:19`
and in the author's own `corpus/live/r91-author/manifest.sha256` entries (both
**historical** receipts — nothing *live* cites the landed sha; the harness cites
the scout sha `efb496e5…` for a different file). Applying it also means a new
commit and, per the r89 precedent (fold `53a0be7` → `r89-verifier-r2`), a
re-verification pass against the new sha. **This seat does not apply it**: the
assignment says zero tracked writes / commit nothing, and the shipping decision
belongs to the operator/integrator. If the gate prefers "no churn on a verified
sha" (the r90-SP1 trade), the fallback disposition is *record-and-keep*; the
finding is then a documented, proven-clean wart rather than a defect.

## 7. Tradeoff and stop line

- **Patch proposed, not applied** (SP1+SP2, −3 lines, §6). Everything else that
  could be deleted is an instrument (SP3), a coverage clause (SP7), or evidence
  (SP6), and SP4/SP5 are audited-and-kept.
- **Stop line**: the next candidates would harm an axis — SP3 (backs a cited
  falsified claim), SP4 (zero-byte refactor that stales a cited sha), SP5
  (defensive loudness), SP6 (the fold's own measurement surface), SP7 (live
  rows/entries/gate). Stopped here.

## 8. Custody notes, residual risks, blockers

- **No tracked file written, no commit, no git mutation by this seat.** New
  files only: this report + `corpus/live/r91-simplifier/**` (manifest excludes
  regenerable scratch/run snapshot trees).
- **HEAD moved mid-session**: `77d2f7e` → `e3fd799` (scribe) → `7330589`
  (reviewer) → **`645fd8e`** (critic). The landing bytes are **unchanged** at
  HEAD (both fixture and harness byte-identical to `77d2f7e`), so this report's
  scope is unaffected. A foreign in-flight edit also landed in the working tree
  at 20:24–20:25 local (r92 `tilemap_lattice` lane: `run_battery.py` +161, new
  `tilemap_lattice.gd`) — outside my scope, recorded only. My control battery
  launched 19:47:39 and its launch snapshot is byte-proven to hold the committed
  bytes; every subsequent audit was re-run against `committed-fixtures/`.
- **Load**: 65 → 80 on 32 cores, 7 concurrent `godot` processes at peak (none of
  them mine — my batteries ran sequentially with `timeout -s KILL` bounds).
  Under this load the documented volatile classes flaked in the folded runs;
  the committed control run was clean 258/258, both folded runs kept nav 11/11
  and the r91 gate true, and the 272-row run (committed + foreign tilemap rows)
  was green end to end.
- **Residual risks**: (a) the SP2 change relies on the crash being bound to the
  *registered* Callable — measured identical today (12/12 receipts incl. the
  abort), but a future engine build that made the abort depend on the callback
  body would change the control (the same class of risk the author already
  flags for `teardown_clean`'s freed-RID read); (b) 4-dp geometry pins ride
  engine vertex order (author's own caveat class); (c) `census` pins are
  build-hash constants (flip loudly on an engine bump, intended); (d) the
  `sync` arm's gate is preceded by its 10-frame ladder (F3) — an observation
  for the critic/verifier, not a defect; (e) the committed critic's F1
  (`r91-critic.md:64`, medium-low: the 4-frame settle-state pins are
  60-tps-conditioned and reject under `--fixed-fps`) is open in the critic's
  lane — none of those pins is touched by this seat's fold.
- **Blockers: none.** The simplifier move is complete: landing audited clean,
  both folds re-verified, 2 provable deletions dispositioned with a patch, and
  every rejection carries a proof.

Seat output complete.
