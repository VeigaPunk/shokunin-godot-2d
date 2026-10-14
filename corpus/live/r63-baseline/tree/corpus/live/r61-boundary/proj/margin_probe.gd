extends SceneTree

# r61-boundary startup-margin probe. Delays `--delay=<sec>` inside SceneTree
# (create_timer), then prints the signature marker and exits 0. The driver
# sweeps delay against run_process bounds to locate the accept/reject margin.

const MARKER := "MARGIN_PROBE: expected signature"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var delay := 0.0
	for a in user_args:
		if a.begins_with("--delay="):
			delay = float(a.trim_prefix("--delay="))
	print("MARGIN_PROBE start delay=", delay)
	if delay > 0.0:
		await create_timer(delay).timeout
	print(MARKER)
	quit(0)
