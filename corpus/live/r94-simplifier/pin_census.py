#!/usr/bin/env python3
"""r94-simplifier pin<->emission census.

Every committed r94 CASES signature is checked against every receipt of its own
arm across the r94 evidence corpus (scout canonical + loadtest, boundary
quiet/load/ff30/ff60/ff120/ff120load/ab, author battery runs, this seat's runs),
plus ERROR:-line and stderr-byte accounting. Also re-verifies that the committed
signatures are byte-equal to the scout's ROWS_PREFIX entries.

Usage: python3 pin_census.py > pin-census.txt
"""
import ast
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"
SCOUT_ROWS = REPO / "corpus" / "live" / "r94-scout" / "author-rows.py.txt"


def load_cases():
    src = HARNESS.read_text()
    tree = ast.parse(src)
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": t[2], "exit": t[3],
                               "sig": t[4]}
    return {k: v for k, v in cases.items() if k.startswith("r94_")}


def load_prefix_rows():
    src = SCOUT_ROWS.read_text()
    tree = ast.parse(src)
    rows = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ROWS_PREFIX":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                rows[t[0]] = t[4]
    return rows


def receipt_files():
    """(case, path, kind) for every file receipt of an r94 arm."""
    out = []
    pat = re.compile(r"^(r94_particles_[\w]+)\.rep\d+\.(out|err|rc)$")
    roots = [
        (REPO / "corpus/live/r94-scout/runs", "scout-canonical"),
        (REPO / "corpus/live/r94-scout/runs/loadtest", "scout-loadtest"),
        (REPO / "corpus/live/r94-boundary/runs", "boundary"),
    ]
    for root, kind in roots:
        for p in sorted(root.rglob("*")):
            m = pat.match(p.name)
            if m:
                if kind == "scout-canonical" and p.parent.name == "loadtest":
                    continue  # counted under its own root
                out.append((m.group(1), p, kind))
    return out


def battery_rows(stamp):
    p = REPO / "corpus/live/runs" / stamp / "verdicts.json"
    d = json.loads(p.read_text())
    return {r["case"]: r for r in d["results"] if r["case"].startswith("r94_")}


def main():
    cases = load_cases()
    prefixes = load_prefix_rows()

    print("== committed signatures vs scout ROWS_PREFIX ==")
    for k, v in cases.items():
        p = prefixes.get(k)
        print("  %-38s committed==prefix: %s" % (k, p == v["sig"]))

    # group file receipts
    files = receipt_files()
    per_case = {k: [] for k in cases}
    for case, path, kind in files:
        if case in per_case:
            per_case[case].append((path, kind))

    # battery outputs
    battery = {}
    for stamp in ["20261016T055703426158Z", "20261016T060430025246Z"]:
        for k, r in battery_rows(stamp).items():
            battery.setdefault(k, []).append((stamp, r))

    print()
    print("== per-case census ==")
    total = 0
    matched = 0
    mismatched = []
    errs = []
    for k, v in cases.items():
        sig = v["sig"]
        recs = per_case[k]
        by_kind = {}
        out_recs = 0
        for path, kind in recs:
            by_kind[kind] = by_kind.get(kind, 0) + 1
            if path.suffix != ".out":
                continue
            out_recs += 1
            text = path.read_text(errors="replace")
            err_p = path.with_suffix(".err")
            rc_p = path.with_suffix(".rc")
            err_b = err_p.stat().st_size if err_p.is_file() else -1
            rc = rc_p.read_text().strip() if rc_p.is_file() else "?"
            total += 1
            if sig in text:
                matched += 1
            else:
                mismatched.append((k, str(path.relative_to(REPO)), kind))
            if err_b not in (0, -1) or rc not in ("0",):
                errs.append((k, str(path.relative_to(REPO)), err_b, rc))
            if "ERROR:" in text:
                errs.append((k, str(path.relative_to(REPO)), err_b, "ERROR-line"))
        b = battery.get(k, [])
        bmatch = 0
        for stamp, r in b:
            total += 1
            text = "\n".join(r["output"])
            if sig in text:
                matched += 1
                bmatch += 1
            else:
                mismatched.append((k, "runs/%s" % stamp, "battery"))
            if "ERROR:" in text:
                errs.append((k, "runs/%s" % stamp, "?", "ERROR-line"))
        print("  %-38s file_out=%-3d battery=%d/%d  (all matching files=%d)"
              % (k, out_recs, bmatch, len(b), len(recs)))

    print()
    print("== totals ==")
    print("  receipts checked: %d  signature present: %d  missing: %d"
          % (total, matched, len(mismatched)))
    print("  non-zero rc / non-empty stderr / ERROR-line events: %d" % len(errs))
    for m in mismatched:
        print("    MISS %-38s %s (%s)" % m)
    for e in errs:
        print("    ERR  %-38s %s err_bytes=%s rc=%s" % e)

    print()
    print("== cross-arm forge surface ==")
    print("  (do foreign-arm receipts satisfy any committed r94 signature?)")
    same_arm = {}
    foreign_forge = []
    no_pass_line = 0
    foreign = 0
    for p in sorted((REPO / "corpus/live/r94-scout/runs").glob("*.out")):
        if re.match(r"^r94_particles_[\w]+\.rep\d+\.out$", p.name):
            continue
        foreign += 1
        text = p.read_text(errors="replace")
        matched = [k for k, v in cases.items() if v["sig"] in text]
        m = re.search(r"PASS particles_lattice ([\w]+)", text)
        if not m:
            if matched:
                foreign_forge.append((p.name, "no PASS line", matched))
            else:
                no_pass_line += 1
            continue
        arm = m.group(1)
        own = "r94_particles_" + arm
        if matched and set(matched) == {own}:
            same_arm[arm] = same_arm.get(arm, 0) + 1
        elif matched:
            foreign_forge.append((p.name, arm, matched))
    print("  non-r94-named receipts scanned: %d  (no particles PASS line: %d)"
          % (foreign, no_pass_line))
    print("  same-arm extra receipts (smoke etc.): %d across %d arms"
          % (sum(same_arm.values()), len(same_arm)))
    print("  FOREIGN-arm receipts satisfying a committed r94 signature: %d"
          % len(foreign_forge))
    for f in foreign_forge:
        print("    %s (arm=%s) matches %s" % f)


if __name__ == "__main__":
    main()
