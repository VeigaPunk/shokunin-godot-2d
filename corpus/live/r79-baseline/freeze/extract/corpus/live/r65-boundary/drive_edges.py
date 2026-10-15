#!/usr/bin/env python3
"""r65 boundary edge driver: forged-REJECTION (post-death ERROR:) probes.

Verdict-path evidence comes from functions VERBATIM-EXTRACTED from the
working-tree runner (ast.get_source_segment -> exec): run_process,
classify_process, classify_streams, pid_alive, kernel_ppid, and the landed
r64 gated_signature_run. Rows tagged vg_*/comm_* run production code.

Instrumented replicas (timed_probe, stalled-reader consumers, stream-split
runner) are corroborating evidence; differences are disclosed in-record.

Writes only under corpus/live/r65-boundary/. Never touches tracked files.
"""
import ast
import fcntl
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

EDGE = Path(__file__).resolve().parent
RUNNER = EDGE.parents[1] / "fixtures" / "run_battery.py"
PROJ_EDGE = EDGE / "proj_edge"
PROJ_STOCK = EDGE / "proj_stock"
RAW = EDGE / "raw"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
ERRLINE = "ERROR: FORGED_DESCENDANT_ERROR injected diagnostic"
GODOT = "godot"

# ---------------------------------------------------------------- verbatim
src = RUNNER.read_text()
tree = ast.parse(src)
runner_sha = __import__("hashlib").sha256(src.encode()).hexdigest()

ns = {
    "subprocess": subprocess, "selectors": selectors, "os": os, "re": re,
    "time": time, "signal": signal, "datetime": datetime,
    "args": SimpleNamespace(godot=GODOT),
    "scratch": PROJ_EDGE, "gate_marker": MARKER, "gate_bound": 3.0,
    "gate_poll_tick": 0.005,
}
wanted = {"run_process", "classify_process", "classify_streams",
          "pid_alive", "kernel_ppid", "gated_signature_run"}
found = set()
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        exec(ast.get_source_segment(src, node), ns)
        found.add(node.name)
missing = wanted - found
assert not missing, f"extraction failed: {missing}"

run_process = ns["run_process"]
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]
pid_alive = ns["pid_alive"]
kernel_ppid = ns["kernel_ppid"]
gated_signature_run = ns["gated_signature_run"]

# ---------------------------------------------------------------- replicas
def cmd_for(proj, extra):
    return [GODOT, "--headless", "--path", str(proj), "--script",
            "res://descendant_pipe_probe.gd", "--"] + list(extra)

def comm_run(case, proj, extra, bound=8.0):
    """Verbatim run_process + classify_process (the CASES consumer path)."""
    started = time.monotonic()
    output, code, error = run_process(cmd_for(proj, extra), bound)
    rec = {"case": case, "consumer": "run_process+classify_process",
           "flags": list(extra), "bound": bound,
           "actual_exit": code, "error": error,
           "elapsed_seconds": round(time.monotonic() - started, 3),
           "output_bytes": len(output.encode(errors="replace")),
           "error_lines": sum(1 for l in output.splitlines() if "ERROR:" in l),
           "marker_present": MARKER in output,
           "clause_exit_match": code == 0, "clause_error_none": error is None,
           "clause_signature": MARKER in output,
           "inner_classification": classify_process(code, error, output, 0, MARKER),
           "output": output}
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", output)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", output)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"write_ppid=(\d+)", output)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["descendant_reaped_by_driver"] = safe_reap(rec["descendant_pid"])
    (RAW / f"{case}.stdout").write_text(output)
    return rec

def streams_run(case, proj, extra, bound=8.0):
    """Separate-stream consumer -> production classify_streams."""
    try:
        proc = subprocess.run(cmd_for(proj, extra), capture_output=True,
                              text=True, timeout=bound)
        out, err, code, error = proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        code, error = None, f"TIMEOUT after {bound} seconds"
    rec = {"case": case, "consumer": "subprocess.run + classify_streams",
           "flags": list(extra), "bound": bound, "actual_exit": code,
           "error": error, "marker_in_stdout": MARKER in out,
           "errline_in_stdout": ERRLINE in out,
           "errline_in_stderr": ERRLINE in err,
           "streams_classification": classify_streams(code, error, out, err, 0, MARKER),
           "merged_classification": classify_process(code, error, out + err, 0, MARKER),
           "stdout": out, "stderr": err}
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", out + err)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    rec["descendant_reaped_by_driver"] = safe_reap(rec["descendant_pid"])
    (RAW / f"{case}.out").write_text(out)
    (RAW / f"{case}.err").write_text(err)
    return rec

def timed_probe(case, proj, extra, bound=3.0, tick=0.005, pre_read_sleep=0.0,
                close_after_sleep=False, sample_pid_from=ERRLINE + "|" + "ERRFORGE"):
    """Instrumented gate-shaped consumer: poll()-gated select loop over both
    pipes, per-event (t, stream, alive_before, n) ledger, marker + first
    'ERROR:'-byte observation stamps, descendant state sampling during a
    pre-read stall (pipe-full probe)."""
    rec = {"case": case, "consumer": "timed_probe",
           "flags": list(extra), "bound": bound, "tick": tick,
           "pre_read_sleep": pre_read_sleep, "timed_out": False,
           "actual_exit": None, "error": None, "events": [],
           "marker_observed_at": None, "marker_alive_before": None,
           "err_first_at": None, "err_alive_before": None,
           "dead_observed_at": None, "descendant_samples": [],
           "bytes_stdout": 0, "bytes_stderr": 0}
    process = subprocess.Popen(cmd_for(proj, extra), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    rec["pipe_sz_stdout"] = fcntl.fcntl(process.stdout.fileno(), fcntl.F_GETPIPE_SZ)
    rec["pipe_sz_stderr"] = fcntl.fcntl(process.stderr.fileno(), fcntl.F_GETPIPE_SZ)
    started = time.monotonic()
    captured = bytearray()
    deadline = started + bound
    if pre_read_sleep > 0:
        # Stall the reader with the pipes OPEN: nobody drains. Sample the
        # whole descendant family (the sh plus any pipeline children — the
        # process actually blocked in write() is the pump child, not the sh).
        stall_end = started + pre_read_sleep
        while time.monotonic() < stall_end:
            family = find_family()
            if family and rec.get("descendant_pid") is None:
                rec["descendant_pid"] = family[0]
            for pid in family:
                try:
                    st = Path(f"/proc/{pid}/stat").read_text()
                    state = st.rsplit(")", 1)[1].split()[0]
                    wchan = Path(f"/proc/{pid}/wchan").read_text().strip()
                    try:
                        syscall = Path(f"/proc/{pid}/syscall").read_text().strip()
                    except OSError:
                        syscall = "unreadable"
                    comm = st[st.index("(") + 1:st.rindex(")")]
                    rec["descendant_samples"].append(
                        {"t": round(time.monotonic() - started, 4), "pid": pid,
                         "comm": comm, "state": state, "wchan": wchan,
                         "syscall": syscall})
                except OSError:
                    pass
            time.sleep(0.05)
        rec["child_state_after_stall"] = process.poll()
        if close_after_sleep:
            for s in (process.stdout, process.stderr):
                try:
                    s.close()
                except OSError:
                    pass
            time.sleep(0.4)
            desc = rec.get("descendant_pid")
            rec["descendant_state_after_close"] = (
                "gone" if not pid_alive(desc) else "alive")
            rec["descendant_exit_status"] = descendant_exit_status(desc)
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            rec["actual_exit"] = process.returncode
            rec["captured_preview"] = captured[:400].decode(errors="replace")
            return finalize_timed(rec, captured.decode(errors="replace"), started)
    with selectors.DefaultSelector() as sel:
        sel.register(process.stdout, selectors.EVENT_READ, "stdout")
        sel.register(process.stderr, selectors.EVENT_READ, "stderr")
        while sel.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                rec["timed_out"] = True
                break
            events = sel.select(min(tick, max(0.0, remaining)))
            now = time.monotonic()
            if rec["dead_observed_at"] is None and process.poll() is not None:
                rec["dead_observed_at"] = round(now - started, 6)
            for key, _ in events:
                alive_before = process.poll() is None
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except OSError:
                    chunk = b""
                if not chunk:
                    sel.unregister(key.fileobj)
                    continue
                captured += chunk
                rec["events"].append({"t": round(now - started, 6),
                                      "stream": key.data, "alive": alive_before,
                                      "n": len(chunk)})
                if key.data == "stdout":
                    rec["bytes_stdout"] += len(chunk)
                else:
                    rec["bytes_stderr"] += len(chunk)
                if rec["marker_observed_at"] is None and MARKER.encode() in captured:
                    rec["marker_observed_at"] = round(now - started, 6)
                    rec["marker_alive_before"] = alive_before
                if rec["err_first_at"] is None and b"ERROR:" in captured:
                    rec["err_first_at"] = round(now - started, 6)
                    rec["err_alive_before"] = alive_before
    if rec["dead_observed_at"] is None and process.poll() is not None:
        rec["dead_observed_at"] = round(time.monotonic() - started, 6)
    if rec["timed_out"]:
        rec["error"] = f"TIMEOUT after {bound} seconds"
    for s in (process.stdout, process.stderr):
        try:
            s.close()
        except OSError:
            pass
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)
    rec["actual_exit"] = process.returncode
    return finalize_timed(rec, captured.decode(errors="replace"), started)

def find_family():
    """Live pids whose cmdline carries this scratch fixture's unique
    FORGED_DESCENDANT_ERROR token (the sh -c descendant, exec'd yes), PLUS
    their direct children (head/yes pipeline components whose own cmdline
    lacks the marker). Deliberately NOT matching the generic gate string so a
    concurrent sibling lane's stock descendants never qualify."""
    matched, stats = set(), {}
    try:
        for p in Path("/proc").iterdir():
            if not p.name.isdigit():
                continue
            try:
                cl = (p / "cmdline").read_bytes()
                st = (p / "stat").read_text()
            except OSError:
                continue
            pid = int(p.name)
            try:
                ppid = int(st.rsplit(")", 1)[1].split()[1])
            except (ValueError, IndexError):
                ppid = -1
            stats[pid] = ppid
            if b"FORGED_DESCENDANT_ERROR" in cl:
                matched.add(pid)
    except OSError:
        pass
    return sorted(matched | {pid for pid, ppid in stats.items()
                             if ppid in matched})

def safe_reap(pid):
    """SIGKILL only if the live pid's cmdline proves it is a fixture
    descendant (DESCENDANT_PIPE / FORGED token) — guards pid reuse."""
    if pid is None or not pid_alive(pid):
        return False
    try:
        cl = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return False
    if b"DESCENDANT_PIPE" not in cl and b"FORGED" not in cl:
        return False
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except OSError:
        return False

def descendant_exit_status(pid):
    if pid is None:
        return None
    # After close, descendant dies of SIGPIPE -> wait status visible only to
    # its reaper (init/systemd). Probe /proc for absence instead; record
    # wchan/syscall state captured during the block for evidence.
    return {"alive": pid_alive(pid)}

def finalize_timed(rec, text, started):
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rec["marker_present"] = MARKER in text
    rec["errline_count"] = text.count(ERRLINE)
    rec["error_token_lines"] = sum(1 for l in text.splitlines() if "ERROR:" in l)
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    rec["godot_pid"] = int(m.group(1)) if m else rec.get("godot_pid")
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    if m:
        rec["descendant_pid"] = int(m.group(1))
    m = re.search(r"write_ppid=(\d+)", text)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["withheld_banner"] = "child_signature=withheld" in text
    rec["gated_signature_accepted"] = bool(
        rec["marker_observed_at"] is not None and rec["marker_alive_before"])
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, MARKER)
    rec["clause_exit_match"] = rec["actual_exit"] == 0
    rec["clause_error_none"] = rec["error"] is None
    rec["clause_signature"] = MARKER in text
    rec["clause_no_unrelated_errors"] = not any(
        "ERROR:" in l for l in text.splitlines())
    rec["descendant_alive_at_return"] = pid_alive(rec.get("descendant_pid"))
    rec["descendant_kernel_ppid_at_return"] = kernel_ppid(rec.get("descendant_pid"))
    rec["descendant_reaped_by_driver"] = safe_reap(rec.get("descendant_pid"))
    rec["output"] = text
    (RAW / f"{rec['case']}.stdout").write_text(text)
    return rec

# ---------------------------------------------------------------- main
def main():
    results = []
    sha_note = {"runner_sha256": runner_sha,
                "runner_path": str(RUNNER),
                "extracted": sorted(found),
                "edge_proj": str(PROJ_EDGE),
                "godot": subprocess.run([GODOT, "--version"],
                                        capture_output=True, text=True).stdout.strip()}

    # ---- Phase A: forged-error arms under the VERBATIM landed gate --------
    gate_runs = [
        ("vg_err_release_r0", ["--spawn-errforge-release"]),
        ("vg_err_release_r1", ["--spawn-errforge-release"]),
        ("vg_err_release_r2", ["--spawn-errforge-release"]),
        ("vg_err_hold", ["--spawn-errforge-hold"]),
        ("vg_err_stderr_r0", ["--spawn-errforge-stderr-release"]),
        ("vg_err_stderr_r1", ["--spawn-errforge-stderr-release"]),
        ("vg_err_predeath", ["--spawn-errforge-predeath"]),
        ("vg_err_split", ["--spawn-errforge-split"]),
        ("vg_err_glue", ["--spawn-errforge-glue"]),
        ("vg_err_midline", ["--spawn-errforge-midline"]),
        ("vg_err_genuine", ["--spawn-genuine-error"]),
        ("vg_combo_hold", ["--spawn-errforge-combo-hold"]),
        ("vg_default_control", []),
        ("vg_sigforge_release_control", ["--spawn-forge-release"]),
        ("vg_flood_2000", ["--spawn-errforge-flood", "--flood-count=2000"]),
        ("vg_pipefull_hold", ["--spawn-errforge-pipefull-hold"]),
    ]
    for name, extra in gate_runs:
        rec = gated_signature_run(name, extra)
        rec["arm"] = extra
        rec["raw_file"] = f"raw/{name}.stdout"
        (RAW / f"{name}.stdout").write_text("\n".join(rec.get("output_lines", [])))
        # Harness-side hygiene (production runner reaps post-meta; verbatim
        # function does not): kill the orphaned descendant, never gated.
        rec["descendant_reaped_by_driver"] = safe_reap(rec.get("descendant_pid"))
        results.append(rec)
        print(f"[gate] {name}: sig_ok={rec['gated_signature_accepted']} "
              f"inner={rec['inner_classification']} exit={rec['actual_exit']} "
              f"err={rec['error']!r} dead_at={rec['dead_observed_at']} "
              f"marker_at={rec['marker_observed_at']}", flush=True)

    # ---- Phase B: forged-error arms under the CASES consumer --------------
    comm_runs = [
        ("comm_err_release_r0", ["--spawn-errforge-release"], 8.0),
        ("comm_err_release_r1", ["--spawn-errforge-release"], 8.0),
        ("comm_err_hold", ["--spawn-errforge-hold"], 4.0),
        ("comm_err_stderr", ["--spawn-errforge-stderr-release"], 8.0),
        ("comm_err_predeath", ["--spawn-errforge-predeath"], 8.0),
        ("comm_err_split", ["--spawn-errforge-split"], 8.0),
        ("comm_err_glue", ["--spawn-errforge-glue"], 8.0),
        ("comm_err_midline", ["--spawn-errforge-midline"], 8.0),
        ("comm_err_genuine", ["--spawn-genuine-error"], 8.0),
        ("comm_combo_hold", ["--spawn-errforge-combo-hold"], 5.0),
        ("comm_default_control", [], 8.0),
        ("comm_sigforge_control", ["--spawn-forge-release"], 8.0),
    ]
    for name, extra, bound in comm_runs:
        rec = comm_run(name, PROJ_EDGE, extra, bound)
        results.append(rec)
        print(f"[comm] {name}: inner={rec['inner_classification']} "
              f"exit={rec['actual_exit']} err={rec['error']!r} "
              f"err_lines={rec['error_lines']} sig={rec['marker_present']}",
              flush=True)

    # ---- Phase C: flood ---------------------------------------------------
    for n in (20, 500, 2000):
        rec = comm_run(f"comm_flood_{n}", PROJ_EDGE,
                       ["--spawn-errforge-flood", f"--flood-count={n}"], 12.0)
        results.append(rec)
        print(f"[flood] N={n}: inner={rec['inner_classification']} "
              f"err_lines={rec['error_lines']} bytes={rec['output_bytes']} "
              f"elapsed={rec['elapsed_seconds']}", flush=True)

    # ---- Phase D: timed probes (gate-shaped replica w/ event ledger) ------
    timed = [
        ("tp_err_release_r0", ["--spawn-errforge-release"], {}),
        ("tp_err_release_r1", ["--spawn-errforge-release"], {}),
        ("tp_err_hold", ["--spawn-errforge-hold"], {}),
        ("tp_err_stderr", ["--spawn-errforge-stderr-release"], {}),
        ("tp_combo_hold", ["--spawn-errforge-combo-hold"], {}),
        ("tp_default", [], {}),
    ]
    for name, extra, kw in timed:
        rec = timed_probe(name, PROJ_EDGE, extra, **kw)
        results.append(rec)
        print(f"[timed] {name}: dead_at={rec['dead_observed_at']} "
              f"marker_at={rec['marker_observed_at']} "
              f"err_at={rec['err_first_at']} err_alive={rec['err_alive_before']} "
              f"sig_ok={rec['gated_signature_accepted']} inner={rec['inner_classification']}",
              flush=True)

    # ---- Phase E: pipe-full ----------------------------------------------
    pf = [
        ("pf_comm_256k", ["--spawn-errforge-pipefull", "--pump-kb=256"], 12.0),
        ("pf_comm_512k", ["--spawn-errforge-pipefull", "--pump-kb=512"], 12.0),
    ]
    for name, extra, bound in pf:
        rec = comm_run(name, PROJ_EDGE, extra, bound)
        results.append(rec)
        print(f"[pipefull-comm] {name}: inner={rec['inner_classification']} "
              f"bytes={rec['output_bytes']} err_lines={rec['error_lines']} "
              f"elapsed={rec['elapsed_seconds']}", flush=True)

    # stalled reader, then drain (proves: descendant's pipeline children
    # block in write() until the reader resumes; nobody else drains for it)
    rec = timed_probe("pf_stall_then_drain", PROJ_EDGE,
                      ["--spawn-errforge-pipefull", "--pump-kb=256"],
                      bound=20.0, pre_read_sleep=1.5)
    results.append(rec)
    print(f"[pipefull-stall] drain-after-stall: samples={len(rec['descendant_samples'])} "
          f"bytes={rec['bytes_stdout']+rec['bytes_stderr']} "
          f"exit={rec['actual_exit']} elapsed={rec['elapsed_seconds']}", flush=True)

    # stalled reader, then close with the UNBOUNDED pump (the sh exec's yes:
    # the descendant itself is the blocked writer -> clean syscall evidence;
    # closing the read end kills it via SIGPIPE)
    rec = timed_probe("pf_stall_then_close", PROJ_EDGE,
                      ["--spawn-errforge-pipefull-hold"],
                      bound=8.0, pre_read_sleep=1.5, close_after_sleep=True)
    results.append(rec)
    print(f"[pipefull-stall] close-after-stall: state={rec.get('descendant_state_after_close')} "
          f"child_state_after_stall={rec['child_state_after_stall']}", flush=True)

    # unbounded pump under the verbatim gate already ran (vg_pipefull_hold);
    # a bounded replicate under the timed consumer with a mid-run close:
    rec = timed_probe("pf_gate_close_observe", PROJ_EDGE,
                      ["--spawn-errforge-pipefull-hold"], bound=3.0)
    results.append(rec)
    print(f"[pipefull-gate] bounded pump: bytes={rec['bytes_stdout']} "
          f"timed_out={rec['timed_out']} desc_alive={rec['descendant_alive_at_return']}",
          flush=True)

    # ---- Phase F: stream-split runs (classify_streams asymmetry) ----------
    for name, extra in [
            ("st_genuine", []),
            ("st_err_stdout", ["--spawn-errforge-release"]),
            ("st_err_stderr", ["--spawn-errforge-stderr-release"]),
            ("st_err_genuine", ["--spawn-genuine-error"])]:
        rec = streams_run(name, PROJ_EDGE, extra)
        results.append(rec)
        print(f"[streams] {name}: streams_cls={rec['streams_classification']} "
              f"merged_cls={rec['merged_classification']} "
              f"err_out={rec['errline_in_stdout']} err_err={rec['errline_in_stderr']}",
              flush=True)

    # ---- Phase G: synthetic classifier unit probes ------------------------
    S = MARKER
    unit_cases = {
        "clean": [S],
        "err_own_line": [S, "ERROR: FORGED x"],
        "err_glued_tail": [S, "DESCENDANT_PIPE_TAIL_OPENERROR: FORGED x"],
        "err_on_sig_line": [S + " ERROR: FORGED x"],
        "err_inside_sig": ["DESCENDANT_PIPE_PROBE: expected ERROR: FORGED signature"],
        "err_midline": ["DESCENDANT_PIPE_PROBE: expected ERROR: FORGED x", "signature"],
        "lowercase_error": [S, "error: lowercase diagnostic"],
        "err_no_colon": [S, "ERROR something"],
        "err_prefix_of_allowed": [S, "ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got [] ERROR: FORGED x"],
        "script_error_anywhere": [S, "prelude SCRIPT ERROR: boom"],
        "parse_error_anywhere": [S, "Parse Error: boom"],
        "err_split_reassembled": [S, "ERROR: FORGED split-token diagnostic"],
        "err_many": [S] + ["ERROR: flood %d" % i for i in range(5)],
        "err_ppid_provenance_line_only": [S, "DESCENDANT_PIPE_ERRFORGE write_ppid=1573"],
    }
    allowed = ("ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []",)
    unit = []
    for label, lines in unit_cases.items():
        text = "\n".join(lines) + "\n"
        unit.append({"case": label,
                     "classify_process": classify_process(0, None, text, 0, S, allowed),
                     "unrelated_lines": [l for l in text.splitlines()
                                         if "ERROR:" in l]})
        print(f"[unit] {label}: classify={unit[-1]['classify_process']}",
              flush=True)
    results.append({"case": "synthetic_classifier_units", "units": unit})

    out = {"runner": sha_note,
           "results": results}
    (EDGE / "edge-verdicts.json").write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", EDGE / "edge-verdicts.json", flush=True)

if __name__ == "__main__":
    sys.exit(main())
