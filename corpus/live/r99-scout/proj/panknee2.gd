extends SceneTree
func _mkstream() -> AudioStreamWAV:
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = 44100
	s.stereo = false
	var n := 264600
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in range(n):
		data.encode_s16(i * 2, int(sin(TAU * 440.0 * float(i) / 44100.0) * 8191.0))
	s.data = data
	return s
func _initialize() -> void:
	var listener := AudioListener2D.new()
	listener.position = Vector2(0, 0)
	root.add_child(listener)
	listener.make_current()
	for cfg in [[2000.0, 1.0], [4000.0, 1.0], [1000.0, 1.0], [2000.0, 0.5]]:
		var p := AudioStreamPlayer2D.new()
		p.stream = _mkstream()
		p.max_distance = cfg[0]
		p.panning_strength = cfg[1]
		root.add_child(p)
		await process_frame
		p.position = Vector2(0, 0)
		p.play()
		var out := "cfg_maxd=%.0f ps=%.1f" % [cfg[0], cfg[1]]
		for x in [0, 32, 64, 96, 128, 200]:
			p.position = Vector2(x, 0)
			var t0 := Time.get_ticks_usec()
			while Time.get_ticks_usec() - t0 < 300000:
				await process_frame
			var l := AudioServer.get_bus_peak_volume_left_db(0, 0)
			var r := AudioServer.get_bus_peak_volume_right_db(0, 0)
			out += " x%d=%.2f" % [x, l - r]
		print(out)
		p.stop()
		p.stream = null
		p.free()
		await process_frame
	listener.free()
	quit(0)
