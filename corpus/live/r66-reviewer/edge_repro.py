#!/usr/bin/env python3
"""r66 reviewer: independent reproduction of the three r65-boundary edges.

Verbatim-extracts the production run_process / classify_process /
classify_streams functions from the COMMITTED corpus/fixtures/run_battery.py
(ast.get_source_segment + exec — same method as the r65 boundary seat, so the
clause under test is the shipped one, not a retype).

Edges under test (all against the committed runner bytes sha cd4824cc...):
  A. newline-split evasion  — post-death 'ERR\n' + 'OR: ...' writes: the forged
     bytes are in the merged capture yet NO line contains 'ERROR:' -> the
     line-local scan classifies True (evades). Control: '--spawn-errforge-split'
     (no newline) reassembles contiguously -> detected (False); stock
     '--spawn-errforge-release' -> detected (False).
  B. allowlist admittance — post-death echo of save_corrupt_negative's exact
     allowlisted line: un-allowlisted classification rejects (False); the same
     captured record classified WITH that allowlist entry admits (True).
  C. reader-drain surface — bounded post-death pump >64KiB drains completely
     under communicate (run_process); stalled reader leaves the descendant
     family blocked in pipe write (wchan /proc evidence); reader close kills
     the unbounded pumper via SIGPIPE.
"""
import ast
import fcntl
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
RUNNER = REPO / "corpus" / "fixtures" / "run_battery.py"
SCRATCH = REPO / "corpus" / "live" / "r66-reviewer"
PROJ_EDGE_SRC = REPO / "corpus" / "live" / "r65-boundary" / "proj_edge"
PROJ_STOCK_SRC = REPO / "corpus" / "live" / "r65-boundary" / "proj_stock"
GODOT = "/usr/bin/godot"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
SAVE_ALLOW = "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR"

OUT = {}


def extract_production():
    """exec the verbatim source of the runner's nested classifier functions."""
    src = RUNNER.read_text()
    tree = ast.parse(src)
    segs = {}
    wanted = {"run_process", "classify_process", "classify_streams"}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in wanted:
            segs[node.name] = ast.get_source_segment(src, node)
    missing = wanted - segs.keys()
    assert not missing, f"missing functions: {missing}"
    # dependency order: classify_streams is self-contained; all three need
    # subprocess (imported inside run_process? no — module-level import)
    ns = {"subprocess": subprocess, "re": re}
    for name in ("run_process", "classify_process", "classify_streams"):
        exec(segs[name], ns)
    # fingerprint: sha of the exact segments we executed
    import hashlib
    fp = {k: hashlib.sha256(v.encode()).hexdigest()[:16] for k, v in segs.items()}
    return ns, fp


def godot_cmd(proj, arm_args):
    return [GODOT, "--headless", "--path", str(proj),
            "--script", "res://descendant_pipe_probe.gd", "--"] + arm_args


def run_case(ns, proj, arm_args, allowed=(), bound=12.0):
    """run through the verbatim production run_process + classify_process."""
    cmd = godot_cmd(proj, arm_args)
    t0 = time.monotonic()
    output, code, error = ns["run_process"](cmd, bound)
    elapsed = time.monotonic() - t0
    cls = ns["classify_process"](code, error, output, 0, MARKER, allowed)
    return {"cmd_tail": arm_args, "elapsed": round(elapsed, 3), "exit": code,
            "error": error, "bytes": len(output.encode()),
            "classification": cls,
            "output_lines": output.splitlines()}


def lines_with_error(output_lines):
    return [ln for ln in output_lines if "ERROR:" in ln]


def proc_find(token):
    """pids whose /proc cmdline carries the fixture-unique token."""
    found = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            cl = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if token in cl:
            found.append(int(p.name))
    return found


def proc_state(pid):
    try:
        stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        state, ppid = stat[0], int(stat[1])
    except OSError:
        return None
    try:
        wchan = Path(f"/proc/{pid}/wchan").read_text().strip()
    except OSError:
        wchan = "?"
    try:
        comm = Path(f"/proc/{pid}/comm").read_text().strip()
    except OSError:
        comm = "?"
    return {"state": state, "ppid": ppid, "wchan": wchan, "comm": comm}


def main():
    ns, fp = extract_production()
    OUT["function_sha16"] = fp
    import hashlib
    OUT["runner_sha256"] = hashlib.sha256(RUNNER.read_bytes()).hexdigest()

    # scratch copies so godot .godot/ writes stay inside my write scope
    proj_edge = SCRATCH / "proj_edge"
    proj_stock = SCRATCH / "proj_stock"
    for src_dir, dst in ((PROJ_EDGE_SRC, proj_edge), (PROJ_STOCK_SRC, proj_stock)):
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src_dir, dst)
    edge_fixture_sha = hashlib.sha256(
        (proj_edge / "descendant_pipe_probe.gd").read_bytes()).hexdigest()
    OUT["edge_fixture_sha256"] = edge_fixture_sha  # expect dded5056...

    # ---------- Edge A: newline-split evasion ----------
    a = {}
    a["newlinesplit"] = run_case(ns, proj_edge, ["--spawn-errforge-newlinesplit"])
    a["split_control"] = run_case(ns, proj_edge, ["--spawn-errforge-split"])
    a["stock_release_control"] = run_case(ns, proj_stock, ["--spawn-errforge-release"])
    # per-line scan evidence on the evading record
    nls_lines = a["newlinesplit"]["output_lines"]
    a["newlinesplit_forged_bytes_in_capture"] = (
        any(ln.strip() == "ERR" for ln in nls_lines)
        and any(ln.strip().startswith("OR: FORGED_DESCENDANT_ERROR") for ln in nls_lines))
    a["newlinesplit_error_lines"] = lines_with_error(nls_lines)
    OUT["edge_A_newline_split"] = a

    # ---------- Edge B: allowlist admittance ----------
    b = {}
    rec = run_case(ns, proj_edge, ["--spawn-errforge-allowlisted"])
    b["no_allowlist"] = rec
    b["with_save_allowlist"] = {
        **rec,
        "classification": ns["classify_process"](
            rec["exit"], rec["error"], "\n".join(rec["output_lines"]),
            0, MARKER, (SAVE_ALLOW,))}
    b["ppid_lines"] = [ln for ln in rec["output_lines"] if "write_ppid" in ln]
    OUT["edge_B_allowlist"] = b

    # ---------- Edge C1: bounded pump drains fully under communicate ----------
    c1 = run_case(ns, proj_edge, ["--spawn-errforge-pipefull", "--pump-kb=512"], bound=20.0)
    c1["error_line_count"] = len(lines_with_error(c1["output_lines"]))
    OUT["edge_C1_bounded_pump_drains"] = c1

    # ---------- Edge C2: stalled reader -> writer blocks; drain -> completes ----------
    c2 = {"arm": "--spawn-errforge-pipefull --pump-kb=512 (Popen, stalled reader)"}
    proc = subprocess.Popen(godot_cmd(proj_edge, ["--spawn-errforge-pipefull", "--pump-kb=512"]),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    godot_rc = proc.wait()          # godot exits; descendant still pumping
    c2["godot_exit"] = godot_rc
    time.sleep(1.2)                 # reparenting gate opens; pump fills 64K
    fam = proc_find("FORGED_DESCENDANT_ERROR")
    c2["stalled_family"] = {pid: proc_state(pid) for pid in fam}
    c2["stalled_family_blocked"] = all(
        (s := proc_state(pid)) and s["state"] == "S" for pid in fam)
    t0 = time.monotonic()
    out, err = proc.communicate(timeout=15)   # now drain
    c2["drain_seconds"] = round(time.monotonic() - t0, 3)
    merged = out + err
    c2["captured_bytes"] = len(merged)
    c2["captured_error_lines"] = sum(1 for ln in merged.splitlines() if b"ERROR:" in ln)
    c2["post_drain_family"] = proc_find("FORGED_DESCENDANT_ERROR")
    c2["marker_present"] = MARKER.encode() in merged
    OUT["edge_C2_stall_then_drain"] = c2

    # ---------- Edge C3: stalled reader + close -> SIGPIPE kills unbounded pump ----------
    c3 = {"arm": "--spawn-errforge-pipefull-hold (unbounded yes; close read ends)"}
    proc = subprocess.Popen(godot_cmd(proj_edge, ["--spawn-errforge-pipefull-hold"]),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    c3["godot_exit"] = proc.returncode
    time.sleep(1.2)
    fam = proc_find("FORGED_DESCENDANT_ERROR")
    c3["stalled_family"] = {pid: proc_state(pid) for pid in fam}
    proc.stdout.close()
    proc.stderr.close()
    time.sleep(0.7)
    c3["family_after_close"] = proc_find("FORGED_DESCENDANT_ERROR")
    c3["family_states_after_close"] = {
        pid: proc_state(pid) for pid in c3["family_after_close"]}
    OUT["edge_C3_stall_then_close_sigpipe"] = c3

    # ---------- summary ----------
    evade = (a["newlinesplit"]["classification"] is True
             and a["newlinesplit_forged_bytes_in_capture"]
             and not a["newlinesplit_error_lines"])
    detected = (a["split_control"]["classification"] is False
                and a["stock_release_control"]["classification"] is False)
    allow = (b["no_allowlist"]["classification"] is False
             and b["with_save_allowlist"]["classification"] is True)
    drain = (c1["bytes"] >= 512 * 1024 and c1["classification"] is False
             and c2["captured_bytes"] >= 512 * 1024)
    blocked = c2["stalled_family_blocked"] and len(c2["stalled_family"]) > 0
    sigpipe = len(c3["family_after_close"]) == 0 and len(c3["stalled_family"]) > 0
    OUT["reproduction"] = {
        "A_newline_split_evades": evade,
        "A_controls_detect": detected,
        "B_allowlist_admits": allow,
        "C1_bounded_pump_fully_drained": drain,
        "C2_writer_blocked_while_stalled": blocked,
        "C3_close_sigpipes_unbounded_writer": sigpipe,
    }
    (SCRATCH / "edge-repro.json").write_text(json.dumps(OUT, indent=2, default=str))
    print(json.dumps(OUT["reproduction"], indent=2))
    print("ALL_EDGES_REPRODUCED" if all(OUT["reproduction"].values()) else "SOME_EDGE_FAILED")


if __name__ == "__main__":
    main()
