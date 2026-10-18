#!/usr/bin/env python3
"""CRIT-6 (r101): floor-gate / dead-entry census coverage audit.

READ-ONLY analysis of corpus/fixtures/run_battery.py. This script NEVER
executes run_battery.py: it parses the source text with `ast`/regex and
reports the wiring that decides whether the r87 floor-gate law (r79-C2 /
r87-F3: "a dead expected_errors entry must not pass silently") covers a
given row family.

It extracts:
  * CASES          — the top-level battery row table (ast.literal_eval of
                     the assignment's literal, no module execution),
  * expected_errors— the per-case allowlist dict literal inside main(),
  * gates          — every "<name>_expected_errors_all_matched": all(...)
                     clause and the case-name prefixes its startswith(...)
                     filters on,
  * cases_integrity— the existence-check prefix tuple (r100-critic F1).

and reports, per gate/prefix:
  * rows matched in CASES, entry-bearing rows matched (vacuity check),
  * entry-bearing CASES rows covered by NO gate (the r87-F3 hole),
  * gate prefixes matching no CASES row (dangling / typo / drop),

usage:
  python3 crit6_floor_gate_coverage.py [--file PATH]
      [--plan-prefix NEW_PREFIX]...

exit code: 0 when no orphan entry-bearing row and no dangling gate prefix
exist among the *current* file; 1 otherwise (useful at integration time).
Planned prefixes (--plan-prefix) are reported but do not affect the exit
code by themselves; they DO affect it if they match entry-bearing rows.
"""
import argparse
import ast
import re
import sys
from pathlib import Path

DEFAULT = Path("corpus/fixtures/run_battery.py")


def extract_cases(tree):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CASES":
                    return [ast.literal_eval(elt)[0] for elt in node.value.elts]
    raise SystemExit("CASES assignment not found")


def extract_expected_errors_keys(text):
    # the dict literal assigned inside main(): "expected_errors = {" (12 sp)
    m = re.search(r"\n +expected_errors = \{", text)
    if not m:
        raise SystemExit("expected_errors dict not found")
    depth = 0
    start = text.index("{", m.start())
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    lit = text[start:end]
    # keys are 'name': (...) or "name": (...) at 16-space indent; strip comments
    keys = []
    for line in lit.splitlines():
        ls = line.strip()
        mm = re.match(r"^(?:'([^']+)'|\"([^\"]+)\")\s*:", ls)
        if mm:
            keys.append(mm.group(1) or mm.group(2))
    return keys


def extract_gates(text):
    gates = []
    for m in re.finditer(r'"(\w+)_expected_errors_all_matched": all\(', text):
        name = m.group(1)
        tail = text[m.end():]
        stop = tail.find('for e in r["entries"]')
        if stop == -1:
            stop = tail.find('for e in r["entries"])')
        span = tail[: stop + 40 if stop != -1 else 1200]
        sm = re.search(r"startswith\(([^)]*)\)", span)
        prefixes = []
        if sm:
            prefixes = re.findall(r'["\']([^"\']+)["\']', sm.group(1))
        gates.append((name, prefixes))
    ci = []
    cm = re.search(r'"cases_integrity": \(', text)
    if cm:
        tail = text[cm.end():]
        pm = re.search(r'for p in \(([^)]*)\)', tail)
        if pm:
            ci = re.findall(r'["\']([^"\']+)["\']', pm.group(1))
    return gates, ci


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, default=DEFAULT)
    ap.add_argument("--plan-prefix", action="append", default=[],
                    help="new-family prefix planned for this round")
    args = ap.parse_args()

    text = args.file.read_text()
    tree = ast.parse(text)

    cases = extract_cases(tree)
    entry_keys = extract_expected_errors_keys(text)
    gates, ci_prefixes = extract_gates(text)

    entry_set = set(entry_keys)
    print(f"file={args.file} cases_rows={len(cases)} "
          f"entry_bearing_cases={len(entry_keys)} "
          f"unique_names={len(set(cases))}")
    dup = sorted(n for n in set(cases) if cases.count(n) > 1)
    print(f"duplicate_case_names={dup}")

    covered = set()
    ok = True
    for name, prefixes in gates:
        rows = [c for c in cases if c.startswith(tuple(prefixes))]
        eb = [c for c in rows if c in entry_set]
        dangling = not rows
        if dangling:
            ok = False
        covered.update(eb)
        print(f"gate={name:34s} prefixes={prefixes!r:50s} "
              f"rows={len(rows):3d} entry_bearing={len(eb):3d}"
              f"{'  DANGLING(no CASES row matches)' if dangling else ''}")

    orphans = sorted(entry_set - covered)
    if orphans:
        ok = False
    print(f"gate_covered_entry_bearing_cases={len(covered)} "
          f"orphan_entry_bearing_cases={orphans}")

    # entry-bearing rows NOT in CASES at all (probe-appended names)
    not_in_cases = sorted(e for e in entry_keys if e not in set(cases))
    print(f"entry_keys_absent_from_CASES={not_in_cases}")

    print(f"cases_integrity_existence_prefixes={ci_prefixes}")
    for p in ci_prefixes:
        n = sum(1 for c in cases if c.startswith(p))
        if n == 0:
            ok = False
        print(f"  ci_prefix={p:18s} rows={n}")

    for p in args.plan_prefix:
        rows = [c for c in cases if c.startswith(p)]
        eb = [c for c in rows if c in entry_set]
        gated = [n for n, pre in gates
                 if any(p.startswith(q) for q in pre)]
        print(f"plan_prefix={p:22s} rows={len(rows)} entry_bearing={len(eb)} "
              f"covered_by_gates={gated or 'NONE'}")
        if eb and not gated:
            ok = False

    print("RESULT:", "OK (no orphans, no dangling prefixes)" if ok
          else "DEFECT (orphan entry rows / dangling prefix / planned "
               "entry-bearing family with no gate)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
