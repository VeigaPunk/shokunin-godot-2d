extends SceneTree
func _initialize() -> void:
 var far := "--far-bottom" in OS.get_cmdline_user_args()
 var target := Node2D.new()
 var camera := Camera2D.new()
 root.add_child(target)
 target.add_child(camera)
 camera.position_smoothing_enabled = false
 camera.limit_bottom = 1000
 if far: camera.limit_bottom = 100000
 await process_frame
 camera.make_current()
 await process_frame
 target.global_position = Vector2(0, 2000)
 await process_frame
 camera.force_update_scroll()
 var center := camera.get_screen_center_position()
 var viewport_half := camera.get_viewport().get_visible_rect().size.y / 2.0
 var expected := 1000.0 - viewport_half
 print("OBS center=(%.2f,%.2f) target=(%.2f,%.2f) height=%.2f half=%.2f bottom=%.2f far=%s" % [center.x, center.y, target.global_position.x, target.global_position.y, camera.get_viewport().get_visible_rect().size.y, viewport_half, camera.limit_bottom, str(far)])
 quit(0)
