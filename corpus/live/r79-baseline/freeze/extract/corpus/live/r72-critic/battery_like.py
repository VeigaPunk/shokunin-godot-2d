"""r72-critic: run the patched probe through the battery's exact capture
path (subprocess.run(capture_output=True, text=True) + PROBE_ENV) and
evaluate the raw-order claim under clean vs ambient-PYTHONUNBUFFERED env.

Also reports what the battery's ARM_LINE parser sees: whether the reorder
arm line parses and whether any raw lines carry the markers fused.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE / "pygame_probe_reorder.py"
PROBE_ENV = {
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
    "PYGAME_HIDE_SUPPORT_PROMPT": "1",
}
ARM_LINE = re.compile(r"^PYGAME-ARM (\S+) \| (.*)$")


def run(env_extra, extra_argv=()):
    env = dict(os.environ)
    env.update(PROBE_ENV)
    env.update(env_extra)
    p = subprocess.run([sys.executable, *extra_argv, str(PROBE)],
                       capture_output=True, text=True, timeout=90, env=env)
    return p.stdout, p.stderr, p.returncode


def classify(raw):
    h, c, t = raw.find("REORDER-HEAD"), raw.find("REORDER-CHILD"), raw.find("REORDER-TAIL")
    if -1 in (h, c, t):
        return "MISSING", (h, c, t)
    if c < h:
        return "reorder", (h, c, t)
    if h < c < t:
        return "midline", (h, c, t)
    if t < c:
        return "append", (h, c, t)
    return "other", (h, c, t)


def parse_arms(stdout):
    arms, raw_reorder_lines = {}, []
    for line in stdout.splitlines():
        m = ARM_LINE.match(line.strip())
        if not m:
            if "REORDER" in line:
                raw_reorder_lines.append(line)
            continue
        arm, body = m.groups()
        kv = dict(p.split("=", 1) for p in body.split() if "=" in p)
        arms.setdefault(arm, {}).update(kv)
    return arms, raw_reorder_lines


out = {}
for name, env_extra, argv in [
    ("clean", {}, ()),
    ("pythonunbuffered", {"PYTHONUNBUFFERED": "1"}, ()),
    ("u_flag", {}, ("-u",)),
]:
    stdout, stderr, rc = run(env_extra, argv)
    topo, idx = classify(stdout)
    arms, raw_lines = parse_arms(stdout)
    out[name] = {
        "topology": topo,
        "idx": list(idx),
        "rc": rc,
        "done_marker": "PYGAME_PROBE_DONE" in stdout,
        "reorder_arm_parsed": "reorder" in arms,
        "reorder_arm": arms.get("reorder"),
        "raw_reorder_lines": raw_lines,
        "prior_spot_check": {
            "viability_driver": arms.get("viability", {}).get("driver"),
            "withhold_small_bufsize": arms.get("withhold_small", {}).get("bufsize"),
            "pump_needed": arms.get("pump", {}).get("pump_needed"),
        },
    }
    (HERE / f"probe-copy.{name}.stdout.txt").write_text(stdout)

print(json.dumps(out, indent=2))
(HERE / "probe-copy-check.json").write_text(json.dumps(out, indent=2) + "\n")
print("receipt:", HERE / "probe-copy-check.json")
