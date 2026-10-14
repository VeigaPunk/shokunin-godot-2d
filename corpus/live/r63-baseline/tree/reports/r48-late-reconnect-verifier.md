# Round 48 late-reconnect verifier — named non-author replay

## Verdict: PASS

I was assigned the named non-author verifier leaf. I did not delegate, did not edit tracked fixture/runner files, and did not commit, push, or merge.

The full default-path command completed with exit 0 and battery PASS: 73/73 cases (62 ordinary, two mutants, nine opt-ins). Raw byte-identical copy: `corpus/lessons/r48-late-reconnect-verifier.json`; run directory: `corpus/live/r48-late-reconnect-verifier/runs/20261013T082736843799Z/`.

The new `slider_adjust_repeat_right_second_focus_restore_reconnect_after_final_left` row is PASS with actual exit 2 and the exact expected-negative signature `SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks`. Its terminal error follows the nine per-edge checks. A marker records values `6,6,6,5,5,5,5,4,4`, receipts `[6]`, and Label `Value 6`; callback is connected at termination. The runner admits this precise expected negative, not an arbitrary error.

Independent evidence supports the causal behavior. The r48 reviewer scratch (`reports/r48-late-reconnect-reviewer.md`) checks focus owner before every edge and numeric value, receipts, and Label after every frame. Callback is connected before edge0; disconnected only after edge0 verifies 6/[6]/Value6; remains disconnected through edge7's value4/[6]/Value6 assertions; reconnects only after those checks; remains connected at edge8, whose release leaves numeric4/[6]/Value6. Its terminal expected-negative occurs only after all nine checks. The bounded Godot 4.7.2 observation is the proposed narrow synthetic parsed-event/frame result, not a claim about physical/OS input.

Compared with immutable `corpus/lessons/r47-reconnect-verifier.json` (72/72), all 63 prior tuple-bearing `(case, verdict, actual_exit, signature)` rows are unchanged. The nine opt-in classifications are present and unchanged apart from run paths. Exactly one new tuple-bearing row appears: the expected-negative PASS exit 2. This yields 62 ordinary + 2 mutants + 9 opt-ins.

The separate `--fault-injection` run also had outer PASS: deliberate hang and unrelated-error inner cases classified FAIL, while the clean expected-negative classified PASS. Raw result: `corpus/live/r48-late-reconnect-verifier/runs/20261013T082901868820Z/fault-verdicts.json`.

I independently sabotaged isolated copies. Omitting edge0's action fails the edge0 numeric/receipt/Label assertion; reconnecting before edge7 action fails the edge7 pre-reconnect assertion; omitting reconnect fails the connection assertion. Each exits 2 before the terminal expected-negative marker, so an early failure cannot be mistaken for the terminal PASS.

Adverse development telemetry remains in the wave reports: the executor's first tracked insertion was malformed, then restored byte-for-byte from HEAD before a fresh additive branch; the first ordinary row failed because the exact ERROR allowance was absent, then fresh ordinary replay passed 62/62 after correction. The critic's malformed and timeout scratch attempts produced no independent engine verdict. The baseline reviewer initially overread an intentional exit 2 as callback emission, then corrected the report; the scribe corrected an edge8 connectivity assertion. None of those attempts count as independent verdicts. The named verifier replay and independent reviewer scratch above are the admitted evidence.

Fixture and runner SHA-256 stayed unchanged across my replay: `slider_adjust.gd` `2ed7367365d7554bdc7b12afa59f329850acecfb2145069bb75953b75044e033`; `run_battery.py` `f978853b2be859674d74c582cb626b553efe4cd0dc5e46cf470ce48bfa70313c`.

Scope: synthetic parsed events and frames in the bounded headless Godot probe. No OS repeat/physical timing, rendered or pointer interaction, accessibility, production, generic signal replay, or internal consumer behavior on unchanged edges is established.
