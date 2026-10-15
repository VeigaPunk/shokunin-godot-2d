extends SceneTree
# r88-critic audio liveness probe: mirrors _arm_audio_pos, but records the
# immediate post-play() ack and the per-frame playing timeline, to test
# whether a fixture-side `if not p.playing: _fail(...)` guard is safe.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_8_BITS
	wav.mix_rate = 44100
	wav.stereo = false
	var data := PackedByteArray()
	for i in 44100 / 10:
		data.append(int(127 + 100 * sin(i * 440.0 * TAU / 44100.0)))
	wav.data = data
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	var listener := AudioListener2D.new()
	root.add_child(listener)
	listener.make_current()
	var p := AudioStreamPlayer2D.new()
	p.stream = wav
	p.position = Vector2(0, 0)
	p.max_distance = 2000.0
	p.attenuation = 1.0
	root.add_child(p)
	p.play()
	var ack := p.playing
	var tl := ""
	for i in 20:
		await process_frame
		tl += ("1" if p.playing else "0")
	print("PASS r88_audio_ack ack=%s tl=%s f20_playing=%s pos=%.3f peak=%.2f" % [
		ack, tl, p.playing, p.get_playback_position(),
		AudioServer.get_bus_peak_volume_left_db(0, 0)])
	quit(0)
