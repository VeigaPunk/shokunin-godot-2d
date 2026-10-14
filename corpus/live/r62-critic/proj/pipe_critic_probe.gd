extends SceneTree

# r62-critic adversarial pipe-attribution probe (scratch-only; not a tracked
# fixture). The child prints its pid and (unless --no-signature) the marker,
# optionally spawns OS descendants via OS.create_process with various fd
# dispositions, optionally hangs via --hang=<s>, then exits 0.

const MARKER := "PIPE_CRITIC: expected signature"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var out_dir := ""
	var mode := ""
	var arg := ""
	var hang := 0.0
	var signature := true
	for a in user_args:
		if a.begins_with("--out-dir="):
			out_dir = a.trim_prefix("--out-dir=")
		elif a.begins_with("--hang="):
			hang = float(a.trim_prefix("--hang="))
		elif a == "--no-signature":
			signature = false
		elif a == "--spawn-hold-write":
			mode = "hold_write"
		elif a == "--spawn-early-write":
			mode = "early_write"
		elif a.begins_with("--spawn-hold="):
			mode = "hold"
			arg = a.trim_prefix("--spawn-hold=")
		elif a.begins_with("--spawn-detach="):
			mode = "detach"
			arg = a.trim_prefix("--spawn-detach=")
		elif a.begins_with("--spawn-stderr-only="):
			mode = "stderr_only"
			arg = a.trim_prefix("--spawn-stderr-only=")
		elif a.begins_with("--spawn-stdout-only="):
			mode = "stdout_only"
			arg = a.trim_prefix("--spawn-stdout-only=")
		elif a.begins_with("--spawn-spoof="):
			mode = "spoof"
			arg = a.trim_prefix("--spawn-spoof=")
		elif a.begins_with("--spawn-pair="):
			mode = "pair"
			arg = a.trim_prefix("--spawn-pair=")
		elif a.begins_with("--spawn-flood="):
			mode = "flood"
			arg = a.trim_prefix("--spawn-flood=")
	print("PIPE_CRITIC godot_pid=", OS.get_process_id())
	if signature:
		print(MARKER)
	var spawned: Array = []
	match mode:
		"hold":
			# Holds BOTH inherited pipes silently for <arg>s, then lands a file.
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"sleep " + arg + "; echo landed > " + out_dir + "/hold.outlived"])))
		"hold_write":
			# Writes one line into the shared stdout pipe ~1s after spawn (the
			# child exits ~0.4s), holds the pipe to ~5s, then lands a file.
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"sleep 1.0; echo DESC_POST_PARENT_WRITE; sleep 4.0; echo landed > " + out_dir + "/hold_write.outlived"])))
		"early_write":
			# SABOTAGE: descendant writes the same post-exit marker ~0.05s after
			# spawn — BEFORE the child's ~0.4s exit — then holds 5s. Any meta
			# gating only on marker presence still passes although the captured
			# line is NOT post-parent-death evidence.
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"echo DESC_POST_PARENT_WRITE; sleep 5"])))
		"detach":
			# All stdio detached at exec: pipes get EOF at the child's exit, yet
			# the descendant outlives both child and return, then lands a file.
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"exec sh -c 'sleep " + arg + "; echo landed > " + out_dir + "/detach.outlived' </dev/null >/dev/null 2>&1"])))
		"stderr_only":
			# Descendant closes fd1 at exec; only stderr pipe stays held.
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"exec sleep " + arg + " 1>&-"])))
		"stdout_only":
			# Descendant closes fd2 at exec; only stdout pipe stays held.
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"exec sleep " + arg + " 2>&-"])))
		"spoof":
			# Descendant WRITES THE SIGNATURE LINE into the shared pipe ~0.8s
			# after spawn — i.e. after the child's ~0.4s exit — then holds the
			# pipe for <arg> more seconds. Combined with --no-signature this
			# produces captured output containing the marker although the child
			# never emitted it.
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"sleep 0.8; echo '" + MARKER + "'; sleep " + arg])))
		"pair":
			# Two pipe-holding descendants with different lifetimes "S1,S2":
			# EOF arrives only when the LAST holder exits.
			var parts := arg.split(",")
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"sleep " + parts[0]])))
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"sleep " + parts[1]])))
		"flood":
			# Descendant floods >64KiB into the shared pipe AFTER the child's
			# exit, then holds the pipe <arg>s.
			spawned.append(OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"i=0; while [ $i -lt 9000 ]; do echo DESC_FLOOD_$i; i=$((i+1)); done; sleep " + arg])))
	for p in spawned:
		if p > 0:
			print("PIPE_CRITIC spawned_pid=", p)
	if hang > 0.0:
		await create_timer(hang).timeout
	quit(0)
