#!/usr/bin/env python3
"""r95 reviewer cross-session pin identity.

Sources per row:
  * this seat's fresh receipts (fresh/<stamp>/*.load.rep*.out)
  * the author's two green runs (corpus/live/runs/{20261016T064742446822Z,
    20261016T065922894811Z}/verdicts.json `output` lists)
  * scout canonical+loadtest receipts (dss_lattice rows)
  * boundary receipts (r95b_order rows)

Reports, per row: the number of distinct printed PASS lines (whole-line rows
must be 1), the distinct pinned-prefix payloads, and the distinct unpinned
tails for the four prefix rows.
"""
import ast
import json
import pathlib
import subprocess

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SEAT = REPO / "corpus/live/r95-reviewer"
PINNED = SEAT / "pinned-tmp/corpus/fixtures"
AUTHOR_RUNS = ["20261016T064742446822Z", "20261016T065922894811Z"]


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
    fresh = sorted((SEAT / "fresh").iterdir())[-1]
    author_lines = {}
    for run in AUTHOR_RUNS:
        d = json.loads((REPO / "corpus/live/runs" / run / "verdicts.json").read_text())
        for r in d["results"]:
            author_lines.setdefault(r["case"], []).append("\n".join(r.get("output", [])))
    out = {"fresh": str(fresh), "rows": {}}
    for case, script, flags, expected_exit, signature in cases:
        lines = []
        for f in sorted(fresh.glob(f"{case}.load.rep*.out")):
            for line in f.read_text().splitlines():
                if line.startswith(signature):
                    lines.append(line)
        src = {"fresh": len(lines)}
        lines_author = [l for blob in author_lines.get(case, [])
                        for l in blob.splitlines() if l.startswith(signature)]
        lines += lines_author
        src["author"] = len(lines_author)
        if case.startswith("dss_lattice_"):
            cell = case.replace("dss_lattice_", "r95_dss_")
            cell = {"r95_dss_shape": "r95_dss_shape_lattice",
                    "r95_dss_shape_rev": "r95_dss_shape_lattice_rev"}.get(cell, cell)
            files = sorted((REPO / "corpus/live/r95-scout/runs").glob(f"{cell}.rep*.out"))
            files += sorted((REPO / "corpus/live/r95-scout/runs/loadtest").glob(
                f"{cell.replace('r95_dss_', 'dss_')}.rep*.out"))
            n = 0
            for f in files:
                for line in f.read_text().splitlines():
                    if line.startswith(signature):
                        lines.append(line)
                        n += 1
            src["scout"] = n
        else:
            cell = case.removeprefix("r95b_order_")
            n = 0
            for batch in sorted((REPO / "corpus/live/r95-boundary/runs").iterdir()):
                if not batch.is_dir():
                    continue
                for f in sorted(batch.glob(f"{cell}.rep*.out")):
                    for line in f.read_text().splitlines():
                        if line.startswith(signature):
                            lines.append(line)
                            n += 1
            src["boundary"] = n
        whole = len(set(lines)) == 1
        # pinned prefix = the line up to the end of the committed signature
        prefixes = {line[: line.find(signature) + len(signature)] for line in lines}
        tails = {line[line.find(signature) + len(signature):] for line in lines}
        out["rows"][case] = {"sources": src, "printed_lines": len(lines),
                             "distinct_lines": len(set(lines)),
                             "distinct_prefixes": len(prefixes),
                             "distinct_tails": len(tails),
                             "whole_line_stable": whole,
                             "tail_sample": sorted(tails)[:2]}
    out["all_whole_line_stable"] = all(
        r["whole_line_stable"] for r in out["rows"].values()
        if r["distinct_tails"] == {""} or True)
    out["prefix_rows_multi_tail"] = {k: v["distinct_tails"] for k, v in out["rows"].items()
                                     if v["distinct_tails"] > 1}
    out["rows_with_multi_prefix"] = [k for k, v in out["rows"].items()
                                     if v["distinct_prefixes"] > 1]
    (SEAT / "cross_session.json").write_text(json.dumps(out, indent=2) + "\n")
    print("rows:", len(out["rows"]))
    print("rows with >1 distinct printed line:", [k for k, v in out["rows"].items()
                                                  if v["distinct_lines"] > 1])
    print("rows with >1 distinct prefix:", out["rows_with_multi_prefix"])
    print("prefix rows multi-tail:", out["prefix_rows_multi_tail"])


if __name__ == "__main__":
    main()
