#!/usr/bin/env python3
"""r89-critic analyzer."""
import ast, hashlib, pathlib, sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
BATTERY = REPO / "corpus/fixtures/run_battery.py"
RUNS = pathlib.Path(__file__).parent / "runs"

def load_cases():
    src = BATTERY.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("CASES not found")

def extract_classifier():
    src = BATTERY.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("def classify_process" + seg.split("def classify_process", 1)[1], ns)
            return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit("classify_process not found")

EXPECTED_ERRORS = {
    "geo2d_lattice_atlasempty": ('ERROR: Condition "p_rects.is_empty()" is true.',),
    "geo2d_lattice_polyendpoly": ("ERROR: Attempt to offset a polyline like a polygon (use offset_polygon instead).",),
}
MODE_Q = "just_after_flush=w_jp[ex=false inex=true]"
MODE_L = "just_after_flush=w_jp[ex=false inex=false]"

def main():
    cases = load_cases()
    cls, sha = extract_classifier()
    r89 = [c for c in cases if c[0].startswith(("geo2d_lattice_", "input89_edges_"))]
    print(f"classifier sha={sha[:12]} cases_total={len(cases)} r89_rows={len(r89)}")
    tag = sys.argv[1] if len(sys.argv) > 1 else "load"
    for name, script, flags, exit_, sig in r89:
        arm = flags[0].split("=")[1]
        reps = sorted(RUNS.glob(f"{script}.{arm}.{tag}.rep*.out"))
        modes = {"Q":0,"L":0,"?":0}
        uniq_out, uniq_err, rcs, pass_n = set(), set(), [], 0
        sig_src = set()
        other_lines = set()
        for o in reps:
            k = o.name.rsplit(".rep",1)[1].split(".")[0]
            base = f"{script}.{arm}.{tag}.rep{k}"
            out = o.read_text(); err = (RUNS / f"{base}.err").read_text()
            rc = int((RUNS / f"{base}.rc").read_text().strip())
            code = -(rc-128) if rc > 128 else rc
            uniq_out.add(out); uniq_err.add(err); rcs.append(rc)
            merged = out + err
            sigs = sig if isinstance(sig, tuple) else (sig,)
            allowed = EXPECTED_ERRORS.get(name, ())
            ok = any(cls(code, None, merged, exit_, s, allowed) for s in sigs)
            pass_n += ok
            for s in sigs:
                if s in out: sig_src.add("stdout")
                elif s in err: sig_src.add("stderr")
                elif s in merged: sig_src.add("merged-only")
                else: sig_src.add("ABSENT")
            if name == "input89_edges_exact":
                line = next((ln for ln in out.splitlines() if ln.startswith("PASS input89_edges exact")), None)
                if line is None: modes["?"] += 1; continue
                if MODE_Q in line: modes["Q"] += 1
                elif MODE_L in line: modes["L"] += 1
                else:
                    modes["?"] += 1
                    other_lines.add(line)
        extra = f" modes={modes}" if name == "input89_edges_exact" else ""
        print(f"{name:34s} reps={len(reps)} out_uniq={len(uniq_out)} err_uniq={len(uniq_err)} rc={sorted(set(rcs))} classified_PASS={pass_n}/{len(reps)} sig_src={sorted(sig_src)}{extra}")
        for ln in other_lines:
            print(f"    THIRD-MODE LINE: {ln}")

if __name__ == "__main__":
    main()
