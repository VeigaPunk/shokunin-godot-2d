#!/usr/bin/env python3
"""r104-C5 exposure census (read-only).

Re-derives every count this seat quotes in reports/round-104/r104-crit5.md from
the repo bytes themselves: tracked-artifact classes, receipt host-path exposure,
per-run PASS-line census, cross-run byte identity, and unregistered fixtures.

Never executes corpus/fixtures/run_battery.py as a program; it is parsed with
`ast` only. Run from the lane repo root:

    python3 reports/round-104/mutations/r104-C5-exposure-census.py
"""
import ast
import collections
import glob
import itertools
import json
import os
import re
import subprocess
import sys

REPO = os.getcwd()
FIX = os.path.join(REPO, "corpus", "fixtures")
HOSTPATH = re.compile(r"(/home/|/var/tmp/|/tmp/|/run/user)")


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


def sec(title):
    print("\n== " + title)


def tracked(patterns):
    out = sh("git ls-files")
    return [p for p in out.splitlines() if any(pat in p for pat in patterns)]


sec("tracked artifact classes")
allfiles = sh("git ls-files").splitlines()
print("tracked files total            :", len(allfiles))
print("tracked under .godot/          :", sum(1 for p in allfiles if "/.godot/" in p))
print("tracked uid_cache.bin          :", sum(1 for p in allfiles if p.endswith("uid_cache.bin")))
print("tracked *.uid                  :", sum(1 for p in allfiles if p.endswith(".uid")))
print("tracked *.pyc                  :", sum(1 for p in allfiles if p.endswith(".pyc")))
for p in allfiles:
    if p.endswith(".pyc"):
        print("   ", p, "-> in HEAD:",
              subprocess.run(["git", "cat-file", "-e", "HEAD:" + p],
                             capture_output=True).returncode == 0)
print("root .gitignore present        :", os.path.exists(os.path.join(REPO, ".gitignore")))
for probe in ("reports/round-102/mutations/__pycache__/x.pyc",
              "corpus/fixtures/__pycache__/x.pyc"):
    r = subprocess.run(["git", "check-ignore", "-v", probe], capture_output=True, text=True)
    print(f"check-ignore {probe:52s} rc={r.returncode} {r.stdout.strip()}")

sec("stored runs: rows, verdicts, host-path PASS lines")
runs = sorted(glob.glob(os.path.join(REPO, "corpus/live/runs/*/verdicts.json")))
print("verdicts.json count:", len(runs))
mats = {}
for f in runs:
    rid = f.split("/")[-2]
    d = json.load(open(f))
    rows = d.get("results") or []
    verd = collections.Counter(r.get("verdict") for r in rows)
    withcmd = [r for r in rows if r.get("command")]
    hostlines = 0
    ownstamp = 0
    for r in rows:
        for line in (r.get("output") or []):
            if isinstance(line, str) and line.startswith("PASS"):
                if HOSTPATH.search(line):
                    hostlines += 1
                    if rid in line:
                        ownstamp += 1
    mats[rid] = {r.get("case"): r.get("output") for r in withcmd}
    print(f"  {rid} rows={len(rows):4d} {dict(verd)} with_command={len(withcmd):3d} "
          f"hostpath_PASS={hostlines:3d} (own_run_stamp={ownstamp:3d})")

sec("PASS-prefix census (gate: line.startswith('PASS '))")
tot = 0
for rid, m in mats.items():
    for out in m.values():
        tot += sum(1 for l in out if isinstance(l, str) and l.startswith("PASS "))
print("PASS-space lines over all runs:", tot)

sec("cross-run byte identity for command-bearing rows")
for a, b in itertools.combinations(sorted(mats), 2):
    A, B = mats[a], mats[b]
    common = set(A) & set(B)
    same = sum(1 for c in common if A[c] == B[c])
    print(f"  comparable={len(common):4d} identical={same:4d}  {a} vs {b}")

sec("fixtures: registered vs on disk (CASES parsed with ast, never executed)")
tree = ast.parse(open(os.path.join(FIX, "run_battery.py")).read())
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = ast.literal_eval(node.value)
scripts = {c[1] for c in cases}
gd = []
for root, _dirs, files in os.walk(FIX):
    if any(x in root for x in (".godot", "__pycache__")):
        continue
    for x in files:
        if x.endswith(".gd"):
            gd.append(os.path.relpath(os.path.join(root, x), FIX))
unreg = sorted(set(gd) - scripts)
print("CASES rows:", len(cases), "distinct scripts:", len(scripts))
print("on-disk .gd:", len(gd), "unregistered:", len(unreg))
for u in unreg:
    print("   ", u)

sec("new r104 fixtures: hashes, PASS print sites, absolute-path leakage")
for p in sorted(glob.glob(os.path.join(FIX, "res_uid*.gd"))):
    body = open(p).read()
    sha = subprocess.run(["sha256sum", p], capture_output=True, text=True).stdout.split()[0]
    leak = [l for l in body.splitlines()
            if "PASS res_uid" in l and HOSTPATH.search(l)]
    print(f"  {os.path.basename(p):20s} {len(body.splitlines()):4d} lines sha={sha[:16]} "
          f"PASS_sites={body.count('PASS res_uid')} path_leak_lines={len(leak)}")
print("\nreminder: run_battery.py was parsed, never executed.")
