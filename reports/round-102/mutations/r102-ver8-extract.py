"""r102-ver8: independent extraction of CASES rows + allowlists from run_battery.py (read-only)."""
import ast, json, sys
from pathlib import Path

BAT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/run_battery.py")

def extract():
    tree = ast.parse(BAT.read_text())
    cases = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            cases = ast.literal_eval(node.value)
    assert cases is not None
    rows = []
    for c in cases:
        name, script, flags, expected_exit, evidence = c
        rows.append({"name": name, "script": script, "flags": list(flags),
                     "expected_exit": expected_exit,
                     "evidence": list(evidence) if isinstance(evidence, (tuple, list)) else evidence})
    # allowlists: expected_errors / required_stderr assigned inside execute()
    def grab(fn_name):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == fn_name:
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == "expected_errors" for t in sub.targets):
                        call = sub.value
                        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                                and call.func.attr == "get"):
                            continue  # the initial `expected_errors = ()` seed
                        d = ast.literal_eval(call.func.value)
                        return {k: list(v) for k, v in d.items()}
        raise SystemExit(f"no expected_errors in {fn_name}")
    ee = grab("execute")
    # required_stderr: second assign inside execute with dict literal directly? shape: {..}.get(name, ())
    def grab_req():
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "execute":
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == "required_stderr" for t in sub.targets):
                        v = sub.value
                        if isinstance(v, ast.Call):
                            d = ast.literal_eval(v.func.value)
                            return {k: list(x) for k, x in d.items()}
                        continue  # the initial `required_stderr = ()` seed
    rs = grab_req()
    return rows, ee, rs

if __name__ == "__main__":
    rows, ee, rs = extract()
    print(f"CASES rows: {len(rows)}  expected_errors keys: {len(ee)}  required_stderr keys: {len(rs)}")
    from collections import Counter
    scripts = Counter(r["script"] for r in rows)
    for s, n in sorted(scripts.items()):
        print(f"  {n:3d}  {s}")
    out = Path("/var/tmp/r102-ver8/rows_all.json")
    out.write_text(json.dumps({"rows": rows, "expected_errors": ee, "required_stderr": rs}, indent=1))
    print("wrote", out)
