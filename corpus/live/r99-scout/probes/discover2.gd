extends SceneTree
# r99-scout DISCOVERY-2 probe — loop/pitch/pause/poly-restart/mixclock/generator-capacity/drain.
# Launch: godot --headless --path proj --script res://discover2.gd -- --arm=<arm> [--drain=N]

var PH := 0

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

func _wav(seconds: float, rate: int = 44100, loop: bool = false, loop_pts: bool = false) -> AudioStreamWAV:
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
	if loop:
		s.loop_mode = AudioStreamWAV.LOOP_FORWARD
		if loop_pts:
			s.loop_begin = 0
			s.loop_end = n
	return s

func _drain(n: int) -> void:
	for i in range(n):
		await process_frame

func _initialize() -> void:
	var arm := _arg("arm", "loop")
	var out := "PASS r99_disc2 %s " % arm
	match arm:
		"loop": out += await _arm_loop(false)
		"loop_pts": out += await _arm_loop(true)
		"pitch": out += await _arm_pitch()
		"pause": out += await _arm_pause()
		"playpos": out += await _arm_playpos()
		"mixclock": out += await _arm_mixclock()
		"gen2": out += await _arm_gen2()
		"poly2": out += await _arm_poly2()
		"drain": out += await _arm_drain()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _arm_loop(with_pts: bool) -> String:
	var stream := _wav(0.1, 44100, true, with_pts)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var lines: Array[String] = []
	var maxpos := 0.0
	var wrapped := 0
	var prev := 0.0
	for f in range(40):
		await process_frame
		var pos := player.get_playback_position()
		if pos < prev - 0.02:
			wrapped += 1
		if pos > maxpos:
			maxpos = pos
		prev = pos
		if f in [2, 4, 9, 19, 29, 39]:
			lines.append("f=%d us=%d pos=%.7f playing=%s" % [f + 1, Time.get_ticks_usec() - t0, pos, _p(player.is_playing())])
	lines.append("wraps=%d maxpos=%.7f playing_end=%s loop_begin=%d loop_end=%d" % [
		wrapped, maxpos, _p(player.is_playing()), stream.loop_begin, stream.loop_end])
	player.stop()
	player.stream = null
	player.free()
	await _drain(60)
	return " | ".join(lines)

func _arm_pitch() -> String:
	var lines: Array[String] = []
	for ps in [2.0, 0.5]:
		var stream := _wav(1.0)
		var player := AudioStreamPlayer.new()
		player.stream = stream
		player.pitch_scale = ps
		root.add_child(player)
		await process_frame
		var t0 := Time.get_ticks_usec()
		player.play()
		var p0 := 0.0
		for f in range(10):
			await process_frame
		p0 = player.get_playback_position()
		var t1 := Time.get_ticks_usec()
		for f in range(20):
			await process_frame
		var p1 := player.get_playback_position()
		var t2 := Time.get_ticks_usec()
		lines.append("pitch=%.1f pos@10=%.7f pos@30=%.7f dpos=%.7f dwall=%.7f ratio=%.4f" % [
			ps, p0, p1, p1 - p0, float(t2 - t1) / 1000000.0, (p1 - p0) / (float(t2 - t1) / 1000000.0)])
		player.stop()
		player.stream = null
		player.free()
		await _drain(30)
	return " | ".join(lines)

func _arm_pause() -> String:
	var stream := _wav(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	for f in range(10):
		await process_frame
	var a := player.get_playback_position()
	player.stream_paused = true
	for f in range(20):
		await process_frame
	var b := player.get_playback_position()
	var playing_paused := player.is_playing()
	player.stream_paused = false
	for f in range(10):
		await process_frame
	var c := player.get_playback_position()
	player.stop()
	player.stream = null
	player.free()
	await _drain(60)
	return "pos_before_pause=%.7f pos_after_pause=%.7f frozen=%s playing_while_paused=%s pos_resumed=%.7f resumed_advanced=%s" % [
		a, b, _p(absf(b - a) < 0.0001), _p(playing_paused), c, _p(c > b + 0.0001)]

func _arm_playpos() -> String:
	var stream := _wav(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	for f in range(10):
		await process_frame
	var before := player.get_playback_position()
	var pb_before := player.get_stream_playback()
	player.play()
	var imm := player.get_playback_position()
	var pb_imm := player.get_stream_playback()
	for f in range(10):
		await process_frame
	var after := player.get_playback_position()
	var pb_after := player.get_stream_playback()
	player.stop()
	player.stream = null
	player.free()
	await _drain(60)
	return "before=%.7f imm_after_play=%.7f after10=%.7f pb_same_before_imm=%s pb_same_imm_after=%s" % [
		before, imm, after, _p(pb_before == pb_imm), _p(pb_imm == pb_after)]

func _arm_mixclock() -> String:
	var lines: Array[String] = []
	var t0 := Time.get_ticks_usec()
	var f0 := Engine.get_process_frames()
	for i in range(120):
		await process_frame
	var t1 := Time.get_ticks_usec()
	var f1 := Engine.get_process_frames()
	lines.append("frames=%d wall=%.7f fps=%.3f" % [f1 - f0, float(t1 - t0) / 1000000.0, float(f1 - f0) / (float(t1 - t0) / 1000000.0)])
	lines.append("since_mix=%.7f to_next=%.7f mix_rate=%d" % [
		AudioServer.get_time_since_last_mix(), AudioServer.get_time_to_next_mix(), AudioServer.get_mix_rate()])
	var stream := _wav(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	var ta := Time.get_ticks_usec()
	var pa := player.get_playback_position()
	var samples: Array[String] = []
	for f in range(30):
		await process_frame
		samples.append("%.9f" % player.get_playback_position())
	var tb := Time.get_ticks_usec()
	var pb := player.get_playback_position()
	lines.append("pa=%.9f pb=%.9f dpos=%.9f dwall=%.9f" % [pa, pb, pb - pa, float(tb - ta) / 1000000.0])
	lines.append("samples=%s" % str(samples))
	player.stop()
	player.stream = null
	player.free()
	await _drain(60)
	return " | ".join(lines)

func _arm_gen2() -> String:
	var lines: Array[String] = []
	for bl in [0.05, 0.1, 0.25]:
		var gen := AudioStreamGenerator.new()
		gen.mix_rate = 44100.0
		gen.buffer_length = bl
		var player := AudioStreamPlayer.new()
		player.stream = gen
		root.add_child(player)
		await process_frame
		player.play()
		await process_frame
		var pb := player.get_stream_playback() as AudioStreamGeneratorPlayback
		lines.append("bl=%.2f avail0=%d" % [bl, pb.get_frames_available()])
		player.stop()
		player.stream = null
		player.free()
		await _drain(30)
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
	var buf := PackedVector2Array()
	for i in range(1000):
		buf.append(Vector2(0.3, 0.3))
	var pushed_buf := pb.push_buffer(buf)
	lines.append("push_buffer_1000=%s avail=%d" % [_p(pushed_buf), pb.get_frames_available()])
	player.stop()
	await process_frame
	var pb_still := player.get_stream_playback()
	lines.append("after_stop_pb_null=%s" % _p(pb_still == null))
	if pb_still != null:
		var err_before := "?"
		var avail_stop := (pb_still as AudioStreamGeneratorPlayback).get_frames_available()
		(pb_still as AudioStreamGeneratorPlayback).clear_buffer()
		lines.append("clear_after_stop avail_before=%d avail_after=%d err=%s" % [
			avail_stop, (pb_still as AudioStreamGeneratorPlayback).get_frames_available(), err_before])
	player.stream = null
	player.free()
	await _drain(60)
	return " | ".join(lines)

func _arm_poly2() -> String:
	var stream := _wav(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.max_polyphony = 3
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	for f in range(6):
		await process_frame
	var a := player.get_playback_position()
	var pba := player.get_stream_playback()
	player.play()
	for f in range(6):
		await process_frame
	var b := player.get_playback_position()
	var pbb := player.get_stream_playback()
	player.play()
	for f in range(6):
		await process_frame
	var c := player.get_playback_position()
	var pbc := player.get_stream_playback()
	var pb_pos := "n/a"
	if pbc != null and pbc.has_method("get_playback_position"):
		pb_pos = "%.7f" % pbc.get_playback_position()
	var lines: Array[String] = []
	lines.append("pos_a=%.7f pos_b=%.7f pos_c=%.7f pb_pos_c=%s us=%d" % [a, b, c, pb_pos, Time.get_ticks_usec() - t0])
	lines.append("pb_distinct=%d" % [int(pba != pbb) + int(pbb != pbc)])
	var pb_playing := "n/a"
	if pbc != null and pbc.has_method("is_playing"):
		pb_playing = _p(pbc.is_playing())
	lines.append("pb_is_playing=%s poly=%d playing=%s" % [pb_playing, player.max_polyphony, _p(player.is_playing())])
	player.stop()
	player.stream = null
	player.free()
	await _drain(60)
	return " | ".join(lines)

func _arm_drain() -> String:
	var n := int(_arg("drain", "0"))
	var stream := _wav(0.1)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	for f in range(10):
		await process_frame
	player.stop()
	player.stream = null
	player.free()
	await _drain(n)
	return "drained=%d frames=%d" % [n, Engine.get_process_frames()]
