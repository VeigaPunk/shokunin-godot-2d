extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _mk_wall(pos: Vector2, size: Vector2) -> StaticBody2D:
	var b := StaticBody2D.new()
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	root.add_child(b)
	return b
func _run() -> void:
	_mk_wall(Vector2(40, 40), Vector2(20, 4))
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(8, 128)
	cs.shape = rs
	b.add_child(cs)
	b.position = Vector2(0, 0)
	b.gravity_scale = 0.0
	b.can_sleep = false
	b.angular_damp = 0.0
	b.contact_monitor = true
	b.max_contacts_reported = 4
	b.body_entered.connect(func(n: Node) -> void: print("HIT pos=%s" % str(b.global_position)))
	root.add_child(b)
	b.angular_velocity = TAU * 15.0
	print("default_angular_damp=%s" % ProjectSettings.get_setting("physics/2d/default_angular_damp"))
	for i in 8:
		await physics_frame
		var axis := b.transform.y.normalized()
		# discrete overlap check at the CURRENT sampled pose
		var p := PhysicsTestMotionParameters2D.new()
		p.from = b.global_transform
		p.motion = Vector2.ZERO
		var r := PhysicsTestMotionResult2D.new()
		var hit := PhysicsServer2D.body_test_motion(b.get_rid(), p, r)
		print("step%d rot=%.2f axisY=%s pos=%s overlap=%s av=%.1f" % [
			i, rad_to_deg(fposmod(b.rotation, TAU)), axis, b.global_position, hit, rad_to_deg(b.angular_velocity)])
	quit(0)
