#!/usr/bin/env python3
"""r94-simplifier fold verification — fresh-process receipts on the COMMITTED bytes.

Re-runs every r94 row's own arm in the battery's exact launch shape
(`godot --headless --path <scratch> --script res://particles_lattice.gd -- <flags>`)
against a byte-verified copy of the committed fixture, classifies each receipt
with the PRODUCTION `classify_process` AST-extracted from the committed harness
plus the row's own committed signature, and re-derives the r94 folds from the
fresh bytes:

  fold A  cpu_pause resume windows widened [4,7] -> [1,7] (ff30 acceptance)
  fold B  cpu_request closed form floor(L/step)+1 (7-step ladder; round fails 2)
  fold C  the fixture-vs-frozen-probe code diff is exactly the 4 declared lines
  fold D  each arm satisfies only its own signature; unknown arm matches none

Usage: python3 verify_folds.py [--reps 3] [--ff30-reps 3]
Outputs: fold-verification.json, fold-verification.log, fold-runs/<stamp>/**
"""
import argparse
import ast
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"
FIXTURE = HERE / "committed-fixtures" / "particles_lattice.gd"
FROZEN = HERE.parent / "r94-scout" / "probes" / "particles_lattice.gd"
PROJ_SRC = HERE / "proj"
GODOT = "godot"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
RUNS = HERE / "fold-runs" / STAMP


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_production_classify(path):
    src = path.read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name == "classify_process":
                    seg = ast.get_source_segment(src, sub)
                    ns = {}
                    exec(seg, ns)
                    return seg, hashlib.sha256(seg.encode()).hexdigest(), ns["classify_process"]
    raise SystemExit("classify_process not found in %s" % path)


def extract_rows(path, prefix="r94_"):
    src = path.read_text()
    tree = ast.parse(src)
    rows = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                rows[t[0]] = {"script": t[1], "flags": list(t[2]),
                              "exit": t[3], "sig": t[4]}
    return {k: v for k, v in rows.items() if k.startswith(prefix)}


def make_scratch(dest, fixture_src):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PROJ_SRC, dest)
    shutil.copy2(fixture_src, dest / "particles_lattice.gd")
    pf = dest / "project.godot"
    pf.write_text(pf.read_text().replace(
        'config/name="MechanicOneShotTest"',
        'config/name="MechanicOneShotTest-%s"' % dest.name, 1))
    return dest


def launch(proj, script, flags, extra=(), timeout=8):
    cmd = [GODOT, "--headless", *extra, "--path", str(proj),
           "--script", "res://" + script, "--", *flags]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out, err, rc, terr = proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        rc, terr = None, "TIMEOUT"
    except OSError as exc:
        out, err, rc, terr = "", str(exc), None, "OSError"
    return {"cmd": cmd, "stdout": out, "stderr": err, "rc": rc, "error": terr,
            "wall_s": round(time.time() - t0, 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--ff30-reps", type=int, default=3)
    args = ap.parse_args()

    RUNS.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(s):
        log_lines.append(s)
        print(s, flush=True)

    seg, seg_sha, classify = extract_production_classify(HARNESS)
    rows = extract_rows(HARNESS)
    log("production classify_process segment sha256: %s" % seg_sha)
    log("committed fixture sha256: %s" % sha256(FIXTURE))
    log("frozen scout probe sha256: %s" % sha256(FROZEN))
    log("r94 rows: %d" % len(rows))

    out = {"stamp": STAMP, "classify_segment_sha256": seg_sha,
           "fixture_sha256": sha256(FIXTURE), "frozen_sha256": sha256(FROZEN),
           "rows": {}, "ff30": {}, "request_ladder": {}, "unknown_arm": {},
           "cross_arm": {}, "raw_vs_frozen_code_diff": None}

    # ---- fold C: static code diff fixture vs frozen probe (comments stripped)
    def code_lines(path):
        outl = []
        for i, l in enumerate(path.read_text().splitlines(), 1):
            s = l.split("#", 1)[0].strip()
            if s:
                outl.append((i, s))
        return outl

    a = code_lines(FROZEN)
    b = code_lines(FIXTURE)
    import difflib
    diff = [d for d in difflib.unified_diff(
        [x[1] for x in a], [x[1] for x in b], lineterm="", n=0)
        if d.startswith(("+", "-")) and not d.startswith(("+++", "---"))]
    out["raw_vs_frozen_code_diff"] = diff
    log("fold C: non-comment code diff lines fixture vs frozen probe: %d" % len(diff))
    for d in diff:
        log("   %s" % d)

    # ---- per-arm receipts on the committed bytes
    scratch = make_scratch(RUNS / "scratch", FIXTURE)
    log("scratch fixture sha256: %s" % sha256(scratch / "particles_lattice.gd"))
    for case, row in sorted(rows.items()):
        arm = row["flags"][0].split("=", 1)[1]
        reps = []
        for r in range(1, args.reps + 1):
            rec = launch(scratch, row["script"], row["flags"])
            merged = rec["stdout"] + rec["stderr"]
            verdict = classify(rec["rc"], rec["error"], merged, row["exit"],
                               row["sig"], ())
            reps.append({"rep": r, "rc": rec["rc"], "stderr_bytes": len(rec["stderr"]),
                         "wall_s": rec["wall_s"], "classify": verdict,
                         "sig_present": row["sig"] in merged,
                         "stdout_sha256": hashlib.sha256(rec["stdout"].encode()).hexdigest(),
                         "stdout": rec["stdout"], "stderr": rec["stderr"]})
        out["rows"][case] = {"arm": arm, "reps": reps,
                             "all_pass": all(x["classify"] for x in reps),
                             "all_sig": all(x["sig_present"] for x in reps),
                             "stderr_all_zero": all(x["stderr_bytes"] == 0 for x in reps)}
        log("  %-38s arm=%-14s classify=%s sig=%s stderr0=%s"
            % (case, arm, all(x["classify"] for x in reps),
               all(x["sig_present"] for x in reps),
               all(x["stderr_bytes"] == 0 for x in reps)))

    # ---- fold A: cpu_pause at --fixed-fps 30, folded vs frozen
    ff30_folded = []
    for r in range(1, args.ff30_reps + 1):
        rec = launch(scratch, "particles_lattice.gd", ["--arm=cpu_pause"],
                     extra=["--fixed-fps", "30"], timeout=25)
        merged = rec["stdout"] + rec["stderr"]
        line = next((l for l in merged.splitlines() if l.startswith("PASS particles_lattice cpu_pause")), "")
        ff30_folded.append({"rep": r, "rc": rec["rc"], "stderr_bytes": len(rec["stderr"]),
                            "line": line,
                            "ok_true": re.search(r"\bcpu_pause ok=true\b", line) is not None,
                            "classify": classify(rec["rc"], rec["error"], merged, 0,
                                                 rows["r94_particles_cpu_pause"]["sig"], ())})
    ff30_frozen = []
    frozen_scratch = make_scratch(RUNS / "scratch-frozen", FROZEN)
    for r in range(1, args.ff30_reps + 1):
        rec = launch(frozen_scratch, "particles_lattice.gd", ["--arm=cpu_pause"],
                     extra=["--fixed-fps", "30"], timeout=25)
        merged = rec["stdout"] + rec["stderr"]
        line = next((l for l in merged.splitlines() if l.startswith("PASS particles_lattice cpu_pause")), "")
        ff30_frozen.append({"rep": r, "rc": rec["rc"], "line": line,
                            "ok_true": re.search(r"\bcpu_pause ok=true\b", line) is not None})
    out["ff30"] = {"folded": ff30_folded, "frozen": ff30_frozen}
    log("fold A: ff30 cpu_pause folded ok=true: %s / frozen ok=true: %s"
        % ([x["ok_true"] for x in ff30_folded], [x["ok_true"] for x in ff30_frozen]))
    for x in ff30_folded + ff30_frozen:
        log("   %s" % x["line"])

    # ---- fold B: request closed form over 7 steps (variant copy, spec list only)
    var_src = FIXTURE.read_text()
    var_src2 = var_src.replace("for spec in [0.1, 0.05]:",
                               "for spec in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4]:", 1)
    assert var_src2 != var_src, "spec-list anchor not found"
    var_proj = make_scratch(RUNS / "scratch-ladder", FIXTURE)
    (var_proj / "particles_lattice.gd").write_text(var_src2)
    rec = launch(var_proj, "particles_lattice.gd", ["--arm=cpu_request"], timeout=25)
    merged = rec["stdout"] + rec["stderr"]
    ladder = []
    for m in re.finditer(r"step([\d.]+)\[fin_call1=(\d+) fin_call_raw=(-?\d+) expected=(\d+) ok=(\w+) n_fin=(\d+)\]", merged):
        spec, call1, raw, expected, ok, nfin = m.groups()
        spec_f = float(spec)
        ladder.append({"step": spec_f, "fin_call1": int(call1), "raw": int(raw),
                       "expected": int(expected), "ok": ok, "n_fin": int(nfin),
                       "floor_plus_1": math.floor(0.5 / spec_f) + 1,
                       "round_plus_1": math.floor(0.5 / spec_f + 0.5) + 1})
    out["request_ladder"] = {"receipt": merged, "rows": ladder,
                             "floor_fits_all": all(x["fin_call1"] == x["floor_plus_1"] for x in ladder),
                             "round_fails": [x["step"] for x in ladder
                                             if x["round_plus_1"] != x["fin_call1"]]}
    log("fold B: 7-step ladder floor fits all: %s  round fails at: %s"
        % (out["request_ladder"]["floor_fits_all"], out["request_ladder"]["round_fails"]))
    for x in ladder:
        log("   step=%.2f fin_call1=%d floor+1=%d round+1=%d"
            % (x["step"], x["fin_call1"], x["floor_plus_1"], x["round_plus_1"]))

    # ---- fold D: unknown arm + cross-arm matrix
    rec = launch(scratch, "particles_lattice.gd", ["--arm=__bogus__"])
    merged = rec["stdout"] + rec["stderr"]
    matched = [k for k, v in rows.items() if v["sig"] in merged]
    out["unknown_arm"] = {"rc": rec["rc"], "line": next(
        (l for l in merged.splitlines() if "unknown arm" in l), ""), "matched_rows": matched}
    log("fold D: unknown arm rc=%s matched rows=%s" % (rec["rc"], matched))

    # cross-arm: for each arm, count which signatures match its receipts
    cross = {}
    for case, row in sorted(rows.items()):
        merged = "\n".join(r["stdout"] + r["stderr"] for r in out["rows"][case]["reps"])
        cross[case] = sorted(k for k, v in rows.items() if v["sig"] in merged)
    out["cross_arm"] = cross
    bad = {k: v for k, v in cross.items() if v != [k]}
    log("fold D: cross-arm violations: %d" % len(bad))
    for k, v in bad.items():
        log("   %s matched by %s" % (k, v))

    (RUNS / "fold-verification.json").write_text(json.dumps(out, indent=1))
    (HERE / "fold-verification.json").write_text(json.dumps(out, indent=1))
    (HERE / "fold-verification.log").write_text("\n".join(log_lines) + "\n")
    print("\nwrote %s" % (RUNS / "fold-verification.json"))


if __name__ == "__main__":
    main()
