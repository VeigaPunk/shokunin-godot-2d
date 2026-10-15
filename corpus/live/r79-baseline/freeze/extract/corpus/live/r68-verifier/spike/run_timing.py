#!/usr/bin/env python3
"""r68-verifier: run the instrumented probe across offsets, measure write-vs-gap."""
import json, re, subprocess, sys

GODOT = "/usr/bin/godot"
PROJ = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r68-verifier/spike/proj"

def run(off, gap=200):
    p = subprocess.run([GODOT, "--headless", "--path", PROJ,
                        "--script", "res://v_timing_probe.gd", "--",
                        f"--off={off}", f"--gap={gap}"],
                       capture_output=True, text=True, timeout=10)
    so, se = p.stdout or "", p.stderr or ""
    merged = so + se
    head = int(re.search(r"V_HEAD_MS=(\d+)", se).group(1))
    tail = int(re.search(r"V_TAIL_MS=(\d+)", se).group(1))
    write = int(re.search(r"V_WRITE_MS=(\d+)", merged).group(1))
    spliced = any("DESCENDANT_PIPE_PROBE: expected " in l and "ERROR:" in l
                  for l in merged.splitlines())
    sig_intact = "DESCENDANT_PIPE_PROBE: expected signature" in merged
    return {"off": off, "gap": gap, "exit": p.returncode,
            "head_ms": head, "tail_ms": tail, "write_ms": write,
            "write_rel_head": write - head, "write_rel_tail": write - tail,
            "gap_measured": tail - head,
            "spliced": spliced, "sig_intact": sig_intact}

def main():
    offsets = [0, 40, 80, 120, 160, 190, 195, 198, 200, 205, 240]
    reps = 3
    out = []
    for off in offsets:
        for rep in range(reps):
            r = run(off)
            r["rep"] = rep
            out.append(r)
            print(f"off={off:4d} rep={rep} write_rel_head={r['write_rel_head']:5d} "
                  f"gap={r['gap_measured']} spliced={r['spliced']} sig_intact={r['sig_intact']}",
                  flush=True)
    json.dump(out, open(sys.argv[1], "w"), indent=1)

main()
