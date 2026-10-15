extends SceneTree
# reviewer variant: 200ms sync delay inside _run() before body creation
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	OS.delay_msec(200)
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var c := CircleShape2D.new(); c.radius = 8.0
	cs.shape = c
	b.add_child(cs)
	b.position = Vector2(0, -50)
	root.add_child(b)
	var ys: Array = []
	for i in 30:
		await physics_frame
		if i == 0 or i == 29:
			ys.append("i=%d y=%.4f v=%.4f" % [i, b.global_position.y, b.linear_velocity.y])
	print("MINFALL3 %s" % " ".join(ys))
	quit(0)
