# Round 49 fresh-after-reconnect critic — adversarial review

## Verdict: causal scratch supports the narrow claim; no tracked edits

Read-only reviewer. Godot 4.7.2 scratch is isolated at `.shokunin/game-dev-2d/corpus/live/r49-fresh-after-reconnect-critic-scratch/`; raw invocation output is `godot.log`, script `project/r49_scratch.gd`. Ran the same nine parsed events and frame waits as r48, then a single parsed `ui_left` press and one frame. Godot exited 0 after the tenth assertion: numeric 3, receipts `[6,3]`, Label `Value 3`. This is synthetic/headless evidence, not the tracked branch or battery replay.

## Timing and ownership review

The r48 history's relevant ordering is sound: edge0 verifies value 6, `[6]`, `Value 6` while connected, then disconnects; edge7 verifies value 4, `[6]`, `Value 6` while disconnected, then reconnects. Edge8 is a slider-owned release with the callback connected; it leaves the value and consumer state unchanged. A following fresh press, still with slider focus and the callback connected, changes 4 to 3 and emits the new receipt. It is not a replay of the earlier missed edge7 change. The scratch directly observed this result.

For the dedicated mode, assert focus owner immediately before **each** of all ten action edges (including edge9), and assert numeric value, cumulative receipts, and Label immediately after each awaited frame. Specifically check callback connected before edge0 and edge9; disconnected after edge0 and before/through edge7; reconnect only after edge7's retained consumer state is asserted; connected after reconnect and on edges8/9. Edge9 must be only a press, not a synthesized release; its expected values are `6,6,6,5,5,5,5,4,4,3`, receipts `[6]` through edge8 then `[6,3]`, and Label `Value 6` through edge8 then `Value 3`.

Terminal classification must distinguish this new branch: print its unique positive marker and exit 0 only after all ten owner/state checks and terminal connected-state assertion. Keep r48's nine-edge expected-negative path and marker/exit2 unchanged. Require both `--repeat-right` and `--second-focus-restore` plus the distinct `--press-after-late-reconnect` flag, and ensure mode ordering does not consume the new flag in another branch. The added runner row should recognize only that marker/exit0; a truncated sequence, wrong value, missing receipt, stale label, bad owner, or wrong connection state must not pass.

## Scope / caveats

The scratch supports this one parsed `ui_left` press after the late reconnect. It does not establish held-key repeat, OS repeat, physical event timing, rendered/pointer interaction, accessibility, production behavior, or arbitrary signal replay. No tracked fixture/runner was changed and no battery run was performed.
