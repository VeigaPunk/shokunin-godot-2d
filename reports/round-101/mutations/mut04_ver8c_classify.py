#!/usr/bin/env python3
"""MUT-4 (r101) — classify ver8's staged variant-C pin against omit/order-swap forgeries.

Pin under test = the exact expected line ver8 stages in r101-ver8-offy-C-cases.patch
(also cross-checked for 439 B / md5 fb57ea8b...). Controls: the currently landed
r95b_order_celloff_y1000 pin (x0 byte-dup) and the r95b_order_celloff_x0 pin.
"""
import ast
import hashlib
import pathlib

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
HARNESS = REPO / "corpus/fixtures/run_battery.py"
OUT = pathlib.Path("/tmp/r101-mut04/out3")


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    # verbatim from corpus/fixtures/run_battery.py:1725-1741 (dedented)
    lines = output.splitlines()
    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def captured(name: str):
    stdout = (OUT / f"{name}.stdout").read_text()
    stderr = (OUT / f"{name}.stderr").read_text()
    rc_text = (OUT / f"{name}.rc").read_text().strip()
    assert rc_text, f"{name}: empty rc"
    return int(rc_text), stdout + stderr


def landed(case_name: str) -> str:
    tree = ast.parse(HARNESS.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            for row in ast.literal_eval(node.value):
                if row[0] == case_name:
                    return row[4]
    raise KeyError(case_name)


def main() -> None:
    c_expected = pathlib.Path("/tmp/r101-mut04/proj3/c_expected.txt").read_text()
    pins = [
        ("C_expected", c_expected),
        ("cur_y1000", landed("r95b_order_celloff_y1000")),
        ("cur_x0", landed("r95b_order_celloff_x0")),
    ]
    outputs = ["c_base", "c_committed", "c_omit_y", "c_swapkeys", "c_dropt64"]
    print(f"harness sha256 = {hashlib.sha256(HARNESS.read_bytes()).hexdigest()}")
    print(f"C_expected: {len(c_expected.encode())} B md5={hashlib.md5(c_expected.encode()).hexdigest()}")
    print("\n=== matrix: classify_process(rc, None, merged_output, 0, pin) ===\n")
    header = "output".ljust(16) + "".join(p[0].ljust(14) for p in pins)
    print(header)
    print("-" * len(header))
    for out_name in outputs:
        rc, out = captured(out_name)
        cells = [("PASS" if classify_process(rc, None, out, 0, pin) else "FAIL").ljust(14)
                 for _, pin in pins]
        print(out_name.ljust(16) + "".join(cells))
    print("\n=== PASS lines ===")
    for out_name in outputs:
        rc, out = captured(out_name)
        line = next((l for l in out.splitlines() if l.startswith("PASS r95b_order celloff")), "<none>")
        print(f"\n[{out_name}] rc={rc} stderr={(OUT / (out_name + '.stderr')).stat().st_size}B")
        print(line)


if __name__ == "__main__":
    main()
