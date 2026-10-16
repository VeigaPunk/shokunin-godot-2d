# r94 critic — adversarial review of committed `c7228893` (19 `r94_*` particles rows, 314-row battery)

Seat `CRITIC` (g2d lane r94) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps default,
`RendererDummy`), Python 3.14.7.
Reviewed commit **`c7228893`** (`r94 author: 19 particles rows (314 total) — folded scout
probe (4-line diff: okb windows, floor); 314/314 x2`, parent `94377598`). `HEAD == c7228893`
at session start **and** at report time.
**No tracked write, no commit.** Seat-owned artifacts: `corpus/live/r94-critic/**`
(+ `manifest.sha256`, 2244 files) and this report.

**Committed tree only.** Every harness-derived check below is pinned to a frozen copy of
the committed tree extracted with `git archive c7228893 -- corpus/fixtures`
(`corpus/live/r94-critic/frozen/fixtures/`), whose three load-bearing files hash
`run_battery.py` = `2b1f4df5426a8da679c58c58057817b75f6fd879f9ffc8ab1045b03deae04238`,
`particles_lattice.gd` = `0701e813e50cdb50e05f0df0194d0baf94c1240f361e941949414dd5c52c00a9` (763 L),
`project.godot` = `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` — all
three byte-equal to `git show c7228893:<path>`. The **worktree** carries a concurrent r95
lane's uncommitted churn (` M corpus/fixtures/run_battery.py` +163, `?? dss_lattice.gd`,
`?? r95b_order.gd`); none of it was read as evidence and none of it was touched (§3).

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host (same as
every prior r89–r94 seat). The change under review is one new fixture file plus an
insertion-only harness block; no symbol-aware rename was needed, so hand analysis +
fresh-process execution is the fallback in use.

**probeParent disclosure.** Exactly **one** read-only `ufo-labrat` (agent `a198afb6`,
depth-2, licence exhausted) was dispatched with two bounded read-only clauses (fixture diff;
signature-vs-receipt).
Clause 2 (4-line fixture diff) returned **CONFIRMED**; Clause 1's *structural* half is
itself wrong (it searched only the scout `loadtest/` subtree and claimed no `rep3..6`
exist — the canonical tree has `105 = 3 arms ×3 + 16 arms ×6` receipts, §2.3), while the
substring property it did check (38 loadtest receipts, 19/19 arms) is corroborated by
this seat's larger census. No second dispatch; the labrat wrote nothing.

**Load regime.** The host was never idle: foreign `loadavg` 55–105 with 56 foreign `yes`
hogs (ppid 1537) for the whole session; this seat added **16** named hogs for exactly one
batch and **32** for one margin probe (both killed; `ps -C yes` shows 0 non-foreign
`yes` afterwards). Loadavg is recorded per batch in the receipt logs.

---

## 0. What I ran — 260 fresh arm launches + 2 full 314-row batteries + 2 harness-mutant batteries

| # | batch | scope | receipts |
|---|---|---|---|
| 1 | `fresh` | 19 r94 arms ×3, default 60 tps, frozen fixture | `runs/fresh/` (57) |
| 2 | `ff30` | 19 arms ×2, `--fixed-fps 30` (the fold's own condition) | `runs/ff30/` (38) |
| 3 | `ff120` | 19 arms ×2, `--fixed-fps 120` (control) | `runs/ff120/` (38) |
| 4 | `load` | 19 arms ×2, +16 seat hogs (loadavg 91.5→104.7) | `runs/load/` (38) |
| 5 | `tps30` | 19 arms ×2, project `physics_ticks_per_second=30` | `runs/tps30/` (38) |
| 6 | `tps120` | 19 arms ×1, project `physics_ticks_per_second=120` | `runs/tps120/` (19) |
| 7 | `hog32` | slowest 4 arms ×3–5, +32 seat hogs (wall margin) | `runs/hog32/` (14) |
| 8 | fixture mutants | 6 mutants (m1…m6) ×3 on the mutated arm | `runs/mutants-m{1..6}/` (18) |
| 9 | harness mutants | trimmed-CASES `base` + synthetic dead-entry `dead` | `battery-runs/harness-{base,dead}/` |
| 10 | **full battery rep1** | frozen committed tree, 314 rows | `battery-runs/full/20261016T064246905292Z/` |
| 11 | **full battery rep2** | frozen committed tree, 314 rows | `battery-runs/full/20261016T064739764761Z/` |

All 260 arm receipts: **rc=0, 0 B stderr, 0 timeouts**; the two batteries: **314/314 PASS**
each (rc=0 for the harness), `probe_error_clause_surface` meta PASS. The signature census
(§2.3) additionally re-scans 478 sibling receipts read-only.

---

## 1. Findings (ranked)

### F1 — MEDIUM · `r94_particles_cpu_contam` is **tautological**: its pinned tokens are structural counts, not measurements

The row's entire pinned signature is
`PASS particles_lattice cpu_contam ok=true n_never=2`. In the committed fixture both tokens
are pure list bookkeeping:

```gdscript
print("PASS particles_lattice cpu_contam",
    " ok=%s n_never=%d" % [str(out.size() == 2), out.size()],   # 763-L fixture, line 396
    " | " + " ".join(out))
```

`out` receives exactly two strings (one per `label in ["never1","never2"]`) **regardless of
whether either node fired**. The actual claim — *each add_pf≥1 never-emitter fires
`finished` on its first update* — lives only in the unpinned tail
(`never1[fin_delta=0 n=1] never2[fin_delta=0 n=1]`).

**Decisive mutant `m1_contam_addpf0`** (seat-built; `mutants/m1_contam_addpf0/mutation.json`):
the two never-nodes are created in frame 0 (`add_pf=0`, before the prior emitter), which the
boundary's own §8 rule predicts will stay **clean**. 3/3 receipts:

```
PASS particles_lattice cpu_contam ok=true n_never=2 | never1[fin_delta=-1 n=0] never2[fin_delta=-1 n=0]
```

The shipped signature still matches → **the row PASSes on bytes that falsify its claim**. This
is the r93-F2 class (pinned token producible by a dead path), now on the r94 block's only
positive control: if a future engine change made never-emitters never fire, `cpu_contam`
(and `cpu_never`, which pins a measured `ok`) would *both* pass and the add_pf rule would
lose its battery-level guard.

- Note the *law* is not in question: the boundary measured it 24/24 (§8), and the scout's
  cell is a stable single value (`uniq=1`). The defect is that the shipped row cannot fail.
- Cheap fix: fold the operands into the boolean, e.g.
  `ok = out.size() == 2 and out[0].contains("fin_delta=0 n=1") and out[1].contains("fin_delta=0 n=1")`
  (or pin the tail, which is byte-stable across all 6 boundary conditions).
- Contrast: `cpu_never` is **not** affected — its `ok`/`never_fired` are computed from the
  measurement, and mutant `m6_never_addpf1` (node added at `add_pf=1`) flips it to
  `ok=false never_fired=false n_fin=1` → FAIL. The pair's *negative* side discriminates; the
  positive side does not.

### F2 — LOW · the `cpu_request` `floor` fold is **inert in the shipped row** (the falsified `round` form would also pass)

The fold `int(round(0.5/spec))+1 → int(floor(0.5/spec))+1` (boundary §6) cannot change any
pinned byte, because the row pins only the integer ratios `spec ∈ {0.10, 0.05}`, where
`round` and `floor` agree. Measured, 3/3 each:

| mutant | emitted | row |
|---|---|---|
| `m4_request_round` (pre-fold form restored) | `step0.10[…expected=6…] step0.05[…expected=11…]` — byte-identical to the committed fixture | **PASS** (cannot discriminate) |
| `m5_request_noplus1` (`+1` removed) | `ok=false step010_ok=false step005_ok=false | …expected=5 / expected=10` | **FAIL** (binds the `+1`) |

So the row binds the closed form's `+1` lattice but not its `floor`-vs-`round` half; the
boundary's decisive steps (0.20→3, 0.30→2) are **not** in the fixture. The author's comment
discloses the inertness ("identical for the integer ratios pinned here"), so this is a
row-shape observation, not a false claim — but a future reader should not treat the fold as
evidence-bearing. Cheap strengthening: add `spec=0.20` (expect 3) to the arm.

### F3 — LOW (documentation) · the 60-tps conditioning risk is **broader than the three rows the author names**

Author §"Remaining risks": *"`cpu_lifetime`/`cpu_expl`/`cpu_speed_pre` `_okb` windows are
60-tps-only … a future project override would reject them."* The reason is right; the blast
radius is 10–11 rows. Measured on the committed fixture with only `physics_ticks_per_second`
changed in the launch project (no other edit):

| condition | rows that reject | examples (committed windows) |
|---|---|---|
| tps 30 (2 reps) | **10**: `cpu_lifetime`, `cpu_expl`, `cpu_speed_pre`, `cpu_stop`, `cpu_pause`, `cpu_restart`, `cpu_retrigger`, `cpu_lt_mid`, `cpu_speed_mid`, `cpu_oneshot_off` | `l025[delta=7]` vs `[12,18]`; `vis_parent=-33` vs `[1,7]`; `stop10[fin_after=5]` vs `[18,22]` |
| tps 120 (1 rep) | **11** = the same 10 + `cpu_amount_mid` | `l025[delta=30]` vs `[12,18]`; `fin_after_set=27` vs `[12,16]` |

Still green at both tps: the 3 pure rows and the 5 state-only rows (`cpu_never`,
`cpu_contam`, `cpu_oneshot_flag`, `cpu_request`, `gpu_headless`). Two distinct mechanisms:
(a) every `_okb` window is a tick count, so it scales with tps; (b) two arms' *observation
bounds* are tick counts too, so at 120 tps the natural end falls outside them
(`cpu_oneshot_off fin_after_off=-1`, `cpu_amount_mid … em_at_end=true`).
Additional measured consequence: at tps 30 the slowest row's wall time doubles —
`cpu_pause` = **5.99 s** (75 % of the harness's 8 s per-case bound) vs 3.9–4.1 s at default.
The battery itself never changes tps (the scratch project edits only `config/name`), and the
committed `project.godot` pins no tps, so today's risk is latent — but the disclosure should
name the measured 10/11-row set, not 3.

### F4 — INFO · wall-time margin: `cpu_pause` is the slowest r94 row; ~2× headroom, no flake

`cpu_pause` wall (harness launch shape): 3.95 s max fresh (loadavg 84–88), **4.12 s** max
with +16 hogs (loadavg 104.7), **3.95 s** max with +32 hogs (5 reps). The r92-F1 crash-row
class (wall straddling the 8 s bound under contention) has **no r94 analogue** in 260
receipts; the block adds ≈ 34 s of battery wall time (sum of the 19 arm max-walls, fresh
batch).

### F5 — INFO · the widened `[1,7]` window is still **discriminating** (the fold is not a blind widen)

Two seat mutants break the freeze mechanism itself, and both flip the row to FAIL even with
the widened window (3/3 each):

| mutant | operand | result |
|---|---|---|
| `m2_pause_parent_nofreeze` (`p.visible = true` at the hide point) | `vis_parent[fin_after_show=-25]` (the particle finished before the show) | `ok=false` → FAIL |
| `m3_pause_pm_nofreeze` (`PROCESS_MODE_DISABLED` never applied) | `pm_disabled[fin_after_enable=-25/-26]` | `ok=false` → FAIL |

The window's coverage is bounded by measurement: over the boundary's 6-condition matrix the
four pause operands take only `vis {4,5,6}`, `vis_parent {2,4,5}`, `pm_disabled {2,4,5}`,
`ts0 {18,19,20}` — i.e. `[1,7]` covers the whole observed range (min 2, max 6) with one tick
of margin. The rejected classes are measured for no-freeze (`−25`) and [I] for
restart-instead-of-resume (a fresh `L=0.25` cycle would land at `+15`, outside the window).
`[1,7]` is a deliberate frame-quantization envelope, not a dead window.

### F6 — INFO · the scout's mixed-revision receipt set (boundary §2) is disclosed and does not carry the rows

The author repeats the boundary's provenance defect and correctly declines to rest the rows
on the scout's 143 receipts. This seat's read-only census adds: the 3 pure cells' signatures
are byte-equal to their `rep1` lines, and all 19 signatures appear in 478 sibling receipts
(105 canonical + 38 loadtest + 323 boundary `r94_particles_*` + 12 `ab`) with **0 misses
except the 3 documented ff30 `cpu_pause` rejections** on the *pre-fold* revision — i.e. the
fold target is exactly the one known rejection and nothing else. The frozen-revision
evidence remains the boundary's 323-check matrix + this seat's 57 fresh receipts.

---

## 2. What survived (positive verifications)

1. **Commit hygiene.** `c7228893` = 3 files, **+1055 / −0**; `run_battery.py` **+91/−0**,
   `particles_lattice.gd` +763/−0, report +201/−0. CASES **288 → 307**; the 19 r94 tuples are
   contiguous at **CASES[284..302]**, immediately after `r93_anim_blend_interleaved` and ahead
   of the unchanged crash/descendant tail `[303..306]`; the 288 pre-existing tuples are
   **byte-identical in order** after removing the r94 rows (AST comparison). No duplicate case
   names; no cross-signature substring collisions; `expected_errors` has no `r94_*` key (the
   only r94 match is the gate name itself).
2. **Fixture provenance and the 4-line fold.** The committed fixture is a fold of the frozen
   scout probe (sha256 `e6a2e0f5…b930`, 741 L): a line-classified diff shows **exactly 4
   non-comment lines** — the three `_okb(…, 4, 7) → _okb(…, 1, 7)` constants in
   `_arm_cpu_pause` and `int(round(0.5/spec))+1 → int(floor(0.5/spec))+1` in
   `_arm_cpu_request` — plus 37 added / 15 removed comment lines. Independently confirmed by
   the labrat clause 2 (full-file comparison of both probes, all arm regions).
3. **Signature census (read-only, 478 receipts).** Every one of the 19 signatures is present
   verbatim in the scout canonical receipts (105: 3 pure arms ×3 + 16 timing arms ×6), the
   scout loadtest (38), the boundary matrix (323 = 57×5 + 38 `r94_particles_*` receipts) and
   the boundary `ab` pairs (12) — the only misses are the **3 ff30 `cpu_pause`** receipts
   of the *unfolded* probe. All 143 scout `.err` and all 759 boundary `.err` files are **0 B**.
   `ROWS_PREFIX` in `corpus/live/r94-scout/author-rows.py.txt` is
   **tuple-for-tuple equal (order included)** to the committed r94 CASES block.
4. **Fresh reproduction.** 57/57 arm receipts clean (rc=0, 0 B stderr, signature present,
   PASS-line starts with the signature). Signature shape confirmed: the 3 pure cells are
   **full-line** signatures (census 8785 B byte-equal), the 16 timing cells are boolean-block
   prefixes whose `| …` tails carry the unpinned ±1 modes.
5. **Full battery ×2, frozen committed tree, independent of the author's runs.** Both
   `verdicts.json`: **verdict PASS, 314/314 rows PASS**, r94 **19/19 PASS**,
   `r94_expected_errors_all_matched=True`, `probe_error_clause_surface` meta PASS, census
   `dead_entry_count=0`. The author's own two runs re-read: identical (314/314, gate True).
6. **The fold verified in the condition that motivated it** (the check the author did not
   run — both author batteries are default-tps only). On the **folded committed fixture**,
   `--fixed-fps 30`: **38/38 clean**, and the operands land exactly where the boundary
   predicted — `vis[4] vis_parent[2] pm_disabled[2] ts0[18]` → `ok=true` (under the scout's
   `[4,7]` window `vis_parent_ok`/`pm_disabled_ok` would both be `false`). `--fixed-fps 120`
   control: 38/38 clean. The ladder rows also survive ff30 (`l01=7, l025=12, l05=28, l1=58`,
   all inside their windows).
7. **Load invariance.** 38/38 clean with +16 seat hogs (loadavg 91.5→104.7), 0 B stderr; all
   pinned booleans identical to the fresh batch; tails move by ±1 exactly as designed
   (`cpu_lifetime l025 14→15`, `gpu_headless flip_after 1↔5` — both unpinned).
8. **Row discrimination mutants.** 6/6 behaved as predicted: `m2`/`m3` (freeze removed) FAIL;
   `m5` (+1 removed) FAIL; `m6` (add_pf=1) FAIL; `m1` PASS **only because it is vacuous**
   (F1); `m4` PASS **only because the fold is inert** (F2).
9. **Floor-gate liveness (r93-critic analogue).** Trimmed-CASES harness copies of the frozen
   tree: `base` (no r94 entries) → `r94_expected_errors_all_matched=True` (vacuous `all()`);
   `dead` (one synthetic never-matching `r94_particles_census` entry) → **`False`**, census
   `dead_in_run=true`/`dead_entry_count=1`. The gate is live and r94-scoped; it protects nothing
   today (0 entries). The two other False keys in both variants
   (`detached_control_row_still_passes`, `prior_meta_rows_stable_29_discriminations`) are
   **trimming artifacts of this seat's mutant**, not gate results — the trimmed CASES removed
   the rows those anchors reference.
10. **Insertion-only + placement.** No other CASES row, no other harness section, no
    `project.godot`, and no other fixture file changed in the commit.

---

## 3. Cross-seat / custody notes

- **The worktree is not the commit.** A concurrent r95 lane has ` M corpus/fixtures/run_battery.py`
  (+163 lines, r95 gate + block), `?? corpus/fixtures/dss_lattice.gd`,
  `?? corpus/fixtures/r95b_order.gd`, and ` M corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`.
  The pyc's embedded source mtime/size (03:41:30, 423661 B) match the **worktree** r95 revision,
  not this seat's frozen copy (390424 B) — the pyc write is the r95 lane's/another importer's,
  not this seat's. This seat executed only the frozen `c7228893` copy and its own
  `corpus/live/r94-critic/**` scripts; `git status` shows **no modification by this seat**.
- **Sibling r94 wave-B lanes** (reviewer/verifier/scribe/simplifier) were active in
  `corpus/live/` during this session; nothing of theirs was read as evidence for this review.
- The author's headline claims re-derived independently: 314/314 ×2 (this seat's two
  batteries), gate True, 19/19 signatures, 4-line fold, insertion-only diff, and the
  0-B-stderr corpus claim (this seat re-counted **all 143** scout `.err` and **all 759**
  boundary `.err` files at 0 B).

---

## 4. Remaining risks / not measured

- **F1** (tautological positive control) is the one row-level defect: it can be fixed
  row-side in the next touching round; until then the add_pf rule has no battery-level guard
  (the boundary's 24/24 matrix and the scout cell remain the evidence).
- **F2/F3** are row-shape/documentation items; no blocking defect.
- **Window semantics** are envelopes: a future engine change landing *inside* `[1,7]` with
  different semantics would pass (measured range is 2–6; the no-freeze/restart classes are
  rejected). Same for every `_okb` window in the block.
- **Not measured here**: the `fixed_fps ≤ 5` stall (not authored), continuous-emitter
  `amount` [U] (not authored), `seed`/per-particle observables, GPU readback (headless-inert
  by law), tps values other than 30/120, and `--fixed-fps` values other than 30/120.
- **Host-conditioned numbers**: every wall time and tail mode above is from a host at
  foreign loadavg 55–105; the boolean gates are the load-proof form (0 rejections at 16 hogs).
- **Blockers: none.**

**Advisory verdict: PASS-WITH-RESERVATIONS on the committed bytes `c7228893`.** No blocking
defect; F1 is a MEDIUM row-level vacuity that should be folded when the block is next
touched, F2/F3 are LOW documentation/row-shape items. The canonical Rust runtime remains the
sole judge.

---

## 5. Evidence index

All under `corpus/live/r94-critic/`; `manifest.sha256` covers every artefact (2244 files).

| artefact | path | notes |
|---|---|---|
| frozen committed tree (`git archive c7228893`) | `frozen/fixtures/` | `run_battery.py` `2b1f4df5…`, `particles_lattice.gd` `0701e813…`, `project.godot` `8de8b3af…` |
| fresh / ff30 / ff120 / load / tps30 / tps120 / hog32 receipts | `runs/{fresh,ff30,ff120,load,tps30,tps120,hog32}/` | 260 launches, rc=0, 0 B stderr |
| fixture mutants + mutation records | `mutants/m{1..6}_*/`, `mutation.json` | m1 contam add_pf=0 · m2/m3 freeze removed · m4 round · m5 no+1 · m6 never add_pf=1 |
| harness mutants (trimmed CASES) + logs | `mutants/harness-{base,dead}/`, `battery-runs/harness-{base,dead}.log` | gate True/False |
| harness-mutant verdicts | `battery-runs/harness-{base,dead}/2026*/verdicts.json` | `discriminations.r94_expected_errors_all_matched` |
| **full battery rep1 / rep2** | `battery-runs/full/20261016T064246905292Z/`, `battery-runs/full/20261016T064739764761Z/`, `battery-runs/full/rep{1,2}.log` | 314/314 PASS, gate True |
| signature census (478 sibling receipts) | `scripts/signature_census.{txt,json}` | 3 known ff30 `cpu_pause` misses only |
| arm verifier + batch JSONs | `scripts/verify_arms.py`, `scripts/verify_*.json` | rc/stderr/signature/prefix/wall per receipt |
| mutant builders | `scripts/build_mutants.py`, `scripts/build_harness_mutants.py` | replayable |
| drivers | `scripts/run_arms.sh`, `scripts/run_one.sh`, `scripts/run_hog32.sh` | `timeout -s KILL 25` |
| tps projects | `proj/`, `proj_tps30/`, `proj_tps120/` | launch shape = harness (`--headless --path … --script res://particles_lattice.gd -- --arm=…`) |
| load logs | `runs/{load,hog32}.log`, batch headers in each receipt dir | loadavg per batch |

Replay (from the repo root): `python3 corpus/live/r94-critic/scripts/build_mutants.py &&
python3 corpus/live/r94-critic/scripts/build_harness_mutants.py &&
bash corpus/live/r94-critic/scripts/run_arms.sh fresh corpus/live/r94-critic/proj 3 &&
python3 corpus/live/r94-critic/scripts/verify_arms.py fresh` — expect 57/57 rc0/stderr0/sig.
