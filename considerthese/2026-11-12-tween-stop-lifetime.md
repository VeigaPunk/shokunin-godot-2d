# 2D: stopping a tween does not rewind its target

Godot's [Tween contract at 4.5-stable](https://github.com/godotengine/godot/blob/4.5-stable/doc/classes/Tween.xml), stop, kill, is_valid and bind_node, separates controller state from animated-property state.

Stopping resets tween state and retains its tweeners, but does not restore target properties to their original values. Killing invalidates the tween. Bound tweens halt while their node is outside the tree and are killed when it is freed. Validity is therefore distinct from running state and from the target's current value. This tagged API is not runtime evidence.

**Proposed practice, unperformed:** Animate an original scalar from two to ten. At a predetermined partial progress point, branch into stop, pause and kill cases. Record target value, validity, running state and permitted restart behavior separately. Add one bound-node removal case and one freeing case, checking after the appropriate lifecycle step. Set expected outcomes before running a pinned headless build. Report fixed-step schedule, object lifetime, API calls, traces and mismatches. Cap at five cases and forty-five minutes. Do not infer smooth rendering or change production animation.

This extends 2D animation lifecycle coverage, not physics interpolation or audio automation cancellation. No fixture, engine, training or assimilation was run.

Original commentary and invented scalar exercise; no source examples or code copied. Documentation reuse clearance is not asserted.

Destination: VeigaPunk/shokunin-godot-2d, main, considerthese/2026-11-12-tween-stop-lifetime.md.
