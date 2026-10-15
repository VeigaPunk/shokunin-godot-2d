extends SceneTree
# r99-scout DISCOVERY-5 — sine-vs-constant peak scale, first-readback stability, skips, gen consumption.
# Launch: godot --headless --path proj --script res://discover5.gd -- --arm=<arm>

var _fin_frame := -1

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

func _mk(seconds: float, kind: String, amp: int, rate: int = 44100) -> AudioStreamWAV:
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = rate
	s.stereo = false
	var n := int(seconds * float(rate))
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in range(n):
		var v := 0
		if kind == "const":
			v = amp
		elif kind == "sine":
			v = int(sin(TAU * 440.0 * float(i) / float(rate)) * float(amp))
		elif kind == "square":
			v = amp if (i % 100) < 50 else -amp
		elif kind == "half":
			v = int(sin(TAU * 440.0 * float(i) / float(rate)) * float(amp)) / 2
		data.encode_s16(i * 2, v)
	s.data = data
	return s

func _drain(n: int) -> void:
	for i in range(n):
		await process_frame

func _initialize() -> void:
	var arm := _arg("arm", "firstread")
	var out := "PASS r99_disc5 %s " % arm
	match arm:
		"firstread": out += await _arm_firstread()
		"peakcal2": out += await _arm_peakcal2()
		"skips": out += await _arm_skips()
		"genconsume": out += await _arm_genconsume()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _arm_firstread() -> String:
	var stream := _mk(3.0, "sine", 8191)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var lines: Array[String] = []
	for f in range(6):
		await process_frame
		lines.append("f=%d us=%d pos=%.9f" % [f + 1, Time.get_ticks_usec() - t0, player.get_playback_position()])
	player.stop()
	player.stream = null
	player.free()
	await _drain(20)
	return " | ".join(lines)

func _arm_peakcal2() -> String:
	var lines: Array[String] = []
	for spec in [["const", 8191], ["sine", 32767], ["sine", 16384], ["sine", 8191], ["square", 8191], ["half", 8191]]:
		var stream := _mk(1.5, spec[0], spec[1])
		var player := AudioStreamPlayer.new()
		player.stream = stream
		root.add_child(player)
		await process_frame
		player.play()
		var t0 := Time.get_ticks_usec()
		while Time.get_ticks_usec() - t0 < 300000:
			await process_frame
		lines.append("%s_%d=%.4f" % [spec[0], spec[1], AudioServer.get_bus_peak_volume_left_db(0, 0)])
		player.stop()
		player.stream = null
		player.free()
		await _drain(20)
	return " | ".join(lines)

func _arm_skips() -> String:
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = 44100.0
	gen.buffer_length = 0.1
	var player := AudioStreamPlayer.new()
	player.stream = gen
	root.add_child(player)
	await process_frame
	player.play()
	await process_frame
	var pb := player.get_stream_playback() as AudioStreamGeneratorPlayback
	var lines: Array[String] = []
	var t0 := Time.get_ticks_usec()
	var last := 0
	for step in range(4):
		while Time.get_ticks_usec() - t0 < (step + 1) * 200000:
			await process_frame
		lines.append("t=%dms skips=%d avail=%d playing=%s" % [
			(step + 1) * 200, pb.get_skips(), pb.get_frames_available(), _p(player.is_playing())])
		last = pb.get_skips()
	player.stop()
	player.stream = null
	player.free()
	await _drain(20)
	return " | ".join(lines)

func _arm_genconsume() -> String:
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = 44100.0
	gen.buffer_length = 0.1
	var player := AudioStreamPlayer.new()
	player.stream = gen
	root.add_child(player)
	await process_frame
	player.play()
	await process_frame
	var pb := player.get_stream_playback() as AudioStreamGeneratorPlayback
	var lines: Array[String] = []
	lines.append("avail0=%d" % pb.get_frames_available())
	var pushed := 0
	while pb.push_frame(Vector2(0.5, 0.5)):
		pushed += 1
	lines.append("pushed=%d avail_after=%d full_push_refused=%s" % [pushed, pb.get_frames_available(), _p(not pb.can_push_buffer(1))])
	var t0 := Time.get_ticks_usec()
	for step in range(3):
		while Time.get_ticks_usec() - t0 < (step + 1) * 200000:
			await process_frame
		lines.append("t=%dms avail=%d skips=%d" % [(step + 1) * 200, pb.get_frames_available(), pb.get_skips()])
	player.stop()
	player.stream = null
	player.free()
	await _drain(20)
	return " | ".join(lines)
