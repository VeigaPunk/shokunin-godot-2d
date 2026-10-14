#!/usr/bin/env python3
"""Extract verbatim classifier/run_process source segments from the tracked
corpus/fixtures/run_battery.py via ast.get_source_segment and exec them into
a module namespace. Independence: never feeds strings to a paraphrase — the
exact tracked bytes run. Usage: `from extract_classifiers import NS`."""
import ast
import hashlib
from pathlib import Path

BATTERY = Path(__file__).resolve().parents[2] / "fixtures" / "run_battery.py"
WANTED = ("run_process", "classify_process", "classify_streams",
          "classify_audio_process")


def load():
    src = BATTERY.read_text()
    tree = ast.parse(src)
    # functions are nested inside main(); find them anywhere in the AST
    segs = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef,)) and node.name in WANTED:
            segs[node.name] = ast.get_source_segment(src, node)
    missing = [n for n in WANTED if n not in segs]
    if missing:
        raise RuntimeError(f"missing segments: {missing}")
    # dependency shims: classify_* reference nothing outside themselves
    # except builtins; run_process uses subprocess/datetime — exec with
    # the real imports available.
    import subprocess
    from datetime import datetime, timezone
    ns = {"subprocess": subprocess, "datetime": datetime,
          "timezone": timezone, "re": __import__("re")}
    for name in WANTED:
        # drop the 4-space method indent
        body = "\n".join(line[4:] if line.startswith("    ") else line
                         for line in segs[name].splitlines())
        exec(compile(body, f"<{name}>", "exec"), ns)
    shas = {n: hashlib.sha256(segs[n].encode()).hexdigest()[:16]
            for n in WANTED}
    return ns, segs, shas


NS, SEGMENTS, SEGMENT_SHAS = load()

if __name__ == "__main__":
    print("battery:", BATTERY)
    print("battery sha256:", hashlib.sha256(BATTERY.read_bytes()).hexdigest()[:16])
    for k, v in SEGMENT_SHAS.items():
        print(f"  {k}: {v}")
