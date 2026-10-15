extends SceneTree
# reviewer r88: audio playing/peak timeline under the Dummy driver
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
	p.max_distance = 2000.0
	p.attenuation = 1.0
	root.add_child(p)
	p.play()
	var seq: Array = []
	for i in 26:
		await process_frame
		seq.append("%d:%s/%.2f" % [i, p.playing, AudioServer.get_bus_peak_volume_left_db(0, 0)])
	print("AUDTL %s" % " ".join(seq))
	print("AUDTL read_at_after_26 playing=%s pos=%.3f" % [p.playing, p.get_playback_position()])
	quit(0)
