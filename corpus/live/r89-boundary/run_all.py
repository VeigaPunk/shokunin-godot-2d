#!/usr/bin/env python3
"""r89-boundary driver.

Every Godot launch is `timeout -s KILL 25 godot --headless --path proj --script res://<probe> -- <flags>`.
Subcommands:
  edges  [--reps N]   run every b89_edge.gd sub in an isolated fresh process
  bridge [--reps N]   run the b89_bridge.gd race arms (with/without 16 `yes` hogs)
  rows   [--reps N]   re-run the 20 claimed-verbatim r89-scout rows under 16 `yes` hogs
  all                 edges rep1 -> bridge -> rows
Receipts land in runs/ as <tag>.repN.{out,err,rc}.
"""
import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SEAT = Path(__file__).resolve().parent
RUNS = SEAT / "runs"
PROJ = SEAT / "proj"
GODOT = os.environ.get("GODOT", "godot")
BOUND = "25"
HOGS = 16


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def launch(script, flags, tag, rep, timeout=BOUND):
    cmd = ["timeout", "-s", "KILL", timeout, GODOT, "--headless", "--path", str(PROJ),
           "--script", f"res://{script}", "--", *flags]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    wall = round(time.time() - t0, 3)
    RUNS.mkdir(exist_ok=True)
    (RUNS / f"{tag}.rep{rep}.out").write_text(p.stdout)
    (RUNS / f"{tag}.rep{rep}.err").write_text(p.stderr)
    (RUNS / f"{tag}.rep{rep}.rc").write_text(f"{p.returncode}\n")
    (RUNS / f"{tag}.rep{rep}.wall").write_text(f"{wall}\n")
    return p.returncode, p.stdout, p.stderr, wall


class Hogs:
    def __init__(self, n=HOGS):
        self.n = n
        self.procs = []

    def __enter__(self):
        for _ in range(self.n):
            self.procs.append(subprocess.Popen(["yes"], stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL))
        time.sleep(1.0)
        return self

    def __exit__(self, *exc):
        for p in self.procs:
            p.kill()
        for p in self.procs:
            p.wait()
        return False


EDGE_SUBS = [
    "sanity",
    "bool_empty_empty", "bool_empty_left", "bool_collinear_clip", "bool_collinear_merge",
    "bool_dup_clip", "bool_bow_merge", "bool_bow_inter", "bool_bow_excl", "bool_bow_bow",
    "bool_bow_rev", "bool_star5_clip",
    "bool_huge_1e6", "bool_huge_1e9", "bool_huge_1e10", "bool_huge_1e12", "bool_huge_1e15",
    "bool_huge_1e18", "bool_huge_3e38", "bool_scale_ladder",
    "bool_tiny_1e6", "bool_tiny_1e20", "bool_denorm", "bool_mixed_scale",
    "bool_nan_clip", "bool_nan_merge", "bool_nan_inter", "bool_nan_excl", "bool_nan_both",
    "bool_inf_clip", "bool_negzero",
    "tri_empty", "tri_star5", "tri_nan", "tri_inf", "tri_huge_1e9", "tri_tiny_1e20",
    "tri_dup_all", "tri_zero_area_4", "tri_eps_col",
    "hull_empty", "hull_dup_all", "hull_nan", "hull_inf", "hull_huge", "hull_tiny", "hull_star5",
    "dec_empty", "dec_bow", "dec_nan", "dec_huge",
    "off_nan_delta", "off_inf_delta", "off_neginf_delta", "off_huge_delta", "off_mega_neg",
    "off_nan_poly", "off_inf_poly", "off_huge_poly", "off_huge_poly_miter", "off_tiny_poly",
    "off_negzero_delta", "off_denorm_delta", "off_exact_boundary", "off_just_beyond",
    "off_delta_ladder",
    "line_1pt", "line_2pt", "line_2pt_dup", "line_col", "line_col_rev", "line_dup4",
    "line_nan", "line_inf", "line_huge", "line_tiny", "line_selfint", "line_star5",
    "line_delta_nan", "line_delta_inf", "line_delta_zero", "line_delta_huge",
    "line_closed2", "line_closed3", "line_rev", "line_empty_reverify",
    "atlas_zero", "atlas_neg", "atlas_huge", "atlas_nan", "atlas_inf", "atlas_many",
    "atlas_zero_plus_real", "atlas_frac",
    "pred_nan", "pred_inf", "pred_huge", "pred_tiny", "isect_nan", "closest_nan",
    "bresenham_nan", "sic_nan", "sic_huge",
]

BRIDGE_PLAN = [
    # (tag, arm, frames, delay, reps, load)
    ("bridge_verbatim_noload", "verbatim", 60, 0, 8, False),
    ("bridge_verbatim_load", "verbatim", 60, 0, 8, True),
    ("bridge_f59_load", "verbatim", 59, 0, 4, True),
    ("bridge_f61_load", "verbatim", 61, 0, 4, True),
    ("bridge_sync_noload", "sync", 60, 0, 6, False),
    ("bridge_sync_load", "sync", 60, 0, 6, True),
    ("bridge_delay200_load", "delay200", 60, 200, 8, True),
    ("bridge_delay500_load", "delay500", 60, 500, 4, True),
    ("bridge_hold_load", "hold", 60, 0, 4, True),
    ("bridge_traj_noload", "traj", 120, 0, 2, False),
    ("ring_traj_noload", "ringtraj", 90, 0, 2, False),
    ("ring_sync_load", "ringsync", 60, 0, 6, True),
    ("ring_verbatim_load", "ringtraj", 60, 0, 6, True),
]


def parse_rows():
    text = (SEAT.parent / "r89-scout" / "author-rows.py.txt").read_text()
    pat = re.compile(r"\('([^']+)',\s*'([^']+)',\s*\[([^\]]*)\],\s*(-?\d+),\s*'([^']*)'\)", re.S)
    rows = []
    for m in pat.finditer(text):
        name, script, flags, rc, sig = m.groups()
        flags = [f.strip().strip("'") for f in flags.split(",") if f.strip()]
        rows.append((name, script, flags, int(rc), sig))
    return rows


def cmd_edges(args):
    subs = EDGE_SUBS
    for sub in subs:
        for rep in range(args.start_rep, args.reps + 1):
            rc, out, err, wall = launch("b89_edge.gd", [f"--sub={sub}"], f"edge_{sub}", rep)
            tail = out.strip().splitlines()[-1] if out.strip() else ""
            print(f"edge {sub} rep{rep} rc={rc} wall={wall} last={tail[:110]}", flush=True)
            if err.strip():
                print(f"    stderr[{len(err)}B]: {err.strip().splitlines()[0][:130]}", flush=True)


def cmd_bridge(args):
    for tag, arm, frames, delay, reps, load in BRIDGE_PLAN:
        hogs = Hogs() if load else None
        if hogs:
            hogs.__enter__()
        try:
            for rep in range(1, reps + 1):
                flags = [f"--arm={arm}", f"--frames={frames}"]
                if delay:
                    flags.append(f"--delay={delay}")
                rc, out, err, wall = launch("b89_bridge.gd", flags, tag, rep)
                first = next((l for l in out.splitlines() if " first=" in l), "")
                rest = next((l for l in out.splitlines() if " rest=" in l or " rest60=" in l
                             or " drop_center=" in l), "")
                print(f"{tag} rep{rep} rc={rc} wall={wall} {first[:70]} | {rest[:100]}", flush=True)
        finally:
            if hogs:
                hogs.__exit__()


def cmd_rows(args):
    rows = parse_rows()
    print(f"parsed rows={len(rows)}")
    with Hogs():
        for name, script, flags, exp_rc, sig in rows:
            ok, uniq, rcs, lines = 0, set(), [], []
            for rep in range(1, args.reps + 1):
                rc, out, err, wall = launch(script, flags, f"row_{name}", rep)
                rcs.append(rc)
                present = sig in out
                ok += 1 if present else 0
                pass_line = next((l for l in out.splitlines() if l.startswith("PASS ") or
                                  l.startswith("R89 lineempty")), "")
                lines.append(pass_line)
                uniq.add(pass_line)
                print(f"row {name} rep{rep} rc={rc} wall={wall} sig={'Y' if present else 'N'} "
                      f"pass={pass_line[:90]}", flush=True)
            print(f"== row {name}: sig_hits={ok}/{args.reps} rc={sorted(set(rcs))} uniq={len(uniq)}",
                  flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["edges", "bridge", "rows", "all"])
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--start-rep", type=int, default=1)
    args = ap.parse_args()
    RUNS.mkdir(exist_ok=True)
    (RUNS / "load.txt").write_text(sh(["uptime"]).stdout)
    if args.cmd in ("edges", "all"):
        cmd_edges(args)
    if args.cmd in ("bridge", "all"):
        cmd_bridge(args)
    if args.cmd in ("rows", "all"):
        cmd_rows(args)


if __name__ == "__main__":
    main()
