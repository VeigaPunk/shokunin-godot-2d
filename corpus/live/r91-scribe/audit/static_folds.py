#!/usr/bin/env python3
"""r91-scribe audit: (a) manifest completeness for the three r91 dossiers,
(b) landed signature structure vs the fixture's print statements:
    - every nav signature is a contiguous prefix of its print statement
    - no scheduler/race tail token appears inside any pinned signature
(c) CASES/row arithmetic on the committed harness."""
import ast, hashlib, json, os, re, sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = ROOT / "corpus/fixtures/nav_lattice.gd"
BAT = ROOT / "corpus/fixtures/run_battery.py"
OUT = ROOT / "corpus/live/r91-scribe/audit"

TAIL_TOKENS = ["settle=", "iter=", "ladder=", "first_reach=", "first_reach_sync=",
               "walk_steps=", "reached_at=", "first_reachable=", "iter_b=",
               "link_iter=", "gate=", "chg_iter_same=", "chg_iter_settled=",
               "dis_same=", "fwd_disabled_same=", "seq_a=", "seq_b=", "vel_a=",
               "vel_b=", "sum_max=", "settle_a=", "settle_b="]

# ---------- (a) manifest completeness ----------
comp = {}
for d in ["r91-scout", "r91-boundary", "r91-author"]:
    p = ROOT / f"corpus/live/{d}"
    entries = set()
    for line in (p / "manifest.sha256").read_text().splitlines():
        if not line.strip():
            continue
        entries.add(line.split(None, 1)[1].strip().lstrip("*").removeprefix("./"))
    ondisk = set()
    for dp, dn, fn in os.walk(p):
        for f in fn:
            ondisk.add(os.path.relpath(os.path.join(dp, f), p))
    missing = sorted(e for e in entries if e not in ondisk)
    extra = sorted(x for x in ondisk if x not in entries)
    comp[d] = {"entries": len(entries), "ondisk": len(ondisk),
               "manifest_entries_missing_on_disk": missing[:5],
               "ondisk_not_in_manifest": extra[:5]}
print("MANIFEST COMPLETENESS", json.dumps(comp, indent=1))

# ---------- (b) signature structure ----------
bat = ast.parse(BAT.read_text())
cases = None
for node in bat.body:
    if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "CASES" for t in node.targets):
        cases = node.value.elts
nav = []
for e in cases:
    name = e.elts[0].value
    if name.startswith("nav_lattice_"):
        nav.append({"case": name, "script": e.elts[1].value,
                    "flags": [x.value for x in e.elts[2].elts],
                    "rc": __import__("ast").literal_eval(e.elts[3]), "sig": e.elts[4].value})
src = FIX.read_text()
lines = src.splitlines()
# reconstruct the print statements: from a `print(` line to its matching close paren
prints = {}
i = 0
while i < len(lines):
    if re.match(r"\s*print\(", lines[i]):
        depth = 0
        buf = []
        j = i
        while j < len(lines):
            depth += lines[j].count("(") - lines[j].count(")")
            buf.append(lines[j])
            if depth <= 0:
                break
            j += 1
        body = "\n".join(buf)
        m = re.search(r'"((?:PASS|STALE|NAV_LATTICE)[^"]*)"', body)
        if m:
            prints[m.group(1)] = (i + 1, body)
        i = j + 1
    else:
        i += 1
print("\nPRINT SITES", len(prints))
for k in sorted(prints):
    print("  line", prints[k][0], repr(k))

report = {"signatures": []}
for row in nav:
    sig = row["sig"]
    rec = {"case": row["case"], "rc": row["rc"], "sig_len": len(sig)}
    # find the print statement whose literal prefix heads this signature
    head = sig.split(" ", 3)[:3]
    cand = [k for k in prints if sig.startswith(k) or k.startswith(sig)]
    rec["prefix_of_print_literal"] = bool(cand)
    rec["print_line"] = prints[cand[0]][0] if cand else None
    if cand:
        body = prints[cand[0]][1]
        # literal string pieces in order
        pieces = re.findall(r'"([^"]*)"', body)
        rec["print_pieces"] = pieces
        # the pinned literal must equal the concatenation of an in-order
        # prefix of the literal pieces (i.e. it ends at a piece boundary)
        acc = ""
        ends_at = None
        for idx, p in enumerate(pieces):
            acc += p
            if sig == acc:
                ends_at = idx
                break
            if not sig.startswith(acc):
                break
        rec["ends_at_piece_index"] = ends_at
        rec["piece_at_end"] = pieces[ends_at] if ends_at is not None else None
    hits = [t for t in TAIL_TOKENS if t in sig]
    rec["tail_tokens_inside_pin"] = hits
    report["signatures"].append(rec)
print("\nSIGNATURE STRUCTURE")
for r in report["signatures"]:
    print(f"  {r['case']:28s} rc={r['rc']:3d} len={r['sig_len']:4d} "
          f"prefix={r['prefix_of_print_literal']} ends_at_piece={r['ends_at_piece_index']} "
          f"tail_inside={r['tail_tokens_inside_pin']}")
(OUT / "static_folds.json").write_text(json.dumps(report, indent=1))
