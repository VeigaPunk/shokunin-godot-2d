extends SceneTree

# r64 BOUNDARY edge variant — scratch-only, NEVER promoted verbatim.
# Base: tracked corpus/fixtures/descendant_pipe_probe.gd sha256 4fce0676…
# r64 boundary additions (probe edges of the while-live signature gate):
#   --spawn-forge-stderr-release / --spawn-forge-stderr-hold
#                      same reparenting-gated post-death forge as the tracked
#                      r63 arms, but the forged signature + write_ppid go to
#                      STDERR instead of stdout (echo >&2). Tests whether the
#                      gate's merged-capture read discriminates identically
#                      when the forged bytes arrive on the second pipe.
#   --spawn-forge-predeath [-hold] [--forge-offset=<s>] [--forge-stderr]
#                      descendant does NOT wait for reparenting: it sleeps a
#                      fixed offset (default 0.15s) then writes the expected
#                      signature while the godot child is still its live
#                      parent — write_ppid read at write time == godot_pid is
#                      in-record PRE-death provenance. This is the declared
#                      gate-defeating shape (observation-time liveness cannot
#                      see authorship). -hold keeps pipes open ~6s more;
#                      --forge-stderr emits to stderr instead of stdout.
#   --spawn-forge-halfhalf [--forge-offset=<s>]
#                      descendant writes the FIRST HALF of the signature
#                      bytes pre-death (printf, no newline), then runs the
#                      reparent gate, then writes the completing bytes:
#                      the marker substring completes post-death — probes
#                      what "observed" means for a split signature.
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"
const FORGE_PPID_WRITE := "DESCENDANT_PIPE_FORGE write_ppid="

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var forge_hold := "--spawn-forge-hold" in user_args
	var forge_release := "--spawn-forge-release" in user_args
	var forge_stderr_release := "--spawn-forge-stderr-release" in user_args
	var forge_stderr_hold := "--spawn-forge-stderr-hold" in user_args
	var predeath := "--spawn-forge-predeath" in user_args
	var predeath_hold := "--spawn-forge-predeath-hold" in user_args
	var halfhalf := "--spawn-forge-halfhalf" in user_args
	var forge_stderr := "--forge-stderr" in user_args
	var forge_offset := "0.15"
	for a in user_args:
		if a.begins_with("--forge-offset="):
			forge_offset = a.trim_prefix("--forge-offset=")
	var withholds := (forge_hold or forge_release or forge_stderr_release
		or forge_stderr_hold or predeath or predeath_hold or halfhalf)
	if withholds:
		print("DESCENDANT_PIPE_FORGE child_signature=withheld")
	else:
		print(MARKER)
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var spawned := -1
	if "--spawn-hold" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo " + POST_EXIT_WRITE + "; sleep 6"]))
	elif "--spawn-detach" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec sh -c 'sleep 8' </dev/null >/dev/null 2>&1"]))
	elif forge_hold or forge_release:
		var tail := "; sleep 6" if forge_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo " + MARKER + "; echo " + FORGE_PPID_WRITE + "$pp" + tail]))
	elif forge_stderr_release or forge_stderr_hold:
		var tail := "; sleep 6" if forge_stderr_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo " + MARKER + " >&2; echo " + FORGE_PPID_WRITE + "$pp >&2" + tail]))
	elif predeath or predeath_hold:
		# No reparent gate: fixed offset then write — pre-death while the
		# offset is inside godot's live window. write_ppid==godot_pid proves
		# the write happened before reparenting (i.e. pre-death).
		var redir := " >&2" if forge_stderr else ""
		var tail := "; sleep 6" if predeath_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep " + forge_offset + "; read -r _ _ _ pp _ < /proc/self/stat; echo " + MARKER + redir + "; echo " + FORGE_PPID_WRITE + "$pp" + redir + tail]))
	elif halfhalf:
		# First half of the marker bytes pre-death (printf, no newline), then
		# reparent-gate, then the completing bytes: marker substring completes
		# post-death in the reader's accumulation buffer.
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep " + forge_offset + "; read -r _ _ _ pp _ < /proc/self/stat; echo FORGE_HALF1 pp=$pp; printf 'DESCENDANT_PIPE_PROBE: expected sign'; while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; printf 'ature\\n'; echo " + FORGE_PPID_WRITE + "$pp"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
