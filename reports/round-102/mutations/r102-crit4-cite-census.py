#!/usr/bin/env python3
"""r102 C4 — citation census (read-only).

Extracts `path:line` citations from r101 receipts and r102 shards, and reports
per-file counts + current-content checks for run_battery.py citations.

Usage: python3 r102-crit4-cite-census.py <repo_root>
Outputs plain text to stdout. Never executes run_battery.py; never writes repo files.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CITE = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_./+-]*\.(?:py|gd|md|cfg|tscn)):(\d+)")
FOLD_SET = {
    "nav_lattice.gd": "simp1/simp3 -3",
    "canvas_lattice.gd": "simp1 -10",
    "r98b_attack.gd": "simp1 -4",
    "r98b_rksenum.gd": "simp1 -3",
    "audio_lattice.gd": "simp1 -2",
    "stree_lattice.gd": "simp2 -17",
    "scene_io_lattice.gd": "simp2 -12",
    "particles_lattice.gd": "simp3 -3",
    "dss_lattice.gd": "simp3 -5",
    "r95b_order.gd": "simp3 -5",
    "r100b_seq.gd": "r100 handoff -5 (patch not in mutations/)",
}


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    per_scope: dict[str, Counter] = {}
    for scope in ("reports/round-101", "reports/round-102"):
        hits: Counter = Counter()
        for md in sorted((root / scope).glob("*.md")):
            text = md.read_text(errors="replace")
            for m in CITE.finditer(text):
                hits[(m.group(1), m.group(2))] += 1
        per_scope[scope] = hits
        print(f"## {scope}: {len(hits)} distinct (file,line) citations, {sum(hits.values())} occurrences")
        byfile: Counter = Counter()
        for (f, _), n in hits.items():
            byfile[f] += 1
        for f, n in byfile.most_common():
            print(f"   {n:4d} distinct lines  {f}")

    rb = root / "corpus/fixtures/run_battery.py"
    lines = rb.read_text(errors="replace").splitlines()
    cited_rb = set()
    for hits in per_scope.values():
        for (f, l) in hits:
            if f.endswith("run_battery.py"):
                cited_rb.add(int(l))
    print(f"\n## run_battery.py cited lines (total file {len(lines)} lines, sha in shard)")
    for l in sorted(cited_rb):
        cur = lines[l - 1].strip()[:110] if 1 <= l <= len(lines) else "<OUT OF RANGE>"
        print(f"   :{l:<5d} {cur}")

    print("\n## .gd citations for fixtures in the C3 fold set (old line numbers; post-fold line = line - deletions above)")
    for hits in per_scope.values():
        for (f, l) in sorted(hits, key=lambda x: (x[0], int(x[1]))):
            base = f.rsplit("/", 1)[-1]
            if base in FOLD_SET:
                print(f"   {base}:{l}  [{FOLD_SET[base]}]  cited in {sum(1 for k in hits if k==(f,l))}x")
    return 0


if __name__ == "__main__":
    sys.exit(main())
