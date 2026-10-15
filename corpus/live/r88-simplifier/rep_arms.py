#!/usr/bin/env python3
"""r88-simplifier direct arm reps: touched arms x N reps, battery launch shape.

usage: rep_arms.py <scratch-dir> <out-dir> [reps]
Normalizes the two declared-volatile tokens (uid digits, .gd line numbers)
exactly as the established compare tool does, then reports per-rep sha256.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ARMS = ["mp_loopback", "light_props", "sprite_phys", "vis_not"]
NORM = [
    (re.compile(r"\.(gd|lua|py):\d+"), r".\1:<N>"),
    (re.compile(r"\b\d{6,}\b"), "<UID>"),
]


def normalize(text: str) -> str:
    for pat, repl in NORM:
        text = pat.sub(repl, text)
    return text


def main() -> int:
    scratch = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    reps = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out.mkdir(parents=True, exist_ok=True)
    print(f"# scratch={scratch} reps={reps}")
    for arm in ARMS:
        for rep in range(reps):
            cmd = ["timeout", "15", "godot", "--headless", "--path", str(scratch),
                   "--script", "res://r88_surfaces.gd", "--", f"--arm={arm}"]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            merged = proc.stdout + proc.stderr
            norm = normalize(merged)
            digest = hashlib.sha256(norm.encode()).hexdigest()
            (out / f"{arm}.rep{rep}.out").write_text(merged)
            (out / f"{arm}.rep{rep}.norm").write_text(norm)
            pass_line = next((l for l in proc.stdout.splitlines()
                              if l.startswith("PASS r88_surfaces")), "<no-pass>")
            print(f"{arm} rep{rep} rc={proc.returncode} norm_sha256={digest[:16]} "
                  f"{pass_line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
