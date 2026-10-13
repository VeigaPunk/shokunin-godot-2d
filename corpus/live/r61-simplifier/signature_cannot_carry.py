#!/usr/bin/env python3
"""r61 simplifier scratch: prove the CASES signature field cannot carry the
crash ERROR line — only the existing per-name expected_errors allowlist can.

Extracts classify_process verbatim from the tracked run_battery.py via ast
(no transcription), feeds it the r60 verifier's captured crash/sigkill stdout,
and records each (expected_exit, signature, allowed_errors) combination.
"""
import ast
import json
import hashlib
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
RUNNER = REPO / "corpus/fixtures/run_battery.py"
CRASH_OUT = REPO / "corpus/live/r60-verifier/scratch-probe/verifier_os_crash_a.stdout"
KILL_OUT = REPO / "corpus/live/r60-verifier/scratch-probe/verifier_self_sigkill.stdout"
RESULT = REPO / "corpus/live/r61-simplifier/classify_matrix.json"

runner_bytes = RUNNER.read_bytes()
tree = ast.parse(runner_bytes)
ns = {}
extracted = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        for inner in node.body:
            if isinstance(inner, ast.FunctionDef) and inner.name == "classify_process":
                seg = ast.get_source_segment(runner_bytes.decode(), inner)
                extracted["classify_process"] = seg
                exec(seg, ns)
assert "classify_process" in ns, "extraction failed"
classify = ns["classify_process"]

crash_text = CRASH_OUT.read_text()
kill_text = KILL_OUT.read_text()
MARKER = "SPONTANEOUS_CRASH_PROBE: expected signature"
CRASH_ERROR = "ERROR: r60 spontaneous crash probe"

matrix = [
    # (label, code, error, output, expected_exit, signature, allowed_errors)
    ("crash exp=-6 sig=marker allowlist=none", -6, None, crash_text, -6, MARKER, ()),
    ("crash exp=-6 sig=marker allowlist=exact", -6, None, crash_text, -6, MARKER, (CRASH_ERROR,)),
    # THE KEY TEST: can the signature field carry the ERROR line? (no allowlist)
    ("crash exp=-6 sig=ERROR-line allowlist=none", -6, None, crash_text, -6, CRASH_ERROR, ()),
    # prefix-comma form also works but exact match is the tighter expression
    ("crash exp=-6 sig=marker allowlist=prefix-comma", -6, None, crash_text, -6, MARKER, ("ERROR: r60 spontaneous crash probe,",)),
    # expected-mismatch rejection must stay untouched
    ("crash exp=-9 sig=marker allowlist=exact", -6, None, crash_text, -9, MARKER, (CRASH_ERROR,)),
    ("crash exp=1 sig=marker allowlist=exact", -6, None, crash_text, 1, MARKER, (CRASH_ERROR,)),
    # the zero-allowlist signal row: self-SIGKILL, empty stderr
    ("sigkill exp=-9 sig=marker allowlist=none", -9, None, kill_text, -9, MARKER, ()),
    ("sigkill exp=-6 sig=marker allowlist=none", -9, None, kill_text, -6, MARKER, ()),
    # wrong-marker spoof on crash arm must still reject
    ("crash exp=-6 sig=absent-marker allowlist=exact", -6, None, crash_text, -6, "NOSUCH_MARKER", (CRASH_ERROR,)),
]

results = []
for label, code, error, output, exp, sig, allowed in matrix:
    verdict = classify(code, error, output, exp, sig, allowed)
    results.append({"label": label, "expected_exit": exp,
                    "signature": sig, "allowed_errors": list(allowed),
                    "classification": verdict})

payload = {
    "mode": "r61_simplifier_signature_cannot_carry",
    "runner_sha256": hashlib.sha256(runner_bytes).hexdigest(),
    "extracted_classify_process_sha256": hashlib.sha256(extracted["classify_process"].encode()).hexdigest(),
    "inputs": {"crash_stdout": str(CRASH_OUT), "sigkill_stdout": str(KILL_OUT)},
    "results": results,
}
RESULT.write_text(json.dumps(payload, indent=2) + "\n")
for r in results:
    print(f"{str(r['classification']):5} {r['label']}")
