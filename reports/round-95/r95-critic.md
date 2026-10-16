# r95 critic — adversarial review of committed `9cd47507` (52 dss/order rows, 366-row battery)

Seat `CRITIC` (g2d lane r95) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps default,
`RendererDummy`), Python 3.14.7.
Reviewed commit **`9cd47507`** (`r95 author: 52 dss/order rows (366 total) — k(k-1) cycle
ladder, perm0-7 creation perms, co-presence attribution folded; 366/366 x2`, parent
`6f817d10`). HEAD at session start **`9cd47507`**; HEAD at report time **`6128778b`** (after
the sibling `35001d1d` r94-simplifier, `5d3a947c` r95-scribe and `6128778b` r95-verifier
commits, all report/corpus-only). `git diff 9cd47507 <HEAD> -- corpus/fixtures/` is **empty**,
and the three load-bearing files still hash
`run_battery.py` = `b93cbdaa3d5c6ae35d69970a545442d86898a959f0e2e2995f1adf58a3444ed7`,
`dss_lattice.gd` = `77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627` (743 L),
`r95b_order.gd` = `4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490` (777 L)
at every revision from `9cd47507` to HEAD — so **the reviewed bytes are the current committed
bytes**.
**No tracked write, no commit.** Seat-owned artifacts: `corpus/live/r95-critic/**`
(`manifest.sha256`) and this report.

**Committed tree only.** Every harness-derived check below is pinned to a frozen copy of the
committed tree extracted with `git archive 9cd47507 -- corpus/fixtures`
(`corpus/live/r95-critic/frozen/corpus/fixtures/`), whose hashes are byte-equal to
`git show HEAD:<path>` for the **whole** `corpus/fixtures/` tree (`diff -rq` clean, §2.1). The
worktree carries other lanes' churn — the r96 author's in-flight `+233`-line `r96 block` in
`corpus/fixtures/run_battery.py` (mtime 07:26Z, not this seat's), untracked `r96b_*.gd`,
`scene_io_lattice.gd`, and a regenerated `__pycache__` — **none of it was read as evidence,
and no tracked file was written by this seat** (`git status --porcelain` shows only the r96
lane's ` M corpus/fixtures/run_battery.py` + ` M …run_battery.cpython-314.pyc`, plus this
seat's two untracked paths).

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host (same as
every r89–r95 seat). The change under review is two new fixture files plus an insertion-only
harness block; no symbol-aware rename was required, so hand analysis + fresh-process
execution is the fallback in use.

**probeParent disclosure.** Exactly **one** read-only `ufo-labrat` (agent `b74a0bde`,
depth-2, licence exhausted) was dispatched with one bounded hypothesis: *"for each of the 52
committed signatures, at least one sibling receipt contains it verbatim and no same-cell
receipt carries a different payload"*. Its verdict was **PARTIAL**, and its decisive
structural claim — *"the receipt corpora do not exist on disk: zero `.out`/`.err` files under
`r95-boundary/` or `r95-scout/`"* — is **wrong on this host**: the corpora exist (1053 files
under `corpus/live/r95-boundary/runs/`, 553 under `corpus/live/r95-scout/runs/`, **472
`.out`**). The seat could not see them (a limitation of its read-only seat, the same
null-visibility class the r94 critic recorded); an empty result was **not** recorded as
absence, and this seat re-ran the census with direct shell access (§2.3). Where the labrat's
fallback evidence (the derived `author-rows.py.txt` / `analysis.txt`) overlaps the direct
census, the two agree. No second dispatch; the labrat wrote nothing.

**Load regime.** The host was never idle: foreign `loadavg` 76–108 with other lanes' Godot
batteries (19–22 `godot` processes) for the whole session; this seat added **16** named hogs
for exactly one batch (killed by PID afterwards; no `pkill`). Loadavg is recorded per batch
in `runs/*/summary.json`.

---

## 0. What I ran — 552 fresh arm launches + 2 full batteries + 2 harness-mutant batteries + a 472-receipt read-only census

| # | batch | scope | receipts |
|---|---|---|---|
| 1 | `fresh` | 52 rows × **3 reps**, 60 tps, frozen fixture | 156 |
| 2 | `ff1` | 52 × 1, `--fixed-fps 1` | 52 |
| 3 | `ff30` | 52 × 1, `--fixed-fps 30` | 52 |
| 4 | `ff120` | 52 × 1, `--fixed-fps 120` | 52 |
| 5 | `tps30` | 52 × 1, project `physics/common/physics_ticks_per_second=30` | 52 |
| 6 | `tps120` | 52 × 1, project `physics/common/physics_ticks_per_second=120` | 52 |
| 7 | `thr` | 52 × 1, project `physics/2d/run_on_separate_thread=true` | 52 |
| 8 | `load` | 52 × 1, **+16 seat hogs** (loadavg 99.1 → 108.1) | 52 |
| 9 | fixture mutants | `m1a` order_core no-measure · `m1b` order_core mirror · `m2` point_cap cap0 operand · `m3` canon +6th collider · `m5` periodx window×2 | 30 |
| 10 | harness mutants | `harness-base` / `harness-dead` (trimmed CASES, floor-gate liveness) | 2 batteries |
| 11 | **full battery rep1 / rep2** | frozen committed tree, 366 rows | 2 batteries (rep2 **PASS 366/366**) |
| 12 | read-only census | every `.out` under `corpus/live/r95-{scout,boundary}/runs/**` | 472 |

All 552 arm receipts: **rc=0, 0 B stderr, 0 timeouts** (verdicts PASS except the deliberate
mutant rejections in rows 9 and 10); per-row PASS-line uniqueness = 1 in every batch (§2.4).
Launch shape is the battery's own (scratch copy of the fixtures,
`config/name` munge, `pickup.tscn` staging, `causal_chain.gd` readiness fix, 8 s per-case
bound, `classify_process` semantics with `expected_errors=()`).

---

## 1. Findings (ranked)

### F1 — LOW/MEDIUM (row shape, disclosed) · the two `order_core` rows are **unfalsifiable by engine behaviour**: their whole pinned signature is the probe's own construction echo

`dss_lattice_order_core` pins `PASS dss_lattice order_core add_order=[a,b,c,d,e]` and
`…_rev` pins the same with `[e,d,c,b,a]`. That token is emitted by
`_it("add_order", "[%s]" % ",".join(order))` — a **literal list the probe itself built**
(`dss_lattice.gd` `_arm_order_core`, lines 483–519). The cell's real measurement
(`rep1=`/`rep2=`/`rep3=` … `insert_perturbs=`, and the t=2 phase vector) is printed but
**outside** the signature, because the landed rows are the scout's `ROWS_PREFIX` form
("cut before the first vector", `corpus/live/r95-scout/author-rows.py.txt`).

Two seat mutants make this decisive:

| mutant | fixture change | emitted PASS line | row verdict |
|---|---|---|---|
| `m1a_ordercore_nomeasure` | every query removed after the echo (`_pass()` inserted before `rep1`) | `PASS dss_lattice order_core add_order=[a,b,c,d,e]` — **byte-identical to the committed signature**, with **zero** `intersect_point`/`intersect_shape` calls executed | **PASS** 3/3 (both rows) |
| `m1b_ordercore_mirror` | real creation order mirrored (echo unchanged) | measured `rep1` moves from `[e#0,a#0,c#0,d#0,b#0]` → `[a#0,e#0,c#0,b#0,d#0]` | **PASS** 3/3 (both rows) |

So a broadphase regression that flipped the multi-hit order would be **invisible** in these
two rows; the `--rev` row is not a second test (boundary §3 already said this), and after the
prefix cut neither is a first one. The author discloses the shape ("arm dispatch + frozen
construction only", `r95-author.md` §"New-cell inventory" and the CASES comment) — this is a
**row-shape** finding, not a false claim, and the two rows are 2/366 of the battery.

**Contrast (measured):** the sibling prefix rows `dss_lattice_point_cap[_rev]` **do** bind a
measurement — their cut keeps `cap0=[]` — and mutant `m2` (cap-0 operand replaced by the full
set) flips both to **FAIL** 3/3. So the prefix form is not uniformly vacuous; the loss is
specific to the cell whose only pre-vector token is the echo.

Cheap fixes: (a) pin the phase-stated vector with the phase in the row's own text
(`rep1=[…]` at t=2 — the boundary's recommendation), or (b) drop the two rows and keep the
arm-dispatch assertion in the block's comment, or (c) at minimum make the row text say
"arm dispatch only" so a future reader does not read it as an order test.

### F2 — LOW (conditioning, **undisclosed**) · `r95b_order_rigid` is **60-tps-only**; the other 51 rows are tps/fixed-fps/thread/load invariant

Measured across the condition matrix (52 rows × 7 conditions):

| condition | `r95b_order_rigid` emitted tail | row |
|---|---|---|
| 60 tps (`fresh` ×3, `load`, `thr`, `ff1`, `ff30`, `ff120`) | `ladder=[t1:2;t2:2;t3:2;t5:2;t10:2] distinct_ticks=1 t10_relpos=[15.9999,14.8732]` | **PASS** |
| tps 120 | `ladder=[t1:2;t2:2;t3:2;t5:2;t10:2] distinct_ticks=1 t10_relpos=[15.9999,3.7093]` | **FAIL** (relpos) |
| tps 30 | `ladder=[t1:2;t2:2;t3:2;t5:2;t10:] distinct_ticks=2 t10_relpos=[]` | **FAIL** (relpos + ladder + distinct) |

The pinned `t10_relpos` is a gravity-integration trajectory, i.e. a function of the physics
step (1/tps): at 120 tps the body falls ≈4× less, at 30 tps it has left the query point by
tick 10 (the empty vector). **Blast radius = exactly 1 of 52 rows** — the same class the r94
critic measured as 10–11 rows on the r94 block, here much tighter. The battery pins no tps
and the scratch project edits only `config/name`, so the risk is latent today; but
`r95-author.md`'s risk section names only the k(k−1)-scope limits and does not name this
row's tps scoping. The t≤5 prefix **is** tps-invariant (`t1..t5` identical in all three
modes), so the row can be made tps-robust by cutting at `t5` (or by arming the three
measured modes as an envelope, the repo's bimodal idiom — noting the 30-tps mode is
degenerate: an empty vector, which would weaken the fingerprint).

### F3 — INFO (provenance precision) · the "0 B stderr" corpus claim holds for the **classified** receipts, not for every file under `runs/`

A read-only sweep of both sibling corpora found exactly **one** non-empty `.err`:
`corpus/live/r95-scout/runs/smoke/census.err` (332 B) —

```
SCRIPT ERROR: Parse Error: The function signature doesn't match the parent. Parent signature is "_set(StringName, Variant) -> bool".
          at: GDScript::reload (res://dss_lattice.gd:118)
ERROR: Failed to load script "res://dss_lattice.gd" with error "Parse error".
```

That is a **superseded revision** of the committed probe: line 118 of the committed
`dss_lattice.gd` is `func _setstr(arr: Array) -> String`, i.e. the landed file is the
post-rename revision (positive provenance evidence — the rename really happened). The
`runs/smoke/*` tree is documented by the scout as "frozen-probe arm smoke tests (superseded
by the canonical cells)", and it is **not** part of the 99 canonical + 51 loadtest = 150
classified receipts, so the author's claim is true as written. Note the harness would reject
that receipt (`SCRIPT ERROR:` ⇒ `passed=False`) — the guard works. Only the blanket phrasing
"0 B stderr across the scout receipts" needs the qualifier "classified".

### F4 — INFO · the `periodx` period is verified with only 3 ticks of post-period margin — but a **window-doubling probe confirms the law beyond it** for all 9 cells

`_arm_periodx` observes `n_ticks = k(k−1)+3` ticks and searches the smallest p ≤ k(k−1) that
repeats over the whole window, so the committed rows confirm "period = k(k−1)" with 3 ticks of
margin. Mutant `m5_periodx_ext_window` (window doubled to `2k(k−1)+3`, search up to
`2k(k−1)`) re-measured every cell (the committed `n_ticks=` token differs by construction, so
this arm was read out of band from its emitted line):

| k | 2 | 3 | 4 | 5 | 5@sp8 | 6 | 7 | 8 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| `cycle_len` over the doubled window | 2 | 6 | 12 | 20 | 20 | 30 | 42 | 56 | **90** |
| k(k−1) | 2 | 6 | 12 | 20 | 20 | 30 | 42 | 56 | 90 |
| ticks observed | 7 | 15 | 27 | 43 | 43 | 63 | 87 | 115 | **183** |

⇒ the cycle is **not** a window artifact; k=10 holds over two full periods (183 ticks). No
finding; this closes the "period confirmed only 3 ticks past the period" reading.

### F5 — INFO (engine-conditional tokens) · the `census` row pins the engine's own method census

`dss_lattice_census` pins `dss_methods=n6[…]`, `dss_sigs=[cast_motion(parameters:24)|…]` and
`dss_cls=cls=GodotPhysicsDirectSpaceState2D` — the documented engine-version-pinned token
class (same family as `joys=0` / `nmethods=86`). Intended, but it is the row a future engine
bump rejects first. A scan of all 52 signatures found **no** pid, filesystem path, timestamp,
version string or hex address (the only slash-bearing tokens are the `layer_forms` tag format
`sb:body1/areas1/only0`, and the only large literal is the deterministic mask default
`4294967295`).

---

## 2. What survived (positive verifications)

### 2.1 Commit hygiene and provenance

1. `9cd47507` = **4 files, +1907 / −0**; `run_battery.py` **+163/−0** in exactly two hunks
   (`@@ -877,0 +878,152 @@` = the r95 comment header + 52 tuples, `@@ -3112,0 +3265,11 @@` = the
   floor gate). CASES **307 → 359**; the 52 r95 tuples are **contiguous at CASES[303..354]**,
   the 307 parent tuples are byte-identical **in order** (AST comparison), 0 parent rows
   elsewhere, **no duplicate case names**, all 52 rows `expected_exit=0`.
2. Both fixtures are **byte-copies** of the frozen lane artifacts (sha256 equal to
   `corpus/live/r95-scout/probes/dss_lattice.gd` and
   `corpus/live/r95-boundary/probes/r95b_order.gd`, and to the hashes the report claims).
   The frozen archive equals `git show HEAD:corpus/fixtures/*` byte-for-byte.
3. The 17 `dss_lattice_*` rows are **element-wise equal (order included)** to the scout's
   `ROWS_PREFIX`; the 4 prefix rows are exactly `point_cap`, `point_cap_rev`, `order_core`,
   `order_core_rev` (the only 4 that differ from the scout's full-line `ROWS`), and each is a
   strict prefix of its own receipt PASS line.
4. `EXPECTED_ERRORS` carries **no** `dss_lattice_*`/`r95b_order_*` key and `REQUIRED_STDERR`
   is untouched — `expected_errors += 0, required_stderr += 0` as claimed. No `procwait`,
   `env` or `layout_changes_order` token appears in any of the 52 case names or signatures.
5. Neither fixture has any write surface (`FileAccess`, `DirAccess`, `ResourceSaver`,
   `OS.execute`, `OS.create_process` = 0 occurrences) — the probes are read-only, as the
   battery requires.

### 2.2 Row arithmetic in the pinned bytes

- `periodx` (9 cells): `cycle_len == expected_kk1 == k(k−1)` for k = 2,3,4,5,5@sp8,6,7,8,10;
  `distinct_ticks == cycle_len == k(k−1)` in every cell.
- `canon`: `t0 = 0,1,2,3,4` (insertion order), `t20 = 0,1,2,3,4` (= t0), `distinct_ticks=20`,
  `cycle_len_dense=20`; the t=2 vector `[e#0,a#0,c#0,d#0,b#0]` is the phase the boundary
  pinned.
- `perm0..7`: **8 distinct ladders and 8 distinct `t2_relpos` vectors** (the real
  insertion-order evidence; the scout's `--rev` label permutation is counter-pinned by
  `scoutrev`'s `t2_relpos_equals_canon=true`).
- `cap40_p0..p2`: `n32=32 n64=40 n0=0` in all three perms, `set32_distinct=5` in all three,
  **3 distinct `set32_t2` subsets** — the above-cap set is not invariant, as claimed.
- `layers_k0/k1`, `twopiles`, `warm_k32`/`warm_keep8`, `free_ab/ba`, `readd_a`, `celloff_*`,
  `rigid` all carry their measured operands inside the pinned line.

### 2.3 Signature-vs-receipt census (read-only, 472 `.out` files, independent of the author's claims)

| corpus | runs / `.out` | result |
|---|---|---|
| `r95-boundary/runs/**` (8 batches) | 261 `.out` | every one of the 35 `r95b_order_*` signatures present verbatim |
| `r95-scout/runs/**` (99 canonical + 51 loadtest + alt/disc/discord/leak-hazard/smoke) | 211 `.out` | every one of the 17 `dss_lattice_*` signatures present verbatim |

**52/52 signatures found; per-cell distinct-payload count = 1 for all 52** (no same-cell PASS
line with a different payload anywhere in either corpus — the counterexample class is empty).
48 signatures are **whole-line** matches and 4 are strict prefixes (the `order_core`/
`point_cap` pair), i.e. exactly the author's "13 full-line + 4 head-only" split. The only
non-empty `.err` is F3's superseded smoke receipt.

### 2.4 Fresh reproduction (156 launches, 3 reps) and byte-stability

- **52/52 rows PASS in all 3 reps**, 0 timeouts, 0 B stderr, 0 unallowlisted `ERROR:` lines;
  every receipt that carries its signature carries it on **stdout** (not merged-stderr) — the
  only receipts without the signature anywhere are the two tps-conditioned `rigid` ones (F2).
- **Per-row PASS-line uniqueness = 1 across reps** for all 52 rows: the pinned bytes are
  stable. The rows whose full stdout varies across reps (34 of 52) vary only in the
  **unpinned** `R95B … ids=[…]` / `env=…` diagnostic lines (instance ids differ per process),
  which is the fixture's documented design (diagnostics are never signature material).

### 2.5 Condition matrix (7 conditions × 52 rows = 364 launches)

| batch | rows rejecting | rows with a different PASS line |
|---|---|---|
| `ff1` | 0 | 0 |
| `ff30` | 0 | 0 |
| `ff120` | 0 | 0 |
| `thr` (`run_on_separate_thread=true`) | 0 | 0 |
| `load` (+16 hogs, loadavg 99→108) | 0 | 0 |
| `tps30` | **1** (`r95b_order_rigid`, F2) | 0 |
| `tps120` | **1** (`r95b_order_rigid`, F2) | 0 |

⇒ 51 of 52 rows are byte-identical to their fresh receipts under every condition tested; the
one exception is F2.

### 2.6 Row discrimination (fixture mutants)

| mutant | fixture change | expected | measured |
|---|---|---|---|
| `m1a` | `order_core`: all queries removed after the echo | row still passes (F1) | **PASS** 3/3 both rows, emitted line byte-identical to the signature |
| `m1b` | `order_core`: real creation order mirrored | row blind (F1) | **PASS** 3/3 both rows, measured `rep1` moved |
| `m2` | `point_cap`: `cap0` operand → full set | FAIL | **FAIL** 3/3 both rows |
| `m3` | `canon`: 6th overlapping collider added | FAIL | **FAIL** 3/3 — the ladder carries the extra `z` token (`t0:0,1,2,3,4,z`) |
| `m5` | `periodx`: window ×2 (out-of-band readout) | n/a | law holds for all 9 k (F4) |

⇒ the 48 whole-line rows bind measured behaviour (m2/m3 are the two decisive positive
controls); the two `order_core` rows do not (m1a/m1b).

### 2.7 Floor-gate liveness (harness mutants, trimmed CASES)

`r95_expected_errors_all_matched` is `all(not dead_in_run for r95 rows for e in entries)` and
the r95 block carries **0** entries, so today it is a vacuous `all()` over an empty sequence.
Liveness proof on the frozen tree:

| variant | CASES | r95 entries | r95 gate | `dead_entry_count` | r93/r94 gates |
|---|---|---|---|---|---|
| `harness-base` | 6 rows (3 r95 + the 3 `save_process_*` rows the battery hard-requires) | 0 | **True** | 0 | True |
| `harness-dead` | same + one synthetic never-matching entry on `dss_lattice_order_core` | 1 | **False** | 1 (`dss_lattice_order_core`, exact-shape) | True |

The r95 row itself still PASSes in the dead variant ⇒ the flip is the gate, not the row; and
the r93/r94 gates stay True ⇒ the flip is r95-scoped. The gate is live and protects nothing
today (0 entries) — same shape as r87–r94.

### 2.8 Wall-time margin and battery cost

| batch | max arm wall | slowest arm | 8 s bound |
|---|---|---|---|
| `fresh` (60 tps, ×3) | 2.451 s | `r95b_order_periodx_k10` (93 ticks) | 3.3× headroom |
| `load` (+16 hogs) | 2.179 s | `r95b_order_periodx_k10` | 3.7× |
| `ff30` / `ff120` | ≤ 0.93 s | — | — |
| `tps30` (project override) | 3.743 s | `r95b_order_periodx_k10` | 2.1× |

The 52 arms add ≈ **64 s** (sum of per-arm maxima) to a ≈ 6 min battery. Wall time scales as
`ticks/tps` (the probes await physics frames and the headless loop runs in real time): the
slowest arm reaches the 8 s bound only below ≈ 12 tps — a tps-conditional class, not a
60-tps-production risk.

### 2.9 The author's own four runs re-read (read-only)

| run | verdict | rows | r95 rows | r95 gate | note |
|---|---|---|---|---|---|
| `…T064148780406Z` | FAIL | 366 | 52/52 PASS | True | `input_lattice_pre_frame` emitted a **third** payload (verified: `post_ph=[ph+0{…} ph+1{…}]` is outside both whitelisted modes) — the pre-existing r87 mode-envelope flake, as the author says |
| `…T064742446822Z` | **PASS** | 366/366 | 52/52 | True | second green on identical bytes |
| `…T065335715243Z` | FAIL | 366 | 52/52 PASS | True | `negative_transition` frame overshoot, `audio_bus_route_invalid_control` `advanced=false` (wall-clock row), and the downstream consistency discrimination with `dead_entry_count=3` — all documented flake classes, none r95 |
| `…T065922894811Z` | **PASS** | 366/366 | 52/52 | True | third green |

The "366/366 ×2" headline is honest; the two FAIL runs are attributable to rows outside the
r95 block (verified from their own `verdicts.json`).

### 2.10 This seat's own two batteries on the frozen committed tree

| rep | verdict | rows | r95 rows | r95 gate | `dead_entry_count` | failures |
|---|---|---|---|---|---|---|
| `full-rep1` (`…T072352354541Z`) | FAIL | 366 | **52/52 PASS** | True | 2 | `overlap`, `transition`, `negative_transition`, `probe_error_clause_surface` |
| `full-rep2` (`…T072952743477Z`) | **PASS** | **366/366** | **52/52 PASS** | True | 0 | — |

**The rep1 failure set is a known pre-existing flake combination, not an r95 regression.** A
read-only census over the 48 battery `verdicts.json` files in `corpus/live/runs/` shows the
same three control rows failing together, plus the downstream consistency discrimination, in
`corpus/live/runs/20261015T200615022811Z` (235 rows: `overlap`, `transition`,
`negative_transition`, `audio_bus_route`, `audio_bus_route_invalid_control`,
`probe_error_clause_surface`). Row-level history over those 48 runs: `overlap` 12 PASS / 1
FAIL, `transition` 12/1, `negative_transition` 11/2, `input_lattice_pre_frame` 6/1,
`audio_bus_route_invalid_control` 11/2 — all pre-existing wall-clock/scene-handoff rows with
prior failures in the corpus. The three failing outputs are scene-identity/signal-timing
assertions in `controls/*.gd` (`overlap_probe.gd:41`, `scene_transition_probe.gd:48`,
`scene_transition_negative.gd:22`), none of which is touched by `9cd47507`. Both reps ran the
52 r95 rows green, so the block reproduces independently of the author's four runs.

---

## 3. Cross-seat / custody notes

- **The worktree is not the commit.** HEAD advanced from `9cd47507` to `6128778b` during this
  session (r94-simplifier, r95-scribe, r95-verifier commits — reports/corpus only); none of them
  touches `corpus/fixtures/`, and the reviewed hashes are unchanged at HEAD (§0). The r95
  sibling wave-B reports are now committed (`reports/round-95/r95-{scribe,verifier}.md`); none
  of their content was read as evidence here.
- A concurrent **r96 author** block is in flight in the worktree's `run_battery.py` (+233
  lines, **57** new `r96_*` CASES tuples) — it was never executed or read as evidence by this
  seat, and every battery run here used the frozen `9cd47507` copy (which is why the frozen-tree
  discipline matters: a worktree run would have picked up the r96 block's 57 extra CASES rows).
- The r95 author's four battery run dirs (`corpus/live/runs/20261016T06*`) are worktree
  artifacts and were read **read-only** for cross-checking (§2.9).
- The scout's `runs/smoke/census.err` (F3) is the only pre-freeze receipt that shows a
  *load* failure; the scout's documented `runs/leak-hazard/*` pre-freeze RID-leak receipts are
  a different, disclosed superseded revision.
- The boundary's frozen attack probe is the committed `r95b_order.gd` **byte-for-byte** — the
  rows therefore inherit the boundary's 261-run matrix, and this seat's fresh 364-condition
  launches reproduce it independently.

---

## 4. Remaining risks / not measured

- **F1** (two echo-only rows) and **F2** (one tps-scoped row) are the two row-level items; no
  blocking defect. Both are cheap to fold when the block is next touched.
- **Window semantics are envelopes:** `periodx` confirms the period over `k(k−1)+3` ticks
  (F4 shows it holds over 2× that); a period that held for two cycles then diverged would
  still pass. `canon` is the only cell observed to t=64.
- **The k(k−1) mechanism remains [I]** (broadphase re-insertion rotation): the rows measure
  the observable, not the cause; non-rect / rotated / server-tier / multi-shape-body periods
  and ray/`cast_motion` multi-hit families remain unmeasured (boundary §11 unchanged).
- **Not measured here:** tps values other than 30/60/120; `--fixed-fps` values other than
  1/30/120; `physics/common/max_physics_steps_per_frame` overrides; non-Linux engine builds;
  the `procwait`-style process-frame harness (deliberately unauthored — a process-frame await
  cannot pin a tick phase).
- **Wall-time/tps coupling:** at tps ≤ 12 the slowest arm approaches the 8 s per-case bound
  (§2.8) — the same tps-conditional class as F2, and not removed by F2's fix.
- **Host-conditioned numbers:** every wall time above is from a host at foreign loadavg
  76–108 with 19–22 foreign `godot` processes; the byte-invariance results are the load-proof
  form, the absolute walls are not.
- **Blockers: none.**

**Advisory verdict: PASS-WITH-RESERVATIONS on the committed bytes `9cd47507`.** No blocking
defect: the commit is insertion-only and hygienic, both probes are byte-copies of the frozen
lane artifacts, all 52 signatures are reproduced verbatim and payload-unique across 472 sibling
receipts and 552 fresh launches, 51/52 rows are invariant under fixed-fps/threaded/load/tps
conditions, the k(k−1) law survives a window-doubling probe for all 9 cells, the 52 rows passed
in all four of this seat's battery runs (including the rep that flaked on pre-existing control
rows), and the floor gate is proven live by a dead-entry mutant. F1 (two echo-only rows) is a
disclosed row-shape weakness that should be folded or relabelled; F2 (one 60-tps-only row) is an
undisclosed conditioning item with a one-row blast radius. The canonical Rust runtime remains the
sole judge.

---

## 5. Evidence index

All under `corpus/live/r95-critic/`; `manifest.sha256` covers every artefact.

| artefact | path | notes |
|---|---|---|
| frozen committed tree (`git archive 9cd47507`) | `frozen/corpus/fixtures/` | `run_battery.py` `b93cbdaa…`, `dss_lattice.gd` `77ae4adb…`, `r95b_order.gd` `4f7e945e…` |
| row extraction / hygiene / claims | `scripts/{extract_rows,hygiene,verify_claims,census}.py` → `scripts/{rows.json,hygiene.json,claims.json,census.json}` | CASES[303..354], +163/−0, 52/52 census |
| arm runner + matrix driver | `scripts/run_arms.py`, `scripts/run_matrix.sh`, `scripts/run_mutants.sh`, `scripts/run_batteries.sh` | battery launch shape, 8 s bound, `classify_process` semantics |
| fresh / ff1 / ff30 / ff120 / tps30 / tps120 / thr / load receipts | `runs/{fresh,ff1,ff30,ff120,tps30,tps120,thr,load}/` | 552 launches, rc=0, 0 B stderr |
| analysis | `scripts/analyze.py` → `scripts/analysis.json` | per-row PASS-line uniqueness + cross-condition table |
| fixture mutants + records | `mutants/m{1a,1b,2,3,5}_*/`, `mutation.json` | order_core no-measure / mirror · point_cap cap0 · canon +collider · periodx window×2 |
| harness mutants + verdicts | `mutants/harness-{base,dead}/`, `battery-runs/harness-{base,dead}*/verdicts.json` | gate True / False, `dead_entry_count` 0 / 1 |
| full battery rep1 / rep2 | `battery-runs/full-rep{1,2}/` + `.log` | rep1 FAIL on 3 pre-existing control rows (52/52 r95 green), rep2 **PASS 366/366** |
| manifest | `manifest.sha256` | covers every artefact above (itself excluded) |

Reproduce: `python3 scripts/extract_rows.py && python3 scripts/hygiene.py &&
python3 scripts/census.py && python3 scripts/verify_claims.py && bash scripts/run_matrix.sh &&
bash scripts/run_mutants.sh && bash scripts/run_batteries.sh && python3 scripts/analyze.py
fresh ff1 ff30 ff120 tps30 tps120 thr load`.
