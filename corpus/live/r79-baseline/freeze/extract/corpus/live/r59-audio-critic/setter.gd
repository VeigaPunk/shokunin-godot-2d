extends SceneTree
func _initialize() -> void:
    AudioServer.add_bus()
    AudioServer.set_bus_name(AudioServer.bus_count - 1, "Effects")
    var p := AudioStreamPlayer.new()
    p.stream = AudioStreamWAV.new()
    root.add_child(p)
    await process_frame
    for route in ["Effects", "MissingBus"]:
        p.bus = route
        print("ASSIGN route=%s index=%s getter=%s" % [route, AudioServer.get_bus_index(route), p.bus])
    quit()
