#!/usr/bin/env python3
"""r64 critic: run the LANDED gated_signature_run verbatim (ast extraction)
against the tracked fixture arms, proving the critic replica measures the
production code path, not a paraphrase."""
import ast, os, re, selectors, signal, subprocess, sys, time
from pathlib import Path

WORKTREE = Path.home() / "Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/run_battery.py"
PROJ = Path.home() / "Projects/shokunin/game-dev-2d-shokunin/corpus/live/r64-critic/proj"
src = WORKTREE.read_text()
tree = ast.parse(src)

grab = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in (
            "gated_signature_run", "pid_alive", "kernel_ppid", "classify_process"):
        grab[node.name] = ast.get_source_segment(src, node)
missing = {"gated_signature_run"} - set(grab)
assert not missing, f"could not extract {missing}"

# classify_process is a closure inside main; extraction still works since
# get_source_segment pulls the def text. pid_alive/kernel_ppid likewise.
env = {"os": os, "re": re, "selectors": selectors, "signal": signal,
       "subprocess": subprocess, "time": time}
for name, seg in grab.items():
    exec(compile(seg, f"<{name}>", "exec"), env)

class A:  # args namespace
    godot = "/usr/bin/godot"
args = A()
scratch = str(PROJ)
gate_marker = "DESCENDANT_PIPE_PROBE: expected signature"
gate_bound = 3.0
gate_poll_tick = 0.005

env.update(args=args, scratch=scratch, gate_marker=gate_marker,
           gate_bound=gate_bound, gate_poll_tick=gate_poll_tick)
run = env["gated_signature_run"]

import json
out = []
for case, flags in [("verbatim_genuine", []),
                    ("verbatim_detach", ["--spawn-detach"]),
                    ("verbatim_release_0", ["--spawn-forge-release"]),
                    ("verbatim_release_1", ["--spawn-forge-release"]),
                    ("verbatim_release_2", ["--spawn-forge-release"]),
                    ("verbatim_hold", ["--spawn-forge-hold"])]:
    rec = run(case, flags)
    rec.pop("output_lines", None)
    out.append(rec)
    print(f"{case:>20} exit={rec['actual_exit']} err={rec['error']!r} "
          f"marker={rec['marker_observed']}@{rec['marker_observed_at']} "
          f"dead@{rec['dead_observed_at']} "
          f"alive_at_obs={rec['child_alive_at_marker_observation']} "
          f"accept={rec['gated_signature_accepted']} "
          f"inner={rec['inner_classification']} "
          f"write_ppid={rec['write_ppid']} elapsed={rec['elapsed_seconds']}",
          flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "verbatim-gate.json"), "w"), indent=2)
print("saved verbatim-gate.json")
