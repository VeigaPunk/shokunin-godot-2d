extends SceneTree
# r99-scout DISCOVERY probe — in-engine audio surface under --headless (Dummy driver).
# Launch: godot --headless --path proj --script res://discover.gd -- --arm=<arm>
# Prints one `PASS r99_disc <arm> ...` line per arm, then quit(0).

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

func _wav(seconds: float, rate: int = 44100, loop: bool = false) -> AudioStreamWAV:
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
	s.loop_mode = AudioStreamWAV.LOOP_FORWARD if loop else AudioStreamWAV.LOOP_DISABLED
	return s

func _initialize() -> void:
	var arm := _arg("arm", "census")
	var out := "PASS r99_disc %s " % arm
	match arm:
		"census": out += _arm_census()
		"advance": out += await _arm_advance()
		"finish": out += await _arm_finish()
		"gen": out += await _arm_gen()
		"poly": out += await _arm_poly()
		"bus": out += await _arm_bus()
		"autoplay": out += await _arm_autoplay()
		"p2d": out += await _arm_p2d()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _arm_census() -> String:
	var parts: Array[String] = []
	parts.append("driver=%s" % AudioServer.get_driver_name())
	parts.append("mix_rate=%d" % AudioServer.get_mix_rate())
	parts.append("speaker_mode=%d" % AudioServer.get_speaker_mode())
	parts.append("output_latency=%.7f" % AudioServer.get_output_latency())
	parts.append("bus_count=%d" % AudioServer.bus_count)
	var names: Array[String] = []
	for i in range(AudioServer.bus_count):
		names.append(AudioServer.get_bus_name(i))
	parts.append("bus_names=%s" % str(names))
	parts.append("bus0_vol=%.4f bus0_mute=%s bus0_solo=%s bus0_send=%s" % [
		AudioServer.get_bus_volume_db(0), _p(AudioServer.is_bus_mute(0)),
		_p(AudioServer.is_bus_solo(0)), AudioServer.get_bus_send(0)])
	parts.append("bus0_effects=%d" % AudioServer.get_bus_effect_count(0))
	parts.append("bus0_peak_l=%.4f bus0_peak_r=%.4f" % [
		AudioServer.get_bus_peak_volume_left_db(0, 0), AudioServer.get_bus_peak_volume_right_db(0, 0)])
	parts.append("out_devices=%s" % str(AudioServer.get_output_device_list()))
	parts.append("in_devices=%s" % str(AudioServer.get_input_device_list()))
	parts.append("playback_type=%d" % AudioServer.get_output_device_list().size())
	parts.append("time_since_mix=%.7f time_to_next=%.7f" % [
		AudioServer.get_time_since_last_mix(), AudioServer.get_time_to_next_mix()])
	var ps: Variant = ProjectSettings.get_setting("audio/driver/enable_input", "<unset>")
	parts.append("enable_input=%s" % _p(ps))
	parts.append("max_fps=%d" % Engine.max_fps)
	parts.append("tps=%d" % Engine.physics_ticks_per_second)
	return " ".join(parts)

func _arm_advance() -> String:
	var stream := _wav(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var lines: Array[String] = []
	lines.append("t0_us=%d" % t0)
	for f in range(24):
		await process_frame
		lines.append("f=%d us=%d pos=%.7f playing=%s" % [
			f + 1, Time.get_ticks_usec() - t0, player.get_playback_position(), _p(player.is_playing())])
	lines.append("pb_null=%s" % _p(player.get_stream_playback() == null))
	var mix_pos: float = player.get_playback_position()
	lines.append("mix_since=%.7f" % AudioServer.get_time_since_last_mix())
	lines.append("mix_next=%.7f" % AudioServer.get_time_to_next_mix())
	player.stop()
	player.free()
	return " | ".join(lines)

func _arm_finish() -> String:
	var stream := _wav(0.1)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	_fin_frame = -1
	_fin_us = 0
	player.finished.connect(_on_finished)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var lines: Array[String] = []
	var prev_playing := true
	for f in range(40):
		await process_frame
		PH = f + 1
		var playing := player.is_playing()
		if prev_playing and not playing:
			lines.append("stopped_at_f=%d us=%d pos=%.7f" % [f + 1, Time.get_ticks_usec() - t0, player.get_playback_position()])
		prev_playing = playing
		if f in [0, 1, 2, 5, 10, 19, 20, 21, 25, 26, 27, 30, 39]:
			lines.append("f=%d us=%d pos=%.7f playing=%s" % [f + 1, Time.get_ticks_usec() - t0, player.get_playback_position(), _p(playing)])
	lines.append("fin_frame=%d fin_us=%d pos_end=%.7f playing_end=%s" % [
		_fin_frame, _fin_us - t0, player.get_playback_position(), _p(player.is_playing())])
	player.stop()
	player.free()
	return " | ".join(lines)

func _arm_gen() -> String:
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = 44100.0
	gen.buffer_length = 0.1
	var player := AudioStreamPlayer.new()
	player.stream = gen
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	await process_frame
	var pb := player.get_stream_playback() as AudioStreamGeneratorPlayback
	var lines: Array[String] = []
	if pb == null:
		lines.append("pb=<null>")
	else:
		lines.append("avail0=%d can256=%s can4096=%s skips=%d" % [
			pb.get_frames_available(), _p(pb.can_push_buffer(256)), _p(pb.can_push_buffer(4096)), pb.get_skips()])
		var pushed := 0
		for i in range(4410):
			if pb.push_frame(Vector2(0.5, 0.5)):
				pushed += 1
			else:
				break
		lines.append("pushed=%d avail_after_push=%d" % [pushed, pb.get_frames_available()])
		for f in range(12):
			await process_frame
			lines.append("f=%d us=%d avail=%d skips=%d playing=%s" % [
				f + 1, Time.get_ticks_usec() - t0, pb.get_frames_available(), pb.get_skips(), _p(player.is_playing())])
		lines.append("can_push_after=%s" % _p(pb.can_push_buffer(256)))
		pb.clear_buffer()
		lines.append("avail_after_clear=%d" % pb.get_frames_available())
		lines.append("push_after_clear=%s" % _p(pb.push_frame(Vector2(0.25, 0.25))))
	player.stop()
	player.free()
	return " | ".join(lines)

func _arm_poly() -> String:
	var stream := _wav(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.max_polyphony = 3
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	for f in range(4):
		await process_frame
	var pos1 := player.get_playback_position()
	var pb1 := player.get_stream_playback()
	player.play()
	for f in range(4):
		await process_frame
	var pos2 := player.get_playback_position()
	var pb2 := player.get_stream_playback()
	player.play()
	for f in range(4):
		await process_frame
	var pos3 := player.get_playback_position()
	var pb3 := player.get_stream_playback()
	var lines: Array[String] = []
	lines.append("poly3 pos1=%.7f pos2=%.7f pos3=%.7f playing=%s" % [pos1, pos2, pos3, _p(player.is_playing())])
	lines.append("pb_same_12=%s pb_same_23=%s pb_null=%s" % [_p(pb1 == pb2), _p(pb2 == pb3), _p(pb3 == null)])
	player.stop()
	player.max_polyphony = 1
	await process_frame
	player.play()
	for f in range(6):
		await process_frame
	var mono_a := player.get_playback_position()
	player.play()
	for f in range(6):
		await process_frame
	var mono_b := player.get_playback_position()
	lines.append("mono1 pos_before_replay=%.7f pos_after_replay=%.7f playing=%s" % [mono_a, mono_b, _p(player.is_playing())])
	lines.append("us=%d" % (Time.get_ticks_usec() - t0))
	player.stop()
	player.free()
	return " | ".join(lines)

func _arm_bus() -> String:
	var lines: Array[String] = []
	AudioServer.add_bus(1)
	var idx := AudioServer.bus_count - 1
	AudioServer.set_bus_name(idx, "r99_probe_bus")
	AudioServer.set_bus_volume_db(idx, -6.0)
	lines.append("added idx=%d name=%s vol=%.4f send=%s" % [
		idx, AudioServer.get_bus_name(idx), AudioServer.get_bus_volume_db(idx), AudioServer.get_bus_send(idx)])
	var eff := AudioEffectAmplify.new()
	eff.volume_db = -3.0
	AudioServer.add_bus_effect(idx, eff)
	lines.append("effects=%d eff0=%s enabled=%s amp_vol=%.4f" % [
		AudioServer.get_bus_effect_count(idx), AudioServer.get_bus_effect(idx, 0).get_class(),
		_p(AudioServer.is_bus_effect_enabled(idx, 0)), AudioServer.get_bus_effect(idx, 0).volume_db])
	var stream := _wav(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.bus = "r99_probe_bus"
	root.add_child(player)
	await process_frame
	player.play()
	var peaks: Array[String] = []
	for f in range(12):
		await process_frame
		peaks.append("%.4f/%.4f" % [
			AudioServer.get_bus_peak_volume_left_db(idx, 0), AudioServer.get_bus_peak_volume_right_db(idx, 0)])
	lines.append("bus_peaks=%s" % str(peaks))
	lines.append("player_pos=%.7f playing=%s bus_readback=%s" % [
		player.get_playback_position(), _p(player.is_playing()), player.bus])
	lines.append("master_peak_l=%.4f" % AudioServer.get_bus_peak_volume_left_db(0, 0))
	lines.append("eff_type_name=%s" % AudioServer.get_bus_effect(idx, 0).get_class())
	AudioServer.set_bus_mute(idx, true)
	lines.append("muted=%s vol_readback=%.4f" % [_p(AudioServer.is_bus_mute(idx)), AudioServer.get_bus_volume_db(idx)])
	AudioServer.set_bus_mute(idx, false)
	AudioServer.remove_bus_effect(idx, 0)
	lines.append("after_remove_effects=%d" % AudioServer.get_bus_effect_count(idx))
	player.stop()
	player.free()
	AudioServer.remove_bus(idx)
	lines.append("bus_count_end=%d" % AudioServer.bus_count)
	return " | ".join(lines)

func _arm_autoplay() -> String:
	var stream := _wav(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.autoplay = true
	var pre := player.is_playing()
	root.add_child(player)
	var at_add := player.is_playing()
	await process_frame
	var after1 := player.is_playing()
	var pos1 := player.get_playback_position()
	for f in range(4):
		await process_frame
	var pos2 := player.get_playback_position()
	player.stop()
	player.free()
	var player2 := AudioStreamPlayer.new()
	player2.stream = stream
	player2.autoplay = false
	root.add_child(player2)
	await process_frame
	var noauto := player2.is_playing()
	player2.play()
	await process_frame
	var manual := player2.is_playing()
	player2.stop()
	player2.free()
	return "pre=%s at_add=%s after1=%s pos1=%.7f pos2=%.7f noauto=%s manual=%s" % [
		_p(pre), _p(at_add), _p(after1), pos1, pos2, _p(noauto), _p(manual)]

func _arm_p2d() -> String:
	var stream := _wav(1.0)
	var p := AudioStreamPlayer2D.new()
	p.stream = stream
	p.position = Vector2(100, 0)
	root.add_child(p)
	await process_frame
	var lines: Array[String] = []
	lines.append("props attenuation=%.4f max_distance=%.4f panning=%.4f area_mask=%d bus=%s volume=%.4f pitch=%.4f" % [
		p.attenuation, p.max_distance, p.panning_strength, p.area_mask, p.bus, p.volume_db, p.pitch_scale])
	lines.append("playing_pre=%s pos_pre=%.7f" % [_p(p.is_playing()), p.get_playback_position()])
	var listener := AudioListener2D.new()
	root.add_child(listener)
	listener.make_current()
	var cur := listener.is_current()
	lines.append("listener_current=%s" % _p(cur))
	player_play(p)
	for f in range(8):
		await process_frame
	lines.append("pos_after=%.7f playing=%s" % [p.get_playback_position(), _p(p.is_playing())])
	p.stop()
	p.free()
	listener.free()
	return " | ".join(lines)

func player_play(p: AudioStreamPlayer2D) -> void:
	p.play()
