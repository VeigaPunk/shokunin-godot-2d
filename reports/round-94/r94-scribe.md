# game-dev-2d round 94 — scribe (r94-scribe): wave-B evidence custody + claim audit on committed `c7228893`

Seat `SCRIBE` (LEAF) | lane `g2d-r94-scribe` | round 94 | host **devin** (32 cores,
loadavg 74–95 with 60–68 foreign `yes` hogs and ~10 concurrent sibling batteries for the
whole session).
Read-only audit of the r94 CPUParticles2D + GPUParticles2D landing: **no tracked file
written, no commit, no runtime config mutated**. The only writes are this report (new,
untracked) and `corpus/live/r94-scribe/**`. Every number below was recomputed from
`git show HEAD:` bytes, from receipts on disk, or from fresh launches on the committed
bytes; nothing is quoted from the audited reports without re-derivation.

Audit-time repository state: HEAD **`c7228893`** (*r94 author: 19 particles rows (314
total) — folded scout probe (4-line diff: okb windows, floor); 314/314 x2*), parent
`94377598` (r93 scribe). `git status --porcelain -uno` was **empty** through the audit's
executions; the landed fixture, `run_battery.py` and `project.godot` are byte-identical
to `HEAD` (verified on `git show HEAD:` bytes and on a `git archive HEAD` extract), and
the three r94 dossier reports are tracked and equal to `HEAD`. **Late-window note:** at
03:41:30 a concurrent r95-author lane inserted its block into the *worktree*
`run_battery.py` (+163 lines, 52 new rows: `dss_lattice_*` + `r95b_order_*`, CASES
307 → 359). It is **foreign, untouched by this seat**, and the r94 content is provably
unaffected: the 19 r94 tuples and the `r94_expected_errors_all_matched` comprehension are
byte-identical between `HEAD` and the dirty worktree, and both of my battery runs used
committed bytes (run 1 copied the fixtures before the foreign write; run 2 ran from the
extract). Every number below is derived from `HEAD` bytes, the extract, or receipts.

**Custody verdict: HOLDS — all 19 declared pins are encoded, load-bearing and verified
on the committed bytes.** The landing is insertion-only (+1055/−0), all 19 landed
signatures are byte-identical to the scout's frozen `ROWS_PREFIX` rows, both lane
manifests verify completely (598/598, 2953/2953), and **two fresh battery runs on the
committed bytes** are green on the r94 surface (19/19 PASS in both; floor gate `true` in
both; run 2 is a full 314/314 PASS). 653 own-arm receipt checks give 650 hits; the only
3 misses are the boundary's three `cpu_pause` ff30 rejections on the *frozen probe*,
which the landed `[1,7]` fold resolves — re-measured by this seat on the landed bytes
(3/3 `ok=true` at `--fixed-fps 30`). All 579 signature mutants and 522 pinned-region
output mutants are rejected by the production classifier. Findings A1–A10 are recorded;
none falsifies a landed pin, allowlist entry, gate key or verdict.

---

## 0. What was run (method)

| # | check | command shape |
|---|---|---|
| 1 | landing identity (worktree vs `HEAD:` blobs) | `static_audit.py` |
| 2 | commit shape + insertion-only proof vs `HEAD~1` | `git show --numstat`, `difflib.SequenceMatcher` |
| 3 | CASES / row arithmetic, contiguity, allowlists, gate | AST over `HEAD:corpus/fixtures/run_battery.py` |
| 4 | fixture vs frozen probe: non-comment code-line diff | comment-stripped `SequenceMatcher` |
| 5 | lane manifest verification + completeness + tracking | sha256 + `os.walk` + `git ls-files` |
| 6 | scout evidence-integrity recompute | mtimes vs probe mtime, hash mentions |
| 7 | **fresh battery run 1** (worktree = committed bytes, under load) | `python3 corpus/fixtures/run_battery.py --runs corpus/live/r94-scribe/battery-runs` (stamp `20261016T063407989183Z`) |
| 8 | **fresh battery run 2** (`git archive HEAD` extract) | same harness from `/home/vgpnk/r94-committed-extract` → `battery-committed/` (stamp `20261016T064405071549Z`) |
| 9 | fresh single-arm receipts on the landed fixture | `fresh_arms.py`: 19 arms × 3 default + cpu_pause/lifetime/request × 3 at `--fixed-fps 30` and `60` (75 receipts) |
| 10 | receipts census (signature binding, collisions, clause constancy) | `receipts_census.py` over 15 sources / 1028 receipts |
| 11 | law re-derivation from raw receipts | `laws_recompute.py` |
| 12 | landed-row mutant test (signature + output) | `recompute.py`, production `classify_process` (segment sha `749fa0607e7707e6…`) |
| 13 | floor-gate loudness (planted dead entry) | `floor_gate.py`, extracted gate expression |
| 14 | classifier properties probe | `classifier_properties.py` |
| 15 | cross-run comparison | `compare_runs.py` |
| 16 | scout verifier re-run (read-only) | `corpus/live/r94-scout/verify_rows.py` |

No `lsp` device and no GDScript language server on this host (unchanged state, same as
r89–r93); no symbol edits were performed — the only "edit" surface was new receipts.
All launches were bounded (`timeout -s KILL 25` for single arms; the battery's own
per-case bounds); no orphaned processes were left.

**Frozen-`probeParent` disclosure.** Exactly **one** read-only `ufo-labrat` was
dispatched (agent `bd3f872e`, one bounded three-clause static hypothesis: landed
signatures vs scout `ROWS_PREFIX`; fixture-vs-probe fold shape; gate/allowlist scope).
Its result is in §5.4; its tool limitation (no shell/diff) is recorded there and the
clause it could not close was closed by this seat's own full code-line diff (§1).

---

## 1. Committed-tree identity + the landing's shape

Worktree bytes == committed bytes for every landing file **at audit time** (the only
later divergence is the foreign r95 insertion of the header note), so "committed tree
only" holds for all execution below:

| file | sha256 (`HEAD` blob; worktree identical at audit time) | size |
|---|---|---|
| `corpus/fixtures/particles_lattice.gd` (new) | `0701e813e50cdb50…c00a9` | 763 lines |
| `corpus/fixtures/run_battery.py` (`+91/−0`) | `2b1f4df5426a8da6…4238` | 4427 lines |
| `corpus/fixtures/project.godot` (untouched) | `8de8b3af9cc737ed…6e9` | 2 lines |
| `reports/round-94/r94-author.md` (new) | tracked | 201 lines |
| `reports/round-94/r94-scout.md`, `r94-boundary.md` | tracked | 483 / 477 lines |

The commit `c7228893` is **3 files, 1055 insertions, 0 deletions**
(`763/0`, `91/0`, `201/0`). `run_battery.py` vs `HEAD~1` is insertion-only: two blocks,
80 lines at old line 798 (the r94 CASES block) and 11 lines at old line 3023 (the floor
gate), `deleted = 0`.

**CASES / row arithmetic (AST):** CASES **288 → 307** tuples; results rows **295 → 314**
(7 meta). The 19 `r94_particles_*` rows are **contiguous at indices 284–302**,
immediately after `r93_anim_blend_interleaved` (283) and **ahead** of the
crash/descendant tail (`crash_spontaneous_sigabrt` 303 … `descendant_pipe_forged_signature_release`
306) — the sleep-8 adjacency the comment requires is preserved.

**Allowlists:** the `expected_errors` dict carries **72 keys** (69 non-empty; 3 map to
empty tuples), **no `r94_` key**; `required_stderr` carries exactly 3 keys
(`geo2d_lattice_lineempty`, `nav_lattice_teardown_crash`, `r92_tilemap_nullts_crash`),
**no `r94_` key**. The r94 block is therefore `ERROR:`-clean by measurement — confirmed
on every r94 receipt of every source (§3).

**Floor gate:** `r94_expected_errors_all_matched` present exactly once
(`run_battery.py:3109`), comprehension scoped by `r["case"].startswith("r94_")`; the
named-by-round family now spans `phys2d_` + r87–r94.

**Fixture vs frozen probe:** the comment-stripped code diff is **exactly 4 lines**:
three `_okb(…, 4, 7) → _okb(…, 1, 7)` window constants in `_arm_cpu_pause`
(`particles_lattice.gd:504–506`) and `round(0.5/spec) → floor(0.5/spec)` in
`_arm_cpu_request` (line 659). Everything else that differs (22 extra lines,
763 vs 741) is comment or blank. All 19 landed signatures are **byte-identical** to the
scout's `ROWS_PREFIX` entries in `corpus/live/r94-scout/author-rows.py.txt`
(`census` = 8785-char string in both).

---

## 2. Two fresh battery runs on the committed bytes

**Run 1 — worktree at `c7228893`** (tracked tree clean at launch; host under ~10
concurrent sibling batteries, loadavg ≈ 86, 60+ foreign `yes` hogs):

```
rep1 — stamp 20261016T063407989183Z  (battery-runs/, log battery-rep1.log)
  rows=314  verdict=FAIL (309/314)   r94 19/19 PASS
  r94_expected_errors_all_matched=true   dead_entry_count=2   rows_with_expected_errors=68
  fails: overlap, transition, negative_transition, audio_playback
         + meta knock-on probe_error_clause_surface (census_bare_classifier_consistent=false)
```

**Run 2 — executed from a `git archive HEAD` extract**
(`/home/vgpnk/r94-committed-extract`; fixture hashes verified before launch, independent
of the worktree):

```
rep2 — stamp 20261016T064405071549Z  (battery-committed/, log battery-rep2.log)
  rows=314  verdict=PASS (314/314)   r94 19/19 PASS
  r94_expected_errors_all_matched=true   dead_entry_count=0   rows_with_expected_errors=68
  fails: none
```

**Cross-run comparison** (`audit/compare_runs.py`, 314 rows): **277 identical**,
**4 tail-only** — all four are r94 rows (`cpu_pause`, `cpu_restart`, `cpu_speed_pre`,
`gpu_headless`, the declared ±1-tick tail cells) — **28 head-diff** (pre-existing
classes: crash/descendant, input, nav, r92/r93 mode rows, save) and **5 verdict flips**
(`overlap`, `transition`, `negative_transition`, `audio_playback`, and the meta
knock-on), all pre-existing volatile classes, **none r94**. The emitted *gating prefix*
of all 19 r94 rows is byte-identical between the two runs.

The run-1 volatile set is the documented host class: `overlap` ("signal occurred before
physics overlap observation"), `transition` (initial `current_scene` identity mismatch),
`audio_playback` (position did not advance) and `negative_transition` — the latter a
knock-on (`SCRIPT ERROR: Cannot call method 'get_instance_id' on a null value` at
`controls/scene_transition_negative.gd:22` → its two allowlisted `ERROR:` lines never
appear → 2 dead entries → the meta row fails **closed**, as designed). No r94 row
flaked in either run.

---

## 3. The declared laws — re-derived from raw receipts

`audit/receipts_census.py` collected **1028 receipts** across 15 sources (scout
canonical 105 + loadtest 38; boundary matrix/reprobe 734; author battery rows 38;
scribe fresh 57 + ff30 9 + ff60 9 + battery rows 38). **653 own-arm checks → 650 hits,
3 misses, 0 cross-arm collisions.** The 3 misses are exactly the boundary's three
`cpu_pause` ff30 receipts on the frozen probe (`ok=false vis_parent_ok=false
pm_disabled_ok=false`, `vis_parent/pm_disabled fin_after=2`); the landed fixture passes
them (§3.4).

| law | pinned token(s) | measured across receipts |
|---|---|---|
| one-shot ladder | `cpu_lifetime ok=true l01/l025/l05/l1_ok=true` | deltas: `l01∈{6,7,8}`, `l025∈{12,13,14,15}`, `l05∈{28,29,30}`, `l1∈{58,59,60}` (50 receipts per token); 60-tps mode `round(L·60)` = 6/15/30/60; the window's 12/28/58 instances are the ff30 mode |
| streamed emission | `cpu_expl ok=true e1/e05/e0_ok=true` | `e1∈{28,29,30}`, `e05∈{40,42,43}`, `e0∈{56,57}` vs model `30 / 43.125 / 56.25` ticks |
| speed / preprocess / fixed_fps | `cpu_speed_pre ok=true ss2/ss05/pre25/ff30_ok=true` | `ss2∈{15,16}`, `ss05∈{58,59,60}`, `pre25∈{12,14,15}`, `ff30∈{28,30,31}` |
| request lattice | `cpu_request ok=true step010/step005_ok=true` | `fin_call1=6` (step 0.10) and `11` (step 0.05) in every receipt incl. ff30/ff60; the boundary's 7-step `floor(L/step)+1` table reproduced from `runs/quiet/r94b_req_var.rep1.out` (0.20→3, 0.30→2 falsify `round`) |
| pause levers | `cpu_pause ok=true vis/vis_parent/pm_disabled/ts0_ok=true` | resume windows by condition: `vis∈{4,5,6}`, `vis_parent/pm_disabled∈{2,4,5}` (2 only at ff30), `ts0∈{18,19,20}` — all inside the landed `[1,7]` / `[15,25]` |
| never-emitter | `cpu_never ok=true never_fired=true n_fin=0` | `n_fin=0`, `fin_delta=-1` in every receipt |
| contamination control | `cpu_contam ok=true n_never=2` | both never nodes `fin_delta=0 n=1` in every receipt (`add_pf≥1` rule, boundary §8 reframing) |
| stop / oneshot | `cpu_stop`, `cpu_oneshot_off`, `cpu_oneshot_flag` | `stop10∈{20,21}`, `stop40∈{18,19,20}`; `fin_after_off∈{50,51}`; `fin_after_flag=-1`, `n_fin=0` |
| restart / retrigger | `cpu_restart`, `cpu_retrigger` | `first_delta∈{15,16}`, `second_after∈{12,14,15}`, `n_fin=2`, `first_em=false first_ise=false em_after_restart=true` |
| mid-flight params | `cpu_lt_mid`, `cpu_speed_mid`, `cpu_amount_mid` | `fin_after_set∈{2,3}` (lifetime), `=12` (speed), `=0` with `em_fin=true ise_fin=true em_at_end=false` (amount hazard) |
| GPU headless | `gpu_headless ok=true os/cont/manual/capture_ok=true` | `flip_after ∈ {-1,1,2,3,4,5,6,7}` (the scout's "3–7" is really **[1,7]**), `os fin_delta=-1 n=0`, `capture_rect=(0,0,0,0)` in every receipt |

**Byte-stable cells:** for the 12 single-valued cells (`census`, `ppm`, `convert`,
`cpu_never`, `cpu_contam`, `cpu_oneshot_off`, `cpu_oneshot_flag`, `cpu_retrigger`,
`cpu_lt_mid`, `cpu_speed_mid`, `cpu_amount_mid`, `cpu_request`) every landed-fixture
receipt (author battery + scribe fresh + ff30/ff60) carries **one distinct full line**;
the landed default receipts are byte-identical to the scout's canonical `rep1` lines,
and all 19 landed gating prefixes match the scout's `rep1` prefixes exactly.

### 3.4 The fold is verified on the landed bytes (new evidence)

The boundary's attack 4 verdict was "`cpu_pause` must not be shipped as-is" — measured on
the **frozen probe**. No seat had re-measured the **folded** fixture under
`--fixed-fps 30`. This seat did (3 reps):

```
fresh-ff30/particles_lattice.cpu_pause.ff30.rep{1,2,3}.out
  PASS particles_lattice cpu_pause ok=true vis_ok=true vis_parent_ok=true pm_disabled_ok=true ts0_ok=true
    | vis[fin_after_show=4 n=1] vis_parent[fin_after_show=2 n=1] pm_disabled[fin_after_enable=2 n=1] ts0[fin_after_restore=18 n=1]
fresh-ff60/…  ok=true, vis_parent=4 pm_disabled=4 ts0=19
fresh/…       ok=true, vis_parent∈{4,5} pm_disabled∈{4,5} ts0∈{19,20}
```

So the landed `[1,7]` fold closes the only `ROWS_PREFIX` rejection of the 6-condition
matrix, on the committed bytes. The landed ladder/request rows also pass at ff30/ff60
(12/28/58 and 7/14/29/59 fall inside the authored windows; `fin_call1=6/11` unchanged).

---

## 4. The floor gate — `r94_expected_errors_all_matched`

* Present once, prefix-scoped, **`true` in both committed-byte runs** and in the
  author's two runs; `rows_with_expected_errors=68` (unchanged by the landing) and
  `dead_entry_count=0` in run 2.
* **Vacuously true today** (no r94 allowlist entries) — but **loud**: the extracted gate
  expression (`floor_gate.py`) evaluated over synthetic census rows gives
  `live entry → True`, `dead entry → False`, `mixed → False`, and a dead **non-r94**
  entry leaves it `True` (prefix scope). Re-evaluated on run 1's real census rows
  (2 dead entries from the volatile `negative_transition`), the gate is still `True` —
  the dead entries are out of prefix scope.
* Pre-existing scope note: the census covers executed rows only; a renamed/orphan `r94_`
  key would produce no census row and stay invisible (same shape as r87–r93).

---

## 5. Dossier claim recompute

### 5.1 Scout (`reports/round-94/r94-scout.md`, committed `2c4b1ff`)

| claim | recomputed |
|---|---|
| 105 canonical + 38 loadtest runs, all rc=0, 0 B stderr | ✓ exact; `err_uniq=1` per cell |
| 12 cells `uniq=1`; 7 cells keep a byte-stable boolean prefix | ✓ AST/canonical counts reproduce (`cpu_expl` 2, `cpu_lifetime` 5, `cpu_pause` 4, `cpu_restart` 2, `cpu_speed_pre` 2, `cpu_stop` 2, `gpu_headless` 4; the other 12 = 1) |
| `ROWS_PREFIX` 19 rows × 143 receipts, `rejected=[]` | ✓ re-run of their own verifier: `rejected=[]`, `ROWS` 30 rejections, segment sha `749fa0607e7707e6` |
| "143/143" as evidence for the frozen probe | **✗ provenance defect (A1)** — 135/143 receipts predate the probe freeze (16:51:26); only `cpu_request` (6+2) postdates it; `RECEIPTS.md` cites `09dd77238668b315…` while `manifest.sha256`/report §11 cite `e6a2e0f5…b930` |
| `flip_after` "3–7" | **✗ range** — measured `{-1,1,2,3,4,5,6,7}`; the landed row correctly does not pin it (A10) |
| "process-global contamination" law | ✗ as framed (boundary §8 reframing, `add_pf` rule); the landed fixture carries the corrected wording and the same pinned booleans |

### 5.2 Boundary (`reports/round-94/r94-boundary.md`, committed `e741cf80`)

* 734 launches = 683 matrix + 51 reprobe ✓ (recount: 138+114+111+111+111+62+36 = 683,
  +51); **0 non-zero rc** (a `timeout -s KILL` would show as rc=137 — none present),
  **0 B stderr**, complete `.out`/`.rc`/`.err` triples (734 each) ✓.
* 323-check matrix on the frozen revision → **exactly 3 rejections, all
  `r94_particles_cpu_pause` at ff30** ✓ reproduced independently (§3 census matrix).
* `ab` interleaved table (`f30` l025=12, l05=28, l1=58 in 3/3 pairs) ✓ re-read from
  `runs/ab/ab*_f30_cpu_lifetime.rep1.out`.
* `req_var` floor table (0.20→3, 0.30→2) ✓ re-read from `runs/quiet/r94b_req_var.rep1.out`.
* GPU `flip_after [1,7]` ✓; `capture_rect` zero ✓; `fixed_fps=1` stall (4 s, n_fin=0) —
  accepted as reported (their receipts; not re-launched here).
* `[U]` continuous-amount (§7.3) — consistent with the receipts; the landing authors no
  row on it ✓.

### 5.3 Author (`reports/round-94/r94-author.md`, committed `c7228893`)

| claim | recomputed |
|---|---|
| fixture sha `0701e813…`, 763 lines; `+91/−0`; `project.godot` untouched | ✓ |
| code diff vs frozen probe = exactly 4 lines | ✓ (comment-stripped diff; 3 windows + `floor`) |
| two green runs 314/314 on final bytes | ✓ `runs/20261016T055703426158Z` and `…060430025246Z`, both PASS 314/314, r94 19/19, gate true, dead 0; **scratch fixture sha == landed fixture in both** |
| `expected_errors += 0`, `required_stderr += 0` | ✓ AST + run census (68 rows, 0 r94 keys) |
| 19 rows generated verbatim from `ROWS_PREFIX` | ✓ byte-identical, all 19 (incl. the 8785-char census) |
| smoke: prefixes byte-exact vs scout `rep1` | ✓ full-line identity for the 12 stable cells; prefix identity for all 19 |
| dispatch-card disclosure (RemoteTransform2D wording has no referent) | ✓ the card text is stale for this lane; nothing was invented to satisfy it (A9) |

### 5.4 Frozen-`probeParent` labrat (one dispatch, agent `bd3f872e`)

Clause 1 (landed signatures vs scout `ROWS_PREFIX`) → **PASS**: 18 short signatures
byte-identical on direct read; the census signature verified by identical head/tail
anchors and length parity (its no-`diff` tool limitation is recorded — this seat's own
byte-identity check over the same strings closed it: 8785-char signature in both).
Clause 2 (fold shape) → **PASS (a)+(b)**: the only differing `_okb` call literals are the
three cpu_pause windows (`4,7 → 1,7`), and exactly one `round(0.5/spec)` →
`floor(0.5/spec)` line; (c) "everything else is comment/blank" was partial without a
diff tool — closed by this seat's comment-stripped diff (exactly 4 code lines).
Clause 3 (gate + allowlists) → **PASS**: gate appears once, prefix-scoped; no `r94_` key
in either allowlist dict; `required_stderr` has exactly the 3 known keys. The labrat
wrote nothing.

---

## 6. Landed-row mutant test + classifier properties

Production `classify_process` extracted verbatim from `HEAD` (segment sha
`749fa0607e7707e6…`, same segment r89–r93 pinned), applied to a real landed-fixture
receipt per row:

```
signature mutants: 579/579 rejected   (412 numeric + 110 boolean + 57 appended conjuncts)
pinned-region output mutants: 522/522 rejected   (110 boolean flips + 412 numeric flips)
baseline (unmutated) verdict: PASS for all 19 rows
```

The output mutants are applied **inside the located pinned region** (exact offsets), so
each one genuinely changes a pinned token — the pins are not decorative.

**Pre-existing classifier properties** (`classifier_properties.py`, recorded so a future
reader does not over-read "signature pinned"): a trailing token appended after the pin on
the same line is accepted 19/19 (substring anchor); the PASS line delivered on **stderr**
is accepted 19/19 (production classifies the merged stdout+stderr blob — only
`required_stderr` rows are stream-anchored, the r89-fold critic F1). Control (signature
destroyed) rejects 19/19. Neither shape is reachable from the fixture's own behaviour
(A6).

---

## 7. Arithmetic cross-check ledger (all reconcile)

| identity | result |
|---|---|
| landing: 3 files, 1055 insertions, 0 deletions; run_battery `+91/−0` in 2 blocks | ✓ |
| CASES 288 → 307; rows 295 → 314 (7 meta); r94 contiguous at 284–302; tail 303–306 intact | ✓ |
| allowlists: 72 expected_errors keys (69 non-empty), 0 r94; 3 required_stderr keys, 0 r94; run census 68 rows | ✓ |
| fixture vs probe: 4 changed code lines; 763 = 741 + 22 comment/blank lines | ✓ |
| manifests: scout 598 = 599 − self; boundary 2953 = 2954 − self; 0 missing/unlisted/hash-mismatch | ✓ |
| census: 1028 receipts collected; 653 own-arm checks = 650 hits + 3 misses; 0 collisions | ✓ |
| boundary matrix: 57×5 + 38 = 323 checks; 3 rejections (cpu_pause ff30) | ✓ |
| landed-fixture census: 151 checks, 0 rejections (57 fresh + 18 fold-mode + 38 author + 38 scribe-battery) | ✓ |
| mutants: 579 sig + 522 output, all rejected | ✓ |
| scout receipts: 105 = 9 + 96; 38 = 19 × 2; 135 predate freeze + 8 post | ✓ |
| author runs: 314 × 2; r94 19 × 2; scratch sha == landed in both | ✓ |
| cross-run: 277 identical + 4 r94 tail-only + 28 head-diff + 5 flips = 314 | ✓ |

---

## 8. Adjudication items (ranked)

| id | dossier | item | severity | disposition |
|---|---|---|---|---|
| **A1** | scout evidence | The scout's "143/143" receipt set mixes **two probe revisions**: 135/143 receipts predate the frozen probe (mtime 16:51:26); `RECEIPTS.md` line 13 cites `09dd77238668b315…` while `manifest.sha256`/report §11 cite `e6a2e0f5…b930` for the same file. The claim is reproducible *on those receipts* but is not evidence for the frozen artifact; the pre-freeze revision is unrecoverable (runs/ gitignored, single commit). The landing's evidence does not rest on it (boundary matrix + landed-fixture receipts + this seat's fresh runs). | **medium-low** (provenance; no verdict change) | reword `RECEIPTS.md` to name the two revisions, or regenerate the 135 receipts on the frozen probe in a future pass |
| **A2** | landing precision | The mandatory `cpu_pause` fold widens `[4,7] → [1,7]`: a 1–3-tick resume would now pass at 60 tps (measured 4–5; 2 at ff30). The lower bound 1 is the physical floor (the signal cannot precede the resume frame), so this is precision loss, not a hole; the fold is declared in the fixture header, the harness comment and the author report. | **low** (declared tradeoff) | keep; if a future round wants the 60-tps precision back, add an ff30-tolerant sibling row or per-condition windows |
| **A3** | landing precision | The `cpu_request` `round → floor` fold is **byte-inert** on the two authored steps (0.10/0.05); the boundary's falsifying steps (0.20/0.30) are deliberately not authored, so the closed form has no witness in the battery. | **low** (scope note) | keep; a `step020`/`step030` cell would make the closed form falsifiable in-row |
| **A4** | custody | The author's two green runs (`corpus/live/runs/20261016T055703426158Z`, `…060430025246Z`) are **worktree-only**: `git ls-files corpus/live/runs` = 0 (gitignored `runs*/`). Same for the scout/boundary `runs/` trees (25/599 and 12/2954 lane files tracked). Manifest-covered where a manifest exists; not carried by the commit. | **low** (convention, same as r87–r93) | record; force-add the two `verdicts.json` at wave fold if the operator wants the evidence in-tree |
| **A5** | landing gate | `r94_expected_errors_all_matched` is **vacuously true today** (zero r94 allowlist entries) and inherits the executed-rows-only census scope. Loudness is demonstrated by the extracted expression (dead entry → `False`, live → `True`, non-r94 dead → `True`). | **info** (intended carried-floor semantics) | keep |
| **A6** | classifier | Pre-existing battery-wide properties: trailing-token-after-pin accepted 19/19; PASS-on-stderr accepted 19/19 (merged-blob classification). Only `required_stderr` rows are stream-anchored. | **info** (not reachable from the fixture's own behaviour) | record; do not read "signature pinned" as stream/line anchoring |
| **A7** | host class | In run 1 the volatile `negative_transition` failure (scene-timing class under ~10 concurrent batteries) removed its two allowlisted `ERROR:` lines → 2 dead entries → the meta row failed **closed**. Run 2 (same bytes) is clean. No r94 row flaked in either run. | **info** (fail-closed, pre-existing class) | record; the meta row is the loud canary, as intended |
| **A8** | landing scope | The `_okb` tick windows are **60-tps-only** (boundary §3: the ladder is `round(L·tps)`). The launch `project.godot` pins no `physics_ticks_per_second` and no battery cell changes it; `--fixed-fps 30/60` values fall inside the windows (12/28/58, 7/14/29/59). The real exposure is a future tps override. | **info** (disclosed by the author; documented in the fixture header) | keep |
| **A9** | dispatch card | The author card named RemoteTransform2D claims that have no referent in this lane; the author disclosed it and authored the particles surface instead — nothing was invented to satisfy stale card wording. | **info** | record for card hygiene |
| **A10** | scout report | `flip_after` "3–7" is wrong (measured `[1,7]` + `-1`); the landed row does not pin it and the fixture comment carries the corrected range. | **info** (no pin impact) | already folded into the fixture comment |

---

## 9. Remaining risks / blockers

1. **No blockers to the landing.** Both committed-byte runs are green on the r94
   surface (19/19 each, gate `true`, run 2 full PASS), the two manifests verify
   completely, the fold is verified on the landed bytes, and every recomputable dossier
   claim reproduces (the label/provenance defects A1/A10 aside).
2. **Host-conditional pins by design** (census enums/defaults/method counts, 4-dp
   floats, 60-tps tick windows) flip loudly on an engine or `project.godot` bump —
   intended, same class as prior rounds.
3. **60-tps scoping (A8)** is the one exposure a future battery cell could trip: any
   `physics_ticks_per_second` override rejects `cpu_lifetime`/`cpu_expl`/`cpu_speed_pre`
   and re-scales `cpu_pause`'s windows. Nothing committed sets it.
4. **Worktree-only custody (A4)** for the author's two green runs and the
   scout/boundary run trees.
5. **Gate inert today (A5)** — correct carried-floor semantics, not a false green.
6. **Pre-existing volatile battery rows (A7)** reproduce under heavy host concurrency
   (run 1: `overlap`/`transition`/`negative_transition`/`audio_playback`); none touches
   an r94 row, and the meta canary fails closed.
7. **A1 provenance defect**: do not cite the scout's "143/143" as frozen-revision
   evidence in the round-94 verdict; cite the boundary's 323-check matrix and this
   seat's landed-fixture census (151 checks, 0 rejections) instead.

---

## 10. Host notes / cleanup

- I added no load beyond my two batteries and 75 single-arm launches; no `yes` hogs were
  started by this seat. No orphaned godot/python processes remain from this lane
  (`pgrep` clean of `r94-scribe`; the foreign batteries and `yes` hogs belong to sibling
  lanes and were left untouched). Host loadavg 74–95 on 32 cores throughout.
- `/tmp` was left alone; the committed-tree extract lives at
  `/home/vgpnk/r94-committed-extract` (retained this session) and the fresh-arm scratch
  project at `/home/vgpnk/r94-scribe-fresh-proj` (outside the repo).
- Zero tracked files written by this seat; `git status --porcelain -uno` was empty at
  audit start and through both battery runs and all fresh launches. **Late-window
  note:** at 03:41:30 a concurrent r95-author lane inserted its own block into the
  worktree `run_battery.py` (+163 lines / 52 rows, CASES 307 → 359); it is foreign, left
  untouched per "preserve unrelated work", and the r94 tuples + floor gate comprehension
  are byte-identical between `HEAD` and that dirty worktree
  (`audit/static_audit.json → foreign_worktree_modification`). The concurrent sibling
  lanes' work (r94 reviewer/verifier/simplifier/critic, r95 author, g3d r97 seats) is
  otherwise untouched.

---

## 11. Evidence index

All under `corpus/live/r94-scribe/`; `manifest.sha256` covers every artefact in that
directory except itself.

| artefact | path | notes |
|---|---|---|
| battery run 1 (worktree, committed bytes) | `battery-runs/20261016T063407989183Z/verdicts.json` + `battery-rep1.log` | 314 rows, 309/314, r94 19/19, gate true, dead 2 |
| battery run 2 (`git archive HEAD` extract) | `battery-committed/20261016T064405071549Z/verdicts.json` + `battery-rep2.log` | 314 rows, 314/314, r94 19/19, gate true, dead 0 |
| fresh single-arm receipts | `fresh/particles_lattice.<arm>.default.rep<N>.{out,err,rc}` (57) | rc=0, 0 B stderr |
| fresh fold-mode receipts | `fresh-ff30/…` (9), `fresh-ff60/…` (9) | ff30 `cpu_pause ok=true` (the fold) |
| static custody audit | `audit/static_audit.py` → `static_audit.json` | identity, diff, CASES, allowlists, gate, manifests, provenance, author runs |
| receipts census | `audit/receipts_census.py` → `receipts_census.json` | 1028 receipts; 650/653; boundary matrix 323/3; landed 151/0 |
| law re-derivation | `audit/laws_recompute.py` → `laws.json` | ladder/expl/request/pause/contam/gpu |
| mutant + dossier recompute | `audit/recompute.py` → `recompute.json` | 579/579 + 522/522; scout 105+38 |
| floor-gate loudness | `audit/floor_gate.py` → `floor_gate.json` | extracted gate expression, synthetic + real census |
| classifier properties | `audit/classifier_properties.py` → `classifier_properties.json` | trailing/stderr/control |
| cross-run comparison | `audit/compare_runs.py` → `compare_runs.json` | 277/4/28/5 |
| scout verifier re-run | `audit/scout_verify_rows.txt` | `rejected=[]`; `ROWS` 30 |
| lane index / replay | `RECEIPTS.md` | commands + headline numbers |
| source reports | `reports/round-94/r94-{scout,boundary,author}.md` | tracked, sha-verified |
