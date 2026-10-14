extends SceneTree
func _initialize() -> void:
    AudioServer.add_bus()
    var idx := AudioServer.bus_count - 1
    AudioServer.set_bus_name(idx, "Effects")
    for route in ["Effects", "MissingBus", ""]:
        var stream := AudioStreamWAV.new()
        stream.format = AudioStreamWAV.FORMAT_16_BITS
        stream.mix_rate = 22050
        var bytes := PackedByteArray()
        for i in range(22050):
            bytes.append(0)
            bytes.append(0)
        stream.data = bytes
        var player := AudioStreamPlayer.new()
        player.bus = route
        player.stream = stream
        root.add_child(player)
        await process_frame
        player.play()
        var before := player.get_playback_position()
        for frame in range(12):
            await process_frame
        print("ROUTE requested=%s bus_index=%s property=%s playing=%s before=%s after=%s" % [route, AudioServer.get_bus_index(route), player.bus, player.is_playing(), before, player.get_playback_position()])
        player.stop()
        player.stream = null
        player.free()
        stream = null
        bytes.clear()
        for frame in range(120):
            await process_frame
    quit(0)
