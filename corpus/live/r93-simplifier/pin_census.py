#!/usr/bin/env python3
"""r93-simplifier pin<->emission census over every committed + fresh receipt.

Sources (all read-only):
  A. corpus/live/r93-author/runs{1,3}/<stamp>/verdicts.json  (author green runs)
  B. corpus/live/r93-author/fresh-reps/*.out                 (author 17 arms x3)
  C. corpus/live/r93-simplifier/runs-control*/<stamp>/verdicts.json (this seat)
  D. corpus/live/r93-scout/runs/*.out                        (scout corpus)
  E. corpus/live/r93-boundary/runs/*.out                     (boundary corpus)
  F. corpus/live/r93-simplifier/fold-runs/*/fold-verification.json (this seat)

For each of the 23 r93 rows it reports: how many receipts of its own arm were
found, in how many the committed signature appears, the distinct-line count of
its arm's PASS line across those receipts, whether the row's line is
byte-stable, and whether any receipt carries an `ERROR:` line (the rows carry
no allowlist entries, so any ERROR line would be an unrelated error).

Usage: python3 pin_census.py > pin-census.txt
"""
import ast
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent  # corpus/live/r93-simplifier -> repo root
HARNESS = HERE / "committed-fixtures" / "run_battery.py"

ARM_RE = re.compile(r"PASS (anim_lattice|r93b_anim) (\w+) ")


def load_rows():
    src = HARNESS.read_text()
    tree = ast.parse(src)
    rows = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                rows[t[0]] = {"script": t[1], "flags": list(t[2]), "sig": t[4]}
    return {k: v for k, v in rows.items() if k.startswith("r93_")}


def arm_of(text):
    m = ARM_RE.search(text)
    if m:
        return (m.group(1), m.group(2))
    m = re.search(r"PASS (anim_lattice|r93b_anim) (\w+)", text)
    if m:
        return (m.group(1), m.group(2))
    return None


def collect_receipts():
    """returns list of dicts: {source, name, text, lines}"""
    recs = []
    # A + C: verdicts.json runs
    for pat in ("r93-author/runs1", "r93-author/runs3", "r93-author/runs2",
                "r93-simplifier/runs-control1", "r93-simplifier/runs-control2",
                "r93-simplifier/runs-fold-gate"):
        for vf in sorted((REPO / "corpus/live" / pat).glob("*/verdicts.json")):
            try:
                data = json.loads(vf.read_text())
            except Exception:
                continue
            for r in data.get("results", []):
                if not r["case"].startswith("r93_"):
                    continue
                recs.append({"source": "%s/%s" % (pat, vf.parent.name),
                             "name": r["case"],
                             "lines": r.get("output") or [],
                             "text": "\n".join(r.get("output") or []),
                             "verdict": r.get("verdict")})
    # B: author fresh-reps
    for f in sorted((REPO / "corpus/live/r93-author/fresh-reps").glob("*.out")):
        txt = f.read_text()
        recs.append({"source": "author/fresh-reps", "name": f.name,
                     "lines": txt.splitlines(), "text": txt, "verdict": None})
    # D: scout runs
    for f in sorted((REPO / "corpus/live/r93-scout/runs").glob("*.out")):
        txt = f.read_text()
        recs.append({"source": "scout/runs", "name": f.name,
                     "lines": txt.splitlines(), "text": txt, "verdict": None})
    # E: boundary runs
    for f in sorted((REPO / "corpus/live/r93-boundary/runs").glob("*.out")):
        txt = f.read_text()
        recs.append({"source": "boundary/runs", "name": f.name,
                     "lines": txt.splitlines(), "text": txt, "verdict": None})
    return recs


def main():
    rows = load_rows()
    recs = collect_receipts()
    out = []
    out.append("receipts collected: %d" % len(recs))
    by_arm = {}
    for r in recs:
        a = arm_of(r["text"])
        if a:
            by_arm.setdefault(a, []).append(r)

    out.append("arms seen: %d" % len(by_arm))
    for (script, arm), rs in sorted(by_arm.items()):
        out.append("  %-16s %-14s receipts=%d sources=%s"
                   % (script, arm, len(rs), ",".join(sorted({x["source"].split("/")[0] for x in rs}))))

    out.append("")
    out.append("== per-row pin census ==")
    out.append("%-38s %-16s %-10s %8s %8s %6s %6s %s"
               % ("case", "script", "arm", "receipts", "sig_hits", "distinct", "error", "verdicts"))
    problems = []
    for case, row in sorted(rows.items()):
        arm = row["flags"][0].split("=", 1)[1]
        rs = by_arm.get((row["script"].removesuffix(".gd"), arm), [])
        hits = [r for r in rs if isinstance(row["sig"], str) and row["sig"] in r["text"]]
        pass_lines = []
        for r in rs:
            for line in r["lines"]:
                if re.match(r"PASS (anim_lattice|r93b_anim) %s " % re.escape(arm), line):
                    pass_lines.append(line)
        distinct = len(set(pass_lines))
        errs = sum(1 for r in rs for line in r["lines"] if "ERROR:" in line)
        verdicts = sorted({r.get("verdict") for r in rs if r.get("verdict")})
        out.append("%-38s %-16s %-10s %8d %8d %6d %6d %s"
                   % (case, row["script"], arm, len(rs), len(hits), distinct, errs,
                      ",".join(verdicts) or "-"))
        if not rs:
            problems.append("%s: no receipt of its arm" % case)
        elif len(hits) != len(rs):
            problems.append("%s: signature missing in %d/%d receipts"
                            % (case, len(rs) - len(hits), len(rs)))
        if errs:
            problems.append("%s: %d ERROR: lines in its receipts (no allowlist entries)"
                            % (case, errs))
    out.append("")
    out.append("== problems ==")
    for p in problems:
        out.append("  %s" % p)
    out.append("  (none)" if not problems else "")

    # ERROR:-line coverage across all r93 receipts
    out.append("")
    out.append("== ERROR:-line coverage over all receipts ==")
    err_lines = sorted({line.strip() for r in recs for line in r["lines"] if "ERROR:" in line})
    out.append("distinct ERROR: lines in r93 receipts: %d" % len(err_lines))
    for l in err_lines[:20]:
        out.append("  %s" % l)
    print("\n".join(out))


if __name__ == "__main__":
    main()
