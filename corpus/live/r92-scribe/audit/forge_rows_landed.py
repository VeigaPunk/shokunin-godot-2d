#!/usr/bin/env python3
"""r92-scribe: re-run the scout's signature-forge test against the LANDED rows.

The scout's forge mutates the *pinned signature* and classifies it against the
canonical receipt (proving the pin is exactly what the engine emitted). Re-run
here with the landed rows — including the 2-payload nav envelope — to check that
the envelope did not make any signature mutant admissible.
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LIVE = REPO / "corpus" / "live"
src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"], cwd=REPO,
                     capture_output=True, check=True).stdout.decode()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = "    " + ast.get_source_segment(src, node).replace("\n", "\n    ")
        break
ns = {}
exec("def _wrap():\n" + fn_src + "\n    return classify_process\n", ns)
classify_process = ns["_wrap"]()
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()

cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
ee = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "expected_errors" for t in node.targets):
        for sub in ast.walk(node.value):
            if isinstance(sub, ast.Dict):
                d = ast.literal_eval(sub)
                if any(k.startswith("r92_") for k in d):
                    ee = d
R92 = {c[0]: c for c in cases if c[0].startswith("r92_")}
ARM = {"nullts_crash": "nullts"}


def receipt(arm):
    """prefer the scribe's own fresh receipt, else the author's rep1."""
    for base in (LIVE / "r92-scribe" / "fresh", LIVE / "r92-author" / "fresh-reps"):
        out = base / f"{arm}.rep1.out"
        if out.exists():
            return (out.read_text(errors="replace")
                    + out.with_suffix(".err").read_text(errors="replace"),
                    int(out.with_suffix(".rc").read_text().strip()))
    raise SystemExit(f"no receipt for {arm}")


def mutate(value):
    if value == "null":
        return "hit"
    if value == "hit":
        return "null"
    if value == "true":
        return "false"
    if value == "false":
        return "true"
    if value == "obj":
        return "null"
    if value == "-1":
        return "0"
    return value[1:] if value.startswith("-") else "-" + value


total = accepted = 0
per_row = {}
for case, script, flags, expected_exit, sig in R92.values():
    arm = case.removeprefix("r92_tilemap_")
    arm = ARM.get(arm, arm)
    output, code = receipt(arm)
    allowed = tuple(ee.get(case, ()))
    sigs = sig if isinstance(sig, (tuple, list)) else (sig,)
    assert any(classify_process(code, None, output, expected_exit, s, allowed)
               for s in sigs), f"control rejected for {case}"
    builds = rejects = 0
    for base_sig in sigs:
        head, _, payload = base_sig.partition(" ")
        tokens = payload.split(" ")
        for i, tok in enumerate(tokens):
            if "=" not in tok:
                continue
            key, _, value = tok.partition("=")
            if not value:
                continue
            mut = list(tokens)
            mut[i] = f"{key}={mutate(value)}"
            if mut[i] == tok:
                continue
            mutant = head + " " + " ".join(mut)
            builds += 1
            total += 1
            if classify_process(code, None, output, expected_exit, mutant, allowed):
                accepted += 1
                print(f"  !! ACCEPTED MUTANT {case} {tok} -> {mut[i]}")
            else:
                rejects += 1
        for extra in ("forged=1", "empty_source=-2", "disabled_f1=hit", "regions_f1=0"):
            mutant = head + " " + " ".join(tokens) + " " + extra
            builds += 1
            total += 1
            if classify_process(code, None, output, expected_exit, mutant, allowed):
                accepted += 1
                print(f"  !! ACCEPTED APPEND {case} +{extra}")
            else:
                rejects += 1
    per_row[case] = {"mutants": builds, "rejected": rejects}

out = {"classify_process_segment_sha256": seg_sha, "total": total,
       "rejected": total - accepted, "accepted": accepted, "per_row": per_row}
print(json.dumps(out, indent=1))
(Path(__file__).parent / "forge_rows_landed.json").write_text(json.dumps(out, indent=1))
