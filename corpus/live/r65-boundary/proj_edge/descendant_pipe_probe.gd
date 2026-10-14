extends SceneTree

# r65-boundary SCRATCH-ONLY edge fixture. Byte-identical stock semantics plus
# additive --spawn-errforge-* arms. The tracked file
# corpus/fixtures/descendant_pipe_probe.gd is NOT touched; this copy lives
# under corpus/live/r65-boundary/proj_edge/ only. Stock arms preserved
# verbatim for control reruns.
#
# Arm map (all errforge descendants reuse the stock reparenting gate — the
# write is provably post-parent-exit unless the arm says PRE-death; pre-death
# arms spawn the descendant BEFORE the marker write and use a fixed offset):
#   --spawn-errforge-release        child prints MARKER + exits 0; descendant
#                                   post-death writes un-allowlisted
#                                   "ERROR: FORGED_DESCENDANT_ERROR ..." on
#                                   stdout + ERRFORGE write_ppid, releases.
#   --spawn-errforge-hold           same write, then holds both pipes ~6s.
#   --spawn-errforge-stderr-release forged error line on fd 2 post-death.
#   --spawn-errforge-predeath       descendant writes the SAME error line at a
#                                   fixed 20ms offset (write_ppid==godot_pid).
#   --spawn-errforge-split          "ERR" then "OR: ..." across two post-death
#                                   writes — the token reassembles in-pipe.
#   --spawn-errforge-glue           child's tail line is printraw-unterminated;
#                                   post-death error bytes glue onto it.
#   --spawn-errforge-midline        descendant spawned first; child emits
#                                   MARKER in two printraw halves with a
#                                   200ms gap; descendant injects the error
#                                   line pre-death into the gap.
#   --spawn-errforge-flood          N post-death error lines (--flood-count=N).
#   --spawn-errforge-combo-hold     child WITHHOLDS signature; descendant
#                                   post-death writes forged signature AND
#                                   forged error, then holds pipes ~6s.
#   --spawn-errforge-pipefull       descendant pumps --pump-kb=K KiB of error
#                                   lines post-death (yes|head -c), exits.
#   --spawn-errforge-pipefull-hold  same pump but UNBOUNDED exec yes — blocks
#                                   in write() once the pipe fills until the
#                                   reader drains or closes (SIGPIPE).
#   --spawn-errforge-newlinesplit   post-death "ERR\n" then "OR: ...\n" — the
#                                   token is split ACROSS a newline; no
#                                   captured line contains "ERROR:".
#   --spawn-errforge-allowlisted    post-death echo of an ALLOWLISTED error
#                                   string (save_corrupt_negative's) — tests
#                                   whether the allowlist is origin-blind.
#   --spawn-errforge-combo-release  child withholds sig; descendant writes
#                                   forged sig AND forged error post-death,
#                                   releases pipes (no timeout).
#   --flood-distinct                modifier: flood lines carry distinct ids.
#   --spawn-genuine-error           control: the CHILD itself emits the same
#                                   ERROR line pre-exit (printerr -> fd 2).

const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"
const FORGE_PPID_WRITE := "DESCENDANT_PIPE_FORGE write_ppid="
const ERR_LINE := "ERROR: FORGED_DESCENDANT_ERROR injected diagnostic"
const ERR_PPID := "DESCENDANT_PIPE_ERRFORGE write_ppid="
const TAIL_OPEN := "DESCENDANT_PIPE_TAIL_OPEN"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var forge_hold := "--spawn-forge-hold" in user_args
	var forge_release := "--spawn-forge-release" in user_args
	var err_release := "--spawn-errforge-release" in user_args
	var err_hold := "--spawn-errforge-hold" in user_args
	var err_stderr := "--spawn-errforge-stderr-release" in user_args
	var err_predeath := "--spawn-errforge-predeath" in user_args
	var err_split := "--spawn-errforge-split" in user_args
	var err_glue := "--spawn-errforge-glue" in user_args
	var err_midline := "--spawn-errforge-midline" in user_args
	var err_flood := "--spawn-errforge-flood" in user_args
	var err_combo := "--spawn-errforge-combo-hold" in user_args
	var err_combo_release := "--spawn-errforge-combo-release" in user_args
	var err_newlinesplit := "--spawn-errforge-newlinesplit" in user_args
	var err_allowlisted := "--spawn-errforge-allowlisted" in user_args
	var err_pipefull := "--spawn-errforge-pipefull" in user_args
	var err_pipefull_hold := "--spawn-errforge-pipefull-hold" in user_args
	var genuine_error := "--spawn-genuine-error" in user_args
	var flood_distinct := "--flood-distinct" in user_args
	var flood_n := "50"
	var pump_kb := "256"
	for a in user_args:
		if a.begins_with("--flood-count="):
			flood_n = a.split("=", false)[1]
		if a.begins_with("--pump-kb="):
			pump_kb = a.split("=", false)[1]
	var godot_pid := OS.get_process_id()
	# Stock reparenting gate: polls /proc/self/stat until ppid flips off this
	# process's pid — the write that follows is provably post-exit.
	var gate := "while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(godot_pid) + "\" ]; do sleep 0.05; done; "

	var spawned := -1
	# Pre-death arms must spawn BEFORE the marker emission so the descendant's
	# fixed-offset write lands inside this process's lifetime.
	if err_predeath:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 0.02; read -r _ _ _ pp _ < /proc/self/stat; echo '" + ERR_LINE + "'; echo " + ERR_PPID + "$pp"]))
	elif err_midline:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 0.08; read -r _ _ _ pp _ < /proc/self/stat; printf '" + ERR_LINE + "\\n'; echo " + ERR_PPID + "$pp"]))

	if forge_hold or forge_release or err_combo or err_combo_release:
		print("DESCENDANT_PIPE_FORGE child_signature=withheld")
	elif err_midline:
		printraw("DESCENDANT_PIPE_PROBE: expected ")
		OS.delay_msec(200)
		print("signature")
	else:
		print(MARKER)
	print("DESCENDANT_PIPE godot_pid=", godot_pid)

	if "--spawn-hold" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(godot_pid) + "\" ]; do sleep 0.05; done; echo " + POST_EXIT_WRITE + "; sleep 6"]))
	elif "--spawn-detach" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec sh -c 'sleep 8' </dev/null >/dev/null 2>&1"]))
	elif forge_hold or forge_release:
		var tail := "; sleep 6" if forge_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo " + MARKER + "; echo " + FORGE_PPID_WRITE + "$pp" + tail]))
	elif err_release or err_hold:
		var tail := "; sleep 6" if err_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + ERR_LINE + "'; echo " + ERR_PPID + "$pp" + tail]))
	elif err_stderr:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + ERR_LINE + "' >&2; echo " + ERR_PPID + "$pp"]))
	elif err_split:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf 'ERR'; sleep 0.05; printf 'OR: FORGED split-token diagnostic\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_glue:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf '" + ERR_LINE + "\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_flood:
		var flood_line := "'" + ERR_LINE + "'"
		if flood_distinct:
			flood_line = "\"ERROR: FORGED_DESCENDANT_ERROR distinct $i\""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "i=0; while [ $i -lt " + flood_n + " ]; do echo " + flood_line + "; i=$((i+1)); done; echo " + ERR_PPID + "$pp"]))
	elif err_combo or err_combo_release:
		var combo_tail := "; sleep 6" if err_combo else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo " + MARKER + "; echo '" + ERR_LINE + "'; echo " + FORGE_PPID_WRITE + "$pp; echo " + ERR_PPID + "$pp" + combo_tail]))
	elif err_newlinesplit:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf 'ERR\\n'; sleep 0.05; printf 'OR: FORGED_DESCENDANT_ERROR newline-split diagnostic\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_allowlisted:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo 'ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR'; echo " + ERR_PPID + "$pp"]))
	elif err_pipefull:
		var pump_bytes := str(int(pump_kb) * 1024)
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "yes '" + ERR_LINE + "' | head -c " + pump_bytes + "; echo " + ERR_PPID + "$pp"]))
	elif err_pipefull_hold:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "read -r _ _ _ pp _ < /proc/self/stat; echo " + ERR_PPID + "$pp; exec yes '" + ERR_LINE + "'"]))
	elif genuine_error:
		printerr(ERR_LINE)
		print("DESCENDANT_PIPE_GENUINE_ERROR emitted_by=child")
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	if err_glue:
		printraw(TAIL_OPEN)
	quit(0)
