#!/usr/bin/env python3
"""r68 verifier: compare two verdicts.json files row-by-row modulo volatile fields."""
import json, re, sys

VOLATILE_KEYS = {"elapsed_seconds", "run_dir", "artifact", "command",
                 "godot_pid", "descendant_pid", "write_ppid", "pid", "pids",
                 "signature_observed_at",
                 "detached_control_descendant_pid",
                 "forged_release_descendant_pid",
                 "forged_gate_descendant_pid",
                 "release_gate_descendant_pid",
                 "descendant_kernel_ppid_at_return"}

def scrub(x):
    if isinstance(x, dict):
        return {k: scrub(v) for k, v in x.items() if k not in VOLATILE_KEYS}
    if isinstance(x, list):
        return [scrub(v) for v in x]
    if isinstance(x, str):
        # scrub absolute run-dir paths and timestamps embedded in strings
        x = re.sub(r"corpus/live/[A-Za-z0-9_-]+/runs/\d{8}T\d+Z", "<RUNS>", x)
        x = re.sub(r"/runs/\d{8}T\d+Z", "/runs/<STAMP>", x)
        x = re.sub(r"\d{8}T\d{6}\d*Z?", "<STAMP>", x)
        x = re.sub(r"MechanicOneShotTest-\d{8}T\d+Z", "MechanicOneShotTest-<STAMP>", x)
        x = re.sub(r"pid=\d+", "pid=<PID>", x)
        x = re.sub(r"spawned_pid=\d+", "spawned_pid=<PID>", x)
        x = re.sub(r"godot_pid=\d+", "godot_pid=<PID>", x)
        x = re.sub(r"write_ppid=\d+", "write_ppid=<PID>", x)
        x = re.sub(r"Node#\d+", "Node#<N>", x)
        # ASLR: hex load/backtrace addresses
        x = re.sub(r"0x[0-9a-fA-F]+", "0x<HEX>", x)
        x = re.sub(r"Load address: [0-9a-fA-F]+", "Load address: <HEX>", x)
        x = re.sub(r"\b[0-9a-f]{12}\b", "<HEX>", x)
        # float last-digit wobble (tween sampling)
        x = re.sub(r"\d+\.\d{4,}", "<FLOAT>", x)
        return x
    if isinstance(x, float):
        return round(x, 3)
    return x

def main():
    a_path, b_path = sys.argv[1], sys.argv[2]
    a = json.load(open(a_path))
    b = json.load(open(b_path))
    ar = {r["case"]: r for r in a["results"]}
    br = {r["case"]: r for r in b["results"]}
    only_a = sorted(set(ar) - set(br))
    only_b = sorted(set(br) - set(ar))
    mismatches = []
    for case in sorted(set(ar) & set(br)):
        if scrub(ar[case]) != scrub(br[case]):
            mismatches.append(case)
    print(f"A={a_path}")
    print(f"B={b_path}")
    print(f"common={len(set(ar)&set(br))} only_A={only_a} only_B={only_b}")
    print(f"mismatches={len(mismatches)} {mismatches[:20]}")
    for case in mismatches[:5]:
        sa, sb = scrub(ar[case]), scrub(br[case])
        for k in sorted(set(sa) | set(sb)):
            if sa.get(k) != sb.get(k):
                print(f"  {case}.{k}: A={json.dumps(sa.get(k))[:200]} B={json.dumps(sb.get(k))[:200]}")
    # also compare verdict tallies
    pa = sum(1 for r in a["results"] if r["verdict"] == "PASS")
    pb = sum(1 for r in b["results"] if r["verdict"] == "PASS")
    print(f"pass A={pa}/{len(ar)} B={pb}/{len(br)}")

main()
