#!/usr/bin/env python3
"""r90-simplifier — explicit r90-row identity: my control run vs the author's two
canonical green runs (tuple + normalized output), restricted to the 12 r90 rows.
"""
import glob
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
NORM = [
    (re.compile(r"[^\s'\"]*corpus/live/[^\s'\"]*"), "<runpath>"),
    (re.compile(r"\.(gd|lua|py):\d+"), r".\1:<N>"),
    (re.compile(r"((?:write_)?ppid|godot_pid|descendant_pid|pid)[\"']?\s*[:=]\s*\d+"), r"\1=<pid>"),
    (re.compile(r"0x[0-9a-f]+"), "0x<addr>"),
    (re.compile(r"\b[0-9a-f]{8,}\b"), "<addr>"),
    (re.compile(r"elapsed[_a-z]*[\"']?\s*[:=]\s*[0-9.]+"), "elapsed=<t>"),
]
TUPLE_KEYS = ("case", "script", "flags", "expected_exit", "actual_exit",
              "signature", "verdict", "error", "expected_errors")


def load(p):
    d = json.loads(pathlib.Path(p).read_text())
    return {r["case"]: r for r in d["results"]}


def norm(lines):
    out = []
    for l in lines or []:
        for rx, rep in NORM:
            l = rx.sub(rep, l)
        out.append(l)
    return out


def main():
    mine = sorted(glob.glob(str(HERE / "runs-control" / "*" / "verdicts.json")))[-1]
    refs = {
        "green9": "corpus/live/r90-author/runs9/20261015T212551992799Z/verdicts.json",
        "green12b": "corpus/live/r90-author/runs12/20261015T220233737605Z/verdicts.json",
    }
    m = load(mine)
    print(f"mine={mine}")
    for tag, path in refs.items():
        r = load(path)
        r90 = [c for c in m if c.startswith("r90_")]
        tup_bad, out_bad = [], []
        for c in r90:
            a, b = m[c], r[c]
            if tuple(a.get(k) for k in TUPLE_KEYS) != tuple(b.get(k) for k in TUPLE_KEYS):
                tup_bad.append(c)
            if norm(a.get("output")) != norm(b.get("output")):
                out_bad.append(c)
        print(f"  {tag}: r90_rows={len(r90)} tuple_mismatches={tup_bad} "
              f"output_diffs={out_bad} identical={not tup_bad and not out_bad}")


if __name__ == "__main__":
    main()
