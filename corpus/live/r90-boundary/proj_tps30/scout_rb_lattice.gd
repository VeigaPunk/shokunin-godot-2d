extends SceneTree
# r90 scout probe — RigidBody2D authorability lattice (r88 census's top-ranked REMAINING
# PINNABLE family: gravity_scale / center_of_mass / custom_integrator + the adjacent extras).
# Launch shape: godot --headless --path <proj|proj_tps120> --script res://rb_lattice.gd --
#   --arm=<name> [--frames=N]
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix scan).
# Every arm prints its own name on the PASS line, so a silent fallback is detectable.
# No RIDs / instance ids / addresses are printed (byte-stability).

var arm := ""
var _frames := 60
var _items: PackedStringArray = []
var _watch_script := load("res://rb_watch.gd") as GDScript

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--frames="):
			_frames = int(a.substr(9))
	_run.call_deferred()

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R90 %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS rb_lattice %s %s" % [arm, " ".join(_items)])
	quit()

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _b(v: bool) -> String:
	return "true" if v else "false"

func _pget(o: Object, n: String) -> String:
	var v: Variant = o.get(n)
	if v == null:
		return "<null>"
	if v is Vector2:
		return _v2(v)
	if v is bool:
		return _b(v)
	if v is float:
		return "%.4f" % v
	if v is int:
		return "%d" % v
	return str(v)

func _body(x: float, y: float, shape: Shape2D) -> RigidBody2D:
	var b := RigidBody2D.new()
	b.position = Vector2(x, y)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	b.add_child(cs)
	return b

func _watch(b: RigidBody2D, cb: Callable) -> void:
	b.set_script(_watch_script)
	b.set("sink", cb)

func _circle(r: float) -> CircleShape2D:
	var s := CircleShape2D.new()
	s.radius = r
	return s

func _rect(w: float, h: float) -> RectangleShape2D:
	var s := RectangleShape2D.new()
	s.size = Vector2(w, h)
	return s

func _floor(width: float, top_y: float) -> StaticBody2D:
	var fb := StaticBody2D.new()
	var cs := CollisionShape2D.new()
	cs.shape = _rect(width, 20.0)
	fb.add_child(cs)
	fb.position = Vector2(0, top_y + 10.0)
	root.add_child(fb)
	return fb

func _samples(labels: Array, bodies: Array) -> String:
	var parts: PackedStringArray = []
	for i in labels.size():
		var b: RigidBody2D = bodies[i]
		parts.append("%s[y=%.4f,vy=%.4f]" % [labels[i], b.position.y, b.linear_velocity.y])
	return "|".join(parts)

func _free_all(nodes: Array) -> void:
	for n in nodes:
		if is_instance_valid(n):
			n.free()

func _run() -> void:
	match arm:
		"props": _arm_props()
		"comread": _arm_comread()
		"comrefuse": _arm_comrefuse()
		"gravity": await _arm_gravity()
		"damp": await _arm_damp()
		"order": await _arm_order()
		"write": await _arm_write()
		"impulse": await _arm_impulse()
		"freezelock": await _arm_freezelock()
		"contacts": await _arm_contacts()
		_: _arm_fallback()

func _arm_fallback() -> void:
	_it("fallback", "1")
	_pass()

# ---------- pure: property census ----------

func _arm_props() -> void:
	var props: PackedStringArray = []
	var usage := {}
	for p in ClassDB.class_get_property_list("RigidBody2D"):
		var n := String(p["name"])
		props.append(n)
		usage[n] = int(p["usage"])
	_it("nprops", "%d" % props.size())
	_it("props", "[%s]" % "|".join(props))
	for n in ["center_of_mass", "center_of_mass_local", "inertia", "linear_damp",
			"angular_damp", "constant_force", "constant_torque", "freeze_mode", "sleeping"]:
		_it("u_" + n, "%d" % int(usage.get(n, -1)))
	var ms: PackedStringArray = []
	for m in ClassDB.class_get_method_list("RigidBody2D"):
		var n2 := String(m["name"])
		if n2.contains("impulse") or n2.contains("force") or n2.contains("torque") \
				or n2.contains("state") or n2.contains("gravity") or n2.contains("damp") \
				or n2.contains("constant"):
			ms.append(n2)
	ms.sort()
	_it("methods", "[%s]" % "|".join(ms))
	_it("enum", "COM_AUTO=%d,COM_CUSTOM=%d,FM_STATIC=%d,FM_KINEMATIC=%d,CCD_OFF=%d,CCD_RAY=%d,CCD_SHAPE=%d,DAMP_COMBINE=%d,DAMP_REPLACE=%d" % [
		RigidBody2D.CENTER_OF_MASS_MODE_AUTO, RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM,
		RigidBody2D.FREEZE_MODE_STATIC, RigidBody2D.FREEZE_MODE_KINEMATIC,
		RigidBody2D.CCD_MODE_DISABLED, RigidBody2D.CCD_MODE_CAST_RAY, RigidBody2D.CCD_MODE_CAST_SHAPE,
		RigidBody2D.DAMP_MODE_COMBINE, RigidBody2D.DAMP_MODE_REPLACE])
	_it("ps_gravity", "%.4f" % float(ProjectSettings.get_setting("physics/2d/default_gravity")))
	_it("ps_ldamp", "%.4f" % float(ProjectSettings.get_setting("physics/2d/default_linear_damp")))
	_it("ps_adamp", "%.4f" % float(ProjectSettings.get_setting("physics/2d/default_angular_damp")))
	_it("ps_tps", "%d" % int(ProjectSettings.get_setting("physics/common/physics_ticks_per_second")))
	var b := RigidBody2D.new()
	root.add_child(b)
	for n3 in ["mass", "inertia", "center_of_mass", "center_of_mass_local", "center_of_mass_mode",
			"gravity_scale", "custom_integrator", "freeze", "freeze_mode", "lock_rotation",
			"can_sleep", "sleeping", "continuous_cd", "max_contacts_reported", "contact_monitor",
			"linear_damp", "linear_damp_mode", "angular_damp", "angular_damp_mode",
			"constant_force", "constant_torque"]:
		_it("d_" + n3, _pget(b, n3))
	_free_all([b])
	_pass()

# ---------- pure: center_of_mass modes / inertia override ----------

func _arm_comread() -> void:
	var b := _body(0, 0, _circle(8))
	root.add_child(b)
	_it("auto_com", _pget(b, "center_of_mass"))
	_it("auto_mode", _pget(b, "center_of_mass_mode"))
	_it("coml_prop", _pget(b, "center_of_mass_local"))
	b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
	b.center_of_mass = Vector2(4, 0)
	_it("custom_mode", _pget(b, "center_of_mass_mode"))
	_it("custom_com", _pget(b, "center_of_mass"))
	# rotated body: the single stored COM property read back unchanged
	var d := _body(400, 0, _circle(8))
	d.rotation = PI / 2.0
	root.add_child(d)
	d.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
	d.center_of_mass = Vector2(4, 0)
	_it("rot_com", _pget(d, "center_of_mass"))
	# inertia write-override readback
	d.inertia = 5.0
	_it("inertia5", _pget(d, "inertia"))
	d.inertia = 0.0
	_it("inertia0", _pget(d, "inertia"))
	d.inertia = 33.0
	d.mass = 4.0
	_it("inertia33_mass4", _pget(d, "inertia"))
	d.mass = 1.0
	_it("inertia33_mass1", _pget(d, "inertia"))
	# gravity_scale readback
	var e := _body(600, 0, _circle(8))
	e.gravity_scale = -1.5
	_it("gscale_neg", _pget(e, "gravity_scale"))
	e.gravity_scale = 0.0
	_it("gscale0", _pget(e, "gravity_scale"))
	_free_all([b, d, e])
	_pass()

# ---------- pure: center_of_mass refusal boundary (ERROR-carrying) ----------

func _arm_comrefuse() -> void:
	var a := _body(0, 0, _circle(8))
	root.add_child(a)
	a.center_of_mass = Vector2(4, 0)
	_it("auto_set4", "com=%s mode=%s" % [_pget(a, "center_of_mass"), _pget(a, "center_of_mass_mode")])
	a.center_of_mass = Vector2(0, 0)
	_it("auto_set0", "com=%s mode=%s" % [_pget(a, "center_of_mass"), _pget(a, "center_of_mass_mode")])
	var c := _body(200, 0, _circle(8))
	root.add_child(c)
	c.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
	c.center_of_mass = Vector2(4, 0)
	_it("custom_set4", "com=%s mode=%s" % [_pget(c, "center_of_mass"), _pget(c, "center_of_mass_mode")])
	c.center_of_mass = Vector2(0, 0)
	_it("custom_set0", "com=%s mode=%s" % [_pget(c, "center_of_mass"), _pget(c, "center_of_mass_mode")])
	c.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_AUTO
	_it("back_auto", "com=%s mode=%s" % [_pget(c, "center_of_mass"), _pget(c, "center_of_mass_mode")])
	_free_all([a, c])
	_pass()

# ---------- physics: gravity_scale lattice ----------

func _arm_gravity() -> void:
	var labels := ["g0", "g05", "g1", "g2", "gm1", "zv", "zv0", "cf"]
	var scales := [0.0, 0.5, 1.0, 2.0, -1.0, 0.0, 0.0, 0.0]
	var bodies: Array[RigidBody2D] = []
	for i in labels.size():
		var b := _body(200.0 * i, 0.0, _circle(8))
		b.gravity_scale = scales[i]
		root.add_child(b)
		bodies.append(b)
	bodies[5].linear_velocity = Vector2(0, -30)
	bodies[6].linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	bodies[6].linear_damp = 0.0
	bodies[6].linear_velocity = Vector2(0, -30)
	bodies[7].constant_force = Vector2(0, 980)
	var half := ""
	var full := ""
	for f in _frames:
		await physics_frame
		if f == int(_frames / 2) - 1:
			half = _samples(labels, bodies)
		full = _samples(labels, bodies)
	_it("f%d" % int(_frames / 2), half)
	_it("f%d" % _frames, full)
	_pass()

# ---------- physics: damping lattice + live total_linear_damp oracle ----------

func _arm_damp() -> void:
	var labels := ["default", "rep0", "rep05", "comb05"]
	var bodies: Array[RigidBody2D] = []
	var oracle := {}
	for i in labels.size():
		var b := _body(200.0 * i, 0.0, _circle(8))
		root.add_child(b)
		bodies.append(b)
		var acc := {"tld": -1.0}
		oracle[labels[i]] = acc
		_watch(b, func(s):
			acc["tld"] = s.total_linear_damp)
	bodies[1].linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	bodies[1].linear_damp = 0.0
	bodies[2].linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	bodies[2].linear_damp = 0.5
	bodies[3].linear_damp_mode = RigidBody2D.DAMP_MODE_COMBINE
	bodies[3].linear_damp = 0.5
	var half := ""
	var full := ""
	for f in _frames:
		await physics_frame
		if f == int(_frames / 2) - 1:
			half = _samples(labels, bodies)
		full = _samples(labels, bodies)
	_it("f%d" % int(_frames / 2), half)
	_it("f%d" % _frames, full)
	var o: PackedStringArray = []
	for l in labels:
		o.append("%s=%.4f" % [l, oracle[l]["tld"]])
	_it("tld", "|".join(o))
	_pass()

# ---------- physics: callback ordering vs integration ----------

func _arm_order() -> void:
	var b := _body(0, 0.0, _circle(8))
	root.add_child(b)
	var trace: Array = []
	_watch(b, func(s):
		trace.append({
			"st": s.step, "ty": s.transform.origin.y, "vy": s.linear_velocity.y,
			"g": s.total_gravity.y, "tld": s.total_linear_damp,
			"im": s.inverse_mass, "iI": s.inverse_inertia}))
	var f1 := ""
	var f2 := ""
	var f3 := ""
	var fin := ""
	for f in _frames:
		await physics_frame
		if f == 0:
			f1 = "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y]
		elif f == 1:
			f2 = "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y]
		elif f == 2:
			f3 = "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y]
		fin = "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y]
	_it("ncb", "%d" % trace.size())
	for i in mini(5, trace.size()):
		var t: Dictionary = trace[i]
		_it("cb%d" % i, "st=%.6f ty=%.4f vy=%.4f g=%.4f tld=%.4f im=%.4f iI=%.6f" % [
			t["st"], t["ty"], t["vy"], t["g"], t["tld"], t["im"], t["iI"]])
	if trace.size() > 5:
		var t2: Dictionary = trace[trace.size() - 1]
		_it("cblast", "st=%.6f ty=%.4f vy=%.4f g=%.4f tld=%.4f im=%.4f iI=%.6f" % [
			t2["st"], t2["ty"], t2["vy"], t2["g"], t2["tld"], t2["im"], t2["iI"]])
	_it("f1", f1)
	_it("f2", f2)
	_it("f3", f3)
	_it("f%d" % _frames, fin)
	_pass()

# ---------- physics: custom_integrator write-through ----------

func _arm_write() -> void:
	var labels := ["wzero", "whold", "wman"]
	var bodies: Array[RigidBody2D] = []
	var step0 := {"v": -1.0}
	for i in labels.size():
		var b := _body(200.0 * i, 0.0, _circle(8))
		b.custom_integrator = true
		root.add_child(b)
		bodies.append(b)
	_watch(bodies[0], func(s):
		s.linear_velocity = Vector2.ZERO)
	_watch(bodies[1], func(s):
		var t: Transform2D = s.transform
		t.origin = Vector2(200.0, -50.0)
		s.transform = t)
	_watch(bodies[2], func(s):
		step0["v"] = s.step
		s.linear_velocity += Vector2(0, 980.0 * s.step))
	var half := ""
	var full := ""
	for f in _frames:
		await physics_frame
		if f == int(_frames / 2) - 1:
			half = _samples(labels, bodies)
		full = _samples(labels, bodies)
	_it("step", "%.6f" % step0["v"])
	_it("f%d" % int(_frames / 2), half)
	_it("f%d" % _frames, full)
	_pass()

# ---------- physics: impulse family on known shapes ----------

func _arm_impulse() -> void:
	var labels := ["c_central", "c_off", "c_tq", "r_tq", "r_off"]
	var bodies: Array[RigidBody2D] = []
	var inv := {}
	for i in labels.size():
		var b := _body(200.0 * i, -100.0, _circle(8) if i < 3 else _rect(20, 10))
		b.gravity_scale = 0.0
		b.linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
		b.linear_damp = 0.0
		b.angular_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
		b.angular_damp = 0.0
		root.add_child(b)
		bodies.append(b)
		var acc := {"iI": -1.0, "im": -1.0}
		inv[labels[i]] = acc
		_watch(b, func(s):
			acc["iI"] = s.inverse_inertia
			acc["im"] = s.inverse_mass)
	for f in 2:
		await physics_frame
	bodies[0].apply_central_impulse(Vector2(0, -60))
	bodies[1].apply_impulse(Vector2(0, -60), Vector2(8, 0))
	bodies[2].apply_torque_impulse(480.0)
	bodies[3].apply_torque_impulse(480.0)
	bodies[4].apply_impulse(Vector2(0, -60), Vector2(8, 0))
	for f in 2:
		await physics_frame
	var parts: PackedStringArray = []
	for i in labels.size():
		var b: RigidBody2D = bodies[i]
		parts.append("%s[v=%s,w=%.4f,iI=%.6f,im=%.4f]" % [labels[i], _v2(b.linear_velocity),
			b.angular_velocity, inv[labels[i]]["iI"], inv[labels[i]]["im"]])
	_it("post", "|".join(parts))
	_pass()

# ---------- physics: freeze / lock_rotation / sleep ----------

func _arm_freezelock() -> void:
	_floor(2600.0, 0.0)
	var labels := ["f_normal", "f_static", "f_kin", "f_kin2", "f_lock", "s_off", "s_on"]
	var bodies: Array[RigidBody2D] = []
	for i in labels.size():
		var b := _body(200.0 * i, -100.0, _circle(8))
		root.add_child(b)
		bodies.append(b)
	bodies[1].freeze = true
	bodies[1].freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
	bodies[2].freeze = true
	bodies[2].freeze_mode = RigidBody2D.FREEZE_MODE_KINEMATIC
	bodies[2].linear_velocity = Vector2(0, -30)
	bodies[3].freeze = true
	bodies[3].freeze_mode = RigidBody2D.FREEZE_MODE_KINEMATIC
	bodies[4].gravity_scale = 0.0
	bodies[4].lock_rotation = true
	bodies[4].linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	bodies[4].linear_damp = 0.0
	bodies[5].can_sleep = false
	bodies[6].can_sleep = true
	bodies[5].position.y = -40.0
	bodies[6].position.y = -40.0
	var parts: PackedStringArray = []
	for f in _frames:
		await physics_frame
		if f == 1:
			bodies[3].linear_velocity = Vector2(0, -30)
			bodies[4].apply_impulse(Vector2(0, -60), Vector2(8, 0))
		if f == 29:
			for i in 5:
				var b: RigidBody2D = bodies[i]
				parts.append("%s[y=%.4f,vy=%.4f,w=%.4f,fz=%s]" % [labels[i], b.position.y,
					b.linear_velocity.y, b.angular_velocity, _b(b.freeze)])
	_it("f30", "|".join(parts))
	_it("sleep", "s_off[sl=%s,y=%.4f,vy=%.4f] s_on[sl=%s,y=%.4f,vy=%.4f]" % [
		_b(bodies[5].sleeping), bodies[5].position.y, bodies[5].linear_velocity.y,
		_b(bodies[6].sleeping), bodies[6].position.y, bodies[6].linear_velocity.y])
	_pass()

# ---------- physics: contact instrument ----------

func _arm_contacts() -> void:
	_floor(400.0, 0.0)
	var b := _body(0, -40.0, _circle(8))
	b.contact_monitor = true
	b.max_contacts_reported = 4
	root.add_child(b)
	var hits := {"entered": 0}
	b.body_entered.connect(func(_other):
		hits["entered"] += 1)
	var acc := {"count": -1, "pos": Vector2.ZERO, "y": 0.0, "vel": Vector2.ZERO}
	_watch(b, func(s):
		acc["count"] = s.get_contact_count()
		acc["y"] = s.transform.origin.y
		if s.get_contact_count() > 0:
			acc["pos"] = s.get_contact_local_position(0)
			acc["vel"] = s.get_contact_local_velocity_at_position(0))
	for f in _frames:
		await physics_frame
	_it("rest", "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y])
	_it("cb", "count=%d y=%.4f pos=%s cvel=%s" % [acc["count"], acc["y"],
		_v2(acc["pos"]), _v2(acc["vel"])])
	_it("entered", "%d" % hits["entered"])
	_pass()
