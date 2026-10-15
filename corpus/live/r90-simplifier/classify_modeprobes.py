#!/usr/bin/env python3
"""r90-simplifier mode-probe classifier.

For every receipt under runs-tps30/ and runs-dummy/ (landed fixture, row flags),
classify with the PRODUCTION classify_process extracted verbatim from the
committed corpus/fixtures/run_battery.py, using the r90 row pins + allowlist
entries. Report per cell: rc, verdict, first differing pinned field.
"""
import ast
import os
import hashlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent.parent.parent
BATTERY = pathlib.Path(os.environ.get("R90_BATTERY", REPO / "corpus" / "fixtures" / "run_battery.py"))


def extract_classifier():
    src = BATTERY.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("def classify_process" + seg.split("def classify_process", 1)[1], ns)
            return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit("classify_process not found")


def load_rows():
    src = BATTERY.read_text()
    tree = ast.parse(src)
    rows, allow = [], {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            for elt in node.value.elts:
                vals = [e.value for e in elt.elts if isinstance(e, ast.Constant)]
                if vals and str(vals[0]).startswith("r90_"):
                    flags = [e.value for e in elt.elts if isinstance(e, ast.List)
                             for e in e.elts if isinstance(e, ast.Constant)]
                    rows.append((vals[0], vals[1], flags, vals[2], vals[3]))
    # allowlist entries: find the dict literal that maps r90_ cases -> tuple of ERROR lines
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and str(k.value).startswith("r90_") \
                        and isinstance(v, ast.Tuple):
                    allow[str(k.value)] = tuple(e.value for e in v.elts
                                                if isinstance(e, ast.Constant))
    return rows, allow


def main():
    classify, seg_sha = extract_classifier()
    rows, allow = load_rows()
    print(f"classifier_sha={seg_sha[:16]} rows={len(rows)} allow={sorted(allow)}")
    for mode in ("tps30", "dummy"):
        print("=" * 78)
        print(f"MODE {mode}  (receipts runs-{mode}/)")
        for name, script, flags, rc, pin in rows:
            arm = next(f.split("=", 1)[1] for f in flags if f.startswith("--arm="))
            for k in (1, 2):
                out_p = HERE / f"runs-{mode}" / f"{arm}.rep{k}.out"
                err_p = HERE / f"runs-{mode}" / f"{arm}.rep{k}.err"
                rc_p = HERE / f"runs-{mode}" / f"{arm}.rep{k}.rc"
                output = out_p.read_text() + err_p.read_text()
                actual_rc = int(rc_p.read_text().strip())
                verdict = classify(actual_rc, None, output, rc, pin, allow.get(name, ()))
                # first differing pinned field (only when a PASS line exists)
                detail = ""
                plines = [l for l in output.splitlines() if l.startswith("PASS r90_lattice")]
                if plines:
                    emitted = plines[0]
                    ptoks = re.findall(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=(\S+)", pin)
                    etoks = dict(re.findall(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=(\S+)", emitted))
                    for key, val in ptoks:
                        if etoks.get(key) != val:
                            detail = f" first_diff={key}: pin={val} got={etoks.get(key)}"
                            break
                else:
                    detail = " no-PASS-line"
                print(f"  {name:24s} rep{k} rc={actual_rc} verdict={'PASS' if verdict else 'FAIL'}{detail}")
        print()


if __name__ == "__main__":
    main()
