#!/usr/bin/env python3
"""r92-simplifier fold verification on the committed 5900431 bytes.

Extracts the PRODUCTION classify_process verbatim (AST) from the committed
run_battery.py and replicates execute()'s full path (rc + signature str-or-
envelope + expected_errors + required_stderr + SCRIPT/Parse clauses).

Arms run in the battery's launch shape:
  godot --headless [--fixed-fps N] --path <proj> --script res://tilemap_lattice.gd -- --arm=<a>

Receipts land in corpus/live/r92-simplifier/fold-runs/<mode>/<arm>.{out,err,rc}.

Usage: python3 verify_folds.py [mode ...]      (default: default ff120 ff150 ff600)
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIX = HERE / "committed-fixtures" / "run_battery.py"
PROJ = HERE / "proj"
GODOT = "/usr/bin/godot"

PASS_ARMS = ["census", "atlas", "cells", "custom", "terrain", "pattern",
             "encoding", "fixinvalid", "srcids", "physics", "timing",
             "quadrant", "nav"]
CRASH_ARM = "nullts"


def extract(path):
    src = path.read_text()
    tree = ast.parse(src)
    fn_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            fn_src = ast.get_source_segment(src, node)
            break
    ns = {}
    exec("import re\n" + fn_src, ns)
    cases, exp_errors, req_stderr = {}, {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                if t[0].startswith("r92_"):
                    cases[t[0]] = {"script": t[1], "flags": t[2],
                                   "expected_exit": t[3], "signature": t[4]}
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "r92_tilemap_atlas" in keys and "nav_lattice_bake" in keys:
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value.startswith("r92_"):
                        exp_errors[k.value] = ast.literal_eval(v)
            if "r92_tilemap_nullts_crash" in keys and "nav_lattice_teardown_crash" in keys:
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value.startswith("r92_"):
                        req_stderr[k.value] = ast.literal_eval(v)
    return (hashlib.sha256(fn_src.encode()).hexdigest(), ns["classify_process"],
            cases, exp_errors, req_stderr)


def run_arm(mode, arm, timeout=15):
    flags = []
    if mode == "ff120":
        flags = ["--fixed-fps", "120"]
    elif mode == "ff150":
        flags = ["--fixed-fps", "150"]
    elif mode == "ff600":
        flags = ["--fixed-fps", "600"]
    cmd = [GODOT, "--headless", *flags, "--path", str(PROJ),
           "--script", "res://tilemap_lattice.gd", "--", "--arm=" + arm]
    out_dir = HERE / "fold-runs" / mode
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        rc = None
    (out_dir / (arm + ".out")).write_text(stdout)
    (out_dir / (arm + ".err")).write_text(stderr)
    (out_dir / (arm + ".rc")).write_text("%s\n" % rc)
    return stdout, stderr, rc


def classify_row(classify, case, row, stdout, stderr, rc,
                 drop_required_stderr=False, only_payload=None):
    """Replicate execute()'s classification path for one row."""
    evidence = row["signature"]
    sigs = list(evidence) if isinstance(evidence, (tuple, list)) else [evidence]
    if only_payload is not None:
        sigs = [sigs[only_payload]]
    entries = tuple(row.get("expected_errors", ()))
    passed = any(classify(rc, None, stdout + stderr, row["expected_exit"], s, entries)
                 for s in sigs)
    req = () if drop_required_stderr else tuple(row.get("required_stderr", ()))
    if req:
        passed = (passed
                  and all(fragment in stderr for fragment in req)
                  and any(sig in stdout for sig in sigs))
    if "SCRIPT ERROR:" in stdout + stderr or "Parse Error:" in stdout + stderr:
        passed = False
    return passed


def field_map(line):
    out = {}
    for p in line.split(" "):
        if "=" in p:
            k, _, v = p.partition("=")
            out[k] = v
    return out


def main():
    modes = sys.argv[1:] or ["default", "ff120", "ff150", "ff600"]
    seg_sha, classify, cases, exp_errors, req_stderr = extract(FIX)
    print("classify_process segment sha256: %s" % seg_sha)
    print("r92 rows: %d  allowlist rows: %d  required_stderr rows: %d"
          % (len(cases), len(exp_errors), len(req_stderr)))

    rows = {}
    for case, row in cases.items():
        row = dict(row)
        row["expected_errors"] = exp_errors.get(case, ())
        row["required_stderr"] = req_stderr.get(case, ())
        rows[case] = row

    results = {"classify_segment_sha256": seg_sha, "modes": {}}
    print()
    print("== A. envelope mode partition (nav, 3 reps per mode) ==")
    env = {}
    for mode in modes:
        env[mode] = []
        for rep in range(3):
            stdout, stderr, rc = run_arm(mode, "nav")
            row = rows["r92_tilemap_nav"]
            sigs = row["signature"]
            m = [classify(rc, None, stdout + stderr, row["expected_exit"], s,
                          row["expected_errors"]) for s in sigs]
            ok = classify_row(classify, "r92_tilemap_nav", row, stdout, stderr, rc)
            env[mode].append({"rc": rc, "payload_matches": m, "row_pass": ok,
                              "line": [l for l in stdout.splitlines() if l.startswith("PASS ")]})
        vals = [r["payload_matches"] for r in env[mode]]
        print("  %-8s reps=3 payload_matches=%s row_pass=%s"
              % (mode, vals, [r["row_pass"] for r in env[mode]]))
    results["modes"]["nav_envelope"] = env

    print()
    print("== B. nav field variance across modes (envelope minimality) ==")
    lines = {}
    for mode in modes:
        line = env[mode][0]["line"][0]
        lines[mode] = field_map(line)
    keys = sorted({k for f in lines.values() for k in f})
    varying = {}
    for k in keys:
        vals = sorted({f.get(k, "<absent>") for f in lines.values()})
        if len(vals) > 1:
            varying[k] = vals
    print("  modes=%s fields=%d varying=%d" % (",".join(modes), len(keys), len(varying)))
    for k, vals in varying.items():
        print("    VARY %-24s %s" % (k, vals))
    results["modes"]["nav_field_variance"] = varying

    print()
    print("== C. nullts crash row: required_stderr liveness (3 reps) ==")
    nullts = []
    for rep in range(3):
        stdout, stderr, rc = run_arm("default", CRASH_ARM)
        row = rows["r92_tilemap_nullts_crash"]
        q1 = classify_row(classify, "r92_tilemap_nullts_crash", row, stdout, stderr, rc)
        q3 = classify_row(classify, "r92_tilemap_nullts_crash", row, stdout, stderr, rc,
                          drop_required_stderr=True)
        # Q2: same rc, foreign stderr (wrong cause, same signal class)
        foreign_err = (HERE / "foreign-crash.err").read_text()
        q2 = classify_row(classify, "r92_tilemap_nullts_crash", row, stdout, foreign_err, rc)
        nullts.append({"rc": rc, "Q1_row_pass": q1, "Q2_foreign_stderr_rejects": not q2,
                       "Q3_drop_required_stderr_still_passes": q3,
                       "stdout_anchor": "R92 nullts about_to_call_tile_data=1" in stdout,
                       "fragments_in_stderr": [f in stderr for f in row["required_stderr"]]})
    print("  " + json.dumps(nullts, indent=2).replace("\n", "\n  "))
    results["modes"]["nullts_required_stderr"] = nullts

    print()
    print("== D. allowlist liveness (bare vs allowlisted, fresh reps) ==")
    live = {}
    for case, row in sorted(rows.items()):
        if not row["expected_errors"]:
            continue
        arm = row["flags"][0].split("=", 1)[1]
        stdout, stderr, rc = run_arm("default", arm)
        bare = classify_row(classify, case, {**row, "expected_errors": ()},
                            stdout, stderr, rc)
        allow = classify_row(classify, case, row, stdout, stderr, rc)
        live[case] = {"bare_rejects": not bare, "allowlisted_passes": allow,
                      "n_entries": len(row["expected_errors"])}
        print("  %-28s entries=%d bare_rejects=%s allowlisted_passes=%s"
              % (case, len(row["expected_errors"]), not bare, allow))
    results["modes"]["allowlist_liveness"] = live

    print()
    print("== E. tombstone encoding decode (from the landed encoding row) ==")
    stdout, stderr, rc = run_arm("default", "encoding")
    line = [l for l in stdout.splitlines() if l.startswith("PASS ")][0]
    f = field_map(line)

    def parse(s):
        return [int(x) for x in s.strip("[]").split(",") if x != ""]

    def records(b):
        return [b[i:i + 12] for i in range(2, len(b), 12)]
    tomb = {
        "header": parse(f["tomb_set_bytes"])[:2],
        "set_record": records(parse(f["tomb_set_bytes"])),
        "erase_record": records(parse(f["tomb_erase_bytes"])),
        "clear_record": records(parse(f["tomb_clear_bytes"])),
        "clear_then_set_records": records(parse(f["tomb_clear_set_bytes"])),
        "stride": f["stride"],
    }
    tomb["erase_tail_all_ff"] = all(x == 255 for x in tomb["erase_record"][0][6:])
    tomb["erase_xy_preserved"] = tomb["erase_record"][0][:4] == tomb["set_record"][0][:4]
    tomb["clear_equals_erase"] = tomb["clear_record"] == tomb["erase_record"]
    tomb["high_water_mark"] = (len(tomb["clear_then_set_records"]) == 2
                               and tomb["clear_then_set_records"][1][:4] == [5, 0, 5, 0])
    print("  " + json.dumps(tomb, indent=2).replace("\n", "\n  "))
    results["modes"]["tombstone_decode"] = tomb

    print()
    print("== F. PASS-arm row classification on fresh default reps ==")
    fresh = {}
    for case, row in sorted(rows.items()):
        if case == "r92_tilemap_nullts_crash":
            continue
        arm = row["flags"][0].split("=", 1)[1]
        stdout, stderr, rc = run_arm("default", arm)
        ok = classify_row(classify, case, row, stdout, stderr, rc)
        fresh[case] = ok
        print("  %-28s rc=%s row_pass=%s" % (case, rc, ok))
    results["modes"]["fresh_rows"] = fresh

    out = HERE / "fold-verification.json"
    out.write_text(json.dumps(results, indent=2) + "\n")
    print()
    print("wrote %s" % out)
    all_ok = (all(r["row_pass"] for m in env.values() for r in m)
              and all(v["bare_rejects"] and v["allowlisted_passes"] for v in live.values())
              and all(fresh.values()))
    print("FOLDS_LIVE=%s" % all_ok)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
