# Round 43 independent second-focus-loss scratch review

## Result

Direct real-engine scratch completed under Godot `4.7.2.stable.arch_linux.ed1daf0bf`. The hypothesized second focus loss behavior occurred. Starting with connected in-tree-style HSlider setup (min 0, max 10, step 1, initial 5), slider GUI focus, value_changed receipt callback, and Label, seven fresh `InputEventAction` events were each parsed and followed by a process frame. Before each event, GUI owner and slider.has_focus() were asserted. After each event, value, cumulative receipts, and Label were asserted:

| Edge | GUI owner before event | Event | Value | Receipts | Label |
|---|---|---|---:|---|---|
| 0 | HSlider | ui_right press | 6 | [6] | Value 6 |
| 1 | Button | ui_right press | 6 | [6] | Value 6 |
| 2 | Button | ui_right release | 6 | [6] | Value 6 |
| 3 | HSlider (restored) | ui_left press | 5 | [6, 5] | Value 5 |
| 4 | HSlider | ui_left release | 5 | [6, 5] | Value 5 |
| 5 | Button (second loss) | ui_left press | 5 | [6, 5] | Value 5 |
| 6 | Button | ui_left release | 5 | [6, 5] | Value 5 |

Each edge's change/no-change receipt behavior was printed, and all seven post-event checks passed. Only after the seven assertions, the scratch emitted its distinct expected-negative `push_error` and exited **2**. This matches r43's candidate result; it does not match r42's paired positive restoration result, which ended at 4 with receipts `[6,5,4]` and Label `Value 4` when the slider retained focus for the second left press.

Bounded command: `timeout 15s godot --headless --path .shokunin/game-dev-2d/corpus/live/r43-second-loss-reviewer-scratch --script res://slider_adjust.gd`
Exit code: `2` (expected negative, not timeout). Terminal output ended `R43_SECOND_FOCUS_LOSS values=6,6,6,5,5,5,5 receipts=[6.0,5.0] label=Value 5 owner_button=true`, followed by the expected-negative diagnostic. Exact run log is represented above; the scratch script itself captures all seven edge rows.

## Scratch and telemetry

My independent scratch is `.shokunin/game-dev-2d/corpus/live/r43-second-loss-reviewer-scratch/` (`project.godot`, `slider_adjust.gd`), built independently and not by editing the fixture. Script SHA256: `ec32b0e7d1115b1b14bc41f3a13b7310892b03aa1a00a970bd53e957c8ac44c0`. Two authoring attempts failed before successful execution: an untyped inferred `edge` parse error (exit 1) and a typed-array assignment error (exit 143 after termination). Both were corrected. The corrected bounded command completed promptly with expected exit 2. The parent separately reported a scratch PID hung for >2 minutes and terminated; that adverse timeout telemetry is not this successful bounded run and is not evidence for PASS. No engine/editor source or fixture was edited.

Scope is synthetic parsed events plus process frames only, not OS auto-repeat, physical keyboard/timing, rendered/pointer UI, accessibility, production, or generic slider behavior. Assertions establish GUI ownership and state/receipts/Label after every requested edge, not internal consumption of unchanged edges.
