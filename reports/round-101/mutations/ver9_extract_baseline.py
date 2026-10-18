#!/usr/bin/env python3
"""r101-VER-9: extract a durable prior-row baseline from a battery verdicts.json.

The r100 final battery receipts live under /var/tmp (not git-tracked).  This
extractor freezes the *comparison-relevant* projection of one receipt -- the
7-field verdict tuple (script, flags, expected_exit, actual_exit, signature,
verdict, error) for every CASES row, plus case/verdict/discriminations for
every probe/meta row -- into a small JSON the orchestrator can commit and
reuse.  Raw `output`, `command`, `scratch`, `xdg_data_home`, `elapsed_seconds`
are deliberately dropped: those are expected to differ between runs (see
reports/round-60/r60-verifier.md, the clause that fixed the 7-field scope).

Usage:
    python3 ver9_extract_baseline.py <verdicts.json> <out.json> [--source-label S]
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

FIELDS = ("script", "flags", "expected_exit", "actual_exit", "signature", "verdict", "error")
PROBE_KEEP = ("case", "verdict", "mode", "discriminations", "census")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--source-label", default=None)
    args = ap.parse_args()

    raw = args.receipt.read_bytes()
    payload = json.loads(raw)
    rows = payload["results"]

    cased, probes = [], []
    for x in rows:
        if "script" in x:
            cased.append({k: x.get(k) for k in ("case",) + FIELDS})
        else:
            probes.append({k: x[k] for k in PROBE_KEEP if k in x})

    names = [x["case"] for x in cased]
    counts = Counter(names)
    dup_names = sorted(n for n, c in counts.items() if c > 1)
    dup_identical = all(
        len({json.dumps(x, sort_keys=True) for x in cased if x["case"] == n}) == 1
        for n in dup_names)

    # Post-9ede7c50 disposition: the r100 landing duplicated the crash-tail
    # CASES tuples; the integration fix removed the extra copies, so a current
    # battery run executes each name once.  Any name whose receipt multiplicity
    # exceeds 1 is expected to run exactly once going forward.
    dispositions = {n: {"receipt_copies": counts[n], "expected_current_copies": 1,
                        "reason": "9ede7c50 dedupe crash sentinel CASES rows (509/509 unique)"}
                    for n in dup_names}

    out = {
        "baseline_id": "r100-final",
        "source_label": args.source_label or str(args.receipt),
        "source_path": str(args.receipt),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_bytes": len(raw),
        "source_battery_verdict": payload.get("verdict"),
        "godot": payload.get("godot"),
        "extractor": "reports/round-101/mutations/ver9_extract_baseline.py",
        "comparison_scope": list(FIELDS),
        "counts": {
            "rows": len(rows),
            "cased_rows": len(cased),
            "probe_rows": len(probes),
            "unique_cased_names": len(set(names)),
            "duplicate_names": dup_names,
            "duplicate_instances_value_identical": dup_identical,
            "unique_probe_names": len({p["case"] for p in probes}),
        },
        "multiplicity_dispositions": dispositions,
        "probe_rows": probes,
        "cased_rows": cased,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes) "
          f"from {args.receipt} sha256={out['source_sha256']}")
    print(f"counts: {out['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
