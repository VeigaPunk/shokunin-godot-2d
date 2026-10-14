extends SceneTree

# r62-author scratch candidate for the tracked descendant pipe-EOF probe.
# Prints the signature marker, then optionally spawns an OS descendant via
# OS.create_process:
#   (none)          -> clean exit 0, no descendant (plain child-exit bound)
#   --spawn-hold    -> descendant inherits and HOLDS the captured stdout/stderr
#                      pipes: writes DESCENDANT_PIPE_AFTER_EXIT_WRITE ~1s after
#                      spawn (i.e. after this process exits), then keeps the
#                      pipe fds open ~6s more. This process exits 0 at once.
#   --spawn-detach  -> descendant execs a nested sh with all stdio redirected
#                      to /dev/null: the pipe fds close with this process's
#                      exit, yet the descendant still outlives it.
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	print(MARKER)
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var spawned := -1
	if "--spawn-hold" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 1; echo " + POST_EXIT_WRITE + "; sleep 6"]))
	elif "--spawn-detach" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec sh -c 'sleep 5' </dev/null >/dev/null 2>&1"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
