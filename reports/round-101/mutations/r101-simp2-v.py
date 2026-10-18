#!/usr/bin/env python3
"""r101 SIMP-2 targeted row runner — replicates run_battery.py's staging and
launch shape for named fixture rows only (the battery itself is never run).

  run: stage fixtures -> scratch (name munge, pickup staging, causal fix),
       execute [godot --headless --path scratch --script res://<fixture> -- <flags>],
       record merged stdout+stderr, rc, wall duration.
  diff: compare two result JSONs; raw then with declared masks.
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

BASE = pathlib.Path("/var/tmp/r101-simp2")
GODOT = "/usr/bin/godot"

MASK_PATTERNS = [
    (re.compile(r"(res://[\w./-]+\.gd):\d+"), r"\1:<L>"),   # engine backtrace line numbers
]


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
                            f'config/name="MechanicOneShotTest-r101simp2-{stamp}"', 1))
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
        out = (p.stdout + p.stderr).decode(errors="replace")
        rc, note = p.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"") + (exc.stderr or b"")
        out = out.decode(errors="replace") if isinstance(out, bytes) else out
        rc, note = None, f"TIMEOUT after {timeout}s"
    return {"rc": rc, "out": out, "dur": round(time.time() - t0, 3), "note": note, "cmd": cmd}


def cmd_run(a):
    rows = json.loads(pathlib.Path(a.rows).read_text())
    scratch = BASE / "scratch" / a.stamp
    stage(a.src, scratch, a.stamp)
    for spec in a.overlay or []:
        name, path = spec.split("=", 1)
        shutil.copy2(path, scratch / name)
        print(f"overlay {name} <- {path}")
    results = {}
    for row in rows:
        results[row["name"]] = run_one(scratch, row["fixture"], row["flags"], a.timeout)
        r = results[row["name"]]
        print(f"{row['name']:48s} rc={r['rc']} {r['dur']:6.2f}s bytes={len(r['out'])}")
    pathlib.Path(a.out).write_text(json.dumps(results, indent=1))
    print("wrote", a.out)


def masked(out):
    for pat, repl in MASK_PATTERNS:
        out = pat.sub(repl, out)
    return out


def cmd_diff(a):
    A = json.loads(pathlib.Path(a.a).read_text())
    B = json.loads(pathlib.Path(a.b).read_text())
    lines = []
    raw_diffs = masked_diffs = 0
    assert set(A) == set(B), (set(A) ^ set(B))
    for row in sorted(A):
        x, y = A[row], B[row]
        same_rc = x["rc"] == y["rc"]
        same_raw = x["out"] == y["out"]
        same_masked = masked(x["out"]) == masked(y["out"])
        raw_diffs += 0 if same_raw else 1
        masked_diffs += 0 if same_masked else 1
        lines.append(f"{row:48s} rc {x['rc']}=={y['rc']}:{same_rc} raw:{same_raw} masked:{same_masked} "
                     f"bytes {len(x['out'])}/{len(y['out'])}")
        if not same_masked:
            import difflib
            d = list(difflib.unified_diff(masked(x["out"]).splitlines(),
                                          masked(y["out"]).splitlines(),
                                          "committed", "folded", lineterm=""))
            lines.extend(d[:40])
    summary = f"rows={len(A)} raw_diffs={raw_diffs} masked_diffs={masked_diffs}"
    text = summary + "\n" + "\n".join(lines) + "\n"
    pathlib.Path(a.out).write_text(text)
    print(text)
    return 0 if masked_diffs == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--src", required=True)
    r.add_argument("--rows", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--stamp", required=True)
    r.add_argument("--overlay", action="append")
    r.add_argument("--timeout", type=int, default=120)
    r.set_defaults(func=cmd_run)
    d = sub.add_parser("diff")
    d.add_argument("--a", required=True)
    d.add_argument("--b", required=True)
    d.add_argument("--out", required=True)
    d.set_defaults(func=cmd_diff)
    a = ap.parse_args()
    sys.exit(a.func(a) or 0)


if __name__ == "__main__":
    main()
