extends SceneTree

const MARKER := "TIMEOUT_PROBE: expected signature"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	print(MARKER)
	if "--delay-clean" in user_args:
		await create_timer(1.5).timeout
	if "--hold-open" in user_args:
		await create_timer(30.0).timeout
	quit(0)
