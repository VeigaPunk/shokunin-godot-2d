#!/usr/bin/env python3
"""r66 boundary phase-2: the AUTHOR-LANDED surface arms
(--spawn-allowforge/-splitforge/-seamforge/-midlineforge) driven through
VERBATIM-extracted production functions from the working-tree runner —
independent reproduction of probe_error_clause_surface discriminations
plus the boundary-seat edge measurements on the real arms.

Same method as drive_surface.py: ast.get_source_segment -> exec; verdicts
always from verbatim classify_process/classify_streams. Scratch-only.
"""
import ast
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import selectors

EDGE = Path(__file__).resolve().parent
REPO = EDGE.parents[1]
RUNNER = REPO / "fixtures" / "run_battery.py"
PROJ = EDGE / "proj_landed"
RAW = EDGE / "raw_landed"
RAW.mkdir(exist_ok=True)
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
ALLOWFORGE_ERROR = ("ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected "
                    "signature=JSON_PARSE_ERROR")
SPLIT_TAIL = "OR: DESCENDANT_PIPE_SPLITFORGE newline-split diagnostic"
SEAM_TAIL = "DESCENDANT_PIPE_SEAMFORGE tail ends in ERROR"
SEAM_HEAD = ": SEAMFORGE phantom fabricated line"
MID_ERROR = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"
GODOT = "godot"
REAP_TOKENS = (b"ALLOWFORGE", b"SPLITFORGE", b"SEAMFORGE", b"MIDLINE",
               b"ERRFORGE", b"FORGE write_ppid")

src = RUNNER.read_text()
tree = ast.parse(src)
runner_sha = hashlib.sha256(src.encode()).hexdigest()
ns = {"subprocess": subprocess, "selectors": selectors, "os": os, "re": re,
      "time": time, "signal": signal, "datetime": __import__("datetime").datetime,
      "args": SimpleNamespace(godot=GODOT), "scratch": PROJ,
      "gate_marker": MARKER, "gate_bound": 3.0, "gate_poll_tick": 0.005}
wanted = {"run_process", "classify_process", "classify_streams", "pid_alive",
          "kernel_ppid", "gated_signature_run"}
found = set()
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        exec(ast.get_source_segment(src, node), ns)
        found.add(node.name)
assert not (wanted - found)
run_process = ns["run_process"]
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]
pid_alive = ns["pid_alive"]
kernel_ppid = ns["kernel_ppid"]
gated_signature_run = ns["gated_signature_run"]


def cmd_for(extra):
    return [GODOT, "--headless", "--path", str(PROJ), "--script",
            "res://descendant_pipe_probe.gd", "--"] + list(extra)


def safe_reap(pid):
    if pid is None or not pid_alive(pid):
        return False
    try:
        cl = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return False
    if not any(t in cl for t in REAP_TOKENS):
        return False
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except OSError:
        return False


def comm_run(case, extra, bound=8.0, allowed_errors=(), expected_exit=0,
             signature=MARKER):
    started = time.monotonic()
    output, code, error = run_process(cmd_for(extra), bound)
    rec = {"case": case, "flags": list(extra), "bound": bound,
           "actual_exit": code, "error": error,
           "elapsed_seconds": round(time.monotonic() - started, 3),
           "signature_observed": signature in output,
           "error_lines": sorted({l.strip() for l in output.splitlines()
                                  if "ERROR:" in l}),
           "output_lines": output.strip().splitlines(),
           "classification_under_given_allowlist": classify_process(
               code, error, output, expected_exit, signature, allowed_errors),
           "classification_bare": classify_process(
               code, error, output, expected_exit, signature, ()),
           "output": output}
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", output)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", output)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"write_ppid=(\d+)", output)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["descendant_reaped_by_driver"] = safe_reap(rec["descendant_pid"])
    (RAW / f"{case}.merged").write_text(output)
    return rec


def streams_run(case, extra, bound=8.0):
    try:
        proc = subprocess.run(cmd_for(extra), capture_output=True, text=True,
                              timeout=bound)
        out, err, code, error = proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        code, error = None, f"TIMEOUT after {bound} seconds"
    rec = {"case": case, "flags": list(extra), "actual_exit": code,
           "error": error,
           "stdout_lines": out.strip().splitlines(),
           "stderr_lines": err.strip().splitlines(),
           "stdout_tail_line": (out.strip().splitlines()[-1].strip()
                                if out.strip() else None),
           "stderr_head_line": (err.strip().splitlines()[0].strip()
                                if err.strip() else None),
           "seam_fabricated_in_stdout": (SEAM_TAIL + SEAM_HEAD) in out,
           "seam_fabricated_in_stderr": (SEAM_TAIL + SEAM_HEAD) in err,
           "streams_classification": classify_streams(
               code, error, out, err, 0, MARKER),
           "merged_classification": classify_process(
               code, error, out + err, 0, MARKER)}
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", out + err)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    rec["descendant_reaped_by_driver"] = safe_reap(rec["descendant_pid"])
    (RAW / f"{case}.out").write_text(out)
    (RAW / f"{case}.err").write_text(err)
    return rec


def main():
    results = {"runner_sha256": runner_sha,
               "landed_fixture_sha256": hashlib.sha256(
                   (PROJ / "descendant_pipe_probe.gd").read_bytes()).hexdigest(),
               "runs": []}

    # (a) allowlist preemptor — the author's exact arm, verbatim classifiers
    for tag, allow, sig in [
            ("comm_allowforge_bare", (), MARKER),
            ("comm_allowforge_matched", (ALLOWFORGE_ERROR,), MARKER),
            ("comm_allowforge_foreign",
             ("ERROR: unrelated different diagnostic",), MARKER)]:
        # one real run, classified three ways — reuse the same capture
        pass
    rec0 = comm_run("allowforge_capture", ["--spawn-allowforge"])
    results["runs"].append(rec0)
    txt = rec0["output"]
    stripped = "\n".join(l for l in txt.splitlines() if "ERROR:" not in l)
    results["allowforge_verdict_map"] = {
        "bare_rejects": classify_process(0, None, txt, 0, MARKER, ()) is False,
        "matched_absorbs": classify_process(
            0, None, txt, 0, MARKER, (ALLOWFORGE_ERROR,)) is True,
        "foreign_rejects": classify_process(
            0, None, txt, 0, MARKER,
            ("ERROR: unrelated different diagnostic",)) is False,
        "stripped_counterfactual_passes": classify_process(
            0, None, stripped, 0, MARKER, ()) is True,
        "write_post_orphan": (rec0["write_ppid"] is not None
                              and rec0["godot_pid"] is not None
                              and rec0["write_ppid"] != rec0["godot_pid"]),
        "error_lines_exact": rec0["error_lines"] == [ALLOWFORGE_ERROR]}
    print("[landed-a]", json.dumps(results["allowforge_verdict_map"]),
          flush=True)

    # (c) splitforge — line-local-scan evasion, real run + contiguous twin
    rec1 = comm_run("splitforge_capture", ["--spawn-splitforge"])
    results["runs"].append(rec1)
    txt1 = rec1["output"]
    contiguous_twin = txt1.replace("ERR\nOR:", "ERROR:")
    results["splitforge_map"] = {
        "clean_exit0": rec1["actual_exit"] == 0 and rec1["error"] is None,
        "signature_present": rec1["signature_observed"],
        "forged_bytes_in_record": ("ERR" in txt1.splitlines()
                                   and SPLIT_TAIL in
                                   [l.strip() for l in txt1.splitlines()]),
        "no_error_line": rec1["error_lines"] == [],
        "evades_merged_scan": rec1["classification_bare"] is True,
        "contiguous_twin_rejects": classify_process(
            0, None, contiguous_twin, 0, MARKER, ()) is False,
        "write_post_orphan": (rec1["write_ppid"] is not None
                              and rec1["godot_pid"] is not None
                              and rec1["write_ppid"] != rec1["godot_pid"])}
    print("[landed-c-split]", json.dumps(results["splitforge_map"]),
          flush=True)

    # (c) seamforge — merged-run fabrication + split-stream non-existence
    rec2 = comm_run("seamforge_capture", ["--spawn-seamforge"])
    rec2s = streams_run("seamforge_split_capture", ["--spawn-seamforge"])
    results["runs"] += [rec2, rec2s]
    fabricated = SEAM_TAIL + SEAM_HEAD
    results["seamforge_map"] = {
        "clean_exit0": rec2["actual_exit"] == 0 and rec2["error"] is None,
        "fabricated_line_in_merged": any(
            l.strip() == fabricated for l in rec2["output_lines"]),
        "merged_rejects": rec2["classification_bare"] is False,
        "line_in_neither_stream": (
            not rec2s["seam_fabricated_in_stdout"]
            and not rec2s["seam_fabricated_in_stderr"]
            and rec2s["stdout_tail_line"] == SEAM_TAIL
            and rec2s["stderr_head_line"] == SEAM_HEAD),
        "split_run_merged_also_rejects": rec2s["merged_classification"] is False,
        "split_run_streams_classification": rec2s["streams_classification"],
        "stderr_lines": rec2s["stderr_lines"],
        "write_post_orphan": (rec2["write_ppid"] is not None
                              and rec2["godot_pid"] is not None
                              and rec2["write_ppid"] != rec2["godot_pid"])}
    print("[landed-c-seam]", json.dumps(results["seamforge_map"]), flush=True)

    # (c) midlineforge — pre-death splice; 3 reps for race stability
    mid = []
    for i in range(3):
        rec3 = comm_run(f"midlineforge_r{i}", ["--spawn-midlineforge"])
        results["runs"].append(rec3)
        spliced = [l for l in rec3["output_lines"]
                   if "DESCENDANT_PIPE_PROBE: expected " in l
                   and MID_ERROR in l]
        stripped3 = "\n".join(l for l in rec3["output"].splitlines()
                              if "ERROR:" not in l)
        mid.append({
            "rep": i,
            "spliced_line": spliced,
            "signature_destroyed": not rec3["signature_observed"],
            "rejects": rec3["classification_bare"] is False,
            "counterfactual_defeated": classify_process(
                0, None, stripped3, 0, MARKER, ()) is False,
            "write_pre_death": (rec3["write_ppid"] is not None
                                and rec3["godot_pid"] is not None
                                and rec3["write_ppid"] == rec3["godot_pid"]),
            "write_ppid": rec3["write_ppid"],
            "godot_pid": rec3["godot_pid"]})
        print(f"[landed-c-mid r{i}] spliced={bool(spliced)} "
              f"sig_destroyed={mid[-1]['signature_destroyed']} "
              f"pre_death={mid[-1]['write_pre_death']}", flush=True)
    results["midlineforge_reps"] = mid

    # boundary extras on the landed arms:
    # - splitforge through classify_streams (stdout chatter invisible there)
    rec4 = streams_run("splitforge_streams", ["--spawn-splitforge"])
    results["runs"].append(rec4)
    # - allowforge through streams (the save line on stdout: streams blind)
    rec5 = streams_run("allowforge_streams", ["--spawn-allowforge"])
    results["runs"].append(rec5)
    # - seamforge under the verbatim while-live gate
    rec6 = gated_signature_run("vg_seamforge", ["--spawn-seamforge"])
    rec6["clauses_sig_destroyed"] = rec6["marker_observed"] is False
    rec6["descendant_reaped_by_driver"] = safe_reap(rec6.get("descendant_pid"))
    rec6.pop("command", None)
    results["runs"].append(rec6)
    results["extras"] = {
        "splitforge_streams_accept": rec4["streams_classification"],
        "splitforge_merged_accept": rec4["merged_classification"],
        "allowforge_streams_accept": rec5["streams_classification"],
        "allowforge_merged_rejects": rec5["merged_classification"],
        "seamforge_gate_sig_observed": rec6["marker_observed"],
        "seamforge_gate_accepted": rec6["gated_signature_accepted"],
        "seamforge_inner_classification": rec6["inner_classification"]}
    print("[landed-extras]", json.dumps(results["extras"]), flush=True)

    out_path = EDGE / "landed-verdicts.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n")
    print("wrote", out_path, flush=True)


if __name__ == "__main__":
    sys.exit(main())
