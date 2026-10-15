extends SceneTree

# r63 verifier scratch variant C: markerless — child emits no signature and
# the descendant writes nothing; pipes release well inside the bound.
# Expected: exit 0, error None, signature ABSENT -> classify_process False.
# A record with no signature cannot forge a PASS at all.

func _initialize() -> void:
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var spawned := OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
		"sleep 0.5"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
