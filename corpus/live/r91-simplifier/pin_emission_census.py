#!/usr/bin/env python3
"""Pin<->emission census for the r91 nav_lattice rows.

Reads the control battery's verdicts.json and, for each nav_lattice_* row:
  - the emitted line carrying the signature
  - asserts the pinned signature is a BYTE-EXACT PREFIX of that emitted line
  - asserts every field name in the remainder (the diagnostic tail) is a
    declared tail field
  - asserts the pinned block carries no unpinned field (i.e. the tail is the
    only thing after the signature)
Also reports the declared expected_errors / required_stderr entries and the
census records (dead_in_run, bare/allowlisted classification) for the two
whitelist-bearing rows.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = sorted((HERE / "runs-control").glob("*/"))[-1]
d = json.loads((RUN / "verdicts.json").read_text())
rows = {r["case"]: r for r in d["results"]}

TAIL_FIELDS = ["settle", "settle_a", "settle_b", "iter", "ladder", "first_reach",
               "first_reach_sync", "walk_steps", "reached_at", "first_reachable",
               "iter_b", "link_iter", "gate", "chg_iter_same",
               "chg_iter_settled", "dis_same", "fwd_disabled_same", "seq_a",
               "seq_b", "vel_a", "vel_b", "sum_max"]

print("== r91 pin<->emission census ==")
print("run: %s" % RUN)
print("battery verdict: %s" % d["verdict"])
print()
ok = True
for name in sorted(rows):
    if not name.startswith("nav_lattice_"):
        continue
    r = rows[name]
    sig = r["signature"]
    lines = r["output"]
    hits = [l for l in lines if sig in l]
    if len(hits) != 1:
        print("%-30s SIGNATURE-HIT-COUNT=%d (expected 1)" % (name, len(hits)))
        ok = False
        continue
    line = hits[0]
    prefix_ok = line.startswith(sig)
    rest = line[len(sig):] if prefix_ok else "<N/A>"
    tail_names = re.findall(r"([a-z_]+)=", rest) if prefix_ok else []
    bad_tail = [t for t in tail_names if t not in TAIL_FIELDS]
    # every declared tail field must be accounted for (emitted or deliberately absent)
    print("%-30s prefix=%s rest_len=%-4d tail_fields=%s unpinned_in_tail=%s"
          % (name, prefix_ok, len(rest), tail_names, bad_tail or "none"))
    if not prefix_ok or bad_tail:
        ok = False
print()
print("ALL_PINS_ARE_BYTE_EXACT_PREFIXES_OF_EMISSION=%s" % ok)
print()

print("-- whitelist / crash-pin liveness (from the run's own census) --")
surf = d.get("surface_census") or d.get("probe_error_clause_surface") or {}
# locate the census payload wherever the harness put it
def find_census(o, path=""):
    if isinstance(o, dict):
        if "rows" in o and "dead_entry_count" in o:
            return o
        for k, v in o.items():
            got = find_census(v, path + "/" + str(k))
            if got is not None:
                return got
    elif isinstance(o, list):
        for i, v in enumerate(o):
            got = find_census(v, path + "/%d" % i)
            if got is not None:
                return got
    return None

census = find_census(d)
if census is None:
    print("census payload not found in verdicts.json")
else:
    for row in census["rows"]:
        if not row["case"].startswith("nav_lattice_"):
            continue
        print("%-30s any_entry_matched=%-5s bare_rejects=%-5s allowlisted_passes=%-5s entries=%s"
              % (row["case"], row["any_entry_matched"],
                 row["bare_classification_rejects"],
                 row["allowlisted_classification_passes"],
                 [(e["entry"][:48], e["matched_lines"], e["dead_in_run"]) for e in row["entries"]]))
    print("census dead_entry_count=%s" % census["dead_entry_count"])
    print("census dead_entries=%s" % census["dead_entries"])

print()
print("-- gate values (from the run's discrimination payload) --")
def find_gates(o):
    if isinstance(o, dict):
        if any(k.startswith("r91_expected") for k in o):
            return o
        for v in o.values():
            got = find_gates(v)
            if got is not None:
                return got
    elif isinstance(o, list):
        for v in o:
            got = find_gates(v)
            if got is not None:
                return got
    return None

gates = find_gates(d)
if gates is None:
    print("  <gates not found>")
else:
    for k, v in sorted(gates.items()):
        if k.startswith(("r87_", "r88_", "r89_", "r90_", "r91_", "phys2d_",
                         "census_", "detached", "prior_meta")):
            print("  %-46s %s" % (k, v))
