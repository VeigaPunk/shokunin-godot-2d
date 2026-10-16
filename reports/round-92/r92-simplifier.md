# game-dev-2d round 92 — simplifier (r92-simplifier): the r92 TileMapLayer landing on committed `5900431` is audited clean — **zero provable YAGNI deletions** (0 write-only stores, 0 dead rows/arms/gates/knobs/entries), all four encoded folds re-verified on the landed bytes with fresh receipts, and the `expected_errors` floor gate proven **loud** under a dead-entry fold (+1 stale entry ⇒ row still PASSes, `r92_expected_errors_all_matched=False` ⇒ battery FAIL); **no patch proposed** (zero tracked writes)

Seat `SIMPLIFIER` (LEAF) | lane `r92` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Work commit **`5900431`** (r92 author: `corpus/fixtures/tilemap_lattice.gd`
929 lines `a699138945ec7c1c1e6c97b6bf052d0941596610ad4cb9d08d184c07409d3dfb` +
`corpus/fixtures/run_battery.py` +161/−0 `5e5182815e6e3c503f40c78b6416b5cf6aaf9d0d3ea3ed7577594bd9f35aa509`
+ author receipts/report, 272 rows). HEAD moved mid-session under the sibling
wave-B seats (`8a0da55` scribe → **`c3c0d16`** reviewer); the **landing bytes are
unchanged at HEAD** — `git show c3c0d16:corpus/fixtures/{tilemap_lattice.gd,run_battery.py}`
are byte-identical to `5900431` (both shas above re-verified), and the worktree
matches HEAD for both (`git diff --stat HEAD -- corpus/fixtures/` empty). **No
tracked file written, no commit, no git mutation by this seat.** Writes are this
report and `corpus/live/r92-simplifier/**` only. Host ran under heavy foreign
oversubscription throughout (loadavg 52–65 on 32 cores, 48 foreign `yes` hogs
ppid 1537 — none mine).

**`lsp` disclosure.** No `lsp` device is exposed in this dispatch and no
GDScript language server exists on this host (`gdlint`/`gdformat`/`gdscript-lsp`/
`gdtoolkit` absent — same finding as the r89–r92 seats; `which` exits 4). Symbol-aware
`references`/`definition`/rename were therefore **unavailable**; no cold result is
recorded as absence. Every caller/consumer claim below rests on (a) a complete
textual enumeration, (b) a scope-aware write-only-store scan, (c) a pin↔emission
census over real receipts, and (d) fresh-process byte comparison.

**Frozen probeParent.** Exactly **one** read-only `ufo-labrat` was dispatched
(agent `3c7e1d6b`, bounded, 4 falsifiable clauses, static scan only, no writes).
It returned **H2 CONSISTENT** (nav payload whitelist: neither-bucket empty,
`regions_f2=1` in every line), **H3 CONSISTENT** (4/4 nullts receipts: rc −6 +
stdout anchor + both stderr fragments), **H4 CONSISTENT** (no field other than
`regions_f1` varies anywhere it scanned), and **H1 REFUTED on the literal
"== 1 line per arm" for nav** — nav emits 2 lines by design (the envelope), its
own H2 then confirms both are whitelisted; its H1 holds for the other 12 arms.
Scope caveat: the probe's scan missed the gitignored `corpus/live/**/runs*/`
trees (it reported zero scout/boundary receipts where this seat's census finds
136) — its verdicts are valid for what it scanned; every count quoted below is
this seat's own full-worktree census. No other descendant was spawned.

---

## 1. Method and proof artefacts

`corpus/live/r92-simplifier/` (`MANIFEST.sha256`, **171 files**, sha
`517bc7b5c20e5a7beb0872daab86957144a9821d0c7bd3bb1ca5bae23efa3b2c`; run/scratch
snapshot trees excluded per r90/r91 precedent — the manifest covers scripts,
receipts, the committed snapshot and the folded tree):

| artefact | content |
|---|---|
| `committed-fixtures/` | byte-exact `git show 5900431:` snapshot of `tilemap_lattice.gd` (`a699138945…`) and `run_battery.py` (`5e518281…`); every audit below re-run against this snapshot |
| `runs-control2/20261016T002049177400Z/` | full battery on the **committed** tree: **272/272 PASS**, verdict PASS, `dead_entry_count=0`, all round gates true, r92 rows 14/14 |
| `runs-control/20261016T001620532378Z/`, `control-battery.stdout` | first full battery: 272 results, only the **documented volatile class** failed (`negative_transition` + its `census_bare_classifier_consistent` knock-on; `dead_entry_count=2`, both entries belonging to that flaked row) — r92 rows **14/14 PASS** |
| `fold-runs/`, `fold-verification.json`, `verify_folds.py` | 42 fresh launches: 4 scheduler modes × 3 reps (nav envelope), 3 nullts reps + counterfactuals, 9 allowlist liveness reps, 1 encoding rep, 13 PASS-arm reps, 4 cross-project nav reps; production `classify_process` AST-extracted (segment sha `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` — the author/boundary convention) |
| `pin-census-author5-control.txt`, `pin_census.py` | pin↔emission census over **6 receipts** (author runs1–5 + control1) × 14 rows |
| `envelope-census.txt`, `envelope_census.py` | worktree-wide nav-receipt partition (**147 receipts**) + per-arm distinct-line census |
| `error-coverage.txt`, `error_coverage.py` | ERROR:-line coverage census (18 entries vs every emitted line; entry-less rows) |
| `audit-static.txt`, `audit_static.py` | scope-aware write-only-store scan, function/print/arm/CLI census, harness r92 block census |
| `fold-gate/`, `fold-gate.diff`, `fold-gate-battery.stdout`, `runs-fold-gate/` | the **dead-entry fold** (+1 stale r92 entry, `e8a9590c…`) and its full battery run: `r92_tilemap_atlas` PASS **but** `r92_expected_errors_all_matched=False`, `dead_entry_count=1` naming the injected entry |
| `proj/`, `proj_tps120/`, `foreign-crash.err`, `geo2d-lineempty.err` | launch projects (60 tps / 120 tps) and the foreign-stderr counterfactual (Clipper2 SIGABRT, right rc class wrong cause) |

## 2. Verdict and findings (ranked)

**Verdict: PASS — the landing is audited clean and no YAGNI deletion is
provable; the four encoded folds are re-verified on the landed bytes, and the
floor gate is loud.** Unlike r91 (SETTLE const + 2 append-only sinks, −3 lines),
this fixture carries **nothing to delete**: the write-only-store axis is empty,
and every other removable-looking line turns out to be a claim, an instrument,
or evidence. 0 blockers.

| # | finding | severity | evidence |
|---|---|---|---|
| F1 | **Zero provable YAGNI deletions.** Scope-aware store scan over 138 declarations (file scope + per function, assignment-target aware): **0 write-only stores**; the fixture contains no `const`/`enum`/`signal`/`static`/`@export` at all (the r91-SETTLE class cannot exist); 14 rows ↔ 14 arms (bijection, no orphan/duplicate); 5 print sites; the only CLI knob read is `--arm=`; the fixture is a **byte-copy** of the frozen scout probe (sha re-verified: `a699138945…` == `corpus/live/r92-scout/probes/tilemap_lattice.gd` == `git show 7a45a60:` copy), whose sha is cited by two tracked files | info (clean) | `audit-static.txt`, `audit_static.py` |
| F2 | **The nav envelope is load-bearing, minimal, and mode-exact.** 4 scheduler modes × 3 reps: default & `--fixed-fps 120` ⇒ payload[0] matches, payload[1] does not; `--fixed-fps 150` & `600` ⇒ payload[0] **fails**, payload[1] matches; the row PASSes in all 12 launches. Across modes **exactly 1 of 19 fields varies** (`regions_f1` 0↔1). Cross-project control reproduces the ratio law independently: `ff240` at 60 tps ⇒ payload[1], at 120 tps ⇒ payload[0]. Worktree-wide: **147 nav receipts** partition payload[0]=97 / payload[1]=50 / neither=**0**, `regions_f2=1` in all 147, exactly 1 distinct line per payload | info (fold verified) | `fold-verification.json`, `fold-runs/`, `envelope-census.txt` |
| F3 | **The floor gate is loud, not decorative.** Fold: `+1` stale entry (`ERROR: … atlas has no tile at (99, 99).`) added to `r92_tilemap_atlas` in a copied harness. Full battery on the folded bytes: the row **still PASSes**, `census_bare_classifier_consistent` and `census_allowlisted_reproduces_verdicts` stay true, **but** `dead_entry_count=1` names exactly the injected entry and `r92_expected_errors_all_matched=False` ⇒ `probe_error_clause_surface` FAIL ⇒ battery FAIL. This is the r79-critic-C2 hole (dead entry passing silently) demonstrated closed on the r92 block, and the gate is **non-redundant** (no other gate's prefixes cover `r92_`; `dead_entry_count` is data, not gated) | info (gate live) | `fold-gate.diff`, `runs-fold-gate/20261016T002515612105Z/verdicts.json`, `fold-gate-battery.stdout` |
| F4 | **The nullts `required_stderr` pin is a live discrimination instrument whose deletion no gate catches.** 3 fresh reps: Q1 (genuine: rc −6 + stdout anchor + both fragments) PASS; Q2 (same rc class, foreign stderr — Clipper2 SIGABRT from `geo2d_lattice` lineempty, and a SIGILL `crash()` probe) **rejects**; Q3 (entry dropped entirely) **still PASSes** — so a silent deletion of the pair would be invisible to the harness (keep, audited; same shape as r91 F5). Cross-refs: reviewer F3 / scribe A1 record that the comment above the pin says "rc=-11" while the pinned exit is −6 (SIGABRT through the engine's signal-11 handler) | info (keep, audited) | `fold-verification.json` §C, `fold-runs/default/nullts.*`, `foreign-crash.err` |
| F5 | **Landing integrity on the committed bytes.** `runs-control2`: **272/272 PASS**, verdict PASS, `dead_entry_count=0`, `rows_with_expected_errors=68`, all 7 round gates + census gates true, **r92 rows 14/14**. `runs-control` (first run, same bytes): 272 results, only `negative_transition` (documented scene-install race under load) + its census knock-on failed; **r92 rows 14/14** and the r92 gate true there too. Cross-session pin identity over **6 receipts**: each of the 12 non-nav PASS rows emits exactly **1 distinct line** present 6/6; nav 1 line 6/6 (payload[0]); nullts 4 stdout diagnostics present 6/6; **0 varying fields** per line | info (integrity) | `runs-control2/…/verdicts.json`, `control2-battery.stdout`, `pin-census-author5-control.txt` |
| F6 | **0 uncovered ERROR: lines; all 9 allowlists load-bearing.** Every `ERROR:` line emitted by the 9 error-emitting arms is absorbed by its row's entries (fresh reps: `TOTAL_UNCOVERED_ERROR_LINES=0`); the 5 entry-less rows (`census`/`timing`/`quadrant`/`nav`/`nullts`) emit **no** `ERROR:` line; `nav`'s only stderr is the `make_polygons_from_outlines()` deprecation WARNING (classifier-inert, scout hazard #11 unchanged). For all 9 rows on fresh reps: bare classifier **rejects**, allowlisted **passes** (entries are necessary and sufficient) | info (audited) | `error-coverage.txt`, `fold-verification.json` §D |
| F7 | **Tombstone encoding decodes exactly as pinned** (independent decode of the landed row's raw bytes): header `[0,0]` + 12-byte LE records `(x,y,source_id,atlas_x,atlas_y,alternative)`; `erase_cell` writes an **in-place tail-0xFF tombstone** (source/atlas/alt = −1) with x,y **preserved** and length unchanged (14→14); `clear()` == erase for every record; a post-clear write **appends** at the high-water mark (14→26); `stride=12`; `two_arr_equals_bytes=1` | info (fold verified) | `fold-verification.json` §E, `fold-runs/default/encoding.out` |
| F8 | **Payload[1] is unreachable in the battery's own launch shape** (default scheduler puts the first physics step before any idle frame; only `--fixed-fps` crosses the boundary, and the battery passes no such flag). It is *not* a deletion candidate: payload[0]-only rejects 2 of the scribe's 416 boundary receipts and 4 of this seat's ff-class receipts — deleting it re-breaks the boundary-falsified fixed pin. Recorded as the envelope's price, cross-referenced to the committed reviewer's F2 | info (keep; cross-ref) | `fold-verification.json` §A, `envelope-census.txt`, `r92-reviewer.md` F2 |
| F9 | **The fixture's `# --- nullts (hazard, not a row)` section comment is now locally stale** (the landing classifies it as a row, `r92_tilemap_nullts_crash`). Any fixture edit would stale the probe sha cited in the harness comment + author report **and** move the `_nullts … :927` required_stderr pin (author-disclosed, deliberate). Recorded as a documentation nit; the harness comment and author report carry the promotion rationale. No action (r90-SP7 zero-gain-edit class) | info (doc nit) | `committed-fixtures/tilemap_lattice.gd:917`, `reports/round-92/r92-author.md` fold 3 |
| F10 | **The 20 s watchdog cannot fire inside the battery** (the harness kills any script at 8 s) but is the intended guard for the manual/boundary launch shapes (`timeout ≤ 25 s`). Defensive loudness — keep (r89-SP7 class); the committed scribe §10.6 concurs | info | `committed-fixtures/tilemap_lattice.gd:113`, `run_battery.py:909` |
| F11 | **Cross-seat classifier-extraction convention mismatch (custody nit).** The r92-scribe reports `classify_process` segment sha `13473e6def6cd2da…`; the author's `verify_author.py`, the boundary's `verify_r92b.py` and this seat's AST extraction all produce `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` on the same committed bytes (I also tried dedent/`+\n`/regex-span variants — none reproduces `13473e6d`). The classifier source is unchanged (worktree == HEAD). Info for the adjudicator: pin the extraction convention (AST `FunctionDef` source segment) | info (custody) | `pin_census.py` output header, `corpus/live/r92-author/verify_author.py`, `r92-scribe.md` §4.2 |

## 3. The fold question — candidates audited

Method: (a) scope-aware **write-only-store** scan over every declaration
(file scope + per function, assignment-target aware); (b) **arm↔row bijection** +
**function/call-site/print-site/CLI-knob** census; (c) **pin↔emission** census on
the real run (6 receipts); (d) direct reading of every statement that writes node/
server state, asking "can this change any pinned byte?"; (e) execution for every
candidate that survives (a)–(d).

| # | candidate | verdict | proof / reason |
|---|---|---|---|
| SP1 | `regions_f1=…` token in **both** nav payloads (−2 fields) | **rejected** | Deletion-invisible: with the token gone the row would still pass in all 4 modes measured (payloads then differ in nothing) — but it is the **one-step registration claim**, cited by the author report (fold 1), boundary §4.1, and the harness comment; deleting it removes the measurement that *motivated* the envelope (r91-F5 / r91-SP6 class). Audited note: this is the only harness-invisible pin in the landing |
| SP2 | nav **payload[1]** (−1 payload) | **rejected** | Required for the `--fixed-fps ≥150` class: payload[0]-only rejects the 2 ff600 boundary receipts (scribe's 416-receipt matrix) **and** this seat's ff150/ff600/ff240/t120-ff480 receipts. Deleting it re-introduces the exact fixed-frame pin the boundary falsified (reviewer F2) |
| SP3 | the 3 non-signature `R92 nullts …` diagnostics (`tileset_null`, `used_after_set`, `src_after_set`) | **rejected** | They are the scout §5.1 hazard receipt (quoted verbatim) and the trigger-precondition evidence ("both halves"); deleting them changes stdout bytes and removes evidence for zero gain (r91-SP6 class) |
| SP4 | `_fail("empty_arm")` / `_fail("unknown_arm")` fallbacks | **rejected** | Defensive loudness (r91-SP5 class); a mistyped `--arm` satisfies no row signature, so the battery still rejects loudly |
| SP5 | the 20 s watchdog timer + its lambda | **rejected** | Reachable in manual/boundary shapes (`timeout 25`), unreachable in the battery (F10) — a guard, not dead weight |
| SP6 | `layer.free()` in `_census` | **rejected** | The only arm that does not add its layer to the tree; deleting `free()` leaks an ObjectDB instance (observable output change + hygiene), 0 lines saved |
| SP7 | `_mk_tileset`'s `"src"`/`"sid"` dictionary keys (unused by 4 of 10 callers) | **rejected** | Shared helper; no line saved, no byte change, and any edit stales the probe sha cited in two tracked files (r90-SP7 zero-gain-refactor class) |
| SP8 | the fixture ↔ scout-probe duplicate (929 lines × 2) | **rejected** | The scout copy is the provenance of record (path + sha cited by the author report and the harness comment); seat receipts under `corpus/live/<seat>/` are the repo convention (r87–r91) |
| SP9 | the harness's ~50-line r92 comment block | **rejected** | It **is** the fold encoding (payload[0] = production mode, the threshold, the nullts binding, the tombstone law, the insertion-position rationale); deleting it orphans the envelope's justification (r91-SP6 class: evidence) |
| SP10 | r92 CASES rows (14), `expected_errors` (18 lines / 9 rows), `required_stderr` (1 row), floor gate | **rejected (nothing dead)** | 14/14 rows PASS on the committed bytes; all 18 entries matched with `bare_rejects=True` on fresh reps and 0 uncovered ERROR lines; the required_stderr pair flips a same-rc foreign crash to FAIL (F4); the gate flips on a dead entry (F3) and no other gate covers the prefix |
| SP11 | helper/duplication refactors with zero byte gain (e.g. `_mk_tileset` reuse in `_atlas`/`_srcids`, method-count probe dedup) | **rejected** | 0 lines saved, 0 battery bytes, stales the cited probe sha (r90-SP7 class) |
| SP12 | *the honest negative* | **no fold** | Nothing survives (a)–(e): the 929-line fixture is a measurement probe where every emitted field is a pinned claim, and the store axis is empty |

**Conclusion.** The r92 landing has **no provable YAGNI deletion**. The only
removable-looking weight is either an instrument (SP1/SP2/SP5), evidence
(SP3/SP9), a family/coverage clause (SP10), or a zero-gain refactor (SP7/SP8/SP11).
Contrast r91, where two deletions were provable and proposed. The honest
simplifier output here is: **nothing to cut**, and the four folds verified below.

## 4. Landing integrity — the narrow check, on the committed bytes

- **Control battery (green)**: `runs-control2/20261016T002049177400Z` —
  **272/272 PASS**, verdict PASS, `dead_entry_count=0`, `rows_with_expected_errors=68`,
  all gates true (`census_*` 3/3, `phys2d_`/`r87_`…`r92_expected_errors_all_matched`),
  r92 rows 14/14 (`actual_exit ∈ {0, −6}`).
- **Control battery (flake-only)**: `runs-control/20261016T001620532378Z` —
  272 results, the only failing row is `negative_transition` (the author-documented
  scene-install race under load) plus its `census_bare_classifier_consistent`
  knock-on (`dead_entry_count=2`, both entries on that row); r92 rows 14/14 and
  the r92 gate true.
- **Pin↔emission census** (6 receipts × 14 rows): the 12 non-nav PASS rows emit
  exactly **1 distinct line** each (present 6/6, byte-identical — **no tail
  fields at all**, a stronger shape than r91's prefix+tail pins); nav 1 line 6/6;
  nullts 4 diagnostics 6/6; per-line field variance **0**.
- **Mechanical census**: 265 CASES tuples, 14 `r92_tilemap_*` rows contiguous
  ahead of the crash/descendant tail (the sleep-8 adjacency comment holds);
  insertion is **+161/−0**; `project.godot` untouched by the commit (0 occurrences
  in `git show --name-only 5900431`, worktree identical to HEAD); 26 functions
  accounted for (only `_initialize`/`_run` have no textual call site — engine
  lifecycle + `call_deferred` string, as in r90/r91); 277 `_it(` sites.
- **Allowlist / gate liveness**: 18/18 entries live, `bare_rejects=True` for all
  9 rows on fresh reps; `dead_entry_count=0`; the r92 gate is the only floor
  covering `r92_`; the dead-entry fold flips it (F3).

## 5. The four encoded folds re-verified on the landed bytes

| fold | claim | receipt |
|---|---|---|
| 1 | `r92_tilemap_nav` is a **2-payload envelope on `regions_f1`**; payload[0] = production mode | default & ff120 → payload[0] only (3/3 each); ff150 & ff600 → payload[1] only (3/3 each); row PASS 12/12; **only 1 of 19 fields varies** across modes; 147-receipt partition 97/50/**0**, `regions_f2=1` everywhere; cross-project ratio control (ff240: 60 tps → payload[1], 120 tps → payload[0]) |
| 2 | `r92_tilemap_nullts_crash`: rc **−6** + stdout anchor + `required_stderr` pair binds the crash to *this* null-deref | 3/3 fresh reps rc −6, anchor present, both fragments on stderr; Q2 foreign same-rc stderr (Clipper2 SIGABRT / SIGILL probe) **rejects**; Q3 entry dropped still PASSes (deletion-invisible, keep); comment-vs-pin `-11`/`-6` prose defect cross-refs reviewer F3 / scribe A1 |
| 3 | Tombstone encoding pinned verbatim | independent byte decode (F7): header `[0,0]`, 12-byte LE records, in-place tail-0xFF erase with x,y preserved, `clear()` == erase, high-water-mark append, `stride=12`; byte-stable 6/6 receipts |
| 4 | `expected_errors` +9 with the floor gate | 9 rows / 18 exact lines, all matched, 0 uncovered ERROR lines; entry-less rows emit none; **fold**: +1 stale entry ⇒ row PASS, census gates true, `dead_entry_count=1` (named), `r92_expected_errors_all_matched=False` ⇒ battery FAIL |

## 6. The proposed fold: **none**

No deletion survives the candidate audit (§3). This seat therefore proposes **no
patch** — unlike r91, where two byte-neutral deletions were provable and attached.
The landing is at its minimal provable weight on the axes this seat can measure
(store scan, row/arm/gate/knob bijection, entry liveness, field variance), and
every remaining removable-looking line is load-bearing as instrument, evidence,
or coverage. If the round is ever re-opened, the only actionable items are the
*precision* notes others already filed: reviewer F2 (payload[1] unreachable in the
battery shape — add a mode discriminator if discrimination matters), scribe A1 /
reviewer F3 (the `-11`/`-6` comment prose), scribe A9 (the unmeasured 2–2.5 ratio
band), and F11 (pin the classifier-extraction convention).

## 7. Evidence index

`corpus/live/r92-simplifier/` — `MANIFEST.sha256` (171 files, sha
`517bc7b5c20e5a7beb0872daab86957144a9821d0c7bd3bb1ca5bae23efa3b2c`):

| artefact | path |
|---|---|
| committed snapshot (byte-exact) | `committed-fixtures/{tilemap_lattice.gd,run_battery.py}` |
| green battery (272/272) + flake-only battery | `runs-control2/20261016T002049177400Z/verdicts.json`, `control2-battery.stdout`, `runs-control/20261016T001620532378Z/`, `control-battery.stdout` |
| dead-entry fold + its battery | `fold-gate.diff`, `fold-gate/run_battery.py` (`e8a9590c…`), `runs-fold-gate/20261016T002515612105Z/verdicts.json`, `fold-gate-battery.stdout` |
| fold verification (envelope/nullts/allowlist/tombstone/fresh rows) | `fold-verification.json`, `fold-verification.log`, `fold-runs/`, `verify_folds.py` |
| censuses | `pin-census-author5-control.txt`, `envelope-census.txt`, `error-coverage.txt`, `audit-static.txt` + their scripts |
| launch projects / counterfactual stderr | `proj/`, `proj_tps120/`, `foreign-crash.err`, `geo2d-lineempty.{out,err}` |
| source reports | `reports/round-92/r92-{scout,boundary,author,scribe,reviewer}.md` |
