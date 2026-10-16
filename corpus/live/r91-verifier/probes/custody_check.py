#!/usr/bin/env python3
"""r91 verifier — custody checks that need no engine run.

1. committed author fresh-reps (corpus/live/r91-author/fresh-reps): rc, signature
   substring, stderr allowlist/required fragment, PASS-line count.
2. committed author battery runs (runs1/runs2) vs my loaded reps: per-case
   (signature, verdict, actual_exit) tuple compare + row-set diff.
"""
import ast
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
V = ROOT / "corpus/live/r91-verifier"
AUTHOR = ROOT / "corpus/live/r91-author"
HARNESS = V / "tree/corpus/fixtures/run_battery.py"

tree = ast.parse(HARNESS.read_text())
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
nav = {c[0]: c for c in cases if c[0].startswith("nav_lattice_")}

print("== committed fresh-reps custody ==")
bad = 0
for name, script, flags, expected_exit, sig in nav.values():
    arm = name.removeprefix("nav_lattice_")
    for rep in range(2, 5):
        out = AUTHOR / f"fresh-reps/{arm}.rep{rep}.out"
        err = AUTHOR / f"fresh-reps/{arm}.rep{rep}.err"
        rc = AUTHOR / f"fresh-reps/{arm}.rep{rep}.rc"
        if not out.exists():
            print(f"  MISSING {out}")
            bad += 1
            continue
        o, e, r = out.read_text(), err.read_text(), rc.read_text().strip()
        ok = (r == str(expected_exit)) and (sig in o)
        extra = []
        if name in ("nav_lattice_sync", "nav_lattice_bake"):
            err_lines = [l.strip() for l in e.splitlines() if l.strip()]
            error_lines = [l for l in err_lines if "ERROR:" in l]
            extra.append(f"err_nonempty={len(err_lines)} error_lines={len(error_lines)}")
            ok = ok and len(error_lines) == 1 and error_lines[0].startswith("ERROR:")
            if name == "nav_lattice_bake":
                ok = ok and any("WARNING:" in l for l in err_lines)
        if name == "nav_lattice_teardown_crash":
            ok = ok and "double free or corruption" in e
            extra.append("stderr_fragment=yes")
        if name == "nav_lattice_teardown_clean":
            ok = ok and e == ""
            extra.append(f"err_bytes={len(e)}")
        pass_lines = [l for l in o.splitlines() if l.startswith("PASS nav_lattice")]
        if arm not in ("teardown_crash",):
            ok = ok and len(pass_lines) == 1
        if not ok:
            bad += 1
        print(f"  {'OK ' if ok else 'BAD'} {arm}.rep{rep} rc={r} {' '.join(extra)}")
print(f"fresh-reps bad={bad}")

print("\n== author battery runs vs my reps (signature tuples) ==")
def load(p):
    d = json.loads(pathlib.Path(p).read_text())
    return {r["case"]: (r.get("signature"), r.get("verdict"), r.get("actual_exit"))
            for r in d["results"]}, d["verdict"]

a1, v1 = load(AUTHOR / "runs1/20261015T223815564642Z/verdicts.json")
a2, v2 = load(AUTHOR / "runs2/20261015T224213073214Z/verdicts.json")
m1, w1 = load(V / "runs/20261015T232439543775Z/verdicts.json")
m2, w2 = load(V / "runs/20261015T232914025617Z/verdicts.json")
for tag, (a, av), (m, mv) in [("author-rep1 vs mine-rep1", (a1, v1), (m1, w1)),
                              ("author-rep2 vs mine-rep2", (a2, v2), (m2, w2)),
                              ("author-rep1 vs author-rep2", (a1, v1), (a2, v2)),
                              ("mine-rep1 vs mine-rep2", (m1, w1), (m2, w2))]:
    common = set(a) & set(m)
    only_a = set(a) - set(m)
    only_m = set(m) - set(a)
    diffs = [k for k in common if a[k] != m[k]]
    print(f"  {tag}: verdicts={av}/{mv} common={len(common)} only_a={len(only_a)} "
          f"only_m={len(only_m)} tuple_mismatches={len(diffs)}")
    for k in sorted(diffs)[:8]:
        print(f"     {k}: author={a[k][1]} mine={m[k][1]}")
    for k in sorted(only_a)[:4]:
        print(f"     only author: {k}")
    for k in sorted(only_m)[:4]:
        print(f"     only mine: {k}")

print("\n== nav row payload stability across 4 battery runs ==")
for name in nav:
    vals = []
    for tag, d in [("a1", a1), ("a2", a2), ("m1", m1), ("m2", m2)]:
        vals.append((tag, d[name][0]))
    same = all(v == vals[0][1] for _, v in vals)
    print(f"  {name}: signature_identical_all4={same}")
    if not same:
        for tag, v in vals:
            print(f"     {tag}: {str(v)[:110]}")
