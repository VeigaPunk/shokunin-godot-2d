# game-dev-2d round 91 — scribe (r91-scribe): wave-B evidence custody + claim audit on committed `77d2f7e`

Seat `SCRIBE` (LEAF) | lane `g2d-r91-scribe` | round 91 | host **devin**.
Read-only audit of the r91 nav_lattice dossier: **no tracked file written, no
commit, no runtime config mutated**. The only writes are this report (new,
untracked) and `corpus/live/r91-scribe/**`. Every number below was recomputed
from the receipts on disk or from a fresh launch on the committed bytes;
nothing is quoted from the reports under audit without re-derivation.

Audit-time repository state: HEAD **`77d2f7e`** (*r91 author: 11 nav_lattice
rows (258 total) — iteration_id gate, scheduler fields to tails, query-order
fix, teardown crash armed rc=-6; 258/258 x2*). `git status --porcelain -uno`
was **empty** at audit start (22:47Z, before my first run) — clean worktree of
tracked files. By 23:25:53Z (the file's mtime when I first observed it) a
**concurrent sibling lane (r92 author)** had added +161 lines to
`corpus/fixtures/run_battery.py` (CASES 251 → 265, r92 tilemap rows); §9.1
verifies that every r91 landing block is **byte-identical** to `HEAD` and that
none of my evidence depends on the modified bytes. The
dossier reports are themselves tracked: scout `af38c696…`, boundary
`110f6817…`, author `b1574b80…`, all equal to `git show HEAD:`.

**Custody verdict: HOLDS.** All three manifests verify completely
(398/398, 1632/1632, 642/642) and each covers every artefact in its directory
except itself. Every claim class I could recompute reproduces — including
**two independent fresh battery runs on the committed bytes** (worktree at
`77d2f7e` and a `git archive HEAD` extract), in which the **r91 surface is
11/11 in both** with the r91 floor gate `true`. All 11 landed nav pins are
**prefix-exact in both runs**, and every rep-to-rep difference lands in a
declared diagnostic tail. **No landed pin, envelope payload, allowlist entry,
gate key, or verdict is falsified.** Two low-severity label/range items (A1,
A2), five info items (A3–A7) and two environment notes (A8, A9) are recorded;
none touches the landing.

---

## 0. What was run (method)

| # | check | command shape |
|---|---|---|
| 1 | manifest verification (all three) | `sha256sum -c manifest.sha256` in `corpus/live/r91-{scout,boundary,author}` |
| 2 | manifest completeness | entry set vs `os.walk` file set per dir (`audit/static_folds.py`) |
| 3 | committed-tree identity | `sha256sum <worktree>` vs `git show HEAD:<path> \| sha256sum`; `git show --numstat 77d2f7e` |
| 4 | CASES / row arithmetic | AST parse of `run_battery.py` at `HEAD` and in the worktree; tuple source segments compared |
| 5 | **fresh battery run 1 (worktree, committed bytes, under load)** | `python3 corpus/fixtures/run_battery.py --runs corpus/live/r91-scribe/battery-runs` (stamp `20261015T224801439124Z`, loadavg 65.8 at launch, 48 foreign `yes` hogs) |
| 6 | **fresh battery run 2 (`git archive HEAD` extract, shas verified)** | same harness from `/home/vgpnk/r91-committed-extract` → `corpus/live/r91-scribe/battery-committed/` (stamp `20261015T232338091246Z`) |
| 7 | cross-run tuple comparison | `audit/compare_runs.py` (row-by-row, pin-region vs tail-region) |
| 8 | static fold verification | `audit/fold_check.py`: 11 fresh single-arm launches (`fresh/`), pin-prefix + tail-token placement + PASS-line census |
| 9 | teardown-binding falsification | `audit/forge_test.py`: production `classify_process` AST-extracted from the committed harness, 5 synthetic variants |
| 10 | author fresh-rep re-derivation | `audit/author_fresh.py` over `corpus/live/r91-author/fresh-reps` (11 arms × 3 reps) |
| 11 | boundary receipt census + claim recompute | `runs/*.rc` census, teardown arm matrix, avoidance samples, gate ladders, `d_v9`/`d_bent`, `rc-summary.txt` |
| 12 | scout receipt recompute | per-cell `out_uniq`/`err_uniq`/rc, `analyze_r91.json` agreement, loadtest census |
| 13 | **`--fixed-fps` mode probe (mine)** | landed fixture under `--fixed-fps 30/120`, arms agent/path/sync (`fixedfps/`) |

No `lsp` device and no GDScript language server on this host (unchanged state,
same as all audited seats); no symbol edits were performed. All probe launches
were `timeout -s KILL 25`-bounded. The frozen-`probeParent` labrat allowance
(one read-only dispatch) was **not used**: the one bounded hypothesis I would
have delegated (does the `rc=-6` teardown row reject a forged crash?) is
directly testable with the production classifier on this host, and I ran it
myself (§4.3) — recorded as a deliberate non-dispatch, not an omission.

---

## 1. Custody table — manifests, git tracking, verdict

| dossier artefact | manifest | verification | completeness | git state at audit |
|---|---|---|---|---|
| `corpus/live/r91-scout/` | `manifest.sha256`, **398 entries** | **398/398 OK** | exact — only the manifest itself is unlisted | 12 tracked / 399 on disk (`runs/` ignored by `corpus/live/.gitignore:1`) |
| `corpus/live/r91-boundary/` | `manifest.sha256`, **1632 entries** | **1632/1632 OK** | exact | 13 tracked / 1633 on disk (`runs/` ignored) |
| `corpus/live/r91-author/` | `manifest.sha256`, **642 entries** | **642/642 OK** | exact | 100 tracked / 643 on disk (99 fresh-rep files + manifest tracked; `runs1/`,`runs2/` ignored by `corpus/live/.gitignore:5` `runs*/`) |

The two green author runs (`runs1/20261015T223815564642Z`,
`runs2/20261015T224213073214Z`, 48 MB) are therefore **worktree-only custody**
— manifest-covered, not tracked (same convention as prior rounds; A7).

---

## 2. Committed-tree identity + two fresh runs on the committed bytes

Worktree bytes == committed bytes for every landing file (so "committed tree
only" holds for all execution below):

| file | sha256 | worktree vs `git show HEAD:` |
|---|---|---|
| `corpus/fixtures/nav_lattice.gd` | `088843399ce37eb2…` (author claim) | **SAME** |
| `corpus/fixtures/run_battery.py` | `f5725ca441565b8c…` | **SAME** (at audit start; see §9.1) |
| `corpus/fixtures/project.godot` | `8de8b3af9cc737ed…` (untouched) | **SAME** |
| `reports/round-91/r91-{scout,boundary,author}.md` | `af38c696…` / `110f6817…` / `b1574b80…` | **SAME** |
| the three `manifest.sha256` | `f0ffab9a…` / `e6785e05…` / `d4cb0a3d…` | **SAME** |

`git show --numstat 77d2f7e` = `882/0 nav_lattice.gd`, `88/0 run_battery.py`
(insertion-only), plus the 99 fresh-rep files + manifest + report.

**Fresh battery run 1** — worktree at `77d2f7e`, worktree clean of modified
tracked files at launch, host under load (loadavg ≈65 at start, 48 foreign
`yes` hogs; concurrent r91-reviewer and g3d batteries):

```
rep1 — stamp 20261015T224801439124Z  (battery-runs/, log battery-rep1.log)
  rows=258  verdict=FAIL (256/258)  nav_lattice_ 11/11 PASS
  r91_expected_errors_all_matched=true   census rows_with_expected_errors=59
  fails: audio_bus_route_invalid_control (pre-existing audio flake class)
         probe_error_clause_surface meta  (cascade: dead_entry_count=1 —
         the audio entry above; census_bare_classifier_consistent=false,
         all other 39 discriminations true)
```

**Fresh battery run 2** — executed from a `git archive HEAD` extract
(`/home/vgpnk/r91-committed-extract`; extracted
`nav_lattice.gd=088843399ce37eb2`, `run_battery.py=f5725ca441565b8c`,
`project.godot=8de8b3af9cc737ed` verified before launch), independent of the
worktree and of the concurrent r92 edit:

```
rep2b — stamp 20261015T232338091246Z  (battery-committed/, log battery-rep2b.log)
  rows=258  verdict=FAIL (257/258)  nav_lattice_ 11/11 PASS
  r91_expected_errors_all_matched=true   all 40/40 discriminations true
  error-clause surface meta PASS   census rows_with_expected_errors=59, dead=[]
  fails: transition (pre-existing scene-readiness flake class)
```

**Cross-run comparison** (`audit/compare_runs.py`, 258 rows): **242 rows
byte-identical**, 13 rows differ only after their pinned signature, 3 rows
differ inside a pin — `transition`, `audio_bus_route_invalid_control`
(pre-existing flake classes) and `input_lattice_release_edge` (a declared
r87 envelope row that legitimately lands a different whitelisted payload).
**All 11 nav rows: the pinned payload matched in both runs**, with variance
confined to the declared tails:

| row | tail difference between the two committed-byte runs |
|---|---|
| `nav_lattice_sync` | `ladder=[…f2:1/1/0…] first_reach=4` vs `[…f2:0/0/0…] first_reach=5` (settle ladder — unpinned) |
| `nav_lattice_agent` | `first_reachable=5` vs `4` (unpinned) |
| `nav_lattice_avoid` | `seq_*/vel_*/sum_max` digits (process-dependent, unpinned; `sum_max` 19.8543 vs 19.8424) |
| `nav_lattice_link` | `settle=5` vs `settle=6` (unpinned) |
| census/path/query/region/bake/teardown_crash/teardown_clean | identical to the byte |

Custody cross-check: the `scratch/nav_lattice.gd` actually launched by both of
my runs (and by the author's `runs1`) is `088843399ce37eb2…` = the committed
fixture in every case.

---

## 3. Static fold verification — receipt-backed (all four declared folds)

`audit/fold_check.py` over 11 fresh single-arm launches in the battery's exact
shape (`fresh/`):

- **Pin-first / tail-last (fold 1).** Every one of the 11 landed signatures is
  a **prefix of the emitted line**; the pin length, emitted length and the
  tail tokens observed after the pin are:

| row | pin len | tail len | tail tokens after the pin |
|---|---|---|---|
| census | 649 | 0 | — |
| path | 604 | 16 | `settle= iter=` |
| query | 607 | 16 | `settle= iter=` |
| sync | 249 | 188 | `dis_same= chg_iter_same= chg_iter_settled= gate= ladder= first_reach= first_reach_sync=` |
| region | 939 | 100 | `dis_same= settle= iter=` |
| agent | 271 | 46 | `walk_steps= reached_at= first_reachable=` |
| avoid | 210 | 217 | `seq_a= seq_b= vel_a= vel_b= sum_max= settle=` |
| bake | 554 | 31 | `iter_b= settle_a= settle_b=` |
| link | 618 | 123 | `fwd_disabled_same= settle= iter= link_iter=` |
| teardown_crash | 52 | 0 | — (marker line only) |
| teardown_clean | 58 | 0 | — |

  **Zero scheduler/race tokens inside any pin** (word-boundary scan for
  `settle/iter/ladder/first_reach*/walk_steps/reached_at/first_reachable/iter_b/
  link_iter/gate/chg_iter_*/dis_same/fwd_disabled_same/seq_*/vel_*/sum_max/
  settle_a/settle_b`). Exactly one PASS line per PASS arm; the crash arm
  prints its marker and no PASS line.
- **Sync gate (fold 2).** `_await_sync` polls `map_get_iteration_id(map) >= 2
  AND reach` with `SYNC_BOUND := 48`; exhaustion calls `_stale()` →
  `STALE nav_lattice <arm> sync_bound_exhausted bound=48` + `_exit_code = 2`.
  Static read: the STALE line satisfies no row signature and the exit class
  fails every PASS row. **Not receipt-backed in my runs**: no arm stalled
  within 48 frames in 11 fresh launches or in 6 `--fixed-fps` launches (§9.3),
  so the STALE path is verified by source + the harness's exit-class check,
  not by a stall receipt of my own.
- **Same-frame OLD-answer reads (fold 3).** `dis_same`/`fwd_disabled_same`
  appear only in the tails of `sync`/`region`/`link`; `chg_same=false` stays
  pinned, as declared.
- **Query order (fold 4).** `_arm_agent` reads `is_navigation_finished()`
  (line 549) before `is_target_reached()` (line 551) and again inside the walk
  loop (line 566 before 567). The pin carries only order-independent final
  state (`fin=/reached=/reachable=` all `true` in every committed receipt);
  `reached_at` is a tail.
- **Avoidance invariants (fold 5).** `sum_bound_ok` requires exactly 5 paired
  measured frames each `|a.x|+|b.x| <= 20.001`; `dirs_ok` requires 5/5
  `a.x>0 & b.x<0` **and** the final velocities' signs. Boundary backing
  re-derived: 20/20 `b_avoid` runs have `per_a=per_b=[1,1,1,1,1]`,
  `n_a=n_b=21`, correct signs; 100 samples in `[19.8350, 20.0000]`, never
  above 20. My own fresh receipt: `sum_bound_ok=true dirs_ok=true`.
- **Teardown pair (fold 6).** `teardown_crash` → rc `-6` (shell 134), stdout
  marker `NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=true`, stderr
  `double free or corruption (!prev)`; `teardown_clean` → rc 0,
  `survived=true has_cb=false`, 0 B stderr (freed-RID callback read is silent,
  as the author disclosed).

---

## 4. Author dossier (`reports/round-91/r91-author.md`, `77d2f7e`)

### 4.1 Harness arithmetic — re-derived

- CASES at `HEAD`: **251 tuples** (240 → 251, +11); the 11 `nav_lattice_*`
  rows sit at indices 236–246, immediately after `r90_lattice_lag`, with
  `crash_spontaneous_sigabrt`, `crash_self_sigkill`,
  `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`
  after them (penultimate `descendant_pipe_detached_control` preserved) — as
  the harness comment requires. Result rows 258 (+11) in all four retained
  stamps (author ×2, mine ×2).
- `expected_errors` += 2 (`nav_lattice_sync`, `nav_lattice_bake`), exact-match
  per line; `required_stderr` += 1 (`nav_lattice_teardown_crash` →
  `double free or corruption`); the r91 floor gate exists and is `true` in the
  author's two runs and in both of mine. `rows_with_expected_errors` 57 → **59**
  in every run I inspected.
- Diff is insertion-only (`88/0`) and the nav tuple source segments, the
  `required_stderr` dict block and the r91 gate block are **byte-identical**
  between `HEAD` and the concurrently-modified worktree (§9.1).

### 4.2 Fresh-arm evidence — re-derived from `fresh-reps/` (11 arms × 3)

All 11 signatures are prefixes of the emitted line in **all 3 reps** of each
arm; rc vectors `0,0,0` (crash arm `-6,-6,-6`); stderr bytes 0 for 8 arms,
512 (`sync`) / 714 (`bake`) / 34 (`teardown_crash`). Rep-to-rep `out_uniq`:
`region=2`, `avoid=3`, all others 1 — and in both cases the differing bytes
are strictly after the pin (`settle=` for region; `seq_*/vel_*/sum_max/settle`
for avoid). The author's stated tail counters (`walk_steps=28 reached_at=28
first_reachable=5`) hold in its reps; `first_reachable` is unpinned and moved
(4/5/7/9) across my runs, exactly as declared.

### 4.3 Teardown binding is load-bearing (my falsification)

`audit/forge_test.py` — production `classify_process` AST-extracted from the
committed harness, plus the row's real `expected_errors`/`required_stderr`
pins, against my fresh receipt:

| variant | classified |
|---|---|
| A genuine (rc=-6, stdout marker, glibc fragment on stderr) | **PASS** |
| B stderr stripped (no fragment) | FAIL |
| C stdout anchor removed | FAIL |
| D rc=0 with the same streams | FAIL |
| E fragment present in merged output but not on stderr | FAIL |

The two halves (`rc=-6` + stdout marker + stderr fragment) are separately
necessary, so the row is bound to the glibc heap-corruption abort, not to the
signal class alone — the same closure shape as `geo2d_lattice_lineempty`.

### 4.4 Author runs — independently re-derived

Both `runs1`/`runs2`: rows 258, **verdict PASS**, nav 11/11, all 40/40
discriminations true, `r91`+`r90` gates true, `census_bare_classifier_consistent=true`,
`dead_entry_count=0`, `rows_with_expected_errors=59`. The author's "258/258 ×2"
and "zero flakes in either run" reproduce exactly.

---

## 5. Boundary dossier (`reports/round-91/r91-boundary.md`)

All recomputable claims reproduce:

- **Run census**: 403 `.rc` files = **346 rc=0 + 57 rc=134 + 0 rc=137**
  (0 timeouts), 403 `.out`/`.wall`; batch arithmetic 60+100+60+60+60+18+24+9+12
  = 403; `runs/rc-summary.txt` shows `timeout_hits=0` and the quoted
  loadavg start→end per batch.
- **Teardown matrix**: 17 runs per arm (3+5+3+3+3) — `c_noclear` 17/17 rc=134,
  `c_clear0` 17/17 rc=134, `c_leak_cb` 17/17 rc=134, `c_clear1` 17/17 rc=0,
  `c_clear2` 17/17 rc=0, `c_leak_clean` 17/17 rc=0 → **51/51 crash + 51/51
  clean** exactly as reported; **all 57 rc=134 runs carry
  `double free or corruption`** on stderr. Scout-probe reproduction:
  `dc_navfree2/5` 6/6 rc=134, `dc_navfree6` 3/3 rc=0.
- **Avoidance**: 100 samples in `[19.8350, 20.0000]`, **never above 20.0000**
  (exact bound hit 3×); `per_a=per_b=[1,1,1,1,1]` and `n_a=n_b=21` in 20/20
  `b_avoid` runs — the scout's `[19.849,19.883]` floor is indeed below the
  observed range.
- **Gate ladder**: 61 gate-pattern receipts (20 `b_gate` + 17 `sv_sync` + 24
  `ab`); `reach_before_iter2=false` in 20/20 `b_gate` and
  `gate_first == first_reach` in 20/20; the 43-frame ff30 receipt
  (`f30_b_gate.rep3.out`) and the never-sync ff120 receipt
  (`f120_b_gate.rep1.out`) are verbatim as quoted; exactly **8** bake runs
  end with `settle_*=24`, matching the report's named file list.
- **Query-order artifact**: `d_v9` 6/6 with `note=step=28 r1=false fin=true
  r2=true` and `reached_at=-1`; `d_bent` 6/6 `dist=226.2742 plen=282.8427
  delta=56.5685`.
- **Portability defect it flagged**: the scout's `nav_lattice_bake` prefix
  carried `iter_b=2` — the landed pin **drops it** (fold verified in §3), so
  the defect was consumed, not inherited.

---

## 6. Scout dossier (`reports/round-91/r91-scout.md`)

- Canonical set recomputed: **45 runs = 3×3 (census/path/query) + 6×6
  (sync/region/agent/avoid/bake/link)**, all rc=0; per-cell `out_uniq`/`err_uniq`
  agree with `runs/analyze_r91.json`: 8/9 cells `out_uniq=1 err_uniq=1`,
  `nav_avoid` `out_uniq=6` with `norm_uniq=1`. Loadtest: 31 runs.
- stderr census: `nav_sync` one ERROR (511 B), `nav_bake` one WARNING + one
  ERROR (712 B), the rest 0 B. The landed fixture's sync stderr is
  **line-for-line identical except the GDScript backtrace line numbers**
  (`nav_lattice.gd:234/142` vs the scout's `181/91`; 512 B) — the allowlist
  entry matches the ERROR line only, so the pin is unaffected.
- Landed-vs-scout row relation (fidelity of the folds): `census`/`query`
  **identical** to the scout's `ROWS_PREFIX`; `path`/`avoid` **extended**
  (`path` gains the scout-measured `gap20` bridge: scout receipts print
  `gap_margin20=[…] reach=true margin=20.0000`, landed pin renames the fields,
  values byte-equal; `avoid` gains the boundary-confirmed invariants);
  `sync`/`region`/`agent`/`bake`/`link` are **reduced/moved** exactly as the
  four folds declare (`chg_iter_same`, `chg_iter_settled`, `dis_same`,
  `walk_steps`, `reached_at`, `iter_b`, `fwd_disabled_same` → tails).

---

## 7. Arithmetic cross-check ledger (all reconcile)

| identity | result |
|---|---|
| author: CASES 251 = 240 + 11; rows 258 = 247 + 11; `run_battery.py` 88/0 insertion-only | ✓ |
| author: 99 fresh-rep files = 11 arms × 3 reps × (out/err/rc); manifest 642 = 643 − self | ✓ |
| author: `rows_with_expected_errors` 59 = 57 + 2; `required_stderr` entries +1 | ✓ |
| mine: rep1 256/258 (nav 11/11) + rep2b 257/258 (nav 11/11); 242/258 rows byte-identical | ✓ |
| boundary: 403 = 346 + 57; 403 = 60+100+60+60+60+18+24+9+12; 1632 = 1633 − self | ✓ |
| boundary: 51/51 + 51/51 teardown arms; 57 = 51 + 6 `dc_*`; 54 = 51 + 3 `dc_*` | ✓ |
| boundary: 8 bake runs with `settle_*=24`; 61 gate receipts; 100 avoid samples | ✓ |
| scout: 45 = 9 + 36 = 3×3 + 6×6; 398 = 399 − self | ✓ |
| cross-dossier: 11/11 landed pins == scout prefix (4 identical, 2 extended, 5 reduced/moved) | ✓ |

---

## 8. Adjudication items (ranked)

| id | dossier | item | severity | disposition |
|---|---|---|---|---|
| **A1** | scout §3.7 | the "law" range `\|a\|+\|b\| ∈ [19.849,19.883]` is the **frame-1-only** range (its own table's `a₀`/`b₀`); the scout's own 30 samples span `[19.841, 20.0000]` — rep1 f2 = 20.0000, f5 = 19.841; rep3 f5 = 19.884; rep4 f5 = 20.0000. The invariant is `≤ 20` | **low** (over-tight range; no landed pin affected) | the boundary already falsified it; the landing pins `sum_bound_ok` (≤ 20.001 over 5 frames) — correct. Reword the scout §3.7 law / §8.3 to "≤ 20 (envelope), exact bound reachable" |
| **A2** | author §"Full battery" | "`project.godot` scan counts in `export_readiness` unaffected" is imprecise: the global-class registration step count moves **41 → 42** with the added fixture script (r90 `runs9` vs r91 `runs1`, ANSI-stripped diff); the substantive claim (export verdict PASS in both runs) holds | low (label-only) | reword to "the added fixture script adds one registration step (41→42); the export verdict stays PASS" |
| **A3** | author §"Fresh-arm evidence" | the substring-verification **script** for the fresh-rep claim is not retained in the dossier (only the 99 receipts); the claim itself reproduces (re-derived here) | info | retain the checker next time; no re-derivation gap remains after this audit |
| **A4** | author §"Host notes" / landed `nav_lattice_agent` | the pin's `settled=`/`dist=`/`final_pos=` are walk-cadence-bearing state (a 28-step walk at 60 tps). They are prefix-stable in every committed receipt and gated by the sync gate, but they are *not* mode-independent: under `--fixed-fps` the boundary measured vacuous/42-step modes | info | keep (the failure mode is a loud mismatch, never a stale mis-PASS — §9.3); if a future engine/frame-count change moves the walk, the row fails loudly |
| **A5** | author §"Labrat advisory" / boundary §"probeParent disclosure" | two distinct labrat citations in one round (author agent `6594ae95`, statically verifiable; boundary's, no-exec null result) — the scribe cannot resolve the dispatch count from receipts | info | record for the adjudicator; both are declared read-only |
| **A6** | my receipts | my `fresh/teardown_crash.err` carries an extra `timeout: the monitored command dumped core` line (my launch used GNU `timeout`); the battery's Python launch shape does not produce it | info | receipt-provenance note only; the `required_stderr` fragment matched in both shapes |
| **A7** | author custody | `runs1/`,`runs2/` (48 MB, the two green runs) are gitignored (`corpus/live/.gitignore:5` `runs*/`) but manifest-covered → worktree-only custody | info | same convention as prior rounds; recorded not escalated |
| **A8** | environment | `/tmp` is a 16 GB tmpfs at 80 % (13 GB used by concurrent lanes); a first `git archive` extract there died mid-way with `Disk quota exceeded`; rep2b was re-run from a `/home` extract | info | environment blocker for `/tmp`-based committed-tree replays on this host |
| **A9** | environment | concurrent lanes during the audit: r92 author editing `run_battery.py` from 23:25:53Z (+14 CASES), r91-reviewer running its own battery from a tree copy, g3d battery | info | see §9.1; no effect on this seat's evidence |

---

## 9. Remaining risks / blockers

1. **Concurrent tracked edit (r92 author).** `corpus/fixtures/run_battery.py`
   was clean when my run 1 started (verified) and had +161 lines by 23:25:53Z.
   I verified the **r91 landing is untouched**: the 11 nav CASES tuple source
   segments, the `required_stderr` dict block and the `r91_expected_errors_all_matched`
   gate block are **byte-identical** between `HEAD` and the current worktree;
   CASES is now 265 (251 + 14 r92 rows) with the nav rows unchanged in name,
   order and bytes. My run 2 executed from a `git archive HEAD` extract, so it
   is committed-bytes by construction. **Blocker for the adjudicator only if a
   future seat replays the worktree harness while the r92 block is mid-edit.**
2. **`/tmp` tmpfs at 80 %** (A8): a committed-tree replay must extract under
   `/home` (795 GB free) on this host; a `/tmp` extract silently truncates.
3. **Worktree-only custody** for the scout (398 entries, 12 tracked) and the
   author's two green runs (48 MB, gitignored): manifest-verified but a
   worktree prune would lose them (A7, recorded).
4. **Host-conditional pins by design**: `srv_methods=199`, `poly_methods=134`,
   enum arrays, default values, 4-dp vertex order, `tps=60` — all flip loudly
   on an engine/solver change (same class as existing census/geometry pins).
   The `gap20_reach=true` / `chg_settled=true` settle-window outcomes are
   60-tps-conditional: my `--fixed-fps` probe shows them flipping to `false`
   (loud row FAIL), never to a stale PASS.
5. **The STALE path (fold 2) has no receipt of its own** in this audit: no arm
   exhausted `SYNC_BOUND=48` in 17 launches (11 fresh + 6 fixed-fps). The
   stall that the boundary measured (43-frame ladder, never-sync at ff120) was
   on the *scout's* probe with a 24-frame silent bound, not on the landed
   fixture. The landed STALE+exit-2 behaviour is source-verified and
   exit-class-checked by the harness, but a receipt-backed stall would close
   it completely.
6. **Pre-existing flake classes** reproduce under load on committed bytes
   (`audio_bus_route_invalid_control` in my rep1, `transition` in my rep2b,
   `input_lattice_release_edge` envelope mode) — they are not r91-caused; the
   r91 surface is 11/11 in both runs.
7. **No blockers to the landing.** The `r91_expected_errors_all_matched` floor
   gate is `true` in all four retained committed-byte runs and the dead-entry
   census is empty in three of them (rep1's single dead entry is the audio
   flake's, not an r91 entry).

---

## 10. Host notes / cleanup

- Host was never idle: my own samples were loadavg 57.2–65.8 from concurrent
  lanes (48 foreign `yes` hogs at audit start, an r91-reviewer battery, a g3d
  battery; the sibling boundary seat recorded 58–118 in its window). I added
  no hogs of my own; all launches were `timeout -s KILL 25`-bounded.
- The `/home/vgpnk/r91-committed-extract` tree used for run 2 is retained in
  this session's receipts (its launched fixture bytes are preserved inside
  `battery-committed/*/scratch/`); it was removed after the audit to free
  space. No `.godot/` cache was written into any tracked project dir by this
  seat (`corpus/fixtures/.godot/` does not exist; `corpus/live/**/.godot` is
  gitignored).
- Zero tracked files written by this seat; `git status --porcelain -uno`
  shows only the concurrent r92 lane's ` M corpus/fixtures/run_battery.py`.

---

## 11. Evidence index

All under `corpus/live/r91-scribe/`; `manifest.sha256` covers every artefact.

| artefact | path | notes |
|---|---|---|
| battery run 1 (worktree, committed bytes) | `battery-runs/20261015T224801439124Z/verdicts.json` + `battery-rep1.log` | 258 rows, nav 11/11, `b8018f35…` log |
| battery run 2 (`git archive HEAD` extract) | `battery-committed/20261015T232338091246Z/verdicts.json` + `battery-rep2b.log` | 258 rows, nav 11/11, all 40/40 discriminations true, `7d95572c…` log |
| fresh single-arm receipts | `fresh/*.{out,err,rc}` | 11 arms in the battery launch shape |
| `--fixed-fps` mode probe | `fixedfps/{agent,path,sync}_ff{30,120}.{out,err}` | pin-match / loud-fail evidence |
| fold checker | `audit/fold_check.py` → `fold_check.json/.txt` | pin-prefix + tail placement |
| manifest/completeness + signature structure | `audit/static_folds.py` → `static_folds.json` | |
| teardown-binding falsification | `audit/forge_test.py` | production classifier, 5 variants |
| cross-run comparison | `audit/compare_runs.py` | 242 identical / 13 tail-only / 3 pin-diff (all pre-existing classes) |
| author fresh-rep re-derivation | `audit/author_fresh.py` → `author_fresh.json` | 11 arms × 3 reps |
| source reports | `reports/round-91/r91-{scout,boundary,author}.md` | tracked, sha-verified |
