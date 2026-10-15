#!/usr/bin/env python3
"""r96-boundary analyzer.

1. scout replication: every r96-scout frozen-arm receipt in runs/<batch>/scout_*.{out,err}
   is compared with the scout's own canonical receipt
   (corpus/live/r96-scout/runs/r96_<cell>.rep1.out + .err), and across batches.
2. boundary arms: per (script, arm) distinct PASS payloads within and across batches.
3. cross-batch token comparison for the decisive id vectors.

Writes runs/analyze_r96b.json and prints a human summary.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
SCOUT = HERE.parent / "r96-scout"
BATCHES = ["quiet", "load", "ff1", "ff30", "ff120"]
OUT = {}


def read(p):
    return p.read_text() if p.exists() else ""


def pass_lines(text):
    return [ln for ln in text.splitlines() if ln.startswith("PASS ")]


def scout_canon(cell):
    p = SCOUT / "runs" / f"r96_{cell}.rep1.out"
    e = SCOUT / "runs" / f"r96_{cell}.rep1.err"
    return read(p), read(e)


# ---------------------------------------------------------------- 1. replication
repl = {}
for batch in BATCHES:
    d = HERE / "runs" / batch
    if not d.exists():
        continue
    for out in sorted(d.glob("scout_*.rep*.out")):
        cell = out.name[len("scout_"):].split(".rep")[0]
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        if not rc.exists():
            continue  # batch still running
        co, ce = scout_canon(cell)
        got, gerr = read(out), read(err)
        rec = repl.setdefault(cell, {})
        rec.setdefault("receipts", []).append({
            "batch": batch, "rep": out.name,
            "rc": int(rc.read_text().strip()) if rc.exists() else None,
            "pass_eq_canon": pass_lines(got) == pass_lines(co),
            "err_eq_canon": gerr == ce,
            "pass_line": pass_lines(got)[0] if pass_lines(got) else "",
        })
    # scout arms whose canonical receipt is missing entirely
for cell, rec in repl.items():
    rec["n"] = len(rec["receipts"])
    rec["all_pass_eq_canon"] = all(r["pass_eq_canon"] for r in rec["receipts"])
    rec["all_err_eq_canon"] = all(r["err_eq_canon"] for r in rec["receipts"])
    rec["rc_set"] = sorted({r["rc"] for r in rec["receipts"] if r["rc"] is not None})
    rec["distinct_pass"] = len({r["pass_line"] for r in rec["receipts"]})
    rec["batches"] = sorted({r["batch"] for r in rec["receipts"]})
OUT["replication"] = repl

# ---------------------------------------------------------------- 2. boundary arms
probes = {}
for batch in BATCHES:
    d = HERE / "runs" / batch
    if not d.exists():
        continue
    for out in sorted(d.glob("r96b_*.rep*.out")):
        stem = out.name.split(".rep")[0]
        script, arm = stem.split("_", 1)
        rcf = out.with_suffix(".rc")
        if not rcf.exists():
            continue  # batch still running
        got = read(out)
        pls = pass_lines(got)
        rec = probes.setdefault(stem, {"batches": {}, "script": script, "arm": arm})
        rec["batches"].setdefault(batch, []).append({
            "rep": out.name,
            "rc": int(out.with_suffix(".rc").read_text().strip()) if out.with_suffix(".rc").exists() else None,
            "err_empty": read(out.with_suffix(".err")) == "",
            "pass": pls[0] if pls else "",
        })
for stem, rec in probes.items():
    allp = [r["pass"] for b in rec["batches"].values() for r in b]
    rec["n"] = len(allp)
    rec["distinct_all"] = len(set(allp))
    rec["distinct_within_batch"] = {b: len({r["pass"] for r in rs}) for b, rs in rec["batches"].items()}
    rec["stable_all_conditions"] = rec["distinct_all"] == 1
    rec["rc_set"] = sorted({r["rc"] for b in rec["batches"].values() for r in b})
    rec["err_all_empty"] = all(r["err_empty"] for b in rec["batches"].values() for r in b)
OUT["probes"] = probes

# ---------------------------------------------------------------- 3. token extraction
TOKENS = {
    "ext_id": re.compile(r"\bext_ids?1=([^\s]+)"),
    "sub_id": re.compile(r"\bsub_id=([^\s]+)"),
    "gen1": re.compile(r"\bgen1=([^\s]+)"),
    "pinned_sha": re.compile(r"\bpinned_sha=([^\s]+)"),
    "sha_uonly": re.compile(r"\bsha_uonly=([^\s]+)"),
    "seq": re.compile(r"\bseq=([^\s]+)"),
}
tokens = {}
for stem, rec in probes.items():
    for b, rs in rec["batches"].items():
        for r in rs:
            for name, rx in TOKENS.items():
                m = rx.search(r["pass"])
                if m:
                    tokens.setdefault(stem, {}).setdefault(name, {}).setdefault(b, set()).add(m.group(1))
OUT["tokens"] = {k: {t: {b: sorted(v) for b, v in bv.items()} for t, bv in tv.items()} for k, tv in tokens.items()}

(HERE / "runs" / "analyze_r96b.json").write_text(json.dumps(OUT, indent=1, sort_keys=True))

# ---------------------------------------------------------------- print
print("== scout replication vs scout canonical receipts ==")
for cell in sorted(repl):
    r = repl[cell]
    flag = "OK " if (r["all_pass_eq_canon"] and r["all_err_eq_canon"]) else "DIFF"
    print(f" {flag} {cell:12s} n={r['n']:2d} rc={r['rc_set']} distinct_pass={r['distinct_pass']} "
          f"pass_eq_canon={r['all_pass_eq_canon']} err_eq_canon={r['all_err_eq_canon']} batches={','.join(r['batches'])}")
    if not r["all_pass_eq_canon"]:
        for x in r["receipts"]:
            if not x["pass_eq_canon"]:
                print(f"      {x['batch']}/{x['rep']}: {x['pass_line'][:160]}")
print("== boundary arms ==")
for stem in sorted(probes):
    r = probes[stem]
    print(f" {'STABLE' if r['stable_all_conditions'] else 'VARIES'} {stem:26s} n={r['n']:2d} rc={r['rc_set']} "
          f"distinct={r['distinct_all']} within={r['distinct_within_batch']} err_empty={r['err_all_empty']}")
print("== decisive tokens per batch ==")
for stem in sorted(tokens):
    for t, bv in sorted(tokens[stem].items()):
        vals = {b: v for b, v in bv.items()}
        n = len({x for v in vals.values() for x in v})
        print(f" {stem:26s} {t:10s} distinct_values={n} {vals}")
sys.exit(0)
