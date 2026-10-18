#!/usr/bin/env python3
"""r101 SIMP-1 analyzer v2: recompute verdicts from receipts with the real allowlists,
then compare base vs folded under declared masks (noisy keys + backtrace line numbers)."""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import simp1  # noqa: E402

WORK = simp1.WORK
BT = re.compile(r"(res://[\w./]+\.gd):\d+")
KV = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\S+)")


def extract_dict(name):
    """Handle both `x = {...}` and `x = {...}.get(k, ())`."""
    src = (simp1.FIX / "run_battery.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            val = node.value
            if isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute) and val.func.attr == "get":
                val = val.func.value
            if not isinstance(val, ast.Dict):
                continue
            out = {}
            for k, v in zip(val.keys, val.values):
                key = ast.literal_eval(k)
                try:
                    out[key] = ast.literal_eval(v)
                except Exception:
                    out[key] = None
            return out
    return {}


def main():
    res = json.loads((WORK / "results.json").read_text())
    extra = WORK / "results_audio_lattice.json"
    if extra.exists():
        res.update(json.loads(extra.read_text()))
    cases, classify_process = simp1.extract()
    expected_errors = extract_dict("expected_errors")
    required_stderr = extract_dict("required_stderr")
    print("allowlist entries:", len(expected_errors), "required_stderr:", len(required_stderr))
    rows = [c for c in cases if c[1] in simp1.FIXTURE_TREES]
    cand_of = {"nav_lattice.gd": "f_nav", "canvas_lattice.gd": "f_canvas",
               "r98b_attack.gd": "f_attack", "r98b_rksenum.gd": "f_rksenum",
               "audio_lattice.gd": "f_audio"}

    def receipt(name, tree, rep):
        stem = "%s.%s.rep%d" % (name, tree, rep)
        so = WORK / "receipts" / (stem + ".stdout")
        if not so.exists():
            return None
        return {"stdout": so.read_text(), "stderr": (WORK / "receipts" / (stem + ".stderr")).read_text(),
                "rc": int((WORK / "receipts" / (stem + ".rc")).read_text().split()[0])}

    def verdict(row, r):
        name = row[0]
        sigs = row[4] if isinstance(row[4], (tuple, list)) else (row[4],)
        allowed = expected_errors.get(name) or ()
        out, err = r["stdout"] + r["stderr"], r["stderr"]
        if name == "r98_canvas_clip":
            pass
        ok = any(classify_process(r["rc"], None, out, row[3], s, allowed) for s in sigs)
        rs = required_stderr.get(name) or ()
        if rs:
            ok = ok and all(f in err for f in rs) and any(s in r["stdout"] for s in sigs)
        if "SCRIPT ERROR:" in out or "Parse Error:" in out:
            ok = False
        return ok

    report = {"rows": {}, "masked_diffs": [], "base_fail": [], "cand_fail": [], "verdict_flips": [],
              "noisy_keys": {}, "pinned_field_issues": []}
    trees_by_fix = simp1.FIXTURE_TREES

    for row in rows:
        name, script = row[0], row[1]
        cand = cand_of[script]
        sides = {}
        for tree in trees_by_fix[script]:
            reps = [1, 2] if tree in ("base", cand) else [1]
            sides[tree] = {}
            for rep in reps:
                r = receipt(name, tree, rep)
                if r is None:
                    continue
                r["verdict"] = verdict(row, r)
                sides[tree][rep] = r
        base_rs = [sides["base"].get(1), sides["base"].get(2)]
        cand_rs = [sides[cand].get(1), sides[cand].get(2)]
        # noisy keys from base reps (declared load-noise mask)
        noisy = set()
        if all(base_rs):
            keys = {}
            for r in base_rs:
                for k, v in KV.findall(r["stdout"]):
                    keys.setdefault(k, set()).add(v)
            noisy = {k for k, vs in keys.items() if len(vs) > 1}
        report["noisy_keys"][name] = sorted(noisy)

        def mask(text):
            text = BT.sub(r"\1:N", text)
            def repl(m):
                return m.group(0) if m.group(1) not in noisy else m.group(1) + "=<NOISE>"
            return KV.sub(repl, text)

        for i, (b, c) in enumerate(zip(base_rs, cand_rs)):
            if not b or not c:
                continue
            if b["stdout"] != c["stdout"]:
                if mask(b["stdout"]) != mask(c["stdout"]):
                    report["masked_diffs"].append({
                        "row": name, "rep": i + 1, "tree": cand,
                        "base": b["stdout"][-400:], "cand": c["stdout"][-400:]})
            if b["rc"] != c["rc"]:
                report["verdict_flips"].append({"row": name, "kind": "rc", "base": b["rc"], "cand": c["rc"]})
            if b["verdict"] != c["verdict"]:
                report["verdict_flips"].append({"row": name, "kind": "verdict", "base": b["verdict"], "cand": c["verdict"]})
            if not b["verdict"]:
                report["base_fail"].append((name, i + 1, b["rc"]))
            if not c["verdict"]:
                report["cand_fail"].append((name, i + 1, c["rc"]))
        # pinned-field census: every key=value token in the row signature
        sig = row[4] if isinstance(row[4], str) else None
        if sig:
            issues = []
            for k, v in KV.findall(sig):
                for tree in (["base", cand] + [t for t in trees_by_fix[script] if t not in ("base", cand)]):
                    vals = {vv for r in sides[tree].values() for kk, vv in KV.findall(r["stdout"]) if kk == k}
                    if v not in vals:
                        issues.append((tree, k, v, sorted(vals)[:3]))
            if issues:
                report["pinned_field_issues"].append({"row": name, "issues": issues[:8]})
        report["rows"][name] = {
            "script": script,
            "base": {str(r): {"sha": None if not sides["base"].get(r) else simp1.sha256 if False else None} for r in (1, 2)},
            "base_verdicts": [sides["base"][r]["verdict"] for r in sorted(sides["base"])],
            "cand_verdicts": [sides[cand][r]["verdict"] for r in sorted(sides[cand])],
            "other": {t: [sides[t][r]["verdict"] for r in sorted(sides[t])]
                      for t in trees_by_fix[script] if t not in ("base", cand)},
        }
    (WORK / "analysis2.json").write_text(json.dumps(report, indent=1))
    print("base_fail:", report["base_fail"])
    print("cand_fail:", report["cand_fail"])
    print("verdict flips:", report["verdict_flips"])
    print("masked diffs:", [(d["row"], d["rep"]) for d in report["masked_diffs"]])
    print("pinned field issues:", [(p["row"], p["issues"][:2]) for p in report["pinned_field_issues"]][:10])
    print("rows with noisy keys:", {k: v for k, v in report["noisy_keys"].items() if v})


if __name__ == "__main__":
    main()
