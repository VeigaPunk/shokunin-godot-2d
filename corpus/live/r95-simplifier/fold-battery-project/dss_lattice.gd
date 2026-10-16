extends SceneTree
# r95 scout FROZEN probe — PhysicsDirectSpaceState2D query lattice + ordering.
# Battery launch shape:
#   godot --headless --path proj --script res://dss_lattice.gd -- --arm=<name> [--rev]
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix
# scan); every arm prints its own name on the PASS line, so a silent `_:` fallback
# is impossible to miss.  Prints `R95 <arm> <key>=<value>` diagnostics and one
# final `PASS dss_lattice <arm> <key>=<value> ...` line (the authorable signature).
# No RIDs / object ids / addresses / instance ids are ever printed (byte-stability):
# identities are node tags, RIDs only as booleans.
#
# Measured laws this probe encodes (all [M], see reports/round-95/r95-scout.md):
#   L1 default max_results is 32 and 0 means ZERO results (not unlimited)
#   L2 point-in-shape is half-open (left/top inclusive, right/bottom exclusive)
#   L3 shape-overlap is inclusive of exact touching; per-shape entries, shape index
#   L4 ray endpoint inclusive; start point classified by the same half-open
#      predicate => a start on a right/bottom face yields a t=0 hit, normal (0,0)
#   L5 nearest-wins; coincident ties resolve to the LAST added collider
#   L6 multi-hit order is a deterministic broadphase artifact of construction +
#      layout (stable per process, perturbed by unrelated inserts/frees)
#   L7 point queries are canvas-layer scoped (canvas_instance_id; 0 = default layer)
#   L8 exclude takes BODY RIDs only (shape RIDs are inert); areas need the flag
#   L9 node-tier position writes are deferred one physics step; server-tier
#      body_set_state and add_child are live for queries in the same frame
#  L10 queries are per-space: a SubViewport world is invisible to root queries

var arm := ""
var _rev := false
var _items: PackedStringArray = []
const CAP := 32

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a == "--rev":
			_rev = true
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": await _arm_census()
		"ray_flags": await _arm_ray_flags()
		"ray_geom": await _arm_ray_geom()
		"ray_order": await _arm_ray_order()
		"point_cap": await _arm_point_cap()
		"point_edge": await _arm_point_edge()
		"point_canvas": await _arm_point_canvas()
		"shape_lattice": await _arm_shape_lattice()
		"order_core": await _arm_order_core()
		"layer_forms": await _arm_layer_forms()
		"cast_rest": await _arm_cast_rest()
		"excl_space": await _arm_excl_space()
		"fresh": await _arm_fresh()
		_: _fail("unknown_arm")

# --------------------------------------------------------------- utilities

func _fail(reason: String) -> void:
	print("FAIL dss_lattice %s reason=%s" % [arm, reason])
	quit(1)

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R95 %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS dss_lattice %s %s" % [arm, " ".join(_items)])
	quit()

func _frames(n: int) -> void:
	for i in n:
		await physics_frame

func _v2(v: Vector2) -> String:
	return "(%.4f,%.4f)" % [v.x, v.y]

func _dv(v: Variant) -> String:
	if v is Vector2:
		return _v2(v)
	if v is bool:
		return "true" if v else "false"
	if v is float:
		return "%.4f" % v
	if v is Array:
		return "n%d" % v.size()
	return str(v)

func _dss() -> PhysicsDirectSpaceState2D:
	return PhysicsServer2D.space_get_direct_state(root.world_2d.space)

func _sorted(a: Array) -> Array:
	var c := a.duplicate()
	c.sort()
	return c

func _has_prop(cls: String, prop: String) -> bool:
	for p in ClassDB.class_get_property_list(cls, true):
		if str(p.get("name")) == prop:
			return true
	return false

func _tag(d: Dictionary) -> String:
	var c: Object = d.get("collider")
	if c == null:
		if d.has("collider_id"):
			c = instance_from_id(int(d.get("collider_id")))
		if c == null:
			return "?"
	return str(c.get_meta("tag", c.get_class()))

func _ord(arr: Array) -> String:
	var parts: PackedStringArray = []
	for d in arr:
		parts.append("%s#%s" % [_tag(d), str(d.get("shape", "-"))])
	return "[%s]" % ",".join(parts)

func _setstr(arr: Array) -> String:
	var keys: Array = []
	for d in arr:
		var k := "%s#%s" % [_tag(d), str(d.get("shape", "-"))]
		if k not in keys:
			keys.append(k)
	return "[%s]" % ",".join(_sorted(keys))

func _mk_body(tag: String, pos: Vector2, size: Vector2, cls := "static") -> CollisionObject2D:
	var b: CollisionObject2D
	match cls:
		"rigid": b = RigidBody2D.new()
		"char": b = CharacterBody2D.new()
		"area": b = Area2D.new()
		_: b = StaticBody2D.new()
	b.name = tag
	b.set_meta("tag", tag)
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	root.add_child(b)
	return b

func _add_shape(b: CollisionObject2D, offset: Vector2, size: Vector2) -> void:
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	cs.position = offset
	b.add_child(cs)

func _ray(from: Vector2, to: Vector2) -> PhysicsRayQueryParameters2D:
	return PhysicsRayQueryParameters2D.create(from, to)

func _pt(pos: Vector2, canvas_id := 0) -> PhysicsPointQueryParameters2D:
	var q := PhysicsPointQueryParameters2D.new()
	q.position = pos
	if canvas_id != 0:
		q.canvas_instance_id = canvas_id
	return q

func _sh(shape: Shape2D, xform: Transform2D, motion := Vector2.ZERO) -> PhysicsShapeQueryParameters2D:
	var q := PhysicsShapeQueryParameters2D.new()
	q.shape = shape
	q.transform = xform
	q.motion = motion
	return q

func _circle(r: float) -> CircleShape2D:
	var c := CircleShape2D.new()
	c.radius = r
	return c

func _rect(size: Vector2) -> RectangleShape2D:
	var r := RectangleShape2D.new()
	r.size = size
	return r

func _rayline(tag: String, hit: Dictionary) -> String:
	if hit.is_empty():
		return "%s={}" % tag
	return "%s={%s pos=%s n=%s}" % [tag, _tag(hit), _v2(hit.get("position", Vector2.ZERO)),
		_v2(hit.get("normal", Vector2.ZERO))]

func _ri_line(ri: Dictionary) -> String:
	if ri.is_empty():
		return "{}"
	return "{%s pt=%s n=%s shape=%s}" % [_tag(ri), _v2(ri.get("point", Vector2.ZERO)),
		_v2(ri.get("normal", Vector2.ZERO)), str(ri.get("shape", "-"))]

# --------------------------------------------------------------- 1. census

func _arm_census() -> void:
	var meths: Array = []
	var sigs: Array = []
	for m in ClassDB.class_get_method_list("PhysicsDirectSpaceState2D", true):
		meths.append(str(m.get("name")))
		var args: Array = []
		for a in m.get("args", []):
			var s := "%s:%s" % [str(a.get("name")), str(a.get("type"))]
			if a.has("default_value"):
				s += "=%s" % str(a.get("default_value"))
			args.append(s)
		sigs.append("%s(%s)" % [str(m.get("name")), ",".join(args)])
	meths.sort()
	sigs.sort()
	_it("dss_methods", "n%d[%s]" % [meths.size(), ",".join(meths)])
	_it("dss_sigs", "[%s]" % "|".join(sigs))
	var skip := ["resource_local_to_scene", "resource_path", "resource_name",
		"resource_scene_unique_id", "script"]
	var keys := {"PhysicsRayQueryParameters2D": "ray", "PhysicsPointQueryParameters2D": "pt",
		"PhysicsShapeQueryParameters2D": "sh"}
	for cls in keys:
		var props: Array = []
		for p in ClassDB.class_get_property_list(cls, true):
			var nm := str(p.get("name"))
			if nm == "" or nm.begins_with("_") or nm in skip:
				continue
			props.append(nm)
		props.sort()
		var inst = ClassDB.instantiate(cls)
		var vals: Array = []
		for nm in props:
			vals.append("%s=%s" % [nm, _dv(inst.get(nm))])
		_it(str(keys[cls]), "props=[%s] defaults=[%s]" % [",".join(props), ",".join(vals)])
	_it("ray_backface", "has=%s" % str(_has_prop("PhysicsRayQueryParameters2D", "backface_collision")))
	_it("pt_canvas", "has=%s" % str(_has_prop("PhysicsPointQueryParameters2D", "canvas_instance_id")))
	var q := _ray(Vector2(1, 2), Vector2(3, 4))
	_it("ray_create", "from=%s to=%s mask=%d excl=%d bodies=%s areas=%s inside=%s" % [
		_v2(q.from), _v2(q.to), q.collision_mask, q.exclude.size(),
		str(q.collide_with_bodies), str(q.collide_with_areas), str(q.hit_from_inside)])
	_it("dss_cls", "cls=%s" % PhysicsServer2D.space_get_direct_state(root.world_2d.space).get_class())
	_it("dss_identity", "same_across_calls=%s" % str(_dss() == _dss()))
	_pass()

# --------------------------------------------------------------- 2. ray flags

func _arm_ray_flags() -> void:
	var wall := _mk_body("w", Vector2(100, 0), Vector2(4, 400))
	var area := _mk_body("w2", Vector2(300, 0), Vector2(4, 400), "area")
	await _frames(2)
	var dss := _dss()
	_it("base", _rayline("r", dss.intersect_ray(_ray(Vector2(0, 0), Vector2(400, 0)))))
	var m2 := _ray(Vector2(0, 0), Vector2(400, 0))
	m2.collision_mask = 2
	_it("mask2", _rayline("r", dss.intersect_ray(m2)))
	var m0 := _ray(Vector2(0, 0), Vector2(400, 0))
	m0.collision_mask = 0
	_it("mask0", _rayline("r", dss.intersect_ray(m0)))
	var nb := _ray(Vector2(0, 0), Vector2(400, 0))
	nb.collide_with_bodies = false
	_it("nobodies", _rayline("r", dss.intersect_ray(nb)))
	var ar := _ray(Vector2(0, 0), Vector2(400, 0))
	ar.collide_with_areas = true
	_it("areas_on", _rayline("r", dss.intersect_ray(ar)))
	var ar2 := _ray(Vector2(0, 0), Vector2(400, 0))
	ar2.collide_with_areas = true
	ar2.collide_with_bodies = false
	_it("areas_only", _rayline("r", dss.intersect_ray(ar2)))
	var ex := _ray(Vector2(0, 0), Vector2(400, 0))
	ex.exclude = [wall.get_rid()]
	_it("excl_wall", _rayline("r", dss.intersect_ray(ex)))
	var ex2 := _ray(Vector2(0, 0), Vector2(400, 0))
	ex2.exclude = [area.get_rid()]
	_it("excl_area", _rayline("r", dss.intersect_ray(ex2)))
	_it("inside_off", _rayline("r", dss.intersect_ray(_ray(Vector2(100, 0), Vector2(400, 0)))))
	var in_on := _ray(Vector2(100, 0), Vector2(400, 0))
	in_on.hit_from_inside = true
	_it("inside_on", _rayline("r", dss.intersect_ray(in_on)))
	var ia := _ray(Vector2(300, 0), Vector2(400, 0))
	ia.hit_from_inside = true
	ia.collide_with_areas = true
	_it("inside_area_on", _rayline("r", dss.intersect_ray(ia)))
	var out_on := _ray(Vector2(0, 0), Vector2(400, 0))
	out_on.hit_from_inside = true
	_it("outside_on", _rayline("r", dss.intersect_ray(out_on)))
	_it("keys", str(_sorted(dss.intersect_ray(_ray(Vector2(0, 0), Vector2(400, 0))).keys())))
	_pass()

# --------------------------------------------------------------- 3. ray geometry

func _arm_ray_geom() -> void:
	_mk_body("w", Vector2(100, 0), Vector2(4, 400))
	_mk_body("c", Vector2(200, 0), Vector2(40, 40))
	await _frames(2)
	var dss := _dss()
	_it("end_at_face", _rayline("r", dss.intersect_ray(_ray(Vector2(0, 0), Vector2(98, 0)))))
	_it("end_eps_before", _rayline("r", dss.intersect_ray(_ray(Vector2(0, 0), Vector2(97.9999, 0)))))
	_it("graze_top", _rayline("r", dss.intersect_ray(_ray(Vector2(0, -200), Vector2(400, -200)))))
	_it("graze_inside", _rayline("r", dss.intersect_ray(_ray(Vector2(0, -199.999), Vector2(400, -199.999)))))
	_it("corner_diag", _rayline("r", dss.intersect_ray(_ray(Vector2(160, -40), Vector2(200, 0)))))
	_it("zero_len_face", _rayline("r", dss.intersect_ray(_ray(Vector2(98, 0), Vector2(98, 0)))))
	_it("zero_len_out", _rayline("r", dss.intersect_ray(_ray(Vector2(0, 0), Vector2(0, 0)))))
	_it("reverse", _rayline("r", dss.intersect_ray(_ray(Vector2(400, 0), Vector2(0, 0)))))
	# boundary starts: the start point is classified by the half-open predicate
	_it("from_left_away", _rayline("r", dss.intersect_ray(_ray(Vector2(98, 0), Vector2(0, 0)))))
	_it("from_left_through", _rayline("r", dss.intersect_ray(_ray(Vector2(98, 0), Vector2(400, 0)))))
	_it("from_right_away", _rayline("r", dss.intersect_ray(_ray(Vector2(102, 0), Vector2(400, 0)))))
	_it("from_right_through", _rayline("r", dss.intersect_ray(_ray(Vector2(102, 0), Vector2(0, 0)))))
	_it("corner_start_away", _rayline("r", dss.intersect_ray(_ray(Vector2(98, -200), Vector2(0, -400)))))
	_pass()

# --------------------------------------------------------------- 4. ray order

func _arm_ray_order() -> void:
	var near := _mk_body("near", Vector2(100, 0), Vector2(4, 400))
	var far := _mk_body("far", Vector2(200, 0), Vector2(4, 400))
	var tie_tags := ["tie_a", "tie_b"]
	if _rev:
		tie_tags.reverse()
	var ties: Array = []
	for t in tie_tags:
		ties.append(_mk_body(str(t), Vector2(300, 0), Vector2(4, 400)))
	await _frames(2)
	var dss := _dss()
	_it("nearest", _rayline("r", dss.intersect_ray(_ray(Vector2(0, 0), Vector2(400, 0)))))
	var tq := _ray(Vector2(0, 0), Vector2(400, 0))
	tq.exclude = [near.get_rid(), far.get_rid()]
	_it("tie", _rayline("r", dss.intersect_ray(tq)))
	var q1 := _ray(Vector2(0, 0), Vector2(400, 0))
	q1.exclude = [near.get_rid(), far.get_rid(), ties[0].get_rid()]
	_it("tie_minus_first", _rayline("r", dss.intersect_ray(q1)))
	var q2 := _ray(Vector2(0, 0), Vector2(400, 0))
	q2.exclude = [near.get_rid(), far.get_rid(), ties[1].get_rid()]
	_it("tie_minus_second", _rayline("r", dss.intersect_ray(q2)))
	_it("tie_add_order", "[%s]" % ",".join(tie_tags))
	_it("last_added_wins", str(_tag(dss.intersect_ray(tq)) == str(tie_tags[1])))
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 5. point cap

func _arm_point_cap() -> void:
	var order: Array = ["a", "b", "c", "d", "e"]
	if _rev:
		order.reverse()
	var made: Array = []
	for i in order.size():
		made.append(_mk_body(str(order[i]), Vector2(i * 8, 0), Vector2(40, 40)))
	await _frames(2)
	var dss := _dss()
	_it("add_order", "[%s]" % ",".join(order))
	_it("cap0", _ord(dss.intersect_point(_pt(Vector2(16, 0)), 0)))
	for cap in [1, 2, 3, 5]:
		_it("cap%d" % cap, _ord(dss.intersect_point(_pt(Vector2(16, 0)), cap)))
	_it("cap_default", _ord(dss.intersect_point(_pt(Vector2(16, 0)))))
	var m2 := _pt(Vector2(16, 0))
	m2.collision_mask = 2
	_it("mask2", _ord(dss.intersect_point(m2, CAP)))
	var nb := _pt(Vector2(16, 0))
	nb.collide_with_bodies = false
	_it("nobodies", _ord(dss.intersect_point(nb, CAP)))
	var ex := _pt(Vector2(16, 0))
	ex.exclude = [made[0].get_rid()]
	_it("excl_first", _ord(dss.intersect_point(ex, CAP)))
	_it("far_out", _ord(dss.intersect_point(_pt(Vector2(500, 500)), CAP)))
	for i in 40:
		_mk_body("p%d" % i, Vector2(1000 + i * 2, 0), Vector2(200, 40))
	await _frames(2)
	_it("pile40_default", "n%d" % dss.intersect_point(_pt(Vector2(1000, 0))).size())
	_it("pile40_cap0", "n%d" % dss.intersect_point(_pt(Vector2(1000, 0)), 0).size())
	_it("pile40_cap64", "n%d" % dss.intersect_point(_pt(Vector2(1000, 0)), 64).size())
	_it("cap32_truncates", str(dss.intersect_point(_pt(Vector2(1000, 0))).size() == 32))
	_pass()

# --------------------------------------------------------------- 6. point edges

func _arm_point_edge() -> void:
	_mk_body("box", Vector2(100, 0), Vector2(40, 40))
	var circ := _mk_body("circ", Vector2(300, 0), Vector2(0, 0))
	var cs: CollisionShape2D = circ.get_child(0)
	cs.shape = _circle(20)
	var rot := _mk_body("rot", Vector2(500, 0), Vector2(40, 40))
	rot.rotation = deg_to_rad(45.0)
	await _frames(2)
	var dss := _dss()
	var probes := {
		"box_left": Vector2(80, 0), "box_right": Vector2(120, 0),
		"box_top": Vector2(100, -20), "box_bottom": Vector2(100, 20),
		"box_left_in": Vector2(80.001, 0), "box_right_in": Vector2(119.999, 0),
		"circ_left": Vector2(280, 0), "circ_left_in": Vector2(280.001, 0),
		"circ_top": Vector2(300, -20), "circ_center": Vector2(300, 0),
		"rot_left": Vector2(471.715729, 0), "rot_right": Vector2(528.284271, 0),
		"rot_top": Vector2(500, -28.284271),
	}
	for key in probes:
		_it(str(key), _ord(dss.intersect_point(_pt(probes[key]), CAP)))
	# the same boundary points through the inclusive shape predicate
	var shape_keys := ["box_right", "box_bottom", "circ_top", "rot_right"]
	for key in shape_keys:
		var tiny := _sh(_rect(Vector2(0.001, 0.001)), Transform2D(0, probes[key]))
		_it("s_%s" % key, _ord(dss.intersect_shape(tiny, CAP)))
	_it("point_half_open", "left=%s right=%s top=%s bottom=%s" % [
		str(not _ord(dss.intersect_point(_pt(Vector2(80, 0)), CAP)).is_empty()),
		str(_ord(dss.intersect_point(_pt(Vector2(120, 0)), CAP)).is_empty()),
		str(not _ord(dss.intersect_point(_pt(Vector2(100, -20)), CAP)).is_empty()),
		str(_ord(dss.intersect_point(_pt(Vector2(100, 20)), CAP)).is_empty())])
	_pass()

# --------------------------------------------------------------- 7. canvas layering

func _arm_point_canvas() -> void:
	_mk_body("def", Vector2(100, 0), Vector2(40, 40))
	var cl := CanvasLayer.new()
	cl.name = "cl"
	root.add_child(cl)
	var clb := StaticBody2D.new()
	clb.name = "clb"
	clb.set_meta("tag", "clb")
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(40, 40)
	cs.shape = rs
	clb.add_child(cs)
	clb.position = Vector2(100, 0)
	cl.add_child(clb)
	await _frames(2)
	var dss := _dss()
	var cl_id := cl.get_instance_id()
	_it("default_q", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("layer_q", _ord(dss.intersect_point(_pt(Vector2(100, 0), cl_id), CAP)))
	_it("layer_q_at_default_spot", _ord(dss.intersect_point(_pt(Vector2(100, 0), cl_id), CAP)))
	_it("layer_scoped", str(_ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)) == "[def#0]"))
	cl.offset = Vector2(200, 0)
	await _frames(2)
	_it("shifted_default_q", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("shifted_layer_q", _ord(dss.intersect_point(_pt(Vector2(100, 0), cl_id), CAP)))
	_it("layer_offset_ignored", str(_ord(dss.intersect_point(_pt(Vector2(100, 0), cl_id), CAP)) == "[clb#0]"))
	_it("ray_sees_default", _rayline("r", dss.intersect_ray(_ray(Vector2(0, 0), Vector2(400, 0)))))
	_it("shape_sees_both", _ord(dss.intersect_shape(_sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(100, 0))), CAP)))
	_it("shape_layer_agnostic", str(_ord(dss.intersect_shape(_sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(100, 0))), CAP)) == "[def#0,clb#0]"))
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 8. shape lattice

func _arm_shape_lattice() -> void:
	var order: Array = ["a", "b", "c", "d", "e"]
	if _rev:
		order.reverse()
	for i in order.size():
		_mk_body(str(order[i]), Vector2(i * 8, 0), Vector2(40, 40))
	var multi := _mk_body("m", Vector2(200, 0), Vector2(20, 20))
	_add_shape(multi, Vector2(30, 0), Vector2(20, 20))
	_add_shape(multi, Vector2(60, 0), Vector2(20, 20))
	await _frames(2)
	var dss := _dss()
	_it("cap0", "n%d" % dss.intersect_shape(_sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0))), 0).size())
	for cap in [1, 3, 5]:
		var q := _sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0)))
		_it("cap%d" % cap, "n%d" % dss.intersect_shape(q, cap).size())
	_it("cap_default", "n%d" % dss.intersect_shape(_sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0)))).size())
	_it("keys", str(_sorted(dss.intersect_shape(_sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0))), CAP)[0].keys())))
	_it("set", _setstr(dss.intersect_shape(_sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0))), CAP)))
	var touch := _sh(_rect(Vector2(20, 20)), Transform2D(0, Vector2(62, 0)))
	_it("touch", _ord(dss.intersect_shape(touch, CAP)))
	var touch_in := _sh(_rect(Vector2(20, 20)), Transform2D(0, Vector2(61.999, 0)))
	_it("touch_in", _ord(dss.intersect_shape(touch_in, CAP)))
	var touch_out := _sh(_rect(Vector2(20, 20)), Transform2D(0, Vector2(62.001, 0)))
	_it("touch_out", _ord(dss.intersect_shape(touch_out, CAP)))
	_it("multi_c0", _ord(dss.intersect_shape(_sh(_rect(Vector2(10, 10)), Transform2D(0, Vector2(200, 0))), CAP)))
	_it("multi_c1", _ord(dss.intersect_shape(_sh(_rect(Vector2(10, 10)), Transform2D(0, Vector2(230, 0))), CAP)))
	_it("multi_c2", _ord(dss.intersect_shape(_sh(_rect(Vector2(10, 10)), Transform2D(0, Vector2(260, 0))), CAP)))
	_it("multi_set", _setstr(dss.intersect_shape(_sh(_rect(Vector2(80, 10)), Transform2D(0, Vector2(230, 0))), CAP)))
	var sr := PhysicsShapeQueryParameters2D.new()
	sr.transform = Transform2D(0, Vector2(230, 0))
	sr.shape_rid = PhysicsServer2D.rectangle_shape_create()
	PhysicsServer2D.shape_set_data(sr.shape_rid, Vector2(10, 10))
	_it("shape_rid", _ord(dss.intersect_shape(sr, CAP)))
	_it("empty", "n%d" % dss.intersect_shape(_sh(_rect(Vector2(10, 10)), Transform2D(0, Vector2(900, 900))), CAP).size())
	# server-tier RIDs must be freed or the engine prints a stdout ERROR at exit
	PhysicsServer2D.free_rid(sr.shape_rid)
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 9. ordering core

func _pile(tags: Array, x0: float, y0: float, out: Array) -> void:
	for i in tags.size():
		out.append(_mk_body(str(tags[i]), Vector2(x0 + i * 8, y0), Vector2(40, 40)))

func _arm_order_core() -> void:
	var order: Array = ["a", "b", "c", "d", "e"]
	if _rev:
		order.reverse()
	var made: Array = []
	_pile(order, 0.0, 0.0, made)
	await _frames(2)
	var dss := _dss()
	_it("add_order", "[%s]" % ",".join(order))
	var first := _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP))
	_it("rep1", first)
	_it("rep2", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("rep3", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("repeat_stable", str(first == _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP))))
	_it("set", _setstr(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("shape_same_order", str(_ord(dss.intersect_shape(_sh(_rect(Vector2(60, 60)), Transform2D(0, Vector2(16, 0))), CAP)) == first))
	_pile(["a2", "b2", "c2", "d2", "e2"], 0.0, 1000.0, [])
	await _frames(2)
	_it("pile_b", _ord(dss.intersect_point(_pt(Vector2(16, 1000)), CAP)))
	_it("layout_changes_order", str(_ord(dss.intersect_point(_pt(Vector2(16, 1000)), CAP)) != first))
	_it("pile_a_after_insert", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("insert_perturbs", str(_ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)) != first))
	_pile(["e3", "d3", "c3", "b3", "a3"], 0.0, 2000.0, [])
	await _frames(2)
	_it("pile_rev", _ord(dss.intersect_point(_pt(Vector2(16, 2000)), CAP)))
	made[2].queue_free()
	await _frames(2)
	_it("after_free", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("free_perturbs", str(_ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)) != first))
	_mk_body("f", Vector2(16, 0), Vector2(40, 40))
	await _frames(2)
	_it("after_readd", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("readd_set", _setstr(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 10. layer forms

func _arm_layer_forms() -> void:
	var canvas := Node2D.new()
	canvas.name = "canvas"
	canvas.set_meta("tag", "canvas")
	canvas.position = Vector2(1100, 0)
	root.add_child(canvas)
	var spr := Sprite2D.new()
	canvas.add_child(spr)
	_mk_body("sb", Vector2(100, 0), Vector2(40, 40))
	_mk_body("ar", Vector2(300, 0), Vector2(40, 40), "area")
	_mk_body("rb", Vector2(500, 0), Vector2(40, 40), "rigid")
	_mk_body("cb", Vector2(700, 0), Vector2(40, 40), "char")
	var srv := PhysicsServer2D.body_create()
	PhysicsServer2D.body_set_space(srv, root.world_2d.space)
	PhysicsServer2D.body_set_mode(srv, PhysicsServer2D.BODY_MODE_STATIC)
	var srv_shape := PhysicsServer2D.rectangle_shape_create()
	PhysicsServer2D.shape_set_data(srv_shape, Vector2(40, 40))
	PhysicsServer2D.body_add_shape(srv, srv_shape)
	PhysicsServer2D.body_set_state(srv, PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(900, 0)))
	await _frames(2)
	var dss := _dss()
	var visible := PackedStringArray()
	for spec in [[100, "sb"], [300, "ar"], [500, "rb"], [700, "cb"], [900, "srv"], [1100, "canvas"]]:
		var pos := Vector2(float(spec[0]), 0)
		var key := str(spec[1])
		var bodies := _ord(dss.intersect_point(_pt(pos), CAP))
		var areas := _pt(pos)
		areas.collide_with_areas = true
		var areas_on := _ord(dss.intersect_point(areas, CAP))
		var only := _pt(pos)
		only.collide_with_areas = true
		only.collide_with_bodies = false
		var areas_only := _ord(dss.intersect_point(only, CAP))
		visible.append("%s:body%s/areas%s/only%s" % [key,
			"1" if bodies != "[]" else "0", "1" if areas_on != "[]" else "0",
			"1" if areas_only != "[]" else "0"])
	_it("point_vis", "[%s]" % ",".join(visible))
	_it("ray_sb", _rayline("r", dss.intersect_ray(_ray(Vector2(0, 0), Vector2(200, 0)))))
	_it("ray_srv", _rayline("r", dss.intersect_ray(_ray(Vector2(800, 0), Vector2(1000, 0)))))
	_it("ray_area_off", _rayline("r", dss.intersect_ray(_ray(Vector2(200, 0), Vector2(400, 0)))))
	var ra := _ray(Vector2(200, 0), Vector2(400, 0))
	ra.collide_with_areas = true
	_it("ray_area_on", _rayline("r", dss.intersect_ray(ra)))
	_it("shape_srv", _ord(dss.intersect_shape(_sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(900, 0))), CAP)))
	_it("shape_area_off", _ord(dss.intersect_shape(_sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(300, 0))), CAP)))
	var sa := _sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(300, 0)))
	sa.collide_with_areas = true
	_it("shape_area_on", _ord(dss.intersect_shape(sa, CAP)))
	_sh(_circle(20), Transform2D(0, Vector2(700, 0)), Vector2(400, 0))
	_it("cast_srv_ignored", str(dss.cast_motion(_sh(_circle(20), Transform2D(0, Vector2(860, 0)), Vector2(80, 0)))))
	_it("server_tier_visible", str(_ord(dss.intersect_point(_pt(Vector2(900, 0)), CAP)) == "[?#0]"))
	_it("canvas_absent", str(_ord(dss.intersect_point(_pt(Vector2(1100, 0)), CAP)) == "[]"))
	# free the server-tier RIDs (see §H3: leaked RIDs print a stdout ERROR at exit)
	PhysicsServer2D.free_rid(srv_shape)
	PhysicsServer2D.free_rid(srv)
	_pass()

# --------------------------------------------------------------- 11. cast + rest + pairs

func _arm_cast_rest() -> void:
	var w1 := _mk_body("w1", Vector2(100, 0), Vector2(4, 400))
	var w2 := _mk_body("w2", Vector2(300, 0), Vector2(4, 400))
	_mk_body("ar", Vector2(200, 0), Vector2(4, 400), "area")
	await _frames(2)
	var dss := _dss()
	var c := _circle(8)
	_it("cm_base", str(dss.cast_motion(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0)))))
	_it("cm_to_wall1", str(dss.cast_motion(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(150, 0)))))
	var cm_m := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	cm_m.collision_mask = 2
	_it("cm_mask2", str(dss.cast_motion(cm_m)))
	var cm_e := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	cm_e.exclude = [w1.get_rid()]
	_it("cm_excl_w1", str(dss.cast_motion(cm_e)))
	var cm_b := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	cm_b.exclude = [w1.get_rid(), w2.get_rid()]
	_it("cm_excl_both", str(dss.cast_motion(cm_b)))
	var cm_a := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	cm_a.collide_with_areas = true
	_it("cm_areas_on", str(dss.cast_motion(cm_a)))
	_it("cm_zero", str(dss.cast_motion(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2.ZERO))))
	_it("cm_negative", str(dss.cast_motion(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(-400, 0)))))
	_it("cm_from_inside", str(dss.cast_motion(_sh(c, Transform2D(0, Vector2(100, 0)), Vector2(400, 0)))))
	_it("cm_inside_skips_overlap", str(dss.cast_motion(_sh(c, Transform2D(0, Vector2(100, 0)), Vector2(400, 0)))[1] > 0.0))
	_it("cm_inside_matches_later_wall", str(absf(dss.cast_motion(_sh(c, Transform2D(0, Vector2(100, 0)), Vector2(400, 0)))[1] * 400.0 + 100.0 - dss.cast_motion(cm_e)[1] * 400.0) < 0.01))
	_it("ri_m50", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(50, 0)))))
	_it("ri_m200", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(200, 0)))))
	_it("ri_m290", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(290, 0)))))
	_it("ri_m300", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(300, 0)))))
	_it("ri_m400", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0)))))
	_it("ri_m600", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(600, 0)))))
	var rl := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(200, 0))
	rl.exclude = [w1.get_rid()]
	_it("ri_m200_excl_w1", _ri_line(dss.get_rest_info(rl)))
	var rl2 := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	rl2.exclude = [w1.get_rid()]
	_it("ri_m400_excl_w1", _ri_line(dss.get_rest_info(rl2)))
	var rm := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	rm.collision_mask = 2
	_it("ri_mask2", _ri_line(dss.get_rest_info(rm)))
	_it("ri_empty", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(500, 500)), Vector2.ZERO))))
	_it("ri_offaxis", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 500)), Vector2(200, 0)))))
	_it("ri_keys", str(_sorted(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(200, 0))).keys())))
	_it("ri_zero_motion", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(96, 0)), Vector2.ZERO))))
	# collide_shape: flattened contact pairs, cap counts PAIRS
	var b1 := _mk_body("b1", Vector2(100, 0), Vector2(4, 400))
	_mk_body("b2", Vector2(112, 0), Vector2(4, 400))
	await _frames(2)
	var cs := dss.collide_shape(_sh(c, Transform2D(0, Vector2(106, 0)), Vector2.ZERO))
	var pts: PackedStringArray = []
	for p in cs:
		pts.append(_v2(p))
	_it("cs_n", str(cs.size()))
	_it("cs_pts", "[%s]" % ",".join(pts))
	_it("cs_cap1", "n%d" % dss.collide_shape(_sh(c, Transform2D(0, Vector2(106, 0)), Vector2.ZERO), 1).size())
	_it("cs_cap2", "n%d" % dss.collide_shape(_sh(c, Transform2D(0, Vector2(106, 0)), Vector2.ZERO), 2).size())
	var ce := _sh(c, Transform2D(0, Vector2(106, 0)), Vector2.ZERO)
	ce.exclude = [b1.get_rid()]
	_it("cs_excl_b1", "n%d" % dss.collide_shape(ce).size())
	var cm2 := _sh(c, Transform2D(0, Vector2(106, 0)), Vector2.ZERO)
	cm2.collision_mask = 2
	_it("cs_mask2", "n%d" % dss.collide_shape(cm2).size())
	_it("cs_rep", "n%d" % dss.collide_shape(_sh(c, Transform2D(0, Vector2(106, 0)), Vector2.ZERO)).size())
	_it("cs_empty", "n%d" % dss.collide_shape(_sh(c, Transform2D(0, Vector2(900, 900)), Vector2.ZERO)).size())
	_pass()

# --------------------------------------------------------------- 12. exclude + space

func _arm_excl_space() -> void:
	var a := _mk_body("a", Vector2(100, 0), Vector2(40, 40))
	await _frames(2)
	var dss := _dss()
	var cs: CollisionShape2D = a.get_child(0)
	var shape_rid := cs.shape.get_rid()
	var body_rid := a.get_rid()
	_it("baseline", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	var q1 := _pt(Vector2(100, 0))
	q1.exclude = [body_rid]
	_it("body_rid", _ord(dss.intersect_point(q1, CAP)))
	var q2 := _pt(Vector2(100, 0))
	q2.exclude = [shape_rid]
	_it("shape_rid_inert", str(_ord(dss.intersect_point(q2, CAP)) == "[a#0]"))
	var q3 := _pt(Vector2(100, 0))
	q3.exclude = [RID()]
	_it("null_rid_inert", str(_ord(dss.intersect_point(q3, CAP)) == "[a#0]"))
	var q4 := _pt(Vector2(100, 0))
	q4.exclude = [body_rid, body_rid]
	_it("dup_rid", _ord(dss.intersect_point(q4, CAP)))
	var r1 := _ray(Vector2(0, 0), Vector2(200, 0))
	r1.exclude = [shape_rid]
	_it("ray_shape_rid_inert", _rayline("r", dss.intersect_ray(r1)))
	_it("shape_rid_is_body_rid", str(shape_rid == body_rid))
	# physics spaces: a SubViewport owns its own world
	var root_body := _mk_body("root_body", Vector2(50, 50), Vector2(40, 40))
	var sv := SubViewport.new()
	sv.name = "sv"
	sv.size = Vector2i(64, 64)
	root.add_child(sv)
	var svb := StaticBody2D.new()
	svb.name = "sv_body"
	svb.set_meta("tag", "sv_body")
	var scs := CollisionShape2D.new()
	var srs := RectangleShape2D.new()
	srs.size = Vector2(40, 40)
	scs.shape = srs
	svb.add_child(scs)
	svb.position = Vector2(50, 50)
	sv.add_child(svb)
	await _frames(2)
	var s_root := root.world_2d.space
	var s_sv := sv.world_2d.space
	_it("same_space", str(s_root == s_sv))
	_it("root_view", _ord(PhysicsServer2D.space_get_direct_state(s_root).intersect_point(_pt(Vector2(50, 50)), CAP)))
	_it("sv_view", _ord(PhysicsServer2D.space_get_direct_state(s_sv).intersect_point(_pt(Vector2(50, 50)), CAP)))
	_it("space_scoped", str(_ord(PhysicsServer2D.space_get_direct_state(s_sv).intersect_point(_pt(Vector2(50, 50)), CAP)) == "[sv_body#0]"))
	_it("dss_identity", "same_across_calls=%s" % str(PhysicsServer2D.space_get_direct_state(s_root) == dss))
	_it("node_world_ok", str(root_body.get_world_2d().space == s_root and svb.get_world_2d().space == s_sv))
	_pass()

# --------------------------------------------------------------- 13. freshness

func _arm_fresh() -> void:
	var dss := _dss()
	var b := _mk_body("f", Vector2(100, 0), Vector2(40, 40))
	_it("add_t0_point", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("add_t0_ray", _rayline("r", dss.intersect_ray(_ray(Vector2(0, 0), Vector2(200, 0)))))
	_it("add_t0_shape", _ord(dss.intersect_shape(_sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(100, 0))), CAP)))
	_it("add_same_frame", str(_ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)) == "[f#0]"))
	await _frames(2)
	b.position = Vector2(500, 0)
	_it("node_move_t0_old", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("node_move_t0_new", _ord(dss.intersect_point(_pt(Vector2(500, 0)), CAP)))
	_it("node_move_deferred", str(_ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)) == "[f#0]"))
	await _frames(2)
	_it("node_move_t1_old", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("node_move_t1_new", _ord(dss.intersect_point(_pt(Vector2(500, 0)), CAP)))
	PhysicsServer2D.body_set_state(b.get_rid(), PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(900, 0)))
	_it("server_tele_t0_old", _ord(dss.intersect_point(_pt(Vector2(500, 0)), CAP)))
	_it("server_tele_t0_new", _ord(dss.intersect_point(_pt(Vector2(900, 0)), CAP)))
	_it("server_write_live", str(_ord(dss.intersect_point(_pt(Vector2(900, 0)), CAP)) == "[f#0]"))
	await _frames(2)
	var c := _mk_body("c", Vector2(1200, 0), Vector2(40, 40))
	await _frames(2)
	_it("pre_free", _ord(dss.intersect_point(_pt(Vector2(1200, 0)), CAP)))
	c.queue_free()
	_it("free_t0", _ord(dss.intersect_point(_pt(Vector2(1200, 0)), CAP)))
	_it("free_deferred", str(_ord(dss.intersect_point(_pt(Vector2(1200, 0)), CAP)) == "[c#0]"))
	await _frames(2)
	_it("free_t1", _ord(dss.intersect_point(_pt(Vector2(1200, 0)), CAP)))
	var d := _mk_body("d", Vector2(1400, 0), Vector2(40, 40))
	await _frames(2)
	d.visible = false
	_it("vis_off", _ord(dss.intersect_point(_pt(Vector2(1400, 0)), CAP)))
	_it("visible_irrelevant", str(_ord(dss.intersect_point(_pt(Vector2(1400, 0)), CAP)) == "[d#0]"))
	var e := _mk_body("e", Vector2(1600, 0), Vector2(40, 40))
	await _frames(2)
	e.collision_layer = 2
	_it("layer_change_t0", _ord(dss.intersect_point(_pt(Vector2(1600, 0)), CAP)))
	await _frames(2)
	_it("layer_change_t1", _ord(dss.intersect_point(_pt(Vector2(1600, 0)), CAP)))
	_pass()
