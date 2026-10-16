#!/usr/bin/env python3
"""r95 reviewer: re-read the author's battery runs from disk (worktree-only)."""
import ast
import json
import pathlib
import subprocess

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
RUNS = REPO / "corpus/live/runs"
SEAT = REPO / "corpus/live/r95-reviewer"


def parse_cases(text):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("CASES not found")


def main():
    head_text = subprocess.run(["git", "show", "9cd47507:corpus/fixtures/run_battery.py"],
                               cwd=REPO, capture_output=True, text=True, check=True).stdout
    cases = [c for c in parse_cases(head_text)
             if c[0].startswith(("dss_lattice_", "r95b_order_"))]
    sigs = {c[0]: c[4] for c in cases}
    tracked = subprocess.run(["git", "ls-files", "corpus/live/runs"], cwd=REPO,
                             capture_output=True, text=True).stdout.split()
    out = {"tracked_run_files": len(tracked), "runs": []}
    for run_dir in sorted(RUNS.glob("2026*")):
        vf = run_dir / "verdicts.json"
        if not vf.exists():
            continue
        try:
            d = json.loads(vf.read_text())
        except Exception as exc:  # noqa: BLE001
            continue
        if not any(r.get("case", "").startswith(("dss_lattice_", "r95b_order_"))
                   for r in d.get("results", [])):
            continue
        results = {r["case"]: r for r in d["results"]}
        r95 = {k: v for k, v in results.items()
               if k.startswith(("dss_lattice_", "r95b_order_"))}
        gates = {}
        for r in d["results"]:
            if r["case"] == "probe_error_clause_surface":
                gates = {k: v for k, v in r.get("discriminations", {}).items()
                         if k.endswith("_expected_errors_all_matched")}
        rec = {
            "run": run_dir.name,
            "verdict": d.get("verdict"),
            "results": len(d["results"]),
            "r95_rows": len(r95),
            "r95_pass": sum(1 for r in r95.values() if r["verdict"] == "PASS"),
            "r95_sig_in_output": sum(1 for k, r in r95.items()
                                     if sigs.get(k) in "\n".join(r.get("output", []))),
            "r95_nonpass": [k for k, r in r95.items() if r["verdict"] != "PASS"],
            "failing_rows": [k for k, r in results.items() if r["verdict"] != "PASS"],
            "gate_r95": gates.get("r95_expected_errors_all_matched"),
            "gates_false": [k for k, v in gates.items() if v is False],
            "dead_entry_count": next((r.get("census", {}).get("dead_entry_count")
                                      for r in d["results"]
                                      if r["case"] == "probe_error_clause_surface"), None),
            "r95_row_fields": {k: {f: v[f] for f in ("verdict", "signature", "expected_exit",
                                                     "actual_exit", "error")}
                               for k, v in r95.items()},
            "r95_outputs": {k: r.get("output") for k, r in r95.items()},
        }
        out["runs"].append(rec)
    (SEAT / "author_runs.json").write_text(json.dumps(out, indent=2) + "\n")
    for r in out["runs"]:
        print(r["run"], r["verdict"], f"{r['r95_pass']}/{r['r95_rows']}",
              "gate_r95=", r["gate_r95"], "fail=", r["failing_rows"],
              "dead=", r["dead_entry_count"], "sig_in_out=", r["r95_sig_in_output"])
    print("tracked corpus/live/runs files:", out["tracked_run_files"])


if __name__ == "__main__":
    main()
