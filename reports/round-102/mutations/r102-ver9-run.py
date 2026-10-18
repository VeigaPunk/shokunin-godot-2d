#!/usr/bin/env python3
"""r102-ver9: independent A/B of the middle-third simplifier folds.

Reads CASES from run_battery.py via AST (never imports/runs it),
stages base and folded Godot projects exactly like the harness staging
block (run_battery.py:1723-1745 @ 1392ca21), runs the affected rows in
an interleaved base/folded order, and applies the null-control rule:
a key counts as a fold effect only if it is stable in base across reps
and differs between base and folded.
"""
import ast, json, re, shutil, subprocess, sys, time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
WORK = Path("/var/tmp/r102-ver9")
GODOT = "/usr/bin/godot"
MIDDLE = ["r98b_rksenum.gd", "audio_lattice.gd", "stree_lattice.gd"]
PATCHES = [
    "r101-simp1-r98-r98b_rksenum.patch",
    "r101-simp1-r99-audio_lattice.patch",
    "r101-simp2-stree_lattice.gd.diff",
]


def extract_rows():
    src = (REPO / "corpus/fixtures/run_battery.py").read_text()
    tree = ast.parse(src)
    cases = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "CASES" for t in node.targets):
            cases = ast.literal_eval(node.value)
            break
    assert cases is not None, "CASES not found"
    rows = []
    for c in cases:
        name, script, flags, exp_exit, sig = c[0], c[1], c[2], c[3], c[4]
        if script in MIDDLE:
            rows.append(dict(name=name, script=script, flags=list(flags),
                             expected_exit=exp_exit, signature=sig))
    return rows


def stage(fixtures: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(fixtures, dst, ignore=shutil.ignore_patterns(
        "run_battery.py", "__pycache__", ".godot"))
    pf = dst / "project.godot"
    t = pf.read_text()
    assert 'config/name="MechanicOneShotTest"' in t, "project name anchor missing"
    pf.write_text(t.replace('config/name="MechanicOneShotTest"',
                            'config/name="MechanicOneShotTest-r102ver9"', 1))
    shutil.copy2(dst / "controls" / "pickup.tscn", dst / "pickup.tscn")
    chain = dst / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in text, "causal anchor missing"
    chain.write_text(text.replace(
        anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))


def build_folded():
    src, dst = WORK / "tree", WORK / "tree_folded"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for p in PATCHES:
        r = subprocess.run(["git", "apply", str(WORK / "patches" / p)],
                           cwd=dst, capture_output=True, text=True)
        print("APPLY", p, "rc=", r.returncode, r.stderr.strip())
        assert r.returncode == 0, p


def run(proj, row, timeout=25):
    cmd = [GODOT, "--headless", "--path", str(proj),
           "--script", "res://" + row["script"], "--", *row["flags"]]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc = "TIMEOUT"
        out = e.stdout if isinstance(e.stdout, str) else (e.stdout or b"").decode(errors="replace")
        err = e.stderr if isinstance(e.stderr, str) else (e.stderr or b"").decode(errors="replace")
    return dict(cmd=cmd, rc=rc, stdout=out, stderr=err, dur=round(time.time() - t0, 2))


KV = re.compile(r"(?<![\w.])([A-Za-z_][A-Za-z0-9_]*)=(\S+)")


def kv(text):
    return dict(KV.findall(text))


def main():
    rows = extract_rows()
    print("ROWS", len(rows), [r["name"] for r in rows])
    build_folded()
    stage(WORK / "tree" / "corpus/fixtures", WORK / "proj_base")
    stage(WORK / "tree_folded" / "corpus/fixtures", WORK / "proj_folded")
    recs = {}
    for row in rows:
        recs[row["name"]] = {}
        for rep in (1, 2):
            recs[row["name"]][f"base{rep}"] = run(WORK / "proj_base", row)
            recs[row["name"]][f"fold{rep}"] = run(WORK / "proj_folded", row)
        b1, f1 = recs[row["name"]]["base1"], recs[row["name"]]["fold1"]
        print(f"{row['name']:38s} base={b1['rc']}/{b1['dur']}s fold={f1['rc']}/{f1['dur']}s")
        sys.stdout.flush()

    summary = {}
    for row in rows:
        name = row["name"]
        r = recs[name]
        sig = {k: (row["signature"] in v["stdout"]) for k, v in r.items()}
        rc = {k: v["rc"] for k, v in r.items()}
        kvb1, kvb2 = kv(r["base1"]["stdout"]), kv(r["base2"]["stdout"])
        kvf1, kvf2 = kv(r["fold1"]["stdout"]), kv(r["fold2"]["stdout"])
        stable = {k for k in kvb1 if k in kvb2 and kvb1[k] == kvb2[k]}
        fold_effects = {k: (kvb1[k], kvf1.get(k)) for k in stable
                        if k in kvf1 and kvf1[k] != kvb1[k]}
        fold_self_unstable = {k for k in kvf1 if k in kvf2 and kvf1[k] != kvf2[k]}
        stdout_eq_1 = r["base1"]["stdout"] == r["fold1"]["stdout"]
        stderr_eq_1 = r["base1"]["stderr"] == r["fold1"]["stderr"]
        summary[name] = dict(
            sig=sig, rc=rc, expected_exit=row["expected_exit"],
            stable_keys=len(stable), fold_effects=fold_effects,
            fold_self_unstable=sorted(fold_self_unstable),
            stdout_eq_1=stdout_eq_1, stderr_eq_1=stderr_eq_1,
            stdout_len=(len(r["base1"]["stdout"]), len(r["fold1"]["stdout"])),
        )
    out = WORK / "results.json"
    out.write_text(json.dumps(dict(summary=summary, recs=recs), indent=1))
    print("\n=== SUMMARY ===")
    for name, s in summary.items():
        ok_sig = all(s["sig"].values())
        rc_vals = set(s["rc"].values())
        ok_rc = rc_vals == {s["expected_exit"]}
        print(f"{name:38s} sig={ok_sig} rc={sorted(map(str, rc_vals))} "
              f"stable={s['stable_keys']} effects={len(s['fold_effects'])} "
              f"out_eq={s['stdout_eq_1']} err_eq={s['stderr_eq_1']}")
        if s["fold_effects"]:
            print("   EFFECTS", s["fold_effects"])
    print("WROTE", out)


if __name__ == "__main__":
    main()
