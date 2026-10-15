#!/usr/bin/env python3
"""r64 boundary driver: edge probes of the while-live signature gate.

Seat: boundary. Scratch-only. Probes the LANDED r64 author meta arm —
`gated_signature_run` inside the working-tree corpus/fixtures/run_battery.py —
on four edges (lane brief):

  1. zombie window: how long a dead-but-unreaped child satisfies kill(pid,0)
     under the runner's communicate() pattern, and whether the gate's
     liveness check ever lands inside that window.
  2. stderr-channel forgery under the gate (merged-capture read).
  3. gate under scheduler load: does the genuine arm ever false-negative.
  4. pre-death forged write: fixture producibility + gate acceptance knee.

Method discipline (r61-r63 lineage): production code paths are
ast.get_source_segment-extracted from the working-tree runner and exec'd —
`classify_process`, `classify_streams`, `pid_alive`, `kernel_ppid`, and the
landed `gated_signature_run` itself (verbatim gate = PRODUCTION evidence).
Instrumented variants (`gated_replica`, `communicate_replica`) replicate the
same loops line-for-line and add a /proc monitor + per-stream buffers; their
timings are corroborating replica evidence, marked replica=True.

Monitor: 1ms transition sampler on /proc/<pid>/stat (state, ppid) plus
os.kill(pid,0) — kill(0) NEVER reaps; it measures the zombie-satisfying
window truthfully. The gate's own poll() is the only reaper in poll mode;
in kill0 mode nothing reaps until post-loop wait() — that is the point.

Receipts: edge-verdicts.json (per-run records), edge-timeline.json (monitor
transitions), raw/<case>.stdout (merged captured bytes per run).
"""
import ast
import hashlib
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
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNNER = REPO / "corpus" / "fixtures" / "run_battery.py"
FIXTURE = REPO / "corpus" / "fixtures" / "descendant_pipe_probe.gd"
PROJ_STOCK = HERE / "proj_stock"
PROJ_EDGE = HERE / "proj_edge"
RAW = HERE / "raw"
GODOT = "/usr/bin/godot"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
MARKER_B = MARKER.encode()
TICK = 0.005
BOUND = 3.0

src = RUNNER.read_text()
tree = ast.parse(src)
ns = {"subprocess": subprocess}
wanted = {"run_process", "classify_process", "classify_streams",
          "pid_alive", "kernel_ppid", "gated_signature_run"}
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
classify_streams = ns["classify_streams"]
pid_alive = ns["pid_alive"]
kernel_ppid = ns["kernel_ppid"]

# Wire the extracted nested gate's closure names: it reads these as globals.
ns["args"] = SimpleNamespace(godot=GODOT)
ns["scratch"] = PROJ_STOCK           # swapped per call for edge arms
ns["gate_marker"] = MARKER
ns["gate_bound"] = BOUND
ns["gate_poll_tick"] = TICK
ns["subprocess"] = subprocess
ns["selectors"] = selectors
ns["os"] = os
ns["re"] = re
ns["time"] = time
ns["signal"] = signal
gated_signature_run = ns["gated_signature_run"]
runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
fixture_sha = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
edge_sha = hashlib.sha256((PROJ_EDGE / "descendant_pipe_probe.gd").read_bytes()).hexdigest()

TIMELINES = {}
RAW.mkdir(exist_ok=True)


def monitor_proc(pid, stop, sink, interval=0.001):
    """Transition sampler: records (t, state, kill0_ok, ppid) on change only.
    Samples BEFORE the stop check so the final reaped transition is captured;
    state None + kill0 False => fully reaped/gone -> stop."""
    statp = f"/proc/{pid}/stat"
    t0 = time.monotonic()
    prev = None
    while True:
        try:
            os.kill(pid, 0)
            k0 = True
        except ProcessLookupError:
            k0 = False
        except PermissionError:
            k0 = True
        except OSError:
            k0 = False
        state = None
        ppid = None
        try:
            with open(statp) as fh:
                parts = fh.read().rsplit(")", 1)[1].split()
            state = parts[0]
            ppid = int(parts[1])
        except (OSError, IndexError):
            pass
        rec = (round(time.monotonic() - t0, 6), state, k0, ppid)
        if rec[1:] != prev:
            sink.append(rec)
            prev = rec[1:]
        if not k0 and state is None:
            break
        if stop.is_set():
            break
        time.sleep(interval)


def timeline_stats(key):
    tl = TIMELINES.get(key) or []
    t_first_z = next((t for t, st, _k, _p in tl if st == "Z"), None)
    t_gone = next((t for t, st, k, _p in tl if k is False and st is None), None)
    state_during = [st for _t, st, _k, _p in tl]
    return {"t_first_zombie_s": t_first_z, "t_kill0_gone_s": t_gone,
            "zombie_kill0_window_ms": (round((t_gone - t_first_z) * 1000, 3)
                                      if t_first_z is not None and t_gone is not None else None),
            "zombie_ever_seen": t_first_z is not None,
            "states_seen": sorted({s for s in state_during if s})}


def state_now(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return None


def finish_record(rec, text, monitor_key=None, klass_extra=None):
    rec["marker_observed"] = MARKER in text
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", text)
    rec["write_ppid"] = int(m.group(1)) if m else None
    m = re.search(r"FORGE_HALF1 pp=(\d+)", text)
    rec["half1_ppid"] = int(m.group(1)) if m else None
    rec["withheld_banner"] = "DESCENDANT_PIPE_FORGE child_signature=withheld" in text
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    if monitor_key:
        rec.update(timeline_stats(monitor_key))
    if klass_extra:
        rec.update(klass_extra)
    return rec


def reap_descendants(records):
    for r in records:
        pid = r.get("descendant_pid")
        if pid_alive(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass


def gated_replica(case, flags, proj, bound=BOUND, tick=TICK, mode="poll",
                  stall_before=0.0, unpin_child=False, monitor=True):
    """Line-for-line replica of the landed gated_signature_run, plus:
    - monitor thread on proc.pid (pure observer; never reaps)
    - mode 'kill0': liveness via os.kill(pid,0), no waitpid inside the loop —
      the zombie stays a zombie for the whole read (the naive-gate failure)
    - per-stream buffers for classify_streams evidence
    - stall_before: injected reader stall AFTER Popen, BEFORE the loop —
      models a descheduled reader deterministically
    """
    rec = {"case": case, "flags": list(flags), "replica": True, "gate_mode": mode,
           "bound_seconds": bound, "poll_tick_seconds": tick,
           "stall_before_s": stall_before,
           "timed_out": False, "actual_exit": None, "error": None,
           "marker_observed": False, "marker_observed_at": None,
           "marker_stream": None,
           "child_alive_at_marker_observation": None,
           "child_alive_after_marker_read": None,
           "state_at_marker_observation": None,
           "dead_observed_at": None, "dead_observed_source": None,
           "elapsed_seconds": None,
           "gated_signature_accepted": False,
           "inner_classification": None, "streams_classification": None}
    cmd = [GODOT, "--headless", "--path", str(proj), "--script",
           "res://descendant_pipe_probe.gd", "--"] + list(flags)
    rec["command"] = cmd
    proc = None
    started = time.monotonic()
    captured = bytearray()
    cap = {"out": bytearray(), "err": bytearray()}
    mon_stop = threading.Event()
    mon_key = case
    mon_thread = None
    TIMELINES[mon_key] = []
    try:
        if unpin_child:
            all_cpus = set(range(os.cpu_count()))
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                preexec_fn=lambda: os.sched_setaffinity(0, all_cpus))
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        if monitor:
            mon_thread = threading.Thread(
                target=monitor_proc,
                args=(proc.pid, mon_stop, TIMELINES[mon_key]),
                daemon=True)
            mon_thread.start()
        if stall_before > 0:
            time.sleep(stall_before)
        deadline = started + bound

        def child_alive_now():
            if mode == "poll":
                return proc.poll() is None
            try:
                os.kill(proc.pid, 0)
                return True
            except ProcessLookupError:
                return False
            except PermissionError:
                return True
            except OSError:
                return False

        with selectors.DefaultSelector() as sel:
            sel.register(proc.stdout, selectors.EVENT_READ, "out")
            sel.register(proc.stderr, selectors.EVENT_READ, "err")
            while sel.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    rec["timed_out"] = True
                    break
                events = sel.select(min(tick, max(0.0, remaining)))
                now = time.monotonic()
                if mode == "poll":
                    # heartbeat reap-check, identical to the landed gate
                    if (rec["dead_observed_at"] is None
                            and proc.poll() is not None):
                        rec["dead_observed_at"] = round(now - started, 6)
                        rec["dead_observed_source"] = "gate_poll"
                for key, _ in events:
                    alive_before = child_alive_now()
                    try:
                        chunk = os.read(key.fileobj.fileno(), 65536)
                    except OSError:
                        chunk = b""
                    if not chunk:
                        sel.unregister(key.fileobj)
                        continue
                    captured += chunk
                    cap[key.data] += chunk
                    if not rec["marker_observed"] and MARKER_B in captured:
                        rec["marker_observed"] = True
                        rec["marker_observed_at"] = round(now - started, 6)
                        rec["marker_stream"] = (
                            "stderr" if MARKER_B in cap["err"] else "stdout")
                        rec["child_alive_at_marker_observation"] = alive_before
                        rec["child_alive_after_marker_read"] = child_alive_now()
                        rec["state_at_marker_observation"] = state_now(proc.pid)
        if mode == "kill0":
            # nothing reaped in-loop; death evidence comes from the monitor
            tl = TIMELINES[mon_key]
            z = next((t for t, st, _k, _p in tl if st == "Z"), None)
            rec["dead_observed_at"] = z
            rec["dead_observed_source"] = "monitor_state_Z"
        if rec["dead_observed_at"] is None and proc.poll() is not None:
            rec["dead_observed_at"] = round(time.monotonic() - started, 6)
            rec["dead_observed_source"] = rec["dead_observed_source"] or "post_loop_poll"
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
                rec["error"] = (rec["error"] or "") + "; post-kill wait timed out"
        rec["actual_exit"] = proc.returncode
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] = (rec["error"] or "") + "; forced cleanup timed out"
        mon_stop.set()
        if mon_thread is not None:
            mon_thread.join(timeout=0.5)   # let it record the final transition
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    if rec["timed_out"] and rec["error"] is None:
        rec["error"] = f"TIMEOUT after {bound} seconds"
    text = captured.decode(errors="replace")
    out_t = bytes(cap["out"]).decode(errors="replace")
    err_t = bytes(cap["err"]).decode(errors="replace")
    rec["gated_signature_accepted"] = bool(
        rec["marker_observed"] and rec["child_alive_at_marker_observation"])
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, MARKER)
    rec["streams_classification"] = classify_streams(
        rec["actual_exit"], rec["error"], out_t, err_t, 0, MARKER)
    (RAW / f"{case}.stdout").write_text(text)
    finish_record(rec, text, mon_key if monitor else None)
    if rec["marker_observed_at"] is not None and rec["dead_observed_at"] is not None:
        rec["dead_to_marker_margin_ms"] = round(
            (rec["marker_observed_at"] - rec["dead_observed_at"]) * 1000, 3)
    return rec


def communicate_replica(case, flags, proj, bound=BOUND):
    """Mirrors run_process (:149-158): subprocess.run equivalent =
    Popen + communicate(timeout); TimeoutExpired -> kill+wait in run()'s
    handler. Monitor measures the dead-but-unreaped window under the
    runner's own consumer pattern."""
    rec = {"case": case, "flags": list(flags), "replica": True,
           "consumer": "communicate", "bound_seconds": bound,
           "timed_out": False, "actual_exit": None, "error": None,
           "marker_observed": False, "child_exit_at_timeout": None,
           "elapsed_seconds": None,
           "inner_classification": None, "streams_classification": None}
    cmd = [GODOT, "--headless", "--path", str(proj), "--script",
           "res://descendant_pipe_probe.gd", "--"] + list(flags)
    rec["command"] = cmd
    started = time.monotonic()
    mon_stop = threading.Event()
    TIMELINES[case] = []
    mon_thread = None
    text = ""
    out_t = err_t = ""
    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True) as proc:
            mon_thread = threading.Thread(
                target=monitor_proc,
                args=(proc.pid, mon_stop, TIMELINES[case]),
                daemon=True)
            mon_thread.start()
            try:
                out, err = proc.communicate(timeout=bound)
                out_t, err_t = out or "", err or ""
                text = out_t + err_t          # :152 merge point, verbatim order
                rec["actual_exit"] = proc.returncode
            except subprocess.TimeoutExpired as exc:
                # subprocess.run timeout path: kill then wait (POSIX)
                proc.kill()
                proc.wait()
                rec["timed_out"] = True
                rec["error"] = f"TIMEOUT after {bound} seconds"
                rec["child_exit_at_timeout"] = proc.returncode
                eo = exc.stdout
                ee = exc.stderr
                out_t = (eo.decode(errors="replace") if isinstance(eo, bytes)
                         else (eo or ""))
                err_t = (ee.decode(errors="replace") if isinstance(ee, bytes)
                         else (ee or ""))
                text = out_t + err_t
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
    finally:
        mon_stop.set()
        if mon_thread is not None:
            mon_thread.join(timeout=0.5)
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, MARKER)
    rec["streams_classification"] = classify_streams(
        rec["actual_exit"], rec["error"], out_t, err_t, 0, MARKER)
    (RAW / f"{case}.stdout").write_text(text)
    finish_record(rec, text, case)
    return rec


def verbatim_gate(case, flags, proj):
    """PRODUCTION path: the landed gated_signature_run, verbatim, with only
    its `scratch` closure rebound to the requested project dir."""
    ns["scratch"] = proj
    rec = gated_signature_run(case, list(flags))
    (RAW / f"{case}.stdout").write_text("\n".join(rec["output_lines"]))
    rec["replica"] = False
    return rec


RECORDS = []


def add(rec):
    RECORDS.append(rec)
    print(json.dumps({k: rec.get(k) for k in (
        "case", "actual_exit", "error", "timed_out", "marker_observed",
        "marker_observed_at", "child_alive_at_marker_observation",
        "state_at_marker_observation", "dead_observed_at",
        "dead_to_marker_margin_ms", "zombie_kill0_window_ms",
        "gated_signature_accepted", "inner_classification",
        "streams_classification", "write_ppid", "godot_pid",
        "half1_ppid", "elapsed_seconds")}), flush=True)
    return rec


print("=== phase A: zombie window under communicate() (runner consumer) ===")
for i in range(3):
    add(communicate_replica(f"comm_forge_hold#{i}", ["--spawn-forge-hold"],
                            PROJ_STOCK, bound=3.0))
for i in range(3):
    add(communicate_replica(f"comm_forge_release#{i}", ["--spawn-forge-release"],
                            PROJ_STOCK, bound=3.0))
add(communicate_replica("comm_spawn_hold", ["--spawn-hold"], PROJ_STOCK, bound=3.0))
for i in range(2):
    add(communicate_replica(f"comm_default#{i}", [], PROJ_STOCK, bound=3.0))

print("=== phase B: verbatim production gate + poll-replica w/ monitor ===")
for i in range(3):
    add(verbatim_gate(f"vg_default#{i}", [], PROJ_STOCK))
for i in range(3):
    add(verbatim_gate(f"vg_forge_release#{i}", ["--spawn-forge-release"], PROJ_STOCK))
add(verbatim_gate("vg_forge_hold", ["--spawn-forge-hold"], PROJ_STOCK))
add(verbatim_gate("vg_detach", ["--spawn-detach"], PROJ_STOCK))
for i in range(4):
    add(gated_replica(f"gp_forge_release#{i}", ["--spawn-forge-release"],
                      PROJ_STOCK, mode="poll"))
for i in range(4):
    add(gated_replica(f"gp_default#{i}", [], PROJ_STOCK, mode="poll"))
add(gated_replica("gp_forge_hold", ["--spawn-forge-hold"], PROJ_STOCK, mode="poll"))

print("=== phase C: kill0-variant gate (zombie-blind liveness) ===")
for i in range(4):
    add(gated_replica(f"k0_forge_release#{i}", ["--spawn-forge-release"],
                      PROJ_STOCK, mode="kill0"))
for i in range(2):
    add(gated_replica(f"k0_default#{i}", [], PROJ_STOCK, mode="kill0"))

print("=== phase D: stderr-channel forgery ===")
for i in range(3):
    add(gated_replica(f"stderr_release#{i}", ["--spawn-forge-stderr-release"],
                      PROJ_EDGE, mode="poll"))
add(gated_replica("stderr_hold", ["--spawn-forge-stderr-hold"], PROJ_EDGE,
                  mode="poll"))
for i in range(2):
    add(gated_replica(f"k0_stderr_release#{i}", ["--spawn-forge-stderr-release"],
                      PROJ_EDGE, mode="kill0"))

print("=== phase E: pre-death forged write (fixture-producible? gate knee) ===")
# smoke test: godot's post-spawn live window is ~50-100ms — sweep brackets it
for off in ("0", "0.02", "0.05", "0.07", "0.09", "0.11", "0.15", "0.25"):
    for i in range(2):
        add(gated_replica(f"predeath_{off}#{i}",
                          ["--spawn-forge-predeath", f"--forge-offset={off}"],
                          PROJ_EDGE, mode="poll"))
add(gated_replica("predeath_hold_0.02",
                  ["--spawn-forge-predeath-hold", "--forge-offset=0.02"],
                  PROJ_EDGE, mode="poll"))
add(gated_replica("predeath_stderr_0.02",
                  ["--spawn-forge-predeath", "--forge-offset=0.02",
                   "--forge-stderr"], PROJ_EDGE, mode="poll"))
for i in range(2):
    add(gated_replica(f"halfhalf_0.02#{i}",
                      ["--spawn-forge-halfhalf", "--forge-offset=0.02"],
                      PROJ_EDGE, mode="poll"))

print("=== phase F: gate under scheduler load (pinned reader vs free godot) ===")
CPU0 = {0}
HOGS = 24
os.sched_setaffinity(0, CPU0)          # reader pinned to cpu0
hogs = []
def hog_pin():
    os.sched_setaffinity(0, CPU0)
for _ in range(HOGS):
    hogs.append(subprocess.Popen(["/usr/bin/sh", "-c", "while :; do :; done"],
                                 preexec_fn=hog_pin,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL))
time.sleep(0.2)
try:
    for i in range(8):
        add(gated_replica(f"load_default#{i}", [], PROJ_STOCK, mode="poll",
                          unpin_child=True, monitor=False))
    for i in range(4):
        add(gated_replica(f"load_forge_release#{i}", ["--spawn-forge-release"],
                          PROJ_STOCK, mode="poll", unpin_child=True,
                          monitor=False))
finally:
    for h in hogs:
        try:
            h.kill()
        except OSError:
            pass
    for h in hogs:
        try:
            h.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass
os.sched_setaffinity(0, set(range(os.cpu_count())))   # release the pin

print("=== phase G: deterministic reader-stall sweep (falsification knee) ===")
for stall in (0.20, 0.35, 0.50, 0.65, 0.90):
    add(gated_replica(f"stall_default_{stall}", [], PROJ_STOCK, mode="poll",
                      stall_before=stall, monitor=False))

reap_descendants(RECORDS)
loadavg = list(os.getloadavg())
payload = {"driver": "r64-boundary drive_edges.py",
           "runner_sha256_worktree": runner_sha,
           "fixture_sha256_stock": fixture_sha,
           "fixture_sha256_edge": edge_sha,
           "godot": GODOT, "python": sys.version.split()[0],
           "loadavg_end": loadavg, "records": RECORDS}
(HERE / "edge-verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
(HERE / "edge-timeline.json").write_text(json.dumps(TIMELINES) + "\n")
print("wrote edge-verdicts.json / edge-timeline.json")
