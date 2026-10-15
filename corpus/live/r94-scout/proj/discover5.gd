extends SceneTree
# r94-scout discovery-5 — which setters end a one-shot cycle?  amount vs
# randomness vs draw_order vs scale_amount; long trace.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _ms(t0: int) -> int:
	return roundi(float(Time.get_ticks_usec() - t0) / 1000.0)

func _trace_setter(arm: String, prop: String, value) -> void:
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
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d/em%s" % [ph[0], _ms(t0), str(n.emitting)]))
	n.emitting = true
	while ph[0] < 30:
		await process_frame
	n.set(prop, value)
	ev.append("set@ph%d/em%s" % [ph[0], str(n.emitting)])
	var marks := 0
	while ph[0] < 200 and ev.size() < 4:
		await process_frame
		if ph[0] % 20 == 0 and ph[0] > 30 and marks < 3:
			marks += 1
			ev.append("t%d/em%s" % [ph[0], str(n.emitting)])
	ev.append("end@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice setter_%s %s" % [arm, " ".join(ev)])
	n.queue_free()

func _initialize() -> void:
	var arm := _arg("arm", "amount")
	match arm:
		"amount": await _trace_setter("amount", "amount", 32)
		"randomness": await _trace_setter("randomness", "randomness", 0.5)
		"draw_order": await _trace_setter("draw_order", "draw_order", 1)
		"scale": await _trace_setter("scale", "scale_amount_min", 3.0)
		"emitting_true": await _trace_setter("emitting_true", "emitting", true)
		_: print("PASS particles_lattice unknown arm=" + arm)
	quit(0)
