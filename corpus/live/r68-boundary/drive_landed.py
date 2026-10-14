#!/usr/bin/env python3
"""r68 boundary phase 3 — post-landing probes on the author's diff.

(a) Landed-arm edge sweep through --midline-offset-ms (offsets beyond the
    author ladder: negative, sub-ladder, jitter reps at the hi edge).
(b) divergent_clause collision cells: synthetic (so,se) pairs through the
    VERBATIM landed divergent_clause + both real classifiers; compare the
    emitted label set against the independently-derived differing-clause set.
(c) sha256 same-input gate edge cells: empty stream, absent stream,
    decode-replace byte collisions, None handling.
"""
import ast, hashlib, json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path.home() / "Projects/shokunin/game-dev-2d-shokunin"
RUNNER = ROOT / "corpus/fixtures/run_battery.py"
OUT = ROOT / "corpus/live/r68-boundary"
PROJ = OUT / "proj"
RAW = OUT / "raw"
GODOT = "/usr/bin/godot"
SIG_TRACKED = "DESCENDANT_PIPE_PROBE: expected signature"
SIG = "STREAM_STDOUT: expected attribution marker"  # stdout_sig of the arm

src = RUNNER.read_text()
tree = ast.parse(src)

def extract(fn):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn:
            return ast.get_source_segment(src, node)
    return None

ns = {"__name__": "b", "hashlib": hashlib}
shas = {}
for fn in ("classify_process", "classify_streams",
           "sd_merged_line_allowed", "sd_stream_line_allowed",
           "divergent_clause", "dual_classify"):
    seg = extract(fn)
    shas[fn] = hashlib.sha256(seg.encode()).hexdigest() if seg else None
    if seg:
        exec(compile(seg, fn, "exec"), ns)
ns["stdout_sig"] = SIG
# dual_classify references classify_* and stdout_sig; divergent_clause
# references the mirrors + stdout_sig — rebind into their globals.
for fn in ("dual_classify", "divergent_clause"):
    ns[fn].__globals__["stdout_sig"] = SIG

classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]
divergent_clause = ns["divergent_clause"]
dual_classify = ns["dual_classify"]
merged_allowed_fn = ns["sd_merged_line_allowed"]
stream_allowed_fn = ns["sd_stream_line_allowed"]

out = {"runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
       "fixture_sha256": hashlib.sha256(
           (ROOT / "corpus/fixtures/descendant_pipe_probe.gd").read_bytes()).hexdigest(),
       "function_shas": shas, "phases": {}}

# ---------- (a) landed-arm edges ----------
def landed_run(offset_ms, rep, extra_flags=()):
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://descendant_pipe_probe.gd", "--", "--spawn-midlineforge",
           f"--midline-offset-ms={offset_ms}"] + list(extra_flags)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
    so, se = p.stdout or "", p.stderr or ""
    merged = so + se
    lines = merged.splitlines()
    spliced = next((l.strip() for l in lines
                    if "DESCENDANT_PIPE_PROBE: expected " in l
                    and "ERROR: DESCENDANT_PIPE_MIDLINE forged splice" in l), None)
    m = re.search(r"godot_pid=(\d+)", merged)
    w = re.search(r"write_ppid=(\d+)", merged)
    rec = {"off": offset_ms, "rep": rep, "exit": p.returncode,
           "spliced": spliced is not None, "spliced_line": spliced,
           "sig_intact": SIG_TRACKED in merged,
           "godot_pid": int(m.group(1)) if m else None,
           "write_ppid": int(w.group(1)) if w else None,
           "merged_cls": classify_process(p.returncode, None, merged, 0,
                                          SIG_TRACKED)}
    rec["pre_death"] = (rec["write_ppid"] is not None
                        and rec["write_ppid"] == rec["godot_pid"])
    if rep == 0:
        (RAW / f"landed_off{offset_ms}.stdout").write_text(so)
        (RAW / f"landed_off{offset_ms}.stderr").write_text(se)
    return rec

p3a = {"offsets": {}}
for off in (-500, -50, -1, 0, 20, 160, 180, 190, 195, 196, 197, 198, 199,
            200, 201, 205, 240, 300, 800):
    reps = [landed_run(off, i) for i in range(3)]
    p3a["offsets"][str(off)] = [
        {"spliced": r["spliced"], "sig": r["sig_intact"],
         "pre_death": r["pre_death"], "merged": r["merged_cls"]} for r in reps]
out["phases"]["p3a_landed_edges"] = p3a

# ---------- (b) divergent_clause collision cells ----------
def true_clause_diffs(so, se, merged_allowed=(), stream_allowed=()):
    """Independent clause-by-clause verdict diff on the same streams."""
    merged_text = so + se
    diffs = set()
    # signature clause
    if (SIG in merged_text) != (SIG in so):
        diffs.add("signature")
    # blob clause
    mb = ("SCRIPT ERROR:" in merged_text or "Parse Error:" in merged_text)
    sb = any(t in so or t in se for t in ("SCRIPT ERROR:", "Parse Error:"))
    if mb != sb:
        diffs.add("blob")
    # scan/audit clause
    mrej = [l for l in merged_text.splitlines()
            if "ERROR:" in l
            and not any(merged_allowed_fn(l, a) for a in merged_allowed)]
    srej = [s for s in (l.strip() for l in se.splitlines())
            if s and not stream_allowed_fn(s, stream_allowed)]
    if bool(mrej) != bool(srej):
        # author's disambiguator
        if (srej and all("ERROR:" in l and any(merged_allowed_fn(l, a)
                                             for a in merged_allowed)
                         for l in srej)):
            diffs.add("allowlist_shape")
        else:
            diffs.add("error_scan")
        # my extension: detect masked allowlist_shape — at least one
        # stream-rejected line is a merged-absorbable ERROR: line while
        # another is not -> BOTH mechanisms diverged
        absorbed_err = [l for l in srej
                        if "ERROR:" in l
                        and any(merged_allowed_fn(l, a) for a in merged_allowed)]
        other = [l for l in srej if l not in absorbed_err]
        if absorbed_err and other:
            diffs.add("allowlist_shape+error_scan_MASKED")
    return diffs

def cell(name, so, se, ma=(), sa=()):
    d = dual_classify(so, se, 0, None, ma, sa)
    return {"merged": d["merged_classification"],
            "streams": d["stream_classification"],
            "divergent": d["divergent"],
            "landed_label": d["divergent_clause"],
            "true_diffs": sorted(true_clause_diffs(so, se, ma, sa)),
            "sha_out": d["raw_stdout_sha256"], "sha_err": d["raw_stderr_sha256"]}

SIGL = SIG
STRUCT_ENTRY = "ERROR: chain incomplete"
STRUCT_LINE = ("ERROR: chain incomplete collections=1 "
               "scene=SceneB:<Node#7> old_alive=false")
H = "Godot Engine v4.7.2 banner\n"

cells = {}
# baseline conformance: replay the author's arm shapes synthetically
cells["c_stdout_error"] = cell("stdout_error",
    H + SIGL + "\nERROR: STREAMDIV stdout-carried diagnostic\n", "")
cells["c_seam_error_allowlisted"] = cell("seam_err",
    H + "STREAMDIV seam tail ends in ERROR", ": STREAMDIV seam phantom\n",
    (), (": STREAMDIV seam phantom",))
cells["c_stderr_chatter"] = cell("chatter",
    H + SIGL + "\n", "STREAM_STDERR: unrelated attribution diagnostic\n")
cells["c_structured_entry"] = cell("struct",
    H + SIGL + "\n", STRUCT_LINE + "\n", (STRUCT_ENTRY,), (STRUCT_ENTRY,))
cells["c_sig_on_stderr_allowlisted"] = cell("sig_err",
    H, SIGL + "\n", (), (SIGL,))
cells["c_seam_sig"] = cell("seam_sig",
    H + "STREAM_STDOUT: expected attribution ", "marker\n", (), ("marker",))
# --- collision cells ---
# distinct mechanisms, same label: stdout-error vs seam-error vs chatter
# all -> ["error_scan"]. sig_on_stderr vs seam_sig -> ["signature"].
# masked allowlist_shape: structured line + chatter coexist
cells["x_masked_allowlist"] = cell("masked",
    H + SIGL + "\n", STRUCT_LINE + "\nnote: plain chatter\n",
    (STRUCT_ENTRY,), ())
# same mixed row, chatter also absorbed -> pure allowlist_shape?
cells["x_mixed_partial"] = cell("mixed_partial",
    H + SIGL + "\n", STRUCT_LINE + "\nnote: plain chatter\n",
    (STRUCT_ENTRY,), ("note: plain chatter",))
# concordant verdict with nonempty clause signature
cells["x_concordant_with_clause_diffs"] = cell("concordant_diffs",
    H + "ERROR: x\n", SIGL + "\n")
# seam fabricating Parse Error (no "ERROR:" substring) vs SCRIPT ERROR
cells["x_seam_parse"] = cell("seam_parse",
    H + SIGL + "\nseam tail ends in Parse Err", "or: forged\n", (), ("or: forged",))
cells["x_seam_script"] = cell("seam_script",
    H + SIGL + "\nseam tail ends in SCRIPT ERR", "OR: forged\n", (), ("OR: forged",))
# stdout ERROR: + signature absent -> merged rejects, streams rejects(sig)
cells["x_stdout_err_no_sig"] = cell("err_no_sig",
    H + "ERROR: x\n", "chatter\n")
# dual divergence: sig-on-stderr BARE (unallowlisted sig line on stderr)
cells["x_sig_stderr_bare"] = cell("sig_bare", H, SIGL + "\n")
# stderr ERROR: absorbed by merged comma-entry but streams-rejected? comma
# exists in both grammars -> concordant control
cells["x_comma_entry"] = cell("comma",
    H + SIGL + "\n", "ERROR: PREFIX, tail=1\n", ("ERROR: PREFIX,",), ("ERROR: PREFIX,",))
# count==2 ERROR: line under comma entry -> both reject?
cells["x_count2"] = cell("count2",
    H + SIGL + "\n", "ERROR: PREFIX, a ERROR: b\n", ("ERROR: PREFIX,",), ("ERROR: PREFIX,",))
out["phases"]["p3b_divergent_clause_cells"] = cells

# collision matrix: group landed rows by label
groups = {}
for name, c in cells.items():
    key = tuple(c["landed_label"])
    groups.setdefault(key, []).append(name)
out["phases"]["p3b_label_groups"] = {str(k): v for k, v in groups.items()}

# ---------- (c) sha256 same-input gate edge cells ----------
p3c = {}
# c1: empty stream
d_empty = dual_classify("x\n" + SIGL + "\n", "", 0, None)
p3c["empty_stderr_sha"] = d_empty["raw_stderr_sha256"]
p3c["empty_stderr_is_e3b0"] = (d_empty["raw_stderr_sha256"] ==
    hashlib.sha256(b"").hexdigest())
# c2: absent stream (OSError path returns "" for stdout, str(exc) for stderr)
d_absent = dual_classify("", "launch error: boom", None, "launch error: boom")
p3c["absent_stdout_sha_is_empty_sha"] = (
    d_absent["raw_stdout_sha256"] == hashlib.sha256(b"").hexdigest())
# c3: decode-replace byte collisions — distinct raw bytes, identical decoded
# str -> identical recorded sha256: the gate binds TEXT, not BYTES.
b1 = b"prefix \xff tail\n"
b2 = b"prefix \xfe tail\n"
s1 = b1.decode(errors="replace")
s2 = b2.decode(errors="replace")
p3c["decode_replace_collision"] = {
    "raw_bytes_distinct": b1 != b2,
    "decoded_equal": s1 == s2,
    "sha_equal": (hashlib.sha256(s1.encode()).hexdigest()
                  == hashlib.sha256(s2.encode()).hexdigest()),
    "sha": hashlib.sha256(s1.encode()).hexdigest()}
# c4: strict-decode path — invalid UTF-8 never reaches the gate (DoV class)
p3c["strict_decode_no_record"] = None
try:
    subprocess.run([sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\xff')"],
                   capture_output=True, text=True, timeout=5)
    p3c["strict_decode_no_record"] = "decoded?!"
except UnicodeDecodeError as e:
    p3c["strict_decode_no_record"] = f"UnicodeDecodeError: {e}"
except Exception as e:
    p3c["strict_decode_no_record"] = f"{type(e).__name__}: {e}"
# c5: surrogate reachability — can a captured str carry lone surrogates?
# errors="replace" produces U+FFFD (encodable); surrogateescape would carry
# surrogates, but neither runner path uses it.
p3c["surrogate_encode_check"] = None
try:
    hashlib.sha256("x\udcff".encode()).hexdigest()
except UnicodeEncodeError as e:
    p3c["surrogate_encode_check"] = f"UnicodeEncodeError: {e}"
# c6: same-input gate semantics — sha proves same STR, and the recorded
# raw_* fields are re-verifiable from the record itself.
p3c["gate_semantics"] = ("sha256(record['raw_stdout'].encode()) recomputed "
    "by a reader equals raw_stdout_sha256 — gate binds the decoded text; "
    "byte-level provenance is unprovable under errors='replace' timeout decode")
out["phases"]["p3c_sha256_edges"] = p3c

(OUT / "landed-verdicts.json").write_text(json.dumps(out, indent=2) + "\n")
print("done", json.dumps(groups, indent=0))
