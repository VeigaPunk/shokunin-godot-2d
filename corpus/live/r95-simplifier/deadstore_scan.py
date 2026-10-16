#!/usr/bin/env python3
"""r95-simplifier scope-aware value-observation (dead-store) scan.

For every `var`/`const` declaration in the two landed fixtures, enumerate the
occurrences *inside the declaring scope* and classify each one:

  decl        the declaration line itself
  assign      bare assignment target (`NAME = ...`)
  append      `NAME.append(...)` / `NAME.push_back(...)` (contents written only)
  idxwrite    `NAME[...] = ...` (contents written only)
  outarg      passed to `_pile(..., NAME)` (the out-parameter position)
  read        anything else (value consumed: used as receiver, argument, in a
              condition, in a `for`, returned, formatted, ...)

A declaration whose occurrences contain NO `read` is a dead store: its stored
value is never observed. Such a store is removable by keeping the side-effecting
call and dropping the binding (byte-neutral if the call is retained).

Usage: python3 deadstore_scan.py > deadstore-scan.txt
"""
import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CF = HERE / "committed-fixtures"
FIXTURES = ["dss_lattice.gd", "r95b_order.gd"]


def strip_code(line: str) -> str:
    out, i, in_str = [], 0, None
    while i < len(line):
        ch = line[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_str = ch
            i += 1
            continue
        if ch == "#":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def classify(line: str, name: str, dline: int, idx: int) -> str:
    if idx + 1 == dline:
        return "decl"
    s = line.strip()
    if re.match(r"^%s\s*(?::=|[+\-*/]?=)(?!=)" % re.escape(name), s):
        return "assign"
    if re.search(r"(?<![\w.])%s\.(append|push_back|append_array)\s*\(" % re.escape(name), line):
        return "append"
    if re.match(r"^%s\s*\[.*\]\s*(?::=|[+\-*/]?=)(?!=)" % re.escape(name), s):
        return "idxwrite"
    if "_pile(" in line and re.search(r"(?<![\w.])%s\s*\)" % re.escape(name), line):
        return "outarg"
    return "read"


def scan(path: Path) -> str:
    lines = path.read_text().splitlines()
    code = [strip_code(l) for l in lines]
    r = [f"### {path.name} ({len(lines)} lines, sha256 "
         f"{hashlib.sha256(path.read_bytes()).hexdigest()})"]

    scopes, scope = {}, "<file>"
    for idx, l in enumerate(code):
        m = re.match(r"^(\s*)func\s+(\w+)", l)
        if m:
            scope = m.group(2)
        scopes[idx] = scope

    decls = [(scopes[i], m.group(1), m.group(2), i + 1)
             for i, l in enumerate(code)
             for m in [re.match(r"^\s*(?:@\w+\s+)*(var|const|signal)\s+(\w+)", l)] if m]

    dead, live = [], []
    for sc, kind, name, dline in decls:
        occ = []
        for idx, l in enumerate(code):
            # function-locals are only visible inside their own scope;
            # file-scope names are scanned file-wide.
            if sc != "<file>" and scopes[idx] != sc:
                continue
            if not re.search(r"(?<![\w.])%s(?![\w])" % re.escape(name), l):
                continue
            occ.append((idx + 1, classify(l, name, dline, idx)))
        reads = [o for o in occ if o[1] == "read"]
        (live if reads else dead).append((sc, kind, name, dline, occ))
    r.append("declarations in scope: %d   live: %d   dead stores: %d"
             % (len(decls), len(live), len(dead)))
    r.append("")
    r.append("== DEAD STORES (no value-consuming read in scope) ==")
    for sc, kind, name, dline, occ in sorted(dead, key=lambda d: d[3]):
        r.append("  %-16s %-5s %-12s line=%-4d  occurrences=%d"
                 % (sc, kind, name, dline, len(occ)))
        for ln, how in occ:
            r.append("      line=%-4d %-8s %s" % (ln, how, lines[ln - 1].strip()[:130]))
    r.append("")
    r.append("== LIVE declarations (>=1 read) ==")
    for sc, kind, name, dline, occ in sorted(live, key=lambda d: d[3]):
        r.append("  %-16s %-5s %-12s line=%-4d reads=%d"
                 % (sc, kind, name, dline, sum(1 for o in occ if o[1] == "read")))
    return "\n".join(r)


if __name__ == "__main__":
    for f in FIXTURES:
        print(scan(CF / f))
        print()
