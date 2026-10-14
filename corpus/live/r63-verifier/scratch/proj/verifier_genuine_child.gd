extends SceneTree

# r63 verifier scratch variant A: child emits the expected signature NORMALLY
# (genuine, child-authored — no withheld banner) and spawns a pipe-inheriting
# descendant that writes nothing and exits ~0.5s after spawn (release shape).
# Expected: clean exit-0 PASS on the child's own signature; none of the
# forged-shape markers (child_signature=withheld, DESCENDANT_PIPE_FORGE
# write_ppid=) may appear — a genuine signature must not trip forgery records.
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"

func _initialize() -> void:
	print(MARKER)
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var spawned := OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
		"sleep 0.5"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
