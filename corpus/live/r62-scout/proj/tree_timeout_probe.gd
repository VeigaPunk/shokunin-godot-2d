extends SceneTree

# r62-scout process-tree probe (scratch-only; NOT a tracked fixture).
# Prints a signature marker and the Godot pid, optionally spawns an OS-level
# descendant via OS.create_process, then exits 0. Arms:
#   (none)          -> clean exit, no descendant (child-exit-bound control)
#   --spawn-hold    -> `sh` inherits the captured stdout/stderr pipes; it writes
#                      TREE_DESC_AFTER_PARENT_WRITE ~1s after spawn (after this
#                      process exits ~0.4s) and holds the pipes ~5s total
#   --spawn-detach  -> `sh` execs a nested sh with all stdio -> /dev/null; the
#                      descendant still outlives us but the captured pipes hit
#                      EOF at this process's exit
const MARKER := "TREE_TIMEOUT_PROBE: expected signature"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	print(MARKER)
	print("TREE_TIMEOUT_PROBE godot_pid=", OS.get_process_id())
	var spawned := -1
	if "--spawn-hold" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 1; echo TREE_DESC_AFTER_PARENT_WRITE; sleep 4"]))
	elif "--spawn-detach" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec sh -c 'sleep 4' </dev/null >/dev/null 2>&1"]))
	if spawned > 0:
		print("TREE_TIMEOUT_PROBE spawned_pid=", spawned)
	quit(0)
