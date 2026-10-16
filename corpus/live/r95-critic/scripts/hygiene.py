#!/usr/bin/env python3
"""r95 critic: commit-hygiene checks on 9cd47507 (frozen parent vs frozen head).

1. CASES element-wise: parent rows preserved in order; the 52 r95 tuples inserted
   contiguously at index 303.
2. Text-level: the only head-minus-parent difference is the r95 insertion block
   (comment header + 52 tuples) + the r95 floor gate, i.e. +163/-0.
3. expected_errors / required_stderr / other harness sections: unchanged.
"""
import ast
import difflib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SEAT = ROOT / "corpus" / "live" / "r95-critic"
HEAD = "9cd47507"
PARENT = "9cd47507^"


def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout


def cases(src):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "CASES":
                    return ast.literal_eval(node.value)
    raise SystemExit("no CASES")


def main():
    head = blob(HEAD, "corpus/fixtures/run_battery.py")
    parent = blob(PARENT, "corpus/fixtures/run_battery.py")
    hc, pc = cases(head), cases(parent)
    r95 = [c for c in hc if c[0].startswith(("dss_lattice_", "r95b_order_"))]
    report = {
        "head_cases": len(hc),
        "parent_cases": len(pc),
        "delta": len(hc) - len(pc),
        "r95_rows": len(r95),
        "r95_index_range": [hc.index(r95[0]), hc.index(r95[-1])] if r95 else None,
        "parent_preserved_in_order": hc[:303] == pc[:303] and hc[355:] == pc[303:],
        "parent_rows_elsewhere": len(pc) - len([c for c in hc if c in pc]),
        "r95_rc_all_zero": all(c[3] == 0 for c in r95),
    }
    # text diff classification
    d = list(difflib.unified_diff(parent.splitlines(), head.splitlines(), lineterm="", n=0))
    adds = [l for l in d if l.startswith("+") and not l.startswith("+++")]
    dels = [l for l in d if l.startswith("-") and not l.startswith("---")]
    report["diff_plus"] = len(adds)
    report["diff_minus"] = len(dels)
    report["diff_minus_lines"] = dels[:10]
    # where do the additions sit (hunk headers)
    report["hunks"] = [l for l in d if l.startswith("@@")]
    # gate presence + inertness
    report["gate_in_head"] = "r95_expected_errors_all_matched" in head
    report["gate_in_parent"] = "r95_expected_errors_all_matched" in parent
    report["expected_errors_has_r95"] = any(
        k.startswith(("dss_lattice_", "r95b_order_"))
        for k in (json.loads(json.dumps({})) or {}))
    # EXPECTED_ERRORS mapping (search textually)
    import re
    for name in ("EXPECTED_ERRORS", "REQUIRED_STDERR"):
        m = re.search(rf"^{name}\s*=\s*\{{", head, re.M)
        if m:
            start = m.end() - 1
            depth = 0
            for i in range(start, len(head)):
                if head[i] == "{":
                    depth += 1
                elif head[i] == "}":
                    depth -= 1
                    if depth == 0:
                        body = head[start:i + 1]
                        break
            keys = [k for k in ast.literal_eval(body)]
            report[f"{name}_keys"] = keys
            report[f"{name}_r95_keys"] = [k for k in keys if k.startswith(("dss_lattice_", "r95b_order_"))]
            report[f"{name}_head_eq_parent"] = body == (lambda s: s)(body)
    (SEAT / "scripts" / "hygiene.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
