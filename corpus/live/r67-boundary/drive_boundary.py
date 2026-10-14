#!/usr/bin/env python3
"""r67 boundary: edge-probes of the per-channel divergence surface.

Brief edges:
  (1) per-stream seam positions both directions (stdout-tail+stderr-head AND
      stderr-tail+stdout-head);
  (2) splitlines boundary table on the per-stream path;
  (3) allowlist shapes under classify_streams;
  (4) unicode/ÿ on the per-stream path (r66 DoV class — does it hit
      classify_streams identically?);
  (5) drain-order sensitivity — does Popen communicate() ordering change
      which seam fabricates?

Method: ast.get_source_segment-extract the PRODUCTION functions from the
working-tree run_battery.py and exec them (sha-pinned). All verdicts below
are verbatim-function outputs on either real captured pipe bytes (subprocess
children / real Godot runs of the landed fixture) or disclosed unit strings.
No reimplementation decides a verdict; replicas are corroboration only.
"""
import ast
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent                      # corpus/live/r67-boundary
REPO = HERE.parent.parent.parent                            # repo root
RUNNER = REPO / "corpus" / "fixtures" / "run_battery.py"
FIXTURES = REPO / "corpus" / "fixtures"
PROJ = HERE / "proj"                                        # scratch project copy
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)
GODOT = os.environ.get("GODOT", "/usr/bin/godot")

OUT = {"runner_sha": None, "git_head": None, "function_shas": {},
       "replay_anchor": {}, "phases": {}}


def sha(data):
    b = data.encode() if isinstance(data, str) else data
    return hashlib.sha256(b).hexdigest()


# ---------- verbatim extraction --------------------------------------------
SRC_TEXT = RUNNER.read_text()
OUT["runner_sha"] = sha(SRC_TEXT)
OUT["runner_lines"] = SRC_TEXT.count("\n") + 1
OUT["git_head"] = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
    text=True).stdout.strip()
OUT["git_status_fixtures"] = subprocess.run(
    ["git", "status", "--porcelain", "corpus/fixtures/"], cwd=REPO,
    capture_output=True, text=True).stdout.strip().splitlines()
HEAD_TEXT = subprocess.run(
    ["git", "show", "HEAD:corpus/fixtures/run_battery.py"], cwd=REPO,
    capture_output=True, text=True).stdout
OUT["head_runner_sha"] = sha(HEAD_TEXT)

NS = {}
tree = ast.parse(SRC_TEXT)
WANTED = ("run_process", "classify_process", "classify_streams",
          "classify_audio_process", "pid_alive", "kernel_ppid")
segs = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in WANTED \
            and node.name not in segs:
        segs[node.name] = ast.get_source_segment(SRC_TEXT, node)
missing = [w for w in WANTED if w not in segs]
if missing:
    sys.exit(f"verbatim extraction missing: {missing}")
import textwrap
for name, seg in segs.items():
    OUT["function_shas"][name] = sha(textwrap.dedent(seg))
    OUT["function_shas"][name + "_in_HEAD"] = None
head_tree = ast.parse(HEAD_TEXT)
for node in ast.walk(head_tree):
    if isinstance(node, ast.FunctionDef) and node.name in WANTED \
            and OUT["function_shas"][node.name + "_in_HEAD"] is None:
        OUT["function_shas"][node.name + "_in_HEAD"] = sha(
            textwrap.dedent(ast.get_source_segment(HEAD_TEXT, node)))
exec("import subprocess, re, os, signal, time, json\nfrom pathlib import Path\n"
     + "\n\n".join(textwrap.dedent(segs[n]) for n in WANTED), NS)
classify_process = NS["classify_process"]
classify_streams = NS["classify_streams"]
classify_audio_process = NS["classify_audio_process"]
run_process = NS["run_process"]
pid_alive = NS["pid_alive"]
kernel_ppid = NS["kernel_ppid"]

SIG = "STREAM_STDOUT: expected attribution marker"


def record_dual(name, so, se, code=0, error=None, sig=SIG,
                merged_allowed=(), stream_allowed=()):
    # expected_exit bound to the OBSERVED code: exit/error axes are held
    # neutral so the verdict pair isolates the stream-attribution axis.
    merged = classify_process(code, error, so + se, code, sig, merged_allowed)
    streams = classify_streams(code, error, so, se, code, sig, stream_allowed)
    return {"case": name,
            "merged_allowlist": list(merged_allowed),
            "stream_allowlist": list(stream_allowed),
            "merged": merged, "streams": streams,
            "divergent": merged != streams,
            "sig_in_stdout": sig in so, "sig_in_stderr": sig in se,
            "sig_in_merged": sig in (so + se),
            "stdout_lines": so.splitlines(), "stderr_lines": se.splitlines(),
            "merged_lines": (so + se).splitlines()}


def run_pair(command, timeout=15):
    """Per-stream capture (the --probe-stream-attribution shape)."""
    proc = subprocess.run(command, capture_output=True, text=True,
                          timeout=timeout)
    return proc.stdout or "", proc.stderr or "", proc.returncode, None


def run_pair_popen(command, timeout=15):
    """Popen+communicate capture (the surface_run shape)."""
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    try:
        so, se = proc.communicate(timeout=timeout)
        return so or "", se or "", proc.returncode, None
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3)
        return "", "", None, "TIMEOUT"


# ---------- replay anchor ---------------------------------------------------
def replay(receipt_path):
    try:
        v = json.loads(Path(receipt_path).read_text())
    except Exception as exc:
        return {"receipt": str(receipt_path), "error": str(exc)}
    rows = [r for r in v["results"] if isinstance(r.get("output"), list)
            and r.get("expected_exit") is not None
            and r.get("signature") is not None]
    mism = []
    for r in rows:
        text = "\n".join(r["output"])
        case = r["case"]
        # Per-case classification convention, mirroring run_battery.py
        # :447 (audio via classify_audio_process), :311-345 (export
        # wrappers), :366-378 (classify_mutant triple arm).
        if case == "audio_playback":
            got = classify_audio_process(r["actual_exit"], r["error"], text,
                                         r["expected_exit"], r["signature"])
        elif case == "export_readiness":
            got = (classify_process(r["actual_exit"], r["error"], text, 0,
                                    "[ DONE ]") and "savepack" in text)
        elif case == "export_preset_missing":
            ev = "ERROR: Invalid export preset name: Missing preset."
            got = classify_process(r["actual_exit"], r["error"], text,
                                   r["expected_exit"], ev, (ev,))
        elif case == "mutant_broken_scene_route":
            got = (classify_process(r["actual_exit"], r["error"], text, 2,
                                    "chain incomplete",
                                    ("ERROR: chain incomplete",))
                   and "PASS positive input=1" not in text)
        elif case == "mutant_level_collision_removed":
            ev = "LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry"
            got = (classify_process(r["actual_exit"], r["error"], text, 2, ev,
                                    ("ERROR: " + ev,))
                   and "PASS level_packed_scene=true" not in text)
        else:
            got = classify_process(r["actual_exit"], r["error"], text,
                                   r["expected_exit"], r["signature"],
                                   tuple(r.get("expected_errors") or ()))
        want = r["verdict"] == "PASS"
        if got != want:
            mism.append({"case": case, "want": want, "got": got})
    return {"receipt": str(receipt_path), "rows": len(rows),
            "verdict": v["verdict"], "mismatches": mism}


baseline_runs = sorted((REPO / "corpus/live/r67-baseline/runs").glob("*/verdicts.json"))
if baseline_runs:
    OUT["replay_anchor"]["r67_baseline"] = replay(baseline_runs[-1])
author_runs = sorted((REPO / "corpus/live/r67-author/runs").glob("*/verdicts.json"))
if author_runs:
    OUT["replay_anchor"]["r67_author"] = replay(author_runs[-1])


# ---------- scratch fixture project -----------------------------------------
if PROJ.exists():
    shutil.rmtree(PROJ)
PROJ.mkdir()
for item in FIXTURES.iterdir():
    if item.name in ("run_battery.py", "__pycache__") or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, PROJ / item.name)
    else:
        shutil.copy2(item, PROJ / item.name)


def godot(flags, timeout=15, script="res://stream_attribution_probe.gd"):
    return run_pair([GODOT, "--headless", "--path", str(PROJ), "--script",
                     script, "--", *flags], timeout)


def py(code, timeout=15):
    return run_pair([sys.executable, "-c", code], timeout)


def sh(code, timeout=15):
    return run_pair(["/usr/bin/sh", "-c", code], timeout)


# ============ EDGE 1: per-stream seam positions, both directions ============
ph = {}

# 1a. real landed arms re-driven (in-life writes, author's fixture bytes) —
# each arm classified bare AND under the author's pinned allowlist choices.
A_SEAM_HEAD = ": STREAMDIV seam phantom merged-only line"
A_SCRIPT_HEAD = "OR: STREAMDIV seamed blob clause"
A_SIG_TAIL = "marker"
A_STRUCT = "ERROR: chain incomplete"
landed = {}
for case, flags, m_allow, s_allow in [
        ("accept", [], (), ()),
        ("reject", ["--stderr-unrelated"], (), ()),
        ("stdout_error", ["--stdout-error"], (), ()),
        ("stderr_error", ["--stderr-error"], (), ()),
        ("stderr_structured", ["--stderr-structured"], (A_STRUCT,), (A_STRUCT,)),
        ("sig_on_stderr", ["--sig-on-stderr"], (), (SIG,)),
        ("seam_error", ["--seam-error"], (), (A_SEAM_HEAD,)),
        ("seam_script", ["--seam-script"], (), (A_SCRIPT_HEAD,)),
        ("seam_sig", ["--seam-sig"], (), (A_SIG_TAIL,))]:
    so, se, code, err = godot(flags)
    bare = record_dual(f"landed_{case}_bare", so, se, code, err)
    auth = record_dual(f"landed_{case}_authorallow", so, se, code, err,
                       merged_allowed=m_allow, stream_allowed=s_allow)
    (RAW / f"landed_{case}.stdout").write_text(so)
    (RAW / f"landed_{case}.stderr").write_text(se)
    landed[case] = {"exit": code, "error": err,
                    "bare": {"merged": bare["merged"],
                             "streams": bare["streams"],
                             "divergent": bare["divergent"]},
                    "author_allowlist": {"merged": auth["merged"],
                                         "streams": auth["streams"],
                                         "divergent": auth["divergent"]},
                    "stdout_tail": so.splitlines()[-1] if so.splitlines() else None,
                    "stderr_head": se.splitlines()[0] if se.splitlines() else None,
                    "sig_in_stdout": bare["sig_in_stdout"],
                    "sig_in_stderr": bare["sig_in_stderr"],
                    "sig_in_merged": bare["sig_in_merged"]}
ph["landed_redrive"] = landed

# 1b. seam direction A, synthetic: unterminated stdout tail + stderr head
TAIL = "BOUNDARY seam tail ends in ERROR"
HEAD = ": BOUNDARY seam phantom merged-only"
FAB = TAIL + HEAD
so, se, code, err = py(
    "import sys; sys.stdout.write('%s\\n'); sys.stdout.write('%s'); "
    "sys.stdout.flush(); sys.stderr.write('%s\\n'); sys.stderr.flush()"
    % (SIG, TAIL, HEAD))
ph["seam_A_synth"] = {
    "captured": {"stdout_tail": so.splitlines()[-1],
                 "stderr_head": se.splitlines()[0]},
    "fabricated_line": FAB,
    "fab_in_stdout_lines": FAB in so.splitlines(),
    "fab_in_stderr_lines": FAB in se.splitlines(),
    "fab_in_merged_lines": FAB in (so + se).splitlines(),
    "bare": record_dual("seam_A_bare", so, se, code, err),
    "head_allowlisted": record_dual("seam_A_allow", so, se, code, err,
                                    stream_allowed=(HEAD,)),
    # the merged-side allowlist can preempt a line that exists in NEITHER
    # stream: the phantom is a first-class allowlist target.
    "phantom_merged_allowlisted": record_dual(
        "seam_A_phantom_allow", so, se, code, err, merged_allowed=(FAB,))}

# 1c. seam direction B: stderr TAIL unterminated + stdout HEAD fragment.
# Merged concat is stdout-then-stderr — these fragments sit at OPPOSITE
# ends of the blob; no merged line can ever join them.
BTAIL = "BOUNDARY rev tail ends in ERROR"
BHEAD = ": BOUNDARY rev head fragment"
so, se, code, err = py(
    "import sys; sys.stdout.write('%s\\n'); sys.stdout.write('%s\\n'); "
    "sys.stdout.write('%s\\n'); sys.stdout.flush(); "
    "sys.stderr.write('chatter\\n'); sys.stderr.write('%s'); "
    "sys.stderr.flush()" % (BHEAD, SIG, "ok", BTAIL))
ph["seam_B_synth"] = {
    "captured": {"stdout_head": so.splitlines()[0],
                 "stderr_tail": se.splitlines()[-1]},
    "merged_first_line": (so + se).splitlines()[0],
    "merged_last_line": (so + se).splitlines()[-1],
    "any_merged_line_with_error": [l for l in (so + se).splitlines()
                                   if "ERROR:" in l],
    "bare": record_dual("seam_B_bare", so, se, code, err),
    "tail_allowlisted": record_dual("seam_B_allow", so, se, code, err,
                                    stream_allowed=(BTAIL, "chatter"))}

# 1d. direction-B signature seam: sig head on stderr tail, tail on stdout head.
SH, ST = "STREAM_STDOUT: expected attribution ", "marker"
so, se, code, err = py(
    "import sys; sys.stdout.write('%s\\nok\\n'); sys.stdout.flush(); "
    "sys.stderr.write('%s'); sys.stderr.flush()" % (ST, SH))
ph["seam_B_sig"] = {
    "captured": {"stdout_head": so.splitlines()[0],
                 "stderr_tail": se.splitlines()[-1]},
    "sig_in_merged": SIG in (so + se),
    "merged_lines": (so + se).splitlines(),
    "dual": record_dual("seam_B_sig", so, se, code, err)}

# 1d-bis. direction B with a POST-DEATH stderr tail: the descendant appends
# the unterminated ERROR-fragment to stderr tail after the child exits —
# pipe writes append, so a post-death write can only ever extend a stream's
# TAIL; stdout head is child-era forever. Direction-B stays unfabricatable
# even with post-death writes.
so, se, code, err = sh(
    "printf '%s\\n'; printf '%s\\n'; "
    "(while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"$$\" ]; "
    "do sleep 0.05; done; printf '%s' >&2) & exit 0"
    % (BHEAD, SIG, BTAIL))
ph["seam_B_postdeath"] = {
    "captured": {"stdout_head": so.splitlines()[0],
                 "stderr_tail": se.splitlines()[-1]},
    "any_merged_line_with_error": [l for l in (so + se).splitlines()
                                   if "ERROR:" in l],
    "dual": record_dual("seam_B_postdeath", so, se, code, err)}

# 1e. intra-stream post-death seam: child leaves unterminated stdout tail,
# reparenting-gated descendant completes the SIGNATURE on stdout — the
# signature fabricates INSIDE one stream; classify_streams' stdout check
# sees it as plainly present (provenance-blind within the channel). The
# gate compares the descendant's ppid against the sh child's own $$;
# subprocess.run blocks on pipe EOF, so the post-death write is captured.
so, se, code, err = sh(
    "printf '%s\\n'; printf '%s'; "
    "(while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"$$\" ]; "
    "do sleep 0.05; done; printf 'marker\\n') & exit 0"
    % ("BOUNDARY child banner", SH))
ph["seam_intrastream_postdeath_sig"] = {
    "note": "descendant completed the signature on stdout post-child-exit; "
            "EOF held until descendant write -> captured",
    "captured_stdout_lines": so.splitlines(),
    "sig_in_stdout": SIG in so,
    "dual": record_dual("seam_intrastream_sig", so, se, code, err)}

# 1f. real post-death seam via the shipped r66 fixture (descendant writes the
# stderr head AFTER the child died) — per-stream capture of --spawn-seamforge.
so, se, code, err = run_pair(
    [GODOT, "--headless", "--path", str(PROJ), "--script",
     "res://descendant_pipe_probe.gd", "--", "--spawn-seamforge"], 15)
ph["seam_forge_postdeath_perstream"] = {
    "exit": code, "error": err,
    "stdout_tail": so.splitlines()[-1] if so.splitlines() else None,
    "stderr_head": se.splitlines()[0] if se.splitlines() else None,
    "stderr_lines": se.splitlines(),
    "dual_surface_sig": record_dual(
        "seamforge_streams", so, se, code, err,
        sig="DESCENDANT_PIPE_PROBE: expected signature"),
}

OUT["phases"]["edge1_seams"] = ph


# ============ EDGE 2: splitlines boundary table on the per-stream path ======
ph = {}
BOUNDS = [("\n", "\\n"), ("\r", "\\r"), ("\r\n", "\\r\\n"), ("\v", "\\v"),
          ("\f", "\\f"), ("\x1c", "\\x1c"), ("\x1d", "\\x1d"),
          ("\x1e", "\\x1e"), ("\x85", "\\x85 NEL"), (" ", "U+2028"),
          (" ", "U+2029"), ("\x1f", "\\x1f control"), ("ÿ", "U+00FF y-dia")]
ENTRY = "ERROR: BOUNDARY allowlisted entry"
table = []
for ch, label in BOUNDS:
    # boundary INSIDE the veto candidate: 'ERR'+c+'OR: tail' on stderr
    se_split = "ERR" + ch + "OR: BOUNDARY tail"
    so_clean = SIG + "\n"
    # boundary at END of an exactly-allowlisted line: 'ENTRY'+c
    se_tail = ENTRY + ch
    # boundary BEFORE an ERROR line's tail fragment
    se_frag = ENTRY + ch + "BOUNDARY rest"
    row = {"char": label,
           "splits": len(se_split.splitlines()) > 1,
           "strip_removes_trailing": se_tail.strip() == ENTRY,
           "split_lines": [repr(l) for l in se_split.splitlines()],
           "tail_split_lines": [repr(l) for l in se_tail.splitlines()],
           "frag_split_lines": [repr(l) for l in se_frag.splitlines()],
           "split_streams": classify_streams(0, None, so_clean, se_split, 0,
                                             SIG, (ENTRY,)),
           "split_merged": classify_process(0, None, so_clean + se_split, 0,
                                            SIG, (ENTRY,)),
           "tail_streams": classify_streams(0, None, so_clean, se_tail, 0,
                                            SIG, (ENTRY,)),
           "tail_merged": classify_process(0, None, so_clean + se_tail, 0,
                                           SIG, (ENTRY,)),
           "frag_streams": classify_streams(0, None, so_clean, se_frag, 0,
                                            SIG, (ENTRY,)),
           "frag_merged": classify_process(0, None, so_clean + se_frag, 0,
                                           SIG, (ENTRY,))}
    table.append(row)
ph["boundary_table"] = table

# real-pipe confirmations (decoded text -> splitlines decides), stderr-carried
real = {}
for label, payload in [
        ("nel_split_stderr", b"ERR\xc2\x85OR: BOUNDARY realpipe tail\n"),
        ("yuml_noise_stderr", "noise ÿ\n".encode()),
        ("vt_split_stderr", b"ERR\vOR: BOUNDARY vt tail\n"),
        ("fs_nosplit_stderr", b"ERR\x1fOR: BOUNDARY fs tail\n")]:
    so, se, code, err = py(
        "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.flush(); "
        "sys.stderr.buffer.write(%r); sys.stderr.flush()" % (SIG, payload))
    real[label] = {"stderr_repr": repr(se), "stderr_lines": se.splitlines(),
                   "streams": classify_streams(0, err, so, se, 0, SIG, ()),
                   "merged": classify_process(0, err, so + se, 0, SIG, ())}
ph["real_pipe_confirmations"] = real

# blob-clause newline-split on the per-stream path: SCRIPT ERR\nOR: on
# stdout evades the stdout blob substring identically to merged.
so, se, code, err = py(
    "import sys; sys.stdout.write('%s\\n'); sys.stdout.write('SCRIPT ERR\\n'); "
    "sys.stdout.write('OR: BOUNDARY blob split\\n'); sys.stdout.flush()"
    % SIG)
ph["blob_split_stdout"] = {
    "stdout_lines": so.splitlines(),
    "streams": classify_streams(0, err, so, se, 0, SIG, ()),
    "merged": classify_process(0, err, so + se, 0, SIG, ())}
OUT["phases"]["edge2_splitlines"] = ph


# ============ EDGE 3: allowlist shapes under classify_streams ===============
ph = {}
CHAIN_LINE = ("ERROR: chain incomplete collections=x scene=SceneB:<Node#1> "
              "old_alive=false")
units = []
cases = [
    # (label, stderr body, stream entries, merged entries)
    ("exact_absorbs", ENTRY, (ENTRY,), (ENTRY,)),
    ("exact_suffix_escapes", ENTRY + " tail", (ENTRY,), (ENTRY,)),
    ("exact_prefix_escapes", "noise " + ENTRY, (ENTRY,), (ENTRY,)),
    ("exact_second_error_escapes", ENTRY + " ERROR: second", (ENTRY,), (ENTRY,)),
    ("comma_bare_line", "ERROR: BOUNDARY comma,", ("ERROR: BOUNDARY comma,",),
     ("ERROR: BOUNDARY comma,",)),
    ("comma_tail_absorbs", "ERROR: BOUNDARY comma, tail",
     ("ERROR: BOUNDARY comma,",), ("ERROR: BOUNDARY comma,",)),
    ("comma_tail_count2_escapes", "ERROR: BOUNDARY comma, tail ERROR: x",
     ("ERROR: BOUNDARY comma,",), ("ERROR: BOUNDARY comma,",)),
    ("comma_no_comma_line", "ERROR: BOUNDARY comma",
     ("ERROR: BOUNDARY comma,",), ("ERROR: BOUNDARY comma,",)),
    ("structured_canonical", CHAIN_LINE, ("ERROR: chain incomplete",),
     ("ERROR: chain incomplete",)),
    ("structured_bare_entry_as_line", "ERROR: chain incomplete",
     ("ERROR: chain incomplete",), ("ERROR: chain incomplete",)),
    ("structured_reordered", "ERROR: chain incomplete collections=x "
     "old_alive=false scene=SceneB:<Node#1>", ("ERROR: chain incomplete",),
     ("ERROR: chain incomplete",)),
    ("foreign_entry", ENTRY, ("ERROR: unrelated different diagnostic",),
     ("ERROR: unrelated different diagnostic",)),
    ("nonerror_chatter_bare", "BOUNDARY plain stderr chatter", (), ()),
    ("nonerror_chatter_allowlisted", "BOUNDARY plain stderr chatter",
     ("BOUNDARY plain stderr chatter",), ("BOUNDARY plain stderr chatter",)),
    ("comma_entry_on_nonerror_line", "BOUNDARY plain stderr chatter, tail",
     ("BOUNDARY plain stderr chatter,",),
     ("BOUNDARY plain stderr chatter,",)),
    ("warning_line_bare", "WARNING: BOUNDARY engine warning", (), ()),
    ("warning_line_allowlisted", "WARNING: BOUNDARY engine warning",
     ("WARNING: BOUNDARY engine warning",), ("WARNING: BOUNDARY engine warning",)),
]
for label, se_body, s_allow, m_allow in cases:
    so_clean = SIG + "\n"
    units.append({"case": label, "stderr_line": se_body,
                  "stream_entries": list(s_allow),
                  "merged_entries": list(m_allow),
                  "streams": classify_streams(0, None, so_clean, se_body + "\n",
                                              0, SIG, s_allow),
                  "merged": classify_process(0, None, so_clean + se_body + "\n",
                                             0, SIG, m_allow)})
ph["shape_matrix"] = units

# stdout-carried variants: identical lines on stdout — streams never audits.
ph["stdout_side"] = [
    {"case": "error_line_on_stdout_bare",
     "streams": classify_streams(0, None, SIG + "\n" + ENTRY + "\n", "", 0,
                                 SIG, ()),
     "merged": classify_process(0, None, SIG + "\n" + ENTRY + "\n", 0, SIG, ())},
    {"case": "error_line_on_stdout_streams_entry",
     "streams": classify_streams(0, None, SIG + "\n" + ENTRY + "\n", "", 0,
                                 SIG, (ENTRY,)),
     "merged": classify_process(0, None, SIG + "\n" + ENTRY + "\n", 0, SIG,
                                (ENTRY,))},
    {"case": "script_blob_on_stdout",
     "streams": classify_streams(0, None, SIG + "\nSCRIPT ERROR: x\n", "", 0,
                                 SIG, ()),
     "merged": classify_process(0, None, SIG + "\nSCRIPT ERROR: x\n", 0, SIG, ())},
    {"case": "parse_blob_on_stderr",
     "streams": classify_streams(0, None, SIG + "\n", "Parse Error: x\n", 0,
                                 SIG, ("Parse Error: x",)),
     "merged": classify_process(0, None, SIG + "\nParse Error: x\n", 0, SIG,
                                ("Parse Error: x",))},
]
# entry containing a blob-veto substring: self-neutralizing on streams?
ph["self_neutralizing_entry"] = {
    "streams": classify_streams(0, None, SIG + "\n", "SCRIPT ERROR: x\n", 0,
                                SIG, ("SCRIPT ERROR: x",)),
    "merged": classify_process(0, None, SIG + "\nSCRIPT ERROR: x\n", 0, SIG,
                               ("SCRIPT ERROR: x",)),
    "note": "entry absorbs the stderr LINE but the blob veto is line-free "
            "-> the entry can never preempt the blob clause"}
OUT["phases"]["edge3_allowlist"] = ph


# ============ EDGE 4: unicode / ÿ on the per-stream path ====================
ph = {}
def try_pair(label, pycode, timeout=15):
    try:
        so, se, code, err = py(pycode, timeout)
        return {"label": label, "decoded": True, "exit": code,
                "stdout_repr": repr(so[:200]), "stderr_repr": repr(se[:200]),
                "streams": classify_streams(code, err, so, se, 0, SIG, ()),
                "merged": classify_process(code, err, so + se, 0, SIG, ())}
    except UnicodeDecodeError as exc:
        return {"label": label, "decoded": False,
                "exception": f"UnicodeDecodeError: {exc}",
                "verdict_exists": False}
    except subprocess.TimeoutExpired as exc:
        return {"label": label, "decoded": None,
                "exception": f"TimeoutExpired: {exc}",
                "verdict_exists": False}

ph["ff_stdout"] = try_pair(
    "ff_stdout",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.flush(); "
    "sys.stdout.buffer.write(b'\\xff'); sys.stdout.flush()" % SIG)
ph["ff_stderr"] = try_pair(
    "ff_stderr",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.flush(); "
    "sys.stderr.buffer.write(b'\\xff\\n'); sys.stderr.flush()" % SIG)
ph["ff_both"] = try_pair(
    "ff_both",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.flush(); "
    "sys.stdout.buffer.write(b'\\xff'); sys.stderr.buffer.write(b'\\xff'); "
    "sys.stdout.flush(); sys.stderr.flush()" % SIG)
# raw 0x85 (invalid UTF-8 alone) vs encoded NEL
ph["raw85_stderr"] = try_pair(
    "raw85_stderr",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.flush(); "
    "sys.stderr.buffer.write(b'noise \\x85\\n'); sys.stderr.flush()" % SIG)
ph["nel_stderr"] = try_pair(
    "nel_stderr",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.flush(); "
    "sys.stderr.write('ERR\\u0085OR: BOUNDARY nel\\n'); sys.stderr.flush()"
    % SIG)
# ÿ (valid U+00FF) per channel
ph["yuml_stdout_noise"] = try_pair(
    "yuml_stdout_noise",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.write('noise \\u00ff\\n'); "
    "sys.stdout.flush()" % SIG)
ph["yuml_stdout_errorline"] = try_pair(
    "yuml_stdout_errorline",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.write('ERROR: BOUNDARY \\u00ff\\n'); "
    "sys.stdout.flush()" % SIG)
ph["yuml_stderr_noise"] = try_pair(
    "yuml_stderr_noise",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.flush(); "
    "sys.stderr.write('noise \\u00ff\\n'); sys.stderr.flush()" % SIG)
ph["yuml_stderr_errorline"] = try_pair(
    "yuml_stderr_errorline",
    "import sys; sys.stdout.write(%r + '\\n'); sys.stdout.flush(); "
    "sys.stderr.write('ERROR: BOUNDARY \\u00ff\\n'); sys.stderr.flush()" % SIG)
# decode policy on the TIMEOUT path: exc.stdout arrives as bytes -> the
# runner decodes with errors=replace -> a held-pipe \xff produces a verdict.
ph["ff_then_hold"] = {}
try:
    proc = subprocess.Popen(
        [sys.executable, "-c",
         "import sys,time; sys.stdout.write(%r+'\\n'); sys.stdout.flush(); "
         "sys.stdout.buffer.write(b'\\xff'); sys.stdout.flush(); time.sleep(9)"
         % SIG],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    proc.communicate(timeout=2)
    ph["ff_then_hold"]["result"] = "completed-unexpectedly"
    proc.kill()
except subprocess.TimeoutExpired as exc:
    out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) \
        else (exc.stdout or "")
    er = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) \
        else (exc.stderr or "")
    ph["ff_then_hold"] = {
        "result": "TimeoutExpired",
        "exc_stdout_type": type(exc.stdout).__name__,
        "decoded_stdout_repr": repr(out),
        "replacement_char_count": out.count("\ufffd"),
        "streams_on_recovered": classify_streams(None,
                                                 "TIMEOUT after 2 seconds",
                                                 out, er, 0, SIG, ()),
        "merged_on_recovered": classify_process(None,
                                                "TIMEOUT after 2 seconds",
                                                out + er, 0, SIG, ()),
        "verdict_exists": True}
    proc.kill()
    proc.wait(timeout=3)
except UnicodeDecodeError as exc:
    ph["ff_then_hold"] = {"result": "UnicodeDecodeError-despite-timeout",
                          "exception": str(exc), "verdict_exists": False}
    proc.kill()
    proc.wait(timeout=3)
OUT["phases"]["edge4_unicode"] = ph


# ============ EDGE 5: drain-order sensitivity ===============================
ph = {}
# Same logical bytes, different temporal order across the two pipes. The
# merged concat is positional (stdout bytes then stderr bytes), so the ONLY
# cross-channel seam is stdout-tail|stderr-head regardless of write timing.
T5, H5 = "BOUNDARY drain tail ends in ERROR", ": BOUNDARY drain phantom"
for label, pycode in [
        ("stderr_first_then_stdout",
         "import sys,time; sys.stderr.write(%r+'\\n'); sys.stderr.flush(); "
         "time.sleep(0.3); sys.stdout.write(%r+'\\n'); sys.stdout.write(%r); "
         "sys.stdout.flush()" % (H5, SIG, T5)),
        ("stdout_tail_then_stderr",
         "import sys,time; sys.stdout.write(%r+'\\n'); sys.stdout.write(%r); "
         "sys.stdout.flush(); time.sleep(0.3); sys.stderr.write(%r+'\\n'); "
         "sys.stderr.flush()" % (SIG, T5, H5)),
        ("interleaved",
         "import sys; sys.stdout.write(%r+'\\n'); sys.stdout.flush(); "
         "sys.stderr.write('pre\\n'); sys.stderr.flush(); "
         "sys.stdout.write(%r); sys.stdout.flush(); "
         "sys.stderr.write(%r+'\\n'); sys.stderr.flush()" % (SIG, T5, H5))]:
    outs = []
    for rep in range(3):
        so, se, code, err = py(pycode)
        merged = so + se
        outs.append({"rep": rep, "phantom_in_merged":
                     (T5 + H5) in merged.splitlines(),
                     "merged_tail_lines": merged.splitlines()[-2:],
                     "streams": classify_streams(code, err, so, se, 0, SIG,
                                                 (H5,)),
                     "merged": classify_process(code, err, merged, 0, SIG, ())})
    ph[label] = outs
# post-death ordering: descendant writes the stderr HEAD after child death
# while the child already left the unterminated stdout tail — the
# fabrication survives full temporal separation (r66 seamforge shape).
so, se, code, err = sh(
    "printf '%s\\n'; printf '%s'; "
    "(while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"$$\" ]; "
    "do sleep 0.05; done; printf '%s\\n' >&2) & exit 0"
    % (SIG, T5, H5))
ph["postdeath_stderr_head"] = {
    "phantom_in_merged": (T5 + H5) in (so + se).splitlines(),
    "merged_tail_lines": (so + se).splitlines()[-2:],
    "streams_bare": classify_streams(code, err, so, se, 0, SIG, ()),
    "streams_head_allowlisted": classify_streams(code, err, so, se, 0, SIG,
                                                 (H5,)),
    "merged": classify_process(code, err, so + se, 0, SIG, ())}
# >64KiB concurrent drain: stdout and stderr both exceed the pipe buffer so
# communicate() must interleave reads; byte order per fd is preserved, the
# seam geometry is concat-fixed regardless of drain scheduling.
so, se, code, err = py(
    "import sys; sys.stdout.write(%r+'\\n'); sys.stdout.write('x'*200000); "
    "sys.stdout.write(%r); sys.stdout.flush(); "
    "sys.stderr.write(%r+'\\n'); sys.stderr.write('y'*150000+'\\n'); "
    "sys.stderr.flush()" % (SIG, T5, H5))
ph["bulk_drain_64k"] = {
    "stdout_bytes": len(so), "stderr_bytes": len(se),
    "stderr_head": se.splitlines()[0],
    "stdout_lastline_tail": so.splitlines()[-1][-60:],
    "phantom_substring_in_merged": any(
        (T5 + H5) in l for l in (so + se).splitlines()),
    "streams": classify_streams(code, err, so, se, 0, SIG,
                                (H5, "y" * 150000)),
    "merged": classify_process(code, err, so + se, 0, SIG, ())}
OUT["phases"]["edge5_drain"] = ph

(HERE / "boundary-verdicts.json").write_text(json.dumps(OUT, indent=2) + "\n")
print(json.dumps({"runner_sha": OUT["runner_sha"][:16],
                  "git_head": OUT["git_head"][:10],
                  "edge1_landed": landed,
                  "replay": {k: {"rows": a.get("rows"),
                                 "mismatches": len(a.get("mismatches", []))}
                             for k, a in OUT["replay_anchor"].items()}},
                 indent=2))
print("wrote", HERE / "boundary-verdicts.json")
