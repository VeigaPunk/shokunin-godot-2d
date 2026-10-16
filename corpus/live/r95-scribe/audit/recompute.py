#!/usr/bin/env python3
"""r95-scribe mutant test — production classify_process vs landed pins.

Extracts classify_process verbatim from HEAD:corpus/fixtures/run_battery.py
(AST + unparse), then on one real landed receipt per r95 row:
  baseline                -> must PASS
  signature mutants       -> must reject (numeric / boolean / appended conjunct)
  pinned-region output    -> must reject (numeric / boolean flips inside the
                             located signature span)
Read-only.
"""
import ast
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LANE = REPO / "corpus/live/r95-scribe"
OUT = LANE / "audit/recompute.json"


def committed_battery_src():
    return subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"],
                          cwd=REPO, capture_output=True, text=True).stdout


def extract_classifier(src):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(src, node)
            return seg, ast.unparse(node)
    raise SystemExit("classify_process not found")


def r95_cases(src):
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CASES":
                    vals = [tuple(ast.literal_eval(e) for e in c.elts) for c in node.value.elts]
                    return [v for v in vals
                            if str(v[0]).startswith(("dss_lattice_", "r95b_order_"))]
    raise SystemExit("no CASES")


src = committed_battery_src()
seg, unparsed = extract_classifier(src)
ns = {}
exec(unparsed, ns)
classify = ns["classify_process"]
seg_sha = __import__("hashlib").sha256(seg.encode()).hexdigest()

cases = r95_cases(src)

# one real receipt per row: prefer scribe fresh receipts, else scribe battery,
# else the author's latest green battery run
receipts = {}
for p in sorted((LANE / "fresh").glob("*.out")):
    case = p.name.split(".")[0]
    receipts.setdefault(case, p.read_text(errors="replace"))
for vf in sorted((LANE / "battery-runs").glob("*/verdicts.json")) + \
        sorted((LANE / "battery-committed").glob("*/verdicts.json")):
    v = json.loads(vf.read_text())
    for r in v["results"]:
        if str(r.get("case", "")).startswith(("dss_lattice_", "r95b_order_")):
            receipts.setdefault(r["case"], "\n".join(r.get("output") or []))
vf = REPO / "corpus/live/runs/20261016T065922894811Z/verdicts.json"
v = json.loads(vf.read_text())
for r in v["results"]:
    if str(r.get("case", "")).startswith(("dss_lattice_", "r95b_order_")):
        receipts.setdefault(r["case"], "\n".join(r.get("output") or []))

NUM = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?)(?![\w.])")
BOOL = re.compile(r"\b(true|false)\b")


def sig_numeric_mutants(sig):
    out = []
    for m in NUM.finditer(sig):
        tok = m.group(1)
        if tok in ("0", "1"):
            rep = "2"
        else:
            rep = str(int(float(tok)) + 1) if "." not in tok else f"{float(tok) + 1:.4f}"
        out.append(sig[:m.start(1)] + rep + sig[m.end(1):])
    return out


def sig_bool_mutants(sig):
    out = []
    for m in BOOL.finditer(sig):
        rep = "false" if m.group(1) == "true" else "true"
        out.append(sig[:m.start(1)] + rep + sig[m.end(1):])
    return out


def sig_append_mutants(sig):
    return [sig + " extra=1", sig + " ok=false", sig + " n=999"]


def output_mutants(text, sig):
    """Flip tokens INSIDE the located signature span only."""
    i = text.find(sig)
    if i < 0:
        return []
    span = text[i:i + len(sig)]
    outs = []
    for m in list(NUM.finditer(span))[:40]:
        tok = m.group(1)
        if tok in ("0", "1"):
            rep = "2"
        else:
            rep = str(int(float(tok)) + 1) if "." not in tok else f"{float(tok) + 1:.4f}"
        outs.append(text[:i] + span[:m.start(1)] + rep + span[m.end(1):] + text[i + len(sig):])
    for m in list(BOOL.finditer(span))[:40]:
        rep = "false" if m.group(1) == "true" else "true"
        outs.append(text[:i] + span[:m.start(1)] + rep + span[m.end(1):] + text[i + len(sig):])
    return outs


report = {
    "classifier_segment_sha256": seg_sha,
    "classifier_segment_lines": len(seg.splitlines()),
    "rows": len(cases),
    "receipts_available": len(receipts),
    "baseline_pass": 0,
    "baseline_fail": [],
    "sig_mutants": 0, "sig_rejected": 0,
    "sig_mutants_per_row": {},
    "output_mutants": 0, "output_rejected": 0,
    "output_mutants_per_row": {},
    "sig_accepted_examples": [],
    "output_accepted_examples": [],
}

for case, script, flags, exit_code, sig in cases:
    text = receipts.get(case)
    if text is None:
        report["baseline_fail"].append({"case": case, "why": "no receipt"})
        continue
    ok = classify(exit_code, None, text, exit_code, sig, ())
    if ok:
        report["baseline_pass"] += 1
    else:
        report["baseline_fail"].append({"case": case, "why": "baseline reject"})
    sm = sig_numeric_mutants(sig) + sig_bool_mutants(sig) + sig_append_mutants(sig)
    rejected = sum(1 for m in sm if not classify(exit_code, None, text, exit_code, m, ()))
    report["sig_mutants"] += len(sm)
    report["sig_rejected"] += rejected
    report["sig_mutants_per_row"][case] = [len(sm), rejected]
    for m in sm:
        if classify(exit_code, None, text, exit_code, m, ()):
            report["sig_accepted_examples"].append({"case": case, "mutant": m[:120]})
    om = output_mutants(text, sig)
    o_rej = sum(1 for t in om if not classify(exit_code, None, t, exit_code, sig, ()))
    report["output_mutants"] += len(om)
    report["output_rejected"] += o_rej
    report["output_mutants_per_row"][case] = [len(om), o_rej]
    for t in om:
        if classify(exit_code, None, t, exit_code, sig, ()):
            report["output_accepted_examples"].append({"case": case})

OUT.write_text(json.dumps(report, indent=2, sort_keys=True))
print(json.dumps({k: v for k, v in report.items()
                  if not k.endswith("per_row") and "examples" not in k}, indent=2))
print("sig accepted examples:", len(report["sig_accepted_examples"]))
print("output accepted examples:", len(report["output_accepted_examples"]))
