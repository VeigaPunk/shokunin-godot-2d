#!/usr/bin/env python3
"""r103 seat V8 — review probe for the C2 receipt-shape meta-gate design.

Answers, with measured bytes:
  Q1 pure function of records?   (AST scan + import side-effect scan + determinism,
                                  cross-run replay of frozen tables)
  Q2 fail-closed?                (field-corruption mutants)
  Q3 false positives on green?   (replay r102 run1 + run2 through both predicates)
  Q4 evasion coverage?           (mut05's 12 evasion rows + mut09's A1/A2/A3 shapes)

Read-only over the repo; never runs run_battery.py. Writes summary JSON to
/var/tmp/r103c-V8/review_out.json.
"""
import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GATE = REPO / "reports/round-103/mutations/r103-ver8-gate_proto.py"
RUNS = {
    "run1": REPO / "corpus/live/runs/20261018T212500022987Z/verdicts.json",
    "run2": REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json",
}
MUT5 = REPO / "reports/round-103/mutations/mut05_gate_evasion.py"
MUT5_JSON = Path("/var/tmp/r103-mut5/evasions.json")
OUT = Path("/var/tmp/r103c-V8/review_out.json")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def group(flags):
    g = {}
    for f in flags:
        g.setdefault(f["reason"], []).append(f)
    return {k: {"n": len(v), "cases": sorted({x["case"] for x in v})[:8]} for k, v in g.items()}


def q1_purity(gate_path):
    src = gate_path.read_text()
    tree = ast.parse(src)
    imports, forbidden, top = [], [], []
    forbidden_names = {"open", "exec", "eval", "compile", "__import__", "input"}
    forbidden_mods = {"subprocess", "os", "socket", "time", "datetime", "random",
                      "pathlib", "shutil", "requests", "urllib", "tempfile",
                      "sqlite3", "http", "ctypes", "multiprocessing", "threading"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module or ""])
            imports.extend(names)
            for n in names:
                if n.split(".")[0] in forbidden_mods:
                    forbidden.append("import:" + n)
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id in forbidden_names:
                forbidden.append("call:" + fn.id)
            if isinstance(fn, ast.Attribute):
                base = fn.value
                root = base.id if isinstance(base, ast.Name) else None
                if root in forbidden_mods:
                    forbidden.append("call:%s.%s" % (root, fn.attr))
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign,
                                 ast.AnnAssign, ast.FunctionDef, ast.Expr)):
            top.append(type(node).__name__)
        if isinstance(node, ast.Expr) and not isinstance(node.value, ast.Constant):
            top.append("Expr:" + type(node.value).__name__)
    mod = load_module(gate_path, "gate_purity")
    rows = json.loads(RUNS["run1"].read_bytes())["results"]
    a = json.dumps(mod.receipt_shape_gate(rows), sort_keys=True)
    b = json.dumps(mod.receipt_shape_gate(copy.deepcopy(rows)), sort_keys=True)
    return {"imports": sorted(set(imports)), "forbidden": forbidden,
            "nontrivial_top_level": top, "determinism_sha": sha_text(a) == sha_text(b),
            "flags_run1": len(json.loads(a))}


def q2_fail_closed(mod):
    rows = json.loads(RUNS["run2"].read_bytes())["results"]
    base = next(r for r in rows if r["case"] == "input_route")
    cases = {}
    r = copy.deepcopy(base); del r["output"]
    cases["missing-output-key"] = r
    r = copy.deepcopy(base); r["output"] = None
    cases["output-is-none"] = r
    r = copy.deepcopy(base); r["output"] = "PASS route=x"
    cases["output-not-a-list"] = r
    r = copy.deepcopy(base); r["output"] = [b"PASS route=x"]
    cases["output-line-not-str"] = r
    r = copy.deepcopy(base); del r["case"]
    cases["missing-case"] = r
    r = copy.deepcopy(base); r["verdict"] = None
    cases["missing-verdict"] = r
    cases["record-not-a-dict"] = "row-as-string"
    r = copy.deepcopy(base); r["output"] = []
    cases["empty-output (green class)"] = r
    r = copy.deepcopy(base); r["output"] = list(r["output"]) + ["FOREIGN_EXTRA injected=x"]
    cases["foreign-line-appended"] = r
    r = copy.deepcopy(base); o = list(r["output"]); b = o.pop(0); o.insert(3, b); r["output"] = o
    cases["banner-moved-to-idx3"] = r
    r = copy.deepcopy(base); r["output"] = list(r["output"]) + ["PASS forged=true"]
    cases["pass-line-forged"] = r
    res = {}
    for k, row in cases.items():
        res[k] = mod.receipt_shape_gate([row])
    return res


def q3_green(mod, min_fn, rows):
    rec = mod.receipt_shape_gate(rows)
    mn = min_fn(rows)
    return {"rows": len(rows), "rec_flags": len(rec), "rec_groups": group(rec),
            "min_flags": len(mn), "min_groups": group(mn)}


def q4_evasions(mod, min_fn):
    if not MUT5_JSON.exists():
        subprocess.run([sys.executable, str(MUT5), "--emit-only"], check=True,
                       capture_output=True)
    payload = json.loads(MUT5_JSON.read_text())
    ev = payload["evasions"]
    ctrl = payload["green_controls"]
    out = {}
    for variant, fn in (("rec", mod.receipt_shape_gate), ("min", min_fn)):
        caught, missed = [], []
        for e in ev:
            flags = fn([e["row"]])
            (caught if flags else missed).append({"name": e["name"],
                                                  "reasons": sorted({f["reason"] for f in flags})})
        ctrl_flags = {c["name"]: fn([c["row"]]) for c in ctrl}
        out[variant] = {"caught": caught, "missed": missed,
                        "green_control_flags": {k: len(v) for k, v in ctrl_flags.items()}}
    return payload, out


def q5_mut09_replay(mod, min_fn):
    rows = json.loads(RUNS["run2"].read_bytes())["results"]
    res = {}
    for base_case in ("export_launch_embed_boot", "r100b_seq_clean"):
        base = next(r for r in rows if r["case"] == base_case)
        o = list(base["output"])
        pin_idx = [i for i, l in enumerate(o) if l.startswith("PASS")]
        mid = pin_idx[0] + 1 if len(pin_idx) > 1 else pin_idx[0]
        shapes = {
            "A1_in_span": (mid, "FOREIGN_EXTRA injected=into_span"),
            "A2_post_span": (len(o), "FOREIGN_EXTRA injected=post_span"),
            "A3_pre_span": (0, "FOREIGN_EXTRA injected=pre_span"),
        }
        per = {"_pin_line_indices": pin_idx}
        for name, (idx, line) in shapes.items():
            r = copy.deepcopy(base)
            out = list(r["output"]); out.insert(idx, line); r["output"] = out
            per[name] = {"rec": mod.receipt_shape_gate([r]),
                         "min": min_fn([r])}
        res[base_case] = per
    return res


def main():
    mod = load_module(GATE, "gate_review")
    min_fn = mod.v_min_span_gate
    min_shim_dir = Path("/var/tmp/r103c-V8")
    min_shim_dir.mkdir(exist_ok=True)
    (min_shim_dir / "r103_ver8_gate_proto.py").write_text(GATE.read_text())
    (min_shim_dir / "vmin_shim.py").write_text(
        "from r103_ver8_gate_proto import v_min_span_gate as receipt_shape_gate\n")
    out = {"gate_sha256": hashlib.sha256(GATE.read_bytes()).hexdigest(),
           "gate_bytes": GATE.stat().st_size}
    out["q1_purity"] = q1_purity(GATE)
    out["q2_fail_closed"] = q2_fail_closed(mod)
    for name, path in RUNS.items():
        runs = json.loads(path.read_bytes())["results"]
        out.setdefault("q3_green", {})[name] = q3_green(mod, min_fn, runs)
    ev_payload, ev_out = q4_evasions(mod, min_fn)
    out["q4_evasions"] = ev_out
    out["q4_run_sha"] = ev_payload["run_sha256"]
    out["q5_mut09_replay"] = q5_mut09_replay(mod, min_fn)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("gate:", out["gate_sha256"][:16], out["gate_bytes"], "bytes ->", OUT)
    print("Q1 purity:", json.dumps(out["q1_purity"]))
    print("Q2 fail-closed:")
    for k, v in out["q2_fail_closed"].items():
        print("   %-28s flags=%d %s" % (k, len(v), [f["reason"] for f in v]))
    print("Q3 green replay:")
    for k, v in out["q3_green"].items():
        print("   %s rows=%d  V-rec flags=%d %s | V-min flags=%d %s" %
              (k, v["rows"], v["rec_flags"], list(v["rec_groups"]),
               v["min_flags"], list(v["min_groups"])))
    print("Q4 evasions (mut05):")
    for variant in ("rec", "min"):
        v = out["q4_evasions"][variant]
        print("   %s caught=%d/%d missed=%s" % (variant, len(v["caught"]),
              len(v["caught"]) + len(v["missed"]),
              [m["name"] for m in v["missed"]]))
        print("      green-control flags:", v["green_control_flags"])
    print("Q5 mut09 replay:")
    for base_case, per in out["q5_mut09_replay"].items():
        print("   base=%s pin-line indices=%s" % (base_case, per["_pin_line_indices"][:6]))
        for k in ("A1_in_span", "A2_post_span", "A3_pre_span"):
            v = per[k]
            print("      %-12s rec=%s min=%s" % (k, [f["reason"] for f in v["rec"]],
                                                 [f["reason"] for f in v["min"]]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
