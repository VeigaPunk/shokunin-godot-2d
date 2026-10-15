extends SceneTree

func _initialize() -> void:
    var no_follow := "--no-follow" in OS.get_cmdline_user_args()
    var target := Node2D.new()
    var camera := Camera2D.new()
    root.add_child(target)
    if no_follow:
        root.add_child(camera)
    else:
        target.add_child(camera)
    camera.position_smoothing_enabled = false
    await process_frame
    camera.make_current()
    await process_frame
    camera.force_update_scroll()
    var before := camera.get_screen_center_position()
    var target_before := target.global_position
    target.global_position = Vector2(120, -53)
    await process_frame
    camera.force_update_scroll()
    var after := camera.get_screen_center_position()
    var moved := target.global_position.distance_to(target_before) > 100.0
    var tracked := camera.is_current() and after.distance_to(target.global_position) < 0.01 and after.distance_to(before) > 100.0
    if not moved or not tracked:
        push_error("camera follow assertion failed: target moved but active center did not track")
        quit(2)
        return
    print("PASS camera_follow moved=true current=true center_matches_target=true")
    quit(0)
