#!/usr/bin/env python3
"""Classify an arbitrary rb_lattice receipt against the committed r90 pins.

usage: check_one.py <case-name> <out> <err> <rc>
Prints the production-classifier verdict plus the first mismatching token.
"""
import ast
import hashlib
import pathlib
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FROZEN = pathlib.Path(__file__).parent / "run_battery.committed-ee20575.py"
BATTERY = FROZEN if FROZEN.is_file() else REPO / "corpus/fixtures/run_battery.py"


def load_cases():
    src = BATTERY.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("CASES not found")


def extract_classifier():
    src = BATTERY.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("def classify_process" + seg.split("def classify_process", 1)[1], ns)
            return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit("classify_process not found")


ALLOW = {
    "r90_lattice_comrefuse": ('ERROR: Condition "center_of_mass_mode != CENTER_OF_MASS_MODE_CUSTOM" is true.',),
    "r90_lattice_impedge": ('ERROR: Condition "p_inertia < 0" is true.',
                            'ERROR: Condition "p_mass <= 0" is true.'),
}


def main():
    name, out_p, err_p, rc_p = sys.argv[1:5]
    cases = load_cases()
    cls, sha = extract_classifier()
    case = next(c for c in cases if c[0] == name)
    _, _, _, exit_, sig = case
    out = pathlib.Path(out_p).read_text()
    err = pathlib.Path(err_p).read_text()
    rc = int(pathlib.Path(rc_p).read_text().strip())
    code = -(rc - 128) if rc > 128 else rc
    merged = out + err
    verdict = cls(code, None, merged, exit_, sig, ALLOW.get(name, ()))
    print(f"case={name} exit={code} classifier_sha={sha[:12]} verdict={'PASS' if verdict else 'FAIL'}")
    if not verdict:
        got = [ln for ln in out.splitlines() if ln.startswith("PASS r90_lattice")]
        if not got:
            print("  no PASS line")
        else:
            pin = sig.split()
            gotl = got[-1].split()
            # first mismatching token
            for i, (a, b) in enumerate(zip(pin, gotl)):
                if a != b:
                    print(f"  first_mismatch@tok{i}: pin={a!r} got={b!r}")
                    break
            else:
                print(f"  token-count pin={len(pin)} got={len(gotl)}")
        errlines = [l for l in err.splitlines() if "ERROR:" in l]
        if errlines:
            print(f"  stderr ERROR lines={len(errlines)}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
