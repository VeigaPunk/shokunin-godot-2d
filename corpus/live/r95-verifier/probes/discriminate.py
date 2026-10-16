#!/usr/bin/env python3
"""Discrimination: would a broken law actually fail the row?

For each of the 52 r95 rows, take the fresh rep1 receipt that classifies PASS,
mutate pinned tokens, re-classify with the production classifier.

Axes:
  - rc flip, injected unrelated ERROR, injected SCRIPT ERROR, Parse Error
  - signature deletion
  - sampled token mutations inside the signature (bool/int/float) — each must reject
  - tail controls: (a) junk appended after the signature (substring semantics),
    (b) for the 4 head-prefix rows, mutation of the *unpinned* tail region
    (the order vector) — must be ADMITTED (that is the deliberate cut).
"""
import ast
import importlib.util
import json
import re
import sys
from pathlib import Path

FIX = Path(sys.argv[1])
VDIR = Path(sys.argv[2])

spec = importlib.util.spec_from_file_location("frozen_run_battery", FIX / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
cases = {c[0]: c for c in mod.CASES if c[0].startswith(("dss_lattice_", "r95b_order_"))}

src = (FIX / "run_battery.py").read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        cls_src = ast.get_source_segment(src, node)
ns = {}
exec(cls_src, ns)
classify_process = ns["classify_process"]

BOOL_RE = re.compile(r"\b(true|false)\b")
INT_RE = re.compile(r"(?<![\d.])-?\d+(?![\d.])")
FLOAT_RE = re.compile(r"-?\d+\.\d+")

def mutate_bool(tok):
    return "false" if tok == "true" else "true"

def mutate_int(tok):
    return str(int(tok) + 1)

def mutate_float(tok):
    head, dot, frac = tok.partition(".")
    last = frac[-1]
    new_last = str((int(last) + 1) % 10)
    return head + dot + frac[:-1] + new_last

results = []
for name, case in sorted(cases.items()):
    expected_exit, sig = case[3], case[4]
    base_out = (VDIR / "arms" / f"{name}.rep1.out").read_text()
    base_err = (VDIR / "arms" / f"{name}.rep1.err").read_text()
    base_rc = int((VDIR / "arms" / f"{name}.rep1.rc").read_text().strip())
    base_merged = base_out + base_err
    lines = base_merged.splitlines()
    matched = next((l for l in lines if sig in l), None)
    assert matched is not None, name
    row = {"case": name, "axes": {}}

    def classify(code, merged, allowed=()):
        return classify_process(code, None, merged, expected_exit, sig, allowed)

    assert classify(base_rc, base_merged), name
    row["baseline_pass"] = True

    # rc flip
    row["axes"]["rc_flip"] = not classify(base_rc + 1, base_merged)
    # injected unrelated ERROR line
    row["axes"]["inject_error"] = not classify(base_rc, base_merged + "\nERROR: unrelated injected diagnostic\n")
    # SCRIPT ERROR / Parse Error
    row["axes"]["inject_script_error"] = not classify(base_rc, base_merged + "\nSCRIPT ERROR: injected\n")
    row["axes"]["inject_parse_error"] = not classify(base_rc, base_merged + "\nParse Error: injected\n")
    # signature deletion (drop the matched line)
    deleted = "\n".join(l for l in lines if l is not matched)
    row["axes"]["signature_deleted"] = not classify(base_rc, deleted)

    # sampled token mutations inside the signature
    tokens = []
    sig_only = sig
    for m in BOOL_RE.finditer(sig_only):
        tokens.append(("bool", m.group(0), m.start(), mutate_bool))
    for m in INT_RE.finditer(sig_only):
        tokens.append(("int", m.group(0), m.start(), mutate_int))
    for m in FLOAT_RE.finditer(sig_only):
        tokens.append(("float", m.group(0), m.start(), mutate_float))
    picks = []
    if tokens:
        picks.append(tokens[0])
        picks.append(tokens[len(tokens) // 2])
        picks.append(tokens[-1])
    if len(tokens) >= 5:
        picks.append(tokens[1])
    # letter-token mutation: the last alphabetic char in the signature
    # (covers rows whose signature carries no numeric/bool token)
    letters = [i for i, ch in enumerate(sig) if ch.isalpha()]
    if letters:
        pos = letters[-1]
        picks.append(("letter", sig[pos], pos, lambda t: "z" if t != "z" else "q"))
    mutations = []
    for kind, tok, pos, fn in picks:
        new_tok = fn(tok)
        if new_tok == tok:
            continue
        mutated_sig = sig[:pos] + new_tok + sig[pos + len(tok):]
        mutated_line = matched.replace(sig, mutated_sig, 1)
        mutated = "\n".join(mutated_line if l is matched else l for l in lines)
        ok = classify(base_rc, mutated)
        mutations.append({"kind": kind, "from": tok, "to": new_tok,
                          "rejected": not ok})
    row["axes"]["token_mutations"] = mutations
    row["axes"]["token_mutations_all_reject"] = all(m["rejected"] for m in mutations)

    # tail control (a): junk appended after the signature on its line
    tail_junk_line = matched + " EXTRA_JUNK=1"
    tail_junk = "\n".join(tail_junk_line if l is matched else l for l in lines)
    row["axes"]["tail_junk_admitted"] = classify(base_rc, tail_junk)

    # tail control (b): prefix rows — mutate the unpinned region beyond the sig
    row["axes"]["prefix_tail_mutation"] = None
    if len(matched) > len(sig):
        tail = matched[len(sig):]
        mut_tail = re.sub(r"[a-z0-9]", lambda m: "z" if m.group(0) != "z" else "y", tail, count=1)
        mut_line = matched[:len(sig)] + mut_tail
        mutated = "\n".join(mut_line if l is matched else l for l in lines)
        row["axes"]["prefix_tail_mutation"] = {
            "tail_len": len(tail), "admitted": classify(base_rc, mutated)}
    results.append(row)

summary = {
    "rows": len(results),
    "rc_flip_rejects": sum(r["axes"]["rc_flip"] for r in results),
    "inject_error_rejects": sum(r["axes"]["inject_error"] for r in results),
    "inject_script_error_rejects": sum(r["axes"]["inject_script_error"] for r in results),
    "inject_parse_error_rejects": sum(r["axes"]["inject_parse_error"] for r in results),
    "signature_deleted_rejects": sum(r["axes"]["signature_deleted"] for r in results),
    "token_mutations_total": sum(len(r["axes"]["token_mutations"]) for r in results),
    "token_mutations_rejected": sum(m["rejected"] for r in results for m in r["axes"]["token_mutations"]),
    "rows_with_token_mutation_gap": [r["case"] for r in results
                                     if not r["axes"]["token_mutations_all_reject"]],
    "tail_junk_admitted_rows": sum(r["axes"]["tail_junk_admitted"] for r in results),
    "prefix_tail_controls": {r["case"]: r["axes"]["prefix_tail_mutation"] for r in results
                             if r["axes"]["prefix_tail_mutation"] is not None},
    "detail": results,
}
(VDIR / "probes" / "discrimination.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: v for k, v in summary.items() if k != "detail"}, indent=2))
