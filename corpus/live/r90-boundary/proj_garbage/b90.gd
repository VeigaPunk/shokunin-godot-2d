extends SceneTree
# r90-boundary probe — stress the r90 scout's RigidBody2D lattice claims before the author
# pins them. Attack surface (task): (1) integrator ordering under load/120 tps, (2) damp
# oracle across physics engines, (3) one-step-lag tps scaling, (4) impulse extremes,
# (5) COM refusal paths, (6) freeze/contact window under starved batches.
# Launch shape: godot --headless --path <proj> --script res://b90.gd --
#   --arm=<name> [--case=<name>] [--stall=none|idle|phys] [--stall_at=N] [--frames=N]
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix scan).
# Every arm prints its own name on the PASS line (no silent fallback). No RIDs / instance
# ids / addresses are printed. Wall time is on a separate DIAG line so PASS lines stay
# byte-stable in the no-load baseline.

var arm := ""
var _case := ""
var _stall := "none"
var _stall_at := 30
var _delay := 0
var _frames := 60
var _items: PackedStringArray = []
var _watch_script := load("res://b90_watch.gd") as GDScript
var _t0 := 0

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--case="):
			_case = a.substr(7)
		elif a.begins_with("--stall="):
			_stall = a.substr(8)
		elif a.begins_with("--stall_at="):
			_stall_at = int(a.substr(11))
		elif a.begins_with("--delay="):
			_delay = int(a.substr(8))
		elif a.begins_with("--frames="):
			_frames = int(a.substr(9))
	_t0 = Time.get_ticks_msec()
	_run.call_deferred()

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("B90 %s %s=%s" % [arm, key, value])

func _diag(key: String, value: String) -> void:
	print("DIAG %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS rb90_boundary %s %s" % [arm, " ".join(_items)])
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

func _dh(vals: Array) -> String:
	# histogram of consecutive deltas of an int series ("1:60", "1:55,2:3", ...)
	if vals.size() < 2:
		return "short"
	var h := {}
	for i in range(1, vals.size()):
		var d: int = int(vals[i]) - int(vals[i - 1])
		h[d] = int(h.get(d, 0)) + 1
	var ks: Array = h.keys()
	ks.sort()
	var parts: PackedStringArray = []
	for k in ks:
		parts.append("%d:%d" % [int(k), int(h[k])])
	return ",".join(parts)

func _free_all(nodes: Array) -> void:
	for n in nodes:
		if is_instance_valid(n):
			n.free()

func _run() -> void:
	if _delay > 0:
		OS.delay_msec(_delay)
	match arm:
		"order": await _arm_order()
		"write": await _arm_write()
		"lag": await _arm_lag()
		"damp": await _arm_damp()
		"impulse": await _arm_impulse()
		"comcase": _arm_comcase()
		"backend": await _arm_backend()
		"stall": await _arm_stall()
		"settle": await _arm_settle()
		_: _arm_fallback()

func _arm_fallback() -> void:
	_it("fallback", "1")
	_pass()

# ---------- attack 1/6: ordering + per-step accounting (instrumented scout order arm) ----------

func _arm_order() -> void:
	var pf0 := Engine.get_physics_frames()
	var b := _body(0, 0.0, _circle(8))
	root.add_child(b)
	var trace: Array = []
	_watch(b, func(s):
		trace.append({
			"pf": Engine.get_physics_frames(),
			"st": s.step, "ty": s.transform.origin.y, "vy": s.linear_velocity.y,
			"g": s.total_gravity.y, "tld": s.total_linear_damp,
			"im": s.inverse_mass, "iI": s.inverse_inertia}))
	var tvals: Array = []
	var f1 := ""
	var f2 := ""
	var f3 := ""
	var fin := ""
	for f in _frames:
		await physics_frame
		tvals.append(Engine.get_physics_frames())
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
	var cbpfs: Array = []
	for t in trace:
		cbpfs.append(t["pf"])
	_it("cb0_rel", "%d" % (int(cbpfs[0]) - pf0) if cbpfs.size() > 0 else "-1")
	_it("obs0_rel", "%d" % (int(tvals[0]) - pf0) if tvals.size() > 0 else "-1")
	_it("pf_delta", "%d" % (Engine.get_physics_frames() - pf0))
	_it("tick_dh", _dh(tvals))
	_it("cbpf_dh", _dh(cbpfs))
	_diag("wall_ms", "%d" % (Time.get_ticks_msec() - _t0))
	_pass()

# ---------- attack 1: write-through under load (scout write arm + per-step accounting) ----------

func _arm_write() -> void:
	var labels := ["wzero", "whold", "wman"]
	var bodies: Array[RigidBody2D] = []
	var acc := {"step": -1.0, "n": 0}
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
		acc["step"] = s.step
		acc["n"] += 1
		s.linear_velocity += Vector2(0, 980.0 * s.step))
	var pf0 := Engine.get_physics_frames()
	var tvals: Array = []
	var half := ""
	var full := ""
	for f in _frames:
		await physics_frame
		tvals.append(Engine.get_physics_frames())
		if f == int(_frames / 2) - 1:
			half = _samples(labels, bodies)
		full = _samples(labels, bodies)
	_it("step", "%.6f" % acc["step"])
	_it("f%d" % int(_frames / 2), half)
	_it("f%d" % _frames, full)
	_it("ncb", "%d" % acc["n"])
	_it("pf_delta", "%d" % (Engine.get_physics_frames() - pf0))
	_it("tick_dh", _dh(tvals))
	_diag("wall_ms", "%d" % (Time.get_ticks_msec() - _t0))
	_pass()

# ---------- attack 3: one-step-lag law vs tps (N*g*dt^2) ----------

func _arm_lag() -> void:
	var a := _body(0, 0, _circle(8))      # built-in, undamped (REPLACE 0)
	a.linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	a.linear_damp = 0.0
	root.add_child(a)
	var b := _body(200, 0, _circle(8))    # custom_integrator, manual gravity
	b.custom_integrator = true
	root.add_child(b)
	var c := _body(400, 0, _circle(8))    # built-in, default damp (control)
	root.add_child(c)
	var acc := {"an": 0, "bn": 0, "step": -1.0, "apre": 0.0, "bpre": 0.0, "bpost": 0.0}
	_watch(a, func(s):
		acc["an"] += 1
		acc["step"] = s.step
		acc["apre"] = s.linear_velocity.y)
	_watch(b, func(s):
		acc["bn"] += 1
		acc["bpre"] = s.linear_velocity.y
		s.linear_velocity += Vector2(0, 980.0 * s.step)
		acc["bpost"] = s.linear_velocity.y)
	var pf0 := Engine.get_physics_frames()
	var tvals: Array = []
	for f in _frames:
		await physics_frame
		tvals.append(Engine.get_physics_frames())
	var dt: float = acc["step"]
	var n: int = acc["an"]
	_it("a", "y=%.4f,vy=%.4f" % [a.position.y, a.linear_velocity.y])
	_it("b", "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y])
	_it("c", "y=%.4f,vy=%.4f" % [c.position.y, c.linear_velocity.y])
	_it("d", "dy=%.4f,dvy=%.4f" % [a.position.y - b.position.y, a.linear_velocity.y - b.linear_velocity.y])
	_it("step", "%.6f" % dt)
	_it("gdt", "%.4f" % (980.0 * dt))
	_it("gdt2", "%.6f" % (980.0 * dt * dt))
	_it("exp", "N=%d exp_dy=%.4f exp_dvy_gdt=%.4f" % [n, float(n) * 980.0 * dt * dt, 980.0 * dt])
	_it("acc", "an=%d,bn=%d,apre=%.4f,bpre=%.4f,bpost=%.4f" % [
		acc["an"], acc["bn"], acc["apre"], acc["bpre"], acc["bpost"]])
	_it("pf_delta", "%d" % (Engine.get_physics_frames() - pf0))
	_it("tick_dh", _dh(tvals))
	_diag("wall_ms", "%d" % (Time.get_ticks_msec() - _t0))
	_pass()

# ---------- attack 2: damp lattice + live oracle (scout damp arm + per-step accounting) ----------

func _arm_damp() -> void:
	var labels := ["default", "rep0", "rep05", "comb05"]
	var bodies: Array[RigidBody2D] = []
	var oracle := {}
	for i in labels.size():
		var b := _body(200.0 * i, 0.0, _circle(8))
		root.add_child(b)
		bodies.append(b)
		var acc := {"tld": -1.0, "n": 0}
		oracle[labels[i]] = acc
		_watch(b, func(s):
			acc["tld"] = s.total_linear_damp
			acc["n"] += 1)
	bodies[1].linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	bodies[1].linear_damp = 0.0
	bodies[2].linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	bodies[2].linear_damp = 0.5
	bodies[3].linear_damp_mode = RigidBody2D.DAMP_MODE_COMBINE
	bodies[3].linear_damp = 0.5
	var pf0 := Engine.get_physics_frames()
	var tvals: Array = []
	var half := ""
	var full := ""
	for f in _frames:
		await physics_frame
		tvals.append(Engine.get_physics_frames())
		if f == int(_frames / 2) - 1:
			half = _samples(labels, bodies)
		full = _samples(labels, bodies)
	_it("f%d" % int(_frames / 2), half)
	_it("f%d" % _frames, full)
	var o: PackedStringArray = []
	for l in labels:
		o.append("%s=%.4f" % [l, oracle[l]["tld"]])
	_it("tld", "|".join(o))
	_it("ncb", "%d" % oracle["default"]["n"])
	_it("pf_delta", "%d" % (Engine.get_physics_frames() - pf0))
	_it("tick_dh", _dh(tvals))
	_diag("wall_ms", "%d" % (Time.get_ticks_msec() - _t0))
	_pass()

# ---------- attack 4: impulse family at inertia/mass extremes ----------

func _arm_impulse() -> void:
	var lanes := [
		["auto", {}, "std"], ["zero", {"inertia": 0.0}, "std"],
		["tiny", {"inertia": 1e-6}, "std"], ["nano", {"inertia": 1e-9}, "std"],
		["huge", {"inertia": 1e9}, "std"], ["neg", {"inertia": -5.0}, "std"],
		["m_small", {"mass": 0.001}, "std"], ["m_large", {"mass": 1e6}, "std"],
		["mass0", {"mass": 0.0}, "std"], ["massneg", {"mass": -1.0}, "std"],
		["nan_i", {"inertia": NAN}, "std"], ["inf_i", {"inertia": INF}, "std"],
		["s_tqneg", {}, "tqneg"], ["s_offneg", {}, "offneg"], ["s_up", {}, "up"],
	]
	var bodies: Array[RigidBody2D] = []
	var accs: Array = []
	var props: Array = []
	for i in lanes.size():
		var lane: Array = lanes[i]
		var b := _body(200.0 * i, -100.0, _circle(8))
		b.gravity_scale = 0.0
		b.linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
		b.linear_damp = 0.0
		b.angular_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
		b.angular_damp = 0.0
		var cfg: Dictionary = lane[1]
		for k in cfg:
			b.set(k, cfg[k])
		root.add_child(b)
		bodies.append(b)
		var acc := {"iI": -999.0, "im": -999.0, "n": 0}
		accs.append(acc)
		_watch(b, func(s):
			acc["iI"] = s.inverse_inertia
			acc["im"] = s.inverse_mass
			acc["n"] += 1)
		props.append("inertia=%s,mass=%s" % [_pget(b, "inertia"), _pget(b, "mass")])
	for f in 2:
		await physics_frame
	for i in lanes.size():
		var b: RigidBody2D = bodies[i]
		match String(lanes[i][2]):
			"tqneg":
				b.apply_torque_impulse(-480.0)
				b.apply_central_impulse(Vector2(0, -60))
			"offneg":
				b.apply_impulse(Vector2(0, -60), Vector2(-8, 0))
			"up":
				b.apply_central_impulse(Vector2(0, 60))
			_:
				b.apply_torque_impulse(480.0)
				b.apply_central_impulse(Vector2(0, -60))
	for f in 2:
		await physics_frame
	var parts: PackedStringArray = []
	for i in lanes.size():
		var b: RigidBody2D = bodies[i]
		parts.append("%s[v=%s,w=%.4f,iI=%.6f,im=%.6f,%s]" % [lanes[i][0], _v2(b.linear_velocity),
			b.angular_velocity, accs[i]["iI"], accs[i]["im"], props[i]])
	_it("post", "|".join(parts))
	_pass()

# ---------- attack 5: center_of_mass refusal paths (one case per process) ----------

func _com(key: String, b: RigidBody2D) -> void:
	_it(key, "com=%s mode=%s" % [_pget(b, "center_of_mass"), _pget(b, "center_of_mass_mode")])

func _arm_comcase() -> void:
	_it("case", _case)
	match _case:
		"intree_auto_diff":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			_com("pre", b)
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
		"intree_auto_same":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass = Vector2(0, 0)
			_com("post", b)
		"intree_custom_diff":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
		"frozen_static_auto_diff":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.freeze = true
			b.freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
			b.freeze = false
			_com("post_unfreeze", b)
		"frozen_kin_auto_diff":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.freeze = true
			b.freeze_mode = RigidBody2D.FREEZE_MODE_KINEMATIC
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
			b.freeze = false
			_com("post_unfreeze", b)
		"frozen_static_custom_diff":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.freeze = true
			b.freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
		"frozen_kin_custom_diff":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.freeze = true
			b.freeze_mode = RigidBody2D.FREEZE_MODE_KINEMATIC
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
		"nottree_auto_diff":
			var b := _body(0, 0, _circle(8))
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
			root.add_child(b)
			_com("post_add", b)
		"nottree_custom_diff":
			var b := _body(0, 0, _circle(8))
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
			root.add_child(b)
			_com("post_add", b)
		"set_via_set":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.set("center_of_mass", Vector2(4, 0))
			_com("post", b)
		"mode_invalid":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass_mode = 99
			_com("post_mode", b)
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
		"mode_neg":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass_mode = -1
			_com("post_mode", b)
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
		"custom_freeze_sequence":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(4, 0)
			b.freeze = true
			b.freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
			b.center_of_mass = Vector2(8, 0)
			_com("post", b)
			b.freeze = false
			_com("post_unfreeze", b)
		"auto_nan":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass = Vector2(NAN, NAN)
			_com("post", b)
		"custom_nan":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(NAN, NAN)
			_com("post", b)
		"frozen_static_auto_then_mode":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.freeze = true
			b.freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
			b.center_of_mass = Vector2(4, 0)
			_com("post", b)
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(4, 0)
			_com("post_custom", b)
		"custom_back_auto_diff":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(4, 0)
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_AUTO
			_com("post_auto", b)
			b.center_of_mass = Vector2(4, 0)
			_com("post_set", b)
		"custom_dupe":
			var b := _body(0, 0, _circle(8))
			root.add_child(b)
			b.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
			b.center_of_mass = Vector2(4, 0)
			b.center_of_mass = Vector2(4, 0)
			_com("post_dupe", b)
			b.center_of_mass = Vector2(8, 0)
			_com("post_new", b)
		_:
			_it("unknown_case", _case)
	_pass()

# ---------- attack 2: live backend identity + drop test (Dummy / Jolt2D-string / garbage) ----------

func _arm_backend() -> void:
	var cfg := str(ProjectSettings.get_setting("physics/2d/physics_engine", "<unset>"))
	var hint := "<absent>"
	for p in ProjectSettings.get_property_list():
		if p.get("name") == "physics/2d/physics_engine":
			hint = str(p.get("hint_string"))
	_it("cfg2d", cfg)
	_it("hint2d", hint)
	var obj = Engine.get_singleton("PhysicsServer2D")
	_it("id2d", obj.get_class() if obj != null else "<nosuch>")
	_it("cls_exists", "GodotPhysicsServer2D=%s,Dummy=%s" % [
		ClassDB.class_exists("GodotPhysicsServer2D"), ClassDB.class_exists("PhysicsServer2DDummy")])
	var w = root.get_world_2d() if root != null else null
	var dss = w.direct_space_state if w != null else null
	_it("dss2d", dss.get_class() if dss != null else "<null>")
	var pf0 := Engine.get_physics_frames()
	var b := _body(0, -100, _circle(8))
	root.add_child(b)
	var acc := {"n": 0, "tld": -1.0}
	_watch(b, func(s):
		acc["n"] += 1
		acc["tld"] = s.total_linear_damp)
	var tvals: Array = []
	for f in 30:
		await physics_frame
		tvals.append(Engine.get_physics_frames())
	_it("drop", "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y])
	_it("ncb", "%d" % acc["n"])
	_it("tld", "%.4f" % acc["tld"])
	_it("pf_delta", "%d" % (Engine.get_physics_frames() - pf0))
	_it("tick_dh", _dh(tvals))
	_diag("wall_ms", "%d" % (Time.get_ticks_msec() - _t0))
	_pass()

# ---------- attack 6: starved batches (idle-context and physics-context stalls) ----------

func _arm_stall() -> void:
	var pf0 := Engine.get_physics_frames()
	var b := _body(0, 0.0, _circle(8))
	root.add_child(b)
	var trace: Array = []
	_watch(b, func(s):
		trace.append({"pf": Engine.get_physics_frames(), "ty": s.transform.origin.y,
			"vy": s.linear_velocity.y}))
	var stalled := {"n": 0}
	if _stall == "idle":
		process_frame.connect(func():
			stalled["n"] += 1
			if stalled["n"] == _stall_at:
				OS.delay_msec(300))
	var tvals: Array = []
	var near := {}
	var fN := ""
	for f in _frames:
		if _stall == "phys" and f == _stall_at:
			OS.delay_msec(300)
		await physics_frame
		tvals.append(Engine.get_physics_frames())
		if f >= _stall_at - 1 and f <= _stall_at + 2:
			near[f] = "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y]
		fN = "y=%.4f,vy=%.4f" % [b.position.y, b.linear_velocity.y]
	var cbpfs: Array = []
	for t in trace:
		cbpfs.append(t["pf"])
	_it("stall", _stall)
	_it("stall_at", "%d" % _stall_at)
	_it("ncb", "%d" % trace.size())
	var np: PackedStringArray = []
	var ks: Array = near.keys()
	ks.sort()
	for k in ks:
		np.append("f%d[%s]" % [int(k), near[k]])
	_it("near", "|".join(np))
	_it("fN", fN)
	_it("pf_delta", "%d" % (Engine.get_physics_frames() - pf0))
	_it("tick_dh", _dh(tvals))
	_it("cbpf_dh", _dh(cbpfs))
	_diag("stalled_n", "%d" % stalled["n"])
	_diag("wall_ms", "%d" % (Time.get_ticks_msec() - _t0))
	_pass()

# ---------- attack 6: freeze/contact window margin (is 120 frames enough under load?) ----------

func _arm_settle() -> void:
	_floor(2000.0, 0.0)
	var b := _body(0, -100.0, _circle(8))
	root.add_child(b)
	var bc := _body(300, -40.0, _circle(8))
	bc.contact_monitor = true
	bc.max_contacts_reported = 4
	root.add_child(bc)
	var hits := {"entered": 0}
	bc.body_entered.connect(func(_o):
		hits["entered"] += 1)
	var acc := {"count": -1, "n": 0}
	_watch(bc, func(s):
		acc["count"] = s.get_contact_count()
		acc["n"] += 1)
	var s_on := _body(600, -40.0, _circle(8))
	s_on.can_sleep = true
	root.add_child(s_on)
	var s_off := _body(800, -40.0, _circle(8))
	s_off.can_sleep = false
	root.add_child(s_off)
	var pf0 := Engine.get_physics_frames()
	var tvals: Array = []
	var samples := {}
	for f in _frames:
		await physics_frame
		tvals.append(Engine.get_physics_frames())
		if f == 29 or f == 59 or f == 89 or f == _frames - 1:
			samples[f + 1] = "n[y=%.4f,vy=%.4f] c[y=%.4f,cnt=%d,ent=%d] so[y=%.4f,sl=%s] sf[y=%.4f,sl=%s]" % [
				b.position.y, b.linear_velocity.y,
				bc.position.y, acc["count"], hits["entered"],
				s_on.position.y, _b(s_on.sleeping), s_off.position.y, _b(s_off.sleeping)]
	var ks: Array = samples.keys()
	ks.sort()
	for k in ks:
		_it("f%d" % int(k), samples[k])
	_it("ncb", "%d" % acc["n"])
	_it("pf_delta", "%d" % (Engine.get_physics_frames() - pf0))
	_it("tick_dh", _dh(tvals))
	_diag("wall_ms", "%d" % (Time.get_ticks_msec() - _t0))
	_pass()
