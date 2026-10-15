# Round 38 edge assertion simplifier — read-only design

Keep the four event injections and `await process_frame` boundaries. Assert the observable tuple `(slider.value, value_receipts, label.text)` immediately after each awaited edge; do not add assertions to `_action` (it is shared by all modes and currently only injects the event), or infer a press result from the later release snapshot.

| Edge | Focused, connected | Focused, disconnected | No focus |
|---|---|---|---|
| ui_right press | `(6, [6], "Value 6")` | `(6, [], "Value 5")` | `(5, [], "Value 5")` |
| ui_right release | `(6, [6], "Value 6")` | `(6, [], "Value 5")` | `(5, [], "Value 5")` |
| ui_left press | `(5, [6,5], "Value 5")` | `(5, [], "Value 5")` | `(5, [], "Value 5")` |
| ui_left release | `(5, [6,5], "Value 5")` | `(5, [], "Value 5")` | `(5, [], "Value 5")` |

Implement as one short mode-specific sequence of four expected tuples, checked after the existing four awaits. This is simpler and less error-prone than separate snapshots (`right_value`, `right_receipts`, etc.) plus pair-level conditions: the second tuple explicitly detects a duplicate release, and the left-press tuple checks the cumulative receipt sequence. Preserve the current setup/focus checks and final intentional negative diagnostics; the disconnected and no-focus controls should still be distinguished by their value expectations. No new CASES, helper abstraction, signal emission, or action injection is needed. The table is a proposed assertion contract, contingent on the scout/executor's real Godot edge measurement; it is not independent evidence that those transitions occurred.
