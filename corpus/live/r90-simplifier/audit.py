#!/usr/bin/env python3
"""r90-simplifier — mechanical audit receipt: arm/row bijection, helper call-site
census, CLI-knob usage, allowlist/gate inventory, and the arms-with-no-row check.
"""
import ast
import os
import re
import pathlib
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent.parent
FIX = pathlib.Path(os.environ.get("R90_FIXTURES", REPO / "corpus" / "fixtures"))


def rows():
    src = (FIX / "run_battery.py").read_text()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            for elt in node.value.elts:
                vals = [e.value for e in elt.elts if isinstance(e, ast.Constant)]
                if vals and str(vals[0]).startswith("r90_"):
                    flags = [e.value for e in elt.elts if isinstance(e, ast.List)
                             for e in e.elts if isinstance(e, ast.Constant)]
                    out.append((vals[0], vals[1], flags))
    return out


def main():
    print("== (a) r90 row -> probe/arm bijection ==")
    r = rows()
    arms = [next(f.split("=", 1)[1] for f in fl if f.startswith("--arm=")) for _, _, fl in r]
    print(f"  rows={len(r)} probes={sorted({s for _, s, _ in r})} arms={len(arms)}")
    print(f"  duplicate arms={[a for a in arms if arms.count(a) > 1]}")
    src = (FIX / "rb_lattice.gd").read_text()
    dispatch = re.findall(r'^\s*"([a-z0-9_]+)": (?:await )?_arm_', src, re.M)
    print(f"  dispatched arms={len(dispatch)} rowless={sorted(set(dispatch) - set(arms))} "
          f"row_without_arm={sorted(set(arms) - set(dispatch))}")
    print(f"  fallback arm present={'_ : _arm_fallback()' in src or '_: _arm_fallback()' in src}")

    print("\n== (b) helper call-site census (definition counts as 0 calls) ==")
    for f in ("rb_lattice.gd", "rb_watch.gd"):
        text = (FIX / f).read_text()
        for m in re.finditer(r"^func ([A-Za-z_][A-Za-z0-9_]*)", text, re.M):
            name = m.group(1)
            calls = len(re.findall(r"\b%s\b" % re.escape(name), text)) - 1
            flag = "  <== NO CALL SITES" if calls == 0 else ""
            print(f"  {f:16s} {name:16s} call_sites={calls}{flag}")

    print("\n== (c) CLI knob usage ==")
    for knob in ("--arm=", "--frames="):
        uses = [name for name, _, fl in r if any(x.startswith(knob) for x in fl)]
        print(f"  {knob:10s} rows_using={len(uses)} {uses if knob == '--frames=' else ''}")

    print("\n== (d) allowlist + gate inventory (r90 block) ==")
    bt = (FIX / "run_battery.py").read_text()
    for case in ("r90_lattice_comrefuse", "r90_lattice_impedge"):
        seg = re.search(r"'%s': \((.*?)\n\s*\)," % case, bt, re.S)
        entries = re.findall(r"'(ERROR:[^']*)'", seg.group(1)) if seg else []
        print(f"  {case}: entries={len(entries)}")
        for e in entries:
            print(f"      {e}")
    for key in ("r87_expected_errors_all_matched", "r88_expected_errors_all_matched",
                "r89_expected_errors_all_matched", "r90_expected_errors_all_matched"):
        print(f"  gate {key}: present={key in bt}")

    print("\n== (e) r90 pin 'PASS ...' prefix shape (signature includes prefix) ==")
    print(f"  signatures with prefix={sum(1 for _, _, _ in r)}/{len(r)}")


if __name__ == "__main__":
    main()
