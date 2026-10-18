#!/usr/bin/env python3
"""MUT-4 (r101) — classify the captured C3 Y-measurement forgeries.

Reads the lane harness TEXT (read-only, never executes run_battery.py) via ast to
lift the exact landed CASES signatures, then applies a verbatim copy of the
battery's own classify_process (source lines 1725-1741 of the run_battery.py the
sha below identifies) to each captured (stdout+stderr)-merged output.

Shapes under test (C3 = a "real Y-translation measurement" row for the celloff
cell that r95 left as a phantom):
  P_cur_y1000 : the LANDED r95b_order_celloff_y1000 pin (byte-dup of x0)
  P_cur_x0    : the landed r95b_order_celloff_x0 pin (byte-exactness control)
  P_full      : full PASS line of the patched baseline at --offy=1000 (candidate fix pin)
  P_head_offy : that line truncated after the offy= key (dss-style head pin, keeps offy)
  P_short     : that line truncated after "off=0.0000" (minimal head pin)
  P_yecho     : the bare "offy=1000.0000" token (echo-only pin)
  P_relposy   : the t2_relpos=[...1000.0000...] key (physics-only pin, no echo)
  P_pair      : env diag line + "\n" + PASS line (multi-line pin)

Outputs under test (captured by mut04_runs.sh under /tmp/r101-mut04/out/):
  unpatched_x0 / unpatched_y1000   : repo fixture, phantom state
  base_offy0 / base_offy1000       : patched baseline
  m1_echo / m2_omitkey / m3_omity / m4_swapkeys / m5_noenv : one-axis forgeries
"""
import ast
import hashlib
import pathlib
import re

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
HARNESS = REPO / "corpus/fixtures/run_battery.py"
OUT = pathlib.Path("/tmp/r101-mut04/out")

# ---------------------------------------------------------------- verbatim classifier
# Copied verbatim from corpus/fixtures/run_battery.py lines 1725-1741 (dedented);
# that file's sha256 is printed in the receipt below. Never executed from the repo.
def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
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


def landed_signature(case_name: str) -> str:
    """Lift the CASES tuple signature for `case_name` out of the harness text (read-only)."""
    tree = ast.parse(HARNESS.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            for row in ast.literal_eval(node.value):
                if row[0] == case_name:
                    assert isinstance(row[4], str), f"{case_name}: tuple signature, not str"
                    return row[4]
    raise KeyError(case_name)


def captured(name: str):
    stdout = (OUT / f"{name}.stdout").read_text()
    stderr = (OUT / f"{name}.stderr").read_text()
    rc_text = (OUT / f"{name}.rc").read_text().strip()
    if not rc_text:
        # tmpfs truncation observed once (m2_omitkey.rc 0 B @16:25); the runner's
        # run_log line is the same shell's rc record -- fall back to it, and say so.
        import re as _re
        log = (OUT / "run_log.txt").read_text()
        m = _re.search(rf"^{_re.escape(name)} rc=(-?\d+) ", log, _re.M)
        assert m, f"{name}: no rc in .rc or run_log"
        rc_text = m.group(1)
        print(f"[note] {name}.rc empty; rc={rc_text} recovered from run_log")
    return int(rc_text), stdout + stderr  # battery merges exactly this way (run_battery.py:1870)


def main() -> None:
    print(f"harness sha256 = {hashlib.sha256(HARNESS.read_bytes()).hexdigest()}")

    p_cur_y1000 = landed_signature("r95b_order_celloff_y1000")
    p_cur_x0 = landed_signature("r95b_order_celloff_x0")

    _, base1000 = captured("base_offy1000")
    pass_line = next(l for l in base1000.splitlines() if l.startswith("PASS r95b_order celloff"))
    env_line = next(l for l in base1000.splitlines() if l.startswith("R95B celloff env="))
    relpos_y = re.search(r"t2_relpos=\[[^\]]*\]", pass_line).group(0)
    p_full = pass_line
    p_head_offy = pass_line[:pass_line.index("add_order=")]
    p_short = pass_line[:pass_line.index("offy=")]
    p_pair = env_line + "\n" + pass_line
    pins = [
        ("P_cur_y1000", p_cur_y1000),
        ("P_cur_x0", p_cur_x0),
        ("P_full", p_full),
        ("P_head_offy", p_head_offy),
        ("P_short", p_short),
        ("P_yecho", "offy=1000.0000"),
        ("P_relposy", relpos_y),
        ("P_pair", p_pair),
    ]
    outputs = ["unpatched_x0", "unpatched_y1000", "base_offy0", "base_offy1000",
               "m1_echo", "m2_omitkey", "m3_omity", "m4_swapkeys", "m5_noenv"]

    print("\n=== matrix: classify_process(rc, None, output, 0, pin) ===\n")
    header = "output".ljust(16) + "".join(p[0].ljust(13) for p in pins)
    print(header)
    print("-" * len(header))
    for out_name in outputs:
        rc, out = captured(out_name)
        cells = []
        for _, pin in pins:
            ok = classify_process(rc, None, out, 0, pin)
            cells.append(("PASS" if ok else "FAIL").ljust(13))
        print(out_name.ljust(16) + "".join(cells))

    print("\n=== key bytes ===")
    for out_name in outputs:
        rc, out = captured(out_name)
        line = next((l for l in out.splitlines() if l.startswith("PASS r95b_order celloff")), "<none>")
        print(f"\n[{out_name}] rc={rc}")
        print(line)
    print("\n[unpatched_y1000 == unpatched_x0 output]", end=" ")
    print(captured("unpatched_y1000")[1] == captured("unpatched_x0")[1])


if __name__ == "__main__":
    main()
