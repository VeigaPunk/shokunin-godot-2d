extends SceneTree

# r66 critic probe — splice/evade arms authored by a post-death descendant.
# Reuses the r62-r65 reparenting gate: the descendant polls /proc/self/stat
# until its ppid flips off this process's pid, so every write is provably
# post-exit. Arms:
#   --splice-phantom   descendant writes "tail ERROR" (no newline) to its
#                      inherited stdout and ": PHANTOM post-death splice" to
#                      inherited stderr: a pure post-death fabrication of a
#                      merged ERROR: line present in neither stream's line
#                      set — no child cooperation, child output line-clean.
#   --splice-allowlisted  same, but the fabricated merged line byte-equals
#                      the save_corrupt_negative allowlist entry.
#   --double           descendant emits a real diagnostic split inside its
#                      ERROR: token ("ERR\nOR:") AND splices a phantom —
#                      evade + fabricate on one record.
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const PPIDI := "CRITIC_SURFACE write_ppid="

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	print(MARKER)
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var spawned := -1
	if "--splice-phantom" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; printf 'descendant tail ERROR'; printf ': PHANTOM post-death splice\\n' >&2; echo " + PPIDI + "$pp >&2"]))
	elif "--splice-allowlisted" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; printf 'ERROR'; printf ': SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR\\n' >&2; echo " + PPIDI + "$pp >&2"]))
	elif "--double" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; printf 'desc tail ERROR'; printf ': PHANTOM fabricated\\nERR\\nOR: real emitted diagnostic\\n' >&2; echo " + PPIDI + "$pp >&2"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
