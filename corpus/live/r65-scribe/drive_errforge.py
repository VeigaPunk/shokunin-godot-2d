#!/usr/bin/env python3
"""r65 scribe: forged-REJECTION dual — independent derivation.

The r65 declared claim: a reparenting-gated descendant that writes an
UN-ALLOWLISTED `ERROR:`-class marker into still-captured pipes AFTER the
direct child's death converts a genuine exit-0 + signature-present record
into a FAIL — i.e. classify_process's rejection axis is as origin-blind as
its signature (acceptance) axis was pinned to be at r63. Dual questions:
does the r64 while-live signature gate also reject the forged-error arm,
and which CASES-visible fields separate a forged error from a genuine
child-emitted error.

ast.get_source_segment-extracts run_process + classify_process VERBATIM from
the tracked corpus/fixtures/run_battery.py and execs them (production code
path, no transcription — the r61..r64 sibling-seat discipline).

Two observation paths per arm:
  naive  — the extracted run_process itself (subprocess.run capture_output
           + timeout) + extracted classify_process => the exact CASES-row
           verdict path.
  gated  — my scratch replica of run_battery.py's r64
           gated_signature_run (Popen + selectors + os.read; poll() at the
           marker-completing read) EXTENDED to also timestamp the first
           un-allowlisted ERROR-completing read and the child liveness at
           that instant — measuring whether the post-death error write is
           gate-visible in capture yet gate-invisible in verdict.

Arms: synthetic /usr/bin/sh children + real headless Godot children on the
scribe-owned proj/ fixture copy (tracked arms preserved; --self-error /
--errforge-* arms added there only).
"""
import ast
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
RUNNER = REPO / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
GODOT = sys.argv[1] if len(sys.argv) > 1 else "godot"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
MARKER_B = MARKER.encode()
ERR_MARKER = "ERROR: INJECTED_DIAGNOSTIC classification tripwire"
ERR_MARKER_B = ERR_MARKER.encode()
SCRIPT_ERR_B = b"SCRIPT ERROR: INJECTED_DIAGNOSTIC"
WITHHELD = "DESCENDANT_PIPE_FORGE child_signature=withheld"
BOUND = 3.0
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)

source = RUNNER.read_text()
tree = ast.parse(source)
funcs = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in (
            "run_process", "classify_process"):
        funcs[node.name] = ast.get_source_segment(source, node)
ns = {"subprocess": subprocess}
for name, seg in funcs.items():
    exec(seg, ns)
run_process = ns["run_process"]
classify_process = ns["classify_process"]

import hashlib
RUNNER_SHA = hashlib.sha256(source.encode()).hexdigest()


def proc_state(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return None


def kernel_ppid(pid):
    if pid is None or pid <= 0:
        return None
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return int(fh.read().rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        return None


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


def unrelated_error_lines(text, allowed_errors=()):
    """Mirror classify_process's scan inputs: every line containing
    'ERROR:' that is not allowlisted (allowed_errors always () here —
    CASES rows for this fixture carry no allowlist)."""
    return [line.strip() for line in text.splitlines() if "ERROR:" in line]


def cases_fields(code, error, text, expected_exit=0, signature=MARKER):
    """The exact fields classify_process reads."""
    return {
        "actual_exit": code, "expected_exit": expected_exit,
        "error": error, "signature_present": signature in text,
        "unrelated_error_lines": unrelated_error_lines(text),
        "script_error_present": "SCRIPT ERROR:" in text,
        "parse_error_present": "Parse Error:" in text,
        "verdict": classify_process(code, error, text, expected_exit,
                                    signature),
    }


def normalize_shape(text):
    """Line-shape fingerprint: pid/number values normalized so forged and
    genuine outputs compare on shape, not identity."""
    return [re.sub(r"\d+", "N", ln) for ln in text.strip().splitlines()]


def reap_descendant(text, rec):
    pid = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(pid.group(1)) if pid else None
    for pat, key in ((r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", "write_ppid"),
                     (r"DESCENDANT_PIPE_ERRFORGE write_ppid=(\d+)", "write_ppid")):
        m = re.search(pat, text)
        if m:
            rec[key] = int(m.group(1))
    rec.setdefault("write_ppid", None)
    rec["godot_pid"] = None
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    if m:
        rec["godot_pid"] = int(m.group(1))
    rec["descendant_kernel_ppid_at_return"] = kernel_ppid(
        rec["descendant_pid"])
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    if pid_alive(rec["descendant_pid"]):
        try:
            os.kill(rec["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass


# ---------------------------------------------------------------- naive path
def naive_run(command, bound, label):
    """The CASES path: extracted run_process + extracted classify_process."""
    rec = {"label": label, "path": "naive_run_process", "command": command,
           "bound_seconds": bound}
    t0 = time.monotonic()
    output, code, error = run_process(command, bound)
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 3)
    rec.update(cases_fields(code, error, output))
    rec["classify_if_error_none"] = classify_process(0, None, output, 0,
                                                     MARKER)
    rec["timed_out"] = error is not None and "TIMEOUT" in error
    rec["withheld_banner"] = WITHHELD in output
    rec["output_shape"] = normalize_shape(output)
    reap_descendant(output, rec)
    rec["output_lines"] = output.strip().splitlines()
    return rec


# ---------------------------------------------------------------- gated path
class DeathMonitor(threading.Thread):
    """Polls /proc/<pid>/stat ~1ms; first dead state WITHOUT reaping."""
    def __init__(self, pid):
        super().__init__(daemon=True)
        self.pid = pid
        self.t_death_ns = None
        self.death_state = None

    def run(self):
        while True:
            state = proc_state(self.pid)
            if state in ("Z", "X") or state is None:
                self.t_death_ns = time.monotonic_ns()
                self.death_state = state or "gone"
                return
            time.sleep(0.001)


def gated_run(command, bound, label):
    """While-live gate replica (r64 poll() primitive) + error-observation
    liveness. The gate VERDICT stays signature-scoped — the error fields are
    observation data, exactly what the tracked gate does and does not see."""
    t0 = time.monotonic_ns()

    def ms(ns):
        return None if ns is None else round((ns - t0) / 1e6, 3)

    rec = {"label": label, "path": "gated_read", "command": command,
           "bound_seconds": bound, "timed_out": False, "error": None,
           "child_exit": None, "t_marker_obs_ms": None,
           "alive_at_marker_obs": None, "t_error_obs_ms": None,
           "alive_at_error_obs": None, "t_death_ms": None,
           "death_state": None, "marker_minus_death_ms": None,
           "error_minus_death_ms": None, "dead_observed_at_gate_ms": None,
           "gated_signature_accepted": None}
    proc = None
    mon = None
    merged = bytearray()
    per_stream = {"stdout": bytearray(), "stderr": bytearray()}
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, bufsize=0)
        rec["child_pid"] = proc.pid
        mon = DeathMonitor(proc.pid)
        mon.start()
        sel = selectors.DefaultSelector()
        sel.register(proc.stdout, selectors.EVENT_READ, "stdout")
        sel.register(proc.stderr, selectors.EVENT_READ, "stderr")
        deadline = t0 + int(bound * 1e9)
        marker_seen = error_seen = False
        dead_seen_ms = None
        while sel.get_map():
            remaining = (deadline - time.monotonic_ns()) / 1e9
            if remaining <= 0:
                rec["timed_out"] = True
                rec["error"] = f"TIMEOUT after {bound} seconds"
                break
            for key, _ in sel.select(timeout=min(0.005, max(0.0, remaining))):
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except OSError:
                    chunk = b""
                now = time.monotonic_ns()
                if dead_seen_ms is None and proc.poll() is not None:
                    dead_seen_ms = ms(now)
                if chunk == b"":
                    sel.unregister(key.fileobj)
                    continue
                per_stream[key.data] += chunk
                merged += chunk
                if not marker_seen and MARKER_B in merged:
                    marker_seen = True
                    rec["t_marker_obs_ms"] = ms(now)
                    rec["alive_at_marker_obs"] = proc.poll() is None
                    rec["marker_stream"] = key.data
                if not error_seen and (ERR_MARKER_B in merged
                                       or SCRIPT_ERR_B in merged):
                    error_seen = True
                    rec["t_error_obs_ms"] = ms(now)
                    rec["alive_at_error_obs"] = proc.poll() is None
                    rec["error_stream"] = key.data
        rec["dead_observed_at_gate_ms"] = dead_seen_ms
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
    finally:
        if proc is not None and proc.poll() is None:
            try:
                proc.kill()
            except OSError:
                pass
        exit_code = None
        if proc is not None:
            try:
                exit_code = proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] = (rec["error"] or "") + "; post-kill wait timed out"
            except ChildProcessError:
                exit_code = proc.returncode
        rec["child_exit"] = exit_code if exit_code is not None else (
            proc.returncode if proc else None)
        if mon is not None:
            mon.join(timeout=0.2)
            rec["t_death_ms"] = ms(mon.t_death_ns)
            rec["death_state"] = mon.death_state
    text = (bytes(per_stream["stdout"]) + bytes(per_stream["stderr"])).decode(
        errors="replace")
    if rec["t_marker_obs_ms"] is not None and rec["t_death_ms"] is not None:
        rec["marker_minus_death_ms"] = round(
            rec["t_marker_obs_ms"] - rec["t_death_ms"], 3)
    if rec["t_error_obs_ms"] is not None and rec["t_death_ms"] is not None:
        rec["error_minus_death_ms"] = round(
            rec["t_error_obs_ms"] - rec["t_death_ms"], 3)
    rec["gated_signature_accepted"] = bool(
        rec["t_marker_obs_ms"] is not None and rec["alive_at_marker_obs"])
    rec.update({f"cases_{k}": v for k, v in
                cases_fields(rec["child_exit"], rec["error"], text).items()})
    rec["withheld_banner"] = WITHHELD in text
    reap_descendant(text, rec)
    rec["output_lines"] = text.strip().splitlines()
    return rec


# ------------------------------------------------------------------- arms
def sh_errforge(tail="", err_line=None, sig_line=None, quiet=False,
                stream=""):
    """sh child: prints MARKER + godot-ish pid (unless withheld), spawns a
    ppid-gated descendant (the fixture's own /proc/self/stat gate) that
    writes err_line (default ERR_MARKER) post-death."""
    err = err_line or ERR_MARKER
    pre = "" if sig_line == "withhold" else f'echo "{MARKER}"; '
    # unquoted echo: the desc lives inside a single-quoted inner sh -c, so
    # embedded single quotes would break it (the fixture does the same for
    # MARKER — echo takes the marker's spaces as separate args)
    desc = (f'echo {err}{stream}; ' +
            ("" if quiet else
             f'echo "DESCENDANT_PIPE_ERRFORGE write_ppid=$pp"{stream}; ')
            + (f'echo "{MARKER}"; ' if sig_line == "withhold" else ""))
    return ["/usr/bin/sh", "-c",
            pre + 'echo DESCENDANT_PIPE godot_pid=$$; '
            'sh -c \'while read -r _ _ _ pp _ < /proc/self/stat && '
            '[ "$pp" = "\'$$\'" ]; do sleep 0.05; done; ' + desc + tail +
            '\' & ' + ("" if quiet else 'echo DESCENDANT_PIPE spawned_pid=$!; ')
            + 'exit 0']


ARMS_SH = {
    "syn_genuine": ["/usr/bin/sh", "-c",
                    f'echo "{MARKER}"; echo DESCENDANT_PIPE godot_pid=$$; exit 0'],
    "syn_self_error": ["/usr/bin/sh", "-c",
                       f'echo "{MARKER}"; echo DESCENDANT_PIPE godot_pid=$$; '
                       f'echo \'{ERR_MARKER}\'; exit 0'],
    "syn_errforge_release": sh_errforge(),
    "syn_errforge_quiet": sh_errforge(quiet=True),
    "syn_errforge_hold": sh_errforge(tail="sleep 6"),
    "syn_errforge_stderr": sh_errforge(stream=" >&2"),
    # forged-PASS + forged-FAIL in one post-death batch: withheld signature
    # AND error both descendant-written.
    "syn_errforge_withhold": sh_errforge(sig_line="withhold"),
    "syn_script_errforge": sh_errforge(
        err_line="SCRIPT ERROR: INJECTED_DIAGNOSTIC classification tripwire"),
    # live-window error forgery (no gate): descendant writes while the child
    # still sleeps — the reject-axis analog of r64's pre-forge blind side.
    "syn_pre_error": ["/usr/bin/sh", "-c",
                      f'echo "{MARKER}"; echo DESCENDANT_PIPE godot_pid=$$; '
                      f'sh -c \'sleep 0.25; echo {ERR_MARKER}; '
                      'echo "DESCENDANT_PIPE_ERRFORGE write_ppid=$PPID"\' & '
                      'echo DESCENDANT_PIPE spawned_pid=$!; sleep 1.5; exit 0'],
    # r63 contrast: forged signature, NO error — the accept-axis forgery.
    "syn_sigforge_release": ["/usr/bin/sh", "-c",
                             'echo DESCENDANT_PIPE godot_pid=$$; '
                             'sh -c \'while read -r _ _ _ pp _ < /proc/self/stat && '
                             '[ "$pp" = "\'$$\'" ]; do sleep 0.05; done; '
                             f'echo "{MARKER}"; '
                             'echo "DESCENDANT_PIPE_FORGE write_ppid=$pp"\' & '
                             'echo DESCENDANT_PIPE spawned_pid=$!; exit 0'],
}


def godot_cmd(flags):
    return [GODOT, "--headless", "--path", str(PROJ), "--script",
            "res://descendant_pipe_probe.gd", "--", *flags]


ARMS_GODOT = {
    "godot_genuine": godot_cmd([]),
    "godot_self_error": godot_cmd(["--self-error"]),
    "godot_detach": godot_cmd(["--spawn-detach"]),
    "godot_errforge_release": godot_cmd(["--errforge-release"]),
    "godot_errforge_quiet": godot_cmd(["--errforge-quiet"]),
    "godot_errforge_hold": godot_cmd(["--errforge-hold"]),
    "godot_errforge_stderr": godot_cmd(["--errforge-stderr"]),
    "godot_errforge_withhold": godot_cmd(["--errforge-withhold"]),
    "godot_errforge_script": godot_cmd(["--errforge-script"]),
    "godot_sigforge_release": godot_cmd(["--spawn-forge-release"]),
}

# (arm, path, reps, bound)
MATRIX = [
    ("syn_genuine", "naive", 5, BOUND),
    ("syn_self_error", "naive", 5, BOUND),
    ("syn_errforge_release", "naive", 15, BOUND),
    ("syn_errforge_quiet", "naive", 10, BOUND),
    ("syn_errforge_hold", "naive", 3, BOUND),
    ("syn_errforge_stderr", "naive", 5, BOUND),
    ("syn_errforge_withhold", "naive", 5, BOUND),
    ("syn_script_errforge", "naive", 5, BOUND),
    ("syn_pre_error", "naive", 5, BOUND),
    ("syn_sigforge_release", "naive", 5, BOUND),
    ("syn_genuine", "gated", 5, BOUND),
    ("syn_self_error", "gated", 5, BOUND),
    ("syn_errforge_release", "gated", 10, BOUND),
    ("syn_errforge_quiet", "gated", 5, BOUND),
    ("syn_errforge_hold", "gated", 2, BOUND),
    ("syn_errforge_withhold", "gated", 5, BOUND),
    ("syn_pre_error", "gated", 5, BOUND),
    ("syn_sigforge_release", "gated", 5, BOUND),
    ("godot_genuine", "naive", 3, BOUND),
    ("godot_self_error", "naive", 3, BOUND),
    ("godot_detach", "naive", 2, BOUND),
    ("godot_errforge_release", "naive", 8, BOUND),
    ("godot_errforge_quiet", "naive", 3, BOUND),
    ("godot_errforge_hold", "naive", 2, BOUND),
    ("godot_errforge_stderr", "naive", 3, BOUND),
    ("godot_errforge_withhold", "naive", 3, BOUND),
    ("godot_errforge_script", "naive", 3, BOUND),
    ("godot_sigforge_release", "naive", 3, BOUND),
    ("godot_genuine", "gated", 3, BOUND),
    ("godot_self_error", "gated", 3, BOUND),
    ("godot_errforge_release", "gated", 5, BOUND),
    ("godot_errforge_quiet", "gated", 3, BOUND),
    ("godot_errforge_hold", "gated", 2, BOUND),
    ("godot_errforge_withhold", "gated", 3, BOUND),
    ("godot_sigforge_release", "gated", 3, BOUND),
]


def main():
    records = []
    for arm, path, reps, bound in MATRIX:
        cmd = ARMS_SH.get(arm) or ARMS_GODOT[arm]
        for rep in range(reps):
            if path == "naive":
                rec = naive_run(cmd, bound, f"{arm}#{rep}")
                print(f"{arm:26s} naive rep={rep} "
                      f"exit={rec['actual_exit']} err={rec['error']!r} "
                      f"sig={rec['signature_present']} "
                      f"unrel={len(rec['unrelated_error_lines'])} "
                      f"verdict={rec['verdict']} "
                      f"if_none={rec['classify_if_error_none']} "
                      f"wppid={rec.get('write_ppid')}", flush=True)
            else:
                rec = gated_run(cmd, bound, f"{arm}#{rep}")
                print(f"{arm:26s} gated rep={rep} "
                      f"mark@{rec['t_marker_obs_ms']}({rec['alive_at_marker_obs']}) "
                      f"err@{rec['t_error_obs_ms']}({rec['alive_at_error_obs']}) "
                      f"death@{rec['t_death_ms']} "
                      f"gated_acc={rec['gated_signature_accepted']} "
                      f"classify={rec['cases_verdict']}", flush=True)
            rec["arm"] = arm
            rec["rep"] = rep
            records.append(rec)
            (RAW / f"{arm}-{path}-{rep}.stdout").write_text(
                "\n".join(rec["output_lines"]) + "\n")
    payload = {"runner": str(RUNNER), "runner_sha256": RUNNER_SHA,
               "extraction": "ast.get_source_segment verbatim exec of "
                             "run_process + classify_process",
               "signature": MARKER, "error_marker": ERR_MARKER,
               "godot": GODOT, "proj": str(PROJ),
               "arms": records}
    out = HERE / "errforge-verdicts.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
