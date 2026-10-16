extends SceneTree
func _initialize() -> void:
	print("TPS_REPORT physics_ticks_per_second=", Engine.physics_ticks_per_second,
		" time_scale=", Engine.time_scale)
	quit(0)
