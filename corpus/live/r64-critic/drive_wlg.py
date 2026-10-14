#!/usr/bin/env python3
"""r64 critic: attack the while-live signature-gate claim.

Gate claim under test (r64 axis-move): a signature read gated on the child's
liveness — marker accepted only if observed while the child is alive —
rejects the forged post-death signature of --spawn-forge-release /
--spawn-forge-hold while still passing the genuine default arm.

Gate variants (same bounded select/read loop, different liveness semantics):
  poll    : author-spike semantics — proc.poll() is None before each os.read
            (waitpid-based; reaps the zombie; spike POLL_TICK=5ms).
  kill0   : liveness = os.kill(pid, 0)  — the repo's pid_alive() helper shape;
            never waitpid's inside the loop -> zombie trap test.
  stale   : liveness sampled once per select iteration BEFORE blocking,
            reused for every chunk read that iteration (stale-snapshot order).
  delayed : poll gate + sleep(D) after select-wake before the liveness check
            (reader scheduling-delay sweep on the genuine arm).
  batch   : communicate()-shaped — signature observed only at return; the
            check at observation is then trivially post-death.
  fine    : poll gate instrumented with a pidfd death edge (no reap) and
            0.5ms tick — true marker-vs-death margin measurement.
"""
import argparse, json, os, re, select, signal, subprocess, sys, time

GODOT = "/usr/bin/godot"
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "proj")
MARKER = b"DESCENDANT_PIPE_PROBE: expected signature"
POLL_TICK = 0.005


def pid_alive(pid):
    """The repo helper shape (run_battery.py pid_alive): os.kill(pid, 0)."""
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


def proc_state(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return None


def open_pidfd(pid):
    try:
        return os.pidfd_open(pid)
    except (OSError, AttributeError):
        return None


def run_arm(script, flags, bound, gate, delay=0.0):
    rec = {"script": script, "flags": flags, "gate": gate, "delay_s": delay,
           "bound_seconds": bound, "timed_out": False, "actual_exit": None,
           "error": None, "marker_observed": False, "t_marker": None,
           "t_first_byte": None, "t_dead_pidfd": None, "t_dead_poll": None,
           "alive_at_marker": None, "marker_proc_state": None,
           "chunks": [], "elapsed_seconds": None}
    cmd = [GODOT, "--headless", "--path", PROJ, "--script",
           f"res://{script}", "--"] + flags
    started = time.monotonic()
    pending = b""
    proc = None
    pidfd = None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gate == "batch":
            try:
                out, err = proc.communicate(timeout=bound)
                pending = (out or b"") + (err or b"")
                rec["actual_exit"] = proc.returncode
            except subprocess.TimeoutExpired as exc:
                rec["timed_out"] = True
                rec["error"] = f"TIMEOUT after {bound} seconds"
                pending = (exc.stdout or b"") + (exc.stderr or b"")
                proc.kill()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pass
            # batch semantics: the observation happens AT return.
            rec["marker_observed"] = MARKER in pending
            rec["alive_at_marker"] = proc.poll() is None
            rec["t_marker"] = rec["t_dead_poll"] = None
            rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
            text = pending.decode(errors="replace")
            rec["text"] = text
            _finish(rec, text, started)
            _reap_descendants(text)
            return rec
        tick = POLL_TICK if gate != "fine" else 0.0005
        pipes = [proc.stdout, proc.stderr]
        deadline = started + bound
        stale_alive = None
        while pipes:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                rec["timed_out"] = True
                break
            if gate == "stale":
                stale_alive = proc.poll() is None
            fds = list(pipes)
            if gate == "fine" and pidfd is None:
                pidfd = open_pidfd(proc.pid)
            sel = fds + ([pidfd] if (gate == "fine" and pidfd is not None) else [])
            readable, _, _ = select.select(sel, [], [], min(tick, max(0.0, remaining)))
            now = time.monotonic()
            if gate == "fine" and pidfd is not None and pidfd in readable:
                if rec["t_dead_pidfd"] is None:
                    rec["t_dead_pidfd"] = round(now - started, 6)
                readable = [r for r in readable if r != pidfd]
            if delay:
                time.sleep(delay)
                now = time.monotonic()
            if gate != "kill0" and rec["t_dead_poll"] is None and proc.poll() is not None:
                rec["t_dead_poll"] = round(now - started, 6)
            for stream in readable:
                if gate == "kill0":
                    alive_before = pid_alive(proc.pid)
                elif gate == "stale":
                    alive_before = stale_alive
                else:
                    alive_before = proc.poll() is None
                try:
                    chunk = os.read(stream.fileno(), 65536)
                except OSError:
                    chunk = b""
                if not chunk:
                    pipes.remove(stream)
                    continue
                if rec["t_first_byte"] is None:
                    rec["t_first_byte"] = round(now - started, 6)
                pending += chunk
                rec["chunks"].append({"t": round(now - started, 6),
                                      "n": len(chunk),
                                      "fd": 1 if stream is proc.stdout else 2,
                                      "alive": alive_before,
                                      "state": proc_state(proc.pid)})
                if not rec["marker_observed"] and MARKER in pending:
                    rec["marker_observed"] = True
                    rec["t_marker"] = round(now - started, 6)
                    rec["alive_at_marker"] = alive_before
                    rec["marker_proc_state"] = proc_state(proc.pid)
            if gate == "kill0":
                # pidfd-only death edge: no waitpid inside the loop so the
                # zombie persists exactly as a kill0-gated reader would see it.
                if pidfd is None:
                    pidfd = open_pidfd(proc.pid)
                if pidfd is not None and rec["t_dead_pidfd"] is None:
                    r, _, _ = select.select([pidfd], [], [], 0)
                    if r:
                        rec["t_dead_pidfd"] = round(time.monotonic() - started, 6)
            elif rec["t_dead_poll"] is None and proc.poll() is not None:
                rec["t_dead_poll"] = round(time.monotonic() - started, 6)
        # Death-edge settle: EOF already ended observation, but the child's
        # zombie transition can lag the fd close by microseconds. Spend up to
        # 100ms filling the death-edge timestamps (reporting only — this never
        # touches alive_at_marker, which is frozen at observation time).
        settle_deadline = time.monotonic() + 0.1
        while time.monotonic() < settle_deadline:
            done = True
            if gate in ("kill0", "fine") and rec["t_dead_pidfd"] is None:
                done = False
                if pidfd is None:
                    pidfd = open_pidfd(proc.pid)
                if pidfd is not None:
                    r, _, _ = select.select([pidfd], [], [], 0.001)
                    if r:
                        rec["t_dead_pidfd"] = round(time.monotonic() - started, 6)
                else:
                    done = True  # pidfd unobtainable; give up on that channel
            if rec["t_dead_poll"] is None:
                done = False
                if proc.poll() is not None:
                    rec["t_dead_poll"] = round(time.monotonic() - started, 6)
            if done:
                break
        if rec["timed_out"]:
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
                proc.wait(timeout=3)
        else:
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        rec["actual_exit"] = proc.returncode
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
        if proc is not None and proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pass
    finally:
        if pidfd is not None:
            try:
                os.close(pidfd)
            except OSError:
                pass
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    text = pending.decode(errors="replace")
    _finish(rec, text, started)
    _reap_descendants(text)
    return rec


def _finish(rec, text, started):
    rec["withheld_banner"] = ("child_signature=withheld" in text)
    m = re.search(r"godot_pid=(\d+)", text)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"write_ppid=(\d+)", text)
    rec["write_ppid"] = int(m.group(1)) if m else None
    if rec["t_marker"] is not None and rec["t_dead_pidfd"] is not None:
        rec["margin_dead_minus_marker_s"] = round(rec["t_dead_pidfd"] - rec["t_marker"], 6)
    else:
        rec["margin_dead_minus_marker_s"] = None
    rec["gated_signature_accepted"] = bool(rec["marker_observed"] and rec["alive_at_marker"])
    rec["text_lines"] = text.strip().splitlines()


def _reap_descendants(text):
    for m in re.finditer(r"spawned_pid=(\d+)", text):
        pid = int(m.group(1))
        if pid_alive(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "wlg-verdicts.json"))
    ap.add_argument("--set", default="all", choices=["all", "margin", "forge",
                                                     "kill0", "stale", "delay",
                                                     "mutant", "batch"])
    args = ap.parse_args()
    DPP = "descendant_pipe_probe.gd"
    WLG = "wlg_critic_probe.gd"
    plan = []
    if args.set in ("all", "margin"):
        plan += [(DPP, [], "fine", 0.0, 12), (DPP, [], "poll", 0.0, 12),
                 (DPP, ["--spawn-detach"], "fine", 0.0, 3),
                 (DPP, ["--spawn-detach"], "poll", 0.0, 5)]
    if args.set in ("all", "forge"):
        plan += [(DPP, ["--spawn-forge-release"], "poll", 0.0, 15),
                 (DPP, ["--spawn-forge-release"], "fine", 0.0, 10),
                 (DPP, ["--spawn-forge-hold"], "poll", 0.0, 3),
                 (DPP, ["--spawn-forge-hold"], "fine", 0.0, 2)]
    if args.set in ("all", "kill0"):
        plan += [(DPP, ["--spawn-forge-release"], "kill0", 0.0, 10),
                 (DPP, ["--spawn-forge-hold"], "kill0", 0.0, 3),
                 (DPP, [], "kill0", 0.0, 5)]
    if args.set in ("all", "stale"):
        plan += [(DPP, ["--spawn-forge-release"], "stale", 0.0, 10)]
    if args.set in ("all", "delay"):
        plan += [(DPP, [], "delayed", d, 6) for d in (0.005, 0.01, 0.02, 0.05)]
    if args.set in ("all", "batch"):
        plan += [(DPP, [], "batch", 0.0, 3),
                 (DPP, ["--spawn-forge-release"], "batch", 0.0, 3)]
    if args.set in ("all", "mutant"):
        plan += [(WLG, ["--forge-during-life"], "poll", 0.0, 8),
                 (WLG, ["--forge-during-life"], "fine", 0.0, 5),
                 (WLG, ["--forge-during-life"], "kill0", 0.0, 3),
                 (WLG, ["--forge-early"], "poll", 0.0, 10),
                 (WLG, ["--forge-during-hold"], "poll", 0.0, 3)]
    results = []
    for script, flags, gate, delay, reps in plan:
        name = os.path.splitext(script)[0] + ("_" + "_".join(f.lstrip("-") for f in flags) if flags else "_default")
        for i in range(reps):
            rec = run_arm(script, flags, 3.0, gate, delay)
            rec["case"] = f"{name}#{i}"
            results.append(rec)
            print(f"{rec['case']:>28} gate={gate:>7} d={delay:<5} "
                  f"exit={rec['actual_exit']} err={rec['error']!r} "
                  f"marker={rec['marker_observed']}@{rec['t_marker']} "
                  f"dead_pidfd={rec['t_dead_pidfd']} dead_poll={rec['t_dead_poll']} "
                  f"margin={rec['margin_dead_minus_marker_s']} "
                  f"alive_at_marker={rec['alive_at_marker']} "
                  f"state={rec['marker_proc_state']} "
                  f"verdict={'ACCEPT' if rec['gated_signature_accepted'] else 'REJECT'} "
                  f"elapsed={rec['elapsed_seconds']}", flush=True)
    with open(args.out, "w") as fh:
        json.dump({"driver": "r64-critic drive_wlg.py", "results": results}, fh, indent=2)
    print(f"wrote {args.out} ({len(results)} runs)", flush=True)


if __name__ == "__main__":
    main()
