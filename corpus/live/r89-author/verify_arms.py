#!/usr/bin/env python3
"""r89-author pre-landing verification:
  * per-cell uniq of (stdout, stderr, rc) across fresh reps
  * every claimed row signature appears byte-for-byte in rep output
  * classify with the production classify_process extracted verbatim
    (same AST-extraction procedure as r89-scout verify_rows.py)
  * input89_edges_exact: report per-rep mode (Q quiet / L loaded / other)
"""
import ast
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent.parent.parent
BATTERY = REPO / "corpus" / "fixtures" / "run_battery.py"
RUNS = HERE / "runs"
SCOUT = REPO / "corpus" / "live" / "r89-scout" / "author-rows.py.txt"

EXPECTED_ERRORS = {
    "geo2d_lattice_atlasempty": ('ERROR: Condition "p_rects.is_empty()" is true.',),
    "geo2d_lattice_polyendpoly": ("ERROR: Attempt to offset a polyline like a polygon (use offset_polygon instead).",
                                  ),
}

MODE_Q_TOKEN = "just_after_flush=w_jp[ex=false inex=true]"
MODE_L_TOKEN = "just_after_flush=w_jp[ex=false inex=false]"


def load_rows():
    ns = {}
    lines = SCOUT.read_text().split("# expected_errors additions")[0].splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("    (") and not ln.lstrip().startswith("#"))
    end = max(i for i, ln in enumerate(lines) if ln.rstrip().endswith("),"))
    body = "\n".join(ln for ln in lines[start:end + 1] if not ln.lstrip().startswith("#"))
    exec("ROWS = [\n" + body + "\n]", ns)
    return ns["ROWS"]


def extract_classifier():
    src = BATTERY.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("def classify_process" + seg.split("def classify_process", 1)[1], ns)
            return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit("classify_process not found")


def cell_of(script, flags):
    pref = {"input89_edges.gd": "in_"}.get(script, "geo_")
    return pref + flags[0].split("=")[1]


def main() -> int:
    rows = load_rows()
    classifier, seg_sha = extract_classifier()
    print(f"classifier segment sha256 {seg_sha[:16]}… rows={len(rows)}")
    bad = []
    unstable = []
    for case, script, flags, exit_, sig in rows:
        cell = cell_of(script, flags)
        reps = sorted(RUNS.glob(f"{cell}.rep*.out"))
        outs, errs, rcs, sig_hit, modes = set(), set(), [], 0, {"Q": 0, "L": 0, "?": 0}
        classified_ok = 0
        for o in reps:
            k = o.stem.split("rep")[1]
            out = o.read_text()
            err = (RUNS / f"{cell}.rep{k}.err").read_text()
            rc = int((RUNS / f"{cell}.rep{k}.rc").read_text().strip())
            code = -(rc - 128) if rc > 128 else rc
            outs.add(out)
            errs.add(err)
            rcs.append(rc)
            allowed = EXPECTED_ERRORS.get(case, ())
            if sig in (out + err):
                sig_hit += 1
            if classifier(code, None, out + err, exit_, sig, allowed):
                classified_ok += 1
            if case == "input89_edges_exact":
                if MODE_Q_TOKEN in out:
                    modes["Q"] += 1
                elif MODE_L_TOKEN in out:
                    modes["L"] += 1
                else:
                    modes["?"] += 1
        repn = len(reps)
        status = "OK " if (len(outs) == 1 and len(errs) == 1 and sig_hit == repn and classified_ok == repn) else "BAD"
        mode_str = f" modes={modes}" if case == "input89_edges_exact" else ""
        print(f"{status} {case:34s} reps={repn} out_uniq={len(outs)} err_uniq={len(errs)} "
              f"rc={sorted(set(rcs))} sig_hit={sig_hit}/{repn} classified={classified_ok}/{repn}{mode_str}")
        if status == "BAD":
            bad.append(case)
        if len(outs) != 1 or len(errs) != 1:
            unstable.append(case)
    print(f"\nrows={len(rows)} bad={bad} unstable={unstable}")
    return 1 if bad or unstable else 0


if __name__ == "__main__":
    sys.exit(main())
