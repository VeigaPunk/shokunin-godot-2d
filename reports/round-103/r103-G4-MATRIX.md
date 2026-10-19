# r103-G4-MATRIX — receipt-shape META gate: replay matrix over stored records (C2 depth)

Seat: G4-MATRIX. Lane game-dev-2d-shokunin, round 103, branch `main` (head `6e3e87f7`, not committed).
Plan (5 lines, written as first action):
1. Locate G1 gate implementation + r102 verdict records; copy gate to scratch, patch per G1 design.
2. Replay patched gate over stored green runs — expect 0 flags.
3. Replay over the 5 G2 adversary attacks — expect 5 flags; AGREE/DISAGREE per attack.
4. Build 6 synthetic corrupt record variants — expect 6 flags; record per-variant verdict.
5. Write AGREE/DISAGREE matrix + exact commands + byte counts; leave r101/r102 untouched.

STATUS: **COMPLETE.** Green 0 flags (4 runs) · attacks 5/5 flagged · corrupt 6/6 flagged · evasions 1/3 (2 measured ceilings).

Host: `uptime` start `20:55:23 up 1 day, 20:55, load average: 1.91, 1.78, 1.63`;
end `21:02:49 up 1 day, 21:03, load average: 7.39, 7.66, 4.73` (sibling lanes active).
Engine in records: `4.7.2.stable.arch_linux.ed1daf0bf`. No battery run, no shared file touched, no commit.

## 1. Lineage of the replayed gate (what actually exists)

* **G0** left a working prototype: `/var/tmp/r103-g0/proto_gate.py` (+ `proto_report.json`). Measured as-is over the 4 stored runs: **97 flagged rows** (27/24/23/23 per run) totalling **106 flag instances** (65 `pass_line_unaccounted` + 41 `own_pin_pass_line_absent`) — false-positive-laden, unusable as a calibration baseline.
* **G1 left no implementation** (shard `reports/round-103/r103-G1.md` is a plan only; scratch `/var/tmp/r103-G1`, `/var/tmp/r103c-G1` empty). G2 likewise (only `/var/tmp/r103-G2/account_residual.py`, a read-only residual inventory).
* **Therefore the "patched copy" replayed here is reconstructed from the G0 prototype + G0/G1 plan text**, and the patch is fully specified in §2 so it can be diffed against intent. This is a documented deviation from the seat wording ("replay the G1 gate"), caused by the two starved predecessors — labelled **observation**.
* **UPDATE (21:0x, concurrent sibling landings).** After this seat's recon, three other gate implementations appeared under `reports/round-103/mutations/`: `r103-G0-receipt_gate.py` (executable G0 spec, F0/F1/F2 taxonomy, public `receipt_shape_gate(records)`), `r103-ver8-gate_proto.py` (V-rec v2: whole-stdout account + pass-count), `r103-V12-receipt_gate.py` (S4 digest account). All three were imported read-only and **cross-replayed** over the same 4 green runs and the same 14 mutants (§4b). No sibling file was modified.

## 2. Gate specification as implemented

Script: `reports/round-103/mutations/r103-G4-matrix-replay.py` (stdlib-only; read-only over stored records).
Design-time constants (all pinned, no re-run of the battery, no classifier change):

| constant | source |
|---|---|
| CASES table (name → script, evidence payloads) | `corpus/fixtures/run_battery.py` (AST read, read-only) |
| multi-PASS allowlist + multiplicity | `reports/round-103/mutations/r103-w4-census.json` (run1/run2) |
| case census (538 case→script pairs) | `reports/round-103/mutations/r103-G4-case-census.json` (derived from the same 4 stored runs; closed-world) |
| fixture print-literals (exact + prefix) | `corpus/fixtures/*.gd` print-family literals (G2's extractor, reused) |
| engine/harness grammar, dynamic receipts | pinned regex list, cited inline in the script |

Checks (a row is flagged if any fires; `PASS`-verdict rows only carry F3–F9):

* **F1 malformed** — missing/blank/typed-wrong `case`/`script`/`signature`/`output`/`verdict` (fail-closed).
* **F2 unknown case** — `case` not in the census, or case/script pair mismatched (closed-world splice check).
* **F3 own pin absent** — no signature payload (any-alternative semantics, mirroring `run_battery.py:2343`) appears in the joined output; for `__godot_export__*` rows the exemption binds to that row's own contract (`[ DONE ]` + `savepack`, `run_battery.py:1956`).
* **F4 PASS-line unaccounted** — observed `PASS ` line not accounted by own payload / allowlist / dynamic template.
* **F5 whole-output accounting** — every output line must be accounted by: engine/harness grammar · own pin · allowlist · fixture literal/prefix · dynamic template. This is the check with teeth against non-PASS foreign lines.
* **F6 PASS-line multiplicity** — per-line occurrence ≤ pinned multiplicity (census, per-run max — never summed across runs) else 1.
* **F7 multiline pin** — a multiline signature payload must occur exactly once, contiguously, byte-exact.
* **F8 exit-field consistency** — `expected_exit == actual_exit` on a certified record.
* **F9 unrelated-ERROR invariant** — re-checks `classify_process`'s rule (`run_battery.py:1792-1808`) using the record's own `expected_errors`; **carved out**: `mutant_*` rows (classify_mutant path) and `__godot_export*__` rows (classify_export path).
* Scope rule: FAIL-verdict rows get F1/F2 only — a FAIL row's output legitimately diverges from its pin (measured: `input89_edges_axisdev`, `input_lattice_census`, `r101_ytrans_*` in r101), so receipt-shape binding would false-positive by construction.

## 3. Evidence — exact commands and observed bytes

All commands run from repo root `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`:

```
python3 reports/round-103/mutations/r103-G4-matrix-replay.py green    # 135 B stdout
python3 reports/round-103/mutations/r103-G4-matrix-replay.py allmut   # 892 B stdout
python3 reports/round-103/mutations/r103-G4-matrix-replay.py evade    # 382 B stdout
```

Replayed inputs (pinned by hash in this session):

```
65986c3f808b6f227143b24944cef9bfd0156d26830916c816f26605c83134c0  corpus/live/runs/20261018T212500022987Z/verdicts.json  (r102-1)
65e7fae0ca987563b40601439b4afe5388196c18ffe38dd91a8fc1c09a6a5f68  corpus/live/runs/20261018T213443471189Z/verdicts.json  (r102-2)
```
plus r101 runs `20261018T200239625248Z` and `20261018T202131127599Z`.
Script sha256 `4f7ad77e66ff23f596561de22163e19ec4ab760b92e1b489ccf0b29eec74a908`;
census sha256 `0e24f391b84f71a39f30fce7f43dc019ddd2c33fb895fc96b822574ac41ed34d`.

### 3.1 Green replay (verbatim)

```
== r101-1: rows=530 flagged=0
== r101-2: rows=530 flagged=0
== r102-1: rows=538 flagged=0
== r102-2: rows=538 flagged=0
TOTAL FLAGS: 0
```

### 3.2 Adversaries (verbatim; every attack is a record mutation over a real r102-1 row)

```
== attacks: 5 mutants
   FLAG  ATK1_mut09_A1_in_span_launch: ['F5_line_unaccounted(1)']
   FLAG  ATK2_mut09_A2_post_span: ['F5_line_unaccounted(1)']
   FLAG  ATK3_pass_line_flood: ['F5_line_unaccounted(3)', 'F4_pass_line_unaccounted(3)', 'F6_pass_line_duplicate(3>1)']
   FLAG  ATK4_foreign_line_in_seqfull_span: ['F3_own_pin_absent', 'F5_line_unaccounted(1)', 'F7_multiline_pin_occurrences=0']
   FLAG  ATK5_engine_banner_spoof: ['F5_line_unaccounted(1)']
== attacks: flagged 5/5
```

Attack construction (each over a real row): ATK1/ATK2 = r102 mut09 A1/A2 shapes (`FOREIGN_EXTRA injected=into_span|post_span` inserted into `export_launch_embed_boot`); ATK3 = 3 × foreign `PASS r99b mixfree …` lines flooded into the same row; ATK4 = `FOREIGN_EXTRA injected=span_mid` inserted inside the 17-line `r101_seqfull_clean` pinned span; ATK5 = banner version rewritten to `4.6.0.stable.arch_linux.deadbeef`.

### 3.3 Synthetic corrupt variants (verbatim)

```
== corrupt: 6 mutants
   FLAG  V1_pin_dropped: ['F3_own_pin_absent']
   FLAG  V2_pin_duplicated: ['F6_pass_line_duplicate(2>1)']
   FLAG  V3_signature_blank: ['F1_malformed:empty_signature']
   FLAG  V4_output_field_removed: ['F1_malformed:missing_output']
   FLAG  V5_case_renamed: ['F2_unknown_case', 'F4_pass_line_unaccounted(2)']
   FLAG  V6_exit_field_forgery: ['F8_exit_mismatch']
== corrupt: flagged 6/6
```

### 3.4 Measured evasions (honest ceiling, flagged 1/3)

```
   CLEAN EV1_warning_shaped_forgery: []                 # 'WARNING: FOREIGN injected=grammar_spoof' appended
   FLAG  EV2_error_shaped_forgery: ['F9_unrelated_error']
   CLEAN EV3_error_in_carveout_row: []                  # ERROR line injected into mutant_broken_scene_route (F9 carve-out)
```

## 4. Verdict matrix

| expected outcome | observed | AGREE/DISAGREE |
|---|---|---|
| 0 flags on r102 verdicts.json | 0 on r102-1, 0 on r102-2 (also 0 on r101-1/-2) | **AGREE** |
| 5 flags for G2's 5 attacks | 5/5 flagged, each by a named check | **AGREE** (with construction caveat §1: G2's attack set never landed; rebuilt from r103-G2.md's plan + mut09's measured shapes) |
| 6 flags for 6 synthetic corrupt variants | 6/6 flagged, one distinct check each | **AGREE** |
| G1 plan's stated check set ("PASS-lines unaccounted by pin or allowlist") suffices | 3 of 5 attacks (ATK1/ATK2/ATK5) carry **non-PASS** foreign lines and are invisible to a PASS-line-only gate | **DISAGREE** — teeth require whole-output accounting (F5); keep F5 in the landed gate |
| G0 prototype (`proto_gate.py`) usable as baseline | 97 flagged rows on green (27/24/23/23; 106 flag instances) | **DISAGREE** — prototype superseded; its greedy all-alternatives matching contradicts `run_battery.py:2343` any-semantics |

## 4b. Cross-implementation replay (4 gates × 4 green runs × 14 mutants)

Adapter: `/var/tmp/r103c-G4-MATRIX/cross_replay.py` — imports all four gate modules read-only and
runs them over the identical inputs. Gates: **A** = this seat (§2), **B** = `r103-G0-receipt_gate.py`,
**C** = `r103-ver8-gate_proto.py`, **D** = `r103-V12-receipt_gate.py`.

Green silence (flagged rows; B counts non-advisory only, its own scoping rule):

| run | rows | A | B | C | D |
|---|---|---|---|---|---|
| r101-1 | 530 | 0 | 0 | 6 | 63 |
| r101-2 | 530 | 0 | 0 | 3 | 67 |
| r102-1 | 538 | 0 | 0 | 0 | 54 |
| r102-2 | 538 | 0 | 0 | 0 | 0 |

* C's r101 flags are **all on FAIL rows** (verified: `input_lattice_census`, `input_lattice_dev_joy`, `input89_edges_axisdev`, `r101_ytrans_{y1000,ym1000,ycop}` — verdict FAIL each) — a scoping difference, not a false positive on certified receipts.
* D's flags are **all on PASS rows** (`tween_flash`, `save_roundtrip`, `save_process_writer/reader`, `export_readiness`, …) and are run-dependent (54 on r102-1 vs **0 on r102-2**) — measured, cause **unknown** (not diagnosed here).

Mutant discrimination (flag = caught):

| mutant | A | B | C | D |
|---|---|---|---|---|
| ATK1 mut09 in-span (launch) | ✔ | ✘ | ✔ | ✔ |
| ATK2 mut09 post-span | ✔ | ✘ | ✔ | ✔ |
| ATK3 PASS-line flood | ✔ | ✔ | ✔ | ✔ |
| ATK4 foreign line in seqfull span | ✔ | ✔ | ✔ | ✔ |
| ATK5 engine-banner spoof | ✔ | ✘ | ✔ | ✔ |
| V1 pin dropped | ✔ | ✔ | ✔ | ✔ |
| V2 pin duplicated | ✔ | ✔ | ✔ | ✔ |
| V3 signature blanked | ✔ | ✘ | ✘ | ✔ |
| V4 output field removed | ✔ | ✔ | ✔ | ✔ |
| V5 case renamed | ✔ | ✔ | ✔ | ✘ |
| V6 exit-field forgery | ✔ | ✘ | ✘ | ✔ |
| EV1 WARNING-shaped forgery (ceiling probe) | ✘ | ✘ | ✔ | ✔ |
| EV2 ERROR-shaped forgery | ✔ | ✘ | ✔ | ✔ |
| EV3 ERROR in F9 carve-out (ceiling probe) | ✘ | ✘ | ✔ | ✔ |
| **totals** | ATK 5/5, COR 6/6, EV 1/3 | ATK 2/5, COR 4/6, EV 0/3 | ATK 5/5, COR 4/6, EV 3/3 | ATK 5/5, COR 5/6, EV 3/3 |

Reading: only **A and B** are green-silent on all four runs. C and D have the higher raw catch
counts partly *because* they flag rows A/B accept (C's FAIL-row advisories; D's 54–67 PASS-row
digest flags) — i.e. their strictness is not yet calibrated against the "0 false flags on green"
requirement. C additionally catches both EV probes, which A leaves as documented ceilings; a
landed gate wanting both properties needs A's whole-output account + C/D's digest discipline,
with C's FAIL-row scoping and D's run-invariance fixed.

## 5. Findings (labelled)

1. **Observation — one green PASS row violates its own stored signature invariant.** `export_readiness` (script `__godot_export__`) has `signature = 'EXPORT PASS preset=Linux/X11 executable_bytes=73703800'` and that string is **not** in the stored `output` in any of the 4 runs (281/281/269/269 lines; `[ DONE ]` and `savepack` present in all four). Cause read from source: this row is classified by `classify_export` against `[ DONE ]` + `savepack` + artifact size (`run_battery.py:1956`), while the stored `signature` is the derived receipt (`run_battery.py:1943`). It is the **only** PASS row with pin∉output in all 4 runs (scanned exhaustively). Gate handling: pinned exemption bound to the row's own contract — not an amnesty, F5/F4/F6/F8/F9 still bind.
2. **Observation — FAIL rows are outside receipt-shape binding.** r101 runs carry FAIL rows whose output diverges from the pin (`input_lattice_census` `…eng=0/1 joys=0|1…`, `input89_edges_axisdev` `joys=0|1`, `r101_ytrans_y1000` ladder order). r102-1/r102-2 have **zero** FAIL rows (all 554 PASS).
3. **Inference — the mut09 lineage is corroborated at the record layer.** mut09's G-B ("row signature must bind an output-bytes/count token") is exactly the gap F5 closes at the meta layer for stored records; mut09's G-A/G-C cautions stay row-level and are untouched here.
4. **Ceilings (measured, not asserted):** (a) engine-grammar-shaped forgeries evade F5 (EV1 CLEAN, identical to the battery's own shape-based ceiling); (b) ERROR-shaped forgeries inside F9's two carve-outs evade F9 (EV3 CLEAN; 3 carve-out rows per run: 1 export row + 2 `mutant_*` rows); (c) the case census is closed-world over these 4 runs, so a splice reusing an existing case name evades F2 (it would still need to satisfy F3–F9); (d) `authority` — the gate reads fixture literals and grammar at r103 HEAD, so it pins the account as-of-now, not as-of-run.
5. **Unknown:** whether any *future* row class (e.g. the C1 export_div rows) needs new account classes — not measured here; C1 fixtures are a different seat's ownership.

## 6. AGREE/DISAGREE summary for the orchestrator

* **AGREE** that a receipt-shape META gate over stored verdict records is implementable without touching the classifier: 0 false flags over 2 136 certified rows across 4 runs, with 11/11 adversaries/corruptions flagged by distinct checks (gate A; gate B also 0-false-flag but catches only 2/5 attacks + 4/6 corruptions).
* **DISAGREE** with landing C (`r103-ver8-gate_proto.py`) or D (`r103-V12-receipt_gate.py`) as the round's gate without calibration work: C flags 6/3 FAIL-row receipts on r101, D flags 60/67/54 PASS-row receipts on three of the four stored runs (run-dependent; cause unknown) — neither meets the C2 "0 false positives on stored green records" bar as measured.
* **AGREE** with C2's framing that the gate is a *meta* layer (G0 spec → implementation) — but note the G1/G2 shards in this round are plan-only; the implementation replayed here is new work, so C2's "G1 implementation diff" clause is satisfied by §2 + the script, not by a pre-existing artifact.
* **DISAGREE** with any landing that keeps only the PASS-line accounting from G1's plan — measured blindness to 3/5 attacks (gate B's measured profile).
* **DISAGREE** with treating `export_readiness`'s stored-record shape as clean; either the record's `output` should carry the classified text (a canonical-runner question outside this seat), or the exemption documented in §5.1 must be part of the landed gate.

## 7. Files, scratch, cleanup

Touched (mine only, no shared file, no commit):

* `reports/round-103/r103-G4-MATRIX.md` (this shard)
* `reports/round-103/mutations/r103-G4-matrix-replay.py` (gate + replay harness; `python3 -m py_compile` clean)
* `reports/round-103/mutations/r103-G4-case-census.json` (pinned case census, 538 entries, 25 173 B)
* `reports/round-103/r103-G4.md` (3-line cross-reference to this shard)
* scratch: `/var/tmp/r103c-G4-MATRIX/` (transcripts `final-{green,allmut,evade}.txt` = 135/892/382 B, `sibling-g0-default.txt` = 1307 B, `cross_replay.py` = 4-gate × mutant adapter, reviewer `resid.py`, `gate.py` prototype copy). No git worktree created; nothing to `worktree remove`. Sibling scratch dirs `/var/tmp/r103{S2,S3,-ver4}` listed, untouched.
* sibling files read-only (not modified): `r103-G0-receipt_gate.py`, `r103-ver8-gate_proto.py`, `r103-V12-receipt_gate.py`, `r103-w4-census.json`.
* note: `reports/round-103/mutations/__pycache__/` now holds `py_compile` products from several seats (incl. `r103-G4-matrix-replay.cpython-314.pyc`); left in place, regenerable and not a deliverable.
