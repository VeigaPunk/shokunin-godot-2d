#!/usr/bin/env python3
"""r94-simplifier YAGNI candidate fold — T0 + start3 dead stores (−3 lines).

Builds the folded fixture (`fold-candidates/particles_lattice.gd`) by deleting
the three provably unread store sites found by the scope-aware scan
(`var T0 := 0` + `T0 = Time.get_ticks_usec()` + `var start3: int = PH`),
writes the exact unified diff (`fold-proposal.diff`), and proves byte-neutrality
by running all 19 r94 arms x N reps on BOTH the committed and the folded bytes
in the battery's exact launch shape, comparing stdout/stderr/rc raw.

Usage: python3 fold_candidates.py [--reps 3]
Outputs: fold-proposal.diff, fold-candidates/**, fold-candidates-verification.json
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"
FIXTURE = HERE / "committed-fixtures" / "particles_lattice.gd"
FOLD_DIR = HERE / "fold-candidates"
PROJ = HERE / "proj"
GODOT = "godot"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def launch(proj, arm, timeout=8):
    cmd = [GODOT, "--headless", "--path", str(proj),
           "--script", "res://particles_lattice.gd", "--", "--arm=" + arm]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return out, err, None, "TIMEOUT"
    except OSError as exc:
        return "", str(exc), None, "OSError"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    args = ap.parse_args()

    src = FIXTURE.read_text().splitlines(keepends=True)
    keep = []
    removed = []
    for i, l in enumerate(src, 1):
        if i in (53, 723, 739):
            removed.append((i, l.rstrip("\n")))
            continue
        keep.append(l)
    folded_text = "".join(keep)
    (HERE / "fold-proposal.diff").write_text(
        "--- a/corpus/fixtures/particles_lattice.gd\n"
        "+++ b/corpus/fixtures/particles_lattice.gd\n"
        "@@ dead stores: T0 (file scope) and start3 (_arm_gpu_headless) @@\n"
        + "".join("-%s\n" % r[1] for r in removed)
        + "@@ fold-candidates/run_battery.py @@\n"
        + "-# Probe particles_lattice.gd sha256 %s\n" % sha256(FIXTURE)
        + "+# Probe particles_lattice.gd sha256 %s\n" % hashlib.sha256(
            folded_text.encode()).hexdigest())

    if FOLD_DIR.exists():
        shutil.rmtree(FOLD_DIR)
    FOLD_DIR.mkdir(parents=True)
    for item in sorted(PROJ.iterdir()):
        if item.is_dir():
            shutil.copytree(item, FOLD_DIR / item.name)
        else:
            shutil.copy2(item, FOLD_DIR / item.name)
    (FOLD_DIR / "particles_lattice.gd").write_text(folded_text)
    hsrc = HARNESS.read_text()
    hfold = hsrc.replace(
        "# Probe particles_lattice.gd sha256 %s" % sha256(FIXTURE),
        "# Probe particles_lattice.gd sha256 %s" % hashlib.sha256(folded_text.encode()).hexdigest(), 1)
    assert hfold != hsrc, "harness comment anchor not found"
    (FOLD_DIR / "run_battery.py").write_text(hfold)
    print("committed fixture sha: %s" % sha256(FIXTURE))
    print("folded fixture sha:    %s" % hashlib.sha256(folded_text.encode()).hexdigest())
    for ln, text in removed:
        print("removed line %d: %s" % (ln, text))

    # scratch projects
    scratch_c = FOLD_DIR.parent / "fold-runs" / STAMP / "scratch-committed"
    scratch_f = FOLD_DIR.parent / "fold-runs" / STAMP / "scratch-folded"
    for dest, fix in ((scratch_c, FIXTURE), (scratch_f, FOLD_DIR / "particles_lattice.gd")):
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(PROJ, dest)
        shutil.copy2(fix, dest / "particles_lattice.gd")
        pf = dest / "project.godot"
        pf.write_text(pf.read_text().replace(
            'config/name="MechanicOneShotTest"',
            'config/name="MechanicOneShotTest-%s"' % dest.name, 1))

    arms = []
    for l in (HERE / "committed-fixtures" / "run_battery.py").read_text().splitlines():
        m = re.match(r"\s*\('r94_particles_(\w+)', 'particles_lattice\.gd', \['--arm=(\w+)'\]", l)
        if m:
            arms.append(m.group(1))

    results = {}
    for arm in arms:
        rows = []
        for rep in range(1, args.reps + 1):
            oc, ec, rc_c, terr_c = launch(scratch_c, arm)
            of, ef, rc_f, terr_f = launch(scratch_f, arm)
            rows.append({
                "rep": rep,
                "committed": {"rc": rc_c, "err": terr_c, "stdout_sha": hashlib.sha256(oc.encode()).hexdigest(),
                              "stderr_sha": hashlib.sha256(ec.encode()).hexdigest(), "stdout_bytes": len(oc),
                              "stdout": oc, "stderr": ec},
                "folded": {"rc": rc_f, "err": terr_f, "stdout_sha": hashlib.sha256(of.encode()).hexdigest(),
                           "stderr_sha": hashlib.sha256(ef.encode()).hexdigest(), "stdout_bytes": len(of),
                           "stdout": of, "stderr": ef},
                "raw_identical": (oc == of and ec == ef and rc_c == rc_f and terr_c == terr_f),
            })
        results[arm] = rows
        ident = all(r["raw_identical"] for r in rows)
        print("  %-16s reps=%d raw_identical=%s" % (arm, args.reps, ident))

    n = sum(len(v) for v in results.values())
    bad = [(a, r["rep"]) for a, v in results.items() for r in v if not r["raw_identical"]]
    out = {"stamp": STAMP, "reps": args.reps, "pairs": n,
           "mismatches": bad, "per_arm": results,
           "committed_sha256": sha256(FIXTURE),
           "folded_sha256": hashlib.sha256(folded_text.encode()).hexdigest(),
           "removed_lines": [{"line": ln, "text": t} for ln, t in removed]}
    (HERE / "fold-candidates-verification.json").write_text(json.dumps(out, indent=1))
    print("pairs=%d mismatches=%d" % (n, len(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
