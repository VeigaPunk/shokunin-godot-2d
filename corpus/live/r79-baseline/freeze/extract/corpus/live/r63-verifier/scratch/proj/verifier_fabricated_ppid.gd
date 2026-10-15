extends SceneTree

# r63 verifier scratch variant B: hold arm with a FABRICATED write_ppid.
# Same shape as --spawn-forge-hold: child withholds the signature, descendant
# polls /proc/self/stat until its ppid flips off the godot pid, then writes
# MARKER plus a deliberately FALSE write_ppid (=godot_pid+4000000 fixed bogus)
# and holds the pipes ~6s. Kernel /proc/<desc>/stat at return must disagree
# with the fabricated claim — the meta's hold_write_ppid_kernel_corroborated
# discrimination exists precisely to catch this slip class.
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const FORGE_PPID_WRITE := "DESCENDANT_PIPE_FORGE write_ppid="

func _initialize() -> void:
	print("DESCENDANT_PIPE_FORGE child_signature=withheld")
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var bogus := OS.get_process_id() + 4000000
	var spawned := OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
		"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo " + MARKER + "; echo " + FORGE_PPID_WRITE + str(bogus) + "; sleep 6"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
