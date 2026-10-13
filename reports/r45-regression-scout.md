# Round 45 regression scout — disconnected signal control

Read-only review of the r45 calibration claim, current fixture/runner, r39 and r44 evidence, and their regression boundaries. No Godot execution or source edits; this report is the only write.

## Paired claim / integration constraint

The r44 positive is a well-defined baseline: same in-tree HSlider (0..10, step 1, initial 5), Button-owned edges 1–2 and 5–6, restoration before edges 3 and 7, nine parsed synthetic events with one process frame each, numeric history `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, Label `Value 4`. Its verifier checked focus owner before every edge and value/receipt/Label after each.

Current `slider_adjust.gd` already has `--disconnect-signal` as a setup-only disconnection of `slider.value_changed.connect(_on_value_changed)`; `_action` and focus handling remain shared. The current `--second-focus-restore` branch checks owner before every event and, when disconnected, derives empty receipts and `Value 5` for every edge while still checking every numeric value. However, after those checks it unconditionally prints the positive `PASS slider_adjust_repeat_second_focus_restore` and quits 0. Thus the candidate branch as currently read does **not** yet implement the required expected-negative disconnected outcome. The runner must keep the connected r44 positive row unchanged and add a separately classified disconnected row whose distinct expected-negative terminal diagnostic/exit 2 occurs only after all nine per-edge assertions. Do not count the diagnostic/exit 2 as sufficient by itself: a premature edge failure must not match the terminal signature. Confirm the disconnected command reaches the final negative only after every owner/value/receipts/Label assertion; preserve baseline positive tuple and existing rows.

Potentially important interpretation: unchanged numeric transitions with empty receipts/Label `Value 5` isolate the callback/consumer's observable outputs from slider numeric adjustment under this synthetic history. They do not show that the disconnected signal was emitted, consumed, or that unchanged edges were internally consumed. The disconnect flag's sole effect must remain signal connection removal; avoid modifying the action sequence or focus path between arms.

## Prior evidence and boundaries

- r39 direct paired evidence independently found connected and disconnected numeric histories equal for a shorter seven-edge sequence; disconnected receipts stayed empty and Label stayed `Value 5`, with exit 2 only after all seven checks. Its regression scout specifically cautioned to check final edge before expected-negative and distinguish expected diagnostic from arbitrary exit 2. This lends support but is not evidence for r45's nine-edge history.
- r44 named non-author verification measured the nine-edge connected history and preserved all 59 prior tuple-bearing rows, plus stable opt-in classifications. It is the appropriate connected comparator; its verifier artifacts do not test this disconnected nine-edge arm.
- Battery `--fault-injection` can have an outer PASS while deliberate inner hang/timeout and unrelated-error cases are FAIL; only the clean expected-negative inner case is PASS. Do not report the meta PASS as those injected faults succeeding. Timeout observations are bounded to tested child behavior, not general descendant cleanup.
- Export readiness, launch, and relative/absolute target issues are separate from this UI claim; historical export passes do not erase adverse export evidence or establish general export reliability. Existing export bounds (including startup/export bounds) are not changed by this probe.

## Bounded scope

Require real Godot 4.7.2 scratch-first paired replay before admitting the claim. Scope is headless Godot, deliberately parsed `InputEventAction` events and a process-frame yield, with observable GUI focus owner, numeric value, signal receipt list, and callback-driven Label. It does not establish OS auto-repeat, physical timing/keyboard behavior, rendering/pointer behavior, accessibility, production behavior, generic HSlider behavior, or internal consumption of unchanged events. No engine/editor/seeded fixture edits, no commit/push/merge.
