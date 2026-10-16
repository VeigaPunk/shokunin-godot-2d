extends SceneTree

# Round-61 tracked spontaneous-crash classification probe, promoted from the
# round-60 scratch probe measured twice on this host (r60-author +
# r60-verifier). Mirrors crash_exit_probe.gd pair structure: same emitted
# marker in every arm; arm selected by user flag:
#   (none)                  -> clean expected nonzero exit 1 (accept shape)
#   --spontaneous-crash     -> marker, then engine self-crash via OS.crash()
#   --spontaneous-sigkill   -> marker, then self SIGKILL via OS.kill(own pid)
const MARKER := "SPONTANEOUS_CRASH_PROBE: expected signature"

func _initialize() -> void:
	print(MARKER)
	var user_args := OS.get_cmdline_user_args()
	if "--spontaneous-crash" in user_args:
		OS.crash("r60 spontaneous crash probe")
	elif "--spontaneous-sigkill" in user_args:
		OS.kill(OS.get_process_id())
	quit(1)
