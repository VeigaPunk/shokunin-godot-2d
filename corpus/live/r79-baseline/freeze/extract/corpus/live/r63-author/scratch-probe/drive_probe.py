#!/usr/bin/env python3
"""r63 author scratch driver: merged-stream signature-spoof boundary probe.

ast.get_source_segment-extracts run_process and classify_process VERBATIM from
the tracked corpus/fixtures/run_battery.py and execs them — the classification
numbers below are the production code path, not a transcription.

Arms (fixture: proj/descendant_pipe_probe.gd, candidate for tracked promotion):
  clean              no descendant, child emits signature      -> True baseline
  detach             --spawn-detach                            -> child-exit-bound True (regression)
  forge_hold_b3      --spawn-forge-hold under bounded Popen(3.0):
                     descendant writes EXPECTED signature + write_ppid after the
                     reparenting gate (provably post-child-exit), holds pipes
                     -> TIMEOUT, signature present, child_exit_at_timeout==0,
                        inner_classification False
  forge_hold_b8      same arm under the 8s CASES bound via run_process:
                     descendant releases ~6.5s < 8s -> exit 0 + signature -> True
                     (bound-dependence of the same forged write)
  forge_release      --spawn-forge-release under run_process(8s): descendant
                     writes signature post-exit, releases immediately -> exit 0,
                     error None, signature present -> classify_process True
                     THE DISCRIMINATOR: post-death forged signature accepted.
  forge_release_wrongsig
                     same output reclassified against a signature never written
                     -> False (presence check still active; not vacuous)

Records JSON to spoof-verdicts.json; raw merged outputs to raw/.
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

HERE = Path(__file__).resolve().parent
PROJ = HERE / "proj"
RUNNER = HERE.parents[2] / "fixtures" / "run_battery.py"
GODOT = sys.argv[1] if len(sys.argv) > 1 else "/usr/bin/godot"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"

src = RUNNER.read_text()
tree = ast.parse(src)
ns = {"subprocess": subprocess}
wanted = {"run_process", "classify_process"}
found = set()
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        seg = ast.get_source_segment(src, node)
        assert seg, node.name
        exec(compile(seg, str(RUNNER), "exec"), ns)
        found.add(node.name)
assert found == wanted, f"missing {wanted - found}"
run_process = ns["run_process"]
classify_process = ns["classify_process"]
runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()


def pid_alive(pid):
    if pid is None or pid <= 0:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def parse_ids(text):
    g = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    d = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    w = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", text)
    return (int(g.group(1)) if g else None,
            int(d.group(1)) if d else None,
            int(w.group(1)) if w else None)


def bounded_popen(flags, bound):
    """Replica of the r62 meta's bounded-Popen pattern (same mechanism)."""
    rec = {"timed_out": False, "child_exit_at_timeout": None,
           "actual_exit": None, "error": None}
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://descendant_pipe_probe.gd", "--", *flags]
    proc = None
    text = ""
    started = time.monotonic()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, bufsize=1)
        try:
            out, err = proc.communicate(timeout=bound)
            text = (out or "") + (err or "")
            rec["actual_exit"] = proc.returncode
        except subprocess.TimeoutExpired as exc:
            rec["timed_out"] = True
            rec["child_exit_at_timeout"] = proc.poll()
            out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            text = out + err
            rec["error"] = f"TIMEOUT after {bound} seconds"
            for stream in (proc.stdout, proc.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    rec["error"] += "; post-kill wait timed out"
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] = (rec["error"] or "") + "; forced cleanup timed out"
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rec["command"] = cmd
    return rec, text


def finish(rec, text, expected_exit, signature, rawname):
    gp, dp, wp = parse_ids(text)
    rec["marker_observed"] = signature in text
    rec["write_ppid_observed"] = wp is not None
    rec["godot_pid"] = gp
    rec["descendant_pid"] = dp
    rec["write_ppid"] = wp
    rec["godot_alive_at_return"] = pid_alive(gp)
    rec["descendant_alive_at_return"] = pid_alive(dp)
    rec["write_post_orphan"] = (wp is not None and gp is not None and wp != gp)
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, expected_exit, signature)
    (HERE / "raw" / f"{rawname}.stdout").write_text(text)
    return rec


results = {}

# 1. clean genuine baseline via production run_process
out, code, err = run_process(
    [GODOT, "--headless", "--path", str(PROJ), "--script",
     "res://descendant_pipe_probe.gd"], 8.0)
results["clean"] = finish(
    {"actual_exit": code, "error": err, "timed_out": False},
    out, 0, MARKER, "clean")

# 2. detach regression control (production run_process)
out, code, err = run_process(
    [GODOT, "--headless", "--path", str(PROJ), "--script",
     "res://descendant_pipe_probe.gd", "--", "--spawn-detach"], 8.0)
results["detach"] = finish(
    {"actual_exit": code, "error": err, "timed_out": False},
    out, 0, MARKER, "detach")

# 3. forge_hold under bounded 3.0s Popen — the TIMEOUT record carrying a
#    descendant-authored post-death signature.
rec, text = bounded_popen(["--spawn-forge-hold"], 3.0)
results["forge_hold_b3"] = finish(rec, text, 0, MARKER, "forge_hold_b3")

# 4. forge_release — THE DISCRIMINATOR (production run_process, 8s CASES bound)
out, code, err = run_process(
    [GODOT, "--headless", "--path", str(PROJ), "--script",
     "res://descendant_pipe_probe.gd", "--", "--spawn-forge-release"], 8.0)
results["forge_release"] = finish(
    {"actual_exit": code, "error": err, "timed_out": False},
    out, 0, MARKER, "forge_release")

# 5. same forge-hold arm under the 8s CASES bound (release ~6.5s < 8s ->
#    clean record with forged signature): bound-dependence evidence.
out, code, err = run_process(
    [GODOT, "--headless", "--path", str(PROJ), "--script",
     "res://descendant_pipe_probe.gd", "--", "--spawn-forge-hold"], 8.0)
results["forge_hold_b8"] = finish(
    {"actual_exit": code, "error": err, "timed_out": False},
    out, 0, MARKER, "forge_hold_b8")

# 6. wrong-signature control on the forged release output (no extra Godot run)
forge_rel_text = (HERE / "raw" / "forge_release.stdout").read_text()
results["forge_release_wrongsig"] = {
    "inner_classification": classify_process(
        results["forge_release"]["actual_exit"], results["forge_release"]["error"],
        forge_rel_text, 0, "DESCENDANT_PIPE_PROBE: a different signature"),
    "signature": "DESCENDANT_PIPE_PROBE: a different signature",
}

# 7. shape comparison: forged-release tuple vs genuine-detach tuple
shape_keys = ("actual_exit", "error", "marker_observed", "inner_classification")
results["shape_compare"] = {
    "forged_release": {k: results["forge_release"].get(k) for k in shape_keys},
    "genuine_detach": {k: results["detach"].get(k) for k in shape_keys},
    "indistinguishable_on_signature_axis": all(
        results["forge_release"].get(k) == results["detach"].get(k)
        for k in shape_keys),
}

# harness hygiene: kill orphaned descendants (bounded sleeps would self-exit)
killed = []
for r in results.values():
    dp = r.get("descendant_pid") if isinstance(r, dict) else None
    if pid_alive(dp):
        try:
            os.kill(dp, signal.SIGKILL)
            killed.append(dp)
        except OSError:
            pass

payload = {"runner_sha256": runner_sha, "godot": GODOT, "proj": str(PROJ),
           "marker": MARKER, "results": results, "hygiene_killed": killed}
out_path = HERE / "spoof-verdicts.json"
out_path.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps({k: (v if k != "results" else "see file") for k, v in payload.items()},
                 indent=2))
for name, rec in results.items():
    if isinstance(rec, dict) and "inner_classification" in rec:
        print(f"{name}: exit={rec.get('actual_exit')} err={rec.get('error')!r} "
              f"sig={rec.get('marker_observed')} timeout={rec.get('timed_out')} "
              f"child_at_to={rec.get('child_exit_at_timeout')} "
              f"wpp={rec.get('write_ppid')} gpid={rec.get('godot_pid')} "
              f"classify={rec['inner_classification']}")
print(f"wrote {out_path}")
