#!/usr/bin/env python3
"""Run the read-only Godot fixtures serially in an isolated scratch project."""
import argparse
import hashlib
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
    ("level_collision", "level_collision/level_probe.gd", [], 0, "PASS level_packed_scene=true cell=2,3 collision_vertices=4"),
    ("contact_runtime", "contact_probe.gd", [], 0, "PASS runtime_tile_contact=true cell=2,3,"),
    ("contact_no_collision", "contact_probe.gd", ["--no-collision"], 2, "CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3"),
    ("animation_property", "animation_property.gd", [], 0, "PASS animation_property_changed=true started=true"),
    ("animation_stuck", "animation_property.gd", ["--stuck"], 2, "ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance"),
    ("export_readiness", "__godot_export__", [], 0, "EXPORT PASS preset=Linux/X11 executable=nonempty"),
    ("export_preset_missing", "__godot_export_missing__", [], 2, "No export preset 'Missing preset' found"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-failing", action="store_true", help="also mutate scratch scene B and prove detection")
    parser.add_argument("--fault-injection", action="store_true", help="run isolated executor fault probes (separate from seeded battery)")
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

    def run_process(command, timeout_seconds):
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
            return proc.stdout + proc.stderr, proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            output += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return output, None, f"TIMEOUT after {timeout_seconds} seconds"
        except OSError as exc:
            return str(exc), None, f"launch error: {exc}"

    def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
        lines = output.splitlines()
        def allowed_error(line, allowed):
            stripped = line.strip()
            if stripped == allowed:
                return True
            if allowed.endswith(","):
                return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
            if allowed == "ERROR: chain incomplete":
                return (stripped.startswith("ERROR: chain incomplete collections=")
                        and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                        and stripped.count("ERROR:") == 1)
            return False

        unrelated_errors = [line for line in lines if "ERROR:" in line
                            and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
        return (code == expected_exit and error is None and signature in output
                and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)

    if args.fault_injection:
        # Fault probes use Python subprocesses, not seeded fixtures or Godot. The
        # deliberately long sleep is bounded only here; the normal CLI is unchanged.
        faults = [
            ("fault_hang", [sys.executable, "-c", "import time; print('FAULT_HANG_STARTED', flush=True); time.sleep(30)"],
             0, "FAULT_HANG_STARTED", 0.25, ()),
            ("fault_clean_expected_negative", [sys.executable, "-c", "print('ERROR: expected negative diagnostic'); raise SystemExit(2)"],
             2, "ERROR: expected negative diagnostic", 2, ("ERROR: expected negative diagnostic",)),
            ("fault_unrelated_error", [sys.executable, "-c", "print('ERROR: expected negative diagnostic'); print('ERROR: unrelated engine failure'); raise SystemExit(2)"],
             2, "ERROR: expected negative diagnostic", 2, ("ERROR: expected negative diagnostic",)),
        ]
        for name, command, expected_exit, signature, timeout_seconds, allowed_errors in faults:
            started = datetime.now(timezone.utc)
            output, code, error = run_process(command, timeout_seconds)
            elapsed = (datetime.now(timezone.utc) - started).total_seconds()
            passed = classify_process(code, error, output, expected_exit, signature, allowed_errors)
            record = {"case": name, "expected_exit": expected_exit, "signature": signature,
                      "actual_exit": code, "verdict": "PASS" if passed else "FAIL", "error": error,
                      "elapsed_seconds": round(elapsed, 3), "timeout_seconds": timeout_seconds,
                      "output": output.strip().splitlines()}
            results.append(record)
            print(f"{record['verdict']} {name}: exit={code} error={error!r}", flush=True)
        expected_verdicts = {"fault_hang": "FAIL", "fault_clean_expected_negative": "PASS",
                             "fault_unrelated_error": "FAIL"}
        payload = {"mode": "fault_injection", "seeded_battery_run": False, "results": results,
                   "verdict": "PASS" if all(r["verdict"] == expected_verdicts[r["case"]] for r in results)
                   and "FAULT_HANG_STARTED" in "\n".join(results[0]["output"])
                   and "ERROR: expected negative diagnostic" in "\n".join(results[1]["output"])
                   and "ERROR: unrelated engine failure" in "\n".join(results[2]["output"])
                   else "FAIL"}
        (run_dir / "fault-verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
        print(f"{payload['verdict']} fault injection: {run_dir / 'fault-verdicts.json'}")
        return 0 if payload["verdict"] == "PASS" else 1

    def execute(name, script, flags, expected_exit, evidence, mutate=False):
        if script in ("__godot_export__", "__godot_export_missing__"):
            export_project = scratch
            preset_name = "Linux/X11"
            if script == "__godot_export_missing__":
                export_project = run_dir / "missing-preset-scratch"
                shutil.copytree(scratch, export_project, ignore=shutil.ignore_patterns(".godot", "out"))
                preset_name = "Missing preset"
            out_dir = export_project / "out"
            out_dir.mkdir(exist_ok=True)
            assert not any(out_dir.iterdir()), "export output directory must start empty"
            export_path = out_dir / "fixture.x86_64"
            command = [args.godot, "--headless", "--path", str(export_project),
                       "--export-debug", preset_name, str(export_path)]
        else:
            command = [args.godot, "--headless", "--path", str(scratch), "--script", "res://" + script, "--", *flags]
        timeout_seconds = 60 if script.startswith("__godot_export") else 8
        output, code, error = run_process(command, timeout_seconds)
        export_record = None
        if script == "__godot_export__":
            size = export_path.stat().st_size if export_path.is_file() else 0
            digest = hashlib.sha256(export_path.read_bytes()).hexdigest() if size else None
            passed = (code == 0 and error is None and size > 0
                      and "ERROR:" not in output and "SCRIPT ERROR:" not in output)
            evidence = f"EXPORT PASS preset=Linux/X11 executable_bytes={size}"
            products = sorted(p.name for p in out_dir.iterdir())
            export_record = {"artifact_bytes": size, "artifact_sha256": digest, "products_created": products, "artifacts_deleted": False}
            for product in out_dir.iterdir():
                if product.is_file():
                    product.unlink()
            export_record["artifacts_deleted"] = not any(out_dir.iterdir())
        elif script == "__godot_export_missing__":
            passed = (code is not None and code != 0 and error is None
                      and "ERROR: Invalid export preset name: Missing preset." in output
                      and not any(out_dir.iterdir()))
            evidence = "ERROR: Invalid export preset name: Missing preset."
        else:
            passed = None
        # The mutant is intentionally expected to violate the positive assertion.
        detected = (classify_process(code, error, output, 2, evidence,
                                     ("ERROR: " + evidence,))
                    and "PASS " not in output)
        if mutate and name == "mutant_broken_scene_route":
            detected = (classify_process(code, error, output, 2, "chain incomplete",
                                         ("ERROR: chain incomplete",))
                        and "PASS positive input=1" not in output)
        if mutate and name == "mutant_level_collision_removed":
            detected = (classify_process(code, error, output, 2, evidence,
                                         ("ERROR: LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry",))
                        and "PASS level_packed_scene=true" not in output)
        if passed is None:
            expected_errors = {
                "negative_overlap": ("ERROR: negative control: expected collected signal was absent with disabled mask",),
                "negative_transition": ("ERROR: Can't change to a null scene. Use unload_current_scene() if you wish to unload it.",
                                      "ERROR: negative control: deliberately invalid scene destination rejected"),
                "negative_signal": ("ERROR: negative control: expected collected signal was absent (dispatch deliberately disabled)",),
                "camera_no_follow": ("ERROR: camera follow assertion failed: target moved but active center did not track",),
                "ui_signal_disconnected": ("ERROR: UI assertion failed: expected in-tree HUD text=Score: 7",),
                "animation_stuck": ("ERROR: ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance,",),
                "export_preset_missing": ("ERROR: Invalid export preset name: Missing preset.",),
                "contact_no_collision": ("ERROR: CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3,",),
            }.get(name, ())
            passed = detected if mutate else classify_process(code, error, output, expected_exit, evidence, expected_errors)
        # A script/parse error never counts as intended mutant detection.
        if "SCRIPT ERROR:" in output or "Parse Error:" in output:
            passed = False
        record = {"case": name, "script": script, "flags": flags, "expected_exit": expected_exit,
                  "actual_exit": code, "signature": evidence, "verdict": "PASS" if passed else "FAIL",
                  "error": error, "output": output.strip().splitlines()}
        if export_record is not None:
            record["export_artifact"] = export_record
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
        execute("mutant_level_collision_removed", "level_collision/level_probe.gd", ["--no-collision"], 2,
                "LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry", mutate=True)
    payload = {"godot": args.godot, "seed": str(HERE), "scratch": str(scratch),
               "probe_failing": args.probe_failing, "results": results,
               "verdict": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL"}
    (run_dir / "verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{payload['verdict']} battery: {run_dir / 'verdicts.json'}")
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
