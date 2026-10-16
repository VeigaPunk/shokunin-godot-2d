#!/usr/bin/env python3
"""Re-derive the pinned ordering laws from the committed signatures (and,
when present, from fresh receipts) instead of trusting the prose.

Checks the r95b law set:
  A canon ladder closes at t20 (t20==t0), 20 distinct phases, still cycling at t64
  B periodx cycle_len == k(k-1) for k=2..10 (+ k=5 spacing 8)
  C perm0..7: 8 distinct t2 position vectors and 8 distinct ladders
  D cap40: n0/n32/n64, set32_distinct=5, three distinct set32_t2 subsets
  E celloff x0/x1000/y1000: identical ladders (translation invariance)
  F free_ab vs free_ba: ladders differ at every sampled tick
  G warm_k32 == canon sampled ladder; warm_keep8 differs (co-presence)
  H scoutrev: t2 vec matches the scout's order_core_rev row; relpos == canon
  I layers_k0 vs k1: pt/sh agreement flips with a CanvasLayer body
  J rigid: distinct_ticks=1
  K twopiles: A-with-B t4 != A-alone t4 (co-presence attribution)
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

FIX = Path(sys.argv[1])
VDIR = Path(sys.argv[2])

spec = importlib.util.spec_from_file_location("frozen_run_battery", FIX / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SIG = {c[0]: c[4] for c in mod.CASES if c[0].startswith(("dss_lattice_", "r95b_order_"))}

def kv(sig, key):
    m = re.search(rf"(?:^|\s){re.escape(key)}=(\S+)", sig)
    return m.group(1) if m else None

def ladder(sig):
    m = re.search(r"ladder=\[([^\]]*)\]", sig)
    if not m:
        return None
    out = {}
    for part in m.group(1).split(";"):
        t, _, vec = part.partition(":")
        out[int(t[1:])] = tuple(int(x) for x in vec.split(","))
    return out

def relpos(sig, key):
    m = re.search(rf"(?:^|\s){re.escape(key)}=\[([^\]]*)\]", sig)
    if not m:
        return None
    return tuple(m.group(1).split("|"))

report = {}

# A — canon
sig = SIG["r95b_order_canon"]
lad = ladder(sig)
phases = [lad[t] for t in range(20)]
report["A_canon"] = {
    "t0": lad[0], "t20": lad[20], "t20_equals_t0": lad[20] == lad[0],
    "t21_equals_t1": lad[21] == lad[1], "t22_equals_t2": lad[22] == lad[2],
    "t64_equals_t4": lad[64] == lad[4],
    "distinct_phases_t0_t19": len(set(phases)),
    "distinct_ticks_field": int(kv(sig, "distinct_ticks")),
    "cycle_len_dense_field": int(kv(sig, "cycle_len_dense")),
    "t0_is_insertion_order": lad[0] == (0, 1, 2, 3, 4),
    "pt_stable_interleaved": kv(sig, "pt_stable_interleaved") == "true",
}

# B — periodx
per = {}
for k, sig_name in [(2, "r95b_order_periodx_k2"), (3, "r95b_order_periodx_k3"),
                    (4, "r95b_order_periodx_k4"), (5, "r95b_order_periodx_k5"),
                    ("5s8", "r95b_order_periodx_k5s8"), (6, "r95b_order_periodx_k6"),
                    (7, "r95b_order_periodx_k7"), (8, "r95b_order_periodx_k8"),
                    (10, "r95b_order_periodx_k10")]:
    s = SIG[sig_name]
    kk = 5 if k == "5s8" else k
    per[str(k)] = {
        "k": kk,
        "cycle_len": int(kv(s, "cycle_len")),
        "expected_kk1": int(kv(s, "expected_kk1")),
        "distinct_ticks": int(kv(s, "distinct_ticks")),
        "cycle_len_eq_k(k-1)": int(kv(s, "cycle_len")) == kk * (kk - 1),
        "expected_matches_field": int(kv(s, "cycle_len")) == int(kv(s, "expected_kk1")),
        "distinct_eq_cycle": int(kv(s, "distinct_ticks")) == int(kv(s, "cycle_len")),
    }
report["B_periodx"] = per

# C — perms
perms = {i: SIG[f"r95b_order_perm{i}"] for i in range(8)}
t2 = {i: tuple(kv(s, "t2_relpos").split("|")) for i, s in perms.items()}
lads = {i: ladder(s) for i, s in perms.items()}
report["C_perms"] = {
    "distinct_t2_relpos": len({v for v in t2.values()}),
    "distinct_ladders": len({tuple(sorted(v.items())) for v in lads.values()}),
    "distinct_t2_vec": len({kv(s, "t2_vec") for s in perms.values()}),
    "map_field_constant": len({kv(s, "map") for s in perms.values()}) == 1,
}
# t0 should equal the creation-order indices: check via add_order
creation = {i: kv(perms[i], "add_order") for i in range(8)}
report["C_perms"]["add_orders_distinct"] = len(set(creation.values()))

# D — cap40
cap = {i: SIG[f"r95b_order_cap40_p{i}"] for i in range(3)}
sets32 = {i: kv(s, "set32_t2") for i, s in cap.items()}

def balanced(sig, key):
    """Extract the balanced [...] payload following `key=`."""
    i = sig.find(key + "=[")
    if i < 0:
        return None
    i += len(key) + 1
    depth = 0
    for j in range(i, len(sig)):
        if sig[j] == "[":
            depth += 1
        elif sig[j] == "]":
            depth -= 1
            if depth == 0:
                return sig[i + 1:j]
    return None

def set_ladder_distinct(sig):
    payload = balanced(sig, "set32_ladder")
    if payload is None:
        return None
    entries = re.split(r";(?=t\d+:)", payload)
    return len(set(entries)), len(entries)

report["D_cap40"] = {
    "n0": [kv(s, "n0") for s in cap.values()],
    "n32": [kv(s, "n32") for s in cap.values()],
    "n64": [kv(s, "n64") for s in cap.values()],
    "set32_distinct": [kv(s, "set32_distinct") for s in cap.values()],
    "set32_ladder_distinct_over_sampled_ticks": [set_ladder_distinct(s) for s in cap.values()],
    "distinct_set32_t2_across_perms": len(set(sets32.values())),
    "set32_t2_sizes": [len(v.split(",")) for v in sets32.values()],
}

# E — celloff
cells = [SIG["r95b_order_celloff_x0"], SIG["r95b_order_celloff_x1000"],
         SIG["r95b_order_celloff_y1000"]]
report["E_celloff"] = {
    "ladders_identical": len({re.search(r"ladder=\[([^\]]*)\]", s).group(1) for s in cells}) == 1,
    "t2_vec_identical": len({kv(s, "t2_vec") for s in cells}) == 1,
    "t2_relpos_identical": len({kv(s, "t2_relpos") for s in cells}) == 1,
}

# F — free order
fab, fba = ladder(SIG["r95b_order_free_ab"]), ladder(SIG["r95b_order_free_ba"])
report["F_free"] = {
    "ticks": sorted(fab),
    "differ_at_all_ticks": all(fab[t] != fba[t] for t in fab),
    "same_final_set": kv(SIG["r95b_order_free_ab"], "set") == kv(SIG["r95b_order_free_ba"], "set"),
    "post_free_cycle_t2_eq_t8": fab[2] == fab[8] and fba[2] == fba[8],
}

# G — warm
canon_lad = ladder(SIG["r95b_order_canon"])
w32, wk8 = SIG["r95b_order_warm_k32"], SIG["r95b_order_warm_keep8"]
w32_lad, wk8_lad = ladder(w32), ladder(wk8)
common = sorted(set(w32_lad) & set(canon_lad))
report["G_warm"] = {
    "k32_ladder_equals_canon_on_common_ticks": all(w32_lad[t] == canon_lad[t] for t in common),
    "k32_t2_vec_equals_canon": kv(w32, "t2_vec") == kv(SIG["r95b_order_canon"], "t2_vec"),
    "keep8_t2_vec_differs_from_canon": kv(wk8, "t2_vec") != kv(SIG["r95b_order_canon"], "t2_vec"),
    "keep8_distinct_ticks": kv(wk8, "distinct_ticks"),
}

# H — scoutrev
sc = SIG["r95b_order_scoutrev"]
report["H_scoutrev"] = {
    "t2_vec_matches_scout_row": kv(sc, "t2_vec_matches_scout_row") == "true",
    "t2_relpos_equals_canon": kv(sc, "t2_relpos_equals_canon") == "true",
    "t2_vec": kv(sc, "t2_vec"),
    "t2_relpos": kv(sc, "t2_relpos"),
    "canon_t2_relpos": kv(SIG["r95b_order_canon"], "t2_relpos"),
}

# I — layers
k0, k1 = SIG["r95b_order_layers_k0"], SIG["r95b_order_layers_k1"]
report["I_layers"] = {
    "k0_pt_eq_sh": kv(k0, "pt_eq_sh"), "k0_sh_len": kv(k0, "sh_len"),
    "k1_pt_eq_sh": kv(k1, "pt_eq_sh"), "k1_sh_len": kv(k1, "sh_len"),
    "k1_pt0_t2_eq_sh": kv(k1, "pt0_t2_eq_sh"),
    "k0_pt0_t2_eq_sh": kv(k0, "pt0_t2_eq_sh"),
}

# J — rigid
report["J_rigid"] = {"distinct_ticks": kv(SIG["r95b_order_rigid"], "distinct_ticks"),
                     "t10_relpos": kv(SIG["r95b_order_rigid"], "t10_relpos")}

# K — twopiles
tw = SIG["r95b_order_twopiles"]
canon_lad = ladder(SIG["r95b_order_canon"])
order = ["a", "b", "c", "d", "e"]
canon_t4_tags = ",".join(f"{order[i]}#0" for i in canon_lad[4])
report["K_twopiles"] = {
    "a_t2_eq_canon_t2": kv(tw, "a_t2_vec") == kv(SIG["r95b_order_canon"], "t2_vec"),
    "a_t4_with_b_vec": kv(tw, "a_t4_with_b_vec"),
    "canon_t4_tags": canon_t4_tags,
    "a_t4_with_b_differs_from_canon_t4": kv(tw, "a_t4_with_b_vec") != canon_t4_tags,
    "b_t2_vec": kv(tw, "b_t2_vec"),
}

(VDIR / "probes" / "laws.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
