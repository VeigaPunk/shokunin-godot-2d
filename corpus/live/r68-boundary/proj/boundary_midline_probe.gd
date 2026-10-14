extends SceneTree

# r68 boundary scratch fixture — midlineforge mechanism edges + drain/timeout.
# Same shape as the tracked descendant_pipe_probe.gd midline arm (halved
# signature, descendant inherits both captured pipes), parameterized:
#   --off=N        descendant writes ERR once at N ms after spawn (may be
#                  negative -> immediate write, races the head print)
#   --pre-head     child delays 150ms BEFORE printraw(head); descendant writes
#                  at ~0ms -> lands provably before the gap opens
#   --dup=A,B      descendant writes the ERR line at both offsets A,B ms
#   --jitter=B,W   descendant writes once at B + $RANDOM%W ms (fuzzy offset)
#   --gap=G        signature gap in ms (default 200)
#   --burst        descendant writes ERR at 20,60,100,140,180,220,260,300,340ms
#   --hold-flood=S bound probe: child exits clean after the gap; descendant
#                  floods stderr with numbered lines T-FLOOD-i every 20ms and
#                  holds both pipes ~S seconds -> TIMEOUT truncation probe
#   --hold-seam    child leaves unterminated stdout tail "... ends in ERROR";
#                  descendant (reparenting-gated, holding pipes ~5s) writes
#                  ": TRUNC phantom fabricated line" to stderr on a schedule
#                  -> TIMEOUT-path seam fabrication probe
#   --sched=T      ms delay for the hold-seam stderr write (default 2500)
const HEAD := "BOUNDARY_MIDLINE: expected "
const TAIL := "signature"
const ERR := "ERROR: BOUNDARY_MIDLINE forged splice"
const PPID := "BOUNDARY_MIDLINE write_ppid="

static func _opt(args: PackedStringArray, name: String, dflt: String) -> String:
	for a in args:
		if a.begins_with(name + "="):
			return a.split("=", true, 2)[1]
	return dflt

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var off := int(_opt(user_args, "--off", "80"))
	var gap := int(_opt(user_args, "--gap", "200"))
	var pre_head := "--pre-head" in user_args
	var burst := "--burst" in user_args
	var hold_flood := "--hold-flood" in user_args or _opt(user_args, "--hold-flood", "") != ""
	var hold_seam := "--hold-seam" in user_args
	var dup := _opt(user_args, "--dup", "")
	var jit := _opt(user_args, "--jitter", "")
	var sched := int(_opt(user_args, "--sched", "2500"))
	var payload := _opt(user_args, "--payload", "")
	var flood_s := int(_opt(user_args, "--hold-flood", "5"))
	print("BOUNDARY_MIDLINE godot_pid=", OS.get_process_id())
	var spawned := -1
	var desc_cmd := ""
	if pre_head:
		desc_cmd = "read -r _ _ _ pp _ < /proc/self/stat; printf '" + ERR + "\\n'; echo " + PPID + "$pp"
	elif dup != "":
		var parts := dup.split(",")
		desc_cmd = ("sleep 0." + parts[0].pad_zeros(3) + "; printf '" + ERR + "\\n'; "
			+ "sleep 0." + str(maxi(1, int(parts[1]) - int(parts[0]))).pad_zeros(3)
			+ "; printf '" + ERR + "\\n'; read -r _ _ _ pp _ < /proc/self/stat; echo " + PPID + "$pp")
	elif jit != "":
		var jp := jit.split(",")
		desc_cmd = ("sleep 0.$(printf %03d $(( " + jp[0] + " + RANDOM % " + jp[1] + " ))); printf '" + ERR
			+ "\\n'; read -r _ _ _ pp _ < /proc/self/stat; echo " + PPID + "$pp")
	elif burst:
		var seq := ""
		var prev := 0
		for t in [20, 60, 100, 140, 180, 220, 260, 300, 340]:
			seq += ("sleep 0." + str(t - prev).pad_zeros(3) + "; printf '"
					+ ERR + " t=" + str(t) + "\\n'; ")
			prev = t
		desc_cmd = seq + "read -r _ _ _ pp _ < /proc/self/stat; echo " + PPID + "$pp"
	elif hold_flood:
		# child exits after the normal gap; descendant floods stderr and holds
		# both pipes so communicate(timeout) must TIMEOUT on pipe EOF.
		desc_cmd = ("i=0; while [ $i -lt " + str(flood_s * 50) + " ]; do echo T-FLOOD-$i >&2; i=$((i+1)); sleep 0.02; done")
	elif hold_seam:
		var reparent_gate := ("while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \""
			+ str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; ")
		desc_cmd = (reparent_gate + "sleep " + str(sched / 1000.0)
			+ "; printf ': TRUNC phantom fabricated line\\n' >&2; echo BOUNDARY_HELD write_ppid=$pp >&2; sleep 5")
	elif payload != "":
		var s2 := "sleep 0." + str(maxi(0, off)).pad_zeros(3) + "; "
		desc_cmd = (s2 + "read -r _ _ _ pp _ < /proc/self/stat; printf '"
			+ payload.replace("~", "\\n") + "'; echo " + PPID + "$pp")
	else:
		var s := "sleep 0." + str(maxi(0, off)).pad_zeros(3) + "; "
		desc_cmd = (s + "read -r _ _ _ pp _ < /proc/self/stat; printf '" + ERR
			+ "\\n'; echo " + PPID + "$pp")
	spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c", desc_cmd]))
	if spawned > 0:
		print("BOUNDARY_MIDLINE spawned_pid=", spawned)
	if pre_head:
		OS.delay_msec(150)
	if hold_seam:
		# stdout tail is deliberately left unterminated so the runner's
		# stdout+stderr concat fabricates the phantom line under timeout
		# truncation; the child then exits; pipes stay descendant-held.
		printraw("BOUNDARY trunc tail ends in ERROR")
		quit(0)
		return
	printraw(HEAD)
	OS.delay_msec(gap)
	print(TAIL)
	quit(0)
