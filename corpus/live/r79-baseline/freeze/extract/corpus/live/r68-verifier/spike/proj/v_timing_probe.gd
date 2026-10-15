extends SceneTree

# r68-verifier independent instrumented midlineforge timing probe.
# The child reports head/tail print timestamps on stderr (CLOCK_REALTIME via
# Time.get_unix_time_from_system); the descendant reports its own write time
# via `date +%s%3N` immediately before the forged write — same clock domain.
# Written independently of r68-author's spike (same mechanics, own layout).

const HEAD := "DESCENDANT_PIPE_PROBE: expected "
const TAIL := "signature"
const FORGED := "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var offset_ms := 80
	var gap_ms := 200
	for a in user_args:
		if a.begins_with("--off="):
			offset_ms = a.get_slice("=", 1).to_int()
		elif a.begins_with("--gap="):
			gap_ms = a.get_slice("=", 1).to_int()
	var spawned := OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
		("sleep %d.%03d; " % [offset_ms / 1000, offset_ms % 1000])
		+ "date '+V_WRITE_MS=%s%3N'; printf '" + FORGED + "\\n'"]))
	printraw(HEAD)
	printerr("V_HEAD_MS=%d" % int(Time.get_unix_time_from_system() * 1000.0))
	OS.delay_msec(gap_ms)
	printerr("V_TAIL_MS=%d" % int(Time.get_unix_time_from_system() * 1000.0))
	print(TAIL)
	quit(0)
