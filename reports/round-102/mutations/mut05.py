#!/usr/bin/env python3
"""
mut05 — resurrection mutation for r102 seat M5 (lane game-dev-2d-shokunin). C3.

Target: "S1's first applied hunk" := the first hunk of the first patch in the
canonical r101-simp1 apply order —
reports/round-101/mutations/r101-simp1-r91-nav_lattice.patch,
hunk @@ -53,7 +53,6 @@ (deletes `const SETTLE := 10` from corpus/fixtures/nav_lattice.gd).

Method (battery NEVER run; targeted headless launches only):
  base   = committed corpus/fixtures staged exactly like run_battery.py:1725-1745
  folded = base + the nav patch (S1's would-be first applied state)
  mutant = folded + the one deleted line re-added at its committed offset (resurrection)
  teeth  = mutant + one live-token change (comparator negative control)
Rows: the 11 nav_lattice CASES rows; pins extracted from run_battery.py via AST
(never executed). Receipts: (rc, stdout bytes, stderr bytes) per row per tree,
rep order folded,mutant interleaved twice + base 1 rep.
Classifier: replica of classify_process (+ required_stderr stream re-check),
run_battery.py:1775-1792 and 2335-2343.

Usage:
  python3 mut05.py --src <repo>/corpus/fixtures --work /var/tmp/r102-mut5 \
      --patch <repo>/reports/round-101/mutations/r101-simp1-r91-nav_lattice.patch \
      --battery <repo>/corpus/fixtures/run_battery.py --godot /usr/bin/godot
"""
import argparse, ast, difflib, hashlib, json, re, shutil, subprocess, sys, time
from pathlib import Path

def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def extract_pins(battery: Path):
    tree = ast.parse(battery.read_text())
    cases, allow, req = None, {}, {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if not isinstance(t, ast.Name):
                continue
            if t.id == "CASES" and cases is None:
                cases = ast.literal_eval(node.value)
            v = node.value
            if (t.id in ("expected_errors", "required_stderr")
                    and isinstance(v, ast.Call)
                    and isinstance(v.func, ast.Attribute) and v.func.attr == "get"
                    and isinstance(v.func.value, ast.Dict)):
                table = ast.literal_eval(v.func.value)
                if t.id == "expected_errors":
                    allow = table
                else:
                    req = table
    if cases is None:
        raise SystemExit("CASES not found")
    nav = [c for c in cases if c[1] == "nav_lattice.gd"]
    return nav, allow, req

def stage_baseline(src: Path, dest: Path, stamp: str):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in sorted(src.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    pj = dest / "project.godot"
    txt = pj.read_text()
    old = 'config/name="MechanicOneShotTest"'
    assert old in txt, "project.godot name anchor missing"
    pj.write_text(txt.replace(old, f'config/name="MechanicOneShotTest-{stamp}"', 1))
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in text, "causal_chain readiness anchor missing"
    chain.write_text(text.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))

def build_folded(base: Path, folded: Path, patchfile: Path):
    if folded.exists():
        shutil.rmtree(folded)
    shutil.copytree(base, folded)
    r = subprocess.run(["patch", "-p3", "-d", str(folded), "-i", str(patchfile.resolve())],
                       capture_output=True, text=True)
    return (r.stdout + r.stderr).strip(), r.returncode

def build_mutant(folded: Path, mutant: Path):
    if mutant.exists():
        shutil.rmtree(mutant)
    shutil.copytree(folded, mutant)
    f = mutant / "nav_lattice.gd"
    text = f.read_text()
    assert "const SETTLE" not in text, "folded tree unexpectedly still has SETTLE"
    needle = "const SYNC_BOUND := 48"
    assert text.count(needle) == 1, "SYNC_BOUND anchor not unique"
    f.write_text(text.replace("\n\n" + needle, "\n\nconst SETTLE := 10\n" + needle, 1))
    return f

def build_teeth(mutant: Path, teeth: Path):
    if teeth.exists():
        shutil.rmtree(teeth)
    shutil.copytree(mutant, teeth)
    f = teeth / "nav_lattice.gd"
    text = f.read_text()
    assert text.count("srv_methods") == 1, "teeth token not unique"
    f.write_text(text.replace("srv_methods", "srv_methodsX", 1))

def launch(godot: str, tree: Path, row, timeout=8):
    cmd = [godot, "--headless", "--path", str(tree), "--script", "res://" + row[1], "--", *row[2]]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return dict(rc=p.returncode, out=p.stdout, err=p.stderr, error=None, cmd=cmd, secs=round(time.time() - t0, 3))
    except subprocess.TimeoutExpired as e:
        out = e.stdout if isinstance(e.stdout, bytes) else (e.stdout or "").encode()
        err = e.stderr if isinstance(e.stderr, bytes) else (e.stderr or "").encode()
        return dict(rc=None, out=out, err=err, error=f"TIMEOUT>{timeout}s", cmd=cmd, secs=round(time.time() - t0, 3))

def classify_process(exit_code, out_b, err_b, expected_exit, signature, allowed_errors):
    out = out_b.decode(errors="replace")
    err = err_b.decode(errors="replace")
    merged = out + err
    lines = merged.splitlines()

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

    unrelated = [line for line in lines if "ERROR:" in line
                 and not any(allowed_error(line, a) for a in allowed_errors)]
    return (exit_code == expected_exit and signature in merged and not unrelated
            and "SCRIPT ERROR:" not in merged and "Parse Error:" not in merged)

def receipt(godot, tree: Path, row, timeout=8):
    res = launch(godot, tree, row, timeout)
    name, script, flags, expected_exit, signature = row
    allowed = ALLOW.get(name, ())
    req = REQ.get(name, ())
    passed = classify_process(res["rc"], res["out"], res["err"], expected_exit, signature, allowed)
    stream_ok = True
    if req:
        s_out = res["out"].decode(errors="replace")
        s_err = res["err"].decode(errors="replace")
        stream_ok = all(frag in s_err for frag in req) and any(sig in s_out for sig in (signature,))
        passed = passed and stream_ok
    return dict(rc=res["rc"], error=res["error"], stdout_sha=sha_bytes(res["out"]),
                stderr_sha=sha_bytes(res["err"]), stdout_len=len(res["out"]),
                stderr_len=len(res["err"]), verdict="PASS" if passed else "FAIL",
                required_stderr_ok=stream_ok, secs=res["secs"], cmd=" ".join(res["cmd"]),
                _out=res["out"], _err=res["err"])

TOKEN = re.compile(r"([A-Za-z0-9_]+)=(\[[^\]]*\]|\S+)")

def keyvals(stdout_b: bytes):
    vals = {}
    for line in stdout_b.decode(errors="replace").splitlines():
        for k, v in TOKEN.findall(line):
            vals.setdefault(k, set()).add(v)
    return vals

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--patch", required=True)
    ap.add_argument("--battery", required=True)
    ap.add_argument("--godot", default="godot")
    a = ap.parse_args()
    src, work, patchfile = Path(a.src), Path(a.work), Path(a.patch)
    global ALLOW, REQ
    rows, ALLOW, REQ = extract_pins(Path(a.battery))
    rows.sort(key=lambda r: r[0])
    print(f"MUT5 pins: {len(rows)} nav rows; allowlists={sorted(k for k in ALLOW if k.startswith('nav_'))}; "
          f"required_stderr={sorted(k for k in REQ if k.startswith('nav_'))}")
    work.mkdir(parents=True, exist_ok=True)
    rec_dir = work / "receipts"
    rec_dir.mkdir(exist_ok=True)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    base = work / "trees" / "base"
    folded = work / "trees" / "folded"
    mutant = work / "trees" / "mutant"
    teeth = work / "trees" / "teeth"
    stage_baseline(src, base, stamp)
    base_gd = base / "nav_lattice.gd"
    print(f"MUT5 base   nav_lattice.gd sha256={sha_bytes(base_gd.read_bytes())}")
    pout, prc = build_folded(base, folded, patchfile)
    print(f"MUT5 patch  rc={prc} out={pout!r}")
    assert prc == 0, "patch did not apply cleanly"
    folded_gd = folded / "nav_lattice.gd"
    folded_sha = sha_bytes(folded_gd.read_bytes())
    print(f"MUT5 folded nav_lattice.gd sha256={folded_sha}")
    assert folded_sha.startswith("b23887e5"), f"folded sha {folded_sha} != simp1-recorded b23887e5..."
    m_gd = build_mutant(folded, mutant)
    mut_sha = sha_bytes(m_gd.read_bytes())
    diff = list(difflib.unified_diff(folded_gd.read_text().splitlines(keepends=True),
                                     m_gd.read_text().splitlines(keepends=True),
                                     "folded/nav_lattice.gd", "mutant/nav_lattice.gd"))
    plus = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    minus = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    print(f"MUT5 mutant nav_lattice.gd sha256={mut_sha} diff_lines=+{len(plus)}/-{len(minus)} resurrected={plus!r}")
    assert len(plus) == 1 and len(minus) == 0 and plus[0] == "+const SETTLE := 10\n", "resurrection diff is not exactly one line"
    build_teeth(mutant, teeth)
    teeth_sha = sha_bytes((teeth / "nav_lattice.gd").read_bytes())
    print(f"MUT5 teeth  nav_lattice.gd sha256={teeth_sha} (live-token srv_methods->srv_methodsX)")

    receipts = {}
    order = []
    for rep in (1, 2):
        for tree_name, tree in (("folded", folded), ("mutant", mutant)):
            for row in rows:
                name = row[0]
                r = receipt(a.godot, tree, row)
                (rec_dir / f"{tree_name}__{name}__rep{rep}.out").write_bytes(r.pop("_out"))
                (rec_dir / f"{tree_name}__{name}__rep{rep}.err").write_bytes(r.pop("_err"))
                r["stdout_path"] = str(rec_dir / f"{tree_name}__{name}__rep{rep}.out")
                r["stderr_path"] = str(rec_dir / f"{tree_name}__{name}__rep{rep}.err")
                receipts[f"{tree_name}:{name}:rep{rep}"] = r
                order.append((tree_name, name, rep, r))
                print(f"MUT5 run {tree_name:6s} rep{rep} {name:26s} rc={r['rc']} verdict={r['verdict']} secs={r['secs']}")
    for row in rows:
        name = row[0]
        r = receipt(a.godot, base, row)
        (rec_dir / f"base__{name}__rep1.out").write_bytes(r.pop("_out"))
        (rec_dir / f"base__{name}__rep1.err").write_bytes(r.pop("_err"))
        r["stdout_path"] = str(rec_dir / f"base__{name}__rep1.out")
        r["stderr_path"] = str(rec_dir / f"base__{name}__rep1.err")
        receipts[f"base:{name}:rep1"] = r
        print(f"MUT5 run base   rep1 {name:26s} rc={r['rc']} verdict={r['verdict']} secs={r['secs']}")
    teeth_row = [r for r in rows if r[0] == "nav_lattice_census"][0]
    tr = receipt(a.godot, teeth, teeth_row)
    (rec_dir / "teeth__nav_lattice_census__rep1.out").write_bytes(tr.pop("_out"))
    (rec_dir / "teeth__nav_lattice_census__rep1.err").write_bytes(tr.pop("_err"))
    tr["stdout_path"] = str(rec_dir / "teeth__nav_lattice_census__rep1.out")
    tr["stderr_path"] = str(rec_dir / "teeth__nav_lattice_census__rep1.err")
    receipts["teeth:nav_lattice_census:rep1"] = tr
    print(f"MUT5 run teeth  rep1 nav_lattice_census        rc={tr['rc']} verdict={tr['verdict']} (expect FAIL)")

    summary = {"rows": [r[0] for r in rows], "shas": {"base": sha_bytes(base_gd.read_bytes()), "folded": folded_sha,
               "mutant": mut_sha, "teeth": teeth_sha}, "receipts": receipts}
    (work / "summary.json").write_text(json.dumps(summary, indent=1, default=str))

    print("\n=== comparison folded vs mutant (per row, both reps) ===")
    all_pass = True
    for row in rows:
        name = row[0]
        f1 = receipts[f"folded:{name}:rep1"]; f2 = receipts[f"folded:{name}:rep2"]
        m1 = receipts[f"mutant:{name}:rep1"]; m2 = receipts[f"mutant:{name}:rep2"]
        b1 = receipts[f"base:{name}:rep1"]
        rcs = {f1["rc"], f2["rc"], m1["rc"], m2["rc"]}
        raw_f = f1["stdout_sha"] == f2["stdout_sha"]
        raw_eq = (f1["stdout_sha"] == m1["stdout_sha"] == m2["stdout_sha"] == f2["stdout_sha"])
        verdicts = sorted({f1["verdict"], f2["verdict"], m1["verdict"], m2["verdict"]})
        base_same_as_f1 = b1["stdout_sha"] == f1["stdout_sha"]
        print(f"MUT5 cmp {name:26s} rc_set={sorted(rcs)} verdicts={verdicts} "
              f"stdout folded-rep-stable={raw_f} all4byte-identical={raw_eq} base==folded_rep1={base_same_as_f1}")
        if verdicts != ["PASS"] and name != "nav_lattice_teardown_crash" or (name == "nav_lattice_teardown_crash" and "PASS" not in verdicts):
            all_pass = False
    print(f"MUT5 teeth verdict={receipts['teeth:nav_lattice_census:rep1']['verdict']} (expect FAIL)")

    print("\n=== divergent-key analysis (per row; keys with >1 value per tree, or fold-effect candidates) ===")
    for row in rows:
        name = row[0]
        fs, ms, bs = [receipts[f"folded:{name}:rep{r}"]["stdout_path"] for r in (1, 2)], \
                     [receipts[f"mutant:{name}:rep{r}"]["stdout_path"] for r in (1, 2)], \
                     [receipts[f"base:{name}:rep1"]["stdout_path"]]
        fv = keyvals(Path(fs[0]).read_bytes()); fv2 = keyvals(Path(fs[1]).read_bytes())
        mv = keyvals(Path(ms[0]).read_bytes()); mv2 = keyvals(Path(ms[1]).read_bytes())
        bv = keyvals(Path(bs[0]).read_bytes())
        for k in sorted(set(fv) | set(mv) | set(bv)):
            fset = fv.get(k, set()) | fv2.get(k, set())
            mset = mv.get(k, set()) | mv2.get(k, set())
            bset = bv.get(k, set())
            f_stable = len(fset) == 1
            if mset != fset or bset != fset:
                kind = "EFFECT" if (f_stable and mset != fset) else "noise-or-ctx"
                print(f"MUT5 key {name:26s} {k:24s} folded={sorted(fset)} mutant={sorted(mset)} base={sorted(bset)} [{kind}]")
    print("\nMUT5 ALLPASS=" + str(all_pass))

if __name__ == "__main__":
    main()
