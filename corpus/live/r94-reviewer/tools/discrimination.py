#!/usr/bin/env python3
"""r94 reviewer: forge-rejection (discrimination) on the 19 r94 rows.

Uses the production classifier extracted verbatim from the PINNED harness and
the committed pins.  For every row and every receipt rep:

  genuine       -> must ACCEPT
  pin_dropped   -> reject
  digit_flipped -> reject (first digit inside the pin flipped 0<->1, else 2<->3)
  bool_flipped  -> reject (first `=true` -> `=false` inside the pin)
  stderr_only   -> reject (pin moved from stdout to stderr)
  wrong_rc      -> reject (rc + 1)
  foreign_error -> reject (foreign `ERROR:` line appended to merged output)
  truncated     -> reject (stdout cut mid-pin)
  prefix_spoof  -> reject (a longer line containing the pin + extra token):
                   DECLARED ACCEPTED by the substring-anchored production
                   classifier (pre-existing battery property, recorded as an
                   observation, not counted as a defect)
"""
import argparse
import ast
import hashlib
import json
import re
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEWER = HERE.parent
PINNED = REVIEWER / "pinned-tmp"


def extract_classifier(p):
    src = p.read_text()
    tree = ast.parse(src)
    fn = [n for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef) and n.name == "classify_process"][0]
    seg = ast.get_source_segment(src, fn)
    ns = {}
    exec(textwrap.dedent(seg), ns)
    return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()


def load_cases(p):
    t = ast.parse(p.read_text())
    for node in t.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "CASES":
            return [ast.literal_eval(e) for e in node.value.elts]


def mutate_digit(pin):
    m = re.search(r"[0-9]", pin)
    if not m:
        return None
    i = m.start()
    d = pin[i]
    n = "1" if d == "0" else "0" if d == "1" else "3" if d == "2" else "2"
    return pin[:i] + n + pin[i + 1:]


def mutate_bool(pin):
    return pin.replace("=true", "=false", 1) if "=true" in pin else (
        pin.replace("=false", "=true", 1) if "=false" in pin else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", type=Path, required=True, help="fresh run dir (with receipts/ and fresh.json)")
    ap.add_argument("--out", type=Path, default=REVIEWER / "discrimination.json")
    args = ap.parse_args()

    classify, seg_sha = extract_classifier(PINNED / "run_battery.py")
    cases = load_cases(PINNED / "run_battery.py")
    r94 = [c for c in cases if c[0].startswith("r94_")]
    fresh = json.loads((args.fresh / "fresh.json").read_text())
    by_case = {r["case"]: r for r in fresh["rows"]}

    report = {"segment_sha256": seg_sha, "fresh": str(args.fresh), "rows": []}
    for name, script, flags, expected_exit, sig in r94:
        rec = by_case[name]
        rep = rec["reps"][0]
        so = (args.fresh / "receipts" / f"{name}.rep{rep['rep']}.out").read_text()
        se = (args.fresh / "receipts" / f"{name}.rep{rep['rep']}.err").read_text()
        rc = rep["rc"]
        row = {"case": name, "pin_len": len(sig), "rc": rc,
               "stderr_bytes": rep["stderr_bytes"], "mutations": {}}
        base_ok = classify(rc, None, so + se, expected_exit, sig, ())
        row["genuine_accept"] = base_ok
        stderr_only_stdout = so.replace(sig, "", 1)
        muts = {
            "pin_dropped": (rc, None, so.replace(sig, "", 1) + se),
            "stderr_only": (rc, None, stderr_only_stdout + se + "\n" + sig + "\n"),
            "wrong_rc": (rc + 1, None, so + se),
            "foreign_error": (rc, None, so + se + "\nERROR: foreign injected diagnostic\n"),
            "truncated_mid_pin": (rc, None, so[:so.index(sig) + max(1, len(sig) // 2)] + se),
            "prefix_spoof": (rc, None, so.replace(sig, sig + " spoof=1", 1) + se),
        }
        d = mutate_digit(sig)
        if d:
            muts["digit_flipped"] = (rc, None, so.replace(sig, d, 1) + se)
        b = mutate_bool(sig)
        if b:
            muts["bool_flipped"] = (rc, None, so.replace(sig, b, 1) + se)
        for k, (c, e, out) in muts.items():
            row["mutations"][k] = classify(c, e, out, expected_exit, sig, ())
        # r93-reviewer-style stricter harness: production's merged-blob
        # classifier accepts a PASS line delivered on stderr; a stdout anchor
        # (the shape r89-fold added for required_stderr rows only) rejects it.
        row["stderr_only_stdout_anchored"] = (
            row["mutations"]["stderr_only"] is True and sig not in stderr_only_stdout)
        report["rows"].append(row)

    # summary
    names = ["pin_dropped", "digit_flipped", "bool_flipped", "stderr_only", "wrong_rc",
             "foreign_error", "truncated_mid_pin"]
    summ = {}
    for k in names:
        tested = [r for r in report["rows"] if k in r["mutations"]]
        rejected = [r for r in tested if r["mutations"][k] is False]
        summ[k] = {"tested": len(tested), "rejected": len(rejected),
                   "accepted": [r["case"] for r in tested if r["mutations"][k] is True]}
    summ["genuine"] = {"tested": len(report["rows"]),
                       "accepted": sum(1 for r in report["rows"] if r["genuine_accept"]),
                       "rejected": [r["case"] for r in report["rows"] if not r["genuine_accept"]]}
    summ["stderr_only_stdout_anchored"] = {
        "tested": len(report["rows"]),
        "rejected": sum(1 for r in report["rows"] if r["stderr_only_stdout_anchored"]),
        "note": "stricter-than-production stdout anchor (r93-reviewer shape)"}
    summ["prefix_spoof"] = {"tested": len(report["rows"]),
                            "accepted": sum(1 for r in report["rows"] if r["mutations"]["prefix_spoof"]),
                            "declared": "substring-anchored production classifier accepts trailing tokens"}
    report["summary"] = summ
    args.out.write_text(json.dumps(report, indent=1))
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
