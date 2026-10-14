# Round 20 top-edge camera scout

## Scope
Read-only scout. Read `.shokunin/game-dev-2d/LOG.md` Round 20 declaration and `/tmp/mission-game-dev-2d-standing.md`; inspected the existing `camera_limit.gd` and `run_battery.py`. No seeded fixture, runner, engine/editor, or controls edits. Scratch only: `.shokunin/game-dev-2d/corpus/live/r20-top-scout-scratch/`.

## Godot API and expected viewport behavior
The fixture uses a `Camera2D` attached to a `Node2D` parent; `Camera2D.limit_top` is the authored upper world-coordinate boundary. With an active camera and limits enabled, camera screen-center position is constrained based on the viewport dimensions. For a 64×64 headless viewport and `limit_top = -500`, the expected top-clamped center y is `limit_top + visible_rect.size.y / 2 = -468` (assuming default zoom/offset and no smoothing). The active center must move away from its initial y=0, yet remain distinct from a parent target moved to y=-2000. A very distant top limit should allow the center to track that target and thereby fail the same bounded-center assertion.

## Scratch evidence
Godot version: `4.7.2.stable.arch_linux.ed1daf0bf`.

I staged a scratch copy of the fixtures and ran a minimal top-limit probe:

`cd .shokunin/game-dev-2d/corpus/live/r20-top-scout-scratch && godot --headless --path . --script res://top_probe.gd`

Exit 0; output observed viewport `S: (64.0, 64.0)`, `limit_top -500`, target y `-2000`, and active screen center y `-468` (the predicted top boundary plus half viewport). This confirms the positive assertion is feasible in the current headless runtime.

Then ran the same scratch script with `-- --far-top-bound`; it sets `limit_top = -100000`:

`cd .shokunin/game-dev-2d/corpus/live/r20-top-scout-scratch && godot --headless --path . --script res://top_probe.gd -- --far-top-bound`

Exit 0; observed center y `-2000`, equal to target y, so the far-top control should fail a positive test's expected-clamp/separation assertion. This is a scratch feasibility probe, not battery evidence.

## Recommendation / caveats
Implement the top check symmetrically to existing right-edge logic: expected center y is `authored_top_boundary + viewport_height / 2`; require it to be at/near that value, above (numerically >=) the authored top boundary, advanced from the pre-move center, and separated from the moved target. The control should reuse that assertion and emit a deliberate camera-limit assertion diagnostic only after confirming target movement and current-camera setup. Keep expected signature and control exit aligned with the existing runner's classification contract. Headless viewport size is observed dynamically as 64×64 here; do not hard-code it. This establishes Camera2D limit state, not rendered pixels or production camera behavior.
