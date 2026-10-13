# Round 51 independent parsed-release observer scratch

Role: read-only reviewer; no tracked fixture/runner edits. Unique scratch project: `.shokunin/game-dev-2d/corpus/live/r51-provenance-reviewer-scratch-20261013/`, copied from the r50 reviewer project and modified only in that scratch. Godot `4.7.2.stable.arch_linux.ed1daf0bf`.

## Method

Added an in-tree `Node` with `_input(event)` that increments a counter only when `event is InputEventAction`, `event.action == "ui_left"`, and `not event.pressed`. For the eleven-edge r50 sequence, captured its count immediately before edge10 and printed it with the post-frame observer count, pre-edge focus owner, numeric value, full receipts, Label, and `Input.is_action_pressed("ui_left")`. Ran three scratch variants: normal parsed `_action("ui_left", false)`, direct `Input.action_release("ui_left")` instead of parsed dispatch, and no dispatch at edge10. The scratch diagnostic branch was purely observational: it did not reject any case based on observer count.

## Results

- **Normal parsed release:** edge10 observer count `3 -> 4`; owner before edge10 `@HSlider@2`; after frame numeric `3.0`, receipts `[6.0, 3.0]`, Label `Value 3`, action pressed `false`. Eleven checks reached the existing exact expected-negative marker and exit2.
- **Direct state clear:** edge10 observer count `3 -> 3`; same owner/value/receipts/Label and action pressed `false`. It also reached the r50 expected-negative marker/exit2, showing the existing assertions do not distinguish it.
- **No dispatch:** edge10 observer count `3 -> 3`; same owner/value/receipts/Label, but action pressed remains `true`. It also reaches the unmodified r50 marker/exit2 because this reviewer scratch intentionally does not include r50's later pre/post state checks. The parent-repaired tracked fixture is separately documented to assert the post-release state and reject this omission.

Earlier three `ui_left` releases account for the baseline observer count of 3; counts are snapshots just before and after edge10, so normal adds exactly one receipt. Results support the hypothesis that this observer distinguishes delivery of the synthetic parsed release from direct Input state clearing and omission in this harness. It proves an in-tree observer sees the matching event; it makes **no** claim that the HSlider consumes it internally.

## Limits and telemetry

This is headless synthetic `Input.parse_input_event`/process-frame evidence only, not OS input, physical timing, rendering/pointer/accessibility, production, or internal consumer behavior. My first three shell launches used malformed triple-quote command syntax and exited 127; I reran all three normally and report only those successful reruns. No tracked files were changed. No engine/editor/seeded edits, commit, push, or merge.
