extends SceneTree
# r99-scout DISCOVERY-4 — finished-signal timing, peak calibration, clear_buffer post-stop, pause.
# Launch: godot --headless --path proj --script res://discover4.gd -- --arm=<arm>

var PH := 0
var _fin_frame := -1
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

func _wav_level(seconds: float, level: int, rate: int = 44100) -> AudioStreamWAV:
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = rate
	s.stereo = false
	var n := int(seconds * float(rate))
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in range(n):
		data.encode_s16(i * 2, level)
	s.data = data
	return s

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
	var arm := _arg("arm", "finwait")
	var out := "PASS r99_disc4 %s " % arm
	match arm:
		"finwait": out += await _arm_finwait()
		"peakcal": out += await _arm_peakcal()
		"clearwait": out += await _arm_clearwait()
		"pause2": out += await _arm_pause2()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _arm_finwait() -> String:
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
	var transition_frame := -1
	var lines: Array[String] = []
	for f in range(140):
		await process_frame
		PH = f + 1
		if transition_frame < 0 and not player.is_playing():
			transition_frame = f + 1
		if f in [13, 27, 41, 55, 60, 70, 100, 139]:
			lines.append("f=%d us=%d pos=%.7f playing=%s fin=%d" % [
				f + 1, Time.get_ticks_usec() - t0, player.get_playback_position(),
				_p(player.is_playing()), _fin_frame])
	lines.append("transition_f=%d fin_frame=%d fin_us=%d pos_end=%.7f internal=%s" % [
		transition_frame, _fin_frame, _fin_us - t0, player.get_playback_position(),
		_p(player.is_processing_internal())])
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	return " | ".join(lines)

func _arm_peakcal() -> String:
	var lines: Array[String] = []
	for level in [32767, 16384, 8191, 4096]:
		var stream := _wav_level(1.5, level)
		var player := AudioStreamPlayer.new()
		player.stream = stream
		root.add_child(player)
		await process_frame
		player.play()
		var t0 := Time.get_ticks_usec()
		while Time.get_ticks_usec() - t0 < 260000:
			await process_frame
		lines.append("level=%d peak_l=%.4f peak_r=%.4f" % [
			level, AudioServer.get_bus_peak_volume_left_db(0, 0), AudioServer.get_bus_peak_volume_right_db(0, 0)])
		player.stop()
		player.stream = null
		player.free()
		await _drain(30)
	var t0 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t0 < 260000:
		await process_frame
	lines.append("idle_peak_l=%.4f" % AudioServer.get_bus_peak_volume_left_db(0, 0))
	return " | ".join(lines)

func _arm_clearwait() -> String:
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
	player.stop()
	var t0 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t0 < 260000:
		await process_frame
	pb.clear_buffer()
	var avail := pb.get_frames_available()
	var skips := pb.get_skips()
	player.stream = null
	player.free()
	await _drain(30)
	return "avail_after_stop_clear=%d skips=%d" % [avail, skips]

func _arm_pause2() -> String:
	var stream := _wav(3.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	var t0 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t0 < 200000:
		await process_frame
	var a := player.get_playback_position()
	player.stream_paused = true
	var t1 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t1 < 100000:
		await process_frame
	var b := player.get_playback_position()
	while Time.get_ticks_usec() - t1 < 400000:
		await process_frame
	var c := player.get_playback_position()
	var playing_paused := player.is_playing()
	player.stream_paused = false
	var t2 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t2 < 300000:
		await process_frame
	var d := player.get_playback_position()
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	return "a=%.7f b=%.7f c=%.7f d=%.7f playing_paused=%s moved_in_100ms=%s moved_in_400ms=%s resumed_advanced=%s" % [
		a, b, c, d, _p(playing_paused), _p(b > a + 0.0001), _p(c > b + 0.0001), _p(d > c + 0.0001)]
