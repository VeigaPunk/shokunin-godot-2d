#!/usr/bin/env python3
"""r102-S2: deadness census per deleted line (scene_io) + token-residue census
for stree def deletions. Text-only (no execution)."""
import json
import re

BASE = "/var/tmp/r102-S2/base/corpus/fixtures"
FOLD = "/var/tmp/r102-S2/foldedsrc"


def enclosing_func(lines, ln):
    name = None
    for i, l in enumerate(lines[:ln], 1):
        m = re.match(r"^func (\w+)", l)
        if m:
            name = m.group(1)
    return name


def func_span(lines, ln):
    start = 1
    for i, l in enumerate(lines[:ln], 1):
        if re.match(r"^func ", l):
            start = i
    end = len(lines)
    for i, l in enumerate(lines[ln:], ln + 1):
        if re.match(r"^func ", l):
            end = i - 1
            break
    return start, end


def is_read(line, name):
    if re.match(r"^\s*(var\s+)?%s\s*(:?=)" % re.escape(name), line):
        return False  # assignment target
    return re.search(r"\b%s\b" % re.escape(name), line) is not None


out = {"scene_io": [], "stree_residue": {}, "stree_old_counts": {}}

# --- scene_io: line-by-line, from armmap hunks
old = open(f"{BASE}/scene_io_lattice.gd").read().splitlines()
armmap = json.load(open("/var/tmp/r102-S2/armmap.json"))
for h in [x for x in armmap if x["patch"] == "scene_io"]:
    # locate each deleted line inside the old-file hunk window
    searches = list(h["deleted"])
    for dl in h["deleted"]:
        ln = None
        for i in range(h["old_start"] - 1, h["old_start"] - 1 + h["old_len"]):
            if old[i] == dl and (i + 1) not in [r.get("line") for r in out["scene_io"]]:
                ln = i + 1
                break
        if ln is None:
            out["scene_io"].append({"hunk": h["hunk"], "deleted": dl, "line": None})
            continue
        m = re.match(r"^\s*var\s+(\w+)\s*:=", dl) or re.match(r"^\s*([\w.]+)\s*=\s*null", dl)
        name = m.group(1) if m else None
        fname = enclosing_func(old, ln)
        fstart, fend = func_span(old, ln)
        reads_after = reads_before = 0
        if name:
            for i in range(fstart, fend + 1):
                if i == ln:
                    continue
                if is_read(old[i - 1], name):
                    if i > ln:
                        reads_after += 1
                    else:
                        reads_before += 1
        out["scene_io"].append({
            "hunk": h["hunk"], "line": ln, "deleted": dl, "var": name,
            "func": fname, "func_span": [fstart, fend],
            "reads_before": reads_before, "reads_after": reads_after})

# --- stree: token residue in folded bytes + old occurrence counts
fold = open(f"{FOLD}/stree_lattice.gd").read()
oldf = open(f"{BASE}/stree_lattice.gd").read()
for tok in ["it_valid", "it_connected", "it_paused", "_tree_names"]:
    out["stree_residue"][tok] = len(re.findall(r"\b%s\b" % tok, fold))
    out["stree_old_counts"][tok] = len(re.findall(r"\b%s\b" % tok, oldf))

json.dump(out, open("/var/tmp/r102-S2/liveness.json", "w"), indent=1)
print("== scene_io deleted-line census ==")
for r in out["scene_io"]:
    print(f"  h{r['hunk']} L{r['line']}: {r['deleted'].strip()!r} var={r['var']} "
          f"func={r['func']} reads_before={r['reads_before']} reads_after={r['reads_after']}")
print("== stree token residue (folded) ==")
for tok, n in out["stree_residue"].items():
    print(f"  {tok}: old={out['stree_old_counts'][tok]} folded={n}")
