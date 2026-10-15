extends SceneTree
# reviewer r88: the author's _arm_light_props logic verbatim, small file
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
	var pl := PointLight2D.new()
	var dl := DirectionalLight2D.new()
	var occ := LightOccluder2D.new()
	var poly := OccluderPolygon2D.new()
	poly.polygon = PackedVector2Array([Vector2(0, 0), Vector2(10, 0), Vector2(10, 10)])
	poly.closed = true
	occ.occluder = poly
	var cm := CanvasModulate.new()
	root.add_child(pl); root.add_child(dl); root.add_child(occ); root.add_child(cm)
	pl.enabled = true
	pl.shadow_enabled = true
	pl.energy = 2.5
	pl.texture_scale = 1.5
	pl.height = 42.0
	pl.color = Color(0.5, 0.25, 0.125)
	pl.range_item_cull_mask = 4
	dl.energy = 0.75
	occ.occluder_light_mask = 2
	occ.sdf_collision = true
	cm.color = Color(0.2, 0.2, 0.4)
	var b := _body(0, -100)
	occ.position = Vector2(0, -40)
	root.add_child(b)
	for i in 40:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q := PhysicsRayQueryParameters2D.create(Vector2(-50, -80), Vector2(-50, 60))
	var hit := dss.intersect_ray(q)
	print("LIGHTX body_y=%.4f ray_empty=%s" % [b.global_position.y, hit.is_empty()])
	quit(0)
