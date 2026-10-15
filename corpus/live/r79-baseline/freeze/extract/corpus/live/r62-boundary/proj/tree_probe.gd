extends SceneTree

# r61-boundary process-tree probe. Prints a signature marker, optionally spawns
# an OS-level descendant via OS.create_process, then either exits cleanly or
# hangs. The descendant in --spawn-hold/--spawn-hang inherits this process's
# stdout/stderr pipes; in --spawn-detach it closes them at exec time.

const MARKER := "TREE_PROBE: expected signature"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var out_dir := ""
	for a in user_args:
		if a.begins_with("--out-dir="):
			out_dir = a.trim_prefix("--out-dir=")
	print(MARKER)
	print("TREE_PROBE godot_pid=", OS.get_process_id())
	var spawned := -1
	if "--spawn-hold" in user_args:
		# Holds inherited pipes: writes one line to the shared stdout ~1s after
		# spawn (i.e. after this process exits), then touches a file at ~7s.
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 1; echo TREE_DESC_AFTER_PARENT_WRITE; sleep 6; echo hold-outlived > " + out_dir + "/hold.descendant-outlived"]))
	elif "--spawn-detach" in user_args:
		# execs a nested sh with all stdio redirected; the pipe write ends close
		# with this process's exit, yet the descendant still outlives it.
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec sh -c 'sleep 5; echo detach-outlived > " + out_dir + "/detach.descendant-outlived' </dev/null >/dev/null 2>&1"]))
	elif "--spawn-hang" in user_args:
		# Holds inherited pipes and touches a file at ~5s; this process hangs.
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 5; echo hang-outlived > " + out_dir + "/hang.descendant-outlived"]))
	if spawned > 0:
		print("TREE_PROBE spawned_pid=", spawned)
	if "--spawn-hang" in user_args:
		await create_timer(30.0).timeout
	quit(0)
