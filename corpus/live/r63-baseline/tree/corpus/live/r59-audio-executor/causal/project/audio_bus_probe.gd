extends SceneTree

func _initialize() -> void:
    var invalid := "--invalid" in OS.get_cmdline_user_args()
    var bus_name := "NoSuchBus" if invalid else "FixtureBus"
    if not invalid:
        AudioServer.add_bus()
        AudioServer.set_bus_name(AudioServer.bus_count - 1, "FixtureBus")
    var stream := AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.mix_rate = 22050
    stream.stereo = false
    var samples := PackedByteArray()
    for i in range(22050):
        var sample := int(sin(TAU * 440.0 * float(i) / 22050.0) * 8191.0)
        samples.append(sample & 0xff)
        samples.append((sample >> 8) & 0xff)
    stream.data = samples
    var player := AudioStreamPlayer.new()
    player.stream = stream
    player.bus = bus_name
    root.add_child(player)
    await process_frame
    player.play()
    var before := player.get_playback_position()
    for i in range(12):
        await process_frame
    var after := player.get_playback_position()
    print("BUS_PROBE invalid=%s requested=%s resolved_index=%s resolved_name=%s playing=%s advanced=%s before=%s after=%s" % [invalid, bus_name, AudioServer.get_bus_index(player.bus), AudioServer.get_bus_name(AudioServer.get_bus_index(player.bus)), player.is_playing(), after > before + 0.001, before, after])
    player.stop()
    player.free()
    for i in range(120):
        await process_frame
    quit(0)
