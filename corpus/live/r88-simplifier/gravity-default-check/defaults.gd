extends SceneTree
# r88-simplifier: independent readback of the default the folded _body relies on.
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var b := RigidBody2D.new()
	print("DEFAULT gravity_scale=%.4f (fold relies on 1.0)" % b.gravity_scale)
	var cs := CollisionShape2D.new()
	var c := CircleShape2D.new()
	c.radius = 8.0
	cs.shape = c
	b.add_child(cs)
	root.add_child(b)
	b.position = Vector2(0, -100)
	for i in 40:
		await physics_frame
	print("DEFAULT-BODY y40=%.4f" % b.global_position.y)
	quit(0)
