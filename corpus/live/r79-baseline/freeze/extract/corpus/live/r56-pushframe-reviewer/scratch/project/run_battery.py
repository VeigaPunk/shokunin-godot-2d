#!/usr/bin/env python3
"""Run the read-only Godot fixtures serially in an isolated scratch project."""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import selectors
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
    ("camera_limit", "camera_limit.gd", [], 0, "PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true far_bound=false"),
    ("camera_far_bound", "camera_limit.gd", ["--far-bound"], 2, "camera limit assertion failed: expected active center within right boundary and distinct from target"),
    ("camera_top_limit", "camera_limit.gd", ["--top-bound"], 0, "PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true"),
    ("camera_far_top_bound", "camera_limit.gd", ["--far-top-bound"], 2, "camera limit assertion failed: expected active center within top boundary and distinct from target"),
    ("camera_left_limit", "camera_limit.gd", ["--left-bound"], 0, "PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true"),
    ("camera_far_left_bound", "camera_limit.gd", ["--far-left-bound"], 2, "camera limit assertion failed: expected active center within left boundary and distinct from target"),
    ("camera_bottom_limit", "camera_limit.gd", ["--bottom-bound"], 0, "PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true"),
    ("camera_far_bottom_bound", "camera_limit.gd", ["--far-bottom-bound"], 2, "camera limit assertion failed: expected active center within bottom boundary and distinct from target"),
    ("ui_signal_hud", "ui_signal_hud.gd", [], 0, "PASS ui_signal connected=true hud_in_tree=true initial=Score: 0 hud_text=Score: 7"),
    ("ui_signal_disconnected", "ui_signal_hud.gd", ["--disconnect-signal"], 2, "UI assertion failed: expected in-tree HUD text=Score: 7"),
    ("health_gauge", "health_gauge.gd", [], 0, "PASS health_gauge in_tree=true range=0..100 values=35,0.0,100.0,100.0 receipts=35,0,100"),
    ("health_gauge_disconnected", "health_gauge.gd", ["--disconnect-signal"], 2, "Health gauge assertion failed: expected in-tree TextureProgressBar value=35 value_changed=1 receipt=35"),
    ("level_collision", "level_collision/level_probe.gd", [], 0, "PASS level_packed_scene=true cell=2,3 collision_vertices=4"),
    ("contact_runtime", "contact_probe.gd", [], 0, "PASS runtime_tile_contact=true cell=2,3,"),
    ("contact_no_collision", "contact_probe.gd", ["--no-collision"], 2, "CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3"),
    ("animation_property", "animation_property.gd", [], 0, "PASS animation_property_changed=true started=true"),
    ("animation_stuck", "animation_property.gd", ["--stuck"], 2, "ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance"),
    ("tween_flash", "tween_flash.gd", [], 0, "PASS tween_flash transient_modulate="),
    ("tween_no_start", "tween_flash.gd", ["--no-tween"], 2, "TWEEN ASSERTION FAILED: modulate did not show flash then return to baseline,"),
    ("audio_playback", "audio_playback.gd", [], 0, "PASS audio_playback in_tree=true playing=true position_advanced=true"),
    ("audio_no_play", "audio_playback.gd", ["--no-play"], 2, "AUDIO ASSERTION FAILED: expected in-tree player playback to advance"),
    ("export_readiness", "__godot_export__", [], 0, "EXPORT PASS preset=Linux/X11 executable=nonempty"),
    ("export_preset_missing", "__godot_export_missing__", [], 1, "No export preset 'Missing preset' found"),
    ("button_activation", "button_activation.gd", [], 0, "PASS button_activation in_tree=true initial=Ready edge_texts=[Ready,Activated 1,Activated 1,Activated 2] receipts=[0,1,1,2]"),
    ("button_activation_disconnected", "button_activation.gd", ["--disconnect-signal"], 2, "UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1"),
    ("button_activation_unfocused", "button_activation.gd", ["--no-focus"], 2, "UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1"),
    ("button_activation_focus_loss", "button_activation.gd", ["--lose-focus-after-first"], 0, "PASS button_activation_focus_loss initial=focused release1=Activated1 mid_sequence=no_focus release2=Activated1 receipts=1"),
    ("checkbox_toggle", "checkbox_toggle.gd", [], 0, "PASS checkbox_toggle edge_states=[false,true,true,false] toggled=[true,false] labels=[On,Off]"),
    ("checkbox_toggle_disconnected", "checkbox_toggle.gd", ["--disconnect-signal"], 2, "ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []"),
    ("button_group_selection", "button_group_selection.gd", [], 0, "PASS button_group_selection exclusive=true toggled=[A:false,B:true,B:false,A:true] labels=[B,A]"),
    ("button_group_selection_disconnected", "button_group_selection.gd", ["--disconnect-signal"], 2, "ERROR: BUTTON_GROUP SIGNAL ASSERTION FAILED: expected transitions [A:false,B:true,B:false,A:true], got []"),
    ("button_group_selection_ungroup_b", "button_group_selection.gd", ["--ungroup-b"], 2, "BUTTON_GROUP ABSENCE ASSERTION FAILED after B→A: expected exclusive selection, got A=true B=true"),
    ("slider_adjust", "slider_adjust.gd", [], 0, "PASS slider_adjust focused=true range=0..10 step=1 values=6,5 receipts=6,5 Labels=Value 6,Value 5"),
    ("slider_adjust_disconnected", "slider_adjust.gd", ["--disconnect-signal"], 2, "SLIDER SIGNAL ASSERTION FAILED: expected value_changed receipts [6,5] and Labels [Value 6,Value 5]"),
    ("slider_adjust_no_focus", "slider_adjust.gd", ["--no-focus"], 2, "SLIDER NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,5"),
    ("slider_adjust_repeat_right", "slider_adjust.gd", ["--repeat-right"], 0, "PASS slider_adjust_repeat focused=true range=0..10 step=1 values=6,7,7,6,6,5,5 receipts=6,7,6,5 Labels=Value 6,Value 7,Value 6,Value 5"),
    ("slider_adjust_repeat_right_disconnected", "slider_adjust.gd", ["--repeat-right", "--disconnect-signal"], 2, "SLIDER REPEAT SIGNAL ASSERTION FAILED: expected value_changed receipts [6,7,6,5] and Labels [Value 6,Value 7,Value 6,Value 5]"),
    ("slider_adjust_repeat_right_no_focus", "slider_adjust.gd", ["--repeat-right", "--no-focus"], 2, "SLIDER REPEAT NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,7,7,6,6,5,5"),
    ("slider_adjust_repeat_right_focus_handoff", "slider_adjust.gd", ["--repeat-right", "--focus-handoff"], 2, "SLIDER REPEAT FOCUS-HANDOFF ASSERTION FAILED: expected post-handoff adjustment after seven checks"),
    ("slider_adjust_repeat_right_focus_restore", "slider_adjust.gd", ["--repeat-right", "--focus-restore"], 0, "PASS slider_adjust_repeat_focus_restore focused=true range=0..10 step=1 values=6,6,6,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4"),
    ("slider_adjust_repeat_right_second_focus_loss", "slider_adjust.gd", ["--repeat-right", "--second-focus-loss"], 2, "SLIDER REPEAT SECOND-FOCUS-LOSS ASSERTION FAILED: expected final restored-focus adjustment after seven checks"),
    ("slider_adjust_repeat_right_second_focus_restore", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore"], 0, "PASS slider_adjust_repeat_second_focus_restore focused=true values=6,6,6,5,5,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4"),
    ("slider_adjust_repeat_right_second_focus_restore_disconnected", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--disconnect-signal"], 2, "SLIDER DOUBLE-RESTORE DISCONNECTED ASSERTION FAILED: expected signal-consumer updates"),
    ("slider_adjust_repeat_right_second_focus_restore_reconnect_after_first_left", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--reconnect-after-first-left"], 0, "PASS slider_adjust_repeat_second_focus_restore_reconnect values=6,6,6,5,5,5,5,4,4 receipts=6,4 Labels=Value 6,Value 4"),
    ("slider_adjust_repeat_right_second_focus_restore_release_after_late_reconnect_press", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--release-after-late-reconnect-press"], 2, "SLIDER RELEASE AFTER LATE-RECONNECT PRESS ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_observe_parsed_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--observe-parsed-release"], 2, "SLIDER PARSED RELEASE OBSERVER ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_composite_push_and_clear", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--composite-push-and-clear"], 2, "SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_clear_then_push_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--clear-then-push-release"], 2, "SLIDER CLEAR THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_clear_frame_then_push_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--clear-frame-then-push-release"], 2, "SLIDER CLEAR FRAME THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_observe_push_input_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--observe-push-input-release"], 2, "SLIDER PUSH INPUT RELEASE ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_press_after_late_reconnect", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--press-after-late-reconnect"], 0, "PASS slider_adjust_repeat_second_focus_restore_press_after_late_reconnect values=6,6,6,5,5,5,5,4,4,3 receipts=6,3 Labels=Value 6,Value 3"),
    ("slider_adjust_repeat_right_second_focus_restore_reconnect_after_final_left", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--reconnect-after-final-left"], 2, "SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks"),
    ("slider_adjust_repeat_right_second_focus_restore_disconnect_after_first", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--disconnect-after-first"], 2, "SLIDER MID-DISCONNECT ASSERTION FAILED: expected cumulative callback history to stay [6]"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-failing", action="store_true", help="also mutate scratch scene B and prove detection")
    parser.add_argument("--fault-injection", action="store_true", help="run isolated executor fault probes (separate from seeded battery)")
    parser.add_argument("--probe-unrelated-error", action="store_true", help="append unrelated ERROR diagnostics to real export outputs and reclassify")
    parser.add_argument("--probe-export-launch", action="store_true", help="export and launch positive/control startup scenes in bounded scratch Linux/X11 builds")
    parser.add_argument("--probe-godot-error", action="store_true", help="run paired real Godot push_error diagnostic classification probes")
    parser.add_argument("--probe-stream-attribution", action="store_true", help="run paired real Godot stdout/stderr stream-attribution classification probes")
    parser.add_argument("--probe-crash-exit", action="store_true", help="run a paired real-Godot normal-exit versus signal-termination probe")
    parser.add_argument("--probe-timeout", action="store_true", help="run a paired real-Godot normal-exit versus timeout probe")
    parser.add_argument("--probe-audio-warning", action="store_true", help="classify captured r12 leaked and clean audio outputs with the production audio verdict")
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

    def classify_streams(code, error, stdout, stderr, expected_exit, signature, allowed_stderr=()):
        """Classify using separate stdout/stderr. Signature must appear on stdout."""
        if code != expected_exit or error is not None:
            return False
        if signature not in stdout:
            return False
        if "SCRIPT ERROR:" in stdout or "SCRIPT ERROR:" in stderr:
            return False
        if "Parse Error:" in stdout or "Parse Error:" in stderr:
            return False
        stderr_lines = stderr.splitlines()
        allowed = set(allowed_stderr)

        def line_allowed(stripped):
            if stripped in allowed:
                return True
            for a in allowed:
                if a.endswith(",") and stripped.startswith(a) and stripped.count("ERROR:") == 1:
                    return True
            return False

        for line in stderr_lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Any unexpected stderr line rejects. Prefix-only checks would
            # false-admit a printerr that is neither ERROR: nor STREAM_STDERR:.
            if not line_allowed(stripped):
                return False
        return True

    def classify_audio_process(code, error, output, expected_exit, signature, allowed_errors=()):
        # Scope this known ObjectDB shutdown leak warning to audio_playback only;
        # export cases can legitimately print nested-project WARNING lines.
        leaked_objectdb = any(
            re.fullmatch(r"WARNING: [1-9][0-9]* ObjectDB instances were leaked at exit(?: \(run with `--verbose` for details\)\.)?", line.strip())
            for line in output.splitlines())
        return (classify_process(code, error, output, expected_exit, signature, allowed_errors)
                and not leaked_objectdb)

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

    if args.probe_audio_warning:
        captured = []
        for label, filename in (("captured_leak", "r12-initial-hold.json"),
                                ("captured_clean", "r12-battery-verifier.json")):
            payload = json.loads((HERE.parent / "lessons" / filename).read_text())
            matches = [item for item in payload["results"] if item.get("case") == "audio_playback"]
            if len(matches) != 1 or not isinstance(matches[0].get("output"), list):
                raise ValueError(f"{filename} lacks exactly one captured audio_playback output")
            record = matches[0]
            raw = "\n".join(record["output"])
            verdict = classify_audio_process(record["actual_exit"], record["error"], raw,
                                             record["expected_exit"], record["signature"])
            captured.append({"case": label, "source": filename, "actual_exit": record["actual_exit"],
                             "verdict": "PASS" if verdict else "FAIL", "output": record["output"]})
        expected = ["FAIL", "PASS"]
        meta = {"case": "probe_audio_warning_captured_r12", "verdict":
                "PASS" if [item["verdict"] for item in captured] == expected
                and "WARNING: 2 ObjectDB instances were leaked at exit" in "\n".join(captured[0]["output"])
                and "WARNING: 2 ObjectDB instances were leaked at exit" not in "\n".join(captured[1]["output"])
                else "FAIL",
                "classifier": "production classify_audio_process", "results": captured}
        results.append(meta)
        print(f"{meta['verdict']} captured r12 audio-warning classifier probe", flush=True)

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
            export_path = (out_dir / "fixture.x86_64").resolve()
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
                "camera_far_bound": ("ERROR: camera limit assertion failed: expected active center within right boundary and distinct from target",),
                "camera_far_top_bound": ("ERROR: camera limit assertion failed: expected active center within top boundary and distinct from target",),
                "camera_far_left_bound": ("ERROR: camera limit assertion failed: expected active center within left boundary and distinct from target",),
                "camera_far_bottom_bound": ("ERROR: camera limit assertion failed: expected active center within bottom boundary and distinct from target",),
                "ui_signal_disconnected": ("ERROR: UI assertion failed: expected in-tree HUD text=Score: 7",),
                "button_activation_disconnected": ("ERROR: UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1,",),
                "button_activation_unfocused": ("ERROR: UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1,",),
                "checkbox_toggle_disconnected": ("ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []",),
                "button_group_selection_disconnected": ("ERROR: BUTTON_GROUP SIGNAL ASSERTION FAILED: expected transitions [A:false,B:true,B:false,A:true], got []",),
                "button_group_selection_ungroup_b": ("ERROR: BUTTON_GROUP ABSENCE ASSERTION FAILED after B→A: expected exclusive selection, got A=true B=true",),
                "slider_adjust_disconnected": ("ERROR: SLIDER SIGNAL ASSERTION FAILED: expected value_changed receipts [6,5] and Labels [Value 6,Value 5]",),
                "slider_adjust_no_focus": ("ERROR: SLIDER NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,5",),
                "slider_adjust_repeat_right_disconnected": ("ERROR: SLIDER REPEAT SIGNAL ASSERTION FAILED: expected value_changed receipts [6,7,6,5] and Labels [Value 6,Value 7,Value 6,Value 5]",),
                "slider_adjust_repeat_right_no_focus": ("ERROR: SLIDER REPEAT NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,7,7,6,6,5,5",),
                "slider_adjust_repeat_right_focus_handoff": ("ERROR: SLIDER REPEAT FOCUS-HANDOFF ASSERTION FAILED: expected post-handoff adjustment after seven checks",),
                "slider_adjust_repeat_right_focus_restore": (),
                "slider_adjust_repeat_right_second_focus_loss": ("ERROR: SLIDER REPEAT SECOND-FOCUS-LOSS ASSERTION FAILED: expected final restored-focus adjustment after seven checks",),
                "slider_adjust_repeat_right_second_focus_restore": (),
                "slider_adjust_repeat_right_second_focus_restore_disconnected": ("ERROR: SLIDER DOUBLE-RESTORE DISCONNECTED ASSERTION FAILED: expected signal-consumer updates",),
                "slider_adjust_repeat_right_second_focus_restore_disconnect_after_first": ("ERROR: SLIDER MID-DISCONNECT ASSERTION FAILED: expected cumulative callback history to stay [6]",),
                "slider_adjust_repeat_right_second_focus_restore_reconnect_after_final_left": ("ERROR: SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks",),
                "slider_adjust_repeat_right_second_focus_restore_press_after_late_reconnect": (),
                "slider_adjust_repeat_right_second_focus_restore_release_after_late_reconnect_press": ("ERROR: SLIDER RELEASE AFTER LATE-RECONNECT PRESS ASSERTION FAILED: expected no new receipt after eleven checks",),
                "slider_adjust_repeat_right_second_focus_restore_observe_parsed_release": ("ERROR: SLIDER PARSED RELEASE OBSERVER ASSERTION FAILED: expected no new receipt after eleven checks",),
                "slider_adjust_repeat_right_second_focus_restore_composite_push_and_clear": ("ERROR: SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks",),
                "slider_adjust_repeat_right_second_focus_restore_clear_then_push_release": ("ERROR: SLIDER CLEAR THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks",),
                "slider_adjust_repeat_right_second_focus_restore_clear_frame_then_push_release": ("ERROR: SLIDER CLEAR FRAME THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks",),
                "slider_adjust_repeat_right_second_focus_restore_observe_push_input_release": ("ERROR: SLIDER PUSH INPUT RELEASE ASSERTION FAILED: expected no new receipt after eleven checks",),
                "health_gauge_disconnected": ("ERROR: Health gauge assertion failed: expected in-tree TextureProgressBar value=35 value_changed=1 receipt=35",),
                "animation_stuck": ("ERROR: ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance,",),
                "tween_no_start": ("ERROR: TWEEN ASSERTION FAILED: modulate did not show flash then return to baseline,",),
                "export_preset_missing": ("ERROR: Invalid export preset name: Missing preset.",),
                "contact_no_collision": ("ERROR: CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3,",),
                "audio_no_play": ("ERROR: AUDIO ASSERTION FAILED: expected in-tree player playback to advance,",),
            }.get(name, ())
            classifier = classify_audio_process if name == "audio_playback" else classify_process
            passed = detected if mutate else classifier(code, error, output, expected_exit, evidence, expected_errors)
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
            executable = (out_dir / "fixture-launch.x86_64").resolve()
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

    if args.probe_stream_attribution:
        def run_process_streams(command, timeout_seconds):
            try:
                proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
                return proc.stdout, proc.stderr, proc.returncode, None
            except subprocess.TimeoutExpired as exc:
                out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                return out, err, None, f"TIMEOUT after {timeout_seconds} seconds"
            except OSError as exc:
                return "", str(exc), None, f"launch error: {exc}"

        stdout_sig = "STREAM_STDOUT: expected attribution marker"
        stderr_diag = "STREAM_STDERR: unrelated attribution diagnostic"
        probe_results = []
        for label, flags in (("stream_accept", []),
                             ("stream_reject", ["--stderr-unrelated"])):
            command = [args.godot, "--headless", "--path", str(scratch), "--script",
                       "res://stream_attribution_probe.gd", "--", *flags]
            stdout, stderr, code, error = run_process_streams(command, 8)
            inner = classify_streams(code, error, stdout, stderr, 0, stdout_sig, allowed_stderr=())
            record = {
                "case": label,
                "command": command,
                "expected_exit": 0,
                "actual_exit": code,
                "error": error,
                "signature": stdout_sig,
                "inner_classification": inner,
                "raw_stdout": stdout,
                "raw_stderr": stderr,
                "raw_stdout_lines": stdout.strip().splitlines() if stdout else [],
                "raw_stderr_lines": stderr.strip().splitlines() if stderr else [],
            }
            probe_results.append(record)
            print(f"{'PASS' if inner else 'FAIL'} {label}: exit={code} classification={inner}", flush=True)

        accept, reject = probe_results

        def has_exact_stdout(record, marker_text):
            return any(line.strip() == marker_text for line in record["raw_stdout_lines"])

        def has_exact_stderr(record, marker_text):
            return any(line.strip() == marker_text for line in record["raw_stderr_lines"])

        script_paths = [record["command"][record["command"].index("--script") + 1]
                        for record in probe_results]
        same_script = (len(set(script_paths)) == 1
                       and script_paths[0] == "res://stream_attribution_probe.gd")
        accept_stdout_ok = has_exact_stdout(accept, stdout_sig)
        reject_stdout_ok = has_exact_stdout(reject, stdout_sig)
        accept_no_stderr_diag = not has_exact_stderr(accept, stderr_diag)
        reject_has_stderr_diag = has_exact_stderr(reject, stderr_diag)
        same_exit = accept["actual_exit"] == reject["actual_exit"] == 0
        meta_pass = (
            accept["inner_classification"] is True
            and reject["inner_classification"] is False
            and accept_stdout_ok and reject_stdout_ok
            and accept_no_stderr_diag and reject_has_stderr_diag
            and same_exit and same_script
            and accept["error"] is None and reject["error"] is None
        )
        probe_payload = {
            "mode": "real_godot_stream_attribution",
            "same_script": same_script,
            "script_paths": script_paths,
            "stdout_signature": stdout_sig,
            "stderr_diagnostic": stderr_diag,
            "results": probe_results,
            "accept_emitted_stdout_marker": accept_stdout_ok,
            "reject_emitted_stdout_marker": reject_stdout_ok,
            "accept_lacks_stderr_diagnostic": accept_no_stderr_diag,
            "reject_emitted_stderr_diagnostic": reject_has_stderr_diag,
            "same_exit_zero": same_exit,
            "verdict": "PASS" if meta_pass else "FAIL",
            "bounded_claim": (
                "one Godot 4.7.2 headless stream-attribution pair; "
                "not crash classification, not process-tree timeout, "
                "not export reliability, not rendered output"
            ),
        }
        artifact = run_dir / "stream-attribution-verdicts.json"
        artifact.write_text(json.dumps(probe_payload, indent=2) + "\n")
        results.append({
            "case": "probe_stream_attribution",
            "verdict": probe_payload["verdict"],
            "artifact": str(artifact),
            "inner_classifications": [r["inner_classification"] for r in probe_results],
        })
        print(f"{probe_payload['verdict']} stream attribution probe: {artifact}")

    if args.probe_crash_exit:
        marker_text = "CRASH_EXIT_PROBE: expected signature"
        script_path = "res://crash_exit_probe.gd"
        timeout_seconds = 8
        cleanup_seconds = 3
        expected_exit = 1
        probe_results = []
        accept_command = [args.godot, "--headless", "--path", str(scratch), "--script",
                          script_path, "--"]
        accept_output, accept_code, accept_error = run_process(accept_command, timeout_seconds)
        accept_classification = classify_process(accept_code, accept_error, accept_output,
                                                 expected_exit, marker_text)
        probe_results.append({"case": "crash_exit_accept", "command": accept_command,
                              "expected_exit": expected_exit, "actual_exit": accept_code,
                              "error": accept_error, "marker_observed": marker_text in accept_output,
                              "inner_classification": accept_classification,
                              "raw_output": accept_output,
                              "raw_output_lines": accept_output.strip().splitlines()})

        reject_command = [args.godot, "--headless", "--path", str(scratch), "--script",
                          script_path, "--", "--hold-open"]
        reject = {"case": "crash_exit_signal_reject", "command": reject_command,
                  "expected_exit": expected_exit, "signal_name": "SIGTERM", "timeout_seconds": timeout_seconds,
                  "cleanup_seconds": cleanup_seconds, "actual_exit": None,
                  "error": None, "marker_observed": False, "process_was_running": False,
                  "signal_sent": False, "inner_classification": False,
                  "raw_stdout": "", "raw_stderr": ""}
        process = None
        try:
            if os.name != "posix" or not hasattr(signal, "SIGTERM"):
                reject["error"] = "SIGTERM probe unsupported on this platform"
            else:
                process = subprocess.Popen(reject_command, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True, bufsize=1)
                selector = selectors.DefaultSelector()
                selector.register(process.stdout, selectors.EVENT_READ)
                deadline = time.monotonic() + timeout_seconds
                observed_line = False
                while time.monotonic() < deadline and not observed_line:
                    if process.poll() is not None:
                        break
                    events = selector.select(min(0.1, max(0.0, deadline - time.monotonic())))
                    for key, _ in events:
                        line = key.fileobj.readline()
                        if line:
                            reject["raw_stdout"] += line
                            observed_line = line.strip() == marker_text
                selector.close()
                reject["marker_observed"] = observed_line
                reject["process_was_running"] = process.poll() is None
                if not reject["marker_observed"]:
                    reject["error"] = "marker not observed before bounded timeout or process exit"
                elif not reject["process_was_running"]:
                    reject["error"] = "process was not live after marker observation"
                else:
                    process.send_signal(signal.SIGTERM)
                    reject["signal_sent"] = True
                try:
                    remaining_out, reject["raw_stderr"] = process.communicate(timeout=cleanup_seconds)
                    reject["raw_stdout"] += remaining_out
                except subprocess.TimeoutExpired:
                    reject["error"] = "signal cleanup timed out; forced kill used"
                    process.kill()
                    remaining_out, reject["raw_stderr"] = process.communicate(timeout=cleanup_seconds)
                    reject["raw_stdout"] += remaining_out
                reject["actual_exit"] = process.returncode
                if reject["signal_sent"] and process.returncode == -signal.SIGTERM:
                    reject["inner_classification"] = classify_process(
                        process.returncode, None, reject["raw_stdout"] + reject["raw_stderr"],
                        expected_exit, marker_text)
                elif reject["signal_sent"] and reject["error"] is None:
                    reject["error"] = f"expected return code {-signal.SIGTERM}, got {process.returncode}"
        except (OSError, ValueError) as exc:
            reject["error"] = f"signal probe launch/read error: {exc}"
            if process is not None and process.poll() is None:
                process.kill()
                try:
                    out, err = process.communicate(timeout=cleanup_seconds)
                    reject["raw_stdout"] += out
                    reject["raw_stderr"] += err
                    reject["actual_exit"] = process.returncode
                except subprocess.TimeoutExpired:
                    reject["error"] += "; forced cleanup timed out"
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                try:
                    out, err = process.communicate(timeout=cleanup_seconds)
                    reject["raw_stdout"] += out
                    reject["raw_stderr"] += err
                    reject["actual_exit"] = process.returncode
                except subprocess.TimeoutExpired:
                    reject["error"] = (reject["error"] or "") + "; bounded forced cleanup timed out"
        probe_results.append(reject)
        accept = probe_results[0]
        same_script = all(record["command"][record["command"].index("--script") + 1] == script_path
                          for record in probe_results)
        same_marker = all(record.get("marker_observed") for record in probe_results)
        same_expected_exit = all(record["expected_exit"] == expected_exit for record in probe_results)
        meta_pass = (accept["inner_classification"] is True
                     and reject["inner_classification"] is False
                     and reject["process_was_running"] and reject["signal_sent"]
                     and reject["actual_exit"] == -signal.SIGTERM
                     and reject["error"] is None and same_script and same_marker and same_expected_exit)
        probe_payload = {"mode": "real_godot_crash_exit", "platform": sys.platform,
                         "signal": "SIGTERM", "signal_return_code": -signal.SIGTERM,
                         "same_script": same_script, "same_expected_exit": same_expected_exit,
                         "signature": marker_text, "results": probe_results,
                         "bounded_claim": "one real Godot normal exit versus POSIX SIGTERM; no general crash or process-tree guarantee",
                         "verdict": "PASS" if meta_pass else "FAIL"}
        artifact = run_dir / "crash-exit-verdicts.json"
        artifact.write_text(json.dumps(probe_payload, indent=2) + "\n")
        results.append({"case": "probe_crash_exit", "verdict": probe_payload["verdict"],
                        "artifact": str(artifact),
                        "inner_classifications": [r["inner_classification"] for r in probe_results]})
        print(f"{probe_payload['verdict']} crash-exit probe: {artifact}")

    if args.probe_timeout:
        marker_text = "TIMEOUT_PROBE: expected signature"
        script_path = "res://timeout_probe.gd"
        old_timeout_seconds = 0.75
        measured_delay_seconds = 1.5
        timeout_seconds = 3.0
        cleanup_seconds = 3
        expected_exit = 0
        def bounded_run(case, extra_args, bound):
            command = [args.godot, "--headless", "--path", str(scratch), "--script",
                       script_path, "--"] + extra_args
            record = {"case": case, "command": command, "expected_exit": expected_exit,
                      "timeout_seconds": bound, "cleanup_seconds": cleanup_seconds,
                      "actual_exit": None, "error": None, "marker_observed": False,
                      "timed_out": False, "process_was_running": False,
                      "direct_child_alive_after_cleanup": None, "raw_stdout": "", "raw_stderr": ""}
            process = None
            started_at = time.monotonic()
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True, bufsize=1)
                try:
                    out, err = process.communicate(timeout=bound)
                    record["raw_stdout"], record["raw_stderr"] = out, err
                    record["actual_exit"] = process.returncode
                except subprocess.TimeoutExpired as exc:
                    record["timed_out"] = True
                    out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                    err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                    record["raw_stdout"], record["raw_stderr"] = out, err
                    record["marker_observed"] = marker_text in out
                    record["process_was_running"] = process.poll() is None
                    record["error"] = f"TIMEOUT after {bound} seconds"
                    if process.poll() is None:
                        process.kill()
                    more_out, more_err = process.communicate(timeout=cleanup_seconds)
                    record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
                    record["cleanup_exit_code"] = process.returncode
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                record["error"] = f"launch/read/cleanup error: {exc}"
                if process is not None and process.poll() is None:
                    process.kill()
                    try:
                        process.communicate(timeout=cleanup_seconds)
                    except subprocess.TimeoutExpired:
                        record["error"] += "; direct-child cleanup timed out"
            finally:
                if process is not None:
                    record["actual_exit"] = None if record["timed_out"] else process.poll()
                    record["direct_child_alive_after_cleanup"] = process.poll() is None
            record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
            record["marker_observed"] = marker_text in record["raw_stdout"]
            record["inner_classification"] = classify_process(
                record["actual_exit"], record["error"], record["raw_stdout"] + record["raw_stderr"],
                expected_exit, marker_text)
            return record

        old_positive = bounded_run("slow_clean_old_bound", ["--delay-clean"], old_timeout_seconds)
        new_positive = bounded_run("slow_clean_new_bound", ["--delay-clean"], timeout_seconds)
        hold_open = bounded_run("hold_open_new_bound", ["--hold-open"], timeout_seconds)
        probe_results = [old_positive, new_positive, hold_open]
        old_rejects = (old_positive["timed_out"] and old_positive["marker_observed"]
                       and old_positive["inner_classification"] is False
                       and old_positive["direct_child_alive_after_cleanup"] is False)
        new_accepts = (not new_positive["timed_out"] and new_positive["actual_exit"] == expected_exit
                       and new_positive["marker_observed"]
                       and new_positive["inner_classification"] is True)
        hold_rejects = (hold_open["timed_out"] and hold_open["marker_observed"]
                        and hold_open["inner_classification"] is False
                        and hold_open["direct_child_alive_after_cleanup"] is False)
        same_script = all(record["command"][record["command"].index("--script") + 1] == script_path
                          for record in probe_results)
        same_expected_exit = all(record["expected_exit"] == expected_exit for record in probe_results)
        meta_pass = old_rejects and new_accepts and hold_rejects and same_script and same_expected_exit
        probe_payload = {"mode": "real_godot_timeout_three_arm", "platform": sys.platform,
                         "same_script": same_script, "same_expected_exit": same_expected_exit,
                         "signature": marker_text, "results": probe_results,
                         "constants": {"old_timeout_seconds": old_timeout_seconds,
                                       "measured_delay_seconds": measured_delay_seconds,
                                       "new_timeout_seconds": timeout_seconds,
                                       "cleanup_seconds": cleanup_seconds},
                         "bounded_claim": "controlled delayed clean startup is rejected by old bound and accepted by new bound; hold-open marker still times out; direct child cleanup only",
                         "verdict": "PASS" if meta_pass else "FAIL"}
        artifact = run_dir / "timeout-verdicts.json"
        artifact.write_text(json.dumps(probe_payload, indent=2) + "\n")
        results.append({"case": "probe_timeout", "verdict": probe_payload["verdict"],
                        "artifact": str(artifact),
                        "inner_classifications": [r["inner_classification"] for r in probe_results]})
        print(f"{probe_payload['verdict']} timeout probe: {artifact}")

    payload = {"godot": args.godot, "seed": str(HERE), "scratch": str(scratch),
               "probe_failing": args.probe_failing, "results": results,
               "verdict": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL"}
    (run_dir / "verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{payload['verdict']} battery: {run_dir / 'verdicts.json'}")
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
