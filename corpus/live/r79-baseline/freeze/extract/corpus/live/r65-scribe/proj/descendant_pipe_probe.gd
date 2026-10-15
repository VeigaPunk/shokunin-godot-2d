extends SceneTree

# r65 SCRIBE SCRATCH COPY of corpus/fixtures/descendant_pipe_probe.gd (r64
# HEAD) — untracked fixture under corpus/live/r65-scribe/proj/. The tracked
# fixture's four arms are preserved verbatim; five scribe-owned arms are
# ADDED for the forged-REJECTION dual measurement (the tracked file is never
# edited by this seat). Arm selected by user flag:
#   (none)               -> clean exit 0, genuine MARKER (same as tracked)
#   --spawn-detach       -> tracked arm (descendant detaches fds; control)
#   --spawn-hold         -> tracked arm (post-exit write + ~6s pipe hold)
#   --spawn-forge-hold / --spawn-forge-release -> tracked r63 arms (child
#                          WITHHOLDS signature; ppid-gated descendant writes
#                          it post-exit + write_ppid echo)
#   --self-error         -> scribe genuine-error control: the child itself
#                          prints MARKER, godot_pid, then the un-allowlisted
#                          error marker ERR_MARKER while ALIVE; exit 0.
#                          Genuine child-emitted error -> classify FAIL.
#   --errforge-release   -> child prints MARKER + godot_pid (signature IS
#                          emitted while alive — the clean-PASS shape) and
#                          spawns a ppid-gated descendant that echoes
#                          ERR_MARKER + DESCENDANT_PIPE_ERRFORGE
#                          write_ppid=<ppid> post-exit, then exits (pipes
#                          release). Expected record: exit0 + signature +
#                          un-allowlisted ERROR -> FAIL forged by post-death
#                          bytes.
#   --errforge-hold      -> same write, then holds both pipes ~6s (TIMEOUT
#                          record carrying the forged error).
#   --errforge-quiet     -> same post-death error write but the child does
#                          NOT echo spawned_pid and the descendant does NOT
#                          echo write_ppid: output is line-shape-identical
#                          to --self-error modulo the pid VALUE — zero
#                          in-record provenance.
#   --errforge-stderr    -> release arm with the error written to >&2.
#   --errforge-withhold  -> child withholds signature (banner), descendant
#                          writes BOTH signature and ERR_MARKER post-death,
#                          releases: forged-PASS + forged-FAIL in one write —
#                          the error axis overrides the signature axis.
#   --errforge-script    -> descendant writes a "SCRIPT ERROR:"-class line
#                          post-death — rejects via the script-error clause
#                          instead of the unrelated-error scan.
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"
const FORGE_PPID_WRITE := "DESCENDANT_PIPE_FORGE write_ppid="
const ERR_MARKER := "ERROR: INJECTED_DIAGNOSTIC classification tripwire"
const ERRFORGE_PPID_WRITE := "DESCENDANT_PIPE_ERRFORGE write_ppid="
const SCRIPT_ERR_MARKER := "SCRIPT ERROR: INJECTED_DIAGNOSTIC classification tripwire"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var forge_hold := "--spawn-forge-hold" in user_args
	var forge_release := "--spawn-forge-release" in user_args
	var errforge_hold := "--errforge-hold" in user_args
	var errforge_release := "--errforge-release" in user_args
	var errforge_quiet := "--errforge-quiet" in user_args
	var errforge_stderr := "--errforge-stderr" in user_args
	var errforge_withhold := "--errforge-withhold" in user_args
	var errforge_script := "--errforge-script" in user_args
	if forge_hold or forge_release or errforge_withhold:
		print("DESCENDANT_PIPE_FORGE child_signature=withheld")
	else:
		print(MARKER)
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	if "--self-error" in user_args:
		print(ERR_MARKER)
		quit(0)
		return
	var spawned := -1
	var quiet := errforge_quiet
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
	elif errforge_hold or errforge_release:
		var tail := "; sleep 6" if errforge_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo '" + ERR_MARKER + "'; echo " + ERRFORGE_PPID_WRITE + "$pp" + tail]))
	elif errforge_quiet:
		# No self-report: the ppid gate still runs (provably post-death write)
		# but no write_ppid line lands in the record.
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo '" + ERR_MARKER + "'"]))
	elif errforge_stderr:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo '" + ERR_MARKER + "' >&2; echo " + ERRFORGE_PPID_WRITE + "$pp >&2"]))
	elif errforge_withhold:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo " + MARKER + "; echo '" + ERR_MARKER + "'; echo " + ERRFORGE_PPID_WRITE + "$pp"]))
	elif errforge_script:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; echo '" + SCRIPT_ERR_MARKER + "'; echo " + ERRFORGE_PPID_WRITE + "$pp"]))
	if spawned > 0 and not quiet:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
