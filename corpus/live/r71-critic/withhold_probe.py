"""r71-critic parent harness: when does a piped Python child's stdout surface?

Measures, per child mode, the first byte event, every subsequent chunk, and
exit — the parent-visible write->readable surface for a pygame battery.
Also re-measures the (c) popen writer-bound shape (flushing child) so the
proposed battery bounds can be checked against this host.

Usage:
  SDL_VIDEODRIVER=dummy ... python3 withhold_probe.py [tag] [--reps N]
Writes withhold_results.<tag>.json next to this file; prints a table.
"""
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHILD = HERE / "withhold_child.py"
PINNED_ENV = dict(os.environ,
                  SDL_VIDEODRIVER="dummy",
                  SDL_AUDIODRIVER="dummy",
                  PYGAME_HIDE_SUPPORT_PROMPT="1")

MODES = ["exit", "exit_pygame", "flushsmall", "single4000", "single8192",
         "single8193", "single16000", "single130k", "single131072",
         "single131073", "single132k", "single200k", "bigwrite",
         "bigwrite128k", "incr64", "incr8000", "incr65_260k",
         "bin_incr64", "bin_single200k", "mixed_invert"]


def drain(fd, t0, events, total):
    while True:
        r, _, _ = select.select([fd], [], [], 0.02)
        if r:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                return total, True          # EOF
            total += len(chunk)
            events.append({"ms": round((time.perf_counter() - t0) * 1e3, 2),
                           "bytes": len(chunk), "cum": total,
                           "head": chunk[:24].decode("ascii", "replace")})
            continue
        return total, False


def run_mode(mode, env_extra=None):
    env = dict(PINNED_ENV)
    env.update(env_extra or {})
    t0 = time.perf_counter()
    proc = subprocess.Popen([sys.executable, str(CHILD), mode],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env)
    fd = proc.stdout.fileno()
    events, total = [], 0
    eof = False
    while not eof:
        total, eof = drain(fd, t0, events, total)
        if not eof and proc.poll() is not None:
            # process gone but pipe not yet EOF: final drain
            total, eof = drain(fd, t0, events, total)
    exit_ms = round((time.perf_counter() - t0) * 1e3, 2)
    proc.wait()
    err = proc.stderr.read().decode("ascii", "replace").strip()
    prov = {}
    for tok in err.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            prov[k] = v
    first = events[0] if events else None
    return {"mode": mode, "exit_ms": exit_ms, "total_bytes": total,
            "first_ms": first["ms"] if first else None,
            "first_bytes": first["bytes"] if first else 0,
            "first_cum": first["cum"] if first else 0,
            "first_head": first["head"] if first else "",
            "n_events": len(events), "events": events,
            "child_stdio": prov, "stderr": err}


def popen_shape(reps=3):
    """The (c) arm: flushing child, writer-bound pipe, byte-exact lines.

    All waits are relative to the Popen call (spawn included), matching
    the frontier probe's parent-visible-latency shape.
    """
    out = []
    for _ in range(reps):
        t0 = time.perf_counter()
        proc = subprocess.Popen(
            [sys.executable, "-u", "-c",
             "import time; print('CHILD-MARK-1',flush=True);"
             " time.sleep(0.12); print('CHILD-MARK-2',flush=True)"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        l1 = proc.stdout.readline().strip()
        l1_wait = (time.perf_counter() - t0) * 1e3
        l2 = proc.stdout.readline().strip()
        l2_wait = (time.perf_counter() - t0) * 1e3
        rest = proc.stdout.read()
        close_wait = (time.perf_counter() - t0) * 1e3
        proc.wait()
        out.append({"l1": l1, "l2": l2, "l1_wait_ms": round(l1_wait, 2),
                    "l2_wait_ms": round(l2_wait, 2),
                    "close_wait_ms": round(close_wait - l2_wait, 2),
                    "rest_len": len(rest), "ret": proc.returncode,
                    "total_ms": round((time.perf_counter() - t0) * 1e3, 2)})
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    reps = 1
    if "--reps" in sys.argv:
        reps = int(sys.argv[sys.argv.index("--reps") + 1])
    tag = args[0] if args else "run"
    modes = MODES
    if "--modes" in sys.argv:
        modes = sys.argv[sys.argv.index("--modes") + 1].split(",")
    results = {"tag": tag, "modes": [], "popen": popen_shape(),
               "host_env": {k: os.environ.get(k) for k in
                            ("PYTHONUNBUFFERED", "PYTHONIOENCODING")}}
    for mode in modes:
        for _ in range(reps):
            results["modes"].append(run_mode(mode))
    # unbuffered control: the window must collapse under PYTHONUNBUFFERED
    results["modes"].append(run_mode("exit", {"PYTHONUNBUFFERED": "1"}))
    results["modes"][-1]["mode"] = "exit_unbuffered"
    (HERE / ("withhold_results.%s.json" % tag)).write_text(
        json.dumps(results, indent=2) + "\n")

    print("tag=%s" % tag)
    print("%-16s %8s %8s %10s %9s %s" % (
        "mode", "first_ms", "first_B", "first_cum", "exit_ms", "events"))
    for m in results["modes"]:
        print("%-16s %8s %8s %10s %9s %s" % (
            m["mode"], m["first_ms"], m["first_bytes"], m["first_cum"],
            m["exit_ms"], [(e["cum"], e["ms"]) for e in m["events"]]))
    print("popen:")
    for p in results["popen"]:
        print("  l1=%r l2=%r l1_wait=%s l2_wait=%s close_wait=%s rest=%s "
              "ret=%s total=%s" % (p["l1"], p["l2"], p["l1_wait_ms"],
                                   p["l2_wait_ms"], p["close_wait_ms"],
                                   p["rest_len"], p["ret"], p["total_ms"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
