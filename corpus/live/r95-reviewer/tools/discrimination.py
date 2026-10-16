#!/usr/bin/env python3
"""r95 reviewer discrimination: forged shapes vs the production classifier.

Uses the fresh receipts of this seat (rep1, load condition) and the committed
pins. Every shape is classified by the production `classify_process` extracted
verbatim from the pinned harness. Shapes that are accepted are reported as
pre-existing classifier properties (substring anchor / merged blob), with the
strict-stream variant recorded alongside.
"""
import ast
import hashlib
import json
import pathlib
import re
import subprocess

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
PINNED = REPO / "corpus/live/r95-reviewer/pinned-tmp/corpus/fixtures"
SEAT = REPO / "corpus/live/r95-reviewer"


def extract(text, name, extra_namespace=None):
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            seg = ast.get_source_segment(text, node)
            ns = dict(extra_namespace or {})
            exec(seg, ns)
            return ns[name], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit(f"{name} not found")


def parse_cases(text):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("CASES not found")


def main():
    harness = (PINNED / "run_battery.py").read_text()
    classify, seg_sha = extract(harness, "classify_process")
    classify_streams, _ = extract(harness, "classify_streams")
    cases = [c for c in parse_cases(harness)
             if c[0].startswith(("dss_lattice_", "r95b_order_"))]

    fresh_dirs = sorted((SEAT / "fresh").iterdir())
    fresh = fresh_dirs[-1]
    out = {"receipts": str(fresh), "classifier_segment_sha256": seg_sha,
           "shapes": {}, "rows": {}}
    shapes = {k: 0 for k in ("genuine_accept", "pin_dropped", "digit_flipped",
                             "bool_flipped", "wrong_rc", "foreign_error",
                             "truncated_mid_pin", "prefix_spoof", "stderr_only",
                             "cross_case_signature", "tail_mutation_inert",
                             "stderr_only_stream_reject", "stdout_carry")}
    rows = {}
    sigs = {c[0]: c[4] for c in cases}
    for case, script, flags, expected_exit, signature in cases:
        out_file = fresh / f"{case}.load.rep1.out"
        err_file = fresh / f"{case}.load.rep1.err"
        if not out_file.exists():
            continue
        text = out_file.read_text()
        err = err_file.read_text()
        rc = int((fresh / f"{case}.load.rep1.rc").read_text().strip())
        r = {}
        r["genuine_accept"] = classify(rc, None, text + err, expected_exit, signature)
        r["stdout_carry"] = signature in text
        r["pin_dropped"] = classify(rc, None, text.replace(signature, "") + err,
                                    expected_exit, signature)
        digits = re.findall(r"\d", signature)
        if digits:
            d = digits[0]
            r["digit_flipped"] = classify(rc, None,
                                          text.replace(d, "7" if d != "7" else "3", 1) + err,
                                          expected_exit, signature)
        if "=true" in signature or "=false" in signature:
            if "=true" in signature:
                forged = signature.replace("=true", "=false", 1)
            else:
                forged = signature.replace("=false", "=true", 1)
            r["bool_flipped"] = classify(rc, None, text.replace(signature, forged) + err,
                                         expected_exit, signature)
        r["wrong_rc"] = classify(rc + 1, None, text + err, expected_exit, signature)
        r["foreign_error"] = classify(rc, None,
                                      text + err + "\nERROR: foreign injected diagnostic",
                                      expected_exit, signature)
        half = signature[: max(1, len(signature) // 2)]
        r["truncated_mid_pin"] = classify(rc, None,
                                          text[: text.find(signature)] + half + err,
                                          expected_exit, signature)
        r["prefix_spoof"] = classify(rc, None,
                                     text.replace(signature, signature + " trailing-token", 1) + err,
                                     expected_exit, signature)
        r["stderr_only"] = classify(rc, None, text.replace(signature, "") + err + "\n" + signature,
                                    expected_exit, signature)
        r["stderr_only_stream_reject"] = classify_streams(
            rc, None, text.replace(signature, ""), err + "\n" + signature,
            expected_exit, signature)
        other = next((s for n, s in sigs.items() if n != case), None)
        if other:
            r["cross_case_signature"] = classify(rc, None, text + err + "\n" + other,
                                                 expected_exit, signature)
        # tail mutation: mutate the unpinned remainder of the PASS line
        line = next((l for l in text.splitlines() if signature in l), None)
        if line:
            tail = line.split(signature, 1)[1]
            if tail:
                mutated = line.replace(tail, tail.replace("0", "9").replace("1", "8"), 1)
                r["tail_mutation_inert"] = classify(rc, None,
                                                    text.replace(line, mutated) + err,
                                                    expected_exit, signature)
        rows[case] = r
        for k, v in r.items():
            if isinstance(v, bool):
                shapes[k] = shapes.get(k, 0) + (1 if v else 0)
    out["shapes"] = shapes
    out["rows"] = rows
    out["rows_total"] = len(rows)
    (SEAT / "discrimination.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in shapes.items()}, indent=1))
    print("rows:", len(rows))


if __name__ == "__main__":
    main()
