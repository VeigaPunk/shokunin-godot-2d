#!/usr/bin/env python3
"""r95 critic: read-only signature-vs-receipt census over the sibling corpora.

For each of the 52 committed r95 rows, map the case to its receipt cell and
collect every `PASS ...` line for that cell from:
  corpus/live/r95-scout/runs/**   (dss_lattice rows: cell r95_dss_<arm>[_rev])
  corpus/live/r95-boundary/runs/** (r95b_order rows: cell <case minus prefix>)
Also scans this seat's own fresh receipts when present.
"""
import json
import re
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SEAT = ROOT / "corpus" / "live" / "r95-critic"
ROOTS = [ROOT / "corpus/live/r95-scout/runs", ROOT / "corpus/live/r95-boundary/runs"]


def cell_for(row):
    name, script, args = row["case"], row["script"], row["args"]
    if script == "dss_lattice.gd":
        arm = next((a.split("=", 1)[1] for a in args if a.startswith("--arm=")), None)
        rev = "--rev" in args
        return f"r95_dss_{arm}" + ("_rev" if rev else "")
    if script == "r95b_order.gd":
        return name[len("r95b_order_"):]
    return None


def main():
    rows = json.loads((SEAT / "scripts" / "rows.json").read_text())["r95_rows"]
    # index PASS lines per cell
    cells = {}
    files_scanned = 0
    nonempty_err = []
    for root in ROOTS:
        for f in sorted(root.rglob("*")):
            if f.suffix == ".err" and f.stat().st_size:
                nonempty_err.append(str(f.relative_to(ROOT)))
            if f.suffix != ".out":
                continue
            files_scanned += 1
            stem = f.name.rsplit(".rep", 1)[0] if ".rep" in f.name else f.stem
            stem = stem[:-4] if stem.endswith(".out") else stem
            text = f.read_text(errors="replace")
            for line in text.splitlines():
                if line.startswith("PASS "):
                    cells.setdefault(stem, set()).add(line)
    out = {"files_scanned": files_scanned, "cells_seen": len(cells),
           "nonempty_err_files": nonempty_err[:20], "rows": []}
    for row in rows:
        cell = cell_for(row)
        payloads = sorted(cells.get(cell, set()))
        sig = row["sig"]
        out["rows"].append({
            "case": row["case"], "cell": cell, "receipts_payloads": len(payloads),
            "sig_present": any(sig in p for p in payloads),
            "sig_exact_line": sig in payloads,
            "distinct_payloads": len(payloads),
            "other_payloads": [p for p in payloads if p != sig][:3],
        })
    (SEAT / "scripts" / "census.json").write_text(json.dumps(out, indent=1))
    bad = [r for r in out["rows"] if not r["sig_present"] or r["distinct_payloads"] != 1]
    print(json.dumps({"files_scanned": files_scanned, "cells_seen": len(cells),
                      "nonempty_err": len(nonempty_err),
                      "rows_total": len(out["rows"]),
                      "rows_with_sig_present": sum(1 for r in out["rows"] if r["sig_present"]),
                      "rows_payload_uniq_1": sum(1 for r in out["rows"] if r["distinct_payloads"] == 1),
                      "rows_with_exact_line_sig": sum(1 for r in out["rows"] if r["sig_exact_line"]),
                      "anomalies": bad}, indent=1))


if __name__ == "__main__":
    main()
