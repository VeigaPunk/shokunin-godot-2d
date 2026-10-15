extends SceneTree
func _initialize() -> void:
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = 44100
	s.stereo = false
	var n := 4410
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in range(n):
		data.encode_s16(i * 2, int(sin(TAU * 440.0 * float(i) / 44100.0) * 8191.0))
	s.data = data
	s.loop_mode = AudioStreamWAV.LOOP_FORWARD
	s.loop_begin = 0
	s.loop_end = 4410
	var p := AudioStreamPlayer.new()
	p.stream = s
	root.add_child(p)
	await process_frame
	p.play()
	var lines: Array[String] = []
	var prev := -1.0
	var t0 := Time.get_ticks_usec()
	for f in range(160):
		await process_frame
		var pos := p.get_playback_position()
		if absf(pos - prev) > 0.000001:
			lines.append("f=%d us=%d pos=%.9f" % [f + 1, Time.get_ticks_usec() - t0, pos])
			prev = pos
	print("PASS loopdbg changes=%d playing=%s" % [lines.size(), str(p.is_playing())])
	print(" | ".join(lines))
	p.stop()
	p.stream = null
	p.free()
	quit(0)
