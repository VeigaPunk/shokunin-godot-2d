extends SceneTree
# r100b boundary mode-evidence probe: prints the launched project's physics
# threading setting + tick rate (proj vs proj_thr) so the `thr` batch is
# self-documenting. One-shot; not part of the cell matrix.
func _initialize() -> void:
	print("META sep2d=%s tps=%d dv=%s" % [
		str(ProjectSettings.get_setting("physics/2d/run_on_separate_thread")),
		Engine.physics_ticks_per_second, DisplayServer.get_name()])
	quit(0)
