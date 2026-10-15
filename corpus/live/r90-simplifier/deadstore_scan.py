#!/usr/bin/env python3
"""r90-simplifier dead-store scan (r89-simplifier methodology, re-implemented).

For every `var`/`const` declaration in the given GDScript files, count
occurrences of the identifier and classify each occurrence as a WRITE
(assignment target, compound assign, index-assign target, `.append()`-class
mutator call on it) or a CONSUMPTION (everything else). A store with zero
consumptions is a write-only store -> dead.

Also reports every local `var` whose only consumptions are inside a `return`
of the same value... (not attempted); the primary output is the write-only list.
"""
import re
import sys

WRITE_CALLS = {
    "append", "push_back", "push_front", "insert", "erase", "clear", "resize",
    "fill", "sort", "shuffle", "reverse", "remove_at", "set", "add", "merge",
    "setv", "assign",
}


def scan(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    src = "\n".join(lines)
    # declaration: `var name`, `var name :=`, `var name: Type`, `const name`
    decl_re = re.compile(r"^\s*(?:var|const)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?::=|:|=|$)")
    decls = {}
    for i, ln in enumerate(lines, 1):
        m = decl_re.match(ln)
        if m:
            name = m.group(1)
            decls.setdefault(name, []).append(i)
    out = []
    for name, decl_lines in sorted(decls.items()):
        occ = []
        tok = re.compile(r"\b%s\b" % re.escape(name))
        for i, ln in enumerate(lines, 1):
            for m in tok.finditer(ln):
                col = m.start()
                rest = ln[m.end():]
                before = ln[:col]
                kind = "read"
                # assignment target: `name =`, `name +=`, `name -=`, `name :=`
                if re.match(r"\s*(:=|\+=|-=|\*=|/=|%=|\|=|&=|\^=|=)(?!=)", rest):
                    # avoid `==` (not matched by the alternation above anyway)
                    kind = "write"
                elif re.match(r"\s*\[", rest):
                    # index assign target: `name[...] = ` or `name[...] += `
                    seg = rest
                    depth = 0
                    j = 0
                    closed = False
                    while j < len(seg):
                        c = seg[j]
                        if c == "[":
                            depth += 1
                        elif c == "]":
                            depth -= 1
                            if depth == 0:
                                closed = True
                                j += 1
                                break
                        j += 1
                    if closed and re.match(r"\s*(:=|\+=|-=|\*=|/=|%=|\|=|&=|\^=|=)(?!=)", seg[j:]):
                        kind = "write"
                elif re.match(r"\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", rest):
                    fn = re.match(r"\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", rest).group(1)
                    if fn in WRITE_CALLS:
                        kind = "write"
                if kind == "write" and name in decls and i in decl_lines:
                    # declaration line itself is neither
                    kind = "decl"
                occ.append((i, col, kind, ln.strip()))
        reads = [o for o in occ if o[2] == "read"]
        writes = [o for o in occ if o[2] == "write"]
        out.append((path, name, decl_lines, len(reads), len(writes), occ))
    return out


def main():
    paths = sys.argv[1:]
    for path in paths:
        print("=" * 78)
        print("FILE", path)
        for p, name, dl, nr, nw, occ in scan(path):
            flag = "  <== WRITE-ONLY (never consumed)" if nr == 0 else ""
            print(f"  {name:24s} decl@{dl} reads={nr} writes={nw}{flag}")
            if nr == 0:
                for (i, c, k, txt) in occ:
                    print(f"        :{i}: [{k}] {txt}")
        print()


if __name__ == "__main__":
    main()
