# game-dev-2d round 95 — simplifier (r95-simplifier): the r95 dss/order landing on committed `9cd47507` is verified on its own bytes (52/52 rows × 3 fresh reps, 149/149 law checks, floor gate proven loud), **15 dead stores** (18 edit sites, −5 lines) are provable YAGNI deletions proposed as an **unapplied byte-neutral patch**, and one **coverage defect** is found: `r95b_order_celloff_y1000` passes `--offy=1000` but the probe never reads it, so the row is a byte-exact duplicate of `celloff_x0` and the claimed **Y-axis** translation invariance was never exercised

Seat `SIMPLIFIER` (LEAF) | lane `r95` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Work commit **`9cd47507`** (r95 author: `corpus/fixtures/dss_lattice.gd` 743
lines `77ae4adb…` + `corpus/fixtures/r95b_order.gd` 777 lines `4f7e945e…` +
`corpus/fixtures/run_battery.py` `+163/−0` `b93cbdaa…` + author report, 366
result rows). **HEAD == the landing** at audit start; every receipt below is
against the byte-exact `committed-fixtures/` snapshot of those three files
(`head-check.txt`). **No tracked file written, no commit, no git mutation by
this seat.** Writes are this report and `corpus/live/r95-simplifier/**` only
(`MANIFEST.sha256`, 215 files).

**Concurrent-lane disclosure (worktree, not mine).** While this seat ran, the
r96 author lane landed in the shared worktree: `corpus/fixtures/scene_io_lattice.gd`
(new, 04:40:22 local), `corpus/fixtures/run_battery.py` `+243` lines (an r96
`scene_io_lattice` block, 04:40:33) and a regenerated tracked
`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` (04:31:05; its bytes
contain 114 `scene_io_lattice`/`r96b_` strings vs 0 in the committed pyc — so it
is compiled from the foreign harness, not from anything this seat ran). None of
it is analysed here, none of it is in any receipt, and this seat did not touch
it. All four of this seat's full battery runs staged their own scratch from the
then-committed fixtures and printed the harness sha they executed
(`control1`/`control2`: `harness sha256: b93cbdaa…`; fold-gate: the folded
harness; fold-battery: its own `fold-battery-project/` copy) — every run
reports **366** rows, not 366+r96.

**`lsp` disclosure.** No `lsp` device is exposed in this dispatch and no
GDScript language server exists on this host (same finding as r89–r94).
Symbol-aware `references`/`definition`/rename were therefore **unavailable**;
no cold result is recorded as absence. No rename was needed (no deletion was
applied), so hand editing never arose. Every caller/consumer claim below rests
on (a) a complete scope-aware value-observation scan, (b) an arm↔row↔gate↔knob
census, (c) a pin↔emission census over 472 independent receipts + 4 author
battery runs, and (d) fresh-process byte comparison.

**Frozen probeParent.** Exactly **one** read-only `ufo-labrat` was dispatched
(agent `fbc1a79d`, bounded, static, no writes, no shell). It returned **H1
CONFIRMED** (an independent full re-derivation of the dead-store set: all 18
edit sites are value-unobserved, no additional site, no listed site actually
read, with an explicit same-name conflation check), **H2 CONFIRMED** (all 52
pin forms: the four dss head-prefix rows carry no multi-hit vector; every other
row's signature ends at its arm's last `_it()` key), **H3 CONFIRMED** (the r95
floor gate is the only gate whose prefixes can match an r95 case; zero
allowlist entries), **H4 UNKNOWN** (no shell/hash capability — its own
disclosure; the two cited shas were verified by this seat in `head-check.txt`).
No other descendant was spawned.

---

## 1. Method and proof artefacts

`corpus/live/r95-simplifier/` (`MANIFEST.sha256`, **215 files**; per-run Godot
scratch trees excluded, the r92/r93/r94 precedent):

| artefact | content |
|---|---|
| `committed-fixtures/` | byte-exact `git show 9cd47507:` snapshot of the two fixtures + harness + author report; every audit re-run against it |
| `head-check.txt`, `head_check.py` | HEAD == landing; worktree tracked-clean at start; fixture↔frozen-probe byte identity (both `identical=True`); harness comment sha citation |
| `audit-static.txt`, `audit_static.py` | declaration census, scope-aware value-observation table (15 dead stores), function/print/arm/CLI census, harness census: CASES 359 (52 r95), block 303..354 contiguous, allowlists, gates, signature redundancy, row↔arm bijection |
| `deadstore-scan.txt`, `deadstore_scan.py` | the authoritative complete dead-store scan (occurrence-classified: decl / assign / append / index-write / `_pile` out-arg / read) |
| `pin-census.txt`, `pin_census.py` | pin↔emission census: 472 receipts (211 scout + 261 boundary), stem-matched per row; author `verdicts.json` × 4 |
| `fold-verification.json` / `.log`, `verify_folds.py`, `fold-runs/<stamp>/` | 52 rows × 3 reps = 156 fresh launches in the battery's exact shape, classified by the **production** `classify_process` (AST segment sha `749fa060…`), plus 149 law re-derivations in Python |
| `ff-matrix.txt` / `.json`, `ff_matrix.py` | 11 order-law rows × `--fixed-fps 30` / `120` / 12-hog load × 2 reps = 66 launches |
| `runs-control1/20261016T071400728267Z`, `control1-battery.stdout`, `run_control1.sh` | full 366-row battery on the committed tree, 8 seat hogs |
| `runs-control2/20261016T072115536844Z`, `control2-battery.stdout`, `run_control2.sh` | full 366-row battery on the committed tree, no seat hogs |
| `fold-gate/`, `fold-gate.diff`, `make_fold_gate.py`, `runs-fold-gate/20261016T072755438325Z`, `fold-gate-battery.stdout`, `run_fold_gate.sh` | +1 stale r95 allowlist entry; full battery on the folded harness |
| `fold-proposal.diff`, `fold_candidates.py`, `fold-candidates.stdout`, `fold-candidates-verification.json`, `fold-runs/<stamp>/scratch-{committed,folded}` | the 18-site dead-store fold and its 52 rows × 3 reps × 2 trees = 312-launch byte-neutrality proof |
| `fold-battery-project/`, `runs-fold-battery/20261016T074031413327Z`, `fold-battery.stdout`, `run_fold_battery.sh` | full 366-row battery on the **folded** fixtures + sha-updated harness |
| `build_manifest.py` | regenerates the manifest |

## 2. Verdict and findings (ranked)

**Verdict: PASS — the landing is verified on its committed bytes; the only
provable YAGNI deletions are 15 dead stores (18 edit sites, −5 lines) proposed
as an unapplied byte-neutral patch; one coverage defect (phantom Y-translation
row) is recorded with the operator to decide fix-vs-delete.** 0 blockers.

| # | finding | severity | evidence |
|---|---|---|---|
| F1 | **`r95b_order_celloff_y1000` is a phantom-coverage row — the claimed Y-axis translation was never exercised.** The row's flags are `["--arm=celloff", "--off=0", "--offy=1000"]`, but `_arm_celloff` (`r95b_order.gd:565-567`) reads only `--off` (`var off := _opt_float("off", 0.0)`; `_pile(…, off, 0.0)`), and `offy` appears **nowhere** in the fixture (grep 0 hits; the probe's own header documents only `--off`). The launch is therefore the *same construction* as `r95b_order_celloff_x0`, and the two committed signatures are byte-identical (`md5 780c02c0648da61cc33c3ddbe4e6b4ea`; emitted PASS line `md5 e06cb7f3753fb61f` in every boundary batch where both ran — quiet and load — and in this seat's 3 fresh reps). The author report's "off 0, +1000 x, +1000 y" claim and `r95-boundary.md` §4's "y = +1000" evidence are **void for the Y axis** (the boundary's own analyzer recorded `"offy": null` for every celloff check — the key was never emitted). Consequence: **Y-translation invariance is unmeasured, not falsified**; the X cells (real offsets) stand. Mechanical census: `--offy` is the **only** unread flag among all 52 rows' flags | **medium** (false coverage claim; row is byte-exact duplicate of x0) | `deadstore-scan.txt`, `pin-census.txt`, `corpus/live/r95-boundary/runs/analyze_r95b.json`, `run_matrix.sh:95,127`, fresh receipts in `fold-verification.json` |
| F2 | **15 dead stores are provable and byte-neutral** (§6): 8 in `dss_lattice.gd` (`pile:357`, `box:370`, `made2:499`, `made3:506`, `fresh:514`, `cast:571`, `ar:585`, `b2:629`) and 7 in `r95b_order.gd` (`dss:415`, `dss:455`, `made:530`, `made:567`, `made:609`, `a:745`, `b:750`) = 18 edit sites, **−5 lines**. Patch attached (`fold-proposal.diff`); **not applied** (this seat writes no tracked file). Independently corroborated by the frozen labrat's H1 | low (clean-up; −5 lines) | `deadstore-scan.txt`, `fold-proposal.diff`, `fold-candidates-verification.json` (312 launches, **0 cross masked diffs, 0 cross pass-line diffs**), `runs-fold-battery` (366/366 green on the folded bytes) |
| F3 | **All 52 rows re-verify on the landed bytes.** 156 fresh launches (3 reps each) in the battery's exact launch shape, classified by the production `classify_process`: **52/52 rows PASS every rep**, 48 rows emit their signature byte-exactly, the 4 designed head-prefix rows (`point_cap[_rev]`, `order_core[_rev]`) emit it as a prefix, and all 52 are rep-stable modulo the declared unstable diagnostic keys (`ids`/`env`/`fresh_id`/`t*_bodypos`) | info (integrity) | `fold-verification.json` |
| F4 | **The boundary folds re-derive from fresh emissions** (149/149 checks): `cycle_len = k(k−1)` for k = 2,3,4,5,5@spacing8,6,7,8,10 (`expected_kk1` echoed, `distinct_ticks == n_ticks−3`), `canon` dense ladder with `t20==t0`, `t64==t4`, `last_change_tick=64`; perm0–7 → 8 distinct `add_order`/`t2_vec`/ladders under the fixed tag→x map; `scoutrev` relpos == canon relpos while labels differ; `celloff` ladders identical x0/x1000; `twopiles` A-alone ≠ A-with-B; `warm_k32` == canon on common ticks while `warm_keep8` differs (`distinct=4`); `free_ab ≠ free_ba` with post-free `t2==t8` (k=3 cycle 6); `readd_a` slot inheritance; `cap40` `n0=0 n32=32 n64=40`, `set32_distinct=5`, three pairwise-distinct `set32_t2`; `layers_k0/k1` `pt_eq_sh` true/false, `sh_len` 5/6; `rigid` `distinct_ticks=1`, `t10_relpos=[15.9999,14.8732]` | info (folds verified) | `fold-verification.log` |
| F5 | **Scheduler robustness re-verified on the landed bytes**: the 11 order-law rows (`canon`, `period_k5`, `periodx_k{2,3,4,5,5s8,6,7,8,10}`) match their committed signatures **2/2** under `--fixed-fps 30`, `--fixed-fps 120`, and a 12-hog load (loadavg 97→103) — 66 launches, 0 failures. The k(k−1) ladder is a tick-counted law, not a clock-mode artifact | info | `ff-matrix.txt` |
| F6 | **Pin↔emission census over 472 independent receipts: every pin is bound by real emissions.** Every one of the 52 rows has stem-matched receipts (scout/boundary matrices: 1–24 per row) and the committed signature appears in **100 %** of them; the author's four battery runs record **PASS 4/4** for all 52 rows. The only `ERROR:` lines in the whole r95 receipt corpus (6, in 4 receipts) are the scout's **pre-fix** `leak-hazard`/`disc` arms (`RID … leaked at exit`) — the falsification that produced the fixture's RID frees (`dss_lattice.gd:473,576-577`); no authored arm carries an ERROR line | info (integrity) | `pin-census.txt` |
| F7 | **Landing integrity (committed bytes).** `runs-control2`: **366/366 PASS**, `dead_entry_count=0`, `rows_with_expected_errors=68`, all gates true, r95 **52/52**. `runs-control1` (8 seat hogs): 366 rows, r95 **52/52**, the only row failures are the documented flake classes (`transition`, `negative_transition` — one-tick window; `audio_playback`, `audio_bus_route_invalid_control` — audio wall-clock rows), which in turn break `probe_error_clause_surface`'s downstream `census_bare_classifier_consistent` (and mark those rows' own allowlist entries `dead_in_run`, `dead_entry_count=3`) — no r95 gate is implicated | info (integrity) | `runs-control2/…/verdicts.json`, `runs-control1/…/verdicts.json` |
| F8 | **The floor gate is loud, not decorative.** Fold: one never-emitted entry `r95b_order_canon → ERROR: r95-simplifier dead-entry fold probe` added to a copied harness (`fold-gate.diff`, harness sha `2d321f27…`). Full battery: the row **still PASSes**, `census_bare_classifier_consistent=True`, all sibling gates stay true, **but** `dead_entry_count=1` names exactly the injected entry, `r95_expected_errors_all_matched=False` ⇒ `probe_error_clause_surface` FAIL ⇒ battery FAIL | info (gate live) | `fold-gate.diff`, `runs-fold-gate/…/verdicts.json` |
| F9 | **Harness insertion is insertion-only and structurally clean**: `git diff 6f817d10 9cd47507` on the harness = `+163/−0`; CASES 307→359, results 314→366 (meta rows unchanged at 7); the r95 block is contiguous (indices 303..354), inserted after `r94_particles_gpu_headless` and ahead of the crash/descendant tail; **0 identical-launch duplicate/subsumption pairs** inside the block; **0** r95 signatures contain a foreign row's signature; `procwait`/`layout_changes_order` appear only in the block's comment (the "deliberately NOT authored" record), never as signed keys | info | `audit-static.txt`, `git diff --numstat` |
| F10 | **Both fixtures are frozen byte-copies of record** (scout probe `77ae4adb…` / boundary probe `4f7e945e…`, both re-verified identical) and every helper has ≥1 call site except the engine-invoked `_initialize`/`_run`; the 4 print sites per fixture are the PASS/FAIL/R95B/R95B-diag lines; the CLI surface is `--arm` (+ `--rev` for dss; `k/spacing/perm/which/order/keep/off` for r95b — `offy` is the sole unread flag, F1) | info | `audit-static.txt`, `head-check.txt` |

## 3. The fold question — candidates audited

Method: (a) scope-aware **value-observation** scan over every `var`/`const`
(occurrence classes: declaration, bare assignment, `append`, index-write,
`_pile` out-arg, read — function locals confined to their own scope, file-scope
names file-wide); (b) **arm↔row↔gate↔knob** bijection; (c) **pin↔emission**
census on 472 real receipts + 4 author runs; (d) **signature redundancy**
census (exact + substring within identical launches); (e) execution for every
candidate that survives (a)–(d).

| # | candidate | verdict | proof / reason |
|---|---|---|---|
| SP1 | 15 dead stores / 18 edit sites (F2) | **FOLD PROPOSED (unapplied, byte-neutral)** | Value never observed in scope (scan + labrat H1); the side-effecting call is retained in every rewrite. Executed: 52 rows × 3 reps on committed vs folded bytes → **0 masked-stdout diffs, 0 PASS-line diffs**, all PASS on both trees; the **full 366-row battery on the folded bytes is 366/366 green** (`runs-fold-battery`, scratch shas = folded shas) |
| SP2 | `r95b_order_celloff_y1000` row (F1) | **REJECTED as a fold — escalated as a defect** | It is *not* a YAGNI deletion: the row's *declared* coverage (Y translation) is void, but deleting it removes the placeholder rather than restoring the claim, and it would change the battery row set (366→365), i.e. **not byte-neutral**. The operator decides: (a) implement `--offy` in the probe+fixture (author-class change, real coverage, new receipts) or (b) drop the row. This seat did neither |
| SP3 | `--offy` knob string itself | **rejected (not the lever)** | Deleting the flag from the row would silently turn it into a second `celloff_x0`; the defect is the missing fixture support, not the flag |
| SP4 | The 4 `--rev` rows (`ray_order_rev`, `point_cap_rev`, `shape_lattice_rev`, `order_core_rev`) | **rejected** | Each pins a real behavioural difference (tie label swap; `touch=[a#0]` vs `[e#0]`; reversed construction echo) and the four are the only rows exercising `--rev` on those arms — the boundary's "label-permutation" finding is encoded *through* them (`scoutrev` counter-pin + `perm0..7`) |
| SP5 | `r95b_order_periodx_k5` vs `r95b_order_period_k5` (both pin k=5 cycle 20) | **rejected** | Different arms, different tick grids, disjoint pinned clauses (`periodx` pins t0/t2/t3 vecs + `expected_kk1`; `period` pins `t_last_vec` and is the load/ff-covered cell) — no subsumption |
| SP6 | The 4 head-prefix dss rows (`point_cap[_rev]`, `order_core[_rev]`) | **rejected** | Deliberate encoding of the boundary refutation: the full lines carry the phase-locked vectors / the refuted `layout_changes_order` key. They pin arm dispatch + the frozen construction; the law lives in the `r95b_order_*` rows (labrat H2 verified the prefix form) |
| SP7 | The ~50-line r95 harness comment block (lines 878–925) | **rejected** | It **is** the fold encoding (boundary verdicts, exclusions, receipt counts, insertion-position rationale); deleting it orphans every justification (r91-SP6/r92-SP9 class) |
| SP8 | The 7-line `r95_expected_errors_all_matched` gate | **rejected** | Proven **loud** (F8) and **non-redundant** (no sibling prefix matches `dss_lattice_`/`r95b_order_`; labrat H3) |
| SP9 | Fixture ↔ frozen-probe duplicates (×2, byte-identical) | **rejected** | The probe copies are the provenance of record (paths + shas cited by the harness comment and the author report); seat receipts under `corpus/live/<seat>/` are the repo convention (r87–r94) |
| SP10 | 5 pre-existing exact-duplicate signature groups outside r95 (`negative_overlap`/`negative_signal`, 3 camera limits, 2 button shapes, 2 crash markers, 2 descendant-pipe markers) | **rejected (not this lane's)** | Intentional scenario pins (different constructions/scenarios pinning the same marker text); they are outside the assigned diff and untouched |
| SP11 | Helper/default tails (e.g. `_opt_int` defaults, `_fail` unknown-arm path, unused-by-rows arms `env`/`procwait`) | **rejected** | All reachable/live: the uncovered arms are the boundary's documented instruments (`procwait` = the §9 [U] instability, `env` = mode facts; both receipted), the unknown-arm fallback is the loudness class (r89-SP7), and defaults are exercised positionally |
| SP12 | *the honest negative* | **no other fold** | Nothing else survives (a)–(d): every emitted field is either a pinned claim or the unpinned discovery surface that produced the pins; the value-observation axis is empty beyond SP1 |

**Conclusion.** The r95 landing carries exactly one class of provable YAGNI
deletion — the 15 dead stores (SP1) — and one *defect* that is not a deletion
(SP2/F1). Everything else that looks removable is an instrument (SP11), a
coverage clause (SP4/SP5/SP6), provenance (SP9), or evidence (SP7).

## 4. Landing integrity — the narrow check, on the committed bytes

- **Control battery (green)**: `runs-control2/20261016T072115536844Z` —
  **366/366 PASS**, verdict PASS, `dead_entry_count=0`,
  `rows_with_expected_errors=68`, all gates true (incl.
  `r95_expected_errors_all_matched`), r95 rows **52/52**.
- **Control battery (flake-only)**: `runs-control1/20261016T071400728267Z`
  (8 seat hogs, loadavg 102→90) — 366 rows; failures are exactly the
  documented classes (`transition`, `negative_transition`,
  `audio_playback`, `audio_bus_route_invalid_control`) plus the meta row they
  break (`census_bare_classifier_consistent=False`, `dead_entry_count=3` from
  those two rows' own entries); r95 **52/52** and the r95 gate true.
- **Fresh-row verification**: 52 rows × 3 reps, production classifier — see F3.
- **Law re-derivation**: 149 checks, 0 failures — see F4.
- **Scheduler matrix**: 66 launches, 0 failures — see F5.
- **Receipt census**: 472 receipts + 4 author runs — see F6.
- **Insertion shape / redundancy**: see F9/F10.

## 5. The fold proposal (dead stores) — how it was proven

`fold-proposal.diff` (150 lines) deletes the 5 whole statements and rewrites
the 13 dependent lines (never removing the side-effecting call):
`dss_lattice.gd` −3 lines (`77ae4adb…` → `c128e9cc…`), `r95b_order.gd` −2
lines (`4f7e945e…` → `b367559e…`), plus the two harness comment sha lines
(`b93cbdaa…` → the folded-harness bytes). Proof of byte-neutrality, on the
landed bytes:

1. **Arm-level**: 52 rows × 3 reps on *both* trees in the battery's exact
   launch shape → `cross masked diffs = 0`, `cross pass-line diffs = 0`,
   `all_pass_committed = all_pass_folded = True`
   (`fold-candidates-verification.json`).
2. **End-to-end**: the full 366-row battery on the folded tree
   (`runs-fold-battery/20261016T074031413327Z`) → **366/366 PASS**,
   `dead_entry_count=0`, r95 **52/52**, with the scratch fixtures proven to be
   the folded bytes (`c128e9cc…` / `b367559e…`).

If the operator applies the patch, two comment lines should be updated with it:
the harness comment's parentheticals "(…, identical bytes)" become false once
the fixtures carry the declared diff — replace with "(…, minimal declared
diff: dead stores removed)". They are inert; the patch leaves them as-is to
stay minimal (the r94 precedent updated only the sha lines).

## 6. Remaining risks / blockers

- **F1 needs an operator decision** (fix `--offy` support vs drop the row).
  Until then, the landing's Y-translation claim is **not** backed by the row
  that appears to test it — a reader of the author/boundary reports would
  over-trust that cell. This is the one finding with a coverage consequence;
  nothing about the 52 rows' *current* PASS verdicts is affected.
- **The `celloff_y1000` duplicate also weakens the boundary §4 table** (it
  lists "y = +1000" among the 14/14 identical offsets). The X-axis cells are
  real; the Y cell's evidence is a duplicate of x0. Recorded, not edited
  (the boundary report is the falsification record of its session).
- **The dead-store patch stales the frozen-probe provenance** if applied: the
  fixtures would no longer be byte-copies of the scout/boundary probes, so the
  receipts in `corpus/live/r95-{scout,boundary}/` document the *pre-fold* bytes
  (their *claims* remain valid — byte-neutrality is proven — but the byte
  identity is broken). Same trade-off the r94 seat accepted; operator decides.
- **`input_lattice_pre_frame` / `transition` / audio wall-clock rows remain
  the live flake surface** under load (pre-existing, outside r95) — they are
  what control1's extra FAILs are; control2 and the folded battery are green.
- **The worktree now contains a foreign in-flight r96 landing** (see
  disclosure). If any future seat re-runs the battery from `corpus/fixtures/`,
  it will execute 366+r96 rows; all receipts here are pinned to the committed
  harness sha printed in each run's stdout.
- **Blockers: none.** Nothing committed; unrelated work untouched.
