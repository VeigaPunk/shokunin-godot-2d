extends SceneTree

# r63-simplifier candidate-minimal forged-signature arm (scratch-only).
# Mirrors the tracked descendant_pipe_probe.gd shape: the child prints its
# pid, prints MARKER unless a forge flag suppresses it, and the descendant
# writes the signature into the inherited pipes ONLY after its own ppid
# flips off the child pid (kernel reparenting gate — provably post-death).
#   --forge-release -> child silent; descendant writes MARKER post-death and
#                      exits (pipes EOF ~immediately after the write)
#   --forge-hold    -> child silent; descendant writes MARKER post-death then
#                      holds the pipes ~6s
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	if "--forge-release" not in user_args and "--forge-hold" not in user_args:
		print(MARKER)
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var spawned := -1
	if "--forge-release" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo '" + MARKER + "'"]))
	elif "--forge-hold" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo '" + MARKER + "'; sleep 6"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
