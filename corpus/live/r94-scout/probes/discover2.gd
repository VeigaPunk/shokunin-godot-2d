extends SceneTree
# r94-scout discovery-2 — fine traces for the surprising discovery cells:
# restart re-fire timing, GPU headless inertness, visibility/tree pause levers,
# request_particles_process determinism, emitting=false at t0.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _ms(t0: int) -> int:
	return roundi(float(Time.get_ticks_usec() - t0) / 1000.0)

# --------------------------------------------------------------- cpu trace

func _arm_trace() -> void:
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.25
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s" % [ph[0], _ms(t0), str(n.emitting)]))
	n.emitting = true
	while ph[0] < 40:
		await process_frame
	ev.append("t40@ph%d/em%s/nf=%d" % [ph[0], str(n.emitting), ev.size()])
	n.restart()
	ev.append("restart@ph%d/em%s" % [ph[0], str(n.emitting)])
	while ph[0] < 80:
		await process_frame
	ev.append("t80@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice trace " + " ".join(ev))
	n.queue_free()

func _arm_retrigger_trace() -> void:
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.25
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s" % [ph[0], _ms(t0), str(n.emitting)]))
	n.emitting = true
	while ph[0] < 40:
		await process_frame
	ev.append("t40@ph%d/em%s" % [ph[0], str(n.emitting)])
	n.emitting = true
	ev.append("set_true@ph%d/em%s" % [ph[0], str(n.emitting)])
	while ph[0] < 80:
		await process_frame
	ev.append("t80@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice retrigger_trace " + " ".join(ev))
	n.queue_free()

# --------------------------------------------------------------- request_particles_process

func _arm_request() -> void:
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.5
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var state := {"fin": -1, "n_fin": 0}
	n.finished.connect(func():
		state["n_fin"] += 1
		if state["fin"] < 0:
			state["fin"] = state["calls"])
	n.emitting = true
	await process_frame
	var calls := 0
	while calls < 40 and state["fin"] < 0:
		n.request_particles_process(0.1)
		state["calls"] = calls
		calls += 1
		await process_frame
	print("PASS particles_lattice request step01 fin_call=%d n_fin=%d calls=%d em=%s ph_na=true" % [
		state["fin"], state["n_fin"], calls, str(n.emitting)])
	n.queue_free()

func _arm_request2() -> void:
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.5
	n.amount = 8
	n.explosiveness = 0.0
	root.add_child(n)
	var state := {"fin": -1, "n_fin": 0}
	n.finished.connect(func():
		state["n_fin"] += 1
		if state["fin"] < 0:
			state["fin"] = state["calls"])
	n.emitting = true
	await process_frame
	var calls := 0
	while calls < 60 and state["fin"] < 0:
		n.request_particles_process(0.1)
		state["calls"] = calls
		calls += 1
		await process_frame
	print("PASS particles_lattice request2 e0_step01 fin_call=%d n_fin=%d calls=%d" % [
		state["fin"], state["n_fin"], calls])
	n.queue_free()

# --------------------------------------------------------------- pause levers

func _arm_vis() -> void:
	# hidden from the start, shown at tick 60; one-shot lifetime 0.25.
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.25
	n.amount = 8
	n.explosiveness = 1.0
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
	while ph[0] < 120 and ev.size() == 0:
		await process_frame
	ev.append("end@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice vis " + " ".join(ev))
	n.queue_free()

func _arm_vis_mid() -> void:
	# visible start, hidden at tick 10, shown at tick 40; one-shot lifetime 0.25.
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.25
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s" % [ph[0], _ms(t0), str(n.emitting)]))
	n.emitting = true
	while ph[0] < 10:
		await process_frame
	n.visible = false
	ev.append("hide@ph%d/em%s" % [ph[0], str(n.emitting)])
	while ph[0] < 40:
		await process_frame
	ev.append("show@ph%d/em%s" % [ph[0], str(n.emitting)])
	n.visible = true
	while ph[0] < 120 and ev.size() < 3:
		await process_frame
	ev.append("end@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice vis_mid " + " ".join(ev))
	n.queue_free()

func _arm_pause() -> void:
	# one-shot lifetime 0.25, PROCESS_MODE_DISABLED at tick 10, re-enabled at tick 40.
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.25
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d" % [ph[0], _ms(t0)]))
	n.emitting = true
	while ph[0] < 10:
		await process_frame
	n.process_mode = Node.PROCESS_MODE_DISABLED
	ev.append("dis@ph%d" % ph[0])
	while ph[0] < 40:
		await process_frame
	n.process_mode = Node.PROCESS_MODE_INHERIT
	ev.append("en@ph%d" % ph[0])
	while ph[0] < 120 and ev.size() < 3:
		await process_frame
	ev.append("end@ph%d" % ph[0])
	print("PASS particles_lattice pause " + " ".join(ev))
	n.queue_free()

func _arm_stop0() -> void:
	# emitting set false before the first process frame; one_shot.
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.25
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var state := {"fin_ph": -1, "n_fin": 0}
	var ph := [0]
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func():
		state["n_fin"] += 1
		state["fin_ph"] = ph[0])
	n.emitting = false
	var p := 0
	while ph[0] < 60 and state["fin_ph"] < 0:
		await process_frame
		p += 1
	print("PASS particles_lattice stop0 fin_ph=%d n_fin=%d em=%s p=%d" % [
		state["fin_ph"], state["n_fin"], str(n.emitting), p])
	n.queue_free()

# --------------------------------------------------------------- gpu headless traces

func _arm_gpu_trace() -> void:
	var out: Array[String] = []
	for name in ["os", "cont"]:
		var n := GPUParticles2D.new()
		n.process_material = ParticleProcessMaterial.new()
		n.lifetime = 0.25
		n.amount = 8
		n.explosiveness = 1.0
		n.one_shot = (name == "os")
		root.add_child(n)
		var ph := [0]
		var fin := [0]
		var flip := [-1]
		var t0 := Time.get_ticks_usec()
		physics_frame.connect(func(): ph[0] += 1)
		n.finished.connect(func(): fin[0] += 1)
		n.emitting = true
		var em0 := n.emitting
		while ph[0] < 60:
			await process_frame
			if flip[0] < 0 and not n.emitting:
				flip[0] = ph[0]
		out.append("%s[em0=%s flip_ph=%d flip_ms=%d fin=%d em_end=%s is_emitting=%s]" % [
			name, str(em0), flip[0], _ms(t0), fin[0], str(n.emitting), str(n.is_emitting())])
		n.queue_free()
	# manual emit_particle on GPU headless
	var g := GPUParticles2D.new()
	g.process_material = ParticleProcessMaterial.new()
	g.one_shot = true
	g.lifetime = 0.25
	root.add_child(g)
	g.emit_particle(Transform2D.IDENTITY, Vector2(1, 0), Color.WHITE, Color.WHITE, 0)
	var fin2 := [0]
	g.finished.connect(func(): fin2[0] += 1)
	g.emitting = true
	var ph2 := [0]
	physics_frame.connect(func(): ph2[0] += 1)
	while ph2[0] < 40:
		await process_frame
	out.append("manual[fin=%d em_end=%s]" % [fin2[0], str(g.emitting)])
	g.queue_free()
	# request_particles_process on GPU
	var g2 := GPUParticles2D.new()
	g2.process_material = ParticleProcessMaterial.new()
	g2.one_shot = true
	g2.lifetime = 0.25
	root.add_child(g2)
	g2.emitting = true
	await process_frame
	var fin3 := [0]
	g2.finished.connect(func(): fin3[0] += 1)
	for i in range(6):
		g2.request_particles_process(0.1)
		await process_frame
	out.append("req[fin=%d em=%s]" % [fin3[0], str(g2.emitting)])
	g2.queue_free()
	print("PASS particles_lattice gpu_trace " + " ".join(out))

func _arm_cpu3d() -> void:
	# CPUParticles3D control: is CPU particle behaviour 2D-specific?
	var n := CPUParticles3D.new()
	n.one_shot = true
	n.lifetime = 0.25
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var ph := [0]
	var state := {"fin_ph": -1}
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): state["fin_ph"] = ph[0])
	n.emitting = true
	while ph[0] < 60 and state["fin_ph"] < 0:
		await process_frame
	print("PASS particles_lattice cpu3d fin_ph=%d em=%s" % [state["fin_ph"], str(n.emitting)])
	n.queue_free()

func _initialize() -> void:
	var arm := _arg("arm", "trace")
	match arm:
		"trace": await _arm_trace()
		"retrigger_trace": await _arm_retrigger_trace()
		"request": await _arm_request()
		"request2": await _arm_request2()
		"vis": await _arm_vis()
		"vis_mid": await _arm_vis_mid()
		"pause": await _arm_pause()
		"stop0": await _arm_stop0()
		"gpu_trace": await _arm_gpu_trace()
		"cpu3d": await _arm_cpu3d()
		_: print("PASS particles_lattice unknown arm=" + arm)
	quit(0)
