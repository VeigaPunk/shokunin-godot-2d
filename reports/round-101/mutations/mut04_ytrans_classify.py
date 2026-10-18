#!/usr/bin/env python3
"""MUT-4 (r101) — classify the omit/order-swap forgeries of the real C3 fixture r101_ytrans.gd.

Applies a verbatim copy of the battery's classify_process (run_battery.py lines 1725-1741,
harness sha printed below) to the captured merged outputs under /tmp/r101-mut04/out2/.

Pin shapes tested (candidate versions of the row signatures the integrator would land):
  P_yfull   : full pristine PASS line of `--arm=ytrans --offy=1000` (r95b/r100 full-line style)
  P_yhead   : that line truncated after dy_resid=0.0000 (dss-style head pin)
  P_yecho   : `PASS r101_ytrans ytrans offy=1000.0000` (echo-only head; the r95 trap shape)
  P_ykey    : `n_at_y=5 n_at_0=0` (contiguous key-subset pin)
  P_yabsy   : the t2_absy=[1000.0000|...] key (physics-only key)
  P_noevid  : full PASS line of mut_omitevid (an evidence-omitting pin shape)
  P_ysep/P_ycop/P_census : full pristine PASS lines of the other three arms
"""
import ast
import hashlib
import pathlib
import re

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
HARNESS = REPO / "corpus/fixtures/run_battery.py"
FIXTURE = REPO / "corpus/fixtures/r101_ytrans.gd"
OUT = pathlib.Path("/tmp/r101-mut04/out2")


# ---- verbatim from corpus/fixtures/run_battery.py:1725-1741 (dedented), never executed from repo
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


def captured(name: str):
    stdout = (OUT / f"{name}.stdout").read_text()
    stderr = (OUT / f"{name}.stderr").read_text()
    rc = int((OUT / f"{name}.rc").read_text().strip())
    return rc, stdout + stderr


def pass_line(text: str, arm: str) -> str:
    return next(l for l in text.splitlines() if l.startswith(f"PASS r101_ytrans {arm}"))


def main() -> None:
    print(f"harness   sha256 = {hashlib.sha256(HARNESS.read_bytes()).hexdigest()}")
    print(f"fixture   sha256 = {hashlib.sha256(FIXTURE.read_bytes()).hexdigest()} (tested snapshot)")

    _, base_y = captured("base_ytrans1000")
    _, base_ysep = captured("base_ysep")
    _, base_ycop = captured("base_ycop")
    _, base_census = captured("base_census")
    _, base_y0 = captured("base_ytrans0")
    line_y = pass_line(base_y, "ytrans")
    p_full = line_y
    p_head = line_y[:line_y.index("dy_resid=") + len("dy_resid=0.0000")]
    p_echo = "PASS r101_ytrans ytrans offy=1000.0000"
    p_key = "n_at_y=5 n_at_0=0"
    p_absy = re.search(r"t2_absy=\[[^\]]*\]", line_y).group(0)
    _, omit_text = captured("mut_omitevid")
    p_noevid = pass_line(omit_text, "ytrans")
    pins = [
        ("P_yfull", p_full), ("P_yhead", p_head), ("P_yecho", p_echo), ("P_ykey", p_key),
        ("P_yabsy", p_absy), ("P_noevid", p_noevid),
        ("P_ysep", pass_line(base_ysep, "ysep")),
        ("P_ycop", pass_line(base_ycop, "ycop")),
        ("P_census", pass_line(base_census, "census")),
    ]
    outputs = ["base_ytrans1000", "base_ytrans0", "base_ysep", "base_ycop", "base_census",
               "mut_noop_full", "mut_omitevid", "mut_omitevid_noop", "mut_swapkeys"]

    print("\n=== matrix: classify_process(rc, None, merged_output, 0, pin) ===\n")
    header = "output".ljust(20) + "".join(p[0].ljust(11) for p in pins)
    print(header)
    print("-" * len(header))
    for out_name in outputs:
        rc, out = captured(out_name)
        row = []
        for _, pin in pins:
            ok = classify_process(rc, None, out, 0, pin)
            row.append(("PASS" if ok else "FAIL").ljust(11))
        print(out_name.ljust(20) + "".join(row))

    print("\n=== byte identity: omit(real physics) vs omit(noop physics) ===")
    a = captured("mut_omitevid")[1]
    b = captured("mut_omitevid_noop")[1]
    print("identical:", a == b)
    if a != b:
        for la, lb in zip(a.splitlines(), b.splitlines()):
            if la != lb:
                print(" A:", la)
                print(" B:", lb)

    print("\n=== PASS lines ===")
    for out_name in outputs:
        rc, out = captured(out_name)
        arm = out_name.replace("base_", "").replace("mut_", "")
        arm = "ytrans" if arm in ("ytrans1000", "ytrans0", "noop_full", "omitevid", "omitevid_noop", "swapkeys") else arm
        print(f"\n[{out_name}] rc={rc}")
        print(pass_line(out, arm))

    print("\n=== guards ===")
    for out_name in outputs:
        rc, out = captured(out_name)
        print(f"{out_name}: rc={rc} stderr_bytes={(OUT / (out_name + '.stderr')).stat().st_size} "
              f"SCRIPT_ERROR={'SCRIPT ERROR:' in out}")


if __name__ == "__main__":
    main()
