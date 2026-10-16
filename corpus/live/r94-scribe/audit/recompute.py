#!/usr/bin/env python3
"""r94 scribe — landed-row mutant test + dossier claim recompute.

Part A: extract the PRODUCTION `classify_process` verbatim from HEAD
(`git show HEAD:corpus/fixtures/run_battery.py`), then for each of the 19 landed
r94 rows:
  (a) signature mutants  — every numeric token (+1), every boolean flip, appended
      never-emitted conjuncts: each must be REJECTED on a real receipt of the arm;
  (b) output mutants     — flip a pinned boolean / numeric token inside the
      receipt's pinned region: must also be REJECTED with the original signature.

Part B: recompute the three dossiers' headline numbers from receipts on disk.

Writes corpus/live/r94-scribe/audit/recompute.json.
"""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r94-scribe/audit"

src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"],
                     cwd=REPO, capture_output=True).stdout.decode()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value
rows = {}
for el in cases.elts:
    t = ast.literal_eval(el)
    if t[0].startswith("r94_"):
        rows[t[0]] = {"script": t[1], "flags": t[2], "exit": t[3], "signature": t[4],
                      "arm": t[2][0].split("=", 1)[1]}

# ---- receipts for mutation: prefer scribe fresh (landed bytes) -------------
def find_receipt(arm):
    for d in ("fresh",):
        for f in sorted((REPO / f"corpus/live/r94-scribe/{d}").glob(f"*.{arm}.*.out")):
            rc = f.with_suffix(".rc").read_text().strip()
            err = f.with_suffix(".err").read_text()
            return f, rc, err
    for f in sorted((REPO / "corpus/live/r94-scout/runs").glob(f"r94_particles_{arm}.rep1.out")):
        return f, f.with_suffix(".rc").read_text().strip(), f.with_suffix(".err").read_text()
    raise SystemExit(f"no receipt for {arm}")


NUM_TOKEN = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?)(?![\w.])")
BOOL_TOKEN = re.compile(r"\b(true|false)\b")


def mutants(sig):
    out = []
    for m in NUM_TOKEN.finditer(sig):
        v = m.group(1)
        if "." in v:
            new = f"{float(v) + 1:.4f}"
        else:
            new = str(int(v) + 1)
        out.append(("numeric", sig[:m.start()] + new + sig[m.end():]))
    for m in BOOL_TOKEN.finditer(sig):
        flip = "false" if m.group(1) == "true" else "true"
        out.append(("boolean", sig[:m.start()] + flip + sig[m.end():]))
    for suffix in (" r94_forge=1", " forged=1", " ok2=true"):
        out.append(("append", sig + suffix))
    return out


def output_mutants(arm, text, sig):
    """mutate INSIDE the located pinned region of the receipt: flip each pinned
    boolean and each numeric token of the signature at its exact offset."""
    idx = text.find(sig)
    assert idx >= 0, "signature not found verbatim in receipt"
    out = []
    for m in BOOL_TOKEN.finditer(sig):
        flip = "false" if m.group(1) == "true" else "true"
        out.append(("bool-out", text[:idx + m.start()] + flip + text[idx + m.end():]))
    for m in NUM_TOKEN.finditer(sig):
        v = m.group(1)
        new = f"{float(v) + 1:.4f}" if "." in v else str(int(v) + 1)
        out.append(("num-out", text[:idx + m.start()] + new + text[idx + m.end():]))
    return out


report = {"classify_process_segment_sha256": seg_sha, "rows": {}}
tot = {"sig": 0, "sig_rejected": 0, "out": 0, "out_rejected": 0, "by_kind": {}}
for name, row in rows.items():
    f, rc, err = find_receipt(row["arm"])
    text = f.read_text() + err
    sig = row["signature"]
    ok0 = classify_process(int(rc), None, text, row["exit"], sig, ())
    sig_mut = mutants(sig)
    out_mut = output_mutants(row["arm"], text, sig)
    sig_rej = [k for k, m in sig_mut if not classify_process(int(rc), None, text, row["exit"], m, ())]
    out_rej = [k for k, m in out_mut if not classify_process(int(rc), None, m, row["exit"], sig, ())]
    report["rows"][name] = {
        "receipt": str(f.relative_to(REPO)), "baseline_pass": ok0,
        "sig_mutants": len(sig_mut), "sig_rejected": len(sig_rej),
        "sig_accepted_kinds": sorted({k for k, m in sig_mut
                                      if classify_process(int(rc), None, text, row["exit"], m, ())}),
        "out_mutants": len(out_mut), "out_rejected": len(out_rej),
        "out_accepted_kinds": sorted({k for k, m in out_mut
                                      if classify_process(int(rc), None, m, row["exit"], sig, ())}),
    }
    for k, m in sig_mut:
        tot["sig"] += 1
        tot["by_kind"].setdefault("sig-" + k, [0, 0])[0] += 1
        if not classify_process(int(rc), None, text, row["exit"], m, ()):
            tot["sig_rejected"] += 1
            tot["by_kind"]["sig-" + k][1] += 1
    for k, m in out_mut:
        tot["out"] += 1
        tot["by_kind"].setdefault("out-" + k, [0, 0])[0] += 1
        if not classify_process(int(rc), None, m, row["exit"], sig, ()):
            tot["out_rejected"] += 1
            tot["by_kind"]["out-" + k][1] += 1
report["totals"] = tot
report["baseline_all_pass"] = all(r["baseline_pass"] for r in report["rows"].values())

# ---- Part B: dossier recompute --------------------------------------------
scout = REPO / "corpus/live/r94-scout"
canon = sorted((scout / "runs").glob("r94_particles_*.rep*.out"))
load = sorted((scout / "runs/loadtest").glob("r94_particles_*.rep*.out"))
per_cell = {}
for f in canon:
    arm = re.search(r"r94_particles_(\w+)\.rep", f.name).group(1)
    per_cell.setdefault(arm, []).append(f.read_text())
scout_stats = {"canonical_runs": len(canon), "loadtest_runs": len(load),
               "rc_nonzero": [], "err_nonempty": [],
               "canonical_out_uniq": {k: len(set(v)) for k, v in sorted(per_cell.items())}}
for f in canon + load:
    if f.with_suffix(".rc").read_text().strip() != "0":
        scout_stats["rc_nonzero"].append(f.name)
    if f.with_suffix(".err").read_bytes():
        scout_stats["err_nonempty"].append(f.name)
report["scout_recompute"] = scout_stats

bnd = REPO / "corpus/live/r94-boundary"
batches = {}
for batch in ("quiet", "load", "ff30", "ff60", "ff120", "ff120load", "ab", "reprobe"):
    d = bnd / "runs" / batch
    outs = sorted(d.glob("*.out"))
    rc_bad = [f.name for f in d.glob("*.rc") if f.read_text().strip() != "0"]
    err_bad = [f.name for f in d.glob("*.err") if f.read_bytes()]
    batches[batch] = {"out_files": len(outs), "rc_nonzero": rc_bad, "err_nonempty": err_bad}
report["boundary_recompute"] = batches

(OUT / "recompute.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"segment_sha": seg_sha[:16], "totals": tot,
                  "baseline_all_pass": report["baseline_all_pass"]}, indent=1))
for name, r in report["rows"].items():
    flag = "" if (r["sig_rejected"] == r["sig_mutants"] and r["out_rejected"] == r["out_mutants"]) else "  <-- ACCEPTED MUTANT"
    print(f"{name:32s} sig {r['sig_rejected']}/{r['sig_mutants']} out {r['out_rejected']}/{r['out_mutants']}{flag}")
print("scout:", {k: v for k, v in scout_stats.items() if k != "canonical_out_uniq"})
print("boundary:", json.dumps(batches))
