extends SceneTree
func _initialize() -> void:
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
	var t0 := Time.get_ticks_usec()
	while Time.get_ticks_usec() - t0 < 150000:
		await process_frame
	print("fed pushed=%d peak=%.2f/%.2f pos=%.7f playing=%s" % [pushed,
		AudioServer.get_bus_peak_volume_left_db(0, 0), AudioServer.get_bus_peak_volume_right_db(0, 0),
		p.get_playback_position(), str(p.is_playing())])
	p.position = Vector2(800, 0)
	while Time.get_ticks_usec() - t0 < 300000:
		await process_frame
	print("fed_right800 peak=%.2f/%.2f" % [AudioServer.get_bus_peak_volume_left_db(0, 0),
		AudioServer.get_bus_peak_volume_right_db(0, 0)])
	p.stop()
	p.stream = null
	p.free()
	listener.free()
	for i in range(30):
		await process_frame
	quit(0)
