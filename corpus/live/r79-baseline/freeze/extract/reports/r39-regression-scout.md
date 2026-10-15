# Round 39 regression scout — HSlider and battery boundaries

Read-only review of the declared r39 repeated-press move, current slider fixture/runner, and r38 evidence. No engine run or source edit; this report is the only write.

## Prior HSlider edge caveat

The r38 edge critic's scratch measurement directly tested an extra fresh `ui_right` `pressed=true` event with a process-frame yield: focused connected HSlider advanced 6→7 with receipt 7. In the regular sequence, `ui_right` release did not duplicate the adjustment, and left press/release returned 6→5. This supports measuring the proposed distinct second press and release independently; it does not establish OS keyboard auto-repeat, physical timing, or generic HSlider behavior. r39 should retain the narrow synthetic `InputEventAction` + next-frame claim and assert the actual signal-driven Label at every edge. The disconnected paired arm must be observed through the final edge before emitting its intended expected-negative result; do not treat its expected exit 2 as a harness failure. Keep the existing no-focus row untouched.

## Battery, export, timeout, and fault boundaries

Current runner has explicit separate opt-ins for export launch, timeout, crash/exit, Godot error, stream attribution, and fault injection. Export work uses a 60-second bound; export-launch startup uses a 5-second bound, while general process paths have their own bounds. These probes are not evidence for slider semantics. The `--fault-injection` meta-test may report outer PASS while deliberately injected inner timeout/unrelated-error cases fail; do not conflate that with fixture results. Preserve these paths and rely on the named verifier's full default/fault replay for any regression claim. Expected-negative slider exit must be classified using its intended diagnostic, not merely exit 2.

## Bounded review

The proposed two fresh right-press sequence is consistent with existing r38 raw evidence, but this scout is not a fresh Godot measurement. Require r39's first scratch measurement to verify connected sequence 5→6→7→7→6→5 and receipts/Labels `[6,7,6,5]` / `Value 6,7,7,6,5`, plus disconnected numeric history and unchanged `Label Value 5` with no receipts. If any edge differs, HOLD or correct the claim. This review makes no standalone axis claim and proposes no runner/export/fault changes.
