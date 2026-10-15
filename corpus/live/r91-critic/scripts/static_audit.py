#!/usr/bin/env python3
"""r91-critic static audit of the committed 77d2f7e landing.

Checks (all read-only, against the frozen committed blobs):
  1. CASES count / nav_lattice_ row count / insertion ordering.
  2. No declared scheduler/race field appears as a token inside any nav pin.
  3. Pin-vs-tail order in the fixture source (pin block first, tail last).
  4. Exactly-once PASS-line invariant: print sites per arm.
  5. Allowlist + required_stderr wiring, floor-gate wiring, final verdict shape.
  6. Insertion-only diff for run_battery.py in 77d2f7e.
"""
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys

SEAT = pathlib.Path(__file__).resolve().parent.parent
REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FROZEN = SEAT / "run_battery.committed-77d2f7e.py"
FIXTURE = SEAT / "nav_lattice.committed-77d2f7e.gd"
OUT = SEAT / "static_audit.json"

TAIL_FIELDS = [
    "settle=", "iter=", "ladder=", "first_reach=", "first_reach_sync=",
    "walk_steps=", "reached_at=", "first_reachable=", "iter_b=",
    "link_iter=", "gate=", "chg_iter_same=", "chg_iter_settled=",
    "dis_same=", "fwd_disabled_same=", "settle_a=", "settle_b=",
]


def load_cases(src):
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("CASES not found")


def main():
    src = FROZEN.read_text()
    cases = load_cases(src)
    names = [c[0] for c in cases]
    nav = [c for c in cases if c[0].startswith("nav_lattice_")]
    rep = {"cases": len(cases), "nav_rows": len(nav),
           "nav_names": [c[0] for c in nav], "findings": []}

    # 1. ordering: nav rows contiguous, immediately after r90_lattice_lag,
    #    before the crash/descendant tail.
    idx = [names.index(c[0]) for c in nav]
    rep["nav_indices"] = idx
    rep["contiguous"] = idx == list(range(idx[0], idx[0] + len(idx)))
    rep["prev_row"] = names[idx[0] - 1]
    rep["next_row"] = names[idx[-1] + 1]
    rep["inserted_after_r90_lag"] = names[idx[0] - 1] == "r90_lattice_lag"
    rep["tail_rows_after"] = names[idx[-1] + 1: idx[-1] + 5]
    if not (rep["contiguous"] and rep["inserted_after_r90_lag"]):
        rep["findings"].append("nav rows are not a contiguous block after r90_lattice_lag")
    if rep["next_row"] != "crash_spontaneous_sigabrt":
        rep["findings"].append("nav block does not sit directly ahead of the crash tail")

    # 2. no scheduler/race tail field as a token inside any nav pin.
    rep["pin_tail_violations"] = []
    for name, script, flags, exit_, sig in nav:
        toks = sig.split()
        for t in toks:
            for f in TAIL_FIELDS:
                if t.startswith(f):
                    rep["pin_tail_violations"].append({"case": name, "token": t, "field": f})
    if rep["pin_tail_violations"]:
        rep["findings"].append("scheduler/race field inside a pin")

    # 3. pin-vs-tail order in the fixture source: for each arm, the first
    #    tail field in the print argument sequence must come after the last
    #    pinned token. We approximate by locating the arm's print call and
    #    scanning its string literals in order.
    fixture = FIXTURE.read_text()
    print_calls = {}
    for m in re.finditer(r'print\("PASS nav_lattice (\w+) "', fixture):
        arm = m.group(1)
        # take the balanced call text from this print to the matching close
        i = m.start()
        depth = 0
        j = i
        while j < len(fixture):
            if fixture[j] == "(":
                depth += 1
            elif fixture[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        print_calls[arm] = fixture[i:j + 1]
    rep["print_call_arms"] = sorted(print_calls)
    rep["pin_tail_order"] = {}
    for name, script, flags, exit_, sig in nav:
        arm = flags[0].split("=")[1] if flags else "?"
        call = print_calls.get(arm)
        if call is None:
            rep["pin_tail_order"][name] = "NO_PRINT_CALL"
            continue
        lits = re.findall(r'"((?:[^"\\]|\\.)*)"', call)
        # field names of the string literals, in print order (strip the
        # leading space and trailing '='); expression args carry no literal.
        lit_fields = []
        for lit in lits:
            s = lit.strip()
            if s.endswith("="):
                lit_fields.append(s[:-1])
        tail_pos = None
        for k, f in enumerate(lit_fields):
            if any(f == t[:-1] for t in TAIL_FIELDS):
                tail_pos = k
                break
        # contiguity: every literal field from tail_pos onward is a tail field
        tail_contiguous = (tail_pos is not None
                           and all(any(f == t[:-1] for t in TAIL_FIELDS)
                                   for f in lit_fields[tail_pos:]))
        # signature field sequence must be a prefix of the print field sequence
        sig_fields = []
        for t in sig.split():
            if "=" in t:
                sig_fields.append(t.split("=", 1)[0])
        prefix_ok = lit_fields[:len(sig_fields)] == sig_fields
        rep["pin_tail_order"][name] = {
            "first_tail_literal_index": tail_pos,
            "n_literal_fields": len(lit_fields),
            "tail_contiguous_to_end": tail_contiguous,
            "sig_fields": len(sig_fields),
            "sig_is_print_prefix": prefix_ok,
            "lit_fields_after_pin": lit_fields[len(sig_fields):len(sig_fields) + 4],
        }
        # informational only: literal-field extraction is lossy for
        # multi-field literals; the runtime check (line.startswith(sig)) is
        # the decisive prefix test.
        if tail_pos is not None and not tail_contiguous:
            rep["findings"].append(f"{name}: tail fields not contiguous at end")
    # 4. exactly-once PASS-line: enumerate print sites in the fixture.
    rep["print_sites"] = [
        {"line": fixture[:m.start()].count("\n") + 1,
         "text": fixture[m.start():m.start() + 90].splitlines()[0]}
        for m in re.finditer(r'print\(', fixture)]
    rep["print_site_count"] = len(rep["print_sites"])
    rep["pass_lattice_print_sites"] = sum(
        1 for m in re.finditer(r'print\("PASS nav_lattice', fixture))
    rep["stale_print_sites"] = sum(
        1 for m in re.finditer(r'print\("STALE nav_lattice', fixture))
    rep["quit_call"] = re.findall(r'quit\(([^)]*)\)', fixture)

    # 5. allowlist / required_stderr / floor gate wiring.
    rep["allow_entries"] = {
        "nav_lattice_sync": "'ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.'" in src,
        "nav_lattice_bake": "'ERROR: The root node needs to be inside the SceneTree.'" in src,
        "teardown_crash": "'double free or corruption'," in src,
    }
    rep["floor_gate_present"] = 'r91_expected_errors_all_matched' in src
    rep["floor_gate_covers_prefix"] = 'r["case"].startswith("nav_lattice_")' in src
    rep["floor_gate_in_sf"] = bool(re.search(
        r'sf_discriminations = \{', src)) and 'r91_expected_errors_all_matched": all(' in src
    rep["sf_meta_all"] = 'sf_meta_ok = all(sf_discriminations.values())' in src
    rep["final_verdict_all"] = 'if all(r["verdict"] == "PASS" for r in results)' in src
    # classifier signature clause: substring over merged output
    rep["classifier_merged_substring"] = 'signature in output' in src
    rep["required_stderr_anchor"] = 'any(sig in proc_stdout for sig in sigs)' in src

    # 6. insertion-only diff for run_battery.py in 77d2f7e.
    diff = subprocess.run(["git", "-C", str(REPO), "show", "--numstat", "77d2f7e",
                           "--", "corpus/fixtures/run_battery.py"],
                          capture_output=True, text=True).stdout.strip()
    rep["run_battery_numstat"] = diff
    added, deleted = (diff.split("\t")[:2] if diff else ("?", "?"))
    rep["insertion_only"] = deleted == "0"

    # meta row count: 258 total rows - 251 cases
    rep["expected_result_rows"] = len(cases) + 7

    OUT.write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps(rep, indent=2))
    return 0 if not rep["findings"] else 1


if __name__ == "__main__":
    sys.exit(main())
