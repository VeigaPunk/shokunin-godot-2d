#!/usr/bin/env python3
"""r94-critic arm receipt verifier: rc/stderr/signature/wall per batch."""
import ast, glob, json, os, sys, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # corpus/live/r94-critic
HARNESS = "/tmp/r94crit-frozen/corpus/fixtures/run_battery.py"

def signatures():
    src = open(HARNESS).read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "CASES":
            return {e.elts[0].value: e.elts[4].value
                    for e in node.value.elts
                    if e.elts[0].value.startswith("r94_")}
    raise SystemExit("CASES not found")

def main():
    sigs = signatures()
    batches = sys.argv[1:] or ["fresh"]
    report = {}
    for batch in batches:
        d = os.path.join(ROOT, "runs", batch)
        rows = {}
        for arm in sorted(sigs):
            stem = arm.removeprefix("r94_particles_")
            recs = []
            for f in sorted(glob.glob(os.path.join(d, stem + ".rep*.out")),
                            key=lambda p: int(p.rsplit(".rep", 1)[1].split(".")[0])):
                base = f[:-4]
                out = open(f, errors="replace").read()
                err = open(base + ".err", errors="replace").read()
                rc = int(open(base + ".rc").read().strip())
                wall = float(open(base + ".wall").read().strip())
                lines = [l for l in out.splitlines() if l.startswith("PASS particles_lattice")]
                ok_line = lines[0] if lines else None
                recs.append({
                    "receipt": os.path.relpath(base, ROOT),
                    "rc": rc, "stderr_bytes": len(err.encode()),
                    "signature_present": sigs[arm] in out,
                    "line_startswith_signature": bool(ok_line and ok_line.startswith(sigs[arm])),
                    "pass_line": ok_line, "wall": wall,
                })
            rows[arm] = {
                "n": len(recs),
                "all_rc0": all(r["rc"] == 0 for r in recs),
                "all_stderr0": all(r["stderr_bytes"] == 0 for r in recs),
                "all_sig": all(r["signature_present"] for r in recs),
                "all_prefix": all(r["line_startswith_signature"] for r in recs),
                "walls": [r["wall"] for r in recs],
                "max_wall": max((r["wall"] for r in recs), default=None),
                "distinct_pass_lines": sorted({r["pass_line"] for r in recs if r["pass_line"]}),
                "receipts": recs,
            }
        report[batch] = rows
        bad = {a: r for a, r in rows.items()
               if not (r["all_rc0"] and r["all_stderr0"] and r["all_sig"])}
        print(f"== batch {batch}: {len(rows)} arms, "
              f"{sum(r['n'] for r in rows.values())} receipts; "
              f"rc/stderr/sig failures: {len(bad)}")
        for a, r in rows.items():
            print(f"  {a:26s} n={r['n']} rc0={r['all_rc0']} stderr0={r['all_stderr0']} "
                  f"sig={r['all_sig']} prefix={r['all_prefix']} maxwall={r['max_wall']:.3f}s")
            if not (r["all_rc0"] and r["all_stderr0"] and r["all_sig"]):
                for rec in r["receipts"]:
                    if not (rec["rc"] == 0 and rec["stderr_bytes"] == 0 and rec["signature_present"]):
                        print("    BAD:", rec["receipt"], rec["rc"], rec["stderr_bytes"],
                              rec["signature_present"])
            if r["distinct_pass_lines"] and len(r["distinct_pass_lines"]) > 1:
                for pl in r["distinct_pass_lines"]:
                    print("    mode:", pl)
    json.dump(report, open(os.path.join(ROOT, "scripts",
              "verify_" + "_".join(batches) + ".json"), "w"), indent=2)

if __name__ == "__main__":
    main()
