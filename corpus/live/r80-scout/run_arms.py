#!/usr/bin/env python3
"""r80-scout scratch runner.

Runs each proposed Godot-2D cell arm in exactly the tracked battery's launch
shape (`godot --headless --path <scratch> --script res://phys2d_motion.gd --
--arm=<name>`, 8 s bound, merged stdout+stderr) and classifies every rep with the
*production* `classify_process` predicate extracted verbatim from
`corpus/fixtures/run_battery.py` (never a re-implementation).

Modes:
  --mode discover   print the measured PASS line for each arm (no pins needed)
  --mode verify     run every arm x reps against the frozen PINS literals below
                    and ablate each row (signature dropped, exit flipped, error
                    whitelist dropped) to prove the pins are load-bearing

Scratch only: writes under corpus/live/r80-scout/.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BATTERY = REPO / "corpus" / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
PROBE = "res://phys2d_motion.gd"
TIMEOUT = 8  # the battery's own bound for non-export scripts

# Frozen pins: literal signature lines transcribed from --discover receipts,
# then re-measured here. expected_errors are the exact `ERROR:` lines the
# production classifier must be allowed to see.
PINS = {
    "ccd_ladder": (0, "PASS phys2d_motion ccd_ladder vels=[600.0, 1150.0, 1200.0, 2000.0, 2400.0, 3000.0, 3600.0] entries=17 d_cross=[0, 0, 0, 0, 1, 0, 1] d_x=[90.3, 90.3, 90.3, 90.3, 1169.494, 90.3, 1754.241] d_vx=[0.0, 0.0, 0.0, 0.0, 2282.856, 0.0, 3424.283] d_ccd=0 r_cross=[0, 0, 0, 0, 0, 0, 0] r_x=[90.16, 90.16, 90.16, 90.16, 90.16, 90.16, 90.16] r_vx=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] r_ccd=1 s_cross=[0, 0, 0, 0, 1, 0, 1] s_x=[90.3, 90.3, 90.3, 90.3, 1169.494, 90.3, 1754.241] s_vx=[0.0, 0.0, 0.0, 0.0, 2282.856, 0.0, 3424.283] s_ccd=2", ()),
    "ccd_gap": (0, "PASS phys2d_motion ccd_gap v=2400 box16x16 gap12 d_cross=1 d_hit=0 d_x=1169.494 r_cross=0 r_hit=2 r_x=90.157 s_cross=1 s_hit=0 s_x=1169.494", ()),
    "ccd_spin": (0, "PASS phys2d_motion ccd_spin w=90deg_per_step bar8x128 wall20x4@(40,+40) d_hit=0 d_rot=308.05 d_ccd=0 r_hit=0 r_rot=308.05 r_ccd=1 s_hit=0 s_rot=308.05 s_ccd=2 endposes=[308.05, 308.05, 308.05] endpose_overlap=[1, 1, 1]", ()),
    "ccd_edge": (0, "PASS phys2d_motion ccd_edge v=2400 circle8@y14 wall4x10@[0,10] d_cross=1 d_hit=0 d_pos=(1169.4938,814.0000) r_cross=1 r_hit=0 r_pos=(1169.4938,1614.0000) s_cross=1 s_hit=0 s_pos=(1169.4938,2414.0000)", ()),
    "btm_from": (0, "PASS phys2d_motion btm_from body@(0,1000) wall@200 no_from[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] with_from[hit=false travel=(400.0000,0.0000) rem=(0.0000,0.0000)] bodypos=(0.0000,1000.0000)", ()),
    "btm_hit": (0, "PASS phys2d_motion btm_hit hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(0.0000,0.0000)", ()),
    "btm_embed": (0, "PASS phys2d_motion btm_embed rec_off[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] rec_on[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] rec_on_sepray[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] away_off[hit=true travel=(-6.9633,0.0000) rem=(-50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] away_on[hit=true travel=(-6.9633,0.0000) rem=(-50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D]", ()),
    "btm_margin": (0, "PASS phys2d_motion btm_margin m0.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m0.08[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m1.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m4.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=4.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D]", ()),
    "btm_from2": (0, "PASS phys2d_motion btm_from2 n1[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] n2[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] srv_tele[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] ident_from[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] with_from3600[hit=false travel=(400.0000,0.0000) rem=(0.0000,0.0000)] b1pos=(0.0000,3000.0000) b3pos=(0.0000,0.0000)", ()),
    "btm_recflag": (0, "PASS phys2d_motion btm_recflag zero_off[hit=true travel=(-6.9633,0.0000) rem=(0.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] zero_on[hit=true travel=(-6.9633,0.0000) rem=(0.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] tiny_off[hit=true travel=(-6.9633,0.0000) rem=(0.0100,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] tiny_on[hit=true travel=(-6.9633,0.0000) rem=(0.0100,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D]", ()),
    "mac_hit": (0, "PASS phys2d_motion mac_hit travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(87.5000,0.0000)", ()),
    "mac_miss": (0, "PASS phys2d_motion mac_miss col=null bodypos=(60.0000,0.0000)", ()),
    "tm_hit": (0, "PASS phys2d_motion tm_hit ret=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(0.0000,0.0000)", ()),
    "mac_test_only": (0, "PASS phys2d_motion mac_test_only col1=travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos_after_test=(0.0000,0.0000) srv_after_test=(0.0000,0.0000) col2=hit pos_after_real=(87.5000,0.0000)", ()),
    "mac_nodecomp": (0, "PASS phys2d_motion mac_nodecomp travel=(87.5000,-87.5000) rem=(112.5000,-112.5000) pos=(98.0000,-88.2812) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(87.5000,-87.5000)", ()),
    "mac_chain": (0, "PASS phys2d_motion mac_chain h0[t=(87.5000,-87.5000) r=(112.5000,-112.5000) n=(-1.0000,0.0000) pos=(87.5000,-87.5000)] h1[t=(0.0000,-10.3271) r=(0.0000,-102.1729) n=(0.0000,1.0000) pos=(87.5000,-97.8271)] n2=null pos=(87.5014,-97.8271)", ()),
    "mac_maxcol": (0, "PASS phys2d_motion mac_maxcol callv5=null bodypos=(0.0000,0.0000)",
     ("ERROR: Error calling method from 'callv': 'CharacterBody2D::move_and_collide': Method expected 4 argument(s), but called with 5.",)),
    "mac_rigid": (0, "PASS phys2d_motion mac_rigid col=null pos_now=(60.0000,0.0000) pos_late=(60.0000,0.0000) srv_late=(60.0000,0.0000) hitcol=travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,900.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D hpos_now=(87.5000,900.0000) hpos_late=(87.5000,900.0000) hsrv_late=(87.5000,900.0000)", ()),
    "mac_embed": (0, "PASS phys2d_motion mac_embed rec_off[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,0.0000)] rec_on[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,600.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,600.0000)] prop5_argdefault[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,1200.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,1200.0000)]", ()),
    "dss_motion": (0, "PASS phys2d_motion dss_motion cm=[0.44921875, 0.453125] cm_away=[1.0, 1.0] cm_zero=[1.0, 1.0] cs_n=2 is_n=1 ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(98.0000,0.0000) n=(-1.0000,0.0000) lv=(0.0000,0.0000) cls=null} ri_zero={}", ()),
    "dss_embed": (0, "PASS phys2d_motion dss_embed cm_toward=[1.0, 1.0] cm_away=[1.0, 1.0] cs_n=2 cs_pts=[(88.0, 0.0), (102.0, 0.0)] is_n=1 ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(102.0000,0.0000) n=(1.0000,0.0000) lv=(0.0000,0.0000) cls=null}", ()),
    "dss_shapes": (0, "PASS phys2d_motion dss_shapes ray_hit={keys=[\"collider\", \"collider_id\", \"normal\", \"position\", \"rid\", \"shape\"] cls=StaticBody2D pos=(98.0000,0.0000) n=(-1.0000,0.0000)} ray_miss={} ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(303.9900,-8.0000) n=(0.0000,-1.0000) lv=(119.6003,0.0000) cls=null} is_n=1 is0={keys=[\"collider\", \"collider_id\", \"rid\", \"shape\"] cls=RigidBody2D} cs_full=2 cs_cap1=2", ()),
    "dss_purity": (0, "PASS phys2d_motion dss_purity equal=true before=[[X: (0.955337, 0.29552), Y: (-0.29552, 0.955337), O: (5.0, 7.0)], (150.0, -40.0), 0.5, 4294967295, true, false, []] after=[[X: (0.955337, 0.29552), Y: (-0.29552, 0.955337), O: (5.0, 7.0)], (150.0, -40.0), 0.5, 4294967295, true, false, []]", ()),
    "dss_wrongarg": (0, "PASS phys2d_motion dss_wrongarg is=0 cm=[] ri={  } cs=0 is_null=0 ray_null={  } pt_null=0",
     ('ERROR: Required object "rp_shape_query" is null.',
      'ERROR: Required object "rp_ray_query" is null.',
      'ERROR: Required object "rp_point_query" is null.')),
    "cont_windows": (0, "PASS phys2d_motion cont_windows entry_f=4 exit_f=6 in_cb=[2, 1] pp_entry=[2, 1] proc_entry=[2, 1] in_exit_cb=[0, 1] pp_exit=[0, 0] proc_exit=[0, 0]", ()),
    "cont_cap": (0, "PASS phys2d_motion cont_cap capped=[count=1 arr=1] uncapped=[count=4 arr=2 cls=StaticBody2D,StaticBody2D]", ()),
    "bds_windows": (0, "PASS phys2d_motion bds_windows oop=obj cnt=0 in_cb={ \"obj\": true, \"count\": 2 } in_phase=obj cnt=2 proc=obj cnt=2 integ_first={ \"count\": 0, \"lv\": (0.0, 65.33334) } integ_last={ \"count\": 2, \"lv\": (0.0383, -0.006104) }", ()),
    "cont_persist": (0, "PASS phys2d_motion cont_persist entry_f=4 exit_f=5 seq[frame,size]=[[5, 1], [6, 0], [7, 0], [8, 0], [9, 0], [10, 0], [11, 0]]", ()),
}

ARMS = [
    "ccd_ladder",
    "ccd_gap",
    "ccd_spin",
    "ccd_edge",
    "btm_from",
    "btm_hit",
    "btm_embed",
    "btm_margin",
    "btm_from2",
    "btm_recflag",
    "mac_hit",
    "mac_miss",
    "tm_hit",
    "mac_test_only",
    "mac_nodecomp",
    "mac_chain",
    "mac_maxcol",
    "mac_rigid",
    "mac_embed",
    "dss_motion",
    "dss_embed",
    "dss_shapes",
    "dss_purity",
    "dss_wrongarg",
    "cont_windows",
    "cont_cap",
    "bds_windows",
    "cont_persist",
]


def production_classifier():
    """Extract classify_process verbatim from the tracked battery and exec it."""
    lines = BATTERY.read_text().splitlines()
    start = next(i for i, line in enumerate(lines)
                 if line.strip().startswith("def classify_process("))
    end = start + 1
    while end < len(lines) and not lines[end].startswith("    def "):
        end += 1
    block = textwrap.dedent("\n".join(lines[start:end]))
    namespace = {"re": re}
    exec(block, namespace)
    return (namespace["classify_process"],
            hashlib.sha256(block.encode()).hexdigest(), (start + 1, end))


def run_arm(arm, proj=PROJ):
    command = ["godot", "--headless", "--path", str(proj),
               "--script", PROBE, "--", "--arm=" + arm]
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=TIMEOUT)
        return {"arm": arm, "rc": proc.returncode, "stdout": proc.stdout,
                "stderr": proc.stderr, "timeout": None, "command": command}
    except subprocess.TimeoutExpired as exc:
        return {"arm": arm, "rc": None, "stdout": (exc.stdout or ""), "stderr": (exc.stderr or ""),
                "timeout": f"TIMEOUT after {TIMEOUT} seconds", "command": command}


def pass_line(receipt):
    for line in (receipt["stdout"] + receipt["stderr"]).splitlines():
        if line.startswith("PASS phys2d_motion"):
            return line
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["discover", "verify"], default="verify")
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--arms", default="")
    parser.add_argument("--proj", default="proj")
    args = parser.parse_args()
    proj = HERE / args.proj

    classify, classifier_sha, classifier_lines = production_classifier()
    arms = [a for a in (args.arms.split(",") if args.arms else ARMS) if a]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = {"stamp": stamp, "mode": args.mode, "reps": args.reps, "project": args.proj,
           "godot": subprocess.run(["godot", "--version"], capture_output=True, text=True).stdout.strip(),
           "classifier_source": {"file": str(BATTERY.relative_to(REPO)),
                                 "lines": list(classifier_lines),
                                 "sha256": classifier_sha},
           "probe": str((PROJ / "phys2d_motion.gd").relative_to(REPO)),
           "probe_sha256": hashlib.sha256((PROJ / "phys2d_motion.gd").read_bytes()).hexdigest(),
           "rows": [], "discover": {}}
    print(f"classifier classify_process from {BATTERY.relative_to(REPO)} "
          f"lines {classifier_lines[0]}-{classifier_lines[1]} sha256={classifier_sha[:16]}")

    if args.mode == "discover":
        for arm in arms:
            receipt = run_arm(arm, proj)
            line = pass_line(receipt)
            out["discover"][arm] = {"line": line, "rc": receipt["rc"],
                                    "stderr_lines": [l for l in receipt["stderr"].splitlines() if "ERROR:" in l],
                                    "stdout": receipt["stdout"], "stderr": receipt["stderr"]}
            print(f"--- {arm} rc={receipt['rc']}")
            for l in receipt["stderr"].splitlines():
                if "ERROR:" in l:
                    print(f"    ERR {l}")
            print(f"    {line}")
    else:
        for arm in arms:
            if arm not in PINS:
                print(f"SKIP {arm}: no frozen pin")
                continue
            expected_exit, signature, expected_errors = PINS[arm]
            reps = []
            for rep in range(args.reps):
                receipt = run_arm(arm, proj)
                merged = receipt["stdout"] + receipt["stderr"]
                verdict = classify(receipt["rc"], receipt["timeout"], merged,
                                   expected_exit, signature, expected_errors)
                reps.append({"rep": rep, "rc": receipt["rc"], "verdict": "PASS" if verdict else "FAIL",
                             "stdout": receipt["stdout"], "stderr": receipt["stderr"],
                             "engine_anchors": sorted({l.strip() for l in receipt["stderr"].splitlines()
                                                       if l.strip().startswith("at:")}),
                             "merged_sha256": hashlib.sha256(merged.encode()).hexdigest()})
            stable = len({(r["stdout"], r["stderr"]) for r in reps}) == 1
            first = reps[0]
            merged = first["stdout"] + first["stderr"]
            ablate = {}
            ablate["signature_dropped"] = classify(first["rc"], None, merged, expected_exit,
                                                   "PASS phys2d_motion __absent__", expected_errors)
            ablate["exit_flipped"] = classify(first["rc"], None, merged,
                                              1 if expected_exit == 0 else 0, signature, expected_errors)
            ablate["errors_dropped"] = classify(first["rc"], None, merged, expected_exit,
                                                signature, ())
            ablate["clean"] = classify(first["rc"], None, merged, expected_exit, signature, expected_errors)
            row = {"arm": arm, "expected_exit": expected_exit, "signature": signature,
                   "expected_errors": list(expected_errors),
                   "rc": [r["rc"] for r in reps], "verdicts": [r["verdict"] for r in reps],
                   "stable_bytes": stable, "measured_line": pass_line({"stdout": first["stdout"], "stderr": first["stderr"]}),
                   "ablations": ablate, "reps": reps,
                   "stderr_error_lines": sorted({l.strip() for l in first["stderr"].splitlines() if "ERROR:" in l})}
            out["rows"].append(row)
            flag = "OK " if all(v == "PASS" for v in row["verdicts"]) and stable else "BAD"
            print(f"{flag} {arm} rc={row['rc']} verdicts={row['verdicts']} stable={stable} "
                  f"ablate(sig={ablate['signature_dropped']},exit={ablate['exit_flipped']},"
                  f"err={ablate['errors_dropped']})")
        bad = [r["arm"] for r in out["rows"]
               if not all(v == "PASS" for v in r["verdicts"]) or not r["stable_bytes"]]
        out["verdict"] = "PASS" if not bad else "FAIL"
        out["bad"] = bad

    (HERE / f"arms-{args.mode}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote corpus/live/r80-scout/arms-{args.mode}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
