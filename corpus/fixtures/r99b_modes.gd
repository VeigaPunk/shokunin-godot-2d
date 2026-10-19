extends SceneTree
# r99-boundary probe — startup-mode / phase / ordering mechanisms of the r99 audio lattice.
# Battery launch shape:
#   godot --headless [mode flags] --path proj --script res://r99b_modes.gd -- --arm=<arm>
# One `PASS r99b <arm> <keys>` line per arm. Wall-time waits only, never frame counts.
#
# Arms:
#  modeinfo   — what the startup mode actually changes (max_fps, measured fps/tps,
#               mix period, project settings, cmdline).
#  mixphase   — the position publish mechanism: first readback, jump histogram,
#               same-frame 3 ms double reads, time-since-last-mix at change instants.
#  startphase — is `first readback == 128 frames` a per-play or a process-startup fact?
#  peakphase  — when the bus peak turns live after play() and clears after stop()
#               (per-block update point, measured in wall ms and tslm).

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

func _mk(seconds: float, kind: String = "sine", amp: int = 8191, rate: int = 44100) -> AudioStreamWAV:
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

func _busy_us(us: int) -> void:
	var t0 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t0 < us:
		pass

func _is_q(pos: float, rate: float = 44100.0) -> bool:
	var frames := pos * rate
	return absf(frames - roundf(frames / 128.0) * 128.0) < 0.01

func _initialize() -> void:
	var arm := _arg("arm", "modeinfo")
	var out := "PASS r99b %s " % arm
	match arm:
		"modeinfo": out += await _arm_modeinfo()
		"mixphase": out += await _arm_mixphase()
		"startphase": out += await _arm_startphase()
		"peakphase": out += await _arm_peakphase()
		"mixfree": out += await _arm_mixfree()
		"finfree": out += await _arm_finfree()
		"advfree": out += await _arm_advfree()
		"splitcycle": out += await _arm_splitcycle()
		"firstlaw": out += await _arm_firstlaw()
		_: out += "unknown_arm"
	print(out)
	quit(0)

func _arm_modeinfo() -> String:
	var parts: Array[String] = []
	parts.append("driver=%s" % AudioServer.get_driver_name())
	parts.append("mix_rate=%d" % AudioServer.get_mix_rate())
	parts.append("latency=%s" % _db(AudioServer.get_output_latency()))
	parts.append("max_fps=%d" % Engine.max_fps)
	parts.append("tps=%d" % Engine.physics_ticks_per_second)
	parts.append("time_scale=%.3f" % Engine.time_scale)
	parts.append("reported_fps=%.1f" % Engine.get_frames_per_second())
	parts.append("mix_period=%.6f" % (AudioServer.get_time_since_last_mix() + AudioServer.get_time_to_next_mix()))
	parts.append("args=%s" % str(OS.get_cmdline_args()))
	for key in ["physics/2d/run_on_separate_thread", "physics/3d/run_on_separate_thread",
			"physics/common/physics_ticks_per_second", "physics/common/physics_interpolation",
			"audio/driver/output_latency", "audio/driver/mix_rate", "application/run/max_fps",
			"application/run/delta_smoothing"]:
		parts.append("ps[%s]=%s" % [key, _p(ProjectSettings.get_setting(key, "<unset>"))])
	var f0 := Engine.get_process_frames()
	var ph0 := Engine.get_physics_frames()
	var t0 := Time.get_ticks_usec()
	await _wait_ms(400)
	var wall := float(Time.get_ticks_usec() - t0) / 1000000.0
	var df := Engine.get_process_frames() - f0
	var dph := Engine.get_physics_frames() - ph0
	parts.append("win_frames=%d win_phys=%d win_wall=%.4f meas_fps=%.1f meas_tps=%.1f pf_per_ph=%.2f" % [
		df, dph, wall, float(df) / wall, float(dph) / wall,
		float(df) / maxf(1.0, float(dph))])
	return " ".join(parts)

func _arm_mixphase() -> String:
	var player := AudioStreamPlayer.new()
	player.stream = _mk(3.0)
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var first := -1.0
	var prev := -1.0
	var hist: Dictionary = {}
	var blocks := 0
	var sub := 0
	var other := 0
	var chg_tslm: Array[String] = []
	var chg_mod: Array[String] = []
	var trace: Array[String] = []
	var frames := 0
	while Time.get_ticks_usec() - t0 < 600000 and frames < 4000:
		await process_frame
		frames += 1
		var pos := player.get_playback_position()
		var fr := pos * 44100.0
		if first < 0.0:
			first = pos
		elif absf(pos - prev) > 1e-9:
			var d := fr - prev * 44100.0
			var di := int(roundf(d))
			hist[di] = hist.get(di, 0) + 1
			if absf(d - 4096.0) <= 2.0:
				blocks += 1
			elif absf(d - 128.0) <= 2.0:
				sub += 1
			else:
				other += 1
			if chg_tslm.size() < 8:
				chg_tslm.append("%.1f" % (AudioServer.get_time_since_last_mix() * 1000000.0))
				chg_mod.append("%d" % (int(roundf(fr)) % 4096))
		if frames <= 16:
			trace.append("%d:%d:%.0f" % [frames, int(roundf(fr)),
				AudioServer.get_time_since_last_mix() * 1000000.0])
		prev = pos
	var intra: Array[String] = []
	for k in range(5):
		var a := player.get_playback_position()
		_busy_us(3000)
		var b := player.get_playback_position()
		intra.append("%d" % int(roundf((b - a) * 44100.0)))
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	var hist_s: Array[String] = []
	var keys := hist.keys()
	keys.sort()
	for k in keys:
		hist_s.append("%d:%d" % [k, hist[k]])
	var prefix := "first=%.9f first_q=%s hist={%s} blocks=%d sub=%d other=%d intra=%s" % [
		first, _p(_is_q(first)), ",".join(hist_s), blocks, sub, other, str(intra)]
	var tail := "chg_tslm_us=%s chg_mod4096=%s trace=%s frames=%d" % [
		str(chg_tslm), str(chg_mod), str(trace), frames]
	return prefix + " | " + tail

func _arm_startphase() -> String:
	var stream := _mk(2.0)
	var imm: Array[String] = []
	var imm_q: Array[String] = []
	var one: Array[String] = []
	var one_q: Array[String] = []
	for k in range(5):
		var player := AudioStreamPlayer.new()
		player.stream = stream
		root.add_child(player)
		await process_frame
		player.play()
		var a := player.get_playback_position()
		imm.append("%.7f" % a)
		imm_q.append(_p(_is_q(a)))
		await process_frame
		var b := player.get_playback_position()
		one.append("%.7f" % b)
		one_q.append(_p(_is_q(b)))
		await _wait_ms(150)
		player.stop()
		player.stream = null
		player.free()
		await _drain(10)
	var imm_set: Dictionary = {}
	for v in imm:
		imm_set[v] = true
	var one_set: Dictionary = {}
	for v in one:
		one_set[v] = true
	var prefix := "imm=%s imm_q=%s imm_uniq=%d one=%s one_q=%s one_uniq=%d" % [
		str(imm), str(imm_q), imm_set.size(), str(one), str(one_q), one_set.size()]
	return prefix

func _arm_peakphase() -> String:
	var player := AudioStreamPlayer.new()
	player.stream = _mk(3.0, "const", 8191)
	root.add_child(player)
	await process_frame
	player.play()
	var onset_ms := -1
	var onset_tslm := -1.0
	var onset_frame := -1
	var peak := -200.0
	var t0 := Time.get_ticks_usec()
	var frames := 0
	while Time.get_ticks_usec() - t0 < 500000:
		await process_frame
		frames += 1
		peak = AudioServer.get_bus_peak_volume_left_db(0, 0)
		if peak > -100.0:
			onset_ms = int((Time.get_ticks_usec() - t0) / 1000)
			onset_tslm = AudioServer.get_time_since_last_mix()
			onset_frame = frames
			break
	player.stop()
	var t1 := Time.get_ticks_usec()
	var clear_ms := -1
	var clear_tslm := -1.0
	var clear_frame := -1
	var frames2 := 0
	while Time.get_ticks_usec() - t1 < 600000:
		await process_frame
		frames2 += 1
		peak = AudioServer.get_bus_peak_volume_left_db(0, 0)
		if peak <= -199.99:
			clear_ms = int((Time.get_ticks_usec() - t1) / 1000)
			clear_tslm = AudioServer.get_time_since_last_mix()
			clear_frame = frames2
			break
	player.stream = null
	player.free()
	await _drain(30)
	var prefix := "onset_ms=%d onset_tslm_us=%.0f onset_frame=%d clear_ms=%d clear_tslm_us=%.0f clear_frame=%d" % [
		onset_ms, onset_tslm * 1000000.0, onset_frame, clear_ms, clear_tslm * 1000000.0, clear_frame]
	return prefix

# ---------------------------------------------------------------------------
# Cap-free variants of the three frozen cells whose loop bound is `wall AND
# frames < cap`: under `--fixed-fps` the engine is unpaced (measured ~100k fps
# at ff30), so the cap — not the wall clock — binds. These arms bound by wall
# time ONLY, to separate the audio law from the frozen probe's frame budget.
# ---------------------------------------------------------------------------

func _arm_mixfree() -> String:
	var player := AudioStreamPlayer.new()
	player.stream = _mk(3.0)
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var first := -1.0
	var prev := -1.0
	var hist: Dictionary = {}
	var blocks := 0
	var sub := 0
	var other := 0
	var all_q := true
	var chg: Array[String] = []
	var frames := 0
	while true:
		await process_frame
		frames += 1
		var pos := player.get_playback_position()
		if first < 0.0:
			first = pos
		elif absf(pos - prev) > 1e-9:
			var d := (pos - prev) * 44100.0
			var di := int(roundf(d))
			hist[di] = hist.get(di, 0) + 1
			if absf(d - roundf(d / 128.0) * 128.0) > 2.0:
				all_q = false
			if absf(d - 4096.0) <= 2.0:
				blocks += 1
			elif absf(d - 128.0) <= 2.0:
				sub += 1
			else:
				other += 1
			if chg.size() < 12:
				chg.append("%d@%.0fus" % [di, AudioServer.get_time_since_last_mix() * 1000000.0])
		prev = pos
		if Time.get_ticks_usec() - t0 >= 700000:
			break
	var period := AudioServer.get_time_since_last_mix() + AudioServer.get_time_to_next_mix()
	var block := 4096.0 / 44100.0
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	var hist_s: Array[String] = []
	var keys := hist.keys()
	keys.sort()
	for k in keys:
		hist_s.append("%d:%d" % [k, hist[k]])
	var prefix := "first=%.9f first_q=%s blocks=%d blocks_ge6=%s sub=%d other=%d all_jumps_q=%s period_is_block=%s" % [
		first, _p(_is_q(first)), blocks, _p(blocks >= 6), sub, other, _p(all_q),
		_p(absf(period - block) < 0.00001)]
	var tail := "hist={%s} chg=%s frames=%d wall=%.4f" % [
		",".join(hist_s), str(chg), frames, float(Time.get_ticks_usec() - t0) / 1000000.0]
	return prefix + " | " + tail

func _arm_finfree() -> String:
	var player := AudioStreamPlayer.new()
	player.stream = _mk(0.3)
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
	while Time.get_ticks_usec() - t0 < 2000000:
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
	player.stream = null
	player.free()
	await _drain(30)
	var prefix := "stopped=%s playing_end=%s pos_end=%.7f finished_seen=%s fin_same_frame=%s played_gt_02=%s" % [
		_p(transition_f > 0), _p(playing_end), pos_end, _p(fin_frame >= 1),
		_p(fin_frame == transition_f), _p(last_pos > 0.2)]
	return prefix + " | transition_f=%d fin_frame=%d fin_us=%d last_pos=%.7f frames=%d" % [
		transition_f, fin_frame, fin_us, last_pos, frames]

func _arm_advfree() -> String:
	var player := AudioStreamPlayer.new()
	player.stream = _mk(1.0)
	root.add_child(player)
	await process_frame
	player.play()
	var before := player.get_playback_position()
	var t0 := Time.get_ticks_usec()
	var frames := 0
	while Time.get_ticks_usec() - t0 < 300000:
		await process_frame
		frames += 1
	var after := player.get_playback_position()
	var playing := player.is_playing()
	var pb := player.get_stream_playback()
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	var prefix := "playing=%s advanced=%s pb_nonnull=%s pos_multiple_q=%s pos_after_gt_before=%s" % [
		_p(playing), _p(after > 0.0), _p(pb != null), _p(_is_q(after)), _p(after > before)]
	return prefix + " | before=%.7f after=%.7f frames=%d" % [before, after, frames]


func _arm_splitcycle() -> String:
	# Hunt the r95-style cycle in the position publish: record every delta (in
	# frames) over ~1.5 s and the time-since-last-mix at each change. Under an
	# unpaced mode the readback is seen to split one block update into two
	# sub-publishes; this arm asks whether the split point cycles.
	var player := AudioStreamPlayer.new()
	player.stream = _mk(4.0)
	root.add_child(player)
	await process_frame
	var t0 := Time.get_ticks_usec()
	player.play()
	var first := -1.0
	var prev := -1.0
	var seq: Array[String] = []
	var frames := 0
	while true:
		await process_frame
		frames += 1
		var pos := player.get_playback_position()
		if first < 0.0:
			first = pos
		elif absf(pos - prev) > 1e-9:
			var d := int(roundf((pos - prev) * 44100.0))
			seq.append("%d@%dus" % [d, int(AudioServer.get_time_since_last_mix() * 1000000.0)])
		prev = pos
		if Time.get_ticks_usec() - t0 >= 1500000:
			break
	var changes := seq.size()
	var last := seq.slice(maxi(0, changes - 4), changes)
	player.stop()
	player.stream = null
	player.free()
	await _drain(30)
	return "first=%.9f first_q=%s changes=%d seq=%s tail4=%s frames=%d" % [
		first, _p(_is_q(first)), changes, str(seq), str(last), frames]

func _arm_firstlaw() -> String:
	# Scope of the "first readback after play() is exactly 128 frames" law:
	# LOOP_DISABLED vs LOOP_FORWARD with default points vs explicit loop_end.
	var specs := [["disabled", AudioStreamWAV.LOOP_DISABLED, 0], ["fwd0", AudioStreamWAV.LOOP_FORWARD, 0],
			["fwd4410", AudioStreamWAV.LOOP_FORWARD, 4410]]
	var out: Array[String] = []
	for spec in specs:
		var s := _mk(1.0)
		s.loop_mode = spec[1]
		s.loop_begin = 0
		s.loop_end = spec[2]
		var player := AudioStreamPlayer.new()
		player.stream = s
		root.add_child(player)
		await process_frame
		player.play()
		var imm := player.get_playback_position()
		await process_frame
		var one := player.get_playback_position()
		await _wait_ms(150)
		var late := player.get_playback_position()
		var late_playing := player.is_playing()
		out.append("%s=%.7f/%.7f/%.7f/%s" % [spec[0], imm, one, late, _p(late_playing)])
		player.stop()
		player.stream = null
		player.free()
		await _drain(10)
	return " ".join(out)
