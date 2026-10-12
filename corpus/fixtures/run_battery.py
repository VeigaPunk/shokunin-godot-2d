#!/usr/bin/env python3
"""Run the read-only Godot fixtures serially in an isolated scratch project."""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = [
    ("mechanic", "controls/mechanic_test.gd", [], 0, "PASS first=true"),
    ("scene_signal", "controls/test_scene_signal.gd", [], 0, "PASS scene_loaded=true"),
    ("input_route", "controls/input_route.gd", [], 0, "PASS route=parse_input_event-to-Node._input"),
    ("route_toggle", "controls/input_route_toggle.gd", [], 0, "PASS toggle=disabled-to-inherit"),
    ("overlap", "controls/overlap_probe.gd", [], 0, "PASS packed_scene=true"),
    ("transition", "controls/scene_transition_probe.gd", [], 0, "PASS valid_transition=true"),
    ("causal", "causal_chain.gd", [], 0, "PASS positive input=1"),
    ("wrong_key", "causal_chain.gd", ["--wrong-key-negative"], 1, "PASS wrong_key=F"),
    ("release", "causal_chain.gd", ["--release-test"], 0, "PASS release press_receipts=1"),
    ("keyup", "causal_chain.gd", ["--keyup-test"], 0, "PASS keyup E_press_receipts=1"),
    ("negative_route", "controls/input_route_negative.gd", [], 1, "PASS negative_route=disabled_node"),
    ("negative_overlap", "controls/overlap_negative.gd", [], 1, "negative control: expected collected signal was absent"),
    ("negative_transition", "controls/scene_transition_negative.gd", [], 1, "PASS invalid_destination_rejected=true"),
    ("negative_signal", "controls/test_scene_signal_negative.gd", [], 1, "negative control: expected collected signal was absent"),
    ("camera_follow", "camera_follow.gd", [], 0, "PASS camera_follow moved=true current=true center_matches_target=true"),
    ("camera_no_follow", "camera_follow.gd", ["--no-follow"], 2, "camera follow assertion failed: target moved but active center did not track"),
    ("ui_signal_hud", "ui_signal_hud.gd", [], 0, "PASS ui_signal connected=true hud_in_tree=true initial=Score: 0 hud_text=Score: 7"),
    ("ui_signal_disconnected", "ui_signal_hud.gd", ["--disconnect-signal"], 2, "UI assertion failed: expected in-tree HUD text=Score: 7"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-failing", action="store_true", help="also mutate scratch scene B and prove detection")
    parser.add_argument("--godot", default="godot")
    parser.add_argument("--runs", type=Path, default=HERE.parent / "live" / "runs")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = args.runs / stamp
    scratch = run_dir / "scratch"
    scratch.mkdir(parents=True)
    for item in HERE.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, scratch / item.name)
        else:
            shutil.copy2(item, scratch / item.name)
    # Seeded controls/pickup.tscn references root pickup.gd; stage its scene in scratch.
    shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")
    # Godot 4.7.2 may install current_scene one process frame after the change.
    chain = scratch / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in text, "causal fixture changed; cannot apply scratch-only readiness fix"
    chain.write_text(text.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    results = []

    def execute(name, script, flags, expected_exit, evidence, mutate=False):
        command = [args.godot, "--headless", "--path", str(scratch), "--script", "res://" + script, "--", *flags]
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=8)
            output = proc.stdout + proc.stderr
            code = proc.returncode
            error = None
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            output += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            code = None
            error = "TIMEOUT after 8 seconds"
        except OSError as exc:
            output = str(exc)
            code = None
            error = f"launch error: {exc}"
        # The mutant is intentionally expected to violate the positive assertion.
        detected = code == 2 and "chain incomplete" in output and "PASS positive input=1" not in output
        passed = detected if mutate else code == expected_exit and evidence in output
        # Any unanticipated Godot error invalidates a passing signature, even for exit-1 controls.
        if not mutate and ("SCRIPT ERROR:" in output or "Parse Error:" in output):
            passed = False
        record = {"case": name, "script": script, "flags": flags, "expected_exit": expected_exit,
                  "actual_exit": code, "signature": evidence, "verdict": "PASS" if passed else "FAIL",
                  "error": error, "output": output.strip().splitlines()}
        results.append(record)
        print(f"{record['verdict']} {name}: exit={code} signature={evidence!r}", flush=True)

    for case in CASES:
        execute(*case)
    if args.probe_failing:
        destination = scratch / "scene_b.tscn"
        original = destination.read_text()
        assert 'marker = "B"' in original, "seeded scene B marker changed; cannot run mutation"
        destination.write_text(original.replace('marker = "B"', 'marker = "BROKEN"', 1))
        execute("mutant_broken_scene_route", "causal_chain.gd", [], 2, "chain incomplete", mutate=True)
    payload = {"godot": args.godot, "seed": str(HERE), "scratch": str(scratch),
               "probe_failing": args.probe_failing, "results": results,
               "verdict": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL"}
    (run_dir / "verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{payload['verdict']} battery: {run_dir / 'verdicts.json'}")
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
