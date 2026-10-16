#!/usr/bin/env python3
"""r95 critic: analyze receipt batches — rep/cross-condition byte stability of the
pinned bytes, signature shape (prefix vs whole line), wall-time margin."""
import json
import sys
from pathlib import Path

SEAT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r95-critic")
RUNS = SEAT / "runs"


def load(batch):
    p = RUNS / batch / "receipts.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def pass_lines(rec):
    """the PASS line(s) of a receipt (the pinned bytes live here)."""
    return [l for l in rec["output"].splitlines() if l.startswith("PASS ")]


def main(batches):
    rows = {r["case"]: r for r in json.loads((SEAT / "scripts" / "rows.json").read_text())["r95_rows"]}
    data = {b: load(b) for b in batches}
    data = {b: v for b, v in data.items() if v}
    out = {"batches": {}, "cross": {}}
    for b, recs in data.items():
        per = {}
        for r in recs:
            per.setdefault(r["case"], []).append(r)
        rowsout = {}
        for case, rs in per.items():
            sig = rows[case]["sig"]
            plines = {tuple(pass_lines(x)) for x in rs}
            rowsout[case] = {
                "reps": len(rs),
                "verdicts": sorted({x["verdict"] for x in rs}),
                "pass_line_uniq": len(plines),
                "stdout_uniq": len({x["stdout_sha256"] for x in rs}),
                "sig_in_stdout": all(x["sig_in_stdout"] for x in rs),
                "sig_whole_line": all(any(l == sig for l in x["output"].splitlines()) for x in rs),
                "max_wall": max(x["wall"] for x in rs),
                "rc": sorted({x["rc"] for x in rs}),
                "stderr_bytes": sorted({x["stderr_bytes"] for x in rs}),
                "pass_lines": sorted(plines)[0] if len(plines) == 1 else None,
            }
        out["batches"][b] = {
            "receipts": len(recs),
            "fail": [r["case"] for r in recs if r["verdict"] != "PASS"],
            "timeouts": [r["case"] for r in recs if r["error"]],
            "max_wall": max(r["wall"] for r in recs),
            "max_wall_case": max(recs, key=lambda r: r["wall"])["case"],
            "rows_stdout_stable": sum(1 for v in rowsout.values() if v["stdout_uniq"] == 1),
            "rows_pass_line_uniq_1": sum(1 for v in rowsout.values() if v["pass_line_uniq"] == 1),
            "rows_pass_line_unstable": sorted(c for c, v in rowsout.items() if v["pass_line_uniq"] != 1),
            "rows_total": len(rowsout),
            "rows_unstable": sorted(c for c, v in rowsout.items() if v["stdout_uniq"] != 1),
            "rows": rowsout,
        }
    # cross-condition: does each pinned signature survive every condition?
    if "fresh" in data:
        base = out["batches"]["fresh"]["rows"]
        cross = {}
        for b in data:
            if b == "fresh":
                continue
            moved, line_moved = [], []
            for case, v in out["batches"][b]["rows"].items():
                if v["verdicts"] != ["PASS"]:
                    moved.append(case)
                elif v["pass_line_uniq"] == 1 and base[case]["pass_line_uniq"] == 1 \
                        and v["pass_lines"] != base[case]["pass_lines"]:
                    line_moved.append(case)
            cross[b] = {"rows_rejecting": moved, "count_rejecting": len(moved),
                        "rows_with_different_pass_line": line_moved,
                        "count_line_moved": len(line_moved)}
        out["cross"] = cross
    (SEAT / "scripts" / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({b: {k: v for k, v in d.items() if k != "rows"} for b, d in out["batches"].items()}, indent=1))
    print("CROSS:", json.dumps(out["cross"], indent=1))


if __name__ == "__main__":
    main(sys.argv[1:] or ["fresh"])
