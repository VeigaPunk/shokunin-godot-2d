#!/usr/bin/env python3
"""Per-row byte comparison table for the r87 baseline replay.

Usage: rowtable.py <mine-verdicts.json> <ref-verdicts.json> <out.txt>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare import canon, godot_output_norm, godot_tuple  # noqa: E402


def raw_output(row):
    if "output" in row and isinstance(row["output"], list):
        return "\n".join(row["output"])
    return None


def main():
    mine_p, ref_p, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    mine = json.loads(mine_p.read_text())
    ref = json.loads(ref_p.read_text())
    m = {r["case"]: r for r in mine["results"]}
    r = {x["case"]: x for x in ref["results"]}
    lines = [f"# mine={mine_p}",
             f"# ref ={ref_p}",
             "# case\tkind\ttuple_byte_identical\traw_stdout_identical\tnormalized_identical\tverdict"]
    for c in m:
        a, b = m[c], r.get(c)
        kind = "seeded" if "script" in a else "meta"
        if b is None:
            lines.append(f"{c}\t{kind}\tABSENT\tABSENT\tABSENT\t{a['verdict']}")
            continue
        tb = canon(godot_tuple(a)) == canon(godot_tuple(b))
        ra, rb = raw_output(a), raw_output(b)
        if ra is None or rb is None:
            raw = "not-carried"
        else:
            raw = "yes" if ra == rb else "NO"
        na, nb = godot_output_norm(a), godot_output_norm(b)
        nrm = "not-carried" if (na is None or nb is None) else ("yes" if na == nb else "NO")
        lines.append(f"{c}\t{kind}\t{'yes' if tb else 'NO'}\t{raw}\t{nrm}\t{a['verdict']}")
    out.write_text("\n".join(lines) + "\n")
    seeded = [l for l in lines[3:] if l.split("\t")[1] == "seeded"]
    meta = [l for l in lines[3:] if l.split("\t")[1] == "meta"]
    print(f"{out}: total={len(lines) - 3} seeded={len(seeded)} meta={len(meta)}")
    print("tuple_byte_identical yes=" + str(sum(1 for l in lines[3:] if l.split("\t")[2] == "yes")))
    print("raw_stdout_identical yes=" + str(sum(1 for l in lines[3:] if l.split("\t")[3] == "yes"))
          + " no=" + str(sum(1 for l in lines[3:] if l.split("\t")[3] == "NO"))
          + " not-carried=" + str(sum(1 for l in lines[3:] if l.split("\t")[3] == "not-carried")))
    print("normalized_identical yes=" + str(sum(1 for l in lines[3:] if l.split("\t")[4] == "yes"))
          + " no=" + str(sum(1 for l in lines[3:] if l.split("\t")[4] == "NO"))
          + " not-carried=" + str(sum(1 for l in lines[3:] if l.split("\t")[4] == "not-carried")))
    print("RAW-DIFF rows: " + ", ".join(l.split("\t")[0] for l in lines[3:] if l.split("\t")[3] == "NO"))


if __name__ == "__main__":
    main()
