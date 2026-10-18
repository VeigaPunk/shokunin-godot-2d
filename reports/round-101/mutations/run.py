#!/usr/bin/env python3
"""r101 SIMP-1: run the 42 in-scope rows against base / per-candidate-fold / combined trees."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import simp1  # noqa: E402

WORK = simp1.WORK
REPS_MAIN = 2
REPS_ALL = 1


def sha(b: str) -> str:
    return hashlib.sha256(b.encode()).hexdigest()[:16]


def main():
    cases, classify_process = simp1.extract()
    expected_errors = simp1.extract_dict("expected_errors")
    required_stderr = simp1.extract_dict("required_stderr")
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rows = [c for c in cases if c[1] in simp1.FIXTURE_TREES and (only is None or c[1] == only)]

    jobs = []
    for rep in range(1, REPS_MAIN + 1):
        for row in rows:
            for tree in simp1.FIXTURE_TREES[row[1]]:
                jobs.append((row, tree, rep))
    for row in rows:  # combined trees, single rep (extra pass)
        for tree in simp1.FIXTURE_TREES[row[1]]:
            if tree in ("f_r98all", "f_all"):
                jobs.append((row, tree, REPS_MAIN + 1))

    outdir = WORK / "receipts"
    outdir.mkdir(parents=True, exist_ok=True)
    results = {}

    def work(job):
        row, tree, rep = job
        scratch = WORK / "trees" / tree
        t0 = time.time()
        stdout, stderr, rc, err = simp1.run_row(scratch, row[1], row[2])
        dur = time.time() - t0
        rec = {
            "row": row[0], "script": row[1], "flags": row[2], "tree": tree, "rep": rep,
            "rc": rc, "err": err, "dur": round(dur, 3),
            "stdout_sha": sha(stdout) if stdout is not None else None,
            "stderr_sha": sha(stderr) if stderr is not None else None,
            "stdout": stdout, "stderr": stderr,
            "verdict": simp1.classify(classify_process, row, stdout, stderr, rc, err,
                                       expected_errors, required_stderr) if stdout is not None else False,
        }
        stem = "%s.%s.rep%d" % (row[0], tree, rep)
        if stdout is not None:
            (outdir / (stem + ".stdout")).write_text(stdout)
            (outdir / (stem + ".stderr")).write_text(stderr)
            (outdir / (stem + ".rc")).write_text("%s dur=%.3f\n" % (rc, dur))
        return job, rec

    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = [pool.submit(work, j) for j in jobs]
        for f in as_completed(futs):
            job, rec = f.result()
            results["%s|%s|%d" % (rec["row"], rec["tree"], rec["rep"])] = rec
            done += 1
            if done % 20 == 0 or done == len(jobs):
                print("  %d/%d launches (%.0fs)" % (done, len(jobs), time.time() - t0), flush=True)

    (WORK / ("results.json" if not only else "results_%s.json" % only.replace(".gd", ""))).write_text(json.dumps(
        {k: {kk: vv for kk, vv in v.items() if kk not in ("stdout", "stderr")} for k, v in results.items()}, indent=1))
    print("elapsed %.1fs for %d launches; receipts in %s" % (time.time() - t0, len(jobs), outdir))


if __name__ == "__main__":
    main()
