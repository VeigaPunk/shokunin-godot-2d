#!/usr/bin/env python3
"""r95-scribe law re-derivation from raw receipts (no report is trusted).

Sources: boundary batches, scout canonical+loadtest, author battery runs,
scribe fresh arms, scribe battery runs.  Read-only.
"""
import json
import re
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LANE = REPO / "corpus/live/r95-scribe"
OUT = LANE / "audit/laws.json"

sources = []


def add_source(name, path, glob):
    for p in sorted(Path(path).glob(glob)):
        sources.append({"source": name, "path": str(p.relative_to(REPO)),
                        "text": p.read_text(errors="replace")})


add_source("boundary", REPO / "corpus/live/r95-boundary/runs", "*/*.out")
add_source("scout", REPO / "corpus/live/r95-scout/runs", "*.out")
add_source("scout-loadtest", REPO / "corpus/live/r95-scout/runs/loadtest", "*.out")
add_source("scout-alt", REPO / "corpus/live/r95-scout/runs/alt", "*.out")
add_source("scribe-fresh", LANE / "fresh", "*.out")
for run in sorted((LANE / "battery-runs").glob("*/verdicts.json")) + \
        sorted((LANE / "battery-committed").glob("*/verdicts.json")):
    v = json.loads(run.read_text())
    text = "\n".join(l for r in v["results"] for l in (r.get("output") or []))
    sources.append({"source": "scribe-battery", "path": str(run.relative_to(REPO)), "text": text})

law = {}


def pass_lines(text):
    return [l for l in text.splitlines() if l.startswith("PASS ")]


def field(lines, key):
    vals = []
    for l in lines:
        m = re.search(rf"\b{re.escape(key)}=([^\s]+)", l)
        if m:
            vals.append(m.group(1))
    return vals


def uniq(vals):
    return sorted(set(vals))


def receipts_for(case_substr, arm_match=None):
    out = []
    for s in sources:
        for l in pass_lines(s["text"]):
            if case_substr in l and (arm_match is None or arm_match in l):
                out.append({"source": s["source"], "path": s["path"], "line": l})
    return out


# ---- canon: cycle closure + t2 phase -------------------------------------
canon = [r for r in receipts_for(" r95b_order canon ") if "ladder=" in r["line"]]
law["canon"] = {
    "receipts": len(canon),
    "distinct_ticks": uniq([m.group(1) for r in canon
                            for m in [re.search(r"distinct_ticks=(\d+)", r["line"])] if m]),
    "cycle_len_dense": uniq([m.group(1) for r in canon
                             for m in [re.search(r"cycle_len_dense=(\d+)", r["line"])] if m]),
    "t2_vec": uniq(field([r["line"] for r in canon], "t2_vec")),
    "t0_eq_t20": [bool(re.search(r"t0:0,1,2,3,4", r["line"])) for r in canon],
    "sources": uniq([r["source"] for r in canon]),
}

# ---- periodx ladder: cycle_len == k(k-1) ---------------------------------
per = []
for r in receipts_for(" r95b_order periodx "):
    m2 = re.search(r"\bk=(\d+)", r["line"])
    m3 = re.search(r"cycle_len=(\d+)", r["line"])
    if m3:
        k = int(m2.group(1)) if m2 else None
        per.append({"path": r["path"], "k": k, "cycle_len": int(m3.group(1)),
                    "distinct_ticks": re.search(r"distinct_ticks=(\d+)", r["line"]).group(1)
                    if re.search(r"distinct_ticks=(\d+)", r["line"]) else None,
                    "source": r["source"]})
law["periodx"] = {
    "cells": per,
    "all_kk1": all(p["k"] and p["cycle_len"] == p["k"] * (p["k"] - 1) for p in per),
    "k_values": sorted({p["k"] for p in per}),
}

# ---- perm0..7: 8 distinct ladders + vectors ------------------------------
perm = {}
for r in receipts_for(" r95b_order perm "):
    m = re.search(r"\bperm=(\d)\b", r["line"])
    if not m:
        continue
    i = m.group(1)
    ladders = re.findall(r"ladder=\[([^\]]+)\]", r["line"])
    vec = re.findall(r"t2_vec=\[([^\]]+)\]", r["line"])
    perm.setdefault(i, {"ladders": set(), "vecs": set(), "receipts": 0})
    perm[i]["receipts"] += 1
    if ladders:
        perm[i]["ladders"].add(ladders[0])
    if vec:
        perm[i]["vecs"].add(vec[0])
law["perm"] = {
    "cells": {k: {"receipts": v["receipts"], "ladder_uniq": len(v["ladders"]),
                  "vec_uniq": len(v["vecs"])} for k, v in sorted(perm.items())},
    "distinct_ladders": len({next(iter(v["ladders"])) for v in perm.values() if v["ladders"]}),
    "distinct_vecs": len({next(iter(v["vecs"])) for v in perm.values() if v["vecs"]}),
}

# ---- celloff: translation invariance -------------------------------------
cell = {}
for r in receipts_for(" r95b_order celloff "):
    m = re.search(r"celloff off=([^\s]+) .*?ladder=\[([^\]]+)\]", r["line"])
    if m:
        cell.setdefault(m.group(2), []).append(m.group(1))
law["celloff"] = {"distinct_ladders": len(cell), "cells": {k[:60]: v for k, v in cell.items()}}

# ---- twopiles co-presence -------------------------------------------------
two = [r["line"] for r in receipts_for(" r95b_order twopiles")]
law["twopiles"] = {
    "receipts": len(two),
    "lines_uniq": len(set(two)),
    "sample": two[0][:400] if two else None,
}

# ---- free order -----------------------------------------------------------
free = {}
for r in receipts_for(" r95b_order free "):
    m = re.search(r"freed=\[([^\]]+)\]", r["line"])
    lad = re.search(r"ladder=\[([^\]]+)\]", r["line"])
    if m and lad:
        free.setdefault(m.group(1), set()).add(lad.group(1))
law["free"] = {k: {"ladders_uniq": len(v), "sample": next(iter(v))[:120]} for k, v in sorted(free.items())}

# ---- cap40 ----------------------------------------------------------------
cap = {}
for r in receipts_for(" r95b_order cap40 "):
    m = re.search(r"perm=(\d)", r["line"])
    if not m:
        continue
    cap.setdefault(m.group(1), {"set32_distinct": set(), "t2": set(), "counts": set(),
                                "receipts": 0})
    cap[m.group(1)]["receipts"] += 1
    for key, tgt in (("set32_distinct", "set32_distinct"), ("set32_t2", "t2")):
        mm = re.search(rf"\b{key}=([^\s\]]+(?:\[[^\]]*\])?)", r["line"])
    mm = re.search(r"set32_distinct=(\d+)", r["line"])
    if mm:
        cap[m.group(1)]["set32_distinct"].add(mm.group(1))
    mm = re.search(r"set32_t2=\[([^\]]+)\]", r["line"])
    if mm:
        cap[m.group(1)]["t2"].add(mm.group(1))
    mm = re.search(r"n32=(\d+) n64=(\d+) n0=(\d+)", r["line"])
    if mm:
        cap[m.group(1)]["counts"].add(mm.groups())
law["cap40"] = {
    "cells": {k: {"receipts": v["receipts"], "set32_distinct": sorted(v["set32_distinct"]),
                  "t2_uniq": len(v["t2"]), "counts": sorted(v["counts"])}
              for k, v in sorted(cap.items())},
    "distinct_t2_subsets": len({next(iter(v["t2"])) for v in cap.values() if v["t2"]}),
}

# ---- layers ---------------------------------------------------------------
lay = {}
for r in receipts_for(" r95b_order layers "):
    m = re.search(r"k=(\d)", r["line"])
    if not m:
        continue
    lay.setdefault(m.group(1), {"pt_eq_sh": set(), "pt0_t2_eq_sh": set(), "sh_len": set()})
    for key, tgt in (("pt_eq_sh", "pt_eq_sh"), ("pt0_t2_eq_sh", "pt0_t2_eq_sh"), ("sh_len", "sh_len")):
        mm = re.search(rf"\b{key}=([^\s]+)", r["line"])
        if mm:
            lay[m.group(1)][tgt].add(mm.group(1))
law["layers"] = {k: {kk: sorted(vv) for kk, vv in v.items()} for k, v in sorted(lay.items())}

# ---- warm: allocation history --------------------------------------------
warm = {}
for r in receipts_for(" r95b_order warm "):
    m = re.search(r"warm k=(\d+) keep=(\d+)", r["line"])
    lad = re.search(r"ladder=\[([^\]]+)\]", r["line"])
    if m and lad:
        key = f"keep{m.group(1)}" if m.group(2) != "0" else f"k{m.group(1)}"
        warm.setdefault(key, set()).add(lad.group(1))
law["warm"] = {k: {"ladder_uniq": len(v)} for k, v in sorted(warm.items())}

# ---- rigid ----------------------------------------------------------------
rig = [r["line"] for r in receipts_for(" r95b_order rigid")]
law["rigid"] = {"receipts": len(rig), "relpos_uniq": uniq(field(rig, "t10_relpos")),
                "distinct_ticks": uniq(field(rig, "distinct_ticks"))}

# ---- scoutrev -------------------------------------------------------------
sr = [r["line"] for r in receipts_for(" r95b_order scoutrev")]
law["scoutrev"] = {"receipts": len(sr), "t2_matches": uniq(field(sr, "t2_vec_matches_scout_row")),
                   "relpos_equals_canon": uniq(field(sr, "t2_relpos_equals_canon"))}

# ---- procwait instability -------------------------------------------------
pw = [r["line"] for r in receipts_for(" r95b_order procwait")]
law["procwait"] = {"receipts": len(pw), "payloads_uniq": len(set(pw)),
                   "sources": uniq([r["source"] for r in receipts_for(" r95b_order procwait")])}

# ---- env ------------------------------------------------------------------
env = [r["line"] for r in receipts_for(" r95b_order env")]
law["env"] = {"receipts": len(env), "payloads_uniq": len(set(env))}

# ---- cross-batch identity of the stable cells -----------------------------
cells = {}
for s in sources:
    for l in pass_lines(s["text"]):
        if " r95b_order " in l or " dss_lattice " in l:
            # arm key: fixture + arm token + the first distinguishing arg token(s)
            parts = l.split()
            if len(parts) < 3:
                continue
            key = " ".join(parts[2:5])
            cells.setdefault(key, set()).add(l)
law["cross_source_cell_stability"] = {
    "cells": len(cells),
    "multi_payload_cells": {k: len(v) for k, v in sorted(cells.items()) if len(v) > 1},
}

# ---- focused comparisons (canon vs warm/free/celloff) ---------------------
def ladder_of(lines):
    out = []
    for l in lines:
        m = re.search(r"ladder=\[([^\]]+)\]", l)
        if m:
            out.append(m.group(1))
    return uniq(out)


canon_lad = ladder_of([r["line"] for r in receipts_for(" r95b_order canon ")])


def ticks(ladder):
    return dict(p.split(":") for p in ladder.split(";"))


def ladder_equal_on_common(a, b):
    ta, tb = ticks(a), ticks(b)
    common = sorted(set(ta) & set(tb), key=lambda s: int(s[1:]))
    return common, all(ta[t] == tb[t] for t in common)


keep8_lad = ladder_of([r["line"] for r in receipts_for(" r95b_order warm ")
                       if re.search(r"warm k=8 keep=1", r["line"])])
keep64_lad = ladder_of([r["line"] for r in receipts_for(" r95b_order warm ")
                        if re.search(r"warm k=64 keep=1", r["line"])])
warm_free_lads = {k: ladder_of([r["line"] for r in receipts_for(" r95b_order warm ")
                                if re.search(rf"warm k={k} keep=0", r["line"])])
                  for k in (0, 1, 2, 3, 5, 8, 13, 32)}
free_ab = ladder_of([r["line"] for r in receipts_for(" r95b_order free ")
                     if "freed=[a,b]" in r["line"]])
free_ba = ladder_of([r["line"] for r in receipts_for(" r95b_order free ")
                     if "freed=[b,a]" in r["line"]])

# celloff keyed by RECEIPT FILE NAME (the y1000 payload echoes only x=0)
celloff_by_file = {}
for s in sources:
    if s["source"] != "boundary":
        continue
    name = Path(s["path"]).name.split(".rep")[0]
    if not name.startswith("celloff_"):
        continue
    lad = ladder_of(pass_lines(s["text"]))
    if lad:
        celloff_by_file.setdefault(name, set()).update(lad)
celloff_lads = {k: sorted(v) for k, v in sorted(celloff_by_file.items())}

law["comparisons"] = {
    "canon_ladder_uniq": len(canon_lad),
    "warm_freed_cells_equal_to_canon_on_common_ticks": {
        k: ladder_equal_on_common(v[0], canon_lad[0])[1] for k, v in warm_free_lads.items() if v
    },
    "warm_keep8_differs_from_canon": keep8_lad != canon_lad,
    "warm_keep64_differs_from_canon": keep64_lad != canon_lad,
    "keep8_ladder": keep8_lad, "keep64_ladder": keep64_lad,
    "free_ab_ladder": free_ab, "free_ba_ladder": free_ba,
    "free_ab_ne_ba": free_ab != free_ba,
    "celloff_cells": {k: len(v) for k, v in celloff_lads.items()},
    "celloff_distinct_ladders": len({v[0] for v in celloff_lads.values()}),
    "celloff_y1000_ladder_equals_x0": (
        celloff_lads.get("celloff_y1000") == celloff_lads.get("celloff_x0")),
}

OUT.write_text(json.dumps(law, indent=2, sort_keys=True))
print(json.dumps(law, indent=2)[:6000])