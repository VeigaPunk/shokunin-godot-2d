# Round 51 provenance simplifier — observer placement and causal decision

Role: read-only simplifier; no tracked edits, no delegation. I reviewed the r51 declared claim, r50 repaired verifier/critic boundary, the immutable baseline reviewer, and scout's independent Godot 4.7.2 observer scratch/report. I did not produce a separate valid Godot causal run: the isolated scratch I began from was already instrumented, so I do not count it as independent evidence.

## Smallest meaningful proposal

Keep one in-tree `Node._input(event)` observer and increment only when `event is InputEventAction`, `event.action == "ui_left"`, and `not event.pressed`. For edge10, snapshot its count immediately before the call to `_action`, then after the one-frame wait require the count to have increased by exactly one. Preserve r50's existing pre-edge owner/callback and action-state checks, plus post-edge pressed-state, value, full receipts, and Label checks. The observer should attest only matching event delivery at this observer's `_input` point; do not describe it as HSlider consumption. If calibrated successfully, expose just one opt-in flag/negative row and one exact terminal diagnostic; avoid broad observer machinery.

## Causal gate result: not met

The scout's independent direct scratch reports the normal eleven parsed events reached the expected terminal negative with values `6,6,6,5,5,5,5,4,4,3,3`, receipts `[6,3]`, and Label `Value 3`, but its observer count remained `3` across nominal edge10 (3 before / 3 after). The same unchanged count occurred for `Input.action_release("ui_left")` direct state-clear and for omitted edge10 dispatch. Therefore the proposed observer fails to observe the normal edge as well as the bypasses; it cannot support the r51 calibration claim. Its cause/effect comparison falsifies the declared hypothesis, not merely a desired edge-case. Do not implement the new flag/row on this evidence; HOLD and retain r50 unchanged.

The distinction is consequential: r50 establishes synthetic parsed `_action` plus pressed-state true→false, and exact omission detection; critic's direct `Input.action_release` bypasses parsed-event dispatch while satisfying r50's state/value checks. The new observer has not closed that gap because it saw no edge10 receipt on the clean path.

Scope throughout: synthetic `Input.parse_input_event` and process frames in Godot 4.7.2 only. No OS/physical timing/input, HSlider internal consumption, rendering/pointer/accessibility, production or generic slider claim. No engine/editor/seeded or tracked fixture/runner changes, commit, push, or merge.
