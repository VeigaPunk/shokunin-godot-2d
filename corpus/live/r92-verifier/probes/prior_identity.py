#!/usr/bin/env python3
"""r92 verifier — prior-row identity + author-run reproduction.

Compares this seat's battery run(s) against
  * the r91 green on 77d2f7e (corpus/live/r91-verifier/runs/20261016T000657222526Z)
    -> the 258 pre-existing rows must be tuple-identical; the 14 r92 rows are new
  * the r92 author's committed-worktree greens (corpus/live/r92-author/runs{4,5})
    -> full 272-row tuple identity (signature, verdict, actual_exit, error)
"""
import json
import pathlib
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r92-verifier"

def load(path):
    data = json.loads(pathlib.Path(path).read_text())
    return {r["case"]: r for r in data["results"]}

def tup(r):
    return (r.get("signature"), r.get("verdict"), r.get("actual_exit"), r.get("error"))

def compare(label, a, b):
    common = sorted(set(a) & set(b))
    mism = [c for c in common if tup(a[c]) != tup(b[c])]
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    print(f"{label}: common={len(common)} mismatches={len(mism)} "
          f"only_in_first={len(only_a)} only_in_second={len(only_b)}")
    for c in mism[:10]:
        print(f"   MISMATCH {c}\n     first ={tup(a[c])}\n     second={tup(b[c])}")
    if only_a:
        print(f"   only_in_first : {only_a[:20]}")
    if only_b:
        print(f"   only_in_second: {only_b[:20]}")
    return len(mism), only_a, only_b

mine = sys.argv[1:]
r91 = load(REPO / "corpus/live/r91-verifier/runs/20261016T000657222526Z/verdicts.json")
print(f"r91 green rows={len(r91)}")
for p in mine:
    m = load(p)
    print(f"\n=== {pathlib.Path(p).parent.name}: rows={len(m)} ===")
    print("verdict tally:", {v: sum(1 for r in m.values() if r['verdict'] == v) for v in ("PASS", "FAIL")})
    compare("vs r91 green (77d2f7e)", r91, m)
    for a in ("runs4", "runs5"):
        d = REPO / "corpus/live/r92-author" / a
        cands = sorted(d.glob("*/verdicts.json")) if d.exists() else []
        if cands:
            auth = load(cands[-1])
            print(f"\n--- vs r92 author {a}/{cands[-1].parent.name} (rows={len(auth)}) ---")
            compare(f"vs r92 author {a}", auth, m)
        else:
            print(f"(no author verdicts under {d})")
