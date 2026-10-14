"""r71 simplifier scratch: artifact comparator for LOVE battery verdicts.json.

Drops known-volatile fields (run paths, timestamps, elapsed) and diffs the
resulting structures, reporting the structural delta as a set of paths.
"""
import json
import sys
from pathlib import Path

VOLATILE = {"probe_dir", "probe", "started_utc", "probe_elapsed_s",
            "love_version_error", "pygame_version_error", "pygame_version",
            "pygame_version_exit", "python"}


def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    if isinstance(obj, str):
        # normalize run-local paths
        return obj.replace(str(Path(obj).parent), "<dir>") if "/" in obj else obj
    return obj


def walk(a, b, path="", out=None):
    if out is None:
        out = []
    if type(a) is not type(b):
        out.append(f"{path}: type {type(a).__name__} != {type(b).__name__}")
        return out
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(f"{path}.{k}: only-in-B")
            elif k not in b:
                out.append(f"{path}.{k}: only-in-A")
            else:
                walk(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f"{path}: len {len(a)} != {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append(f"{path}: {a!r} != {b!r}")
    return out


def main():
    a = json.loads(Path(sys.argv[1]).read_text())
    b = json.loads(Path(sys.argv[2]).read_text())
    diffs = walk(strip(a), strip(b))
    print(f"A={sys.argv[1]}")
    print(f"B={sys.argv[2]}")
    print(f"verdict A={a['verdict']} B={b['verdict']}  "
          f"totals A={a['totals']} B={b['totals']}")
    if not diffs:
        print("STRUCTURAL DIFF: none (identical modulo volatile fields)")
    else:
        print(f"STRUCTURAL DIFF: {len(diffs)} row(s)")
        for d in diffs:
            print(f"   {d}")


if __name__ == "__main__":
    main()
