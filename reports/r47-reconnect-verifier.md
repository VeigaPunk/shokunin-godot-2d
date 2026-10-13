# Round 47 reconnect verifier — named non-author replay

## Verdict: PASS

I independently replayed the candidate as a non-author. The prescribed full default-path command completed with exit 0, battery `PASS`, 72/72 cases (61 ordinary, two mutants, nine opt-ins). Raw JSON is `corpus/lessons/r47-reconnect-verifier.json`; run directory is `corpus/live/r47-reconnect-verifier/runs/20261013T081039988235Z/`.

The new candidate `slider_adjust_repeat_right_second_focus_restore_reconnect_after_first_left` uniquely returned exit 0 only after its branch assertions. Its signature records numeric values `6,6,6,5,5,5,5,4,4`, cumulative callback receipts `[6,4]`, and Labels `Value 6,Value 4`. Direct reviewer evidence independently checks owners before each action and values/receipts/Labels after each frame, with disconnect after edge 0 and reconnect after edge 3. The full edge evidence is in `reports/r47-reconnect-reviewer.md`.

Compared with `corpus/lessons/r46-mid-disconnect-verifier.json`, all 62 prior tuple-bearing `(case, verdict, actual_exit, signature)` rows are unchanged. The nine probe classification rows are also unchanged, ignoring run-path output. Exactly one new tuple-bearing PASS exit 0 appears.

The required separate `--fault-injection` replay produced an outer PASS: deliberate hang and unrelated-error inner probes were classified FAIL; clean expected-negative classified PASS. Raw result: `corpus/lessons/r47-fault-verifier.json`.

I independently sabotaged the branch in isolated copies. Skipping reconnect fails the connection-state assertion; reconnecting before edge 3's action fails the edge 3 receipt/Label assertion; skipping the first press fails edge 0's value/receipt/Label assertion. All terminate with exit 2 before the positive terminal marker. The default-path full replay also exercised expected-negative/error, export-launch, stream-attribution, crash-exit and timeout probes; their inner unrelated-error/reject cases remained FAIL rather than being accepted as positive.

Adverse telemetry remains explicit: the executor initially replaced the r46 branch and runner row, then had a tainted invocation reporting 1/1 while omitting r46. Neither that invocation nor the initial scratch/type-error or terminated runs count as evidence. The corrected candidate was additive. Fixture and runner SHA-256 before/after replay are unchanged: `dcc70439fb950b28789b4ea63f2655df98759a50100dc9068f6c8270f334bc33` (`slider_adjust.gd`), `d6077491cbee8c4c82a7ae9a728799a04b55e8840840dc7ec318781478121914` (`run_battery.py`). No tracked fixture/runner edits were made by this verifier.

Scope is headless synthetic parsed input events plus frames. This does not establish OS repeat, physical timing/input, rendered or pointer interaction, accessibility, production behavior, or internal consumer handling of unchanged edges.
