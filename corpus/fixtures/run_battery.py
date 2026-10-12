#!/usr/bin/env python3
"""Run the read-only Godot fixtures serially in an isolated scratch project."""
import argparse
import hashlib
import json
import os
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
    ("export_preset_missing", "__godot_export_missing__", [], 1, "No export preset 'Missing preset' found"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-failing", action="store_true", help="also mutate scratch scene B and prove detection")
    parser.add_argument("--fault-injection", action="store_true", help="run isolated executor fault probes (separate from seeded battery)")
    parser.add_argument("--probe-unrelated-error", action="store_true", help="append unrelated ERROR diagnostics to real export outputs and reclassify")
    parser.add_argument("--probe-export-launch", action="store_true", help="export and launch positive/control startup scenes in bounded scratch Linux/X11 builds")
    parser.add_argument("--probe-godot-error", action="store_true", help="run paired real Godot push_error diagnostic classification probes")
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
            evidence = f"EXPORT PASS preset=Linux/X11 executable_bytes={size}"
            def classify_export(candidate_output):
                return (classify_process(code, error, candidate_output, 0, "[ DONE ]")
                        and "savepack" in candidate_output
                        and export_path.is_file() and export_path.stat().st_size > 0)
            passed = classify_export(output)
            if args.probe_unrelated_error:
                clean_verdict = classify_export(output)
                injected_output = output + "\nERROR: unrelated injected diagnostic\n"
                injected_verdict = classify_export(injected_output)
                marker_line = next(line for line in output.splitlines() if "savepack" in line)
                suffix_spoof = output.replace(marker_line, marker_line + " ERROR: unrelated injected diagnostic", 1)
                prefix_spoof = output.replace(marker_line, "ERROR: unrelated injected diagnostic " + marker_line, 1)
                suffix_verdict = classify_export(suffix_spoof)
                prefix_verdict = classify_export(prefix_spoof)
                results.append({"case": "probe_unrelated_error_export_readiness", "verdict":
                                "PASS" if clean_verdict and not injected_verdict and not suffix_verdict and not prefix_verdict else "FAIL",
                                "clean_classification": clean_verdict,
                                "injected_classification": injected_verdict,
                                "same_line_suffix_classification": suffix_verdict,
                                "same_line_prefix_classification": prefix_verdict,
                                "raw_output": output.strip().splitlines(),
                                "injected_output": injected_output.strip().splitlines(),
                                "same_line_suffix_output": suffix_spoof.strip().splitlines(),
                                "same_line_prefix_output": prefix_spoof.strip().splitlines(),
                                "injected_line": "ERROR: unrelated injected diagnostic"})
            products = sorted(p.name for p in out_dir.iterdir())
            export_record = {"artifact_bytes": size, "artifact_sha256": digest, "products_created": products, "artifacts_deleted": False}
            for product in out_dir.iterdir():
                if product.is_file():
                    product.unlink()
            export_record["artifacts_deleted"] = not any(out_dir.iterdir())
        elif script == "__godot_export_missing__":
            evidence = "ERROR: Invalid export preset name: Missing preset."
            def classify_export(candidate_output):
                return (classify_process(code, error, candidate_output, expected_exit, evidence, (evidence,))
                        and not any(out_dir.iterdir()))
            passed = classify_export(output)
            if args.probe_unrelated_error:
                clean_verdict = classify_export(output)
                injected_output = output + "\nERROR: unrelated injected diagnostic\n"
                injected_verdict = classify_export(injected_output)
                spoof_output = output.replace(evidence, evidence + " ERROR: unrelated injected diagnostic", 1)
                spoof_verdict = classify_export(spoof_output)
                results.append({"case": "probe_unrelated_error_export_preset_missing", "verdict":
                                "PASS" if clean_verdict and not injected_verdict and not spoof_verdict else "FAIL",
                                "clean_classification": clean_verdict,
                                "injected_classification": injected_verdict,
                                "same_line_spoof_classification": spoof_verdict,
                                "raw_output": output.strip().splitlines(),
                                "injected_output": injected_output.strip().splitlines(),
                                "same_line_spoof_output": spoof_output.strip().splitlines(),
                                "injected_line": "ERROR: unrelated injected diagnostic"})
        else:
            passed = None
        # The mutant is intentionally expected to violate the positive assertion.
        def classify_mutant(candidate_output):
            candidate = (classify_process(code, error, candidate_output, 2, evidence,
                                          ("ERROR: " + evidence,))
                         and "PASS " not in candidate_output)
            if name == "mutant_broken_scene_route":
                candidate = (classify_process(code, error, candidate_output, 2, "chain incomplete",
                                              ("ERROR: chain incomplete",))
                             and "PASS positive input=1" not in candidate_output)
            if name == "mutant_level_collision_removed":
                candidate = (classify_process(code, error, candidate_output, 2, evidence,
                                              ("ERROR: LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry",))
                             and "PASS level_packed_scene=true" not in candidate_output)
            return candidate
        detected = classify_mutant(output)
        if mutate and args.probe_unrelated_error:
            injected_output = output + "\nERROR: unrelated injected diagnostic\n"
            injected_detected = classify_mutant(injected_output)
            first_error_line = next(line for line in output.splitlines() if "ERROR:" in line)
            suffix_spoof = output.replace(first_error_line, first_error_line + " ERROR: unrelated injected diagnostic", 1)
            prefix_spoof = output.replace(first_error_line, "ERROR: unrelated injected diagnostic " + first_error_line, 1)
            suffix_detected = classify_mutant(suffix_spoof)
            prefix_detected = classify_mutant(prefix_spoof)
            results.append({"case": "probe_unrelated_error_" + name, "verdict":
                            "PASS" if detected and not injected_detected and not suffix_detected and not prefix_detected else "FAIL",
                            "clean_classification": detected,
                            "injected_classification": injected_detected,
                            "same_line_suffix_classification": suffix_detected,
                            "same_line_prefix_classification": prefix_detected,
                            "raw_output": output.strip().splitlines(),
                            "injected_output": injected_output.strip().splitlines(),
                            "same_line_suffix_output": suffix_spoof.strip().splitlines(),
                            "same_line_prefix_output": prefix_spoof.strip().splitlines(),
                            "injected_line": "ERROR: unrelated injected diagnostic"})
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
    if args.probe_export_launch:
        # Isolated Linux/X11 exported-app launch probe. Both variants are scratch-only;
        # the negative removes only the startup script attachment, then exercises
        # the exact same signature assertion against the launched process.
        launch_root = run_dir / "export-launch"
        positive = launch_root / "positive"
        negative = launch_root / "negative"
        shutil.copytree(scratch, positive, ignore=shutil.ignore_patterns(".godot", "out"))
        shutil.copytree(scratch, negative, ignore=shutil.ignore_patterns(".godot", "out"))
        expected_launch = "EXPORT_LAUNCH_READY scene=fixture"
        launch_results = []

        def configure_launch(project, with_event):
            scene = project / "export_launch.tscn"
            script = project / "export_launch.gd"
            scene.write_text('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://export_launch.gd" id="1"]\n\n[node name="ExportLaunch" type="Node"]\nscript = ExtResource("1")\n')
            event_code = ('    print("EXPORT_LAUNCH_READY scene=fixture")\n' if with_event else '')
            script.write_text('extends Node\n\nfunc _ready() -> void:\n' + event_code + '    get_tree().quit()\n')
            project_file = project / "project.godot"
            config = project_file.read_text()
            config = config.replace('config/features=PackedStringArray("4.7")\n', 'config/features=PackedStringArray("4.7")\nrun/main_scene="res://export_launch.tscn"\n', 1)
            project_file.write_text(config)

        def launch_variant(label, project, with_event):
            configure_launch(project, with_event)
            out_dir = project / "out"
            out_dir.mkdir(exist_ok=True)
            executable = out_dir / "fixture-launch.x86_64"
            export_cmd = [args.godot, "--headless", "--path", str(project), "--export-debug", "Linux/X11", str(executable)]
            exp_output, exp_code, exp_error = run_process(export_cmd, 60)
            exp_ok = (classify_process(exp_code, exp_error, exp_output, 0, "[ DONE ]")
                      and "savepack" in exp_output and executable.is_file() and executable.stat().st_size > 0)
            export_bytes = executable.stat().st_size if executable.is_file() else 0
            pack_path = executable.with_suffix(".pck")
            pack_bytes = pack_path.stat().st_size if pack_path.is_file() else 0
            pack_sha256 = hashlib.sha256(pack_path.read_bytes()).hexdigest() if pack_bytes else None
            launch_cmd = [str(executable), "--headless"]
            # Run with cwd containing only exported products, never source project files.
            launch_cwd = str(out_dir)
            launch_output, launch_code, launch_error = "", None, "export failed; launch skipped"
            if exp_ok:
                try:
                    proc = subprocess.run(launch_cmd, cwd=launch_cwd, capture_output=True, text=True, timeout=5)
                    launch_output, launch_code, launch_error = proc.stdout + proc.stderr, proc.returncode, None
                except subprocess.TimeoutExpired as exc:
                    launch_output = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                    launch_output += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                    launch_code, launch_error = None, "TIMEOUT after 5 seconds"
            signature_lines = [line.strip() for line in launch_output.splitlines() if line.strip() == expected_launch]
            asserted = (exp_ok and classify_process(launch_code, launch_error, launch_output, 0, expected_launch)
                        and len(signature_lines) == 1 and not (Path(launch_cwd) / "project.godot").exists()
                        and not (Path(launch_cwd) / "export_launch.gd").exists()
                        and not (Path(launch_cwd) / "export_launch.tscn").exists())
            clean_without_signature = (launch_code == 0 and launch_error is None
                and "SCRIPT ERROR:" not in launch_output and "Parse Error:" not in launch_output
                and "ERROR:" not in launch_output)
            products = sorted(item.name for item in out_dir.iterdir())
            executable_sha256 = hashlib.sha256(executable.read_bytes()).hexdigest() if executable.is_file() else None
            for item in list(out_dir.iterdir()):
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            launch_results.append({"case": label, "expected_signature": expected_launch,
                "expected_startup_event": with_event, "export_command": export_cmd,
                "export_exit": exp_code, "export_error": exp_error,
                "export_output": exp_output.strip().splitlines(), "export_bytes": export_bytes,
                "executable_sha256": executable_sha256, "pack_bytes": pack_bytes,
                "pack_sha256": pack_sha256,
                "launch_command": launch_cmd, "launch_cwd": launch_cwd, "launch_exit": launch_code,
                "launch_error": launch_error, "launch_output": launch_output.strip().splitlines(),
                "clean_process_without_signature": clean_without_signature,
                "same_signature_assertion": asserted, "products_before_cleanup": products,
                "products_after_cleanup": sorted(item.name for item in out_dir.iterdir())})

        launch_variant("export_launch_positive", positive, True)
        launch_variant("export_launch_missing_startup_event", negative, False)
        launch_payload = {"display": os.environ.get("DISPLAY"), "expected_signature": expected_launch,
                          "results": launch_results,
                          "verdict": "PASS" if launch_results[0]["same_signature_assertion"]
                          and launch_results[1]["export_exit"] == 0
                          and launch_results[1]["export_bytes"] > 0
                          and not launch_results[1]["same_signature_assertion"]
                          and launch_results[1]["clean_process_without_signature"]
                          and launch_results[0]["pack_sha256"] != launch_results[1]["pack_sha256"]
                          and all(not r["products_after_cleanup"] for r in launch_results) else "FAIL"}
        (run_dir / "export-launch-verdicts.json").write_text(json.dumps(launch_payload, indent=2) + "\n")
        results.append({"case": "probe_export_launch", "verdict": launch_payload["verdict"],
                        "artifact": str(run_dir / "export-launch-verdicts.json"),
                        "positive_assertion": launch_results[0]["same_signature_assertion"],
                        "negative_assertion": launch_results[1]["same_signature_assertion"]})
        print(f"{launch_payload['verdict']} export launch probe: {run_dir / 'export-launch-verdicts.json'}", flush=True)

    if args.probe_godot_error:
        expected_error = "ERROR: " + "EXPECTED_NEGATIVE: deliberate assertion rejected"
        unrelated_error = "ERROR: " + "UNRELATED_FAULT: unrelated engine diagnostic"
        probe_results = []
        for label, flags in (("godot_error_expected_negative", []),
                             ("godot_error_unrelated", ["--unrelated-error"])):
            command = [args.godot, "--headless", "--path", str(scratch), "--script",
                       "res://godot_error_probe.gd", "--", *flags]
            output, code, error = run_process(command, 8)
            inner = classify_process(code, error, output, 1,
                                     "EXPECTED_NEGATIVE: deliberate assertion rejected",
                                     (expected_error,))
            record = {"case": label, "command": command, "expected_exit": 1,
                      "actual_exit": code, "error": error,
                      "signature": "EXPECTED_NEGATIVE: deliberate assertion rejected",
                      "inner_classification": inner, "raw_output": output,
                      "raw_output_lines": output.strip().splitlines()}
            probe_results.append(record)
            print(f"{'PASS' if inner else 'FAIL'} {label}: exit={code} classification={inner}", flush=True)
        clean, fault = probe_results
        def exact_error_lines(record, diagnostic):
            return [line.strip() for line in record["raw_output_lines"]
                    if line.strip().startswith("ERROR:") and line.strip() == diagnostic]

        clean_expected_lines = exact_error_lines(clean, expected_error)
        fault_expected_lines = exact_error_lines(fault, expected_error)
        fault_unrelated_lines = exact_error_lines(fault, unrelated_error)
        script_paths = [record["command"][record["command"].index("--script") + 1]
                        for record in probe_results]
        same_script = len(set(script_paths)) == 1 and script_paths[0] == "res://godot_error_probe.gd"
        same_expected_exit = clean["expected_exit"] == fault["expected_exit"] == 1
        same_signature = clean["signature"] == fault["signature"]
        clean_emitted_expected = len(clean_expected_lines) == 1
        fault_emitted_expected = len(fault_expected_lines) == 1
        fault_emitted_unrelated = len(fault_unrelated_lines) == 1
        meta_pass = (clean["inner_classification"] and not fault["inner_classification"]
                     and clean_emitted_expected and fault_emitted_expected and fault_emitted_unrelated
                     and clean["actual_exit"] == fault["actual_exit"] == 1
                     and same_script and same_expected_exit and same_signature)
        probe_payload = {"mode": "real_godot_push_error", "same_script": same_script,
                         "script_paths": script_paths, "same_expected_exit": same_expected_exit,
                         "same_signature": same_signature,
                         "expected_diagnostic": expected_error,
                         "unrelated_diagnostic": unrelated_error, "results": probe_results,
                         "expected_error_lines": {"clean": clean_expected_lines, "fault": fault_expected_lines},
                         "unrelated_error_lines": fault_unrelated_lines,
                         "emitted_expected_once_in_both": clean_emitted_expected and fault_emitted_expected,
                         "unrelated_emitted_once_in_fault": fault_emitted_unrelated,
                         "verdict": "PASS" if meta_pass else "FAIL"}
        artifact = run_dir / "godot-error-verdicts.json"
        artifact.write_text(json.dumps(probe_payload, indent=2) + "\n")
        results.append({"case": "probe_godot_error", "verdict": probe_payload["verdict"],
                        "artifact": str(artifact), "inner_classifications":
                        [r["inner_classification"] for r in probe_results]})
        print(f"{probe_payload['verdict']} Godot diagnostic probe: {artifact}")

    payload = {"godot": args.godot, "seed": str(HERE), "scratch": str(scratch),
               "probe_failing": args.probe_failing, "results": results,
               "verdict": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL"}
    (run_dir / "verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{payload['verdict']} battery: {run_dir / 'verdicts.json'}")
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
