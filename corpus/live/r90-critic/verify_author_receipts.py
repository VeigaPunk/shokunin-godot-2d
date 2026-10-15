#!/usr/bin/env python3
"""r90-critic: re-derive the author's per-arm 6-rep byte-stability from their own
receipts (corpus/live/r90-author/runs/<arm>.rep<k>.{out,err,rc}).

This is an independent replay of the author's claim '12/12 cells: out_uniq=1
err_uniq=1, constant rc, sig_hit=6/6' using the production classifier.
"""
import ast
import hashlib
import pathlib

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FROZEN = pathlib.Path(__file__).parent / "run_battery.committed-ee20575.py"
BATTERY = FROZEN if FROZEN.is_file() else REPO / "corpus/fixtures/run_battery.py"
AUTHOR_RUNS = REPO / "corpus/live/r90-author/runs"


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


ALLOW = {
    "r90_lattice_comrefuse": ('ERROR: Condition "center_of_mass_mode != CENTER_OF_MASS_MODE_CUSTOM" is true.',),
    "r90_lattice_impedge": ('ERROR: Condition "p_inertia < 0" is true.',
                            'ERROR: Condition "p_mass <= 0" is true.'),
}


def main():
    cases = load_cases()
    cls, sha = extract_classifier()
    print(f"classifier_segment_sha256={sha}")
    for name, script, flags, exit_, sig in [c for c in cases if c[0].startswith("r90_")]:
        arm = flags[0].split("=")[1]
        outs, errs, rcs, sig_hits, pin_eq = set(), set(), [], 0, 0
        reps = sorted(AUTHOR_RUNS.glob(f"{arm}.rep*.out"))
        for o in reps:
            k = o.name.rsplit(".rep", 1)[1].split(".")[0]
            out = o.read_text()
            err = (AUTHOR_RUNS / f"{arm}.rep{k}.err").read_text()
            rc = int((AUTHOR_RUNS / f"{arm}.rep{k}.rc").read_text().strip())
            code = -(rc - 128) if rc > 128 else rc
            outs.add(out)
            errs.add(err)
            rcs.append(rc)
            sig_hits += (sig in out)
            pin_eq += any(ln == sig for ln in out.splitlines())
            ok = cls(code, None, out + err, exit_, sig, ALLOW.get(name, ()))
            assert ok, f"{name} rep{k} classified FAIL"
        print(f"{name:24s} reps={len(reps)} out_uniq={len(outs)} err_uniq={len(errs)} "
              f"rc={sorted(set(rcs))} sig_hit={sig_hits}/{len(reps)} pin_byteeq={pin_eq}/{len(reps)} "
              f"classified=all-PASS")


if __name__ == "__main__":
    main()
