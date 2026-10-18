#!/usr/bin/env python3
"""r101-D2: full-replay pin material + forgery discrimination check for the
`r100b_seq_clean` / `r100b_seq_noclean` rows (r101 C2, seat D2 slice: cells
6-10 = cursor, clip, drag, touch, subvp).

Captures were produced with the battery's launch shape:
  /usr/bin/godot --headless --path /tmp/r101-D2/proj --script res://r100b_seq.gd -- --clean={0,1}
on a byte-identical copy of corpus/fixtures/r100b_seq.gd (sha256 4718a19e...).
`forged*` captures inject `FORGED_EXTRA_CLIP_CELL` at the head of `_cell_clip`.

Read-only: never runs run_battery.py. `--rows-from <file>` reads the CASES rows
from an arbitrary harness copy (used to validate the patched full-pin rows).
"""
import ast
import difflib
import hashlib
import pathlib
import re
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
CAP = pathlib.Path("/tmp/r101-D2")
FIXTURE_SHA = "4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd"
CELLS = ["cursor", "clip", "drag", "touch", "subvp"]

src_path = REPO / "corpus/fixtures/run_battery.py"
if "--rows-from" in sys.argv:
    src_path = pathlib.Path(sys.argv[sys.argv.index("--rows-from") + 1])
src = src_path.read_text()
print(f"rows from: {src_path}")


def sig_value(node):
    if isinstance(node, ast.Constant):
        return node.value
    return eval(compile(ast.Expression(node), "<sig>", "eval"), {"__builtins__": {}}, {})


tree = ast.parse(src)
rows = {}
fresh = {}
for node in ast.walk(tree):
    if not (isinstance(node, ast.Tuple) and node.elts
            and isinstance(node.elts[0], ast.Constant)
            and isinstance(node.elts[0].value, str)):
        continue
    name = node.elts[0].value
    if name in ("r100b_seq_clean", "r100b_seq_noclean"):
        rows[name] = sig_value(node.elts[4])
    if name.startswith("r100_gui_") and len(node.elts) == 5:
        fresh[name.removeprefix("r100_gui_")] = sig_value(node.elts[4])
assert set(rows) == {"r100b_seq_clean", "r100b_seq_noclean"}, rows.keys()


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    # verbatim replica of corpus/fixtures/run_battery.py:1725
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


def capture(name):
    out = (CAP / f"{name}.out").read_text()
    err = (CAP / f"{name}.err").read_text()
    return out, err, out + err


def block_pin(stdout):
    lines = stdout.split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("PASS r100_gui census "))
    end = next(i for i, l in enumerate(lines) if l.startswith("SEQ_DONE clean="))
    return "\n".join(lines[start:end + 1])


def cell_map(text):
    return {m.group(1): line for line in text.splitlines()
            if (m := re.match(r"PASS r100_gui ([a-z]+) ", line))}


ALLOWED = ('ERROR: Parameter "t" is null.',)
clean1_out, clean1_err, clean1_all = capture("clean1")
clean0_out, clean0_err, clean0_all = capture("clean0")
forged_out, forged_err, forged_all = capture("forged")
forged0_out, forged0_err, forged0_all = capture("forged0")
pin1 = block_pin(clean1_out)
pin0 = block_pin(clean0_out)

print("== pin material ==")
for tag, pin in (("clean", pin1), ("noclean", pin0)):
    assert all(c not in pin for c in "'\"\\"), "pin not quote/backslash-safe"
    print(f"{tag}: lines={pin.count(chr(10)) + 1} chars={len(pin)} sha256={hashlib.sha256(pin.encode()).hexdigest()}")

print("\n== classify matrix (production predicate, allowed_errors=1 line) ==")
checks = [
    ("genuine clean=1  current rows", classify_process(0, None, clean1_all, 0, rows["r100b_seq_clean"], ALLOWED)),
    ("genuine clean=1  FULL-block pin", classify_process(0, None, clean1_all, 0, pin1, ALLOWED)),
    ("genuine clean=0  current rows", classify_process(0, None, clean0_all, 0, rows["r100b_seq_noclean"], ALLOWED)),
    ("genuine clean=0  FULL-block pin", classify_process(0, None, clean0_all, 0, pin0, ALLOWED)),
    ("forged  clean=1  current rows", classify_process(0, None, forged_all, 0, rows["r100b_seq_clean"], ALLOWED)),
    ("forged  clean=1  FULL-block pin", classify_process(0, None, forged_all, 0, pin1, ALLOWED)),
    ("forged  clean=0  current rows", classify_process(0, None, forged0_all, 0, rows["r100b_seq_noclean"], ALLOWED)),
    ("forged  clean=0  FULL-block pin", classify_process(0, None, forged0_all, 0, pin0, ALLOWED)),
]
for label, verdict in checks:
    print(f"{label:34s} -> {'PASS' if verdict else 'FAIL'}")

print("\n== cells 6-10 replay vs landed fresh pins ==")
c1, c0 = cell_map(clean1_out), cell_map(clean0_out)
for cell in CELLS:
    for tag, cm in (("clean", c1), ("noclean", c0)):
        if cm[cell] == fresh[cell]:
            print(f"{cell:7s} {tag:8s} EQUAL to landed fresh pin")
        else:
            print(f"{cell:7s} {tag:8s} DIVERGES; first-diff fields:")
            sm = difflib.SequenceMatcher(None, fresh[cell], cm[cell])
            for op, a1, a2, b1, b2 in sm.get_opcodes():
                if op != "equal":
                    print(f"    {op}: fresh[{a1}:{a2}]={fresh[cell][a1:a2]!r} replay[{b1}:{b2}]={cm[cell][b1:b2]!r}")
print("\nforged line rank:", [i for i, l in enumerate(forged_out.split("\n")) if "FORGED" in l])
print("fixture sha pinned:", FIXTURE_SHA.startswith("4718a19e"))
