extends RigidBody2D
## r90-scout helper — forwards every `_integrate_forces` callback to `sink` (a Callable
## receiving the PhysicsDirectBodyState2D). Used by rb_lattice.gd to read live state
## (total_gravity/total_linear_damp/inverse_inertia/step) and to prove write-through.
var sink: Callable

func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
	if sink.is_valid():
		sink.call(state)
