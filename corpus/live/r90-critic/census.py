#!/usr/bin/env python3
"""r90-critic: reproduce the battery's expected_errors dead-entry census and the
r90_expected_errors_all_matched discrimination from seat-owned receipts.

usage: census.py <tag>
"""
import ast
import hashlib
import pathlib
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FROZEN = pathlib.Path(__file__).parent / "run_battery.committed-ee20575.py"
BATTERY = FROZEN if FROZEN.is_file() else REPO / "corpus/fixtures/run_battery.py"
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


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "load"
    cases = load_cases()
    cls, sha = extract_classifier()
    allow = {
        "r90_lattice_comrefuse": ('ERROR: Condition "center_of_mass_mode != CENTER_OF_MASS_MODE_CUSTOM" is true.',),
        "r90_lattice_impedge": ('ERROR: Condition "p_inertia < 0" is true.',
                                'ERROR: Condition "p_mass <= 0" is true.'),
    }
    gate = True
    for name, script, flags, exit_, sig in [c for c in cases if c[0].startswith("r90_")]:
        entries = allow.get(name, ())
        if not entries:
            continue
        arm = flags[0].split("=")[1]
        reps = sorted(RUNS.glob(f"{tag}.{arm}.rep*.out"))
        if not reps:
            continue
        for o in reps:
            k = o.name.rsplit(".rep", 1)[1].split(".")[0]
            base = RUNS / f"{tag}.{arm}.rep{k}"
            out = o.read_text()
            err = (RUNS / f"{base}.err").read_text()
            merged = out + err
            rc = int((RUNS / f"{base}.rc").read_text().strip())
            code = -(rc - 128) if rc > 128 else rc
            bare_passes = cls(code, None, merged, exit_, sig, ())
            allow_p = cls(code, None, merged, exit_, sig, tuple(entries))
            counts = {}
            for e in entries:
                counts[e] = sum(1 for ln in merged.splitlines() if ln.strip() == e)
            dead = [e for e in entries if counts[e] == 0]
            gate = gate and not dead
            print(f"{tag} {name} rep{k}: bare_classification_passes={bare_passes} "
                  f"(production bare_rejects={not bare_passes}) allowlisted_passes={allow_p} "
                  f"matched={ {e.split('\"')[1][:28]: c for e, c in counts.items()} } "
                  f"dead={len(dead)}")
    print(f"r90_expected_errors_all_matched={gate} (recomputed over {tag} receipts; classifier_sha={sha[:12]})")


if __name__ == "__main__":
    main()
