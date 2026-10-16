#!/usr/bin/env python3
"""r93-simplifier: emitted-but-unpinned token census + helper-parameter census.

1. For every r93 arm, split its PASS line into `key=value` tokens and report
   which keys are pinned by at least one r93 row signature and which are not
   (the deliberately-unpinned mode surface).
2. Helper-parameter census: for each shared helper in the two fixtures, count
   call sites that pass each optional parameter (a default never overridden is
   the only 'unused parameter' shape; recorded, not deleted).

Usage: python3 unpinned_census.py > unpinned-census.txt
"""
import ast
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"
FIXES = [HERE / "committed-fixtures" / "anim_lattice.gd",
         HERE / "committed-fixtures" / "r93b_anim.gd"]
REPO = HERE.parent.parent.parent


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


def arm_line(text, probe, arm):
    for line in text.splitlines():
        if line.startswith("PASS %s %s " % (probe, arm)):
            return line
    return None


def token_keys(line):
    # keys are `name=` tokens outside of brackets; values may contain
    # brackets/commas, so scan left-to-right.
    keys = []
    for m in re.finditer(r"(?:^|[\s\[])([a-zA-Z_][\w]*)=(?![=])", line):
        keys.append(m.group(1))
    return keys


def main():
    rows = load_rows()
    out = []
    receipts = []
    for pat, probe in (("r93-author/runs1", None), ("r93-author/runs3", None),
                       ("r93-author/fresh-reps", None)):
        base = REPO / "corpus/live" / pat
        for f in sorted(base.rglob("*.out")):
            receipts.append(f.read_text())
    out.append("receipt files scanned: %d" % len(receipts))

    arms = sorted({(r["script"].removesuffix(".gd"), r["flags"][0].split("=", 1)[1])
                   for r in rows.values()})
    out.append("")
    out.append("== emitted vs pinned token census ==")
    for probe, arm in arms:
        lines = [l for l in (arm_line(t, probe, arm) for t in receipts) if l]
        if not lines:
            out.append("  %-14s %-14s NO RECEIPT" % (probe, arm))
            continue
        line = lines[0]
        keys = sorted(set(token_keys(line)))
        sigs = [r["sig"] for r in rows.values()
                if r["script"].removesuffix(".gd") == probe
                and r["flags"][0].split("=", 1)[1] == arm and isinstance(r["sig"], str)]
        pinned = [k for k in keys if any(k + "=" in s for s in sigs)]
        unpinned = [k for k in keys if k not in pinned]
        out.append("  %-14s %-14s tokens=%d pinned=%d unpinned=%d"
                   % (probe, arm, len(keys), len(pinned), len(unpinned)))
        if unpinned:
            out.append("      unpinned: %s" % ", ".join(unpinned))
        if arm == "clock":
            out.append("      NOTE: the whole `clock` arm is an unpinned launch fingerprint "
                       "(boundary evidence; no CASES row by design).")

    out.append("")
    out.append("== helper-parameter census ==")
    for fix in FIXES:
        src = fix.read_text()
        lines = src.splitlines()
        out.append("  %s" % fix.name)
        funcs = {}
        for i, l in enumerate(lines):
            m = re.match(r"^func (\w+)\((.*)\)", l)
            if m:
                funcs[m.group(1)] = {"params": [p.strip() for p in m.group(2).split(",") if p.strip()],
                                     "def_line": i + 1, "calls": []}
        for name, info in funcs.items():
            for i, l in enumerate(lines):
                if i + 1 == info["def_line"]:
                    continue
                if re.search(r"(?<![\w.])%s\s*\(" % re.escape(name), l):
                    info["calls"].append(l.strip())
        for name, info in funcs.items():
            if not info["params"]:
                continue
            opt = [p for p in info["params"] if "=" in p]
            if not opt:
                continue
            names = [p.split(":")[0].split("=")[0].strip() for p in info["params"]]
            required = len([p for p in info["params"] if "=" not in p])
            positional = {n: 0 for n in names}
            keyword = {n: 0 for n in names}
            for call in info["calls"]:
                inner = call.split("(", 1)[1].rsplit(")", 1)[0] if "(" in call else ""
                depth = 0
                args, cur = [], ""
                for ch in inner:
                    if ch in "([{":
                        depth += 1
                    elif ch in ")]}":
                        depth -= 1
                    if ch == "," and depth == 0:
                        args.append(cur)
                        cur = ""
                    else:
                        cur += ch
                if cur.strip():
                    args.append(cur)
                for i, a in enumerate(args):
                    if re.match(r"\s*(\w+)\s*=", a):
                        keyword[re.match(r"\s*(\w+)", a).group(1)] += 1
                    elif i < len(names):
                        positional[names[i]] += 1
            out.append("    %-18s optional=%s  required=%d  positional_passes=%s  keyword_passes=%s"
                       % (name, [p.split(":")[0].split("=")[0].strip() for p in opt],
                          required, {k: v for k, v in positional.items() if k in
                                     [p.split(":")[0].split("=")[0].strip() for p in opt]},
                          {k: v for k, v in keyword.items() if v}))
    print("\n".join(out))


if __name__ == "__main__":
    main()
