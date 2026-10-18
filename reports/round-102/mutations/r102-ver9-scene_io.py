#!/usr/bin/env python3
"""r102-ver9 scene_io A/B: S2-slice second file. Base = committed bytes;
folded = stree+scene_io patches applied (S2's exact slice). Interleaved
base,fold,base,fold per row; null-control stable-key rule as in the main
runner. Writes /var/tmp/r102-ver9/scene_io-results.json.
"""
import ast, json, re, shutil, subprocess, sys, time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
WORK = Path("/var/tmp/r102-ver9")
GODOT = "/usr/bin/godot"
PATCHES = ["r101-simp2-stree_lattice.gd.diff", "r101-simp2-scene_io_lattice.gd.diff"]
SCRIPT = "scene_io_lattice.gd"


def extract_rows():
    src = (REPO / "corpus/fixtures/run_battery.py").read_text()
    cases = None
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "CASES" for t in node.targets):
            cases = ast.literal_eval(node.value)
            break
    return [dict(name=c[0], script=c[1], flags=list(c[2]),
                 expected_exit=c[3], signature=c[4])
            for c in cases if c[1] == SCRIPT]


def stage(fixtures, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(fixtures, dst, ignore=shutil.ignore_patterns(
        "run_battery.py", "__pycache__", ".godot"))
    pf = dst / "project.godot"
    t = pf.read_text()
    pf.write_text(t.replace('config/name="MechanicOneShotTest"',
                            'config/name="MechanicOneShotTest-r102ver9s2"', 1))
    shutil.copy2(dst / "controls" / "pickup.tscn", dst / "pickup.tscn")
    chain = dst / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    chain.write_text(text.replace(
        anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))


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


def main():
    rows = extract_rows()
    print("ROWS", len(rows), [r["name"] for r in rows])
    tree, dst = WORK / "tree", WORK / "tree_s2"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(tree, dst)
    for p in PATCHES:
        r = subprocess.run(["git", "apply", str(WORK / "patches" / p)],
                           cwd=dst, capture_output=True, text=True)
        print("APPLY", p, "rc=", r.returncode, r.stderr.strip())
        assert r.returncode == 0
    stage(dst / "corpus/fixtures", WORK / "proj_s2f")
    base = WORK / "proj_base"
    recs, summary = {}, {}
    for row in rows:
        recs[row["name"]] = {}
        for rep in (1, 2):
            recs[row["name"]][f"base{rep}"] = run(base, row)
            recs[row["name"]][f"fold{rep}"] = run(WORK / "proj_s2f", row)
        r = recs[row["name"]]
        b1, f1 = r["base1"], r["fold1"]
        kb1 = dict(KV.findall(b1["stdout"]))
        kb2 = dict(KV.findall(r["base2"]["stdout"]))
        kf1 = dict(KV.findall(f1["stdout"]))
        kf2 = dict(KV.findall(r["fold2"]["stdout"]))
        stable = {k for k in kb1 if k in kb2 and kb1[k] == kb2[k]}
        effects = {k: (kb1[k], kf1.get(k)) for k in stable if k in kf1 and kf1[k] != kb1[k]}
        summary[row["name"]] = dict(
            sig={k: row["signature"] in v["stdout"] for k, v in r.items()},
            rc={k: v["rc"] for k, v in r.items()}, expected_exit=row["expected_exit"],
            effects=effects,
            fold_self_unstable=sorted({k for k in kf1 if k in kf2 and kf1[k] != kf2[k]}),
            stdout_eq_1=b1["stdout"] == f1["stdout"],
            stderr_eq_1=b1["stderr"] == f1["stderr"])
        print(f"{row['name']:28s} base={b1['rc']}/{b1['dur']}s fold={f1['rc']}/{f1['dur']}s")
        sys.stdout.flush()
    (WORK / "scene_io-results.json").write_text(json.dumps(dict(summary=summary, recs=recs), indent=1))
    print("=== SUMMARY ===")
    bad = 0
    for name, s in summary.items():
        ok = all(s["sig"].values()) and set(map(str, s["rc"].values())) == {str(s["expected_exit"])} and not s["effects"]
        bad += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} {name} sig={all(s['sig'].values())} "
              f"out_eq={s['stdout_eq_1']} err_eq={s['stderr_eq_1']} eff={s['effects']}")
    print("FAILS", bad)


if __name__ == "__main__":
    main()
