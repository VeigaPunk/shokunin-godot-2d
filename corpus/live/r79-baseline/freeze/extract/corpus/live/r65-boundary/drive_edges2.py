#!/usr/bin/env python3
"""r65 boundary edge driver v2: forged-REJECTION (post-death ERROR:) probes.

Verdict-path evidence comes from functions VERBATIM-EXTRACTED from the
working-tree runner (ast.get_source_segment -> exec): run_process,
classify_process, classify_streams, pid_alive, kernel_ppid, and the landed
r64 gated_signature_run. Rows tagged vg_*/comm_* run production code.

Instrumented replicas (timed_probe, stalled-reader consumers, stream-split
runner) are corroborating evidence; differences are disclosed in-record.

Writes only under corpus/live/r65-boundary/. Never touches tracked files.

v2 changes vs the dead first attempt:
- safe_reap ONLY kills the pid this driver's own run printed, and only when
  its /proc cmdline carries this fixture's unique token (edge runs:
  FORGED_DESCENDANT_ERROR; stock runs: DESCENDANT_PIPE_ERRFORGE). A generic
  DESCENDANT_PIPE match could SIGKILL a concurrent sibling seat's
  descendant (an r65-critic battery ran during this session).
- Unbounded `yes` pump under the verbatim gate runs in a subprocess under
  RLIMIT_AS — the gate's `captured` bytearray is uncapped, so a 3s
  unbounded post-death pump is a memory-exhaustion surface; the guarded
  wrapper makes the outcome reportable either way.
- comm_err_hold also runs at the production 8s CASES bound: the ~6s pipe
  hold releases INSIDE it, so the hold arm exits the timeout axis and
  becomes a pure error-axis FAIL on a clean exit-0 record.
- per-clause conjunct table for every classification (the verdict is a
  single AND; "which axis rejects" = which conjuncts evaluate False).
"""
import ast
import fcntl
import json
import os
import re
import resource
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
RAW = EDGE / "raw2"
RAW.mkdir(exist_ok=True)
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
ERRLINE = "ERROR: FORGED_DESCENDANT_ERROR injected diagnostic"
STOCK_ERRLINE = "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
ALLOWLISTED_ERR = ("ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected "
                   "signature=JSON_PARSE_ERROR")
GODOT = "godot"
EDGE_TOKEN = b"FORGED_DESCENDANT_ERROR"
STOCK_TOKEN = b"DESCENDANT_PIPE_ERRFORGE"

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


def clauses(code, error, output, expected_exit=0, signature=MARKER,
            allowed_errors=()):
    """Per-conjunct truth table of the landed classify_process expression
    (verbatim logic, exploded so 'which axis rejects' is visible)."""
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False

    unrelated = [l for l in lines if "ERROR:" in l
                 and not any(allowed_error(l, a) for a in allowed_errors)]
    table = {
        "code_eq_expected": code == expected_exit,
        "error_is_none": error is None,
        "signature_present": signature in output,
        "no_unrelated_errors": not unrelated,
        "no_script_error": "SCRIPT ERROR:" not in output,
        "no_parse_error": "Parse Error:" not in output,
    }
    table["verdict"] = all(table.values())
    table["unrelated_error_lines"] = unrelated[:40]
    table["unrelated_error_count"] = len(unrelated)
    table["full_classify_process"] = classify_process(
        code, error, output, expected_exit, signature, allowed_errors)
    return table


# ---------------------------------------------------------------- replicas
def cmd_for(proj, extra):
    return [GODOT, "--headless", "--path", str(proj), "--script",
            "res://descendant_pipe_probe.gd", "--"] + list(extra)


def safe_reap(pid, token):
    """SIGKILL only the pid this driver's own run printed, and only if its
    cmdline proves it is a fixture descendant carrying the expected unique
    token — guards pid reuse and NEVER matches a sibling seat's concurrent
    stock-fixture descendants (different token / different pid)."""
    if pid is None or not pid_alive(pid):
        return False
    try:
        cl = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return False
    if token not in cl:
        return False
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except OSError:
        return False


def token_for(proj):
    return EDGE_TOKEN if proj == PROJ_EDGE else STOCK_TOKEN


def comm_run(case, proj, extra, bound=8.0, allowed_errors=(), tag_token=None):
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
           "clauses": clauses(code, error, output, 0, MARKER, allowed_errors),
           "output": output}
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", output)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", output)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"write_ppid=(\d+)", output)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["descendant_reaped_by_driver"] = safe_reap(
        rec["descendant_pid"], tag_token or token_for(proj))
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
           "errline_in_stdout": ERRLINE in out or STOCK_ERRLINE in out,
           "errline_in_stderr": ERRLINE in err or STOCK_ERRLINE in err,
           "streams_classification": classify_streams(code, error, out, err, 0, MARKER),
           "merged_classification": classify_process(code, error, out + err, 0, MARKER),
           "stdout": out, "stderr": err}
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", out + err)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    rec["descendant_reaped_by_driver"] = safe_reap(
        rec["descendant_pid"], token_for(proj))
    (RAW / f"{case}.out").write_text(out)
    (RAW / f"{case}.err").write_text(err)
    return rec


def timed_probe(case, proj, extra, bound=3.0, tick=0.005, pre_read_sleep=0.0,
                close_after_sleep=False, capture_cap=None):
    """Instrumented gate-shaped consumer: poll()-gated select loop over both
    pipes, per-event (t, stream, alive_before, n) ledger, marker + first
    'ERROR:'-byte observation stamps, descendant state sampling during a
    pre-read stall (pipe-full probe). capture_cap bounds STORED bytes only —
    byte counters stay exact (disclosed in-record)."""
    rec = {"case": case, "consumer": "timed_probe",
           "flags": list(extra), "bound": bound, "tick": tick,
           "pre_read_sleep": pre_read_sleep, "timed_out": False,
           "capture_cap": capture_cap, "capture_truncated": False,
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
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            rec["actual_exit"] = process.returncode
            rec["captured_preview"] = captured[:400].decode(errors="replace")
            return finalize_timed(rec, captured.decode(errors="replace"), started, proj)
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
                if capture_cap is None or len(captured) < capture_cap:
                    captured += chunk
                else:
                    rec["capture_truncated"] = True
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
    return finalize_timed(rec, captured.decode(errors="replace"), started, proj)


def find_family():
    """Live pids whose cmdline carries this scratch fixture's unique
    FORGED_DESCENDANT_ERROR token (the sh -c descendant, exec'd yes), PLUS
    their direct children (head/yes pipeline components whose own cmdline
    lacks the marker). Deliberately NOT matching the generic gate string so
    a concurrent sibling seat's stock descendants never qualify."""
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
            if EDGE_TOKEN in cl:
                matched.add(pid)
    except OSError:
        pass
    return sorted(matched | {pid for pid, ppid in stats.items()
                             if ppid in matched})


def finalize_timed(rec, text, started, proj):
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
    rec["clauses"] = clauses(rec["actual_exit"], rec["error"], text, 0, MARKER)
    rec["descendant_alive_at_return"] = pid_alive(rec.get("descendant_pid"))
    rec["descendant_kernel_ppid_at_return"] = kernel_ppid(rec.get("descendant_pid"))
    rec["descendant_reaped_by_driver"] = safe_reap(
        rec.get("descendant_pid"), token_for(proj))
    rec["output"] = text[:200000]
    (RAW / f"{rec['case']}.stdout").write_text(text[:2000000])
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
        ("vg_err_newlinesplit", ["--spawn-errforge-newlinesplit"]),
        ("vg_err_allowlisted", ["--spawn-errforge-allowlisted"]),
        ("vg_err_glue", ["--spawn-errforge-glue"]),
        ("vg_err_midline", ["--spawn-errforge-midline"]),
        ("vg_err_genuine", ["--spawn-genuine-error"]),
        ("vg_combo_hold", ["--spawn-errforge-combo-hold"]),
        ("vg_combo_release", ["--spawn-errforge-combo-release"]),
        ("vg_default_control", []),
        ("vg_sigforge_release_control", ["--spawn-forge-release"]),
        ("vg_flood_2000", ["--spawn-errforge-flood", "--flood-count=2000"]),
        # NOTE: --spawn-errforge-pipefull-hold under the verbatim gate is
        # run separately in a memory-guarded subprocess (Phase E2): the
        # gate's `captured` bytearray is uncapped and `yes` fills it for
        # the whole 3s bound.
    ]
    for name, extra in gate_runs:
        rec = gated_signature_run(name, extra)
        rec["arm"] = extra
        rec["raw_file"] = f"raw2/{name}.stdout"
        (RAW / f"{name}.stdout").write_text("\n".join(rec.get("output_lines", [])))
        rec["clauses"] = clauses(rec["actual_exit"], rec["error"],
                                 "\n".join(rec.get("output_lines", [])), 0, MARKER)
        rec["descendant_reaped_by_driver"] = safe_reap(
            rec.get("descendant_pid"), EDGE_TOKEN)
        results.append(rec)
        print(f"[gate] {name}: sig_ok={rec['gated_signature_accepted']} "
              f"inner={rec['inner_classification']} exit={rec['actual_exit']} "
              f"err={rec['error']!r} dead_at={rec['dead_observed_at']} "
              f"marker_at={rec['marker_observed_at']}", flush=True)

    # ---- Phase B: forged-error arms under the CASES consumer --------------
    comm_runs = [
        ("comm_err_release_r0", PROJ_EDGE, ["--spawn-errforge-release"], 8.0, ()),
        ("comm_err_release_r1", PROJ_EDGE, ["--spawn-errforge-release"], 8.0, ()),
        # hold arm at the PRODUCTION 8s CASES bound: pipes release ~6s ->
        # clean exit-0 record, pure error-axis rejection (no timeout).
        ("comm_err_hold_b8", PROJ_EDGE, ["--spawn-errforge-hold"], 8.0, ()),
        ("comm_err_hold_b4", PROJ_EDGE, ["--spawn-errforge-hold"], 4.0, ()),
        ("comm_err_stderr", PROJ_EDGE, ["--spawn-errforge-stderr-release"], 8.0, ()),
        ("comm_err_predeath", PROJ_EDGE, ["--spawn-errforge-predeath"], 8.0, ()),
        ("comm_err_split", PROJ_EDGE, ["--spawn-errforge-split"], 8.0, ()),
        ("comm_err_newlinesplit", PROJ_EDGE, ["--spawn-errforge-newlinesplit"], 8.0, ()),
        ("comm_err_glue", PROJ_EDGE, ["--spawn-errforge-glue"], 8.0, ()),
        ("comm_err_midline", PROJ_EDGE, ["--spawn-errforge-midline"], 8.0, ()),
        # allowlisted forged error: same record classified without and with
        # the matching allowlist entry (origin-blind allowlist probe).
        ("comm_err_allowlisted", PROJ_EDGE, ["--spawn-errforge-allowlisted"], 8.0, ()),
        ("comm_err_allowlisted_allowed", PROJ_EDGE, ["--spawn-errforge-allowlisted"], 8.0,
         (ALLOWLISTED_ERR,)),
        ("comm_err_genuine", PROJ_EDGE, ["--spawn-genuine-error"], 8.0, ()),
        # combo (forged sig + forged error) at 8s bound: hold releases ~6s
        # -> clean exit-0 record, error-only rejection even on combo-hold.
        ("comm_combo_hold_b8", PROJ_EDGE, ["--spawn-errforge-combo-hold"], 8.0, ()),
        ("comm_combo_hold_b4", PROJ_EDGE, ["--spawn-errforge-combo-hold"], 4.0, ()),
        ("comm_combo_release", PROJ_EDGE, ["--spawn-errforge-combo-release"], 8.0, ()),
        ("comm_default_control", PROJ_EDGE, [], 8.0, ()),
        ("comm_sigforge_control", PROJ_EDGE, ["--spawn-forge-release"], 8.0, ()),
        # stock (author's) arms through the verbatim CASES consumer:
        # independent reproduction of the landed claim on the real fixture.
        ("comm_stock_release", PROJ_STOCK, ["--spawn-errforge-release"], 8.0, ()),
        ("comm_stock_hold_b8", PROJ_STOCK, ["--spawn-errforge-hold"], 8.0, ()),
        ("comm_stock_hold_b3", PROJ_STOCK, ["--spawn-errforge-hold"], 3.0, ()),
        ("comm_stock_genuine", PROJ_STOCK, ["--emit-errforge"], 8.0, ()),
        ("comm_stock_detach", PROJ_STOCK, ["--spawn-detach"], 8.0, ()),
        ("comm_stock_sigforge", PROJ_STOCK, ["--spawn-forge-release"], 8.0, ()),
    ]
    for name, proj, extra, bound, allowed in comm_runs:
        rec = comm_run(name, proj, extra, bound, allowed_errors=allowed)
        results.append(rec)
        print(f"[comm] {name}: verdict={rec['clauses']['verdict']} "
              f"exit={rec['actual_exit']} err={rec['error']!r} "
              f"err_lines={rec['error_lines']} sig={rec['marker_present']} "
              f"elapsed={rec['elapsed_seconds']}", flush=True)

    # ---- Phase C: flood ---------------------------------------------------
    for n, distinct in ((20, False), (500, False), (2000, False),
                        (200, True), (2000, True)):
        extra = ["--spawn-errforge-flood", f"--flood-count={n}"]
        if distinct:
            extra.append("--flood-distinct")
        rec = comm_run(f"comm_flood_{n}{'_distinct' if distinct else ''}",
                       PROJ_EDGE, extra, 12.0)
        results.append(rec)
        print(f"[flood] N={n} distinct={distinct}: "
              f"verdict={rec['clauses']['verdict']} "
              f"err_lines={rec['error_lines']} bytes={rec['output_bytes']} "
              f"elapsed={rec['elapsed_seconds']}", flush=True)

    # ---- Phase D: timed probes (gate-shaped replica w/ event ledger) ------
    timed = [
        ("tp_err_release_r0", ["--spawn-errforge-release"], {}),
        ("tp_err_release_r1", ["--spawn-errforge-release"], {}),
        ("tp_err_hold", ["--spawn-errforge-hold"], {}),
        ("tp_err_stderr", ["--spawn-errforge-stderr-release"], {}),
        ("tp_err_predeath", ["--spawn-errforge-predeath"], {}),
        ("tp_err_newlinesplit", ["--spawn-errforge-newlinesplit"], {}),
        ("tp_combo_hold", ["--spawn-errforge-combo-hold"], {}),
        ("tp_combo_release", ["--spawn-errforge-combo-release"], {}),
        ("tp_default", [], {}),
    ]
    for name, extra, kw in timed:
        rec = timed_probe(name, PROJ_EDGE, extra, **kw)
        results.append(rec)
        print(f"[timed] {name}: dead_at={rec['dead_observed_at']} "
              f"marker_at={rec['marker_observed_at']} "
              f"err_at={rec['err_first_at']} err_alive={rec['err_alive_before']} "
              f"sig_ok={rec['gated_signature_accepted']} "
              f"verdict={rec['clauses']['verdict']}", flush=True)

    # ---- Phase E: pipe-full ----------------------------------------------
    pf = [
        ("pf_comm_256k", ["--spawn-errforge-pipefull", "--pump-kb=256"], 12.0),
        ("pf_comm_512k", ["--spawn-errforge-pipefull", "--pump-kb=512"], 12.0),
    ]
    for name, extra, bound in pf:
        rec = comm_run(name, PROJ_EDGE, extra, bound)
        results.append(rec)
        print(f"[pipefull-comm] {name}: verdict={rec['clauses']['verdict']} "
              f"bytes={rec['output_bytes']} err_lines={rec['error_lines']} "
              f"elapsed={rec['elapsed_seconds']}", flush=True)

    # stalled reader, then drain (proves: descendant's pipeline children
    # block in write() until the reader resumes; nobody else drains for it)
    rec = timed_probe("pf_stall_then_drain", PROJ_EDGE,
                      ["--spawn-errforge-pipefull", "--pump-kb=256"],
                      bound=20.0, pre_read_sleep=1.5)
    results.append(rec)
    print(f"[pipefull-stall] drain-after-stall: samples={len(rec['descendant_samples'])} "
          f"bytes={rec['bytes_stdout'] + rec['bytes_stderr']} "
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

    # unbounded pump under a gate-shaped reader, capture capped at 8 MiB
    # (byte counters stay exact; storage cap disclosed in-record)
    rec = timed_probe("pf_gate_bounded_read", PROJ_EDGE,
                      ["--spawn-errforge-pipefull-hold"], bound=3.0,
                      capture_cap=8 * 1024 * 1024)
    results.append(rec)
    print(f"[pipefull-gate] unbounded pump, capped store: "
          f"bytes_out={rec['bytes_stdout']} bytes_err={rec['bytes_stderr']} "
          f"timed_out={rec['timed_out']} trunc={rec['capture_truncated']} "
          f"desc_alive={rec['descendant_alive_at_return']}", flush=True)

    # ---- Phase E2: verbatim gate vs UNBOUNDED pump, memory-guarded --------
    guarded = subprocess.run(
        [sys.executable, "-c", GUARDED_GATE_SNIPPET, str(PROJ_EDGE)],
        capture_output=True, text=True, timeout=60,
        env={**os.environ, "RLIMIT_AS_GB": "5"})
    (RAW / "guarded_gate_pipefull.json").write_text(
        guarded.stdout or guarded.stderr)
    try:
        guarded_rec = json.loads(guarded.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        guarded_rec = {"case": "vg_pipefull_hold_guarded",
                       "driver_error": guarded.stderr[-2000:],
                       "returncode": guarded.returncode}
    results.append(guarded_rec)
    print(f"[pipefull-gate-verbatim] rc={guarded.returncode} "
          f"rec={json.dumps(guarded_rec)[:400]}", flush=True)

    # ---- Phase F: stream-split runs (classify_streams asymmetry) ----------
    for name, proj, extra in [
            ("st_genuine", PROJ_EDGE, []),
            ("st_err_stdout", PROJ_EDGE, ["--spawn-errforge-release"]),
            ("st_err_stderr", PROJ_EDGE, ["--spawn-errforge-stderr-release"]),
            ("st_err_genuine", PROJ_EDGE, ["--spawn-genuine-error"]),
            ("st_stock_genuine", PROJ_STOCK, ["--emit-errforge"]),
            ("st_stock_release", PROJ_STOCK, ["--spawn-errforge-release"])]:
        rec = streams_run(name, proj, extra)
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
        "err_newline_split": [S, "ERR", "OR: FORGED newline-split diagnostic"],
        "lowercase_error": [S, "error: lowercase diagnostic"],
        "err_no_colon": [S, "ERROR something"],
        "err_prefix_of_allowed": [S, "ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got [] ERROR: FORGED x"],
        "script_error_anywhere": [S, "prelude SCRIPT ERROR: boom"],
        "parse_error_anywhere": [S, "Parse Error: boom"],
        "err_many": [S] + ["ERROR: flood %d" % i for i in range(5)],
        "err_ppid_provenance_line_only": [S, "DESCENDANT_PIPE_ERRFORGE write_ppid=1573"],
        "err_allowlisted_forged": [S, ALLOWLISTED_ERR],
        "err_allowlisted_forged_glued": [S + " tail", ALLOWLISTED_ERR + " trailing-junk"],
        "err_allowlisted_forged_prefixed": [S, "noise-prefix " + ALLOWLISTED_ERR],
    }
    allowed = ("ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []",)
    allowed_save = (ALLOWLISTED_ERR,)
    unit = []
    for label, lines in unit_cases.items():
        text = "\n".join(lines) + "\n"
        unit.append({"case": label,
                     "cls_no_allow": classify_process(0, None, text, 0, S, ()),
                     "cls_cb_allow": classify_process(0, None, text, 0, S, allowed),
                     "cls_save_allow": classify_process(0, None, text, 0, S, allowed_save),
                     "unrelated_lines": [l for l in text.splitlines()
                                         if "ERROR:" in l]})
        print(f"[unit] {label}: cls={unit[-1]['cls_no_allow']}/"
              f"{unit[-1]['cls_cb_allow']}/{unit[-1]['cls_save_allow']}",
              flush=True)
    results.append({"case": "synthetic_classifier_units", "units": unit})

    out = {"runner": sha_note,
           "results": results}
    (EDGE / "edge-verdicts.json").write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", EDGE / "edge-verdicts.json", flush=True)


GUARDED_GATE_SNIPPET = r'''
import ast, json, resource, selectors, subprocess, sys, time, os
from pathlib import Path
from types import SimpleNamespace
proj = sys.argv[1]
limit = int(os.environ.get("RLIMIT_AS_GB", "5")) * (1 << 30)
resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
# re-extract verbatim from the working-tree runner
runner = Path(proj).resolve().parents[2] / "fixtures" / "run_battery.py"
src = runner.read_text()
tree = ast.parse(src)
ns = {"subprocess": subprocess, "selectors": selectors, "os": os,
      "re": __import__("re"), "time": time, "signal": __import__("signal"),
      "datetime": __import__("datetime").datetime,
      "args": SimpleNamespace(godot="godot"),
      "scratch": Path(proj), "gate_marker": "DESCENDANT_PIPE_PROBE: expected signature",
      "gate_bound": 3.0, "gate_poll_tick": 0.005}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in {
            "gated_signature_run", "pid_alive", "kernel_ppid",
            "classify_process", "run_process"}:
        exec(ast.get_source_segment(src, node), ns)
try:
    rec = ns["gated_signature_run"]("vg_pipefull_hold_guarded",
                                    ["--spawn-errforge-pipefull-hold"])
    out = {"case": "vg_pipefull_hold_guarded", "outcome": "completed",
           "captured_bytes": len("\n".join(rec.get("output_lines", []))),
           "timed_out": rec["timed_out"], "error": rec["error"],
           "elapsed": rec["elapsed_seconds"],
           "gated_signature_accepted": rec["gated_signature_accepted"],
           "inner_classification": rec["inner_classification"],
           "descendant_alive_at_return": rec["descendant_alive_at_return"],
           "error_token_lines": sum(1 for l in rec.get("output_lines", [])
                                    if "ERROR:" in l)}
except MemoryError:
    out = {"case": "vg_pipefull_hold_guarded", "outcome": "MemoryError",
           "note": "uncapped `captured` bytearray hit RLIMIT_AS inside the "
                   "verbatim gate loop — unbounded post-death pump is a "
                   "memory-exhaustion surface of the gated read"}
except Exception as exc:  # noqa
    out = {"case": "vg_pipefull_hold_guarded", "outcome": type(exc).__name__,
           "error": str(exc)[:500]}
print(json.dumps(out))
'''

if __name__ == "__main__":
    sys.exit(main())
