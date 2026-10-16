#!/usr/bin/env python3
"""Per-arm summary of the fold comparison receipts (tails masked)."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / (sys.argv[1] if len(sys.argv) > 1 else "runs-fold-main")
ARMS = ["census", "sync", "path", "query", "region", "agent", "avoid", "bake",
        "link", "teardown_crash", "teardown_clean"]
TAIL = ["settle_a", "settle_b", "settle", "iter", "ladder", "first_reach_sync",
        "first_reach", "walk_steps", "reached_at", "first_reachable", "iter_b",
        "link_iter", "gate", "chg_iter_same", "chg_iter_settled", "dis_same",
        "fwd_disabled_same", "seq_a", "seq_b", "vel_a", "vel_b", "sum_max"]
MASK = [(f, re.compile(r"(?<![a-z_])%s=\S*" % re.escape(f))) for f in TAIL]
BACKTRACE = re.compile(r"nav_lattice\.gd:\d+")

def mask(line):
    for _, rx in MASK:
        line = rx.sub("", line)
    return re.sub(r"\s+", " ", line).strip()

variants = sorted(p.name for p in OUT.iterdir() if p.is_dir() and p.name != "control")
print("== per-arm fold comparison vs control (receipts in %s) ==" % OUT.name)
print("%-17s %-9s %-11s %-11s %s" % ("arm", "variant", "raw-ident", "masked-ident", "notes"))
for arm in ARMS:
    for v in variants:
        reps = sorted((OUT / "control").glob("%s.rep*.out" % arm))
        raw = masked = 0
        note = []
        for f in reps:
            n = f.name
            if not (OUT / v / n).exists():
                continue
            a_out = f.read_text()
            a_err = (OUT / "control" / n.replace(".out", ".err")).read_text()
            a_rc = (OUT / "control" / n.replace(".out", ".rc")).read_text().strip()
            b_out = (OUT / v / n).read_text()
            b_err = (OUT / v / n.replace(".out", ".err")).read_text()
            b_rc = (OUT / v / n.replace(".out", ".rc")).read_text().strip()
            if (a_out, a_err, a_rc) == (b_out, b_err, b_rc):
                raw += 1
            same_out = mask(a_out) == mask(b_out)
            same_err = [BACKTRACE.sub("L", l) for l in a_err.splitlines()] == \
                       [BACKTRACE.sub("L", l) for l in b_err.splitlines()]
            if same_out and same_err and a_rc == b_rc:
                masked += 1
            if a_out != b_out:
                note.append("stdout differs (tail only)")
            if a_err != b_err:
                note.append("stderr backtrace line numbers")
        print("%-17s %-9s %-11s %-11s %s" % (
            arm, v, "%d/%d" % (raw, len(reps)), "%d/%d" % (masked, len(reps)),
            "; ".join(sorted(set(note))) or "-"))
