extends SceneTree

# r68-author spike: instrumented midlineforge timing probe (scratch-only).
# Descendant reports its own write timestamp (CLOCK_REALTIME via date %s%3N);
# the child reports head/tail print timestamps on stderr — same clock domain.
func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var offset_ms := 80
	var gap_ms := 200
	for a in user_args:
		if a.begins_with("--midline-offset-ms="):
			offset_ms = a.get_slice("=", 1).to_int()
		elif a.begins_with("--gap-ms="):
			gap_ms = a.get_slice("=", 1).to_int()
	var t0 := int(Time.get_unix_time_from_system() * 1000.0)
	printerr("CHILD_MS t0=%d pid=%d" % [t0, OS.get_process_id()])
	var spawned := OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
		("sleep %d.%03d; " % [offset_ms / 1000, offset_ms % 1000])
		+ "date '+DESC_WRITE_MS=%s%3N'; read -r _ _ _ pp _ < /proc/self/stat; printf 'ERROR: DESCENDANT_PIPE_MIDLINE forged splice\\n'; echo DESCENDANT_PIPE_MIDLINE write_ppid=$pp"]))
	printerr("CHILD_MS spawned=%d pid=%d" % [int(Time.get_unix_time_from_system() * 1000.0) - t0 + t0, spawned])
	printraw("DESCENDANT_PIPE_PROBE: expected ")
	printerr("CHILD_MS head=%d" % int(Time.get_unix_time_from_system() * 1000.0))
	OS.delay_msec(gap_ms)
	print("signature")
	printerr("CHILD_MS tail=%d" % int(Time.get_unix_time_from_system() * 1000.0))
	quit(0)
