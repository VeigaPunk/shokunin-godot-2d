#!/usr/bin/env python3
"""r102-S2: per-hunk analysis for the two owned patches.

For each hunk: target file, old/new span, deleted/added lines, enclosing
GDScript function in the OLD file, and — for deleted helpers — the arms that
call them (call-site census). Emits JSON for the shard's per-hunk table."""
import json
import re
import sys

PATCHES = [
    ("stree", "/var/tmp/r102-S2/patches/r101-simp2-stree_lattice.gd.diff",
     "/var/tmp/r102-S2/base/corpus/fixtures/stree_lattice.gd"),
    ("scene_io", "/var/tmp/r102-S2/patches/r101-simp2-scene_io_lattice.gd.diff",
     "/var/tmp/r102-S2/base/corpus/fixtures/scene_io_lattice.gd"),
]

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")


def funcs_by_line(lines):
    """top-level + nested func name active at each line (1-based)."""
    starts = []
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^(\s*)(?:static )?func (\w+)\s*\(", ln)
        if m:
            starts.append((i, len(m.group(1)), m.group(2)))
    active = {}
    for i in range(1, len(lines) + 1):
        name = None
        for s, _indent, n in starts:
            if s <= i:
                name = n
            else:
                break
        active[i] = name
    return active, starts


def main():
    out = []
    for key, patch_path, old_path in PATCHES:
        lines = open(old_path).read().splitlines()
        active, starts = funcs_by_line(lines)
        ptext = open(patch_path).read().splitlines()
        i = 0
        hn = 0
        while i < len(ptext):
            m = HUNK_RE.match(ptext[i])
            if not m:
                i += 1
                continue
            hn += 1
            old_start = int(m.group(1))
            old_len = int(m.group(2) or 1)
            new_len = int(m.group(4) or 1)
            body = []
            j = i + 1
            while j < len(ptext) and not ptext[j].startswith(("@@", "--- ", "+++ ", "diff ")):
                body.append(ptext[j])
                j += 1
            minus = [b[1:] for b in body if b.startswith("-") and not b.startswith("---")]
            plus = [b[1:] for b in body if b.startswith("+") and not b.startswith("+++")]
            enc = sorted({active.get(old_start), active.get(old_start + old_len - 1)} - {None})
            # call-site census for identifiers deleted in this hunk
            callsite_arms = {}
            for ln in minus:
                fm = re.match(r"^\s*(?:static\s+)?func\s+(\w+)", ln)
                if fm:
                    fname = fm.group(1)
                    arms = []
                    for k, l in enumerate(lines, 1):
                        if re.search(r"\b%s\s*\(" % re.escape(fname), l):
                            if re.match(r"^\s*func %s\s*\(" % re.escape(fname), l):
                                continue
                            a = active.get(k)
                            if a and a != fname and a not in arms:
                                arms.append(a)
                    callsite_arms[fname] = arms
            out.append({
                "patch": key, "hunk": hn,
                "old_start": old_start, "old_len": old_len, "new_len": new_len,
                "enclosing": enc, "deleted": minus, "added": plus,
                "callsite_arms": callsite_arms,
            })
            i = j
    json.dump(out, open("/var/tmp/r102-S2/armmap.json", "w"), indent=1)
    for h in out:
        print(f"{h['patch']} hunk {h['hunk']:>2} old {h['old_start']}+{h['old_len']} "
              f"enc={h['enclosing']} -{len(h['deleted'])}/+{len(h['added'])}")
        for d in h["deleted"]:
            print(f"    - {d.strip()[:110]}")
        for p in h["added"]:
            print(f"    + {p.strip()[:110]}")
        if h["callsite_arms"]:
            print(f"    callers={h['callsite_arms']}")


if __name__ == "__main__":
    main()
