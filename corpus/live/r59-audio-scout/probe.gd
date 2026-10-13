extends SceneTree
func _initialize() -> void:
    AudioServer.add_bus()
    var idx := AudioServer.bus_count - 1
    AudioServer.set_bus_name(idx, "FixtureSfx")
    print("BUS_SETUP count=%d idx=%d name=%s lookup=%d master=%d" % [AudioServer.bus_count, idx, AudioServer.get_bus_name(idx), AudioServer.get_bus_index("FixtureSfx"), AudioServer.get_bus_index("Master")])
    var stream := AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.mix_rate = 22050
    var samples := PackedByteArray()
    for i in range(22050):
        var s := int(sin(TAU * 440.0 * float(i) / 22050.0) * 8191.0)
        samples.append(s & 255); samples.append((s >> 8) & 255)
    stream.data = samples
    var p := AudioStreamPlayer.new()
    p.stream = stream
    p.bus = "FixtureSfx"
    root.add_child(p)
    await process_frame
    print("POSITIVE bus=%s idx=%d" % [p.bus, AudioServer.get_bus_index(p.bus)])
    p.play()
    var b := p.get_playback_position()
    for f in range(12): await process_frame
    print("POSITIVE playing=%s before=%s after=%s" % [p.is_playing(), b, p.get_playback_position()])
    p.stop(); p.bus = "DefinitelyMissingBus"; p.play()
    for f in range(12): await process_frame
    print("INVALID bus=%s lookup=%d playing=%s pos=%s" % [p.bus, AudioServer.get_bus_index(p.bus), p.is_playing(), p.get_playback_position()])
    quit()
