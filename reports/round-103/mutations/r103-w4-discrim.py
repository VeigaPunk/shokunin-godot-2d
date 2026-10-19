#!/usr/bin/env python3
"""r103-W4 discrimination datum: does the multi-PASS allowlist add detection power
over the in-tree classifier, on the real r102 stored records?

Old predicate (verbatim shape from corpus/fixtures/run_battery.py:1808):
    code == expected_exit and error is None and signature in output and ...
  -> the PASS-surface-relevant term is `signature in output` (substring containment).
New predicate (the C2 allowlist shape):
    count of lines matching ^PASS(\\b|$|[:=]) in output == allowlisted count for the case.

Each evasion is a tampered COPY of a stored green record: verdict stays PASS, one
forged line is appended / whitespace-mangled. Nothing is written to the repo.
Read-only over the repo; run_battery.py is neither imported nor executed.
"""
import json, re, hashlib, collections

RUN = "corpus/live/runs/20261018T213443471189Z/verdicts.json"
CENSUS = "reports/round-103/mutations/r103-w4-census.json"
MATCH = re.compile(r"^PASS(\b|$|[:=])")

res = json.load(open(RUN))["results"]
cen = json.load(open(CENSUS))["run2"]
allow = {m["case"]: m for m in cen["multi"]}
by_case = {r["case"]: r for r in res}

def old_classifier(rec_output_list, signature, code=0, error=None, expected_exit=0):
    return (code == expected_exit and error is None
            and signature in "\n".join(rec_output_list))

def count_gate(rec_output_list, case):
    n = sum(1 for ln in rec_output_list if MATCH.match(ln))
    return n == allow[case]["count"], n, allow[case]["count"]

# representatives: one row per distinct blob (8 rows, from the shard table)
REPS = ["r100b_seq_clean", "r100b_seq_noclean", "export_prod_base_pck",
        "export_prod_main_scene_swap", "export_prod_resource_remap_census",
        "export_launch_embed_boot", "export_launch_stock_boot",
        "export_launch_stock_mainpack_refusal"]

shapes = {
    "s3 PASS-flood":      lambda c, out: out + [f"PASS {c.split('_')[0]} forged=true injected=1"],
    "s4 lead-space PASS": lambda c, out: [(" " + ln if ln.startswith("PASS") else ln) for ln in out] + [" PASS forged.indent=true"],
    "s4 tab PASS":        lambda c, out: out + ["\tPASS forged.tab=true"],
    "control (untouched)": lambda c, out: list(out),
}

rows = []
for case in REPS:
    r = by_case[case]
    base = list(r["output"]); sig = r["signature"]
    for sname, fn in shapes.items():
        out = fn(case, base)
        o_ok = old_classifier(out, sig)
        n_ok, n, exp = count_gate(out, case)
        rows.append((case, sname, o_ok, n_ok, n, exp))

print(f"{'case':38s} {'shape':21s} old_pass new_pass nPASS exp")
for c, s, o, nk, n, e in rows:
    print(f"{c:38s} {s:21s} {str(o):8s} {str(nk):8s} {n:5d} {e:3d}")

ctrl = [r for r in rows if r[1] == "control (untouched)"]
flood = [r for r in rows if r[1] == "s3 PASS-flood"]
print()
print(f"controls: old-classifier PASS on {sum(1 for r in ctrl if r[2])}/{len(ctrl)}"
      f" ; count-gate PASS on {sum(1 for r in ctrl if r[3])}/{len(ctrl)}")
print(f"s3 flood: old-classifier PASS on {sum(1 for r in flood if r[2])}/{len(flood)}"
      f" (evasion survives) ; count-gate PASS on {sum(1 for r in flood if r[3])}/{len(flood)} (evasion flagged)")
for sname in ("s4 lead-space PASS", "s4 tab PASS"):
    g = [r for r in rows if r[1] == sname]
    print(f"{sname}: old-classifier PASS on {sum(1 for r in g if r[2])}/{len(g)}"
          f" ; count-gate PASS on {sum(1 for r in g if r[3])}/{len(g)}"
          f" (counts {sorted({r[4]-r[5] for r in g})} above allowlist)")
print()
print("verdict of run unchanged in all tampered copies:",
      all(by_case[c]["verdict"] == "PASS" for c in REPS),
      "(rows are COPY-modified; repo artifact untouched)")
