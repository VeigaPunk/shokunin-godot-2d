#!/usr/bin/env python3
"""mut05_load — forced-contention positive control for mut05 (r102 seat M5).

Launches folded link/path reps with K concurrent Godot processes to test whether the
unpinned scheduler field settle= can reach 6 on the folded (S1-applied) tree itself,
without any resurrection. settle=6 under contention on folded == load class proven.

Usage: python3 mut05_load.py --work /var/tmp/r102-mut5 --battery <repo>/corpus/fixtures/run_battery.py --godot /usr/bin/godot
"""
import argparse, importlib.util, json, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def load_mut05(p: Path):
    spec = importlib.util.spec_from_file_location("mut05", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--battery", required=True)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--jobs", type=int, default=24)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    m = load_mut05(Path(__file__).with_name("mut05.py"))
    rows, ALLOW, REQ = m.extract_pins(Path(a.battery))
    m.ALLOW, m.REQ = ALLOW, REQ
    by = {r[0]: r for r in rows}
    folded = Path(a.work) / "trees" / "folded"
    jobs = []
    for i in range(a.jobs):
        jobs.append((by["nav_lattice_link"] if i % 2 == 0 else by["nav_lattice_path"], i))
    results = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(m.receipt, a.godot, folded, row) for row, i in jobs]
        for (row, i), f in zip(jobs, futs):
            r = f.result()
            mt = re.search(r"settle=(\d+)", r["_out"].decode(errors="replace"))
            settle = mt.group(1) if mt else None
            results.append({"row": row[0], "i": i, "rc": r["rc"], "verdict": r["verdict"], "settle": settle})
            print(f"MUT5LOAD {row[0]} job{i} rc={r['rc']} verdict={r['verdict']} settle={settle}", flush=True)
    got6 = sorted({x["row"] for x in results if x["settle"] == "6"})
    print(f"MUT5LOAD settle_values={sorted({x['settle'] for x in results})} rows_with_6={got6} "
          f"verdicts={sorted({x['verdict'] for x in results})}")
    (Path(a.work) / "load.json").write_text(json.dumps(results, indent=1))

if __name__ == "__main__":
    main()
