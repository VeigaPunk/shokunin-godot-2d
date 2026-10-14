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
#   --spawn-errforge-release / --spawn-errforge-hold (r65 additions,
#                      the forged-REJECTION dual) -> this process runs
#                      CLEAN: the genuine signature is printed while alive
#                      and it exits 0; the reparenting-gated descendant
#                      echoes an UN-ALLOWLISTED "ERROR:"-class marker
#                      (ERRFORGE_ERROR, byte-identical to the genuine arm's
#                      push_error text) and DESCENDANT_PIPE_ERRFORGE
#                      write_ppid=<ppid> post-exit. -release exits right
#                      after writing (clean exit-0 + signature-present
#                      record that FAILs only on the descendant's line);
#                      -hold keeps the pipes ~6s (the forged error lands
#                      inside the TIMEOUT record and the still-alive
#                      descendant's /proc ppid corroborates write_ppid).
#                      Meta-driven via probe_descendant_error_spoof, not a
#                      CASES arm: an expected-FAIL record is inexpressible
#                      in the all-PASS battery (r62 hold-arm precedent).
#   --emit-errforge    -> genuine-error control: this process emits the
#                      identical ERROR: marker bytes itself, pre-death, via
#                      push_error (the engine stderr path), then exits 0 —
#                      child-authored error, no descendant.
#   r66 rejection-clause SURFACE arms (meta-driven via
#   probe_error_clause_surface, never CASES tuples — expected-FAIL/evading
#   records are inexpressible in the all-PASS battery, r62 precedent):
#   --spawn-allowforge  -> child runs CLEAN (genuine signature, exit 0);
#                      reparenting-gated descendant echoes save_corrupt_
#                      negative's byte-exact ALLOWLISTED error string
#                      post-death + ALLOWFORGE write_ppid=<ppid> — the
#                      forged error is verdict-inert iff classified under
#                      that allowlist entry (the preemptor row).
#   --spawn-splitforge  -> child runs CLEAN; reparenting-gated descendant
#                      writes "ERR\n" then "OR: DESCENDANT_PIPE_SPLITFORGE
#                      newline-split diagnostic\n" post-death + write_ppid —
#                      the ERROR: token is split across a newline, so no
#                      captured LINE contains it: line-local-scan evasion.
#   --spawn-seamforge   -> child runs CLEAN; reparenting-gated descendant
#                      leaves "DESCENDANT_PIPE_SEAMFORGE tail ends in ERROR"
#                      as the UNTERMINATED last bytes of stdout and ": ...
#                      phantom fabricated line" as the first bytes of
#                      stderr post-death — the runner's stdout+stderr concat
#                      FABRICATES a reject line present in neither stream.
#   --spawn-midlineforge -> descendant is spawned while the child is ALIVE
#                      (write_ppid==godot_pid); the child
#                      emits the signature as two printraw halves with a
#                      200ms gap after all bookkeeping lines — the splice
#                      lands mid-line: the ERROR: line is fabricated AND
#                      the signature substring is destroyed (dual-clause
#                      corruption; a post-death gate cannot produce it).
#                      The descendant write offset into the gap is
#                      parameterized: --midline-offset-ms=N (default 80,
#                      the r66 point sample). r68 measured ladder: the
#                      fabrication lands iff the write reaches the pipe
#                      between the head and tail flushes — offsets below
#                      the ~200ms gap edge splice; at/over it they miss
#                      (signature survives; error lands on its own line).
const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
const MARKER_SPLICE_HEAD := "DESCENDANT_PIPE_PROBE: expected "
const MARKER_SPLICE_TAIL := "signature"
const POST_EXIT_WRITE := "DESCENDANT_PIPE_AFTER_EXIT_WRITE"
const FORGE_PPID_WRITE := "DESCENDANT_PIPE_FORGE write_ppid="
const ERRFORGE_PPID_WRITE := "DESCENDANT_PIPE_ERRFORGE write_ppid="
const ERRFORGE_ERROR_BODY := "DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
const ERRFORGE_ERROR := "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
const ALLOWFORGE_ERROR := "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR"
const ALLOWFORGE_PPID_WRITE := "DESCENDANT_PIPE_ALLOWFORGE write_ppid="
const SPLITFORGE_PPID_WRITE := "DESCENDANT_PIPE_SPLITFORGE write_ppid="
const SEAMFORGE_STDOUT_TAIL := "DESCENDANT_PIPE_SEAMFORGE tail ends in ERROR"
const SEAMFORGE_STDERR_HEAD := ": SEAMFORGE phantom fabricated line"
const SEAMFORGE_PPID_WRITE := "DESCENDANT_PIPE_SEAMFORGE write_ppid="
const MIDLINE_ERROR := "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"
const MIDLINE_PPID_WRITE := "DESCENDANT_PIPE_MIDLINE write_ppid="

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	var forge_hold := "--spawn-forge-hold" in user_args
	var forge_release := "--spawn-forge-release" in user_args
	var errforge_hold := "--spawn-errforge-hold" in user_args
	var errforge_release := "--spawn-errforge-release" in user_args
	var emit_errforge := "--emit-errforge" in user_args
	var allowforge := "--spawn-allowforge" in user_args
	var splitforge := "--spawn-splitforge" in user_args
	var seamforge := "--spawn-seamforge" in user_args
	var midline_forge := "--spawn-midlineforge" in user_args
	if forge_hold or forge_release:
		print("DESCENDANT_PIPE_FORGE child_signature=withheld")
	elif not midline_forge:
		print(MARKER)
	if errforge_hold or errforge_release:
		print("DESCENDANT_PIPE_ERRFORGE child=clean signature=genuine error=descendant_post_exit")
	elif emit_errforge:
		print("DESCENDANT_PIPE_ERRFORGE child_error=genuine_pre_exit")
		push_error(ERRFORGE_ERROR_BODY)
	elif allowforge or splitforge or seamforge:
		print("DESCENDANT_PIPE_SURFACEFORGE child=clean signature=genuine clause_surface=descendant_post_exit")
	elif midline_forge:
		var gap_probe_ms := 200
		for arg in user_args:
			if arg.begins_with("--midline-gap-ms="):
				gap_probe_ms = arg.get_slice("=", 1).to_int()
		print("DESCENDANT_PIPE_MIDLINE child=splice_target signature=halved gap_ms=" + str(gap_probe_ms))
	print("DESCENDANT_PIPE godot_pid=", OS.get_process_id())
	var reparent_gate := ("while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \""
		+ str(OS.get_process_id()) + "\" ]; do sleep 0.05; done; ")
	var spawned := -1
	if "--spawn-hold" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			reparent_gate + "echo " + POST_EXIT_WRITE + "; sleep 6"]))
	elif "--spawn-detach" in user_args:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			"exec sh -c 'sleep 8' </dev/null >/dev/null 2>&1"]))
	elif forge_hold or forge_release:
		var tail := "; sleep 6" if forge_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			reparent_gate + "echo " + MARKER + "; echo " + FORGE_PPID_WRITE + "$pp" + tail]))
	elif errforge_hold or errforge_release:
		var err_tail := "; sleep 6" if errforge_hold else ""
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			reparent_gate + "echo " + ERRFORGE_ERROR + "; echo " + ERRFORGE_PPID_WRITE + "$pp" + err_tail]))
	elif allowforge:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			reparent_gate + "echo '" + ALLOWFORGE_ERROR + "'; echo " + ALLOWFORGE_PPID_WRITE + "$pp"]))
	elif splitforge:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			reparent_gate + "printf 'ERR\\n'; sleep 0.05; printf 'OR: DESCENDANT_PIPE_SPLITFORGE newline-split diagnostic\\n'; echo " + SPLITFORGE_PPID_WRITE + "$pp"]))
	elif seamforge:
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			reparent_gate + "echo DESCENDANT_PIPE_SEAMFORGE post_death_write=1; printf '" + SEAMFORGE_STDOUT_TAIL + "'; echo '" + SEAMFORGE_STDERR_HEAD + "' >&2; echo " + SEAMFORGE_PPID_WRITE + "$pp >&2"]))
	elif midline_forge:
		var midline_offset_ms := 80
		for arg in user_args:
			if arg.begins_with("--midline-offset-ms="):
				midline_offset_ms = arg.get_slice("=", 1).to_int()
		spawned = OS.create_process("/usr/bin/sh", PackedStringArray(["-c",
			("sleep %d.%03d; " % [midline_offset_ms / 1000, midline_offset_ms % 1000])
			+ "read -r _ _ _ pp _ < /proc/self/stat; printf '" + MIDLINE_ERROR + "\\n'; echo " + MIDLINE_PPID_WRITE + "$pp"]))
	if spawned > 0:
		print("DESCENDANT_PIPE spawned_pid=", spawned)
	if midline_forge:
		# The halves are emitted last so no child line can intervene; the
		# descendant's parameterized-offset write splices into the 200ms gap
		# iff it lands inside it — write_ppid==godot_pid proves the write was
		# pre-death.
		printraw(MARKER_SPLICE_HEAD)
		var midline_gap_ms := 200
		for arg in user_args:
			if arg.begins_with("--midline-gap-ms="):
				midline_gap_ms = arg.get_slice("=", 1).to_int()
		OS.delay_msec(midline_gap_ms)
		print(MARKER_SPLICE_TAIL)
	quit(0)
