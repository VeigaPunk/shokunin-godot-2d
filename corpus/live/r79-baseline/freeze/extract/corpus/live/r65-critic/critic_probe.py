#!/usr/bin/env python3
"""r65 critic probe: counterexample arms the landed fixture cannot express.

Extracts classify_process VERBATIM from run_battery.py (exec the indented
function body after dedent) so classification semantics cannot drift from
the tracked code under review. All runs are bounded Popens in the r65
errforge_run record shape.
"""
import json
import os
import re
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJ = ROOT / "proj"
GODOT = "/usr/bin/godot"
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
ERR = "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
BOUND = 3.0

# --- verbatim classify_process extraction ---
src = (ROOT.parent.parent / "fixtures" / "run_battery.py").read_text()
m = re.search(r"(    def classify_process\(.*?\n)(?=    def classify_streams)", src, re.S)
assert m, "classify_process block not found"
ns = {"re": re}
exec(textwrap.dedent(m.group(1)), ns)
classify_process = ns["classify_process"]
print(f"[harness] classify_process extracted verbatim ({len(m.group(1))} chars)")


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


def kernel_ppid(pid):
    if pid is None or pid <= 0:
        return None
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    # field 4 after the comm's closing paren
    return int(stat.rsplit(")", 1)[1].split()[1])


def run_arm(case, extra_args, bound=BOUND, split_streams=False):
    """Bounded Popen in the author's errforge_run shape (+ split streams)."""
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://critic_errforge_probe.gd", "--"] + list(extra_args)
    rec = {"case": case, "flags": list(extra_args), "command": cmd,
           "bound_seconds": bound, "timed_out": False, "actual_exit": None,
           "error": None, "elapsed_seconds": None}
    started = time.monotonic()
    out_text, err_text = "", ""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    try:
        o, e = proc.communicate(timeout=bound)
        out_text, err_text = o or "", e or ""
        rec["actual_exit"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        rec["timed_out"] = True
        rec["child_exit_at_timeout"] = proc.poll()
        out_text = exc.stdout or ""
        err_text = exc.stderr or ""
        rec["error"] = f"TIMEOUT after {bound} seconds"
        for s in (proc.stdout, proc.stderr):
            try:
                s.close()
            except OSError:
                pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait(timeout=3)
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    text = out_text + err_text                       # the r65/errforge merge
    rec["signature_observed"] = SIG in text
    rec["error_marker_captured"] = ERR in text
    rec["error_lines"] = sorted({l.strip() for l in text.splitlines()
                                 if "ERROR:" in l})
    rec["raw_stdout_error_lines"] = sorted({l.strip() for l in
                                            out_text.splitlines() if "ERROR:" in l})
    rec["raw_stderr_error_lines"] = sorted({l.strip() for l in
                                            err_text.splitlines() if "ERROR:" in l})
    pid_match = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    rec["godot_pid"] = int(pid_match.group(1)) if pid_match else None
    pid_match = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(pid_match.group(1)) if pid_match else None
    pid_match = re.search(r"DESCENDANT_PIPE_ERRFORGE write_ppid=(\d+)", text)
    rec["write_ppid"] = int(pid_match.group(1)) if pid_match else None
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    rec["descendant_kernel_ppid_at_return"] = kernel_ppid(rec["descendant_pid"])
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, SIG)
    stripped = "\n".join(l for l in text.splitlines() if "ERROR:" not in l)
    rec["stripped_classification"] = classify_process(
        rec["actual_exit"], rec["error"], stripped, 0, SIG)
    rec["output_lines"] = text.strip().splitlines()
    rec["stdout_lines"] = out_text.strip().splitlines()
    rec["stderr_lines"] = err_text.strip().splitlines()
    if proc.poll() is None:
        proc.kill()
    return rec


def splice_phantom():
    """stdout tail 'ERROR' + stderr head ':' -> merged line neither stream
    contained. The merged line-split FABRICATES an ERROR: line."""
    out_text = "DESCENDANT_PIPE_PROBE: expected signature\npartial line ending in ERROR"
    err_text = ": PHANTOM forged by the stdout|stderr concat boundary\n"
    text = out_text + err_text                        # the verbatim merge
    merged_lines = [l for l in text.splitlines() if "ERROR:" in l]
    raw = {"stdout_ERROR_lines": [l for l in out_text.splitlines() if "ERROR:" in l],
           "stderr_ERROR_lines": [l for l in err_text.splitlines() if "ERROR:" in l],
           "merged_ERROR_lines": merged_lines,
           "classification": classify_process(0, None, text, 0, SIG),
           "classification_no_splice": classify_process(
               0, None, out_text + "\n" + err_text, 0, SIG)}
    return raw


def allowlist_matrix():
    """Minimal mutations of the marker against the verbatim classifier —
    which forged strings flip and which escape, incl. the two OTHER reject
    clauses (SCRIPT ERROR:/Parse Error:) and allowlist-echo acceptance."""
    base = "DESCENDANT_PIPE_PROBE: expected signature\n"
    variants = {
        "errforge_verbatim": "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic",
        "lowercase_error": "error: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic",
        "mixedcase_Error": "Error: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic",
        "no_colon": "ERROR DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic",
        "spaced_colon": "ERROR : DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic",
        "midline": "prefix text ERROR: DESCENDANT_PIPE_ERRFORGE injected",
        "suffix_no_text": "ERROR:",
        "script_error_clause": "SCRIPT ERROR: forged post-death script marker",
        "parse_error_clause": "Parse Error: forged post-death parse marker",
        "warning_class": "WARNING: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic",
        "double_error_one_line": "ERROR: first ERROR: second on one line",
        "newline_split": "line ends in ERROR\n: colon starts next line",
    }
    table = {}
    for name, line in variants.items():
        text = base + line + "\n"
        table[name] = {
            "emitted": line,
            "rejects_empty_allowlist": not classify_process(0, None, text, 0, SIG),
            "error_lines_seen": sorted({l.strip() for l in text.splitlines()
                                        if "ERROR:" in l}),
        }
    # allowlisted-echo acceptance: a forged line exactly matching a per-case
    # allowlisted expected-error is ACCEPTED even post-death — the allowlist
    # is as origin-blind as everything else.
    allowlisted = "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR"
    table["allowlisted_echo_accepts"] = {
        "emitted": allowlisted,
        "rejects_empty_allowlist": not classify_process(
            0, None, base + allowlisted + "\n", 0, SIG),
        "accepts_when_allowlisted": classify_process(
            0, None, base + allowlisted + "\n", 0, SIG, (allowlisted,)),
    }
    # allowlist count==1 guard: allowlisted prefix + a second injected ERROR:
    # escapes the allowlist (count>1) -> still rejects.
    table["double_error_defeats_allowlist"] = {
        "rejects_even_allowlisted": not classify_process(
            0, None, base + allowlisted + " ERROR: tail\n", 0, SIG,
            (allowlisted,)),
    }
    return table


def main():
    outfile = ROOT / "probes" / "emitted_post_death.txt"
    outfile_late = ROOT / "probes" / "emitted_post_return.txt"
    for f in (outfile, outfile_late):
        if f.exists():
            f.unlink()
    records = {}
    records["detach_errforge"] = run_arm(
        "detach_errforge", ["--detach-errforge",
                            f"--errforge-outfile={outfile}"])
    records["detach_errforge_late"] = run_arm(
        "detach_errforge_late", ["--detach-errforge-late",
                                 f"--errforge-outfile={outfile_late}"])
    records["stderr_errforge"] = run_arm("stderr_errforge", ["--stderr-errforge"])
    records["double_errforge"] = run_arm("double_errforge", ["--double-errforge"])
    time.sleep(2.0)   # let the late detach arm's delayed emission land
    records["_splice_phantom"] = splice_phantom()
    records["_allowlist_matrix"] = allowlist_matrix()
    for f, key in ((outfile, "detach_emitted_file"),
                   (outfile_late, "detach_late_emitted_file")):
        records[key] = {"exists": f.exists(),
                        "content": f.read_text().splitlines() if f.exists() else []}
    # orphan hygiene for the stderr/double arms (they hold pipes briefly;
    # both already exited by EOF, but reap if not)
    for rec in records.values():
        if isinstance(rec, dict) and pid_alive(rec.get("descendant_pid")):
            try:
                os.kill(rec["descendant_pid"], signal.SIGKILL)
            except OSError:
                pass
    out = ROOT / "critic-probe-results.json"
    out.write_text(json.dumps(records, indent=2) + "\n")
    print(f"[harness] wrote {out}")
    for k, v in records.items():
        if isinstance(v, dict) and "inner_classification" in v:
            print(f"{k}: exit={v['actual_exit']} err={v['error']!r} "
                  f"sig={v['signature_observed']} errcap={v['error_marker_captured']} "
                  f"cls={v['inner_classification']} strip={v['stripped_classification']} "
                  f"err_lines={v['error_lines']}")


if __name__ == "__main__":
    main()
