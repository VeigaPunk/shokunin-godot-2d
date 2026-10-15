#!/usr/bin/env python3
"""r79 boundary-exec scratch runner — live falsification of the §1.4 pins.

Control arms run the byte-identical scout probe (proj/phys2d_events.gd, sha
7329acb2…) through the PRODUCTION `classify_process` predicate extracted
verbatim from corpus/fixtures/run_battery.py (via the scout's own extraction
function) against the scout's frozen PINS. Falsification arms run
proj/boundary_probe.gd and are measurement-only (`XPROBE ...` lines).

Scratch only: writes under corpus/live/r79-boundary-exec/runs/.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCOUT = REPO / "corpus" / "live" / "r79-scout"
BATTERY = REPO / "corpus" / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
TIMEOUT = 8  # the battery's own bound for non-export scripts
SKIP_CONTROLS = "--skip-controls" in sys.argv

sys.path.insert(0, str(SCOUT))
import run_arms  # noqa: E402  scout scratch runner: PINS + production classifier extraction

CONTROL_ARMS = [
    ("cm_on", 3),
    ("rb_node_position", 3),
    ("rb_dss_in_cb", 3),
    ("rb_queue_free", 20),
]
X_ARMS = [
    ("xcm_two_floors", 3),
    ("xcm_swap_noop", 3),
    ("xcm_swap_shrink", 3),
    ("xcm_swap_grow", 3),
    ("xcm_floor_move", 3),
    ("xrb_immediate_scout", 3),
    ("xrb_immediate_nosamp", 3),
    ("xrb_immediate_postread", 3),
    ("xrb_immediate_sampler", 3),
    ("xrb_immediate_ordertest", 3),
    ("xrb_immediate_nocolliders", 3),
    ("xrb_immediate_noderead", 3),
    ("xrb_immediate_readonly", 3),
    ("xrb_immediate_posread", 3),
    ("xrb_immediate_one", 3),
    ("xrb_immediate_two", 3),
    ("xrb_deferred_one", 3),
    ("xrb_deferred_two", 3),
    ("xrb_free_immediate", 3),
    ("xrb_dss_foreign", 3),
]


def run_probe(arm, probe, proj=PROJ):
    command = ["godot", "--headless", "--path", str(proj),
               "--script", "res://" + probe, "--", "--arm=" + arm]
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=TIMEOUT)
        return {"arm": arm, "probe": probe, "rc": proc.returncode,
                "stdout": proc.stdout, "stderr": proc.stderr, "timeout": None,
                "command": command}
    except subprocess.TimeoutExpired as exc:
        return {"arm": arm, "probe": probe, "rc": None,
                "stdout": exc.stdout or "", "stderr": exc.stderr or "",
                "timeout": f"TIMEOUT after {TIMEOUT} seconds", "command": command}


def pass_line(receipt):
    for line in (receipt["stdout"] + receipt["stderr"]).splitlines():
        if line.startswith("PASS phys2d_events"):
            return line
    return None


def xprobe_line(receipt):
    for line in receipt["stdout"].splitlines():
        if line.startswith("XPROBE ") and "|" in line:
            return line
    return None


def main():
    classify, classifier_sha, classifier_lines = run_arms.production_classifier()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = HERE / "runs" / stamp
    run_dir.mkdir(parents=True)
    godot_version = subprocess.run(["godot", "--version"], capture_output=True,
                                   text=True).stdout.strip()
    out = {
        "stamp": stamp,
        "godot": godot_version,
        "repo": str(REPO),
        "run_battery_sha256": hashlib.sha256(BATTERY.read_bytes()).hexdigest(),
        "classifier_source": {"file": str(BATTERY.relative_to(REPO)),
                              "lines": list(classifier_lines),
                              "sha256": classifier_sha},
        "control_probe": {"file": "proj/phys2d_events.gd",
                          "sha256": hashlib.sha256((PROJ / "phys2d_events.gd").read_bytes()).hexdigest()},
        "x_probe": {"file": "proj/boundary_probe.gd",
                    "sha256": hashlib.sha256((PROJ / "boundary_probe.gd").read_bytes()).hexdigest()},
        "controls": [], "falsification": [],
    }
    print(f"classifier classify_process {BATTERY.relative_to(REPO)} lines "
          f"{classifier_lines[0]}-{classifier_lines[1]} sha256={classifier_sha}")

    for arm, reps in ([] if SKIP_CONTROLS else CONTROL_ARMS):
        expected_exit, signature, expected_errors = run_arms.PINS[arm]
        rows = []
        for rep in range(reps):
            r = run_probe(arm, "phys2d_events.gd")
            merged = r["stdout"] + r["stderr"]
            verdict = classify(r["rc"], r["timeout"], merged, expected_exit,
                               signature, expected_errors)
            (run_dir / f"control-{arm}__rep{rep}.stdout.txt").write_text(r["stdout"])
            (run_dir / f"control-{arm}__rep{rep}.stderr.txt").write_text(r["stderr"])
            rows.append({"rep": rep, "rc": r["rc"], "timeout": r["timeout"],
                         "verdict": "PASS" if verdict else "FAIL",
                         "measured_line": pass_line(r),
                         "stdout_sha256": hashlib.sha256(r["stdout"].encode()).hexdigest(),
                         "stderr_sha256": hashlib.sha256(r["stderr"].encode()).hexdigest()})
        stable = len({(row["stdout_sha256"], row["stderr_sha256"]) for row in rows}) == 1
        row = {"arm": arm, "reps": reps, "rc": [x["rc"] for x in rows],
               "verdicts": [x["verdict"] for x in rows], "stable_bytes": stable,
               "pin": signature, "measured_line": rows[0]["measured_line"],
               "matches_pin": rows[0]["measured_line"] == signature,
               "per_rep": rows}
        out["controls"].append(row)
        print(f"{'OK ' if all(v == 'PASS' for v in row['verdicts']) and stable else 'BAD'} "
              f"control {arm} rc={row['rc']} verdicts={row['verdicts']} stable={stable} "
              f"pin_exact={row['matches_pin']}")

    for arm, reps in X_ARMS:
        rows = []
        for rep in range(reps):
            r = run_probe(arm, "boundary_probe.gd")
            (run_dir / f"x-{arm}__rep{rep}.stdout.txt").write_text(r["stdout"])
            (run_dir / f"x-{arm}__rep{rep}.stderr.txt").write_text(r["stderr"])
            rows.append({"rep": rep, "rc": r["rc"], "timeout": r["timeout"],
                         "line": xprobe_line(r), "done": "XPROBE_DONE " + arm in r["stdout"],
                         "error_lines": sorted({l.strip() for l in (r["stdout"] + r["stderr"]).splitlines()
                                                if "ERROR:" in l}),
                         "script_errors": sorted({l.strip() for l in (r["stdout"] + r["stderr"]).splitlines()
                                                   if "SCRIPT ERROR:" in l}),
                         "stdout_sha256": hashlib.sha256(r["stdout"].encode()).hexdigest()})
        stable = len({x["stdout_sha256"] for x in rows}) == 1
        out["falsification"].append({"arm": arm, "reps": reps, "rc": [x["rc"] for x in rows],
                                     "stable_bytes": stable, "per_rep": rows})
        print(f"--- x {arm} rc={[x['rc'] for x in rows]} stable={stable}")
        print(f"    {rows[0]['line']}")
        if rows[0]["error_lines"]:
            for l in rows[0]["error_lines"]:
                print(f"    ERR {l}")
        if rows[0]["script_errors"]:
            for l in rows[0]["script_errors"]:
                print(f"    SERR {l}")

    (run_dir / "probe.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {run_dir.relative_to(REPO)}/probe.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
