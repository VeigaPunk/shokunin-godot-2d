extends SceneTree

const STDOUT_MARKER := "STREAM_STDOUT: expected attribution marker"
const STDERR_MARKER := "STREAM_STDERR: unrelated attribution diagnostic"
# r67 per-channel divergence arms (meta-driven via probe_stream_attribution;
# the SAME captured stdout/stderr pair is re-classified by BOTH the merged
# classify_process and the per-stream classify_streams — the verdict pairs
# pin exactly which bytes diverge on the stream-attribution axis):
#   --stdout-error        -> genuine signature + one ERROR: line, BOTH on
#                          stdout: merged rejects (unrelated error line),
#                          per-stream absorbs (stdout is never error-scanned).
#   --stderr-error        -> signature on stdout + one ERROR: line on stderr:
#                          the concordant control — both reject bare, both
#                          absorb under the byte-exact allowlist entry.
#   --stderr-structured   -> signature on stdout + a chain-incomplete-shaped
#                          ERROR: line on stderr: the "ERROR: chain
#                          incomplete" allowlist entry absorbs merged-only —
#                          line_allowed has no structured branch (the
#                          allowlist's per-stream match asymmetry).
#   --sig-on-stderr       -> the signature itself emitted on stderr: merged
#                          accepts, per-stream rejects on the signature axis
#                          even with stderr fully allowlisted.
#   --seam-error          -> unterminated stdout tail "...ends in ERROR" +
#                          stderr head ": ..." fabricate an ERROR: line that
#                          exists only in the merged concat; per-stream
#                          absorbs iff that stderr head line is allowlisted.
#   --seam-script         -> unterminated stdout tail "...SCRIPT ERR" +
#                          stderr head "OR: ..." fabricate the SCRIPT ERROR:
#                          blob token only in the merged concat — per-stream
#                          blob checks are seam-immune.
#   --seam-sig            -> the signature split across the seam: stdout tail
#                          is its unterminated head, the stderr head
#                          completes it — contiguous only in merged.
const STREAMDIV_STDOUT_ERROR := "ERROR: STREAMDIV stdout-carried diagnostic"
const STREAMDIV_STDERR_ERROR := "ERROR: STREAMDIV stderr-carried diagnostic"
const STREAMDIV_STRUCTURED := "ERROR: chain incomplete collections=streamdiv scene=SceneB:<Node#6700> old_alive=false"
const STREAMDIV_SEAM_TAIL := "STREAMDIV seam tail ends in ERROR"
const STREAMDIV_SEAM_HEAD := ": STREAMDIV seam phantom merged-only line"
const STREAMDIV_SCRIPT_TAIL := "STREAMDIV seam tail ends in SCRIPT ERR"
const STREAMDIV_SCRIPT_HEAD := "OR: STREAMDIV seamed blob clause"
const STREAMDIV_SIG_HEAD := "STREAM_STDOUT: expected attribution "
const STREAMDIV_SIG_TAIL := "marker"

func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	if "--seam-sig" in user_args:
		printraw(STREAMDIV_SIG_HEAD)
		printerr(STREAMDIV_SIG_TAIL)
	elif "--sig-on-stderr" in user_args:
		printerr(STDOUT_MARKER)
	else:
		print(STDOUT_MARKER)
	if "--stderr-unrelated" in user_args:
		printerr(STDERR_MARKER)
	if "--stdout-error" in user_args:
		print(STREAMDIV_STDOUT_ERROR)
	if "--stderr-error" in user_args:
		printerr(STREAMDIV_STDERR_ERROR)
	if "--stderr-structured" in user_args:
		printerr(STREAMDIV_STRUCTURED)
	if "--seam-error" in user_args:
		printraw(STREAMDIV_SEAM_TAIL)
		printerr(STREAMDIV_SEAM_HEAD)
	if "--seam-script" in user_args:
		printraw(STREAMDIV_SCRIPT_TAIL)
		printerr(STREAMDIV_SCRIPT_HEAD)
	quit(0)
