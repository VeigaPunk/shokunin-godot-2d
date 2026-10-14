extends SceneTree

# r62-verifier scratch variant of corpus/fixtures/descendant_pipe_probe.gd.
# Same spawn mechanism (OS.create_process of /usr/bin/sh); the descendant arms
# are instrumented so the /proc/self/stat ppid gate is OBSERVABLE, and two
# forgery arms exist. All descendant introspection appends to the trace log
# path passed via --trace-log=<abs> (absolute path; pipe-independent evidence).
#
#   --gate-trace      committed hold semantics, instrumented: log first-observed
#                     ppid, per-loop ppid while gated, ppid at release, times;
#                     then write POST_EXIT_WRITE and keep pipes open 6s.
#   --forge-immediate stripped gate: write POST_EXIT_WRITE immediately, but first
#                     record own ppid + parent /proc state at write time (proves
#                     whether the write precedes parent death), hold pipes 6s.
#   --forge-detach    write POST_EXIT_WRITE through the inherited pipe, then exec
#                     a nested sh with all stdio to /dev/null and live 8s more:
#                     marker captured but pipes NOT held past parent exit.
#   --parent-delay-ms=N  parent busy-sleeps N ms after spawn before quit(0):
#                     makes gate-hold deterministic (gated arm) or makes a
#                     pre-exit write deterministic (forge-immediate arm).
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	print(MARKER)
	var godot_pid := OS.get_process_id()
	print("DESCENDANT_PIPE godot_pid=", godot_pid)
	var trace := ""
	var delay_ms := 0
	for a in user_args:
		if a.begins_with("--trace-log="):
			trace = a.split("=", true, 1)[1]
		elif a.begins_with("--parent-delay-ms="):
			delay_ms = int(a.split("=", true, 1)[1])
	assert(trace != "", "--trace-log=<abs> required")
	var g := str(godot_pid)
	var sh_body := ""
	if "--gate-trace" in user_args:
		# Same ppid-flip gate as the committed --spawn-hold arm, instrumented.
		# Field 4 of /proc/self/stat is ppid (pid (comm) state ppid ...).
		sh_body = (
			"read -r _ _ _ pp _ < /proc/self/stat; "
			+ "echo \"first_pp=$pp godot_pid=" + g + " t=$(date +%s.%N)\" >> " + trace + "; "
			+ "iters=0; "
			+ "while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + g + "\" ]; do iters=$((iters+1)); sleep 0.05; done; "
			+ "read -r _ _ _ pp _ < /proc/self/stat; "
			+ "st=$(cut -d' ' -f3 /proc/" + g + "/stat 2>/dev/null || echo gone); "
			+ "echo \"release_pp=$pp gate_iters=$iters godot_state_at_release=$st t=$(date +%s.%N)\" >> " + trace + "; "
			+ "echo " + POST_EXIT_WRITE + "; sleep 6")
	elif "--forge-detach" in user_args:
		sh_body = (
			"read -r _ _ _ pp _ < /proc/self/stat; "
			+ "st=$(cut -d' ' -f3 /proc/" + g + "/stat 2>/dev/null || echo gone); "
			+ "echo \"pre_write pp=$pp godot_state=$st t=$(date +%s.%N)\" >> " + trace + "; "
			+ "echo " + POST_EXIT_WRITE + "; "
			+ "exec sh -c 'sleep 8' </dev/null >/dev/null 2>&1")
	elif "--forge-immediate" in user_args:
		# Presence-only forgery: marker written with NO ppid gate; record own
		# ppid and the parent's liveness state AT write time.
		sh_body = (
			"read -r _ _ _ pp _ < /proc/self/stat; "
			+ "st=$(cut -d' ' -f3 /proc/" + g + "/stat 2>/dev/null || echo gone); "
			+ "echo \"pre_write pp=$pp godot_state=$st t=$(date +%s.%N)\" >> " + trace + "; "
			+ "echo " + POST_EXIT_WRITE + "; sleep 6")
	else:
		printerr("verifier_pipe_probe: no arm selected")
		quit(2)
		return
	var spawned := OS.create_process("/usr/bin/sh", PackedStringArray(["-c", sh_body]))
	print("DESCENDANT_PIPE spawned_pid=", spawned)
	if delay_ms > 0:
		OS.delay_msec(delay_ms)
	quit(0)
