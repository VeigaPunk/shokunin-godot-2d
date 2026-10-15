#!/usr/bin/env python3
"""r64 scribe: while-live signature-gate discrimination measurement.

Independent re-derivation of the mechanism the r64 axis-move claims: a
marker read GATED ON CHILD LIVENESS AT OBSERVATION TIME should reject the
forged post-death signature (fixture arms --spawn-forge-release /
--spawn-forge-hold) while still accepting the genuine child signature
(unmodified descendant_pipe_probe default arm).

ast.get_source_segment-extracts run_process + classify_process VERBATIM from
the tracked corpus/fixtures/run_battery.py and execs them (production code
path, no transcription — the r61/r62/r63 sibling-seat discipline). The gate
under test is my own scratch read loop: Popen + selectors + os.read; on the
chunk that first completes the marker in the arrival buffer, evaluate one
of five child-liveness primitives:

  poll        proc.poll() is None            (waitpid WNOHANG; REAPS zombies)
  waitid      os.waitid(WEXITED|WNOHANG|WNOWAIT) is None   (kernel state, no reap)
  procstat    /proc/<pid>/stat state not in {Z,X}           (kernel state, no reap)
  kill0       os.kill(pid, 0) succeeds        (signal-0: zombie reads ALIVE)
  returncode  proc.returncode is None         (stale attribute, never reaps)

A separate monitor thread polls /proc/<pid>/stat ~every 2ms to timestamp
the real death (first Z/X/vanish) WITHOUT reaping, so death-vs-observation
deltas are measured independently of the gate primitive under test.

Arms: synthetic /usr/bin/sh children (fast: genuine fast/slow, ppid-gated
forge release/hold mirroring the fixture's own gate, pre-death forgery
control) plus REAL headless Godot children on the tracked fixture
descendant_pipe_probe.gd (default / --spawn-detach / --spawn-forge-release
/ --spawn-forge-hold) on a two-file scratch project copy.
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
BOUND = 3.0
BOUND_HOLD = 3.0
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


def proc_state(pid):
    """Kernel /proc state char: 'R','S','Z','X',... or None if gone."""
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
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


class DeathMonitor(threading.Thread):
    """Polls /proc/<pid>/stat; records first dead state ('Z','X') or
    disappearance, WITHOUT reaping (zombie semantics preserved)."""

    def __init__(self, pid):
        super().__init__(daemon=True)
        self.pid = pid
        self.t_death_ns = None
        self.death_state = None
        self.samples = 0
        self._t0 = None

    def run(self):
        self._t0 = time.monotonic_ns()
        while True:
            self.samples += 1
            state = proc_state(self.pid)
            if state in ("Z", "X") or state is None:
                self.t_death_ns = time.monotonic_ns()
                self.death_state = state or "gone"
                return
            time.sleep(0.001)


def gate_answer(gate, proc):
    """Evaluate child liveness at this instant under the named primitive."""
    if gate == "poll":
        rc = proc.poll()
        return rc is None, f"poll()={rc!r}"
    if gate == "poll_delay50":
        # Reader-lag stress: 50ms between pipe-read and the liveness eval —
        # models a slow/batched reader checking liveness at consume time.
        time.sleep(0.05)
        rc = proc.poll()
        return rc is None, f"poll()={rc!r} after 50ms lag"
    if gate == "waitid":
        try:
            res = os.waitid(os.P_PID, proc.pid,
                            os.WEXITED | os.WNOHANG | os.WNOWAIT)
        except ChildProcessError:
            return False, "waitid ChildProcessError(reaped)"
        return res is None, f"waitid={res!r}"
    if gate == "procstat":
        state = proc_state(proc.pid)
        return state not in ("Z", "X") and state is not None, f"state={state!r}"
    if gate == "kill0":
        try:
            os.kill(proc.pid, 0)
        except ProcessLookupError:
            return False, "kill ESRCH"
        except PermissionError:
            return True, "kill EPERM"
        return True, "kill ok"
    if gate == "returncode":
        return proc.returncode is None, f"returncode={proc.returncode!r}"
    raise ValueError(gate)


def gated_run(command, gate, bound, label):
    """One bounded while-live gated read. Returns the measurement record."""
    t0 = time.monotonic_ns()

    def ms(ns):
        return None if ns is None else round((ns - t0) / 1e6, 3)

    rec = {"label": label, "gate": gate, "command": command,
           "marker": MARKER, "bound_seconds": bound,
           "child_pid": None, "descendant_pid": None,
           "t_marker_obs_ms": None, "marker_stream": None,
           "alive_at_obs": None, "gate_detail_at_obs": None,
           "t_death_ms": None, "death_state": None,
           "obs_minus_death_ms": None,
           "t_eof_ms": None, "elapsed_ms": None, "timed_out": False,
           "error": None, "child_exit": None,
           "zombie_linger_ms": None,
           "descendant_alive_at_return": None,
           "gated_accept": None, "naive_marker_present": None,
           "naive_classify": None, "classify_if_error_none": None}
    proc = None
    mon = None
    merged_arrival = bytearray()   # arrival-ordered (what the gate sees)
    per_stream = {"stdout": bytearray(), "stderr": bytearray()}
    events = []
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
        marker_seen = False
        while sel.get_map():
            remaining = (deadline - time.monotonic_ns()) / 1e9
            if remaining <= 0:
                rec["timed_out"] = True
                rec["error"] = f"TIMEOUT after {bound} seconds"
                break
            for key, _ in sel.select(timeout=remaining):
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except OSError:
                    chunk = b""
                now = time.monotonic_ns()
                if chunk == b"":
                    sel.unregister(key.fileobj)
                    events.append({"t_ms": ms(now), "stream": key.data,
                                   "kind": "eof"})
                    continue
                per_stream[key.data] += chunk
                merged_arrival += chunk
                events.append({"t_ms": ms(now), "stream": key.data,
                               "kind": "data", "bytes": len(chunk)})
                if not marker_seen and MARKER_B in merged_arrival:
                    marker_seen = True
                    alive, detail = gate_answer(gate, proc)
                    rec["t_marker_obs_ms"] = ms(now)
                    rec["marker_stream"] = key.data
                    rec["alive_at_obs"] = alive
                    rec["gate_detail_at_obs"] = detail
        rec["t_eof_ms"] = ms(time.monotonic_ns())
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
    finally:
        if rec["timed_out"] or (proc is not None and proc.poll() is None
                                and mon is not None and mon.t_death_ns is None):
            if proc is not None and proc.poll() is None:
                try:
                    proc.kill()
                except OSError:
                    pass
        reap0 = time.monotonic_ns()
        exit_code = None
        if proc is not None:
            try:
                exit_code = proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] = (rec["error"] or "") + "; post-kill wait timed out"
            except ChildProcessError:
                exit_code = proc.returncode
        rec["child_exit"] = exit_code if exit_code is not None else proc.returncode if proc else None
        if mon is not None:
            mon.join(timeout=0.2)
            rec["t_death_ms"] = ms(mon.t_death_ns)
            rec["death_state"] = mon.death_state
            rec["monitor_samples"] = mon.samples
        if rec["t_death_ms"] is not None and mon is not None:
            # How long the child sat as a reapable corpse before we reaped:
            # the window during which kill0/returncode gates read 'alive'.
            if mon.death_state == "Z":
                rec["zombie_linger_ms"] = round(
                    (reap0 - mon.t_death_ns) / 1e6, 3)
    rec["elapsed_ms"] = ms(time.monotonic_ns())
    text = (bytes(per_stream["stdout"]) + bytes(per_stream["stderr"])).decode(
        errors="replace")
    rec["naive_marker_present"] = MARKER in text
    rec["naive_classify"] = classify_process(
        rec["child_exit"], rec["error"], text, 0, MARKER)
    rec["classify_if_error_none"] = classify_process(
        0, None, text, 0, MARKER)
    rec["gated_accept"] = bool(rec["t_marker_obs_ms"] is not None
                               and rec["alive_at_obs"])
    if rec["t_marker_obs_ms"] is not None and rec["t_death_ms"] is not None:
        rec["obs_minus_death_ms"] = round(
            rec["t_marker_obs_ms"] - rec["t_death_ms"], 3)
    pid = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    if pid:
        rec["descendant_pid"] = int(pid.group(1))
    wppid = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", text)
    rec["write_ppid"] = int(wppid.group(1)) if wppid else None
    if pid_alive(rec["descendant_pid"]):
        rec["descendant_alive_at_return"] = True
        try:
            os.kill(rec["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass
    else:
        rec["descendant_alive_at_return"] = (
            False if rec["descendant_pid"] else None)
    rec["output_lines"] = text.strip().splitlines()
    rec["events"] = events
    return rec


# --- synthetic /usr/bin/sh arms -------------------------------------------
# The descendant ppid-flip gate is the fixture's own (descendant_pipe_probe.gd
# L56-65): poll /proc/self/stat until ppid != child pid -> provably post-exit.
GATE = ('while read -r _ _ _ pp _ < /proc/self/stat && '
        '[ "$pp" = "{pid}" ]; do sleep 0.05; done; ')


def sh_child(desc_tail):
    """Child prints pids, spawns pipe-inheriting gated descendant, exits 0.
    Never prints the signature itself — any captured MARKER is the
    descendant's post-death write (the fixture's forge-arm shape)."""
    return ["/usr/bin/sh", "-c",
            'echo WL_CHILD_PID=$$; '
            'sh -c \'while read -r _ _ _ pp _ < /proc/self/stat && '
            '[ "$pp" = "\'$$\'" ]; do sleep 0.05; done; ' + desc_tail + '\' & '
            'echo DESCENDANT_PIPE spawned_pid=$!; exit 0']


ARMS_SH = {
    "syn_genuine_fast": ["/usr/bin/sh", "-c",
                         f'echo "{MARKER}"; exit 0'],
    "syn_genuine_slow": ["/usr/bin/sh", "-c",
                         f'echo "{MARKER}"; sleep 0.4; exit 0'],
    "syn_release": sh_child(
        f'echo "{MARKER}"; echo "DESCENDANT_PIPE_FORGE write_ppid=$pp"'),
    "syn_hold": sh_child(
        f'echo "{MARKER}"; echo "DESCENDANT_PIPE_FORGE write_ppid=$pp"; sleep 5'),
    # Pre-death forgery control: descendant writes while the child is still
    # alive (no ppid gate) — the gate's blind side by construction.
    "syn_pre_forge": ["/usr/bin/sh", "-c",
                      'echo WL_CHILD_PID=$$; '
                      f'sh -c \'sleep 0.25; echo "{MARKER}"; echo '
                      'DESCENDANT_PIPE_FORGE write_ppid=$PPID\' & '
                      'echo DESCENDANT_PIPE spawned_pid=$!; sleep 1.5; exit 0'],
}


def godot_cmd(flags):
    return [GODOT, "--headless", "--path", str(PROJ), "--script",
            "res://descendant_pipe_probe.gd", "--", *flags]


ARMS_GODOT = {
    "godot_genuine": godot_cmd([]),
    "godot_detach": godot_cmd(["--spawn-detach"]),
    "godot_release": godot_cmd(["--spawn-forge-release"]),
    "godot_hold": godot_cmd(["--spawn-forge-hold"]),
}

MATRIX = [
    # (arm, gate, reps, bound)
    ("syn_genuine_fast", "poll", 30, BOUND),
    ("syn_genuine_fast", "kill0", 10, BOUND),
    ("syn_genuine_slow", "poll", 10, BOUND),
    ("syn_release", "poll", 15, BOUND),
    ("syn_release", "waitid", 5, BOUND),
    ("syn_release", "procstat", 5, BOUND),
    ("syn_release", "kill0", 10, BOUND),
    ("syn_release", "returncode", 10, BOUND),
    ("syn_hold", "poll", 3, BOUND_HOLD),
    ("syn_hold", "kill0", 2, BOUND_HOLD),
    ("syn_pre_forge", "poll", 10, BOUND),
    ("syn_genuine_fast", "poll_delay50", 10, BOUND),
    ("syn_release", "poll_delay50", 5, BOUND),
    ("godot_genuine", "poll_delay50", 3, BOUND),
    ("godot_release", "poll_delay50", 2, BOUND),
    ("godot_genuine", "poll", 5, BOUND),
    ("godot_genuine", "kill0", 3, BOUND),
    ("godot_detach", "poll", 2, BOUND),
    ("godot_release", "poll", 5, BOUND),
    ("godot_release", "procstat", 2, BOUND),
    ("godot_release", "kill0", 3, BOUND),
    ("godot_release", "returncode", 3, BOUND),
    ("godot_hold", "poll", 2, BOUND_HOLD),
    ("godot_hold", "kill0", 1, BOUND_HOLD),
]


def main():
    records = []
    for arm, gate, reps, bound in MATRIX:
        cmd = ARMS_SH.get(arm) or ARMS_GODOT[arm]
        for rep in range(reps):
            rec = gated_run(cmd, gate, bound, f"{arm}#{rep}")
            rec["arm"] = arm
            rec["rep"] = rep
            records.append(rec)
            print(f"{arm:22s} gate={gate:10s} rep={rep} "
                  f"marker@{rec['t_marker_obs_ms']}ms "
                  f"death@{rec['t_death_ms']}ms({rec['death_state']}) "
                  f"alive_at_obs={rec['alive_at_obs']} "
                  f"gated={rec['gated_accept']} "
                  f"naive={rec['naive_marker_present']}/"
                  f"{rec['naive_classify']} "
                  f"exit={rec['child_exit']} err={rec['error']}",
                  flush=True)
            (RAW / f"{arm}-{gate}-{rep}.stdout").write_text(
                "\n".join(rec["output_lines"]) + "\n")
    payload = {"runner": str(RUNNER),
               "extraction": "ast.get_source_segment verbatim exec",
               "gate_design": "marker accepted only if observed while child "
                              "alive at observation time; five liveness "
                              "primitives compared; /proc monitor "
                              "(non-reaping) timestamps real death",
               "signature": MARKER, "godot": GODOT, "proj": str(PROJ),
               "arms": records}
    out = HERE / "whilelive-verdicts.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
