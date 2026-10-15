extends SceneTree

# r65 critic counterexample probe — scratch-only, never tracked. Reuses the
# author's reparenting gate verbatim (/proc/self/stat ppid poll) but adds the
# arms the fixture lacks:
#   --detach-errforge        -> descendant exec-redirects all stdio to
#                               /dev/null BEFORE the gate, then emits the
#                               byte-identical ERROR: marker + write_ppid
#                               post-death into a FILE: post-death emission
#                               happens, but nothing enters the captured
#                               pipe -> the record should stay clean PASS.
#   --detach-errforge-late   -> same, plus a 1.5s sleep after the gate so
#                               the emission lands after communicate()
#                               returns (post-RETURN write, provably lost).
#   --stderr-errforge        -> gate-gated descendant echoes the marker on
#                               stderr (>&2): first-party stream check (the
#                               author leaned on the scribe lane's matrix).
#   --double-errforge        -> child push_error's the marker pre-death AND
#                               a gate-gated descendant echoes the same
#                               bytes post-death: two emissions, one
#                               deduped error_lines entry.

const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const ERRFORGE_PPID_WRITE := "DESCENDANT_PIPE_ERRFORGE write_ppid="
const ERRFORGE_ERROR_BODY := "DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
const ERRFORGE_ERROR := "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var detach := "--detach-errforge" in user_args
	var detach_late := "--detach-errforge-late" in user_args
	var stderr_arm := "--stderr-errforge" in user_args
	var double_arm := "--double-errforge" in user_args
	var outfile := ""
	for a in user_args:
		if a.begins_with("--errforge-outfile="):
			outfile = a.split("=", true, 1)[1]
	print(MARKER)
	print("DESCENDANT_PIPE_ERRFORGE critic_arm")
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var spawned := -1
	var gate := "while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done"
	if detach or detach_late:
		var delay := "; sleep 1.5" if detach_late else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec >/dev/null 2>&1; " + gate + delay + "; { echo " + ERRFORGE_ERROR + "; echo " + ERRFORGE_PPID_WRITE + "$pp; } > " + outfile]))
	elif stderr_arm:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "; echo " + ERRFORGE_ERROR + " >&2; echo " + ERRFORGE_PPID_WRITE + "$pp"]))
	elif double_arm:
		push_error(ERRFORGE_ERROR_BODY)
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "; echo " + ERRFORGE_ERROR + "; echo " + ERRFORGE_PPID_WRITE + "$pp"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
