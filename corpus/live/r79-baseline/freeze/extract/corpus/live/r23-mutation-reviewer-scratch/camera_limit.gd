extends SceneTree
func _initialize() -> void:
    var far_left := "--far-left-bound" in OS.get_cmdline_user_args()
    var target := Node2D.new()
    var camera := Camera2D.new()
    root.add_child(target)
    target.add_child(camera)
    camera.position_smoothing_enabled = false
    camera.limit_left = -100000 if far_left else -1000
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
    target.global_position = Vector2(-2000, 0)
    await process_frame
    camera.force_update_scroll()
    var center := camera.get_screen_center_position()
    if target.global_position.distance_to(target_before) <= 1000.0 or not camera.is_current():
        push_error("camera limit setup failed")
        quit(2)
        return
    var boundary := -1000.0
    var viewport_half := camera.get_viewport().get_visible_rect().size.x / 2.0
    var expected := boundary + viewport_half
    var ok := center.x >= boundary - 0.01 and absf(center.x - expected) <= 0.01 and center.distance_to(before) > 100.0 and center.distance_to(target.global_position) > 1.0
    if not ok:
        print("OBSERVED center=(%.2f,%.2f) expected=%.2f target=(%.2f,%.2f) far_left=%s" % [center.x, center.y, expected, target.global_position.x, target.global_position.y, str(far_left)])
        push_error("camera limit assertion failed: expected active center within left boundary and distinct from target")
        quit(2)
        return
    print("PASS camera_limit left=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true far_left=%s" % str(far_left))
    quit(0)
