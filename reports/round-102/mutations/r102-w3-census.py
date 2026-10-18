#!/usr/bin/env python3
"""r102-w3 census: byte/line/hunk census of the r101 simplifier patch queue.

Reads the committed patch shards (reports/round-101/mutations/r101-simp*),
parses every unified-diff hunk for gross -/+ line and byte counts, then applies
the union of the queue to a scratch extraction of HEAD (git archive) and
measures real before->after file sizes, line counts and sha256s.
Also censuses the stale `.shokunin/game-dev-2d/corpus/` citations.

Read-only w.r.t. the repo. Scratch: /var/tmp/r102-w3/tree. REPO never edited.
"""
import hashlib
import os
import re
import subprocess

REPO = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
MUT = os.path.join(REPO, "reports/round-101/mutations")
SCR = "/var/tmp/r102-w3"
TREE = os.path.join(SCR, "tree")

PATCHES = [
    ("simp1 r91  nav_lattice",     f"{MUT}/r101-simp1-r91-nav_lattice.patch"),
    ("simp1 r98  canvas_lattice",  f"{MUT}/r101-simp1-r98-canvas_lattice.patch"),
    ("simp1 r98  r98b_attack",     f"{MUT}/r101-simp1-r98-r98b_attack.patch"),
    ("simp1 r98  r98b_rksenum",    f"{MUT}/r101-simp1-r98-r98b_rksenum.patch"),
    ("simp1 r99  audio_lattice",   f"{MUT}/r101-simp1-r99-audio_lattice.patch"),
    ("simp2 r97  stree_lattice",   f"{MUT}/r101-simp2-stree_lattice.gd.diff"),
    ("simp2 r96  scene_io_lattice",f"{MUT}/r101-simp2-scene_io_lattice.gd.diff"),
    ("simp3 r94  particles_lattice", f"{MUT}/r101-simp3-particles-fold.patch"),
    ("simp3 r95  dss+r95b_order",  f"{MUT}/r101-simp3-r95-fold.patch"),
]
HARNESS = ("simp3 r95  harness comment run_battery.py", f"{MUT}/r101-simp3-r95-harness-comment.patch")

# folded shas recorded by the originating shards (prefix match)
RECORDED_FOLDED = {
    "corpus/fixtures/nav_lattice.gd": "b23887e5",
    "corpus/fixtures/canvas_lattice.gd": "8bfddb74",
    "corpus/fixtures/r98b_attack.gd": "7021e53c",
    "corpus/fixtures/r98b_rksenum.gd": "5d7e3aab",
    "corpus/fixtures/audio_lattice.gd": "91161bf5",
    "corpus/fixtures/stree_lattice.gd": "4c457f887d933760f0ce446d68fda935a561689995f356384d7b3520e754314e",
    "corpus/fixtures/scene_io_lattice.gd": "18bc06da6c4d5ca6c261051f9ee56eb4b0de0b4f60ba33a764a1ddae184fff50",
    "corpus/fixtures/particles_lattice.gd": "afd2aa88",
    "corpus/fixtures/dss_lattice.gd": "c128e9cc",
    "corpus/fixtures/r95b_order.gd": "b367559e",
}
RECORDED_BASE = {  # base shas quoted by the shards (prefix match)
    "corpus/fixtures/nav_lattice.gd": "088843399",
    "corpus/fixtures/stree_lattice.gd": "61954f87",
    "corpus/fixtures/scene_io_lattice.gd": "8aeab1cb",
    "corpus/fixtures/particles_lattice.gd": "0701e813",
    "corpus/fixtures/dss_lattice.gd": "77ae4adb",
    "corpus/fixtures/r95b_order.gd": "4f7e945e",
}

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, check=True).stdout

def parse_patch(path):
    """Return per-file sections: path, hunks, rem/add lines, rem/add bytes."""
    files = []
    cur = None
    hunk = None
    with open(path, "rb") as f:
        for raw in f:
            if raw.startswith(b"diff --git"):
                continue
            if raw.startswith(b"--- "):
                old = raw[4:].strip()
                cur = {"old": old, "hunks": [], "rem_lines": 0, "add_lines": 0,
                       "rem_bytes": 0, "add_bytes": 0}
                files.append(cur)
                hunk = None
            elif raw.startswith(b"+++ "):
                new = raw[4:].strip()
                cur["new"] = new
                cur["file"] = new.split(b"/", 1)[1].decode() if b"/" in new else new.decode()
            elif raw.startswith(b"@@"):
                hunk = {"rem": 0, "add": 0, "remb": 0, "addb": 0}
                cur["hunks"].append(hunk)
            elif raw.startswith(b"-") and not raw.startswith(b"---"):
                if hunk is not None:
                    hunk["rem"] += 1
                    hunk["remb"] += len(raw) - 1
                    cur["rem_lines"] += 1
                    cur["rem_bytes"] += len(raw) - 1
            elif raw.startswith(b"+") and not raw.startswith(b"+++"):
                if hunk is not None:
                    hunk["add"] += 1
                    hunk["addb"] += len(raw) - 1
                    cur["add_lines"] += 1
                    cur["add_bytes"] += len(raw) - 1
    return files

def wc_lines(b):
    return b.count(b"\n") + (0 if (not b or b.endswith(b"\n")) else 1)

print("=" * 78)
print("A. PATCH-TEXT CENSUS (gross -/+ lines and bytes per patch, per file)")
print("=" * 78)
tot = {"hunks": 0, "rem_lines": 0, "add_lines": 0, "rem_bytes": 0, "add_bytes": 0}
all_sections = {}
for label, p in PATCHES + [HARNESS]:
    blob = open(p, "rb").read()
    secs = parse_patch(p)
    print(f"\n-- {label}  [{os.path.basename(p)}]")
    print(f"   patch sha256={sha256(blob)[:16]}  size={len(blob)}B")
    for s in secs:
        tgt = s["file"]
        print(f"   {tgt}: hunks={len(s['hunks'])}  -{s['rem_lines']} lines/{s['rem_bytes']}B"
              f"  +{s['add_lines']} lines/{s['add_bytes']}B  net={s['add_lines']-s['rem_lines']:+d} lines,"
              f" {s['add_bytes']-s['rem_bytes']:+d}B")
        if label.startswith("simp3 r95  harness"):
            continue
        all_sections.setdefault(tgt, []).append((label, s))
        tot["hunks"] += len(s["hunks"])
        for k in ("rem_lines", "add_lines", "rem_bytes", "add_bytes"):
            tot[k] += s[k]

print("\n-- TOTALS, 10 fixture files, printed per file (sum of all sections):")
grand = {"hunks": 0, "reml": 0, "addl": 0, "remb": 0, "addb": 0}
for tgt, secs in all_sections.items():
    hunks = sum(len(s["hunks"]) for _, s in secs)
    reml = sum(s["rem_lines"] for _, s in secs)
    addl = sum(s["add_lines"] for _, s in secs)
    remb = sum(s["rem_bytes"] for _, s in secs)
    addb = sum(s["add_bytes"] for _, s in secs)
    grand["hunks"] += hunks
    grand["reml"] += reml
    grand["addl"] += addl
    grand["remb"] += remb
    grand["addb"] += addb
    print(f"   {tgt}: hunks={hunks} -{reml}/+{addl} lines  -{remb}/+{addb}B"
          f"  net {addl-reml:+d} lines {addb-remb:+d}B")
print(f"\n   QUEUE TOTAL (fixtures): hunks={grand['hunks']}  "
      f"gross removed=-{grand['reml']} lines/-{grand['remb']}B  "
      f"gross added=+{grand['addl']} lines/+{grand['addb']}B  "
      f"NET={grand['addl']-grand['reml']:+d} lines, {grand['addb']-grand['remb']:+d}B")

print()
print("=" * 78)
print("B. ACTUAL APPLICATION on scratch HEAD extraction (git archive) + measurement")
print("=" * 78)
os.makedirs(SCR, exist_ok=True)
subprocess.run(f"rm -rf {TREE} && mkdir -p {TREE} && git -C {REPO} archive HEAD corpus/fixtures | tar -x -C {TREE}",
               shell=True, check=True)

targets = list(RECORDED_FOLDED.keys())
before = {}
for rel in targets:
    b = open(os.path.join(TREE, rel), "rb").read()
    before[rel] = b
    tag = ""
    if rel in RECORDED_BASE:
        tag = " base-sha-match=" + ("YES" if sha256(b).startswith(RECORDED_BASE[rel]) else "NO!")
    print(f"BEFORE {rel}: {len(b)}B  {wc_lines(b)} lines  sha={sha256(b)[:16]}{tag}")

for label, p in PATCHES:
    r = subprocess.run(["patch", "-p1", "-d", TREE, "-i", p], capture_output=True, text=True)
    print(f"\nAPPLY {label}: rc={r.returncode}")
    print("  " + r.stdout.strip().replace("\n", "\n  "))

harness_path = os.path.join(TREE, "corpus/fixtures/run_battery.py")
hb_before = open(harness_path, "rb").read()
r = subprocess.run(["patch", "-p1", "-d", TREE, "-i", HARNESS[1]], capture_output=True, text=True)
hb_after = open(harness_path, "rb").read()
print(f"\nAPPLY {HARNESS[0]}: rc={r.returncode}  before={len(hb_before)}B after={len(hb_after)}B "
      f"delta={len(hb_after)-len(hb_before):+d}B  lines {wc_lines(hb_before)}->{wc_lines(hb_after)}")

print("\n-- AFTER (patched scratch tree) per file:")
ftot = {"db": 0, "dl": 0}
for rel in targets:
    a = open(os.path.join(TREE, rel), "rb").read()
    b = before[rel]
    ok = "MATCH" if sha256(a).startswith(RECORDED_FOLDED[rel]) else "NO-MATCH!"
    ftot["db"] += len(a) - len(b)
    ftot["dl"] += wc_lines(a) - wc_lines(b)
    print(f"AFTER {rel}: {len(a)}B  {wc_lines(a)} lines  sha={sha256(a)}")
    print(f"   delta: {len(a)-len(b):+d}B  {wc_lines(a)-wc_lines(b):+d} lines   recorded-folded={ok}")
print(f"\n   FILE-TRUTH TOTAL: byte delta = {ftot['db']:+d}B   line delta = {ftot['dl']:+d} lines")
print(f"   PATCH-TEXT TOTAL: byte delta = {grand['addb']-grand['remb']:+d}B   "
      f"line delta = {grand['addl']-grand['reml']:+d} lines   (must agree)")

print()
print("=" * 78)
print("C. STALE `.shokunin/game-dev-2d/` CITATION CENSUS (HEAD bytes)")
print("=" * 78)
NEEDLE = b".shokunin/game-dev-2d/"
NEEDLE_FULL = b".shokunin/game-dev-2d/corpus/"
saving_per = len(NEEDLE_FULL) - len(b"corpus/")
for rel in ["SCORECARD.md", "PROVINCE.md", "LOG.md", "README.md", "SHONEN.md",
            "corpus/README.md"]:
    try:
        c = git("show", f"HEAD:{rel}")
    except subprocess.CalledProcessError:
        print(f"{rel}: absent")
        continue
    n_all = c.count(NEEDLE)
    n_full = c.count(NEEDLE_FULL)
    n_prefix_only = n_all - n_full  # occurrences not followed by corpus/
    t = c.replace(NEEDLE_FULL, b"corpus/")
    print(f"{rel}: occ(.shokunin/game-dev-2d/)={n_all}  occ(...corpus/)={n_full} "
          f" bare-prefix={n_prefix_only}  stripped-bytes={len(c)}->{len(t)} ({len(t)-len(c):+d}B)")

ls = subprocess.run(["git", "-C", REPO, "grep", "-I", "-o", "-F",
                     ".shokunin/game-dev-2d/corpus/", "HEAD", "--", "corpus/lessons"],
                    capture_output=True, text=True).stdout.splitlines()
files = {ln.split(":", 2)[1] for ln in ls if ln.strip()}
print(f"corpus/lessons/: files={len(files)} occurrences={len(ls)} "
      f"mechanical-strip={-saving_per*len(ls):+d}B (policy call, historical receipts)")

sc = git("show", "HEAD:SCORECARD.md").decode().splitlines()
print("\nSCORECARD.md current lines 8-10 (1-based):")
for i in (7, 8, 9):
    print(f"  {i+1}: {sc[i]}")
pv = git("show", "HEAD:PROVINCE.md").decode().splitlines()
print("PROVINCE.md line 6:")
print(f"  6: {pv[5]}")
