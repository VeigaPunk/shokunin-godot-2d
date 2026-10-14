extends SceneTree
func _initialize() -> void:
 var target := Node2D.new()
 var camera := Camera2D.new()
 root.add_child(target)
 target.add_child(camera)
 camera.limit_top = -500
 if "--far-top-bound" in OS.get_cmdline_user_args(): camera.limit_top = -100000
 camera.position_smoothing_enabled = false
 await process_frame
 camera.make_current()
 await process_frame
 camera.force_update_scroll()
 print("VIEWPORT ", camera.get_viewport().get_visible_rect())
 print("BEFORE ", camera.get_screen_center_position(), " target ", target.global_position)
 target.global_position = Vector2(0, -2000)
 await process_frame
 camera.force_update_scroll()
 print("AFTER ", camera.get_screen_center_position(), " target ", target.global_position, " limit_top ", camera.limit_top)
 quit()
