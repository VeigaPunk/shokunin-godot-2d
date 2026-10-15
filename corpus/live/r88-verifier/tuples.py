#!/usr/bin/env python3
"""Emit the frozen tuple set for one battery receipt.

godot: one line per row —  <case>\t<verdict>\t<sha256 of the stable verdict
       tuple>  where the stable tuple is (case, script, flags, expected_exit,
       actual_exit, signature, verdict, error, expected_errors) for seeded
       rows and (case, verdict, canonical-JSON of the row minus volatile
       path/pid keys) for meta rows.
love:  one line per row —  <arm>|<key>\t<pinned>\t<verdict>\t<sha256 of the
       whole-row canonical JSON>

Usage: tuples.py {godot|love} <verdicts.json> <out.txt>
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare import canon, godot_tuple  # noqa: E402


def godot_tuple_sha(row):
    return hashlib.sha256(canon(list(godot_tuple(row))).encode()).hexdigest()


def main():
    mode, src, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    d = json.loads(src.read_text())
    lines = [f"# {mode} tuple set from {src}",
             f"# rows={len(d['results'])} verdict={d['verdict']} "
             f"file_sha256={hashlib.sha256(src.read_bytes()).hexdigest()}"]
    if mode == "godot":
        for r in d["results"]:
            lines.append(f"{r['case']}\t{r['verdict']}\t{godot_tuple_sha(r)}")
    elif mode == "love":
        for r in d["results"]:
            lines.append(f"{r['arm']}|{r['key']}\t{r['pinned']}\t"
                         f"{r['verdict']}\t"
                         f"{hashlib.sha256(canon(r).encode()).hexdigest()}")
    else:
        raise SystemExit("mode must be godot|love")
    out.write_text("\n".join(lines) + "\n")
    print(f"{out}: {len(lines) - 2} rows")


if __name__ == "__main__":
    main()
