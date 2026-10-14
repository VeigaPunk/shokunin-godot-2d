# Round 50 release scout

- Role: leaf scout; no delegation. No tracked fixture/runner edits.
- Godot: `4.7.2.stable.arch_linux.ed1daf0bf`.
- Unique bounded scratch: `/tmp/r50-release-scout-f88sgzg7` (copied fixture project; only scratch `slider_adjust.gd` edited).
- Invocation: `godot --headless --path /tmp/r50-release-scout-f88sgzg7/project --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --release-after-late-reconnect-press`.
- Result: exit 2 as expected after the eleven edge checks. Terminal marker: `SLIDER_RELEASE_AFTER_LATE_RECONNECT_PRESS values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true`; distinct diagnostic states expected no new receipt after eleven checks.
- Before every edge, scratch asserted expected GUI focus owner and callback connection state; after each dispatched parsed action and frame, it asserted numeric value, full cumulative receipts, and Label. Reconnection occurs after edge7; edge9 fresh left press changes 4→3 and adds receipt 3; edge10 release leaves 3/[6,3]/Value 3.
- Hypothesis corroborated in this bounded scratch. This is synthetic parsed-event/frame evidence only; no OS repeat, physical input/timing, rendered/pointer UI, accessibility, production, generic slider, or broader signal-consumer claim.
- Worktree/standing brief says preserve prior 74 and HOLD on any Godot mismatch. No tracked edits or commit made by scout.
