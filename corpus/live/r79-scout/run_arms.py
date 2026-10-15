#!/usr/bin/env python3
"""r79-scout scratch runner.

Runs each proposed Godot-2D cell arm in exactly the tracked battery's launch
shape (`godot --headless --path <scratch> --script res://phys2d_events.gd --
--arm=<name>`, 8 s bound, merged stdout+stderr) and classifies every rep with the
*production* `classify_process` predicate extracted verbatim from
`corpus/fixtures/run_battery.py` (never a re-implementation).

Modes:
  --discover   print the measured PASS line for each arm (no pins needed)
  --verify     run every arm x reps against the frozen PINS literals below and
               ablate each row (signature dropped, exit flipped, error whitelist
               dropped) to prove the pins are load-bearing

Scratch only: writes under corpus/live/r79-scout/.
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
PROBE = "res://phys2d_events.gd"
TIMEOUT = 8  # the battery's own bound for non-export scripts

# Frozen pins: literal signature lines transcribed from the --discover receipts,
# then re-measured here. expected_errors are the exact `ERROR:` lines the
# production classifier must be allowed to see.
PINS = {
    "edge_srv": (0, "PASS phys2d_events edge_srv q_before=1 srv_before=(100.0, 0.0) srv_after=(200.0, 0.0) q_new=1 q_old=0 q_new_n1=1 q_old_n1=0", ()),
    "edge_node_srv": (0, "PASS phys2d_events edge_node_srv q_before=1 srv_after=(200.0, 0.0) q_new=1 q_old=0 node_prop_in_cb=(300.0, 0.0) srv_n1=(200.0, 0.0) node_prop_n1=(300.0, 0.0) q_new_n1=1 q_old_n1=0", ()),
    "edge_node": (0, "PASS phys2d_events edge_node node_prop_in_cb=(400.0, 0.0) srv_in_cb=(300.0, 0.0) q_new=0 q_old=1 srv_n1=(400.0, 0.0) q_new_n1=1 q_old_n1=0", ()),
    "edge_revert": (0, "PASS phys2d_events edge_revert q_srv_w0=1 srv_after_node_w0=(200.0, 0.0) q_srv_after_node_w0=1 q_node_after_node_w0=0 srv_n1=(400.0, 0.0) q_srv_n1=0 q_node_n1=1 node_prop_n1=(400.0, 0.0)", ()),
    "area_edge": (0, "PASS phys2d_events area_edge q_before=1 node_prop_in_cb=(100.0, 0.0) srv_in_cb=(0.0, 0.0) q_new=0 q_old=1 srv_n1=(100.0, 0.0) q_new_n1=1 q_old_n1=0 node_prop_n1=(100.0, 0.0) srv_direct_in_cb=(200.0, 0.0) q_direct=1 node_prop_direct_in_cb=(100.0, 0.0) srv_direct_n2=(200.0, 0.0) node_prop_direct_n2=(100.0, 0.0)", ()),
    "cm_on": (0, "PASS phys2d_events cm_on entered=2 exited=1 entry1_frame=1 entry2_frame=20 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 valid=true exit1_frame=7", ()),
    "cm_off": (0, "PASS phys2d_events cm_off entered=0 exited=0 entry1_frame=-1 entry2_frame=-1 cb_fired=false cb_count=- cb_colliders=- cb_monitor=- cb_max=- valid=true exit1_frame=-1", ()),
    "cm_max0": (0, "PASS phys2d_events cm_max0 entered=0 exited=0 entry1_frame=-1 entry2_frame=-1 cb_fired=false cb_count=- cb_colliders=- cb_monitor=- cb_max=- valid=true exit1_frame=-1", ()),
    "cm_toggle_cb": (0, "PASS phys2d_events cm_toggle_cb entered=2 exited=1 entry1_frame=1 entry2_frame=20 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=true post_monitor=true post_count=2 valid=true exit1_frame=7", ('ERROR: Can\'t disable contact monitoring during in/out callback. Use call_deferred("set_contact_monitor", false) instead.',)),
    "cm_deferred_cb": (0, "PASS phys2d_events cm_deferred_cb entered=1 exited=0 entry1_frame=1 entry2_frame=-1 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=true post_monitor=false valid=true exit1_frame=-1", ()),
    "cm_max0_cb": (0, "PASS phys2d_events cm_max0_cb entered=1 exited=1 entry1_frame=1 entry2_frame=-1 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=0 post_max=0 valid=true exit1_frame=1", ()),
    "rb_srv_set_state": (0, "PASS phys2d_events rb_srv_set_state entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=(500.0, 500.0) cb_node_unchanged=true cb_node_read=- cb_srv_before=- next_node=(500.0001, 501.0889) next_srv=(500.0001, 501.0889) late_node=(500.0006, 516.297) node_write_stuck=false node_follows_srv=true valid_after=true", ()),
    "rb_node_position": (0, "PASS phys2d_events rb_node_position entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=(600.0, 600.0) cb_srv_before=(0.000128, -4.56002) next_node=(0.000128, -4.672004) next_srv=(0.000128, -4.672004) late_node=(0.000128, -4.699955) node_write_stuck=false node_follows_srv=false valid_after=true", ()),
    "rb_queue_free": (0, "PASS phys2d_events rb_queue_free entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=<dead> next_srv=<dead> late_node=<dead> node_write_stuck=false node_follows_srv=false valid_after=false cb_queued=true", ()),
    "rb_free_rid": (0, "PASS phys2d_events rb_free_rid entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=(0.000128, -4.56002) next_srv=<null> late_node=(0.000128, -4.56002) node_write_stuck=false node_follows_srv=false valid_after=true cb_freed=true", ('ERROR: Parameter "body" is null.', "ERROR: Invalid ID.")),
    "rb_dss_in_cb": (0, "PASS phys2d_events rb_dss_in_cb entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=(0.000128, -4.672004) next_srv=(0.000128, -4.672004) late_node=(0.000128, -4.699955) node_write_stuck=false node_follows_srv=false valid_after=true cb_dss_null=false cb_q_hits=1", ()),
    "area_monitoring_direct": (0, "PASS phys2d_events area_monitoring_direct entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=true cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0", ('ERROR: Function blocked during in/out signal. Use set_deferred("monitoring", true/false).',)),
    "area_monitoring_deferred": (0, "PASS phys2d_events area_monitoring_deferred entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=true cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=false entries=1 exits=1", ()),
    "area_free_rid": (0, "PASS phys2d_events area_free_rid entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=true cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -2.911111) next_srv=<null> late_node=(0.0, -2.911111) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=1", ('ERROR: Parameter "body" is null.', "ERROR: Invalid ID.")),
    "area_queue_free": (0, "PASS phys2d_events area_queue_free entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=true cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=<dead> next_srv=<dead> late_node=<dead> node_write_stuck=false node_follows_srv=false valid_after=false post_monitoring=true entries=1 exits=1", ()),
    "area_srv_set_state": (0, "PASS phys2d_events area_srv_set_state entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=(0.0, -2.911111) cb_srv_read=(500.0, 500.0) cb_node_read=- next_node=(500.0, 502.176) next_srv=(500.0, 502.176) late_node=(500.0, 521.7144) node_write_stuck=false node_follows_srv=true valid_after=true post_monitoring=true entries=1 exits=1", ()),
    "area_node_position": (0, "PASS phys2d_events area_node_position entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=(600.0, 600.0) next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0", ()),
    "area_dss_in_cb": (0, "PASS phys2d_events area_dss_in_cb entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0 cb_dss_null=false cb_q_hits=1", ()),
}

ARMS = [
    "edge_srv",
    "edge_node_srv",
    "edge_node",
    "edge_revert",
    "area_edge",
    "cm_on",
    "cm_off",
    "cm_max0",
    "cm_toggle_cb",
    "cm_deferred_cb",
    "cm_max0_cb",
    "rb_srv_set_state",
    "rb_node_position",
    "rb_queue_free",
    "rb_free_rid",
    "rb_dss_in_cb",
    "area_monitoring_direct",
    "area_monitoring_deferred",
    "area_free_rid",
    "area_queue_free",
    "area_srv_set_state",
    "area_node_position",
    "area_dss_in_cb",
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
        if line.startswith("PASS phys2d_events"):
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
           "probe": str((PROJ / "phys2d_events.gd").relative_to(REPO)),
           "probe_sha256": hashlib.sha256((PROJ / "phys2d_events.gd").read_bytes()).hexdigest(),
           "rows": [], "discover": {}}
    print(f"classifier classify_process from {BATTERY.relative_to(REPO)} "
          f"lines {classifier_lines[0]}-{classifier_lines[1]} sha256={classifier_sha[:16]}")

    if args.mode == "discover":
        for arm in arms:
            receipt = run_arm(arm, proj)
            line = pass_line(receipt)
            out["discover"][arm] = {"line": line, "rc": receipt["rc"],
                                    "stderr_lines": [l for l in receipt["stderr"].splitlines() if "ERROR:" in l]}
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
            # ablations against the first measured receipt
            ablate = {}
            ablate["signature_dropped"] = classify(first["rc"], None, merged, expected_exit,
                                                   "PASS phys2d_events __absent__", expected_errors)
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
    print(f"wrote corpus/live/r79-scout/arms-{args.mode}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
