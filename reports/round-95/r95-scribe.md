# game-dev-2d round 95 — scribe (r95-scribe): wave-B evidence custody + claim audit on committed `9cd47507`

Seat `SCRIBE` (LEAF) | lane `g2d-r95-scribe` | round 95 | host **devin** (32 cores,
loadavg 75–98 with 48 foreign `yes` hogs and ~10–16 concurrent Godot processes from
sibling lanes for the whole session).
Read-only audit of the r95 `PhysicsDirectSpaceState2D` query-lattice + order-cycle
landing: **no tracked file written, no commit, no runtime config mutated**. The only
writes are this report (new, untracked) and `corpus/live/r95-scribe/**`. Every number
below was recomputed from `git show <audited-commit>:` bytes (`9cd47507`), from receipts
on disk, or from fresh launches on the committed bytes; nothing is quoted from the
audited reports without re-derivation.

Audit-time repository state: HEAD **`9cd47507`** (*r95 author: 52 dss/order rows (366
total) — k(k-1) cycle ladder, perm0-7 creation perms, co-presence attribution folded;
366/366 x2*), parent `6f817d10` (r94 verifier). `git status --porcelain -uno` was
**empty** at audit start and at every check through both battery runs, the 160 fresh
launches and all recomputations; the landed fixtures, `run_battery.py` and
`project.godot` are byte-identical to the audited commit, and the three r95 dossier
reports are tracked and equal to it.

**Late-window note.** During the audit's recomputations a concurrent lane committed
**`35001d1d`** (*r94 simplifier PASS -3 + adjudicated ADMIT-with-findings*) and HEAD
advanced. That commit touches only `LOG.md`, `SCORECARD.md`,
`corpus/live/r94-simplifier/**` and `reports/round-94/r94-{simplifier,adjudicator}.md`
— **every r95 artefact is byte-identical between the audited `9cd47507` and the current
HEAD** (both fixtures, `run_battery.py`, `project.godot` and all three r95 dossier
reports; blob-by-blob verified, `audit/static_audit.json → late_window`). All execution
below used the audited bytes; the static audit now pins `9cd47507` explicitly rather
than a moving `HEAD`.

**Second late-window note (foreign worktree edit, 07:26:40Z — after every launch in
this audit).** A concurrent **r96-author** lane then inserted its r96 block into the
*worktree* `run_battery.py` (`+223/−0`: 13 `r96_*` CASES tuples, an
`r96_expected_errors_all_matched` gate and comments; CASES 359 → 419). It is
**foreign, untouched by this seat**, and the r95 content is provably unaffected: all 52
r95 CASES tuples are element-wise identical between `HEAD` and the dirty worktree, the
r95 gate expression is present, and the r95 rows still occupy indices 303–354 (the
r96 block sits at 355–367, ahead of the crash/descendant tail). Both of this seat's
battery runs used committed bytes (run 1 launched at 07:08 on the then-clean worktree,
run 2 from the `git archive HEAD` extract), so no measured number below depends on the
dirty file.

**Custody verdict: HOLDS — all 52 landed rows are encoded, load-bearing and verified
on the committed bytes.** The landing is insertion-only (+1907/−0), both fixtures are
byte-copies of the frozen probes (`77ae4adb…` / `4f7e945e…`), both lane manifests
verify completely (565/566 and 1062/1063, 0 missing / 0 mismatch / 0 unlisted), the 17
`dss_lattice_*` rows are the scout's `ROWS_PREFIX` element-wise and the 35
`r95b_order_*` rows are whole canonical PASS lines of their own boundary cell
(308 receipts checked, 52/52 own-cell bound), **two fresh battery runs on the committed
bytes** are green on the r95 surface (52/52 in both; gate `true` in both; 361/366 and
364/366 overall, all failures the documented pre-existing volatile class), 160 fresh
single-arm launches (default/`--fixed-fps` 30/120/threaded) are 160/160 rc=0 with 0 B
stderr and signature present, 472 row-receipt checks hit 472/472 with 0 `ERROR:` lines,
and the production classifier rejects 3288/3288 signature mutants and 1492/1492
pinned-region output mutants. Findings F1–F8 are recorded; none falsifies a landed pin,
allowlist entry, gate key or verdict.

---

## 0. What was run (method)

| # | check | command shape |
|---|---|---|
| 1 | landing identity (worktree vs `HEAD:` blobs) | `audit/static_audit.py` |
| 2 | commit shape + insertion-only proof vs `HEAD~1` | `git show --numstat`, `difflib.SequenceMatcher` |
| 3 | CASES / row arithmetic, contiguity, allowlists, gate | AST over `HEAD:corpus/fixtures/run_battery.py` |
| 4 | fixture vs frozen probe byte identity | sha256 both directions (fixtures, lane `proj/` copies) |
| 5 | lane manifest verification + completeness + tracking | sha256 + `os.walk` + `git ls-files` |
| 6 | scout `ROWS` / `ROWS_PREFIX` element-wise binding | AST equality over `corpus/live/r95-scout/author-rows.py.txt` |
| 7 | own-cell binding (each row's signature in *its own* cell receipts) | receipt globs, 35 r95b (308 receipts) + 17 dss (150 receipts) |
| 8 | **fresh battery run 1** (worktree = committed bytes, under load) | `python3 corpus/fixtures/run_battery.py --runs corpus/live/r95-scribe/battery-runs` (stamp `20261016T070820061770Z`) |
| 9 | **fresh battery run 2** (`git archive HEAD` extract) | same harness from `/home/vgpnk/r95-committed-extract` → `battery-committed/` (stamp `20261016T071623277563Z`) |
| 10 | fresh single-arm receipts on the landed fixtures | `audit/fresh_arms.py`: 52 arms × 2 default + 35 ff30 + 5 ff120 + 16 threaded = **160** launches |
| 11 | receipts census (binding, collisions, `ERROR:` lines) | `audit/receipts_census.py` over 5 source classes / 892 receipts |
| 12 | law re-derivation from raw receipts | `audit/laws_recompute.py` → `laws.json` |
| 13 | landed-row mutant test (signature + pinned-region output) | `audit/recompute.py`, production `classify_process` (segment sha `749fa0607e7707e6…`) |
| 14 | floor-gate loudness + classifier properties | `audit/floor_gate.py` |
| 15 | cross-run comparison | `audit/compare_runs.py` |
| 16 | scout verifier re-run (read-only) | `corpus/live/r95-scout/verify_rows.py` → `audit/scout_verify_rows.txt` |

No `lsp` device and no GDScript language server on this host (unchanged state, same as
r89–r94); no symbol edits were performed — the only "edit" surface was new receipts.
All launches were bounded (`timeout -s KILL 12` for single arms; the battery's own
per-case bounds); no orphaned processes were left.

**Frozen-`probeParent` disclosure.** Exactly **one** read-only `ufo-labrat` was
dispatched (agent `9442934a`, four bounded static clauses: gate scope/fail-closed
semantics; allowlist r95-key absence; the four head-prefix cuts; declared-hash textual
consistency). Its result is in §5.4; its one caveat (fixture headers declare no sha256)
is recorded as F4 and was closed by this seat's own direct hashing. It wrote nothing.

---

## 1. Committed-tree identity + the landing's shape

Worktree bytes == committed bytes for every landing file at audit time, so "committed
tree only" holds for all execution below:

| file | sha256 (`HEAD` blob; worktree identical) | size |
|---|---|---|
| `corpus/fixtures/dss_lattice.gd` (new) | `77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627` | 743 lines |
| `corpus/fixtures/r95b_order.gd` (new) | `4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490` | 777 lines |
| `corpus/fixtures/run_battery.py` (`+163/−0`) | `b93cbdaa3d5c6ae35d69970a545442d86898a959f0e2e2995f1adf58a3444ed7` | 4590 lines |
| `corpus/fixtures/project.godot` (untouched) | `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` | 3 lines |
| `reports/round-95/r95-author.md` (new) | tracked | 224 lines |

The commit `9cd47507` is **4 files, 1907 insertions, 0 deletions** (`743/0`, `777/0`,
`163/0`, `224/0`). `run_battery.py` vs `HEAD~1` is insertion-only: two blocks, **152
lines at old line 877** (the r95 comment header + CASES tuples, HEAD lines 878–1029)
and **11 lines at old line 3113** (the floor gate, HEAD lines 3266–3276), `deleted = 0`.
`project.godot` is byte-identical to `HEAD~1`.

**CASES / row arithmetic (AST):** CASES **307 → 359** tuples; results rows **314 → 366**
(7 meta). The 52 r95 rows are **contiguous at indices 303–354** — immediately after
`r94_particles_gpu_headless` (302) and **ahead** of the crash/descendant tail
(`crash_spontaneous_sigabrt` 355, `crash_self_sigkill` 356,
`descendant_pipe_detached_control` 357, `descendant_pipe_forged_signature_release` 358)
— the tail is untouched and the sleep-8 adjacency requirement is preserved.

**Fixture identity:** both landed fixtures are **byte-copies of the frozen probes** —
`dss_lattice.gd` ≡ `corpus/live/r95-scout/probes/dss_lattice.gd` and
`r95b_order.gd` ≡ `corpus/live/r95-boundary/probes/r95b_order.gd` (sha256 equality in
both directions, and the lanes' own `proj/` launch copies hash identically too, as do
both lanes' `proj/project.godot` vs the committed `corpus/fixtures/project.godot`).

**Allowlists:** the `expected_errors` mapping carries **72 keys** (69 non-empty; 3 map
to empty tuples), `required_stderr` carries exactly **3 keys**
(`geo2d_lattice_lineempty`, `nav_lattice_teardown_crash`, `r92_tilemap_nullts_crash`),
and **neither carries an `r95_` key** — the r95 block is `ERROR:`-clean by measurement,
confirmed on every r95 receipt of every source (§3, §5).

**Floor gate:** `r95_expected_errors_all_matched` present exactly once
(`run_battery.py:3272`), comprehension scoped by
`r["case"].startswith(("dss_lattice_", "r95b_order_"))`; the named-by-round family now
spans `phys2d_` + r87–r95.

**Scout rows:** all 17 committed `dss_lattice_*` tuples equal the scout's
`ROWS_PREFIX` entries **element-wise** (17/17, fields included); 13 of them also equal
the scout's full-line `ROWS` entries and the 4 order-vector cells
(`point_cap`, `point_cap_rev`, `order_core`, `order_core_rev`) are strict prefixes of
their `ROWS` lines, cut before the first vector token (`cap1=[`, `rep1=[`).

**Refuted-token scan:** no landed signature contains `layout_changes_order`,
`shape_same_order`, `repeat_stable`, `pile_b=`, `pile_rev=`, `after_free=`,
`free_perturbs` or `insert_perturbs` (all such mentions in the r95 block are comments
recording the exclusions). The only "conditional-token" hits are `scoutrev`'s positive
counter-pins (`scout_row_rev_t2_vec=…`, `t2_vec_matches_scout_row=true`,
`t2_relpos_equals_canon=true`) — exactly the boundary's re-pin of the label-permutation
falsification.

---

## 2. Two fresh battery runs on the committed bytes

**Run 1 — worktree at `9cd47507`** (tracked tree clean at launch; host loadavg ≈ 88–98,
48 foreign `yes` hogs, ~10 sibling Godot processes):

```
rep1 — stamp 20261016T070820061770Z  (battery-runs/, log battery-rep1.log)
  rows=366  verdict=FAIL (361/366)   r95 52/52 PASS
  r95_expected_errors_all_matched=true   dead_entry_count=2   rows_with_expected_errors=68
  fails: overlap, transition, negative_transition, audio_bus_route
         + meta knock-on probe_error_clause_surface (census_bare_classifier_consistent=false)
```

**Run 2 — executed from a `git archive HEAD` extract**
(`/home/vgpnk/r95-committed-extract`; fixture hashes verified before launch, independent
of the worktree):

```
rep2 — stamp 20261016T071623277563Z  (battery-committed/, log battery-rep2.log)
  rows=366  verdict=FAIL (364/366)   r95 52/52 PASS
  r95_expected_errors_all_matched=true   dead_entry_count=2   rows_with_expected_errors=68
  fails: negative_transition + meta knock-on probe_error_clause_surface
```

**Cross-run comparison** (`audit/compare_runs.py`, 366 rows): **307 identical**,
**59 differing** — of which **24 are r95 rows and every one of the 24 differs only in
the unpinned `proc=<N>` process-frame counter** of the fixture's `R95B <arm> env=…`
line (the 17 `dss_lattice_*` outputs are byte-identical) — and **3 verdict flips**
(`overlap`, `transition`, `audio_bus_route`, all FAIL→PASS), all pre-existing volatile
classes, **none r95**. **No r95 row flipped verdict in either direction.**

The failures are the documented host class, each with its own receipt text:
`overlap` ("signal occurred before physics overlap observation"), `transition`
("initial current_scene identity/marker mismatch"), `negative_transition` ("probe
exceeded 120 frames" → its two allowlisted `ERROR:` lines never appear → **2 dead
entries** → the meta row fails **closed**, as designed), `audio_bus_route`
(`advanced=false`, audio wall-clock row). The meta row's failing discrimination is
`census_bare_classifier_consistent` — a downstream consistency discrimination that the
volatile rows break, not an independent failure.

All six 366-row runs on this landing (author ×4 + this seat ×2) agree on the r95
surface:

| run | rows PASS | r95 PASS | gate | dead |
|---|---|---|---|---|
| author `…064148780406Z` | 365/366 | 52/52 | true | 0 |
| author `…064742446822Z` | **366/366** | 52/52 | true | 0 |
| author `…065335715243Z` | 363/366 | 52/52 | true | 3 |
| author `…065922894811Z` | **366/366** | 52/52 | true | 0 |
| scribe `…070820061770Z` (worktree) | 361/366 | 52/52 | true | 2 |
| scribe `…071623277563Z` (extract) | 364/366 | 52/52 | true | 2 |

---

## 3. The declared laws — re-derived from raw receipts

`audit/laws_recompute.py` collected every r95 PASS line from 5 source classes
(boundary 261, scout canonical 99 + loadtest 51 + alt 9, author 4×52, scribe battery
2×52, scribe fresh 160) and re-derived the laws from the raw strings:

| law | pinned token(s) | measured across receipts |
|---|---|---|
| cycle closure (canon) | `distinct_ticks=20 cycle_len_dense=20`, `t0:0,1,2,3,4`, `t20` = `t0`, `t2_vec` | 31 receipts (boundary + scribe battery + scribe fresh), **1 distinct ladder**; `t0 == t20` in all; single `t2_vec=[e#0,a#0,c#0,d#0,b#0]` |
| cycle length **k(k−1)** | `cycle_len=… expected_kk1=…` | 13 `periodx` receipts, k ∈ {2,3,4,5,6,7,8,10}: **`cycle_len == k(k−1)` in every receipt** (2, 6, 12, 20, 30, 42, 56, 90); `periodx_k5s8` (spacing 8) also 20 |
| creation-order dependence | `perm=0..7` ladders + `t2_vec` | **8/8 distinct ladders and 8/8 distinct t2 vectors**; 3–14 receipts per permutation, 1 payload each |
| translation invariance | `celloff off=… ladder=[…]` | **14 cells (x ∈ {0, ±0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, ±1000}, y = +1000) → 1 distinct ladder**; the `y1000` receipt's ladder equals `x0`'s |
| co-presence | `twopiles a_t2_vec / a_t4_with_b_vec / b_t2_vec` | 9 receipts, 1 distinct line: A-alone t2 = canon; A at t4 **with B** ≠ A alone; B at t2 = the scout's old `pile_b` row |
| free order | `free freed=[…] ladder=[…]` | `ab` vs `ba` differ at every sampled tick; each variant byte-stable (1 payload per variant across sources) |
| above-cap set | `set32_distinct`, `n32/n64/n0`, `set32_t2` | 15 receipts: `set32_distinct=5` in all, `n32=32 n64=40 n0=0`, **3 distinct t2 subsets** (p0/p1/p2) |
| layer-conditional order | `pt_eq_sh`, `sh_len` | `k=0`: `pt_eq_sh=true sh_len=5`; `k=1`: `pt_eq_sh=false sh_len=6` (single values across all receipts) |
| allocation history | `warm k=… keep=…` | `warm_k{0,1,2,3,5,8,13,32}` (freed) ladders **equal canon on all common ticks**; `keep8`/`keep64` differ (1 payload each) |
| rigid determinism | `t10_relpos` | 5 receipts, single `[15.9999,14.8732]`, `distinct_ticks=1` |
| label permutation | `scoutrev` | 4 receipts: `t2_vec_matches_scout_row=true`, `t2_relpos_equals_canon=true` |
| the two instabilities | `procwait`, `env` | `procwait` 16 receipts / **8 distinct payloads**; `env` 4 receipts / 2 payloads (frame counters) — neither authored |

**Cross-source stability:** 94 distinct arm keys; **only 2 keys carry >1 payload across
all 5 source classes** — `ray_order` (rev / non-rev) and `shape_lattice` (rev /
non-rev) — i.e. the only per-key variation is the two declared `--rev` sub-arms, not
instability. Canon's instance-id line is byte-identical across all boundary batches;
`warm` ids vary by cell while ladders hold (the boundary's documented id-vs-order
independence).

---

## 4. The floor gate — `r95_expected_errors_all_matched`

* Present once, prefix-scoped, **`true` in all six 366-row runs** (author ×4, scribe
  ×2); `rows_with_expected_errors=68` (unchanged by the landing) and
  `dead_entry_count=0` in the two author-green runs.
* **Vacuously true today** (zero r95 allowlist entries; zero r95 rows in the census) —
  but **loud**: the extracted gate expression (`audit/floor_gate.py`, segment sha
  `486414297a7cb3af…`) evaluated over synthetic census rows gives `live r95 entry →
  True`, `dead r95 entry → False`, `mixed → False`, `dead non-r95 entry → True`
  (prefix scope), `no entries → True`, `empty census → True`. Re-evaluated on a real
  run's census rows (68 rows, 0 dead, 0 r95) the gate is `True`.
* Pre-existing scope note: the census covers executed rows only; a renamed/orphan `r95_`
  key would produce no census row and stay invisible (same shape as r87–r94).

**Classifier properties** (`audit/floor_gate.py`, 52 rows): a trailing token appended
*after* the pin on the same line is accepted 52/52 (substring anchor); a PASS line
delivered on **stderr** is accepted 52/52 (production classifies the merged
stdout+stderr blob — only `required_stderr` rows are stream-anchored, the r89-fold
critic F1); control (signature destroyed) rejects 52/52. Neither accepted shape is
reachable from the fixtures' own behaviour.

---

## 5. Dossier claim recompute

### 5.1 Scout (`reports/round-95/r95-scout.md`, committed)

| claim | recomputed |
|---|---|
| 99 canonical runs (1 census ×3 + 16 ×6), 17/17 cells `out_uniq=1 err_uniq=1 rc=[0]`, 0 B stderr | ✓ exact: 99 receipts, 17 cells, all uniq=1, 0 B stderr in every `.err` |
| 51 loadtest runs at loadavg 95–109, 0 rejections | ✓ 51 receipts, 17 cells, all rc=0, 0 B stderr, `out_uniq=1` |
| `ROWS` 150/150, `ROWS_PREFIX` 150/150, `rejected=[]` | ✓ re-run of their own verifier: both 150/150, `rejected=[]`, classifier segment `749fa0607e7707e6` |
| 9 alt-construction runs | ✓ 9 receipts present |
| the 17 rows are ready to land | ✓ 17/17 element-wise `ROWS_PREFIX`; 17/17 bound to their own cell receipts (150 receipts checked) |

*Note (not a defect):* unlike r94, the scout's **full-line** `ROWS` also passes 150/150
here; the author still shipped the `ROWS_PREFIX` form for the 4 vector cells, which is
the strictly safer choice given the boundary's phase finding.

### 5.2 Boundary (`reports/round-95/r95-boundary.md`, committed)

| claim | recomputed |
|---|---|
| 261 runs, 8 batches, 0 non-zero rc, 0 B stderr, 0 × rc=137 | ✓ recount 132+53+8+16+16+13+8+15 = 261; 0 non-zero rc, 0 stderr bytes, no rc=137 |
| 58 cells in the quiet batch; 69 distinct cell ids across the 8 batches | ✓ 58 quiet cells, 69 distinct ids |
| every cell except `procwait` byte-stable within its batch / identical across batches | ✓ per-cell PASS-line uniqueness: only `procwait` (8 payloads) and `env` (2) vary |
| k(k−1) cycle table for k = 2…10, two layouts | ✓ all 13 `periodx` receipts satisfy `cycle_len == k(k−1)`; `k5s8` = 20 |
| `perm*` 8/8 distinct | ✓ 8/8 ladders + 8/8 t2 vectors |
| `celloff` 14/14 identical ladders | ✓ 14 cells → 1 distinct ladder; `y1000 == x0` |
| `twopiles` co-presence attribution | ✓ 1 distinct line, values as quoted |
| `free_ab` vs `free_ba` differ at every sampled tick | ✓ |
| `cap40` `set32_distinct=5`, 3 distinct t2 subsets, `n32/n64/n0` | ✓ 15 receipts |
| `layers_k0/k1` conditional order agreement | ✓ |
| `warm` freed cells identical, `keep8/64` differ | ✓ (canon-common-tick comparison) |
| `rigid` byte-identical `t10_relpos` | ✓ single value over 5 receipts |
| `procwait` 8 distinct payloads / 16 receipts; `env` 2 payloads | ✓ exact |
| instance ids byte-identical across batches | ✓ canon id line single-valued across all batches |
| (doc) `RECEIPTS.md` quiet batch "55 cells" | ✗ **58** — the report's §0 "58 cells" is right; the RECEIPTS.md table cell is stale (**F2**) |

### 5.3 Author (`reports/round-95/r95-author.md`, committed `9cd47507`)

| claim | recomputed |
|---|---|
| fixture sha256s `77ae4adb…` / `4f7e945e…`, 743/777 lines; `+163/−0`; `project.godot` untouched | ✓ |
| both probes byte-copies of the frozen sources | ✓ sha256 equality (and the lanes' `proj/` copies) |
| CASES 307 → 359, rows 314 → 366, r95 block inserted ahead of the crash tail | ✓ AST + index map |
| `expected_errors += 0`, `required_stderr += 0` | ✓ AST (72/3 keys, 0 r95) |
| floor gate added, `true` in all runs | ✓ line 3272; true in all six 366-row runs |
| 17 `dss_lattice_*` rows are `ROWS_PREFIX` verbatim | ✓ element-wise |
| 35 `r95b_order_*` rows are canonical whole PASS lines of the boundary receipts | ✓ 35/35 whole-line hits in their own cells (308 own-cell receipts checked) |
| per-cell `pass_uniq=1` for all authored r95b cells | ✓ (only `procwait`/`env` vary, neither authored) |
| four runs on the final bytes (2 green, 2 flake-class) with 52/52 each | ✓ `…064148` 365/366, `…064742` 366/366, `…065335` 363/366, `…065922` 366/366; r95 52/52 and gate `true` in all four |
| scratch fixture sha == landed fixture in each run | ✓ all four runs' `scratch/{dss_lattice,r95b_order}.gd` hash to the landed values |
| boundary-verdict exclusions honoured (`procwait`, `env`, `layout_changes_order`, thin order rows) | ✓ refuted-token scan over the 52 signatures is clean; exclusions appear only as comments |

### 5.4 Frozen-`probeParent` labrat (one dispatch, agent `9442934a`)

Clause 1 (gate scope + fail-closed) → **CONFIRMED** with source quoted
(`all(not e["dead_in_run"] for r in census_rows if r["case"].startswith((…)) …)`),
exactly one r95-named gate.
Clause 2 (allowlists) → **CONFIRMED**: 72 `expected_errors` keys and 3
`required_stderr` keys observed, zero r95-prefixed keys.
Clause 3 (prefix cuts) → **CONFIRMED**: the four vector rows are strict prefixes cut
before `cap1=[` / `rep1=[` and equal the `ROWS_PREFIX` entries; the other 13 compare
byte-equal to `ROWS` with no divergence.
Clause 4 (declared-hash consistency) → **CONFIRMED with caveat**: the two sha256
strings are textually identical wherever they appear (battery comment header, author
report) — but **the fixture headers declare no sha256 at all** (the clause's premise
was vacuous), so the identity claim rests on this seat's direct hashing (**F4**).
It wrote nothing; advisory only.

---

## 6. Landed-row mutant test + classifier properties

Production `classify_process` extracted verbatim from `HEAD` (segment sha
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`, 18 lines — the same
segment pinned by r89–r94), applied to a real landed-fixture receipt per row:

```
baseline (unmutated) verdict: PASS for all 52 rows
signature mutants: 3288/3288 rejected   (numeric + boolean + appended conjuncts)
pinned-region output mutants: 1492/1492 rejected
mutants accepted: 0
```

The output mutants are applied **inside the located pinned region** (exact offsets), so
each one genuinely changes a pinned token — the pins are not decorative.

---

## 7. Arithmetic cross-check ledger (all reconcile)

| identity | result |
|---|---|
| landing: 4 files, 1907 insertions, 0 deletions; run_battery `+163/−0` in 2 blocks | ✓ |
| CASES 307 → 359; rows 314 → 366 (7 meta); r95 contiguous at 303–354; tail 4 intact | ✓ |
| allowlists: 72 expected_errors keys (69 non-empty), 0 r95; 3 required_stderr keys, 0 r95; census 68 rows | ✓ |
| fixtures: byte-copies (sha256 both directions); 743 + 777 lines; project.godot unchanged | ✓ |
| manifests: scout 565 = 566 − self; boundary 1062 = 1063 − self; 0 missing / mismatch / unlisted | ✓ |
| boundary: 132+53+8+16+16+13+8+15 = 261 runs; 69 cells; 0 rc≠0; 0 B stderr | ✓ |
| scout: 99 + 51 + 9 receipts; 150/150 both forms; 17/17 cells uniq=1 | ✓ |
| census: 892 receipts; 472 row receipts = 472 hits + 0 misses; 0 `ERROR:` lines; 20 collisions (x0/y1000 pair) | ✓ |
| own-cell binding: 35/35 r95b (308 receipts) + 17/17 dss (150 receipts) | ✓ |
| laws: periodx k(k−1) all true; perm 8/8; celloff 14/14→1; cap40 distinct=5 & 3 subsets; layers k0/k1; warm freed = canon, keep8/64 differ | ✓ |
| mutants: 52 baseline + 3288 sig + 1492 output, all rejected | ✓ |
| cross-run: 307 identical + 59 differing (24 r95, `proc=` only) + 3 flips = 366 | ✓ |
| six 366-row runs: r95 52/52 and gate `true` in every one | ✓ |

---

## 8. Adjudication items (ranked)

| id | dossier | item | severity | disposition |
|---|---|---|---|---|
| **F1** | landing precision | `r95b_order_celloff_x0` and `r95b_order_celloff_y1000` carry **byte-identical signatures**: the probe's payload echoes only the x offset (`off=0.0000`), so the y=+1000 cell's PASS line is indistinguishable from x=0's; the discriminator is the `--offy=1000` flag. All 20 census "collisions" are exactly this pair. The row is still a distinct configuration (a behaviour change at y=+1000 changes the ladder and rejects), but the two rows are not independently *pinned* by signature text. | **low** (precision; no verdict change) | keep; if precision is wanted, echo the y offset in the fixture's cell header line in a future pass |
| **F2** | dossier arithmetic | `corpus/live/r95-boundary/RECEIPTS.md` batch table says the `quiet` batch has **55 cells**; measured **58** (and the boundary report §0 says 58). | **low** (doc) | record; report §0 is authoritative |
| **F3** | unpinned surface | Every `r95b_order_*` row's output also carries `R95B <arm> env=tps=60 pf=<N> proc=<M> sep2d…` whose **`proc=` process-frame counter varies per run**; between my two runs 24/52 r95b rows had differing full outputs, and *all* 24 differences were exactly that token (physics-frame `pf=` and every pinned PASS line are stable). The author declared `env` unstable and did not author it — this is the same class, recorded so nobody reads "row output" as byte-frozen. | **info** (declared, not pinned) | keep; no row pins `proc=` |
| **F4** | provenance | The two landed fixture **headers declare no sha256** (the labrat's clause-4 caveat). The hash declarations live in the battery comment header (`run_battery.py:882/885`) and the author report; byte identity is nevertheless proven by direct hashing of committed bytes. | **info** | record; add the sha to the fixture header in a future pass if the convention matters |
| **F5** | landing gate | `r95_expected_errors_all_matched` is **vacuously true today** (0 r95 allowlist entries, 0 r95 census rows) and inherits the executed-rows-only census scope; loudness demonstrated by the extracted expression (dead r95 entry → `False`, live → `True`, dead non-r95 → `True`). | **info** (intended carried-floor semantics) | keep |
| **F6** | host class | Both committed-byte runs' failures are the documented pre-existing volatile class (`overlap`, `transition`, `negative_transition`, `audio_bus_route`); `negative_transition`'s missing allowlisted lines produce 2 dead entries and the meta row fails **closed** (`census_bare_classifier_consistent=false`). No r95 row flaked in any of the six runs. | **info** (fail-closed, pre-existing) | record; the meta row is the loud canary, as intended |
| **F7** | coverage scope | This seat's mode coverage: all 35 r95b rows at `--fixed-fps 30`, 5 r95b sentinels at ff120, 16 cells (10 dss + 6 r95b) under threaded physics — the **17 `dss_lattice_*` rows have no ff30/ff120 re-measurement here** (scout measured them 150/150 at 60 tps incl. 16-hog load; the boundary's ff/thr identity evidence is r95b-only). | **info** (declared coverage gap) | record; the dss rows are frame-disciplined (`await _frames`) like the r95b rows, so the risk is bounded |
| **F8** | evidence custody | The author's four 366-row runs live under gitignored `corpus/live/runs/**` (`git ls-files corpus/live/runs` = 0) and the scout/boundary `runs/` trees are largely untracked (13 of 566 and 10 of 1063 files tracked); the manifests cover them where they exist. | **low** (convention, same as r87–r94) | record; force-add `verdicts.json` at wave fold if the operator wants run evidence in-tree |

---

## 9. Remaining risks / blockers

1. **No blockers to the landing.** Both committed-byte runs are green on the r95
   surface (52/52 each, gate `true`), both manifests verify completely, the 52 rows are
   bound to their own-cell receipts, and every recomputable dossier claim reproduces
   (the F1/F2/F4 notes aside).
2. **Phase-locked order pins by design.** The 35 `r95b_order_*` rows pin the
   tick-phase-resolved k(k−1) cycle; a fixture edit that changes the tick discipline
   breaks them loudly — that is the law, not a phase (the r95 scout's original
   single-phase rows were the wrong thing to pin; the boundary's finding is folded).
3. **Frozen-scene scope.** `warm_keep8` (and the unpinned `keep64`) show that live
   unrelated colliders perturb the returned order deterministically; the pinned vectors
   are valid only for their frozen scene composition.
4. **Thin prefix rows.** `point_cap[_rev]` and `order_core[_rev]` pin only
   `add_order=…` (+ `cap0=[]`); every ordering claim is carried by the `r95b_order_*`
   rows — intended, but do not read those four rows as order coverage.
5. **k(k−1) is measured for point queries over static rectangles** (boundary §11);
   `intersect_shape`/`intersect_ray` cycles are spot-checked only, and non-rect /
   rotated / server-tier periods are unmeasured.
6. **Host-conditional tokens** (class enums, `RID(0)`/`canvas_instance_id` defaults,
   4-dp float strings, `tps=60`) flip loudly on an engine or `project.godot` bump —
   intended, same class as prior rounds.
7. **`procwait`/`env` remain un-authored** (correctly): a process-frame-awaiting harness
   cannot pin a tick-phase vector even on an idle host.
8. **Gitignored run trees (F8)** mean the strongest run evidence is lane-local until a
   wave fold force-adds it.

---

## 10. Host notes / cleanup

- I added no `yes` hogs; my own load was 2 batteries + 160 bounded single-arm launches.
  No orphaned `godot`/`python3` processes remain from this lane (`pgrep` clean of
  `r95-scribe`); sibling lanes' processes were left untouched.
- `/tmp` untouched; the committed-tree extract lives at
  `/home/vgpnk/r95-committed-extract` (retained this session); the fresh-arm scratch
  projects live inside the lane (`fresh-proj/`, `fresh-proj-threaded/`) and are
  byte-copies of the committed fixtures.
- **Late-window commit:** `35001d1d` (concurrent r94-simplifier lane) advanced HEAD
  during the audit; no r95 artefact changed (blob-by-blob verified). This seat wrote
  no tracked file, committed nothing, and left the concurrent lane's work untouched.
- Zero tracked files written: `git status --porcelain -uno` was empty at audit start,
  after both battery runs, after all 160 launches and after every recomputation; the
  tracked `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` was **not**
  regenerated (the harness was always executed as a script, never imported). At the
  final check the only entry is the concurrent r96-author lane's foreign worktree edit
  of `corpus/fixtures/run_battery.py` (see the second late-window note) — left
  untouched per "preserve unrelated work".
- `manifest.sha256` covers 1091 files (every lane artefact except itself and the two
  regenerable scratch project copies); it verifies with 0 missing / 0 mismatch.

---

## 11. Evidence index

All under `corpus/live/r95-scribe/`; `manifest.sha256` covers every artefact in that
directory except itself and the two scratch project copies.

| artefact | path | notes |
|---|---|---|
| battery run 1 (worktree, committed bytes) | `battery-runs/20261016T070820061770Z/verdicts.json` + `battery-rep1.log` | 366 rows, 361 PASS, r95 52/52, gate true, dead 2 |
| battery run 2 (`git archive HEAD` extract) | `battery-committed/20261016T071623277563Z/verdicts.json` + `battery-rep2.log` | 366 rows, 364 PASS, r95 52/52, gate true, dead 2 |
| fresh single-arm receipts | `fresh/<case>.<mode>.rep<N>.{out,err,rc}` (160) | 104 default + 35 ff30 + 5 ff120 + 16 threaded; all rc=0, 0 B stderr, sig present |
| static custody audit | `audit/static_audit.py` → `static_audit.json` | identity, diff shape, CASES, allowlists, gate, manifests, scout rows, author runs |
| own-cell binding | `audit/own_cell_binding.json`, `audit/scout_own_cell_binding.json` | 35/35 + 17/17 |
| receipts census | `audit/receipts_census.py` → `receipts_census.json` | 892 receipts; 472/472; 0 `ERROR:`; 20 collisions |
| law re-derivation | `audit/laws_recompute.py` → `laws.json` | cycle/perm/celloff/twopiles/free/cap40/layers/warm/rigid/procwait/env |
| mutant + classifier | `audit/recompute.py` → `recompute.json`; `audit/floor_gate.py` → `floor_gate.json` | 3288/3288 + 1492/1492; gate loudness; trailing/stderr/control |
| cross-run comparison | `audit/compare_runs.py` → `compare_runs.json` | 307/59/3 |
| scout verifier re-run | `audit/scout_verify_rows.txt` | `ROWS` 150/150, `ROWS_PREFIX` 150/150 |
| fresh-arm driver | `audit/fresh_arms.py` | replay script |
| lane index / replay | `RECEIPTS.md` | commands + headline numbers |
| source reports | `reports/round-95/r95-{scout,boundary,author}.md` | tracked, sha-verified |
