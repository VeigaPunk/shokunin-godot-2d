extends SceneTree

const MARKER := "TIMEOUT_PROBE: expected signature"
const PRE := "TIMEOUT_PROBE: pre-delay"

func _initialize() -> void:
	print(PRE)
	await create_timer(1.25).timeout
	print(MARKER)
	var user_args := OS.get_cmdline_user_args()
	if "--hold-open" in user_args:
		await create_timer(30.0).timeout
	quit(0)
