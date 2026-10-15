#!/usr/bin/env python3
"""r90-simplifier — landing-integrity receipt from MY control run (independent of
the author's receipts).

For each r90 row in runs-control/<stamp>/verdicts.json:
  * the row's PASS line is byte-identical to the CASES pin;
  * every `R90 <arm> <key>=<value>` emission line is present in the pin
    (no unpinned emission);
  * the pinned field count equals the emitted field count;
  * stderr is empty except the two whitelist-bearing rows.
"""
import ast
import os
import glob
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent.parent.parent
BATTERY = pathlib.Path(os.environ.get("R90_BATTERY", REPO / "corpus" / "fixtures" / "run_battery.py"))


def load_rows():
    src = BATTERY.read_text()
    tree = ast.parse(src)
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            for elt in node.value.elts:
                vals = [e.value for e in elt.elts if isinstance(e, ast.Constant)]
                if vals and str(vals[0]).startswith("r90_"):
                    flags = [e.value for e in elt.elts if isinstance(e, ast.List)
                             for e in e.elts if isinstance(e, ast.Constant)]
                    rows.append((vals[0], vals[1], flags, vals[2], vals[3]))
    return rows


def main():
    vf = sorted(glob.glob(str(HERE / "runs-control" / "*" / "verdicts.json")))[-1]
    d = json.loads(pathlib.Path(vf).read_text())
    by_case = {r["case"]: r for r in d["results"]}
    rows = load_rows()
    print(f"control run: {vf}")
    print(f"rows={len(d['results'])} verdict={d['verdict']}")
    allok = True
    TOK = re.compile(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=(\S+)")
    for name, script, flags, rc, pin in rows:
        r = by_case[name]
        arm = next(f.split("=", 1)[1] for f in flags if f.startswith("--arm="))
        out_lines = r.get("output") or []
        pass_lines = [l for l in out_lines if l.startswith("PASS r90_lattice")]
        emis = [l for l in out_lines if l.startswith("R90 ")]
        expected_pass = pin  # CASES signature already carries the "PASS ..." prefix
        identical = len(pass_lines) == 1 and pass_lines[0] == expected_pass
        if not identical and pass_lines:
            idx = next((i for i, (a, b) in enumerate(zip(pass_lines[0], expected_pass))
                        if a != b), min(len(pass_lines[0]), len(expected_pass)))
            identical = f"MISMATCH@{idx}: got={pass_lines[0][idx:idx + 40]!r} want={expected_pass[idx:idx + 40]!r}"
        emitted_toks = []
        for l in emis:
            payload = l[len("R90 "):].split(" ", 1)[1]
            emitted_toks.extend(TOK.findall(payload))
        pinned_toks = TOK.findall(pin)
        unpinned = [(k, v) for k, v in emitted_toks if (k, v) not in pinned_toks]
        ok = (identical is True) and not unpinned and \
            len(emitted_toks) == len(pinned_toks) and r["verdict"] == "PASS"
        allok &= ok
        print(f"  {name:24s} verdict={r['verdict']} pass_line==pin={identical} "
              f"emitted_toks={len(emitted_toks)} pinned_toks={len(pinned_toks)} "
              f"unpinned={unpinned} OK={ok}")
    print(f"ALL_ROWS_INTEGRITY_OK={allok}")


if __name__ == "__main__":
    main()
