extends SceneTree

# r63-critic adversarial forged-signature probe (scratch-only; NOT a tracked
# fixture). Replicates the r63 author's --spawn-forge-* mechanism and mutates
# it to attack the claim that the forged-signature record is distinguishable
# from a genuine child signature ONLY via child_exit_at_timeout/timed_out.
#
# The child prints a banner line (or the real MARKER), its pid, the spawned
# descendant pid, then exits --exit-code=N (default 0). The descendant is an
# /usr/bin/sh -c inheriting both captured pipes; arm selected by flag:
#
#   --forge-release        gated on /proc/self/stat ppid flip off godot_pid:
#                          echo MARKER; echo "write_ppid=$pp"; exit
#                          (author's arm re-derived independently)
#   --forge-release-stderr gated; writes MARKER to fd2 (stderr), ppid line fd1
#   --forge-ungated-honest NO gate: writes MARKER + real $pp ~0.05s post-spawn
#                          (pre-death; $pp == godot_pid, record self-disproves)
#   --forge-lying-ppid     NO gate: writes MARKER + hardcoded write_ppid=1
#                          ~0.05s post-spawn — pre-death forgery whose printed
#                          provenance claims post-orphan; attacks the
#                          self-reported write_ppid discrimination
#   --forge-hold=S         gated; writes MARKER + write_ppid, then holds S s
#   --genuine-hold=S       child prints MARKER itself; gated descendant echoes
#                          ONLY the write_ppid line and holds S s — same
#                          timed_out/child_exit/marker/inner AND same
#                          write_ppid!=godot_pid as the forged-hold arm
#   --double-forge-hold=S  child prints MARKER itself AND gated descendant
#                          also writes MARKER + write_ppid + holds S — the
#                          "provably descendant-authored" confusion case
#   --forge-livechild      child HANGS (--hang=30); UNGATED descendant writes
#                          MARKER at +0.8s and holds 5s — attacks whether
#                          child_exit_at_timeout can be forged (kernel poll)
#   --forge-midhold=1.2    gated; writes MARKER+write_ppid then holds only
#                          1.2s — release tracked to EOF well inside bound
#   --forge-stderr-hold=S  gated; MARKER to stderr only, ppid line stdout,
#                          holds S — stream-blindness under the TIMEOUT path
#
# Every gated arm polls /proc/self/stat field 4 (ppid) until it differs from
# this process's pid — kernel reparenting is immediate at the parent's exit,
# so the write is provably post-death at the source (same gate the author
# uses; independent derivation).

const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const PPID_LINE := "DESCENDANT_PIPE_FORGE write_ppid="
const NEG_SIG := "ERROR: SPOOFED NEGATIVE DIAGNOSTIC forged by descendant"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var mode := ""
	var arg := ""
	var hang := 0.0
	var exit_code := 0
	var withhold := true
	for a in user_args:
		if a.begins_with("--hang="):
			hang = float(a.trim_prefix("--hang="))
		elif a.begins_with("--exit-code="):
			exit_code = int(a.trim_prefix("--exit-code="))
		elif a == "--child-prints-marker":
			withhold = false
		elif a.begins_with("--forge-hold="):
			mode = "forge_hold"; arg = a.trim_prefix("--forge-hold=")
		elif a.begins_with("--genuine-hold="):
			mode = "genuine_hold"; arg = a.trim_prefix("--genuine-hold=")
		elif a.begins_with("--double-forge-hold="):
			mode = "double_forge_hold"; arg = a.trim_prefix("--double-forge-hold=")
		elif a.begins_with("--forge-midhold="):
			mode = "forge_midhold"; arg = a.trim_prefix("--forge-midhold=")
		elif a.begins_with("--forge-stderr-hold="):
			mode = "forge_stderr_hold"; arg = a.trim_prefix("--forge-stderr-hold=")
		elif a == "--forge-release":
			mode = "forge_release"
		elif a == "--forge-release-stderr":
			mode = "forge_release_stderr"
		elif a == "--forge-ungated-honest":
			mode = "forge_ungated_honest"
		elif a == "--forge-lying-ppid":
			mode = "forge_lying_ppid"
		elif a == "--forge-livechild":
			mode = "forge_livechild"
		elif a == "--forge-neg-exit":
			mode = "forge_neg_exit"; exit_code = 2
	var gate := "while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" \
		+ str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; "
	if withhold:
		print("SIG_SPOOF_PROBE child_signature=withheld")
	else:
		print(MARKER)
	print("SIG_SPOOF godot_pid=", OS.get_process_id())
	var spawned := -1
	match mode:
		"forge_release":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				gate + "echo '" + MARKER + "'; echo " + PPID_LINE + "$pp"]))
		"forge_release_stderr":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				gate + "echo '" + MARKER + "' >&2; echo " + PPID_LINE + "$pp"]))
		"forge_ungated_honest":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"read -r _ _ _ pp _ < /proc/self/stat; echo '" + MARKER
				+ "'; echo " + PPID_LINE + "$pp"]))
		"forge_lying_ppid":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"echo '" + MARKER + "'; echo " + PPID_LINE + "1"]))
		"forge_hold":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				gate + "echo '" + MARKER + "'; echo " + PPID_LINE + "$pp; sleep " + arg]))
		"genuine_hold":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				gate + "echo " + PPID_LINE + "$pp; sleep " + arg]))
		"double_forge_hold":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				gate + "echo '" + MARKER + "'; echo " + PPID_LINE + "$pp; sleep " + arg]))
		"forge_livechild":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				"sleep 0.8; echo '" + MARKER + "'; echo " + PPID_LINE
				+ "livechild; sleep 5"]))
		"forge_midhold":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				gate + "echo '" + MARKER + "'; echo " + PPID_LINE + "$pp; sleep " + arg]))
		"forge_stderr_hold":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				gate + "echo '" + MARKER + "' >&2; echo " + PPID_LINE + "$pp; sleep " + arg]))
		"forge_neg_exit":
			spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
				gate + "echo '" + NEG_SIG + "'; echo " + PPID_LINE + "$pp"]))
	if spawned > 0:
		print("SIG_SPOOF spawned_pid=", spawned)
	if hang > 0.0:
		await create_timer(hang).timeout
	quit(exit_code)
