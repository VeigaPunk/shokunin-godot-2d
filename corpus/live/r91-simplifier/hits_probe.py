#!/usr/bin/env python3
"""r91-simplifier side-probe: does the avoidance callback BODY ever execute in
the two teardown arms?

The two teardown arms register a live avoidance callback and never read the
`hits` array it appends to. If the callback never fires inside the arm's
3-frame window, the append is unreachable in practice as well as unread
(write-only), which is what makes it a YAGNI candidate.

Scratch-only: a diagnostic print is added to a COPY of the committed fixture
(committed-fixtures/nav_lattice.gd, sha 088843399...) — no tracked file is
touched. 2 reps per arm, battery launch shape.
"""
import hashlib
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WORK = HERE / "fold-scratch" / "hitsprobe"
OUT = HERE / "runs-fold-teardown"

base = (HERE / "committed-fixtures" / "nav_lattice.gd").read_text()
t = base.replace(
    "\tprint(\"NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=\",\n"
    "\t\tNavigationServer2D.agent_has_avoidance_callback(a))\n",
    "\tprint(\"R91S_HITS_CRASH \", hits.size())\n"
    "\tprint(\"NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=\",\n"
    "\t\tNavigationServer2D.agent_has_avoidance_callback(a))\n", 1)
assert "R91S_HITS_CRASH" in t
t = t.replace(
    "\tNavigationServer2D.agent_set_avoidance_callback(a, Callable())\n"
    "\tawait _await_frames(1)\n"
    "\tNavigationServer2D.free_rid(a)\n",
    "\tprint(\"R91S_HITS_CLEAN \", hits.size())\n"
    "\tNavigationServer2D.agent_set_avoidance_callback(a, Callable())\n"
    "\tawait _await_frames(1)\n"
    "\tNavigationServer2D.free_rid(a)\n", 1)
assert "R91S_HITS_CLEAN" in t

src = REPO / "corpus" / "fixtures"
if WORK.exists():
    shutil.rmtree(WORK)
shutil.copytree(src, WORK, ignore=shutil.ignore_patterns(
    "run_battery.py", "__pycache__", ".godot", "*.pyc", "tilemap_lattice.gd"))
(WORK / "nav_lattice.gd").write_text(t)
print("scratch probe sha256=%s lines=%d (committed base sha256=%s)" % (
    hashlib.sha256(t.encode()).hexdigest(), t.count("\n") + 1,
    hashlib.sha256(base.encode()).hexdigest()))

for arm in ["teardown_crash", "teardown_clean"]:
    for rep in (1, 2):
        p = subprocess.run(["godot", "--headless", "--path", str(WORK),
                            "--script", "res://nav_lattice.gd", "--",
                            "--arm=" + arm], capture_output=True, text=True, timeout=25)
        d = OUT / "hitsprobe"
        d.mkdir(parents=True, exist_ok=True)
        (d / ("%s.rep%d.out" % (arm, rep))).write_text(p.stdout)
        (d / ("%s.rep%d.err" % (arm, rep))).write_text(p.stderr)
        (d / ("%s.rep%d.rc" % (arm, rep))).write_text(str(p.returncode) + "\n")
        hits = [l for l in p.stdout.splitlines() if l.startswith("R91S_HITS")]
        print("  %-16s rep%d rc=%-3s %s" % (arm, rep, p.returncode, hits))
