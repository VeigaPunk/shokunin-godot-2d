#!/usr/bin/env python3
"""r64 scout: while-live signature-read gate — insertion-surface measurements.

ast.get_source_segment-extracts run_process + classify_process VERBATIM from
the tracked corpus/fixtures/run_battery.py (production code path — the
r61/r62/r63 sibling-seat discipline) for the presence-axis baseline.

Mechanism arms use /usr/bin/sh children (the classifier sees bytes + exit;
the gate sees liveness — POSIX semantics, same as r63-scout). The decisive
arms re-measure under REAL Godot 4.7.2 on a scratch copy of the tracked
fixture (proj/ = project.godot + descendant_pipe_probe.gd copied verbatim).

Questions under measurement (r64 brief):
  Q1  where can an observation be timestamped vs child liveness, and which
      liveness primitive is sound: proc.poll() (waitpid WNOHANG),
      os.kill(pid,0), /proc/<pid> existence-or-state.
  Q2  do pipe-buffered bytes survive child death (post-death read observes
      pre-death bytes) — i.e. is "observed while alive" the checkable
      property, never "written while alive".

Gate semantics under test: a line is "live-observed" iff the liveness check
performed IMMEDIATELY after the readline() that returned it still reports
the child running. Events carry a non-destructive truth channel too:
/proc/<pid>/stat state char (Z/X = dead-or-dying; None-after-alive = reaped).

Arms:
  bytes_survive_death   child writes SIG, exits, is reaped; parent reads
                        pipe 0.5s later -> SIG still delivered (Q2 proof)
  sh_genuine x REPS     `echo SIG; exit 0` fast-exit genuine lower bound
  sh_forge_poll         ppid-gated descendant writes SIG post-death, exits;
                        gate = proc.poll()
  sh_forge_kill0        same shape; gate = os.kill(pid,0) (never reaps
                        in-loop -> zombie probe)
  godot_genuine x REPS  real fixture default arm (no flags)
  godot_forge_release   real --spawn-forge-release under poll gate
  godot_forge_hold      real --spawn-forge-hold under poll gate, bound 3.0
"""
import ast
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE.parent.parent / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
BOUND = 3.0
GODOT = "godot"
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
    """/proc/<pid>/stat state char; None if unreadable (gone/reaped)."""
    try:
        with open(f"/proc/{pid}/stat") as stat_file:
            return stat_file.read().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return None


def gated_read(cmd, bound, gate):
    """Selector+readline loop; per-line liveness gate + truth channel.

    gate: 'poll'     -> proc.poll() is None   (waitpid WNOHANG, reaps)
          'kill0'    -> os.kill(pid,0)        (zombie-blind; never poll in-loop)
          'procstat' -> /proc/<pid>/stat state not in {Z,X}
    """
    rec = {"command": cmd, "gate": gate, "bound_seconds": bound,
           "timed_out": False, "error": None, "actual_exit": None,
           "events": [], "t_first_dead": None, "t_marker": None,
           "marker_observed": False, "marker_while_live": False,
           "marker_states": []}
    t0 = time.monotonic()
    proc = None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, bufsize=1)

        def gate_alive():
            if gate == "poll":
                return proc.poll() is None
            if gate == "kill0":
                try:
                    os.kill(proc.pid, 0)
                    return True
                except OSError:
                    return False
            # procstat
            return proc_state(proc.pid) not in ("Z", "X", None)

        sel = selectors.DefaultSelector()
        sel.register(proc.stdout, selectors.EVENT_READ, "stdout")
        sel.register(proc.stderr, selectors.EVENT_READ, "stderr")
        deadline = t0 + bound
        eof = set()
        seen_alive = False
        truth_dead_t = None
        while time.monotonic() < deadline and len(eof) < 2:
            now = time.monotonic() - t0
            state = proc_state(proc.pid)
            if state in ("R", "S", "D", "T", "I"):
                seen_alive = True
            if truth_dead_t is None and seen_alive and state in ("Z", "X", None):
                truth_dead_t = now
            for key, _ in sel.select(min(0.02, max(0.0, deadline - time.monotonic()))):
                line = key.fileobj.readline()
                if line == "":
                    eof.add(key.data)
                    try:
                        sel.unregister(key.fileobj)
                    except Exception:
                        pass
                    continue
                t_line = time.monotonic() - t0
                alive = gate_alive()
                state_at = proc_state(proc.pid)
                rec["events"].append({"t": round(t_line, 6), "stream": key.data,
                                      "line": line.rstrip("\n"),
                                      "gate_alive": alive, "state": state_at})
                if SIG in line:
                    rec["marker_observed"] = True
                    if rec["t_marker"] is None:
                        rec["t_marker"] = round(t_line, 6)
                    if alive:
                        rec["marker_while_live"] = True
                    rec["marker_states"].append(state_at)
                if truth_dead_t is None and seen_alive and state_at in ("Z", "X", None):
                    truth_dead_t = t_line
        sel.close()
        rec["timed_out"] = len(eof) < 2
        rec["t_first_dead"] = round(truth_dead_t, 6) if truth_dead_t is not None else None
        # drain + reap (bounded)
        try:
            out, err = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate(timeout=3)
            rec["error"] = (rec["error"] or "") + "; post-bound cleanup kill"
        rec["actual_exit"] = proc.returncode
        remainder = (out or "") + (err or "")
        rec["remainder"] = remainder
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
        if proc is not None and proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] += "; forced cleanup timed out"
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 3)
    merged = "".join(e["line"] + "\n" for e in rec["events"]) + rec.get("remainder", "")
    rec["merged_text"] = merged
    rec["presence_class"] = classify_process(
        rec["actual_exit"], rec["error"] or (f"TIMEOUT after {bound} seconds" if rec["timed_out"] else None),
        merged, 0, SIG)
    rec["gated_class"] = bool(rec["marker_while_live"]
                              and rec["actual_exit"] == 0 and not rec["timed_out"])
    return rec


# --- arm: bytes_survive_death (Q2 direct) ---------------------------------
surv = {"arm": "bytes_survive_death"}
p = subprocess.Popen(["/usr/bin/sh", "-c", f'echo "{SIG}"; exit 0'],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
rc = p.wait()                       # full reap: child provably dead AND gone
time.sleep(0.5)
surv["child_reaped_exit"] = rc
surv["proc_dir_exists_after_reap"] = Path(f"/proc/{p.pid}").exists()
data = p.stdout.read() + p.stderr.read()
surv["post_death_read_text"] = data.strip().splitlines()
surv["sig_observed_after_death"] = SIG in data
print("bytes_survive_death:", surv["sig_observed_after_death"],
      "| reaped exit", rc, "| /proc gone:", not surv["proc_dir_exists_after_reap"])
(RAW / "bytes_survive_death.stdout").write_text(data)


# --- sh forge-arm shapes (ppid-gated, fixture-equivalent) ------------------
def sh_forge_cmd(tail):
    return ["/usr/bin/sh", "-c",
            'echo WL_CHILD_PID=$$; '
            'sh -c \'while read -r _ _ _ pp _ < /proc/self/stat && '
            '[ "$pp" = "\'$$\'" ]; do sleep 0.05; done; ' + tail + '\' & '
            'echo WL_DESC_PID=$!; exit 0']


records = []
REPS_FAST = 20
for i in range(REPS_FAST):
    r = gated_read(["/usr/bin/sh", "-c",
                    f'echo "{SIG}"; echo WL_CHILD_PID=$$; exit 0'],
                   BOUND, "poll")
    r["arm"] = "sh_genuine"; r["rep"] = i
    records.append(r)
print("sh_genuine: live-observed",
      sum(r["marker_while_live"] for r in records), "/", REPS_FAST)

for gate, arm, reps in (("poll", "sh_forge_poll", 5),
                        ("kill0", "sh_forge_kill0", 5),
                        ("procstat", "sh_forge_procstat", 5)):
    for i in range(reps):
        r = gated_read(sh_forge_cmd(f'echo "{SIG}"; echo WL_FORGE write_ppid=$pp'),
                       BOUND, gate)
        r["arm"] = arm; r["rep"] = i
        records.append(r)
    live = sum(r["marker_while_live"] for r in records if r["arm"] == arm)
    obs = sum(r["marker_observed"] for r in records if r["arm"] == arm)
    print(f"{arm}: observed {obs}/{reps} while-live {live}/{reps}")

# --- real Godot arms --------------------------------------------------------
godot_cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
             "res://descendant_pipe_probe.gd"]

REPS_GODOT = 10
for i in range(REPS_GODOT):
    r = gated_read(godot_cmd, BOUND, "poll")
    r["arm"] = "godot_genuine"; r["rep"] = i
    records.append(r)
live = sum(r["marker_while_live"] for r in records if r["arm"] == "godot_genuine")
print("godot_genuine: live-observed", live, "/", REPS_GODOT)

for i in range(5):
    r = gated_read(godot_cmd + ["--", "--spawn-forge-release"], BOUND, "poll")
    r["arm"] = "godot_forge_release"; r["rep"] = i
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", r["merged_text"])
    r["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", r["merged_text"])
    r["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", r["merged_text"])
    r["write_ppid"] = int(m.group(1)) if m else None
    records.append(r)
obs = sum(r["marker_observed"] for r in records if r["arm"] == "godot_forge_release")
live = sum(r["marker_while_live"] for r in records if r["arm"] == "godot_forge_release")
print(f"godot_forge_release: observed {obs}/5 while-live {live}/5")

for i in range(3):
    r = gated_read(godot_cmd + ["--", "--spawn-forge-hold"], BOUND, "poll")
    r["arm"] = "godot_forge_hold"; r["rep"] = i
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", r["merged_text"])
    r["descendant_pid"] = int(m.group(1)) if m else None
    records.append(r)
    # orphan hygiene — same duty as the tracked meta rows
    if r["descendant_pid"]:
        try:
            os.kill(r["descendant_pid"], 0)
            os.kill(r["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass
obs = sum(r["marker_observed"] for r in records if r["arm"] == "godot_forge_hold")
live = sum(r["marker_while_live"] for r in records if r["arm"] == "godot_forge_hold")
print(f"godot_forge_hold: observed {obs}/3 while-live {live}/3")

payload = {"runner": str(RUNNER),
           "extraction": "ast.get_source_segment verbatim exec",
           "signature": SIG, "bound_seconds": BOUND,
           "bytes_survive_death": surv, "arms": records}
(HERE / "whilelive-verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
for r in records:
    print(f'{r["arm"]}[{r["rep"]}] gate={r["gate"]} exit={r["actual_exit"]} '
          f'to={r["timed_out"]} sig={r["marker_observed"]} '
          f'live={r["marker_while_live"]} t_sig={r["t_marker"]} '
          f't_dead={r["t_first_dead"]} states={r["marker_states"]} '
          f'presence={r["presence_class"]} gated={r["gated_class"]}')
