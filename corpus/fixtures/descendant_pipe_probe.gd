extends SceneTree

# Round-62 tracked descendant pipe-EOF classification probe, promoted from the
# r61 boundary scratch probe (corpus/live/r61-boundary/proj/tree_probe.gd) and
# re-measured at r62 (corpus/live/r62-author/scratch-probe/). Prints the
# signature marker, then optionally spawns an OS descendant via
# OS.create_process; arm selected by user flag:
#   (none)          -> clean exit 0, no descendant (plain child-exit bound)
#   --spawn-hold    -> descendant inherits and HOLDS the captured stdout/stderr
#                      pipes: writes DESCENDANT_PIPE_AFTER_EXIT_WRITE only after
#                      its own ppid flips off this process's pid — i.e. provably
#                      after this process has exited (kernel reparenting is
#                      immediate; a presence-only write was shown forgeable by
#                      the r62 critic), then
#                      keeps the pipe fds open ~6s more. This process exits 0
#                      at once; the runner still reports TIMEOUT at the bound —
#                      the pinned pipe-EOF misattribution. Meta-driven, not a
#                      CASES arm: its record carries error set (always False).
#   --spawn-detach  -> descendant execs a nested sh with all stdio redirected
#                      to /dev/null: the pipe fds close with this process's
#                      exit, yet the descendant still outlives it — the
#                      child-exit-bound discriminating control (CASES row).
#   --spawn-forge-hold / --spawn-forge-release (r63 additions) ->
#                      this process WITHHOLDS the expected signature itself
#                      (prints a withheld banner instead of MARKER), so any
#                      occurrence of "DESCENDANT_PIPE_PROBE: expected
#                      signature" in captured output is provably the
#                      descendant's write. The descendant reuses the
#                      reparenting gate — it polls /proc/self/stat until its
#                      ppid flips off this process's pid, so the signature
#                      write is provably post-exit — then echoes the expected
#                      signature and DESCENDANT_PIPE_FORGE write_ppid=<ppid>
#                      (the reparented ppid; != godot_pid is in-record
#                      post-orphan provenance). -hold keeps both captured
#                      pipes open ~6s more (TIMEOUT record at the 3.0s meta
#                      bound; under the 8s CASES bound the same arm releases
#                      in time and also forges a PASS); -release exits
#                      immediately after writing, so pipe EOF arrives well
#                      inside the bound and the runner returns exit 0 with
#                      the forged signature present — the tracked
#                      known-accepting forgery row.
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"
const FORGE_PPID_WRITE := "DESCENDANT_PIPE_FORGE write_ppid="

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var forge_hold := "--spawn-forge-hold" in user_args
	var forge_release := "--spawn-forge-release" in user_args
	if forge_hold or forge_release:
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
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	quit(0)
