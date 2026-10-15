extends SceneTree
# r99-scout DISCOVERY-7 — looping position readback characterization + 2D pan knee.
# Launch: godot --headless --path proj --script res://discover7.gd -- --arm=<arm>

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _wav(seconds: float, rate: int, loop_mode: int, lb: int, le: int) -> AudioStreamWAV:
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = rate
	s.stereo = false
	var n := int(seconds * float(rate))
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in range(n):
		var sample := int(sin(TAU * 440.0 * float(i) / float(rate)) * 8191.0)
		data.encode_s16(i * 2, sample)
	s.data = data
	s.loop_mode = loop_mode
	s.loop_begin = lb
	s.loop_end = le
	return s

func _drain(n: int) -> void:
	for i in range(n):
		await process_frame

func _initialize() -> void:
	var arm := _arg("arm", "loop_trace")
	var out := "PASS r99_disc7 %s " % arm
	match arm:
		"loop_trace": out += await _arm_loop_trace()
		"loop_short": out += await _arm_loop_short()
		"pan_knee": out += await _arm_pan_knee()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _arm_loop_trace() -> String:
	var stream := _wav(1.0, 44100, AudioStreamWAV.LOOP_FORWARD, 0, 44100)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var lines: Array[String] = []
	var prev := -1.0
	var changes := 0
	var frames := 0
	while Time.get_ticks_usec() - t0 < 1500000 and frames < 2000:
		await process_frame
		frames += 1
		var pos := player.get_playback_position()
		if absf(pos - prev) > 0.000001:
			changes += 1
			if changes <= 40:
				lines.append("f=%d us=%d pos=%.9f" % [frames, Time.get_ticks_usec() - t0, pos])
			prev = pos
	lines.append("changes=%d frames=%d playing=%s pos_end=%.9f loop=%d..%d" % [
		changes, frames, str(player.is_playing()), player.get_playback_position(), stream.loop_begin, stream.loop_end])
	player.stop()
	player.stream = null
	player.free()
	await _drain(20)
	return " | ".join(lines)

func _arm_loop_short() -> String:
	var stream := _wav(1.0, 44100, AudioStreamWAV.LOOP_FORWARD, 0, 8820)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var lines: Array[String] = []
	var prev := -1.0
	var changes := 0
	var frames := 0
	while Time.get_ticks_usec() - t0 < 1200000 and frames < 1600:
		await process_frame
		frames += 1
		var pos := player.get_playback_position()
		if absf(pos - prev) > 0.000001:
			changes += 1
			if changes <= 30:
				lines.append("f=%d us=%d pos=%.9f" % [frames, Time.get_ticks_usec() - t0, pos])
			prev = pos
	lines.append("changes=%d frames=%d playing=%s pos_end=%.9f" % [
		changes, frames, str(player.is_playing()), player.get_playback_position()])
	player.stop()
	player.stream = null
	player.free()
	await _drain(20)
	return " | ".join(lines)

func _arm_pan_knee() -> String:
	var stream := _wav(6.0, 44100, AudioStreamWAV.LOOP_DISABLED, 0, 0)
	var listener := AudioListener2D.new()
	listener.position = Vector2(0, 0)
	root.add_child(listener)
	listener.make_current()
	var p := AudioStreamPlayer2D.new()
	p.stream = stream
	root.add_child(p)
	await process_frame
	p.position = Vector2(0, 0)
	p.play()
	var lines: Array[String] = []
	for x in [0, 100, 200, 300, 400, 600, 800, 1000]:
		p.position = Vector2(x, 0)
		var t0 := Time.get_ticks_usec()
		while Time.get_ticks_usec() - t0 < 400000:
			await process_frame
		var l := AudioServer.get_bus_peak_volume_left_db(0, 0)
		var r := AudioServer.get_bus_peak_volume_right_db(0, 0)
		lines.append("x%d l=%.2f r=%.2f diff=%.2f" % [x, l, r, l - r])
	p.stop()
	p.stream = null
	p.free()
	listener.free()
	await _drain(20)
	return " | ".join(lines)
