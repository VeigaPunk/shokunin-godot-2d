# Round 54 named non-author verifier — clear-then-push ordering

## Verdict: PASS

LEAF non-author verification, no delegation. Runtime: Godot `4.7.2.stable.arch_linux.ed1daf0bf`. I read the round declaration/LOG, r51–r53 reports and raw baseline, and the r54 wave reports. Candidate verification did not mutate tracked fixture or runner. SHA-256 before and after: `slider_adjust.gd` `da84345352fc60637f35fcb94d4adf8ebf36be1c06f5a1cf10d83b36b65421cd`; `run_battery.py` `6652003110eec0936fb6272c5d4dbcb2560bfbab168339af06a1ca724ff638e8`.

## Full default-path battery and comparison

Command:

```text
python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r54-named-verifier/runs
```

Raw: `.shokunin/game-dev-2d/corpus/lessons/r54-order-non-author.json`, SHA-256 `5ff28df0baf8a4ebe6e1f3ec5a7b95caf00a19d88df3cfe2a61ccd3e76780eaf`. Result is **79/79 PASS** = 68 ordinary + 2 mutants + 9 opt-in classifications. Against r53 raw `corpus/lessons/r53-composite-non-author.json`, all **69/69** prior tuple-bearing `(case, verdict, actual_exit, signature)` rows match exactly by case. Exactly one tuple-bearing row is added: `slider_adjust_repeat_right_second_focus_restore_clear_then_push_release` (expected/actual exit 2, PASS, unique terminal `SLIDER CLEAR THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks`). All **9/9** opt-in classifications match r53. The intentionally rejected inner `godot_error_unrelated` and `stream_reject` are failures within outer PASS probes, not clean fixture passes.

## Separate fault receipt and targeted sabotage

Separate `--fault-injection` raw: `corpus/lessons/r54-fault-non-author.json`, SHA-256 `cc50beaf84dfdc2010358eafda5dbb50e217ed6327d8e39fd7b3538cc612fd8f`; outer PASS. As designed, inner hang times out/FAIL, clean expected-negative is PASS, unrelated error is rejected/FAIL.

Two independent scratch sabotages copied the candidate fixture and removed only one edge10 operation while retaining the production expected-negative terminal contract and same flags. Omitting clear exited 2 at `ui_left remains pressed`; omitting push exited 2 at `parsed ui_left release observer failed: expected exactly one delivered release`. Neither reached the candidate's unique terminal. Both are rejected by the contract; they are not classified candidate passes. Scratch was isolated under `corpus/live/r54-named-verifier/sabotage/`; no tracked or seeded mutation.

## Evidence interpretation and limits

Together with wave1 scratch measurements, verifier evidence supports that reverse edge10 order (clear then matching pushed release, before same frame) mimics parsed r51 and push-then-clear r53 on the measured state: observer 3→4, action false, value 3, receipts `[6,3]`, Label `Value 3`, focus owner and callback connected. The candidate row confirms all eleven checked edges reach the exact negative terminal. The battery comparison verifies additive row stability, not route identity or uniqueness.

This is limited to the synthetic Godot 4.7.2 fixture. No claim about HSlider internal event consumption, OS/physical input or timing, rendering, pointer/accessibility, production behavior, or general event provenance. One initial malformed shell invocation exited 127 before launch; it produced no test evidence and was discarded. No constants changed; no engine/editor/seeded changes, commit, push, or merge.
