#!/usr/bin/env python3
"""r102-D2 ad-hoc counterfactuals: 8-rep old-arm block + paired 0.75-vs-1.2 bounds.

Reproduces the section 6/9 numbers of reports/round-102/r102-D2.md.
Run: python3 reports/round-102/mutations/d2_timeout_extras.py [block|paired|both]
Writes /var/tmp/r102-D2/out/old_arm_dist.json and paired_bounds.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d2_timeout_replay as m  # noqa: E402

PROJ = "/var/tmp/r102-D2/proj"
OUT = Path("/var/tmp/r102-D2/out")


def block(n=8):
    res = []
    for i in range(n):
        r = m.bounded_run("godot", PROJ, f"old_rep_{i}", ["--delay-clean"], 0.75)
        t = m.timed_run("godot", PROJ, "boot_marker.gd")
        res.append({"i": i, "marker": r["marker_observed"], "elapsed": r["elapsed_seconds"],
                    "pre_len": len(r.get("pre_timeout_stdout") or ""),
                    "post_len": len(r.get("post_drain_stdout") or ""),
                    "cleanup_exit": r.get("cleanup_exit_code"),
                    "boot_marker_t": t["boot_marker_t"], "banner_t": t["first_byte_t"]})
    (OUT / "old_arm_dist.json").write_text(json.dumps(res, indent=2) + "\n")
    return res


def paired(n=6, low=0.75, high=1.2):
    res = []
    for i in range(n):
        a = m.bounded_run("godot", PROJ, f"pair075_{i}", ["--delay-clean"], low)
        b = m.bounded_run("godot", PROJ, f"pair120_{i}", ["--delay-clean"], high)
        res.append({"i": i, "b075_marker": a["marker_observed"], "b075_elapsed": a["elapsed_seconds"],
                    "b120_marker": b["marker_observed"], "b120_elapsed": b["elapsed_seconds"],
                    "b120_timed_out": b["timed_out"], "b120_inner": b["inner_classification"]})
    (OUT / "paired_bounds.json").write_text(json.dumps(res, indent=2) + "\n")
    return res


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("block", "both"):
        print(json.dumps(block(), indent=1))
    if which in ("paired", "both"):
        print(json.dumps(paired(), indent=1))
