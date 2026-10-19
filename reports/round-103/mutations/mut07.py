#!/usr/bin/env python3
"""r103-mut7 — harness-dead class driver for the export_div family.

Question: if an `export_div*` harness goes silently dead (fixture body no-ops,
prints nothing, or the script never lands), does the battery row FAIL — or does
it pass vacuously? This driver answers with measurements, using the production
row contract (execute() shape + classify_process body copied VERBATIM from
corpus/fixtures/run_battery.py at the sha recorded in every receipt).

Hard rules honoured: the shared corpus/fixtures/run_battery.py is NEVER
executed (never imported as __main__ either); every artifact lives under
/var/tmp/r103-mut7/ (NOT /tmp: EDQUOT). The repo is read-only from here.

Phases:
  setup        stage /var/tmp/r103-mut7/scratch as a battery-faithful copy of
               corpus/fixtures (run_battery.py + dotfiles excluded; app name
               suffixed; pickup.tscn staged; causal_chain readiness patch).
  blank        generic harness-dead unit: blank fixture + row command shape,
               classified with the production classifier; includes the
               vacuity-shape controls (empty signature / banner signature).
  absent       the class by absence: row command with the fixture file missing.
  rows         registry-driven: AST-extract CASES from a scratch copy of the
               live battery; for every export_div* row blank the executor in
               the scratch copy and classify the blank capture with THAT row's
               expected_exit/signature; hygiene-check the signature for
               vacuous shapes. NO_ROWS + recipe when the splice has not landed.
  fixture-row  per landed fixture: live control run (collect its own PASS
               lines), then blank the fixture and classify the dead capture
               against each collected line (must be False). Auto-syncs the
               fixture from the repo into scratch. --tag suffixes the receipt
               name so per-arm runs do not overwrite each other.
  registered   registration-shaped kill proof: builds the row tuple the CASES
               splice will add — expected_exit / arity / allowed-errors taken
               from the landed neighbour rows of another family (observation),
               signature taken from the live PASS line — and demands
               classification True live, False dead, plus signature hygiene and
               the banner-signature counterfactual.

Receipts: <root>/receipts/<phase>[-<name>].json (raw bytes, exact commands,
shas); <root> = $R103_MUT7_ROOT, else /var/tmp/r103-mut7. Verdict convention
(r101/r102-mut7): phase verdict PASS means the harness-dead unit was correctly
rejected (row-level FAIL).

Run examples:
  python3 reports/round-103/mutations/mut07.py setup
  python3 reports/round-103/mutations/mut07.py blank
  python3 reports/round-103/mutations/mut07.py absent --fixture export_div.gd
  python3 reports/round-103/mutations/mut07.py rows
  python3 reports/round-103/mutations/mut07.py fixture-row --fixture export_div.gd --tag=iso
  python3 reports/round-103/mutations/mut07.py registered --fixture export_div_s02.gd --flag=--arm=iso
"""

import argparse
import ast
import datetime
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
# Keyed scratch root: R103_MUT7_ROOT overrides the historical default so a
# completion seat runs its own copy without clobbering prior-attempt receipts.
ROOT = Path(os.environ.get("R103_MUT7_ROOT") or "/var/tmp/r103-mut7")
RECEIPTS = ROOT / "receipts"

BLANK_UNIT = """extends SceneTree

func _initialize() -> void:
    quit(0)
"""

BANNER_PREFIX = "Godot Engine v"


def sha256_file(path: Path):
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def godot_version(godot="godot"):
    try:
        out = subprocess.run([godot, "--version"], capture_output=True, text=True, timeout=30)
        return (out.stdout + out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else None
    except Exception as exc:  # noqa: BLE001 - recorded, not raised
        return f"probe failed: {exc}"


def receipt(name, payload):
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    payload = dict(payload)
    payload.setdefault("phase", name)
    payload.setdefault("timestamp", datetime.datetime.now().isoformat(timespec="seconds"))
    payload.setdefault("battery_sha256", sha256_file(BATTERY))
    payload.setdefault("godot_version", godot_version())
    payload.setdefault("head", subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                                              capture_output=True, text=True).stdout.strip())
    path = RECEIPTS / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n")
    print(f"[receipt] {path}")
    return payload


# classify_process body copied VERBATIM from run_battery.py (main(), sha recorded per receipt).
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


def run_row_command(command, timeout_seconds, env):
    started = time.monotonic()
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, env=env)
        stdout, stderr, code, error = proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        code, error = None, f"TIMEOUT after {timeout_seconds} seconds"
    except OSError as exc:
        stdout, stderr, code, error = "", str(exc), None, f"launch error: {exc}"
    return {"command": command, "exit": code, "error": error,
            "stdout": stdout, "stderr": stderr, "wall_seconds": round(time.monotonic() - started, 3)}


def row_env():
    env = os.environ.copy()
    # quota-safe scratch for any TMPDIR-respecting fixture-root candidate.
    tmp = ROOT / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(tmp)
    return env


def scratch_dir():
    return ROOT / "scratch"


def setup_scratch(root: Path = ROOT):
    scratch = root / "scratch"
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    copied, skipped = 0, []
    for item in sorted(FIXTURES.iterdir(), key=lambda p: p.name):
        if item.name == "run_battery.py" or item.name.startswith("."):
            skipped.append(item.name)
            continue
        if item.name == "__pycache__":
            skipped.append(item.name)
            continue
        if item.is_dir():
            shutil.copytree(item, scratch / item.name)
        else:
            shutil.copy2(item, scratch / item.name)
        copied += 1
    # Battery-faithful staging (run_battery.py main() lines 1750-1762).
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    project_file = scratch / "project.godot"
    text = project_file.read_text()
    assert 'config/name="MechanicOneShotTest"' in text, "staging drift: app name anchor changed"
    project_file.write_text(text.replace('config/name="MechanicOneShotTest"',
                                         f'config/name="MechanicOneShotTest-{stamp}"', 1))
    shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")
    chain = scratch / "causal_chain.gd"
    anchor = "    await process_frame\n    var old := current_scene"
    ctext = chain.read_text()
    assert anchor in ctext, "staging drift: causal_chain anchor changed"
    chain.write_text(ctext.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    imp = subprocess.run(["godot", "--headless", "--path", str(scratch), "--import"],
                         capture_output=True, text=True, timeout=300)
    return {"scratch": str(scratch), "copied": copied, "skipped": skipped,
            "import_exit": imp.returncode, "import_tail": (imp.stdout + imp.stderr).strip().splitlines()[-3:]}


def phase_setup(_args):
    info = setup_scratch()
    receipt("setup", {"stdout_tail": info.pop("import_tail"), **info,
                      "verdict": "PASS" if info["import_exit"] == 0 else "FAIL"})


def phase_blank(args):
    scratch = scratch_dir()
    assert scratch.is_dir(), "run setup first"
    blank = scratch / "blank_export_div.gd"
    blank.write_text(BLANK_UNIT)
    command = ["godot", "--headless", "--path", str(scratch), "--script", "res://blank_export_div.gd", "--", "--arm=base"]
    run = run_row_command(command, 30, row_env())
    capture = run["stdout"] + run["stderr"]
    blank_sha = sha256_file(blank)
    sigs = args.signature or ["PASS export_div", "PASS export_div_s01", "EXPORT_DIV_READY"]
    rows = []
    for sig in sigs:
        rows.append({"signature": sig,
                     "classification_on_blank_capture": classify_process(run["exit"], run["error"], capture, 0, sig),
                     "positive_control_appended": classify_process(
                         run["exit"], run["error"], capture + "\n" + sig + "\n", 0, sig)})
    vacuity = [
        {"shape": "empty signature", "signature": "",
         "classification_on_blank_capture": classify_process(run["exit"], run["error"], capture, 0, "")},
        {"shape": "engine-banner signature", "signature": BANNER_PREFIX,
         "classification_on_blank_capture": classify_process(run["exit"], run["error"], capture, 0, BANNER_PREFIX)},
    ]
    kill_ok = all(not r["classification_on_blank_capture"] and r["positive_control_appended"] for r in rows)
    vacuity_ok = all(v["classification_on_blank_capture"] for v in vacuity)  # vacuity shapes MUST pass blank (that's why they are holes)
    verdict = "PASS" if kill_ok and vacuity_ok else "FAIL"
    receipt("blank", {"verdict": verdict, "blank_unit_sha256": blank_sha, "run": run,
                      "blank_capture_bytes": len(capture.encode()), "capture_lines": capture.splitlines(),
                      "signature_matrix": rows, "vacuity_shapes": vacuity,
                      "note": "vacuity_shapes classify True on a dead capture BY CONSTRUCTION; a row whose "
                              "signature is one of them would pass vacuously. Cleaner run = kill proof only."})
    print(f"{verdict} blank (harness-dead unit rejected={kill_ok}; vacuity shapes reproduce={vacuity_ok})")
    return 0 if verdict == "PASS" else 1


def phase_absent(args):
    scratch = scratch_dir()
    assert scratch.is_dir(), "run setup first"
    fixture = args.fixture
    target = scratch / fixture
    if target.exists():
        target.rename(target.with_suffix(target.suffix + ".mut07-stash"))
    command = ["godot", "--headless", "--path", str(scratch), "--script", f"res://{fixture}", "--", *args.flag]
    run = run_row_command(command, 30, row_env())
    capture = run["stdout"] + run["stderr"]
    classification = classify_process(run["exit"], run["error"], capture, 0, "PASS export_div")
    verdict = "PASS" if classification is False else "FAIL"
    receipt(f"absent-{fixture}", {"verdict": verdict, "fixture_absent": fixture, "run": run,
                                  "classification_on_absent_capture": classification,
                                  "capture_lines": capture.splitlines()})
    print(f"{verdict} absent ({fixture}: classification={classification}, exit={run['exit']})")
    return 0 if verdict == "PASS" else 1


def extract_cases(battery_copy: Path):
    tree = ast.parse(battery_copy.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("CASES not found in scratch battery copy")


def phase_rows(args):
    scratch = scratch_dir()
    assert scratch.is_dir(), "run setup first"
    battery_copy = ROOT / "run_battery_scratch.py"
    shutil.copy2(BATTERY, battery_copy)
    cases = extract_cases(battery_copy)
    rows = [r for r in cases if isinstance(r, (list, tuple)) and len(r) >= 5
            and str(r[1]).startswith(args.prefix)]
    result = {"verdict": None, "battery_sha256": sha256_file(BATTERY),
              "battery_copy": str(battery_copy), "cases_total": len(cases),
              "rows_found": len(rows), "rows": []}
    if not rows:
        result["verdict"] = "NO_ROWS"
        result["recipe"] = ("after the CASES splice lands: python3 reports/round-103/mutations/mut07.py "
                            "setup && python3 reports/round-103/mutations/mut07.py rows "
                            "(expect every export_div* row classification_on_blank_capture=false)")
        receipt("rows", result)
        print("NO_ROWS — export_div* CASES registration not landed yet; recipe recorded")
        return 0

    all_killed, hygiene_bad = True, []
    env = row_env()
    for name, script, flags, expected_exit, signature in [tuple(r[:5]) for r in rows]:
        allowed = tuple(r[5]) if len(r) > 5 and isinstance(r[5], (list, tuple)) else ()
        sig_members = tuple(signature) if isinstance(signature, (tuple, list)) else (signature,)
        hygiene = {"row": name, "signature_empty_member": any(s == "" for s in sig_members),
                   "signature_banner_or_prefix_1": any(BANNER_PREFIX in s for s in sig_members)}
        if hygiene["signature_empty_member"]:
            hygiene_bad.append(name)
        target = scratch / script
        fixture_present = target.exists()
        target_sha_before = sha256_file(target)
        if fixture_present:
            target.write_text(BLANK_UNIT)
        command = ["godot", "--headless", "--path", str(scratch), "--script", f"res://{script}", "--", *flags]
        run = run_row_command(command, args.timeout, env)
        capture = run["stdout"] + run["stderr"]
        classification = classify_process(run["exit"], run["error"], capture, expected_exit, signature, allowed)
        killed = classification is False
        all_killed &= killed
        result["rows"].append({
            "row": name, "script": script, "flags": flags, "expected_exit": expected_exit,
            "signature": signature, "fixture_present": fixture_present,
            "fixture_sha256_before_blank": target_sha_before,
            "classification_on_blank_capture": classification, "killed": killed,
            "run": {"exit": run["exit"], "error": run["error"], "wall_seconds": run["wall_seconds"],
                    "capture_bytes": len(capture.encode()), "capture_lines": capture.splitlines()},
            "hygiene": hygiene})
    result["hygiene_violations"] = hygiene_bad
    result["verdict"] = "PASS" if all_killed and not hygiene_bad else "FAIL"
    receipt("rows", result)
    print(f"{result['verdict']} rows ({len(rows)} export_div* rows, all killed={all_killed}, "
          f"hygiene violations={hygiene_bad})")
    return 0 if result["verdict"] == "PASS" else 1


def phase_fixture_row(args):
    scratch = scratch_dir()
    assert scratch.is_dir(), "run setup first"
    fixture = args.fixture
    src = FIXTURES / fixture
    assert src.is_file(), f"fixture not landed in repo: {src}"
    dst = scratch / fixture
    shutil.copy2(src, dst)
    command = ["godot", "--headless", "--path", str(scratch), "--script", f"res://{fixture}", "--", *args.flag]
    live = run_row_command(command, args.timeout, row_env())
    live_capture = live["stdout"] + live["stderr"]
    pass_lines = [line for line in live["stdout"].splitlines() if line.startswith("PASS ")]
    dst.write_text(BLANK_UNIT)
    dead = run_row_command(command, args.timeout, row_env())
    dead_capture = dead["stdout"] + dead["stderr"]
    matrix = [{"signature": line,
               "live_present": line in live_capture,
               "classification_on_dead_capture": classify_process(dead["exit"], dead["error"], dead_capture, 0, line),
               "positive_control_appended": classify_process(
                   dead["exit"], dead["error"], dead_capture + "\n" + line + "\n", 0, line)}
              for line in pass_lines]
    if not pass_lines:
        verdict = "NO_KILL_CLAIM"
    else:
        verdict = "PASS" if all((not m["classification_on_dead_capture"]) and m["positive_control_appended"] for m in matrix) else "FAIL"
    payload = {"verdict": verdict, "fixture": fixture, "fixture_sha256": sha256_file(src),
               "flags": args.flag, "tag": args.tag,
               "live": {k: live[k] for k in ("exit", "error", "wall_seconds")},
               "live_pass_lines": pass_lines, "live_capture_lines": live_capture.splitlines(),
               "dead": {k: dead[k] for k in ("exit", "error", "wall_seconds")},
               "dead_capture_bytes": len(dead_capture.encode()), "dead_capture_lines": dead_capture.splitlines(),
               "signature_matrix": matrix,
               "production_row_timeout_seconds": 8,
               "production_timeout_fits": None if live["error"] else live["wall_seconds"] < 8}
    receipt(f"fixture-row-{fixture}" + (f"-{args.tag}" if args.tag else ""), payload)
    print(f"{verdict} fixture-row {fixture} {args.flag} (live wall {live['wall_seconds']}s, "
          f"pass_lines={len(pass_lines)}, dead capture {payload['dead_capture_bytes']}B)")
    return 0 if verdict == "PASS" else 1


def extract_neighbours(battery_copy: Path, script_name: str):
    cases = extract_cases(battery_copy)
    return [tuple(r) for r in cases
            if isinstance(r, (list, tuple)) and len(r) >= 5 and r[1] == script_name]


def phase_registered(args):
    """Registration-shaped kill proof: build the row tuple the W5 CASES splice
    will add — expected_exit / arity / allowed-errors taken from the LANDED
    neighbour rows of the same family (observation, not assumption) — then show
    it PASSes on the live fixture and FAILs on a blanked one."""
    scratch = scratch_dir()
    assert scratch.is_dir(), "run setup first"
    fixture = args.fixture
    src = FIXTURES / fixture
    assert src.is_file(), f"fixture not landed in repo: {src}"
    battery_copy = ROOT / "run_battery_scratch.py"
    shutil.copy2(BATTERY, battery_copy)
    neighbours = extract_neighbours(battery_copy, args.neighbour_script)
    assert neighbours, f"no neighbour rows for script {args.neighbour_script}"
    exits = sorted({n[3] for n in neighbours})
    arities = sorted({len(n) for n in neighbours})
    allowed_forms = sorted({repr(tuple(n[5])) for n in neighbours if len(n) > 5})
    dst = scratch / fixture
    shutil.copy2(src, dst)
    expected_exit = args.expected_exit if args.expected_exit is not None else exits[0]
    command = ["godot", "--headless", "--path", str(scratch), "--script", f"res://{fixture}", "--", *args.flag]
    live = run_row_command(command, args.timeout, row_env())
    live_capture = live["stdout"] + live["stderr"]
    signature = args.signature or next((line for line in live["stdout"].splitlines()
                                       if line.startswith("PASS ")), None)
    assert signature, "no PASS line in the live capture to use as registration signature"
    allowed = tuple(args.allowed) if args.allowed else ()
    live_classification = classify_process(live["exit"], live["error"], live_capture,
                                          expected_exit, signature, allowed)
    dst.write_text(BLANK_UNIT)
    dead = run_row_command(command, args.timeout, row_env())
    dead_capture = dead["stdout"] + dead["stderr"]
    dead_classification = classify_process(dead["exit"], dead["error"], dead_capture,
                                           expected_exit, signature, allowed)
    weak_classification = classify_process(dead["exit"], dead["error"], dead_capture,
                                           expected_exit, BANNER_PREFIX, allowed)
    shutil.copy2(src, dst)
    hygiene = {"signature_empty": signature == "",
               "signature_carries_engine_banner": BANNER_PREFIX in signature,
               "dead_exit_equals_expected_exit": dead["exit"] == expected_exit,
               "live_exit_equals_expected_exit": live["exit"] == expected_exit}
    verdict = "PASS" if (live_classification is True and dead_classification is False
                         and not hygiene["signature_empty"]
                         and not hygiene["signature_carries_engine_banner"]) else "FAIL"
    payload = {"verdict": verdict, "fixture": fixture, "fixture_sha256": sha256_file(src),
               "registered_row_tuple": [args.row_name, fixture, args.flag, expected_exit, signature, list(allowed)],
               "neighbour_script": args.neighbour_script, "neighbour_count": len(neighbours),
               "neighbour_arities": arities, "neighbour_expected_exits": exits,
               "neighbour_allowed_forms": allowed_forms,
               "expected_exit_source": "args" if args.expected_exit is not None else "neighbour consensus",
               "live": {k: live[k] for k in ("exit", "error", "wall_seconds", "stdout")},
               "dead": {k: dead[k] for k in ("exit", "error", "wall_seconds")},
               "dead_capture_bytes": len(dead_capture.encode()), "dead_capture_lines": dead_capture.splitlines(),
               "classification_live": live_classification,
               "classification_dead": dead_classification,
               "classification_dead_with_banner_signature": weak_classification,
               "hygiene": hygiene,
               "production_row_timeout_seconds": 8,
               "production_timeout_fits": None if live["error"] else live["wall_seconds"] < 8}
    receipt(f"registered-{fixture}" + (f"-{args.tag}" if args.tag else ""), payload)
    print(f"{verdict} registered {fixture} (live={live_classification} dead={dead_classification} "
          f"dead_banner_signature={weak_classification})")
    return 0 if verdict == "PASS" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="phase", required=True)

    p = sub.add_parser("setup")
    p.set_defaults(func=phase_setup)

    p = sub.add_parser("blank")
    p.add_argument("--signature", action="append")
    p.set_defaults(func=phase_blank)

    p = sub.add_parser("absent")
    p.add_argument("--fixture", default="export_div.gd")
    p.add_argument("--flag", action="append", default=[])
    p.set_defaults(func=phase_absent)

    p = sub.add_parser("rows")
    p.add_argument("--prefix", default="export_div")
    p.add_argument("--timeout", type=int, default=120)
    p.set_defaults(func=phase_rows)

    p = sub.add_parser("fixture-row")
    p.add_argument("--fixture", required=True)
    p.add_argument("--flag", action="append", default=[])
    p.add_argument("--timeout", type=int, default=200)
    p.add_argument("--tag", default=None)
    p.set_defaults(func=phase_fixture_row)

    p = sub.add_parser("registered")
    p.add_argument("--fixture", required=True)
    p.add_argument("--flag", action="append", default=[])
    p.add_argument("--timeout", type=int, default=200)
    p.add_argument("--tag", default=None)
    p.add_argument("--row-name", default="export_div_s02_user_iso")
    p.add_argument("--signature", default=None)
    p.add_argument("--expected-exit", type=int, default=None)
    p.add_argument("--allowed", action="append", default=[])
    p.add_argument("--neighbour-script", default="export_launch.gd")
    p.set_defaults(func=phase_registered)

    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
