#!/usr/bin/env python3
"""MUT-8 — CRLF seam injected into the r100b_seq replay pins.

Mutation: append a carriage return to printed line(s) of the `r100b_seq.gd`
replay so the child's raw byte stream carries CRLF (`\\r\\n`) line seams.

The mutation is measured against the landed harness bytes at the round's
start commit (read-only): the two landed signatures are parsed out of
`corpus/fixtures/run_battery.py` with `ast` (the harness is never executed),
and a full-replay `\\n`-joined pin is built from an unmutated transcript.

Capture modes mirror the harness exactly:

  text   subprocess.run(..., capture_output=True, text=True) success branch
         (run_battery.py:1701-1702 -> run_process_streams, universal newlines)
  raw    the same bytes decoded with bytes.decode(errors="replace") — the
         timeout branch's transformation (run_battery.py:1712-1714, 1719-1721)

Targeted `godot --headless` runs only; `run_battery.py` is never run.

Usage:
  python3 reports/round-101/mutations/mut08_crlf_seam.py \
      --fixtures corpus/fixtures \
      --scratch /tmp/r101-mut08/scratch \
      --out /var/tmp/r101-mut08
"""

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

SEQ_SHA = "4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd"
ALLOWED = ('ERROR: Parameter "t" is null.',)


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    """Faithful replica of run_battery.py:1725-1742."""
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
            and not unrelated_errors and "SCRIPT ERROR:" not in output
            and "Parse Error:" not in output)


def landed_signatures(harness_path):
    """Pull the two r100b_seq_* rows out of the CASES literal without running it."""
    tree = ast.parse(Path(harness_path).read_text())
    cases = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            cases = ast.literal_eval(node.value)
            break
    assert cases is not None, "CASES literal not found"
    rows = {c[0]: c for c in cases if c[0].startswith("r100b_seq_")}
    assert set(rows) == {"r100b_seq_clean", "r100b_seq_noclean"}, sorted(rows)
    return rows


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def run_capture(cmd, timeout, text_mode):
    """subprocess.run replica; on timeout return the harness's decode path."""
    if text_mode:
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return p.stdout, p.stderr, p.returncode, None, "success"
        except subprocess.TimeoutExpired as exc:
            out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return out, err, None, f"TIMEOUT after {timeout} seconds", "timeout"
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return (p.stdout or b"").decode(errors="replace"), (p.stderr or b"").decode(errors="replace"), p.returncode, None, "success"
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace")
        err = (exc.stderr or b"").decode(errors="replace")
        return out, err, None, f"TIMEOUT after {timeout} seconds", "timeout"


SEAMS = {
    # name: (needle, replacement) — unique print sites in r100b_seq.gd
    "seamA_census_line": (
        'print("PASS r100_gui census %s" % " ".join(facts))',
        'print("PASS r100_gui census %s\\r" % " ".join(facts))',
    ),
    "seamB_pinned_lines": (
        'print("PASS r100_gui hover %s" % " ".join(out))',
        'print("PASS r100_gui hover %s\\r" % " ".join(out))',
    ),
    # content-forgery anchor (r100-critic m_seq shape): a real extra line
    # inside the replay — the class of mutant a full-replay pin must reject.
    "seamC_forged_line": (
        'print("PASS r100_gui hover %s" % " ".join(out))',
        'print("FORGED_EXTRA_CELL_OUTPUT")\n\tprint("PASS r100_gui hover %s" % " ".join(out))',
    ),
    # detection positive control: a CR that lands INSIDE the pinned text
    # (normalizes to a line break in the middle of the pinned line).
    "seamD_cr_inside_pinned_text": (
        'print("PASS r100_gui cursor %s" % " ".join(out))',
        'print("PASS r100_gui cursor\\r %s" % " ".join(out))',
    ),
}
SEAM_B_CURSOR = (
    'print("PASS r100_gui cursor %s" % " ".join(out))',
    'print("PASS r100_gui cursor %s\\r" % " ".join(out))',
)


def make_variant(src_text, name):
    text = src_text
    if name in ("seamA_census_line", "seamC_forged_line", "seamD_cr_inside_pinned_text"):
        needle, repl = SEAMS[name]
        assert text.count(needle) == 1
        text = text.replace(needle, repl)
    elif name == "seamB_pinned_lines":
        for needle, repl in (SEAMS["seamB_pinned_lines"], SEAM_B_CURSOR):
            assert text.count(needle) == 1
            text = text.replace(needle, repl)
    else:
        raise SystemExit(f"unknown variant {name}")
    return text


def full_replay_pin(captured):
    lines = [ln for ln in captured.splitlines() if ln.startswith("PASS r100_gui ")]
    assert len(lines) == 14, f"expected 14 cell lines, got {len(lines)}"
    return "\n".join(lines)


def boundary_sweep(baseline_text, pin, landed):
    """Insert a bare CR before each '\\n' boundary of the REAL captured
    transcript and report which pins reject it, in both decode modes.

    The mutation only ever inserts a byte at a boundary, so replaying it on
    real captured bytes is equivalent to re-running the child; the two
    real-godot seam variants (seamA/seamB) validate that equivalence."""
    boundaries = [i for i, ch in enumerate(baseline_text) if ch == "\n"]
    rows = []
    for i in boundaries:
        mutant_raw = baseline_text[:i] + "\r" + baseline_text[i:]
        # success-path capture: universal newlines translate \r\n -> \n
        normalized = mutant_raw.replace("\r\n", "\n")
        rows.append({
            "boundary_index": i,
            "context": baseline_text[max(0, i - 24):i][-24:],
            "normalized_equals_baseline": normalized == baseline_text,
            "raw_landed_pin": landed in mutant_raw,
            "raw_full_pin": pin in mutant_raw,
            "text_landed_pin": landed in normalized,
            "text_full_pin": pin in normalized,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", default="corpus/fixtures")
    ap.add_argument("--scratch", default="/tmp/r101-mut08/scratch")
    ap.add_argument("--out", default="/var/tmp/r101-mut08")
    ap.add_argument("--godot", default="godot")
    args = ap.parse_args()

    fixtures = Path(args.fixtures)
    scratch = Path(args.scratch)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)

    src_path = fixtures / "r100b_seq.gd"
    src_text = src_path.read_text()
    src_sha = hashlib.sha256(src_path.read_bytes()).hexdigest()
    assert src_sha == SEQ_SHA, f"fixture bytes drifted: {src_sha}"

    shutil.copy2(fixtures / "project.godot", scratch / "project.godot")
    (scratch / "r100b_seq.gd").write_text(src_text)

    rows = landed_signatures(fixtures / "run_battery.py")
    pins = {name: row[4] for name, row in rows.items()}
    exits = {name: row[3] for name, row in rows.items()}

    variants = {"baseline": src_text}
    for name in SEAMS:
        variants[name] = make_variant(src_text, name)

    runs = {}
    for vname, vtext in variants.items():
        (scratch / "r100b_seq.gd").write_text(vtext)
        for mode, flag in (("clean", "--clean=1"), ("noclean", "--clean=0")):
            cmd = [args.godot, "--headless", "--path", str(scratch),
                   "--script", "res://r100b_seq.gd", "--", flag]
            for cap in ("text", "raw"):
                t0 = time.time()
                so, se, rc, err, path = run_capture(cmd, 60, cap == "text")
                key = f"{vname}/{mode}/{cap}"
                raw_file = out_dir / (key.replace("/", "_") + ".stdout.txt")
                raw_file.write_text(so)
                runs[key] = {
                    "stdout": so, "stderr": se, "rc": rc, "error": err,
                    "capture_path": path, "elapsed_s": round(time.time() - t0, 2),
                    "stdout_sha256": sha(so), "stdout_bytes": len(so.encode()),
                    "cr_count": so.count("\r"), "line_count": len(so.splitlines()),
                }

    # Timeout-branch probe: the timeout decode must be exercised on a real process.
    timeout_script = scratch / "r101_mut08_timeout.gd"
    pin_clean = pins["r100b_seq_clean"]
    timeout_script.write_text(
        "extends SceneTree\n"
        "func _initialize() -> void:\n"
        f'\tprint("{pin_clean}\\r")\n'
        '\tprint("SECOND_LINE")\n'
        "\tOS.delay_msec(5000)\n"
        "\tquit(0)\n")
    cmd = [args.godot, "--headless", "--path", str(scratch),
           "--script", "res://r101_mut08_timeout.gd"]
    so, se, rc, err, path = run_capture(cmd, 1.5, True)
    two_line_pin = pin_clean + "\nSECOND_LINE"
    timeout_probe = {
        "stdout_repr": repr(so), "stderr": se, "rc": rc, "error": err,
        "capture_path": path, "cr_count": so.count("\r"),
        "nonempty": bool(so.strip()),
        # pin presence in the decoded timeout text, and in the same text
        # after a success-path-style normalization
        "pin_in_decoded_landed": pin_clean in so,
        "pin_in_decoded_two_line": two_line_pin in so,
        "pin_in_normalized_two_line": two_line_pin in so.replace("\r\n", "\n"),
        # verdict on the harness timeout path (error is not None -> FAIL)
        "classify_landed_pin": classify_process(rc, err, so + se, 0, pin_clean, ALLOWED),
        "classify_two_line_pin": classify_process(rc, err, so + se, 0, two_line_pin, ALLOWED),
    }

    # Classification matrix.
    matrix = []
    sweeps = {}
    for vname in variants:
        for mode, row in (("clean", "r100b_seq_clean"), ("noclean", "r100b_seq_noclean")):
            base_text = runs[f"baseline/{mode}/text"]["stdout"] + runs[f"baseline/{mode}/text"]["stderr"]
            fr = full_replay_pin(base_text)
            if vname == "baseline":
                sweeps[mode] = boundary_sweep(base_text, fr, pins[row])
            for cap in ("text", "raw"):
                r = runs[f"{vname}/{mode}/{cap}"]
                blob = r["stdout"] + r["stderr"]
                matrix.append({
                    "variant": vname, "mode": mode, "capture": cap,
                    "stdout_sha256": r["stdout_sha256"],
                    "cr_count": r["cr_count"],
                    "landed_pin": classify_process(r["rc"], r["error"], blob, exits[row], pins[row], ALLOWED),
                    "full_replay_pin": classify_process(r["rc"], r["error"], blob, exits[row], fr, ALLOWED),
                })

    receipt = {
        "mutation": "MUT-8 CRLF seam injected into r100b_seq replay print sites",
        "mutation_sites": {k: {"needle": v[0], "replacement": v[1]} for k, v in SEAMS.items()},
        "fixture_sha256": src_sha,
        "landed_rows": {k: {"signature": v[4], "expected_exit": v[3]} for k, v in rows.items()},
        "runs": {k: {kk: vv for kk, vv in v.items() if kk not in ("stdout", "stderr")}
                 for k, v in runs.items()},
        "baseline_stdout_sha256": {m: runs[f"baseline/{m}/text"]["stdout_sha256"]
                                   for m in ("clean", "noclean")},
        "matrix": matrix,
        "boundary_sweep": sweeps,
        "timeout_probe": timeout_probe,
    }
    (out_dir / "mut08_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")

    print(f"fixture sha256 {src_sha}")
    print(f"{'variant':22s} {'mode':8s} {'cap':4s} {'cr':>3s} {'landed':>7s} {'full14':>7s} sha")
    for m in matrix:
        print(f"{m['variant']:22s} {m['mode']:8s} {m['capture']:4s} {m['cr_count']:3d} "
              f"{str(m['landed_pin']):>7s} {str(m['full_replay_pin']):>7s} {m['stdout_sha256'][:12]}")
    for mode, rows_ in sweeps.items():
        n = len(rows_)
        raw_seen = sum(1 for r in rows_ if not r["raw_full_pin"])
        print(f"sweep {mode}: {n} boundaries; full-pin rejects {raw_seen}/{n} in raw decode; "
              f"normalized==baseline {sum(1 for r in rows_ if r['normalized_equals_baseline'])}/{n}; "
              f"text full-pin rejects {sum(1 for r in rows_ if not r['text_full_pin'])}/{n}; "
              f"raw landed-pin rejects {sum(1 for r in rows_ if not r['raw_landed_pin'])}/{n}")
    print("timeout probe:", json.dumps({k: timeout_probe[k] for k in
                                        ("nonempty", "cr_count", "pin_in_decoded_landed",
                                         "pin_in_decoded_two_line", "pin_in_normalized_two_line",
                                         "classify_landed_pin", "classify_two_line_pin")}))
    print("timeout stdout repr:", timeout_probe["stdout_repr"][:200])


if __name__ == "__main__":
    main()
