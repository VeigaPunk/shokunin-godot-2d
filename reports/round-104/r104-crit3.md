# r104-crit3 — C3 critique: attack the probe (vacuity + cost census)

HOST: `uptime` @ start `22:29:44 up 1 day, 22:29, 1 user, load average: 3.77, 2.11, 1.84` (load low; sibling game-dev-3d lane hands-off).
REPO: `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` @ `eff29d1d` (main). Godot `4.7.2.stable.arch_linux.ed1daf0bf`. No commits. Scratch `/var/tmp/r104-crit3/`. `run_battery.py` NEVER executed (hard rule 1) — it is only `import`ed for its pure functions.
SEAT: KEY=C3, critic. Targets: (a) the in-battery gate-evasion replay probe, (b) the orphaned-companion disposition.

PLAN (5 lines):
1. Read the receipt-shape gate + draft probe; pin the exact flag contract and the probe's hook site.
2. Enumerate K>=8 synthetic evasion shapes; replay each against the **live** gate to find vacuous passes.
3. Cost census: wall time + bytes of the gate and of a K-shape replay, to size the in-battery budget.
4. Attack the orphaned-companion disposition: is adopt-with-fresh-pins vs retire decidable from in-repo evidence?
5. Write findings with exact commands + output bytes; label observation/inference/unknown.

STATUS: complete. All commands below were run from the repo root; artifacts under `/var/tmp/r104-crit3/`.

---

## 1. Contract pinned (observation)

`receipt_shape_flag(row)` — `corpus/fixtures/run_battery.py:1877`; wrapper `receipt_shape_audit(rows)` — `:1990`. Importing the module runs **no** battery (`__main__` guard at EOF), so a probe can call the live function:

```
$ python3 -c "import importlib.util; spec=importlib.util.spec_from_file_location('rb','corpus/fixtures/run_battery.py'); ..."
IMPORT_OK secs=0.0298 ; CASES n=552 ; SIG n=552 ; GRAMMAR n=19
AUDIT corpus/live/runs/20261019T005558434174Z/verdicts.json audited=554 flags=0 secs=0.0031 ; run_verdict=PASS
```

Green base is live: `20261019T005558434174Z` = 571 rows, all PASS, `audited=554`, `flags=0`. The gate's **first** statement is a case-name lookup, and three early `return []` paths bypass all content inspection:

- `case not in CASES_SIG_BY_CASE` -> `[]` (r103 fold F5 comment: "probe artifacts, not battery receipts").
- `case in RECEIPT_SHAPE_DERIVED_EVIDENCE` -> `[]` (`export_readiness`, `export_preset_missing`).
- `receipt_shape_audit`: `verdict != "PASS"` -> skipped; `"script" not in row and output not a list` -> skipped.

## 2. r103 catalog replay reproduces "4 flag / 6 unflagged" byte-exactly (observation)

`python3 /var/tmp/r104-crit3/attack2.py` (rebuilds the 10 mut05 shapes from `mut05_gate_evasion.py`'s own base rows) over run `20261019T005558434174Z`:

| shape | live flags | why |
|---|---|---|
| s1a_banner_forged_seq | 0 | — |
| s1b_banner_dup_launch | 0 | — |
| s2a_diag_other_family_simple | 0 | — |
| s2b_diag_forged_launch | 0 | — |
| s3a_flood5_simple | 1 | `unaccounted_pass_lines` obs=6 decl=1 |
| s3b_flood1_seq | 1 | `pass_line_grammar_mismatch` obs=15 decl=14 |
| s4a_tab_lead_simple | 0 | — |
| s4b_trail_space_simple | 2 | `unaccounted_pass_lines`, `anchor_line_multiplicity` |
| s4c_trail_nbsp_simple | 1 | `unaccounted_pass_lines` |
| s4d_tab_after_pass_simple | 0 | — |

Matches `reports/round-103/r103-adjudicator.md:57-58` ("4 flag … 6 unflagged") exactly. Fresh r104 shapes (all unflagged): `n1_pass_vtab`, `n2_pass_cr`, `n3_diag_renamed_family` (`ZZZ_DIAG`), `n4_exportprogress_foreign` (`[ 50%]`), `n6_ansi_only_injection`, `n7_banner_suffix_junk`, `n8_case_rename_invented`, `n9_derived_case_skip`. `n5_seq_foreign_insidespan` flags `foreign_in_span`; `n10_banner_deleted` (see §3) does not.

## 3. **F1 — the banner regex is dead outside span/DIAG windows** (observation, severity: high)

`RECEIPT_BANNER_RE` is referenced by `receipt_shape_flag` but only as a *skip* predicate inside the span/diag branches. On a row with neither a `SEQ_BEGIN` nor a `*_DIAG` line there is no window, so a forged or deleted banner is invisible:

```
== C: forged banner into a simple row ==
  input_route -> []
== A: foreign plain line, no-DIAG no-SEQ row ==
  input_route -> []   camera_follow -> []   geo2d_lattice_census -> []
== B: same injection into a DIAG row ==
  export_launch_embed_boot -> [foreign_in_diag_window]   export_prod_base_pck -> [foreign_in_diag_window]
```

`n10_banner_deleted` (real row with the banner line removed) also returns `[]`. [inf] r103-crit2's a11_banner_deleted flagged only because its row was a `SEQ_` row. This is the same class as the r103 mut7 vacuity counter-shape (`reports/round-103/r103-mut7.md:53-54`) — that finding was about *signatures*, not the gate; the gate itself has the hole.

## 4. **F2 — 15-flag false-flag surface inside the gate's own DIAG window** (observation, severity: medium)

Run `20261019T001435805887Z` (571 rows, `run_verdict=FAIL`) audits to **15 flags**, all `export_div_s01_*` / `export_div_s02_*` rows, all the same line:

```
$ python3 - <<'PY' ... rb.receipt_shape_audit(json.load(open('corpus/live/runs/20261019T001435887Z/verdicts.json'))['results'])
audited 554 flags 15
 {"case":"export_div_s01_pack","why":"foreign_in_diag_window","line":"Unicode parsing error, some characters were replaced with \ufffd (U+FFFD): Unexpected"}
```

[obs] r103's Fixture fix (NUL-safe ASCII name decode) drove exactly these to 0 by the next run (`20261019T003019776183Z` -> `flags=0`). [inf] Consequence for the C3 probe: the flag count is **not run-invariant** — a probe asserting a *specific* flag count would flip on this run. Any probe must assert a property, not a number.

## 5. **F3 — the vacuity door: probe shapes must live under REAL case names** (observation, severity: high)

Vacuity test method: load the live module and a *lobotomized* twin (`receipt_shape_flag` patched to `return []` before its first statement), replay identical shapes through both. A shape whose live and lobotomized results agree has **zero discriminating power**.

```
$ python3 /var/tmp/r104-crit3/discrim.out
shape                live     lobo     discrim?   live flag reasons
s3a_flood5           1        0        True       ["unaccounted_pass_lines"]
s3b_grammar15        1        0        True       ["pass_line_grammar_mismatch"]
s4b_trail_space      1        0        True       ["unaccounted_pass_lines","anchor_line_multiplicity"]
s4c_nbsp             1        0        True       ["unaccounted_pass_lines"]
s4a_tab_lead         0        0        False      []
s4d_tab_after        0        0        False      []
s1a_banner_forged    0        0        False      []
s2a_diag_foreign     0        0        False      []
s2b_diag_samefam     0        0        False      []
clean_control        0        0        False      []
shapes that CANNOT distinguish the live gate from a flag-logic-deleted gate: 6/10
```

The `[ 50%]`/`ZZZ_DIAG`/invented-case shapes are all `0/0` too. **Only 4 of the ~18 shapes have any discriminating power.** The other ~14 return `[]` identically under a deleted gate, so a probe that merely asserts "shape X is unflagged" is satisfied by an early `return []`.

The single most dangerous variant is the natural implementation: storing the probe's synthetic shapes as **battery rows under invented case names** (`probe_evasion_shape_*`), which is exactly what the r103 F5 fold made skippable:

```
== D: case-name lookup gate (vacuity door) ==
  case=probe_receipt_shape_meta_gate  -> []
  case=probe_evasion_shape_s1         -> []
  case=export_readiness               -> []
  case=mutant_broken_scene_route      -> []
audit over 18 probe-named rows: audited=18 flags=19     <- all 19 are `dead_shape_allowlist_entry`; ZERO row-content flags
```

[inf] Probe requirement: each synthetic shape must be stored as a *tampered copy of a real base row keeping that row's case name*, never under a `probe_*` name. Otherwise the probe reports green while inspecting nothing.

## 6. Cost census (observation)

```
$ python3 /var/tmp/r104-crit3/cost2.out
import_cold_secs=0.0072
20261018T212500022987Z rows=554 audited=538 flags=0  med_ms=2.410  battery_wall_s=569  gate_share=4.23e-04%
20261018T213443471189Z rows=554 audited=538 flags=0  med_ms=2.390  battery_wall_s=559  gate_share=4.28e-04%
20261019T001435805887Z rows=571 audited=554 flags=15 med_ms=2.591  battery_wall_s=662  gate_share=3.91e-04%
20261019T003019776183Z rows=571 audited=554 flags=0  med_ms=2.532  battery_wall_s=605  gate_share=4.19e-04%
20261019T004115354212Z rows=571 audited=554 flags=0  med_ms=2.429  battery_wall_s=712  gate_share=3.41e-04%
20261019T005558434174Z rows=571 audited=554 flags=0  med_ms=2.426  battery_wall_s=649  gate_share=3.74e-04%
K18_replay_us=44.8  per_shape_us=2.49
with_extra_probe_row audited 554->554 flags 0->0
K18 stored-shape bytes=14642  verdicts.json bytes=1464781  ratio=1.00%
```

- Gate full-corpus audit: **~2.4-2.6 ms** (median of 7) per 554-row run; import **7 ms** cold.
- K=18 replay: **45 µs** — the probe's marginal CPU is ~2.5 µs/shape, i.e. **~5e-6 of a battery run** (~570-710 s wall, measured stamp -> newest non-scratch artifact mtime).
- Storage: K=18 shapes as JSON rows = **14.6 KB**, 1.00 % of a 1.46 MB `verdicts.json`. [obs] `verdicts.json` is not the only artifact — the run dir holds ~1.5 MB total plus `export-launch-verdicts.json` 65 KB.
- [obs] Adding one `probe_*` meta row leaves `audited`/`flags` unchanged (554/0) — the probe row is invisible to the gate it probes (consistent with §5). [obs] Auditing 18 rows *renamed* to `probe_evasion_shape` yields `audited=18, flags=19`, and all 19 are `dead_shape_allowlist_entry` (the grammar rows absent from the set) — **zero row-content flags**, confirming §5's door.

**Verdict on cost:** the probe is free (microseconds, 1 % storage). There is **no cost reason** to weaken it. The entire risk is vacuity (§5) and false flags (§4), not budget.

## 7. C3b — orphaned-companion disposition: **RETIRE is the decidable call** (observation + inference)

`python3 /var/tmp/r104-crit3/orphan.out` over `reports/round-101/mutations/orphaned-fixtures/` (11 files, 11 distinct sha256; none referenced by any harness path — `grep -rn "orphaned-fixtures\|export_prod_s0\|export_prod_s1" corpus/fixtures/*.py corpus/fixtures/*.gd` -> no hits):

- **Landed coverage:** 7 registered rows (`export_prod_base_pck`, `subdir_census`, `include_exclude_filter`, `main_scene_swap`, `mainpack_quit_after_frames`, `resource_remap_census`, `icon_uid_census`) + 8 arms in `export_prod.gd` (`base zip det_a det_b swap remap refusal notemplates`). All 11 orphan scenario descriptions in the README map onto one of these.
- **Pin decidability:** for each of the 11 shards I searched `reports/round-101/r101-E*.md` for a machine-replayable pin of the form `PASS export_prod_sNN …`. Result: **0/11**. The shards carry *fragments* (e.g. `r101-E1.md:121` shows a `PASS export_prod_s01 …` line; `r101-E7.md:91` shows a `PASS export_prod_s07 …` contract) but no per-fixture complete receipt, and 4 of the 11 (s03/s05/s06/s09) are the README's *broken* set with exit codes only.

[inf] **Adopt-with-fresh-pins is not decidable from in-repo evidence**, because the "fresh pins" would have to be *measured*, and the only way to measure a Godot fixture's receipt is to run `godot --headless` on it — which is a C3-adjacent seat's scope (S1 owns this), not a critic's. What a critic *can* settle:
1. There is no coverage delta to recover — the README's own claim ("C1 breadth is unaffected") is verified by the landed-row/arm census above. [obs]
2. The 4 broken fixtures (s03/s05/s06/s09) are declared incomplete by their own README; adopting them requires authoring work, not pinning work. [obs]
3. Therefore the only *evidence-free* disposition available to the orchestrator is **RETIRE** (keep the README as the historical record); **ADOPT** requires a measured-pin producer, which is S1's seat. [inf]

Recommendation to the orchestrator: retire the 11 files, retain `README.md` (it is the provenance record, per the r103 "citation-rot law" — `reports/round-103/r103-connector.md:52`). If S1 lands measured pins, adopt per-fixture then; the two are not in conflict.

## 8. Verdict (C3 axis view)

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 18 shapes replayed against the live gate (§2); 2 new escape families found (F1 dead-banner-regex, F3 probe-named skip) plus 8 fresh unflagged shapes |
| depth | **improved** | gate contract fully pinned (§1); the vacuity test is *mechanical* (live vs lobotomized) and reproducible; flag-count non-invariance disclosed (F2) |
| calibration | **improved** | cost measured, not assumed: 2.4 ms/run, 45 µs/K18, 14.6 KB (1 % of `verdicts.json`); orphan disposition reduced to a decidable call (§7) |

## 9. Handoff — what the C3 probe MUST do (falsifiable requirements)

1. **No self-referential oracle.** The expected result for each shape must be a hand-labelled constant, not `receipt_shape_flag`'s own output. The lobotomized-gate test (`/var/tmp/r104-crit3/discrim.out`) is the acceptance test: the probe must go RED on a `return []` gate.
2. **Shapes must keep a real base row's `case`** (F3). A `probe_*` case name is invisible to the gate.
3. **Assert properties, not counts** (F2). A count assertion flips on the `export_div_s01` flag surface.
4. **Declare the ~14 zero-discriminating shapes** as *accounted-by-design*, with the reason, so the probe's green is not read as "18/18 shapes were inspected".
5. **Consider routing F1** (banner-regex dead outside windows) to the r104 C2 gate-boundary seat: it is a gate hole, not a probe hole, and it is the cheapest of the three fixes.

## 10. Residuals / unknowns

- **[unknown]** Whether the probe will be implemented as a Python meta row (`probe_*`, invisible to the gate, §6) or as stored synthetic rows in `verdicts.json`. Only the latter is auditable by the gate.
- **[unknown]** S1's per-fixture adopt/retire calls were not visible when this shard was written; §7 gives the decidable subset only.
- **[inference]** The 6 unflagged r103 shapes are *substantively* accounted (a crafted foreign line would flag) but *not* safely green: `s4a`/`s4d` are honestly "whitespace-evaded, unaccounted PASS line" (§5) — the escape is real, the tab-PASS family (routed to C2) is the fix.
- No shared file touched; no battery run; no worktree created; no commits. All scratch under `/var/tmp/r104-crit3/` (16 files, max 6.8 KB).
