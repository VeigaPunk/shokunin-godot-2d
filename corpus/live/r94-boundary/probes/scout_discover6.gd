extends SceneTree
# r94-scout discovery-6 — amount-setter immediate-finish anatomy.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _ms(t0: int) -> int:
	return roundi(float(Time.get_ticks_usec() - t0) / 1000.0)

func _arm_amount_long() -> void:
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 1.0
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s/ise%s" % [ph[0], _ms(t0), str(n.emitting), str(n.is_emitting())]))
	n.emitting = true
	while ph[0] < 30:
		await process_frame
	n.amount = 32
	ev.append("set@ph%d/em%s" % [ph[0], str(n.emitting)])
	while ph[0] < 200:
		await process_frame
		if ph[0] % 15 == 0:
			ev.append("t%d/em%s" % [ph[0], str(n.emitting)])
	ev.append("end@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice amount_long " + " ".join(ev))
	n.queue_free()

func _arm_amount_cont() -> void:
	# continuous emitter: does the amount setter emit a spurious finished?
	var n := CPUParticles2D.new()
	n.one_shot = false
	n.lifetime = 0.5
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var state := {"n_fin": 0, "ph": 0, "t0": Time.get_ticks_usec()}
	physics_frame.connect(func(): state["ph"] += 1)
	n.finished.connect(func(): state["n_fin"] += 1)
	n.emitting = true
	while state["ph"] < 30:
		await process_frame
	n.amount = 32
	var set_ph: int = state["ph"]
	while state["ph"] < 90:
		await process_frame
	print("PASS particles_lattice amount_cont set_ph=%d n_fin=%d em=%s" % [set_ph, state["n_fin"], str(n.emitting)])
	n.queue_free()

func _arm_amount_pre_start() -> void:
	# amount set before the emitter ever runs: no spurious finished.
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.5
	n.amount = 8
	n.explosiveness = 1.0
	root.add_child(n)
	var state := {"n_fin": 0, "ph": 0}
	physics_frame.connect(func(): state["ph"] += 1)
	n.finished.connect(func(): state["n_fin"] += 1)
	n.amount = 32
	var p := 0
	while state["ph"] < 40 and state["n_fin"] == 0:
		await process_frame
		p += 1
	print("PASS particles_lattice amount_pre_start n_fin=%d ph=%d em=%s" % [state["n_fin"], state["ph"], str(n.emitting)])
	n.queue_free()

func _initialize() -> void:
	var arm := _arg("arm", "amount_long")
	match arm:
		"amount_long": await _arm_amount_long()
		"amount_cont": await _arm_amount_cont()
		"amount_pre_start": await _arm_amount_pre_start()
		_: print("PASS particles_lattice unknown arm=" + arm)
	quit(0)
