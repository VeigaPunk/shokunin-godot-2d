#!/usr/bin/env python3
"""r101 CRIT-3 attack on the r95 `--offy` row (C3).

Read-only against the repo: extracts the three `r95b_order_celloff_*` pinned
signatures from corpus/fixtures/run_battery.py by AST, then stages scratch
project copies under /tmp/r101-crit3/mut/<mutant>/ with ONE fixture mutation
each and runs the three row commands with the harness launch shape
(`godot --headless --path <proj> --script res://r95b_order.gd -- <flags>`).
Verdicts are computed with the harness's own acceptance rule on the committed
signature (`signature in stdout+stderr`, exit 0, no SCRIPT ERROR/Parse Error).

Never runs corpus/fixtures/run_battery.py and never writes inside corpus/.
"""
import ast
import json
import pathlib
import shutil
import os
import subprocess

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
HARNESS = REPO / "corpus/fixtures/run_battery.py"
FIXTURE = REPO / "corpus/fixtures/r95b_order.gd"
PROJECT = REPO / "corpus/fixtures/project.godot"
# /tmp is a usrquota tmpfs shared with the whole 64-seat swarm; EDQUOT was
# observed twice under load (16:23, 16:31). CRIT3_ROOT lets the seat point the
# scratch at a filesystem with headroom (btrfs /home) without touching any
# shared repo file.
ROOT = pathlib.Path(os.environ.get("CRIT3_ROOT", "/tmp/r101-crit3"))
MUT = ROOT / "mut"
GODOT = shutil.which("godot") or "godot"

ROWS = ["r95b_order_celloff_x0", "r95b_order_celloff_x1000", "r95b_order_celloff_y1000"]


def pinned_signatures():
    tree = ast.parse(HARNESS.read_text())
    cases = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "CASES" for t in node.targets):
            cases = node.value
    out = {}
    for el in cases.elts:
        if not isinstance(el, ast.Tuple):
            continue
        name = ast.literal_eval(el.elts[0])
        if name in ROWS:
            out[name] = {"flags": ast.literal_eval(el.elts[2]),
                         "exit": ast.literal_eval(el.elts[3]),
                         "signature": ast.literal_eval(el.elts[4])}
    assert len(out) == 3, sorted(out)
    return out


MUTATIONS = {
    # flag echoed but the pile AND the query never move: "the flag has no
    # spatial effect" -- the shape the committed --offy already has.
    "m_dead_off": [
        ('made := _pile(["a", "b", "c", "d", "e"], off, 0.0)',
         'made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)'),
        ("var lad := await _ladder(ticks, off)",
         "var lad := await _ladder(ticks, 0.0)"),
    ],
    # --offy becomes a REAL Y translation of the pile; the query stays at y=0.
    "m_live_offy_naive": [
        ('made := _pile(["a", "b", "c", "d", "e"], off, 0.0)',
         'made := _pile(["a", "b", "c", "d", "e"], off, _opt_float("offy", 0.0))'),
    ],
    # remediation shape: pile translated in X and Y, query follows in Y,
    # relpos normalised on BOTH axes, and a live `offy` token is printed.
    "m_live_offy_full": [
        ("func _relpos(arr: Array, ox: float) -> String:",
         "func _relpos(arr: Array, ox: float, oy: float = 0.0) -> String:"),
        ('parts.append("%.4f,%.4f" % [p.x - ox, p.y])',
         'parts.append("%.4f,%.4f" % [p.x - ox, p.y - oy])'),
        ("func _ladder(ticks: Array, ox: float) -> Dictionary:",
         "func _ladder(ticks: Array, ox: float, oy: float = 0.0) -> Dictionary:"),
        ("var q := Vector2(16.0 + ox, 0.0)",
         "var q := Vector2(16.0 + ox, oy)"),
        ("first_relpos = _relpos(r, ox)", "first_relpos = _relpos(r, ox, oy)"),
        ('"last_relpos": _relpos(last, ox),', '"last_relpos": _relpos(last, ox, oy),'),
        ('var off := _opt_float("off", 0.0)',
         'var off := _opt_float("off", 0.0)\n\tvar offy := _opt_float("offy", 0.0)'),
        ('made := _pile(["a", "b", "c", "d", "e"], off, 0.0)',
         'made := _pile(["a", "b", "c", "d", "e"], off, offy)'),
        ('_it("off", "%.4f" % off)',
         '_it("off", "%.4f" % off)\n\t_it("offy", "%.4f" % offy)'),
        ("var lad := await _ladder(ticks, off)",
         "var lad := await _ladder(ticks, off, offy)"),
    ],
    # committed bytes, unmutated control.
    "m_control": [],
}
# m_live_offy_full plus an unpinned diagnostic printing the pile's RAW y, so
# "the translation physically happened" is measured and not inferred from the
# offset-normalised (hence offset-invariant) pinned tokens.
MUTATIONS["m_live_offy_full_raw"] = MUTATIONS["m_live_offy_full"] + [
    ('\t_it("off", "%.4f" % off)\n\t_it("offy", "%.4f" % offy)',
     '\t_it("off", "%.4f" % off)\n\t_it("offy", "%.4f" % offy)\n'
     '\t_diag("oy_raw", "%.4f" % (made[0] as Node2D).global_position.y)\n'
     '\t_diag("ox_raw", "%.4f" % (made[0] as Node2D).global_position.x)'),
]

# The "cheap fix" candidate: echo the flag into the pinned line and nothing
# else -- the translation is still never applied. If a pin built from the
# remediation's tokens accepts this fixture, the fix re-creates the class.
MUTATIONS["m_forge_offy_echo"] = [
    ('\t_it("off", "%.4f" % off)',
     '\t_it("off", "%.4f" % off)\n\t_it("offy", "%.4f" % _opt_float("offy", 0.0))'),
]

# Remediation with the offset-NORMALISED tokens plus one token derived from
# geometry (the pile's raw y), i.e. a pin that binds the effect, not the echo.
MUTATIONS["m_fix_pinned_live"] = MUTATIONS["m_live_offy_full"] + [
    ('\t_it("off", "%.4f" % off)\n\t_it("offy", "%.4f" % offy)',
     '\t_it("off", "%.4f" % off)\n\t_it("offy", "%.4f" % offy)\n'
     '\t_it("oy_raw", "%.4f" % (made[0] as Node2D).global_position.y)'),
]


def stage(name, edits):
    # /tmp is a usrquota tmpfs shared with the whole swarm (EDQUOT observed at
    # 16:23 under load 41), so ONE project directory is reused and only the
    # 25 KB script is rewritten per mutant.
    proj = MUT
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROJECT, proj / "project.godot")
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) == 1, (name, old, text.count(old))
        text = text.replace(old, new)
    (proj / "r95b_order.gd").write_text(text)
    return proj


def run(proj, flags):
    cmd = [GODOT, "--headless", "--path", str(proj), "--script", "res://r95b_order.gd", "--", *flags]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return cmd, proc.stdout + proc.stderr, proc.returncode


def main():
    sigs = pinned_signatures()
    results = {"signatures": sigs, "mutants": {}}
    for name, edits in MUTATIONS.items():
        proj = stage(name, edits)
        per_row = {}
        probes = dict(sigs)
        probes["PROBE_y_neg777"] = {"flags": ["--arm=celloff", "--off=0", "--offy=-777.25"], "exit": 0,
                                    "signature": ""}
        for row, spec in probes.items():
            cmd, output, code = run(proj, spec["flags"])
            accepted = (code == spec["exit"] and bool(spec["signature"]) and spec["signature"] in output
                        and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)
            passed_lines = [ln for ln in output.splitlines() if ln.startswith("PASS r95b_order")]
            per_row[row] = {
                "flags": spec["flags"],
                "command": " ".join(cmd),
                "exit": code,
                "accepted_with_committed_signature": accepted,
                "output_sha256": __import__("hashlib").sha256(output.encode()).hexdigest(),
                "pass_lines": passed_lines,
            }
            (ROOT / f"{name}.{row}.out").write_text(output)
        results["mutants"][name] = per_row
        print(f"== {name}")
        for row, r in per_row.items():
            print(f"   {row:24s} exit={r['exit']} accepted={r['accepted_with_committed_signature']}")
            for ln in r["pass_lines"]:
                print(f"       {ln[:150]}")
    (ROOT / "mutant_verdicts.json").write_text(json.dumps(results, indent=2) + "\n")
    print("wrote", ROOT / "mutant_verdicts.json")

    # Remediation pin matrix: which of the two candidate pins binds the EFFECT
    # (geometry) rather than the ECHO (the flag value)?
    def first_pass_line(path):
        for ln in path.read_text().splitlines():
            if ln.startswith("PASS r95b_order"):
                return ln
        return None

    pins = {
        "PIN_echo_normalised": first_pass_line(ROOT / "m_live_offy_full.r95b_order_celloff_y1000.out"),
        "PIN_geometry": first_pass_line(ROOT / "m_fix_pinned_live.r95b_order_celloff_y1000.out"),
    }
    fixtures = ["m_control", "m_forge_offy_echo", "m_live_offy_full", "m_fix_pinned_live", "m_dead_off"]
    matrix = {"pins": pins, "accepts": {}}
    for pin_name, pin in pins.items():
        matrix["accepts"][pin_name] = {}
        for fx in fixtures:
            out = (ROOT / f"{fx}.r95b_order_celloff_y1000.out")
            if not out.exists():
                matrix["accepts"][pin_name][fx] = None
                continue
            matrix["accepts"][pin_name][fx] = bool(pin) and pin in out.read_text()
    (ROOT / "remediation_pin_matrix.json").write_text(json.dumps(matrix, indent=2) + "\n")
    print("\n== remediation pin matrix (flags --arm=celloff --off=0 --offy=1000) ==")
    for pin_name, acc in matrix["accepts"].items():
        print(f"  {pin_name:22s} " + "  ".join(f"{fx}={acc}" for fx, acc in acc.items()))
    print("wrote", ROOT / "remediation_pin_matrix.json")


if __name__ == "__main__":
    main()
