extends SceneTree

const STDOUT_MARKER := "STREAM_STDOUT: expected attribution marker"
const STDERR_MARKER := "STREAM_STDERR: unrelated attribution diagnostic"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	print(STDOUT_MARKER)
	if "--stderr-unrelated" in user_args:
		printerr(STDERR_MARKER)
	quit(0)
