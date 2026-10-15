#!/usr/bin/env python3
"""r69 simplifier: delete-and-recompute on the MEASURED gapladder artifact.

Replays the landed verdict+discrimination logic (run_battery.py
--probe-midlineforge-gapladder block) against a real emitted artifact with
candidate cells removed, answering "which cells are load-bearing" with
measured data instead of a rerun. The artifact carries elapsed/pids, so
inter-run byte-identity is impossible by construction; the operative
equivalence is verdict + discriminations + surviving cell outcomes.

Usage: cell_delete_sim.py <midlineforge-gapladder-verdicts.json>
"""
import json, sys

d = json.load(open(sys.argv[1]))
midline_error = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"


def verdict_and_disc(cells):
    landed = [c["gap_ms"] for c in cells if c["outcome"] == "fabricated"]
    missed = [c["gap_ms"] for c in cells if c["outcome"] == "missed"]
    mixed = [c["gap_ms"] for c in cells if c["outcome"] == "mixed"]
    inside = [c["gap_ms"] for c in cells if c["write_inside_gap"]]
    outside = [c for c in cells if not c["write_inside_gap"]]
    cross = [c for c in cells if c["offset_ms"] > 198]
    cross_fab = all(c["outcome"] == "fabricated" for c in cross)
    cross_miss = all(c["outcome"] == "missed" for c in cross)
    reps = [r for c in cells for r in c["reps"]]
    if (sorted(landed) == sorted(inside)
            and (not cross or cross_fab)):
        v = "gap_relative"
    elif cross_miss and all(
            c["outcome"] == "fabricated" for c in cells
            if c["offset_ms"] <= 198 and c["write_inside_gap"]):
        v = "absolute_edge"
    elif (not mixed and not missed
          and len(landed) == len(cells)):
        v = "absolute_write_latency"
    else:
        v = "unclassified"
    disc = {
        "clean_exit0": all(
            r["actual_exit"] == 0 and r["error"] is None
            and not r["timed_out"] for r in reps),
        "all_reject": all(
            r["inner_classification"] is False for r in reps),
        "fab_iff_sig_destroyed": all(
            r["fabrication_landed"] == (not r["signature_observed"])
            for r in reps),
        "spliced_line_fusion": all(
            r["spliced_line"] is None
            or (r["spliced_line"].startswith(
                    "DESCENDANT_PIPE_PROBE: expected ")
                and midline_error in r["spliced_line"])
            for r in reps),
        "gap200_anchor": (
            [c["outcome"] for c in cells if c["gap_ms"] == 200]
            == ["fabricated"]),
        "sub_off_never_fab": all(
            c["outcome"] == "missed" for c in outside),
        "sub_off_sig_intact": all(
            r["signature_observed"] for c in outside for r in c["reps"]),
        "super_off_always_fab": all(
            c["outcome"] == "fabricated" for c in cells
            if c["write_inside_gap"]),
        "super_off_pre_death": all(
            r["write_pre_death"] for c in cells
            if c["write_inside_gap"] for r in c["reps"]),
        "referent_gap_relative": v == "gap_relative",
        "crossed_refute_abs_edge": cross_fab,
        "crossed_elapsed_tracks": all(
            r["elapsed_seconds"] is not None
            and r["elapsed_seconds"] > c["gap_ms"] / 2000.0
            for c in cross for r in c["reps"]),
    }
    return v, disc


cells = d["gapladder"]
v0, d0 = verdict_and_disc(cells)
print(f"FULL ({len(cells)} cells): verdict={v0} "
      f"all_disc={all(d0.values())}")

for drop in [(80, 400), (300, 800), (80, 50), (80, 100), (80, 200),
             (80, 800), (300, 400), (600, 800)]:
    sub = [c for c in cells
           if (c["offset_ms"], c["gap_ms"]) != drop]
    v, dd = verdict_and_disc(sub)
    broken = [k for k in dd if d0[k] and not dd[k]]
    changed = [k for k in dd if dd[k] != d0[k]]
    print(f"drop {str(drop):>9}: verdict={v:<12} "
          f"all_disc={all(dd.values())} "
          f"{'FLIP/FAIL: '+str(changed) if changed else 'stable'}")
