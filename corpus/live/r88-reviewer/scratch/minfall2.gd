extends SceneTree
# reviewer variant: prefix work before body creation (author-arm shape)
var arm := ""
func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")
func _run() -> void:
	print("arm=%s" % arm)
	match arm:
		"minfall2":
			await _arm()
		_:
			quit(1)
func _arm() -> void:
	var pl := PointLight2D.new()
	var dl := DirectionalLight2D.new()
	var occ := LightOccluder2D.new()
	var cm := CanvasModulate.new()
	root.add_child(pl); root.add_child(dl); root.add_child(occ); root.add_child(cm)
	pl.enabled = true; pl.shadow_enabled = true; pl.energy = 2.5; pl.texture_scale = 1.5
	pl.height = 42.0; pl.color = Color(0.5, 0.25, 0.125); pl.range_item_cull_mask = 4
	var s := "pl=[en=%s sh=%s en2=%.3f]" % [pl.enabled, pl.shadow_enabled, pl.energy]
	print("R88S light %s" % s)
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
	print("MINFALL2 %s" % " ".join(ys))
	quit(0)
