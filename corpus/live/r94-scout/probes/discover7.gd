extends SceneTree
# r94-scout discovery-7 — emitting=false on a one-shot, one_shot flag flipped
# mid-cycle, hidden parent, Engine.time_scale as a particle clock lever.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _ms(t0: int) -> int:
	return roundi(float(Time.get_ticks_usec() - t0) / 1000.0)

func _arm_os_stop() -> void:
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
	while ph[0] < 10:
		await process_frame
	n.emitting = false
	ev.append("off@ph%d" % ph[0])
	while ph[0] < 120 and ev.size() < 2:
		await process_frame
	ev.append("end@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice os_stop " + " ".join(ev))
	n.queue_free()

func _arm_os_flag_off() -> void:
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
	n.one_shot = false
	ev.append("osoff@ph%d" % ph[0])
	while ph[0] < 90 and ev.size() < 2:
		await process_frame
	ev.append("end@ph%d/em%s" % [ph[0], str(n.emitting)])
	print("PASS particles_lattice os_flag_off " + " ".join(ev))
	n.queue_free()

func _arm_hidden_parent() -> void:
	var parent := Node2D.new()
	root.add_child(parent)
	var n := CPUParticles2D.new()
	n.one_shot = true
	n.lifetime = 0.25
	n.amount = 8
	n.explosiveness = 1.0
	parent.add_child(n)
	var ev: Array[String] = []
	var ph := [0]
	var t0 := Time.get_ticks_usec()
	physics_frame.connect(func(): ph[0] += 1)
	n.finished.connect(func(): ev.append("fin@ph%d/ms%d" % [ph[0], _ms(t0)]))
	n.emitting = true
	while ph[0] < 10:
		await process_frame
	parent.visible = false
	ev.append("hide@ph%d" % ph[0])
	while ph[0] < 40:
		await process_frame
	parent.visible = true
	ev.append("show@ph%d" % ph[0])
	while ph[0] < 90 and ev.size() < 3:
		await process_frame
	ev.append("end@ph%d" % ph[0])
	print("PASS particles_lattice hidden_parent " + " ".join(ev))
	parent.queue_free()

func _arm_time_scale() -> void:
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
	Engine.time_scale = 0.0
	ev.append("ts0@ph%d" % ph[0])
	while ph[0] < 40:
		await process_frame
	Engine.time_scale = 1.0
	ev.append("ts1@ph%d" % ph[0])
	while ph[0] < 120 and ev.size() < 3:
		await process_frame
	ev.append("end@ph%d" % ph[0])
	print("PASS particles_lattice time_scale " + " ".join(ev))
	n.queue_free()

func _initialize() -> void:
	var arm := _arg("arm", "os_stop")
	match arm:
		"os_stop": await _arm_os_stop()
		"os_flag_off": await _arm_os_flag_off()
		"hidden_parent": await _arm_hidden_parent()
		"time_scale": await _arm_time_scale()
		_: print("PASS particles_lattice unknown arm=" + arm)
	quit(0)
