# r91 verifier — independent non-author verification of `77d2f7e`

Seat `VERIFIER` (g2d lane r91, independent non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7, 32 cores. Target:
`77d2f7ec2db788fffa5279c213079715a403996b` (*r91 author: 11 nav_lattice rows
(258 total) — iteration_id gate, scheduler fields to tails, query-order fix,
teardown crash armed rc=-6; 258/258 x2*). Receipts: `corpus/live/r91-verifier/`
(index in `RECEIPTS.md` there; `manifest.sha256` 1807/1807 OK, `tree/` excluded).
Author report: `reports/round-91/r91-author.md`.

**`lsp` disclosure.** No `lsp` device and no GDScript language server is exposed
to this seat (unchanged lane state); every semantic check below is an AST/static
read of the committed bytes plus fresh-process execution — the recorded
fallback. The change is a new fixture file plus an insertion-only harness block
(no renames), so no symbol-aware operation was possible or required.

**Frozen probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2, agent
`57f3a492`) was dispatched with one bounded static hypothesis. It had **no exec
tool**, wrote nothing, spawned nothing. It returned clause (A) **FALSIFIED** by
three substring counterexamples — `n_a` (also matching inside `en_a=` and
`warm_n_a=`), `pre_iter=` (contains `iter=`), `settled=` (inside
`dis_settled=`) — plus clauses (B)/(C)/(D) CONSISTENT. Delimiter-aware re-check
(below) shows all three were bare-token false positives of my over-broad probe
wording, not fixture defects; the substantive clauses it confirmed are
independently re-verified here. No second dispatch; its null runtime scope is
recorded, not silently omitted.

**Concurrent-worktree disclosure.** The worktree's `corpus/fixtures/run_battery.py`
carries a foreign in-flight **r92 author** edit (+161 lines, mtime 20:25:53). It
is not in `77d2f7e` and was not read as the reviewed bytes: everything below
runs against the frozen extraction at `corpus/live/r91-verifier/tree/`.

**No tracked writes, no commits.** All artefacts are untracked
`corpus/live/r91-verifier/**` plus this report.

---

## 1. Method — frozen tree

- **Fileset**: `git ls-tree -r --name-only 77d2f7e` (100,530) vs extracted
  `find -type f -o -type l` (100,462 files + 68 symlinks = 100,530) —
  **0 diffs** (`freeze/fileset-diff.txt` empty).
- **Content**: absolute `GIT_DIR` + `GIT_WORK_TREE=tree` `git diff --quiet 77d2f7e`
  → **rc=0**, 0-byte stderr (`freeze/content-diff.err`). (Relative `GIT_DIR`
  resolves inside the work tree and fails with "packfile index unavailable" —
  recorded because the first attempt failed that way; the absolute-path form is
  the one that holds.)
- **Fixture shas (frozen tree)**: `nav_lattice.gd` `088843399ce3…`,
  `run_battery.py` `f5725ca441…`, `project.godot` `8de8b3af…`,
  `rb_lattice.gd` `10da2291…` — all byte-equal to the author's declared pins.
- **Scout provenance**: `corpus/live/r91-scout/probes/nav_lattice.gd`
  (`efb496e5…`) vs committed fixture → 532-line diff, +262/−60, every hunk
  inside the declared fold (header, `SYNC_BOUND`/`_exit_code`/`_stale`, gate +
  loud abort in all 8 sync-dependent arms, tail moves in 6 arms, avoid-invariant
  computation, agent fin-before-reached order, two teardown arms). No pinned
  value changes call sites.
- **Harness delta**: `run_battery.py` **+88/−0** (insertion-only, 4 hunks);
  `nav_lattice.gd` new (+882).

**AST audit of the committed harness** (`probes/audit-committed.txt`):

- CASES **251** tuples (r90: 240) → **258** result rows (251 + 7 meta); the 11
  `nav_lattice_*` rows sit at indices 236–246, immediately after
  `r90_lattice_lag`, ahead of `crash_spontaneous_sigabrt`.
- `expected_errors` = exactly the two declared entries (`nav_lattice_sync`,
  `nav_lattice_bake`); `required_stderr` = exactly
  `nav_lattice_teardown_crash → ('double free or corruption',)`; floor gate
  `r91_expected_errors_all_matched` present (harness lines 2746/2749, predicate
  `case.startswith("nav_lattice_")`).
- **Zero field-form leaks**: no `settle=`/`iter=`/`ladder=`/`gate=`/
  `first_reach*=`/`walk_steps=`/`reached_at=`/`first_reachable=`/`iter_b=`/
  `link_iter=`/`chg_iter_*=`/`dis_same=`/`fwd_disabled_same=`/`seq_*=`/`vel_*=`/
  `sum_max=` (delimiter-aware) appears inside any of the 11 signatures. The
  deliberate pinned non-scheduler reads are `pre_iter=` (pre-sync state),
  `settled=` (state quintuple), `warm_n_a=/n_a=/n_b=` (boundary-confirmed
  cadence counts).
- Tail print sites are strictly after each pin (sync 301–307, path 357–358,
  query 415–416, region 512–514, agent 584–586, avoid 682–685, bake 769–770,
  link 832–835); the `STALE nav_lattice <arm> sync_bound_exhausted bound=48`
  line satisfies no signature.

---

## 2. Results per dispatch item

### 2.1 Battery ×5 on the committed bytes — **rep5 green 258/258, tuple-identical to both author runs; nav 11/11 in all five**

| rep | window loadavg | verdict | nav rows | non-nav failures |
|---|---|---|---|---|
| rep1 `…232439543775Z` | 72→79 | FAIL | **11/11 PASS** | `negative_transition` + census cascade |
| rep2 `…232914025617Z` (+8 seat hogs) | 76→83 | FAIL | **11/11 PASS** | `overlap`, `negative_transition`, `input_lattice_pre_frame` + cascade |
| rep3 `…233351481686Z` | 83→87 | FAIL | **11/11 PASS** | `overlap`, `transition`, `negative_transition` + cascade |
| rep4 `…000302026150Z` | 53→55 | FAIL | **11/11 PASS** | `transition` |
| rep5 `…000657222526Z` | 55→69 | **PASS** | **11/11 PASS** | none — 258/258 |

- **55/55 nav row-instances PASS** across the five loaded reps; every round
  gate (`r91_…` plus r87–r90/phys2d) `true` in all five.
- **rep5 is tuple-identical to BOTH committed-worktree author runs**
  (`runs1/20261015T223815564642Z`, `runs2/20261015T224213073214Z`) across all
  258 rows — signature, verdict, actual exit, error — 0 mismatches, 0
  signature diffs. The committed bytes reproduce a full green in a different
  session under load.
- Nav census entries in every rep: `nav_lattice_sync`/`nav_lattice_bake`
  `matched_lines=1`, `dead_in_run=false`, `bare_classification_rejects=true`,
  `allowlisted_classification_passes=true`; `teardown_crash actual_exit=-6`.
- **Prior-row identity**: r90 green (`r90-author/runs9/…`, 247 rows) vs r91
  author runs1 (258): 247 common, **0 tuple mismatches**, +11 nav rows, 0
  removals. My rep1's PASS rows vs the same r90 green: 245 common, 0 mismatches.
- The only row diffs vs the author greens in reps 1–4 are the four documented
  pre-existing volatile classes (F2); no nav row or gate was ever affected.

### 2.2 Fresh arms — **33/33 clean**; allowlists and stream anchors load-bearing

11 arms × 3 fresh launches in the battery's launch shape on the frozen fixture
(`timeout -s KILL 15` + Python bound), receipts `arms/*.rep*.{out,err,rc}`,
re-checked under the production stderr rule (`probes/check_arms.py` → 33/33):

- rc == expected for every receipt (9 arms 0; `teardown_crash` −6 ×3);
  signature is an exact line prefix; exactly one `PASS nav_lattice` line per
  PASS arm; **every byte after the signature is a declared tail field**.
- `sync`/`bake` stderr: exactly one `ERROR:` line each (the whitelisted ones;
  the `at:`/backtrace continuation lines carry no `ERROR:` token; bake also
  emits the deprecation WARNING — no `ERROR:` substring, as declared).
- `teardown_crash`: rc=−6, stdout marker, stderr `double free or corruption
  (!prev)` 3/3; `teardown_clean`: rc=0, 0-byte stderr 3/3.
- **Production-classifier discrimination** (AST-extracted `classify_process` /
  `classify_streams`, `probes/classify-discriminate.txt`): `sync`/`bake`
  `bare=False, allowlist=True` 3/3 each (the two entries are load-bearing);
  all other arms `bare=True`; the crash row rejects both the
  fragment-spoofed-onto-stdout shape and the signature-on-stderr-only shape.
- Committed author receipts custody: 33/33 (`custody_check.py`) — rc, signature,
  exactly one `ERROR:` line, crash fragment, clean 0-byte stderr.

### 2.3 Boundary folds — all six encoded; five live-verified, one refuted in its stated formula (F1)

**Fold 1 — scheduler fields in diagnostic tails only: HOLDS.** Static: zero
field-form leaks (above). Behavioral: across 8 observations per row (5 battery
runs + 3 fresh reps) every pinned field is constant while the tails vary —
`path settle=4|5`, `query settle=4|5|6`, `sync ladder` 4 distinct shapes /
`first_reach=3|4|5`, `agent first_reachable=5|6`, `bake settle_a=2|3|4
settle_b=0|1|2|3`, `link settle=4|5|6`, `avoid seq_a/seq_b/vel_a/vel_b` 8/8
distinct (`sum_max` 19.8434…20.0000). `probes/tail-variance.txt`.

**Fold 2 — `iteration_id≥2 AND reach` gate with loud exhaustion: HOLDS.**
Source read (`_await_sync` lines 120–129, `SYNC_BOUND=48`, `_stale` prints +
`_exit_code=2`, `quit(_exit_code)`); every gated arm `return`s before its print
on `-1`. Own-rig gate probe (`gate` arm, 3 maps × 3 reps = 9/9):
`first_reach ∈ {3,4}`, `iter_at_reach=2`, **`reach_before_iter2=false`**.
Live stall surface: under `--fixed-fps 30`, **6/16 gating-arm runs emitted
`STALE nav_lattice <arm> sync_bound_exhausted bound=48` with rc=2 and zero PASS
lines** (`arms/fixedfps/`); under `--fixed-fps 120` all 16 gating-arm runs
synced inside the bound in my window (load ~55–70) — the margin is
load-dependent (the boundary's ff120 ran at load ~112 and never synced; the
reviewer saw 8/22 STALE), but **every exhaustion is loud** and no stale-PASS
shape exists.

**Fold 3 — same-frame race fields in tails only: HOLDS.** `dis_same` (sync,
region) and `fwd_disabled_same` (link) are printed after their pins (lines
301/512/832); the pinned halves (`chg_same=false`, `chg_settled=true`,
`dis_settled=false`, settled paths) held in every 60-tps receipt.

**Fold 4 — fin-before-reached query order: HOLDS.** Source: `fin_now =
is_navigation_finished()` before `is_target_reached()` in the walk loop
(lines 566–567), and `s_fin` before `s_reached` (549/551). Verifier-owned rig
(`agent_order`, 3/3): in the arrival frame `r1=false, fin=true, r2=true`
(dist=2.2741) — the artifact reproduced; `agent_reached_only` 3/3 reads `false`
— the stale shape the fold closes. The pinned final state is the post-refresh
read (it passed 55/55 loaded row-instances; the critic's M3 swap mutant,
cross-seat evidence, measured the pin itself order-robust); the tail
`reached_at` is not (deliberately unpinned).

**Fold 5 — avoidance invariants probe-side: HOLDS as an assertion; its stated
formula is refuted (see F1).** `sum_bound_ok=true dirs_ok=true` are in-fixture
assertions over exactly 5 paired measured frames; the committed rig measures
`sum_max ∈ [19.8434, 20.0000]` across 8 observations (never above 20.0000, the
bound touched exactly once). My discriminating rigs show the *general* bound is
`(d − r_a − r_b)/τ`, not `(r_a + r_b)/τ`; on the committed rig the two coincide
(40 − 20 = 20), so the assertion threshold `20.001` is rig-correct and the pin
is stable.

**Fold 6 — teardown crash negative control: HOLDS.** Fresh arms 3/3 rc=−6 with
the glibc fragment. Verifier-owned 4-cell rig ×3 (`arms/probe/teardown_*`):
live callback + free → SIGABRT ×3; cleared + free → 0 ×3; live + leak → SIGABRT
×3; cleared + leak → 0 ×3 — the crash requires a **live** callback, not the
free, exactly as the boundary qualifier states. `teardown_clean` is the
discipline control (0-byte stderr 3/3 fresh + 5/5 battery).

### 2.4 Independent re-derivations — **43/43**

`probes/rederive.py` recomputes every analytic pin from the fixture geometry:
diagonal/edge-center polylines (200√2 vs 301.2452 — the `length=282.8427` pin is
the CORRIDORFUNNEL(0)/pp0 corner-cut polyline, so there is no length/path
mismatch), clamp crossing points `(40,8.8889)`/`(40,22.2222)`/`(200,40)`, gap20
midpoint `(205,20)`, `maxlen=30` truncation `(24.2426,150.3015)`, `maxpolys=1`
first-edge cut, the metadata flag matrix, agent `160√2 → 226.27` and
`1.608√2 → 2.2741`, ORCA bound, bake erosion `±50→±55` and rect `−150→−145`,
region/link/census/sync/crash pins. All 43 closed forms agree with the
committed signatures.

**`maxrad` characterization** (`arms/probe/maxrad.*`, deterministic): R=0 →
full path; 1→0.9929, 5→0.9647, 10→0.9293, 20→0.8586, 30→0.7879, **60→0.5757
(the committed pin, byte-exact)**, 120→0.1515; 226→cut at the first-leg end;
300→full. For 1 ≤ R ≤ 120 the stub endpoint moves along the path as
`dx = 0.1414 − 0.001R`. The doc-level reading of "maximum radius" would predict
the opposite direction; the pin is empirical and stable (F3).

---

## 3. Findings (ranked)

**F1 (MEDIUM — evidence caption / committed comment; no landing effect).** The
avoidance invariant is attributed to `(r_a + r_b)/τ = 20` in the committed
fixture comment (`nav_lattice.gd:659–660`) and boundary §5.2. Five
verifier-owned rigs refute that as a general law and identify the real one,
`|safe_a| + |safe_b| ≤ (d − r_a − r_b)/τ` (surface gap / time horizon):

| rig (d, r, τ) | gap | radii sum | `(r_a+r_b)/τ` predicts | **gap/τ predicts** | measured `sum_max` |
|---|---|---|---|---|---|
| 40, 10, 1 (committed shape) | 20 | 20 | 20 | 20 | 19.84–20.00 |
| 40, 5, 1 | 30 | 10 | ≤10 | 30 | **29.76–30.00** |
| 60, 5, 1 | 50 | 10 | ≤10 | 50 | **49.62–50.00** |
| 60, 10, 1 | 40 | 20 | ≤20 | 40 | **39.68–39.83** |
| 40, 5, 2 | 30 | 10 | ≤5 | 15 | **14.94–15.00** |

The radii-sum formula is refuted by 3–6× margins; gap/τ fits all five (three of
the five rigs touch the bound exactly; the other two stay within 0.8% of it).
On the committed rig the two formulas coincide (gap = 20 = radii sum), which is
why the boundary's 100 samples could not discriminate — the landed assertion
(`sum <= 20.001`) is rig-correct, and `sum_bound_ok=true` is stable across 5
battery reps + 33 fresh reps. Recommended: a lane note (or comment fix) stating
the gap/τ law; do **not** reuse the `20.001` threshold with different radii
without recomputing it.

**F2 (LOW — pre-existing volatile classes; no r91 attribution).** Four of five
loaded battery reps failed at top level on non-nav rows: `negative_transition`
(3/5), `overlap` (2/5), `transition` (2/5), `input_lattice_pre_frame` (1/5),
plus the `probe_error_clause_surface` census cascade when a dead entry belongs
to a failed row. All are the classes r90's verifier and the r87 boundary
documented; rep5 was fully green and byte-identical to both author runs. The
author's "zero flakes observed" is host luck, not a landing property — lane
note only.

**F3 (LOW/INFO — `maxrad` semantics are inverted vs the doc-level reading; pin
stable).** The committed `path_return_max_radius=60` cell returns a 0.5757-long
start-anchored stub; the ladder shows the stub *shrinks* as R grows
(0.9929→0.1515 for R=1→120) and the full path returns at R=0/300. Deterministic
and byte-stable across reps, so the pin is sound; the scout's caption ("tiny
start-anchored stub") is accurate while a "maximum radius" reading is not.
Worth a one-line comment so a future reader does not assume monotone
truncation.

**F4 (INFO — labrat clause-(A) false positives, recorded).** The three
counterexamples the labrat raised (`n_a`, `pre_iter`, `settled`) are bare-token
hits inside `en_a=`/`n_a=`, `pre_iter=`, `dis_settled=`/`settled=`. Under
delimiter-aware matching there are **zero** field-form leaks, and the three
values are deliberate pins (boundary-confirmed cadence counts, pre-sync state,
state quintuple). The probe hypothesis as worded was falsified; the fixture
claim it was testing holds.

**F5 (INFO — custody: the author's battery runs are worktree-only).**
`corpus/live/r91-author/runs1|runs2` are not in `77d2f7e` (the commit carries
99 fresh-rep receipts + `manifest.sha256`; `runs*/` is gitignored). My
byte-identical comparison therefore used worktree artefacts; the durable green
substitute is my own rep5 (`runs/20261016T000657222526Z/verdicts.json`, in this
seat's untracked receipts, listed in `manifest.sha256`). Corroborates the
reviewer's F1.

---

## 4. Residual risks / disclosures

- **R1 — rep-level flake residue (pre-existing).** Four of five reps were not
  green; rep5 was, and it is tuple-identical to both author greens. No nav row
  flaked in any of 55 row-instances.
- **R2 — the 48-frame sync bound's margin is host-load dependent.** My ff120
  window (load ~55–70) synced every arm; the boundary's ff120 (load ~112) never
  did; my ff30 window stalled 6/16 gating runs. The failure direction is always
  loud (STALE + exit 2), which is the point of the fold; the bound is a failure
  surface, not a scheduler.
- **R3 — 60-tps-conditioned settle pins (1-frame margin).** The reviewer's F1 /
  critic's F1 stand: `chg_settled`/`dis_settled`/`gap20*`/region/link settled
  reads sit 1 frame above the boundary's measured worst case (≤3) and reject
  loudly under `--fixed-fps` (my ff30 `sync` rep1 shows `chg_settled=false` →
  pin mismatch, row FAIL, no mis-PASS).
- **R4 — build/host tokens.** `srv_methods=199`, `poly_methods=134`, enum
  arrays, `*_defaults`, 4-dp vertex pins and the glibc `double free or
  corruption` fragment are build/toolchain-conditional; each flips loudly.
- **R5 — `teardown_clean` reads a freed RID** (`has_cb=false`, silent in 3
  fresh + 5 battery runs). A future build that makes freed-RID reads loud fails
  the row loudly; the fix is to query before `free_rid` (value already
  captured). Author-disclosed; confirmed, not a defect.
- **R6 — foreign worktree churn.** A concurrent r92 lane is editing
  `run_battery.py`; any later commit folding it is a new artefact set whose r91
  rows would need a diff-scoped re-check. Nothing in this report reads those
  edits.

## 5. Blockers

None. Shipping/admission decisions remain with the operator.

## 6. Verdict

**VERIFIED-WITH-RESERVATIONS.** The committed `77d2f7e` bytes are exactly what
the author claims: frozen tree byte-identical (100,530 entries, 0-diff fileset,
content rc=0, all four fixture shas match, the scout→committed fold exactly as
declared), harness delta insertion-only (+88/−0, 251 CASES → 258 rows, the 11
rows at 236–246, both `expected_errors` entries, the `required_stderr` pin and
the floor gate present), **11/11 nav rows PASS in all five loaded battery reps
(55/55 row-instances) with rep5 a full 258/258 green tuple-identical to both
author runs**, 33/33 fresh arms with the two allowlists and the crash stream
anchors proven load-bearing, all six folds encoded and five live-verified
(gate 9/9 own-rig + 6/16 ff30 loud STALE; tails-only fields; fin-before-reached
artifact reproduced 3/3; crash qualifier reproduced on a 4-cell own rig; avoid
assertions stable), 43/43 closed-form re-derivations, and prior-row identity
247/247 with zero drift.

Reservations: (a) **F1** — the committed comment and boundary report attribute
the avoidance bound to `(r_a+r_b)/τ`, which five discriminating rigs refute; the
general law is `gap/τ`. The landing is unaffected (the two coincide on the
committed rig, the threshold is rig-correct, the pinned booleans are stable) —
this is a caption/comment accuracy defect, same class as r90's F1; (b) **F2** —
four of five reps carried pre-existing non-nav volatile rows (rep5 green covers
the landing); (c) **F3** — `maxrad` semantics are non-obvious (pin stable);
(d) **F5** — the author's battery run trees are worktree-only, so this seat's
green rep is the durable substitute until the wave folds evidence.
