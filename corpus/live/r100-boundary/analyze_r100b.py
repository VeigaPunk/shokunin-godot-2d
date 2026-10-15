#!/usr/bin/env python3
"""r100-boundary analyzer.

Sections:
  1. per-mode per-cell receipt census (reps / out_uniq / pass_uniq / err_uniq / rc)
  2. cross-mode payload portability (one distinct PASS line per cell across modes?)
  3. byte-replay check against the frozen r100-scout receipts (quiet rep1 vs scout rep1)
  4. production `classify_process` (AST-extracted from corpus/fixtures/run_battery.py)
     over EVERY receipt in every mode, using the scout's own ROWS
  5. artifact-probe census (per arm per mode) + cross-mode payload sets
  6. same-process sequencing (r100b_seq) per-cell comparison against the fresh-process line
"""
import ast
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
CELLS = ["census", "routing", "hover", "motion", "localpos", "cursor", "clip",
         "drag", "touch", "subvp", "warp", "focus", "render", "osmeta"]
MODES = ["quiet", "load", "ff30", "ff60", "ff120", "thr", "ff1"]
PROBE_ARMS = ["cursorphase", "hoverphase", "dragphase", "coalesce", "velphase",
              "startup", "flushpos", "orderin", "dblclick", "seq_noclean", "seq_clean"]
SCOUT = HERE.parent / "r100-scout"
FIXTURE = HERE.parent.parent / "fixtures" / "run_battery.py"


def pass_line(text, prefix="PASS "):
    for ln in text.splitlines():
        if ln.startswith(prefix):
            return ln
    return None


def read_receipt(out):
    err = out.with_suffix(".err")
    rc = out.with_suffix(".rc")
    return (out.read_text(),
            err.read_text() if err.exists() else "",
            rc.read_text().strip() if rc.exists() else "?")


# ---------------------------------------------------------------- 1/2 matrix
matrix = {}
for mode in MODES:
    per = {}
    for cell in CELLS:
        outs = sorted((HERE / "runs" / mode).glob(f"r100b_gui_{cell}.rep*.out"))
        if not outs:
            continue
        texts, errs, rcs, passes = set(), set(), set(), set()
        for out in outs:
            t, e, rc = read_receipt(out)
            texts.add(t)
            errs.add(e)
            rcs.add(rc)
            pl = pass_line(t, "PASS r100_gui ")
            if pl:
                passes.add(pl)
        per[cell] = {
            "reps": len(outs), "out_uniq": len(texts), "pass_uniq": len(passes),
            "err_uniq": len(errs), "rc": sorted(rcs),
            "pass_line": sorted(passes)[0] if len(passes) == 1 else None,
        }
    matrix[mode] = per

# cross-mode portability
portable = {}
for cell in CELLS:
    lines = {}
    for mode in MODES:
        d = matrix.get(mode, {}).get(cell)
        if d:
            lines[mode] = d["pass_line"]
    distinct = sorted({v for v in lines.values() if v is not None})
    portable[cell] = {
        "modes": sorted(lines),
        "pass_uniq": len(distinct),
        "portable": len(distinct) == 1 and len(lines) == len([m for m in MODES if m in lines]),
        "pass_line": distinct[0] if len(distinct) == 1 else None,
        "diff_modes": sorted(m for m, v in lines.items() if len(distinct) > 1 and v != distinct[0]),
    }

# ---------------------------------------------------------------- 3 replay vs scout
replay = {}
for cell in CELLS:
    scout_out = SCOUT / "runs" / f"r100_gui_{cell}.rep1.out"
    mine = HERE / "runs" / "quiet" / f"r100b_gui_{cell}.rep1.out"
    if not scout_out.exists() or not mine.exists():
        continue
    s_txt, s_err, s_rc = read_receipt(scout_out)
    m_txt, m_err, m_rc = read_receipt(mine)
    replay[cell] = {
        "stdout_equal": s_txt == m_txt,
        "stderr_equal": s_err == m_err,
        "pass_equal": pass_line(s_txt, "PASS r100_gui ") == pass_line(m_txt, "PASS r100_gui "),
        "scout_rc": s_rc, "mine_rc": m_rc,
    }

# ---------------------------------------------------------------- 4 classifier
src = FIXTURE.read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src, "classify_process not found"
seg_sha = __import__("hashlib").sha256(fn_src.encode()).hexdigest()
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

rows_ns = {}
exec((SCOUT / "author-rows.py.txt").read_text(), rows_ns)
ROWS = rows_ns["ROWS"]
EXPECTED = rows_ns.get("EXPECTED_ERRORS", {})

classifier = {"segment_sha256": seg_sha, "checked": 0, "rejected": [], "per_mode": {}}
for mode in MODES:
    per_mode_rejects = []
    for case, _script, _flags, expected_exit, sig in ROWS:
        cell = case[len("r100_gui_"):]
        allowed = EXPECTED.get(case, ())
        for out in sorted((HERE / "runs" / mode).glob(f"r100b_gui_{cell}.rep*.out")):
            t, e, rc = read_receipt(out)
            code = int(rc) if rc.isdigit() else None
            classifier["checked"] += 1
            if not classify_process(code, None, t + e, expected_exit, sig, allowed):
                classifier["rejected"].append([case, mode, out.name])
                per_mode_rejects.append([case, out.name])
    classifier["per_mode"][mode] = per_mode_rejects

# ---------------------------------------------------------------- 5 probes
probes = {}
for mode in MODES:
    per = {}
    for arm in PROBE_ARMS:
        outs = sorted((HERE / "runs" / "probes" / mode).glob(f"r100b_{arm}.rep*.out"))
        if not outs:
            continue
        texts, errs, rcs, passes = set(), set(), set(), set()
        for out in outs:
            t, e, rc = read_receipt(out)
            texts.add(t)
            errs.add(e)
            rcs.add(rc)
            pl = pass_line(t, "PASS r100b_phase ")
            if pl:
                passes.add(pl)
        per[arm] = {
            "reps": len(outs), "out_uniq": len(texts), "err_uniq": len(errs),
            "rc": sorted(rcs),
            "pass_lines": sorted(passes),
        }
    probes[mode] = per

# cross-mode probe payloads
probe_cross = {}
for arm in PROBE_ARMS:
    lines = {}
    for mode in MODES:
        d = probes.get(mode, {}).get(arm)
        if d and len(d["pass_lines"]) == 1:
            lines[mode] = d["pass_lines"][0]
    probe_cross[arm] = {
        "modes": sorted(lines),
        "pass_uniq": len(set(lines.values())),
        "pass_lines": {m: v for m, v in sorted(lines.items())},
    }

# ---------------------------------------------------------------- 6 seq vs fresh
seq = {}
ref = {}
for cell in CELLS:
    d = matrix.get("quiet", {}).get(cell)
    if d and d["pass_line"]:
        ref[cell] = d["pass_line"]
for variant in ("seq_noclean", "seq_clean"):
    per_mode = {}
    for mode in MODES:
        outs = sorted((HERE / "runs" / "probes" / mode).glob(f"r100b_{variant}.rep*.out"))
        if not outs:
            continue
        matches = {}
        first_diff = None
        for out in outs:
            t, _e, _rc = read_receipt(out)
            got = {}
            for ln in t.splitlines():
                if ln.startswith("PASS r100_gui "):
                    got[ln.split()[2]] = ln
            for cell in CELLS:
                ok = cell in got and cell in ref and got[cell] == ref[cell]
                matches.setdefault(cell, []).append(bool(ok))
                if not ok and first_diff is None:
                    first_diff = [cell, out.name]
        per_mode[mode] = {
            "receipts": len(outs),
            "cells_matching_all_receipts": sorted(c for c, v in matches.items() if all(v)),
            "cells_diverging": sorted(c for c, v in matches.items() if not all(v)),
            "first_divergence": first_diff,
        }
    seq[variant] = per_mode

out = {
    "matrix": matrix,
    "portability": portable,
    "replay_vs_scout": replay,
    "classifier": classifier,
    "probes": probes,
    "probe_cross_mode": probe_cross,
    "seq_vs_fresh": seq,
}
(HERE / "runs" / "analyze_r100b.json").write_text(json.dumps(out, indent=2) + "\n")

lines = []
lines.append("## 1/2 matrix census + cross-mode portability")
for mode in MODES:
    unstable = [c for c, d in matrix.get(mode, {}).items()
                if not (d["out_uniq"] == 1 and d["pass_uniq"] == 1 and d["err_uniq"] == 1 and d["rc"] == ["0"])]
    cells = len(matrix.get(mode, {}))
    lines.append(f"[{mode}] cells={cells} UNSTABLE={unstable}")
for cell in CELLS:
    p = portable.get(cell, {})
    lines.append(f"portable {cell:9s} modes={len(p.get('modes', []))} pass_uniq={p.get('pass_uniq')} "
                 f"portable={p.get('portable')} diff_modes={p.get('diff_modes')}")
lines.append("")
lines.append("## 3 replay vs scout")
for cell in CELLS:
    r = replay.get(cell, {})
    lines.append(f"replay {cell:9s} stdout_eq={r.get('stdout_equal')} stderr_eq={r.get('stderr_equal')} "
                 f"pass_eq={r.get('pass_equal')} rc={r.get('scout_rc')}->{r.get('mine_rc')}")
lines.append("")
lines.append(f"## 4 classifier segment={seg_sha[:16]} checked={classifier['checked']} "
             f"rejected={len(classifier['rejected'])}")
for mode, rej in classifier["per_mode"].items():
    lines.append(f"classifier [{mode}] rejects={rej}")
lines.append("")
lines.append("## 5 probe census")
for mode in MODES:
    for arm, d in probes.get(mode, {}).items():
        unstable = "" if (d["out_uniq"] == 1 and d["err_uniq"] == 1 and d["rc"] == ["0"]) else "  <-- UNSTABLE"
        lines.append(f"[{mode}] {arm:12s} reps={d['reps']} out_uniq={d['out_uniq']} "
                     f"err_uniq={d['err_uniq']} rc={d['rc']} pass_uniq={len(d['pass_lines'])}{unstable}")
lines.append("")
lines.append("## 5b probe cross-mode")
for arm, d in probe_cross.items():
    lines.append(f"probe {arm:12s} modes={len(d['modes'])} pass_uniq={d['pass_uniq']}")
    if d["pass_uniq"] > 1:
        for m, v in d["pass_lines"].items():
            lines.append(f"    {m}: {v}")
lines.append("")
lines.append("## 6 seq vs fresh")
for variant, per_mode in seq.items():
    for mode, d in per_mode.items():
        lines.append(f"[{variant} {mode}] receipts={d['receipts']} "
                     f"match_all={d['cells_matching_all_receipts']} "
                     f"diverge={d['cells_diverging']} first={d['first_divergence']}")
(HERE / "runs" / "analyze_r100b.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
