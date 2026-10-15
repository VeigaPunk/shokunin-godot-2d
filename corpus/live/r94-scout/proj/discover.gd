extends SceneTree
# r94-scout discovery probe — CPUParticles2D + GPUParticles2D emission lattice.
# Launch: godot --headless --path proj --script res://discover.gd -- --arm=<arm>
# Every arm prints exactly one `PASS particles_lattice <arm> ...` line.
# Discovery arms are exploratory; the frozen primary probe is particles_lattice.gd.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _v(v: Vector2) -> String:
	return "(%.4f,%.4f)" % [v.x, v.y]

func _sv(v) -> String:
	if v is float:
		return "%.4f" % v
	if v is Vector2:
		return _v(v)
	if v is Color:
		return "%.3f/%.3f/%.3f/%.3f" % [v.r, v.g, v.b, v.a]
	if v == null:
		return "<null>"
	return str(v)

func _consts(cls: String) -> String:
	var parts: Array[String] = []
	var names := ClassDB.class_get_integer_constant_list(cls, true)
	for n in names:
		parts.append("%s=%d" % [n, ClassDB.class_get_integer_constant(cls, n)])
	return ",".join(parts)

func _props(cls: String) -> String:
	var parts: Array[String] = []
	var pl := ClassDB.class_get_property_list(cls)
	for p in pl:
		var usage: int = p["usage"]
		if usage & PROPERTY_USAGE_GROUP or usage & PROPERTY_USAGE_CATEGORY:
			continue
		if not (usage & PROPERTY_USAGE_EDITOR or usage & PROPERTY_USAGE_STORAGE):
			continue
		var inst = ClassDB.instantiate(cls)
		parts.append("%s=%s" % [p["name"], _sv(inst.get(p["name"]))])
	return ",".join(parts)

func _methods(cls: String) -> String:
	var names: Array[String] = []
	for m in ClassDB.class_get_method_list(cls):
		names.append(m["name"])
	names.sort()
	return ",".join(names)

# ------------------------------------------------------------------ census

func _arm_census() -> void:
	print("PASS particles_lattice census",
		" cpu_consts=" + _consts("CPUParticles2D"),
		" gpu_consts=" + _consts("GPUParticles2D"),
		" ppm_consts=" + _consts("ParticleProcessMaterial"))
	print("CENSUS cpu_props=" + _props("CPUParticles2D"))
	print("CENSUS gpu_props=" + _props("GPUParticles2D"))
	print("CENSUS ppm_props=" + _props("ParticleProcessMaterial"))
	print("CENSUS cpu_methods=" + _methods("CPUParticles2D"))
	print("CENSUS gpu_methods=" + _methods("GPUParticles2D"))
	print("CENSUS ppm_methods=" + _methods("ParticleProcessMaterial"))

# ------------------------------------------------------------------ timing harness

# Runs one CPUParticles2D emitter until `finished` (or bound) and returns a
# measurement dictionary.  Counts process frames (unthrottled headless: large),
# physics ticks (60/s: the stable clock) and wall ms.
func _run_oneshot(cfg: Dictionary, max_ph: int = 300) -> Dictionary:
	var n := CPUParticles2D.new()
	for k in cfg:
		n.set(k, cfg[k])
	root.add_child(n)
	var state := {"p": 0, "ph": 0, "fin_ph": -1, "fin_ms": -1.0, "n_fin": 0, "em_fin": false}
	var t0 := Time.get_ticks_usec()
	n.finished.connect(func():
		state["n_fin"] += 1
		state["fin_ph"] = state["ph"]
		state["fin_ms"] = float(Time.get_ticks_usec() - t0) / 1000.0
		state["em_fin"] = n.emitting)
	physics_frame.connect(func(): state["ph"] += 1)
	n.emitting = true
	while state["ph"] < max_ph and state["fin_ph"] < 0:
		await process_frame
		state["p"] += 1
	var out := {
		"fin_ph": state["fin_ph"], "fin_ms": state["fin_ms"], "n_fin": state["n_fin"],
		"p_frames": state["p"], "ph_total": state["ph"],
		"em_after": n.emitting, "one_shot_after": n.one_shot,
		"em_at_fin": state["em_fin"], "node": n,
	}
	return out

func _fmt(r: Dictionary) -> String:
	return "fin_ph=%d fin_ms=%d n_fin=%d p=%d ph=%d em_after=%s os_after=%s em_at_fin=%s" % [
		r["fin_ph"], roundi(r["fin_ms"]), r["n_fin"], r["p_frames"], r["ph_total"],
		str(r["em_after"]), str(r["one_shot_after"]), str(r["em_at_fin"])]

# ------------------------------------------------------------------ cpu one-shot ladder

func _arm_cpu_os() -> void:
	var r1 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	var r2 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 0.0})
	var r3 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 0.5})
	print("PASS particles_lattice cpu_os e1[%s] e0[%s] e05[%s]" % [_fmt(r1), _fmt(r2), _fmt(r3)])
	r1["node"].queue_free(); r2["node"].queue_free(); r3["node"].queue_free()

func _arm_cpu_speed() -> void:
	var r1 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "speed_scale": 2.0})
	var r2 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "speed_scale": 0.5})
	print("PASS particles_lattice cpu_speed ss2[%s] ss05[%s]" % [_fmt(r1), _fmt(r2)])
	r1["node"].queue_free(); r2["node"].queue_free()

func _arm_cpu_pre() -> void:
	var r1 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "preprocess": 0.25})
	var r2 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 0.0, "preprocess": 0.25})
	print("PASS particles_lattice cpu_pre e1_pre25[%s] e0_pre25[%s]" % [_fmt(r1), _fmt(r2)])
	r1["node"].queue_free(); r2["node"].queue_free()

func _arm_cpu_fixed() -> void:
	var r1 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "fixed_fps": 30})
	var r2 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "fixed_fps": 30, "fract_delta": false})
	print("PASS particles_lattice cpu_fixed ff30[%s] ff30_nofract[%s]" % [_fmt(r1), _fmt(r2)])
	r1["node"].queue_free(); r2["node"].queue_free()

func _arm_cpu_lt() -> void:
	var r1 := await _run_oneshot({"one_shot": true, "lifetime": 1.0, "amount": 8, "explosiveness": 1.0})
	var r2 := await _run_oneshot({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0})
	var r3 := await _run_oneshot({"one_shot": true, "lifetime": 0.1, "amount": 8, "explosiveness": 1.0})
	print("PASS particles_lattice cpu_lt l1[%s] l025[%s] l01[%s]" % [_fmt(r1), _fmt(r2), _fmt(r3)])
	r1["node"].queue_free(); r2["node"].queue_free(); r3["node"].queue_free()

# ------------------------------------------------------------------ cpu continuous / stop

func _arm_cpu_stop() -> void:
	# continuous emitter, stop at a chosen physics tick, then watch for finished.
	var n := CPUParticles2D.new()
	n.one_shot = false
	n.lifetime = 0.5
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var state := {"p": 0, "ph": 0, "fin_ph": -1, "n_fin": 0, "stop_ph": -1, "em_at_stop": false}
	var t0 := Time.get_ticks_usec()
	n.finished.connect(func():
		state["n_fin"] += 1
		state["fin_ph"] = state["ph"])
	physics_frame.connect(func(): state["ph"] += 1)
	n.emitting = true
	while state["ph"] < 10:
		await process_frame
		state["p"] += 1
	state["em_at_stop"] = n.emitting
	state["stop_ph"] = state["ph"]
	n.emitting = false
	var stop_ms := float(Time.get_ticks_usec() - t0) / 1000.0
	while state["ph"] < 120 and state["fin_ph"] < 0:
		await process_frame
		state["p"] += 1
	print("PASS particles_lattice cpu_stop stop_ph=%d stop_ms=%d em_at_stop=%s fin_ph=%d fin_after_stop=%s n_fin=%d live_after_stop=%s" % [
		state["stop_ph"], roundi(stop_ms), str(state["em_at_stop"]), state["fin_ph"],
		str(state["fin_ph"] - state["stop_ph"]), state["n_fin"],
		str(state["fin_ph"] > state["stop_ph"] and state["fin_ph"] >= 0)])
	n.queue_free()

func _arm_cpu_stop_late() -> void:
	# continuous emitter left running past one lifetime, then stopped.
	var n := CPUParticles2D.new()
	n.one_shot = false
	n.lifetime = 0.5
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var state := {"p": 0, "ph": 0, "fin_ph": -1, "n_fin": 0, "stop_ph": -1}
	n.finished.connect(func():
		state["n_fin"] += 1
		state["fin_ph"] = state["ph"])
	physics_frame.connect(func(): state["ph"] += 1)
	n.emitting = true
	while state["ph"] < 40:
		await process_frame
		state["p"] += 1
	state["stop_ph"] = state["ph"]
	n.emitting = false
	var wait_ph: int = int(state["ph"]) + 60
	while state["ph"] < wait_ph and state["fin_ph"] < 0:
		await process_frame
		state["p"] += 1
	print("PASS particles_lattice cpu_stop_late stop_ph=%d fin_ph=%d fin_after_stop=%s n_fin=%d" % [
		state["stop_ph"], state["fin_ph"], str(state["fin_ph"] - state["stop_ph"]), state["n_fin"]])
	n.queue_free()

func _arm_cpu_restart() -> void:
	# one-shot: wait for finish, restart(), wait for a second finish.
	var r1 := await _run_oneshot({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0})
	var n: CPUParticles2D = r1["node"]
	var state := {"p": 0, "ph": 0, "fin2_ph": -1, "n_fin": 0, "em_before": n.emitting}
	state["ph0"] = state["ph"]
	n.finished.connect(func():
		state["n_fin"] += 1
		state["fin2_ph"] = state["ph"])
	n.restart()
	var em_after_restart := n.emitting
	while state["ph"] < 200 and state["fin2_ph"] < 0:
		await process_frame
		state["p"] += 1
	print("PASS particles_lattice cpu_restart first[%s] em_before_restart=%s em_after_restart=%s fin2_ph=%d n_fin=%d" % [
		_fmt(r1), str(state["em_before"]), str(em_after_restart), state["fin2_ph"], state["n_fin"]])
	n.queue_free()

func _arm_cpu_retrigger() -> void:
	# one-shot: after finished, set emitting=true again.
	var r1 := await _run_oneshot({"one_shot": true, "lifetime": 0.25, "amount": 8, "explosiveness": 1.0})
	var n: CPUParticles2D = r1["node"]
	var state := {"p": 0, "ph": 0, "fin2_ph": -1, "n_fin": 0}
	n.finished.connect(func():
		state["n_fin"] += 1
		state["fin2_ph"] = state["ph"])
	n.emitting = true
	var em_set := n.emitting
	while state["ph"] < 200 and state["fin2_ph"] < 0:
		await process_frame
		state["p"] += 1
	print("PASS particles_lattice cpu_retrigger first[%s] em_set=%s fin2_ph=%d n_fin=%d em_after=%s" % [
		_fmt(r1), str(em_set), state["fin2_ph"], state["n_fin"], str(n.emitting)])
	n.queue_free()

func _arm_cpu_hidden() -> void:
	var r1 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0, "visible": false})
	var r2 := await _run_oneshot({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	print("PASS particles_lattice cpu_hidden hidden[%s] visible[%s]" % [_fmt(r1), _fmt(r2)])
	r1["node"].queue_free(); r2["node"].queue_free()

func _arm_cpu_detach() -> void:
	# one-shot: remove from tree mid-flight (tick 5), then re-add at tick 20.
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.5
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var state := {"p": 0, "ph": 0, "fin_ph": -1, "n_fin": 0}
	n.finished.connect(func():
		state["n_fin"] += 1
		state["fin_ph"] = state["ph"])
	physics_frame.connect(func(): state["ph"] += 1)
	n.emitting = true
	while state["ph"] < 5:
		await process_frame
		state["p"] += 1
	root.remove_child(n)
	var det_ph: int = int(state["ph"])
	while state["ph"] < det_ph + 15:
		await process_frame
		state["p"] += 1
	root.add_child(n)
	var re_ph: int = int(state["ph"])
	var bound: int = re_ph + 90
	while state["ph"] < bound and state["fin_ph"] < 0:
		await process_frame
		state["p"] += 1
	print("PASS particles_lattice cpu_detach det_ph=%d re_ph=%d fin_ph=%d fin_after_re=%s n_fin=%d" % [
		det_ph, re_ph, state["fin_ph"], str(state["fin_ph"] - re_ph), state["n_fin"]])
	n.queue_free()

# ------------------------------------------------------------------ gpu headless

func _arm_gpu() -> void:
	var results: Array[String] = []
	for cfg_name in ["one_shot", "continuous"]:
		var n := GPUParticles2D.new()
		var m := ParticleProcessMaterial.new()
		n.process_material = m
		n.lifetime = 0.5
		n.amount = 8
		n.explosiveness = 1.0
		n.one_shot = (cfg_name == "one_shot")
		root.add_child(n)
		var state := {"p": 0, "ph": 0, "fin_ph": -1, "n_fin": 0}
		n.finished.connect(func():
			state["n_fin"] += 1
			state["fin_ph"] = state["ph"])
		physics_frame.connect(func(): state["ph"] += 1)
		n.emitting = true
		while state["ph"] < 90 and state["fin_ph"] < 0:
			await process_frame
			state["p"] += 1
		results.append("%s[fin_ph=%d n_fin=%d ph=%d em_after=%s em_set=%s]" % [
			cfg_name, state["fin_ph"], state["n_fin"], state["ph"], str(n.emitting), str(n.emitting)])
		n.queue_free()
	# 3D control: GPUParticles3D on the same build (is the inertness 2D-specific?)
	var n3 := GPUParticles3D.new()
	n3.lifetime = 0.5
	n3.amount = 8
	n3.explosiveness = 1.0
	n3.one_shot = true
	n3.process_material = ParticleProcessMaterial.new()
	root.add_child(n3)
	var s3 := {"p": 0, "ph": 0, "fin_ph": -1, "n_fin": 0}
	n3.finished.connect(func():
		s3["n_fin"] += 1
		s3["fin_ph"] = s3["ph"])
	physics_frame.connect(func(): s3["ph"] += 1)
	n3.emitting = true
	while s3["ph"] < 90 and s3["fin_ph"] < 0:
		await process_frame
		s3["p"] += 1
	print("PASS particles_lattice gpu " + " ".join(results) + " gpu3d[fin_ph=%d n_fin=%d em_after=%s]" % [
		s3["fin_ph"], s3["n_fin"], str(n3.emitting)])
	n3.queue_free()

# ------------------------------------------------------------------ misc readbacks

func _arm_rs() -> void:
	var n := CPUParticles2D.new()
	root.add_child(n)
	var g := GPUParticles2D.new()
	g.process_material = ParticleProcessMaterial.new()
	root.add_child(g)
	print("PASS particles_lattice rs cpu_rid=%s gpu_rid=%s rs_particles_active=%s" % [
		str(n.get_rid()), str(g.get_rid()), str(RenderingServer.has_method("particles_is_inactive"))])
	n.queue_free(); g.queue_free()

# ------------------------------------------------------------------ dispatch

func _initialize() -> void:
	var arm := _arg("arm", "census")
	match arm:
		"census": _arm_census()
		"cpu_os": await _arm_cpu_os()
		"cpu_speed": await _arm_cpu_speed()
		"cpu_pre": await _arm_cpu_pre()
		"cpu_fixed": await _arm_cpu_fixed()
		"cpu_lt": await _arm_cpu_lt()
		"cpu_stop": await _arm_cpu_stop()
		"cpu_stop_late": await _arm_cpu_stop_late()
		"cpu_restart": await _arm_cpu_restart()
		"cpu_retrigger": await _arm_cpu_retrigger()
		"cpu_hidden": await _arm_cpu_hidden()
		"cpu_detach": await _arm_cpu_detach()
		"gpu": await _arm_gpu()
		"rs": _arm_rs()
		_:
			print("PASS particles_lattice unknown arm=" + arm)
	quit(0)
