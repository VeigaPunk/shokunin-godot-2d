extends SceneTree

func _initialize() -> void:
    var invalid := "--invalid" in OS.get_cmdline_user_args()
    var requested_bus := "NoSuchFixtureBus" if invalid else "FixtureBus"
    if not invalid:
        AudioServer.add_bus()
        AudioServer.set_bus_name(AudioServer.bus_count - 1, requested_bus)

    var stream := AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.mix_rate = 22050
    stream.stereo = false
    var samples := PackedByteArray()
    for index in range(22050):
        var sample := int(sin(TAU * 440.0 * float(index) / 22050.0) * 8191.0)
        samples.append(sample & 0xff)
        samples.append((sample >> 8) & 0xff)
    stream.data = samples

    var player := AudioStreamPlayer.new()
    player.name = "FixtureBusRoutePlayer"
    player.stream = stream
    player.bus = requested_bus
    root.add_child(player)
    await process_frame
    var in_tree := player.is_inside_tree()
    player.play()
    var before := player.get_playback_position()
    for frame in range(12):
        await process_frame
    var playing := player.is_playing()
    var after := player.get_playback_position()
    var advanced := after > before + 0.001
    var resolved_index := AudioServer.get_bus_index(player.bus)
    var resolved_bus := AudioServer.get_bus_name(resolved_index) if resolved_index >= 0 else "<invalid>"
    player.stop()
    player.stream = null
    player.free()
    if not invalid and resolved_index > 0:
        AudioServer.remove_bus(resolved_index)
    for frame in range(120):
        await process_frame

    if invalid:
        var invalid_route_detected := player_bus_route_did_not_resolve(requested_bus, resolved_index, resolved_bus)
        if not in_tree or not playing or not advanced:
            push_error("AUDIO BUS CONTROL ASSERTION FAILED: invalid-route playback observation unavailable, in_tree=%s playing=%s advanced=%s" % [in_tree, playing, advanced])
            quit(2)
            return
        if not invalid_route_detected:
            push_error("AUDIO BUS CONTROL ASSERTION FAILED: requested bus resolved to a non-Master route, requested=%s resolved_index=%s resolved_bus=%s" % [requested_bus, resolved_index, resolved_bus])
            quit(2)
            return
        push_error("AUDIO BUS CONTROL ASSERTION FAILED: requested invalid route silently fell back to Master, requested=%s resolved_index=%s resolved_bus=%s playing=true position_advanced=true" % [requested_bus, resolved_index, resolved_bus])
        quit(2)
        return
    else:
        var resolved_explicit_non_master := resolved_index > 0 and resolved_bus == requested_bus
        if not in_tree or not playing or not advanced or not resolved_explicit_non_master:
            push_error("AUDIO BUS ROUTE ASSERTION FAILED: explicit non-Master route/playback mismatch, in_tree=%s playing=%s advanced=%s requested=%s resolved_index=%s resolved_bus=%s" % [in_tree, playing, advanced, requested_bus, resolved_index, resolved_bus])
            quit(2)
            return
        print("PASS audio_bus_route in_tree=true requested=%s resolved_index=%s resolved_bus=%s playing=true position_advanced=true" % [requested_bus, resolved_index, resolved_bus])
    quit(0)

func player_bus_route_did_not_resolve(requested: String, index: int, resolved: String) -> bool:
    return index == 0 and resolved == "Master" and resolved != requested
