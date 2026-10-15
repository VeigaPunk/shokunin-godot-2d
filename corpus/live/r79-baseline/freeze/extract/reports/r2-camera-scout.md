# Round 2 camera scout: Godot 4.7.2 headless behavior and fixture conventions

## Environment and scope

`godot --version` in this workspace reports `4.7.2.stable.arch_linux.ed1daf0bf`. This is read-only scouting; no fixture or runner was changed. The seeded project declares `config/features=PackedStringArray("4.7")`.

## Camera2D behavior relevant to a headless probe

A `Camera2D` does not expose a built-in target/node-follow reference in the ordinary Godot 4 API: following a target is implemented by parenting the camera under the target (or by a script that copies the target transform). To make a deterministic hierarchy-follow fixture, use a fresh `Node2D` target, add an enabled `Camera2D` as its child, disable position smoothing, set zero offset/rotation and unrestricted limits, and make the camera current. Move the target to a distinct global position after initialization, await a process frame, then inspect camera/viewport state.

The useful observable is `Camera2D.get_screen_center_position()` (the camera's effective screen center), not a rendered screenshot. Check `Camera2D.is_current()` as a setup/precondition. A positive probe can assert the target moved and that the effective screen center follows it to the expected position (with a small Vector2 tolerance); also verify it differs from the original center. In headless mode this tests scene-tree/viewport camera state, not pixel rendering or visual framing. Avoid smoothing, limits, drag margins, and offset because each can make screen center differ legitimately from target position. If a fresh headless viewport's effective screen center is not initialized until a frame after `make_current()`, await that setup frame before capturing the baseline.

This proposal is falsifiable: a positive test fails if the target is moved but effective center remains at its baseline or fails to reach the target position after the settling frame. Confirm exact API/runtime behavior in the executor's scratch-only probe; this report did not mutate or execute a new camera fixture.

## Existing fixture and battery conventions

- Fixture scripts live under `corpus/fixtures/controls/`, are standalone `extends SceneTree` scripts, and schedule asynchronous work with `call_deferred("_run")` or `call_deferred` equivalents. They await `process_frame` / `physics_frame`, print a stable `PASS ...` signature, and `quit(0)`; failures use `push_error(...)` and nonzero exit.
- Negative controls intentionally prove absence/rejection and have an expected exit of 1 plus a specific output signature. Examples: `controls/input_route_negative.gd`, `controls/overlap_negative.gd`, and `controls/scene_transition_negative.gd`.
- `run_battery.py` copies the fixture tree to a timestamped scratch project, then runs each script as `godot --headless --path <scratch> --script res://...`; `CASES` declares expected exit and signature. It rejects parse/script errors even when an expected negative exit/signature appears. Seeded fixtures must remain unchanged; scratch mutations are explicitly permitted by the runner pattern.
- Each subprocess has an 8-second timeout. The battery emits `verdicts.json`; case output should therefore carry a unique, stable positive/negative signature suitable for checking by the case table.
- Other probes use bounded frame waits (commonly 8 frames for input delivery and 120 as a global watchdog), explicit state preconditions, and report relevant counts/state in PASS output. Camera probe should bound settling frames rather than wait indefinitely.

## Suggested moved-target assertion and negative control

**Positive (`camera_follow.gd`):** create target and child camera; make current; await setup frame(s); record the baseline effective screen center; move target to e.g. `Vector2(137, -53)`; assert target really moved; await a frame (or bounded few frames); assert camera remains current and `get_screen_center_position().distance_to(target.global_position) < 0.01`, and that the center differs from baseline. Print a signature such as `PASS camera_follow moved=true current=true center_matches_target=true` and exit 0. The unusual target coordinates make an accidental unchanged/default position easy to catch.

**Negative control (`camera_follow_negative.gd`):** use the same assertions but deliberately leave the camera detached from the target (or, equivalently, use a scratch-only no-follow mutation that omits the follow relationship). Move the target to the same distinct location. The control must demonstrate that the target moved while the effective center did not track it, then report a stable `PASS negative_control=no_follow center_did_not_track=true` signature and exit 1, matching the suite's intentional-negative convention. If the positive assertion is merely weakened to scene load/current-camera, this control would no longer discriminate; keep the moved-position comparison central. Prefer detached camera to `enabled=false` if the goal is specifically target-follow discrimination, since a disabled camera tests camera activation instead.

The API details above are grounded in Godot 4 Camera2D semantics; whether `get_screen_center_position()` is reliably updated by a headless viewport in this exact runner setup remains an explicit executor validation point.
