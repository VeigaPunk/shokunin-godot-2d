"""r72-verifier scratch harness: replay the X1 reorder claim.

Spawns reorder_subject.py with stdout=PIPE, reads the raw fd with
os.read (no stdio buffering this side), and classifies delivered byte
ORDER:
  INJECTED lands before HEAD   -> reorder_prefix (fabricated order)
  HEAD < INJECTED < TAIL       -> midline_splice (Godot/LOVE topology)

Predictions under test (brief pin):
  buffered  -> reorder_prefix
  -u        -> midline_splice
  flushed   -> midline_splice
  PYTHONUNBUFFERED=1 -> midline_splice
and the topology must be identical with/without pygame imported
(language-layer property, spawn-layer seam).

Writes reorder_cells.json + prints a cell table. No repo writes.
"""
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "reorder_subject.py"
OUT = HERE / "reorder_cells.json"

BASE_ENV = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}

CELLS = [
    # (name, argv_extra, mode, surface, env_extra, prediction)
    ("pygame_buffered", [], "buffered", "pygame", {}, "reorder_prefix"),
    ("pygame_dash_u", ["-u"], "buffered", "pygame", {}, "midline_splice"),
    ("pygame_flushed", [], "flushed", "pygame", {}, "midline_splice"),
    ("pygame_env_unbuf", [], "buffered", "pygame",
     {"PYTHONUNBUFFERED": "1"}, "midline_splice"),
    ("bare_buffered", [], "buffered", "bare", {}, "reorder_prefix"),
    ("bare_dash_u", ["-u"], "buffered", "bare", {}, "midline_splice"),
    ("bare_flushed", [], "flushed", "bare", {}, "midline_splice"),
]


def classify(data):
    i_inj = data.find(b"INJECTED")
    i_head = data.find(b"HEAD")
    i_tail = data.find(b"TAIL")
    if i_inj < 0 or i_head < 0 or i_tail < 0:
        return "unclassified"
    if i_inj < i_head:
        return "reorder_prefix"
    if i_head < i_inj < i_tail:
        return "midline_splice"
    return "unclassified"


def run_cell(name, argv_extra, mode, surface, env_extra, prediction):
    env = dict(BASE_ENV)
    env.update(env_extra)
    t0 = time.perf_counter()
    proc = subprocess.Popen(
        [sys.executable] + argv_extra + [str(SUBJECT), mode, surface],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
    fd = proc.stdout.fileno()
    data = b""
    chunks = []
    while True:
        ready, _, _ = select.select([fd], [], [], 15.0)
        if not ready:
            chunks.append((-1.0, -1))
            break
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        chunks.append((round((time.perf_counter() - t0) * 1e3, 2),
                       len(chunk)))
        data += chunk
    proc.wait()
    topology = classify(data)
    ok = topology == prediction
    return {"cell": name, "argv_extra": argv_extra, "mode": mode,
            "surface": surface, "env_extra": env_extra,
            "delivered": data.decode("utf-8", "replace"),
            "delivered_repr": repr(data),
            "read_chunks": chunks, "ret": proc.returncode,
            "topology": topology, "predicted": prediction,
            "verdict": "PASS" if ok else "FAIL"}


def main():
    results = [run_cell(*c) for c in CELLS]
    payload = {"subject": str(SUBJECT), "python": sys.version.split()[0],
               "results": results,
               "pass": sum(1 for r in results if r["verdict"] == "PASS"),
               "fail": sum(1 for r in results if r["verdict"] == "FAIL")}
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    for r in results:
        print(f"{r['verdict']:4} {r['cell']:18} -> {r['topology']:15} "
              f"(pred {r['predicted']:15}) delivered={r['delivered_repr']}")
    print(f"totals: {payload['pass']}/{len(results)} PASS -> {OUT}")
    return 0 if payload["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
