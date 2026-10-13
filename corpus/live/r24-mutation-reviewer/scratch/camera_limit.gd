extends SceneTree

func _initialize() -> void:
    var far_bound := "--far-bound" in OS.get_cmdline_user_args()
    var far_top_bound := "--far-top-bound" in OS.get_cmdline_user_args()
    var far_left_bound := "--far-left-bound" in OS.get_cmdline_user_args()
    var far_bottom_bound := "--far-bottom-bound" in OS.get_cmdline_user_args()
    var target := Node2D.new()
    var camera := Camera2D.new()
    root.add_child(target)
    target.add_child(camera)
    camera.position_smoothing_enabled = false
    camera.limit_right = 1000
    camera.limit_top = -1000
    camera.limit_left = -1000
    camera.limit_bottom = 100000
    if far_bound:
        camera.limit_right = 100000
    if far_left_bound:
        camera.limit_left = -100000
    if far_top_bound:
        camera.limit_top = -100000
    if far_bottom_bound:
        camera.limit_bottom = 100000
    if far_bottom_bound:
        camera.limit_bottom = 100000

    await process_frame
    camera.make_current()
    await process_frame
    camera.force_update_scroll()
    if not camera.is_current():
        push_error("camera limit setup failed: camera is not current")
        quit(2)
        return

    var left_test := "--left-bound" in OS.get_cmdline_user_args() or far_left_bound
    var top_test := "--top-bound" in OS.get_cmdline_user_args() or far_top_bound
    var bottom_test := "--bottom-bound" in OS.get_cmdline_user_args() or far_bottom_bound
    var before := camera.get_screen_center_position()
    var target_before := target.global_position
    target.global_position = Vector2(-2000, 0) if left_test else (Vector2(2000, 0) if not top_test and not bottom_test else (Vector2(0, -2000) if top_test else Vector2(0, 2000)))
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

    var boundary := -1000.0 if left_test or top_test else 1000.0
    var viewport_half := camera.get_viewport().get_visible_rect().size.x / 2.0 if left_test or (not top_test and not bottom_test) else camera.get_viewport().get_visible_rect().size.y / 2.0
    var expected_clamp := boundary - viewport_half if bottom_test else (boundary + viewport_half if left_test or top_test else boundary - viewport_half)
    var center_axis := center.x if left_test or (not top_test and not bottom_test) else center.y
    var at_expected_clamp := absf(center_axis - expected_clamp) <= 0.01
    var within_boundary := center_axis <= boundary + 0.01 if bottom_test else (center_axis >= boundary - 0.01 if left_test or top_test else center_axis <= boundary + 0.01)
    var center_advanced := center.distance_to(before) > 100.0
    var separated_from_target := center.distance_to(target.global_position) > 1.0
    if not within_boundary or not at_expected_clamp or not center_advanced or not separated_from_target:
        print("OBSERVED camera_limit center=(%.2f,%.2f) boundary=%.2f expected_clamp=%.2f target=(%.2f,%.2f) top_test=%s" % [center.x, center.y, boundary, expected_clamp, target.global_position.x, target.global_position.y, str(top_test)])
        push_error("camera limit assertion failed: expected active center within %s boundary and distinct from target" % ("left" if left_test else ("top" if top_test else ("bottom" if bottom_test else "right"))))
        quit(2)
        return
    print("PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true far_bound=%s far_top_bound=%s far_left_bound=%s far_bottom_bound=%s top_test=%s left_test=%s bottom_test=%s" % [str(far_bound), str(far_top_bound), str(far_left_bound), str(far_bottom_bound), str(top_test), str(left_test), str(bottom_test)])
    quit(0)
