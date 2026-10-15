extends SceneTree
# r94-scout discovery-3 — resolve the open questions from discovery 1/2:
# same-frame restart quirk, request_particles_process isolation, GPU boot stall,
# hidden-from-start resume, mid-flight lifetime/speed changes, convert_from_particles.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _ms(t0: int) -> int:
	return roundi(float(Time.get_ticks_usec() - t0) / 1000.0)

func _new_cpu(lifetime: float, explosiveness: float, one_shot: bool = true) -> CPUParticles2D:
	var n := CPUParticles2D.new()
	n.one_shot = one_shot
	n.lifetime = lifetime
	n.amount = 8
	n.explosiveness = explosiveness
	return n

# ------------------------------------------------------- same-frame restart

func _arm_same_frame_restart() -> void:
	var n := _new_cpu(0.25, 1.0)
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s" % [ph[0], _ms(t0), str(n.emitting)]))
	n.emitting = true
	while ev.size() == 0:
		await process_frame
	ev.append("restart@ph%d/ms%d" % [ph[0], _ms(t0)])
	n.restart()
	while ph[0] < 40:
		await process_frame
	ev.append("t40@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice same_frame_restart " + " ".join(ev))
	n.queue_free()

func _arm_restart_later() -> void:
	var n := _new_cpu(0.25, 1.0)
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s" % [ph[0], _ms(t0), str(n.emitting)]))
	n.emitting = true
	while ev.size() == 0:
		await process_frame
	while ph[0] < 30:
		await process_frame
	ev.append("restart@ph%d/ms%d" % [ph[0], _ms(t0)])
	n.restart()
	while ph[0] < 80:
		await process_frame
	ev.append("t80@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice restart_later " + " ".join(ev))
	n.queue_free()

# ------------------------------------------------------- request isolation

func _arm_request_iso() -> void:
	Engine.time_scale = 0.0
	var out: Array[String] = []
	for spec in [["e1", 0.5, 1.0, 0.1], ["e1_005", 0.5, 1.0, 0.05], ["e0", 0.5, 0.0, 0.1]]:
		var n := _new_cpu(spec[1], spec[2])
		root.add_child(n)
		var state := {"fin": -1, "n_fin": 0, "calls": 0}
		n.finished.connect(func():
			state["n_fin"] += 1
			if state["fin"] < 0:
				state["fin"] = state["calls"])
		n.emitting = true
		await process_frame
		var calls := 0
		while calls < 120 and state["fin"] < 0:
			n.request_particles_process(spec[3])
			state["calls"] = calls
			calls += 1
			await process_frame
		out.append("%s[fin_call=%d n_fin=%d calls=%d em=%s]" % [spec[0], state["fin"], state["n_fin"], calls, str(n.emitting)])
		n.queue_free()
	Engine.time_scale = 1.0
	print("PASS particles_lattice request_iso " + " ".join(out))

# ------------------------------------------------------- gpu boot stall

func _arm_gpu_boot() -> void:
	var out: Array[String] = []
	# control: no GPU node
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	while ph[0] < 6:
		await process_frame
	out.append("control[ms@ph6=%d]" % _ms(t0))
	# with GPU node emitting
	var g := GPUParticles2D.new()
	g.process_material = ParticleProcessMaterial.new()
	g.one_shot = true
	g.lifetime = 0.25
	root.add_child(g)
	var ph2 := [0]
	var t1 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph2[0] += 1)
	g.emitting = true
	var stamps: Array[String] = []
	while ph2[0] < 6:
		await process_frame
		if stamps.size() < ph2[0]:
			stamps.append("%d@%d" % [ph2[0], _ms(t1)])
	out.append("gpu[%s em=%s]" % [",".join(stamps), str(g.emitting)])
	g.queue_free()
	print("PASS particles_lattice gpu_boot " + " ".join(out))

# ------------------------------------------------------- hidden from start

func _arm_vis_start() -> void:
	var n := _new_cpu(0.25, 1.0)
	n.visible = false
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s" % [ph[0], _ms(t0), str(n.emitting)]))
	n.emitting = true
	while ph[0] < 60:
		await process_frame
	ev.append("show@ph%d/em%s" % [ph[0], str(n.emitting)])
	n.visible = true
	while ph[0] < 120 and ev.size() < 2:
		await process_frame
	ev.append("end@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice vis_start " + " ".join(ev))
	n.queue_free()

# ------------------------------------------------------- emitting false/true toggles

func _arm_stop0_cont() -> void:
	var n := _new_cpu(0.25, 1.0, false)
	root.add_child(n)
	var ph := [0]
	var state := {"fin": -1, "n_fin": 0}
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func():
		state["n_fin"] += 1
		state["fin"] = ph[0])
	n.emitting = false
	while ph[0] < 60 and state["fin"] < 0:
		await process_frame
	print("PASS particles_lattice stop0_cont fin_ph=%d n_fin=%d em=%s" % [state["fin"], state["n_fin"], str(n.emitting)])
	n.queue_free()

func _arm_resume() -> void:
	var n := _new_cpu(0.5, 1.0, false)
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s" % [ph[0], _ms(t0), str(n.emitting)]))
	n.emitting = true
	while ph[0] < 10:
		await process_frame
	n.emitting = false
	ev.append("off@ph%d" % ph[0])
	while ph[0] < 30:
		await process_frame
	n.emitting = true
	ev.append("on@ph%d" % ph[0])
	while ph[0] < 120 and ev.size() < 3:
		await process_frame
	ev.append("end@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice resume " + " ".join(ev))
	n.queue_free()

# ------------------------------------------------------- mid-flight levers

func _arm_lt_mid() -> void:
	var n := _new_cpu(1.0, 1.0)
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d" % [ph[0], _ms(t0)]))
	n.emitting = true
	while ph[0] < 10:
		await process_frame
	n.lifetime = 0.2
	ev.append("lt02@ph%d" % ph[0])
	while ph[0] < 80 and ev.size() < 2:
		await process_frame
	ev.append("end@ph%d" % ph[0])
	print("PASS particles_lattice lt_mid " + " ".join(ev))
	n.queue_free()

func _arm_speed_mid() -> void:
	var n := _new_cpu(1.0, 1.0)
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d" % [ph[0], _ms(t0)]))
	n.emitting = true
	while ph[0] < 10:
		await process_frame
	n.speed_scale = 4.0
	ev.append("ss4@ph%d" % ph[0])
	while ph[0] < 120 and ev.size() < 2:
		await process_frame
	ev.append("end@ph%d" % ph[0])
	print("PASS particles_lattice speed_mid " + " ".join(ev))
	n.queue_free()

func _arm_amount_mid() -> void:
	# does changing amount mid-flight restart/alter the finish?
	var n := _new_cpu(0.5, 1.0)
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d" % [ph[0], _ms(t0)]))
	n.emitting = true
	while ph[0] < 10:
		await process_frame
	n.amount = 32
	ev.append("amt32@ph%d" % ph[0])
	while ph[0] < 80 and ev.size() < 2:
		await process_frame
	ev.append("end@ph%d" % ph[0])
	print("PASS particles_lattice amount_mid " + " ".join(ev))
	n.queue_free()

# ------------------------------------------------------- convert / capture / signatures

func _arm_sig() -> void:
	var out: Array[String] = []
	for cls in ["CPUParticles2D", "GPUParticles2D"]:
		for m in ClassDB.class_get_method_list(cls):
			if m["name"] in ["convert_from_particles", "capture_rect", "emit_particle", "request_particles_process", "restart", "is_emitting"]:
				var args: Array[String] = []
				for a in m["args"]:
					args.append("%s:%d" % [a["name"], a["type"]])
				out.append("%s.%s(%s)->%d" % [cls, m["name"], ",".join(args), m["return"]["type"]])
	print("PASS particles_lattice sig " + " ".join(out))

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
	print("PASS particles_lattice convert",
		" amount=%d lifetime=%.4f one_shot=%s expl=%.4f rand=%.4f speed=%.4f ffps=%d pre=%.4f local=%s draw=%d" % [
			c.amount, c.lifetime, str(c.one_shot), c.explosiveness, c.randomness, c.speed_scale,
			c.fixed_fps, c.preprocess, str(c.local_coords), c.draw_order],
		" dir=(%.4f,%.4f) spread=%.4f grav=(%.4f,%.4f) iv=%.4f..%.4f scale=%.4f..%.4f" % [
			c.direction.x, c.direction.y, c.spread, c.gravity.x, c.gravity.y,
			c.initial_velocity_min, c.initial_velocity_max, c.scale_amount_min, c.scale_amount_max],
		" color=%.3f/%.3f/%.3f/%.3f shape=%d sph=%.4f" % [
			c.color.r, c.color.g, c.color.b, c.color.a, c.emission_shape, c.emission_sphere_radius])
	g.queue_free(); c.queue_free()

func _arm_capture() -> void:
	var g := GPUParticles2D.new()
	g.process_material = ParticleProcessMaterial.new()
	g.lifetime = 0.25
	g.amount = 8
	g.one_shot = true
	root.add_child(g)
	g.emitting = true
	var ph := [0]
	physics_frame.connect(func(): ph[0] += 1)
	while ph[0] < 10:
		await process_frame
	var r: Rect2 = g.capture_rect()
	print("PASS particles_lattice capture rect=(%.4f,%.4f,%.4f,%.4f) em=%s" % [r.position.x, r.position.y, r.size.x, r.size.y, str(g.emitting)])
	g.queue_free()

func _initialize() -> void:
	var arm := _arg("arm", "sig")
	match arm:
		"same_frame_restart": await _arm_same_frame_restart()
		"restart_later": await _arm_restart_later()
		"request_iso": await _arm_request_iso()
		"gpu_boot": await _arm_gpu_boot()
		"vis_start": await _arm_vis_start()
		"stop0_cont": await _arm_stop0_cont()
		"resume": await _arm_resume()
		"lt_mid": await _arm_lt_mid()
		"speed_mid": await _arm_speed_mid()
		"amount_mid": await _arm_amount_mid()
		"sig": _arm_sig()
		"convert": _arm_convert()
		"capture": await _arm_capture()
		_: print("PASS particles_lattice unknown arm=" + arm)
	quit(0)
