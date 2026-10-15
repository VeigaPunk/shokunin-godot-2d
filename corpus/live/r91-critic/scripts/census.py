#!/usr/bin/env python3
"""r91-critic: reproduce the battery's expected_errors dead-entry census and the
r91_expected_errors_all_matched discrimination from seat-owned receipts.

usage: census.py <tag>
Mirrors run_battery.py's census block (surface_allowed_error / entry_shape /
classify_process extracted from the frozen committed blob).
"""
import ast
import hashlib
import json
import pathlib
import sys

SEAT = pathlib.Path(__file__).resolve().parent.parent
FROZEN = SEAT / "run_battery.committed-77d2f7e.py"
RUNS = SEAT / "runs"

ALLOW = {
    "nav_lattice_sync": (
        "ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.",),
    "nav_lattice_bake": ("ERROR: The root node needs to be inside the SceneTree.",),
}


def load_cases():
    src = FROZEN.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("CASES not found")


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
    tag = sys.argv[1]
    cases = load_cases()
    surface_allowed_error, sha1 = extract("surface_allowed_error")
    entry_shape, sha2 = extract("entry_shape")
    classify_process, sha3 = extract("classify_process")
    rows = []
    for case in cases:
        name, script, flags, exit_, sig = case
        if name not in ALLOW:
            continue
        arm = flags[0].split("=")[1]
        entries = ALLOW[name]
        recs = []
        for o in sorted(RUNS.glob(f"{tag}.{arm}.rep*.out")):
            k = o.name.rsplit(".rep", 1)[1].split(".")[0]
            base = RUNS / f"{tag}.{arm}.rep{k}"
            text = o.read_text() + (RUNS / f"{base}.err").read_text()
            rc = int((RUNS / f"{base}.rc").read_text().strip())
            code = -(rc - 128) if rc > 128 else rc
            entry_records = []
            for entry in entries:
                matched = [ln.strip() for ln in text.splitlines()
                           if surface_allowed_error(ln, entry)]
                entry_records.append({"entry": entry, "shape": entry_shape(entry),
                                      "matched_lines": len(matched),
                                      "dead_in_run": not matched,
                                      "first_match": matched[0] if matched else None})
            recs.append({"rep": k, "code": code, "entries": entry_records})
        rows.append({"case": name, "reps": recs})
    dead = [{"case": r["case"], "rep": rep["rep"], "entry": e["entry"]}
            for r in rows for rep in r["reps"] for e in rep["entries"]
            if e["dead_in_run"]]
    gate = all(not e["dead_in_run"]
               for r in rows for rep in r["reps"] for e in rep["entries"])
    out = {"tag": tag, "segment_sha256": {"surface_allowed_error": sha1,
                                          "entry_shape": sha2,
                                          "classify_process": sha3},
           "rows": rows, "dead_entry_count": len(dead), "dead_entries": dead,
           "r91_expected_errors_all_matched": gate}
    (SEAT / f"census.{tag}.json").write_text(json.dumps(out, indent=2) + "\n")
    for r in rows:
        for rep in r["reps"]:
            print(f"{r['case']:20s} rep{rep['rep']} code={rep['code']:3d} " +
                  " ".join(f"{e['shape']}:n{e['matched_lines']}"
                           f"{'*DEAD*' if e['dead_in_run'] else ''}"
                           for e in rep["entries"]))
    print(f"dead_entry_count={len(dead)} "
          f"r91_expected_errors_all_matched={gate}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
