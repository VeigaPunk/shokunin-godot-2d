#!/usr/bin/env python3
"""r90-critic analyzer: production-classifier replay of the r90 rows.

Extracts `classify_process` from the committed corpus/fixtures/run_battery.py
(AST, byte-segment sha recorded) and classifies fresh receipts captured in the
battery's exact launch shape. Also byte-compares each receipt's PASS line with
the committed pin and reports out/err/rc uniqueness.
"""
import ast
import hashlib
import pathlib
import re
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


def expected_errors_map():
    """Parse the per-case allowlist mapping out of the committed source."""
    src = BATTERY.read_text()
    # The r90 entries live in the literal dict passed to .get(name, ()).
    out = {}
    for name in ("r90_lattice_comrefuse", "r90_lattice_impedge"):
        m = re.search(r"'%s': \(\n((?:\s+'.*?',\n)+)\s+\)" % name, src)
        if not m:
            raise SystemExit(f"allowlist for {name} not found")
        out[name] = tuple(re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1)))
    return out


def main():
    cases = load_cases()
    cls, sha = extract_classifier()
    allow = expected_errors_map()
    r90 = [c for c in cases if c[0].startswith("r90_")]
    print(f"classifier_segment_sha256={sha}")
    print(f"cases_total={len(cases)} r90_rows={len(r90)} allowlists={allow}")
    tag = sys.argv[1] if len(sys.argv) > 1 else "load"
    worst = 0
    seen = 0
    for name, script, flags, exit_, sig in r90:
        arm = flags[0].split("=")[1]
        reps = sorted(RUNS.glob(f"{tag}.{arm}.rep*.out"),
                      key=lambda p: int(p.name.rsplit(".rep", 1)[1].split(".")[0]))
        if not reps:
            continue
        seen += 1
        uniq_out, uniq_err, rcs, pass_n, sig_src, pin_eq = set(), set(), [], 0, set(), 0
        lines = {}
        for o in reps:
            k = o.name.rsplit(".rep", 1)[1].split(".")[0]
            base = RUNS / f"{tag}.{arm}.rep{k}"
            out = o.read_text()
            err = (RUNS / f"{base}.err").read_text()
            rc = int((RUNS / f"{base}.rc").read_text().strip())
            code = -(rc - 128) if rc > 128 else rc
            uniq_out.add(out)
            uniq_err.add(err)
            rcs.append(rc)
            merged = out + err
            allowed = allow.get(name, ())
            ok = cls(code, None, merged, exit_, sig, allowed)
            pass_n += ok
            if sig in out:
                sig_src.add("stdout")
            elif sig in err:
                sig_src.add("stderr")
            elif sig in merged:
                sig_src.add("merged-only")
            else:
                sig_src.add("ABSENT")
            got = [ln for ln in out.splitlines() if ln.startswith("PASS r90_lattice ")]
            lines.setdefault(tuple(got), 0)
            lines[tuple(got)] += 1
            if any(ln == sig for ln in out.splitlines()):
                pin_eq += 1
        verdict = "PASS" if pass_n == len(reps) and len(reps) else "FAIL"
        if verdict == "FAIL":
            worst = 1
        print(f"{name:24s} arm={arm:10s} reps={len(reps):2d} out_uniq={len(uniq_out)} "
              f"err_uniq={len(uniq_err)} rc={sorted(set(rcs))} "
              f"classified_PASS={pass_n}/{len(reps)} sig_src={sorted(sig_src)} "
              f"pin_byteeq={pin_eq}/{len(reps)} verdict={verdict}")
        for got, n in lines.items():
            if n and len(got) != 1:
                for ln in got:
                    print(f"    VARIANT({n}x): {ln[:220]}")
    print(f"ANALYZE_TAG={tag} rows_seen={seen} ANALYZE_WORST=" + ("FAIL" if worst else "PASS"))
    return worst


if __name__ == "__main__":
    sys.exit(main())
