#!/usr/bin/env python3
"""r64 verifier forge spot-checks — own-scratch replication of the while-live
signature gate with a PARAMETERIZED liveness primitive.

Gate under test (verbatim shape of run_battery.py:gated_signature_run):
binary selectors loop over both pipes; on each readable event sample liveness
BEFORE os.read; the marker-completing chunk's liveness decides acceptance.

Variants:
  poll  -> process.poll() is None  (waitpid WNOHANG; REAPS the zombie)
  kill0 -> os.kill(pid, 0) succeeds (zombie-blind: an unreaped zombie still
           exists, so kill(pid,0) reports it alive -> false-accepts a
           post-death forged write landing inside the zombie window)

Arms:
  forge_release x N under each gate (real tracked fixture
    --spawn-forge-release; descendant write is reparenting-gated post-death)
  wlg_critic_probe.gd --forge-during-life / --forge-early under poll gate
    (descendant writes the SAME marker BEFORE the child's death -> the gate
    must accept: liveness-of-child != authorship-of-write)

/proc/<pid>/stat state field recorded at marker observation as the kernel
truth sample (Z = dead-but-unreaped zombie).
"""
import json
import os
import re
import selectors
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent / "proj"
GODOT = "/usr/bin/godot"
MARKER = b"DESCENDANT_PIPE_PROBE: expected signature"
BOUND = 3.0
TICK = 0.005


def proc_state(pid):
    try:
        # /proc/<pid>/stat field 3, after the comm's closing paren
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except Exception:
        return None


def kernel_ppid(pid):
    try:
        return int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[1])
    except Exception:
        return None


def gated_run(script, extra_args, gate, bound=BOUND):
    rec = {"script": script, "flags": extra_args, "gate": gate,
           "marker_observed": False, "marker_observed_at": None,
           "alive_at_marker": None, "alive_after_marker": None,
           "proc_state_at_marker": None, "dead_poll_at": None,
           "timed_out": False, "exit": None, "write_ppid": None,
           "gated_signature_accepted": False}
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           f"res://{script}", "--"] + list(extra_args)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    started = time.monotonic()
    captured = bytearray()

    def alive():
        if gate == "poll":
            return proc.poll() is None            # reaps zombie
        os.kill(proc.pid, 0)                      # zombie-BLIND
        return True

    try:
        deadline = started + bound
        with selectors.DefaultSelector() as sel:
            sel.register(proc.stdout, selectors.EVENT_READ)
            sel.register(proc.stderr, selectors.EVENT_READ)
            while sel.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    rec["timed_out"] = True
                    break
                events = sel.select(min(TICK, max(0.0, remaining)))
                now = time.monotonic()
                if gate == "poll" and rec["dead_poll_at"] is None \
                        and proc.poll() is not None:
                    rec["dead_poll_at"] = round(now - started, 6)
                for key, _ in events:
                    ab = alive()
                    try:
                        chunk = os.read(key.fileobj.fileno(), 65536)
                    except OSError:
                        chunk = b""
                    if not chunk:
                        sel.unregister(key.fileobj)
                        continue
                    captured += chunk
                    if not rec["marker_observed"] and MARKER in captured:
                        rec["marker_observed"] = True
                        rec["marker_observed_at"] = round(now - started, 6)
                        rec["alive_at_marker"] = ab
                        rec["alive_after_marker"] = alive()
                        rec["proc_state_at_marker"] = proc_state(proc.pid)
    finally:
        for s in (proc.stdout, proc.stderr):
            try:
                s.close()
            except OSError:
                pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
        rec["exit"] = proc.returncode
    text = captured.decode(errors="replace")
    m = re.search(r"write_ppid=(\d+)", text) or re.search(r"_ppid=(\d+)", text)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["withheld_banner"] = ("child_signature=withheld" in text)
    rec["gated_signature_accepted"] = bool(
        rec["marker_observed"] and rec["alive_at_marker"])
    rec["lines"] = [l for l in text.strip().splitlines()]
    return rec


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = {"runs": []}
    # (a) kill0 false-accept through the zombie window — real forged arm
    for i in range(reps):
        out["runs"].append({"arm": "forge_release_kill0",
                            **gated_run("descendant_pipe_probe.gd",
                                        ["--spawn-forge-release"], "kill0")})
    # control: same arm under poll — must reject
    for i in range(reps):
        out["runs"].append({"arm": "forge_release_poll",
                            **gated_run("descendant_pipe_probe.gd",
                                        ["--spawn-forge-release"], "poll")})
    # (b) live-window forgery under the poll gate — descendant writes pre-death
    for i in range(reps):
        out["runs"].append({"arm": "forge_during_life_poll",
                            **gated_run("wlg_critic_probe.gd",
                                        ["--forge-during-life"], "poll")})
    for i in range(reps):
        out["runs"].append({"arm": "forge_early_poll",
                            **gated_run("wlg_critic_probe.gd",
                                        ["--forge-early"], "poll")})
    dest = HERE / "forge-verdicts.json"
    dest.write_text(json.dumps(out, indent=2))
    for r in out["runs"]:
        print(f"{r['arm']:26} gate={r['gate']:5} marker={r['marker_observed']} "
              f"alive_at_marker={r['alive_at_marker']} state={r['proc_state_at_marker']} "
              f"dead_poll_at={r['dead_poll_at']} marker_at={r['marker_observed_at']} "
              f"ACCEPT={r['gated_signature_accepted']} exit={r['exit']} "
              f"write_ppid={r['write_ppid']}")


if __name__ == "__main__":
    main()
