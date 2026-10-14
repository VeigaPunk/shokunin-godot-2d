# Round 5 animation scout — Godot 4.7.2

Read-only probe run on `/usr/bin/godot` (`4.7.2.stable.arch_linux.ed1daf0bf`), using a temporary SceneTree script and the fixture project path. The deterministic route works without editor or project-source changes:

1. Add a named `Node2D` and an `AnimationPlayer` to the SceneTree root.
2. Build an in-memory one-second `Animation` with a `TYPE_VALUE` track at `Animated:position`, keys `(0, Vector2.ZERO)` and `(1, Vector2(100, 0))`; put it in an `AnimationLibrary` and add the library to the player under `""`.
3. Await `process_frame` so the target path resolves. Call `player.play("move")`, record the target position, then call `player.advance(0.5)` synchronously and record again.

Observed positive output: `before=(0.0, 0.0) after=(50.0, 0.0) playing=true position=0.500`. This demonstrates a property change from an explicit bounded advance, not elapsed wall-clock timing.

Same assertion can detect a stuck control: reset target to `Vector2.ZERO`, replay, set `player.speed_scale = 0.0`, record before/after `advance(0.5)`, and require a position delta. Observed control: `before=(50.0, 0.0) after=(50.0, 0.0) playing=true position=0.500`; `is_playing()` stays true, so do not use it alone as evidence of animation progress. Use a position delta (e.g. length > 1) as the shared assertion: positive passes, zero-speed control fails it.

A `stop()` control also leaves the property unchanged, but `current_animation_position` emits `AnimationPlayer has no current animation` after stop; zero `speed_scale` avoids that unrelated error and more cleanly models a stuck-but-playing animation. Probe tested in-memory property state only; it does not establish rendered motion, visual smoothness, production scene wiring, or audio/juice quality. No repository fixture or engine/editor files were changed by this scout.
