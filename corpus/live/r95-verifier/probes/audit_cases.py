#!/usr/bin/env python3
"""Static audit of the frozen committed harness (9cd47507) — CASES shape and
the r95 block's placement, flags, signature provenance surface."""
import importlib.util
import json
import re
import sys
from pathlib import Path

FIX = Path(sys.argv[1])  # frozen corpus/fixtures dir
OUT = Path(sys.argv[2])

spec = importlib.util.spec_from_file_location("frozen_run_battery", FIX / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

cases = mod.CASES
names = [c[0] for c in cases]
r95_idx = [i for i, n in enumerate(names) if n.startswith(("dss_lattice_", "r95b_order_"))]
r95 = [(i, cases[i][0], cases[i][1], cases[i][2], cases[i][3]) for i in r95_idx]
dss = [r for r in r95 if r[1].startswith("dss_lattice_")]
ordr = [r for r in r95 if r[1].startswith("r95b_order_")]

src = (FIX / "run_battery.py").read_text()
# occurrences of r95 tokens outside the CASES block (line < 878 or > 1030)
lines = src.splitlines()
outside = [(i + 1, l) for i, l in enumerate(lines)
           if re.search(r"dss_lattice_|r95b_order_|r95_expected_errors", l)
           and not (878 <= i + 1 <= 1030)]
gate = "r95_expected_errors_all_matched" in src
# r95 names as keys of expected_errors / required_stderr dicts?
name_keys = re.findall(r"^\s*['\"](dss_lattice_[a-z_0-9]+|r95b_order_[a-z_0-9]+)['\"]\s*:", src, re.M)

report = {
    "cases_total": len(cases),
    "r95_count": len(r95_idx),
    "r95_first_index": r95_idx[0],
    "r95_last_index": r95_idx[-1],
    "r95_contiguous": r95_idx == list(range(r95_idx[0], r95_idx[-1] + 1)),
    "dss_count": len(dss),
    "order_count": len(ordr),
    "flags": {r[1]: r[3] for r in r95},
    "scripts": sorted({r[2] for r in r95}),
    "expected_exit_set": sorted({r[4] for r in r95}),
    "floor_gate_present": gate,
    "r95_tokens_outside_cases_block": outside,
    "r95_names_as_dict_keys": name_keys,
    "next_case_after_r95": names[r95_idx[-1] + 1] if r95_idx[-1] + 1 < len(names) else None,
    "prev_case_before_r95": names[r95_idx[0] - 1],
    "last_cases": names[-4:],
}
OUT.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: report[k] for k in
                  ("cases_total", "r95_count", "r95_first_index", "r95_last_index",
                   "r95_contiguous", "dss_count", "order_count", "floor_gate_present",
                   "next_case_after_r95", "prev_case_before_r95", "r95_names_as_dict_keys",
                   "r95_tokens_outside_cases_block")}, indent=2))
