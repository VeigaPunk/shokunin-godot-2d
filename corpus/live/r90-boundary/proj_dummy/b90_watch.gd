extends RigidBody2D
## r90-boundary helper — forwards every `_integrate_forces` callback to `sink`
## (a Callable receiving the PhysicsDirectBodyState2D). Same shape as the scout's
## rb_watch.gd; the boundary probe reads live state and proves write-through.
var sink: Callable

func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
	if sink.is_valid():
		sink.call(state)
