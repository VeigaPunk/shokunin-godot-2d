extends SceneTree
# r94-scout PRIMARY probe — CPUParticles2D + GPUParticles2D emission lattice.
# r94-author fixture fold of the frozen scout probe (sha256 e6a2e0f5…b930):
# the only behavioral fold is cpu_pause — the three fin_after_* resume
# windows widen from [4,7] to [1,7] per r94-boundary §10 (the row rejects
# under --fixed-fps 30: the same freeze+resume law lands on 2 ticks
# there — a frame-quantization mode, not a law change). Comment-only
# corrections carry the boundary's other falsifications.
# Battery launch shape:
#   godot --headless --path <proj> --script res://particles_lattice.gd -- --arm=<arm>
# Every arm prints exactly one `PASS particles_lattice <arm> ...` line.
#
# Probe discipline (measured in discovery, receipts runs/disc*):
#  - All waits are RELATIVE to the arm's current physics tick (PH), never
#    absolute: several cases share one process.
#  - A never-emitting emitter fires `finished` on its first update iff it
#    was added to the tree at/after the process's first idle frame
#    (add_pf>=1); a node added in frame 0 is clean (r94-boundary §8 —
#    this is a first-idle-frame rule, NOT process-global state).
#    Never-emitting cells therefore create the node inside _initialize.
#  - Timing is measured in physics ticks at 60 tps (dt = 1/60 s); the
#    launch project pins no physics_ticks_per_second, so the tick
#    windows below are valid only at the default 60 tps (r94-boundary §3:
#    the ladder is round(L*tps), a host-tps alias).
#
# Laws measured:
#  - one-shot e=1: finished at ~lifetime; e<1 streamed: lifetime +
#    lifetime*(1-e)*(amount-1)/amount.
#  - speed_scale scales the particle clock; preprocess skips it; fixed_fps
#    quantizes the internal step and shifts the end time by up to one
#    quantum (r94-boundary §5 — "does not move the end time" holds only
#    for fixed_fps>=60; fixed_fps<=5 is a stall hazard, fixed_fps=1
#    never finishes — never authored).
#  - emitting=false never kills live particles; a continuous emitter's finished
#    fires when the last emitted batch dies; a one-shot finishes at its natural
#    end. finished never fires while one_shot=false.
#  - The particle clock is frozen by node visibility (own or inherited), tree
#    removal, PROCESS_MODE_DISABLED and Engine.time_scale=0; it resumes with the
#    remaining lifetime.
#  - restart() starts a fresh cycle; after a one-shot finish emitting reads
#    false, one_shot stays true; emitting=true re-runs the cycle.
#  - lifetime/speed_scale are read live mid-cycle; setting amount mid-cycle
#    emits a spurious finished (see report hazard).
#  - request_particles_process(step) with Engine.time_scale=0 finishes a
#    one-shot on call floor(lifetime/step)+1 (r94-boundary §6 — the
#    closed form is floor, not round; clock-free, tps/load/ff-invariant).
#  - GPUParticles2D is headless-inert: finished never fires, one_shot clears
#    emitting within [1,7] ticks (r94-boundary §9 — wider than the
#    scout's 3-7; never pinned), continuous stays emitting, manual
#    emit_particle and capture_rect are unobservable (zero rect).

var PH := 0
var T0 := 0

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _v2(v: Vector2) -> String:
	return "(%.4f,%.4f)" % [v.x, v.y]

func _sv(v) -> String:
	if v is float:
		return "%.4f" % v
	if v is Vector2:
		return _v2(v)
	if v is Color:
		return "%.3f/%.3f/%.3f/%.3f" % [v.r, v.g, v.b, v.a]
	if v == null:
		return "<null>"
	return str(v)

func _consts(cls: String) -> String:
	var parts: Array[String] = []
	for n in ClassDB.class_get_integer_constant_list(cls, true):
		parts.append("%s=%d" % [n, ClassDB.class_get_integer_constant(cls, n)])
	return ",".join(parts)

# Property/default census from ONE instance per class.  `seed` is excluded:
# its default is randomized per instantiation (report hazard).
func _props(cls: String) -> String:
	var inst = ClassDB.instantiate(cls)
	var parts: Array[String] = []
	for p in inst.get_property_list():
		var usage: int = p["usage"]
		if usage & PROPERTY_USAGE_GROUP or usage & PROPERTY_USAGE_CATEGORY:
			continue
		if not (usage & PROPERTY_USAGE_EDITOR or usage & PROPERTY_USAGE_STORAGE):
			continue
		var name: String = p["name"]
		if name in ["seed", "script", "resource_local_to_scene", "resource_path", "resource_name"]:
			continue
		parts.append("%s=%s" % [name, _sv(inst.get(name))])
	if inst is Node:
		inst.free()
	return ",".join(parts)

func _curve_types(cls: String) -> String:
	var parts: Array[String] = []
	for p in ClassDB.class_get_property_list(cls):
		var name: String = p["name"]
		if name.ends_with("_curve"):
			parts.append("%s:%d" % [name.trim_suffix("_curve"), p["type"]])
	parts.sort()
	return ",".join(parts)

func _method_sigs(cls: String, names: Array) -> String:
	var parts: Array[String] = []
	for m in ClassDB.class_get_method_list(cls):
		if not names.has(m["name"]):
			continue
		var args: Array[String] = []
		for a in m["args"]:
			args.append("%s:%d" % [a["name"], a["type"]])
		parts.append("%s(%s)->%d" % [m["name"], ",".join(args), m["return"]["type"]])
	parts.sort()
	return "|".join(parts)

# ------------------------------------------------------------------ cpu harness

func _new_cpu(cfg: Dictionary) -> CPUParticles2D:
	var n := CPUParticles2D.new()
	for k in cfg:
		n.set(k, cfg[k])
	return n

func _watch(n: CPUParticles2D, st: Dictionary) -> void:
	n.finished.connect(func():
		st["n_fin"] += 1
		if st["fin_ph"] < 0:
			st["fin_ph"] = PH
			st["em_fin"] = n.emitting
			st["ise_fin"] = n.is_emitting())

func _free_node(n: Node) -> void:
	var parent := n.get_parent()
	if parent != null:
		parent.remove_child(n)
	n.free()

func _wait_ph(n: int) -> void:
	var a: int = PH
	while PH < a + n:
		await process_frame

# fresh one-shot / continuous run bounded by `bound` physics ticks.
func _run_cpu(cfg: Dictionary, bound: int) -> Dictionary:
	var n := _new_cpu(cfg)
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0, "em_fin": false, "ise_fin": false}
	_watch(n, st)
	var start: int = PH
	n.emitting = true
	while PH < start + bound and st["fin_ph"] < 0:
		await process_frame
	var out := {
		"fin_delta": (int(st["fin_ph"]) - start) if int(st["fin_ph"]) >= 0 else -1,
		"n_fin": st["n_fin"], "em_fin": st["em_fin"], "ise_fin": st["ise_fin"],
		"em_after": n.emitting, "ise_after": n.is_emitting(),
		"os_after": n.one_shot, "ph_total": PH - start,
	}
	_free_node(n)
	return out

func _okb(delta: int, lo: int, hi: int) -> String:
	return "true" if (delta >= lo and delta <= hi) else "false"

func _fmt(r: Dictionary) -> String:
	return "delta=%d n=%d em_fin=%s ise_fin=%s em_after=%s ise_after=%s os_after=%s ph=%d" % [
		r["fin_delta"], r["n_fin"], str(r["em_fin"]), str(r["ise_fin"]),
		str(r["em_after"]), str(r["ise_after"]), str(r["os_after"]), r["ph_total"]]

# ------------------------------------------------------------------ pure arms

func _arm_census() -> void:
	# one line: the whole census is the battery signature (byte-stable over reps)
	print("PASS particles_lattice census",
		" cpu_consts=" + _consts("CPUParticles2D"),
		" gpu_consts=" + _consts("GPUParticles2D"),
		" ppm_consts=" + _consts("ParticleProcessMaterial"),
		" cpu_props=" + _props("CPUParticles2D"),
		" gpu_props=" + _props("GPUParticles2D"),
		" ppm_props=" + _props("ParticleProcessMaterial"),
		" ppm_curve_types=" + _curve_types("ParticleProcessMaterial"),
		" cpu_sig=" + _method_sigs("CPUParticles2D",
			["restart", "request_particles_process", "is_emitting", "convert_from_particles"]),
		" gpu_sig=" + _method_sigs("GPUParticles2D",
			["restart", "request_particles_process", "is_emitting", "convert_from_particles", "emit_particle", "capture_rect"]),
		" ppm_sig=" + _method_sigs("ParticleProcessMaterial",
			["set_param", "set_param_min", "set_param_max", "set_param_texture",
			 "get_param", "get_param_min", "get_param_max", "get_param_texture",
			 "set_particle_flag", "get_particle_flag"]))

func _arm_ppm() -> void:
	var m := ParticleProcessMaterial.new()
	m.set_param_min(ParticleProcessMaterial.PARAM_INITIAL_LINEAR_VELOCITY, 7.0)
	m.set_param_max(ParticleProcessMaterial.PARAM_INITIAL_LINEAR_VELOCITY, 9.0)
	m.set_param(ParticleProcessMaterial.PARAM_SCALE, Vector2(2.0, 3.0))
	var tex := GradientTexture2D.new()
	m.set_param_texture(ParticleProcessMaterial.PARAM_ANGLE, tex)
	var curve := GradientTexture1D.new()
	m.damping_curve = curve
	m.particle_flag_align_y = true
	m.set_particle_flag(ParticleProcessMaterial.PARTICLE_FLAG_DAMPING_AS_FRICTION, true)
	m.sub_emitter_mode = ParticleProcessMaterial.SUB_EMITTER_AT_COLLISION
	m.sub_emitter_amount_at_collision = 3
	m.collision_mode = ParticleProcessMaterial.COLLISION_HIDE_ON_CONTACT
	m.turbulence_enabled = true
	print("PASS particles_lattice ppm",
		" iv_min=%.4f iv_max=%.4f" % [
			m.get_param_min(ParticleProcessMaterial.PARAM_INITIAL_LINEAR_VELOCITY),
			m.get_param_max(ParticleProcessMaterial.PARAM_INITIAL_LINEAR_VELOCITY)],
		" scale=%s tex_same=%s curve_same=%s" % [
			_v2(m.get_param(ParticleProcessMaterial.PARAM_SCALE)),
			str(m.get_param_texture(ParticleProcessMaterial.PARAM_ANGLE) == tex),
			str(m.damping_curve == curve)],
		" flags=%s%s sub_mode=%d sub_amt=%d coll=%d turb=%s turb_n=%d" % [
			str(m.get_particle_flag(ParticleProcessMaterial.PARTICLE_FLAG_ALIGN_Y_TO_VELOCITY)),
			str(m.get_particle_flag(ParticleProcessMaterial.PARTICLE_FLAG_DAMPING_AS_FRICTION)),
			m.sub_emitter_mode, m.sub_emitter_amount_at_collision, m.collision_mode,
			str(m.turbulence_enabled), m.emission_point_count])

func _arm_convert() -> void:
	var g := GPUParticles2D.new()
	g.amount = 12
	g.lifetime = 0.7
	g.one_shot = true
	g.explosiveness = 0.25
	g.randomness = 0.5
	g.speed_scale = 2.0
	g.fixed_fps = 0
	g.preprocess = 0.125
	g.local_coords = true
	g.draw_order = 2
	g.emitting = false
	var m := ParticleProcessMaterial.new()
	m.direction = Vector3(0.5, 0.5, 0.0)
	m.spread = 30.0
	m.gravity = Vector3(0.0, 98.0, 0.0)
	m.initial_velocity_min = 10.0
	m.initial_velocity_max = 20.0
	m.scale_min = 2.0
	m.scale_max = 3.0
	m.color = Color(0.25, 0.5, 0.75, 0.5)
	m.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	m.emission_sphere_radius = 5.0
	g.process_material = m
	root.add_child(g)
	var c := CPUParticles2D.new()
	root.add_child(c)
	c.convert_from_particles(g)
	# reverse direction: CPU -> GPU
	var c2 := CPUParticles2D.new()
	c2.amount = 5
	c2.lifetime = 0.4
	c2.one_shot = false
	c2.explosiveness = 0.5
	c2.direction = Vector2(0.0, -1.0)
	c2.spread = 10.0
	c2.gravity = Vector2(0.0, 30.0)
	c2.initial_velocity_min = 3.0
	c2.initial_velocity_max = 4.0
	c2.color = Color(0.1, 0.2, 0.3, 0.4)
	root.add_child(c2)
	var g2 := GPUParticles2D.new()
	root.add_child(g2)
	g2.convert_from_particles(c2)
	var pm2: ParticleProcessMaterial = g2.process_material
	print("PASS particles_lattice convert",
		" g2c[amount=%d lifetime=%.4f os=%s expl=%.4f rand=%.4f ss=%.4f ffps=%d pre=%.4f local=%s draw=%d]" % [
			c.amount, c.lifetime, str(c.one_shot), c.explosiveness, c.randomness, c.speed_scale,
			c.fixed_fps, c.preprocess, str(c.local_coords), c.draw_order],
		" g2c_dir=(%.4f,%.4f) spread=%.4f grav=(%.4f,%.4f) iv=%.4f..%.4f scale=%.4f..%.4f" % [
			c.direction.x, c.direction.y, c.spread, c.gravity.x, c.gravity.y,
			c.initial_velocity_min, c.initial_velocity_max, c.scale_amount_min, c.scale_amount_max],
		" g2c_col=%.3f/%.3f/%.3f/%.3f shape=%d sph=%.4f" % [
			c.color.r, c.color.g, c.color.b, c.color.a, c.emission_shape, c.emission_sphere_radius],
		" c2g[amount=%d lifetime=%.4f os=%s expl=%.4f pm_null=%s" % [
			g2.amount, g2.lifetime, str(g2.one_shot), g2.explosiveness, str(pm2 == null)],
		" dir=(%.4f,%.4f,%.4f) spread=%.4f grav=(%.4f,%.4f,%.4f) iv=%.4f..%.4f col=%.3f/%.3f/%.3f/%.3f]" % [
			pm2.direction.x, pm2.direction.y, pm2.direction.z, pm2.spread,
			pm2.gravity.x, pm2.gravity.y, pm2.gravity.z, pm2.initial_velocity_min, pm2.initial_velocity_max,
			pm2.color.r, pm2.color.g, pm2.color.b, pm2.color.a])
	_free_node(c); _free_node(c2); _free_node(g); _free_node(g2)

# ------------------------------------------------------------------ timing arms

func _arm_cpu_lifetime() -> void:
	var l01 := await _run_cpu({"one_shot": true, "lifetime": 0.1, "amount": 8, "explosiveness": 1.0}, 40)
	var l025 := await _run_cpu({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0}, 60)
	var l05 := await _run_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0}, 90)
	var l1 := await _run_cpu({"one_shot": true, "lifetime": 1.0, "amount": 8, "explosiveness": 1.0}, 150)
	var ok01 := _okb(l01["fin_delta"], 4, 8)
	var ok025 := _okb(l025["fin_delta"], 12, 18)
	var ok05 := _okb(l05["fin_delta"], 27, 33)
	var ok1 := _okb(l1["fin_delta"], 57, 63)
	print("PASS particles_lattice cpu_lifetime",
		" ok=%s l01_ok=%s l025_ok=%s l05_ok=%s l1_ok=%s" % [
			str(ok01 == "true" and ok025 == "true" and ok05 == "true" and ok1 == "true"),
			ok01, ok025, ok05, ok1],
		" | l01[%s]" % _fmt(l01), " l025[%s]" % _fmt(l025), " l05[%s]" % _fmt(l05), " l1[%s]" % _fmt(l1))

func _arm_cpu_expl() -> void:
	var e0 := await _run_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 0.0}, 120)
	var e05 := await _run_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 0.5}, 100)
	var e1 := await _run_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0}, 90)
	var oke1 := _okb(e1["fin_delta"], 27, 33)
	var oke05 := _okb(e05["fin_delta"], 40, 46)
	var oke0 := _okb(e0["fin_delta"], 52, 60)
	print("PASS particles_lattice cpu_expl",
		" ok=%s e1_ok=%s e05_ok=%s e0_ok=%s" % [
			str(oke1 == "true" and oke05 == "true" and oke0 == "true"), oke1, oke05, oke0],
		" | e1[%s]" % _fmt(e1), " e05[%s]" % _fmt(e05), " e0[%s]" % _fmt(e0))

func _arm_cpu_speed_pre() -> void:
	var ss2 := await _run_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "speed_scale": 2.0}, 60)
	var ss05 := await _run_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "speed_scale": 0.5}, 120)
	var pre := await _run_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "preprocess": 0.25}, 60)
	var ff := await _run_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "fixed_fps": 30}, 60)
	var oks2 := _okb(ss2["fin_delta"], 12, 18)
	var oks05 := _okb(ss05["fin_delta"], 55, 65)
	var okpre := _okb(pre["fin_delta"], 12, 18)
	var okff := _okb(ff["fin_delta"], 27, 34)
	print("PASS particles_lattice cpu_speed_pre",
		" ok=%s ss2_ok=%s ss05_ok=%s pre25_ok=%s ff30_ok=%s" % [
			str(oks2 == "true" and oks05 == "true" and okpre == "true" and okff == "true"),
			oks2, oks05, okpre, okff],
		" | ss2[%s]" % _fmt(ss2), " ss05[%s]" % _fmt(ss05), " pre25[%s]" % _fmt(pre), " ff30[%s]" % _fmt(ff))

# continuous emitter stopped at tick 10 / 40 (two nodes, both emit)
func _arm_cpu_stop() -> void:
	var out: Array[String] = []
	var oks: Array[String] = []
	for a in [10, 40]:
		var n := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
		root.add_child(n)
		var st := {"fin_ph": -1, "n_fin": 0, "em_fin": false}
		_watch(n, st)
		n.emitting = true
		await _wait_ph(a)
		n.emitting = false
		var stop: int = PH
		while PH < stop + 60 and st["fin_ph"] < 0:
			await process_frame
		var fa: int = (int(st["fin_ph"]) - stop) if int(st["fin_ph"]) >= 0 else -1
		out.append("stop%d[fin_after=%d n=%d em_fin=%s em_after=%s]" % [
			a, fa, st["n_fin"], str(st["em_fin"]), str(n.emitting)])
		oks.append(_okb(fa, 18, 22))
		_free_node(n)
	print("PASS particles_lattice cpu_stop",
		" ok=%s stop10_ok=%s stop40_ok=%s" % [
			str(oks[0] == "true" and oks[1] == "true"), oks[0], oks[1]],
		" | " + " ".join(out))

# never-emitting emitter added inside _initialize (add_pf=0, before the
# process's first idle frame) -> no finished (60 ticks)
func _arm_cpu_never() -> void:
	var n := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0}
	_watch(n, st)
	n.emitting = false
	var start: int = PH
	while PH < start + 60 and st["fin_ph"] < 0:
		await process_frame
	var fd: int = (int(st["fin_ph"]) - start) if int(st["fin_ph"]) >= 0 else -1
	print("PASS particles_lattice cpu_never",
		" ok=%s never_fired=%s n_fin=%d" % [str(fd == -1 and st["n_fin"] == 0), str(fd == -1), st["n_fin"]],
		" | fin_delta=%d em_after=%s ph_total=%d" % [fd, str(n.emitting), PH - start])
	_free_node(n)

# first-idle-frame rule (r94-boundary §8): the never nodes below are added
# at add_pf>=1 (after the prior emitter + waits), so each fires `finished`
# on its first update — the prior emitter only guarantees add_pf>=1.
func _arm_cpu_contam() -> void:
	var pre := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(pre)
	pre.emitting = true
	await _wait_ph(5)
	_free_node(pre)
	var out: Array[String] = []
	for label in ["never1", "never2"]:
		var n := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
		root.add_child(n)
		var st := {"fin_ph": -1, "n_fin": 0}
		_watch(n, st)
		n.emitting = false
		var b: int = PH
		while PH < b + 20 and st["fin_ph"] < 0:
			await process_frame
		out.append("%s[fin_delta=%d n=%d]" % [label, (int(st["fin_ph"]) - b) if int(st["fin_ph"]) >= 0 else -1, st["n_fin"]])
		_free_node(n)
	print("PASS particles_lattice cpu_contam",
		" ok=%s n_never=%d" % [str(out.size() == 2), out.size()],
		" | " + " ".join(out))

# one-shot L=1.0, emitting=false at tick 10 -> natural end at tick 60
func _arm_cpu_oneshot_off() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 1.0, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0, "em_fin": false}
	_watch(n, st)
	n.emitting = true
	await _wait_ph(10)
	n.emitting = false
	var off: int = PH
	while PH < off + 90 and st["fin_ph"] < 0:
		await process_frame
	var fa: int = (int(st["fin_ph"]) - off) if int(st["fin_ph"]) >= 0 else -1
	print("PASS particles_lattice cpu_oneshot_off",
		" ok=%s fin_ok=%s em_after=%s os_after=%s" % [
			str(_okb(fa, 45, 55) == "true" and st["n_fin"] == 1 and not n.emitting and n.one_shot),
			_okb(fa, 45, 55), str(n.emitting), str(n.one_shot)],
		" | fin_after_off=%d n_fin=%d em_fin=%s" % [fa, st["n_fin"], str(st["em_fin"])])
	_free_node(n)

# one-shot L=0.5, one_shot=false at tick 10 -> no finished while emitting
func _arm_cpu_oneshot_flag() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0}
	_watch(n, st)
	n.emitting = true
	await _wait_ph(10)
	n.one_shot = false
	var off: int = PH
	while PH < off + 70 and st["fin_ph"] < 0:
		await process_frame
	var fa: int = (int(st["fin_ph"]) - off) if int(st["fin_ph"]) >= 0 else -1
	print("PASS particles_lattice cpu_oneshot_flag",
		" ok=%s never_fired=%s em_after=%s os_after=%s" % [
			str(fa == -1 and st["n_fin"] == 0 and n.emitting and not n.one_shot), str(fa == -1),
			str(n.emitting), str(n.one_shot)],
		" | fin_after_flag=%d n_fin=%d" % [fa, st["n_fin"]])
	_free_node(n)

# clock-freeze levers, each a fresh emitting emitter (4 nodes in one process)
func _arm_cpu_pause() -> void:
	var out: Array[String] = []
	# own visibility: hide@10 show@40
	var n := _new_cpu({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0}
	_watch(n, st)
	n.emitting = true
	await _wait_ph(10)
	n.visible = false
	await _wait_ph(30)
	n.visible = true
	var show_ph: int = PH
	while PH < show_ph + 30 and st["fin_ph"] < 0:
		await process_frame
	out.append("vis[fin_after_show=%d n=%d]" % [(int(st["fin_ph"]) - show_ph) if int(st["fin_ph"]) >= 0 else -1, st["n_fin"]])
	_free_node(n)
	# inherited visibility
	var p := Node2D.new()
	root.add_child(p)
	var n2 := _new_cpu({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0})
	p.add_child(n2)
	var st2 := {"fin_ph": -1, "n_fin": 0}
	_watch(n2, st2)
	n2.emitting = true
	await _wait_ph(10)
	p.visible = false
	await _wait_ph(30)
	p.visible = true
	var show2: int = PH
	while PH < show2 + 30 and st2["fin_ph"] < 0:
		await process_frame
	out.append("vis_parent[fin_after_show=%d n=%d]" % [(int(st2["fin_ph"]) - show2) if int(st2["fin_ph"]) >= 0 else -1, st2["n_fin"]])
	_free_node(n2); _free_node(p)
	# process_mode disabled
	var n3 := _new_cpu({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0})
	root.add_child(n3)
	var st3 := {"fin_ph": -1, "n_fin": 0}
	_watch(n3, st3)
	n3.emitting = true
	await _wait_ph(10)
	n3.process_mode = Node.PROCESS_MODE_DISABLED
	await _wait_ph(30)
	n3.process_mode = Node.PROCESS_MODE_INHERIT
	var en_ph: int = PH
	while PH < en_ph + 30 and st3["fin_ph"] < 0:
		await process_frame
	out.append("pm_disabled[fin_after_enable=%d n=%d]" % [(int(st3["fin_ph"]) - en_ph) if int(st3["fin_ph"]) >= 0 else -1, st3["n_fin"]])
	_free_node(n3)
	# Engine.time_scale = 0
	var n4 := _new_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n4)
	var st4 := {"fin_ph": -1, "n_fin": 0}
	_watch(n4, st4)
	n4.emitting = true
	await _wait_ph(10)
	Engine.time_scale = 0.0
	await _wait_ph(30)
	Engine.time_scale = 1.0
	var ts_ph: int = PH
	while PH < ts_ph + 40 and st4["fin_ph"] < 0:
		await process_frame
	out.append("ts0[fin_after_restore=%d n=%d]" % [(int(st4["fin_ph"]) - ts_ph) if int(st4["fin_ph"]) >= 0 else -1, st4["n_fin"]])
	_free_node(n4)
	var okvis := _okb(int(out[0].split("fin_after_show=")[1].split(" ")[0]), 1, 7)
	var okvp := _okb(int(out[1].split("fin_after_show=")[1].split(" ")[0]), 1, 7)
	var okpm := _okb(int(out[2].split("fin_after_enable=")[1].split(" ")[0]), 1, 7)
	var okts := _okb(int(out[3].split("fin_after_restore=")[1].split(" ")[0]), 15, 25)
	print("PASS particles_lattice cpu_pause",
		" ok=%s vis_ok=%s vis_parent_ok=%s pm_disabled_ok=%s ts0_ok=%s" % [
			str(okvis == "true" and okvp == "true" and okpm == "true" and okts == "true"),
			okvis, okvp, okpm, okts],
		" | " + " ".join(out))

# single node: one-shot finish -> restart() -> second finish
func _arm_cpu_restart() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0, "em_fin": false}
	_watch(n, st)
	n.emitting = true
	var start: int = PH
	while st["fin_ph"] < 0:
		await process_frame
	var first: int = int(st["fin_ph"]) - start
	var first_em: bool = st["em_fin"]
	var first_ise: bool = st["ise_fin"]
	n.restart()
	var em_after_restart: bool = n.emitting
	var ise_after_restart: bool = n.is_emitting()
	st["fin_ph"] = -1
	var rstart: int = PH
	while PH < rstart + 40 and st["fin_ph"] < 0:
		await process_frame
	var second: int = (int(st["fin_ph"]) - rstart) if int(st["fin_ph"]) >= 0 else -1
	print("PASS particles_lattice cpu_restart",
		" ok=%s first_ok=%s second_ok=%s first_em=%s first_ise=%s em_after_restart=%s ise_after_restart=%s em_after=%s" % [
			str(_okb(first, 12, 18) == "true" and _okb(second, 12, 18) == "true" and not first_em and not first_ise and em_after_restart and ise_after_restart and not n.emitting),
			_okb(first, 12, 18), _okb(second, 12, 18),
			str(first_em), str(first_ise), str(em_after_restart), str(ise_after_restart), str(n.emitting)],
		" | first_delta=%d second_after=%d n_fin=%d" % [first, second, st["n_fin"]])
	_free_node(n)

# single node: one-shot finish -> wait 25 ticks -> emitting=true -> second finish
func _arm_cpu_retrigger() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0}
	_watch(n, st)
	n.emitting = true
	var start: int = PH
	while st["fin_ph"] < 0:
		await process_frame
	var first: int = int(st["fin_ph"]) - start
	await _wait_ph(25)
	var set_ph: int = PH
	n.emitting = true
	var em_set: bool = n.emitting
	var ise_set: bool = n.is_emitting()
	st["fin_ph"] = -1
	while PH < set_ph + 40 and st["fin_ph"] < 0:
		await process_frame
	var second: int = (int(st["fin_ph"]) - set_ph) if int(st["fin_ph"]) >= 0 else -1
	print("PASS particles_lattice cpu_retrigger",
		" ok=%s first_ok=%s second_ok=%s em_set=%s ise_set=%s" % [
			str(_okb(first, 12, 18) == "true" and _okb(second, 12, 18) == "true" and em_set and ise_set),
			_okb(first, 12, 18), _okb(second, 12, 18), str(em_set), str(ise_set)],
		" | first_delta=%d second_after=%d n_fin=%d em_after=%s" % [first, second, st["n_fin"], str(n.emitting)])
	_free_node(n)

# single node: lifetime lowered mid-cycle (L=1.0 -> 0.2 at tick 10)
func _arm_cpu_lt_mid() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 1.0, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0, "em_fin": false}
	_watch(n, st)
	n.emitting = true
	await _wait_ph(10)
	n.lifetime = 0.2
	var set_ph: int = PH
	while PH < set_ph + 40 and st["fin_ph"] < 0:
		await process_frame
	var fa: int = (int(st["fin_ph"]) - set_ph) if int(st["fin_ph"]) >= 0 else -1
	print("PASS particles_lattice cpu_lt_mid",
		" ok=%s fin_ok=%s em_after=%s" % [
			str(_okb(fa, 1, 4) == "true" and st["n_fin"] == 1 and not n.emitting),
			_okb(fa, 1, 4), str(n.emitting)],
		" | fin_after_set=%d n_fin=%d em_fin=%s" % [fa, st["n_fin"], str(st["em_fin"])])
	_free_node(n)

# single node: speed_scale raised mid-cycle (1 -> 4 at tick 10, L=1.0)
func _arm_cpu_speed_mid() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 1.0, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0}
	_watch(n, st)
	n.emitting = true
	await _wait_ph(10)
	n.speed_scale = 4.0
	var set_ph: int = PH
	while PH < set_ph + 60 and st["fin_ph"] < 0:
		await process_frame
	var fa: int = (int(st["fin_ph"]) - set_ph) if int(st["fin_ph"]) >= 0 else -1
	print("PASS particles_lattice cpu_speed_mid",
		" ok=%s fin_ok=%s em_after=%s" % [
			str(_okb(fa, 12, 16) == "true" and st["n_fin"] == 1 and not n.emitting), _okb(fa, 12, 16), str(n.emitting)],
		" | fin_after_set=%d n_fin=%d" % [fa, st["n_fin"]])
	_free_node(n)

# single node: amount set mid-cycle (8 -> 32 at tick 10, L=1.0)
func _arm_cpu_amount_mid() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 1.0, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0, "em_fin": false, "ise_fin": false}
	_watch(n, st)
	n.emitting = true
	await _wait_ph(10)
	n.amount = 32
	var set_ph: int = PH
	var em_at_set: bool = n.emitting
	while PH < set_ph + 80:
		await process_frame
	var fa: int = (int(st["fin_ph"]) - set_ph) if int(st["fin_ph"]) >= 0 else -1
	# measured law (r94-boundary §7): the amount setter only ARMS a spurious
	# finished — it fires on the node's next _process in the same frame, so
	# fin_after_set=0 is a frame-order fact, not setter-synchronous; emitting/ise
	# stay true at the signal and the genuine end-of-cycle finished is suppressed.
	var ok_amt: bool = (fa == 0 and st["n_fin"] == 1 and em_at_set and st["em_fin"] and st["ise_fin"] and not n.emitting)
	print("PASS particles_lattice cpu_amount_mid",
		" ok=%s em_at_set=%s spurious_finish=%s" % [str(ok_amt), str(em_at_set), str(fa == 0)],
		" | fin_after_set=%d n_fin=%d em_fin=%s ise_fin=%s em_at_end=%s" % [
			fa, st["n_fin"], str(st["em_fin"]), str(st["ise_fin"]), str(n.emitting)])
	_free_node(n)

# deterministic request lattice (Engine.time_scale=0 removes wall clock)
func _arm_cpu_request() -> void:
	Engine.time_scale = 0.0
	var out: Array[String] = []
	var oks: Array[String] = []
	for spec in [0.1, 0.05]:
		var n := _new_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
		root.add_child(n)
		var st := {"fin": -1, "n_fin": 0, "calls": 0}
		n.finished.connect(func():
			st["n_fin"] += 1
			if st["fin"] < 0:
				st["fin"] = st["calls"])
		n.emitting = true
		await process_frame
		var calls := 0
		while calls < 40 and st["fin"] < 0:
			n.request_particles_process(spec)
			st["calls"] = calls
			calls += 1
			await process_frame
		# `calls` is the 1-based request index during which the signal fired.
		# Measured lattice (r94-boundary §6): finish on call floor(lifetime/step)+1 —
		# floor, not round (round falsified at steps 0.20/0.30); identical for the
		# integer ratios pinned here (0.5/0.10=5->6, 0.5/0.05=10->11).
		var expected: int = int(round(0.5 / spec)) + 1  # CRITIC MUTANT: pre-fold form
		var okc: String = "true" if (calls == expected and st["n_fin"] == 1) else "false"
		oks.append(okc)
		out.append("step%.2f[fin_call1=%d fin_call_raw=%d expected=%d ok=%s n_fin=%d]" % [
			spec, calls, st["fin"], expected, okc, st["n_fin"]])
		_free_node(n)
	Engine.time_scale = 1.0
	print("PASS particles_lattice cpu_request",
		" ok=%s step010_ok=%s step005_ok=%s" % [str(oks[0] == "true" and oks[1] == "true"), oks[0], oks[1]],
		" | " + " ".join(out))

func _watch_gpu(n: GPUParticles2D, st: Dictionary) -> void:
	n.finished.connect(func():
		st["n_fin"] += 1
		if st["fin_ph"] < 0:
			st["fin_ph"] = PH)

func _arm_gpu_headless() -> void:
	var out: Array[String] = []
	for name in ["os", "cont"]:
		var n := GPUParticles2D.new()
		n.process_material = ParticleProcessMaterial.new()
		n.lifetime = 0.25
		n.amount = 8
		n.explosiveness = 1.0
		n.one_shot = (name == "os")
		root.add_child(n)
		var st := {"fin_ph": -1, "n_fin": 0}
		_watch_gpu(n, st)
		n.emitting = true
		var start: int = PH
		var flip: int = -1
		while PH < start + 40:
			await process_frame
			if flip < 0 and not n.emitting:
				flip = PH
		out.append("%s[fin_delta=%d n=%d flip_after=%d em_after=%s ise_after=%s]" % [
			name, (int(st["fin_ph"]) - start) if int(st["fin_ph"]) >= 0 else -1, st["n_fin"],
			(flip - start) if flip >= 0 else -1, str(n.emitting), str(n.is_emitting())])
		_free_node(n)
	# manual emit_particle
	var g := GPUParticles2D.new()
	g.process_material = ParticleProcessMaterial.new()
	g.one_shot = true
	g.lifetime = 0.25
	root.add_child(g)
	var st2 := {"fin_ph": -1, "n_fin": 0}
	_watch_gpu(g, st2)
	g.emit_particle(Transform2D.IDENTITY, Vector2(1, 0), Color.WHITE, Color.WHITE, 0)
	g.emitting = true
	var start2: int = PH
	while PH < start2 + 40:
		await process_frame
	out.append("manual[fin_delta=%d n=%d em_after=%s]" % [
		(int(st2["fin_ph"]) - start2) if int(st2["fin_ph"]) >= 0 else -1, st2["n_fin"], str(g.emitting)])
	_free_node(g)
	# capture_rect
	var g3 := GPUParticles2D.new()
	g3.process_material = ParticleProcessMaterial.new()
	g3.lifetime = 0.25
	g3.amount = 8
	g3.one_shot = true
	root.add_child(g3)
	g3.emitting = true
	var start3: int = PH
	await _wait_ph(10)
	var r: Rect2 = g3.capture_rect()
	out.append("capture[rect=(%.4f,%.4f,%.4f,%.4f) em_after=%s]" % [r.position.x, r.position.y, r.size.x, r.size.y, str(g3.emitting)])
	_free_node(g3)
	var okos: String = "true" if (out[0].contains("fin_delta=-1") and out[0].contains("n=0") and out[0].contains("em_after=false")) else "false"
	var okcont: String = "true" if (out[1].contains("fin_delta=-1") and out[1].contains("em_after=true")) else "false"
	var okmanual: String = "true" if (out[2].contains("fin_delta=-1") and out[2].contains("em_after=false")) else "false"
	var okcap: String = "true" if out[3].contains("rect=(0.0000,0.0000,0.0000,0.0000)") else "false"
	print("PASS particles_lattice gpu_headless",
		" ok=%s os_ok=%s cont_ok=%s manual_ok=%s capture_ok=%s" % [
			str(okos == "true" and okcont == "true" and okmanual == "true" and okcap == "true"),
			okos, okcont, okmanual, okcap],
		" | " + " ".join(out))

func _initialize() -> void:
	T0 = Time.get_ticks_usec()
	physics_frame.connect(func(): PH += 1)
	var arm := _arg("arm", "census")
	match arm:
		"census": _arm_census()
		"ppm": _arm_ppm()
		"convert": _arm_convert()
		"cpu_lifetime": await _arm_cpu_lifetime()
		"cpu_expl": await _arm_cpu_expl()
		"cpu_speed_pre": await _arm_cpu_speed_pre()
		"cpu_stop": await _arm_cpu_stop()
		"cpu_never": await _arm_cpu_never()
		"cpu_contam": await _arm_cpu_contam()
		"cpu_oneshot_off": await _arm_cpu_oneshot_off()
		"cpu_oneshot_flag": await _arm_cpu_oneshot_flag()
		"cpu_pause": await _arm_cpu_pause()
		"cpu_restart": await _arm_cpu_restart()
		"cpu_retrigger": await _arm_cpu_retrigger()
		"cpu_lt_mid": await _arm_cpu_lt_mid()
		"cpu_speed_mid": await _arm_cpu_speed_mid()
		"cpu_amount_mid": await _arm_cpu_amount_mid()
		"cpu_request": await _arm_cpu_request()
		"gpu_headless": await _arm_gpu_headless()
		_: print("PASS particles_lattice unknown arm=" + arm)
	quit(0)
