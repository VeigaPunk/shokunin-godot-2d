#!/usr/bin/env python3
"""r104-mut5 — harness-dead class driver for the res_uid family (round 104).

Question (seat KEY=M5): if a `res_uid*` harness goes silently dead — fixture
body no-ops, prints nothing, or the script never lands — does the battery row
FAIL, or does it pass vacuously? This driver answers with measurements, using
the production row contract (`execute()` command shape + `classify_process`
body copied VERBATIM from `corpus/fixtures/run_battery.py` at the sha recorded
in every receipt).

Precedent: `reports/round-103/mutations/mut07.py` (harness-dead on export_div).
This is the same class, re-pointed at the res_uid family and with one extra
arm (`shape`) that proves the class on a scratch-authored res_uid-shaped probe
so the proof exists before the E-seat fixtures land.

Hard rules honoured: the shared `corpus/fixtures/run_battery.py` is NEVER
executed (never imported as `__main__` either); every artifact lives under
/var/tmp/r104-mut5/ (NOT /tmp: EDQUOT). The repo is read-only from here.

Phases:
  setup        stage /var/tmp/r104-mut5/scratch as a battery-faithful copy of
               corpus/fixtures (run_battery.py + dotfiles excluded; app name
               suffixed; pickup.tscn staged; causal_chain readiness patch).
               Also AST-diff the embedded classify_process against the live one.
  blank        generic harness-dead unit: blank fixture + res_uid row command
               shape, classified with the production classifier; includes the
               vacuity-shape controls (empty signature / banner signature).
  absent       the class by absence: row command with the fixture file missing.
  shape        res_uid-shaped harness-dead proof: a scratch-authored fixture
               that really calls ResourceUID (text_to_id/id_to_text/has_id),
               run live to collect its own PASS lines, then blanked; every
               collected line must classify False on the dead capture with a
               True positive control. Plus a registration-shaped tuple proof.
  rows         registry-driven: AST-extract CASES from a scratch copy of the
               live battery; for every res_uid* row blank the executor in the
               scratch copy and classify the blank capture with THAT row's
               expected_exit/signature; hygiene-check the signature for
               vacuous shapes. NO_ROWS + recipe when nothing is registered.
  fixture-row  per landed fixture: live control run (collect its own PASS
               lines), then blank the fixture and classify the dead capture
               against each collected line (must be False). --tag suffixes the
               receipt name so per-arm runs do not overwrite each other.

Receipts: <root>/receipts/<phase>[-<name>].json (raw bytes, exact commands,
shas); <root> = $R104_MUT5_ROOT, else /var/tmp/r104-mut5. Verdict convention
(r101/r102/r103-mut7): phase verdict PASS means the harness-dead unit was
correctly rejected (row-level FAIL).

Run examples:
  python3 reports/round-104/mutations/mut05.py setup
  python3 reports/round-104/mutations/mut05.py blank
  python3 reports/round-104/mutations/mut05.py absent --fixture res_uid_s01.gd
  python3 reports/round-104/mutations/mut05.py shape
  python3 reports/round-104/mutations/mut05.py rows
  python3 reports/round-104/mutations/mut05.py fixture-row --fixture res_uid_s01.gd --flag=--arm=census
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
import textwrap
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "corpus" / "fixtures"
BATTERY = FIXTURES / "run_battery.py"
ROOT = Path(os.environ.get("R104_MUT5_ROOT") or "/var/tmp/r104-mut5")
RECEIPTS = ROOT / "receipts"

BLANK_UNIT = """extends SceneTree

func _initialize() -> void:
	quit(0)
"""

# Scratch-authored res_uid-shaped probe. It really calls ResourceUID, so the
# kill proof below is over live UID code, not a stub. Output is byte-stable
# (fixed constants, no RIDs/addresses/paths) so the line is a portable pin.
SHAPE_UNIT = """extends SceneTree

const PIN_TEXT := "uid://bq3xk7y2n8v9m"

func _initialize() -> void:
	var arm := "base"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--arm="):
			arm = arg.substr("--arm=".length())
	var uid := ResourceUID.text_to_id(PIN_TEXT)
	var back := ResourceUID.id_to_text(uid)
	var has := ResourceUID.has_id(uid)
	print("PASS res_uid_shape arm=%s text_to_id=%d id_to_text=%s has_id=%s" % [arm, uid, back, str(has)])
	quit(0)
"""

BANNER_PREFIX = "Godot Engine v"


def sha256_file(path: Path):
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str):
    return hashlib.sha256(text.encode()).hexdigest()


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


def live_classify_source():
    """Return (source_text, line_no) of the live classify_process definition."""
    tree = ast.parse(BATTERY.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            lines = BATTERY.read_text().splitlines()
            return "\n".join(lines[node.lineno - 1:node.end_lineno]), node.lineno
    return None, None


def ast_body(source):
    tree = ast.parse(source)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
    return ast.dump(ast.Module(body=fn.body, type_ignores=[]))


# classify_process body copied VERBATIM from run_battery.py (sha recorded per receipt).
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
    for key, sub in (("TMPDIR", "tmp"), ("XDG_DATA_HOME", "xdg-data"),
                     ("XDG_CACHE_HOME", "xdg-cache"), ("XDG_CONFIG_HOME", "xdg-config")):
        path = ROOT / sub
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
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
        if item.name == "run_battery.py" or item.name.startswith(".") or item.name == "__pycache__":
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
    live_src, line_no = live_classify_source()
    fidelity = {"live_definition_line": line_no,
                "live_definition_sha256": sha256_text(live_src) if live_src else None,
                "ast_bodies_identical": None}
    if live_src:
        import inspect
        mine = inspect.getsource(classify_process)
        # strip the decorator-free def header: compare bodies only
        def body_of(src):
            # the live definition is nested inside main() -> its source is
            # indented; dedent before parsing.
            tree = ast.parse(textwrap.dedent(src))
            fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
            return ast.dump(ast.Module(body=fn.body, type_ignores=[]))
        fidelity["ast_bodies_identical"] = body_of(live_src) == body_of(mine)
    receipt("setup", {"stdout_tail": info.pop("import_tail"), **info, "classifier_fidelity": fidelity,
                      "verdict": "PASS" if info["import_exit"] == 0 else "FAIL"})


def phase_blank(args):
    scratch = scratch_dir()
    assert scratch.is_dir(), "run setup first"
    blank = scratch / "blank_res_uid.gd"
    blank.write_text(BLANK_UNIT)
    command = ["godot", "--headless", "--path", str(scratch), "--script", "res://blank_res_uid.gd", "--", "--arm=base"]
    run = run_row_command(command, 30, row_env())
    capture = run["stdout"] + run["stderr"]
    blank_sha = sha256_file(blank)
    sigs = args.signature or ["PASS res_uid", "PASS res_uid_s01", "PASS res_uid_shape", "RES_UID_READY"]
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
    vacuity_ok = all(v["classification_on_blank_capture"] for v in vacuity)  # holes reproduce BY CONSTRUCTION
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
    stash = target.with_suffix(target.suffix + ".mut05-stash")
    if target.exists():
        target.rename(stash)
    command = ["godot", "--headless", "--path", str(scratch), "--script", f"res://{fixture}", "--", *args.flag]
    run = run_row_command(command, 30, row_env())
    capture = run["stdout"] + run["stderr"]
    classification = classify_process(run["exit"], run["error"], capture, 0, "PASS res_uid")
    verdict = "PASS" if classification is False else "FAIL"
    if stash.exists():
        stash.rename(target)  # leave the scratch tree as the setup phase built it
    receipt(f"absent-{fixture}", {"verdict": verdict, "fixture_absent": fixture, "run": run,
                                  "classification_on_absent_capture": classification,
                                  "capture_bytes": len(capture.encode()), "capture_lines": capture.splitlines()})
    print(f"{verdict} absent ({fixture}: classification={classification}, exit={run['exit']})")
    return 0 if verdict == "PASS" else 1


def phase_shape(args):
    """res_uid-shaped harness-dead proof over a scratch-authored live probe."""
    scratch = scratch_dir()
    assert scratch.is_dir(), "run setup first"
    fixture = "res_uid_shape.gd"
    dst = scratch / fixture
    dst.write_text(SHAPE_UNIT)
    command = ["godot", "--headless", "--path", str(scratch), "--script", f"res://{fixture}", "--", "--arm=base"]
    live = run_row_command(command, 30, row_env())
    live_capture = live["stdout"] + live["stderr"]
    pass_lines = [line for line in live["stdout"].splitlines() if line.startswith("PASS ")]
    live_ok = classify_process(live["exit"], live["error"], live_capture, 0, pass_lines[0]) if pass_lines else False
    dst.write_text(BLANK_UNIT)
    dead = run_row_command(command, 30, row_env())
    dead_capture = dead["stdout"] + dead["stderr"]
    dst.write_text(SHAPE_UNIT)  # restore: the scratch tree must keep its live shape fixture
    matrix = [{"signature": line,
               "live_present": line in live_capture,
               "classification_on_dead_capture": classify_process(dead["exit"], dead["error"], dead_capture, 0, line),
               "positive_control_appended": classify_process(
                   dead["exit"], dead["error"], dead_capture + "\n" + line + "\n", 0, line)}
              for line in pass_lines]
    # registration-shaped tuple proof: the exact CASES tuple this row would get
    row_tuple = ["res_uid_shape_base", fixture, ["--arm=base"], 0, pass_lines[0] if pass_lines else None, []]
    hygiene = {"signature_empty": not pass_lines or pass_lines[0] == "",
               "signature_carries_engine_banner": any(BANNER_PREFIX in line for line in pass_lines),
               "signature_is_portable": all(str(ROOT) not in line for line in pass_lines),
               "dead_exit_equals_expected_exit": dead["exit"] == 0,
               "live_exit_equals_expected_exit": live["exit"] == 0}
    if not pass_lines:
        verdict = "NO_KILL_CLAIM"
    else:
        verdict = "PASS" if (live_ok and all((not m["classification_on_dead_capture"])
                                            and m["positive_control_appended"] for m in matrix)
                             and not hygiene["signature_empty"]
                             and not hygiene["signature_carries_engine_banner"]) else "FAIL"
    receipt("shape", {"verdict": verdict, "fixture": fixture, "fixture_sha256": sha256_text(SHAPE_UNIT),
                      "registered_row_tuple": row_tuple,
                      "live": {k: live[k] for k in ("exit", "error", "wall_seconds")},
                      "live_pass_lines": pass_lines, "live_capture_lines": live_capture.splitlines(),
                      "live_capture_bytes": len(live_capture.encode()),
                      "dead": {k: dead[k] for k in ("exit", "error", "wall_seconds")},
                      "dead_capture_bytes": len(dead_capture.encode()), "dead_capture_lines": dead_capture.splitlines(),
                      "signature_matrix": matrix, "hygiene": hygiene,
                      "production_row_timeout_seconds": 8,
                      "production_timeout_fits": None if live["error"] else live["wall_seconds"] < 8})
    print(f"{verdict} shape (live={live_ok}, pass_lines={len(pass_lines)}, "
          f"dead capture {len(dead_capture.encode())}B, "
          f"hygiene_bad={[k for k, v in hygiene.items() if v and k.startswith('signature_') and k != 'signature_is_portable']})")
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
    battery = Path(args.battery) if args.battery else BATTERY
    battery_copy = ROOT / "run_battery_scratch.py"
    shutil.copy2(battery, battery_copy)
    cases = extract_cases(battery_copy)
    rows = [r for r in cases if isinstance(r, (list, tuple)) and len(r) >= 5
            and str(r[1]).startswith(args.prefix)]
    result = {"verdict": None, "battery_sha256": sha256_file(battery), "battery_used": str(battery),
              "battery_copy": str(battery_copy), "cases_total": len(cases), "tag": args.tag,
              "rows_found": len(rows), "rows": []}
    receipt_name = "rows" + (f"-{args.tag}" if args.tag else "")
    if not rows:
        result["verdict"] = "NO_ROWS"
        result["recipe"] = ("after the res_uid* CASES splice lands: python3 reports/round-104/mutations/mut05.py "
                            "setup && python3 reports/round-104/mutations/mut05.py rows "
                            "(expect every res_uid* row classification_on_blank_capture=false)")
        receipt(receipt_name, result)
        print(f"NO_ROWS — {args.prefix}* CASES registration not landed yet (cases_total={len(cases)}); recipe recorded")
        return 0

    all_killed, hygiene_bad = True, []
    env = row_env()
    for row in rows:
        name, script, flags, expected_exit, signature = tuple(row[:5])
        allowed = tuple(row[5]) if len(row) > 5 and isinstance(row[5], (list, tuple)) else ()
        sig_members = tuple(signature) if isinstance(signature, (tuple, list)) else (signature,)
        hygiene = {"row": name, "signature_empty_member": any(s == "" for s in sig_members),
                   "signature_banner_or_prefix_1": any(BANNER_PREFIX in s for s in sig_members)}
        if hygiene["signature_empty_member"]:
            hygiene_bad.append(name)
        target = scratch / script
        fixture_present = target.exists()
        target_sha_before = sha256_file(target)
        original_bytes = target.read_bytes() if fixture_present else None
        command = ["godot", "--headless", "--path", str(scratch), "--script", f"res://{script}", "--", *flags]
        # live control first (fixture as-is): the row's own pin must classify True,
        # otherwise the kill below is vacuous (an unregistered/absent row fails
        # for the wrong reason). Only run it when the fixture is actually present.
        live_classification, live_run = None, None
        if fixture_present:
            live_run = run_row_command(command, args.timeout, env)
            live_capture = live_run["stdout"] + live_run["stderr"]
            live_classification = classify_process(live_run["exit"], live_run["error"], live_capture,
                                                   expected_exit, signature, allowed)
            target.write_bytes(original_bytes)
            target.write_text(BLANK_UNIT)
            run = run_row_command(command, args.timeout, env)
            # restore immediately: several rows can share one script, and a
            # blanked file would make the next row's live control vacuous.
            target.write_bytes(original_bytes)
        else:
            run = run_row_command(command, args.timeout, env)
        capture = run["stdout"] + run["stderr"]
        classification = classify_process(run["exit"], run["error"], capture, expected_exit, signature, allowed)
        killed = classification is False
        all_killed &= killed
        result["rows"].append({
            "row": name, "script": script, "flags": flags, "expected_exit": expected_exit,
            "signature": signature, "fixture_present": fixture_present,
            "fixture_sha256_before_blank": target_sha_before,
            "live_classification": live_classification,
            "live_capture_bytes": len((live_run["stdout"] + live_run["stderr"]).encode()) if live_run else None,
            "live_pass_lines": ([line for line in live_run["stdout"].splitlines()
                                 if line.startswith("PASS ")] if live_run else None),
            "classification_on_blank_capture": classification, "killed": killed,
            "run": {"exit": run["exit"], "error": run["error"], "wall_seconds": run["wall_seconds"],
                    "capture_bytes": len(capture.encode()), "capture_lines": capture.splitlines()},
            "hygiene": hygiene})
    result["hygiene_violations"] = hygiene_bad
    live_ok = all(r["live_classification"] is True for r in result["rows"] if r["fixture_present"])
    result["live_controls_all_true"] = live_ok
    result["verdict"] = "PASS" if all_killed and live_ok and not hygiene_bad else "FAIL"
    receipt(receipt_name, result)
    print(f"{result['verdict']} rows ({len(rows)} {args.prefix}* rows, all killed={all_killed}, "
          f"live controls true={live_ok}, hygiene violations={hygiene_bad})")
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
    shutil.copy2(src, dst)  # restore: later phases run against this scratch tree
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="phase", required=True)

    sub.add_parser("setup").set_defaults(func=phase_setup)

    p = sub.add_parser("blank")
    p.add_argument("--signature", action="append")
    p.set_defaults(func=phase_blank)

    p = sub.add_parser("absent")
    p.add_argument("--fixture", default="res_uid_s01.gd")
    p.add_argument("--flag", action="append", default=[])
    p.set_defaults(func=phase_absent)

    sub.add_parser("shape").set_defaults(func=phase_shape)

    p = sub.add_parser("rows")
    p.add_argument("--prefix", default="res_uid")
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--tag", default=None,
                   help="suffix the receipt name (rows-<tag>.json) so registry proofs do not overwrite the NO_ROWS receipt")
    p.add_argument("--battery", default=None,
                   help="battery source to AST-read CASES from (default: repo corpus/fixtures/run_battery.py); "
                        "used to exercise the registry path against a scratch splice without touching the repo")
    p.set_defaults(func=phase_rows)

    p = sub.add_parser("fixture-row")
    p.add_argument("--fixture", required=True)
    p.add_argument("--flag", action="append", default=[])
    p.add_argument("--timeout", type=int, default=200)
    p.add_argument("--tag", default=None)
    p.set_defaults(func=phase_fixture_row)

    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
