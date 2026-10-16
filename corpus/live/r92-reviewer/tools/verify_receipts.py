#!/usr/bin/env python3
"""r92-reviewer receipt classifier — production classify_process (AST-extracted
from the PINNED committed harness) + execute()'s stream-anchored
required_stderr path. Reports per-row verdicts, rep-to-rep byte stability,
first-divergence offsets vs the pinned prefix, and bare-classifier load-bearing.

usage: verify_receipts.py <receipts-dir> [--json <out.json>]
"""
import argparse, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ufo_r92

ARMS = ["census", "atlas", "cells", "custom", "terrain", "pattern", "encoding",
        "fixinvalid", "srcids", "physics", "timing", "quadrant", "nav", "nullts"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", type=pathlib.Path)
    ap.add_argument("--json", type=pathlib.Path, default=None)
    args = ap.parse_args()
    C = ufo_r92.load()
    rows = {k: v for k, v in C["cases"].items() if k.startswith("r92_")}
    arm_of = {k: k.removeprefix("r92_tilemap_") for k in rows}
    arm_of["r92_tilemap_nullts_crash"] = "nullts"

    out_records = []
    fails = 0
    for case, row in sorted(rows.items()):
        arm = arm_of[case]
        sigs = row["signature"] if isinstance(row["signature"], (tuple, list)) else (row["signature"],)
        ee = C["exp_err"].get(case, ())
        rs = C["req_err"].get(case, ())
        outs, errs, rcs, verdicts, offsets, bare = [], [], [], [], [], []
        for rep in range(1, 6):
            f = args.dir / f"{arm}.rep{rep}.out"
            if not f.is_file():
                continue
            o = f.read_text()
            e = (args.dir / f"{arm}.rep{rep}.err").read_text()
            rc = int((args.dir / f"{arm}.rep{rep}.rc").read_text().strip())
            merged = o + e
            passed = any(C["classify"](rc, None, merged, row["expected_exit"], s, ee) for s in sigs)
            if rs:
                passed = passed and all(frag in e for frag in rs) and any(s in o for s in sigs)
            bare_passed = any(C["classify"](rc, None, merged, row["expected_exit"], s, ()) for s in sigs)
            outs.append(o); errs.append(e); rcs.append(rc)
            verdicts.append(bool(passed)); bare.append(bool(bare_passed))
            if not passed:
                fails += 1
            # first-divergence vs pinned prefix (payload[0] for envelope rows)
            pin = sigs[0]
            off = None
            for s in sigs:
                if s in o:
                    pin = s
                    break
            idx = next((i for i in range(min(len(pin), len(o))) if o[i] != pin[i]), None)
            if idx is None:
                offsets.append("identical-or-prefix" if pin in o else "no-pin")
            else:
                offsets.append(f"{idx} (pin_len={len(pin)})")
        rec = {"case": case, "arm": arm, "reps": len(outs),
               "rcs": sorted(set(rcs)), "expected_exit": row["expected_exit"],
               "verdicts": verdicts, "fails": sum(1 for v in verdicts if not v),
               "out_uniq": len(set(outs)), "err_uniq": len(set(errs)),
               "bare_classifier_passes": bare,
               "first_divergence_vs_pin": offsets,
               "envelope_payloads": len(sigs) if isinstance(row["signature"], (tuple, list)) else 1}
        out_records.append(rec)
        flag = "OK  " if rec["fails"] == 0 else "FAIL"
        print(f"{flag} {case:28s} reps={rec['reps']} rc={rec['rcs']} "
              f"out_uniq={rec['out_uniq']} err_uniq={rec['err_uniq']} "
              f"bare={rec['bare_classifier_passes']} div={offsets}", flush=True)
    print(f"\nrows={len(out_records)} receipts={sum(r['reps'] for r in out_records)} fails={fails}")
    print(f"classify_process segment sha256={C['seg_sha']}")
    if args.json:
        args.json.write_text(json.dumps({"segment_sha256": C["seg_sha"],
                                         "harness_sha256": C["src_sha"],
                                         "dir": str(args.dir),
                                         "rows": out_records}, indent=1))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
