# Teleports need a new interpolation history

[Godot4.7 interpolation guidance](https://docs.godotengine.org/en/4.7/tutorials/physics/interpolation/using_physics_interpolation.html) distinguishes continuous movement from initial placement. A teleport should not visually traverse the distance from its previous location.

reset_physics_interpolation sets the stored previous transform equal to the current one. Ordering matters: first place the object, then reset. For an immediately moving spawn, the documented sequence additionally sets the expected next-tick transform after resetting. This avoids spending the first interval apparently stationary.

That refinement concerns presentation history, not collision sweeps or deterministic replay. The existing replay-boundary note already separates smoothing from simulation guarantees; animation-state travel is another distinct meaning of teleport.

Ordinary interpolated movement, including parent-driven movement, belongs on physics ticks. Resetting discontinuities is not a general replacement for correctly timed movement. This is a versioned contract, not an introduction-date claim or measured rendering result. The lane's headless replay evidence does not validate visible spawn behavior. No engine settings changed.

Godot contributors' documentation is CC BY3.0; original commentary only, without copied code or assets.
