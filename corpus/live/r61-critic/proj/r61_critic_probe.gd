extends SceneTree

# r61 CRITIC sabotage battery — scratch only, never tracked.
# Attacks the planned crash row (expected_exit=-6 + ERROR-marker allowlist):
# forgeries that reach -6 without a genuine spontaneous OS.crash abort,
# marker-order mutants, unrelated-ERROR injections, and alternate signal routes.
const MARKER := "R61_CRITIC_SPONTANEOUS: expected signature"
const CRASH_MSG := "r61 critic abort"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var pid := OS.get_process_id()
	# arm that crashes BEFORE printing the marker (flush/order sabotage)
	if "--crash-before-marker" in user_args:
		OS.crash(CRASH_MSG)
	print(MARKER)
	if "--os-crash" in user_args:
		OS.crash(CRASH_MSG)
	elif "--crash-diff-msg" in user_args:
		OS.crash("a different spontaneous abort")
	elif "--ext-abrt" in user_args:
		# externally delivered SIGABRT, no ERROR line emitted at all
		OS.create_process("/usr/bin/kill", ["-6", str(pid)])
		await create_timer(3.0).timeout
	elif "--ext-abrt-forged-marker" in user_args:
		# forge the exact allowlisted ERROR text, then external SIGABRT
		printerr("ERROR: " + CRASH_MSG)
		OS.create_process("/usr/bin/kill", ["-6", str(pid)])
		await create_timer(3.0).timeout
	elif "--ext-abrt-extra-error" in user_args:
		printerr("ERROR: unrelated injected diagnostic")
		OS.create_process("/usr/bin/kill", ["-6", str(pid)])
		await create_timer(3.0).timeout
	elif "--ext-ill" in user_args:
		# external SIGILL — same signal OS.crash raises internally
		OS.create_process("/usr/bin/kill", ["-4", str(pid)])
		await create_timer(3.0).timeout
	elif "--ext-segv" in user_args:
		OS.create_process("/usr/bin/kill", ["-11", str(pid)])
		await create_timer(3.0).timeout
	elif "--ext-kill9" in user_args:
		# external SIGKILL — forges the self-OS.kill arm's -9 shape
		OS.create_process("/usr/bin/kill", ["-9", str(pid)])
		await create_timer(3.0).timeout
	elif "--ext-term" in user_args:
		# harness-style SIGTERM (r21 shape) against the -6 row
		OS.create_process("/usr/bin/kill", ["-15", str(pid)])
		await create_timer(3.0).timeout
	elif "--self-kill" in user_args:
		OS.kill(pid)
	elif "--exit-134" in user_args:
		quit(134)
	elif "--forge-prefix" in user_args:
		# a printerr that EXTENDS the allowlisted text: harmless under exact
		# match, blessed by a comma-prefix allowlist entry
		printerr("ERROR: " + CRASH_MSG + ", EXTRA_UNRELATED_CONTENT")
		OS.crash(CRASH_MSG)
	elif "--printerr-clean" in user_args:
		printerr("ERROR: " + CRASH_MSG)
		quit(0)
	elif "--assert-fail" in user_args:
		assert(false)
	elif "--stack-overflow" in user_args:
		_recurse()
	quit(1)

func _recurse() -> void:
	_recurse()
