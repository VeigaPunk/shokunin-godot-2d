#!/usr/bin/env python3
"""r92 critic seat probe driver.

Two jobs, both against the FROZEN committed tree (git archive 5900431):
  run      -- launch `godot --headless --path <proj> --script res://<fixture> -- <flags>`
              in the battery's exact shape (subprocess.run, capture_output, 8 s
              timeout, merged output = stdout + stderr kept separately), N reps.
  classify -- re-classify receipts through the PRODUCTION classify_process
              extracted verbatim (AST) from the committed run_battery.py, with
              the committed CASES / expected_errors / required_stderr tables and
              execute()'s envelope + stream-anchor semantics.

Read-only w.r.t. the repository: everything lands under the seat directory.
"""
import argparse, ast, hashlib, json, pathlib, subprocess, sys, time

SEAT = pathlib.Path(__file__).resolve().parent.parent
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"
HARNESS = FROZEN / "run_battery.py"


def load_production(harness=HARNESS):
    """Extract classify_process + CASES + expected_errors + required_stderr."""
    src = harness.read_text()
    tree = ast.parse(src)
    out = {"src": src}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            fn_src = ast.get_source_segment(src, node)
            out["seg_sha"] = hashlib.sha256(fn_src.encode()).hexdigest()
            ns = {}
            exec("import re\n" + fn_src, ns)
            out["classify"] = ns["classify_process"]
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            cases = {}
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": t[2], "exit": t[3],
                               "signature": t[4]}
            out["cases"] = cases
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "r92_tilemap_atlas" in keys:
                out["expected_errors"] = {
                    k.value: ast.literal_eval(v) for k, v in zip(node.keys, node.values)
                    if isinstance(k, ast.Constant) and k.value.startswith("r92_")}
            if "nav_lattice_teardown_crash" in keys and "geo2d_lattice_lineempty" in keys:
                out["required_stderr"] = {
                    k.value: ast.literal_eval(v) for k, v in zip(node.keys, node.values)
                    if isinstance(k, ast.Constant) and k.value.startswith("r92_")}
    return out


def classify_receipt(prod, case, out_text, err_text, rc):
    """Replicate execute()'s full path for one receipt."""
    row = prod["cases"][case]
    sigs = (row["signature"] if isinstance(row["signature"], (tuple, list))
            else (row["signature"],))
    ee = prod["expected_errors"].get(case, ())
    rs = prod["required_stderr"].get(case, ())
    merged = out_text + err_text
    passed = any(prod["classify"](rc, None, merged, row["exit"], sig, ee)
                 for sig in sigs)
    bare_passes = None
    if ee:
        bare_passes = any(prod["classify"](rc, None, merged, row["exit"], sig, ())
                   for sig in sigs)
    if rs:
        passed = (passed and all(f in err_text for f in rs)
                  and any(s in out_text for s in sigs))
    return {"case": case, "passed": passed, "bare_passes": bare_passes, "rc": rc,
            "n_sigs": len(sigs), "n_ee": len(ee), "n_rs": len(rs)}


def cmd_run(a):
    proj = pathlib.Path(a.proj).resolve()
    outdir = pathlib.Path(a.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    arms = a.arms.split(",")
    log = open(outdir / f"{a.tag}.log", "a")
    rc_all = {}
    for rep in range(1, a.reps + 1):
        for arm in arms:
            cmd = [a.godot, "--headless", "--path", str(proj), "--script",
                   f"res://{a.fixture}", "--", f"--arm={arm}"]
            if a.fixed_fps:
                cmd.insert(1, "--fixed-fps")
                cmd.insert(2, str(a.fixed_fps))
            t0 = time.time()
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout)
                so, se, code, err = p.stdout, p.stderr, p.returncode, None
            except subprocess.TimeoutExpired as exc:
                so = (exc.stdout or "") if not isinstance(exc.stdout, bytes) else exc.stdout.decode(errors="replace")
                se = (exc.stderr or "") if not isinstance(exc.stderr, bytes) else exc.stderr.decode(errors="replace")
                code, err = None, f"TIMEOUT after {a.timeout}"
            except OSError as exc:
                so, se, code, err = "", str(exc), None, f"launch error: {exc}"
            wall = round(time.time() - t0, 3)
            stem = f"{a.tag}.{arm}.rep{rep}"
            (outdir / f"{stem}.out").write_text(so)
            (outdir / f"{stem}.err").write_text(se)
            (outdir / f"{stem}.rc").write_text(str(code))
            (outdir / f"{stem}.wall").write_text(str(wall))
            rc_all[stem] = code
            log.write(f"{stem} rc={code} wall={wall} err={err!r}\n")
            log.flush()
    log.close()
    print(json.dumps(rc_all, indent=0))


def cmd_classify(a):
    prod = load_production(pathlib.Path(a.harness))
    d = pathlib.Path(a.dir).resolve()
    stems = sorted({p.name[:-3] for p in d.glob(f"{a.tag}.*.rc")})
    results = []
    for stem in stems:
        arm = a.case_from or stem.split(".")[1]
        case = a.arm_to_case.get(arm, a.prefix + arm)
        out_text = (d / f"{stem}.out").read_text()
        err_text = (d / f"{stem}.err").read_text()
        rc = int((d / f"{stem}.rc").read_text().strip())
        r = classify_receipt(prod, case, out_text, err_text, rc)
        r["stem"] = stem
        results.append(r)
        flag = "PASS" if r["passed"] else "FAIL"
        extra = f" bare_passes={r['bare_passes']}" if r["bare_passes"] is not None else ""
        print(f"{flag} {stem} rc={rc}{extra}", flush=True)
    n_fail = sum(1 for r in results if not r["passed"])
    print(f"TOTAL receipts={len(results)} fails={n_fail} "
          f"classify_process_segment_sha256={prod['seg_sha'][:16]}")
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(results, indent=1))
    sys.exit(1 if n_fail else 0)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--proj", required=True)
    r.add_argument("--outdir", required=True)
    r.add_argument("--tag", required=True)
    r.add_argument("--arms", required=True)
    r.add_argument("--reps", type=int, default=1)
    r.add_argument("--fixture", default="tilemap_lattice.gd")
    r.add_argument("--godot", default="godot")
    r.add_argument("--fixed-fps", type=int, default=0)
    r.add_argument("--timeout", type=float, default=8)
    r.set_defaults(func=cmd_run)
    c = sub.add_parser("classify")
    c.add_argument("--dir", required=True)
    c.add_argument("--tag", required=True)
    c.add_argument("--harness", default=str(HARNESS))
    c.add_argument("--prefix", default="r92_tilemap_")
    c.add_argument("--case-from", default=None)
    c.add_argument("--json", default=None)
    c.set_defaults(func=cmd_classify, arm_to_case={"nullts": "r92_tilemap_nullts_crash"})
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
