# r80 VERIFIER — independent battery replay + forgery probes

Seat `VERIFIER` (LEAF) | lane `g2d` | round 80 | host **devin**.
Runtime Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python
3.14.7, 32 cores, Linux. HEAD `d9320dd` (*r79 report-last: adjudicator
ADMIT-corr + ledger*) + r80 dirty landing, verified live before probing:
` M corpus/fixtures/run_battery.py` sha256 `66bfe3e2…` (matches the
baseline-documented post-landing digest), `?? corpus/fixtures/phys2d_motion.gd`
sha256 `f622b89e…`.

Scope per dispatch: (1) two full dirty-tree battery replays, (2) rows-1–111
verdict/signature tuple identity vs `corpus/live/r80-baseline/freeze/
godot-tuples-rep1.txt`, (3) three forgery probes on the 28 new
`phys2d_motion_*` rows, (4) floor-verification of the 2 new `expected_errors`
entries. All mutations on scratch copies under `corpus/live/r80-verify/`;
**no tracked edits** (`git status` delta vs the landing: zero — only the
untracked `corpus/live/r80-verify/**` scratch was added).

| check | result |
|---|---|
| (1) rep1 battery | **139/139 PASS** (rc=0) |
| (1) rep2 battery | **139/139 PASS** (rc=0) |
| (2) prior 111 rows vs freeze | **110 identical tuples ×2 reps**; 1 explained delta (§2) — zero unexplained drift |
| (3a) flipped signature token | row FAIL detected, battery FAIL |
| (3b) deleted new CASES row | **138/138 PASS**, zero side-effects |
| (3c) neutered arm discriminating line | row FAIL detected, battery FAIL |
| (4) 2 expected_errors entries | **floor-verified** — every declared line matched real emitted ERRORs, `dead_entry_count=0` |

---

## 1. Full battery ×2 on the dirty tree — **139/139 both reps**

`python3 corpus/fixtures/run_battery.py --runs <abs>` from repo root, dirty
tree as landed. Receipts:

| rep | run dir | verdicts.json sha256 | rows | PASS | FAIL |
|---|---|---|---|---|---|
| rep1 | `corpus/live/r80-verify/runs1/20261015T060158785402Z/` | `3fad5028…` | 139 | 139 | 0 |
| rep2 | `corpus/live/r80-verify/runs2/20261015T060158829168Z/` | `f4fc0cc3…` | 139 | 139 | 0 |

All 28 `phys2d_motion_*` rows present and PASS in both reps. Zero `^FAIL`
lines in either stdout log; both stderr logs empty; the documented SDL
`joypad_sdl.cpp:141` flake did **not** occur in any of this seat's five runs.
rep1↔rep2 are tuple-identical across all 139 rows (sha-compare of the two
emitted tuple sets: `godot-tuples-rep{1,2}.txt`, diff empty) — the 28 new
rows are deterministic on this host, not just passing.

## 2. Prior-row identity vs the frozen baseline — **PASS (110 identical + 1 explained)**

Compared **by case name** (meta rows move from positions 105–111 to 133–139
under the r80 insertion; positional diff would be spurious). Tooling:
`corpus/live/r80-baseline/tuples.py` emits the same `(case, verdict,
sha256 of stable verdict tuple)` lines as the freeze; `corpus/live/
r80-verify/diff_freeze.py` (sha `3241c4fd…`) set-diffs them.

Both reps, identical result: **110/111 frozen cases carry byte-identical
verdict tuples**; 0 missing; frozen relative order preserved; `new_only`
= exactly the 28 `phys2d_motion_*` cases.

The single tuple-sha difference is **`probe_error_clause_surface`** (meta row;
verdict PASS in freeze and both my reps). Field-level diff vs the baseline's
`runs1` verdicts shows the delta is the r80 landing's *own footprint* inside
that row's self-census, nothing else:

- `census.rows_with_expected_errors`: 43 → 45 — the two new allowlisted rows
  (`phys2d_motion_mac_maxcol`, `phys2d_motion_dss_wrongarg`) are now censused;
  all 43 shared census rows byte-identical.
- `census.scan_clause_census["ERROR:_per_line_lines"]`: 53 → 61 — +8 ERROR
  lines emitted by the two new rows' outputs (1 callv refusal + 7
  wrong-arg/null-query refusals; itemized in §4).
- Remaining raw-JSON diffs (`arms`, `seam_split_run` pids/elapsed) are keys
  the tuple normalizer already excludes (`META_ARM_RECORD_KEYS`,
  `META_VOLATILE_KEY`) — not part of the compared tuple.

That is deterministic, explained drift caused by the new rows themselves —
rep1 and rep2 produce the *same* new sha `27b33ab9…`. Per the dispatch's
flake rule: no `expected_errors=[]` row flipped; no SDL joypad line appeared;
the one mismatch needed no re-run because it is structural (census counters),
confirmed identical across two independent reps.

## 3. Forgery probes on the 28 new rows

Scratch copies of the entire `corpus/fixtures/` dir (`fx-a`, `fx-b`, `fx-c`),
each self-contained (`HERE`-relative scratch staging), run with
`--runs corpus/live/r80-verify/runs-probe-<x>`.

| probe | mutation | verdicts.json | result |
|---|---|---|---|
| (a) signature-token flip | `fx-a/run_battery.py` row `phys2d_motion_btm_hit`: expected `depth=0.2813`→`depth=0.9999` | `runs-probe-a/20261015T060410936550Z/` sha `c64a4756…` | **battery FAIL** (rc=1), 138/139; only `phys2d_motion_btm_hit` FAIL (exit 0, signature absent — emitted line still shows real `depth=0.2813`) |
| (b) CASES-row removal | `fx-b/run_battery.py`: deleted `phys2d_motion_cont_persist` row | `runs-probe-b/20261015T060410980907Z/` sha `9da6b68f…` | **138/138 PASS** (rc=0); 27 `phys2d_motion_*` rows; every remaining row unaffected |
| (c) neutered discriminating line | `fx-c/phys2d_motion.gd` `_arm_btm_hit`: test motion `Vector2(200,0)`→`Vector2(50,0)` (wall face x=98 unreachable) | `runs-probe-c/20261015T060411030702Z/` sha `87636c9d…` | **battery FAIL** (rc=1), 138/139; only `phys2d_motion_btm_hit` FAIL — emitted `hit=false travel=(50.0000,0.0000)` vs pinned `hit=true travel=(87.5000,…)` |

The pinned signatures are load-bearing in both directions: a forged harness
expectation fails (a), and a real behavior change in the fixture fails (c) —
the rows are not decorative.

## 4. `expected_errors` floor verification — **PASS**

Two new allowlist entries, both discharged against real emitted lines (the
row outputs in rep1 `verdicts.json`, cross-checked by the in-band
`probe_error_clause_surface.census` — self-validated by the real classifier):

| case | declared entry | emitted count | `dead_in_run` |
|---|---|---|---|
| `phys2d_motion_mac_maxcol` | `ERROR: Error calling method from 'callv': 'CharacterBody2D::move_and_collide': Method expected 4 argument(s), but called with 5.` | 1 | false |
| `phys2d_motion_dss_wrongarg` | `ERROR: Required object "rp_shape_query" is null.` | **5** (4 wrong-class calls + null `intersect_shape`) | false |
|  | `ERROR: Required object "rp_ray_query" is null.` | 1 | false |
|  | `ERROR: Required object "rp_point_query" is null.` | 1 | false |

For both rows the census records `bare_classification_rejects=true` (the
emitted ERROR lines would FAIL without the allowlist) and
`allowlisted_classification_passes=true` — i.e., the entries are exactly
floor-and-ceiling: they match real lines and are necessary. Battery-wide
`dead_entry_count=0`.

## Evidence index

- Reps: `corpus/live/r80-verify/runs{1,2}/<stamp>/verdicts.json`,
  `rep{1,2}.stdout` (140 `^PASS` lines each = 139 rows + battery banner),
  `rep{1,2}.stderr` (empty), `godot-tuples-rep{1,2}.txt`
  (sha `0c2a77b3…` / `5b903825…`).
- Probes: `corpus/live/r80-verify/fx-{a,b,c}/` (mutated copies),
  `runs-probe-{a,b,c}/<stamp>/verdicts.json`, `probe-{a,b,c}.stdout`.
- Compare tooling: `corpus/live/r80-verify/diff_freeze.py`; baseline freeze
  `corpus/live/r80-baseline/freeze/godot-tuples-rep1.txt` (111 rows,
  verdict=PASS).

## Risks / blockers

- None blocking. Residual: tuple comparison inherits the baseline
  normalizer's declared volatile-key exclusions (pids/paths/elapsed) —
  appropriate for host bookkeeping, and the two reps agreeing sha-identical
  on all 139 rows (including the censused meta row) bounds nondeterminism
  independently of the normalizer.
- The `phys2d_expected_errors_all_matched` discrimination inside
  `probe_error_clause_surface` gates only `phys2d_events_*` (r79 rows); the
  two new `phys2d_motion_*` allowlist rows are floor-verified instead by the
  universal `census_bare_classifier_consistent` gate plus this report's §4
  census read — adequate for r80, but a `phys2d_motion_*`-prefixed dead entry
  in a future round would ride on the universal gate alone.
