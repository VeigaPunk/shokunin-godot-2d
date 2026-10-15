extends SceneTree
# r99-scout DISCOVERY-6 — AudioStreamPlayer2D pan/attenuation lattice with lag-safe waits.
# Launch: godot --headless --path proj --script res://discover6.gd -- --arm=<arm>

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _p(v) -> String:
	if v is float:
		return "%.7f" % v
	if v is bool:
		return "true" if v else "false"
	if v == null:
		return "<null>"
	return str(v)

func _wav(seconds: float, rate: int = 44100) -> AudioStreamWAV:
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
	return s

func _wait_ms(ms: int) -> void:
	var t0 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t0 < ms * 1000:
		await process_frame

func _drain(n: int) -> void:
	for i in range(n):
		await process_frame

func _initialize() -> void:
	var arm := _arg("arm", "pan")
	var out := "PASS r99_disc6 %s " % arm
	match arm:
		"pan": out += await _arm_pan()
		"p2dgen": out += await _arm_p2dgen()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _peak() -> String:
	return "%.4f/%.4f" % [AudioServer.get_bus_peak_volume_left_db(0, 0), AudioServer.get_bus_peak_volume_right_db(0, 0)]

func _arm_pan() -> String:
	var stream := _wav(6.0)
	var listener := AudioListener2D.new()
	listener.position = Vector2(0, 0)
	root.add_child(listener)
	listener.make_current()
	var p := AudioStreamPlayer2D.new()
	p.stream = stream
	root.add_child(p)
	await process_frame
	var lines: Array[String] = []
	p.position = Vector2(0, 0)
	p.play()
	await _wait_ms(400)
	lines.append("x0=%s pos=%.7f" % [_peak(), p.get_playback_position()])
	for x in [-800, 800, -1500, 1500]:
		p.position = Vector2(x, 0)
		await _wait_ms(400)
		lines.append("x%d=%s pos=%.7f" % [x, _peak(), p.get_playback_position()])
	for y in [-1500, -2500, -1999, -2001]:
		p.position = Vector2(0, y)
		await _wait_ms(400)
		lines.append("y%d=%s" % [y, _peak()])
	p.stop()
	p.stream = null
	p.free()
	listener.free()
	await _drain(20)
	return " | ".join(lines)

func _arm_p2dgen() -> String:
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = 44100.0
	gen.buffer_length = 0.1
	var listener := AudioListener2D.new()
	listener.position = Vector2(0, 0)
	root.add_child(listener)
	listener.make_current()
	var p := AudioStreamPlayer2D.new()
	p.stream = gen
	root.add_child(p)
	await process_frame
	p.play()
	await process_frame
	var pb := p.get_stream_playback() as AudioStreamGeneratorPlayback
	var pushed := 0
	while pb.push_frame(Vector2(0.9, 0.9)):
		pushed += 1
	await _wait_ms(400)
	var lines: Array[String] = []
	lines.append("pushed=%d avail=%d skips=%d peak=%s" % [pushed, pb.get_frames_available(), pb.get_skips(), _peak()])
	p.stop()
	p.stream = null
	p.free()
	listener.free()
	await _drain(20)
	return " | ".join(lines)
