extends SceneTree

const MARKER := "CRASH_EXIT_PROBE: expected signature"

func _initialize() -> void:
	print(MARKER)
	var user_args := OS.get_cmdline_user_args()
	if "--hold-open" in user_args:
		await create_timer(30.0).timeout
	quit(1)
