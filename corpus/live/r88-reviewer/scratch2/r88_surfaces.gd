extends SceneTree
# reviewer r88: the author's _arm_sprite_phys logic verbatim, in a small file
# (no arm dispatch, no other arms) — startup-time mode probe.
func _initialize() -> void:
	call_deferred("_run")
func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]
func _body(x: float, y: float, gs := 1.0) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(x, y)
	b.gravity_scale = gs
	return b
func _run() -> void:
	var results: PackedStringArray = []
	for variant in ["plain", "flipped", "regioned", "scaled_neg"]:
		var b := _body(variant.length() * 50, -50)
		var spr := Sprite2D.new()
		var img := Image.create(16, 16, false, Image.FORMAT_RGBA8)
		spr.texture = ImageTexture.create_from_image(img)
		b.add_child(spr)
		match variant:
			"flipped": spr.flip_h = true; spr.flip_v = true
			"regioned": spr.region_enabled = true; spr.region_rect = Rect2(2, 2, 4, 4); spr.hframes = 2; spr.frame = 3
			"scaled_neg": spr.scale = Vector2(-1, -1)
		root.add_child(b)
	for i in 30:
		await physics_frame
	for b in root.get_children():
		if b is RigidBody2D:
			var spr: Sprite2D = null
			for c in b.get_children():
				if c is Sprite2D: spr = c
			results.append("pos=%.4f,%.4f spr_rel=%s" % [b.global_position.x, b.global_position.y, spr.transform])
	print("AR MX [%s]" % "|".join(results))
	quit(0)
