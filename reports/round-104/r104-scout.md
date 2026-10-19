# r104 SCOUT shard

Host: `uptime` at open = `22:29:30 up 1 day, 22:29, 1 user, load average: 3.06, 1.89, 1.77`.
Repo HEAD at open = `eff29d1d` (`round-103 record: LOG + SCORECARD verdicts (work 752cdc32)`).
Branch `main`. Godot `4.7.2.stable.arch_linux.ed1daf0bf`. No commit, no shared-file edit,
`run_battery.py` never executed. Scratch: `/var/tmp/r104-scout/`. No device-census tokens pinned.

Plan (5 lines):
1. CASES count at HEAD (expect 552) — count via AST over `corpus/fixtures/run_battery.py` (read-only).
2. Census of routed-but-unlanded items across r101–r103 adjudicators, with exact pointers.
3. Orphaned-fixtures inventory state (fixture files with no CASES row / no reference).
4. Every finding carries exact command + output bytes; label observation / inference / unknown.
5. Shard only; diffs as content, orchestrator applies.

Labels: **[O]** observation, **[I]** inference, **[U]** unknown.

STATUS: **COMPLETE**. All three assigned asks measured (CASES=552, routed census, orphan inventory).
No worktree created by this seat, so nothing to `git worktree remove`. Scratch kept at
`/var/tmp/r104-scout/parse/` (the 11 archived companions + a minimal `project.godot`).

---

## S1 — CASES count at HEAD = **552** (expectation met)  [O]

Command:
`python3 -c "ast.parse(corpus/fixtures/run_battery.py); literal_eval(CASES)"`

```
CASES rows: 552
end line of CASES assign: 1759
tuple arity set: [5]
unique names: 552
dups: []
```

Reconciliation vs the r103 close (`LOG.md:1294`: "CASES 536->552"): 536 + 16 `export_div_*` = 552 ✓.

Prefix census (row names, top 14): `phys2d` 79, `r96b` 47, `export` 38, `r95b` 34, `camera` 25,
`input` 24, `r93` 23, `slider` 22, `r94` 19, `geo2d` 18, `r99` 18, `dss` 17, `r98b` 16, `r98` 15.

**Receipt reconciliation (latest stored run).** `corpus/live/runs/20261019T005558434174Z/verdicts.json`
(sha256 `9f66675ef24b94291b9200738e45733c835f0760d0270e2378db9ea9950ff282`, 1 464 781 B):

```
rows: 571 CASES: 552 non-CASES rows: 19
CASES rows missing from receipt: []            # ← 0 missing
verdicts: {'PASS': 571}                        # ← 0 FAIL
non-CASES rows: probe_* (17) + mutant_* (2)
```

**[I]** The 19 non-CASES rows are probe/mutant artifacts, not battery rows — consistent with the
r103 F5 fold (`run_battery.py:1888-1890`: records whose case is not a CASES row are probe artifacts,
skipped by the shape gate). **[O]** 552 + 19 = 571 exactly.

---

## S2 — PASS-line grammar census (feeds C2a)  [O]

Command: replay `verdicts.json` with `^PASS ` vs `^PASS` and `^(PASS\t|\t+PASS)`.

```
20261019T004115354212Z rows=571 pass_space=582 pass_any=582 delta=0
20261019T005558434174Z rows=571 pass_space=582 pass_any=582 delta=0
rows containing tab-PASS shaped lines: 0 {}
```

**[O]** Over both latest stored runs: 582 PASS-space lines, 582 PASS-any lines, **delta 0**,
**0** rows carrying a tab-shaped PASS line. So the r103 "tab-PASS is grammar-invisible"
class is **not currently occupied by any real row** — it is a *latent* grammar hole, not an
observed evasion. (Cross-check: `mut05_gate_evasion.py` s4a/s4d construct `"\tPASS forged=true"`
and `"PASS\tforged=true"` synthetically.)

**Grammar-hole evidence at HEAD** (the exact sites C2a must touch — all four use a literal
space, so a tab-separated PASS line is invisible to every one):

| line | site | selector |
|---|---|---|
| `run_battery.py:1904` | `pass_lines = [...]` | `line.startswith("PASS ")` |
| `run_battery.py:1965` | span closure (in-span allowed) | `line.startswith("PASS ")` |
| `run_battery.py:1970` | span closure (post-span allowed) | `line.startswith("PASS ")` |
| `run_battery.py:1988` | diag-window closure | `line.startswith("PASS ")` |

**[I]** Widening these four to `startswith("PASS")` is the whole of C2a's tightening; the
false-positive risk is bounded by S2's measurement (delta 0 ⇒ no real row changes verdict).
**[U]** What a *widened* selector does to the 582-line population is not measured here — C2a
must re-run the census with the widened predicate (that is exactly the "false-positive analysis
required" in the claim). A row whose line is `PASS` with no trailing space at all would newly
enter `pass_lines`; S2 shows none exists today, but the widened predicate should be
`^PASS\b`-equivalent, not bare `startswith("PASS")`, or `PASSIVE_*`-shaped lines would flood.

---

## S3 — Orphaned-fixtures inventory state  [O]

### S3.1 Classification of every `.gd` under `corpus/fixtures/` (96 files)

| bucket | n | meaning |
|---|---|---|
| row-bound | **74** | basename appears in a CASES row's 2nd field (incl. `controls/`, `level_collision/`) |
| battery-referenced, not a row | **11** | probe/helper scripts the harness invokes (`timeout_probe.gd`, `stream_attribution_probe.gd`, `save_process.gd`, `scene_marker.gd`, `rb_watch.gd`, `crash_exit_probe.gd`, `godot_error_probe.gd`, `r97_scene_marker.gd`, `pickup.gd`, `controls/pickup.gd`, `controls/scene_marker.gd`) |
| unreferenced | **11** | see S3.2 |

### S3.2 The 11 unreferenced fixtures  [O]

| fixture | bytes | git | disposition class |
|---|---|---|---|
| `export_launch_s01..s06.gd` (6) | 19 544 / 16 264 / 26 773 / 12 186 / 22 333 / 29 466 | **tracked** | r102 C1 companions — **[O] referenced nowhere**: not in CASES, not in `run_battery.py` text, and **not by `export_launch.gd` either** |
| `baseline_actor.gd`, `causal_actor.gd`, `causal_pickup.gd` (3) | 453 / 679 / 233 | tracked | reached only at runtime from `causal_chain.gd` (which IS row-bound) — **[I]** helper trio, not orphans |
| `controls/input_route_receiver.gd`, `controls/negative_test.gd` (2) | — | tracked | `controls/` helpers — **[I]** referenced by the row-bound `input_route*.gd` / `negative_test` family at runtime |

**Finding (correction to the r102 ROUTED block, `LOG.md:1253`).** That line names
`export_prod_s03/s05/s06/s09 (+superseded s01/s02/s04/s07/s08/s10/s11)` as living "in
`reports/round-101/mutations/orphaned-fixtures/`". Verified [O]: the directory exists and holds
exactly those **11** `export_prod_s*.gd` files + a `README.md` (23533…17879 B each, all mtime
`Oct 18 22:21`, all git-tracked, none in CASES, none in `run_battery.py` text). So the block is
**accurate for the 11 `export_prod_s*`** — but it is **silent about the 6 `export_launch_s0*`
companions**, which are a *second, different* orphan class: they live **inside** `corpus/fixtures/`
(the directory the r101 README declares "must stay runnable and shard-backed") yet are referenced
by nothing. **[I]** this is the "orphaned-companion disposition" target of C3(b).

### S3.3 Parse state of the 11 archived companions (measured, not inherited)  [O]

Command (per file, scratch project `/var/tmp/r104-scout/parse/`; `run_battery.py` never run):

```
godot --headless --path /var/tmp/r104-scout/parse --check-only --script res://<f>.gd
```

```
export_prod_s01.gd     rc=0 parse_errs=0
export_prod_s02.gd     rc=0 parse_errs=0
export_prod_s03.gd     rc=0 parse_errs=0
export_prod_s04.gd     rc=0 parse_errs=0
export_prod_s05.gd     rc=1 parse_errs=1 | SCRIPT ERROR: Parse Error: Invalid argument for
                         "_emit_pack()" function: argument 2 should be "PackedByteArray" but is "Dictionary".
export_prod_s06.gd     rc=0 parse_errs=0
export_prod_s07.gd     rc=0 parse_errs=0
export_prod_s08.gd     rc=0 parse_errs=0
export_prod_s09.gd     rc=0 parse_errs=0
export_prod_s10.gd     rc=0 parse_errs=0
export_prod_s11.gd     rc=0 parse_errs=0
```

**[O]** 10/11 parse clean; **`export_prod_s05.gd` is broken** (rc 1, one parse error). Its README
entry ("exit=1, no PASS line (incomplete remap/UID census)") was accurate at retirement and the
file was never repaired. sha256 of the 11 (for the orchestrator's adopt/retire record):
s01 `d6a2868d…`, s02 `d953f689…`, s03 `d5e5314e…`, s04 `763087b6…`, s05 `8f16f47e…`,
s06 `772fb51e…`, s07 `e159f37c…`, s08 `e6c63361…`, s09 `79e723f1…`, s10 `55ac8760…`, s11 `755207e9…`
(full digests reproducible with `sha256sum reports/round-101/mutations/orphaned-fixtures/*.gd`).

**[I]** Disposition evidence base: s03/s06/s09 parse clean and are *adopt-with-fresh-pins*
candidates (their scenarios are already covered by `export_prod.gd`'s 12 rows, so adoption is
additive coverage); **s05 must be repaired or retired** — it cannot be adopted as-is; s01/s02/s04/
s07/s08/s10/s11 are the design-superseded set whose seats E1/E2/E4/E7/E8/E10/E11 completed
(seat tags verified [O]: each file's header carries `r101-E<NN>`), i.e. their pins already exist in
`reports/round-101/r101-E*.md` — registration would be additive, not repair. **[U]** No seat has
measured whether any of the 11 still produces its documented behavior under the *current*
`corpus/fixtures/` project (they were written against r101-era scratch projects).

### S3.4 Worktree state  [O]

`git worktree list` at HEAD:

```
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin         eff29d1d [main]
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r100 2d562282 [wt-r100] locked
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r98  68bee6e7 [wt-r98]  locked
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r99  fe1a996e [wt-r99]  locked
/var/tmp/r104-ver3/wt                                      eff29d1d (detached HEAD)
/var/tmp/r104-ver5/repo                                    eff29d1d (detached HEAD)
```

**[O]** Four of the six scratch worktrees the r103 scout listed (`/var/tmp/r103-S1/repo`,
`r103-S2/wt`, `r103-S3`, `r103-ver4/wt`, plus `/var/tmp/r102-S1`) are **gone**. The two live
non-lane ones (`r104-ver3/wt`, `r104-ver5/repo`, both detached at `eff29d1d`) belong to **this**
round's verifier seats — not mine to remove. **[O]** This seat created no worktree.

---

## S4 — Routed-but-unlanded census (r101–r103 adjudicators), status re-measured at HEAD

Pointers are to the **adjudicator blocks** that filed each item; "status" is this seat's measurement.

| # | routed item | source pointer | status at HEAD (`eff29d1d`) |
|---|---|---|---|
| 1 | stale `.shokunin/game-dev-2d/corpus/` citations | `reports/round-101/r101-adjudicator.md:92`; census `reports/round-101/r101-scout.md:47`; re-derived `reports/round-103/r103-scout.md:191` | **[O] unchanged**: SCORECARD 0, README 0, PROVINCE 0, SHONEN 0; `LOG.md` **44**, `corpus/lessons/` **100 files / 732 lines**. Still a preserve-vs-rewrite policy call (operator-owned). |
| 2 | VER-13: `export_preset_missing` `expected_errors` entry is dead code | `reports/round-101/r101-adjudicator.md:88-91`; carried `LOG.md:1308` | **[O] still open**: CASES row `run_battery.py:59`; dict entry `:2379`; inline `passed = classify_export(output)` at `:2249` and `:2281` (never consults the dict); the row is now also in `RECEIPT_SHAPE_DERIVED_EVIDENCE` at `:1779`. No behavior defect. **[O] pointer drift**: the same dict entry is cited as `:2011` (r101) and `:2078` (r103-scout) — line numbers move with every CASES splice; this table's numbers are the only ones measured at `eff29d1d`. |
| 3 | r62 timeout-probe `hold_open_new_bound` red ×2 | `reports/round-101/r101-adjudicator.md:82-85`; fix `reports/round-102/r102-adjudicator.md:32` | **[O] landed**: bound `0.75 → 1.25` at `run_battery.py:5671`, rationale comment `:5666-5670` ("host spawn→marker latency drifted ~0.39s (r22 era) to ~0.8s (r101+)"; counterfactuals 1.0→4/4, 1.25→4/4, 1.4→2/2). |
| 4 | 3 legacy `joys` rows red (host-state class) | `reports/round-101/r101-scout.md:196` (`r103-scout` S7 row 4) | **[U] not re-measured** — rule honored: no device-census token pinned anywhere in this shard. |
| 5 | pre/post-span foreign-line residual (mut09 span attack) | `reports/round-102/r102-adjudicator.md:105` ("bounded: pre/post-span foreign-line residual routed"); `LOG.md:1283` | **[O] still open**: the "whole-blob row-count gate for foreign lines outside pinned spans" is still only a ROUTED line; `run_battery.py` has no such gate (`grep` for `whole.blob`/`blob_row`/`row_count` → only comment text at `:3788, :4110, :5143`). |
| 6 | QUALITY.md scribe note | `reports/round-102/r102-adjudicator.md:122-125`; census `reports/round-103/r103-scout.md:196` | **[O] still open**: `corpus/QUALITY.md` absent (`ls` → No such file); `corpus/knowledge/` holds only `2026-10-12-production-checklist.md` + `seed.md`. Census answer (fleet convention) stands; write decision operator/scribe-owned. |
| 7 | mut01/mut06 script staging defects | `reports/round-102/r102-adjudicator.md:106` | **[O] unchanged**: not re-run by this seat (no battery). |
| 8 | stray worktrees | `reports/round-103/r103-scout.md:198` | **[O] mostly cleared** — see S3.4; only this round's `r104-ver3`/`r104-ver5` remain. |
| 9 | tab-PASS grammar tightening | `LOG.md:1307` (ROUTED r104+); `reports/round-103/r103-adjudicator.md:59-60` | **[O] still open** — this is r104 **C2a**; exact sites in S2 above. |
| 10 | mut05 full gate-replay wiring (catalog vs verdicts) | `LOG.md:1307` | **[O] still open** — this is r104 **C3a**'s vehicle. The r103 artifact `reports/round-103/mutations/mut05_gate_evasion.py` defines **10** synthetic shapes (s1a/s1b/s2a/s2b/s3a/s3b/s4a/s4b/s4c/s4d), i.e. the `reports/round-103/r103-adjudicator.md:57` "4/10 synthetic shapes flag" figure is a **flag count**, not a shape count. |
| 11 | 3D side-round before 2D r105 | `LOG.md:1309`; `reports/round-103/r103-connector.md:129` | **[U]** sibling lane — hands off entirely per instructions; not touched. |

**Routed-but-unlanded tally: 6 still open** (#1, #2, #5, #6, #9, #10), 2 landed/cleared (#3, #8),
3 not-measurable-by-design (#4, #7, #11).

---

## S5 — Loose ends / corrections worth carrying forward  [O]/[I]

- **[O]** `reports/round-101/mutations/orphaned-fixtures/README.md` says the archive exists so that
  `corpus/fixtures/` "must stay runnable and shard-backed" — yet the 6 `export_launch_s0*` companions
  (r102) sit *inside* `corpus/fixtures/` with zero references. **[I]** r102 applied the r101 rule
  only to the `export_prod` family; the `export_launch` companions never got the same treatment.
- **[O]** The r103 in-battery gate probe (`run_battery.py:5764-5769`) reports only
  `audited`/`flag_count` and a `bounded_claim`; it does **not** replay synthetic shapes. That is
  precisely the C3a gap ("in-battery gate-evasion replay probe ... green only if every shape flags
  as classified").
- **[O]** Repo dirty state at HEAD: ` D reports/round-102/mutations/__pycache__/r102-S3-verify.cpython-314.pyc`,
  `?? reports/round-103/mutations/__pycache__/`, `?? reports/round-104/`. Nothing else modified.
- **[O]** This seat's only repo write is `reports/round-104/r104-scout.md`. Scratch kept at
  `/var/tmp/r104-scout/` (`parse/` = the 11 archived companions + a minimal `project.godot`).
  No worktree created, so nothing to `git worktree remove`.

## Handoff (for the orchestrator, not this seat's claim)

1. **C2a sites are exactly four lines** — `run_battery.py:1904, 1965, 1970, 1988`. S2's delta-0
   census is the false-positive baseline to re-measure with the widened predicate. Prefer a
   `PASS`-token match over bare `startswith("PASS")` to avoid a `PASSIVE_*`-style flood class.
2. **C3b disposition**: adopt-with-fresh-pins = s03/s06/s09 (parse clean, scenarios already covered
   by `export_prod.gd`'s 12 rows, pins already in `reports/round-101/r101-E{3,6,9}.md`);
   **repair-or-retire = s05** (broken parse, sha256 `8f16f47e…`); superseded-with-existing-pins =
   s01/s02/s04/s07/s08/s10/s11. The **6 `export_launch_s0*` in `corpus/fixtures/`** are an
   un-routed second class the LOG does not mention.
3. **LOG correction candidate**: `reports/round-103/r103-adjudicator.md:59` "4/10 synthetic shapes" — 10 is the shape count,
   4 is the flag count.
