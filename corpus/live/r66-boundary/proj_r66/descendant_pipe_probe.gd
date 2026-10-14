extends SceneTree

# r66-boundary SCRATCH-ONLY surface fixture. Byte-identical stock semantics
# plus additive edge arms. The tracked file
# corpus/fixtures/descendant_pipe_probe.gd is NOT touched; this copy lives
# under corpus/live/r66-boundary/proj_r66/ only. Stock arms preserved
# verbatim for control reruns; the r65-boundary edge arms carried forward
# where the r66 surface needs them.
#
# Arm map (post-death arms reuse the stock reparenting gate — the write is
# provably post-parent-exit; PRE-death arms spawn the descendant first and
# use a fixed offset):
#   (none)                          child prints MARKER, exits 0.
#   --spawn-hold / --spawn-detach   stock r62 arms (pipe-hold / fd-detach).
#   --spawn-forge-release/-hold     stock r63 arms (withheld signature,
#                                   descendant post-death forges MARKER).
#   --spawn-errforge-release/-hold  stock r65 arms (genuine signature, post-
#                                   death un-allowlisted ERROR: line).
#   --emit-errforge                 stock r65 genuine-error control.
#   --spawn-errforge-stderr-release r65: forged error on fd 2 post-death.
#   --spawn-errforge-newlinesplit   r65: "ERR\n" then "OR: ..." post-death —
#                                   token split ACROSS a newline; no captured
#                                   line contains "ERROR:".
#   --spawn-errforge-split          r65: "ERR" then "OR: ..." no newline —
#                                   reassembles contiguously, detected.
#   --spawn-errforge-allowlisted    r65: post-death echo of
#                                   save_corrupt_negative's allowlisted line.
#   --spawn-genuine-error           r65: child printerr's ERR_LINE pre-exit.
#
# r66 arms (rejection-clause surface map):
#   --spawn-errforge-script         post-death "SCRIPT ERROR: FORGED_..." —
#                                   the SCRIPT ERROR: blob veto.
#   --spawn-errforge-parse          post-death "Parse Error: FORGED_..." —
#                                   the Parse Error: blob veto.
#   --spawn-errforge-triple         post-death unrelated ERROR: + SCRIPT
#                                   ERROR: + Parse Error: lines — one record
#                                   tripping all three error clauses.
#   --spawn-errforge-scriptsplit    post-death "SCRIPT ERR\n" then "OR: ..." —
#                                   newline-split evades the BLOB clause too
#                                   (substring is contiguous nowhere).
#   --spawn-errforge-bulk-straddle  post-death 65535 pad bytes then the ERROR
#                                   token + newline: "ERROR:" straddles the
#                                   64KiB pipe-buffer offset in-stream.
#   --spawn-errforge-bulk-embed     post-death ~150KiB clean burst with the
#                                   ERROR line embedded mid-burst (~70KiB).
#   --spawn-errforge-bulk-nlsplit   pad to 65534 then "ERR\n" then "OR: ...":
#                                   the newline split itself straddles the
#                                   64KiB boundary — evasion is position-free.
#   --spawn-errforge-dualline       post-death ONE line carrying BOTH the
#                                   signature substring and an ERROR: token —
#                                   the line that satisfies the signature is
#                                   the line that rejects.
#   --spawn-errforge-dualline-withheld  child WITHHOLDS the signature; the
#                                   descendant's single dual-substring line
#                                   is the ONLY signature occurrence — the
#                                   forged signature carries its own veto.
#   --spawn-errforge-negrow         child exits 2 printing ONLY a banner (no
#                                   evidence); descendant post-death echoes
#                                   save_corrupt_negative's signature line —
#                                   which IS an allowlisted error: negative-
#                                   row evidence fabricated wholesale.
#   --spawn-errforge-stderr-noise   post-death non-ERROR chatter on fd 2:
#                                   classify_streams rejects (any unexpected
#                                   stderr line) while classify_process
#                                   accepts (no "ERROR:" substring) — the
#                                   reverse asymmetry direction.
#   --spawn-errforge-splice-self    child printraw tail ending in "ERROR"
#                                   unterminated on stdout; descendant head
#                                   ": PHANTOM ..." on stdout — in-pipe
#                                   contiguity fabricates an ERROR: line
#                                   NEITHER process wrote as a line.
#   --spawn-errforge-splice-xstream same tail on stdout; descendant head on
#                                   STDERR — the stdout+stderr CONCAT fabricates
#                                   the reject line across the merge seam.
#   --spawn-errforge-comma          post-death echo of animation_stuck's
#                                   ,-prefix entry + suffix (absorbed).
#   --spawn-errforge-comma-escape   same + appended " ERROR:" (count==2 gate
#                                   breaks the allowlist -> rejects).
#   --spawn-errforge-chain          post-death echo of a chain-incomplete
#                                   structured-form line (absorbed).
#   --spawn-errforge-chain-escape   chain-shaped but scene=SceneC -> the
#                                   structured match fails -> rejects.
#   --spawn-errforge-allowed-script child clean; descendant post-death echoes
#                                   an EXACT-allowlisted plain error line AND
#                                   a SCRIPT ERROR: line that is itself an
#                                   allowlist entry: the allowlist absorbs
#                                   both from clause 1, the blob veto still
#                                   rejects — allowlist preempts ONLY the
#                                   unrelated_errors conjunct.

const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"
const FORGE_PPID_WRITE := "DESCENDANT_PIPE_FORGE write_ppid="
const ERRFORGE_PPID_WRITE := "DESCENDANT_PIPE_ERRFORGE write_ppid="
const ERRFORGE_ERROR_BODY := "DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
const ERRFORGE_ERROR := "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
const ERR_LINE := "ERROR: FORGED_DESCENDANT_ERROR injected diagnostic"
const ERR_PPID := "DESCENDANT_PIPE_ERRFORGE write_ppid="
const SAVE_SIG := "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR"
const SCRIPT_LINE := "SCRIPT ERROR: FORGED_DESCENDANT_ERROR injected script diagnostic"
const PARSE_LINE := "Parse Error: FORGED_DESCENDANT_ERROR injected parse diagnostic"
const COMMA_LINE := "ERROR: ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance, got 999.0"
const CHAIN_LINE := "ERROR: chain incomplete collections=7 scene=SceneB:<Node#4242> old_alive=false forged=1"
const CHAIN_ESCAPE := "ERROR: chain incomplete collections=7 scene=SceneC:<Node#4242> old_alive=false forged=1"
const NOISE_LINE := "INNOCENT_DESCENDANT_CHATTER not an error token"
const SPLICE_TAIL := "DESCENDANT_PIPE_SPLICE_TAIL unterminated ending in ERROR"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var forge_hold := "--spawn-forge-hold" in user_args
	var forge_release := "--spawn-forge-release" in user_args
	var errforge_hold := "--spawn-errforge-hold" in user_args
	var errforge_release := "--spawn-errforge-release" in user_args
	var emit_errforge := "--emit-errforge" in user_args
	var err_stderr := "--spawn-errforge-stderr-release" in user_args
	var err_split := "--spawn-errforge-split" in user_args
	var err_newlinesplit := "--spawn-errforge-newlinesplit" in user_args
	var err_allowlisted := "--spawn-errforge-allowlisted" in user_args
	var genuine_error := "--spawn-genuine-error" in user_args
	var err_script := "--spawn-errforge-script" in user_args
	var err_parse := "--spawn-errforge-parse" in user_args
	var err_triple := "--spawn-errforge-triple" in user_args
	var err_scriptsplit := "--spawn-errforge-scriptsplit" in user_args
	var err_bulk_straddle := "--spawn-errforge-bulk-straddle" in user_args
	var err_bulk_embed := "--spawn-errforge-bulk-embed" in user_args
	var err_bulk_nlsplit := "--spawn-errforge-bulk-nlsplit" in user_args
	var err_dualline := "--spawn-errforge-dualline" in user_args
	var err_dualline_wh := "--spawn-errforge-dualline-withheld" in user_args
	var err_negrow := "--spawn-errforge-negrow" in user_args
	var err_noise := "--spawn-errforge-stderr-noise" in user_args
	var err_splice_self := "--spawn-errforge-splice-self" in user_args
	var err_splice_x := "--spawn-errforge-splice-xstream" in user_args
	var err_comma := "--spawn-errforge-comma" in user_args
	var err_comma_esc := "--spawn-errforge-comma-escape" in user_args
	var err_chain := "--spawn-errforge-chain" in user_args
	var err_chain_esc := "--spawn-errforge-chain-escape" in user_args
	var err_allowed_script := "--spawn-errforge-allowed-script" in user_args
	var forge_stderr := "--spawn-forge-stderr" in user_args
	var godot_pid := OS.get_process_id()
	# Stock reparenting gate: polls /proc/self/stat until ppid flips off this
	# process's pid — the write that follows is provably post-exit.
	var gate := "while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(godot_pid) + "\" ]; do sleep 0.05; done; "

	if forge_hold or forge_release or err_dualline_wh or forge_stderr:
		print("DESCENDANT_PIPE_FORGE child_signature=withheld")
	else:
		print(MARKER)
	if errforge_hold or errforge_release:
		print("DESCENDANT_PIPE_ERRFORGE child=clean signature=genuine error=descendant_post_exit")
	elif emit_errforge:
		print("DESCENDANT_PIPE_ERRFORGE child_error=genuine_pre_exit")
		push_error(ERRFORGE_ERROR_BODY)
	elif err_negrow:
		print("DESCENDANT_PIPE_NEGROW child_exits=2 evidence=withheld")
	print("DESCENDANT_PIPE godot_pid=", godot_pid)

	var spawned := -1
	if "--spawn-hold" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + str(godot_pid) + "\" ]; do sleep 0.05; done; echo " + POST_EXIT_WRITE + "; sleep 6"]))
	elif "--spawn-detach" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec sh -c 'sleep 8' </dev/null >/dev/null 2>&1"]))
	elif forge_hold or forge_release:
		var tail := "; sleep 6" if forge_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo " + MARKER + "; echo " + FORGE_PPID_WRITE + "$pp" + tail]))
	elif errforge_hold or errforge_release:
		var err_tail := "; sleep 6" if errforge_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo " + ERRFORGE_ERROR + "; echo " + ERRFORGE_PPID_WRITE + "$pp" + err_tail]))
	elif err_stderr:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + ERR_LINE + "' >&2; echo " + ERR_PPID + "$pp"]))
	elif err_split:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf 'ERR'; sleep 0.05; printf 'OR: FORGED split-token diagnostic\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_newlinesplit:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf 'ERR\\n'; sleep 0.05; printf 'OR: FORGED_DESCENDANT_ERROR newline-split diagnostic\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_allowlisted:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + SAVE_SIG + "'; echo " + ERR_PPID + "$pp"]))
	elif err_script:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + SCRIPT_LINE + "'; echo " + ERR_PPID + "$pp"]))
	elif err_parse:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + PARSE_LINE + "'; echo " + ERR_PPID + "$pp"]))
	elif err_triple:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + ERR_LINE + "'; echo '" + SCRIPT_LINE + "'; echo '" + PARSE_LINE + "'; echo " + ERR_PPID + "$pp"]))
	elif err_scriptsplit:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf 'SCRIPT ERR\\n'; sleep 0.05; printf 'OR: FORGED_DESCENDANT_ERROR script-split diagnostic\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_bulk_straddle:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "head -c 65535 /dev/zero | tr '\\0' 'A'; printf '" + ERR_LINE + "\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_bulk_embed:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "head -c 70000 /dev/zero | tr '\\0' 'A'; printf '\\n" + ERR_LINE + "\\n'; head -c 80000 /dev/zero | tr '\\0' 'B'; printf '\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_bulk_nlsplit:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "head -c 65534 /dev/zero | tr '\\0' 'A'; printf 'ERR\\n'; sleep 0.05; printf 'OR: FORGED_DESCENDANT_ERROR boundary-split diagnostic\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_dualline:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf '" + MARKER + " " + ERR_LINE + "\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_dualline_wh:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf '" + MARKER + " " + ERR_LINE + "\\n'; echo " + FORGE_PPID_WRITE + "$pp; echo " + ERR_PPID + "$pp"]))
	elif err_negrow:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + SAVE_SIG + "'; echo " + ERR_PPID + "$pp"]))
	elif err_noise:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + NOISE_LINE + "' >&2; echo " + ERR_PPID + "$pp"]))
	elif err_splice_self:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf ': PHANTOM_SPLICE line fabricated intra-pipe\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_splice_x:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf ': PHANTOM_XSPLICE line fabricated across merge\\n' >&2; echo " + ERR_PPID + "$pp >&2"]))
	elif err_comma:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + COMMA_LINE + "'; echo " + ERR_PPID + "$pp"]))
	elif err_comma_esc:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "printf '" + COMMA_LINE + " ERROR: second token\\n'; echo " + ERR_PPID + "$pp"]))
	elif err_chain:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + CHAIN_LINE + "'; echo " + ERR_PPID + "$pp"]))
	elif err_chain_esc:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + CHAIN_ESCAPE + "'; echo " + ERR_PPID + "$pp"]))
	elif err_allowed_script:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo '" + SAVE_SIG + "'; echo '" + SCRIPT_LINE + "'; echo " + ERR_PPID + "$pp"]))
	elif forge_stderr:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			gate + "echo " + MARKER + " >&2; echo " + FORGE_PPID_WRITE + "$pp >&2"]))
	elif genuine_error:
		printerr(ERR_LINE)
		print("DESCENDANT_PIPE_GENUINE_ERROR emitted_by=child")
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	if err_splice_self or err_splice_x:
		printraw(SPLICE_TAIL)
	if err_negrow:
		quit(2)
		return
	quit(0)
