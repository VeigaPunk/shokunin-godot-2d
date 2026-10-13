extends SceneTree

const MARKER := "TIMEOUT_PROBE: same signature"

func _initialize() -> void:
	print(MARKER)
	if "--hold-open" in OS.get_cmdline_user_args():
		await create_timer(30.0).timeout
	quit(0)
