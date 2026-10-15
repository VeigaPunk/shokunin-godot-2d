#!/usr/bin/env python3
"""r65 critic: REAL-PIPE splice phantom + hold-arm race margin."""
import json
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
ERR = "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"

src = (ROOT.parent.parent / "fixtures" / "run_battery.py").read_text()
m = re.search(r"(    def classify_process\(.*?\n)(?=    def classify_streams)", src, re.S)
ns = {"re": re}
exec(textwrap.dedent(m.group(1)), ns)
classify_process = ns["classify_process"]

out = {}

# --- real-pipe splice: child writes 'ERROR' to stdout tail (no \n),
# 'phantom...\n' to stderr head; the run_process/errforge merge fabricates
# a line containing 'ERROR:' that exists in NEITHER stream ---
cmd = ["/usr/bin/sh", "-c",
       f"printf '%s\\nending in ERROR' '{SIG}'; printf ': PHANTOM real-pipe splice\\n' >&2"]
p = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
merged = p.stdout + p.stderr
out["real_splice"] = {
    "stdout_tail": p.stdout.splitlines()[-1],
    "stderr_head": p.stderr.splitlines()[0],
    "stdout_ERROR_lines": [l for l in p.stdout.splitlines() if "ERROR:" in l],
    "stderr_ERROR_lines": [l for l in p.stderr.splitlines() if "ERROR:" in l],
    "merged_ERROR_lines": [l for l in merged.splitlines() if "ERROR:" in l],
    "classification": classify_process(p.returncode, None, merged, 0, SIG),
    "classification_with_newline_guard": classify_process(
        p.returncode, None, p.stdout + "\n" + p.stderr, 0, SIG),
}

# --- hold-arm race margin: measure descendant post-death write latency
# against the 3.0s meta bound. Time the same gate+echo in isolation:
# spawn godot probe (author's hold arm), record when the forged error
# bytes arrive relative to godot death via a selector read ---
import os, selectors
cmd = ["/usr/bin/godot", "--headless", "--path", str(ROOT / "proj"),
       "--script", "res://critic_errforge_probe.gd", "--", "--stderr-errforge"]
err_bytes = ERR.encode()
sig_bytes = SIG.encode()
lat = []
for i in range(5):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    started = time.monotonic()
    captured = bytearray()
    dead_at = err_at = sig_at = None
    deadline = started + 3.0
    with selectors.DefaultSelector() as sel:
        sel.register(proc.stdout, selectors.EVENT_READ)
        sel.register(proc.stderr, selectors.EVENT_READ)
        while sel.get_map() and time.monotonic() < deadline:
            for key, _ in sel.select(0.005):
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except OSError:
                    chunk = b""
                if not chunk:
                    sel.unregister(key.fileobj)
                    continue
                captured += chunk
            now = time.monotonic()
            if dead_at is None and proc.poll() is not None:
                dead_at = now - started
            if sig_at is None and sig_bytes in captured:
                sig_at = now - started
            if err_at is None and err_bytes in captured:
                err_at = now - started
    proc.wait(timeout=3)
    lat.append({"rep": i, "sig_at": sig_at, "dead_at": dead_at,
                "err_at": err_at,
                "write_lag_after_death": (err_at - dead_at) if (err_at and dead_at) else None,
                "margin_to_3s_bound": 3.0 - err_at if err_at else None})
    for d in (proc.stdout, proc.stderr):
        try: d.close()
        except OSError: pass
out["hold_race_margin"] = lat
(ROOT / "splice-and-race.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
