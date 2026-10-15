extends SceneTree
# r99-scout DISCOVERY-3 probe — 2D attenuation peaks, poly voice readback, clear_buffer hold,
# finish/stop position semantics, mix-block ladder.
# Launch: godot --headless --path proj --script res://discover3.gd -- --arm=<arm>

var PH := 0
var _fin_frame := -1
var _fin_pos := -1.0
var _fin_us := 0

func _on_finished() -> void:
	_fin_frame = PH
	_fin_us = Time.get_ticks_usec()

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

func _drain(n: int) -> void:
	for i in range(n):
		await process_frame

func _initialize() -> void:
	var arm := _arg("arm", "p2d_peak")
	var out := "PASS r99_disc3 %s " % arm
	match arm:
		"p2d_peak": out += await _arm_p2d_peak()
		"poly3": out += await _arm_poly3()
		"clearhold": out += await _arm_clearhold()
		"finish2": out += await _arm_finish2()
		"stoppos": out += await _arm_stoppos()
		"block": out += await _arm_block()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _peak() -> String:
	return "%.4f/%.4f" % [AudioServer.get_bus_peak_volume_left_db(0, 0), AudioServer.get_bus_peak_volume_right_db(0, 0)]

func _wait_block() -> void:
	# ~1.5 mix blocks at 147 process fps (block = 4096 frames = 92.9 ms)
	for i in range(24):
		await process_frame

func _arm_p2d_peak() -> String:
	var stream := _wav(3.0)
	var listener := AudioListener2D.new()
	listener.position = Vector2(0, 0)
	root.add_child(listener)
	listener.make_current()
	var p := AudioStreamPlayer2D.new()
	p.stream = stream
	p.volume_db = 0.0
	root.add_child(p)
	await process_frame
	var lines: Array[String] = []
	p.position = Vector2(0, 0)
	p.play()
	await _wait_block()
	lines.append("at_origin peak=%s pos=%.7f playing=%s" % [_peak(), p.get_playback_position(), _p(p.is_playing())])
	p.position = Vector2(-800, 0)
	await _wait_block()
	lines.append("left800 peak=%s pos=%.7f" % [_peak(), p.get_playback_position()])
	p.position = Vector2(800, 0)
	await _wait_block()
	lines.append("right800 peak=%s pos=%.7f" % [_peak(), p.get_playback_position()])
	p.position = Vector2(0, -1500)
	await _wait_block()
	lines.append("far1500 peak=%s" % _peak())
	p.position = Vector2(0, -2500)
	await _wait_block()
	lines.append("far2500 peak=%s" % _peak())
	lines.append("max_distance=%.1f attenuation=%.2f panning=%.2f area_mask=%d" % [
		p.max_distance, p.attenuation, p.panning_strength, p.area_mask])
	p.stop()
	p.stream = null
	p.free()
	listener.free()
	await _drain(30)
	return " | ".join(lines)

func _arm_poly3() -> String:
	var stream := _wav(3.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.max_polyphony = 3
	root.add_child(player)
	await process_frame
	var lines: Array[String] = []
	player.play()
	await _wait_block()
	var pb1 := player.get_stream_playback()
	lines.append("v1 player=%.7f pb1=%.7f pb1_playing=%s" % [
		player.get_playback_position(), pb1.get_playback_position(), _p(pb1.is_playing())])
	player.play()
	await _wait_block()
	var pb2 := player.get_stream_playback()
	lines.append("v2 player=%.7f pb1=%.7f pb2=%.7f pb2_playing=%s" % [
		player.get_playback_position(), pb1.get_playback_position(), pb2.get_playback_position(), _p(pb2.is_playing())])
	player.play()
	await _wait_block()
	var pb3 := player.get_stream_playback()
	lines.append("v3 player=%.7f pb1=%.7f pb2=%.7f pb3=%.7f" % [
		player.get_playback_position(), pb1.get_playback_position(), pb2.get_playback_position(), pb3.get_playback_position()])
	lines.append("distinct=%d poly=%d playing=%s" % [
		int(pb1 != pb2) + int(pb2 != pb3), player.max_polyphony, _p(player.is_playing())])
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	return " | ".join(lines)

func _arm_clearhold() -> String:
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
	var avail_a := pb.get_frames_available()
	var err_active := false
	pb.clear_buffer()  # refused while active -> ERROR line
	var avail_b := pb.get_frames_available()
	player.stop()
	await process_frame
	pb.clear_buffer()
	var avail_c := pb.get_frames_available()
	player.stream = null
	player.free()
	await _drain(30)
	return "avail_play=%d after_refused_clear=%d after_stop_clear=%d err_active_refused=%s" % [
		avail_a, avail_b, avail_c, _p(err_active)]

func _arm_finish2() -> String:
	var stream := _wav(0.3)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	_fin_frame = -1
	_fin_us = 0
	player.finished.connect(_on_finished)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var prev_pos := 0.0
	var pos_at_stop := -1.0
	var frames := 0
	for f in range(60):
		await process_frame
		PH = f + 1
		frames += 1
		var pos := player.get_playback_position()
		if prev_pos > 0.05 and pos < 0.02 and pos_at_stop < 0.0:
			pos_at_stop = prev_pos
		prev_pos = pos
		if not player.is_playing():
			break
	var pos_after := player.get_playback_position()
	var playing_after := player.is_playing()
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	return "frames=%d playing_after=%s pos_after=%.7f fin_frame=%d fin_us=%d pos_at_stop=%.7f" % [
		frames, _p(playing_after), pos_after, _fin_frame, _fin_us - t0, pos_at_stop]

func _arm_stoppos() -> String:
	var stream := _wav(3.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	await _wait_block()
	var a := player.get_playback_position()
	var playing_a := player.is_playing()
	player.stop()
	var b := player.get_playback_position()
	var playing_b := player.is_playing()
	await process_frame
	var c := player.get_playback_position()
	player.stream = null
	player.free()
	await _drain(30)
	return "before_stop=%.7f playing_a=%s imm_after_stop=%.7f playing_b=%s after_frame=%.7f" % [
		a, _p(playing_a), b, _p(playing_b), c]

func _arm_block() -> String:
	var stream := _wav(3.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var lines: Array[String] = []
	var prev := -1.0
	var jump_start := -1
	for f in range(160):
		await process_frame
		var pos := player.get_playback_position()
		if absf(pos - prev) > 0.000001:
			if prev >= 0.0:
				lines.append("f=%d us=%d pos=%.9f jump=%.9f" % [f + 1, Time.get_ticks_usec() - t0, pos, pos - prev])
			else:
				jump_start = f + 1
				lines.append("f=%d us=%d pos=%.9f first" % [f + 1, Time.get_ticks_usec() - t0, pos])
		prev = pos
	lines.append("jumps=%d first_jump_f=%d" % [lines.size(), jump_start])
	lines.append("since_mix=%.7f to_next=%.7f period=%.7f" % [
		AudioServer.get_time_since_last_mix(), AudioServer.get_time_to_next_mix(),
		AudioServer.get_time_since_last_mix() + AudioServer.get_time_to_next_mix()])
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	return " | ".join(lines)
