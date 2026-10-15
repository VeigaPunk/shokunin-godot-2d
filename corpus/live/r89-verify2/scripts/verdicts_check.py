#!/usr/bin/env python3
# r89-verifier2: per-run verdicts.json analysis on frozen 53a0be7 bytes.
#   * every r89 row (geo2d_lattice_* / input89_edges_*) PASS, and for
#     geo2d_lattice_lineempty the record carries the populated required_stderr
#     pin list (the two Clipper2 fragments);
#   * every r90 row (r90_lattice_*) PASS;
#   * the emitted line that satisfied the signature is BYTE-IDENTICAL to a
#     pinned payload (string or envelope tuple member) — no substring slack.
# Usage: verdicts_check.py <verdicts.json>
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RB = ROOT / "tree" / "corpus" / "fixtures" / "run_battery.py"

src = RB.read_text()
tree = ast.parse(src)
cases = {}
pin_dict = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "CASES":
                for elt in node.value.elts:
                    row = ast.literal_eval(elt)
                    cases[row[0]] = row
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "required_stderr" \
                    and isinstance(node.value, ast.Call):
                pin_dict = ast.literal_eval(node.value.func.value)

v = json.load(open(sys.argv[1]))
rows = v["results"]
by_case = {r["case"]: r for r in rows}

R89 = sorted(n for n in cases if n.startswith(("geo2d_lattice_", "input89_edges_")))
R90 = sorted(n for n in cases if n.startswith("r90_lattice_"))

report = {"file": sys.argv[1], "total_rows": len(rows),
          "verdict_field": v.get("verdict"),
          "r89": {}, "r90": {}, "pin": {}, "sig_byte_check": [],
          "non_r89r90_fails": []}
ok = True
for n in R89 + R90:
    r = by_case.get(n)
    if r is None:
        report["r89" if n in R89 else "r90"][n] = "MISSING"
        ok = False
        continue
    fam = "r89" if n in R89 else "r90"
    report[fam][n] = r["verdict"]
    if r["verdict"] != "PASS":
        ok = False
        continue
    # byte-identical emitted line vs pinned payload(s)
    sig = r["signature"]
    payloads = list(sig) if isinstance(sig, list) else [sig]
    lines = r.get("output") or []
    exact = [ln for ln in lines if ln in payloads]
    contains = [ln for ln in lines if any(p in ln for p in payloads)]
    entry = {"case": n, "exact_line": bool(exact),
             "contains_only": (not exact) and bool(contains),
             "emitted": exact[0] if exact else (contains[0] if contains else None)}
    if not exact:
        ok = False
    report["sig_byte_check"].append(entry)

# the pin record on lineempty
le = by_case.get("geo2d_lattice_lineempty")
want = sorted(pin_dict["geo2d_lattice_lineempty"])
got = sorted(le.get("required_stderr") or [])
report["pin"] = {
    "case": "geo2d_lattice_lineempty",
    "record_required_stderr": le.get("required_stderr"),
    "expected_fragments": list(pin_dict["geo2d_lattice_lineempty"]),
    "populated_match": got == want,
    "actual_exit": le.get("actual_exit"),
    "verdict": le.get("verdict"),
}
if got != want or le["verdict"] != "PASS" or le.get("actual_exit") != -6:
    ok = False
# required_stderr must be present-but-empty on every other r89/r90 row
others = [n for n in R89 + R90 if n != "geo2d_lattice_lineempty"
          and by_case[n].get("required_stderr")]
report["pin"]["stray_required_stderr_rows"] = others
if others:
    ok = False

for r in rows:
    if r["verdict"] != "PASS" and not r["case"].startswith(
            ("geo2d_lattice_", "input89_edges_", "r90_lattice_")):
        report["non_r89r90_fails"].append(r["case"])

report["r89_pass"] = sum(1 for n in R89 if report["r89"].get(n) == "PASS")
report["r90_pass"] = sum(1 for n in R90 if report["r90"].get(n) == "PASS")
report["ok"] = ok
print(json.dumps(report, indent=2))
sys.exit(0 if ok else 1)
