# Round 23 mutation review — authored-left limit sabotage

Scope: independent scratch-only check of the proposed left-edge Camera2D pair. No delegation. No tracked fixture edits were made by this reviewer; probe is at `corpus/live/r23-mutation-reviewer-scratch/camera_limit.gd`.

The scratch probe establishes `camera.limit_left=-1000`, moves the parent target to `(-2000, 0)`, and checks active center against the viewport-adjusted authored edge (`-1000 + viewport_width/2`). Godot 4.7.2 headless positive exited 0 with `PASS camera_limit left=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true far_left=false` (actual viewport half-width 32px; center x=-968).

Sabotage changes only the authored left limit to `-100000`, leaving target and assertion unchanged. The far-left run exited 2, printed center `(-2000,0)` equal to target, expected `-968`, and emitted `camera limit assertion failed: expected active center within left boundary and distinct from target`. Thus the positive is bounded by the actual authored limit and the far-left control fails the same intended center assertion, not setup. This is headless center-state evidence only; it does not establish rendered framing or any other camera behavior.

Command shape: `godot --headless --path <scratch> --script res://camera_limit.gd [-- --far-left-bound]`. No engine/editor launch, seeded control, or source mutation. Tracked executor files showed pre-existing workspace modifications at inspection, but this reviewer did not edit them.
