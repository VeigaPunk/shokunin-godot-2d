# r95 verifier — independent non-author verification of `9cd47507`

**VERDICT: VERIFIED-WR** — the committed r95 landing clears the wave-B gate on
every axis this seat can test, with reservations stated in §10 (four declared
thin head-prefix rows; the phase-locked scope of the `dss_lattice` full-line
rows; the pre-existing load-flake rows that made two of three battery reps red
while the r95 block stayed 52/52 in every rep).

Seat `VERIFIER` (g2d lane r95, independent non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, default
60 tps), Python 3.14.7, 32 cores. Target:
`9cd475078dfb8c7df1d394c68d81a1dce14d585b` (*r95 author: 52 dss/order rows
(366 total) — k(k-1) cycle ladder, perm0-7 creation perms, co-presence
attribution folded; 366/366 x2*). Receipts: `corpus/live/r95-verifier/`
(index in `RECEIPTS.md`; `manifest.sha256` — 1390 entries, `sha256sum -c`
rc=0 — covers every artefact outside the regenerable trees declared in
`MANIFEST-SCOPE.txt`). Author
report `reports/round-95/r95-author.md`; inputs `reports/round-95/r95-scout.md`,
`reports/round-95/r95-boundary.md`.

**`lsp` disclosure.** No `lsp` device and no GDScript language server is
exposed to this seat (unchanged lane state r89–r95); every semantic check below
is a static read of the committed bytes plus fresh-process execution — the
recorded fallback. The change is two new fixtures plus an insertion-only
harness block (no renames, no symbol moves), so no symbol-aware operation was
possible or required.

**Frozen probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2,
agent `694c40ee`) was dispatched with one bounded static hypothesis in four
clauses over the committed bytes: (A) both committed fixtures are
byte-identical to the frozen lane probes; (B) the four vector cells carry the
scout's `ROWS_PREFIX` cut (no `cap1=`/`rep1=` leak) and the other 13 carry
full lines; (C) the committed `r95b_order_canon` signature appears
byte-for-byte in `runs/quiet/canon.rep1.out` including `t20`/`t22`/
`cycle_len_dense=20`; (D) every committed `--arm=` has a fixture match arm and
`procwait`/`env` are fixture-only. Results: **A CONFIRMED** (via the lane
manifests and line counts; the labrat's seat has no shell, so this seat's own
`sha256sum` runs close the hash gap — §1), **B CONFIRMED**, **C CONFIRMED**,
**D CONFIRMED**. Advisory only; no second dispatch; it wrote nothing.

**Concurrent-worktree disclosure.** HEAD was `9cd47507` at freeze time
(07:05Z) and has since advanced to `5d3a947c` (*r95 scribe: CUSTODY HOLDS on
9cd47507*, on top of `35001d1d` r94 simplifier/adjudicator) — but
`git diff 9cd47507 HEAD -- corpus/fixtures` is **empty**: the committed fixture
and harness bytes at HEAD are exactly the verified ones. A foreign seat (the
**r96 author**) is concurrently editing the shared worktree's
`corpus/fixtures/run_battery.py` (+233 lines: an r96 block, CASES 359 → 419)
and, by importing it, regenerated the tracked
`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` (mtime 07:31Z).
Re-checked (`probes/worktree-integrity.txt`): all 52 committed r95 tuples are
**byte-identical** in the worktree copy, still at CASES indices 303–354, the
r95 floor gate is untouched, and there are no r95 allowlist keys — that edit is
additive to this report's scope. All battery reps, fresh arms and probes ran
the **frozen extraction** (`git archive 9cd47507 corpus/fixtures`), whose 83
files match their git blob sha1s exactly
(`freeze/blob-identity-mismatches.txt`, 83/83, 0 mismatches); the worktree copy
of `corpus/fixtures/run_battery.py` was byte-identical to the committed blob
(`b93cbdaa…`) at freeze time, and the two fixture files are byte-identical to
both the commit and the frozen lane probes.

**Tracked writes: zero — both tracked modifications now in the worktree are
foreign.** All artefacts are untracked `corpus/live/r95-verifier/**` plus this
report. This seat never imported the worktree harness: its imports all load
`corpus/live/r95-verifier/freeze/corpus/fixtures/run_battery.py`, which has its
own `__pycache__` (written 07:06Z, inside the receipts). The worktree's
` M corpus/fixtures/run_battery.py` and ` M …/run_battery.cpython-314.pyc` are
the r96 author's (timestamps 07:21–07:31Z, after this seat's last import).

---

## 1. Method — frozen committed bytes

- **Whole-repo content check**: `git diff --quiet HEAD` → rc=0 at freeze
  (`git rev-parse HEAD` = `9cd47507`).
- **Fileset**: committed `corpus/fixtures` subtree = **83 entries** vs 83 files
  in the extraction — 0 diffs.
- **Blob identity**: every extracted file hashed as a git blob sha1 against
  `git ls-tree -r 9cd47507` — **83/83 match, 0 mismatches**.
- **Pins (frozen, `sha256sum` computed here)**: `dss_lattice.gd`
  `77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627`
  (743 lines); `r95b_order.gd`
  `4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490`
  (777 lines); `run_battery.py`
  `b93cbdaa3d5c6ae35d69970a545442d86898a959f0e2e2995f1adf58a3444ed7`
  (4590 lines); `project.godot` `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9`.
  The two fixture hashes equal the frozen probes
  `corpus/live/r95-scout/probes/dss_lattice.gd` and
  `corpus/live/r95-boundary/probes/r95b_order.gd` (byte-identity, zero diff).
- **Commit scope**: `git show --stat 9cd47507` = 4 paths —
  `corpus/fixtures/dss_lattice.gd` (+743), `corpus/fixtures/r95b_order.gd`
  (+777), `corpus/fixtures/run_battery.py` (+163),
  `reports/round-95/r95-author.md` (+224); **no other fixture, no
  `project.godot`, no receipts corpus** (the standing worktree-only battery
  custody property, r94 F5).
- **Launch project**: `corpus/fixtures/project.godot` is 3 lines and pins no
  `physics_ticks_per_second`; the battery scratch edits only `config/name`.

**Harness delta `6f817d10 → 9cd47507`** (`probes/audit-committed.txt`,
`probes/cases-delta.txt`, `probes/tail-check.txt`):

- `git diff --numstat` = **163 / 0** — two pure-insertion hunks:
  `@@ -877,0 +878,152 @@` (CASES block) and `@@ -3113,0 +3266,11 @@` (floor gate).
- CASES **307 → 359** tuples; the 52 `r95_*` rows sit at **CASES indices
  303–354** (contiguous), immediately after `r94_particles_gpu_headless` and
  immediately before `crash_spontaneous_sigabrt`.
- **Pure-insertion proof at tuple level**: `child[:303] == parent[:303]` and
  `child[355:] == parent[303:]` — the child is exactly the parent plus the
  block. The **last four CASES tuples are byte-identical** to the parent's
  (`crash_spontaneous_sigabrt`, `crash_self_sigkill`,
  `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`),
  and the parent harness contains **0** r95 tokens.
- 17 `dss_lattice_*` + 35 `r95b_order_*` = 52 rows; scripts are only
  `dss_lattice.gd` / `r95b_order.gd`; every expected exit is 0; every flag set
  is `--arm=…` (+ optional `--rev`/`--k=`/`--perm=`/…).
- `expected_errors` / `required_stderr`: **0 r95 entries** (no r95 case name
  appears as a dict key anywhere in the harness).
- The floor gate `r95_expected_errors_all_matched` (predicate
  `case.startswith(("dss_lattice_", "r95b_order_"))`) is present — the same
  named-by-round shape as r87–r94 (10 round gates in the harness).
- The production `classify_process` segment hashes to
  `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`
  (AST source segment) — **identical to the r89–r94 pin**.
- **Scout-row provenance**: all 17 committed `dss_lattice_*` signatures are
  **byte-identical to the scout's `ROWS_PREFIX`** entries (17/17) and are
  prefixes of the scout's full-line `ROWS` entries (17/17). The four vector
  cells carry the cut form (`…cap0=[]`, `…add_order=[a,b,c,d,e]`,
  `…add_order=[e,d,c,b,a]`) — no `cap1=`/`rep1=`/`layout_changes_order`
  leak. The other 13 are the full lines.
- **Boundary-receipt provenance**: all 35 committed `r95b_order_*`
  signatures are **exact whole `PASS` lines** of their matching cells in the
  boundary receipts (35/35), and **every receipt of a committed cell carries
  the same single PASS line** (`pass_uniq=1`; see §4).
- **Fixture dispatch coverage**: 13/13 `dss_lattice` arms and 13/13 committed
  `r95b` arms exist in the fixtures' `match arm:` blocks; `procwait` and `env`
  are declared fixture arms with **no committed row** (the boundary's two
  unstable cells, deliberately unauthored — §4).

---

## 2. Battery on the frozen committed harness

`python3 <frozen>/run_battery.py --runs corpus/live/r95-verifier/runs` — the
frozen committed harness, its own scratch staging (`pickup.tscn`, app-name
munging, `causal_chain` readiness fix), 8 s per-case bound.

| rep | run dir | verdict | rows | failures | r95 rows | r95 gate | dead entries |
|---|---|---|---|---|---|---|---|
| rep1 | `runs/20261016T070634425299Z/` | FAIL | 366 | `overlap`, `phys2d_motion_bds_windows` | **52/52 PASS** | True | 0 |
| rep2 | `runs/20261016T071643670729Z/` | FAIL | 366 | `negative_transition`, `audio_playback`, `audio_bus_route`, knock-on `probe_error_clause_surface` | **52/52 PASS** | True | 2 |
| rep3 | `runs/20261016T072400528215Z/` | **PASS** | **366/366** | none | **52/52 PASS** | True | 0 |

All ten round gates (`phys2d`, r87–r95) are `True` in every rep. The mutant
run's r95 gate is `False` by construction (§6). Loadavg stamps per rep:
`probes/run-stamps.txt` (rep1 ≈95, rep2 97.9 — run concurrently with the
mutant battery, rep3 75.2 alone).

**Author runs re-verified** (`probes/summarize_runs.py` over
`corpus/live/runs/20261016T05*/06*`): the commit message's *366/366 ×2* claim
is confirmed —

| author run | rows | failures |
|---|---|---|
| `20261016T055703426158Z` (r94 tree, 314 rows) | 314 | none |
| `20261016T060430025246Z` (r94 tree, 314 rows) | 314 | none |
| `20261016T064148780406Z` | 366 | `input_lattice_pre_frame` (documented r87 one-tick flake) |
| `20261016T064742446822Z` | 366 | **none** |
| `20261016T065335715243Z` | 366 | `negative_transition`, `audio_bus_route_invalid_control`, knock-on `probe_error_clause_surface` |
| `20261016T065922894811Z` | 366 | **none** |

**The rep1/rep2 failures are the pre-existing load class, not
r95-attributable.**

- `overlap` (CASES 4) failed with `ERROR: overlap probe: signal occurred before
  physics overlap observation` — the same row failed in the r94 verifier's
  rep1 under load, and it is CASES index 4 ≪ 303.
- `phys2d_motion_bds_windows` (CASES 3) is a **float-tail row** pinning
  `integ_last={ "count": 2, "lv": (0.0383, -0.006104) }`. It emitted
  `lv=(-0.000088, 0.000015)` once — under loadavg ≈ 100 — while **6/6 prior
  runs emitted the byte-identical pinned tail**. This is a load-sensitive
  pre-existing row (r80-era), not touched by the r95 block; the r95 rows were
  **52/52 PASS in the same rep**.
- rep2's three row failures are the lane's documented wall-clock/one-tick
  class: `negative_transition` ("negative transition probe exceeded 120
  frames" — the same row failed in the author's run3 and in the r94 verifier's
  reps 1/3), `audio_playback` (`position_before == position_after`,
  non-advancing wall-clock audio), `audio_bus_route` (`advanced=false` — the
  sibling of the row that failed in the r94 verifier's rep1). Its
  `probe_error_clause_surface` FAIL is the documented **knock-on**: the two
  `negative_transition` allowlist entries die with it (`dead_entry_count=2`,
  both named in `census.dead_entries`), flipping exactly
  `census_bare_classifier_consistent` — the same shape r94's verifier
  recorded. The r95 gate itself stayed `True`.
- Every failing row is CASES index ≤ 37 ≪ 303 and executes minutes before the
  r95 block; the r95 rows carry no allowlist and no interaction with them.
- rep2 ran **concurrently with the gate-mutant battery** (a second full
  battery) — disclosed; rep3 ran alone and is **green 366/366**.

**Per-row stability across 9 runs** (`probes/row-stability.txt`): 9 battery
runs × 52 rows = **468 r95 row-instances, 0 mixed verdicts**, every row emitted
**exactly one distinct line**, and no run missed a line — the pinned signature
bytes are identical across quiet and loaded conditions, the author's six runs
(two on the r94 tree, four on the r95 block) and this seat's three.

---

## 3. Fresh arms — 156/156 clean on the committed bytes

`probes/fresh_arms.py` (battery's exact launch shape on the frozen fixtures,
`--headless --path <scratch> --script res://<fixture> -- <flags>`, 8 s bound;
receipts `arms/<case>.rep{1,2,3}.{out,err,rc,wall_ms}`):

- **156/156 launches rc=0, 0 B stderr**, every PASS line on stdout.
- **156/156 row classifications PASS** with the production `classify_process`
  (AST-extracted from the frozen harness).
- Slowest arm wall: `r95b_order_periodx_k10` 2.32 s max (8 s bound, ≈3.4×
  headroom); `periodx_k8` 1.83 s, `celloff_x0` 1.80 s, `canon` 1.80 s.
- Full-line byte stability: 48 rows emit the exact signature line; the 4
  `dss_lattice` vector cells emit the longer full line (the signature is their
  head — by design; `nonexact_rows` lists exactly those four).

---

## 4. Signature coverage, receipt hygiene, forgery surface

`probes/signature_coverage.py` → `probes/signature-coverage.{txt,json}`: every
canonical receipt of an r95 row's own cell is re-classified with the production
classifier and must contain the committed signature.

- **326 canonical receipts** (r95-scout 150 = 99 canonical + 51 loadtest;
  r95-boundary 176 for the committed cells) → **326 PASS / 0 REJECT / 0 MISS**;
  **290 exact whole-line** matches + **36 substring-only** — and the 36 are
  exactly the 4 head-prefix rows × 9 receipts, i.e. the cut is where the report
  says it is, with the vector tails still present as data.
- **All 411 receipts of the whole r95-scout/r95-boundary cell sets** (including
  the unauthored cells): **0 stderr bytes, 0 `ERROR:` lines**. All 150 scout
  and 261 boundary `.rc` receipts are **rc=0** (0 timeouts).
- **PASS-line uniqueness per cell**: 69 boundary cells → only `procwait`
  (8 distinct payloads) and `env` (2) vary; all 17 scout cells (and all 67
  other boundary cells) emit a single distinct PASS line — the boundary's
  §8/§9 stability table re-derived independently from its own receipts.
- **No fallback forgery**: `unknown_arm` appears in **no** canonical receipt;
  the fixtures' fallback line is `FAIL dss_lattice %s reason=%s` /
  `FAIL r95b_order %s reason=%s` (both `quit(1)`), and **no committed
  signature is a substring of it** (every committed signature starts with
  `PASS `).
- **Pre-freeze residue (not reproducible on the frozen bytes)**: one non-empty
  `.err` in the whole corpus — `runs/smoke/census.err` (332 B: a *pre-freeze*
  `dss_lattice.gd` revision whose `_set` signature mismatched the parent at
  line 118), plus `runs/disc/` and `runs/leak-hazard/` receipts carrying the
  server-RID leak `ERROR: … 'P11GodotBody2D' were leaked at exit` — the
  discovery-phase hazard the scout documented, fixed before the freeze. The
  canonical cell set (all 411 receipts) is leak-clean and 0 B stderr; this
  seat's 156 fresh launches are also 0 B stderr. Same class as r94 F4.

---

## 5. Discrimination — would a broken law actually fail the row?

`probes/discriminate.py` → `probes/discrimination.{txt,json}`: for each of the
52 rows, take the fresh rep1 receipt that classifies PASS, mutate, re-classify.

- **Global axes, all 52 rows**: rc flip **52/52 reject**, injected unrelated
  `ERROR:` line **52/52**, `SCRIPT ERROR:` **52/52**, `Parse Error:` **52/52**,
  signature deletion **52/52**.
- **250/250 sampled in-signature token mutations reject** (bool flips, integer
  ±1, float last-digit, last-letter), sampled first/middle/last per signature —
  **no row has a token-mutation gap**. This includes the thin rows: mutating
  `cap0=[]` → `cap1=[]` in `dss_lattice_point_cap` rejects, so the cap-0 pin is
  load-bearing.
- **Tail controls**: appending junk after the signature is admitted **52/52**
  (substring semantics — the classifier is a `signature in output` test, the
  documented property); for the 4 head-prefix rows the *unpinned* tail
  (239–431 chars of order vectors) is admitted when mutated — the deliberate
  cut, now measured, not assumed.

---

## 6. The `r95_expected_errors_all_matched` floor gate

- **Static**: present, keyed on `case.startswith(("dss_lattice_",
  "r95b_order_"))`; **vacuous today** (0 r95 allowlist entries).
- **Live**: `True` in all three of this seat's reps and in all four r95-era
  prior runs (the two r94-tree runs predate the gate).
- **Mutant run** (`probes/make_gate_mutant.py` → `gate-mutant/`, one dead r95
  allowlist entry injected for `dss_lattice_census`, diff in
  `probes/gate-mutant-build.txt`; run `runs-mutant/20261016T071733368310Z/`):
  `r95_expected_errors_all_matched` = **False**, `dead_entry_count` 3 with the
  injected entry named in `census.dead_entries`, `dss_lattice_census` itself
  still **PASSes** (its `expected_errors` now carries the injected entry), and
  **every other round gate stays True**. The gate is therefore **load-bearing**
  — a future dead r95 allowlist entry cannot die silently. (The mutant run's
  own `negative_transition` flake additionally flipped the unrelated
  `census_bare_classifier_consistent` discrimination, the same knock-on as
  rep2; the r95 gate flip is independent of it.)

---

## 7. The pinned laws re-derived from the committed signatures

`probes/verify_laws.py` → `probes/laws.{txt,json}`: 47 boolean law checks
parsed out of the committed signature strings themselves, **47 true / 0
false**:

| check | result |
|---|---|
| canon ladder closes: `t20==t0`, `t21==t1`, `t22==t2`, `t64==t4`; 20 distinct phases; `t0` = insertion order; `distinct_ticks=20`, `cycle_len_dense=20` | all true |
| `cycle_len == k(k−1)` and `distinct_ticks == cycle_len` for k = 2,3,4,5,5@spacing8,6,7,8,10 (2,6,12,20,20,30,42,56,90) | all true |
| 8 permutations → 8 distinct ladders, 8 distinct `t2_relpos` vectors, 8 distinct `t2_vec`; `map` constant; 8 distinct `add_order` | all true |
| cap40: `n0=0 n32=32 n64=40`; `set32_distinct=5` and the 5 sampled tick-sets are 5 distinct 32-subsets; 3 creation orders → 3 distinct `set32_t2` | all true |
| `celloff` x0/x1000/y1000 identical ladder, `t2_vec`, `t2_relpos` (translation invariance) | all true |
| `free_ab` vs `free_ba`: differ at every sampled tick, same final set, post-free cycle `t2==t8` | all true |
| `warm_k32` ladder == canon on all common ticks, `t2_vec` equal; `warm_keep8` differs (`distinct_ticks=4`) | all true |
| `scoutrev`: `t2_vec` = the scout's `order_core_rev` row, `t2_relpos` == canon's | all true |
| `layers_k0` `pt_eq_sh=true sh_len=5` vs `layers_k1` `pt_eq_sh=false sh_len=6` | all true |
| `rigid` `distinct_ticks=1`, `t10_relpos=[15.9999,14.8732]` | all true |
| `twopiles`: A-alone `t2` == canon; A-with-B `t4` = `[e,a,c,b,d]` ≠ canon `t4` `[e,a,b,c,d]` | all true |

The measuring helpers are real measurements, not echoes: `periodx` *searches*
for the smallest periodic p over `k(k−1)+3` sampled ticks (a wrong period
would emit `cycle_len=-1` and fail the row); `canon` derives `distinct_ticks`/
`cycle_len_dense` from the sampled sequence; `layers`/`canon` compute the
point/shape equality from two measured vectors (and it *is* false in the
`layers_k1` branch); `scoutrev` compares measured vectors against the scout's
literals. No pinned boolean was found to be tautological.

---

## 8. Findings (ranked)

**F1 (LOW — pre-existing load flakes, not r95; new).**
Under loadavg ≈ 95–100 my rep1 and rep2 failed 2 and 3 pre-existing rows
(`overlap`, `phys2d_motion_bds_windows`, `negative_transition`,
`audio_playback`, `audio_bus_route`) plus the documented allowlist knock-on
`probe_error_clause_surface`; rep3 (loadavg 75) is **366/366 green**. The
`phys2d_motion_bds_windows` float tail is byte-identical across all 6 prior
runs and diverged only in the loaded rep1 — a latent lane property (r80-era
row), unchanged by this landing; the r95 block was 52/52 PASS in **every** rep
including the FAIL ones.

**F2 (LOW — the four `dss_lattice` order-vector rows are thin by design;
declared).** `point_cap[_rev]` pin only `add_order=… cap0=[]` and
`order_core[_rev]` only `add_order=…`; every ordering claim lives in the 35
`r95b_order_*` rows. Discrimination confirms the pins that remain are
load-bearing (§5) and that the vector tails are deliberately unpinned (the
`layout_changes_order` key the boundary refuted is outside the signed region).
Risk: a broadphase-order change at the t=2 phase is only caught by the `r95b`
ladder rows, not by these four.

**F3 (LOW — pre-freeze receipt residue; new).** `runs/smoke/census.err` (332 B,
parse-error revision) and the `disc/`+`leak-hazard/` RID-leak `ERROR:` receipts
are pre-freeze revisions; not reproducible on the frozen bytes (411 canonical
receipts 0 B stderr/0 `ERROR:`; 156 fresh launches 0 B stderr). The scout marks
them as not-evidence; they are the same pre-freeze-revision class r94's
verifier recorded.

**F4 (INFO — scope limit pinned as data, declared).** `warm_keep8` shows that
live unrelated colliders change the returned order (`[a,e,b,c,d]`,
`distinct_ticks=4`); the pinned vectors are valid only for their frozen scene
composition. Pinned as data, not as a bug.

**F5 (INFO — phase-locked pins, now bounded by law rows).** The pinned order
vectors are the t=2 phase of a k(k−1) cycle. The landing pins the cycle *law*
(`canon` t20==t0 + 20 distinct phases; `periodx` k=2…10) rather than one phase
in isolation, so a cycle-length change or a non-closing drift is caught; only a
pure *phase shift with unchanged period* could pass the ladder rows while
changing a t=2 vector. The `procwait`/`env` cells (process-frame awaits, 8 and
2 distinct payloads) remain correctly unauthored.

**F6 (INFO — wall-time margin).** Slowest r95 arm 2.32 s fresh (8 s bound);
mean 1.09 s per launch, so the 52-row block adds ≈ 55–60 s to a 366-row
battery.

---

## 9. Remaining risks / not measured

- **Host is multi-lane and heavily loaded** (loadavg 75–103 throughout this
  seat's runs); all numbers are host-conditioned. rep2 additionally ran
  concurrently with the gate-mutant battery (disclosed); rep3, run alone at
  loadavg 75, is green 366/366.
- **k(k−1) is pinned for point queries over static rectangles** (boundary §11);
  ray/shape/cast families, rotated/non-rect/multi-shape bodies and areas are
  not cycle-scanned. The pinned cells are exactly the measured set.
- **`--fixed-fps` / threaded-physics coverage is inherited from the boundary
  receipts** (re-classified here, byte-identical), not re-executed by this
  seat.
- **The `dss_lattice` full-line rows remain construction-bound** (the scout's
  own caveat): they pin a frozen construction's lattice, not a general law —
  the laws are the `r95b` rows.
- **Blockers: none.** Nothing committed; other lanes' untracked `corpus/live/`
  artifacts untouched.

---

## 10. Reservations (why WR, not a bare VERIFIED)

1. **Four declared thin rows** — `dss_lattice_point_cap[_rev]` pin only
   `add_order=… cap0=[]` and `order_core[_rev]` only `add_order=…`. The
   remaining pins are load-bearing (discrimination §5), but the rows cannot
   fail for the ordering claims; every ordering claim is carried by the 35
   `r95b` rows. Declared by the author and by the boundary; measured here, not
   assumed.
2. **Phase-locked scope of the `dss_lattice` full-line rows** — the emitted
   order vectors are the t=2 phase of a k(k−1) cycle. The landing pins the
   cycle *law* (`canon` t20==t0 + 20 distinct phases; `periodx` k=2…10), so a
   period change or a non-closing drift fails; only a pure phase shift with
   unchanged period could pass the ladder rows while changing a t=2 vector.
3. **The battery as a whole is not green under load** — two of three reps
   carried pre-existing flake rows (`overlap`,
   `phys2d_motion_bds_windows`, `negative_transition`, `audio_playback`,
   `audio_bus_route` + the allowlist knock-on meta row), all with failure
   history in the corpus and none r95-attributable. The r95 block itself was
   52/52 PASS in all three reps and byte-stable across 9 runs (468 instances).
4. **Inherited (not re-executed) determinism conditions** — fixed-fps 1/30/120
   and threaded physics are verified by re-classifying the boundary's own
   receipts (byte-identical per cell), not by new runs.
