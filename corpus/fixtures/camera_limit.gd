extends SceneTree

func _initialize() -> void:
    var far_bound := "--far-bound" in OS.get_cmdline_user_args()
    var target := Node2D.new()
    var camera := Camera2D.new()
    root.add_child(target)
    target.add_child(camera)
    camera.position_smoothing_enabled = false
    camera.limit_right = 1000
    if far_bound:
        camera.limit_right = 100000

    await process_frame
    camera.make_current()
    await process_frame
    camera.force_update_scroll()
    if not camera.is_current():
        push_error("camera limit setup failed: camera is not current")
        quit(2)
        return

    var before := camera.get_screen_center_position()
    var target_before := target.global_position
    target.global_position = Vector2(2000, 0)
    await process_frame
    camera.force_update_scroll()
    var center := camera.get_screen_center_position()
    var moved := target.global_position.distance_to(target_before) > 1000.0
    if not moved:
        push_error("camera limit setup failed: parent target did not move")
        quit(2)
        return
    if not camera.is_current():
        push_error("camera limit setup failed: camera lost current status")
        quit(2)
        return

    var authored_right_boundary := 1000.0
    var expected_clamped_center_x: float = authored_right_boundary - camera.get_viewport().get_visible_rect().size.x / 2.0
    var within_right_boundary := center.x <= authored_right_boundary + 0.01
    var at_expected_clamp := absf(center.x - expected_clamped_center_x) <= 0.01
    var center_advanced := center.distance_to(before) > 100.0
    var separated_from_target := center.distance_to(target.global_position) > 1.0
    if not within_right_boundary or not at_expected_clamp or not center_advanced or not separated_from_target:
        print("OBSERVED camera_limit center=(%.2f,%.2f) right_boundary=%.2f expected_clamp_x=%.2f target=(%.2f,%.2f)" % [center.x, center.y, authored_right_boundary, expected_clamped_center_x, target.global_position.x, target.global_position.y])
        push_error("camera limit assertion failed: expected active center within right boundary and distinct from target")
        quit(2)
        return
    print("PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true far_bound=%s" % str(far_bound))
    quit(0)
