extends SceneTree
# r95 scout DISCOVERY micro-probe — PhysicsDirectSpaceState2D query lattice.
# Battery launch shape:
#   godot --headless --path proj --script res://discover.gd -- --arm=<name> [--rev]
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix
# scan); every arm prints its own name, so a silent arm fallback is impossible.
# Prints `R95 <arm> <key>=<value>` diagnostics and one final
# `PASS dss_lattice <arm> <key>=<value> ...` line.  No RIDs / object ids /
# addresses are ever printed (byte-stability); identities are node tags.

var arm := ""
var _rev := false
var _perm := 0
var _items: PackedStringArray = []
const CAP := 32

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a == "--rev":
			_rev = true
		elif a.begins_with("--perm="):
			_perm = int(a.substr(7))
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": await _arm_census()
		"ray_params": await _arm_ray_params()
		"ray_edge": await _arm_ray_edge()
		"ray_order": await _arm_ray_order()
		"point_cap": await _arm_point_cap()
		"point_canvas": await _arm_point_canvas()
		"point_edge": await _arm_point_edge()
		"ray_boundary": await _arm_ray_boundary()
		"shape_cap": await _arm_shape_cap()
		"order_stab": await _arm_order_stab()
		"layer_forms": await _arm_layer_forms()
		"cast_lattice": await _arm_cast_lattice()
		"rest_deep": await _arm_rest_deep()
		"collide_pair": await _arm_collide_pair()
		"excl_forms": await _arm_excl_forms()
		"space_scope": await _arm_space_scope()
		"fresh": await _arm_fresh()
		"rest_semantics": await _arm_rest_semantics()
		"order_alt": await _arm_order_alt()
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

func _set_prop_if(q: Object, prop: String, value: Variant) -> bool:
	if _has_prop(q.get_class(), prop):
		q.set(prop, value)
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

func _add_shape(b: CollisionObject2D, tag: String, offset: Vector2, size: Vector2) -> void:
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	cs.position = offset
	cs.name = tag
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

func _rayline(tag: String, q: PhysicsRayQueryParameters2D, hit: Dictionary) -> String:
	if hit.is_empty():
		return "%s={}" % tag
	return "%s={%s pos=%s n=%s}" % [tag, _tag(hit), _v2(hit.get("position", Vector2.ZERO)),
		_v2(hit.get("normal", Vector2.ZERO))]

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
	_it("pt_maxresults", "has=%s" % str(_has_prop("PhysicsPointQueryParameters2D", "max_results")))
	_it("sh_maxresults", "has=%s" % str(_has_prop("PhysicsShapeQueryParameters2D", "max_results")))
	var q := _ray(Vector2(1, 2), Vector2(3, 4))
	_it("ray_create", "from=%s to=%s mask=%d excl=%d bodies=%s areas=%s inside=%s" % [
		_v2(q.from), _v2(q.to), q.collision_mask, q.exclude.size(),
		str(q.collide_with_bodies), str(q.collide_with_areas), str(q.hit_from_inside)])
	_it("dss_cls", "cls=%s null=%s" % [PhysicsServer2D.space_get_direct_state(root.world_2d.space).get_class(),
		str(PhysicsServer2D.space_get_direct_state(root.world_2d.space) == null)])
	_it("server", "has_space_get_direct_state=%s" % str(PhysicsServer2D.has_method("space_get_direct_state")))
	_pass()

# --------------------------------------------------------------- 2. ray flags

func _arm_ray_params() -> void:
	var wall := _mk_body("w", Vector2(100, 0), Vector2(4, 400))
	var wall2 := _mk_body("w2", Vector2(300, 0), Vector2(4, 400), "area")
	await _frames(2)
	var dss := _dss()
	var base := _ray(Vector2(0, 0), Vector2(400, 0))
	var hit := dss.intersect_ray(base)
	_it("base", _rayline("r", base, hit))
	var m2 := _ray(Vector2(0, 0), Vector2(400, 0))
	m2.collision_mask = 2
	_it("mask2", _rayline("r", m2, dss.intersect_ray(m2)))
	var m0 := _ray(Vector2(0, 0), Vector2(400, 0))
	m0.collision_mask = 0
	_it("mask0", _rayline("r", m0, dss.intersect_ray(m0)))
	var nb := _ray(Vector2(0, 0), Vector2(400, 0))
	nb.collide_with_bodies = false
	_it("nobodies", _rayline("r", nb, dss.intersect_ray(nb)))
	var ar := _ray(Vector2(0, 0), Vector2(400, 0))
	ar.collide_with_areas = true
	_it("areas", _rayline("r", ar, dss.intersect_ray(ar)))
	var ar2 := _ray(Vector2(0, 0), Vector2(400, 0))
	ar2.collide_with_areas = true
	ar2.collide_with_bodies = false
	_it("areasonly", _rayline("r", ar2, dss.intersect_ray(ar2)))
	var ex := _ray(Vector2(0, 0), Vector2(400, 0))
	ex.exclude = [wall.get_rid()]
	_it("excl_wall", _rayline("r", ex, dss.intersect_ray(ex)))
	var ex2 := _ray(Vector2(0, 0), Vector2(400, 0))
	ex2.exclude = [wall2.get_rid()]
	_it("excl_area", _rayline("r", ex2, dss.intersect_ray(ex2)))
	# hit_from_inside: ray starts inside the wall, travels +x.
	var inside := _ray(Vector2(100, 0), Vector2(400, 0))
	_it("inside_off", _rayline("r", inside, dss.intersect_ray(inside)))
	var inside2 := _ray(Vector2(100, 0), Vector2(400, 0))
	inside2.hit_from_inside = true
	_it("inside_on", _rayline("r", inside2, dss.intersect_ray(inside2)))
	# inside an area only (bodies off, areas on)
	var ia := _ray(Vector2(300, 0), Vector2(400, 0))
	ia.hit_from_inside = true
	ia.collide_with_areas = true
	_it("inside_area_on", _rayline("r", ia, dss.intersect_ray(ia)))
	# toggling inside on a ray that starts outside must not change the answer
	var out_on := _ray(Vector2(0, 0), Vector2(400, 0))
	out_on.hit_from_inside = true
	_it("outside_on", _rayline("r", out_on, dss.intersect_ray(out_on)))
	_pass()

# --------------------------------------------------------------- 3. ray edges

func _arm_ray_edge() -> void:
	_mk_body("w", Vector2(100, 0), Vector2(4, 400))
	_mk_body("c", Vector2(200, 0), Vector2(40, 40))
	await _frames(2)
	var dss := _dss()
	# exactly ending on the surface (wall near face at x=98)
	var end_at := _ray(Vector2(0, 0), Vector2(98, 0))
	_it("end_at_face", _rayline("r", end_at, dss.intersect_ray(end_at)))
	var end_in := _ray(Vector2(0, 0), Vector2(97.9999, 0))
	_it("end_eps_before", _rayline("r", end_in, dss.intersect_ray(end_in)))
	# starting exactly on the far face going away
	var away := _ray(Vector2(102, 0), Vector2(300, 0))
	_it("start_far_face", _rayline("r", away, dss.intersect_ray(away)))
	# grazing along the wall's top edge (y = -200 is the rect top)
	var graze := _ray(Vector2(0, -200), Vector2(400, -200))
	_it("graze_top", _rayline("r", graze, dss.intersect_ray(graze)))
	var graze_in := _ray(Vector2(0, -199.999), Vector2(400, -199.999))
	_it("graze_inside", _rayline("r", graze_in, dss.intersect_ray(graze_in)))
	# diagonal through the corner of the 40x40 box at (200,0): corner (180,-20)
	var corner := _ray(Vector2(160, -40), Vector2(200, 0))
	_it("corner_diag", _rayline("r", corner, dss.intersect_ray(corner)))
	# zero-length ray (from == to)
	var zero := _ray(Vector2(98, 0), Vector2(98, 0))
	_it("zero_len", _rayline("r", zero, dss.intersect_ray(zero)))
	var zero_out := _ray(Vector2(0, 0), Vector2(0, 0))
	_it("zero_len_outside", _rayline("r", zero_out, dss.intersect_ray(zero_out)))
	# reversed ray from beyond the wall back toward origin
	var back := _ray(Vector2(400, 0), Vector2(0, 0))
	_it("reverse", _rayline("r", back, dss.intersect_ray(back)))
	_pass()

# --------------------------------------------------------------- 4. ray order

func _arm_ray_order() -> void:
	# two walls crossing the same ray at different distances: nearest must win
	var near := _mk_body("near", Vector2(100, 0), Vector2(4, 400))
	var far := _mk_body("far", Vector2(200, 0), Vector2(4, 400))
	# overlapping walls at the SAME x (coincident boxes): tie
	var tie_tags := ["tie_a", "tie_b"]
	if _rev:
		tie_tags.reverse()
	var tie_bodies: Array = []
	for t in tie_tags:
		tie_bodies.append(_mk_body(str(t), Vector2(300, 0), Vector2(4, 400)))
	await _frames(2)
	var dss := _dss()
	_it("tie_add_order", "[%s]" % ",".join(tie_tags))
	var q := _ray(Vector2(0, 0), Vector2(400, 0))
	_it("nearest", _rayline("r", q, dss.intersect_ray(q)))
	var tq := _ray(Vector2(0, 0), Vector2(400, 0))
	tq.exclude = [near.get_rid(), far.get_rid()]
	_it("tie", _rayline("r", tq, dss.intersect_ray(tq)))
	var tq2 := _ray(Vector2(0, 0), Vector2(400, 0))
	tq2.exclude = [near.get_rid(), far.get_rid(), tie_bodies[0].get_rid()]
	_it("tie_minus_first", _rayline("r", tq2, dss.intersect_ray(tq2)))
	var tq3 := _ray(Vector2(0, 0), Vector2(400, 0))
	tq3.exclude = [near.get_rid(), far.get_rid(), tie_bodies[1].get_rid()]
	_it("tie_minus_second", _rayline("r", tq3, dss.intersect_ray(tq3)))
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 5. point cap

func _arm_point_cap() -> void:
	var tags := ["a", "b", "c", "d", "e"]
	var order: Array = tags.duplicate()
	if _rev:
		order.reverse()
	var made: Array = []
	for i in order.size():
		made.append(_mk_body(str(order[i]), Vector2(i * 8, 0), Vector2(40, 40)))
	await _frames(2)
	var dss := _dss()
	_it("add_order", "[%s]" % ",".join(order))
	for cap in [0, 1, 2, 3, 5, 10]:
		var q := _pt(Vector2(16, 0))
		_it("cap%d" % cap, _ord(dss.intersect_point(q, cap)))
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
	# geometric boundary: body a spans x -4..36; probe its right edge exactly
	_it("edge_in", _ord(dss.intersect_point(_pt(Vector2(36, 0)), CAP)))
	_it("edge_eps_in", _ord(dss.intersect_point(_pt(Vector2(35.999, 0)), CAP)))
	_it("edge_eps_out", _ord(dss.intersect_point(_pt(Vector2(36.001, 0)), CAP)))
	_it("corner", _ord(dss.intersect_point(_pt(Vector2(36, 20)), CAP)))
	_it("corner_eps_out", _ord(dss.intersect_point(_pt(Vector2(36.001, 20.001)), CAP)))
	_it("far_out", _ord(dss.intersect_point(_pt(Vector2(500, 500)), CAP)))
	# default cap: a 40-body pile (default max_results is 32)
	var made2: Array = []
	for i in 40:
		made2.append(_mk_body("p%d" % i, Vector2(1000 + i * 2, 0), Vector2(200, 40)))
	await _frames(2)
	_it("pile40_default", "n%d" % dss.intersect_point(_pt(Vector2(1000, 0))).size())
	_it("pile40_cap0", "n%d" % dss.intersect_point(_pt(Vector2(1000, 0)), 0).size())
	_it("pile40_cap64", "n%d" % dss.intersect_point(_pt(Vector2(1000, 0)), 64).size())
	_it("pile40_cap8", "n%d" % dss.intersect_point(_pt(Vector2(1000, 0)), 8).size())
	_pass()

# --------------------------------------------------------------- 5b. canvas layering

func _arm_point_canvas() -> void:
	# default canvas layer (viewport) body
	var def := _mk_body("def", Vector2(100, 0), Vector2(40, 40))
	# CanvasLayer-hosted body (its own canvas instance id, offset transform)
	var cl := CanvasLayer.new()
	cl.name = "cl"
	cl.set_meta("tag", "cl")
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
	_it("cl_offset", _v2(cl.offset))
	_it("default_q", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("default_q_at_layer_off", _ord(dss.intersect_point(_pt(Vector2(300, 0)), CAP)))
	_it("layer_q", _ord(dss.intersect_point(_pt(Vector2(100, 0), cl_id), CAP)))
	_it("layer_q_at_layer_off", _ord(dss.intersect_point(_pt(Vector2(300, 0), cl_id), CAP)))
	# shift the layer: the query position must be read in the layer's own space
	cl.offset = Vector2(200, 0)
	await _frames(2)
	_it("shifted_default_q", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("shifted_layer_q", _ord(dss.intersect_point(_pt(Vector2(100, 0), cl_id), CAP)))
	_it("shifted_default_q_off", _ord(dss.intersect_point(_pt(Vector2(300, 0)), CAP)))
	_it("shifted_layer_q_off", _ord(dss.intersect_point(_pt(Vector2(300, 0), cl_id), CAP)))
	_it("world_pos", _v2(clb.global_position))
	# ray/shape queries have no canvas_instance_id: do they see the layer body?
	var rq := _ray(Vector2(0, 0), Vector2(400, 0))
	_it("ray", _rayline("r", rq, dss.intersect_ray(rq)))
	var sq := _sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(100, 0)))
	_it("shape_local", _ord(dss.intersect_shape(sq, CAP)))
	var sq2 := _sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(300, 0)))
	_it("shape_world", _ord(dss.intersect_shape(sq2, CAP)))
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 6. shape cap

func _arm_shape_cap() -> void:
	var tags := ["a", "b", "c", "d", "e"]
	var order: Array = tags.duplicate()
	if _rev:
		order.reverse()
	var made: Array = []
	for i in order.size():
		made.append(_mk_body(str(order[i]), Vector2(i * 8, 0), Vector2(40, 40)))
	# multi-shape body: three 20x20 boxes in a row
	var multi := _mk_body("m", Vector2(200, 0), Vector2(20, 20))
	_add_shape(multi, "m1", Vector2(30, 0), Vector2(20, 20))
	_add_shape(multi, "m2", Vector2(60, 0), Vector2(20, 20))
	await _frames(2)
	var dss := _dss()
	_it("add_order", "[%s]" % ",".join(order))
	for cap in [0, 1, 2, 3, 5, 10]:
		var q := _sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0)))
		var res := dss.intersect_shape(q, cap)
		_it("cap%d" % cap, "n%d%s" % [res.size(), _ord(res)])
	_it("cap_default", "n%d" % dss.intersect_shape(_sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0)))).size())
	var mq := _sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0)))
	mq.collision_mask = 2
	_it("mask2", _ord(dss.intersect_shape(mq, CAP)))
	var ex := _sh(_rect(Vector2(120, 60)), Transform2D(0, Vector2(16, 0)))
	ex.exclude = [made[0].get_rid()]
	_it("excl_first", _ord(dss.intersect_shape(ex, CAP)))
	var nohit := _sh(_rect(Vector2(10, 10)), Transform2D(0, Vector2(500, 500)))
	_it("empty", _ord(dss.intersect_shape(nohit, CAP)))
	# touching but not overlapping: probe's left edge at body e's right edge (52)
	var touch := _sh(_rect(Vector2(20, 20)), Transform2D(0, Vector2(62, 0)))
	_it("touch", _ord(dss.intersect_shape(touch, CAP)))
	var touch_in := _sh(_rect(Vector2(20, 20)), Transform2D(0, Vector2(61.999, 0)))
	_it("touch_eps_in", _ord(dss.intersect_shape(touch_in, CAP)))
	var touch_out := _sh(_rect(Vector2(20, 20)), Transform2D(0, Vector2(62.001, 0)))
	_it("touch_eps_out", _ord(dss.intersect_shape(touch_out, CAP)))
	# multi-shape body: probe each of its three boxes
	var mp := _sh(_rect(Vector2(10, 10)), Transform2D(0, Vector2(200, 0)))
	_it("multi_c0", _ord(dss.intersect_shape(mp, CAP)))
	var mp1 := _sh(_rect(Vector2(10, 10)), Transform2D(0, Vector2(230, 0)))
	_it("multi_c1", _ord(dss.intersect_shape(mp1, CAP)))
	var mp2 := _sh(_rect(Vector2(10, 10)), Transform2D(0, Vector2(260, 0)))
	_it("multi_c2", _ord(dss.intersect_shape(mp2, CAP)))
	var all3 := _sh(_rect(Vector2(80, 10)), Transform2D(0, Vector2(230, 0)))
	_it("multi_all", _ord(dss.intersect_shape(all3, CAP)))
	# shape_rid form of the same query (vs .shape)
	var sr := PhysicsShapeQueryParameters2D.new()
	sr.transform = Transform2D(0, Vector2(230, 0))
	sr.shape_rid = PhysicsServer2D.rectangle_shape_create()
	PhysicsServer2D.shape_set_data(sr.shape_rid, Vector2(10, 10))
	_it("shape_rid", _ord(dss.intersect_shape(sr, CAP)))
	_pass()

# --------------------------------------------------------------- 7. order stability

func _pile(tags: Array, x0: float, y0: float, out: Array) -> void:
	for i in tags.size():
		out.append(_mk_body(str(tags[i]), Vector2(x0 + i * 8, y0), Vector2(40, 40)))

func _arm_order_stab() -> void:
	var tags := ["a", "b", "c", "d", "e"]
	var order: Array = tags.duplicate()
	if _rev:
		order.reverse()
	var made: Array = []
	_pile(order, 0.0, 0.0, made)
	await _frames(2)
	var dss := _dss()
	_it("add_order", "[%s]" % ",".join(order))
	var q := _pt(Vector2(16, 0))
	var first := _ord(dss.intersect_point(q, CAP))
	_it("rep1", first)
	_it("rep2", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("rep3", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("shape_rep1", _ord(dss.intersect_shape(_sh(_rect(Vector2(60, 60)), Transform2D(0, Vector2(16, 0))), CAP)))
	_it("repeat_stable", str(first == _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP))))
	# same relative geometry translated: spatial position probe
	var tags2 := ["a2", "b2", "c2", "d2", "e2"]
	var made2: Array = []
	_pile(tags2, 0.0, 1000.0, made2)
	await _frames(2)
	var q2 := _pt(Vector2(16, 1000))
	_it("pile_b", _ord(dss.intersect_point(q2, CAP)))
	_it("pile_b_shape", _ord(dss.intersect_shape(_sh(_rect(Vector2(60, 60)), Transform2D(0, Vector2(16, 1000))), CAP)))
	# re-query pile A after the insertion of pile B (insertion reshuffle probe)
	_it("pile_a_after_insert", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	# same geometry, reversed add order, same process
	var tags3 := ["e3", "d3", "c3", "b3", "a3"]
	var made3: Array = []
	_pile(tags3, 0.0, 2000.0, made3)
	await _frames(2)
	_it("pile_rev", _ord(dss.intersect_point(_pt(Vector2(16, 2000)), CAP)))
	# churn: free the middle body of pile A, re-query, then add a fresh one
	made[2].queue_free()
	await _frames(2)
	_it("after_free", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	var fresh := _mk_body("f", Vector2(16, 0), Vector2(40, 40))
	await _frames(2)
	_it("after_readd", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))
	_it("fresh_visible", str(_ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)).contains("f#0")))
	# does the free change pile B's order too?
	_it("pile_b_after_churn", _ord(dss.intersect_point(_pt(Vector2(16, 1000)), CAP)))
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 8. layer forms

func _arm_layer_forms() -> void:
	# canvas-only node (no collision object) must be invisible
	var canvas := Node2D.new()
	canvas.name = "canvas"
	canvas.set_meta("tag", "canvas")
	canvas.position = Vector2(1100, 0)
	root.add_child(canvas)
	var spr := Sprite2D.new()
	canvas.add_child(spr)
	# each object in its own clean area: node-tier classes + one server-tier body
	var sb := _mk_body("sb", Vector2(100, 0), Vector2(40, 40))
	var ar := _mk_body("ar", Vector2(300, 0), Vector2(40, 40), "area")
	var rb := _mk_body("rb", Vector2(500, 0), Vector2(40, 40), "rigid")
	var cb := _mk_body("cb", Vector2(700, 0), Vector2(40, 40), "char")
	var srv_body := PhysicsServer2D.body_create()
	PhysicsServer2D.body_set_space(srv_body, root.world_2d.space)
	PhysicsServer2D.body_set_mode(srv_body, PhysicsServer2D.BODY_MODE_STATIC)
	var srv_shape := PhysicsServer2D.rectangle_shape_create()
	PhysicsServer2D.shape_set_data(srv_shape, Vector2(40, 40))
	PhysicsServer2D.body_add_shape(srv_body, srv_shape)
	PhysicsServer2D.body_set_state(srv_body, PhysicsServer2D.BODY_STATE_TRANSFORM,
		Transform2D(0, Vector2(900, 0)))
	await _frames(2)
	var dss := _dss()
	for spec in [[100, "sb"], [300, "ar"], [500, "rb"], [700, "cb"], [900, "srv"], [1100, "canvas"]]:
		var pos := Vector2(float(spec[0]), 0)
		var key := str(spec[1])
		var bodies := _pt(pos)
		var areas := _pt(pos)
		areas.collide_with_areas = true
		var only := _pt(pos)
		only.collide_with_areas = true
		only.collide_with_bodies = false
		_it("%s_body" % key, _ord(dss.intersect_point(bodies, CAP)))
		_it("%s_areas" % key, _ord(dss.intersect_point(areas, CAP)))
		_it("%s_areas_only" % key, _ord(dss.intersect_point(only, CAP)))
	# ray probes: node-tier at 100 and server-tier at 900
	var r1 := _ray(Vector2(0, 0), Vector2(200, 0))
	_it("ray_sb", _rayline("r", r1, dss.intersect_ray(r1)))
	var r2 := _ray(Vector2(800, 0), Vector2(1000, 0))
	_it("ray_srv", _rayline("r", r2, dss.intersect_ray(r2)))
	var r3 := _ray(Vector2(200, 0), Vector2(400, 0))
	_it("ray_area", _rayline("r", r3, dss.intersect_ray(r3)))
	var r3a := _ray(Vector2(200, 0), Vector2(400, 0))
	r3a.collide_with_areas = true
	_it("ray_area_on", _rayline("r", r3a, dss.intersect_ray(r3a)))
	var s1 := _sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(900, 0)))
	_it("shape_srv", _ord(dss.intersect_shape(s1, CAP)))
	var s2 := _sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(300, 0)))
	_it("shape_area_off", _ord(dss.intersect_shape(s2, CAP)))
	var s2a := _sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(300, 0)))
	s2a.collide_with_areas = true
	_it("shape_area_on", _ord(dss.intersect_shape(s2a, CAP)))
	var c1 := _sh(_circle(20), Transform2D(0, Vector2(900, 0)))
	_it("cast_srv", str(dss.cast_motion(c1)))
	_it("rids", "sb=%s srv=%s" % [str(sb.get_rid().is_valid()), str(srv_body.is_valid())])
	_it("canvas_absent", str(not _ord(dss.intersect_point(_pt(Vector2(1100, 0)), CAP)).contains("canvas")))
	_pass()

# --------------------------------------------------------------- 8b. point edge semantics

func _arm_point_edge() -> void:
	var b := _mk_body("box", Vector2(100, 0), Vector2(40, 40))
	var c := _mk_body("circ", Vector2(300, 0), Vector2(0, 0))
	var cc: CollisionShape2D = c.get_child(0)
	cc.shape = _circle(20)
	# rotated box: 45 degrees
	var r := _mk_body("rot", Vector2(500, 0), Vector2(40, 40))
	r.rotation = deg_to_rad(45.0)
	await _frames(2)
	var dss := _dss()
	var probes := {
		"box_left": Vector2(80, 0), "box_right": Vector2(120, 0),
		"box_top": Vector2(100, -20), "box_bottom": Vector2(100, 20),
		"box_center": Vector2(100, 0), "box_left_in": Vector2(80.001, 0),
		"box_right_in": Vector2(119.999, 0), "box_top_in": Vector2(100, -19.999),
		"box_bottom_in": Vector2(100, 19.999),
		"circ_left": Vector2(280, 0), "circ_left_in": Vector2(280.001, 0),
		"circ_right": Vector2(320, 0), "circ_top": Vector2(300, -20),
		"circ_center": Vector2(300, 0),
		"rot_left": Vector2(500 - 28.284271, 0), "rot_right": Vector2(500 + 28.284271, 0),
		"rot_top": Vector2(500, -28.284271),
	}
	for key in probes:
		_it(str(key), _ord(dss.intersect_point(_pt(probes[key]), CAP)))
	# same predicates through intersect_shape with a tiny probe (1e-3 box)
	for key in probes:
		var tiny := _sh(_rect(Vector2(0.001, 0.001)), Transform2D(0, probes[key]))
		_it("s_%s" % str(key), _ord(dss.intersect_shape(tiny, CAP)))
	_pass()

# --------------------------------------------------------------- 8c. ray boundary starts

func _arm_ray_boundary() -> void:
	var w := _mk_body("w", Vector2(100, 0), Vector2(4, 400))
	await _frames(2)
	var dss := _dss()
	# starts exactly on each face, travelling away from the body
	_it("from_left_away", _rayline("r", _ray(Vector2(98, 0), Vector2(0, 0)), dss.intersect_ray(_ray(Vector2(98, 0), Vector2(0, 0)))))
	_it("from_right_away", _rayline("r", _ray(Vector2(102, 0), Vector2(400, 0)), dss.intersect_ray(_ray(Vector2(102, 0), Vector2(400, 0)))))
	_it("from_left_through", _rayline("r", _ray(Vector2(98, 0), Vector2(400, 0)), dss.intersect_ray(_ray(Vector2(98, 0), Vector2(400, 0)))))
	_it("from_right_through", _rayline("r", _ray(Vector2(102, 0), Vector2(0, 0)), dss.intersect_ray(_ray(Vector2(102, 0), Vector2(0, 0)))))
	# starts strictly inside, travelling out
	_it("inside_out", _rayline("r", _ray(Vector2(100, 0), Vector2(400, 0)), dss.intersect_ray(_ray(Vector2(100, 0), Vector2(400, 0)))))
	# epsilon outside the left face, travelling away
	_it("eps_out_away", _rayline("r", _ray(Vector2(97.999, 0), Vector2(0, 0)), dss.intersect_ray(_ray(Vector2(97.999, 0), Vector2(0, 0)))))
	# zero-length ray exactly on a face and strictly inside
	_it("zero_on_face", _rayline("r", _ray(Vector2(98, 0), Vector2(98, 0)), dss.intersect_ray(_ray(Vector2(98, 0), Vector2(98, 0)))))
	_it("zero_inside", _rayline("r", _ray(Vector2(100, 0), Vector2(100, 0)), dss.intersect_ray(_ray(Vector2(100, 0), Vector2(100, 0)))))
	var zi := _ray(Vector2(100, 0), Vector2(100, 0))
	zi.hit_from_inside = true
	_it("zero_inside_on", _rayline("r", zi, dss.intersect_ray(zi)))
	# corner start
	_it("corner_start_away", _rayline("r", _ray(Vector2(98, -200), Vector2(0, -400)), dss.intersect_ray(_ray(Vector2(98, -200), Vector2(0, -400)))))
	_pass()

# --------------------------------------------------------------- 9. cast lattice

func _arm_cast_lattice() -> void:
	var w1 := _mk_body("w1", Vector2(100, 0), Vector2(4, 400))
	var w2 := _mk_body("w2", Vector2(300, 0), Vector2(4, 400))
	var ar := _mk_body("ar", Vector2(200, 0), Vector2(4, 400), "area")
	await _frames(2)
	var dss := _dss()
	var c := _circle(8)
	var q := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	_it("base", str(dss.cast_motion(q)))
	var q1 := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(150, 0))
	_it("to_wall1", str(dss.cast_motion(q1)))
	var qm := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	qm.collision_mask = 2
	_it("mask2", str(dss.cast_motion(qm)))
	var qe := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	qe.exclude = [w1.get_rid()]
	_it("excl_w1", str(dss.cast_motion(qe)))
	var qe2 := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	qe2.exclude = [w1.get_rid(), w2.get_rid()]
	_it("excl_both", str(dss.cast_motion(qe2)))
	var qa := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	qa.collide_with_areas = true
	_it("areas_on", str(dss.cast_motion(qa)))
	var qa2 := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(400, 0))
	qa2.collide_with_areas = true
	qa2.collide_with_bodies = false
	_it("areas_only", str(dss.cast_motion(qa2)))
	var qz := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2.ZERO)
	_it("zero_motion", str(dss.cast_motion(qz)))
	var qneg := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(-400, 0))
	_it("negative", str(dss.cast_motion(qneg)))
	# cast from inside the wall
	var qi := _sh(c, Transform2D(0, Vector2(100, 0)), Vector2(400, 0))
	_it("from_inside", str(dss.cast_motion(qi)))
	_pass()

# --------------------------------------------------------------- 10. rest_info

func _ri_line(ri: Dictionary) -> String:
	if ri.is_empty():
		return "{}"
	return "{%s pt=%s n=%s shape=%s}" % [_tag(ri), _v2(ri.get("point", Vector2.ZERO)),
		_v2(ri.get("normal", Vector2.ZERO)), str(ri.get("shape", "-"))]

func _arm_rest_deep() -> void:
	# two overlapping walls at the same x: same depth -> tie
	var a := _mk_body("a", Vector2(100, 0), Vector2(4, 400))
	var b := _mk_body("b", Vector2(100, 0), Vector2(4, 400))
	# a ladder of walls along the motion axis (circle at 96 sweeps +x)
	var l1 := _mk_body("l1", Vector2(300, 0), Vector2(4, 400))
	var l2 := _mk_body("l2", Vector2(400, 0), Vector2(4, 400))
	var l3 := _mk_body("l3", Vector2(500, 0), Vector2(4, 400))
	await _frames(2)
	var dss := _dss()
	var c := _circle(8)
	_it("tie_rest", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(96, 0)), Vector2.ZERO))))
	var q2 := _sh(c, Transform2D(0, Vector2(96, 0)), Vector2.ZERO)
	q2.exclude = [a.get_rid()]
	_it("tie_excl_first", _ri_line(dss.get_rest_info(q2)))
	var q2b := _sh(c, Transform2D(0, Vector2(96, 0)), Vector2.ZERO)
	q2b.exclude = [b.get_rid()]
	_it("tie_excl_second", _ri_line(dss.get_rest_info(q2b)))
	var q3 := _sh(c, Transform2D(0, Vector2(96, 0)), Vector2.ZERO)
	q3.collision_mask = 2
	_it("mask2", _ri_line(dss.get_rest_info(q3)))
	# motion ladder: the nearest wall along the sweep must be the rest contact
	_it("ladder", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(96, 0)), Vector2(600, 0)))))
	var ql := _sh(c, Transform2D(0, Vector2(96, 0)), Vector2(600, 0))
	ql.exclude = [l1.get_rid()]
	_it("ladder_minus_l1", _ri_line(dss.get_rest_info(ql)))
	# zero motion + overlapping bodies of different depth
	var shallow := _mk_body("shallow", Vector2(900, 0), Vector2(4, 400))
	var deep := _mk_body("deep", Vector2(910, 0), Vector2(4, 400))
	await _frames(2)
	var qz := _sh(c, Transform2D(0, Vector2(902, 0)), Vector2.ZERO)
	_it("overlap_zero", _ri_line(dss.get_rest_info(qz)))
	var qz2 := _sh(c, Transform2D(0, Vector2(902, 0)), Vector2.ZERO)
	qz2.exclude = [shallow.get_rid()]
	_it("overlap_excl_shallow", _ri_line(dss.get_rest_info(qz2)))
	var ri4 := dss.get_rest_info(_sh(c, Transform2D(0, Vector2(500, 500)), Vector2.ZERO))
	_it("empty", "{}" if ri4.is_empty() else "nonempty")
	_it("keys", str(_sorted(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(96, 0)), Vector2.ZERO)).keys())))
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 11. collide pairs

func _arm_collide_pair() -> void:
	var a := _mk_body("a", Vector2(100, 0), Vector2(4, 400))
	var b := _mk_body("b", Vector2(104, 0), Vector2(4, 400))
	await _frames(2)
	var dss := _dss()
	var c := _circle(8)
	var q := _sh(c, Transform2D(0, Vector2(102, 0)), Vector2.ZERO)
	var cs := dss.collide_shape(q)
	_it("n", str(cs.size()))
	var pts: Array = []
	for p in cs:
		pts.append(_v2(p))
	_it("pts", "[%s]" % ",".join(pts))
	for cap in [1, 2, 4, 32]:
		var qc := _sh(c, Transform2D(0, Vector2(102, 0)), Vector2.ZERO)
		_it("cap%d" % cap, "n%d" % dss.collide_shape(qc, cap).size())
	var qm := _sh(c, Transform2D(0, Vector2(102, 0)), Vector2.ZERO)
	qm.collision_mask = 2
	_it("mask2", "n%d" % dss.collide_shape(qm).size())
	var qe := _sh(c, Transform2D(0, Vector2(102, 0)), Vector2.ZERO)
	qe.exclude = [a.get_rid()]
	_it("excl_a", "n%d" % dss.collide_shape(qe).size())
	var qz := _sh(c, Transform2D(0, Vector2(500, 500)), Vector2.ZERO)
	_it("empty", "n%d" % dss.collide_shape(qz).size())
	var qr := _sh(c, Transform2D(0, Vector2(102, 0)), Vector2.ZERO)
	_it("rep", "n%d" % dss.collide_shape(qr).size())
	_it("rev", str(_rev))
	_pass()

# --------------------------------------------------------------- 12. exclude forms

func _arm_excl_forms() -> void:
	var a := _mk_body("a", Vector2(100, 0), Vector2(40, 40))
	await _frames(2)
	var dss := _dss()
	var cs: CollisionShape2D = a.get_child(0)
	var shape_rid := cs.shape.get_rid()
	var body_rid := a.get_rid()
	var q := _pt(Vector2(100, 0), 0)
	_it("baseline", _ord(dss.intersect_point(q)))
	var q1 := _pt(Vector2(100, 0), 0)
	q1.exclude = [body_rid]
	_it("body_rid", _ord(dss.intersect_point(q1)))
	var q2 := _pt(Vector2(100, 0), 0)
	q2.exclude = [shape_rid]
	_it("shape_rid", _ord(dss.intersect_point(q2)))
	var q3 := _pt(Vector2(100, 0), 0)
	q3.exclude = [RID()]
	_it("null_rid", _ord(dss.intersect_point(q3)))
	var q4 := _pt(Vector2(100, 0), 0)
	q4.exclude = []
	_it("empty_excl", _ord(dss.intersect_point(q4)))
	var q5 := _pt(Vector2(100, 0), 0)
	q5.exclude = [body_rid, body_rid]
	_it("dup_rid", _ord(dss.intersect_point(q5)))
	var q6 := _ray(Vector2(0, 0), Vector2(200, 0))
	q6.exclude = [shape_rid]
	_it("ray_shape_rid", _rayline("r", q6, dss.intersect_ray(q6)))
	_it("shape_rid_matches", str(shape_rid == body_rid))
	_pass()

# --------------------------------------------------------------- 13b. freshness

func _arm_fresh() -> void:
	var dss := _dss()
	var b := _mk_body("f", Vector2(100, 0), Vector2(40, 40))
	_it("add_t0_point", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	var r0 := _ray(Vector2(0, 0), Vector2(200, 0))
	_it("add_t0_ray", _rayline("r", r0, dss.intersect_ray(r0)))
	var s0 := _sh(_rect(Vector2(40, 40)), Transform2D(0, Vector2(100, 0)))
	_it("add_t0_shape", _ord(dss.intersect_shape(s0, CAP)))
	await physics_frame
	_it("add_t1_point", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	await physics_frame
	_it("add_t2_point", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	# node-tier position write, same frame
	b.position = Vector2(500, 0)
	_it("move_t0_point_old", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("move_t0_point_new", _ord(dss.intersect_point(_pt(Vector2(500, 0)), CAP)))
	await physics_frame
	_it("move_t1_point_old", _ord(dss.intersect_point(_pt(Vector2(100, 0)), CAP)))
	_it("move_t1_point_new", _ord(dss.intersect_point(_pt(Vector2(500, 0)), CAP)))
	# server-tier teleport (the r79 edge-0 write), same frame
	PhysicsServer2D.body_set_state(b.get_rid(), PhysicsServer2D.BODY_STATE_TRANSFORM,
		Transform2D(0, Vector2(900, 0)))
	_it("tele_t0_point_old", _ord(dss.intersect_point(_pt(Vector2(500, 0)), CAP)))
	_it("tele_t0_point_new", _ord(dss.intersect_point(_pt(Vector2(900, 0)), CAP)))
	await physics_frame
	_it("tele_t1_point_old", _ord(dss.intersect_point(_pt(Vector2(500, 0)), CAP)))
	_it("tele_t1_point_new", _ord(dss.intersect_point(_pt(Vector2(900, 0)), CAP)))
	# free, same frame
	var c := _mk_body("c", Vector2(1200, 0), Vector2(40, 40))
	await physics_frame
	_it("pre_free", _ord(dss.intersect_point(_pt(Vector2(1200, 0)), CAP)))
	c.queue_free()
	_it("free_t0", _ord(dss.intersect_point(_pt(Vector2(1200, 0)), CAP)))
	await physics_frame
	_it("free_t1", _ord(dss.intersect_point(_pt(Vector2(1200, 0)), CAP)))
	# visibility toggle
	var d := _mk_body("d", Vector2(1400, 0), Vector2(40, 40))
	await physics_frame
	d.visible = false
	_it("vis_off_point", _ord(dss.intersect_point(_pt(Vector2(1400, 0)), CAP)))
	# disable/collision_layer change, same frame
	var e := _mk_body("e", Vector2(1600, 0), Vector2(40, 40))
	await physics_frame
	e.collision_layer = 2
	_it("layer_t0", _ord(dss.intersect_point(_pt(Vector2(1600, 0)), CAP)))
	await physics_frame
	_it("layer_t1", _ord(dss.intersect_point(_pt(Vector2(1600, 0)), CAP)))
	_pass()

func _arm_rest_semantics() -> void:
	_mk_body("w", Vector2(100, 0), Vector2(4, 400))
	_mk_body("w2", Vector2(300, 0), Vector2(4, 400))
	_mk_body("short", Vector2(150, 0), Vector2(4, 20))
	await _frames(2)
	var dss := _dss()
	var c := _circle(8)
	_it("A_200", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(200, 0)))))
	_it("A_600", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(600, 0)))))
	_it("A_50", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(50, 0)))))
	_it("B_from96_600", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(96, 0)), Vector2(600, 0)))))
	_it("B_from96_200", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(96, 0)), Vector2(200, 0)))))
	_it("B_from96_0", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(96, 0)), Vector2.ZERO))))
	var exq := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(600, 0))
	exq.exclude = [root.get_node("w").get_rid()]
	_it("C_excl_w", _ri_line(dss.get_rest_info(exq)))
	var exq2 := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(600, 0))
	exq2.exclude = [root.get_node("w2").get_rid()]
	_it("C_excl_w2", _ri_line(dss.get_rest_info(exq2)))
	var exq3 := _sh(c, Transform2D(0, Vector2(0, 0)), Vector2(600, 0))
	exq3.exclude = [root.get_node("short").get_rid()]
	_it("C_excl_short", _ri_line(dss.get_rest_info(exq3)))
	_it("E_motion0_far", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(500, 500)), Vector2(0, 0)))))
	_it("F_from0_150", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 0)), Vector2(150, 0)))))
	_it("G_offaxis", _ri_line(dss.get_rest_info(_sh(c, Transform2D(0, Vector2(0, 500)), Vector2(200, 0)))))
	# larger shape sweeping across both walls
	_it("H_rect60x20", _ri_line(dss.get_rest_info(_sh(_rect(Vector2(60, 20)), Transform2D(0, Vector2(0, 0)), Vector2(400, 0)))))
	_it("H_rect60x20_zero", _ri_line(dss.get_rest_info(_sh(_rect(Vector2(60, 20)), Transform2D(0, Vector2(0, 0)), Vector2(0, 0)))))
	_pass()

func _shq(shape: Shape2D, at: Vector2, motion: Vector2, mask: int, excl: Array) -> PhysicsShapeQueryParameters2D:
	var q := _sh(shape, Transform2D(0, at), motion)
	q.collision_mask = mask
	q.exclude = excl
	return q

# --------------------------------------------------------------- 7b. alt-construction ordering

func _mk_shape_body(tag: String, pos: Vector2, kind: String, rot_deg := 0.0) -> CollisionObject2D:
	var b := StaticBody2D.new()
	b.name = tag
	b.set_meta("tag", tag)
	var cs := CollisionShape2D.new()
	match kind:
		"circle30": cs.shape = _circle(30.0)
		"circle50": cs.shape = _circle(50.0)
		"rect60x20": cs.shape = _rect(Vector2(60, 20))
		"rect100": cs.shape = _rect(Vector2(100, 100))
		"rect20x80": cs.shape = _rect(Vector2(20, 80))
		"capsule": var cap := CapsuleShape2D.new(); cap.height = 40.0; cap.radius = 10.0; cs.shape = cap
	b.add_child(cs)
	b.position = pos
	b.rotation = deg_to_rad(rot_deg)
	root.add_child(b)
	return b

func _arm_order_alt() -> void:
	# 6 mixed-shape colliders, all covering the probe point; add order permuted.
	var specs := {
		"q0": [Vector2(0, 0), "circle30", 0.0],
		"q1": [Vector2(5, 0), "rect60x20", 30.0],
		"q2": [Vector2(-5, 0), "capsule", 0.0],
		"q3": [Vector2(0, 0), "rect100", 0.0],
		"q4": [Vector2(10, 0), "circle50", 0.0],
		"q5": [Vector2(0, 5), "rect20x80", 0.0],
	}
	var perms := [["q0", "q1", "q2", "q3", "q4", "q5"],
		["q5", "q4", "q3", "q2", "q1", "q0"],
		["q2", "q0", "q4", "q1", "q5", "q3"]]
	var order: Array = perms[_perm % perms.size()]
	var made: Array = []
	for t in order:
		var s: Array = specs[t]
		made.append(_mk_shape_body(str(t), s[0], str(s[1]), float(s[2])))
	await _frames(2)
	var dss := _dss()
	_it("perm", str(_perm))
	_it("add_order", "[%s]" % ",".join(order))
	_it("point_order", _ord(dss.intersect_point(_pt(Vector2(0, 0)), CAP)))
	_it("point_set", _ord(dss.intersect_point(_pt(Vector2(0, 0)), CAP)))
	_it("shape_order", _ord(dss.intersect_shape(_sh(_rect(Vector2(2, 2)), Transform2D(0, Vector2(0, 0))), CAP)))
	_it("point_rep", str(_ord(dss.intersect_point(_pt(Vector2(0, 0)), CAP)) == _ord(dss.intersect_point(_pt(Vector2(0, 0)), CAP))))
	# same construction translated: layout dependence
	var made2: Array = []
	for t in order:
		var s2: Array = specs[t]
		made2.append(_mk_shape_body(str(t) + "b", s2[0] + Vector2(0, 5000), str(s2[1]), float(s2[2])))
	await _frames(2)
	_it("shifted_order", _ord(dss.intersect_point(_pt(Vector2(0, 5000)), CAP)))
	_it("shifted_same", str(_ord(dss.intersect_point(_pt(Vector2(0, 5000)), CAP)) == _ord(dss.intersect_point(_pt(Vector2(0, 0)), CAP))))
	_pass()

func _arm_space_scope() -> void:
	var root_body := _mk_body("root_body", Vector2(50, 50), Vector2(40, 40))
	var sv := SubViewport.new()
	sv.name = "sv"
	sv.size = Vector2i(64, 64)
	root.add_child(sv)
	var sv_body := StaticBody2D.new()
	sv_body.name = "sv_body"
	sv_body.set_meta("tag", "sv_body")
	var scs := CollisionShape2D.new()
	var srs := RectangleShape2D.new()
	srs.size = Vector2(40, 40)
	scs.shape = srs
	sv_body.add_child(scs)
	sv_body.position = Vector2(50, 50)
	sv.add_child(sv_body)
	await _frames(2)
	var s_root := root.world_2d.space
	var s_sv := sv.world_2d.space
	_it("same_space", str(s_root == s_sv))
	_it("both_valid", "root=%s sv=%s" % [str(s_root.is_valid()), str(s_sv.is_valid())])
	var d_root := PhysicsServer2D.space_get_direct_state(s_root)
	var d_sv := PhysicsServer2D.space_get_direct_state(s_sv)
	_it("root_view", _ord(d_root.intersect_point(_pt(Vector2(50, 50), 0))))
	_it("sv_view", _ord(d_sv.intersect_point(_pt(Vector2(50, 50), 0))))
	_it("root_view_svspot", _ord(d_root.intersect_point(_pt(Vector2(50, 50), 0))))
	_it("dss_identity", "same=%s" % str(d_root == _dss()))
	_it("node_world", "root_body=%s sv_body=%s" % [str(root_body.get_world_2d().space == s_root),
		str(sv_body.get_world_2d().space == s_sv)])
	_pass()
