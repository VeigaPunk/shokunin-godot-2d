extends SceneTree

# r63-boundary multi-depth descendant probe (scratch only, sibling of the r62
# tracked descendant_pipe_probe.gd). Prints the signature marker unless
# --no-signature is passed, then optionally spawns ONE intermediate OS
# descendant via OS.create_process that executes a driver-written shell file:
#
#   --script-file=<name>  -> `sh -c 'sh <out-dir>/<name>'`; the file decides
#                          whether a grandchild (depth 2) or great-grandchild
#                          (depth 3) is spawned, whether each level holds the
#                          inherited captured pipes, and who writes what.
#                          Script files are driver-generated receipts under
#                          corpus/live/r63-boundary/arms/.
#   --no-signature        -> suppress MARKER (spoof arms: any signature in the
#                          captured merged stream came from a descendant).
#   --linger=<s>          -> await <s> before quit(0): keeps this process alive
#                          past an intermediate's death so a grandchild can be
#                          re-adopted as a DIRECT child (d2_reparent arm).
#   --hang                -> await 30s instead of exiting (live-child bound arm).
#
# Prints DEPTH_PROBE godot_pid= and DEPTH_PROBE spawned_pid= for /proc
# cross-checks; deeper pids are announced by the shell files themselves.

const MARKER := "DEPTH_PROBE: expected signature"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var out_dir := ""
	var script_file := ""
	var linger := 0.0
	for a in user_args:
		if a.begins_with("--out-dir="):
			out_dir = a.trim_prefix("--out-dir=")
		elif a.begins_with("--script-file="):
			script_file = a.trim_prefix("--script-file=")
		elif a.begins_with("--linger="):
			linger = float(a.trim_prefix("--linger="))
	if not "--no-signature" in user_args:
		print(MARKER)
	print("DEPTH_PROBE godot_pid=", OS.get_process_id())
	var spawned := -1
	if script_file != "":
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sh " + out_dir + "/" + script_file]))
	if spawned > 0:
		print("DEPTH_PROBE spawned_pid=", spawned)
	if "--hang" in user_args:
		await create_timer(30.0).timeout
	elif linger > 0.0:
		await create_timer(linger).timeout
	quit(0)
