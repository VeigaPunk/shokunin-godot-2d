extends SceneTree
# r94-scout discovery-4 — precise traces: amount-change mid-flight, GPU emitting
# flip per tick, request_particles_process arg semantics.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _ms(t0: int) -> int:
	return roundi(float(Time.get_ticks_usec() - t0) / 1000.0)

func _arm_amount_trace() -> void:
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.5
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
	n.amount = 32
	ev.append("amt32@ph%d/em%s" % [ph[0], str(n.emitting)])
	while ph[0] < 70:
		await process_frame
		if ph[0] % 10 == 0 and ev.size() < 4:
			ev.append("t%d/em%s" % [ph[0], str(n.emitting)])
	ev.append("end@ph%d/em%s/nfin=%d" % [ph[0], str(n.emitting), ev.size()])
	print("PASS particles_lattice amount_trace " + " ".join(ev))
	n.queue_free()

func _arm_amount_same() -> void:
	# control: set amount to the SAME value mid-flight.
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.5
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
	n.amount = 8
	ev.append("same8@ph%d" % ph[0])
	while ph[0] < 50 and ev.size() < 2:
		await process_frame
	ev.append("end@ph%d" % ph[0])
	print("PASS particles_lattice amount_same " + " ".join(ev))
	n.queue_free()

func _arm_amount_lower() -> void:
	# amount lowered mid-flight (8 -> 2)
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.5
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
	n.amount = 2
	ev.append("amt2@ph%d" % ph[0])
	while ph[0] < 50 and ev.size() < 2:
		await process_frame
	ev.append("end@ph%d" % ph[0])
	print("PASS particles_lattice amount_lower " + " ".join(ev))
	n.queue_free()

func _arm_gpu_flip() -> void:
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
		var t0 := Time.get_ticks_usec()
		physics_frame.connect(func(): ph[0] += 1)
		n.emitting = true
		var stamps: Array[String] = []
		while ph[0] < 5:
			await process_frame
			stamps.append("ph%d/ms%d/em%s/ise%s" % [ph[0], _ms(t0), str(n.emitting), str(n.is_emitting())])
		out.append("%s[%s]" % [name, "|".join(stamps)])
		n.queue_free()
	print("PASS particles_lattice gpu_flip " + " ".join(out))

func _arm_request_args() -> void:
	Engine.time_scale = 0.0
	var out: Array[String] = []
	for spec in [["a_0.1_0.0", 0.1, 0.0], ["b_0.1_0.1", 0.1, 0.1], ["c_0.05_0.05", 0.05, 0.05], ["d_0.1_0.05", 0.1, 0.05]]:
		var n := CPUParticles2D.new()
		n.one_shot = true
		n.lifetime = 0.5
		n.amount = 8
		n.explosiveness = 1.0
		root.add_child(n)
		var state := {"fin": -1, "n_fin": 0, "calls": 0}
		n.finished.connect(func():
			state["n_fin"] += 1
			if state["fin"] < 0:
				state["fin"] = state["calls"])
		n.emitting = true
		await process_frame
		var calls := 0
		while calls < 60 and state["fin"] < 0:
			n.request_particles_process(spec[1], spec[2])
			state["calls"] = calls
			calls += 1
			await process_frame
		await process_frame
		out.append("%s[fin_call=%d n_fin=%d em=%s]" % [spec[0], state["fin"], state["n_fin"], str(n.emitting)])
		n.queue_free()
	Engine.time_scale = 1.0
	print("PASS particles_lattice request_args " + " ".join(out))

func _arm_request_e0() -> void:
	# e=0 under request-only time, with residual arg + more calls.
	Engine.time_scale = 0.0
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.5
	n.amount = 8
	n.explosiveness = 0.0
	root.add_child(n)
	var state := {"fin": -1, "n_fin": 0, "calls": 0}
	n.finished.connect(func():
		state["n_fin"] += 1
		if state["fin"] < 0:
			state["fin"] = state["calls"])
	n.emitting = true
	await process_frame
	var calls := 0
	while calls < 300 and state["fin"] < 0:
		n.request_particles_process(0.1, 0.1)
		state["calls"] = calls
		calls += 1
		await process_frame
	await process_frame
	print("PASS particles_lattice request_e0 fin_call=%d n_fin=%d calls=%d em=%s" % [
		state["fin"], state["n_fin"], calls, str(n.emitting)])
	Engine.time_scale = 1.0
	n.queue_free()

func _initialize() -> void:
	var arm := _arg("arm", "amount_trace")
	match arm:
		"amount_trace": await _arm_amount_trace()
		"amount_same": await _arm_amount_same()
		"amount_lower": await _arm_amount_lower()
		"gpu_flip": await _arm_gpu_flip()
		"request_args": await _arm_request_args()
		"request_e0": await _arm_request_e0()
		_: print("PASS particles_lattice unknown arm=" + arm)
	quit(0)
