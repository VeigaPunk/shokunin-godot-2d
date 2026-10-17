extends SceneTree
# r99-scout PRIMARY probe — in-engine audio surface under --headless (Dummy driver).
# Battery launch shape:
#   godot --headless --path <proj> --script res://audio_lattice.gd -- --arm=<arm>
# Every arm prints exactly one `PASS r99_audio <arm> <stable prefix> | <tail>` line.
#
# Measured laws (fresh-process receipts under corpus/live/r99-scout/runs/):
#  - The Dummy driver runs a REAL mix clock: `AudioStreamPlayer.get_playback_position()`
#    advances at wall-clock rate in 128-frame quanta published in 4096-frame steps
#    (one step per ~92.8798 ms mix period); streams finish, `finished` fires,
#    bus peaks are live dB values, AudioStreamGenerator frames are consumed.
#  - r88's "headless-null audio" verdict is a stream-configuration confound:
#    `LOOP_FORWARD` with default loop points (loop_begin=loop_end=0) terminates after
#    one sample (playing=false, pos=0.0), and a finished/stopped player reads pos=0.0.
#  - AudioStreamPlayer2D: distance attenuation is linear `1 - d/max_distance`
#    (dB = 20*log10(1-d/max_distance)), hard cutoff to -200 dB past max_distance,
#    center pan = 0.5 per channel, lateral pan saturating at +/-0.5.
#  - AudioStreamGenerator buffer capacity = next_pow2(buffer_length*mix_rate) - 1
#    (4095 / 8191 / 16383 measured); `clear_buffer()` is refused while active.
#
# Probe discipline: all block-sensitive waits are WALL-TIME based (`_wait_ms`) with a
# frame cap, never frame counts (headless process frames run ~147 fps here and vary
# under load). Every arm frees its players and drains frames so no ObjectDB leak
# WARNING reaches stderr.

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

func _db(v: float) -> String:
	return "%.2f" % v

func _mk(seconds: float, kind: String = "sine", amp: int = 8191, rate: int = 44100,
		loop_mode: int = AudioStreamWAV.LOOP_DISABLED, loop_begin: int = 0, loop_end: int = 0) -> AudioStreamWAV:
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
		else:
			v = int(sin(TAU * 440.0 * float(i) / float(rate)) * float(amp))
		data.encode_s16(i * 2, v)
	s.data = data
	s.loop_mode = loop_mode
	s.loop_begin = loop_begin
	s.loop_end = loop_end
	return s

func _wait_ms(ms: int, cap: int = 4000) -> void:
	var t0 := Time.get_ticks_usec()
	var frames := 0
	while Time.get_ticks_usec() - t0 < ms * 1000 and frames < cap:
		await process_frame
		frames += 1

func _drain(n: int) -> void:
	for i in range(n):
		await process_frame

func _peak_l() -> float:
	return AudioServer.get_bus_peak_volume_left_db(0, 0)

func _peak_r() -> float:
	return AudioServer.get_bus_peak_volume_right_db(0, 0)

func _peak2() -> String:
	return "%s/%s" % [_db(_peak_l()), _db(_peak_r())]

func _is_q(pos: float, rate: float = 44100.0) -> bool:
	var frames := pos * rate
	return absf(frames - roundf(frames / 128.0) * 128.0) < 0.01

func _initialize() -> void:
	var arm := _arg("arm", "census")
	var out := "PASS r99_audio %s " % arm
	match arm:
		"census": out += _arm_census()
		"mixblock": out += await _arm_mixblock()
		"advance": out += await _arm_advance()
		"finish": out += await _arm_finish()
		"loop_degenerate": out += await _arm_loop_degenerate()
		"loop_pts": out += await _arm_loop_pts()
		"gen": out += await _arm_gen()
		"gen_peak": out += await _arm_gen_peak()
		"poly": out += await _arm_poly()
		"bus": out += await _arm_bus()
		"bus_peak": out += await _arm_bus_peak()
		"p2d": out += await _arm_p2d()
		"pan_law": out += await _arm_pan_law()
		"gen2d": out += await _arm_gen2d()
		"autoplay": out += await _arm_autoplay()
		"pause": out += await _arm_pause()
		"stoppos": out += await _arm_stoppos()
		"peak_calib": out += await _arm_peak_calib()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _arm_census() -> String:
	var names: Array[String] = []
	for i in range(AudioServer.bus_count):
		names.append(AudioServer.get_bus_name(i))
	var parts: Array[String] = []
	parts.append("driver=%s" % AudioServer.get_driver_name())
	parts.append("mix_rate=%d" % AudioServer.get_mix_rate())
	parts.append("speaker_mode=%d" % AudioServer.get_speaker_mode())
	parts.append("output_latency=%s" % _db(AudioServer.get_output_latency()))
	parts.append("bus_count=%d" % AudioServer.bus_count)
	parts.append("bus_names=%s" % str(names))
	parts.append("bus0_vol=%s" % _db(AudioServer.get_bus_volume_db(0)))
	parts.append("bus0_mute=%s" % _p(AudioServer.is_bus_mute(0)))
	parts.append("bus0_solo=%s" % _p(AudioServer.is_bus_solo(0)))
	parts.append("bus0_send_empty=%s" % _p(AudioServer.get_bus_send(0) == ""))
	parts.append("bus0_effects=%d" % AudioServer.get_bus_effect_count(0))
	parts.append("idle_peak=%s" % _peak2())
	parts.append("out_devices=%s" % str(AudioServer.get_output_device_list()))
	parts.append("in_devices=%s" % str(AudioServer.get_input_device_list()))
	var ps: Variant = ProjectSettings.get_setting("audio/driver/enable_input", "<unset>")
	parts.append("enable_input=%s" % _p(ps))
	parts.append("max_fps=%d" % Engine.max_fps)
	parts.append("tps=%d" % Engine.physics_ticks_per_second)
	return " ".join(parts)

func _arm_mixblock() -> String:
	var stream := _mk(3.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var first := 0.0
	var jumps: Array[float] = []
	var wall: Array[float] = []
	var prev := -1.0
	var last_jump_t := Time.get_ticks_usec()
	var frames := 0
	while Time.get_ticks_usec() - t0 < 700000 and frames < 900:
		await process_frame
		frames += 1
		var pos := player.get_playback_position()
		var now := Time.get_ticks_usec()
		if prev < 0.0:
			first = pos
		elif absf(pos - prev) > 0.000001:
			jumps.append(pos - prev)
			wall.append(float(now - last_jump_t) / 1000000.0)
			last_jump_t = now
		prev = pos
	var period := AudioServer.get_time_since_last_mix() + AudioServer.get_time_to_next_mix()
	var block := 4096.0 / 44100.0
	var jmax := 0.0
	var jmin := 999.0
	var all_q := true
	var block_jumps := 0
	for j in jumps:
		jmax = maxf(jmax, j)
		jmin = minf(jmin, j)
		var fr := j * 44100.0
		if absf(fr - roundf(fr / 128.0) * 128.0) > 2.0:
			all_q = false
		if absf(fr - 4096.0) <= 2.0:
			block_jumps += 1
	var wmax := 0.0
	for w in wall:
		wmax = maxf(wmax, w)
	player.stop()
	player.free()
	await _drain(30)
	var prefix := "q_frames=128 jump_frames=4096 jump6=%.6f first=%.9f first_is_q=%s all_jumps_q=%s block_jumps_ge6=%s period_is_block=%s" % [
		block, first, _p(_is_q(first)), _p(all_q), _p(block_jumps >= 6),
		_p(absf(period - block) < 0.00001)]
	var tail := "jumps=%d block_jumps=%d jmin=%.9f jmax=%.9f wall_max=%.4f frames=%d" % [
		jumps.size(), block_jumps, jmin, jmax, wmax, frames]
	return prefix + " | " + tail

func _arm_advance() -> String:
	var stream := _mk(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	var before := player.get_playback_position()
	await _wait_ms(300)
	var after := player.get_playback_position()
	var playing := player.is_playing()
	var pb := player.get_stream_playback()
	player.stop()
	player.free()
	await _drain(30)
	var prefix := "playing=%s advanced=%s pb_nonnull=%s pos_multiple_q=%s pos_after_gt_before=%s" % [
		_p(playing), _p(after > 0.0), _p(pb != null), _p(_is_q(after)), _p(after > before)]
	return prefix + " | before=%.7f after=%.7f" % [before, after]

func _arm_finish() -> String:
	var stream := _mk(0.3)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	_fin_frame = -1
	_fin_us = 0
	player.finished.connect(_on_finished)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var transition_f := -1
	var last_pos := 0.0
	var frames := 0
	while Time.get_ticks_usec() - t0 < 2000000 and frames < 3000:
		await process_frame
		frames += 1
		PH = frames
		if player.is_playing():
			last_pos = player.get_playback_position()
		elif transition_f < 0:
			transition_f = frames
		if transition_f > 0 and frames > transition_f + 30:
			break
	var playing_end := player.is_playing()
	var pos_end := player.get_playback_position()
	var fin_frame := _fin_frame
	var fin_us := _fin_us - t0
	player.stop()
	player.free()
	await _drain(30)
	var prefix := "stopped=%s playing_end=%s pos_end=%.7f finished_seen=%s fin_frame_ge_1=%s fin_same_frame=%s played_gt_02=%s" % [
		_p(transition_f > 0), _p(playing_end), pos_end, _p(fin_frame >= 1),
		_p(fin_frame >= 1), _p(fin_frame == transition_f), _p(last_pos > 0.2)]
	var tail := "transition_f=%d fin_frame=%d fin_us=%d last_pos=%.7f frames=%d" % [
		transition_f, fin_frame, fin_us, last_pos, frames]
	return prefix + " | " + tail

func _arm_loop_degenerate() -> String:
	var stream := _mk(0.1, "sine", 8191, 44100, AudioStreamWAV.LOOP_FORWARD, 0, 0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	var maxpos := 0.0
	var wraps := 0
	var prev := -1.0
	var frames := 0
	var t0 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t0 < 500000 and frames < 800:
		await process_frame
		frames += 1
		var pos := player.get_playback_position()
		if prev >= 0.0 and pos < prev - 0.01:
			wraps += 1
		if pos > maxpos:
			maxpos = pos
		prev = pos
	var playing_end := player.is_playing()
	var pos_end := player.get_playback_position()
	player.stop()
	player.free()
	await _drain(30)
	var prefix := "playing_end=%s pos_end=%.7f looped=%s maxpos_lt_001=%s" % [
		_p(playing_end), pos_end, _p(wraps >= 1), _p(maxpos < 0.001)]
	return prefix + " | maxpos=%.7f wraps=%d frames=%d" % [maxpos, wraps, frames]

func _arm_loop_pts() -> String:
	var stream := _mk(0.1, "sine", 8191, 44100, AudioStreamWAV.LOOP_FORWARD, 0, 4410)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	var maxpos := 0.0
	var wraps := 0
	var prev := -1.0
	var frames := 0
	var t0 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t0 < 700000 and frames < 900:
		await process_frame
		frames += 1
		var pos := player.get_playback_position()
		if prev >= 0.0 and pos < prev - 0.001:
			wraps += 1
		if pos > maxpos:
			maxpos = pos
		prev = pos
	var playing_end := player.is_playing()
	player.stop()
	player.free()
	await _drain(30)
	var prefix := "playing_end=%s looped=%s wraps_ge2=%s maxpos_le_loop=%s" % [
		_p(playing_end), _p(wraps >= 1), _p(wraps >= 2), _p(maxpos <= 0.11)]
	return prefix + " | wraps=%d maxpos=%.7f frames=%d" % [wraps, maxpos, frames]

func _arm_gen() -> String:
	var caps: Array[String] = []
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
		caps.append("%d" % pb.get_frames_available())
		player.stop()
		player.free()
		await _drain(20)
	var gen2 := AudioStreamGenerator.new()
	gen2.mix_rate = 44100.0
	gen2.buffer_length = 0.1
	var player2 := AudioStreamPlayer.new()
	player2.stream = gen2
	root.add_child(player2)
	await process_frame
	player2.play()
	await process_frame
	var pb2 := player2.get_stream_playback() as AudioStreamGeneratorPlayback
	var pushed := 0
	while pb2.push_frame(Vector2(0.5, 0.5)):
		pushed += 1
	var avail_full := pb2.get_frames_available()
	var can_full := pb2.can_push_buffer(1)
	pb2.clear_buffer()  # refused while active (expected ERROR)
	var avail_after_refused := pb2.get_frames_available()
	player2.stop()
	await _wait_ms(250)
	var avail_stopped := pb2.get_frames_available()
	pb2.clear_buffer()  # still refused after stop (expected ERROR)
	var avail_after_stop := pb2.get_frames_available()
	player2.free()
	await _drain(30)
	var gen3 := AudioStreamGenerator.new()
	gen3.mix_rate = 44100.0
	gen3.buffer_length = 0.1
	var player3 := AudioStreamPlayer.new()
	player3.stream = gen3
	root.add_child(player3)
	await process_frame
	player3.play()
	await process_frame
	var pb3 := player3.get_stream_playback() as AudioStreamGeneratorPlayback
	await _wait_ms(300)
	var skips_dry := pb3.get_skips()
	player3.stop()
	player3.free()
	await _drain(30)
	var prefix := "caps=%s pushed=%d avail_full=%d full_refused=%s clear_noop_active=%s clear_noop_stopped=%s skips_dry_gt0=%s" % [
		str(caps), pushed, avail_full, _p(not can_full),
		_p(avail_after_refused == avail_full), _p(avail_after_stop == avail_stopped),
		_p(skips_dry > 0)]
	var tail := "avail_after_refused=%d avail_stopped=%d avail_after_stop=%d skips_dry=%d" % [
		avail_after_refused, avail_stopped, avail_after_stop, skips_dry]
	return prefix + " | " + tail

func _arm_gen_peak() -> String:
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
	var pushed := 0
	while pb.push_frame(Vector2(0.9, 0.9)):
		pushed += 1
	await _wait_ms(150)
	var live := _peak_l()
	await _wait_ms(500)
	var dry := _peak_l()
	player.stop()
	player.free()
	await _drain(30)
	var prefix := "live_gt_neg10=%s dry_is_minus200=%s live_gt_dry=%s" % [
		_p(live > -10.0), _p(dry <= -199.99), _p(live > dry + 100.0)]
	return prefix + " | pushed=%d live=%s dry=%s" % [pushed, _db(live), _db(dry)]

func _arm_poly() -> String:
	var stream := _mk(3.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.max_polyphony = 3
	root.add_child(player)
	await process_frame
	player.play()
	await _wait_ms(300)
	var pb1 := player.get_stream_playback()
	var p1 := pb1.get_playback_position()
	player.play()
	await _wait_ms(300)
	var pb2 := player.get_stream_playback()
	var p2 := pb2.get_playback_position()
	var p1b := pb1.get_playback_position()
	player.play()
	await _wait_ms(300)
	var pb3 := player.get_stream_playback()
	var p3 := pb3.get_playback_position()
	var p2b := pb2.get_playback_position()
	var p1c := pb1.get_playback_position()
	var player_read := player.get_playback_position()
	var distinct := 0
	if pb1 != pb2:
		distinct += 1
	if pb2 != pb3:
		distinct += 1
	var newest_tracked := player_read < p2b - 0.05 and player_read >= p3 - 0.11 and player_read <= p3 + 0.11
	var prefix := "voices=3 distinct=%d newest_tracked=%s older_advanced=%s all_playing=%s playing=%s" % [
		distinct, _p(newest_tracked), _p(p1c > p2b and p2b > p3),
		_p(pb1.is_playing() and pb2.is_playing() and pb3.is_playing()), _p(player.is_playing())]
	var tail := "p1=%.7f p2=%.7f p3=%.7f p1b=%.7f p2b=%.7f p1c=%.7f player_read=%.7f" % [
		p1, p2, p3, p1b, p2b, p1c, player_read]
	player.stop()
	player.free()
	await _drain(30)
	return prefix + " | " + tail

func _arm_bus() -> String:
	AudioServer.add_bus(1)
	var idx := AudioServer.bus_count - 1
	AudioServer.set_bus_name(idx, "r99_probe_bus")
	AudioServer.set_bus_volume_db(idx, -6.0)
	var eff := AudioEffectAmplify.new()
	eff.volume_db = -3.0
	AudioServer.add_bus_effect(idx, eff)
	var name_read := AudioServer.get_bus_name(idx)
	var vol_read := AudioServer.get_bus_volume_db(idx)
	var send_empty := AudioServer.get_bus_send(idx) == ""
	var eff_class := AudioServer.get_bus_effect(idx, 0).get_class()
	var eff_read: float = AudioServer.get_bus_effect(idx, 0).volume_db
	var eff_enabled := AudioServer.is_bus_effect_enabled(idx, 0)
	var player := AudioStreamPlayer.new()
	player.stream = _mk(1.0)
	player.bus = "r99_probe_bus"
	root.add_child(player)
	await process_frame
	var resolved := AudioServer.get_bus_index(player.bus)
	var invalid_idx := AudioServer.get_bus_index("NoSuchBus")
	player.bus = "NoSuchBus"
	var invalid_readback := player.bus
	player.bus = "r99_probe_bus"
	var valid_readback := player.bus
	player.play()
	await _wait_ms(300)
	var advanced := player.get_playback_position() > 0.0
	player.stop()
	player.free()
	AudioServer.remove_bus_effect(idx, 0)
	var eff_after := AudioServer.get_bus_effect_count(idx)
	AudioServer.remove_bus(idx)
	await _drain(30)
	var prefix := "added_name=%s added_vol=%s send_empty=%s effects=1 eff_class=%s eff_vol=%s eff_enabled=%s resolved_idx=%d invalid_idx=%d invalid_readback=%s valid_readback=%s advanced=%s removed_effects=%d bus_count_end=%d" % [
		name_read, _db(vol_read), _p(send_empty), eff_class, _db(eff_read),
		_p(eff_enabled), resolved, invalid_idx, invalid_readback, valid_readback,
		_p(advanced), eff_after, AudioServer.bus_count]
	return prefix

func _arm_bus_peak() -> String:
	var player := AudioStreamPlayer.new()
	player.stream = _mk(1.0)
	root.add_child(player)
	await process_frame
	player.play()
	await _wait_ms(300)
	var live := _peak_l()
	var pos_live := player.get_playback_position()
	player.stop()
	await _wait_ms(300)
	var idle := _peak_l()
	player.free()
	await _drain(30)
	var prefix := "live_gt_neg20=%s idle_is_minus200=%s live_gt_idle=%s" % [
		_p(live > -20.0), _p(idle <= -199.99), _p(live > idle + 100.0)]
	var tail := "live=%s idle=%s pos_live=%.7f" % [_db(live), _db(idle), pos_live]
	return prefix + " | " + tail

func _arm_p2d() -> String:
	var stream := _mk(6.0)
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
	await _wait_ms(400)
	var center_l := _peak_l()
	var center_r := _peak_r()
	var pos_center := p.get_playback_position()
	var probe: Array[String] = []
	var x400 := 0.0
	var x800l := 0.0
	var x800r := 0.0
	var xm800l := 0.0
	var xm800r := 0.0
	var y1500 := 0.0
	var y2001 := 0.0
	var y2500 := 0.0
	for x in [-400, -800, 800]:
		p.position = Vector2(x, 0)
		await _wait_ms(400)
		var l := _peak_l()
		var r := _peak_r()
		if x == -400:
			x400 = l - r
		if x == -800:
			xm800l = l
			xm800r = r
		if x == 800:
			x800l = l
			x800r = r
		probe.append("x%d=%s/%s" % [x, _db(l), _db(r)])
	for y in [-1500, -2001, -2500]:
		p.position = Vector2(0, y)
		await _wait_ms(400)
		var l := _peak_l()
		var r := _peak_r()
		if y == -1500:
			y1500 = l
		if y == -2001:
			y2001 = l
		if y == -2500:
			y2500 = l
		probe.append("y%d=%s/%s" % [y, _db(l), _db(r)])
	p.position = Vector2(800, -1500)
	await _wait_ms(400)
	var diag_l := _peak_l()
	var diag_r := _peak_r()
	probe.append("diag800-1500=%s/%s" % [_db(diag_l), _db(diag_r)])
	var listener_current := listener.is_current()
	var props := "attenuation=%.2f max_distance=%.2f panning=%.2f area_mask=%d bus=%s volume=%.2f pitch=%.2f" % [
		p.attenuation, p.max_distance, p.panning_strength, p.area_mask, p.bus, p.volume_db, p.pitch_scale]
	var prefix := "%s listener_current=%s advanced=%s center_lr_equal=%s left_louder=%s right_louder=%s far_att_lt_center=%s cutoff_2001=%s cutoff_2500=%s diag_pan_saturated=%s" % [
		props, _p(listener_current), _p(pos_center > 0.0), _p(absf(center_l - center_r) < 0.05),
		_p(xm800l > xm800r + 3.0), _p(x800r > x800l + 3.0), _p(y1500 < center_l - 5.0),
		_p(y2001 <= -199.99), _p(y2500 <= -199.99), _p(absf(diag_l - diag_r) > 9.0)]
	var tail := "center=%s/%s x400_diff=%s x-800=%s/%s x800=%s/%s y-1500=%s y-2001=%s y-2500=%s diag=%s/%s probe=%s" % [
		_db(center_l), _db(center_r), _db(x400), _db(xm800l), _db(xm800r), _db(x800l), _db(x800r),
		_db(y1500), _db(y2001), _db(y2500), _db(diag_l), _db(diag_r), str(probe)]
	p.stop()
	p.free()
	listener.free()
	await _drain(30)
	return prefix + " | " + tail

func _arm_pan_law() -> String:
	var listener := AudioListener2D.new()
	listener.position = Vector2(0, 0)
	root.add_child(listener)
	listener.make_current()
	var diffs: Dictionary = {}
	for cfg in [[2000.0, 1.0], [4000.0, 1.0], [2000.0, 0.5]]:
		var p := AudioStreamPlayer2D.new()
		p.stream = _mk(6.0)
		p.max_distance = cfg[0]
		p.panning_strength = cfg[1]
		root.add_child(p)
		await process_frame
		p.position = Vector2(0, 0)
		p.play()
		for pt in [Vector2(0, 0), Vector2(32, 0), Vector2(64, 0), Vector2(200, 0), Vector2(32, -1500)]:
			p.position = pt
			await _wait_ms(300)
			diffs["%d_%d_%.0f_%.1f" % [int(pt.x), int(pt.y), cfg[0], cfg[1]]] = _peak_l() - _peak_r()
		p.stop()
		p.free()
		await _drain(20)
	listener.free()
	await _drain(20)
	var d32: float = diffs["32_0_2000_1.0"]
	var d64: float = diffs["64_0_2000_1.0"]
	var d200: float = diffs["200_0_2000_1.0"]
	var d64_4k: float = diffs["64_0_4000_1.0"]
	var d64_half: float = diffs["64_0_2000_0.5"]
	var d32_far: float = diffs["32_-1500_2000_1.0"]
	var d0: float = diffs["0_0_2000_1.0"]
	var prefix := "center_zero=%s x32_diff=%s x64_diff=%s x200_sat=%s maxd_independent=%s ps_half=%s x_only=%s" % [
		_p(absf(d0) < 0.01), _db(absf(d32)), _db(absf(d64)), _p(absf(d200 - d64) < 0.05),
		_p(absf(d64_4k - d64) < 0.05), _db(absf(d64_half)), _p(absf(d32_far - d32) < 0.05)]
	var tail := "d32=%.4f d64=%.4f d200=%.4f d64_4k=%.4f d64_half=%.4f d32_far=%.4f" % [
		d32, d64, d200, d64_4k, d64_half, d32_far]
	return prefix + " | " + tail

func _arm_gen2d() -> String:
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
	await _wait_ms(150)
	var live_l := _peak_l()
	var live_r := _peak_r()
	var pos_live := p.get_playback_position()
	p.stop()
	p.free()
	listener.free()
	await _drain(30)
	var prefix := "pushed=%d center_peak=%s/%s center_half_pan=%s advanced=%s" % [
		pushed, _db(live_l), _db(live_r),
		_p(absf(live_l + 6.94) < 0.05 and absf(live_r + 6.94) < 0.05), _p(pos_live > 0.0)]
	var tail := "live_l=%.4f live_r=%.4f pos=%.7f" % [live_l, live_r, pos_live]
	return prefix + " | " + tail

func _arm_autoplay() -> String:
	var stream := _mk(1.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.autoplay = true
	var pre := player.is_playing()
	root.add_child(player)
	var at_add := player.is_playing()
	await process_frame
	var after1 := player.is_playing()
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
	await _drain(30)
	return "pre=%s at_add=%s after1=%s noauto=%s manual=%s" % [
		_p(pre), _p(at_add), _p(after1), _p(noauto), _p(manual)]

func _arm_pause() -> String:
	var stream := _mk(3.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	await _wait_ms(300)
	var a := player.get_playback_position()
	player.stream_paused = true
	await _wait_ms(200)
	var b := player.get_playback_position()
	await _wait_ms(400)
	var c := player.get_playback_position()
	var playing_paused := player.is_playing()
	player.stream_paused = false
	await _wait_ms(300)
	var d := player.get_playback_position()
	player.stop()
	player.free()
	await _drain(30)
	var prefix := "playing_while_paused=%s frozen_400ms=%s resumed_advanced=%s pos_gt_frozen=%s" % [
		_p(playing_paused), _p(absf(c - b) < 0.0001), _p(d > c + 0.0001), _p(d > c)]
	return prefix + " | a=%.7f b=%.7f c=%.7f d=%.7f" % [a, b, c, d]

func _arm_stoppos() -> String:
	var stream := _mk(3.0)
	var player := AudioStreamPlayer.new()
	player.stream = stream
	root.add_child(player)
	await process_frame
	player.play()
	await _wait_ms(300)
	var a := player.get_playback_position()
	player.stop()
	var b := player.get_playback_position()
	var playing_b := player.is_playing()
	await process_frame
	var c := player.get_playback_position()
	player.free()
	await _drain(30)
	return "before_gt0=%s imm_zero=%s playing_after=%s after_frame_zero=%s" % [
		_p(a > 0.0), _p(b == 0.0), _p(playing_b), _p(c == 0.0)]

func _arm_peak_calib() -> String:
	var values: Array[String] = []
	var const8191 := 0.0
	var sine8191 := 0.0
	var sine4096 := 0.0
	var const16384 := 0.0
	for spec in [["const", 8191], ["sine", 8191], ["sine", 4096], ["const", 16384]]:
		var stream := _mk(1.2, spec[0], spec[1])
		var player := AudioStreamPlayer.new()
		player.stream = stream
		root.add_child(player)
		await process_frame
		player.play()
		await _wait_ms(250)
		var v := _peak_l()
		values.append("%s_%d=%s" % [spec[0], spec[1], _db(v)])
		if spec[0] == "const" and spec[1] == 8191:
			const8191 = v
		elif spec[0] == "sine" and spec[1] == 8191:
			sine8191 = v
		elif spec[0] == "sine" and spec[1] == 4096:
			sine4096 = v
		else:
			const16384 = v
		player.stop()
		player.free()
		await _drain(20)
	await _wait_ms(250)
	var idle := _peak_l()
	var prefix := "const8191_minus12=%s sine8191_matches_const=%s const16384_minus6=%s sine4096_minus18=%s idle_after_minus200=%s" % [
		_p(absf(const8191 + 12.04) < 0.05), _p(absf(sine8191 - const8191) < 0.05),
		_p(absf(const16384 + 6.02) < 0.05), _p(absf(sine4096 + 18.06) < 0.05),
		_p(idle <= -199.99)]
	return prefix + " | " + " ".join(values)
