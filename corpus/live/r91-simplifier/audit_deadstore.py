#!/usr/bin/env python3
"""Scope-aware write-only-store scan of the committed nav_lattice.gd.

Splits the file into top-level functions, then for every `var` declaration
inside a function checks whether the name is READ anywhere in that same
function (excluding the declaration line and excluding pure assignment LHS).
File-scope `var`/`const` are checked across the whole file.
Emits a receipt on stdout.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
GD = (HERE / "committed-fixtures" / "nav_lattice.gd").read_text()
lines = GD.splitlines()

# split into top-level funcs
func_starts = [i for i, l in enumerate(lines) if re.match(r"^func ", l)]
funcs = {}
for k, s in enumerate(func_starts):
    e = func_starts[k + 1] if k + 1 < len(func_starts) else len(lines)
    name = re.match(r"^func ([a-z_0-9]+)\(", lines[s]).group(1)
    funcs[name] = (s, e)

ASSIGN = re.compile(r"\b%s(?:\.\w+|\[[^\]]*\])*\s*(?:=[^=]|\+=|-=|\*=|/=)")

def read_lines(name, lo, hi, decl_line):
    """Lines in [lo,hi) where `name` is read (not a bare assignment target)."""
    out = []
    for j in range(lo, hi):
        if j == decl_line:
            continue
        l = lines[j]
        for m in re.finditer(r"\b%s\b" % re.escape(name), l):
            rest = l[m.start():]
            prefix = l[:m.start()]
            # pure assignment target: name [.x|[i]]* = ... and nothing else
            # interesting before it on the line
            if ASSIGN.match(rest) and not re.search(r"\b%s\b" % re.escape(name), prefix):
                continue
            out.append(j + 1)
    return out

print("== r91-simplifier scope-aware write-only-store scan ==")
print("file: corpus/live/r91-simplifier/committed-fixtures/nav_lattice.gd "
      "(byte-exact 77d2f7e)")
print()

dead = []
# file scope
for i, l in enumerate(lines):
    m = re.match(r"^(var|const) ([A-Za-z_0-9]+)", l)
    if not m:
        continue
    kind, name = m.group(1), m.group(2)
    reads = read_lines(name, 0, len(lines), i)
    status = "READ" if reads else "WRITE-ONLY"
    if not reads:
        dead.append(("file", name, i + 1))
    print("  %-5s %-14s decl@%-5d %-10s reads=%s" % (kind, name, i + 1, status, reads))

print()
print("-- per-function locals --")
for fname, (s, e) in funcs.items():
    for i in range(s, e):
        m = re.match(r"^\t+var ([A-Za-z_0-9]+)", lines[i])
        if not m:
            continue
        name = m.group(1)
        reads = read_lines(name, s, e, i)
        status = "READ" if reads else "WRITE-ONLY"
        if not reads:
            dead.append((fname, name, i + 1))
        print("  %-24s %-14s decl@%-5d %-10s reads=%s" % (fname, name, i + 1, status, reads))

print()
print("WRITE-ONLY STORES: %d" % len(dead))
for scope, name, ln in dead:
    print("  %-24s %-14s line %d" % (scope, name, ln))

# lambda-body writes (appends to captured arrays) are reads of the array name,
# so the scan above already treats `hits.append(v)` as a read of `hits`.
print()
print("note: `name.append(...)` counts as a READ of `name` (the receiver is")
print("dereferenced); a pure-append-never-dereferenced array is reported below.")
for fname, (s, e) in funcs.items():
    for i in range(s, e):
        m = re.match(r"^\t+var ([A-Za-z_0-9]+)", lines[i])
        if not m:
            continue
        name = m.group(1)
        body = "\n".join(lines[s:e])
        # reads other than `name.append(` / `name.size()` style receiver use
        uses = [u for u in re.finditer(r"\b%s\b" % re.escape(name), body)]
        value_reads = 0
        for u in uses:
            rest = body[u.end():].lstrip()
            if rest.startswith(".append(") or rest.startswith("= ") or rest.startswith(":="):
                continue
            value_reads += 1
        if value_reads == 0:
            print("  PURE-SINK (append-only, never value-read): %-14s %s@%d"
                  % (name, fname, i + 1))
print()
print("== end scan ==")
