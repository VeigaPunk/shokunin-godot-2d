extends SceneTree
# seat-owned minimal fall probe (reviewer r88) — boundary §2 shape:
# body created in deferred _run(), then N awaits of physics_frame.
var _b: RigidBody2D
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	_b = RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var c := CircleShape2D.new(); c.radius = 8.0
	cs.shape = c
	_b.add_child(cs)
	_b.position = Vector2(0, -50)
	root.add_child(_b)
	var ys: Array = []
	for i in 30:
		await physics_frame
		if i == 0 or i == 29:
			ys.append("i=%d y=%.4f v=%.4f" % [i, _b.global_position.y, _b.linear_velocity.y])
	print("MINFALL %s" % " ".join(ys))
	quit(0)
