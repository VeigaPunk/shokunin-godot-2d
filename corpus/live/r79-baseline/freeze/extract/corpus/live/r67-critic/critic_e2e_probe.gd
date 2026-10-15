extends SceneTree

const SIG := "CRITIC_E2E: expected marker"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	if "--sig-stderr" in user_args:
		printerr(SIG)
	else:
		print(SIG)
	if "--stdout-error" in user_args:
		print("ERROR: stdout carried diagnostic")
	if "--stderr-error" in user_args:
		printerr("ERROR: stderr carried diagnostic")
	if "--stderr-push" in user_args:
		push_error("stderr pushed error")
	if "--stderr-warning" in user_args:
		printerr("WARNING: benign stderr chatter")
	if "--stdout-no-newline" in user_args:
		# Raw non-newline-terminated stdout byte run via FileAccess on fd 1.
		var f := FileAccess.open("/dev/stdout", FileAccess.WRITE)
		if f:
			f.store_string("ERR")
			f.flush()
	quit(0)
