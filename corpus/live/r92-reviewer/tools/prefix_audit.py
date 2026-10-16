#!/usr/bin/env python3
"""r92-reviewer: prefix/byte-stability analysis of arm receipts against the
pinned signatures. Reports, per row and rep: the PASS line, whether the pin is
a byte-prefix of it, and the first divergence offset (pin length vs actual) so
rep-to-rep variance is provably confined to the declared tails.

usage: prefix_audit.py <receipts-dir> [--json out.json]
"""
import argparse, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ufo_r92

ARMS = ["census", "atlas", "cells", "custom", "terrain", "pattern", "encoding",
        "fixinvalid", "srcids", "physics", "timing", "quadrant", "nav", "nullts"]


def pass_line(out):
    for line in out.splitlines():
        if line.startswith("PASS tilemap_lattice ") or line.startswith("FAIL tilemap_lattice "):
            return line
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", type=pathlib.Path)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--json", type=pathlib.Path, default=None)
    args = ap.parse_args()
    C = ufo_r92.load()
    rows = {k: v for k, v in C["cases"].items() if k.startswith("r92_")}
    arm_of = {k: k.removeprefix("r92_tilemap_") for k in rows}
    arm_of["r92_tilemap_nullts_crash"] = "nullts"
    records = []
    for case, row in sorted(rows.items()):
        arm = arm_of[case]
        sigs = row["signature"] if isinstance(row["signature"], (tuple, list)) else (row["signature"],)
        plines, prefix_ok, div, payload_used = [], [], [], []
        for rep in range(1, args.reps + 1):
            f = args.dir / f"{arm}.rep{rep}.out"
            if not f.is_file():
                continue
            out = f.read_text()
            pl = pass_line(out)
            plines.append(pl)
            hit = None
            for i, s in enumerate(sigs):
                if s in out:
                    hit = i
                    break
            payload_used.append(hit)
            s = sigs[hit] if hit is not None else sigs[0]
            if pl is None:
                prefix_ok.append(False); div.append("no-pass-line")
                continue
            if pl.startswith(s):
                prefix_ok.append(True)
                div.append(f"tail={len(pl) - len(s)}")
            else:
                prefix_ok.append(False)
                idx = next((i for i in range(min(len(s), len(pl))) if pl[i] != s[i]), None)
                div.append(f"first_diff={idx} pin_len={len(s)} line_len={len(pl)}")
        records.append({"case": case, "arm": arm, "payload_used": payload_used,
                        "prefix_ok": prefix_ok, "divergence": div,
                        "pass_line_uniq": len(set(plines)),
                        "pass_lines": sorted(set(p for p in plines if p))})
        print(f"{case:28s} prefix_ok={prefix_ok} payload={payload_used} div={div} "
              f"line_uniq={len(set(plines))}", flush=True)
    if args.json:
        args.json.write_text(json.dumps({"dir": str(args.dir), "rows": records}, indent=1))
    bad = [r["case"] for r in records if not all(r["prefix_ok"])]
    print(f"\nrows={len(records)} all-prefix-ok={not bad} bad={bad}")


if __name__ == "__main__":
    main()
