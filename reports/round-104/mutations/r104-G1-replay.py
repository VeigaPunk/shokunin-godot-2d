#!/usr/bin/env python3
"""r104-G1 — replay the receipt-shape predicate imported from a run_battery.py
copy over (a) the r103 mut05 evasion catalog and (b) stored verdicts.json runs.

Read-only over the repo; run_battery.py is never executed (hard rule 1).

  --battery PATH   run_battery.py copy whose receipt_shape_flag is imported
  --evasions PATH  /var/tmp/r103-mut5/evasions.json-style catalog
  --runs GLOB      replay every stored run matching GLOB (per-row flags)
"""
import argparse
import glob
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

_MODN = [0]


def load_battery(path):
    _MODN[0] += 1
    spec = importlib.util.spec_from_file_location("r104_g1_bat%d" % _MODN[0], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = Path(path).read_bytes()
    print("BATTERY=%s sha256=%s bytes=%d" %
          (path, hashlib.sha256(src).hexdigest(), len(src)))
    return mod


def replay_evasions(mod, path):
    payload = json.loads(Path(path).read_text())
    flagged = 0
    rows = payload["evasions"] + payload["green_controls"]
    for e in payload["evasions"]:
        flags = mod.receipt_shape_flag(e["row"])
        flagged += bool(flags)
        print("EVASION %-28s flagged=%-5s n=%d :: %s" %
              (e["name"], bool(flags), len(flags),
               "; ".join(sorted({f.get("why", "?") for f in flags})) or "-"))
    silent = 0
    for c in payload["green_controls"]:
        flags = mod.receipt_shape_flag(c["row"])
        silent += not flags
        print("CONTROL %-28s silent=%-5s :: %s" %
              (c["name"], not flags, flags[:2] if flags else "-"))
    print("REPLAY_SUMMARY evasions=%d flagged=%d controls=%d silent=%d"
          % (len(payload["evasions"]), flagged, len(payload["green_controls"]),
             silent))
    return flagged


def replay_runs(mod, pattern):
    total_rows = 0
    total_flags = 0
    for path in sorted(glob.glob(pattern)):
        data = json.loads(Path(path).read_text())
        rows = data.get("results") or []
        n = 0
        fl = []
        for row in rows:
            if row.get("verdict") != "PASS":
                continue
            out = row.get("output")
            if not isinstance(out, list):
                continue
            n += 1
            fl.extend(mod.receipt_shape_flag(row))
        total_rows += n
        total_flags += len(fl)
        print("RUN %-24s rows=%d flags=%d %s" %
              (Path(path).parent.name, n, len(fl),
               sorted({f.get("why") for f in fl}) or ""))
        for f in fl[:10]:
            print("      FLAG %s" % json.dumps(f)[:160])
    print("RUNS_SUMMARY rows=%d flags=%d" % (total_rows, total_flags))
    return total_flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", required=True)
    ap.add_argument("--evasions")
    ap.add_argument("--runs")
    args = ap.parse_args()
    mod = load_battery(args.battery)
    if args.evasions:
        replay_evasions(mod, args.evasions)
    if args.runs:
        replay_runs(mod, args.runs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
