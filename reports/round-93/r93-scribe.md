# game-dev-2d round 93 — scribe (r93-scribe): wave-B evidence custody + claim audit on committed `4b75151`

Seat `SCRIBE` (LEAF) | lane `g2d-r93-scribe` | round 93 | host **devin** (32 cores,
loadavg 74–87 with 60 foreign `yes` hogs for the whole session).
Read-only audit of the r93 AnimationPlayer + Tween landing: **no tracked file written, no
commit, no runtime config mutated**. The only writes are this report (new, untracked) and
`corpus/live/r93-scribe/**`. Every number below was recomputed from receipts on disk or from
a fresh launch on the committed bytes; nothing is quoted from the audited reports without
re-derivation.

Audit-time repository state: HEAD **`4b75151`** (*r93 author: 23 anim/tween rows (295 total)
— overshoot not clamp, N-1 await law, crossfade weight law, DEFERRED routes; 295/295 x2*).
`git status --porcelain -uno` was **empty** at audit start and at every re-check; the two
landed fixtures, `run_battery.py` and `project.godot` are byte-identical to `HEAD`, and the
three r93 dossier reports are tracked and equal to `HEAD`.

**Custody verdict: HOLDS — 4/4 declared law families are encoded and load-bearing.** All
three lane manifests verify completely (304/304, 1049/1049, 1086/1086) and each covers every
artefact in its directory except itself. **Two fresh battery runs on the committed bytes**
(worktree, and a `git archive HEAD` extract) are green on the r93 surface: **23/23 in both**,
the `r93_expected_errors_all_matched` floor gate `true` in both, `dead_entry_count=0` in
both, and **all 23 emitted lines byte-identical between the two runs**. All 23 pinned
signatures appear verbatim in **every** committed receipt of their own arm (387 receipts
checked; 16–25 per arm), 110/110 signature mutants are rejected by the production
classifier, and the four encoded laws re-derive from the raw receipts. Findings A1–A9 are
recorded; none falsifies a landed pin, allowlist entry, gate key or verdict.

---

## 0. What was run (method)

| # | check | command shape |
|---|---|---|
| 1 | manifest verification (all three lanes) | `sha256sum -c` equivalent in `static_audit.py` (hash + completeness vs `os.walk`) |
| 2 | committed-tree identity | worktree `sha256sum` vs `git show HEAD:<path>`; whole-commit numstat |
| 3 | CASES / row arithmetic + fold shape | AST parse of `HEAD:corpus/fixtures/run_battery.py` (`ast.literal_eval`) |
| 4 | insertion-only diff vs `HEAD~1` | `difflib.SequenceMatcher` over `git show HEAD~1:` vs `HEAD:` bytes |
| 5 | **fresh battery run 1 (worktree = committed bytes, under load)** | `python3 corpus/fixtures/run_battery.py --runs corpus/live/r93-scribe/battery-runs` (stamp `20261016T010005212465Z`) |
| 6 | **fresh battery run 2 (`git archive HEAD` extract)** | same harness from `/home/vgpnk/r93-committed-extract` → `battery-committed/` (stamp `20261016T010554750817Z`) |
| 7 | cross-run tuple comparison | `audit/compare_runs.py` (identical / tail-only / pin-diff per row) |
| 8 | receipt census: binding + cross-arm collisions | `audit/receipts_census.py` over every committed r93 receipt (scout + boundary + author) |
| 9 | law re-derivation | same script: overshoot inequalities, `pos10=9δ`, `w_i=(i−1)/(N−1)`, DEFERRED routes, manual-clock invariants, clause constancy |
| 10 | landed-row mutant test | `audit/recompute.py`: production `classify_process` (AST from HEAD, segment sha `749fa0607e7707e6…`) vs 110 mutated signatures |
| 11 | scout/boundary/author dossier recompute | `audit/recompute.py` + the scout's own `verify_rows.py` re-run |
| 12 | fresh single-arm receipts (17 arms ×3) | `fresh_arms.sh` on the committed extract, battery launch shape, isolated `XDG_DATA_HOME` |

No `lsp` device and no GDScript language server on this host (unchanged state, same as all
audited seats); no symbol edits were performed — the only "edit" surface was new receipts.
All probe launches were bounded (25 s `timeout -s KILL`); no orphaned processes were left.

**Frozen-`probeParent` disclosure.** Exactly **one** read-only `ufo-labrat` was dispatched
(agent `11415ff9`), one bounded three-clause hypothesis (signature binding, cross-arm
collision census, crossfade-law re-derivation). Its result is reported in §3.5; the seat's
toolset limitation (if any) is recorded with the finding.

---

## 1. Custody table — manifests, git tracking, verdict

| dossier artefact | manifest | verification | completeness | git state at audit |
|---|---|---|---|---|
| `corpus/live/r93-scout/` | `manifest.sha256`, **304 entries** | **304/304 OK** | exact — only the manifest itself is unlisted | 16 tracked / 304 on disk (`runs/` ignored by `corpus/live/.gitignore:5` `runs*/`) |
| `corpus/live/r93-boundary/` | `manifest.sha256`, **1049 entries** | **1049/1049 OK** | exact | 9 tracked / 1049 on disk (`runs/` ignored) |
| `corpus/live/r93-author/` | `manifest.sha256`, **1086 entries** | **1086/1086 OK** | exact | 235 tracked / 1086 on disk (`runs*/` ignored) |

The scout's/boundary's `runs/` trees and the author's `runs1..3` verdict trees are therefore
**worktree-only custody** — manifest-covered, not tracked (same convention as r87–r92; A8).
The author's lane additionally *tracks* the launch `proj/` copy and all 153 fresh-rep files
(`fresh-reps/`), which r92 did not.

---

## 2. Committed-tree identity + two fresh runs on the committed bytes

Worktree bytes == committed bytes for every landing file, so "committed tree only" holds for
all execution below:

| file | sha256 (worktree == `git show HEAD:`) |
|---|---|
| `corpus/fixtures/anim_lattice.gd` (689 lines) | `6a919ae04d4e7549…` |
| `corpus/fixtures/r93b_anim.gd` (466 lines) | `3c8dd8f10d6888e1…` |
| `corpus/fixtures/run_battery.py` (4336 lines) | `a79bfdd6f3f468d7…` |
| `corpus/fixtures/project.godot` (untouched by the landing) | `8de8b3af9cc737ed…` |
| `corpus/live/r93-scout/probes/anim_lattice.gd` | `6a919ae04d4e7549…` — **byte-copy** |
| `corpus/live/r93-boundary/probes/scout_anim_lattice.gd` | `6a919ae04d4e7549…` — **byte-copy** |
| `corpus/live/r93-boundary/probes/r93b_anim.gd` | `3c8dd8f10d6888e1…` — **byte-copy** |

The landed fixtures are literally the frozen probes (no fixture folds; every boundary fold
lands row-side), and the whole commit is **insertion-only** (`git show --numstat`: 239 files,
**0 deletions**; `run_battery.py` `+111/−0`, `anim_lattice.gd` `+689/−0`, `r93b_anim.gd`
`+466/−0`).

**Fresh battery run 1** — worktree at `4b75151`, tracked tree clean at launch, host under
foreign load (loadavg ≈74–87, 32 cores, 60 foreign `yes` hogs owned by another lane; no other
lane's battery was running in my window):

```
rep1 — stamp 20261016T010005212465Z  (battery-runs/, log battery-rep1.log)
  rows=295  verdict=FAIL (293/295)  r93 23/23 PASS
  r93_expected_errors_all_matched=true   dead_entry_count=0   rows_with_expected_errors=68
  fails: transition (exit=1), audio_playback (exit=2) — the pre-existing volatile classes; no r93 row
```

**Fresh battery run 2** — executed from a `git archive HEAD` extract
(`/home/vgpnk/r93-committed-extract`; fixture hashes verified before launch), independent of
the worktree:

```
rep2 — stamp 20261016T010554750817Z  (battery-committed/, log battery-rep2.log)
  rows=295  verdict=FAIL (294/295)  r93 23/23 PASS
  r93_expected_errors_all_matched=true   dead_entry_count=0   rows_with_expected_errors=68
  fails: overlap (exit=1) — the same pre-existing volatile input-route class; no r93 row
```

**Cross-run comparison** (`audit/compare_runs.py`, 295 rows): **263 identical**,
**16 tail-only** (differ only after the pinned signature), **13 pin-region-head diffs**,
0 signature-less rows, **3 verdict flips** — `transition`, `audio_playback`, `overlap`, all
pre-existing volatile classes, none r93. The 13 head diffs are explained and non-binding:
7 are disclosed r93 mode rows (`tweenproc`/`animproc`/`frame`/`blend`-family mode cells —
the pinned clause is still verbatim in both runs), 3 are envelope rows that matched the
*other* whitelisted payload arm across runs (`input89_edges_exact`, `input_lattice_api_press`,
`input_lattice_ui_ns`), and 3 are ordinary noisy heads with the pin verbatim in both
(`descendant_pipe_forged_signature_release`, `r88_surfaces_mp_loopback`,
`save_process_missing`). **The emitted signature field is byte-identical for all 295 rows
across the two runs** — including all 23 r93 rows.

---

## 3. The four encoded law families — re-derived from raw receipts

`audit/receipts_census.py` collected **387 committed r93 receipts** (54 scout canonical + 24
scout loadtest + 258 boundary + 51 author fresh reps) plus the per-row battery outputs of all
five committed runs. For every row the census checks the *pinned substring only* against
every receipt of the row's own arm.

### 3.1 Runtime overshoot is encoded, not clamped — `r93_anim_overshoot`

The `r93b_anim.gd --arm=purity` line pins `overshoot=[back025=0.10286344587803,back050=5.5]`
and `overshoot2=[spr050=10.510157585144,spr100=10.0,ela025=9.11611652374268]` on tweens
`scale:y 1→10` (BACK/EASE_IN_OUT) and `position:y 0→10` (SPRING/EASE_OUT, ELASTIC/EASE_OUT).

| check | result |
|---|---|
| receipts of the arm | **16** (boundary q/l/f30/f60/f120/f120l) |
| signature present in all | **16/16** |
| `back025 < 1.0` (below the tween's *start* value) | **16/16** — value byte-identical `0.10286344587803` |
| `spr050 > 10.0` (above the tween's *end* value) | **16/16** — value byte-identical `10.510157585144` |
| `ela025 ∈ (0,10)` | **16/16** — `9.11611652374268` |
| distinct values across all 16 receipts | **1 per token** |

The same row carries the no-clamp static path (`clamp=[neg=-5.0,over=15.0]`) and the extreme
deltas (`tiny=1e-8`, `huge` completes with `huge_running=false`, `neg=0.0,neg_elapsed=-0.5`,
`accum1000=1.0`), all constant 16/16. The scout's "runtime tween clamps" parenthetical is
falsified in the *landed* bytes, and the falsification is what the row pins.

### 3.2 N−1 await law — `r93_anim_await_offbyone`, `r93_anim_physics_tick`, `r93_anim_phys_delta`

| check | result |
|---|---|
| `idle=[x1=0.0` present in every `frame`-arm receipt | **16/16** (x1 is read after the *first* awaited process frame) |
| `pos10` under `--fixed-fps` | **exactly 9×δ**: 0.3 @ff30, 0.15 @ff60, 0.075 @ff120, 0.075 @ff120+16 hogs (err = 0) |
| `pos10` at the default rate (q/l/l32) | 0.0459…0.0719 — **a mode**, deliberately unpinned (author-disclosed) |
| `mixer_applied_10=10` | **16/16** |
| physics lattice `phys=[y1=0.0,y2=0.0,y3=1.66666674613953,y6=6.66666698455811]` | **16/16**, byte-identical |
| `phys_delta=0.01666666666667` | **16/16** |

So the row binds the N−1 law at its only launch-invariant instance (the first await), and the
fixed-fps lattice makes the general rule measurable; the pinned prefix ends before `,x2=` —
scope recorded (A6).

### 3.3 Crossfade weight law `w_i=(i−1)/(N−1)` at three granularities — `r93_anim_blend_finished` (+ `r93_anim_blend_interleaved`)

The `animblend` row pins the same 1 s blend (100→500) sampled at **three step granularities**:
`finished_010` (N=10 steps of 0.1), `finished_005` (N=20 steps of 0.05), `finished_020` (N=5
steps of 0.2). Re-deriving the law from the *pinned arrays*:

| array | N | first | last | max abs deviation from `100+400(i−1)/(N−1)` |
|---|---|---|---|---|
| `finished_010` | 10 | 100.0 | 500.0 | 2.37e-05 (float32 representation) |
| `finished_005` | 20 | 100.0 | 500.0 | 3.37e-05 |
| `finished_020` | 5 | 100.0 | 500.0 | 0.0 |

Each array is **byte-identical in all 23 receipts** of the arm (1 distinct array per token),
and the three mid-values differ per N (e.g. 2nd element 144.44 / 121.05 / 200.0), so the pin
itself encodes that mid-blend values are granularity-scoped. The `r93b_anim.gd --arm=blend`
row additionally pins `interleaved_eq_plain=true` — **16/16**, i.e. the same 10×0.1 lattice
with an awaited process frame between steps reproduces the plain lattice byte-for-byte — and
`hard_after_frame=500.0` (**16/16**).

### 3.4 DEFERRED flush routes — `r93_anim_deferred_flush`

| pinned token | receipts containing it |
|---|---|
| `manual_def=[after_adv=[],next_proc=[7,8],second_proc=[7,8]]` (queue on `advance()`, flush on next process frame, survives a second) | **16/16** |
| `manual_def_phys=[after_adv=[],after_phys=[7,8]]` (**physics frame also flushes** — the new route) | **16/16** |
| `two_adv=[after=[],flush=[7,8]]` (two advances still queue) | **16/16** |
| `immediate=[after_adv=[7,8],after_frame=[7,8]]` (IMMEDIATE lands inside `advance()`) | **16/16** |

### 3.5 Binding census, collisions, clause constancy, and the labrat

* **Binding:** all **23/23** rows hit in **every** receipt of their own arm — 16 (r93b arms),
  17–25 (anim_lattice arms) receipts each; no miss.
* **Cross-arm collisions:** exactly **one** — `phys_delta=0.01666666666667`
  (`r93_anim_phys_delta`, `--arm=frame`) also appears in all 16 `clock`-arm receipts. The
  `clock` arm is **not a CASES row**, so the substring can only ever be observed inside a
  `frame` run; benign (A7, same finding the author's own labrat returned). No other row
  collides.
* **Mode-cell clause constancy** (the only pinnable tokens of the mode arms):
  `tweenproc stable=[…]` and `phys_manual=[…]` **25/25**; `animproc stable=[…]` and
  `manual=[…] frozen=[…] inactive=[…]` **25/25**; `frame` `mixer_applied_10`+`phys` **16/16**;
  `deferred` 4 tokens **16/16**; `purity` 2 tokens **16/16**; `manual_inv` `inv`+`step_exact`
  **16/16**; `blend` 2 tokens **16/16**.
* **Labrat (frozen `probeParent`, one dispatch, agent `11415ff9`):** dispatched on the
  three-clause hypothesis (signature binding, cross-arm collision census, crossfade-law
  re-derivation). **All three clauses PASS.** Clause 1: every canonical `.out` receipt of
  each row's own arm contains the pin verbatim (31–42 receipts per row across scout /
  boundary / author / verifier / reviewer / scribe trees; the only misses are the critic's
  intentional mutants and the disclosed `defect/noscript` receipt). Clause 2: exactly one
  collision — `phys_delta=0.01666666666667` in **30/30** `clock`-arm receipts across all
  trees (root cause measured: `r93b_anim` prints `phys_delta` unconditionally at
  phys_tps=60); no other pin collides, and no `defect`/`disc-` receipt contains any pin.
  Clause 3: max deviations `2.3736e-05` / `3.3730e-05` / `0.0` (N=10/20/5) and
  `interleaved_eq_plain=true` in **37/37** blend-arm receipts — matching my own
  recompute (2.37e-05 / 3.37e-05 / 0.0, §3.3). No toolset limitation was hit.

---

## 4. The floor gate — `r93_expected_errors_all_matched`

* `CASES` at `HEAD` is **288 tuples** (265 + 23); the 23 `r93_*` rows are contiguous at
  indices **261–283**, immediately after `r92_tilemap_nullts_crash` (260) and **ahead** of
  `crash_spontaneous_sigabrt`, `crash_self_sigkill`, `descendant_pipe_detached_control`,
  `descendant_pipe_forged_signature_release` — the sleep-8 adjacency the comment requires is
  preserved.
* `expected_errors` carries **68 cases** (the last 9 are `r92_tilemap_*`); `required_stderr`
  carries **3 cases** (`geo2d_lattice_lineempty`, `nav_lattice_teardown_crash`,
  `r92_tilemap_nullts_crash`). **No `r93_*` key exists in either** — the r93 block is
  `ERROR:`-clean by measurement (0 B stderr in 54/54 scout canonical, 24/24 scout loadtest,
  258/258 boundary receipts on disk, 51/51 author fresh reps, 51/51 scribe fresh reps).
* The gate exists, is prefix-scoped to `r93_`, and is **vacuously `true` today** (zero
  entries) — deliberately carried so a future r93 allowlist entry cannot die silently, same
  named-by-round shape as r87–r92. `rows_with_expected_errors` stays **68** in every run
  (author ×3, scribe ×2), i.e. the landing added no allowlist rows.
* In both of my committed-byte runs the gate is `true`, `dead_entry_count=0`,
  `census_bare_classifier_consistent=true`, `census_allowlisted_reproduces_verdicts=true`.

---

## 5. Dossier claim recompute

### 5.1 Author (`reports/round-93/r93-author.md`, `4b75151`)

| claim | recomputed |
|---|---|
| fixtures = byte-copies of the frozen probes; `project.godot` untouched | ✓ `6a919ae0…`/`3c8dd8f1…` in all copies; commit file list excludes `project.godot` |
| `run_battery.py` +111/−0, CASES 265→288, rows 272→295 | ✓ insertion-only (two insert blocks: the 101-line row block + the 10-line gate block), AST-verified |
| two green runs 295/295 | ✓ `runs1` `20261016T003655…` and `runs3` `20261016T004609…`, both PASS 295/295 |
| interim run fails only on documented volatile classes; no r93 row flaked | ✓ `runs2` fails = `crash_spontaneous_sigabrt` + knock-ons `probe_spontaneous_crash_classification`, `probe_error_clause_surface`; **r93 23/23 PASS in all three runs** |
| 51 fresh reps (17 arms ×3), all rc=0, all 0 B stderr | ✓ 51 `out` files / 153 files, `rc=[0]`, `err_bytes=[0]` |
| all 23 rows classify PASS ×3 through the production `classify_process` (segment sha `749fa0607e7707e6`) | ✓ **69/69**; my extracted segment sha is `749fa0607e7707e6…` — the same segment r89–r92 pinned |
| all 15 scout gating rows carried verbatim | ✓ byte-identical (case name, flags, signature) for all 15 — and the scout's own `verify_rows.py` re-run reproduces **15 rows / 108 checks / rejected=[]** |
| clause rows are the documented modes; full-line arms `uniq=1` | ✓ my 3-rep fresh set: full-line arms uniq=1; clause arms up to uniq=3 |
| manifest 1087 entries | **✗ actual 1086 entries** (A2); the manifest covers exactly the 1086 lane files (completeness exact) |
| "51 receipts (out/err/rc)" | **label**: 153 files = 51 reps × 3 streams (A3) |
| "in 258/258 frame runs" (harness comment + report) | **✗ mislabel**: the `frame` arm has 16 receipts (258 is the whole matrix) — the pin itself is 16/16 committed + 3/3 author + 3/3 scribe (A4) |

### 5.2 Boundary (`reports/round-93/r93-boundary.md`)

* 258 canonical receipts on disk, batches `q` 51, `l` 51, `f30/f60/f120/f120l` 34 each,
  `l32` 20; **rc = 0 for all, stderr 0 B for all, 0 timeouts**, wall max **2.26 s** — ✓
  (the 16 extended-purity runs overwrote the `*_purity` receipts in place, so the on-disk
  set is 258 valid receipt sets from 274 launches; A9).
* "9/11 cells byte-identical to the scout, 2 are modes" — ✓ my cross table: census, tweenval,
  tweenval_grid, animtrack, animmethod, tweenchain, animblend, tweenstep, animseek are
  byte-identical to the scout's canonical bytes in every batch; tweenproc/animproc differ.
* "the two `stable` clauses byte-identical in 9/9 (extended 32/32)" — ✓ extended further:
  25/25 receipts per arm incl. every batch.
* "`x1=0.0` in 258/258 runs of the frame arm" — **✗ mislabel** (16 receipts; A4).
* purity launch-invariant 16/16; clock 16/16 unique (fingerprint, intentionally unauthored) — ✓
* harness defect (162 vacuous runs, `runs/defect/noscript.{out,err,rc}` preserved) — recorded
  as self-reported; the defect receipts are manifest-covered and the re-run overwrote the
  voided receipts, so no invalid receipt survives on disk.

### 5.3 Scout (`reports/round-93/r93-scout.md`)

* 54 canonical runs (4 pure ×3 + 7 runtime ×6) and 24 loadtest runs (8 cells ×3); all rc=0,
  all stderr 0 B — ✓ recomputed from receipts.
* canonical `out_uniq`: 9 cells = 1; `tweenproc` = 5; `animproc` = 6 — ✓ exact.
* 15 gating rows / 108 receipt checks / `rejected=[]` — ✓ re-run of the scout's own verifier
  and my independent classifier pass.
* "runtime tween clamps" (§3.2) — falsified by the boundary and **not inherited**: the
  landed row pins the opposite (A-landing, correct).
* §8 open unknown "independent replication is missing" — closed by the boundary's second
  seat and again by this seat's two fresh runs.

---

## 6. Landed-row mutant test (are the pins load-bearing?)

`audit/recompute.py` extracts `classify_process` verbatim from `HEAD` and applies each row's
*full* pass condition to a real receipt, mutating the pinned signature one token at a time:

```
TOTAL mutants=110  rejected=110  accepted=0
  value flips       57
  boolean flips      7
  appended conjuncts 46
```

Every numeric value-flip, every `true↔false` flip and every appended never-emitted conjunct
(`r93_forge=1`, `forged=1`) is rejected on its own row's receipt — the classifier still
requires the signature to appear verbatim in the emitted output, so the 23 pins are not
decorative. (This is the same shape as r92's 396/396 result; the mutant count is smaller
because this seat caps at 8 numeric tokens per row plus all boolean tokens.)

---

## 7. Arithmetic cross-check ledger (all reconcile)

| identity | result |
|---|---|
| landing: CASES 265 = 265 + 0 deletions; 288 = 265 + 23; rows 295 = 272 + 23 (7 meta) | ✓ |
| r93 rows contiguous at 261–283; crash/descendant tail intact | ✓ |
| `expected_errors` 68 cases / 0 r93 keys; `required_stderr` 3 cases / 0 r93 keys | ✓ |
| manifest arithmetic: 304 = 305 − self; 1049 = 1050 − self; **1086 = 1087 − self** | ✓ (the author's "1087" counted the self entry — A2) |
| author fresh-reps: 153 files = 17 arms × 3 reps × 3 streams; 51 reps | ✓ |
| author runs: 295 rows × 3; r93 23/23 × 3; green ×2 | ✓ |
| boundary: 258 receipts = 51 + 51 + 34×4 + 20; 274 launches incl. the 16 overwriting purity re-runs | ✓ |
| scout: 54 canonical = 4×3 + 7×6; +24 loadtest = 78 gated runs | ✓ |
| receipt census: 387 = 54 + 24 + 258 + 51; 23/23 signatures all-hit | ✓ |
| mutants: 110 = 57 + 7 + 46; rejected 110 | ✓ |
| mine: rep1 293/295, rep2 294/295; r93 23/23 ×2; cross-run 263 identical / 16 tail-only / 13 head-diff (all signature-verbatim) / 3 verdict flips (volatile classes) | ✓ |

---

## 8. Adjudication items (ranked)

| id | dossier | item | severity | disposition |
|---|---|---|---|---|
| **A1** | carried from r92 (harness comment) | The comment above the r92 `required_stderr` block still reads "binds the **rc=-11** to the engine's own signal-11 crash handler" (line 1338); the row's `expected_exit` is **−6** (SIGABRT). The r92 scribe recorded this and the r93 landing did not touch it (the r93 diff is insertion-only). The pin itself is right. | **low** (comment-only; a future reader could "fix" the row to −11 and silently break it) | reword to "binds the rc=−6 (SIGABRT through the engine's crash handler) to the signal-11 handler header …" — same recorded class as r91's comment-formula defect |
| **A2** | author (evidence index) | The manifest claim is off: **1086** entries (not 1087), and the "source reports" row of the evidence index is **not** manifest-covered (the manifest lists only lane-relative paths). Both reports are git-tracked, so custody holds, but the manifest does not cover them. | **low** (label/custody description) | say "1086 entries, covering every file under the lane dir; the reports are git-tracked, not manifest-covered" |
| **A3** | author §"Fresh-arm evidence" | "51 receipts (`out`/`err`/`rc`)" is imprecise: the directory holds **153 files** = 51 reps × 3 streams. | **info** (label) | reword to "51 reps × (out/err/rc)" — r92 A5 class |
| **A4** | boundary §1/§9 + landed harness comment | "`x1=0.0` in **258/258** runs of the `frame` arm" — the `frame` arm has **16** receipts (q3 + l3 + l32 2 + ff 2×4); 258 is the whole matrix. The pinned instance is 16/16 committed + 3/3 author + 3/3 scribe, so no verdict impact. | **low** (claim mislabel; identical wording propagated into the landed comment) | reword to "16/16 frame-arm receipts (all launch modes)"; the law statement itself is correct |
| **A5** | harness comment | "The manual clock … are byte-stable under loadavg 118 and 32 hogs" — the **pinned tokens** are (16/16); the arm's full stdout varies per rep (uniq 2–3 per batch) because the unpaused control and `proc_delta` vary. | **low** (scope imprecision in a comment; the row pins only the invariant tokens) | say "the pinned invariant tokens are byte-stable; the unpaused control and `proc_delta` are modes" |
| **A6** | landing (scope) | `r93_anim_await_offbyone` pins the prefix `idle=[x1=0.0` (ends before `,x2=`): it binds the N−1 law's first-await instance only; the general `pos10=(N−1)δ` is a mode at the default rate and is deliberately unpinned (disclosed in the comment). | info | keep; the row is correctly scoped, the general law is measured but not pinned |
| **A7** | landing (collision) | `phys_delta=0.01666666666667` also matches the `clock` arm's launch-fingerprint line. `clock` is not a CASES row, so the substring can only be observed inside a `frame` run; if a future fixture bumps `physics_ticks_per_second` the `frame` row fails as designed. | info | keep (author/labrat disclosed; re-confirmed here) |
| **A8** | custody | Author `runs1..3` verdict trees and the scout/boundary `runs/` trees are gitignored (`runs*/`) but manifest-covered → **worktree-only custody**; the two green runs' `verdicts.json` would be lost on a worktree prune (their per-row verdicts survive in the tracked `battery1..3.log`). | info | same convention as r87–r92; recorded, not escalated |
| **A9** | boundary provenance | The 16 extended-purity runs **overwrote** the `*_purity` receipts in place (274 launches → 258 receipt sets on disk). All on-disk receipts are valid; the overwrite is disclosed in `RECEIPTS.md`. | info | recorded; no invalid receipt survives |

---

## 9. Remaining risks / blockers

1. **No blockers to the landing.** Both committed-byte runs are green on the r93 surface
   (23/23 each, floor gate true, zero dead entries), the three manifests verify completely,
   and every recomputable dossier claim reproduces (three low-severity label/comment defects
   aside).
2. **Comment defects A1/A4/A5** could mislead a future author: A1 can cause a −11 re-pin of a
   load-bearing crash row; A4/A5 are claim-scope wording in the landed comment.
3. **Worktree-only custody (A8)** for the author's three battery runs and the
   scout/boundary `runs/` trees: manifest-verified but not tracked.
4. **Host-conditional pins by design**: `anim_consts`/`mixer_consts`/enum orders, signal
   lists, `an_m_count`/`ap_m_count`/`tw_m_count` method counts, 4-dp floats,
   `phys_delta=0.01666666666667` (60-tps project) — all flip loudly on an engine or
   `project.godot` bump (intended; same class as existing census pins).
5. **Mode-cell pins are clause-only**: `tweenproc`/`animproc`/`frame`/`blend`/`deferred`/
   `manual_inv` full lines vary under load; the rows pin only the invariant clauses
   (verified constant 16/16–25/25). A future fixture change to the *unpinned* counters cannot
   fail these rows — by design, and the author discloses it.
6. **Pre-existing flake classes** reproduce under load on committed bytes
   (`transition`, `audio_playback` in my rep1; `overlap` in my rep2;
   `crash_spontaneous_sigabrt` + knock-ons in the author's `runs2`). None touches an r93
   row.
7. **The `r93_expected_errors_all_matched` gate is vacuously true today** (zero r93
   allowlist entries). It is correctly prefix-scoped and will cover a future entry, but it
   cannot fail on the current bytes — that is the intended "carried floor" semantics, not a
   false green.
8. **`--fixed-fps` boot transient** (`ff30` first six deltas are not 1/30) is a measured,
   unpinned artifact; the fixed-fps *lattice* pins (`pos10=9δ`) are taken at the settled
   regime and are exact in all ff receipts.

---

## 10. Host notes / cleanup

- I added no load of my own beyond the two batteries, 51 fresh-arm launches and no `yes`
  hogs; no orphaned processes (`ps` clean of my launches). The 60 foreign `yes` hogs belong
  to another lane and were left untouched. Host loadavg 74–87 on 32 cores throughout.
- `/tmp` is a 16 GB tmpfs at 76 % used; the committed-tree extract was therefore run from
  `/home` (`/home/vgpnk/r93-committed-extract`, retained this session).
- `corpus/fixtures/.godot/` was not created in the repo (the battery writes its engine cache
  into each run's own `scratch/`; my fresh-arm project lives outside the repo).
- Zero tracked files written by this seat; `git status --porcelain -uno` was empty at audit
  start and at every re-check through both battery runs. **Late-window note:** after the
  audit's executions, a concurrent lane began an in-flight r94 insertion into
  `corpus/fixtures/run_battery.py` (uncommitted `M`, +91 lines, mtime 02:56:54 — not this
  seat's write, left untouched per "preserve unrelated work"). Every number in this report
  was derived from `git show HEAD:` bytes or the hash-verified `git archive HEAD` extract,
  so the dirty tail does not affect any custody claim above; it is recorded only so a
  later reader does not mistake it for scribe work.

---

## 11. Evidence index

All under `corpus/live/r93-scribe/`; `manifest.sha256` covers every artefact in that
directory except itself.

| artefact | path | notes |
|---|---|---|
| battery run 1 (worktree, committed bytes) | `battery-runs/20261016T010005212465Z/verdicts.json` + `battery-rep1.log` | 295 rows, 293/295, r93 23/23, gate true, dead 0 |
| battery run 2 (`git archive HEAD` extract) | `battery-committed/20261016T010554750817Z/verdicts.json` + `battery-rep2.log` | 295 rows, 294/295, r93 23/23, gate true, dead 0 |
| fresh single-arm receipts (17 arms ×3) | `fresh/<fixture>.<arm>.rep<N>.{out,err,rc}` | battery launch shape, committed extract, rc=0, 0 B stderr |
| fresh-arm driver | `fresh_arms.sh` | replay script |
| static custody + folds + manifests | `audit/static_audit.py` → `static_audit.json` | landing identity, CASES/rows, allowlists, gate, manifest completeness, diff shape |
| receipt census + law re-derivation | `audit/receipts_census.py` → `receipts_census.json` | 387 receipts; binding 23/23; collisions; clauses; four laws |
| dossier recompute + mutant test | `audit/recompute.py` → `recompute.json` | scout/boundary/author recompute; 110/110 mutants rejected |
| cross-run comparison | `audit/compare_runs.py` → `compare_runs.json` | identical / tail-only / pin-diff per row |
| lane index / replay | `RECEIPTS.md` | commands + headline numbers |
| source reports | `reports/round-93/r93-{scout,boundary,author}.md` | tracked, sha-verified |
