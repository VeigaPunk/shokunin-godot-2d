#!/usr/bin/env python3
"""r92 verifier — nullts crash-row wall-time distribution.

The battery bounds every non-export case at 8 s.  This probe launches the
committed nullts arm N times in the battery's exact launch shape, times each
run, and records rc / stderr length so the 8 s margin can be characterized
(the crash handler dumps a C++ backtrace before abort(); under host load that
dump's wall time is the only thing between rc=-6 and a TIMEOUT).
"""
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r92-verifier"
PROJ = V / "arms" / "proj"
OUT = V / "arms" / "nullts_wall"
OUT.mkdir(exist_ok=True)
GODOT = "godot"

n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
       "res://tilemap_lattice.gd", "--", "--arm=nullts"]
times = []
n_timeout = 0
for i in range(1, n + 1):
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        rc = None
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    dt = time.monotonic() - t0
    times.append(dt)
    if rc is None:
        n_timeout += 1
    (OUT / f"nullts_wall.rep{i}.out").write_text(out)
    (OUT / f"nullts_wall.rep{i}.err").write_text(err)
    (OUT / f"nullts_wall.rep{i}.rc").write_text(f"{rc}\n")
    print(f"rep{i:2d} wall={dt:7.3f}s rc={rc} err_lines={len(err.splitlines())}", flush=True)

ok = [t for t in times if t < 8]
print(f"\nn={n} timeouts={n_timeout} min={min(times):.3f}s max={max(times):.3f}s "
      f"median={sorted(times)[len(times)//2]:.3f}s")
print(f"margin: max completed wall / 8s bound = {max(ok)/8:.3f}" if ok else "no completed run")
