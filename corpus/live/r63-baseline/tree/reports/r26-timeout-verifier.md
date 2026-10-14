# Round 26 timeout verifier report

Named non-author verifier; independent full replay against the tracked fixture and runner. No tracked edits, engine/editor changes, seeded-control changes, commit, or delegation.

## Full real-Godot replay

Command:
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

Exit 0; outer verdict **50/50 PASS: 39 ordinary + 2 mutants + 9 opt-in**. The prior r25 verifier has the same 50 case names, verdicts, actual exits, and signatures (no differences). As in prior records, expected negative inner outcomes are represented as outer PASS. Raw complete outer record: `corpus/lessons/r26-timeout-verifier.json`; three-arm timeout record: `corpus/lessons/r26-timeout-detail.json`.

The tracked script is identical across the three timeout arms (`res://timeout_probe.gd`), and all require exit 0 and the exact `TIMEOUT_PROBE: expected signature` marker:

- **Old bound, slow clean:** intentional 1.5s post-marker delay, 0.75s timeout; marker was already captured at timeout, `timed_out=true`, `actual_exit=null`, inner classification false, process live at timeout, direct child reaped (`cleanup_exit_code=-9`); elapsed 0.753s.
- **New bound, same slow clean script/arguments:** 3.0s timeout; marker observed, clean exit 0, no timeout/error, classification true; elapsed 1.972s (about 1.028s below the bound).
- **New bound, hold-open:** same marker emitted before 30s wait; at 3.0s deadline marker observed and process still running, `actual_exit=null`, classification false, direct child reaped (`cleanup_exit_code=-9`); elapsed 3.009s.

This verifies the required marker-before-timeout counterfactual in the tracked fixture, unlike the earlier reviewer scratch arm whose expected marker was absent. It establishes this bounded delay on this Godot 4.7.2 Linux host only, not arbitrary startup/freeze behavior, process-tree cleanup, or cross-platform robustness.

## Separate fault injection

Command `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection` exited 0 with top-level meta PASS. Preserved raw `corpus/lessons/r26-fault-verifier.json`: intended inner `fault_hang` and `fault_unrelated_error` remain FAIL; clean expected-negative control PASS. No failures were retried or relabeled.

## Integrity and verdict

Final runner SHA-256 `431f922421af2780529860151347a7146204952d55e09607779b34632bc682cc`; fixture SHA-256 `4994893281fea8221d980f5c551f2e0541464530e3e542ac97b2cabe97a61462`. These match before/after verifier hashes. For provenance, committed baseline hashes were runner `ab0d0352445113b2ba7f742b57500f97e62b2196411f96fe7f8b594e69cdab41`, fixture `e100202690d0101a6fbf0148bdb9f47dd`.

The LOG baseline-count correction is confirmed: 39 ordinary `CASES`, not 40. **Calibration improved** for the declared controlled slow-positive / hold-open contrast; **depth unchanged**, **coverage unchanged**; no observed harm in this finite replay. Constants evidenced: old timeout 0.75s, intentional delay 1.5s, new timeout 3.0s, cleanup 3s (unchanged). No broader reliability claim.
