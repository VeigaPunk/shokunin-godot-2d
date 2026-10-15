extends SceneTree
func _initialize() -> void:
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
	var listener := AudioListener2D.new()
	listener.position = Vector2(0, 0)
	root.add_child(listener)
	listener.make_current()
	var p := AudioStreamPlayer2D.new()
	p.stream = s
	root.add_child(p)
	await process_frame
	p.position = Vector2(0, 0)
	p.play()
	for x in [0, 1, 5, 20, 50, 100, 800]:
		p.position = Vector2(x, 0)
		var t0 := Time.get_ticks_usec()
		while Time.get_ticks_usec() - t0 < 400000:
			await process_frame
		var l := AudioServer.get_bus_peak_volume_left_db(0, 0)
		var r := AudioServer.get_bus_peak_volume_right_db(0, 0)
		print("x=%d l=%.2f r=%.2f diff=%.2f" % [x, l, r, l - r])
	p.stop()
	p.stream = null
	p.free()
	listener.free()
	quit(0)
