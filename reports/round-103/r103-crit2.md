# r103-crit2 — C2 receipt-shape meta-gate: attack seat
- Plan step 1: read r102 adjudicator routing + cases_integrity gate + r102 mut09 / r100-critic F1 span-foreign residual
- Plan step 2: locate the stored per-row stdout record format; enumerate what a META gate can/can't see
- Plan step 3: evasion battery — banner-shaped foreign line, R101Y-style diag prefix, PASS-line with trailing whitespace, pin-span injection
- Plan step 4: false-flag sweep over legit families (multi-PASS allowlist candidates) + green r101/r102 records
- Plan step 5: demand account list + evasion tests; write findings, keep <400 lines; status: IN PROGRESS

## Re-seat (attempt 3, KEY=C2) — plan delta written FIRST, per hard rule 6
1. Reuse mut05_gate_evasion.py (evasions over real green r102 records + green controls); emit evasions.json.
2. Target: no landed G1 implementation existed (G1/G0/G2/G3/G4 shards plan-only or scratch-only); build the
   reference META gate as the attack target and land it as reports/round-103/mutations/r103-crit2-meta-gate.py
   (+ frozen account registry r103-crit2-registry.json). NEVER a classifier change: records-only, read-only.
3. Green-silence sweep over r101-run1/run2 + r102-run1/run2 stored verdicts.json (546/546/554/554 rows) — zero flags.
4. Evasion replay: mut05's evasions + seat-authored adversaries + green controls.
5. False-flag families: classify every row the naive G0 proto flags; attribute each to gate-spec defect vs data nuance.
- uptime at re-seat start: `20:55:34 up 1 day, 20:55, 1 user, load average: 1.94, 1.79, 1.64`
- uptime at v3 close: `21:03:24 up 1 day, 21:03, 1 user, load average: 7.74, 7.74, 4.87` (sibling lanes active)
- Scratch: `/var/tmp/r103c-C2/` (never /tmp: host EDQUOT). No git worktree created by this seat.
- Status: **COMPLETE (gate v3)**. `run_battery.py` never executed; no shared file edited; no commit.

## 0. Landed artifacts (new files, untracked → orchestrator applies)
| file | bytes | sha256 |
|---|---|---|
| `reports/round-103/mutations/r103-crit2-meta-gate.py` | 8384 | `f69089d2e4613bb016bbb917e51891b08ed8ead803c9b67a14d4c93dd4ace972` |
| `reports/round-103/mutations/r103-crit2-registry.json` | 603783 | `34e6f4200a512e38daa30f3a5a5b2d401d542d1b7a6833e9b4584d6ec5f5a3bb` |

Scratch (evidence, retained): `gen_registry.py`, `gate_ref.py` (the same gate code; scratch copy defaults to the
scratch-side `registry.json`, landed copy to `r103-crit2-registry.json`), `evasion_driver.py`,
`falseflag_classify.py`, `census.py`, `evasions.json` (60368 B, `27de0112…`), `evasion_results.json`
(`6d7c9ef1…`), `green_sweep_v3.json`, `falseflag_families.json`, `mut05_gate_run_v3.txt`.
Registry-path resolution re-verified after a `cp` had reverted it: `DEFAULT exists: True` →
`…/reports/round-103/mutations/r103-crit2-registry.json`.
Gate compiles: `python3 -c "import py_compile; py_compile.compile('reports/round-103/mutations/r103-crit2-meta-gate.py', doraise=True)"` → `py_compile OK`.

## 1. Ground truth pinned (read-only reconnaissance)
- [obs] Classifier pin semantics: `classify_process` grades `signature in output` — a whole-output **substring**
  check (`corpus/fixtures/run_battery.py:1808`). Extra PASS lines / foreign lines never affect grading → the
  residual class r102-mut9/seqfull established. `allowed_error` semantics at `run_battery.py:1794-1804`
  (exact after strip; `endswith(",")` prefix form; special `ERROR: chain incomplete`) — mirrored by the gate.
- [obs] Final-state census over the 4 stored runs (546+546+554+554 rows):
  * banner: exactly one `Godot Engine v…` line at index 0 in every row that has output (0 anomalies);
  * 0 nonstandard PASS-shaped lines, 0 PASS lines with trailing whitespace, 0 exact-duplicate PASS lines in any record;
  * 538 rows with output / 16 rows `output=None` (all `probe_*` meta rows) / 48 zero-PASS rows (negative arms);
  * 566 PASS lines per r102 run; 19 multi-distinct-PASS cases per run (matches w4 census);
  * 8 rows per run carry a **2-member list signature** (r87 any-listed-payload precedent):
    `input_lattice_{pre_frame,api_press,phys_peer,press_phys,release_edge,ui_ns}`, `input89_edges_exact`, `r92_tilemap_nav`;
  * run verdicts: r101-run1/run2 = FAIL (7 failing records each), r102-run1/run2 = PASS (554/554).
- [obs] Consequence: content rules must scope to `verdict == PASS` records; FAIL receipts are not green evidence.
- [obs] `mut05_gate_evasion.py` was repaired by a concurrent M5 seat at 20:59:15 (md5 `acf2f0210bf66acf9d0a88320916bfbb`);
  this seat did **not** edit it. `evasion_driver.py` handles both the pre-repair 2-tuple and current shapes.

## 2. Gate spec v3 (landed; records-only META predicate)
R0 scope: content rules audit `verdict == PASS` rows only; unknown verdict → flag.
R1 schema fail-closed: `output` list[str] or None; `output=None` allowed only for the frozen 16-case opaque set.
R2 banner: exactly one banner, at index 0, engine pin `Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf`.
R3 PASS shape: PASS-shaped lines (lstrip starts with `PASS`) must be canonical (`PASS ` prefix, no trailing
   whitespace) → catches tab-lead, trailing-space/NBSP, TAB-after-PASS forgeries.
R4 PASS account: canonical PASS lines must be byte-equal to the frozen case/script allow-list or start with the
   row's own signature payload line; byte-exact duplicates inside one record flag.
R5 non-PASS account: blank/banner ok; ERROR-bearing lines accounted by the row's `expected_errors`
   (classifier-mirror) OR the row's own signature contained in the line (mutant/export rows whose pin IS the
   ERROR); all other lines must be token-known to the row's script (frozen per-script verb registry, 58 scripts)
   with every `key=` atom inside the frozen key-set for `(script, token)`.
R6 signature presence: str pin must appear in the output text; list pin requires ≥1 member present;
   exceptions only via frozen `sig_offline` set (`export_readiness`) **and** a non-empty `export_artifact`
   field (substance clause).
Registry composition [obs]: `engine_pins` 1; `opaque_cases` 16; `sig_offline_cases` `['export_readiness']`;
`sig_mixed_cases` `[]`; `scripts` 58 with per-token key-sets; `pass_lines_by_case` 490 and
`pass_lines_by_script` (frozen full-line allowlists); `generated_from` sha256s:
r101-run1 `8a53f0e2…`, r101-run2 `5f6c0efa…`, r102-run1 `65986c3f…`, r102-run2 `65e7fae0…` (latter two = w4's anchors).

## 3. Green-silence sweep (command + observed output)
```
$ python3 reports/round-103/mutations/r103-crit2-meta-gate.py --json-out /var/tmp/r103c-C2/green_sweep_v3.json
corpus/live/runs/20261018T200239625248Z/verdicts.json              rows=546 flagged=0 run_verdict=FAIL consistent=True
corpus/live/runs/20261018T202131127599Z/verdicts.json              rows=546 flagged=0 run_verdict=FAIL consistent=True
corpus/live/runs/20261018T212500022987Z/verdicts.json              rows=554 flagged=0 run_verdict=PASS consistent=True
corpus/live/runs/20261018T213443471189Z/verdicts.json              rows=554 flagged=0 run_verdict=PASS consistent=True
```
[obs] 0 flags / 2200 records (both r101 runs included their 7 FAIL receipts, correctly unaudited).

## 4. Evasion battery (15 flagged / 2 declared survivors / 4 green controls silent; 21 units, 0 mismatches)
Driver: `python3 /var/tmp/r103c-C2/evasion_driver.py` → `MISMATCHES=0 / 21 units`.
10 mut05 evasions (each a tampered copy of a real green r102 record) + 7 seat adversaries:

| unit | expect | gate flags [obs] |
|---|---|---|
| s1a_banner_forged_seq | flag | `banner_layout=[0, 2]`, `banner_version@2` |
| s1b_banner_dup_launch | flag | `banner_layout=[0, 4]` |
| s2a_diag_other_family_simple | flag | `unaccounted_line@3 tok='EXPORT_LAUNCH_DIAG'` |
| s2b_diag_forged_launch | flag | `diag_key@6 tok='EXPORT_LAUNCH_DIAG' extra=['forged=']` |
| s3a_flood5_simple | flag | `pass_unaccounted@3…@7` (5 forged lines) |
| s3b_flood1_seq | flag | `pass_unaccounted@23='PASS r100_gui forged=1'` |
| s4a_tab_lead_simple | flag | `pass_shape@3='\tPASS forged=true'` + `unaccounted_line tok='<ind> PASS'` |
| s4b_trail_space_simple | flag | `pass_shape@3` (trailing space on duplicate) |
| s4c_trail_nbsp_simple | flag | `pass_shape@3='PASS forged=true\xa0'` + `pass_unaccounted@3` |
| s4d_tab_after_pass_simple | flag | `pass_shape@3='PASS\tforged=true'` + `unaccounted_line tok='PASS'` |
| a5_banner_version_swap (seat) | flag | `banner_version@0` (forged v9.9.9 occupies the real slot) |
| a6_legit_prefix_junk_suffix (seat) | **survive** | none — declared residual R1 below |
| a7_pass_exact_dup (seat) | flag | `pass_dup='PASS route=parse_input_event-to-Node._input …'` |
| a8_diag_known_key_foreign_value (seat) | **survive** | none — declared residual R2 below |
| a9_foreign_prefix_before_pin (seat) | flag | `unaccounted_line@3 tok='X'` |
| a10_fail_to_pass_flip (seat; r101 FAIL record + `verdict="PASS"`) | flag | `sig_absent` |
| a11_banner_deleted (seat) | flag | `banner_layout=[]` |
| green_launch / green_prod / green_seq / green_simple | silent | `[]` ×4 |

## 5. Instrument-to-instrument replay (the original mut05 oracle vs the landed gate)
```
$ python3 reports/round-103/mutations/mut05_gate_evasion.py --gate reports/round-103/mutations/r103-crit2-meta-gate.py
GATE_COPY=/var/tmp/r103-mut5/gate.py sha256=f69089d2e4613bb016bbb917e51891b08ed8ead803c9b67a14d4c93dd4ace972 bytes=8384
GATE_FUNC=receipt_shape_gate … GATE_RESULT_TYPE=list … rc=0
```
[obs] All 10 mut05 evasion rows appear in the flagged result list with the flags in §4; `receipt_shape_gate`
list-call convention accepted (no TypeError fallback needed).

## 6. False-flag families — naive prototype vs v3
Baseline [read, no rerun]: G0's scratch prototype report (`/var/tmp/r103-g0/proto_report.json`) flags
27/24/23/23 rows across the four runs (97 total). Classification script asserts the v3 gate is **silent on
all 97** and attributes every proto flag:
```
$ python3 /var/tmp/r103c-C2/falseflag_classify.py     →  family counts: {'F_FAMILY': 88, 'F_FAIL': 9}
```
- **F_FAIL (9)** [obs]: rows whose record verdict is FAIL (r101 failures — proto audited failing receipts;
  v3 scopes to PASS). Examples: `input_lattice_census` (r101-run1: FAIL, PASS in r102), `r101_ytrans_ycop`.
- **F_FAMILY (88)** [obs]: rows whose observed PASS lines are covered by the frozen full-line account but not
  by the proto's own-pin + same-script CASES set. Sub-classes:
  * multi-PASS accounting (e.g. `r100b_seq_clean`/`noclean` 14-line seq receipts, `r93_*`, `r99b_*`,
    `input89_edges_axisdev`) — proto's `pass_line_unaccounted`;
  * 8 list-pin cases per run ×4 = 32 flags were `own_pin_pass_line_absent` under str-only handling; the v3
    any-member list rule (R6) + frozen allowlists absorb them (`input_lattice_*`, `input89_edges_exact`,
    `r92_tilemap_nav`);
  * `save_process_missing` (`pass_line_unaccounted`: the observed PASS line is the one its record stores,
    proto's CASES walk missed the row's own pin).
- [inf] Family rates are stable across runs (r101: 27/24, r102: 23/23) — the false-flag mass is structural
  (account completeness), not run noise.

## 7. Bounded residuals (declared, with bytes) — what this META gate still cannot see
- **R1 legit-prefix + same-line junk SURVIVES** (a6): appending ` extracted=1` to
  `PASS route=parse_input_event-to-Node._input key=R receipt_count=1 frames=3` passes because the pin is a
  prefix like the classifier's substring semantics. Closing this needs per-case full-line shape pins
  (byte pinning the tail); the frozen allowlist only catches non-prefix changes. Same family as r102-mut9.
- **R2 DIAG known-key foreign-value SURVIVES** (a8): `EXPORT_LAUNCH_DIAG embed root=/forged/root` passes the
  key-set account (root ∈ frozen keys); value semantics are not pinned. Closing needs per-key value shapes.
- **R3 any-member list pins**: one listed payload present is accepted (mirrors the r87 whitelist precedent);
  a record forgeable only to the extent it reproduces a legit payload.
- **R4 continuation tokens are script-scoped, not adjacency-scoped**: an indented continuation line using a
  token the script legitimately emits might slip in; foreign tokens do not (a9/s4a/s4d show the catch side).
- **R5 FAIL-scope**: FAIL records are not content-audited; a FAIL→PASS flip IS caught (a10 `sig_absent`), but
  a tampered FAIL record could theoretically be made to look pinned if the forger rewrites its output too.
- **R6 `ERROR`-line duplicates are not multiplicity-checked** (r101 failures show ERROR lines can be dynamic).
- **R7 opaque rows**: the 16 `probe_*` rows (`output=None`) are audited only through their other channels.
- **R8 sig_offline exception**: `export_readiness` bypasses R6 only with a non-empty `export_artifact`.

## 8. Verdict (C2 axis view)
| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | records-only META gate v3 catches all 10 mut05 evasions + 5 seat adversaries (banner-foreign x3, diag-prefixed x2, PASS flood x2, whitespace x4, dup x1, FAIL-flip x1, foreign-prefix x1, banner-deleted x1) with byte-exact flags (§4) |
| depth | **improved** | classifier substring semantics isolated (`run_battery.py:1808`); 8 list-pin cases + 16 opaque rows + 1 export-channel row given explicit, frozen accounts; 97 proto false flags attributed (88 account-completeness, 9 FAIL-scope) with the v3 gate silent on all |
| calibration | **improved** | frozen account registry regenerated from 4 runs (sha-pinned anchors, w4 agreement: 566 PASS lines, 19 multi-PASS rows); 0 flags / 2200 green records; 0/21 battery mismatches; residuals R1–R8 disclosed with exact bytes |

## 9. Handoff notes
- **Orchestrator apply**: both landed files are new (`reports/round-103/mutations/r103-crit2-*`); integrate the
  gate as a post-run META check over stored verdict records (never inside `classify_process`); regenerate the
  registry each round with `python3 /var/tmp/r103c-C2/gen_registry.py` (or a landed copy) and re-run §3.
- Concurrent-seat facts left untouched: `mut05_gate_evasion.py` repaired at 20:59 by the M5 seat (not by me);
  `mut02.py` live under `/var/tmp/r103-mut2` (app.pck written 20:56) — not touched; `mut07.py` receipts exist
  from 18:52 (`/var/tmp/r103-mut7/receipts/`: absent/blank/rows) — not rerun (W7 claim).
- Stray worktrees listed, NOT removed (per instruction):
  `/var/tmp/r103-S2/wt`, `/var/tmp/r103-S3`, `/var/tmp/r103-ver4/wt`, `/var/tmp/r102-S1`,
  `/var/tmp/r103c-C3/wt`, `/var/tmp/r103c-C4/wt` (plus the three locked `game-dev-2d-shokunin-wt-r*`).
- [unk] Whether the concurrent seats will land their own G0/G1 variants; if so, reconcile rule R6 list-pin
  semantics and the `expected_errors`-mirror clause against theirs before final admission.
- No commits made; no shared file touched; no battery run.
