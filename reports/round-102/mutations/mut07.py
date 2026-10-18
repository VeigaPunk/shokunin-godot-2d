#!/usr/bin/env python3
"""mut07 — M7: harness-dead class on export_launch (round 102).

A fixture that silently no-ops (exit 0, prints nothing) must make its battery
row FAIL, not vacuously PASS. This driver measures the class against:

  * `blank`      — a blank SceneTree fixture run through the exact CASES
                   execute() command shape (run_battery.py:1892-1921) and the
                   production classifier (run_battery.py:1775-1792).
  * `probe-base` — the committed `probe_export_launch` block (run_battery.py:
                   4510-4601), unmutated: live control.
  * `probe-dead` — the same block with the positive arm's startup-event print
                   stripped (silent no-op): the mutant. Verdict must be FAIL.

Never executes the shared `corpus/fixtures/run_battery.py`; never writes inside
the lane repo. All state lives under /var/tmp/r102-mut7/. Usage:

    python3 reports/round-102/mutations/mut07.py all
    python3 reports/round-102/mutations/mut07.py blank --signature 'PASS export_launch ...'

The helper bodies are copies of the nested helpers in run_battery.py at the
sha256 recorded in each receipt; the helpers are nested functions, so they
cannot be imported. This driver runs them, not the battery.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "corpus" / "fixtures"
BATTERY = FIXTURES / "run_battery.py"
WORK = Path("/var/tmp/r102-mut7")
GODOT = "godot"
EXPECTED_LAUNCH = "EXPORT_LAUNCH_READY scene=fixture"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_process(command, timeout_seconds, env=None):
    # Verbatim semantics of run_battery.py:1748-1757 (merged stdout+stderr);
    # the env parameter is a driver extension for EXPORT_LAUNCH_ROOT runs.
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, env=env)
        return proc.stdout + proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        output += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return output, None, f"TIMEOUT after {timeout_seconds} seconds"
    except OSError as exc:
        return str(exc), None, f"launch error: {exc}"


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    # Verbatim body of run_battery.py:1775-1792.
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


def receipt_base(phase):
    return {
        "phase": phase,
        "when": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "host": os.uname().nodename,
        "godot": subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip(),
        "battery_sha256": sha256(BATTERY),
        "head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                               capture_output=True, text=True).stdout.strip(),
    }


def write_receipt(name, payload):
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"receipt: {path}")
    return path


# ---------------------------------------------------------------- setup phase

def phase_setup(_args):
    if (WORK / "scratch").exists():
        shutil.rmtree(WORK / "scratch")
    scratch = WORK / "scratch"
    scratch.mkdir(parents=True)
    copied = 0
    for item in sorted(FIXTURES.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, scratch / item.name)
        else:
            shutil.copy2(item, scratch / item.name)
        copied += 1
    # Battery-faithful scratch post-processing (run_battery.py:1730-1745).
    project_file = scratch / "project.godot"
    project_text = project_file.read_text()
    project_text = project_text.replace('config/name="MechanicOneShotTest"',
                                        'config/name="MechanicOneShotTest-r102-mut7"', 1)
    project_file.write_text(project_text)
    shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")
    chain = scratch / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in text, "causal fixture changed; cannot apply scratch-only readiness fix"
    chain.write_text(text.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    # Warm the copied project's import cache once (battery scratch inherits it
    # from earlier rows; a fresh copy must be imported before exports).
    warm = run_process([GODOT, "--headless", "--path", str(scratch), "--import"], 180)
    payload = receipt_base("setup")
    payload.update({"scratch": str(scratch), "items_copied": copied,
                    "warm_import": {"exit": warm[1], "error": warm[2],
                                    "output_bytes": len(warm[0]),
                                    "output_tail": warm[0].strip().splitlines()[-3:]}})
    write_receipt("setup", payload)
    print(f"setup: copied={copied} warm_import_exit={warm[1]} scratch={scratch}")


# ---------------------------------------------------------------- blank phase

BLANK_UNIT = "extends SceneTree\n\nfunc _initialize() -> void:\n    quit(0)\n"


def phase_blank(args):
    scratch = WORK / "scratch"
    if not scratch.exists():
        sys.exit("run the setup phase first")
    blank = scratch / "blank_export_launch.gd"
    blank.write_text(BLANK_UNIT)
    # Exact CASES execute() command shape for a script row (run_battery.py:1912).
    command = [GODOT, "--headless", "--path", str(scratch), "--script",
               "res://blank_export_launch.gd", "--", "--arm=base"]
    started = time.time()
    output, code, error = run_process(command, 8)
    elapsed = round(time.time() - started, 3)
    signatures = [EXPECTED_LAUNCH] + list(args.signature or [])
    rows = []
    for signature in signatures:
        rows.append({
            "signature": signature,
            "expected_exit": 0,
            "classification": classify_process(code, error, output, 0, signature),
        })
    # Positive control: the same capture + the marker must classify True, so a
    # False below is the row's signature check, not a blanket-reject classifier.
    control = classify_process(code, error, output + "\n" + EXPECTED_LAUNCH + "\n", 0, EXPECTED_LAUNCH)
    payload = receipt_base("blank")
    payload.update({
        "unit": BLANK_UNIT,
        "command": command,
        "actual_exit": code,
        "error": error,
        "elapsed_seconds": elapsed,
        "fixture_bytes_stdout": len(output),
        "fixture_output_lines": output.strip().splitlines(),
        "rows": rows,
        "marker_append_control": control,
        "verdict": "PASS" if (error is None and code == 0
                              and all(not r["classification"] for r in rows) and control) else "FAIL",
    })
    write_receipt("blank", payload)
    print(f"blank unit: exit={code} bytes={len(output)} rows="
          f"{[(r['signature'][:40], r['classification']) for r in rows]} "
          f"control={control} verdict={payload['verdict']}")


# ---------------------------------------------------------------- probe phase

def phase_probe(variant, dead_positive):
    scratch = WORK / "scratch"
    if not scratch.exists():
        sys.exit("run the setup phase first")
    launch_root = WORK / f"probe-{variant}" / "export-launch"
    if (WORK / f"probe-{variant}").exists():
        shutil.rmtree(WORK / f"probe-{variant}")
    positive = launch_root / "positive"
    negative = launch_root / "negative"
    shutil.copytree(scratch, positive, ignore=shutil.ignore_patterns(".godot", "out"))
    shutil.copytree(scratch, negative, ignore=shutil.ignore_patterns(".godot", "out"))
    expected_launch = EXPECTED_LAUNCH

    def configure_launch(project, with_event):
        # Body copied from run_battery.py:4522-4531; MUTANT: in dead mode the
        # positive arm's startup-event print is stripped, converting the
        # launched app into a silent no-op (extends Node -> quit(), no bytes).
        scene = project / "export_launch.tscn"
        script = project / "export_launch.gd"
        scene.write_text('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://export_launch.gd" id="1"]\n\n[node name="ExportLaunch" type="Node"]\nscript = ExtResource("1")\n')
        event_code = ('    print("EXPORT_LAUNCH_READY scene=fixture")\n' if with_event else '')
        if dead_positive and with_event:
            event_code = ''
        script.write_text('extends Node\n\nfunc _ready() -> void:\n' + event_code + '    get_tree().quit()\n')
        project_file = project / "project.godot"
        config = project_file.read_text()
        config = config.replace('config/features=PackedStringArray("4.7")\n', 'config/features=PackedStringArray("4.7")\nrun/main_scene="res://export_launch.tscn"\n', 1)
        project_file.write_text(config)

    def launch_variant(label, project, with_event):
        # Body copied from run_battery.py:4533-4583.
        configure_launch(project, with_event)
        out_dir = project / "out"
        out_dir.mkdir(exist_ok=True)
        executable = (out_dir / "fixture-launch.x86_64").resolve()
        export_cmd = [GODOT, "--headless", "--path", str(project), "--export-debug", "Linux/X11", str(executable)]
        exp_output, exp_code, exp_error = run_process(export_cmd, 60)
        exp_ok = (classify_process(exp_code, exp_error, exp_output, 0, "[ DONE ]")
                  and "savepack" in exp_output and executable.is_file() and executable.stat().st_size > 0)
        export_bytes = executable.stat().st_size if executable.is_file() else 0
        pack_path = executable.with_suffix(".pck")
        pack_bytes = pack_path.stat().st_size if pack_path.is_file() else 0
        pack_sha256 = sha256(pack_path) if pack_bytes else None
        launch_cmd = [str(executable), "--headless"]
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
        executable_sha256 = sha256(executable) if executable.is_file() else None
        for item in list(out_dir.iterdir()):
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        return {"case": label, "expected_signature": expected_launch,
                "expected_startup_event": with_event, "export_command": export_cmd,
                "export_exit": exp_code, "export_error": exp_error,
                "export_output": exp_output.strip().splitlines(), "export_bytes": export_bytes,
                "executable_sha256": executable_sha256, "pack_bytes": pack_bytes,
                "pack_sha256": pack_sha256,
                "launch_command": launch_cmd, "launch_cwd": launch_cwd, "launch_exit": launch_code,
                "launch_error": launch_error, "launch_output": launch_output.strip().splitlines(),
                "clean_process_without_signature": clean_without_signature,
                "same_signature_assertion": asserted, "products_before_cleanup": products,
                "products_after_cleanup": sorted(item.name for item in out_dir.iterdir())}

    results = [launch_variant("export_launch_positive", positive, True),
               launch_variant("export_launch_missing_startup_event", negative, False)]
    # Verdict expression copied from run_battery.py:4587-4595.
    verdict = ("PASS" if results[0]["same_signature_assertion"]
               and results[1]["export_exit"] == 0
               and results[1]["export_bytes"] > 0
               and not results[1]["same_signature_assertion"]
               and results[1]["clean_process_without_signature"]
               and results[0]["pack_sha256"] != results[1]["pack_sha256"]
               and all(not r["products_after_cleanup"] for r in results) else "FAIL")
    clauses = {
        "positive_same_signature_assertion": results[0]["same_signature_assertion"],
        "negative_export_exit_zero": results[1]["export_exit"] == 0,
        "negative_export_bytes_nonzero": results[1]["export_bytes"] > 0,
        "negative_signature_absent": not results[1]["same_signature_assertion"],
        "negative_clean_process_without_signature": results[1]["clean_process_without_signature"],
        "pack_sha256_differs": results[0]["pack_sha256"] != results[1]["pack_sha256"],
        "products_cleaned": all(not r["products_after_cleanup"] for r in results),
    }
    payload = receipt_base(f"probe-{variant}")
    payload.update({"mutation": ("positive startup-event print stripped (silent no-op)"
                                 if dead_positive else "none (committed block)"),
                    "clauses": clauses, "results": results, "verdict": verdict})
    write_receipt(f"probe-{variant}", payload)
    print(f"probe-{variant}: verdict={verdict} clauses={clauses}")


def phase_quit_after(_args):
    """Surface B': silent non-quitting app run with --quit-after frames.

    Models the E1/E2 row shape (self-contained binary + `--quit-after N`):
    the launched app is a silent no-op (`_ready()` does nothing), so the only
    possible exit path is the engine's frame bound.
    """
    scratch = WORK / "scratch"
    if not scratch.exists():
        sys.exit("run the setup phase first")
    root = WORK / "quit-after"
    if root.exists():
        shutil.rmtree(root)
    project = root / "project"
    shutil.copytree(scratch, project, ignore=shutil.ignore_patterns(".godot", "out"))
    scene = project / "export_launch.tscn"
    script = project / "export_launch.gd"
    scene.write_text('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://export_launch.gd" id="1"]\n\n[node name="ExportLaunch" type="Node"]\nscript = ExtResource("1")\n')
    script.write_text('extends Node\n\nfunc _ready() -> void:\n    pass\n')
    project_file = project / "project.godot"
    config = project_file.read_text()
    config = config.replace('config/features=PackedStringArray("4.7")\n', 'config/features=PackedStringArray("4.7")\nrun/main_scene="res://export_launch.tscn"\n', 1)
    project_file.write_text(config)
    out_dir = project / "out"
    out_dir.mkdir(exist_ok=True)
    executable = (out_dir / "fixture-quit-after.x86_64").resolve()
    export_cmd = [GODOT, "--headless", "--path", str(project), "--export-debug", "Linux/X11", str(executable)]
    exp_output, exp_code, exp_error = run_process(export_cmd, 60)
    exp_ok = (classify_process(exp_code, exp_error, exp_output, 0, "[ DONE ]")
              and "savepack" in exp_output and executable.is_file() and executable.stat().st_size > 0)
    bounded = run_process([str(executable), "--headless", "--quit-after", "2"], 8)
    unbounded = run_process([str(executable), "--headless"], 4) if exp_ok else ("", None, "export failed")
    classification = classify_process(bounded[1], bounded[2], bounded[0], 0, EXPECTED_LAUNCH)
    payload = receipt_base("quit-after")
    payload.update({
        "app_script": script.read_text(),
        "export_command": export_cmd, "export_exit": exp_code, "export_error": exp_error,
        "export_bytes": executable.stat().st_size if executable.is_file() else 0,
        "bounded_command": [str(executable), "--headless", "--quit-after", "2"],
        "bounded_exit": bounded[1], "bounded_error": bounded[2],
        "bounded_output_lines": bounded[0].strip().splitlines(),
        "marker_present": EXPECTED_LAUNCH in bounded[0],
        "row_classification_against_marker": classification,
        "unbounded_command": [str(executable), "--headless"],
        "unbounded_exit": unbounded[1], "unbounded_error": unbounded[2],
        "verdict": ("PASS" if exp_ok and bounded[1] == 0 and bounded[2] is None
                    and EXPECTED_LAUNCH not in bounded[0] and not classification
                    and unbounded[2] is not None else "FAIL"),
    })
    write_receipt("quit-after", payload)
    print(f"quit-after: exp_ok={exp_ok} bounded_exit={bounded[1]} marker={payload['marker_present']} "
          f"classification={classification} unbounded_error={unbounded[2]!r} verdict={payload['verdict']}")


def phase_rows(_args):
    """Surface A against the final row registry (run after integration).

    Imports a scratch copy of run_battery.py (never executes main), discovers
    `export_launch*` CASES rows, blanks each executor in the scratch copy only,
    runs the exact row command, and classifies with the row's own
    expected_exit/signature.
    """
    scratch = WORK / "scratch"
    if not scratch.exists():
        sys.exit("run the setup phase first")
    snapshot = WORK / "rb_snapshot.py"
    shutil.copy2(BATTERY, snapshot)
    sys.path.insert(0, str(WORK))
    import rb_snapshot as mod
    banner = "Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf"
    discovered = [c for c in mod.CASES if str(c[1]).startswith("export_launch")]
    rows, hygiene = [], []
    for name, script, flags, expected_exit, signature in discovered:
        target = scratch / script
        if not target.is_file():
            rows.append({"case": name, "script": script, "blank_unit_not_applied": True})
            continue
        if not str(signature).strip() or str(signature) in banner:
            hygiene.append({"case": name, "signature": signature,
                            "risk": "empty or engine-banner substring can vacuous-pass on silence"})
        original = target.read_bytes()
        original_sha = hashlib.sha256(original).hexdigest()
        target.write_text(BLANK_UNIT)
        command = [GODOT, "--headless", "--path", str(scratch), "--script", "res://" + script, "--", *flags]
        output, code, error = run_process(command, 8)
        target.write_bytes(original)
        restored_sha = sha256(target)
        rows.append({"case": name, "script": script, "flags": list(flags),
                     "expected_exit": expected_exit, "signature": signature,
                     "fixture_sha_before": original_sha, "fixture_sha_after_restore": restored_sha,
                     "command": command, "actual_exit": code, "error": error,
                     "fixture_bytes": len(output), "output_lines": output.strip().splitlines(),
                     "classification": classify_process(code, error, output, expected_exit, signature)})
    measured = [r for r in rows if "classification" in r]
    if not discovered:
        verdict = "NO_ROWS"
    elif any(r.get("blank_unit_not_applied") for r in rows):
        verdict = "INCOMPLETE"
    else:
        verdict = "PASS" if all(not r["classification"] for r in measured) and not hygiene else "FAIL"
    payload = receipt_base("rows")
    payload.update({"rows_found": len(discovered), "rows": rows, "hygiene": hygiene, "verdict": verdict})
    write_receipt("rows", payload)
    print(f"rows: found={len(discovered)} measured={len(measured)} "
          f"classifications={[r['classification'] for r in measured]} hygiene={len(hygiene)} verdict={verdict}")


def phase_fixture_row(args):
    """Blank a real fixture (scratch copy only) and classify its own PASS lines.

    Live control first: run the fixture unmutated and collect every `PASS ...`
    line it emits. Then overwrite the scratch copy with BLANK_UNIT, rerun the
    same command, and classify the blank capture against each collected PASS
    line plus any --signature given. Every classification must be False (the
    row FAILs) for the phase to pass.
    """
    scratch = WORK / "scratch"
    fixture = scratch / args.fixture
    if not fixture.is_file():
        sys.exit(f"fixture not found in scratch: {fixture}")
    flags = list(args.flag or [])
    command = [GODOT, "--headless", "--path", str(scratch), "--script",
               "res://" + args.fixture, "--", *flags]
    env = os.environ.copy()
    env["EXPORT_LAUNCH_ROOT"] = str(WORK / (args.fixture.removesuffix(".gd") + "-root"))
    real_output, real_code, real_error = run_process(command, args.timeout, env=env)
    pass_lines = [line.strip() for line in real_output.splitlines() if line.strip().startswith("PASS ")]
    signatures = pass_lines + list(args.signature or [])
    original = fixture.read_bytes()
    fixture.write_text(BLANK_UNIT)
    blank_output, blank_code, blank_error = run_process(command, 30, env=env)
    fixture.write_bytes(original)
    classifications = [{"signature": s,
                        "classification": classify_process(blank_code, blank_error, blank_output,
                                                           args.expect_exit, s)}
                       for s in signatures]
    payload = receipt_base("fixture-row")
    payload.update({
        "fixture": args.fixture, "fixture_sha256": hashlib.sha256(original).hexdigest(),
        "flags": flags, "expect_exit": args.expect_exit, "command": command,
        "live_control": {"exit": real_code, "error": real_error,
                         "output_lines": real_output.strip().splitlines(),
                         "pass_lines": pass_lines},
        "blank_run": {"exit": blank_code, "error": blank_error, "bytes": len(blank_output),
                      "output_lines": blank_output.strip().splitlines()},
        "classifications": classifications,
        "verdict": ("PASS" if real_code == args.expect_exit and pass_lines
                    and blank_code == 0 and all(not c["classification"] for c in classifications)
                    else "FAIL"),
    })
    slug = args.fixture.removesuffix(".gd") + "-" + "-".join(a.lstrip("-").replace("=", "_") for a in flags)
    write_receipt("fixture-row-" + slug, payload)
    print(f"fixture-row {slug}: live_exit={real_code} pass_lines={len(pass_lines)} "
          f"blank_exit={blank_code} classifications={[c['classification'] for c in classifications]} "
          f"verdict={payload['verdict']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["setup", "blank", "probe-base", "probe-dead",
                                          "quit-after", "fixture-row", "rows", "all"])
    parser.add_argument("--signature", action="append",
                        help="extra pinned row signature to classify against the blank capture")
    parser.add_argument("--fixture", help="fixture file name for the fixture-row phase")
    parser.add_argument("--flag", action="append", default=[],
                        help="one fixture flag for the fixture-row phase (repeatable)")
    parser.add_argument("--expect-exit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=120,
                        help="live-control timeout seconds for the fixture-row phase")
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    if args.phase in ("setup", "all"):
        phase_setup(args)
    if args.phase in ("blank", "all"):
        phase_blank(args)
    if args.phase in ("probe-base", "all"):
        phase_probe("base", dead_positive=False)
    if args.phase in ("probe-dead", "all"):
        phase_probe("dead", dead_positive=True)
    if args.phase in ("quit-after", "all"):
        phase_quit_after(args)
    if args.phase == "fixture-row":
        phase_fixture_row(args)
    if args.phase in ("rows", "all"):
        phase_rows(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
