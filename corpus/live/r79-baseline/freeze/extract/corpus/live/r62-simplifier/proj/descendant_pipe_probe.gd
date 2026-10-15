extends SceneTree

# Round-62 tracked descendant pipe-EOF classification probe, promoted from the
# r61 boundary scratch probe (corpus/live/r61-boundary/proj/tree_probe.gd) and
# re-measured at r62 (corpus/live/r62-author/scratch-probe/). Prints the
# signature marker, then optionally spawns an OS descendant via
# OS.create_process; arm selected by user flag:
#   (none)          -> clean exit 0, no descendant (plain child-exit bound)
#   --spawn-hold    -> descendant inherits and HOLDS the captured stdout/stderr
#                      pipes: writes DESCENDANT_PIPE_AFTER_EXIT_WRITE ~1s after
#                      spawn (provably after this process's ~0.4s exit), then
#                      keeps the pipe fds open ~6s more. This process exits 0
#                      at once; the runner still reports TIMEOUT at the bound —
#                      the pinned pipe-EOF misattribution. Meta-driven, not a
#                      CASES arm: its record carries error set (always False).
#   --spawn-detach  -> descendant execs a nested sh with all stdio redirected
#                      to /dev/null: the pipe fds close with this process's
#                      exit, yet the descendant still outlives it — the
#                      child-exit-bound discriminating control (CASES row).
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	print(MARKER)
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var spawned := -1
	if "--spawn-hold" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 1; echo " + POST_EXIT_WRITE + "; sleep 6"]))
	elif "--spawn-detach" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec sh -c 'sleep 5' </dev/null >/dev/null 2>&1"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
