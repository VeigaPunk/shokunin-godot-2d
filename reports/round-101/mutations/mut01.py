#!/usr/bin/env python3
"""mut01.py — MUT-1 (round 101): forge an EXTRA LINE inside the r100b seq replay.

Closes r100-critic §F2 discrimination gap: the two `r100b_seq_*` CASES rows pin
exactly one line each of a 14-cell replay, so a forged extra line inside the
replay rides to PASS on the landed pins.

What this script does (all writes under --root, default /tmp/r101-mut1):
  1. builds a scratch copy of `corpus/fixtures` (minus run_battery.py/dotfiles),
     mirroring the harness's own scratch prep (project-name rewrite);
  2. extracts, from the *landed* harness bytes, the two `r100b_seq_*` rows
     (flags/expected_exit/signature) plus the harness's own `classify_process`
     body and the per-row `expected_errors` allowlist, so classification is the
     landed semantics, not a paraphrase;
  3. CONTROL run: unmutated fixture must classify both rows PASS (else INVALID —
     a broken launch must not be misread as a rejection);
  4. MUTANT runs: inject a forged extra print line into the replay loop of the
     scratch copy of `r100b_seq.gd`, re-run the same godot command, classify;
  5. prints ACCEPT (mutant survives: row PASS) / REJECT (row FAIL) vs --expect;
  6. also measures, on the mutant transcript bytes, whether three candidate
     post-fix pin shapes would reject it (simulation of the fix, labelled as
     such) — evidence for the C2 lander;
  7. asserts the repo fixture bytes are unchanged at exit (repo pristine).

Arms (--arm, default extra):
  extra        print("FORGED_EXTRA_CELL_OUTPUT") appended after the hover cell
  forged_cell  a forged line in the pin's own dialect, after the warp cell:
               print("PASS r100_gui warp FORGED_EXTRA_CELL_OUTPUT cursor=(99.0, 99.0)")

Usage:
  python3 reports/round-101/mutations/mut01.py --expect accept   # pre-fix: defect reproduces
  python3 reports/round-101/mutations/mut01.py --expect reject   # post-fix: fix is load-bearing

Exit code: 0 = expectation met, 1 = expectation not met, 2 = INVALID (control failed).
"""
import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]                     # <repo>/reports/round-101/mutations/mut01.py
FIXTURES = REPO / "corpus" / "fixtures"
SEQ_FIXTURE = "r100b_seq.gd"
ROWS = ("r100b_seq_clean", "r100b_seq_noclean")
REPLAY_CELLS = ("census", "routing", "hover", "motion", "localpos", "cursor", "clip",
                "drag", "touch", "subvp", "warp", "focus", "render", "osmeta")

FORGERIES = {
    # arm name: (anchor stripped-line, injected source line, printed token to look for)
    "extra": ("await _cell_hover()", 'print("FORGED_EXTRA_CELL_OUTPUT")',
              "FORGED_EXTRA_CELL_OUTPUT"),
    "forged_cell": ("await _cell_warp()",
                    'print("PASS r100_gui warp FORGED_EXTRA_CELL_OUTPUT cursor=(99.0, 99.0)")',
                    "FORGED_EXTRA_CELL_OUTPUT cursor=(99.0, 99.0)"),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(root: Path) -> dict:
    return {str(p.relative_to(root)): sha256_bytes(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def diff_snapshots(before: dict, after: dict) -> dict:
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in set(before) & set(after) if before[k] != after[k])
    return {"added": added, "removed": removed, "changed": changed,
            "clean": not (added or removed or changed)}


def harness_ast(harness: Path):
    return ast.parse(harness.read_text())


def extract_cases(tree):
    """CASES rows, from landed literal bytes (falls back to module import)."""
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "CASES"):
            try:
                return ast.literal_eval(node.value), "ast-literal"
            except ValueError:
                break
    import importlib.util
    spec = importlib.util.spec_from_file_location("mut01_harness", harness)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CASES, "module-import"


def extract_classify(tree):
    """The harness's own nested classify_process, compiled from landed source."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            mod = ast.Module(body=[node], type_ignores=[])
            ast.fix_missing_locations(mod)
            namespace = {}
            exec(compile(mod, "<harness classify_process>", "exec"), namespace)
            return namespace["classify_process"], True
    raise SystemExit("mut01: classify_process not found in harness — cannot classify")


def extract_allowlists(tree):
    """The per-row `{...}.get(name, ())` expected_errors dict, literal-evaluated."""
    out = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)):
            continue
        func = node.value.func
        if not (isinstance(func, ast.Attribute) and func.attr == "get"
                and isinstance(func.value, ast.Dict)):
            continue
        for key, value in zip(func.value.keys, func.value.values):
            try:
                out[ast.literal_eval(key)] = ast.literal_eval(value)
            except ValueError:
                continue
    return out


def build_scratch(root: Path, name: str, stamp: str, forge_arm: str, full_copy: bool = False):
    """Scratch project for the row's own launch shape.

    Minimal by default (project.godot + the fixture the row names): project.godot
    declares no autoloads/main scene (89 bytes, [application] only), so nothing
    else in `corpus/fixtures` is referenced by `--script res://r100b_seq.gd`.
    Kept small also because /tmp here is a 16G tmpfs shared by 64 seats and
    EDQUOT on a 1.9M copy was observed (this run, under host load).
    """
    scratch = root / name
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    if full_copy:
        for item in sorted(FIXTURES.iterdir()):
            if item.name == "run_battery.py" or item.name.startswith("."):
                continue
            if item.is_dir():
                shutil.copytree(item, scratch / item.name)
            else:
                shutil.copy2(item, scratch / item.name)
    else:
        shutil.copy2(FIXTURES / "project.godot", scratch / "project.godot")
        shutil.copy2(FIXTURES / SEQ_FIXTURE, scratch / SEQ_FIXTURE)
    project_file = scratch / "project.godot"
    text = project_file.read_text()
    project_file.write_text(text.replace('config/name="MechanicOneShotTest"',
                                         f'config/name="MechanicOneShotTest-{stamp}-{name}"', 1))
    fixture = scratch / SEQ_FIXTURE
    before = fixture.read_bytes()
    injected = None
    forged_token = None
    if forge_arm:
        anchor, source, token = FORGERIES[forge_arm]
        lines = before.split(b"\n")
        hits = [i for i, line in enumerate(lines) if line.strip() == anchor.encode()]
        if len(hits) != 1:
            raise SystemExit(f"mut01: anchor {anchor!r} matched {len(hits)} lines in {SEQ_FIXTURE}")
        index = hits[0]
        indent = lines[index][: len(lines[index]) - len(lines[index].lstrip())]
        lines.insert(index + 1, indent + source.encode())
        injected = source
        forged_token = token
        fixture.write_bytes(b"\n".join(lines))
    return scratch, before, fixture.read_bytes(), injected, forged_token


def run_row(godot: str, scratch: Path, flags, timeout: int):
    command = [godot, "--headless", "--path", str(scratch),
               "--script", "res://" + SEQ_FIXTURE, "--", *flags]
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        output = proc.stdout + proc.stderr
        return command, output, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return command, stdout + stderr, None, f"TIMEOUT after {timeout} seconds"
    except OSError as exc:
        return command, str(exc), None, f"launch error: {exc}"


def run_all_rows(args, cases, allowlists, classify, scratch: Path, writer: "SafeWriter",
                 stamp: str, tag: str):
    """Run every r100b_seq_* row in its own launch shape and classify it.

    Each row carries its own flags (`--clean=1` / `--clean=0`), which is exactly
    the distinction the two rows measure, so a single shared invocation cannot
    classify both.
    """
    per_row = {}
    for name in ROWS:
        row = next((c for c in cases if c[0] == name), None)
        if row is None:
            raise SystemExit(f"mut01: landed harness has no CASES row {name!r}")
        _, script, flags, expected_exit, signature = row[:5]
        if script != SEQ_FIXTURE:
            raise SystemExit(f"mut01: row {name!r} runs {script!r}, expected {SEQ_FIXTURE!r}")
        allowed = tuple(allowlists.get(name, ()))
        command, output, code, error = run_row(args.godot, scratch, flags, args.timeout)
        capture = writer.write_text(f"{stamp}-{tag}-{name}.txt", output)
        per_row[name] = {
            "name": name,
            "command": command,
            "flags": list(flags),
            "expected_exit": expected_exit,
            "signature_sha256": sha256_bytes(signature.encode()),
            "signature_lines": signature.count("\n") + 1,
            "exit_code": code,
            "error": error,
            "allowed_errors": list(allowed),
            "output": output,
            "output_capture": capture,
            "sha256_output": sha256_bytes(output.encode()),
            "transcript": transcript_shape(output),
            "verdict": "PASS" if classify(code, error, output, expected_exit, signature, allowed) else "FAIL",
        }
    return {"scratch": str(scratch), "rows": per_row}


def transcript_shape(frame: str):
    """Line census of the replay transcript: PASS lines, SEQ_DONE line, totals."""
    lines = frame.splitlines()
    pass_lines = [line for line in lines if line.startswith("PASS r100_gui ")]
    cells = [line.split()[2] for line in pass_lines]
    done = [line for line in lines if line.startswith("SEQ_DONE ")]
    return {
        "total_lines": len(lines),
        "pass_r100_gui_lines": len(pass_lines),
        "cells_in_order": cells,
        "seq_done_lines": done,
    }


def pin_shape_probe(mutant_frame: str, control_frame: str, baseline_lines: int):
    """Simulated post-fix pin shapes over the observed mutant transcript.

    LABELLED SIMULATION: candidate pin shapes computed on the captured bytes,
    not the landed post-fix harness. `control_frame` is this row's own unmutated
    transcript, so A0/A0b use the canonical 14-cell transcript as the pin. Each
    value is True when the shape rejects the mutant (i.e. the row would FAIL).
    """
    def pass_lines(frame):
        return [line for line in frame.splitlines() if line.startswith("PASS r100_gui ")]

    canonical = pass_lines(control_frame)
    canonical_joined = "\n".join(canonical)
    mutant_pass = pass_lines(mutant_frame)
    cells = [line.split()[2] for line in mutant_pass]
    expected_cells = list(REPLAY_CELLS)
    return {
        "A0_joined_transcript_substring_pin": canonical_joined not in mutant_frame,
        "A0b_joined_transcript_equality_pin": canonical_joined != "\n".join(mutant_pass),
        "A1_cell_count_and_order_pin": not (len(mutant_pass) == 14 and cells == expected_cells),
        "A2_pass_line_set_pin": set(mutant_pass) != set(canonical),
        "A3_total_line_count_pin": mutant_frame.count("\n") + 1 != baseline_lines,
    }


def pick_root(primary: Path, fallback: Path):
    """First root that accepts a real write. /tmp here is a 16G tmpfs shared by
    all seats of both lanes and returns EDQUOT under foreign pressure even for
    an 89-byte copy (observed twice this run), so a fallback root is required
    for the measurement to be possible at all."""
    for candidate, label in ((primary, "primary"), (fallback, "fallback")):
        if candidate is None:
            continue
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".mut01-write-probe"
            probe.write_bytes(b"m" * 65536)
            probe.unlink()
            print(f"mut01: scratch root = {candidate} ({label})")
            return candidate, label
        except OSError as exc:
            print(f"mut01: scratch root {candidate} unusable: {exc}")
    raise SystemExit("mut01: no writable scratch root (primary and fallback both failed)")


class SafeWriter:
    """Evidence writes that survive a flapping shared-/tmp quota.

    /tmp here is a 16G tmpfs shared by both lanes' seats; EDQUOT was observed
    mid-run after a successful write probe. Evidence is not optional, so each
    write retries on the fallback root and records the path actually used.
    """

    def __init__(self, primary: Path, fallback: Path):
        self.bases = [(primary, "primary"), (fallback, "fallback")]
        self.paths = {}

    def write_text(self, name: str, text: str):
        payload = text.encode()
        for base, label in self.bases:
            try:
                base.mkdir(parents=True, exist_ok=True)
                path = base / name
                path.write_bytes(payload)
                if path.stat().st_size != len(payload):
                    raise OSError(f"short write: {path.stat().st_size} != {len(payload)} bytes")
                self.paths[name] = {"path": str(path), "root_choice": label}
                return str(path)
            except OSError as exc:
                print(f"mut01: capture write to {base} ({label}) failed: {exc}")
        self.paths[name] = {"path": None, "root_choice": None}
        print(f"mut01: WARNING capture {name} could not be written anywhere")
        return None


def build_scratch_any(candidates, name: str, stamp: str, forge_arm: str, full_copy: bool):
    """Build the scratch project on whichever root accepts it (EDQUOT-resilient)."""
    last = None
    for root, label in candidates:
        try:
            scratch, before, after, injected, token = build_scratch(root, name, stamp, forge_arm, full_copy)
            return scratch, before, after, injected, token, root, label
        except OSError as exc:
            last = exc
            print(f"mut01: scratch build on {root} ({label}) failed: {exc}")
    raise SystemExit(f"mut01: no writable scratch root for {name}: {last}")


def simulate_postfix(classify, cases, allowlists, control_row, mutant_row):
    """In-memory simulation of the described C2 fix: replace this row's 1-line
    signature with the row's own canonical 14-cell joined transcript (the `\\n`.join
    shape r100-critic F2 names), then reclassify the mutant output against it.

    SIMULATION, not the landed fix: the pin bytes come from this run's control
    transcript and the classifier is the landed one.
    """
    row = next((c for c in cases if c[0] == control_row["name"]), None)
    _, script, flags, expected_exit, _ = row[:5]
    canonical = [line for line in control_row["output"].splitlines()
                 if line.startswith("PASS r100_gui ")]
    joined = "\n".join(canonical)
    allowed = tuple(allowlists.get(control_row["name"], ()))
    verdict = classify(mutant_row["exit_code"], mutant_row["error"], mutant_row["output"],
                       expected_exit, joined, allowed)
    return {"simulated_pin_lines": joined.count("\n") + 1,
            "simulated_pin_sha256": sha256_bytes(joined.encode()),
            "mutant_verdict": "PASS" if verdict else "FAIL",
            "mutant_rejected": not verdict}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--godot", default="godot")
    parser.add_argument("--harness", type=Path, default=FIXTURES / "run_battery.py")
    parser.add_argument("--root", type=Path, default=Path("/tmp/r101-mut1"))
    parser.add_argument("--fallback-root", type=Path, default=Path("/var/tmp/r101-mut1"),
                        help="used when --root rejects writes (EDQUOT on the shared /tmp tmpfs)")
    parser.add_argument("--arm", choices=("extra", "forged_cell", "both"), default="extra")
    parser.add_argument("--expect", choices=("accept", "reject"), default="reject")
    parser.add_argument("--timeout", type=int, default=60,
                        help="per-run timeout; harness uses 8s, widened here for host load")
    parser.add_argument("--full-copy", action="store_true",
                        help="copy the whole fixtures dir into scratch (harness shape) "
                             "instead of the row's two files")
    parser.add_argument("--postfix-harness-out", type=Path, default=None,
                        help="write a copy of --harness whose two r100b_seq_* signatures are the "
                             "canonical 14-cell transcripts from the control run (post-fix pin shape), "
                             "then run mut01.py against it with --expect reject")
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    root, root_label = pick_root(args.root, args.fallback_root)
    roots = [(root, root_label)]
    other = args.fallback_root if root != args.fallback_root else args.root
    roots.append((other, "fallback" if other == args.fallback_root else "primary"))
    writer = SafeWriter(root / "evidence", other / "evidence")
    writer.write_text(f"{stamp}-probe.txt", "mut01 evidence writer probe\n")
    fixtures_snapshot_before = snapshot(FIXTURES)

    tree = harness_ast(args.harness)
    cases, cases_source = extract_cases(tree)
    classify, _ = extract_classify(tree)
    allowlists = extract_allowlists(tree)
    harness_sha = sha256_bytes(args.harness.read_bytes())
    print(f"mut01: harness={args.harness} sha256={harness_sha}")
    print(f"mut01: CASES extracted via {cases_source}; {len(cases)} rows; "
          f"allowlist keys for seq rows: {[k for k in allowlists if k.startswith('r100b_seq')]}")

    arms = list(FORGERIES) if args.arm == "both" else [args.arm]
    report = {"stamp": stamp, "godot": args.godot, "harness": str(args.harness),
              "harness_sha256": harness_sha, "cases_source": cases_source,
              "scratch_root": str(root), "scratch_root_choice": root_label,
              "expect": args.expect, "arms": {}, "timeout_seconds": args.timeout}

    # ---- CONTROL (unmutated) -------------------------------------------------
    control_scratch, control_before, control_after, _, _, croot, croot_label = build_scratch_any(
        roots, "control", stamp, None, args.full_copy)
    control = run_all_rows(args, cases, allowlists, classify, control_scratch,
                           writer, stamp, "control")
    control["scratch_root"] = {"path": str(croot), "root_choice": croot_label}
    report["control"] = control
    for name in ROWS:
        row = control["rows"][name]
        print(f"mut01: CONTROL {name}: {row['verdict']} (pin {row['signature_lines']} line(s), "
              f"exit {row['exit_code']}) :: {' '.join(row['command'])}")
        print(f"mut01: CONTROL {name} transcript: {row['transcript']['total_lines']} lines, "
              f"{row['transcript']['pass_r100_gui_lines']} PASS r100_gui lines, "
              f"cells={row['transcript']['cells_in_order']}")
    if any(control["rows"][name]["verdict"] != "PASS" for name in ROWS):
        print("mut01: INVALID — control run does not satisfy the landed pins; "
              "rejection evidence would be uninterpretable. See evidence transcripts.")
        print("RESULT: INVALID")
        return 2
    baseline_lines = {name: control["rows"][name]["transcript"]["total_lines"] for name in ROWS}

    # ---- canonical transcripts + post-fix harness copy (simulation of the fix) ----
    canonical = {}
    for name in ROWS:
        canonical[name] = "\n".join(line for line in control["rows"][name]["output"].splitlines()
                                    if line.startswith("PASS r100_gui "))
        capture = writer.write_text(f"{stamp}-canonical-{name}.txt", canonical[name] + "\n")
        control["rows"][name]["canonical_transcript_capture"] = capture
    report["canonical_transcript_sha256"] = {n: sha256_bytes(t.encode()) for n, t in canonical.items()}
    if args.postfix_harness_out is not None:
        text = args.harness.read_text()
        for name in ROWS:
            row = next((c for c in cases if c[0] == name), None)
            old = row[4]
            if old not in text:
                raise SystemExit(f"mut01: cannot locate {name} signature literal in harness source")
            escaped = canonical[name].replace("\\", "\\\\").replace("\n", "\\n")
            text = text.replace(old, escaped, 1)
        out = args.postfix_harness_out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        cases2, _ = extract_cases(ast.parse(text))
        verified = all(next(c for c in cases2 if c[0] == name)[4] == canonical[name] for name in ROWS)
        report["postfix_harness_sim"] = {"path": str(out), "pins_verified": verified,
                                         "sha256": sha256_bytes(text.encode()),
                                         "base_harness_sha256": harness_sha}
        print(f"mut01: SIMULATED-POSTFIX HARNESS written to {out} "
              f"(sha256={sha256_bytes(text.encode())}, pins_verified={verified})")

    # ---- MUTANT arms ---------------------------------------------------------
    outcomes = {}
    for arm in arms:
        mutant_scratch, mutant_before, mutant_after, injected, token, mroot, mroot_label = build_scratch_any(
            roots, f"mutant-{arm}", stamp, arm, args.full_copy)
        mutant = run_all_rows(args, cases, allowlists, classify, mutant_scratch,
                              writer, stamp, f"mutant-{arm}")
        mutant["scratch_root"] = {"path": str(mroot), "root_choice": mroot_label}
        verdicts = {name: mutant["rows"][name] for name in ROWS}
        forged_line_present = token is not None and all(
            token in mutant["rows"][name]["output"] for name in ROWS)
        outcome = "REJECT" if any(verdicts[name]["verdict"] == "FAIL" for name in ROWS) else "ACCEPT"
        deltas = {name: verdicts[name]["transcript"]["total_lines"] - baseline_lines[name]
                  for name in ROWS}
        probes = {name: pin_shape_probe(mutant["rows"][name]["output"],
                                        control["rows"][name]["output"],
                                        baseline_lines[name])
                  for name in ROWS}
        simulated = {name: simulate_postfix(classify, cases, allowlists,
                                            control["rows"][name], mutant["rows"][name])
                     for name in ROWS}
        outcomes[arm] = {"outcome": outcome, "rows": verdicts, "forged_line": injected,
                         "forged_token_present_in_all_outputs": forged_line_present,
                         "line_delta_vs_control": deltas,
                         "fixture_sha256": sha256_bytes(mutant_after),
                         "simulated_pin_shapes": probes,
                         "simulated_postfix_pins": simulated}
        print(f"mut01: ARM {arm}: injected {injected!r}; forged_token_present_in_all_outputs="
              f"{forged_line_present} line_delta_vs_control={deltas}")
        for name in ROWS:
            print(f"mut01: ARM {arm} {name}: {verdicts[name]['verdict']} "
                  f"(exit {verdicts[name]['exit_code']})")
            print(f"mut01: ARM {arm} {name} simulated post-fix pins would reject: {probes[name]}")
            print(f"mut01: ARM {arm} {name} SIMULATED-POSTFIX(pin={simulated[name]['simulated_pin_lines']}"
                  f" lines, {simulated[name]['simulated_pin_sha256'][:16]}…) mutant_verdict="
                  f"{simulated[name]['mutant_verdict']} rejected={simulated[name]['mutant_rejected']}")
        print(f"mut01: ARM {arm} OUTCOME={outcome}")

    report["arms"] = outcomes
    overall = "ACCEPT" if all(v["outcome"] == "ACCEPT" for v in outcomes.values()) else "REJECT"
    expectation_met = (overall.lower() == args.expect)

    report["observed_overall"] = overall
    report["expectation_met"] = expectation_met
    diff = diff_snapshots(fixtures_snapshot_before, snapshot(FIXTURES))
    watched = ("run_battery.py", SEQ_FIXTURE, "project.godot")
    diff["watched_files_clean"] = not any(path in diff[k] for k in ("added", "removed", "changed")
                                          for path in watched)
    report["fixtures_snapshot_diff"] = diff
    report["evidence_paths"] = writer.paths
    json_path = writer.write_text(f"{stamp}-mut01-verdict.json", json.dumps(report, indent=2) + "\n")

    print(f"mut01: observed overall outcome across arms: {overall}; expectation: {args.expect} "
          f"-> {'met' if expectation_met else 'NOT met'}")
    print(f"mut01: repo fixtures snapshot diff clean={diff['clean']} "
          f"added={diff['added']} removed={diff['removed']} changed={diff['changed']}")
    print(f"mut01: files this seat reads (run_battery.py, r100b_seq.gd, project.godot) unchanged="
          f"{diff['watched_files_clean']}")
    print(f"mut01: verdict json: {json_path}")
    print(f"RESULT: {'PASS' if expectation_met else 'FAIL'}")
    return 0 if expectation_met else 1


if __name__ == "__main__":
    sys.exit(main())
