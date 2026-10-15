extends SceneTree
# r88-critic strip probe #2: the author's EXACT _arm_light_props code
# (verbatim, lines 241-281 of corpus/fixtures/r88_surfaces.gd) in a minimal
# file — startup-cost control for the body_y pin.

func _initialize() -> void:
	call_deferred("_run")

func _finish(line: String) -> void:
	print("PASS r88_surfaces " + line)
	quit(0)

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
	await _arm_light_props()

func _arm_light_props() -> void:
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
	pl.height = 42.0  # the verbatim leg's `range_height` is not a 4.7.2 property
	pl.color = Color(0.5, 0.25, 0.125)
	pl.range_item_cull_mask = 4
	dl.energy = 0.75
	occ.occluder_light_mask = 2
	occ.sdf_collision = true
	cm.color = Color(0.2, 0.2, 0.4)
	var pl_str := "pl=[en=%s sh=%s en2=%.3f ts=%.3f h=%.3f col=%s mask=%d mo=%s]" % [
		pl.enabled, pl.shadow_enabled, pl.energy, pl.texture_scale, pl.height,
		pl.color, pl.range_item_cull_mask, pl.shadow_item_cull_mask]
	var dl_str := "dl=[en=%.3f mask=%d]" % [dl.energy, dl.range_item_cull_mask]
	var occ_str := "occ=[closed=%s cull=%d mask=%d sdf=%s n=%d]" % [
		poly.closed, poly.cull_mode, occ.occluder_light_mask, occ.sdf_collision, poly.polygon.size()]
	var cm_str := "cm=[col=%s]" % cm.color
	print("R88S light_props %s %s %s %s" % [pl_str, dl_str, occ_str, cm_str])
	var b := _body(0, -100)
	occ.position = Vector2(0, -40)
	root.add_child(b)
	for i in 40:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q := PhysicsRayQueryParameters2D.create(Vector2(-50, -80), Vector2(-50, 60))
	var hit := dss.intersect_ray(q)
	_finish("light_props %s %s %s %s body_y=%.4f ray_through_occluder=%s occ_cls=%s occ_is_co=%s" % [
		pl_str, dl_str, occ_str, cm_str,
		b.global_position.y, hit.is_empty(), occ.get_class(),
		is_instance_of(occ, CollisionObject2D)])
