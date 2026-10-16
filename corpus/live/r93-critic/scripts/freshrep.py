#!/usr/bin/env python3
"""r93-critic: 3 correctly-named fresh reps per r93 arm + byte-comparison against the
committed author fresh-reps (corpus/live/r93-author/fresh-reps).

Receipts: corpus/live/r93-critic/runs/freshrep/<script>.<arm>.rep<N>.{out,err,rc}
Output  : corpus/live/r93-critic/author_compare.json
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SEAT = Path(__file__).resolve().parent.parent
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"
AUTHOR = SEAT.parent / "r93-author" / "fresh-reps"
GODOT = "/usr/bin/godot"
REPS = 3
BOUND = 25


def main():
    rows = json.loads((SEAT / "scripts" / "r93_rows.json").read_text())
    arms = sorted({(r[1], r[2][0]) for r in rows})
    proj = SEAT / "proj-freshrep"
    if proj.exists():
        shutil.rmtree(proj)
    shutil.copytree(FROZEN, proj)
    out = {}
    same = diff = nocounter = 0
    for script, flag in arms:
        arm = flag.split("=")[1]
        recs = []
        for rep in range(1, REPS + 1):
            base = SEAT / "runs" / "freshrep" / f"{script}.{arm}.rep{rep}"
            base.parent.mkdir(parents=True, exist_ok=True)
            cmd = [GODOT, "--headless", "--path", str(proj), "--script", f"res://{script}", "--", flag]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=BOUND)
            base.with_name(base.name + ".out").write_text(p.stdout)
            base.with_name(base.name + ".err").write_text(p.stderr)
            base.with_name(base.name + ".rc").write_text(str(p.returncode) + "\n")
            recs.append(p.stdout)
            a = AUTHOR / f"{script}.{arm}.rep{rep}.out"
            if not a.exists():
                nocounter += 1
                continue
            if a.read_bytes() == p.stdout.encode():
                same += 1
            else:
                diff += 1
                out.setdefault("diffs", []).append(f"{script}.{arm}.rep{rep}")
        out[f"{script}:{arm}"] = {"uniq_out": len(set(recs)),
                                  "rc": [int((SEAT / 'runs' / 'freshrep' / f'{script}.{arm}.rep{n}.rc').read_text().strip()) for n in range(1, REPS + 1)],
                                  "stderr_bytes": [(SEAT / 'runs' / 'freshrep' / f'{script}.{arm}.rep{n}.err').stat().st_size for n in range(1, REPS + 1)]}
        print(f"{script}:{arm:16s} uniq={out[f'{script}:{arm}']['uniq_out']} "
              f"stderr={out[f'{script}:{arm}']['stderr_bytes']} rc={out[f'{script}:{arm}']['rc']}")
    out["_compare"] = {"byte_equal_to_author": same, "differing": diff, "no_author_counterpart": nocounter}
    (SEAT / "author_compare.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"# vs committed author fresh-reps: byte-equal {same}, differing {diff}, no counterpart {nocounter}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
