#!/usr/bin/env python3
"""r91-critic: cross-check the author's untracked evidence (secondary).

  - runs1/runs2 verdicts.json: row count, all-PASS, nav rows present & PASS,
    r91 floor-gate discrimination value.
  - fresh-reps/*.out|err|rc (11 arms x 3): re-classified through the
    production classifier extracted from the frozen committed blob.
Read-only; nothing written outside this seat dir.
"""
import ast
import glob
import hashlib
import json
import pathlib
import sys

SEAT = pathlib.Path(__file__).resolve().parent.parent
REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
AUTHOR = REPO / "corpus/live/r91-author"
FROZEN = SEAT / "run_battery.committed-77d2f7e.py"

ALLOW = {
    "nav_lattice_sync": (
        "ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.",),
    "nav_lattice_bake": ("ERROR: The root node needs to be inside the SceneTree.",),
}
REQ_STDERR = {"nav_lattice_teardown_crash": ("double free or corruption",)}


def extract(fname):
    src = FROZEN.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == fname:
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("def " + fname + seg.split("def " + fname, 1)[1], ns)
            return ns[fname], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit(fname + " not found")


def main():
    cases = None
    src = FROZEN.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            cases = ast.literal_eval(node.value)
    cls, sha = extract("classify_process")
    nav = {c[0]: c for c in cases if c[0].startswith("nav_lattice_")}
    report = {"classifier_sha256": sha, "battery_runs": {}, "fresh_reps": {}}

    for run in sorted(AUTHOR.glob("runs*/2026*")):
        v = json.loads((run / "verdicts.json").read_text())
        rows = v["results"]
        nav_rows = [r for r in rows if r["case"].startswith("nav_lattice_")]
        meta = next((r for r in rows if r["case"] == "probe_error_clause_surface"), None)
        report["battery_runs"][run.parent.name] = {
            "rows": len(rows), "verdict": v["verdict"],
            "nav_rows": len(nav_rows),
            "nav_all_pass": all(r["verdict"] == "PASS" for r in nav_rows),
            "r91_gate": (meta or {}).get("discriminations", {}).get(
                "r91_expected_errors_all_matched"),
            "teardown_crash_exit": next(
                (r["actual_exit"] for r in nav_rows
                 if r["case"] == "nav_lattice_teardown_crash"), None),
        }

    ok = bad = 0
    for out_p in sorted((AUTHOR / "fresh-reps").glob("*.out")):
        arm = out_p.name.split(".")[0]
        base = out_p.with_suffix("")
        err = pathlib.Path(str(base) + ".err").read_text()
        rc = int(pathlib.Path(str(base) + ".rc").read_text().strip())
        code = -(rc - 128) if rc > 128 else rc
        name = f"nav_lattice_{arm}"
        case = nav[name]
        sig = case[4]
        verdict = cls(code, None, out_p.read_text() + err, case[3], sig,
                      ALLOW.get(name, ()))
        if name in REQ_STDERR:
            verdict = verdict and all(f in err for f in REQ_STDERR[name]) \
                and sig in out_p.read_text()
        report["fresh_reps"][out_p.name] = "PASS" if verdict else "FAIL"
        ok += verdict
        bad += (not verdict)
    report["fresh_reps_pass"] = ok
    report["fresh_reps_fail"] = bad
    (SEAT / "author_crosscheck.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
