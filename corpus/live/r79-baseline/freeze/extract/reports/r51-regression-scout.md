# Round 51 regression scout — baseline integrity and r44–r50 caveats

Role: leaf, read-only for tracked files. I read the r49/r50 non-author JSON artifacts and reports; scratch-only normalized comparison is `corpus/live/r51-regression-scout-20261013/baseline-comparison.json`.

## Baselines

- r49 non-author baseline: `corpus/lessons/r49-fresh-after-reconnect-non-author.json`, PASS 74/74: 63 ordinary + 2 mutants + 9 opt-ins; 65 tuple-bearing rows.
- r50 repaired non-author baseline: `corpus/lessons/r50-release-repaired-non-author.json`, PASS 75/75: 64 ordinary + 2 mutants + 9 opt-ins; 66 tuple-bearing rows. Relative to r49, all 65 prior `(case, verdict, actual_exit, signature)` tuples match exactly and only `slider_adjust_repeat_right_second_focus_restore_release_after_late_reconnect_press` is added. Opt-in classifications stay stable: Godot error `[true,false]`, stream attribution `[true,false]`, crash exit `[true,false]`, timeout `[false,true,false]`; other opt-ins retain their PASS classifications.
- Separate r50 fault result `corpus/lessons/r50-release-repaired-fault-non-author.json`: outer/meta PASS, but intended `fault_hang` and `fault_unrelated_error` are inner FAIL; only `fault_clean_expected_negative` is inner PASS. This is classifier evidence, not all-inner-pass evidence.

## Regression scope and warnings

The r44–r50 sequence progresses from restored-focus control, through signal disconnect/reconnect histories and a fresh post-reconnect press, to an ordinary parsed release. r50 repaired branch has 11 edge assertions and `Input.is_action_pressed` true→false checks; its successful normal parsed-event result is not universal dispatch provenance. The r50 report retains prior adverse outcomes: pre-repair no-dispatch falsely passed because changed state was not measured; direct `Input.action_release("ui_left")` bypassed parsed dispatch but also cleared state and passed those checks. Neither adverse may be erased by a successful normal-path row.

For r51 the relevant causal experiment is decisive against the proposed specific `_input` observer: independent scout scratch says clean eleven-edge path yielded only three matching observer receipts total, with count 3 before and after edge10; direct state-clear bypass and no-dispatch both also yielded 3→3. The clean final parsed release was not observed by this root `_input` monitor. Thus no exact negative test should be added for normal-vs-bypass on this evidence; that would classify the clean case as negative too. This confirms no tracked fixture/runner regression was introduced by this scout; current tracked hashes are fixture `abf833021df686f01d6778646a9d1a96bbabab00905bcb554ac7f8e2d68e7434`, runner `4afc03127ecd13d274eb6bfe8f569bbdd849108558b3884c8d7247775ad3d77c` (runner matches r50). No engine/editor/seeded changes, commits, push, or merge.

Prior r44–r50 bounds persist: headless Godot 4.7.2 synthetic parsed input plus process frames only. No OS repeat, physical input/timing, rendered/pointer behavior, accessibility, production, generic HSlider behavior, or internal slider consumption claims. Timeout observations are bounded to tested direct-child cleanup; export readiness is not export launch reliability, and prior relative export path failed. Keep first-attempt setup/scratch failures and r50 false-PASS / bypass adverse as telemetry, not silently normalized.
