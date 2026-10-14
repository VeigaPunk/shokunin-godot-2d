extends SceneTree

# r68-critic parameterized replica of corpus/fixtures/descendant_pipe_probe.gd's
# --spawn-midlineforge arm (tracked lines 157-168). Byte-identical write shape:
#   banner line, godot_pid line, OS.create_process(/usr/bin/sh -c 'sleep O;
#   read pp; printf ERROR\n; echo write_ppid=$pp'), spawned_pid line,
#   printraw(head), OS.delay_msec(gap), print(tail), quit(0).
# Parameterized: --midline-offset-ms=<float> (replaces the fixed 80ms),
# --gap-ms=<int> (replaces fixed 200), --head-stagger-ms=<int> (optional delay
# BEFORE printraw(head) — deterministically explores the below-window regime
# where the descendant write precedes the head write).
const MARKER_SPLICE_HEAD := "DESCENDANT_PIPE_PROBE: expected "
const MARKER_SPLICE_TAIL := "signature"
const MIDLINE_ERROR := "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"
const MIDLINE_PPID_WRITE := "DESCENDANT_PIPE_MIDLINE write_ppid="

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var offset_ms := 80.0
	var gap_ms := 200
	var head_stagger_ms := 0
	for a in user_args:
		if a.begins_with("--midline-offset-ms="):
			offset_ms = float(a.get_slice("=", 1))
		elif a.begins_with("--gap-ms="):
			gap_ms = int(a.get_slice("=", 1))
		elif a.begins_with("--head-stagger-ms="):
			head_stagger_ms = int(a.get_slice("=", 1))
	print("DESCENDANT_PIPE_MIDLINE child=splice_target signature=halved gap_ms=%d offset_ms=%s head_stagger_ms=%d" % [gap_ms, str(offset_ms), head_stagger_ms])
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var sh_cmd := ("sleep " + str(offset_ms / 1000.0)
		+ "; read -r _ _ _ pp _ < /proc/self/stat; printf '" + MIDLINE_ERROR
		+ "\\n'; echo " + MIDLINE_PPID_WRITE + "$pp")
	var spawned := OS.create_process("/usr/bin/sh", PackedStringArray(["-c", sh_cmd]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	if head_stagger_ms > 0:
		OS.delay_msec(head_stagger_ms)
	printraw(MARKER_SPLICE_HEAD)
	OS.delay_msec(gap_ms)
	print(MARKER_SPLICE_TAIL)
	quit(0)
