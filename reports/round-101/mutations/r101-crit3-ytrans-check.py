#!/usr/bin/env python3
"""r101 CRIT-3 follow-up: does the in-flight C3 artifact (`corpus/fixtures/r101_ytrans.gd`,
E17) close the forgery class that my `m_forge_offy_echo` opened on the r95 row, and does
the r95 X-cell residual survive the ver8 `--offy` patch?

Read-only on the repo; scratch under CRIT3B_ROOT (default /tmp/r101-crit3b).
"""
import os
import pathlib
import shutil
import subprocess

import ast

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
YTRANS = REPO / "corpus/fixtures/r101_ytrans.gd"
R95B = REPO / "corpus/fixtures/r95b_order.gd"
PROJECT = REPO / "corpus/fixtures/project.godot"
HARNESS = REPO / "corpus/fixtures/run_battery.py"
ROOT = pathlib.Path(os.environ.get("CRIT3B_ROOT", "/tmp/r101-crit3b"))
GODOT = shutil.which("godot") or "godot"


def run(script, flags):
    cmd = [GODOT, "--headless", "--path", str(ROOT), "--script", f"res://{script}", "--", *flags]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return " ".join(cmd), p.stdout + p.stderr, p.returncode


def pass_line(out):
    for ln in out.splitlines():
        if ln.startswith("PASS "):
            return ln
    return None


def stage(script_text, name):
    (ROOT / name).write_text(script_text)
    return name


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROJECT, ROOT / "project.godot")
    shutil.copy2(R95B, ROOT / "r95b_order.gd")          # for the census arm
    ytrans_text = YTRANS.read_text()
    stage(ytrans_text, "r101_ytrans.gd")

    print("== pristine r101_ytrans.gd (E17, sha256 %s) ==" % __import__("hashlib").sha256(
        ytrans_text.encode()).hexdigest()[:16])
    pins = {}
    for tag, flags in [("y0", ["--arm=ytrans", "--offy=0"]),
                       ("y1000", ["--arm=ytrans", "--offy=1000"]),
                       ("ym1000", ["--arm=ytrans", "--offy=-1000"]),
                       ("census", ["--arm=census"]),
                       ("ysep", ["--arm=ysep", "--offy=1000", "--qoffy=0"])]:
        cmd, out, code = run("r101_ytrans.gd", flags)
        pins[tag] = pass_line(out)
        (ROOT / f"yt_{tag}.out").write_text(out)
        print(f"  {tag:7s} exit={code}")
        print(f"    {pins[tag][:200] if pins[tag] else None}")
        if pins[tag]:
            extra = [k for k in ("dy_resid", "t2_absy", "n_at_0", "t2_relpos", "ladder") if k in pins[tag]]
            print(f"    keys present: {extra}")

    # Forgery: the r95 phantom, now with an echo. Flag echoed, geometry at y=0,
    # query at y=0 -> every geometry-derived key still reports the truth (y=0).
    forge = (ytrans_text
             .replace('var made := _pile(["a", "b", "c", "d", "e"], 0.0, offy)',
                      'var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)', 1)
             .replace('var lad: Dictionary = await _ladder(ticks, 0.0, offy)',
                      'var lad: Dictionary = await _ladder(ticks, 0.0, 0.0)', 1)
             .replace('_pt(Vector2(16.0, offy))', '_pt(Vector2(16.0, 0.0))', 1))
    assert forge != ytrans_text
    stage(forge, "forge_ytrans.gd")
    cmd, out, code = run("forge_ytrans.gd", ["--arm=ytrans", "--offy=1000"])
    (ROOT / "yt_forge.out").write_text(out)
    fl = pass_line(out)
    print("\n== echo-only forgery of the ytrans arm (--offy=1000) ==")
    print(f"  forged PASS: {fl[:200] if fl else None}")
    accepted = pins["y1000"] is not None and pins["y1000"] in out
    print(f"  E17 intended pin (live y1000 line) accepted on the forgery: {accepted}"
          "   [False == the artifact closes the class]")
    print(f"  forged line still carries the echo offy=1000.0000: {'offy=1000.0000' in (fl or '')}")

    # X-cell residual against the ver8 patch: does m_dead_off still pass x0/x1000 when
    # the ver8 _ladder/_arm_celloff change is applied?
    ver8 = (REPO / "reports/round-101/mutations/r101-ver8-offy-C.patch").read_text()
    patched = None
    for hunk in ver8.split("@@")[1:]:
        pass
    # apply the two hunks textually (the patch text is simple -/+ pairs)
    text = R95B.read_text()
    pairs = []
    cur = None
    for ln in ver8.splitlines():
        if ln.startswith("+"):
            pairs.append(["+" + ln[1:], None])
        elif ln.startswith("-"):
            if pairs and pairs[-1][1] is None:
                pairs[-1][1] = ln[1:]
            else:
                pairs.append([None, ln[1:]])
    applied = 0
    for new, old in pairs:
        if new is None or old is None:
            continue
        if text.count(old) == 1:
            text = text.replace(old, new, 1)
            applied += 1
    print(f"\n== ver8-C patch applied to a scratch r95b_order.gd: {applied} replacements ==")
    stage(text, "r95b_ver8.gd")
    dead = text.replace('made := _pile(["a", "b", "c", "d", "e"], off, offy)',
                        'made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)', 1)
    dead = dead.replace("var lad := await _ladder(ticks, off, offy)",
                        "var lad := await _ladder(ticks, 0.0, 0.0)", 1)
    assert dead != text
    stage(dead, "r95b_ver8_dead.gd")

    # committed signatures (pre-patch) for x0/x1000 are untouched by ver8-C
    tree = ast.parse(HARNESS.read_text())
    cases = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "CASES" for t in node.targets):
            cases = node.value
    sigs = {}
    for el in cases.elts:
        if isinstance(el, ast.Tuple):
            nm = ast.literal_eval(el.elts[0])
            if nm in ("r95b_order_celloff_x0", "r95b_order_celloff_x1000"):
                sigs[nm] = (ast.literal_eval(el.elts[2]), ast.literal_eval(el.elts[4]))
    for nm, (flags, sig) in sigs.items():
        cmd, out, code = run("r95b_ver8_dead.gd", flags)
        print(f"  {nm:28s} on ver8-C + dead-off fixture: accepted={sig in out} (exit={code})")


if __name__ == "__main__":
    main()
