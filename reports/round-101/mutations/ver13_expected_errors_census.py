#!/usr/bin/env python3
"""VER-13 (r101) — expected_errors expansion census probe.

Read-only on the lane repo. Extracts the REAL `classify_process` closure
(run_battery.py:1725, an inner function of main()) via AST + exec, then
classifies VER-13's own captured probe receipts under the lane's existing
allowlist shapes and under proposed entries for the export refusal classes.
Also statically censuses CASES names vs expected_errors dict keys vs the
per-round dead-entry gates, and demonstrates the C2 full-transcript pin.

Usage: python3 ver13_expected_errors_census.py
Writes: reports/round-101/mutations/ver13_census_out.json (next to this file).
"""
import ast
import hashlib
import json
import re
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
HARNESS = REPO / "corpus" / "fixtures" / "run_battery.py"
PROBES = Path("/var/tmp/r101-ver13/probes")
OUT = HERE / "ver13_census_out.json"

SRC = HARNESS.read_text()


def extract_classify_process(src):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            fn_src = textwrap.dedent(ast.get_source_segment(src, node))
            ns = {}
            exec(compile(fn_src, "<classify_process-extracted>", "exec"), ns)
            return ns["classify_process"], fn_src
    raise SystemExit("classify_process not found")


def extract_cases(src):
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", "") == "CASES" for t in node.targets):
            out = []
            for elt in node.value.elts:
                if isinstance(elt, ast.Tuple) and len(elt.elts) >= 5:
                    name, script, exit_code, evidence = (elt.elts[0], elt.elts[1],
                                                         elt.elts[3], elt.elts[4])
                    if (isinstance(name, ast.Constant)
                            and isinstance(script, ast.Constant)):
                        out.append({"name": name.value, "script": script.value,
                                    "exit": exit_code.value
                                    if isinstance(exit_code, ast.Constant) else None,
                                    "evidence": evidence.value
                                    if isinstance(evidence, ast.Constant) else None})
            return out
    raise SystemExit("CASES not found")


def extract_dict_and_enclosing_test(src):
    tree = ast.parse(src)
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def chain(node):
        seen = []
        cur = node
        while cur in parents:
            cur = parents[cur]
            seen.append(cur)
        return seen

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", "") == "expected_errors" for t in node.targets):
            val = node.value
            if (isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute)
                    and val.func.attr == "get" and isinstance(val.func.value, ast.Dict)):
                keys = [k.value for k in val.func.value.keys if isinstance(k, ast.Constant)]
                enclosing = [type(p).__name__ for p in chain(node)]
                ifs = [p for p in chain(node) if isinstance(p, ast.If)]
                tests = [ast.unparse(p.test) for p in ifs]
                return keys, node.lineno, enclosing, tests
    raise SystemExit("expected_errors dict not found")


GATE_RE = re.compile(r'"([a-z0-9_]+_expected_errors_all_matched)"')


def extract_gates(src):
    gates = {}
    for m in GATE_RE.finditer(src):
        chunk = src[m.end():m.end() + 400]
        m2 = re.search(r"startswith\(\((.*?)\)\)", chunk, re.S)
        if m2:
            prefixes = re.findall(r'"([^"]+)"', m2.group(1))
        else:
            m3 = re.search(r'startswith\("([^"]+)"\)', chunk)
            prefixes = [m3.group(1)] if m3 else []
        gates[m.group(1)] = prefixes
    m = re.search(r'"cases_integrity"', src)
    chunk = src[m.end():m.end() + 700]
    m2 = re.search(r"for p in \((.*?)\)\)", chunk, re.S)
    gates["cases_integrity(existence)"] = re.findall(r'"([^"]+)"', m2.group(1)) if m2 else []
    return gates


def blob(name):
    return ((PROBES / f"{name}.stdout").read_text()
            + (PROBES / f"{name}.stderr").read_text())


def digest(name):
    d = {}
    for stream in ("stdout", "stderr"):
        p = PROBES / f"{name}.{stream}"
        d[stream] = {"bytes": p.stat().st_size,
                     "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    return d


classify_process, FN_SRC = extract_classify_process(SRC)
cases = extract_cases(SRC)
keys, dict_line, enclosing, if_tests = extract_dict_and_enclosing_test(SRC)
gates = extract_gates(SRC)

case_by_name = {c["name"]: {"script": c["script"], "evidence": c["evidence"]}
                for c in cases}
inline_shadowed = [c["name"] for c in cases
                   if str(c["script"]).startswith("__godot_export")]

gate_prefixes = {}
for g, pfx in gates.items():
    for p in pfx:
        gate_prefixes.setdefault(p, []).append(g)
entry_bearing = [k for k in keys if k in case_by_name]
uncovered = [n for n in entry_bearing
             if not any(n.startswith(p) for p in gate_prefixes)]

EV = 'ERROR: Invalid export preset name: Missing preset.'
E1 = 'ERROR: Cannot export project with preset "Linux/X11" due to configuration errors:'
E2 = 'ERROR: Project export for preset "Linux/X11" failed.'
T = 'ERROR: Parameter "t" is null.'
SIG_UP = "No export preset 'Missing preset' found"
SIG_CURSOR = case_by_name["r100b_seq_clean"]["evidence"]

seq_lines = (PROBES / "seq-clean.stdout").read_text().splitlines()
sig_full = "\n".join(seq_lines[2:16])
forged_lines = list(seq_lines)
forged_lines.insert(5, "FORGED_EXTRA_CELL_OUTPUT")
forged_blob = "\n".join(forged_lines) + "\n" + (PROBES / "seq-clean.stderr").read_text()
clean_blob = blob("seq-clean")

A = blob("unknown-preset")
B = blob("tmpl-missing")
E = blob("celloff")
tmpl_detail = [ln for ln in B.splitlines() if "export_templates" in ln]

cells = [
    ("A_unknown_preset_inline_evidence_accepts",
     classify_process(1, None, A, 1, EV, (EV,)), True),
    ("A_unknown_preset_bare_rejects",
     classify_process(1, None, A, 1, EV, ()), False),
    ("A_unknown_preset_cases_signature_absent_from_capture",
     SIG_UP in A, False),
    ("A_unknown_preset_foreign_line_rejects",
     classify_process(1, None, A + "\nERROR: forged unrelated\n", 1, EV, (EV,)), False),
    ("B_templates_missing_two_entries_accept",
     classify_process(1, None, B, 1, E2, (E1, E2)), True),
    ("B_templates_missing_bare_rejects",
     classify_process(1, None, B, 1, E2, ()), False),
    ("B_templates_missing_single_entry_rejects",
     classify_process(1, None, B, 1, E2, (E1,)), False),
    ("B_templates_missing_foreign_line_rejects",
     classify_process(1, None, B + "\nERROR: forged unrelated\n", 1, E2, (E1, E2)), False),
    ("B_detail_lines_error_inert",
     all("ERROR:" not in ln for ln in tmpl_detail) and len(tmpl_detail) == 2, True),
    ("B_stderr_error_line_count_is_2",
     len([ln for ln in B.splitlines() if "ERROR:" in ln]), 2),
    ("D1_seq_clean_allowlisted_accepts",
     classify_process(0, None, clean_blob, 0, SIG_CURSOR, (T,)), True),
    ("D1_seq_clean_bare_rejects",
     classify_process(0, None, clean_blob, 0, SIG_CURSOR, ()), False),
    ("D1_seq_full_transcript_pin_accepts_clean",
     classify_process(0, None, clean_blob, 0, sig_full, (T,)), True),
    ("D1_seq_full_transcript_pin_rejects_forged_extra_line",
     classify_process(0, None, forged_blob, 0, sig_full, (T,)), False),
    ("F2_current_single_line_pin_accepts_forge",
     classify_process(0, None, forged_blob, 0, SIG_CURSOR, (T,)), True),
    ("E_celloff_no_error_lines",
     len([ln for ln in E.splitlines() if "ERROR:" in ln]), 0),
    ("E_celloff_clean_classifies_with_empty_allowlist",
     classify_process(0, None, E, 0, "PASS r95b_order celloff", ()), True),
]

matrix = [{"cell": name, "expected": exp, "actual": act, "ok": act == exp}
          for name, act, exp in cells]

payload = {
    "repo_harness": str(HARNESS),
    "harness_sha256": hashlib.sha256(HARNESS.read_bytes()).hexdigest(),
    "classify_process_extracted_lineno": 1725,
    "classify_process_source_sha256": hashlib.sha256(FN_SRC.encode()).hexdigest(),
    "expected_errors_dict_declared_at_line": dict_line,
    "expected_errors_enclosed_by": {"ifs": if_tests, "gates_directly": enclosing[:6]},
    "expected_errors_key_count": len(keys),
    "cases_row_count": len(cases),
    "keys_not_in_cases": [k for k in keys if k not in case_by_name],
    "export_rows_inline_shadowed": inline_shadowed,
    "entry_bearing_cases": len(entry_bearing),
    "entry_bearing_uncovered_by_any_dead_entry_gate": uncovered,
    "gate_prefixes": gates,
    "classifier_matrix": matrix,
    "all_cells_ok": all(m["ok"] for m in matrix),
    "receipts": {name: digest(name) for name in
                 ("unknown-preset", "unknown-preset-r2", "tmpl-missing",
                  "tmpl-missing-r2", "tmpl-missing-debug", "ctrl-release",
                  "seq-clean", "seq-noclean", "celloff")},
    "seq_full_signature_lines": len(sig_full.splitlines()),
    "tmpl_detail_lines": tmpl_detail,
}

OUT.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps({k: payload[k] for k in (
    "expected_errors_key_count", "cases_row_count", "keys_not_in_cases",
    "export_rows_inline_shadowed", "entry_bearing_uncovered_by_any_dead_entry_gate",
    "all_cells_ok")}, indent=2))
fails = [m for m in matrix if not m["ok"]]
print(f"matrix: {len(matrix)} cells, {len(fails)} mismatches")
for m in fails:
    print("  MISMATCH:", m)
print(f"wrote {OUT}")
