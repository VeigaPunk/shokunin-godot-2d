#!/usr/bin/env python3
"""r95 critic: parse the frozen committed run_battery.py, dump the r95 CASES rows
plus the whole CASE/RESULT structure needed for hygiene checks."""
import ast
import json
import pathlib
import sys

FROZEN = pathlib.Path(__file__).resolve().parents[1] / "frozen" / "corpus" / "fixtures" / "run_battery.py"
OUT = pathlib.Path(__file__).resolve().parents[1] / "scripts"


def find_cases(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "CASES":
                    return node.value
    raise SystemExit("CASES not found")


def main():
    src = FROZEN.read_text()
    tree = ast.parse(src)
    cases_node = find_cases(tree)
    cases = ast.literal_eval(cases_node)
    rows = []
    for i, c in enumerate(cases):
        name, script, args, rc, sig = c
        rows.append({"idx": i, "case": name, "script": script, "args": list(args), "rc": rc, "sig": sig})
    r95 = [r for r in rows if r["case"].startswith(("dss_lattice_", "r95b_order_"))]
    meta = [r for r in rows if r["case"].startswith(("probe_error_clause_surface", "census_", "floor_")) or "meta" in r["case"]]
    names = [r["case"] for r in rows]
    dupes = sorted({n for n in names if names.count(n) > 1})
    data = {
        "total_cases": len(rows),
        "r95_count": len(r95),
        "r95_rows": r95,
        "duplicate_case_names": dupes,
        "scripts_used_by_r95": sorted({r["script"] for r in r95}),
        "r95_nonzero_rc": [r["case"] for r in r95 if r["rc"] != 0],
        "r95_sig_lengths": {r["case"]: len(r["sig"]) for r in r95},
    }
    (OUT / "rows.json").write_text(json.dumps(data, indent=1))
    # TSV for quick inspection
    with (OUT / "rows.tsv").open("w") as fh:
        fh.write("idx\tcase\tscript\targs\trc\tsiglen\n")
        for r in rows:
            fh.write(f"{r['idx']}\t{r['case']}\t{r['script']}\t{' '.join(r['args'])}\t{r['rc']}\t{len(r['sig'])}\n")
    print(json.dumps({k: v for k, v in data.items() if k not in ("r95_rows", "r95_sig_lengths")}, indent=1))
    print("r95 case names:")
    for r in r95:
        print(f"  {r['idx']:4d} {r['case']:32s} {r['script']:20s} {' '.join(r['args'])}  siglen={len(r['sig'])}")


if __name__ == "__main__":
    sys.exit(main())
