#!/usr/bin/env python3
"""r68-scribe — verify the two declared r68 receipt-shape upgrades on a
stream-attribution-verdicts.json artifact:

  (1) divergence_table rows carry `divergent_clause` — a signature over
      {exit, signature, error_scan, blob, allowlist_shape} naming which
      clause diverged between merged and per-stream classification.
  (2) every dual_classify-shaped record carries sha256(raw_stdout) +
      sha256(raw_stderr) (the same-input gate).

Also replays: prior-row byte-stability is checked by the caller comparing
key fields against the r67 receipt shape.

Usage: check_receipt_upgrades.py <verdicts.json>
"""
import hashlib
import json
import sys
from pathlib import Path

CLAUSES = {"exit", "signature", "error_scan", "blob", "allowlist_shape"}


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def find_dual_records(payload):
    """Every dict shaped like a dual_classify record."""
    recs = []
    def walk(o, path):
        if isinstance(o, dict):
            if ("merged_classification" in o
                    and "stream_classification" in o
                    and "divergent" in o):
                recs.append((path, o))
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(payload, "$")
    return recs


def main():
    p = Path(sys.argv[1])
    payload = json.loads(p.read_text())
    div = payload.get("divergence", {})
    table = div.get("divergence_table", [])
    report = {"artifact": str(p),
              "artifact_sha256": sha(p.read_text()),
              "divergence_rows": len(table),
              "rows_missing_clause": [],
              "clause_values": {},
              "dual_records": 0,
              "dual_missing_sha": [],
              "dual_sha_mismatch": []}
    for i, row in enumerate(table):
        dc = row.get("divergent_clause")
        if dc is None:
            report["rows_missing_clause"].append(row.get("case", i))
        else:
            vals = dc if isinstance(dc, list) else [dc]
            bad = [v for v in vals if v not in CLAUSES]
            report["clause_values"][row.get("case", i)] = dc
            if bad:
                report.setdefault("clause_out_of_vocabulary", []).append(
                    {"case": row.get("case", i), "bad": bad})
    for path, rec in find_dual_records(payload):
        report["dual_records"] += 1
        s_out = rec.get("sha256_raw_stdout") or rec.get("raw_stdout_sha256")
        s_err = rec.get("sha256_raw_stderr") or rec.get("raw_stderr_sha256")
        if not (s_out and s_err):
            report["dual_missing_sha"].append(path)
            continue
        # recompute when the record carries its own streams
        if isinstance(rec.get("raw_stdout"), str):
            if sha(rec["raw_stdout"]) != s_out:
                report["dual_sha_mismatch"].append(
                    {"path": path, "which": "stdout",
                     "claimed": s_out, "actual": sha(rec["raw_stdout"])})
        if isinstance(rec.get("raw_stderr"), str):
            if sha(rec["raw_stderr"]) != s_err:
                report["dual_sha_mismatch"].append(
                    {"path": path, "which": "stderr",
                     "claimed": s_err, "actual": sha(rec["raw_stderr"])})
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
