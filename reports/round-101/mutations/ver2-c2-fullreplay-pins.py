#!/usr/bin/env python3
"""r101 VER-2 / C2 — full-replay pins for the r100b_seq_* rows.

Closes r100-critic F2: each `r100b_seq_*` CASES row currently pins ONE line of a
14-cell replay, so a forged extra output line inside the replay leaves both rows
PASS and 3 of the replay's 4 divergences from the fresh-process pins are
unconstrained by any row.

This script does NOT edit the lane's harness. It
  1. extracts the production `classify_process` from corpus/fixtures/run_battery.py
     (AST, so the proof runs on the harness's own bytes),
  2. reads the two live CASES pins,
  3. replays `r100b_seq.gd` twice (--clean=1 / --clean=0) in a scratch copy,
  4. builds the proposed 14-line whole-replay signature per variant,
  5. runs an accept/reject matrix over real + forged transcripts under the
     current one-line pin and under the proposed whole-replay pin,
  6. with --apply, writes a PATCHED harness copy to a scratch path and prints
     the CASES diff for integration (the shared file is never touched).

Usage
  python3 reports/round-101/mutations/ver2-c2-fullreplay-pins.py            # measure
  python3 reports/round-101/mutations/ver2-c2-fullreplay-pins.py --apply    # + patched copy
"""
import argparse
import ast
import difflib
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[3]
HARNESS = REPO / "corpus/fixtures/run_battery.py"
PROBE_PROJ = REPO / "corpus/live/r100-boundary/proj"
CELLS = ["census", "routing", "hover", "motion", "localpos", "cursor", "clip",
         "drag", "touch", "subvp", "warp", "focus", "render", "osmeta"]


def extract_classify():
    """Compile the production classify_process out of the harness AST."""
    tree = ast.parse(HARNESS.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            mod = ast.Module(body=[node], type_ignores=[])
            ns = {}
            exec(compile(ast.fix_missing_locations(mod), str(HARNESS), "exec"), ns)
            return ns["classify_process"]
    raise SystemExit("classify_process not found in harness")


def cases_pins():
    """Return {row_name: signature} for the two live r100b_seq_* CASES rows."""
    src = HARNESS.read_text()
    out = {}
    pat = re.compile(
        r"\('(r100b_seq_\w+)',\s*'r100b_seq\.gd',\s*\[[^\]]*\],\s*0,\s*\n\s*'((?:[^'\\]|\\.)*)'\)")
    for m in pat.finditer(src):
        out[m.group(1)] = m.group(2)
    if set(out) != {"r100b_seq_clean", "r100b_seq_noclean"}:
        raise SystemExit("expected 2 seq rows, got %r" % sorted(out))
    return out


def row_allowlist():
    """Pull the live per-row stderr allowlist out of the harness dict literal."""
    src = HARNESS.read_text()
    out = {}
    for name in ("r100b_seq_clean", "r100b_seq_noclean"):
        m = re.search(r"'%s': \(\n(.*?)\n\s*\)," % name, src, re.S)
        if not m:
            raise SystemExit("allowlist entry not found for %s" % name)
        found = re.findall(
            r"""^\s*(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)'),\s*$""",
            m.group(1), re.M)
        out[name] = tuple(a or b for a, b in found)
    return out


def cell_lines(stdout):
    """Ordered 14 `PASS r100_gui <cell> ...` lines, keyed by cell."""
    got = {}
    for line in stdout.splitlines():
        m = re.match(r"(PASS r100_gui (\w+) .*)$", line)
        if m and m.group(2) in CELLS:
            got[m.group(2)] = m.group(1)
    missing = [c for c in CELLS if c not in got]
    if missing:
        raise SystemExit("missing cells %r" % missing)
    return [got[c] for c in CELLS]


def replay(work, clean):
    proj = work / ("proj_clean" if clean else "proj_noclean")
    shutil.copytree(PROBE_PROJ, proj)
    arg = "--clean=1" if clean else "--clean=0"
    p = subprocess.run(
        ["godot", "--headless", "--path", str(proj),
         "--script", "res://r100b_seq.gd", "--", arg],
        capture_output=True, text=True, timeout=300)
    return p.stdout, p.stderr, p.returncode


def forged(variant, kind):
    """Return (blob, note) for a tampered transcript."""
    lines = variant.split("\n")
    if kind == "real":
        return variant, "unmodified"
    if kind == "mid_block":
        # inject between two cells, exactly the r100-critic m_seq shape
        i = next(i for i, l in enumerate(lines) if l.startswith("PASS r100_gui motion"))
        out = lines[:i] + ["FORGED_EXTRA_CELL_OUTPUT"] + lines[i:]
        return "\n".join(out), "extra line between hover and motion"
    if kind == "post_seq":
        return variant + "\nFORGED_TRAILING_LINE", "extra line after SEQ_DONE"
    if kind == "cell_edit":
        i = next(i for i, l in enumerate(lines) if l.startswith("PASS r100_gui warp"))
        out = lines[:]
        out[i] = out[i].replace("w4 mode=0", "w4 mode=9")
        return "\n".join(out), "warp cell edited (mode 0 -> 9)"
    raise SystemExit(kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="also emit a patched harness copy")
    args = ap.parse_args()

    classify = extract_classify()
    pins = cases_pins()
    allow = row_allowlist()
    work = pathlib.Path(tempfile.mkdtemp(prefix="r101-ver2-c2-"))
    print("scratch:", work)
    print("harness sha256:", hashlib.sha256(HARNESS.read_bytes()).hexdigest())
    print("classify_process extracted via AST from the live harness bytes\n")

    variants = {}
    for name, clean in (("r100b_seq_clean", True), ("r100b_seq_noclean", False)):
        stdout, stderr, rc = replay(work, clean)
        lines = cell_lines(stdout)
        variants[name] = dict(stdout=stdout, stderr=stderr, rc=rc,
                              cells=lines, full="\n".join(lines))
        print("%-18s rc=%d cells=%d stdout=%dB stderr=%dB"
              % (name, rc, len(lines), len(stdout), len(stderr)))
        print("  current pin len=%d md5=%s"
              % (len(pins[name]), hashlib.md5(pins[name].encode()).hexdigest()[:12]))
        print("  full-replay  len=%d md5=%s"
              % (len(variants[name]["full"]),
                 hashlib.md5(variants[name]["full"].encode()).hexdigest()[:12]))
        print("  current pin is a substring of the transcript:", pins[name] in stdout)

    print("\n%-18s %-12s %-10s %-10s" % ("variant", "forgery", "current", "full-replay"))
    print("-" * 56)
    results = []
    for name, v in variants.items():
        blob = v["stdout"] + v["stderr"]
        for kind in ("real", "mid_block", "post_seq", "cell_edit"):
            forged_blob = forged(blob, kind)[0]
            cur = classify(v["rc"], None, forged_blob, 0, pins[name], allow[name])
            full = classify(v["rc"], None, forged_blob, 0, v["full"], allow[name])
            results.append((name, kind, cur, full))
            print("%-18s %-12s %-10s %-10s" % (name, kind, "PASS" if cur else "FAIL",
                                               "PASS" if full else "FAIL"))

    # The discrimination the fix buys: forged rows the current pin accepts but
    # the whole-replay pin rejects.
    gain = [(n, k) for n, k, c, f in results if c and not f]
    print("\nforgeries accepted by current pin, rejected by full-replay pin: %d" % len(gain))
    for n, k in gain:
        print("  %s / %s" % (n, k))
    regress = [(n, k) for n, k, c, f in results if f and not c]
    print("real transcripts rejected by full-replay pin (must be 0): %d" % len(regress))

    if args.apply:
        src = HARNESS.read_text()
        patched = src
        for name, v in variants.items():
            old = "'%s'" % pins[name]
            new = repr(v["full"])
            if old not in src:
                raise SystemExit("pin literal not found verbatim for %s" % name)
            patched = patched.replace(old, new, 1)
        out = work / "run_battery.patched.py"
        out.write_text(patched)
        print("\npatched harness copy:", out)
        diff = difflib.unified_diff(src.splitlines(True), patched.splitlines(True),
                                    "run_battery.py", "run_battery.patched.py", n=1)
        sys.stdout.writelines(diff)


if __name__ == "__main__":
    main()
