# r103-adjudicator — round 103 verdict (orchestrator seat)

Date: 2026-10-18. Swarm: THREE attempts on the scheduled provider (opencode-go/
deepseek-v4.1-flash): attempt 1 on key 7 starved after ~2h (59 skeleton shards +
real artifacts: 3 fold patches, w4 census, w5 splice, s02 fixture); attempt 2 on
key 4 died instantly (`402 Insufficient account funds`); attempt 3 on key 2
completed 58/58. All seats across attempts: opencode-go lane. Disclosed per the
stop-rule audit: the provider survived via key rotation within the scheduled
lane; no unscheduled provider was substituted.

## Declared claims

| claim | axis | before | after |
|---|---|---|---|
| C1 export_div divergence surface | coverage | 0 rows | +16 rows (5 fixture families, 20 arms measured) |
| C2 receipt-shape meta-gate | depth | span-foreign residual open (r102 mut09; r100-critic F1 family) | W10 gate green ×2 + adversary proofs |
| C3 simplifier gaps + print law | calibration | 3 unclaimed queue gaps + by-design FAIL-arm prints | 3 folds landed (−10 net lines), S4 print fix |

## Landed changes

- C1: `export_div_s01..s05.gd` + 16 CASES rows (s02 pair per r103-V11 with
  load-bearing adjacency; s02 re-entrancy defect found by E0 seat mid-round and
  fixed in-fixture — `_wipe_dir` blind to dot-dirs) + floor gates + cases_integrity.
- C2: `RECEIPT_MULTI_PASS_GRAMMAR` + receipt-shape META gate (W10; G4-verified 0
  flags over 4 stored runs; account tables measured over r102's two green runs;
  floor-not-ceiling discipline: new multi-PASS rows fail the gate until declared).
- C3: r97 F6 / r99 F2 / r100 SP2-SP3 fold patches applied (git apply clean;
  byte-identity evidence in S1/S2/S3 + V4/V5/V6 shards); S4 probe reject-arm
  print-semantics fix (designed-verb prints; verdict logic untouched).

## Before → after measurements

Counting command (SCORECARD repaired form): `python corpus/fixtures/run_battery.py
--probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error
--probe-stream-attribution --probe-crash-exit --probe-timeout`.

- C1: 0 → 16 rows; receipts: 16/16 PASS ×2 (both runs 570 PASS / 0 FAIL).
- C2: gate verdicts: **PASS ×2** — audited=554, flags=0 both runs; G4 matrix green over
  4 stored runs pre-landing; orchestrator replay of the 10-shape evasion catalog:
  4 flag at the shape layer (PASS-flood ×2, trailing-space ×2), 6 unflagged are
  accounted-by-design (banner/diag classes) or verdict-layer-harmless (tab-PASS
  vs space-anchored pins) — the gate's boundary is now measured, not assumed.
- C3: −10 net lines (r97 −4, r99b −1, r100b +1/−6); cross-run stability: 549
  comparable rows r102↔r103, 542 byte-identical, 7 diffs = run-dir paths (5) +
  by-design print-fix lines (2); probe arm prints now carry designed verbs.

## Provider-battle disclosure

Attempt 1 (key 7): ~2h starvation, 0 completions, partial artifacts. Attempt 2
(key 4): immediate 402 Insufficient account funds ×64. Attempt 3 (key 2):
58/58 completed in ~16 min. Seat counts: the round used ONE batched AgentSwarm
per attempt (3 attempts total) — disclosed against the one-swarm-per-round norm
as a provider-failure recovery, all within the scheduled provider lane.

## Mutation / verification battery

- mut05_gate_evasion replay (orchestrator, import+call): 4/10 synthetic shapes
  flag at the shape layer; 6 unflagged = accounted classes (banner/diag) or
  verdict-layer-harmless (tab-PASS) — boundary disclosed per class; the tab-PASS
  grammar-tightening candidate routed to a future round.
- mut07 fixture-row: harness-dead capture detected (dead 101B, pass_lines=1 →
  the row fails closed, not vacuously).
- mut02 (user:// spoof): executed, verdicts at /var/tmp/r103-mut2/out/ per shard.
- Gate iterate loops (orchestrator folds): F4 pin-timing race (r87-r92 records
  serialize signature after gate evaluation → gate now reads CASES pins);
  F5 probe-artifact skip (mutant twins/ctrls are not battery receipts); F6
  derived-evidence account (the two `__godot_export__` rows per VER-13).
- Fixture fix: export_div_s01 NUL-safe ASCII name decode (3 stderr warnings → 0,
  receipts byte-unchanged).

## Verdict

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | +16 `export_div` rows green ×2 (s01 ×5 arms incl. preset-vs-CLI identity proofs, s02 ×2 with the mid-round re-entrancy fix, s03 ×3 multi-preset, s04 ×3 PCK header census incl. keyless-encryption directory arm, s05 ×3 store/heal/ctb); 570 PASS / 0 FAIL ×2 |
| depth | **improved** | receipt-shape META gate landed (W10; account-table discipline; classifiers untouched): 0 flags over 554 audited rows ×2; measured boundary vs 10 synthetic evasion shapes (4 flag, 6 accounted/harmless — disclosed); three iterate-loop folds (F4 pin-timing race, F5 probe artifacts, F6 derived evidence) |
| calibration | **improved** | 3 simplifier gap folds landed (−10 net lines; byte-identity per S/V shards; cross-run stability 542/549 identical); probe reject-arm print-semantics fix (designed verbs; verdict logic untouched); s01 UTF-8 warning class eliminated fixture-side |

**Admission: ADMIT-WITH-FINDINGS** — provider battle (3 attempts: key 7
starvation, key 4 insufficient-funds, key 2 success; all within the scheduled
opencode-go lane), gate boundary classes, and the routed tab-PASS hardening
disclosed.

## SHONEN

- [~] decision tables: gate design + boundary classes + divergence lessons
  (3 lesson files land in this commit); probation gate operator-owned.
- [ ] end-to-end domain task — untouched.
- [~] executable instructions: the export_div path runs end-to-end (16 rows).
- [~] no cross-domain bleed: connector filed 0 contests; 3D lane untouched
  (observed at r106 under the parallel session early in the round).

L0: 3D side-round STILL deferred — must land before 2D r105; r104 opens with a
3D-lane quiet check (its r106 may have closed by now).
