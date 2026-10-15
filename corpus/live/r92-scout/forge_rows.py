#!/usr/bin/env python3
"""r92-scout row forge test — proves every row is discriminating, not vacuous.

For each row: take its signature, split into whitespace tokens, and for every
token of the form `key=value` build a mutant where the value is replaced by a
different token. Classify each mutant against the canonical receipt for that arm
with the production `classify_process`. A row is discriminating iff every mutant
is rejected (the row's payload is exactly what the engine emitted, so any other
value must fail).

Mutants that differ only by an inserted/duplicated token are also built (the
"missing conjunct" forge: appending a plausible key=value that the engine never
printed must still reject).
"""
import ast
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
FIXTURE = HERE.parent.parent / "fixtures" / "run_battery.py"
src = FIXTURE.read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()

rows_ns = {}
exec((HERE / "author-rows.py.txt").read_text(), rows_ns)
ROWS = rows_ns["ROWS"]
EXPECTED = rows_ns["EXPECTED_ERRORS"]


def receipt_for(case):
    cell = case.replace("r92_tilemap_", "tm_")
    out = sorted((HERE / "runs").glob(f"r92_{cell}.rep1.out"))[0]
    err = out.with_suffix(".err")
    return out.read_text() + (err.read_text() if err.exists() else ""), int(
        out.with_suffix(".rc").read_text().strip())


def mutate(value, i):
    """A different token for the same key: numeric -> n+1/n-1, else flip."""
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
    try:
        if value.startswith("-"):
            return value[1:]
        return "-" + value
    except Exception:
        return value + "X"


total = accepted = 0
per_row = {}
for case, script, flags, expected_exit, sig in ROWS:
    output, code = receipt_for(case)
    allowed = EXPECTED.get(case, ())
    head, _, payload = sig.partition(" ")
    # (a) payload-preserving control: the exact line must be accepted
    assert classify_process(code, None, output, expected_exit, sig, allowed), \
        f"control rejected for {case}"
    tokens = payload.split(" ")
    rejects = 0
    builds = 0
    for i, tok in enumerate(tokens):
        if "=" not in tok:
            continue
        key, _, value = tok.partition("=")
        if not value:
            continue
        mut = list(tokens)
        mut[i] = f"{key}={mutate(value, i)}"
        if mut[i] == tok:
            continue
        mutant = head + " " + " ".join(mut)
        builds += 1
        total += 1
        if not classify_process(code, None, output, expected_exit, mutant, allowed):
            rejects += 1
        else:
            accepted += 1
            print(f"  !! ACCEPTED MUTANT {case} {tok} -> {mut[i]}")
    # (b) appended-conjunct forge: a plausible key=value the engine never printed
    for extra in ("forged=1", "empty_source=-2", "disabled_f1=hit", "regions_f1=0"):
        mutant = head + " " + " ".join(tokens) + " " + extra
        builds += 1
        total += 1
        if not classify_process(code, None, output, expected_exit, mutant, allowed):
            rejects += 1
        else:
            accepted += 1
            print(f"  !! ACCEPTED APPEND {case} +{extra}")
    per_row[case] = (rejects, builds)
    print(f"{case}: mutants={builds} rejected={rejects}")

print()
print(f"classify_process segment sha256={seg_sha[:16]}")
print(f"TOTAL mutants={total} rejected={total - accepted} accepted={accepted}")
sys.exit(1 if accepted else 0)
