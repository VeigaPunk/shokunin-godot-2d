#!/usr/bin/env python3
"""r94-critic harness mutant builder: trimmed-CASES harness copies (base + synthetic dead r94 entry).

Mirrors the r93-critic harness-mutant liveness proof for the r94 floor gate
`r94_expected_errors_all_matched`.
"""
import ast, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "/tmp/r94crit-frozen/corpus/fixtures"

def build(variant, dead_entry):
    dst = os.path.join(ROOT, "mutants", "harness-" + variant)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(SRC, dst)
    h = os.path.join(dst, "run_battery.py")
    text = open(h).read()
    tree = ast.parse(text)
    node = next(n for n in tree.body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "CASES")
    keep = [e for e in node.value.elts
            if e.elts[0].value in ("mechanic", "r94_particles_census", "r94_particles_ppm",
                                   "save_process_writer", "save_process_reader",
                                   "save_process_missing")]
    lines = text.splitlines(keepends=True)
    start = node.lineno - 1
    end = node.end_lineno
    new = ["CASES = [\n"]
    for e in keep:
        row = tuple(ast.literal_eval(x) for x in e.elts)
        new.append("    " + repr(row) + ",\n")
    new.append("]\n")
    text = "".join(lines[:start]) + "".join(new) + "".join(lines[end:])
    if dead_entry:
        anchor = "            expected_errors = {\n"
        assert text.count(anchor) == 1
        text = text.replace(anchor, anchor +
                            '                "r94_particles_census": ("ERROR: synthetic never-matching r94 entry",),\n', 1)
    open(h, "w").write(text)
    json.dump({"variant": variant, "dead_entry": dead_entry,
               "cases": [ast.literal_eval(x)[0] for x in keep] if False else [e.elts[0].value for e in keep]},
              open(os.path.join(dst, "mutant.json"), "w"), indent=2)
    return dst

if __name__ == "__main__":
    for variant, dead in (("base", False), ("dead", True)):
        d = build(variant, dead)
        print("built", d)
