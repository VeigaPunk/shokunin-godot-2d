extends SceneTree
func _initialize() -> void:
    var stream := AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.mix_rate = 22050
    stream.stereo = false
    var samples := PackedByteArray()
    for i in range(22050):
        var sample := int(sin(TAU * 440.0 * float(i) / 22050.0) * 8191.0)
        samples.append(sample & 255)
        samples.append((sample >> 8) & 255)
    stream.data = samples
    AudioServer.add_bus()
    AudioServer.set_bus_name(1, "ProbeNonMaster")
    for bus_name in ["ProbeNonMaster", "ProbeMissing"]:
        var p := AudioStreamPlayer.new()
        p.name = bus_name
        p.stream = stream
        p.bus = bus_name
        root.add_child(p)
        await process_frame
        p.play()
        var before := p.get_playback_position()
        for frame in range(12):
            await process_frame
        print("RESULT bus=%s effective_bus=%s playing=%s before=%s after=%s" % [bus_name, p.get_bus(), p.is_playing(), before, p.get_playback_position()])
        p.stop()
        p.free()
    quit()
