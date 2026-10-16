#!/usr/bin/env python3
"""r93-simplifier fold verification — fresh-process receipts on the COMMITTED bytes.

Re-runs every r93 row's own arm in the battery's exact launch shape
(`godot --headless --path <scratch> --script res://<script> -- <flags>` via
subprocess.run, no shell), classifies each receipt with the PRODUCTION
`classify_process` AST-extracted from the committed harness plus the row's own
committed signature, and re-derives the four encoded folds from the fresh bytes:

  fold 1  runtime overshoot  (BACK below start, SPRING above end, no clamp)
  fold 2  N-1 await law      (x1=0.0; --fixed-fps 30/60/120: pos10 = 9/N,
                              x2/x3/x5 = 1/2/4 applied steps)
  fold 3  crossfade w_i=(i-1)/(N-1) at 3 granularities + await immunity
  fold 4  DEFERRED -> process frame AND physics frame flush

Plus: byte-stability of the clause-pinned mode cells across reps, and the
cross-arm substring check the author's labrat flagged (phys_delta / finished_010
appearing on a non-row arm).

Usage: python3 verify_folds.py [--reps 3] [--fixed-fps-reps 2]
Outputs: fold-verification.json, fold-verification.log, fold-runs/<stamp>/**
"""
import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"
PROJ_SRC = HERE / "proj"
GODOT = "godot"


def extract_production_classify(path):
    """AST-extract the classify_process FunctionDef source segment (r89-r93
    convention) and exec it in a bare namespace."""
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


def extract_rows(path):
    src = path.read_text()
    tree = ast.parse(src)
    rows = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                rows[t[0]] = {"script": t[1], "flags": list(t[2]),
                              "exit": t[3], "sig": t[4]}
    return {k: v for k, v in rows.items() if k.startswith("r93_")}


def make_scratch(dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PROJ_SRC, dest)
    pf = dest / "project.godot"
    stamp = dest.name
    pf.write_text(pf.read_text().replace(
        'config/name="MechanicOneShotTest"',
        'config/name="MechanicOneShotTest-%s"' % stamp, 1))
    return dest


def launch(proj, script, flags, extra=()):
    cmd = [GODOT, "--headless", *extra, "--path", str(proj),
           "--script", "res://" + script, "--", *flags]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        out, err, rc = proc.stdout, proc.stderr, proc.returncode
        terr = None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        rc, terr = None, "TIMEOUT"
    except OSError as exc:
        out, err, rc, terr = "", str(exc), None, "OSError"
    return {"cmd": cmd, "stdout": out, "stderr": err, "rc": rc, "error": terr,
            "wall_s": round(time.time() - t0, 3)}


def num(s):
    return float(s)


def check_frame_law(out, expect_rate):
    """N-1 await law on the `frame` arm.

    The `move` animation is 0 -> 100 over 1.0 s; xs[i] is read after
    (1,2,3,5,10) awaits => (0,1,2,4,9) applied steps.  Under --fixed-fps N the
    per-step value is 100/N; pos10 is the animation *position* = 9/N.
    The ff30 boot transient perturbs steps >= 2 (boundary §6), so only x2 is
    checked exactly there; the cumulative position stays exact.
    """
    checks = {}
    m = re.search(r"idle=\[x1=([-\d.e]+),x2=([-\d.e]+),x3=([-\d.e]+),x5=([-\d.e]+),x10=([-\d.e]+)\]", out)
    if not m:
        return {"parse": False}
    x1, x2, x3, x5, x10 = (num(g) for g in m.groups())
    checks["x1"] = x1
    checks["x1_is_pre_play_zero"] = x1 == 0.0
    checks["x2"], checks["x3"], checks["x5"], checks["x10"] = x2, x3, x5, x10
    if expect_rate:
        step = 100.0 / expect_rate
        checks["expected_step_value"] = step
        checks["x2_is_1_step"] = abs(x2 - 1 * step) < 1e-3
        if expect_rate == 30:
            # boot transient: steps 2 and 4 are perturbed, but by step 9 the
            # cumulative value is exact again (the transient redistributes the
            # elapsed time, it does not lose it) and pos10 is exact.
            checks["x3_transient_affected"] = abs(x3 - 2 * step) > 1e-3
            checks["x5_transient_affected"] = abs(x5 - 4 * step) > 1e-3
            checks["x10_is_9_steps"] = abs(x10 - 9 * step) < 1e-3
        else:
            checks["x3_is_2_steps"] = abs(x3 - 2 * step) < 1e-3
            checks["x5_is_4_steps"] = abs(x5 - 4 * step) < 1e-3
            checks["x10_is_9_steps"] = abs(x10 - 9 * step) < 1e-3
        m2 = re.search(r"pos10=([-\d.e]+)", out)
        if m2:
            checks["pos10"] = num(m2.group(1))
            checks["pos10_is_9_steps"] = abs(num(m2.group(1)) - 9.0 / expect_rate) < 1e-9
    m3 = re.search(r"mixer_applied_10=(\d+)", out)
    if m3:
        checks["mixer_applied_10_is_10"] = int(m3.group(1)) == 10
    m4 = re.search(r"phys=\[y1=([-\d.e]+),y2=([-\d.e]+),y3=([-\d.e]+),y6=([-\d.e]+)\]", out)
    if m4:
        checks["phys_lattice"] = [num(g) for g in m4.groups()]
        checks["phys_y1_y2_zero"] = num(m4.group(1)) == 0.0 and num(m4.group(2)) == 0.0
        checks["phys_increment_2ticks"] = abs((num(m4.group(3)) - num(m4.group(2))) - 2.0 / 60.0 * 100.0) < 1e-2
    m5 = re.search(r"phys_delta=([-\d.e]+)", out)
    if m5:
        checks["phys_delta"] = num(m5.group(1))
        checks["phys_delta_is_1_60"] = abs(num(m5.group(1)) - 1.0 / 60.0) < 1e-9
    return checks


def check_overshoot(out):
    checks = {}
    m = re.search(r"overshoot=\[back025=([-\d.e]+),back050=([-\d.e]+)\]", out)
    m2 = re.search(r"overshoot2=\[spr050=([-\d.e]+),spr100=([-\d.e]+),ela025=([-\d.e]+)\]", out)
    m3 = re.search(r"clamp=\[neg=([-\d.e]+),over=([-\d.e]+)\]", out)
    if not (m and m2 and m3):
        return {"parse": False}
    back025, back050 = num(m.group(1)), num(m.group(2))
    spr050, spr100, ela025 = num(m2.group(1)), num(m2.group(2)), num(m2.group(3))
    neg, over = num(m3.group(1)), num(m3.group(2))
    checks["back025"] = back025
    checks["back_below_start"] = back025 < 1.0
    checks["back050"] = back050
    checks["back_midpoint"] = abs(back050 - 5.5) < 1e-6
    checks["spr050"] = spr050
    checks["spring_above_end"] = spr050 > 10.0
    checks["spr100"] = spr100
    checks["spring_endpoint"] = abs(spr100 - 10.0) < 1e-6
    checks["ela025"] = ela025
    checks["static_no_clamp"] = (neg == -5.0 and over == 15.0)
    return checks


def check_blend(out):
    checks = {}
    for name, N in (("finished_010", 10), ("finished_005", 20), ("finished_020", 5)):
        m = re.search(re.escape(name) + r"=\[([^\]]*)\]", out)
        if not m:
            checks["%s_parsed" % name] = False
            continue
        vals = [float(x) for x in m.group(1).split(",")]
        expect = [100.0 + 400.0 * i / (N - 1) for i in range(N)]
        checks["%s_parsed" % name] = True
        checks["%s_len" % name] = len(vals)
        checks["%s_law" % name] = (len(vals) == N
                                   and max(abs(a - b) / max(1.0, abs(b))
                                           for a, b in zip(vals, expect)) < 5e-6)
    mi = re.search(r"interleaved=\[([^\]]*)\]", out)
    mf = re.search(r"finished_010=\[([^\]]*)\]", out)
    if mi and mf:
        checks["interleaved_eq_plain"] = mi.group(1) == mf.group(1)
    checks["interleaved_eq_plain_token"] = "interleaved_eq_plain=true" in out
    mh = re.search(r"hard_after_frame=([-\d.e]+)", out)
    if mh:
        checks["hard_after_frame_500"] = num(mh.group(1)) == 500.0
    return checks


def check_deferred(out):
    checks = {}
    for key, frag in (("manual_def", "manual_def=[after_adv=[],next_proc=[7,8],second_proc=[7,8]]"),
                      ("manual_def_phys", "manual_def_phys=[after_adv=[],after_phys=[7,8]]"),
                      ("two_adv", "two_adv=[after=[],flush=[7,8]]"),
                      ("immediate", "immediate=[after_adv=[7,8],after_frame=[7,8]]")):
        checks["%s_exact" % key] = frag in out
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--fixed-fps-reps", type=int, default=2)
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = HERE / "fold-runs" / stamp
    proj = make_scratch(run_dir / "proj")

    seg, seg_sha, classify_process = extract_production_classify(HARNESS)
    rows = extract_rows(HARNESS)
    log = []
    log.append("classify_process segment sha256 = %s (%d bytes)" % (seg_sha, len(seg)))
    log.append("rows: %d" % len(rows))

    result = {"stamp": stamp, "classifier_segment_sha256": seg_sha,
              "godot": subprocess.run([GODOT, "--version"], capture_output=True,
                                      text=True).stdout.strip(),
              "reps": args.reps, "rows": {}, "law_runs": {}}

    # ---- per-row fresh reps in the battery launch shape ----
    per_rep_lines = {}
    for case, row in rows.items():
        reps = []
        for i in range(args.reps):
            r = launch(proj, row["script"], row["flags"])
            output = r["stdout"] + r["stderr"]
            passed = classify_process(r["rc"], r["error"], output,
                                      row["exit"], row["sig"], ())
            reps.append({"rc": r["rc"], "error": r["error"], "wall_s": r["wall_s"],
                         "stdout_lines": r["stdout"].splitlines(),
                         "stderr_bytes": len(r["stderr"]),
                         "pass": bool(passed)})
            per_rep_lines.setdefault(case, []).append(r["stdout"])
            log.append("%-38s rep%d rc=%s pass=%s wall=%.2fs stderr=%dB"
                       % (case, i + 1, r["rc"], passed, r["wall_s"], len(r["stderr"])))
        result["rows"][case] = {
            "script": row["script"], "flags": row["flags"], "sig_len": len(row["sig"]),
            "pass_count": sum(1 for x in reps if x["pass"]), "reps": args.reps,
            "rep_detail": reps}

    # ---- byte-stability of the full line per arm (mode vs stable) ----
    for case, outs in per_rep_lines.items():
        uniq = len({o for o in outs})
        result["rows"][case]["distinct_stdout"] = uniq
    log.append("")
    log.append("== per-row distinct stdout across %d reps ==" % args.reps)
    for case, row in sorted(result["rows"].items()):
        log.append("  %-38s distinct=%d pass=%d/%d"
                   % (case, row["distinct_stdout"], row["pass_count"], row["reps"]))

    # ---- law runs: N-1 await law under fixed fps ----
    log.append("")
    log.append("== N-1 await law under --fixed-fps (frame arm) ==")
    for rate in (30, 60, 120):
        key = "frame_fixed_fps_%d" % rate
        result["law_runs"][key] = []
        for i in range(args.fixed_fps_reps):
            r = launch(proj, "r93b_anim.gd", ["--arm=frame"], extra=("--fixed-fps", str(rate)))
            out = r["stdout"] + r["stderr"]
            checks = check_frame_law(out, rate)
            result["law_runs"][key].append({"rc": r["rc"], "checks": checks,
                                            "stdout": r["stdout"].splitlines()})
            law_keys = ("x1_is_pre_play_zero", "x2_is_1_step", "pos10_is_9_steps",
                        "x3_is_2_steps", "x5_is_4_steps", "x10_is_9_steps",
                        "x3_transient_affected", "x5_transient_affected",
                        "x10_transient_affected")
            law_ok = all(v for k, v in checks.items() if k in law_keys)
            log.append("  ff%-4d rep%d rc=%s x1=%s x2=%s x3=%s x5=%s pos10=%s law=%s"
                       % (rate, i + 1, r["rc"], checks.get("x1"), checks.get("x2"),
                          checks.get("x3"), checks.get("x5"), checks.get("pos10"),
                          law_ok))
    # default-rate law run (battery shape)
    for i in range(args.fixed_fps_reps):
        r = launch(proj, "r93b_anim.gd", ["--arm=frame"])
        out = r["stdout"] + r["stderr"]
        checks = check_frame_law(out, None)
        result["law_runs"].setdefault("frame_default", []).append(
            {"rc": r["rc"], "checks": checks, "stdout": r["stdout"].splitlines()})
        log.append("  default rep%d rc=%s x1=%s mixer10=%s phys_delta=%s"
                   % (i + 1, r["rc"], checks.get("x1"),
                      checks.get("mixer_applied_10_is_10"), checks.get("phys_delta")))

    # ---- fold-specific law extraction from the per-row receipts ----
    log.append("")
    log.append("== fold checks (from the per-row receipts) ==")
    folds = {}
    for case, outs in per_rep_lines.items():
        out = outs[0]
        if case == "r93_anim_overshoot":
            folds["overshoot"] = [check_overshoot(o) for o in outs]
        if case in ("r93_anim_blend_finished", "r93_anim_blend_interleaved"):
            folds.setdefault("blend", []).append({case: [check_blend(o) for o in outs]})
        if case == "r93_anim_deferred_flush":
            folds["deferred"] = [check_deferred(o) for o in outs]
    result["folds"] = folds
    log.append("overshoot reps: %s" % json.dumps(folds.get("overshoot"), indent=1))
    log.append("deferred reps: %s" % json.dumps(folds.get("deferred"), indent=1))

    # ---- cross-arm substring check (author-labrat F2 corroboration) ----
    log.append("")
    log.append("== cross-arm substring check ==")
    clock = launch(proj, "r93b_anim.gd", ["--arm=clock"])
    clock_out = clock["stdout"] + clock["stderr"]
    cross = {
        "phys_delta_token_in_clock": "phys_delta=0.01666666666667" in clock_out,
        "finished_010_token_in_clock": "finished_010=[100.0," in clock_out,
    }
    # does any r93 row's signature get emitted by an arm that is NOT its own?
    arms = {}
    for case, row in rows.items():
        arms.setdefault(row["script"], set()).add(row["flags"][0])
    foreign = []
    arm_outputs = {}
    for script, arm_set in arms.items():
        for arm in sorted(arm_set):
            r = launch(proj, script, [arm])
            arm_outputs[(script, arm)] = r["stdout"] + r["stderr"]
    for case, row in rows.items():
        own = (row["script"], row["flags"][0])
        for (script, arm), o in arm_outputs.items():
            if (script, arm) == own:
                continue
            if isinstance(row["sig"], str) and row["sig"] in o:
                foreign.append({"case": case, "foreign_script": script,
                                "foreign_arm": arm})
    cross["signature_satisfied_by_a_foreign_arm"] = foreign
    cross["arms_launched"] = len(arm_outputs)
    # fallback path: an unknown --arm must satisfy no r93 signature
    fallback_hits = []
    for script in sorted(arms):
        r = launch(proj, script, ["--arm=__bogus__"])
        o = r["stdout"] + r["stderr"]
        for case, row in rows.items():
            if row["script"] == script and isinstance(row["sig"], str) and row["sig"] in o:
                fallback_hits.append({"case": case, "script": script})
    cross["signature_satisfied_by_the_unknown_arm_fallback"] = fallback_hits
    cross["clock_out_head"] = clock_out.splitlines()[:1]
    result["cross_arm"] = cross
    log.append(json.dumps(cross, indent=1)[:2000])

    (run_dir / "fold-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "fold-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "fold-verification.log").write_text("\n".join(log) + "\n")
    print("\n".join(log))
    print("\nwrote %s" % (run_dir / "fold-verification.json"))


if __name__ == "__main__":
    sys.exit(main())
