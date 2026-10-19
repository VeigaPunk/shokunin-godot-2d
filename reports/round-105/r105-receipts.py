"""r105: compact committed receipts from full-battery verdicts.json files.

Usage (lane root): python3 reports/round-105/r105-receipts.py <verdicts.json> [<verdicts.json> ...] > reports/round-105/r105-battery-receipts.json
The run directories themselves live under the ignored corpus/live/runs/; this
file keeps what the round's claims rest on: per-run totals, every res_uid_ and
r105_ row (execution order, verdict, signature, elapsed), and the shared-project
control record.
"""
import json
import ast
import hashlib
from collections import Counter
import sys
from pathlib import Path

out = []
for path in sys.argv[1:]:
    data = json.loads(Path(path).read_text())
    rows = data["results"]
    verdicts = [r.get("verdict") for r in rows]
    source_blobs = data.get("source_blobs", {})
    root = Path(__file__).resolve().parents[2]
    blob_matches = {}
    for relative, expected in source_blobs.items():
        file = root / relative
        if not file.is_file():
            file = root / "corpus" / "fixtures" / relative
        raw = file.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        blob_matches[relative] = actual == expected
    tree = ast.parse((root / "corpus/fixtures/run_battery.py").read_text())
    case_nodes = next(n.value.elts for n in ast.walk(tree) if isinstance(n, ast.Assign)
                      and any(getattr(t, "id", None) == "CASES" for t in n.targets)
                      and isinstance(n.value, ast.List))
    case_names = {n.elts[0].value for n in case_nodes}
    counts = Counter(r.get("case") for r in rows)
    focus = []
    for index, row in enumerate(rows):
        case = str(row.get("case", ""))
        if case.startswith(("res_uid_", "r105_")):
            focus.append({
                "order": index,
                "case": case,
                "verdict": row.get("verdict"),
                "actual_exit": row.get("actual_exit"),
                "signature": row.get("signature"),
                "signature_in_output": any(
                    line.strip() == row.get("signature") for line in row.get("output", [])),
                "elapsed_seconds": row.get("elapsed_seconds"),
                "isolated_project": Path(row["scratch_project"]).name if row.get("scratch_project") else None,
            })
    shared = next((r for r in rows if r.get("case") == "probe_res_uid_shared"), None)
    if shared is not None:
        shared = {k: v for k, v in shared.items()
                  if k not in ("shared_scratch_project", "shared_xdg_data_home", "shared_res_uid_root")}
    out.append({
        "run": Path(path).parent.name,
        "battery_verdict": data.get("verdict"),
        "source_blobs": source_blobs,
        "current_matches_source_blobs": blob_matches,
        "cases_count": len(case_nodes),
        "cases_backed_rows": sum(v for k, v in counts.items() if k in case_names),
        "cases_bad_multiplicity": {k: counts[k] for k in case_names if counts[k] != 1},
        "meta_rows": sum(v for k, v in counts.items() if k not in case_names),
        "duplicate_result_names": {k: v for k, v in counts.items() if v != 1},
        "rows": len(rows),
        "pass": verdicts.count("PASS"),
        "fail": verdicts.count("FAIL"),
        "res_uid_rows": sum(1 for f in focus if f["case"].startswith("res_uid_")),
        "res_uid_pass": sum(1 for f in focus if f["case"].startswith("res_uid_") and f["verdict"] == "PASS"),
        "r105_rows": sum(1 for f in focus if f["case"].startswith("r105_")),
        "r105_pass": sum(1 for f in focus if f["case"].startswith("r105_") and f["verdict"] == "PASS"),
        "res_uid_execution_order": [f["case"] for f in focus if f["case"].startswith("res_uid_")],
        "focus_rows": focus,
        "probe_res_uid_shared": shared,
    })
print(json.dumps(out, indent=1))
