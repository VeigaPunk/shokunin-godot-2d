extends SceneTree

# r64 critic mutant probe: forged signatures written DURING the child's life.
# The while-live gate claims to discriminate "forged post-death signatures"
# from "genuine child signatures". These arms keep the child provably alive
# while a pipe-inheriting descendant writes the very same expected marker, so
# the gate observes the forged bytes with the child alive -> the gate's
# alive-at-observation test cannot tell descendant bytes from child bytes.
#   --forge-during-life  : child withholds MARKER, stays alive ~1.2s via
#                          OS.delay_msec (a foreground wait); descendant writes
#                          MARKER at +0.15s then exits -> forged signature lands
#                          squarely inside the child's live window.
#   --forge-early        : child withholds MARKER and exits at once; descendant
#                          writes MARKER immediately with NO ppid gate -> the
#                          forged write races the child's own exit: observed
#                          pre- or post-death depending on scheduling.
#   --forge-during-hold  : like during-life but the descendant holds both pipes
#                          ~5s after writing -> marker accepted-live AND the
#                          run still hits the bound on held pipes.
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var during_life := "--forge-during-life" in user_args
	var early := "--forge-early" in user_args
	var during_hold := "--forge-during-hold" in user_args
	print("WLG_CRITIC_FORGE child_signature=withheld")
	print("WLG_CRITIC godot_pid=", OS.get_process_id())
	var spawned := -1
	if during_life:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 0.15; echo " + MARKER + "; echo WLG_CRITIC_FORGE during_life_ppid=$PPID; sleep 0.2"]))
	elif during_hold:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"sleep 0.15; echo " + MARKER + "; echo WLG_CRITIC_FORGE during_hold_ppid=$PPID; sleep 5"]))
	elif early:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"echo " + MARKER + "; echo WLG_CRITIC_FORGE early_ppid=$PPID"]))
	elif "--forge-fastpost" in user_args:
		# Same reparenting gate as the tracked fixture but a BUSY ppid poll:
		# the forged write lands microseconds after the child's death instead
		# of ~30-50ms, testing whether stale-ordering gates can be fooled.
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(OS.get_process_id()) + "\" ]; do :; done; echo " + MARKER + "; echo WLG_CRITIC_FORGE fastpost_ppid=$pp"]))
	if spawned > 0:
		print("WLG_CRITIC spawned_pid=", spawned)
	if during_life or during_hold:
		# Foreground wait: the child is provably alive across the forged write.
		OS.delay_msec(1200)
	quit(0)
