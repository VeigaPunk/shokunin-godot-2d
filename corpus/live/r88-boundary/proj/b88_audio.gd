extends SceneTree
# r88 BOUNDARY seat — positional audio under the Dummy driver: per-frame timeline of
# playing/position/bus-peak, near and far, to test the "playing=false" negative pin
# and hunt for any false positive or bimodality.
# Launch: godot --headless --path proj --script res://b88_audio.gd -- --arm=<arm>

var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm.is_empty():
		print("R88B ARM_MISSING")
		quit(1)
		return
	print("R88B arm=%s" % arm)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"timeline": _arm_timeline()
		_:
			print("R88B unknown_arm=%s" % arm)
			quit(2)

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _arm_timeline() -> void:
	print("R88B audio driver=%s mix_rate=%.1f" % [
		AudioServer.get_driver_name(), AudioServer.get_mix_rate()])
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_8_BITS
	wav.mix_rate = 44100
	wav.stereo = false
	var data := PackedByteArray()
	for i in 4410:  # 0.1 s 440 Hz
		data.append(int(127 + 100 * sin(i * 440.0 * TAU / 44100.0)))
	wav.data = data
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	var listener := AudioListener2D.new()
	root.add_child(listener)
	listener.position = Vector2(0, 0)
	listener.make_current()
	var p := AudioStreamPlayer2D.new()
	p.stream = wav
	p.position = Vector2(0, 0)
	p.max_distance = 2000.0
	p.attenuation = 1.0
	root.add_child(p)
	print("R88B audio pre_play playing=%s pos=%.3f peak=%.2f listener_current=%s" % [
		p.playing, p.get_playback_position(),
		AudioServer.get_bus_peak_volume_left_db(0, 0), listener.is_current()])
	p.play()
	print("R88B audio sync_after_play playing=%s pos=%.3f" % [
		p.playing, p.get_playback_position()])
	var near: Array = []
	for i in 20:
		await process_frame
		near.append("f%d:%s/%.3f/%.2f" % [
			i, p.playing, p.get_playback_position(),
			AudioServer.get_bus_peak_volume_left_db(0, 0)])
	print("R88B audio near_seq=%s" % ",".join(near))
	p.position = Vector2(1800, 0)
	var far: Array = []
	for i in 20:
		await process_frame
		far.append("f%d:%s/%.3f/%.2f" % [
			i, p.playing, p.get_playback_position(),
			AudioServer.get_bus_peak_volume_left_db(0, 0)])
	print("R88B audio far_seq=%s" % ",".join(far))
	p.stop()
	print("R88B audio after_stop playing=%s pos=%.3f listen_pos=%s listener_current=%s" % [
		p.playing, p.get_playback_position(), _v2(listener.global_position),
		listener.is_current()])
	quit()
