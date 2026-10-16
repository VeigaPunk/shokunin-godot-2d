#!/usr/bin/env python3
"""r91-simplifier fold experiments.

Builds isolated scratch projects from the byte-exact 77d2f7e fixture and runs
the nav_lattice arms in the battery's exact launch shape, then compares
observable receipts (stdout/stderr/rc) with declared diagnostic tails masked.

Variants
  control  : committed nav_lattice.gd (sha 088843399...)
  foldA    : control minus `const SETTLE := 10`            (dead const, -1 line)
  foldB    : foldA + teardown arms' append-only `hits` sink removed (-2 lines)
  stale    : foldA with SYNC_BOUND := 1 (force gate exhaustion -> loud STALE)

Usage: python3 fold_experiments.py [--only control,foldA,...]
Writes receipts under runs-fold/<variant>/<arm>.rep<N>.{out,err,rc} and a
comparison receipt on stdout.
"""
import argparse
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FIX = HERE / "committed-fixtures"
WORK = HERE / "fold-scratch"
OUT = HERE / "runs-fold"
GODOT = "godot"

ARMS = ["census", "sync", "path", "query", "region", "agent", "avoid", "bake",
        "link", "teardown_crash", "teardown_clean"]

TAIL_FIELDS = ["settle", "settle_a", "settle_b", "iter", "ladder", "first_reach",
               "first_reach_sync", "walk_steps", "reached_at", "first_reachable",
               "iter_b", "link_iter", "gate", "chg_iter_same",
               "chg_iter_settled", "dis_same", "fwd_disabled_same", "seq_a",
               "seq_b", "vel_a", "vel_b", "sum_max"]
MASK_RE = [(f, re.compile(r"(?<![a-z_])%s=\S*" % re.escape(f))) for f in TAIL_FIELDS]


def mask(line):
    for _, rx in MASK_RE:
        line = rx.sub("", line)
    return re.sub(r"\s+", " ", line).strip()


# A deleted line shifts every later source line number, and Godot's unpinned
# GDScript backtrace frames carry `nav_lattice.gd:<line>`. Normalise those
# frames (they are not pinned by any signature, expected_errors entry or
# required_stderr fragment) so the comparison isolates semantics.
BACKTRACE_RE = re.compile(r"nav_lattice\.gd:\d+")


def norm(s):
    return BACKTRACE_RE.sub("nav_lattice.gd:<LINE>", s)


def build_projects():
    src = REPO / "corpus" / "fixtures"
    base = (FIX / "nav_lattice.gd").read_text()
    assert "const SETTLE := 10\n" in base
    foldA = base.replace("const SETTLE := 10\n", "", 1)

    foldB = foldA
    old_crash = """\tvar hits: Array[Vector2] = []
\tNavigationServer2D.agent_set_map(a, map)
\tNavigationServer2D.agent_set_avoidance_enabled(a, true)
\tNavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
\t\thits.append(v))
"""
    new_crash = """\tNavigationServer2D.agent_set_map(a, map)
\tNavigationServer2D.agent_set_avoidance_enabled(a, true)
\tNavigationServer2D.agent_set_avoidance_callback(a, func(_v: Vector2) -> void:
\t\tpass)
"""
    assert foldB.count(old_crash) == 2, foldB.count(old_crash)
    foldB = foldB.replace(old_crash, new_crash)

    stale = foldA.replace("const SYNC_BOUND := 48", "const SYNC_BOUND := 1", 1)
    assert stale != foldA

    variants = {"control": base, "foldA": foldA, "foldB": foldB, "stale": stale}
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    for name, text in variants.items():
        proj = WORK / name
        shutil.copytree(src, proj, ignore=shutil.ignore_patterns(
            "run_battery.py", "__pycache__", ".godot", "*.pyc"))
        (proj / "nav_lattice.gd").write_text(text)
        print("%-8s nav_lattice.gd sha256=%s lines=%d" % (
            name, hashlib.sha256(text.encode()).hexdigest(), text.count("\n") + 1))
    return variants


def run_arm(variant, arm, rep, timeout=25):
    proj = WORK / variant
    cmd = [GODOT, "--headless", "--path", str(proj), "--script",
           "res://nav_lattice.gd", "--", "--arm=" + arm]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        so, se, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as exc:
        so = (exc.stdout or "") if isinstance(exc.stdout, str) else (exc.stdout or b"").decode()
        se = (exc.stderr or "") if isinstance(exc.stderr, str) else (exc.stderr or b"").decode()
        rc = "TIMEOUT"
    d = OUT / variant
    d.mkdir(parents=True, exist_ok=True)
    (d / ("%s.rep%d.out" % (arm, rep))).write_text(so)
    (d / ("%s.rep%d.err" % (arm, rep))).write_text(se)
    (d / ("%s.rep%d.rc" % (arm, rep))).write_text(str(rc) + "\n")
    return so, se, rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="control,foldA,foldB,stale")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--out", default="runs-fold")
    args = ap.parse_args()
    only = args.only.split(",")
    arms = args.arms.split(",")
    global OUT
    OUT = HERE / args.out

    print("== r91-simplifier fold experiments ==")
    variants = build_projects()
    OUT.mkdir(parents=True, exist_ok=True)

    print("\n-- launch matrix (battery shape: godot --headless --path <proj> "
          "--script res://nav_lattice.gd -- --arm=<a>) --")
    for v in only:
        for arm in arms:
            for rep in range(1, args.reps + 1):
                so, se, rc = run_arm(v, arm, rep)
                first = (so.strip().splitlines() or ["<no stdout>"])[0]
                print("  %-8s %-16s rep%d rc=%-4s stdout[:60]=%r stderr_lines=%d" % (
                    v, arm, rep, rc, first[:60], len(se.splitlines())))
                sys.stdout.flush()

    print("\n-- observable comparison vs control (declared tails masked) --")
    mismatches = 0
    raw_identical = 0
    for arm in arms:
        for rep in range(1, args.reps + 1):
            base_out = (OUT / "control" / ("%s.rep%d.out" % (arm, rep))).read_text()
            base_err = (OUT / "control" / ("%s.rep%d.err" % (arm, rep))).read_text()
            base_rc = (OUT / "control" / ("%s.rep%d.rc" % (arm, rep))).read_text().strip()
            for v in only:
                if v == "control":
                    continue
                p = OUT / v
                if not (p / ("%s.rep%d.out" % (arm, rep))).exists():
                    continue
                o = (p / ("%s.rep%d.out" % (arm, rep))).read_text()
                e = (p / ("%s.rep%d.err" % (arm, rep))).read_text()
                rc = (p / ("%s.rep%d.rc" % (arm, rep))).read_text().strip()
                if (o, e, rc) == (base_out, base_err, base_rc):
                    raw_identical += 1
                # tail masking drops the tail values; compare what remains
                same_out = mask(base_out) == mask(o)
                # stderr: the glibc abort line's trailing (!prev) is unpinned,
                # and backtrace line numbers shift with any deleted line
                def errkey(s):
                    return [norm(ln) for ln in s.splitlines() if "double free" not in ln]
                same_err = errkey(base_err) == errkey(e)
                same_rc = base_rc == rc
                tag = "IDENTICAL" if (same_out and same_err and same_rc) else "DIFF"
                if tag == "DIFF":
                    mismatches += 1
                    print("  %-8s %-16s rep%d %s (out=%s err=%s rc=%s)" % (
                        v, arm, rep, tag, same_out, same_err, same_rc))
                    if not same_out:
                        print("      control: %s" % mask(base_out)[:160])
                        print("      variant: %s" % mask(o)[:160])
                    if not same_err:
                        print("      ctl.err: %r" % base_err[:160])
                        print("      var.err: %r" % e[:160])
                    if not same_rc:
                        print("      rc %s -> %s" % (base_rc, rc))
    print("\nMISMATCHES=%d  raw-byte-identical receipts=%d" % (mismatches, raw_identical))

    if "stale" in only:
        print("\n-- stale variant invariants (fold 2: loud failure, never a "
              "PASS-shaped payload off an unsynced map) --")
        for arm in arms:
            for rep in range(1, args.reps + 1):
                f = OUT / "stale" / ("%s.rep%d.out" % (arm, rep))
                if not f.exists():
                    continue
                o = f.read_text()
                rc = (OUT / "stale" / ("%s.rep%d.rc" % (arm, rep))).read_text().strip()
                has_stale = "STALE nav_lattice %s " % arm in o
                has_pass = "PASS nav_lattice" in o
                print("  %-16s rep%d rc=%-3s stale_line=%-5s pass_line=%-5s" % (
                    arm, rep, rc, has_stale, has_pass))
    print("== end fold experiments ==")


if __name__ == "__main__":
    main()
