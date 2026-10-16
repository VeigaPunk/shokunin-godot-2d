#!/usr/bin/env python3
"""r93-critic seat harness mutant: is the r93 floor gate live?

The committed r93 block carries ZERO expected_errors entries, so
`r93_expected_errors_all_matched` is `all(...)` over an empty generator — vacuous True.
This script tests the two halves of that statement against the harness ITSELF:

  base  : trimmed CASES (2 r93 rows), harness otherwise byte-identical -> gate True
  dead  : same, plus one synthetic r93 allowlist entry that can never match -> gate False

Both variants run the real harness (its own census + gate code) on the frozen
committed fixtures. Nothing tracked is written.
"""
import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SEAT = Path(__file__).resolve().parent.parent
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"
OUT = SEAT / "harness-mut"
GODOT = "/usr/bin/godot"

KEEP = ["r93_tween_census", "r93_tween_interp_value", "r93_anim_overshoot"]
INJECT = '        expected_errors = {\n            "r93_tween_census": ("ERROR: r93-critic fabricated dead entry",),\n'


def build(variant, inject):
    dst = OUT / variant
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for item in FROZEN.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dst / item.name)
        else:
            shutil.copy2(item, dst / item.name)
    src = (FROZEN / "run_battery.py").read_text()
    tree = ast.parse(src)
    cases_node = None
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", None) == "CASES" for x in n.targets):
            cases_node = n
    assert cases_node is not None
    lines = src.split("\n")
    start = cases_node.lineno - 1
    end = cases_node.end_lineno
    # keep the r93 rows under test plus the rows the unconditional meta probes look up
    all_rows = [ast.literal_eval(c) for c in cases_node.value.elts]
    wanted = set(KEEP) | {"save_process_writer", "save_process_reader", "save_process_missing"}
    keep_rows = [r for r in all_rows if r[0] in wanted]
    assert {r[0] for r in keep_rows} == wanted, sorted(wanted - {r[0] for r in keep_rows})
    generated = ["CASES = ["]
    for r in keep_rows:
        generated.append("    " + repr(tuple(r)) + ",")
    generated.append("]")
    lines[start:end] = generated
    src = "\n".join(lines)
    if inject:
        old = "        expected_errors = {\n"
        assert src.count(old) == 1
        src = src.replace(old, INJECT, 1)
    (dst / "run_battery.py").write_text(src)
    return dst


def run(dst, variant):
    runs = OUT / f"{variant}-runs"   # OUTSIDE the harness dir: the harness copies HERE into scratch
    cmd = [sys.executable, str(dst / "run_battery.py"), "--runs", str(runs), "--godot", GODOT]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    log = OUT / f"{variant}.log"
    log.write_text(p.stdout + "\n--- stderr ---\n" + p.stderr)
    vfiles = sorted(runs.glob("*/verdicts.json"))
    assert vfiles, "no verdicts.json"
    data = json.loads(vfiles[-1].read_text())
    rows = {r["case"]: r["verdict"] for r in data["results"]}
    surface = [r for r in data["results"] if r["case"] == "probe_error_clause_surface"]
    disc = surface[0]["discriminations"] if surface else {}
    return {"variant": variant, "rc": p.returncode, "rows": rows,
            "gate": disc.get("r93_expected_errors_all_matched"),
            "flipped_false": sorted(k for k, v in disc.items() if v is False),
            "census_r93": [r for r in surface[0].get("census", {}).get("rows", [])
                           if r["case"].startswith("r93_")] if surface else []}


def main():
    OUT.mkdir(exist_ok=True)
    print(f"# loadavg {Path('/proc/loadavg').read_text().strip()}")
    res = []
    for variant, inject in (("base", False), ("dead", True)):
        dst = build(variant, inject)
        r = run(dst, variant)
        res.append(r)
        print(f"{variant:5s} rc={r['rc']} gate={r['gate']} flipped_false={r['flipped_false']} "
              f"rows={r['rows']}")
        for cr in r["census_r93"]:
            print(f"      census {cr['case']}: entries={cr['entries']} "
                  f"any_matched={cr['any_entry_matched']}")
    (SEAT / "harness-mut.json").write_text(json.dumps(res, indent=1) + "\n")
    ok = (res[0]["gate"] is True and res[1]["gate"] is False
          and "r93_expected_errors_all_matched" in res[1]["flipped_false"])
    print("# HYPOTHESIS", "CONFIRMED" if ok else "NOT CONFIRMED",
          "- gate vacuous with no entries, live (False) when an r93 entry is dead")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
