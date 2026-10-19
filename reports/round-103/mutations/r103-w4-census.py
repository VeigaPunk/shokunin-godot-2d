#!/usr/bin/env python3
"""r103-W4 receipt census: rows whose stored stdout carries >1 PASS-line.
Reads r102 verdicts.json runs read-only; emits exact per-row PASS-line lists.
"""
import json, re, sys, hashlib, io

RUNS = {
    "run1": "corpus/live/runs/20261018T212500022987Z/verdicts.json",
    "run2": "corpus/live/runs/20261018T213443471189Z/verdicts.json",
}
PASS_START = re.compile(r"^PASS(\b|$|[:=])")

def lines_of(row):
    out = row.get("output")
    if out is None:
        return None
    if isinstance(out, str):
        return out.splitlines()
    return [str(x) for x in out]

def census(path):
    j = json.load(open(path))
    res = j["results"]
    n = len(res)
    vc = {}
    have_output = 0
    multi = []
    zero = 0
    raw_diff = []
    shape_first_tokens = {}
    for i, r in enumerate(res):
        vc[r.get("verdict")] = vc.get(r.get("verdict"), 0) + 1
        ls = lines_of(r)
        if ls is None:
            continue
        have_output += 1
        p = [ln for ln in ls if PASS_START.match(ln)]
        for ln in p:
            tok = ln.split()[0] if ln.split() else ln
            shape_first_tokens[tok] = shape_first_tokens.get(tok, 0) + 1
        if len(p) == 0:
            zero += 1
        if len(p) > 1:
            raw = r.get("raw_output")
            raw_ls = None
            if raw is not None:
                raw_ls = raw.splitlines() if isinstance(raw, str) else [str(x) for x in raw]
                raw_p = [ln for ln in raw_ls if PASS_START.match(ln)]
                if raw_p != p:
                    raw_diff.append(r.get("case"))
            multi.append({
                "case": r.get("case"), "script": r.get("script"),
                "verdict": r.get("verdict"), "count": len(p),
                "pass_lines": p, "row_index": i,
                "has_raw_output": raw is not None,
            })
    return {"file": path, "rows": n, "verdict_counts": vc,
            "rows_with_output": have_output, "rows_zero_pass": zero,
            "multi_count": len(multi), "multi": multi,
            "raw_output_pass_mismatch_cases": raw_diff,
            "shape_first_tokens": shape_first_tokens}

def main():
    report = {k: census(v) for k, v in RUNS.items()}
    out = json.dumps(report, indent=1, ensure_ascii=False)
    dest = "reports/round-103/mutations/r103-w4-census.json"
    open(dest, "w").write(out + "\n")
    print("WROTE", dest, len(out.encode()) + 1, "bytes")
    for k, r in report.items():
        print(f"[{k}] rows={r['rows']} verdicts={r['verdict_counts']} "
              f"rows_with_output={r['rows_with_output']} zero_pass={r['rows_zero_pass']} "
              f"multi={r['multi_count']} raw_mismatch={r['raw_output_pass_mismatch_cases']}")
        for m in r["multi"]:
            print(f"  {k} #{m['row_index']} case={m['case']!r} script={m['script']!r} "
                  f"verdict={m['verdict']} nPASS={m['count']} raw={m['has_raw_output']}")
            for ln in m["pass_lines"]:
                print(f"    | {ln}")
        print(f"  [{k}] first-token shapes: {r['shape_first_tokens']}")

if __name__ == "__main__":
    main()
