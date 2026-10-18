#!/usr/bin/env python3
"""r101-D2: land the full-replay pins for `r100b_seq_clean` / `r100b_seq_noclean`.

Closes r100-critic F2: each row currently pins ONE line of the 14-cell replay,
so a forged extra output line inside the replay passes both rows. This patcher
replaces each row's signature with a `"\\n".join((...))` expression over the
full 15-line replay transcript (14 `PASS r100_gui <cell>` lines + `SEQ_DONE`),
captured from a byte-identical copy of corpus/fixtures/r100b_seq.gd
(sha256 4718a19e...) with the battery's launch shape. The classifier is
unchanged (`signature in output`, output = stdout+stderr; the block is a
contiguous stdout substring), so no `execute()` change is needed.

Usage:
  python3 reports/round-101/mutations/r101-D2_apply_fullpin.py            # dry-run, prints diff
  python3 .../r101-D2_apply_fullpin.py --apply                            # write repo harness
  python3 .../r101-D2_apply_fullpin.py --target /tmp/copy.py --apply      # write a copy (test)

Pins are read from the r101-D2 captures (default /tmp/r101-D2), bound by the
sha256 constants below. Guards: fixture sha, capture sha, exactly one row per
name, all other CASES rows byte-identical, result parses and re-evaluates to
the pins. Only the two signature expressions are rewritten.
"""
import argparse
import ast
import difflib
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
REPO = HERE.parents[3]
FIXTURE = REPO / "corpus/fixtures/r100b_seq.gd"
TARGET_DEFAULT = REPO / "corpus/fixtures/run_battery.py"
FIXTURE_SHA = "4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd"
ROW_CAPTURE = {
    "r100b_seq_clean": ("clean1.out", "2fc9a28f0dc2a44f4301d346ef46a81bfab87a6514bf21b070a9334412b0372a"),
    "r100b_seq_noclean": ("clean0.out", "bb1e76767fcd3bf08807cebca6ac7340c5029096793e838d0c6bf92029a95c83"),
}


def pin_lines(capture_dir, filename, want_sha):
    raw = (capture_dir / filename).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    assert got == want_sha, f"{filename}: sha256 {got} != pinned {want_sha}"
    lines = raw.decode().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("PASS r100_gui census "))
    end = next(i for i, l in enumerate(lines) if l.startswith("SEQ_DONE clean="))
    return lines[start:end + 1]


def expr_for(lines):
    body = ",\n".join("         " + repr(line) for line in lines)
    return '"\\n".join((\n' + body + "))"


def find_node(tree, name):
    hits = [n for n in ast.walk(tree)
            if isinstance(n, ast.Tuple) and len(n.elts) == 5 and n.elts
            and isinstance(n.elts[0], ast.Constant) and n.elts[0].value == name]
    assert len(hits) == 1, f"{name}: {len(hits)} rows"
    return hits[0]


def sig_value(node):
    if isinstance(node, ast.Constant):
        return node.value
    return eval(compile(ast.Expression(node), "<sig>", "eval"), {"__builtins__": {}}, {})


def all_rows(src):
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Tuple) and len(node.elts) == 5
                and isinstance(node.elts[0], ast.Constant)
                and isinstance(node.elts[0].value, str)):
            out[node.elts[0].value] = sig_value(node.elts[4])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=pathlib.Path, default=TARGET_DEFAULT)
    ap.add_argument("--captures-dir", type=pathlib.Path, default=pathlib.Path("/tmp/r101-D2"))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    fixture_sha = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert fixture_sha == FIXTURE_SHA, f"fixture sha {fixture_sha} != {FIXTURE_SHA}"
    src = args.target.read_text()
    before = all_rows(src)
    assert set(ROW_CAPTURE) <= set(before), set(ROW_CAPTURE) - set(before)

    for name, (fname, csha) in ROW_CAPTURE.items():
        pin = pin_lines(args.captures_dir, fname, csha)
        node = find_node(ast.parse(src), name).elts[4]
        assert node.lineno == node.end_lineno, f"{name}: signature is not single-line"
        lines = src.splitlines(keepends=True)
        line = lines[node.lineno - 1]
        assert line.isascii(), f"{name}: signature line is not ASCII"
        lines[node.lineno - 1] = line[:node.col_offset] + expr_for(pin) + line[node.end_col_offset:]
        src = "".join(lines)

    after = all_rows(src)
    assert set(after) == set(before), "row-name set changed"
    changed = [n for n in before if before[n] != after[n]]
    assert changed == list(ROW_CAPTURE), f"unexpected changed rows: {changed}"
    for name, (fname, csha) in ROW_CAPTURE.items():
        assert after[name] == "\n".join(pin_lines(args.captures_dir, fname, csha)), name
    compile(src, str(args.target), "exec")  # syntax

    diff = list(difflib.unified_diff(args.target.read_text().splitlines(True),
                                     src.splitlines(True), str(args.target), str(args.target) + ".patched", n=1))
    sys.stdout.writelines(diff)
    print(f"\nrows changed: {changed}; other rows unchanged; result compiles")
    if args.apply:
        args.target.write_text(src)
        print(f"APPLIED {args.target}")
    else:
        print("dry-run (pass --apply to write)")


if __name__ == "__main__":
    main()
