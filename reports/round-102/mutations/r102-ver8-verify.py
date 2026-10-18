"""r102-ver8: independent staged runner + production classifier for targeted CASES rows.

Subcommands:
  stage  --raw <dir> --dest <dir> --stamp <s>        build battery-shaped scratch project
  run    --tree <dir> --rows <rows.json> --out <jsonl> --rep N [--filter name1,name2]
  classify --rows_all <rows_all.json> --receipts <jsonl> --out <json>
  compare  --a <jsonl> --b <jsonl> [--label-a ...] [--label-b ...]   (uses classify first)
"""
import argparse, json, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

GODOT = "godot"
TIMEOUT = 25  # battery uses 8s; we record elapsed separately


def stage(raw: Path, dest: Path, stamp: str):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in sorted(raw.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    project_file = dest / "project.godot"
    text = project_file.read_text()
    n = text.count('config/name="MechanicOneShotTest"')
    assert n == 1, f"expected 1 name token, got {n}"
    text = text.replace('config/name="MechanicOneShotTest"',
                        f'config/name="MechanicOneShotTest-{stamp}"', 1)
    project_file.write_text(text)
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    ctext = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in ctext, "causal fixture changed; cannot apply scratch readiness fix"
    chain.write_text(ctext.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    print(f"staged {dest} stamp={stamp}")


def run_rows(tree: Path, rows_path: Path, out: Path, rep: int, names=None):
    data = json.loads(rows_path.read_text())
    rows = data["rows"] if isinstance(data, dict) else data
    if names:
        rows = [r for r in rows if r["name"] in names]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        for r in rows:
            cmd = [GODOT, "--headless", "--path", str(tree), "--script", "res://" + r["script"]]
            if r["flags"]:
                cmd += ["--"] + list(r["flags"])
            t0 = time.monotonic()
            error = None
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
                stdout, stderr, rc = p.stdout, p.stderr, p.returncode
            except subprocess.TimeoutExpired as exc:
                stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(errors="replace")
                stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(errors="replace")
                rc, error = None, f"TIMEOUT after {TIMEOUT} seconds"
            except OSError as exc:
                stdout, stderr, rc, error = "", str(exc), None, f"launch error: {exc}"
            rec = {"case": r["name"], "rep": rep, "tree": str(tree), "command": cmd,
                   "actual_exit": rc, "error": error, "elapsed": round(time.monotonic() - t0, 3),
                   "stdout": stdout, "stderr": stderr,
                   "stamp": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")}
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(f"[rep{rep}] {r['name']}: rc={rc} elapsed={rec['elapsed']}s err={error}", flush=True)


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


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    lines = output.splitlines()
    unrelated = [line for line in lines if "ERROR:" in line
                 and not any(allowed_error(line, a) for a in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def classify_row(rec, row, allow, req):
    code, error = rec["actual_exit"], rec["error"]
    stdout, stderr = rec["stdout"], rec["stderr"]
    output = stdout + stderr
    ev = row["evidence"]
    sigs = ev if isinstance(ev, list) else [ev]
    ee = allow.get(row["name"], [])
    passed = any(classify_process(code, error, output, row["expected_exit"], s, ee) for s in sigs)
    fragments = req.get(row["name"], [])
    if fragments:
        passed = (passed and all(f in stderr for f in fragments)
                  and any(s in stdout for s in sigs))
    if "SCRIPT ERROR:" in output or "Parse Error:" in output:
        passed = False
    return passed


def classify(rows_all: Path, receipts: Path, out: Path):
    data = json.loads(rows_all.read_text())
    by_name = {r["name"]: r for r in data["rows"]}
    allow, req = data["expected_errors"], data["required_stderr"]
    out_recs = []
    for line in receipts.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        row = by_name[rec["case"]]
        verdict = classify_row(rec, row, allow, req)
        out_recs.append({"case": rec["case"], "rep": rec["rep"], "verdict": "PASS" if verdict else "FAIL",
                         "rc": rec["actual_exit"], "elapsed": rec["elapsed"], "error": rec["error"]})
    out.write_text(json.dumps(out_recs, indent=1))
    p = sum(1 for r in out_recs if r["verdict"] == "PASS")
    print(f"classified {len(out_recs)}: {p} PASS / {len(out_recs)-p} FAIL -> {out}")
    for r in out_recs:
        if r["verdict"] != "PASS":
            print(f"  FAIL {r['case']} rep{r['rep']} rc={r['rc']} err={r['error']}")


BT = re.compile(r"(res://[A-Za-z0-9_./-]+\.gd):(\d+)")
def mask_backtraces(text):
    return BT.sub(r"\1:<line>", text)


def compare(a_path: Path, b_path: Path, la="A", lb="B", out=None, mask_bt=True):
    A = [json.loads(l) for l in a_path.read_text().splitlines() if l.strip()]
    B = [json.loads(l) for l in b_path.read_text().splitlines() if l.strip()]
    Am, Bm = {r["case"]: r for r in A}, {r["case"]: r for r in B}
    assert set(Am) == set(Bm), f"row sets differ: {set(Am)^set(Bm)}"
    rows = []
    for name in sorted(Am):
        ra, rb = Am[name], Bm[name]
        sa, sb = ra["stdout"], rb["stdout"]
        same_stdout = sa == sb
        same_stdout_masked = mask_backtraces(sa) == mask_backtraces(sb) if mask_bt else same_stdout
        diff_lines = [] if same_stdout else [
            (x, y) for x, y in zip(sa.splitlines(), sb.splitlines()) if x != y]
        rows.append({"case": name, "rc_a": ra["actual_exit"], "rc_b": rb["actual_exit"],
                     "same_rc": ra["actual_exit"] == rb["actual_exit"],
                     "same_stdout": same_stdout, "same_stdout_masked": same_stdout_masked,
                     "n_stdout_lines_a": len(sa.splitlines()), "n_stdout_lines_b": len(sb.splitlines()),
                     "diff_line_pairs": diff_lines[:6], "n_diff_line_pairs": len(diff_lines),
                     "elapsed_a": ra["elapsed"], "elapsed_b": rb["elapsed"],
                     "stderr_same": ra["stderr"] == rb["stderr"],
                     "stderr_masked_same": mask_backtraces(ra["stderr"]) == mask_backtraces(rb["stderr"])})
    raw = sum(1 for r in rows if not r["same_stdout"])
    masked = sum(1 for r in rows if not r["same_stdout_masked"])
    rc = sum(1 for r in rows if not r["same_rc"])
    smask = sum(1 for r in rows if not r["stderr_masked_same"])
    print(f"{la} vs {lb}: rows={len(rows)} stdout_raw_diffs={raw} stdout_masked_diffs={masked} "
          f"rc_diffs={rc} stderr_masked_diffs={smask}")
    for r in rows:
        if not r["same_stdout_masked"] or not r["same_rc"]:
            print(f"  {r['case']}: rc {r['rc_a']}->{r['rc_b']} masked_diffs={r['n_diff_line_pairs']}")
            for x, y in r["diff_line_pairs"]:
                print(f"    {la}: {x[:160]}")
                print(f"    {lb}: {y[:160]}")
    if out:
        Path(out).write_text(json.dumps(rows, indent=1))
        print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stage"); s.add_argument("--raw", required=True); s.add_argument("--dest", required=True); s.add_argument("--stamp", required=True)
    r = sub.add_parser("run"); r.add_argument("--tree", required=True); r.add_argument("--rows", required=True); r.add_argument("--out", required=True); r.add_argument("--rep", type=int, default=1); r.add_argument("--filter", default=None)
    c = sub.add_parser("classify"); c.add_argument("--rows_all", required=True); c.add_argument("--receipts", required=True); c.add_argument("--out", required=True)
    d = sub.add_parser("compare"); d.add_argument("--a", required=True); d.add_argument("--b", required=True); d.add_argument("--la", default="A"); d.add_argument("--lb", default="B"); d.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.cmd == "stage":
        stage(Path(args.raw), Path(args.dest), args.stamp)
    elif args.cmd == "run":
        names = set(args.filter.split(",")) if args.filter else None
        run_rows(Path(args.tree), Path(args.rows), Path(args.out), args.rep, names)
    elif args.cmd == "classify":
        classify(Path(args.rows_all), Path(args.receipts), Path(args.out))
    elif args.cmd == "compare":
        compare(Path(args.a), Path(args.b), args.la, args.lb, args.out)


if __name__ == "__main__":
    main()
