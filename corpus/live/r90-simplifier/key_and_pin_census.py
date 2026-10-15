#!/usr/bin/env python3
"""r90-simplifier — dictionary-key scan + pin/emission census.

1. dict-key scan: every string literal used as a dictionary key in
   `{"k": ...}` / `d["k"]` / `.get("k", ...)` / `d.get("k")` is classified as
   WRITE (assignment target `d["k"] = `, literal-init key) or READ (anything
   else). A key with zero reads is a dead dict key.

2. pin/emission census: for each r90 CASES row, parse the pinned signature
   into ordered `key=value` tokens and compare with the fields the arm
   actually emits on its PASS line (from a receipt), in both directions:
   emitted-but-unpinned (unfalsifiable evidence) and pinned-but-unemitted
   (impossible row).
"""
import ast
import os
import re
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")


def dict_key_scan(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    keys = {}
    for i, ln in enumerate(lines, 1):
        for m in re.finditer(r'\["([A-Za-z_][A-Za-z0-9_]*)"\]', ln):
            k = m.group(1)
            after = ln[m.end():]
            kind = "write" if re.match(r"\s*(=|\+=|-=)", after) else "read"
            keys.setdefault(k, []).append((i, kind, ln.strip()))
        for m in re.finditer(r'\.get\("([A-Za-z_][A-Za-z0-9_]*)"', ln):
            keys.setdefault(m.group(1), []).append((i, "read", ln.strip()))
        for m in re.finditer(r'\{"([A-Za-z_][A-Za-z0-9_]*)":', ln):
            keys.setdefault(m.group(1), []).append((i, "init", ln.strip()))
    return keys


def cases():
    src = Path(os.environ.get("R90_BATTERY", REPO / "corpus/fixtures/run_battery.py")).read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            for elt in node.value.elts:
                vals = [e.value for e in elt.elts if isinstance(e, ast.Constant)]
                if vals and str(vals[0]).startswith("r90_"):
                    flags = [e.value for e in elt.elts
                             if isinstance(e, ast.List)
                             for e in e.elts if isinstance(e, ast.Constant)]
                    out.append((vals[0], vals[1], flags, vals[2], vals[3]))
    return out


def main():
    print("=" * 78)
    print("DICT-KEY SCAN")
    for f in ("corpus/fixtures/rb_lattice.gd", "corpus/fixtures/rb_watch.gd"):
        print(f"\nFILE {f}")
        keys = dict_key_scan(REPO / f)
        dead = []
        for k, occ in sorted(keys.items()):
            nread = sum(1 for o in occ if o[1] == "read")
            nwrite = sum(1 for o in occ if o[1] in ("write", "init"))
            flag = ""
            if nread == 0:
                dead.append(k)
                flag = "  <== DEAD DICT KEY (never read)"
            print(f"  {k:22s} reads={nread} writes={nwrite}{flag}")
        print(f"  dead_keys={dead}")

    print("\n" + "=" * 78)
    print("PIN/EMISSION CENSUS (r90 rows)")
    recdir = REPO / "corpus/live/r90-author/runs"
    for name, script, flags, rc, pin in cases():
        arm = next((f.split("=", 1)[1] for f in flags if f.startswith("--arm=")), None)
        receipt = recdir / f"{arm}.rep1.out"
        text = receipt.read_text(encoding="utf-8")
        pass_lines = [l for l in text.splitlines() if l.startswith("PASS r90_lattice")]
        assert len(pass_lines) == 1, (name, pass_lines)
        emitted = pass_lines[0][len(f"PASS r90_lattice {arm} "):]
        # emitted key=value tokens (values may contain '|' and ',' but not ' ')
        etoks = re.findall(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=(\S+)", emitted)
        ptoks = re.findall(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=(\S+)", pin)
        en = {k: v for k, v in etoks}
        pn = {k: v for k, v in ptoks}
        missing = [k for k in en if k not in pn]
        extra = [k for k in pn if k not in en]
        mismatch = [k for k in en if k in pn and en[k] != pn[k]]
        print(f"  {name:26s} emitted={len(en):2d} pinned={len(pn):2d} "
              f"unpinned={missing} pinned_but_unemitted={extra} value_mismatch={mismatch}")


if __name__ == "__main__":
    main()
