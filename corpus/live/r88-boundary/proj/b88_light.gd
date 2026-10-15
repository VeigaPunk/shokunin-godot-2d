extends SceneTree
# r88 BOUNDARY seat — light_props: hang class of `range_height`, the `height` repair, and
# the occluder-vs-physics pin with a sharp ray + a collision control.
# Launch: godot --headless --path proj --script res://b88_light.gd -- --arm=<arm>

var arm := ""
var startup_delay_ms := 0

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--delay="):
			startup_delay_ms = int(a.substr(8))
	if arm.is_empty():
		print("R88B ARM_MISSING")
		quit(1)
		return
	print("R88B arm=%s startup_delay_ms=%d" % [arm, startup_delay_ms])
	if startup_delay_ms > 0:
		OS.delay_msec(startup_delay_ms)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"hang_min": _arm_hang_min()
		"fixed": _arm_fixed()
		"fixed_sync": _arm_fixed_sync()
		"control": _arm_control()
		_:
			print("R88B unknown_arm=%s" % arm)
			quit(2)

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _tri() -> PackedVector2Array:
	return PackedVector2Array([Vector2(0, 0), Vector2(10, 0), Vector2(10, 10)])

func _body(x: float, y: float) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(x, y)
	return b

func _own_props(cls: String, no_inherit: bool) -> PackedStringArray:
	var out: PackedStringArray = []
	for p in ClassDB.class_get_property_list(cls, no_inherit):
		out.append(String(p.get("name", "")))
	return out

func _has_prop(cls: String, prop: String) -> bool:
	for p in ClassDB.class_get_property_list(cls, true):
		if String(p.get("name", "")) == prop:
			return true
	return false

# Minimal reproduction of the scout's hang: one invalid assignment, then a marker + quit().
# If the assignment aborts the function, neither the marker nor quit() runs and the tree idles.
func _arm_hang_min() -> void:
	print("R88B hang_min own_props=%s has_range_height=%s has_height=%s" % [
		_own_props("PointLight2D", true),
		_has_prop("PointLight2D", "range_height"),
		_has_prop("PointLight2D", "height")])
	var pl := PointLight2D.new()
	root.add_child(pl)
	print("R88B hang_min before_assign")
	pl.range_height = 42.0
	print("R88B hang_min UNREACHABLE_AFTER_ASSIGN")
	quit()

# Scout's repaired leg (range_height -> height) + edge probes:
#  - the scout's original ray is vertical at x=-50 and never crosses the occluder polygon
#    (global x in [0,10]) -> add a sharp horizontal ray through the polygon's interior;
#  - print the polygon's global vertices and a point-in-polygon witness for the sharp ray.
func _arm_fixed() -> void:
	var pl := PointLight2D.new()
	var dl := DirectionalLight2D.new()
	var occ := LightOccluder2D.new()
	var poly := OccluderPolygon2D.new()
	poly.polygon = _tri()
	poly.closed = true
	occ.occluder = poly
	var cm := CanvasModulate.new()
	root.add_child(pl)
	root.add_child(dl)
	root.add_child(occ)
	root.add_child(cm)
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
	print("R88B fixed pl=[en=%s sh=%s en2=%.3f ts=%.3f h=%.3f col=%s mask=%d mo=%s]" % [
		pl.enabled, pl.shadow_enabled, pl.energy, pl.texture_scale, pl.height, pl.color,
		pl.range_item_cull_mask, pl.shadow_item_cull_mask],
		" dl=[en=%.3f mask=%d]" % [dl.energy, dl.range_item_cull_mask],
		" occ=[closed=%s cull=%d mask=%d sdf=%s n=%d]" % [
			poly.closed, poly.cull_mode, occ.occluder_light_mask, occ.sdf_collision,
			poly.polygon.size()],
		" cm=[col=%s]" % cm.color)
	occ.position = Vector2(0, -40)
	var tri_global: Array = []
	for v in poly.polygon:
		tri_global.append(_v2(occ.to_global(v)))
	print("R88B fixed tri_global=[%s] pip_local_mid=%s pip_local_far=%s" % [
		";".join(tri_global),
		Geometry2D.is_point_in_polygon(Vector2(7, 5), poly.polygon),
		Geometry2D.is_point_in_polygon(Vector2(20, 5), poly.polygon)])
	var b := _body(0, -100)
	root.add_child(b)
	for i in 40:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q_orig := PhysicsRayQueryParameters2D.create(Vector2(-50, -80), Vector2(-50, 60))
	var hit_orig := dss.intersect_ray(q_orig)
	var q_sharp := PhysicsRayQueryParameters2D.create(Vector2(-50, -35), Vector2(50, -35))
	var hit_sharp := dss.intersect_ray(q_sharp)
	print("R88B fixed body_y=%.4f ray_orig_empty=%s ray_sharp_empty=%s occ_cls=%s occ_is_co=%s height_after=%.3f" % [
		b.global_position.y, hit_orig.is_empty(), hit_sharp.is_empty(), occ.get_class(),
		is_instance_of(occ, CollisionObject2D), pl.height])
	quit()

# Sync-anchored variant of the repaired leg: skip emissions until the body's first
# integration is visible, then count 39 more (40 integrations from rest) — the recipe
# that is immune to the startup step-count race.
func _arm_fixed_sync() -> void:
	var occ := LightOccluder2D.new()
	var poly := OccluderPolygon2D.new()
	poly.polygon = _tri()
	poly.closed = true
	occ.occluder = poly
	root.add_child(occ)
	occ.position = Vector2(0, -40)
	var b := _body(0, -100)
	root.add_child(b)
	var guard := 0
	while b.linear_velocity.y == 0.0 and guard < 5:
		await physics_frame
		guard += 1
	var v1 := b.linear_velocity.y
	for i in 39:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q_sharp := PhysicsRayQueryParameters2D.create(Vector2(-50, -35), Vector2(50, -35))
	var hit_sharp := dss.intersect_ray(q_sharp)
	print("R88B fixed_sync guard=%d v1=%.4f body_y=%.4f ray_sharp_empty=%s occ_is_co=%s" % [
		guard, v1, b.global_position.y, hit_sharp.is_empty(),
		is_instance_of(occ, CollisionObject2D)])
	quit()

# Collision control: the same triangle, at the same place, as real collision geometry.
# If the dropped body is stopped and the sharp ray hits, the occluder pin's coordinates
# genuinely intersect collision-relevant geometry (the occluder arm's "pass-through" is
# not vacuous). If not, the whole pin family is geometrically empty.
func _arm_control() -> void:
	var sb := StaticBody2D.new()
	var cp := CollisionPolygon2D.new()
	cp.polygon = _tri()
	sb.add_child(cp)
	sb.position = Vector2(0, -40)
	root.add_child(sb)
	var b := _body(0, -100)
	root.add_child(b)
	for i in 40:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q_sharp := PhysicsRayQueryParameters2D.create(Vector2(-50, -35), Vector2(50, -35))
	var hit_sharp := dss.intersect_ray(q_sharp)
	var q_orig := PhysicsRayQueryParameters2D.create(Vector2(-50, -80), Vector2(-50, 60))
	var hit_orig := dss.intersect_ray(q_orig)
	print("R88B control body_y=%.4f ray_sharp_empty=%s ray_orig_empty=%s sb_cls=%s" % [
		b.global_position.y, hit_sharp.is_empty(), hit_orig.is_empty(), sb.get_class()])
	quit()
