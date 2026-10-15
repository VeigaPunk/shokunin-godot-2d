#!/usr/bin/env python3
"""r91 reviewer — re-classify nav_lattice receipts with the production classifier.

Usage:
  verify_receipts.py <receipts_dir> [<receipts_dir> ...]

A receipt set is a directory holding files named <arm>.rep<N>.{out,err,rc}
(the author's fresh-reps layout). Each is classified with the production
`classify_process` extracted verbatim from the committed harness (sha
749fa060…), with the per-row expected_errors and required_stderr allowlists
parsed from the committed CASES/allowlist dicts.

Checks per receipt:
  * exit code equals the row's expected_exit
  * signature present (merged blob, as production does)
  * every pinned `required_stderr` fragment present on stderr
  * signature additionally present on stdout (production's stream anchor)
  * no unrelated ERROR: line (production allowlist)
  * PASS line byte-prefix relationship: the pin is a prefix of the PASS line
  * `PASS nav_lattice <arm>` token matches the arm, exactly one PASS line
"""
import ast
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
# Committed bytes pulled straight from the review commit (`git show 77d2f7e:…`),
# so this tool keeps working after the scratch `tree/` extraction is pruned:
#   pinned/run_battery.py sha256 f5725ca441565b8c9903b5e98aeb1112ea5c56a11a1f422b6feb46f904953220
PINNED = HERE.parent / "pinned"
HARNESS = PINNED / "run_battery.py"

sys.path.insert(0, str(HERE))
from classify_process import classify_process  # noqa: E402  (extracted, verbatim)


def _lit(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp):
        return -_lit(node.operand)
    if isinstance(node, (ast.Tuple, ast.List)):
        return tuple(_lit(e) for e in node.elts)
    raise ValueError(ast.dump(node))


def parse_harness(path):
    src = path.read_text()
    tree = ast.parse(src)
    cases = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for e in node.value.elts:
                name = _lit(e.elts[0])
                if name.startswith("nav_lattice_"):
                    cases[name] = {
                        "flags": [_lit(a) for a in e.elts[2].elts],
                        "rc": _lit(e.elts[3]),
                        "sig": _lit(e.elts[4]),
                    }
    # allowlist dicts live inside main(): find the two dict literals keyed by
    # nav_lattice_ names
    expected_errors, required_stderr = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "nav_lattice_sync" in keys:
                for k, v in zip(node.keys, node.values):
                    expected_errors[k.value] = tuple(_lit(v))
            if "nav_lattice_teardown_crash" in keys:
                for k, v in zip(node.keys, node.values):
                    required_stderr[k.value] = tuple(_lit(v))
    return cases, expected_errors, required_stderr


def main(dirs):
    cases, expected_errors, required_stderr = parse_harness(HARNESS)
    print(f"rows parsed: {len(cases)}  ee_keys={sorted(expected_errors)}  rs_keys={sorted(required_stderr)}")
    total = {"pass": 0, "fail": 0, "rows": {}}
    for d in dirs:
        d = pathlib.Path(d)
        for out in sorted(d.glob("*.rep*.out")):
            arm = out.name.split(".rep")[0]
            row = cases.get(f"nav_lattice_{arm}")
            assert row is not None, f"no CASES row for arm {arm}"
            err = out.with_suffix(".err")
            rc = out.with_suffix(".rc")
            stdout = out.read_text()
            stderr = err.read_text()
            code = int(rc.read_text().strip())
            merged = stdout + stderr
            ee = expected_errors.get(f"nav_lattice_{arm}", ())
            rs = required_stderr.get(f"nav_lattice_{arm}", ())
            verdict = classify_process(code, None, merged, row["rc"], row["sig"], ee)
            if rs:
                verdict = verdict and all(f in stderr for f in rs) and row["sig"] in stdout
            lines = [l for l in stdout.splitlines() if l.startswith("PASS nav_lattice")]
            prefix = bool(lines) and lines[0].startswith(row["sig"])
            one_pass = len(lines) == 1
            stale = any(l.startswith("STALE nav_lattice") for l in stdout.splitlines())
            key = f"nav_lattice_{arm}"
            rec = total["rows"].setdefault(key, {"n": 0, "fail": 0, "prefix": True, "onepass": True,
                                                "stale": False, "err_variants": set(), "out_variants": set()})
            rec["n"] += 1
            rec["err_variants"].add(stderr)
            rec["out_variants"].add(stdout)
            rec["prefix"] &= prefix
            rec["onepass"] &= one_pass
            rec["stale"] |= stale
            if verdict:
                total["pass"] += 1
            else:
                total["fail"] += 1
                rec["fail"] += 1
                print(f"  FAIL {key} {out.name}: rc={code} exp={row['rc']} prefix={prefix} onepass={one_pass}")
    print(f"\ntotal receipts classified: {total['pass']} PASS / {total['fail']} FAIL")
    print(f"\n{'row':32s} {'n':>3s} {'fail':>4s} {'prefix':>6s} {'1pass':>5s} {'stale':>5s} {'out_uniq':>8s} {'err_uniq':>8s}")
    for k, r in sorted(total["rows"].items()):
        print(f"{k:32s} {r['n']:3d} {r['fail']:4d} {str(r['prefix']):>6s} {str(r['onepass']):>5s} "
              f"{str(r['stale']):>5s} {len(r['out_variants']):8d} {len(r['err_variants']):8d}")
    json.dump({k: {"n": v["n"], "fail": v["fail"], "prefix": v["prefix"], "onepass": v["onepass"],
                   "stale": v["stale"], "out_uniq": len(v["out_variants"]), "err_uniq": len(v["err_variants"])}
               for k, v in total["rows"].items()},
              open(HERE.parent / "receipt_summary.json", "w"), indent=1)
    return 0 if total["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
