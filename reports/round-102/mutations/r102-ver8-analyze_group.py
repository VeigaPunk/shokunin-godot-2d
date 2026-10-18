"""r102-ver8: fold-vs-base analyzer — stable-field census, verdict/rc/receipt classes.

Rule (r101-simp1 null control): a field counts as a fold effect only if it is
single-valued on the committed side (both base reps) and differs on the folded side.
"""
import json, re, sys
from pathlib import Path

KV = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)=(\S+)")
BT = re.compile(r"(res://[A-Za-z0-9_./-]+\.gd):(\d+)")

def keys_of(text):
    out = {}
    for k, v in KV.findall(text):
        out.setdefault(k, []).append(v)
    return out

def load(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]

def main(base1, base2, fold1, fold2, out=None, filt=None):
    B1, B2, F1, F2 = map(load, (base1, base2, fold1, fold2))
    if filt:
        keep = set(json.loads(Path(filt).read_text())["cases"])
        B1 = [r for r in B1 if r["case"] in keep]
        B2 = [r for r in B2 if r["case"] in keep]
        F1 = [r for r in F1 if r["case"] in keep]
        F2 = [r for r in F2 if r["case"] in keep]
    B1m = {r["case"]: r for r in B1}; B2m = {r["case"]: r for r in B2}
    F1m = {r["case"]: r for r in F1}; F2m = {r["case"]: r for r in F2}
    names = sorted(B1m)
    report = {"rows": len(names), "stable_field_violations": [],
              "rc_diffs": [], "noise_rows_base": [], "noise_rows_fold": [],
              "receipt_identical_4": 0, "receipt_identical_masked_4": 0,
              "fold_stdout_foldrep_stable": 0}
    for n in names:
        rb1, rb2, rf1, rf2 = B1m[n], B2m[n], F1m[n], F2m[n]
        if not (rb1["actual_exit"] == rb2["actual_exit"] == rf1["actual_exit"] == rf2["actual_exit"]):
            report["rc_diffs"].append({"case": n, "rc": [rb1["actual_exit"], rb2["actual_exit"],
                                                          rf1["actual_exit"], rf2["actual_exit"]]})
        texts_base = [rb1["stdout"] + rb1["stderr"], rb2["stdout"] + rb2["stderr"]]
        texts_fold = [rf1["stdout"] + rf1["stderr"], rf2["stdout"] + rf2["stderr"]]
        kb = [keys_of(t) for t in texts_base]
        stable = {k: v[0] for k, v in kb[0].items() if kb[1].get(k) == [v[0]] and len(v) == 1}
        for k, v in kb[1].items():
            if k in stable and v != [stable[k]]:
                stable.pop(k, None)
        # noise detection on base itself
        if texts_base[0].strip() != texts_base[1].strip():
            mb = BT.sub(r"\1:<l>", texts_base[0].strip()) == BT.sub(r"\1:<l>", texts_base[1].strip())
            report["noise_rows_base"].append({"case": n, "backtrace_only": mb})
        if texts_fold[0].strip() != texts_fold[1].strip():
            mf = BT.sub(r"\1:<l>", texts_fold[0].strip()) == BT.sub(r"\1:<l>", texts_fold[1].strip())
            report["noise_rows_fold"].append({"case": n, "backtrace_only": mf})
        # fold-side stability of its own value sets
        kf = [keys_of(t) for t in texts_fold]
        for k, v in stable.items():
            fv = kf[0].get(k)
            if fv is None:
                report["stable_field_violations"].append({"case": n, "key": k, "base": v, "fold": None})
                continue
            allf = set(kf[0].get(k, [])) | set(kf[1].get(k, []))
            if allf != {v}:
                report["stable_field_violations"].append({"case": n, "key": k, "base": v,
                                                          "fold_rep1": kf[0].get(k), "fold_rep2": kf[1].get(k)})
        # whole-receipt identity across the 4
        four = [t.strip() for t in texts_base + texts_fold]
        if len(set(four)) == 1:
            report["receipt_identical_4"] += 1
        mfour = {BT.sub(r"\1:<l>", t) for t in four}
        if len(mfour) == 1:
            report["receipt_identical_masked_4"] += 1
        # fold rep stability
        if texts_fold[0] == texts_fold[1]:
            report["fold_stdout_foldrep_stable"] += 1
    print(json.dumps({k: v for k, v in report.items() if k != "stable_field_violations"}, indent=1)[:1400])
    print("stable_field_violations:", len(report["stable_field_violations"]))
    for v in report["stable_field_violations"][:20]:
        print(" ", v)
    if out:
        Path(out).write_text(json.dumps(report, indent=1))
        print("wrote", out)
    return 1 if report["stable_field_violations"] or report["rc_diffs"] else 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5], out=sys.argv[5] if len(sys.argv) > 5 else None,
                  filt=sys.argv[6] if len(sys.argv) > 6 else None))
