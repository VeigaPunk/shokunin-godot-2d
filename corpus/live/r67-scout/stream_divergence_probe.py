#!/usr/bin/env python3
"""r67 scout: measure classify_streams vs classify_process divergence on real
per-stream bytes. Executes the VERBATIM nested defs extracted from
corpus/fixtures/run_battery.py via ast.get_source_segment (r66-author
precedent) — the classifier bodies are not imported, they are the tracked
source itself."""
import ast, json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BATTERY = REPO / "corpus" / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
GODOT = "/usr/bin/godot"
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
STREAM_SIG = "STREAM_STDOUT: expected attribution marker"
ERRFORGE_ERROR = "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"

# --- extract verbatim classifier source -------------------------------------
tree = ast.parse(BATTERY.read_text())
wanted = {"classify_process": None, "classify_streams": None,
          "classify_audio_process": None}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        seg = ast.get_source_segment(BATTERY.read_text(), node)
        if seg and seg.startswith("def " + node.name):
            wanted[node.name] = seg
assert all(wanted.values()), {k: v is None for k, v in wanted.items()}
ns = {"re": __import__("re")}
for name, seg in wanted.items():
    exec(seg, ns)
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]

# --- runners ----------------------------------------------------------------
def run(flags, script="descendant_pipe_probe.gd", bound=8.0):
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://" + script, "--"] + flags
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=bound)
        out, err, code, error = p.stdout, p.stderr, p.returncode, None
    except subprocess.TimeoutExpired as e:
        out = e.stdout or ""
        err = e.stderr or ""
        code, error = None, f"TIMEOUT after {bound} seconds"
    return {"flags": flags, "script": script, "elapsed_s": round(time.monotonic() - t0, 3),
            "exit": code, "error": error, "stdout": out, "stderr": err,
            "stdout_lines": out.strip().splitlines(),
            "stderr_lines": err.strip().splitlines()}

def verdicts(rec, signature=SIG, expected=0, allowed_errors=(), allowed_stderr=()):
    merged = rec["stdout"] + rec["stderr"]
    return {
        "merged_cls": classify_process(rec["exit"], rec["error"], merged,
                                       expected, signature, allowed_errors),
        "streams_cls": classify_streams(rec["exit"], rec["error"], rec["stdout"],
                                        rec["stderr"], expected, signature,
                                        allowed_stderr),
        "streams_cls_allowed": classify_streams(
            rec["exit"], rec["error"], rec["stdout"], rec["stderr"],
            expected, signature, allowed_stderr or (ERRFORGE_ERROR,)),
        "merged_cls_allowed": classify_process(
            rec["exit"], rec["error"], merged, expected, signature,
            allowed_errors or (ERRFORGE_ERROR,)),
    }

arms = {
    "errforge_release": run(["--spawn-errforge-release"]),
    "errforge_genuine": run(["--emit-errforge"]),
    "allowforge": run(["--spawn-allowforge"]),
    "splitforge": run(["--spawn-splitforge"]),
    "seamforge": run(["--spawn-seamforge"]),
    "stream_accept": run([], script="stream_attribution_probe.gd"),
    "stream_reject": run(["--stderr-unrelated"], script="stream_attribution_probe.gd"),
}
for name, rec in arms.items():
    sig = STREAM_SIG if name.startswith("stream_") else SIG
    rec["verdicts"] = verdicts(rec, signature=sig)

# seam positions on seamforge
sf = arms["seamforge"]
sf["seam"] = {
    "stdout_tail_line": sf["stdout_lines"][-1] if sf["stdout_lines"] else None,
    "stderr_head_line": sf["stderr_lines"][0] if sf["stderr_lines"] else None,
    "merged_tail": (sf["stdout"] + sf["stderr"]).splitlines()[-2:]
        if (sf["stdout"] + sf["stderr"]).splitlines() else [],
}

# --- synthetic per-stream cells through the REAL classifiers -----------------
def cell(name, stdout, stderr, sig=SIG, expected=0,
         allowed_errors=(), allowed_stderr=()):
    return {"cell": name,
            "merged": classify_process(expected, None, stdout + stderr,
                                       expected, sig, allowed_errors),
            "streams": classify_streams(expected, None, stdout, stderr,
                                        expected, sig, allowed_stderr),
            "stdout": stdout, "stderr": stderr,
            "allowed_errors": list(allowed_errors),
            "allowed_stderr": list(allowed_stderr)}

BANNER = "Godot Engine v4.7.2.stable\n"
chain_entry = "ERROR: chain incomplete"
chain_line = ("ERROR: chain incomplete collections=1 "
              "scene=SceneB:<Node#7> old_alive=false")
cells = [
    cell("stdout_ERROR_stderr_clean", BANNER + SIG + "\nERROR: forged on stdout\n", ""),
    cell("stderr_ERROR_stdout_clean", BANNER + SIG + "\n", "ERROR: forged on stderr\n"),
    cell("stderr_ERROR_allowlisted", BANNER + SIG + "\n", "ERROR: forged on stderr\n",
         allowed_errors=("ERROR: forged on stderr",),
         allowed_stderr=("ERROR: forged on stderr",)),
    cell("stdout_ERROR_allowlisted", BANNER + SIG + "\nERROR: forged on stdout\n", "",
         allowed_errors=("ERROR: forged on stdout",),
         allowed_stderr=("ERROR: forged on stdout",)),
    cell("stderr_nonerror_noise", BANNER + SIG + "\n", "   at: _initialize (res://x.gd:12)\n"),
    cell("signature_on_stderr", BANNER + "\n", SIG + "\n"),
    cell("signature_straddles_seam", BANNER + "DESCENDANT_PIPE_PROBE: expected ", "signature\n"),
    cell("seam_phantom_stderr_head_clean", BANNER + SIG + "\ntail ends in ERROR", ""),
    cell("seam_phantom_fabricated", BANNER + SIG + "\ntail ends in ERROR",
         ": PHANTOM fabricated line\n"),
    cell("seam_phantom_head_allowlisted", BANNER + SIG + "\ntail ends in ERROR",
         ": PHANTOM fabricated line\n",
         allowed_errors=(": PHANTOM fabricated line",),
         allowed_stderr=(":", ": PHANTOM fabricated line")),
    cell("structured_entry_stderr", BANNER + SIG + "\n", chain_line + "\n",
         allowed_errors=(chain_entry,), allowed_stderr=(chain_entry,)),
    cell("comma_entry_stderr", BANNER + SIG + "\n",
         "ERROR: E, path=/tmp/x\n",
         allowed_errors=("ERROR: E,",), allowed_stderr=("ERROR: E,",)),
    cell("script_error_seam_split", BANNER + SIG + "\nends in SCRIPT ERR", "OR: x\n"),
    cell("newline_split_error", BANNER + SIG + "\nERR\nOR: split\n", ""),
]

out = {"godot": "4.7.2.stable", "classifier_source": "verbatim ast-exec from "
       + str(BATTERY), "arms": arms, "synthetic_cells": cells}
(HERE / "stream-divergence.json").write_text(json.dumps(out, indent=2) + "\n")
for name, rec in arms.items():
    print(name, "exit=", rec["exit"], "stderr_lines=", len(rec["stderr_lines"]),
          "verdicts=", rec["verdicts"])
print("---cells---")
for c in cells:
    print(f"{c['cell']:34s} merged={c['merged']!s:5s} streams={c['streams']!s:5s} "
          f"{'DIVERGE' if c['merged'] != c['streams'] else 'agree'}")
