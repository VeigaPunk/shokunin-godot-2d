# r103-PLANNER — lattice map for C1/C2/C3 (planner seat)

Date: 2026-10-18. Repo `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
branch `main`. Host: `uptime` = `18:50:02 up 1 day, 18:50, 1 user, load average: 3.20, 3.63, 4.25`.
Round 102 closed at 6e3e87f7 (work commit adf1e693 per r102 adjudicator; role: read-only planner).

Plan (5 lines):
1. Read SCORECARD tail + LOG tail + r102/r101 adjudicator (done — claims, routed items, laws extracted).
2. Map the harness surfaces C1/C2/C3 touch: CASES registry shape, record fields, meta gates, export rows (read-only).
3. Produce C1 row-name + registration-order spec (export_div family) with insertion point and naming law.
4. Produce C2 meta-gate design constraints (over stored per-row stdout records; classification-invariant) + fail-closed shape.
5. Saturation bookkeeping: stagnation count, saturation line status, and the owning files for each claim.

## Status: COMPLETE (see sections below)

---

# PLANNER attempt 3 (completion seat, 2026-10-18T23:55Z) — recon of the PARTIAL state

Plan (5 lines, first action):
1. `uptime` + full `find reports/round-103` census → classify all ~62 files as skeleton/real (done above).
2. Verify the REAL artifacts: 3 fold patches (`git apply --check`), `export_div_s02.gd` (structural read), w4-census.json (schema+counts), w5 patch/splice (anchors vs HEAD), mut02/mut05/mut07 (importable).
3. Lattice per claim C1/C2/C3: exists vs missing per sub-item, owner shard, blocking dependency.
4. Final C1 CASES row names (s01..s05) + registration order + evidence rule per row (echo vs redirect) from w5 splice + s02 fixture.
5. Integration order for the orchestrator (dependency graph: patches → C1 rows → C2 gate → C3 fold apply → receipts).

## Attempt-3 recon results

Snapshot time: `2026-10-18T23:56:05Z` (20:56 local, UTC-3). `uptime` = `1 day, 20:55, load average: 1.84, 1.77, 1.63` (recorded at 23:55:26Z). HEAD `6e3e87f7`, branch `main`. `git status --porcelain` = `?? corpus/fixtures/export_div_s02.gd`, `?? reports/round-102/mutations/__pycache__/`, `?? reports/round-103/`. 61 top-level `r103-*.md` + 27 mutation files. **Concurrent writers active during this recon**: `r103-E0-spec.md`, `r103-E4.md`, `r103-G4-MATRIX.md`, `r103-S1.md` resumption, `r103-ver10/11/13.md` all appeared or grew at ~20:55–20:56 local [obs]. Every count below is therefore a *snapshot*, not a frozen census.

### Headline facts (all [obs] unless labeled)

1. **`export_div` occurs 0 times in `corpus/fixtures/run_battery.py`** (`grep -c` → 0, rc=1). The entire C1 CASES registration is missing.
2. Fixture inventory: **only `corpus/fixtures/export_div_s02.gd` exists** (457 lines, untracked, mtime 18:53); no `export_div.gd`, no `_s01/_s03/_s04/_s05` (`ls corpus/fixtures/export_div*`).
3. The 3 fold patches apply CLEAN (`git apply --check` each) and `--numstat` gives: r97_scene_marker.gd **0 added / 4 deleted**; r99b_modes.gd **0 / 1**; r100b_seq.gd **1 added / 6 deleted** (5 net deletions, 1 replacement line `match arm:`→`match a:`).
4. `w5_export_div.patch` (38 lines) applies CLEAN but is **gate-only**: it adds `"export_div_"` to `cases_integrity`'s prefix tuple + two floor clauses. It registers **no** CASES rows. The splice script's own docstring: "H1/H2 must land in the SAME splice as the C1 CASES rows. A gate-only splice turns the next battery red (self-test cells M/P)". → **w5 patch is unlandable until the rows exist.**
5. CASES tuple arity = **5** `(name, script, flags, expected_exit, signature)`; `expected_errors` is attached separately by a per-case dict (run_battery.py:2035-2038, `expected_errors = ()` then the `if passed is None:` dict), so new rows need no 6th tuple element; a row with no entries is "vacuous-but-honest" under the r-chained dead-entry gates (w5's design).
6. w4 census substantive: run1/run2 each 554 rows, 554 PASS/0 FAIL, 538 rows with output, 48 zero-PASS, **19 multi-PASS rows / 566 PASS-lines**; per-case PASS-line lists byte-identical across the two r102 runs for all 19 (w4 shard §cross-run invariants); 28 drifted single-PASS rows (timing/pid) — gate baseline must be per-record-shape, not cross-run bytes.
7. `export_div_s02.gd` is self-contained and row-shaped: 2 arms → 2 rows; header comment pins the row names verbatim: arm=iso → **`export_div_s02_user_iso`**, arm=xdg → **`export_div_s02_xdg_override`**; PASS line shape `PASS export_div s02 arm=<arm> <fields>` with host paths confined to `EXPORT_DIV_DIAG` lines + unpinned trailing `proj=` (r102 export evidence rule).
8. Worktrees present at snapshot (`git worktree list`): main + 3 locked `wt-r98/r99/r100` + `/var/tmp/r102-S1` + `/var/tmp/r103-S1/repo` + `/var/tmp/r103-S2/wt` + `/var/tmp/r103-S3` + `/var/tmp/r103-ver4/wt`. Owners must `git worktree remove` the r103 ones at close (hard rule 5).

### COMPLETION LATTICE (per claim → sub-item → state → owner → blocker)

Legend: **DONE** = artifact on disk + verified by this seat; **PART** = artifact/evidence partial; **PLAN** = shard plan only, no artifact; **MISS** = nothing.

#### C1 coverage (export_div family)

| # | sub-item | state | owner | evidence / blocker |
|---|---|---|---|---|
| C1-a | s02 fixture `export_div_s02.gd` | **DONE** (recon-validated structurally; 457 lines, 2 arms, fail-closed `_fail` on missing template/root, `timeout -k 1 5` child bound, XDG isolation sentinels) | E2 | file untracked; *runtime* validation = E2-VALIDATE re-seated, in flight |
| C1-b | s01 fixture `export_div_s01.gd` (preset vs `--export-pack`) | **MISS** | E1 / W9 | E1 shard still plan-only at snapshot; W9 independent repro plan-only. Crit1 attack-class (a) waits |
| C1-c | s03 fixture `export_div_s03.gd` (multi-preset sequential) | **MISS** | E3 / M3 | E3 plan-only; M3 v2 plan (20:55:41) in flight |
| C1-d | s04 fixture `export_div_s04.gd` (PCK extended header) | **MISS** | E4 | E4 shard re-entered IN PROGRESS at ~20:55 (appeared during recon); `r103-E3_packparse.py` + `r103-crit1_pck.py` are the only header tooling on disk |
| C1-e | s05 fixture `export_div_s05.gd` (editor-settings override) | **MISS** | E5 / V3 | both plan-only; V3 grinding ground truth |
| C1-f | CASES rows registered in run_battery.py | **MISS** | orchestrator | `grep -c export_div` = 0. Row tuples spec = E0-spec (in flight, re-seated) |
| C1-g | expected_errors entries for the family | n/a by design | W5 | nested export output redirected to logs (r102 rule) → no entries needed; w5 gate stays vacuous-but-honest + a future entry cannot die silently |
| C1-h | `cases_integrity` prefix + floor gates (w5) | **PART** (patch text ready, verified apply-clean this seat; **must not land alone**) | W5 / orchestrator | atomicity constraint per w5 splice docstring; `--min-rows N` freeze blocked on C1-f row count |
| C1-i | count-floor N freeze | **MISS** | W5/ver11 | N unknown until fixtures land. If s02=2 rows and s01/s03/s04/s05 = 1 row each → N=6 (INFERENCE; E0-spec owns the measured answer) |
| C1-j | adversary: mut02 user:// spoof | **PART** (script DONE, 405 lines, py_compile-clean; not yet run) | M2 | needs ~60 s export + Godot; scratch `/var/tmp/r103-mut2` |
| C1-k | adversary: mut3 cross-contamination, mut4 header echo | **PLAN** | M3/M4 | mut3 v2 in flight; mut4 plan-only |

#### C2 depth (receipt-shape meta-gate)

| # | sub-item | state | owner | evidence / blocker |
|---|---|---|---|---|
| C2-a | G0 spec | **PLAN** (re-seated attempt 3 at 20:55, "derive diag regex empirically") | G0 | in flight during recon |
| C2-b | G1 implementation diff (META gate over stored verdict records ONLY) | **MISS** (no patch under `mutations/`) | G1 / W10-ver13 | G1 shard plan-only; `r103-ver13.md` (W10) drafting a "mechanical gate insertion diff vs HEAD" — the only live producer |
| C2-c | allowlist baseline (19 multi-PASS rows) | **DONE** | W4 | `r103-w4-census.json` (70653 B, sha256 `3d75774e…`) + `r103-w4-verify.py`; w4 shard has the cross-run byte-stability proof |
| C2-d | fail-closed material (16 `output=None` + 48 zero-PASS rows) | **DONE** | W4 | same census; exact case list in w4 shard §fail-closed |
| C2-e | G2 adversary proofs | **PLAN** | G2 | G2 shard plan-only; mut05 evasion corpus exists but needs C2-b |
| C2-f | G4 replay matrix | **IN FLIGHT** | G4-MATRIX | shard appeared ~20:55 with matrix plan; "locate G1 gate implementation" → blocked on C2-b |
| C2-g | G3 / W2 diag-regex account | **PLAN** | G3 / W2 | both plan-only (G3: print-statement census; W2: regex + false-positive table) |
| C2-h | W7 mut09 replay (mut08 harness) | **PLAN** | M8/W7 | plan-only; needs C2-b + `reports/round-102` mut09 attack JSON |
| C2-i | mut05 evasion harness | **PART** (script DONE, 204 lines, py_compile-clean; `--emit-only` runnable today) | M5 | `--gate PATH` blocked on C2-b |

#### C3 calibration

| # | sub-item | state | owner | evidence / blocker |
|---|---|---|---|---|
| C3-a | 3 fold patches apply clean | **DONE** (this seat: `git apply --check` ×3 CLEAN at 23:55Z; `--numstat` byte-verified) | S0 | `mutations/r103-S0-E{1,2,3}-*.patch` (+`r103-S0-build_candidates.py`) |
| C3-b | S1 r99 F2 byte-identity | **PART** (36-receipt sweep + pre/post trees on `/var/tmp/r103-S1/`; frozen r102 receipts extracted) | S1 | re-entered 23:55Z: needs `r103-S1-compare.py` run + the one `startphase one_uniq` 2-vs-1 field divergence adjudicated |
| C3-c | S2 r100 SP2/SP3 byte-identity | **PART** (patch done; scratch `/var/tmp/r103-S2/wt` exists) | S2 | shard plan-only; sweep not evidenced |
| C3-d | S3 r97 F6 byte-identity | **PLAN** (patch done; re-seated at 23:55Z) | S3 | sweep not evidenced |
| C3-e | V4/V5/V6 independent verification | **PLAN** (V4 recon done; `/var/tmp/r103-ver4/wt` exists) | V4/5/6 | all three plan/recon only |
| C3-f | discrimination evidence (folds don't kill teeth) | **PLAN** | crit3 / M6 | both plan-only |
| C3-g | S4 probe reject-arm print fix | **MISS** (no diff anywhere) | S4 | S4 shard plan-only; W6 blast-radius plan-only; V7 verify plan-only |
| C3-h | W3 line-delta accounting | **PLAN** | W3 | arithmetic now computable from C3-a numstats (see below) |

### C3 line-delta numbers (this seat, from `git apply --numstat`, [obs])

- r97 F6 (`r97_scene_marker.gd` 7→3 lines): **−4**.
- r99 F2 (`r99b_modes.gd` 453→452): **−1**.
- r100 SP2/SP3 (`r100b_seq.gd` 790→785): **−6 deleted, +1 replacement** = **5 net lines removed**.
- Total: **10 net lines removed** across 3 fixtures (matches the r103 claim wording "−N lines").

### FINAL C1 CASES row names (as deliverable to the orchestrator)

Measured/fixture-authored (authoritative):
- `export_div_s02_user_iso` — `export_div_s02.gd`, flags `["--arm=iso"]`, exit 0, pin prefix `PASS export_div s02 arm=iso`.
- `export_div_s02_xdg_override` — `export_div_s02.gd`, flags `["--arm=xdg"]`, exit 0, pin prefix `PASS export_div s02 arm=xdg`.

PROPOSED (fixture not landed; names set by this PLANNER so E-seats converge; each MUST be re-confirmed against the landed fixture's own receipt before splice):
- `export_div_s01_preset_vs_pack` — `export_div_s01.gd` (E1).
- `export_div_s03_multi_preset` — `export_div_s03.gd` (E3).
- `export_div_s04_pck_header` — `export_div_s04.gd` (E4).
- `export_div_s05_editor_settings` — `export_div_s05.gd` (E5).
- Registration order: s01, s02_iso, s02_xdg, s03, s04, s05 — contiguous block inserted **ahead of the crash/descendant tail** (the r63/r101 convention, run_battery.py:749 comment) and immediately after the r102 `export_launch_*` block.
- If any landed fixture ships 2 arms → 2 rows, N grows; the count floor `--min-rows N` must be frozen from the AST count **after** the splice, not before.

### INTEGRATION ORDER (dependency graph for the orchestrator)

1. **Fixtures first** (parallel, per-seat): land `export_div_s01/s03/s04/s05.gd` (E1/E3/E4/E5) + finish s02 runtime validation (E2-VALIDATE). Each fixture's own receipt freezes its row tuple.
2. **Row-tuple freeze**: E0-spec emits the measured tuples; PLANNER propsals above reconciled against fixture receipts.
3. **Atomic CASES + w5 splice** (single orchestrator edit to `run_battery.py`): CASES rows (step 2) + w5 H1 (`cases_integrity` tuple) + w5 H2 (two floor clauses) with `--min-rows N` **in the same edit**; py_compile-gated; `--check` must print POST-SPLICE. Never land w5 alone.
4. **C2 gate landing** (separate edit, after or with step 3): G0 spec → W10-ver13/G1 mechanical diff → land; then mut05 `--gate`, G2 attacks, G4 replay, mut08/mut09 replay, G3/W2 regex account.
5. **C3 folds**: apply the 3 patches (byte-identity sweeps S1/S2/S3 + V4/V5/V6 re-verification) — independent of steps 3–4 (different files: r97_scene_marker.gd, r99b_modes.gd, r100b_seq.gd).
6. **S4 print-semantics fix** (run_battery.py again — serialize with steps 3–4 to avoid splice collisions; W6 blast-radius + V7 verify).
7. **Battery ×2** by orchestrator on the fully spliced tree (never by a seat), receipts to `corpus/live/runs/…`; then adjudicator.

Collision note [inf]: steps 3, 4, 6 all edit `run_battery.py`; they must be applied sequentially in one session, each `--check`-gated, with the post-splice sha recorded between steps.

### Residual / open questions for the orchestrator

- Row count N (C1-i) is the one number the w5 gate needs and nobody has frozen yet (E0-spec in flight).
- C2-b (G1 diff) is the single widest blocker: 5 other sub-items (C2-e/f/h/i + landing) are stacked behind it.
- 5 r103 worktrees under `/var/tmp` must be removed at close by their owners.
- S1's `startphase one_uniq` 2-vs-1 divergence is an open adjudication (fold-effect vs run-noise) — do not let it be silently dropped.
- No shared files touched by this seat; no battery run; no Godot runs (recon was filesystem + git only).

### FRESHNESS DELTA (snapshot 2, `2026-10-18T23:57:25Z` / 20:57 local)

The wave-3 re-seat is landing artifacts *while this recon runs*; corrections to the lattice above:

1. **`export_div_s02.gd` was rewritten mid-recon** (18:53: 17422 B / 457 L → 20:57: **17975 B / 468 L**, sha256 `c08792c1c208d47a8af66c669e7296eb6a1d94fe3d20872aeb73d4d6620a4898`). Row names and arm structure unchanged [obs: grep hits lines 9/18 header comments, `const VARIANT := "div_s02"` line 57, PASS/FAIL prints 115/121/124]. E2-VALIDATE is actively editing→validating; **any earlier s02 hash in other shards is stale**.
2. **C1-c / C1-d now have a live author**: seat V2 (attempt-4) took over authoring `export_div_s03.gd` + `export_div_s04.gd` after E3/E4 starved with zero fixtures.
3. **C3-g patch text now exists**: `reports/round-103/mutations/r103-V7-reject-arm-prints.patch` (46 lines, sha256 `6c75e617e75060d710dee07210266ace577e93c9c5755ee5981a5b240bf695fe`), this seat verified `git apply --check` CLEAN, `--numstat` = **10 added / 6 deleted** in run_battery.py (hunks at 4630 / 4697 → live sites confirmed at run_battery.py:4633/4647 and 4700/4720). Semantics: each probe loop gains `designed_inner`; verdict becomes `inner is designed_inner`; print gains `designed=<bool>` suffix. **Divergence for the orchestrator**: S4 rev2's plan wanted a `REJECT-ARM (designed)` verb — V7's patch instead keeps `PASS`/`FAIL` and annotates `designed=`. Pick one text before landing (do not land both).
4. **C2-g G3 half has an artifact**: `reports/round-103/mutations/r103-g3-diag-census.py` (sha256 `446e73089219787a0aa5b28ccdae16e58502a29cb0b1da14b2098bdfc9a339e3`).
5. **C2 converging producers**: crit2 re-seat is building a *reference* META gate as its attack target (`mutations/r103-crit2_meta_gate.py`, in flight); G2's `mut09_replay.py` was imported at 20:57:47 (in flight). C2-b (the official G1 landing diff) is still the only MISS, but multiple independent gate texts are converging — the orchestrator should pick ONE as official.
6. **S1/S2/S3/V10 evidence runs started**: `r103-S1-compare.py` + `r103-S2-harness.py` updated, `r103_s3_r97_f6_identity.py`, `r103-ver10-bytes.py`, `r103-w4-recount.py` all landed at 20:57.
7. **This seat's verifications** [obs]: `w5_export_div_gate_splice.py --check` on the live file → `sha256=40440356f0bf04481f518adc332d1ebb7ba79213878a9f3836421a512828a5c4`, `anchor_gate=1 anchor_tuple=1`, **PRE-SPLICE** (rc=2; matches the script's `PINNED_SHA` constant exactly → the w5 patch is still anchor-valid). CASES via AST = **536 unique, arity set [5], 0 `export_div*` rows**. `py_compile` OK for mut02.py, mut05_gate_evasion.py, mut07.py, r103-w4-verify.py.
8. **Hygiene**: `reports/round-103/mutations/__pycache__/` (5 `.pyc`, 20:56:56–20:57:47, incl. one from another seat's import) is untracked scratch inside the round dir — **exclude from any commit / remove at close** alongside the r102 `__pycache__` already flagged by `git status`.
