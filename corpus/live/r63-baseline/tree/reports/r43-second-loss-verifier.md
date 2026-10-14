# Round 43 named non-author verifier — second focus loss

## Result

**Verified; HOLD/admission is a parent decision.** I independently ran direct scratch and the default-path battery; I did not edit tracked fixture/runner files. The clean bounded default-path command exited 0 and produced 68/68 PASS (57 ordinary + 2 mutants + 9 opt-in rows), including exactly one new `slider_adjust_repeat_right_second_focus_loss` PASS with actual exit 2 and the distinct expected terminal diagnostic. This expected-negative row is not a positive PASS claim about adjustment; it confirms all seven edge assertions reached the declared terminal negative.

The author's initial integrated battery run failed: `export_preset_missing` exited 1, and the new row initially had an empty diagnostic classifier. The parent then corrected only that new row's exact allowed terminal diagnostic. Preserve both initial failures as adverse telemetry, not PASS. Subsequent independent bounded default-path replays report `export_preset_missing` exit 1 with its precise expected diagnostic (`ERROR: Invalid export preset name: Missing preset.`), and classify it PASS; both replays exited 0 with 68/68. The initial author failure is retained and is not erased or promoted to PASS evidence.

## Independent Godot scratch

Using Godot `4.7.2.stable.arch_linux.ed1daf0bf`, I ran both candidate and paired positive in fresh scratch project copies. Candidate `--repeat-right --second-focus-loss` exited 2 only after all seven per-edge checks; output reported values `6,6,6,5,5,5,5`, cumulative receipts `[6,5]`, Labels `Value 6,Value 5`, then `SLIDER REPEAT SECOND-FOCUS-LOSS ASSERTION FAILED: expected final restored-focus adjustment after seven checks`. Paired `--repeat-right --focus-restore` exited 0 with final `4/[6,5,4]` and `Value 4`.

Sabotage checks rejected both omissions before reaching the terminal expected-negative classifier: omitting the second focus transfer failed the owner assertion at edge 5; omitting the first press failed edge 0's value/receipt assertion. Each returned exit 2 but lacked the terminal diagnostic, so neither is classified as the expected candidate. The scratch uses the same seven fresh parsed actions and one process frame per event, connected `value_changed` callback, and Label state checks. Owner sequence was slider at 0,3,4 and Button at 1,2,5,6.

## Default-path comparison and artifacts

Command:
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r43-second-loss-verifier/runs`

- First run: exit 0; 68/68 PASS. Raw lesson: `corpus/lessons/r43-second-loss-verifier.json` (byte-identical to run `20261013T071853230789Z/verdicts.json`, SHA-256 `0410d27255173b5ed85ef43ad3ff6491800f87d3de8d65810ceda9446cf6467d`).
- Retry after retaining the author's export failure telemetry: exit 0; 68/68 PASS, run `corpus/live/r43-second-loss-verifier/retry-runs/20261013T072102595281Z/verdicts.json`.
- All 58 r42 prior rows carrying `(case, verdict, actual_exit, signature)` tuples are unchanged (including mutants). The only added tuple-bearing row is `slider_adjust_repeat_right_second_focus_loss`, PASS/exit 2 with the declared exact signature. The nine opt-in rows retain stable outer and inner classifications: all outer PASS; inner diagnostic/stream/crash/timeout classifications remain `[true,false]`, `[true,false]`, `[true,false]`, `[false,true,false]`. Run-specific paths are excluded from comparison.
- Separate `--fault-injection` outer verdict PASS, raw `corpus/lessons/r43-fault-verifier.json`: deliberate `fault_hang` and `fault_unrelated_error` inner FAIL; `fault_clean_expected_negative` PASS. This is a clean negative-control result, not battery case PASS evidence.

## Integrity, scope, and limits

Tracked SHA-256 before/after verifier: `slider_adjust.gd` `203fd9eac5acdff9e4318a395602f194af34de267b1a8ef1270b64ccc654d421`; `run_battery.py` `046e7900672ddee49304567afe30b9d97d48c71a5902dd7a9c07ac5504982f23`. No tracked edits, commit, push, or merge by verifier.

This establishes only headless synthetic parsed-event/frame behavior with this connected HSlider/Label/Button setup. It does not establish OS repeat, physical keyboard/timing, rendered or pointer behavior, accessibility, production behavior, or internal consumption of unchanged edges; it is not a generic slider guarantee.
