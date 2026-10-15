#!/usr/bin/env python3
"""r95b boundary analysis.

Per-cell receipt stability (per batch), cross-condition comparison, and the
targeted falsification checks for the r95 scout's ordering claims.  Writes
runs/analyze_r95b.json and analysis.txt.

Cell name -> (arm, params) is carried by the driver's spec lines; this script
groups by the receipt file name, which encodes the same cell id.
"""
import glob
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
BATCHES = ["quiet", "load", "ff1", "ff30", "ff120", "thr", "label", "extra"]
ORDER_CELLS = ("canon", "perm", "warm", "free", "readd", "cap40", "layers",
               "celloff", "rigid", "procwait", "period", "twopiles", "scoutrev")


def read_receipts(batch):
    cells = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(ROOT, "runs", batch, "*.out"))):
        cell = os.path.basename(f).split(".rep")[0]
        cells[cell].append(f)
    return cells


def parse_pass(path):
    for line in open(path, errors="replace"):
        if line.startswith("PASS r95b_order "):
            d = {}
            for t in line.split()[3:]:
                if "=" in t:
                    k, v = t.split("=", 1)
                    d[k] = v
            return d
    return None


def keysig(d):
    return tuple(sorted(d.items()))



def ladder_map(ladder):
    """'[t2:a;t3:b]' -> {2:'a',3:'b'}"""
    if not ladder or not ladder.startswith("["):
        return {}
    out = {}
    for part in ladder[1:-1].split(";"):
        if ":" in part:
            t, v = part.split(":", 1)
            out[int(t[1:])] = v
    return out


def ladder_eq(a, b, ticks):
    """compare two ladder strings on the given tick set only"""
    ma, mb = ladder_map(a), ladder_map(b)
    return all(t in ma and t in mb and ma[t] == mb[t] for t in ticks)


def shorten(s, n=140):
    return s if len(s) <= n else s[:n] + "..."


def main():
    report = {"batches": {}, "cells": {}, "cross": {}, "checks": {}}
    per_batch_cell_sig = {}   # batch -> cell -> {sig: count}

    for batch in BATCHES:
        if not os.path.isdir(os.path.join(ROOT, "runs", batch)):
            continue
        b = {"cells": {}, "loadavg": ""}
        try:
            b["loadavg"] = open(os.path.join(ROOT, "runs", batch, "rc-summary.txt")).read().strip().splitlines()
        except FileNotFoundError:
            pass
        per_batch_cell_sig[batch] = {}
        for cell, files in sorted(read_receipts(batch).items()):
            rcs = []
            for f in files:
                rcf = f[:-4] + ".rc"
                rcs.append(int(open(rcf).read().strip()) if os.path.exists(rcf) else None)
            passes = [parse_pass(f) for f in files]
            good = [p for p in passes if p]
            sigs = defaultdict(int)
            for p in good:
                sigs[keysig(p)] += 1
            lines = set()
            for f in files:
                for line in open(f, errors="replace"):
                    if line.startswith("PASS r95b_order "):
                        lines.add(line.strip())
            entry = {
                "reps": len(files), "rc": rcs, "parsed": len(good),
                "key_uniq": len(sigs), "line_uniq": len(lines),
                "distinct": [dict(s) for s in sigs] if len(sigs) > 1 else None,
            }
            if good:
                entry["sample"] = good[0]
            b["cells"][cell] = entry
            per_batch_cell_sig[batch][cell] = sigs
        report["batches"][batch] = b

    # ---- cross-batch comparison (same cell id in >1 batch)
    all_cells = set()
    for batch in per_batch_cell_sig:
        all_cells |= set(per_batch_cell_sig[batch])
    for cell in sorted(all_cells):
        rows = {}
        for batch in per_batch_cell_sig:
            sigs = per_batch_cell_sig[batch].get(cell)
            if sigs:
                rows[batch] = {"key_uniq": len(sigs), "sig": dict(next(iter(sigs)))}
        report["cross"][cell] = rows

    # ---- targeted checks
    def sig_of(batch, cell, rep=0):
        p = os.path.join(ROOT, "runs", batch, f"{cell}.rep{rep + 1}.out")
        return parse_pass(p) if os.path.exists(p) else None

    checks = {}

    # C1 canon ladder per batch + the scout's pinned t2
    canon_rows = {}
    for batch in per_batch_cell_sig:
        p = sig_of(batch, "canon")
        if p:
            canon_rows[batch] = {"ladder": p.get("ladder"), "t2_vec": p.get("t2_vec"),
                                 "distinct_ticks": p.get("distinct_ticks"),
                                 "cycle_len_dense": p.get("cycle_len_dense"),
                                 "t64_vec": p.get("t64_vec"),
                                 "pt_stable_interleaved": p.get("pt_stable_interleaved"),
                                 "t2_pt_eq_sh": p.get("t2_pt_eq_sh")}
    checks["canon"] = canon_rows
    checks["canon_ladder_uniq_across_batches"] = len(
        {v["ladder"] for v in canon_rows.values() if v.get("ladder")})

    # C2 perm ladders (position permutations) - add-order dependence
    perm_rows = {}
    for cell in sorted(c for c in all_cells if c.startswith("perm")):
        p = sig_of("quiet", cell) or sig_of("load", cell)
        if p:
            perm_rows[cell] = {"add_order": p.get("add_order"), "ladder": p.get("ladder"),
                               "t2_vec": p.get("t2_vec"), "t2_relpos": p.get("t2_relpos")}
    checks["perm"] = perm_rows
    checks["perm_ladder_uniq"] = len({v["ladder"] for v in perm_rows.values() if v.get("ladder")})
    checks["perm_t2_relpos_uniq"] = len({v["t2_relpos"] for v in perm_rows.values() if v.get("t2_relpos")})

    # C3 celloff: translation invariance of the whole ladder
    x0 = (sig_of("quiet", "celloff_x0") or {}).get("ladder")
    celloff_ticks = [2, 3, 4, 6, 8, 16, 32, 64]
    off_rows = {}
    for cell in sorted(c for c in all_cells if c.startswith("celloff")):
        p = sig_of("quiet", cell)
        if p:
            off_rows[cell] = {"off": p.get("off"), "offy": p.get("offy"),
                              "ladder_eq_x0": ladder_eq(p.get("ladder"), x0, celloff_ticks),
                              "t2_relpos": p.get("t2_relpos"), "t64_relpos": p.get("t64_relpos")}
    checks["celloff"] = off_rows
    checks["celloff_ladder_eq_x0_true"] = sum(1 for v in off_rows.values() if v["ladder_eq_x0"])
    checks["celloff_ladder_eq_x0_false"] = [c for c, v in off_rows.items() if not v["ladder_eq_x0"]]

    # C4 period
    per_rows = {}
    for cell in sorted(c for c in all_cells if c.startswith("period") or c.startswith("periodx")):
        p = sig_of("quiet", cell) or sig_of("load", cell) or sig_of("ff30", cell) or sig_of("extra", cell)
        if p:
            per_rows[cell] = {"k": p.get("k"), "cycle_len": p.get("cycle_len"),
                              "distinct_ticks": p.get("distinct_ticks")}
    checks["period"] = per_rows
    checks["period_k_times_k_minus_1"] = {
        c: {"k": v["k"], "cycle_len": v["cycle_len"],
            "expected_k_k1": str(int(v["k"]) * (int(v["k"]) - 1)) if v.get("k") else None}
        for c, v in per_rows.items()}

    # C5 free-order permutations for the same final set
    free_rows = {}
    for cell in sorted(c for c in all_cells if c.startswith("free") or c.startswith("readd")):
        p = sig_of("quiet", cell) or sig_of("load", cell)
        if p:
            free_rows[cell] = {"freed": p.get("freed"), "which": p.get("which"),
                               "ladder": p.get("ladder"), "t1_relpos": p.get("t1_relpos"),
                               "t16_vec": p.get("t16_vec"), "set": p.get("set")}
    checks["free"] = free_rows
    checks["free_ab_eq_ba"] = (free_rows.get("free_ab", {}).get("ladder") ==
                               free_rows.get("free_ba", {}).get("ladder"))
    checks["free_ac_eq_ca"] = (free_rows.get("free_ac", {}).get("ladder") ==
                               free_rows.get("free_ca", {}).get("ladder"))

    # C5b free-order period cross-check: the sampled ladder must be consistent
    # with period k(k-1), k = colliders left in the space.
    fper = {}
    for cell in sorted(c for c in all_cells if c.startswith("free_") or c.startswith("layers")):
        p = sig_of("quiet", cell)
        if not p:
            continue
        lm = ladder_map(p.get("ladder") or p.get("pt0_ladder"))
        if cell.startswith("free"):
            freed = p.get("freed", "[]").strip("[]").split(",")
            k = 5 - len([x for x in freed if x])
        else:
            k = 5 + int(p.get("k", 0))
        per = k * (k - 1)
        pairs = [(t, t + per) for t in sorted(lm) if t + per in lm]
        fper[cell] = {"k_colliders": k, "period_kk1": per,
                      "pairs_checked": pairs,
                      "consistent": all(lm[a] == lm[b] for a, b in pairs) if pairs else None}
    checks["free_period"] = fper

    # C6 cap40: set invariance above the cap
    cap_rows = {}
    for cell in sorted(c for c in all_cells if c.startswith("cap40")):
        p = sig_of("quiet", cell) or sig_of("load", cell)
        if p:
            cap_rows[cell] = {"perm": p.get("perm"), "n32": p.get("n32"), "n64": p.get("n64"),
                              "n0": p.get("n0"), "set32_t2": p.get("set32_t2"),
                              "set32_distinct": p.get("set32_distinct"),
                              "set32_ladder": p.get("set32_ladder"), "set64": p.get("set64")}
    checks["cap40"] = cap_rows
    checks["cap40_set32_t2_uniq"] = len({v["set32_t2"] for v in cap_rows.values() if v.get("set32_t2")})
    checks["cap40_set32_distinct_values"] = sorted(
        {v["set32_distinct"] for v in cap_rows.values() if v.get("set32_distinct")})

    # C7 warm (allocation history) - ladder equality against canon
    warm_rows = {}
    canon_ladder = (sig_of("quiet", "canon") or {}).get("ladder")
    warm_ticks = [2, 3, 4, 6, 8, 16, 32]
    for cell in sorted(c for c in all_cells if c.startswith("warm")):
        p = sig_of("quiet", cell) or sig_of("load", cell)
        if p:
            warm_rows[cell] = {"k": p.get("k"), "keep": p.get("keep"),
                               "ladder_eq_canon": ladder_eq(p.get("ladder"), canon_ladder, warm_ticks),
                               "t2_vec": p.get("t2_vec"), "t32_vec": p.get("t32_vec"),
                               "ladder": p.get("ladder")}
    checks["warm"] = warm_rows
    checks["warm_ladder_eq_canon_true"] = [c for c, v in warm_rows.items() if v["ladder_eq_canon"]]
    checks["warm_ladder_eq_canon_false"] = [c for c, v in warm_rows.items() if not v["ladder_eq_canon"]]

    # C8 layers
    lay_rows = {}
    for cell in sorted(c for c in all_cells if c.startswith("layers")):
        p = sig_of("quiet", cell) or sig_of("load", cell)
        if p:
            lay_rows[cell] = {"k": p.get("k"),
                              "pt0_ladder_eq_canon": ladder_eq(p.get("pt0_ladder"), canon_ladder, warm_ticks),
                              "pt0_ladder": p.get("pt0_ladder"), "pt0_t2_vec": p.get("pt0_t2_vec"),
                              "pt0_t2_eq_sh": p.get("pt0_t2_eq_sh"), "pt_eq_sh": p.get("pt_eq_sh"),
                              "sh_len": p.get("sh_len"), "sh_vec": p.get("sh_vec")}
    checks["layers"] = lay_rows

    # C9 twopiles (co-presence confound)
    tp_rows = {}
    for batch in per_batch_cell_sig:
        p = sig_of(batch, "twopiles")
        if p:
            tp_rows[batch] = {k: p.get(k) for k in
                              ("a_t2_vec", "a_t4_with_b_vec", "b_t2_vec", "b_t2_relpos",
                               "a_t6_with_b_vec", "b_t4_vec")}
    checks["twopiles"] = tp_rows

    # C10 procwait (process-frame scheduler sensitivity)
    pw_rows = {}
    for batch in per_batch_cell_sig:
        p = sig_of(batch, "procwait")
        if p:
            pw_rows[batch] = {"pf_per_procawait": p.get("pf_per_procawait"),
                              "distinct": p.get("distinct"), "ladder": p.get("ladder_procawait")}
    checks["procwait"] = pw_rows

    # C11 scoutrev (label-permutation proof)
    sr_rows = {}
    for batch in per_batch_cell_sig:
        p = sig_of(batch, "scoutrev")
        if p:
            sr_rows[batch] = {k: p.get(k) for k in
                              ("add_order", "t2_vec", "t2_relpos", "t2_vec_matches_scout_row",
                               "t2_relpos_equals_canon", "ladder")}
    checks["scoutrev"] = sr_rows

    # C11b scoutrev ladder == perm0 ladder under the tag-index mirror i -> 4-i
    p0 = ladder_map((sig_of("quiet", "perm0") or {}).get("ladder"))
    sr = ladder_map((sig_of("label", "scoutrev") or sig_of("quiet", "scoutrev") or {}).get("ladder"))
    mirrored = {t: ",".join(str(4 - int(x)) for x in v.split(",")) for t, v in p0.items()}
    common = sorted(set(sr) & set(mirrored))
    checks["scoutrev_ladder_mirrors_perm0"] = {
        "ticks_compared": common,
        "all_equal": all(sr[t] == mirrored[t] for t in common),
        "scoutrev": {t: sr[t] for t in common},
        "perm0_mirrored": {t: mirrored[t] for t in common},
    }

    # C12 rigid (solver determinism)
    rig_rows = {}
    for batch in per_batch_cell_sig:
        p = sig_of(batch, "rigid")
        if p:
            rig_rows[batch] = {"ladder": p.get("ladder"), "distinct_ticks": p.get("distinct_ticks"),
                               "t10_relpos": p.get("t10_relpos")}
    checks["rigid"] = rig_rows

    # ---- diagnostics stability (values printed on R95B lines only)
    diag = {}
    for batch in BATCHES:
        for cell in sorted(read_receipts(batch)) if os.path.isdir(os.path.join(ROOT, "runs", batch)) else []:
            vals = defaultdict(set)
            for f in read_receipts(batch)[cell]:
                for line in open(f, errors="replace"):
                    if line.startswith("R95B ") and "=" in line:
                        k, v = line.split(" ", 2)[2].strip().split("=", 1)
                        if k in ("ids", "t10_bodypos", "fresh_id"):
                            vals[k].add(v)
            if vals:
                diag[f"{batch}/{cell}"] = {k: {"uniq": len(v), "n": len(vals[k]),
                                               "sample": sorted(v)[0][:200]} for k, v in vals.items()}
    checks["diag_stability"] = diag
    dvals = {}
    for batch in BATCHES:
        if not os.path.isdir(os.path.join(ROOT, "runs", batch)):
            continue
        for cell in sorted(read_receipts(batch)):
            for f in read_receipts(batch)[cell]:
                for line in open(f, errors="replace"):
                    if line.startswith("R95B ") and "=" in line:
                        k, v = line.split(" ", 2)[2].strip().split("=", 1)
                        if k in ("ids", "t10_bodypos"):
                            dvals.setdefault((batch, cell), {}).setdefault(k, set()).add(v)
    def union(key, cells):
        u = set()
        for (b, c), kv in dvals.items():
            if key in kv and (not cells or c in cells):
                u |= kv[key]
        return u
    checks["diag_cross"] = {
        "ids_canon_across_batches_uniq": len(union("ids", {"canon"})),
        "ids_perm0_across_batches_uniq": len(union("ids", {"perm0"})),
        "ids_warm_k0_vs_k1_vs_k32_uniq": len(union("ids", {"warm_k0", "warm_k1", "warm_k32"})),
        "ids_keep8_vs_canon_uniq": len(union("ids", {"canon", "warm_keep8"})),
        "t10_bodypos_rigid_across_batches_uniq": len(union("t10_bodypos", {"rigid"})),
        "ids_canon_sample": sorted(union("ids", {"canon"}))[0] if union("ids", {"canon"}) else None,
        "ids_warm_k1_sample": sorted(union("ids", {"warm_k1"}))[0] if union("ids", {"warm_k1"}) else None,
    }
    report["checks"] = checks

    with open(os.path.join(ROOT, "runs", "analyze_r95b.json"), "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)

    # ---------------- text summary
    out = []
    for batch in BATCHES:
        if batch not in report["batches"]:
            continue
        b = report["batches"][batch]
        out.append(f"== batch {batch} ==")
        for line in b.get("loadavg", [])[:2]:
            out.append("   " + line)
        for cell, e in b["cells"].items():
            flag = "  <<< UNSTABLE" if e["key_uniq"] > 1 else ""
            out.append(f"   {cell:16s} reps={e['reps']} rc={e['rc']} key_uniq={e['key_uniq']} "
                       f"line_uniq={e['line_uniq']}{flag}")
            if e["key_uniq"] > 1:
                for d in e["distinct"]:
                    diff = {k: shorten(v) for k, v in d.items() if k in ORDER_CELLS or k in
                            ("ladder", "t2_vec", "vec", "relpos", "set", "ladder_procawait",
                             "set32_ladder", "pf_per_procawait", "t2_relpos", "t1_relpos",
                             "t16_vec", "t32_vec", "a_t4_with_b_vec", "b_t2_vec")}
                    out.append("       " + json.dumps(diff, sort_keys=True))
        out.append("")

    out.append("== cross-batch (same cell id in >1 batch) ==")
    for cell, rows in sorted(report["cross"].items()):
        uniq = len({json.dumps(r["sig"], sort_keys=True) for r in rows.values()})
        if len(rows) > 1:
            out.append(f"   {cell:16s} batches={len(rows)} uniq_sig={uniq}"
                       + ("   <<< MODE-SENSITIVE" if uniq > 1 else ""))

    out.append("")
    out.append("== targeted checks ==")
    c = report["checks"]
    out.append(f"canon: ladder uniq across batches = {c['canon_ladder_uniq_across_batches']}")
    for batch, v in c["canon"].items():
        out.append(f"   [{batch}] t2={v['t2_vec']} distinct_ticks={v['distinct_ticks']} "
                   f"cycle_len_dense={v['cycle_len_dense']} t64={v['t64_vec']}")
        out.append(f"        ladder={shorten(v['ladder'], 400)}")
    out.append(f"perm: distinct ladders={c['perm_ladder_uniq']} distinct t2_relpos={c['perm_t2_relpos_uniq']}")
    for cell, v in c["perm"].items():
        out.append(f"   {cell} add_order={v['add_order']} t2_relpos={v['t2_relpos']} ladder={shorten(v['ladder'], 200)}")
    out.append(f"celloff: ladder==x0 true for {c['celloff_ladder_eq_x0_true']} cells; "
               f"false for {c['celloff_ladder_eq_x0_false']}")
    for cell, v in c["celloff"].items():
        out.append(f"   {cell:16s} off={v['off']} offy={v['offy']} eq_x0={v['ladder_eq_x0']}")
    out.append(f"period: {json.dumps(c['period'], sort_keys=True)}")
    out.append(f"free: ab==ba ladder -> {c['free_ab_eq_ba']}; ac==ca -> {c['free_ac_eq_ca']}")
    for cell, v in c["free"].items():
        out.append(f"   {cell:12s} freed={v['freed']} which={v['which']} t1_relpos={v['t1_relpos']} "
                   f"set={v['set']} ladder={shorten(v['ladder'], 160)}")
    out.append("free/layers period cross-check (ladder[t] == ladder[t+k(k-1)]):")
    for cell, v in c["free_period"].items():
        out.append(f"   {cell:12s} k_colliders={v['k_colliders']} k(k-1)={v['period_kk1']} "
                   f"pairs={v['pairs_checked']} consistent={v['consistent']}")
    out.append(f"cap40: set32_t2 uniq={c['cap40_set32_t2_uniq']} distinct-values={c['cap40_set32_distinct_values']}")
    for cell, v in c["cap40"].items():
        out.append(f"   {cell} n32={v['n32']} n64={v['n64']} n0={v['n0']} set32_t2={shorten(v['set32_t2'], 400)}")
    out.append(f"warm: ladder==canon true={c['warm_ladder_eq_canon_true']} false={c['warm_ladder_eq_canon_false']}")
    for cell, v in c["warm"].items():
        out.append(f"   {cell:16s} k={v['k']} keep={v['keep']} eq_canon={v['ladder_eq_canon']} t2={v['t2_vec']}")
    for cell, v in c["layers"].items():
        out.append(f"layers {cell}: k={v['k']} pt0_ladder_eq_canon={v['pt0_ladder_eq_canon']} "
                   f"pt0_t2_eq_sh={v['pt0_t2_eq_sh']} pt_eq_sh={v['pt_eq_sh']} sh_len={v['sh_len']} sh_vec={v['sh_vec']}")
    for batch, v in c["twopiles"].items():
        out.append(f"twopiles [{batch}] a_t2={v['a_t2_vec']} a_t4_with_b={v['a_t4_with_b_vec']} "
                   f"b_t2={v['b_t2_vec']} b_t2_relpos={v['b_t2_relpos']} b_t4={v['b_t4_vec']}")
    for batch, v in c["procwait"].items():
        out.append(f"procwait [{batch}] pf_per_procawait={v['pf_per_procawait']} distinct={v['distinct']}")
    for batch, v in c["scoutrev"].items():
        out.append(f"scoutrev [{batch}] add_order={v['add_order']} t2_vec={v['t2_vec']} "
                   f"matches_scout_row={v['t2_vec_matches_scout_row']} relpos_equals_canon={v['t2_relpos_equals_canon']}")
        out.append(f"        ladder={v['ladder']}")
    sr = c.get("scoutrev_ladder_mirrors_perm0", {})
    out.append(f"scoutrev ladder mirrors perm0 (i->4-i): {sr.get('all_equal')} over ticks {sr.get('ticks_compared')}")
    out.append("diag cross-batch (values are NOT in the PASS line): " + json.dumps(c.get("diag_cross", {}), sort_keys=True))
    out.append("diag stability (instance ids / rigid body positions, NOT in the PASS line):")
    for key, v in sorted(c["diag_stability"].items()):
        for k2, v2 in v.items():
            flag = "  <<< VARIES" if v2["uniq"] > 1 else ""
            out.append(f"   {key:18s} {k2:12s} uniq={v2['uniq']}/{v2['n']}{flag}")
    for batch, v in c["rigid"].items():
        out.append(f"rigid [{batch}] distinct_ticks={v['distinct_ticks']} t10_relpos={v['t10_relpos']}")

    text = "\n".join(out)
    with open(os.path.join(ROOT, "analysis.txt"), "w") as fh:
        fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
