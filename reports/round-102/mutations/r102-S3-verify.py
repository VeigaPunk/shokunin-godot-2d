#!/usr/bin/env python3
"""r102-S3 targeted row runner + classifier (battery NEVER run).

Staging replicates run_battery.py:1725-1745 exactly (fixture copy minus
run_battery.py/dotfiles, project-name munge, controls/pickup.tscn staging,
causal_chain two-frame readiness fix). Launch shape is the battery's:
  godot --headless --path <scratch> --script res://<fixture> -- <flags>
Classifier replicates classify_process / classify_streams semantics from
run_battery.py:1775-1825; allowlists (expected_errors, required_stderr) are
extracted from the CASES source by AST (the dict is the value of a
``.get(name, ())`` call on a Dict literal), never executed.

subcommands:
  extract --src <run_battery.py> --rows <out.json>
  run     --src <fixtures-dir> --rows <rows.json> --out <res.json> --stamp S [--overlay name=path ...]
  analyze --base <res.json> --fold <res.json> --out <report.txt> [--label X]
"""
import argparse
import ast
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

GODOT = "/usr/bin/godot"
TARGET_FIXTURES = ("scene_io_lattice.gd", "particles_lattice.gd", "dss_lattice.gd", "r95b_order.gd")

MASK_GD_LINE = (re.compile(r"(res://[\w./-]+\.gd):\d+"), r"\1:<L>")
MASK_ENV = (re.compile(r"env=tps=\d+ pf=\d+ proc=\d+"), "env=tps=<L> pf=<L> proc=<L>")
MASK_IDS = (re.compile(r"\b\w*ids=\[[^\]]*\]"), "ids=[<L>]")
MASK_FRESH = (re.compile(r"fresh_id=\d+"), "fresh_id=<L>")
MASK_BODYPOS = (re.compile(r"bodypos=\[[^\]]*\]"), "bodypos=[<L>]")


def masks(out, level):
    if level >= 1:
        out = MASK_GD_LINE[0].sub(MASK_GD_LINE[1], out)
    if level >= 2:
        out = MASK_ENV[0].sub(MASK_ENV[1], out)
    if level >= 3:
        out = MASK_IDS[0].sub(MASK_IDS[1], out)
        out = MASK_FRESH[0].sub(MASK_FRESH[1], out)
        out = MASK_BODYPOS[0].sub(MASK_BODYPOS[1], out)
    return out


def extract_cases(path):
    t = ast.parse(pathlib.Path(path).read_text())
    node = next(n for n in t.body if isinstance(n, ast.Assign)
                and getattr(n.targets[0], "id", "") == "CASES")
    cases = [ast.literal_eval(e) for e in node.value.elts]

    def dictget(name):
        out = {}
        for n in ast.walk(t):
            if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                    and getattr(n.targets[0], "id", "") == name:
                v = n.value
                if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) \
                        and v.func.attr == "get" and isinstance(v.func.value, ast.Dict):
                    out.update(ast.literal_eval(v.func.value))
                elif isinstance(v, ast.Dict):
                    out.update(ast.literal_eval(v))
        return out
    return cases, dictget("expected_errors"), dictget("required_stderr")


def stage(src, dst, stamp):
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for item in sorted(src.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dst / item.name)
        else:
            shutil.copy2(item, dst / item.name)
    pf = dst / "project.godot"
    t = pf.read_text()
    assert 'config/name="MechanicOneShotTest"' in t
    pf.write_text(t.replace('config/name="MechanicOneShotTest"',
                            f'config/name="MechanicOneShotTest-r102s3-{stamp}"', 1))
    shutil.copy2(dst / "controls" / "pickup.tscn", dst / "pickup.tscn")
    ch = dst / "causal_chain.gd"
    t = ch.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in t
    ch.write_text(t.replace(anchor,
                            "    await process_frame\n    await process_frame\n    var old := current_scene", 1))


def run_one(scratch, fixture, flags, timeout):
    cmd = [GODOT, "--headless", "--path", str(scratch), "--script", "res://" + fixture, "--", *flags]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        so = p.stdout.decode(errors="replace")
        se = p.stderr.decode(errors="replace")
        rc, note = p.returncode, None
    except subprocess.TimeoutExpired as exc:
        so = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        se = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        rc, note = None, f"TIMEOUT after {timeout}s"
    return {"rc": rc, "so": so, "se": se, "out": so + se,
            "dur": round(time.time() - t0, 3), "note": note, "cmd": cmd}


def classify(code, error, so, se, expected_exit, signature, allowed, required):
    out = so + se
    if code != expected_exit or error is not None:
        return False, f"rc={code}!={expected_exit} err={error}"
    sig_ok = signature in out if isinstance(signature, str) else any(s in out for s in signature)
    if not sig_ok:
        return False, "signature_missing"
    if "SCRIPT ERROR:" in out or "Parse Error:" in out:
        return False, "script_or_parse_error"

    def allowed_line(line, a):
        s = line.strip()
        if s == a:
            return True
        if a.endswith(","):
            return s.startswith(a) and s.count("ERROR:") == 1
        if a == "ERROR: chain incomplete":
            return (s.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in s and "old_alive=false" in s
                    and s.count("ERROR:") == 1)
        return False

    if not required:
        bad = [l for l in out.splitlines() if "ERROR:" in l
               and not any(allowed_line(l, a) for a in allowed)]
        if bad:
            return False, f"unrelated_errors={len(bad)}"
        return True, "pass(strict)"
    # required_stderr path == classify_streams semantics
    if "SCRIPT ERROR:" in so or "SCRIPT ERROR:" in se:
        return False, "script_error"
    if not isinstance(signature, str) or signature not in so:
        return False, "signature_not_on_stdout"
    allow = set(required)
    for line in se.splitlines():
        s = line.strip()
        if not s:
            continue
        if s in allow:
            continue
        if not any(a.endswith(",") and s.startswith(a) and s.count("ERROR:") == 1 for a in allow):
            return False, f"stderr_line_not_allowed={s[:40]!r}"
    return True, "pass(streams)"


def cmd_extract(a):
    cases, ee, rs = extract_cases(a.src)
    rows, dropped = [], []
    for name, script, flags, expected_exit, evidence in cases:
        if script in TARGET_FIXTURES or (script == "r101_ytrans.gd" and name == "r101_ytrans_census"):
            rows.append({"name": name, "fixture": script, "flags": list(flags),
                         "expected_exit": expected_exit,
                         "evidence": list(evidence) if isinstance(evidence, (list, tuple)) else evidence,
                         "ee": list(ee.get(name, ())), "rs": list(rs.get(name, ()))})
        else:
            dropped.append(name)
    json.dump(rows, open(a.rows, "w"), indent=1)
    print(f"extracted rows={len(rows)} dropped={len(dropped)}")
    for r in rows:
        print(f"  {r['name']:44s} {r['fixture']:26s} flags={r['flags']} exit={r['expected_exit']} ee={len(r['ee'])} rs={len(r['rs'])}")


def cmd_run(a):
    rows = json.loads(pathlib.Path(a.rows).read_text())
    scratch = pathlib.Path(a.stamp)
    stage(a.src, scratch, scratch.name)
    for spec in a.overlay or []:
        name, path = spec.split("=", 1)
        shutil.copy2(path, scratch / name)
        print(f"overlay {name} <- {path} sha256={hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()[:16]}")
    results = {}
    t0 = time.time()
    for row in rows:
        results[row["name"]] = run_one(scratch, row["fixture"], row["flags"], a.timeout)
        r = results[row["name"]]
        print(f"{row['name']:44s} rc={r['rc']} {r['dur']:6.2f}s bytes={len(r['out'])}")
    print(f"total {time.time()-t0:.1f}s")
    pathlib.Path(a.out).write_text(json.dumps(results, indent=1))
    print("wrote", a.out)


def cmd_analyze(a):
    rows = json.loads(pathlib.Path(a.rows).read_text())
    B = json.loads(pathlib.Path(a.base).read_text())
    F = json.loads(pathlib.Path(a.fold).read_text())
    lines, counts = [], {"rows": 0, "rc_diff": 0, "raw_diff": 0, "m1_diff": 0, "m2_diff": 0, "m3_diff": 0,
                         "base_fail": 0, "fold_fail": 0, "sig_gate_fail_both": 0}
    for row in rows:
        n = row["name"]
        b, f = B[n], F[n]
        counts["rows"] += 1
        cb, whyb = classify(b["rc"], b["note"], b["so"], b["se"], row["expected_exit"], row["evidence"], row["ee"], row["rs"])
        cf, whyf = classify(f["rc"], f["note"], f["so"], f["se"], row["expected_exit"], row["evidence"], row["ee"], row["rs"])
        raw = b["out"] == f["out"]
        m1 = masks(b["out"], 1) == masks(f["out"], 1)
        m2 = masks(b["out"], 2) == masks(f["out"], 2)
        m3 = masks(b["out"], 3) == masks(f["out"], 3)
        rc = b["rc"] == f["rc"]
        counts["rc_diff"] += 0 if rc else 1
        counts["raw_diff"] += 0 if raw else 1
        counts["m1_diff"] += 0 if m1 else 1
        counts["m2_diff"] += 0 if m2 else 1
        counts["m3_diff"] += 0 if m3 else 1
        counts["base_fail"] += 0 if cb else 1
        counts["fold_fail"] += 0 if cf else 1
        counts["sig_gate_fail_both"] += 1 if (not cb and not cf) else 0
        lines.append(f"{n:44s} rc {b['rc']}=={f['rc']}:{rc} raw={raw} m1={m1} m2={m2} m3={m3} "
                     f"basePASS={cb}({whyb}) foldPASS={cf}({whyf}) bytes {len(b['out'])}/{len(f['out'])}")
        if not m2:
            import difflib
            d = list(difflib.unified_diff(masks(b["out"], 2).splitlines(), masks(f["out"], 2).splitlines(),
                                          "base", "fold", lineterm=""))
            lines.extend(["    " + l for l in d[:30]])
    summary = (f"[{a.label}] rows={counts['rows']} rc_diff={counts['rc_diff']} raw_diff={counts['raw_diff']} "
               f"m1_diff={counts['m1_diff']} m2_diff={counts['m2_diff']} m3_diff={counts['m3_diff']} "
               f"base_fail={counts['base_fail']} fold_fail={counts['fold_fail']}")
    text = summary + "\n" + "\n".join(lines) + "\n"
    pathlib.Path(a.out).write_text(text)
    print(text)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract"); e.add_argument("--src", required=True); e.add_argument("--rows", required=True); e.set_defaults(func=cmd_extract)
    r = sub.add_parser("run")
    r.add_argument("--src", required=True); r.add_argument("--rows", required=True)
    r.add_argument("--out", required=True); r.add_argument("--stamp", required=True)
    r.add_argument("--overlay", action="append"); r.add_argument("--timeout", type=int, default=25)
    r.set_defaults(func=cmd_run)
    n = sub.add_parser("analyze")
    n.add_argument("--rows", required=True); n.add_argument("--base", required=True); n.add_argument("--fold", required=True)
    n.add_argument("--out", required=True); n.add_argument("--label", default="?")
    n.set_defaults(func=cmd_analyze)
    a = ap.parse_args()
    sys.exit(a.func(a) or 0)


if __name__ == "__main__":
    main()
