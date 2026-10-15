"""r72-critic: parent-mode x child-mode matrix over a parent-role script.

Capture path is subprocess.run(capture_output=True) -- byte-for-byte the
same capture the tracked pygame_battery.run_process uses (pipe stdout ->
CPython block-buffers the parent). Classification is a raw byte-index
relation on the captured stream:

  CHILD before HEAD          -> reorder   (Python-buffered topology)
  HEAD < CHILD < TAIL        -> midline   (Godot/LOVE splice topology)
  TAIL < CHILD               -> append    (window closed before write)

Usage: python3 matrix.py <parent-script.py>
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def classify(raw):
    h, c, t = raw.find("HEAD"), raw.find("CHILD"), raw.find("TAIL")
    if -1 in (h, c, t):
        return "MISSING", (h, c, t)
    if c < h:
        return "reorder", (h, c, t)
    if h < c < t:
        return "midline", (h, c, t)
    if t < c:
        return "append", (h, c, t)
    return "other", (h, c, t)


def run(cmd, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)
    return p.stdout, p.stderr, p.returncode


def main():
    script = str(Path(sys.argv[1]).resolve())
    py = sys.executable
    modes = {
        "buffered": ([py, script], {}),
        "u":        ([py, "-u", script], {}),
        "envunbuf": ([py, script], {"PYTHONUNBUFFERED": "1"}),
    }
    cells = [
        ("buffered", "printf", 1, 0.0, "line"),
        ("buffered", "pybuf",  1, 0.0, "line"),
        ("buffered", "pyu",    1, 0.0, "line"),
        ("buffered", "pyslow", 1, 0.0, "line"),
        ("buffered", "bg",     1, 0.6, "line"),
        ("buffered", "bg",     0, 0.6, "line"),
        ("u",        "printf", 1, 0.0, "line"),
        ("u",        "pybuf",  1, 0.0, "line"),
        ("u",        "pyu",    1, 0.0, "line"),
        ("u",        "pyslow", 1, 0.0, "line"),
        ("u",        "bg",     1, 0.6, "line"),
        ("envunbuf", "printf", 1, 0.0, "line"),
        ("buffered", "printf", 1, 0.0, "inline"),
    ]
    out = []
    for pm, child, fl, sl, style in cells:
        base, extra = modes[pm]
        cmd = base + ["--child", child, "--flush-after-tail", str(fl),
                      "--sleep", str(sl), "--marker-style", style]
        stdout, stderr, rc = run(cmd, extra)
        topo, idx = classify(stdout)
        rec = {"parent_mode": pm, "child": child, "flush_after_tail": fl,
               "sleep": sl, "marker_style": style, "rc": rc,
               "topology": topo, "idx": list(idx), "raw": stdout,
               "stderr": stderr}
        out.append(rec)
        print(f"{pm:9} child={child:6} flush={fl} sleep={sl} {style:6} "
              f"-> {topo:8} idx={idx} raw={stdout!r}")
    dest = HERE / (Path(script).stem + "-matrix.json")
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print("receipt:", dest)


if __name__ == "__main__":
    main()
