# Round 50 repair critic — edge-10 release-state evidence

- Role: leaf critic; no delegation, no tracked edits.
- Godot: `4.7.2.stable.arch_linux.ed1daf0bf`.
- Unique scratch: `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r50-repair-critic-20261013T090528343674Z`. Seeded fixture/runner copied from tracked corpus; history lessons staged only to make scratch self-contained.
- Tracked hashes observed: `slider_adjust.gd` `abf833021df686f01d6778646a9d1a96bbabab00905bcb554ac7f8e2d68e7434`; `run_battery.py` `4afc03127ecd13d274eb6bfe8f569bbdd849108558b3884c8d7247775ad3d77c`. No tracked tree modifications by this critic.

## Clean and no-dispatch pair

Clean invocation:

`godot --headless --path '/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r50-repair-critic-20261013T090528343674Z/seed' --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --release-after-late-reconnect-press`

Exit **2**. It emits the complete eleven-edge marker (`values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true`) and then the exact expected terminal diagnostic `ERROR: SLIDER RELEASE AFTER LATE-RECONNECT PRESS ASSERTION FAILED: expected no new receipt after eleven checks`.

No-dispatch sabotage uses the same flags and all owner/callback prechecks, edge-state checks, frame wait and state assertions, but skips only `_action(...)` when `i == 10`. It exits **2** at `ERROR: SLIDER input-state post-release assertion failed: ui_left remains pressed`; neither the eleven-edge marker nor the terminal diagnostic appears. This is a real dispatch omission (not release replaced by press). Applying the production classifier rules (`classify_process`: expected exit/signature, no unallowed `ERROR:`, `SCRIPT ERROR:` or parse error; this case's expected_errors entry permits only the exact terminal diagnostic), the result is **rejected**: required terminal signature absent and the post-release `ERROR:` is unallowed. This reproduces the fix for the initial false-PASS.

Paired prior positive:

`godot --headless --path <seed> --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --press-after-late-reconnect`

Exit **0**, marker `PASS slider_adjust_repeat_second_focus_restore_press_after_late_reconnect values=6,6,6,5,5,5,5,4,4,3 receipts=6,3 Labels=Value 6,Value 3`. This is the r49 10-edge positive path and remains unaffected by repair.

## Adversarial limit / scope

I additionally replaced edge10 dispatch with `Input.action_release("ui_left")` (directly clears the synthetic action state without dispatching the edge's `InputEventAction`), retaining the frame, state, numeric/receipt/Label checks. It passes those checks, prints the eleven-edge marker, and reaches the exact expected-negative terminal diagnostic (exit 2). Thus pre/post `Input.is_action_pressed` distinguishes omission but not an alternate direct state-clear that bypasses the declared parsed release event. This is a limitation if the threat model includes arbitrary state mutation; it does not invalidate the specifically requested exact omission sabotage or establish parsed-event dispatch independently against that stronger mutation. Keep claim narrow: synthetic action-state transition under the ordinary `_action` path, with targeted omission detection; no generic dispatch instrumentation, OS/physical input or timing, render/UI, accessibility, or production claim.

No verdict/promotion opinion beyond this repair challenge. Scratch runs retained above; no commit, push, or merge.
