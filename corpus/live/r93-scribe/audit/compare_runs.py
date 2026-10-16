#!/usr/bin/env python3
"""r93-scribe cross-run comparison: two fresh battery runs on committed bytes.

For every row: identical / tail-only (differs only after the pinned signature)
/ pin-diff (differs inside or before the signature) / no-signature rows.
Writes JSON under corpus/live/r93-scribe/audit/.
"""
import ast
import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
src = subprocess.run(["git", "-C", str(REPO), "show",
                      "HEAD:corpus/fixtures/run_battery.py"],
                     capture_output=True, text=True).stdout
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        CASES = ast.literal_eval(node.value)
SIG = {c[0]: c[4] for c in CASES}
R93 = {c[0] for c in CASES if c[0].startswith("r93_")}


def load(vj):
    d = json.loads(Path(vj).read_text())
    return {r["case"]: r for r in d["results"]}, d["verdict"]


def region(text, sig):
    i = text.find(sig)
    if i < 0:
        return None
    return i, i + len(sig)


def main(a, b, out):
    ra, va = load(a)
    rb, vb = load(b)
    report = {"run_a": str(a), "run_b": str(b), "verdict_a": va, "verdict_b": vb,
              "rows_a": len(ra), "rows_b": len(rb),
              "buckets": {"identical": [], "tail_only": [], "pin_diff": [],
                          "no_signature": [], "verdict_diff": []},
              "r93": {}}
    for case in sorted(set(ra) | set(rb)):
        if case not in ra or case not in rb:
            report["buckets"]["verdict_diff"].append(case)
            continue
        ta = "\n".join(ra[case]["output"] or [])
        tb = "\n".join(rb[case]["output"] or [])
        if ta == tb:
            report["buckets"]["identical"].append(case)
            if case in R93:
                report["r93"][case] = "identical"
            continue
        sig = SIG.get(case)
        if not sig:
            report["buckets"]["no_signature"].append(case)
            if case in R93:
                report["r93"][case] = "no_signature"
            continue
        sigs = sig if isinstance(sig, (list, tuple)) else [sig]
        best = None
        for s in sigs:
            ra_ = region(ta, s)
            rb_ = region(tb, s)
            if ra_ and rb_:
                # compare the pre-signature + signature region
                same_head = ta[:ra_[1]] == tb[:rb_[1]]
                best = (same_head, s)
                if same_head:
                    break
        if best is None:
            report["buckets"]["pin_diff"].append(case)
            if case in R93:
                report["r93"][case] = "pin_diff"
        elif best[0]:
            report["buckets"]["tail_only"].append(case)
            if case in R93:
                report["r93"][case] = "tail_only"
        else:
            report["buckets"]["pin_diff"].append(case)
            if case in R93:
                report["r93"][case] = "pin_diff"
    report["counts"] = {k: len(v) for k, v in report["buckets"].items()}
    Path(out).write_text(json.dumps(report, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in report.items() if k != "buckets"},
                     indent=1)[:4000])
    print("counts:", report["counts"])
    print("tail_only:", report["buckets"]["tail_only"])
    print("pin_diff:", report["buckets"]["pin_diff"])
    print("no_signature:", report["buckets"]["no_signature"])
    print("verdict_diff:", report["buckets"]["verdict_diff"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
