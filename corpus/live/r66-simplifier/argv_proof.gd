extends SceneTree

# r66-simplifier: proves the reparent_gate local-var extraction produces
# byte-identical sh -c argv for every while-gated arm of the r66
# descendant_pipe_probe.gd (8 variants, 6 while-gate copies).
# Old forms pasted verbatim from the tracked author diff; new forms use
# the extracted `reparent_gate` local. The --spawn-midlineforge arm uses a
# single-shot `read` (not the while-gate) and is deliberately NOT folded.

const MARKER := "DESCENDANT_PIPE_PROBE: expected signature"
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

func _initialize() -> void:
	var pid := str(OS.get_process_id())
	var reparent_gate := ("while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \""
		+ pid + "\" ]; do sleep 0.05; done; ")
	var gate_old := "while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" + pid + "\" ]; do sleep 0.05; done; "
	var cases := []
	cases.append(["gate_prefix_itself", gate_old, reparent_gate])
	cases.append(["spawn-hold",
		gate_old + "echo " + POST_EXIT_WRITE + "; sleep 6",
		reparent_gate + "echo " + POST_EXIT_WRITE + "; sleep 6"])
	for tail: String in ["; sleep 6", ""]:
		cases.append(["forge" + ("-hold" if tail else "-release"),
			gate_old + "echo " + MARKER + "; echo " + FORGE_PPID_WRITE + "$pp" + tail,
			reparent_gate + "echo " + MARKER + "; echo " + FORGE_PPID_WRITE + "$pp" + tail])
		cases.append(["errforge" + ("-hold" if tail else "-release"),
			gate_old + "echo " + ERRFORGE_ERROR + "; echo " + ERRFORGE_PPID_WRITE + "$pp" + tail,
			reparent_gate + "echo " + ERRFORGE_ERROR + "; echo " + ERRFORGE_PPID_WRITE + "$pp" + tail])
	cases.append(["allowforge",
		gate_old + "echo '" + ALLOWFORGE_ERROR + "'; echo " + ALLOWFORGE_PPID_WRITE + "$pp",
		reparent_gate + "echo '" + ALLOWFORGE_ERROR + "'; echo " + ALLOWFORGE_PPID_WRITE + "$pp"])
	cases.append(["splitforge",
		gate_old + "printf 'ERR\\n'; sleep 0.05; printf 'OR: DESCENDANT_PIPE_SPLITFORGE newline-split diagnostic\\n'; echo " + SPLITFORGE_PPID_WRITE + "$pp",
		reparent_gate + "printf 'ERR\\n'; sleep 0.05; printf 'OR: DESCENDANT_PIPE_SPLITFORGE newline-split diagnostic\\n'; echo " + SPLITFORGE_PPID_WRITE + "$pp"])
	cases.append(["seamforge",
		gate_old + "echo DESCENDANT_PIPE_SEAMFORGE post_death_write=1; printf '" + SEAMFORGE_STDOUT_TAIL + "'; echo '" + SEAMFORGE_STDERR_HEAD + "' >&2; echo " + SEAMFORGE_PPID_WRITE + "$pp >&2",
		reparent_gate + "echo DESCENDANT_PIPE_SEAMFORGE post_death_write=1; printf '" + SEAMFORGE_STDOUT_TAIL + "'; echo '" + SEAMFORGE_STDERR_HEAD + "' >&2; echo " + SEAMFORGE_PPID_WRITE + "$pp >&2"])
	var ok := true
	for c in cases:
		var same: bool = c[1] == c[2]
		ok = ok and same
		print("ARGV_EQ ", c[0], " ", same, " sha256=", (c[1] as String).sha256_text())
	print("ARGV_PROOF ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)
