#!/usr/bin/env python3
"""r81-scout scratch runner.

Runs each proposed Godot-2D joint/layer cell arm in exactly the tracked battery's
launch shape (`godot --headless --path <scratch> --script res://phys2d_jl.gd --
--arm=<name>`, 8 s bound, merged stdout+stderr) and classifies every rep with the
*production* `classify_process` predicate extracted verbatim from
`corpus/fixtures/run_battery.py` (never a re-implementation).

Modes:
  --mode discover   print the measured PASS line for each arm (no pins needed)
  --mode verify     run every arm x reps against the frozen PINS literals (inline
                    below, or `pins.json` beside this file when present) and
                    ablate each row (signature dropped, exit flipped, error
                    whitelist dropped) to prove the pins are load-bearing

Scratch only: writes under corpus/live/r81-scout/.
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
PROBE = "res://phys2d_jl.gd"
PROBE_NAME = "phys2d_jl"
TIMEOUT = 8  # the battery's own bound for non-export scripts

# Frozen pins: literal signature lines transcribed from --discover receipts, then
# re-measured here. expected_errors are the exact `ERROR:` lines the production
# classifier must be allowed to see. Overridden by pins.json when it exists.
PINS = {}

ARMS = [
    "joint_census",
    "joint_unset_refusal",
    "joint_pin_tiers",
    "joint_pin_clear",
    "joint_node_clear",
    "joint_freed_rid",
    "joint_node_freed_rid",
    "joint_spring_env",
    "joint_pin_params",
    "joint_node_anchor",
    "joint_groove",
    "joint_disable_coll",
    "layer_or_table",
    "layer_zero_table",
    "layer_dyn_pair",
    "layer_flip_mid",
    "layer_flip_cb",
    "area_lattice",
    "area_body_gate",
    "area_entry_order",
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
        if line.startswith("PASS " + PROBE_NAME):
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

    pins = PINS
    pins_path = HERE / "pins.json"
    if pins_path.is_file():
        pins = {k: (v["exit"], v["signature"], tuple(v["errors"]))
                for k, v in json.loads(pins_path.read_text()).items()}

    classify, classifier_sha, classifier_lines = production_classifier()
    arms = [a for a in (args.arms.split(",") if args.arms else ARMS) if a]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = {"stamp": stamp, "mode": args.mode, "reps": args.reps, "project": args.proj,
           "godot": subprocess.run(["godot", "--version"], capture_output=True, text=True).stdout.strip(),
           "classifier_source": {"file": str(BATTERY.relative_to(REPO)),
                                 "lines": list(classifier_lines),
                                 "sha256": classifier_sha},
           "probe": str((PROJ / "phys2d_jl.gd").relative_to(REPO)),
           "probe_sha256": hashlib.sha256((PROJ / "phys2d_jl.gd").read_bytes()).hexdigest(),
           "pins_source": "pins.json" if pins_path.is_file() else "inline",
           "rows": [], "discover": {}}
    print(f"classifier classify_process from {BATTERY.relative_to(REPO)} "
          f"lines {classifier_lines[0]}-{classifier_lines[1]} sha256={classifier_sha[:16]}")

    if args.mode == "discover":
        for arm in arms:
            receipt = run_arm(arm, proj)
            line = pass_line(receipt)
            out["discover"][arm] = {"line": line, "rc": receipt["rc"],
                                    "stderr_lines": sorted({l.strip() for l in receipt["stderr"].splitlines()
                                                            if "ERROR:" in l}),
                                    "stdout": receipt["stdout"], "stderr": receipt["stderr"]}
            print(f"--- {arm} rc={receipt['rc']}")
            for l in sorted({l.strip() for l in receipt["stderr"].splitlines() if "ERROR:" in l}):
                print(f"    ERR {l}")
            print(f"    {line}")
    else:
        for arm in arms:
            if arm not in pins:
                print(f"SKIP {arm}: no frozen pin")
                continue
            expected_exit, signature, expected_errors = pins[arm]
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
                                                   "PASS " + PROBE_NAME + " __absent__", expected_errors)
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
    print(f"wrote corpus/live/r81-scout/arms-{args.mode}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
