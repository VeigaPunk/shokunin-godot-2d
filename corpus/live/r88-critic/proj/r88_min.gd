extends SceneTree
# r88-critic minimal startup-mode probe: same arm shape as r88_surfaces.gd's
# sprite_phys (deferred _run, body at (250,-50), 30 awaited physics frames),
# but with a minimal file so engine+script startup cost is lower.
func _initialize() -> void:
	print("T0 %d" % Time.get_ticks_usec())
	call_deferred("_run")

func _run() -> void:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(250, -50)
	b.gravity_scale = 1.0
	root.add_child(b)
	var first_v := ""
	for i in 30:
		await physics_frame
		if i == 0:
			first_v = str(b.linear_velocity)
	print("PASS r88_min mode first_v=%s y30=%.4f phys_frames=%d" % [
		first_v, b.global_position.y, Engine.get_physics_frames()])
	quit(0)
