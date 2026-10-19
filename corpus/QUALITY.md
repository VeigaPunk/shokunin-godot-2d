# game-dev-2d-shokunin — Quality bar

What good looks like in 2D game production verified by executable headless fixtures on Godot 4.7.2
(LEARNING.md). Grown only from lessons: every criterion cites the lesson that produced it
(`corpus/lessons/round-105.md` §Mistakes maps M-classes to rows). A criterion is replaced by a new
row naming the row it supersedes, never rewritten. Source tiers live in `corpus/SOURCES.md`
(contract rule 3: pointed to, not restated).

## Admission criteria

| # | criterion | why (lesson) | supersedes |
|---|---|---|---|
| Q1 | Cites a resolvable source: repo path, command output, or external document (a `corpus/SOURCES.md` row id for external material) | CORPUS.md evidence standard | — |
| Q2 | Falsifiable, or explicitly marked opinion | CORPUS.md | — |
| Q3 | Domain-specific (2D game production on Godot 4.7.2) — no generic agent advice | PROTOCOL.md invariants | — |
| Q4 | **headers.** Every knowledge entry admitted from r105 onward opens with `# title` then `source:`, `verified-at:`, `recheck:` lines, one each; check `grep -cE '^(source\|verified-at\|recheck):' corpus/knowledge/2026-10-19-*.md` → 3 per file. Inherited `seed.md` and `2026-10-12-production-checklist.md` remain legacy/unretrofitted, explicitly not counted as new admissions. | M16 · LOG.md:1287,1307 | — |
| Q5 | **runnable recheck.** The `recheck:` line holds a bounded command runnable from the lane root plus the exact `PASS …` prefix it must print; check by running it under `timeout` and matching that prefix. | M2 · LOG.md:169-172; M23 · LOG.md:1271-1278 | — |
| Q6 | **claim has a row.** Every behavioural claim names a CASES tuple `('<row>','<fixture>.gd',["--arm=…"],0,'<exact PASS line>')` that appears in both serial receipts; check `grep -c '<row>' corpus/fixtures/run_battery.py` ≥ 1 and the same PASS line in each `verdicts.json`. | M8 · SCORECARD.md:280 | — |
| Q7 | **discriminating control.** The positive must exercise the pinned mechanism (no muted `-`/`null` pinned field), the negative twin must start and end in an empty scratch and fail at the same assertion, and that FAIL must be the one distinguishing the claim; check the negative `reason=` names that assertion. | M1 · LOG.md:57; M22 · SCORECARD.md:158; seed.md:11-13 | — |
| Q8 | **serial-only receipts.** Admission evidence comes from serial battery runs, never concurrent launches; check for one receipt dir per run and no second battery overlapping it. | M26 · seed.md:14-15; M7 · LOG.md:1108-1111 | — |
| Q9 | **committed bytes.** The verdict cites the blob SHA it ran, landings are additive for evidence (no prior CASES expected string changes — harness code may change, pinned strings may not), and a post-commit replay writes a new unique receipt instead of overwriting the committed one; check `git rev-parse HEAD:<path>`, `git diff -U0 -- corpus/fixtures/run_battery.py \| grep -E "^-    \('"` empty, unique receipt paths. | M3 · SCORECARD.md:24; M17 · LOG.md:537; M18 · LOG.md:543 | — |
| Q10 | **row isolation.** A fixture whose state can leak proves its project/cache preconditions with reversed-order runs and a shared-project writer→reader control: identical fresh templates, unseeded shared baseline, then one explicit writer intervention; preserve both arms' raw results and require only the intervention arm to reproduce the named failure class. Do not infer within-family order dependence from a cache-seeded vs cache-less comparison. | M11 · LOG.md:1319-1320; M28 · run_battery.py:2526-2533 @e8990516; M29 · round-105 lesson | — |
| Q11 | **no fixed globals.** No fixture may pin a global port or path, and concurrency-safety ships a bind-loser negative; check `grep -nE '127\.0\.0\.1:[0-9]{4}\|localhost:[0-9]{4}' corpus/fixtures/*.gd` → 0 and the bind-loser row exists. | M7 · LOG.md:1108-1111 | — |
| Q12 | **dead tokens retired.** Every token a claim measures (`--flag`, receipt field) occurs at least once in the fixture that emits it, and a retired token's row is gone from CASES; check `grep -c -- '<flag>' <fixture>` ≥ 1 and `grep -c '<retired_row>' run_battery.py` → 0. | M8 · SCORECARD.md:280; M25 · LOG.md:1127-1128 | — |
| Q13 | **evidence at its link.** Every cited `corpus/...:line` resolves and the cited line carries the claim, and corrections append "adverse retained" instead of rewriting the cited text; check `test -f <path> && sed -n '<line>p' <path>`. | M9 · LOG.md:1196,1206 | — |
| Q14 | **ignore hygiene.** Ignore rules are verified by `git ls-files`, never assumed, and a round adds no file under `corpus/live/`; check `git diff --name-only <base> HEAD -- corpus/live \| wc -l` → 0 (the 40,677 legacy tracked live files are routed defect D11, not an admission blocker). | M14 · LOG.md:60 | — |
| Q15 | **scope and disposition.** Each seat states its write scope and touched files, and a failed seat's registered-but-unowned fixtures carry a disposition before close; check the touched-file list against `git status --porcelain` and each orphan's disposition line. | M13 · LOG.md:520; M10 · LOG.md:1254-1256; M21 · LOG.md:248 | — |
| Q16 | **no self-contradicting row.** A row may not carry a field contradicting its own pin (`matches_pinned=false`, unmapped census entry) and still be admitted, and a row retired after its last green run needs a fresh run or an explicit disclosed gap; check the receipt field and the disclosure line. | M24 · LOG.md:1321-1322; M12 · LOG.md:1323-1324 | — |
| Q17 | **resolution and margin.** A measurement states its grid resolution/ε and edge uncertainty, and a latency bound pins the measurable margin re-derived on host drift, not the constant alone; check the entry quotes both and the recheck re-measures both sides of the bound. | M4 · SCORECARD.md:64; M23 · LOG.md:1271-1278 | — |
| Q18 | **row-set integrity.** Every CASES name appears exactly once among CASES-backed results; other results are named meta/probe rows, counted separately and unique by name; the audit reads CASES/results, not mutable builder records — compare AST names with receipt identities/multiplicity, not total JSON rows against CASES count. | M19 · LOG.md:1204; M27 · LOG.md:1312-1313 | — |
| Q19 | **pins are claims.** Each pin names the mechanism it exercises and what would falsify it, and a refuted pin lands as a correction line naming the falsified clause; check the pin text and the correction. | M6 · SCORECARD.md:158; M5 · SCORECARD.md:81 | — |
| Q20 | **labels.** Evidence carries `[obs]`/`[inf]`/`[unk]` labels and no causal attribution is recorded as an observation, ledger corrections being appended with the original retained; check `grep -cE '\[(obs\|inf\|unk)\]' <entry>` ≥ 1 and the correction's append-only shape. | M20 · LOG.md:1266-1268 | — |
| Q21 | **tier floor.** A claim's `source:` line carries at least one A/B row scoped to that claim, tier-C rows corroborating only; check the ids against the `tier` column in `corpus/SOURCES.md`. | M4 · SCORECARD.md:64 | — |
| Q22 | **engine-clean observation.** A value returned by an engine call counts as an observation only if that call emitted no engine `ERROR:`; a pinned return that rides an allowlisted ERROR is a refusal receipt, never a coordinate/state fact — check the row's allowlist entry in `run_battery.py` against the fields its PASS line asserts | M15 · `tilemap_lattice.gd:727-741` + allowlist `run_battery.py:2817-2819` at `e8990516` (`ERROR: Parameter "found" is null.`) | — |
| Q23 | **finite-life probe adjacency.** New probes run before the crash/descendant tail, never between the detached-control launch and its meta liveness check; inspect the CASES dispatch call site and exercise the added probe plus the full tail→meta path under the unchanged `sleep 8` lifetime. Do not widen the lifetime or suppress a failed discrimination to accommodate extra work. | M32 · `reports/round-105/r105-scheduling-failure.json`; runner adjacency comments lines 99–102 at `7d9d9741` | — |

## Signals of weak material

| # | signal | why (lesson) |
|---|---|---|
| W1 | Harness prints PASS while the thing under test is broken or confounded (contaminated negative, cross-connected ports, shared state, muted pinned fields) | M1, M7, M11, M22 — the lane's recurring shape |
| W2 | A count quoted from a seat patch or report instead of re-run at the measured commit | M27 |
| W3 | A criterion or recheck that is command-shaped text never executed this round | M2, M25 |
| W4 | A source row with an `opened` date but no round-lesson `## Gate` quote | SOURCES-CONTRACT-v1 rule 1 |
| W5 | Determinism, isolation or "unreachable" asserted from one host/run without the control that could refute it | M5, M15, M28 |

## Check

```sh
grep -cE '^(source|verified-at|recheck):' corpus/knowledge/*.md      # Q4: 3 per entry
grep -hE '^recheck: ' corpus/knowledge/*.md                          # Q5: run each, match PASS prefix
grep -c '<row_name>' corpus/fixtures/run_battery.py                  # Q6: row is a CASES tuple
grep -n 'FAIL <stem> <arm> .*reason=' <run>/verdicts.json            # Q7: same-assertion negative
ls -d corpus/live/runs/*/ | wc -l                                    # Q8: one dir per serial run
git rev-parse HEAD:<path>                                            # Q9: blob SHA matches verdict
git diff -U0 -- corpus/fixtures/run_battery.py | grep -E "^-    \('"  # Q9: no pinned CASES row rewritten
grep -cE '<isolation_control_row_or_probe_flag>' corpus/fixtures/run_battery.py  # Q10: negative control exists
grep -nE '127\.0\.0\.1:[0-9]{4}|localhost:[0-9]{4}' corpus/fixtures/*.gd  # Q11: none
grep -c -- '<flag>' corpus/fixtures/<fixture>.gd                     # Q12: token really emitted
test -f <cited_path> && sed -n '<line>p' <cited_path>                # Q13: claim at its link
git diff --name-only <base> HEAD -- corpus/live | wc -l              # Q14: 0 new live files
git status --porcelain                                               # Q15: matches touched-file list
grep -c '<entry_field>' <receipt>                                    # Q16: no self-contradiction
python3 -c "import ast;t=ast.parse(open('corpus/fixtures/run_battery.py').read());print([len(n.value.elts) for n in ast.walk(t) if isinstance(n,ast.Assign) and any(getattr(x,'id',None)=='CASES' for x in n.targets) and isinstance(n.value,ast.List)])"  # Q18: CASES count
grep -cE '\[(obs|inf|unk)\]' corpus/knowledge/<entry>.md             # Q20: labels present
```
