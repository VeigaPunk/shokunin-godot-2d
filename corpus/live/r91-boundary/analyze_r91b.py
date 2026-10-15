#!/usr/bin/env python3
"""r91b boundary analyzer — parse receipts, run the claim checks, emit JSON + text.

Reads runs/<cell>.rep<N>.{out,err,rc,wall} written by run_matrix.sh.
Cell-name prefixes encode the condition: q_ quiet, l_ load(16 hogs),
f30_ fixed-fps 30, f120_ fixed-fps 120, f120l_ ff120+load, q2_ quiet repeat.
"""
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
OUT = os.path.join(HERE, "analyze_r91b.json")

CELL_RE = re.compile(r"^([a-z0-9_]+)\.rep(\d+)\.(out|err|rc|wall)$")
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\[[^\]]*\]|\S+)")
PREFIXES = [("f120l_", "ff120load"), ("f120_", "ff120"), ("f30_", "ff30"),
            ("q2_", "quiet2"), ("l_", "load"), ("q_", "quiet")]


def condition(cell):
    for p, name in PREFIXES:
        if cell.startswith(p):
            return name
    return "other"


def base(cell):
    for p, name in PREFIXES:
        if cell.startswith(p):
            return cell[len(p):]
    return cell


def read(path):
    try:
        with open(path, "r", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def parse_pass(out):
    for line in out.splitlines():
        if line.startswith("PASS "):
            return line
    return ""


def fields(line):
    return {k: v for k, v in KV_RE.findall(line)}


def list_field(d, key):
    v = d.get(key, "")
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1]
        return [x for x in inner.split(",") if x != ""]
    return []


def load_cells():
    cells = collections.defaultdict(dict)
    for p in sorted(glob.glob(os.path.join(RUNS, "*"))):
        m = CELL_RE.match(os.path.basename(p))
        if not m:
            continue
        cell, rep, kind = m.group(1), int(m.group(2)), m.group(3)
        cells[cell].setdefault(rep, {})[kind] = p
    return cells


def cell_summary(cell, reps):
    rows = []
    rcs = []
    walls = []
    outs = []
    errs = []
    for rep in sorted(reps):
        r = reps[rep]
        rc = read(r.get("rc", "")).strip()
        wall = read(r.get("wall", "")).strip()
        out = read(r.get("out", ""))
        err = read(r.get("err", ""))
        pl = parse_pass(out)
        rows.append({"rep": rep, "rc": rc, "wall": wall, "pass": pl,
                     "fields": fields(pl), "err_bytes": len(err),
                     "err_has_double_free": "double free or corruption" in err,
                     "err_lines": [l for l in err.splitlines() if l.strip()]})
        rcs.append(rc)
        walls.append(float(wall) if wall else -1.0)
        outs.append(pl)
        errs.append(err)
    return {
        "reps": len(reps),
        "rcs": rcs,
        "walls": walls,
        "out_uniq": len(set(outs)),
        "err_uniq": len(set(errs)),
        "rows": rows,
    }


def collect(data):
    """Flatten parsed field rows for one cell across all conditions."""
    out = []
    for cell, cs in data.items():
        for row in cs["rows"]:
            out.append({"cell": cell, "cond": condition(cell), **row})
    return out


def nums(rows, key):
    vals = []
    for r in rows:
        v = r["fields"].get(key)
        if v is None:
            continue
        try:
            vals.append(int(v))
        except ValueError:
            try:
                vals.append(float(v))
            except ValueError:
                pass
    return vals


def bools(rows, key):
    return [r["fields"].get(key) for r in rows]


def main():
    cells = load_cells()
    data = {c: cell_summary(c, reps) for c, reps in cells.items() if c not in ("rc-summary",)}
    text = []
    p = text.append

    p("r91b boundary analysis")
    p("======================")
    conds = collections.defaultdict(list)
    for c in data:
        conds[condition(c)].append(c)
    for cond in ["quiet", "load", "ff30", "ff120", "ff120load", "quiet2"]:
        if cond in conds:
            p("  %-10s cells=%s" % (cond, ",".join(sorted(conds[cond]))))

    # per-cell table
    p("")
    p("%-14s %-10s %-4s %-9s %-4s %-4s  rc" % ("cell", "cond", "reps", "out_uniq", "err", "wall"))
    for c in sorted(data):
        cs = data[c]
        wall = max(cs["walls"]) if cs["walls"] else -1
        p("%-14s %-10s %-4d %-9d %-4d %5.1f  %s" %
          (c, condition(c), cs["reps"], cs["out_uniq"], cs["err_uniq"], wall, " ".join(cs["rcs"])))

    # ---------------------------------------------------------------- claims
    claims = {}
    allrows = collect(data)

    def rows_for(prefix):
        return [r for r in allrows if base(r["cell"]).startswith(prefix)]

    # C1 sync gate (b_gate)
    g = rows_for("b_gate")
    c1 = {
        "runs": len(g),
        "reach_before_iter2_any": any(r["fields"].get("reach_before_iter2") == "true" for r in g),
        "gate_first_eq_first_reach": all(
            r["fields"].get("gate_first") == r["fields"].get("first_reach") for r in g),
        "first_reach_by_cond": {},
        "first_reach_gt24": [r["cell"] + ".rep" + str(r["rep"]) for r in g
                             if nums([r], "first_reach") and nums([r], "first_reach")[0] > 24],
        "first_reach_none": [r["cell"] + ".rep" + str(r["rep"]) for r in g
                             if r["fields"].get("first_reach") == "-1"],
        "frames_iter2_to_reach": sorted(set(nums(g, "frames_iter2_to_reach"))),
        "async_first_reach_by_cond": {},
        "async_first_reach_none": [r["cell"] + ".rep" + str(r["rep"]) for r in g
                                   if r["fields"].get("async_first_reach") == "-1"],
        "async_first_reach_gt24": [r["cell"] + ".rep" + str(r["rep"]) for r in g
                                   if nums([r], "async_first_reach") and nums([r], "async_first_reach")[0] > 24],
        "async_chg_t_by_cond": {},
        "async_dis_t_by_cond": {},
        "async_old_gone_t_by_cond": {},
        "pf_per_await": sorted(set(nums(g, "pf_per_await"))),
        "proc_per_await": sorted(set(nums(g, "proc_per_await"))),
        "async_pf_per_await": sorted(set(nums(g, "async_pf_per_await"))),
        "async_proc_per_await": sorted(set(nums(g, "async_proc_per_await"))),
    }
    for r in g:
        for key, dest in [("first_reach", "first_reach_by_cond"),
                          ("async_first_reach", "async_first_reach_by_cond"),
                          ("async_chg_t", "async_chg_t_by_cond"),
                          ("async_dis_t", "async_dis_t_by_cond"),
                          ("async_old_gone_t", "async_old_gone_t_by_cond")]:
            c1[dest].setdefault(r["cond"], []).append(r["fields"].get(key))
    claims["sync_gate"] = c1

    # C1b scout sync arm (sv_sync)
    s = rows_for("sv_sync")
    claims["scout_sync"] = {
        "runs": len(s),
        "chg_same": sorted(set(bools(s, "chg_same"))),
        "chg_settled": sorted(set(bools(s, "chg_settled"))),
        "dis_same": sorted(set(bools(s, "dis_same"))),
        "dis_settled": sorted(set(bools(s, "dis_settled"))),
        "first_reach_by_cond": collections.defaultdict(list),
        "first_reach_sync_by_cond": collections.defaultdict(list),
        "ladder_uniq": len(set(r["fields"].get("ladder") for r in s)),
    }
    for r in s:
        claims["scout_sync"]["first_reach_by_cond"][r["cond"]].append(r["fields"].get("first_reach"))
        claims["scout_sync"]["first_reach_sync_by_cond"][r["cond"]].append(r["fields"].get("first_reach_sync"))

    # C2 change application (b_change)
    ch = rows_for("b_change")
    c2 = {"runs": len(ch), "by_cond": {}, "max_t": 0, "not_applied": []}
    for r in ch:
        d = r["fields"]
        ts = {k: d.get(k) for k in ("tr_t", "dis_t", "cost_t", "lay_t", "poly_t", "link_t", "gap_t")}
        for k, v in ts.items():
            if v is None:
                continue
        for k in ts:
            v = ts[k]
            if v == "-1":
                c2["not_applied"].append(r["cell"] + ".rep" + str(r["rep"]) + ":" + k)
            else:
                c2["max_t"] = max(c2["max_t"], int(v))
        c2["by_cond"].setdefault(r["cond"], []).append(
            "tr=%s dis=%s cost=%s lay=%s poly=%s link=%s gap=%s" %
            (ts["tr_t"], ts["dis_t"], ts["cost_t"], ts["lay_t"], ts["poly_t"], ts["link_t"], ts["gap_t"]))
    # stale same-frame reads
    c2["same_frame"] = {
        "tr_same_new": sorted(set(bools(ch, "tr_same_new"))),
        "tr_same_old": sorted(set(bools(ch, "tr_same_old"))),
        "dis_same_reach": sorted(set(bools(ch, "dis_same_reach"))),
        "cost_same": sorted(set(bools(ch, "cost_same"))),
        "lay_same_top": sorted(set(bools(ch, "lay_same_top"))),
        "poly_same_top": sorted(set(bools(ch, "poly_same_top"))),
        "link_same": sorted(set(bools(ch, "link_same"))),
        "gap_same": sorted(set(bools(ch, "gap_same"))),
    }
    claims["change_application"] = c2

    # C3 agent split (b_agent, sv_agent, diag)
    a = rows_for("b_agent")
    sa = rows_for("sv_agent")
    claims["agent_split"] = {
        "b_runs": len(a),
        "b_split_by_cond": collections.defaultdict(list),
        "b_reached_at_by_cond": collections.defaultdict(list),
        "b_fin_at_by_cond": collections.defaultdict(list),
        "b_fin_same_frame": sorted(set(bools(a, "fin_same_frame"))),
        "b_walk_steps": sorted(set(nums(a, "walk_steps"))),
        "b_first_reachable": sorted(set(nums(a, "first_reachable"))),
        "b_b_split_by_cond": collections.defaultdict(list),
        "b_b_walk_steps": sorted(set(nums(a, "b_walk_steps"))),
        "sv_runs": len(sa),
        "sv_reached_at": sorted(set(bools(sa, "reached_at"))),
        "sv_walk_steps": sorted(set(nums(sa, "walk_steps"))),
        "sv_first_reachable": sorted(set(nums(sa, "first_reachable"))),
    }
    for r in a:
        for k, dest in [("split", "b_split_by_cond"), ("reached_at", "b_reached_at_by_cond"),
                        ("fin_at", "b_fin_at_by_cond"), ("b_split", "b_b_split_by_cond")]:
            claims["agent_split"][dest].setdefault(r["cond"], []).append(r["fields"].get(k))
    for v in ("d_v1", "d_v5", "d_v7", "d_v8", "d_v9"):
        rows = rows_for(v)
        claims["agent_split"][v] = {
            "runs": len(rows),
            "reached_at_by_cond": collections.defaultdict(list),
            "fin_same_frame_by_cond": collections.defaultdict(list),
            "note": sorted(set(r["fields"].get("note", "") for r in rows)),
        }
        for r in rows:
            claims["agent_split"][v]["reached_at_by_cond"][r["cond"]].append(r["fields"].get("reached_at"))
            claims["agent_split"][v]["fin_same_frame_by_cond"][r["cond"]].append(r["fields"].get("fin_same_frame"))

    bent = rows_for("d_bent")
    claims["bent_distance"] = {
        "runs": len(bent),
        "dist": sorted(set(r["fields"].get("dist") for r in bent)),
        "plen": sorted(set(r["fields"].get("plen") for r in bent)),
        "delta": sorted(set(r["fields"].get("delta") for r in bent)),
        "dist_eq_straight": sorted(set(r["fields"].get("dist_eq_straight") for r in bent)),
        "plen_eq_L": sorted(set(r["fields"].get("plen_eq_L") for r in bent)),
    }

    # C4 avoidance
    av = rows_for("b_avoid") + rows_for("sv_avoid")
    sums = []
    perframes = []
    for r in av:
        for s in list_field(r["fields"], "sums"):
            try:
                sums.append(float(s))
            except ValueError:
                pass
        for k in ("per_a", "per_b"):
            v = r["fields"].get(k, "")
            if v.startswith("["):
                for x in v[1:-1].split(","):
                    try:
                        perframes.append(int(x.strip()))
                    except ValueError:
                        pass
    claims["avoidance"] = {
        "runs": len(av),
        "sum_min": min(sums) if sums else None,
        "sum_max": max(sums) if sums else None,
        "sum_gt20": [s for s in sums if s > 20.0 + 1e-9],
        "sum_lt198": [s for s in sums if s < 19.8],
        "sum_uniq": len(set(round(s, 4) for s in sums)),
        "perframe_values": sorted(set(perframes)),
        "n_a_values": sorted(set(nums(av, "n_a"))),
        "warm_n_a_values": sorted(set(nums(av, "warm_n_a"))),
        "sum_by_cond": collections.defaultdict(list),
    }
    for r in av:
        for s in list_field(r["fields"], "sums"):
            try:
                claims["avoidance"]["sum_by_cond"][r["cond"]].append(round(float(s), 4))
            except ValueError:
                pass

    # C5 bake
    b = rows_for("b_bake") + rows_for("sv_bake")
    claims["bake"] = {
        "runs": len(b),
        "outline_polys": sorted(set(nums(b, "outline_polys"))),
        "outline_verts": sorted(set(nums(b, "outline_verts"))),
        "baked_polys": sorted(set(nums(b, "baked_polys"))),
        "baked_verts": sorted(set(nums(b, "baked_verts"))),
        "collider_only_polys": sorted(set(nums(b, "collider_only_polys"))),
        "parse_obs": sorted(set(nums(b, "parse_obs"))),
        "parse_trav": sorted(set(nums(b, "parse_trav"))),
        "iter_b": sorted(set(nums(b, "iter_b"))),
        "settle_a": sorted(set(nums(b, "settle_a"))),
        "settle_b": sorted(set(nums(b, "settle_b"))),
        "hole_across_uniq": len(set(r["fields"].get("hole_across") for r in b)),
        "through_uniq": len(set(r["fields"].get("through") for r in b)),
        "orphan_err_any": any("root node needs to be inside the SceneTree" in " ".join(r["err_lines"]) for r in b),
        "deprecation_any": any("make_polygons_from_outlines" in " ".join(r["err_lines"]) for r in b),
    }

    # C6 teardown crash class
    crash = {}
    for cell in sorted(c for c in data if base(c).startswith("c_")):
        cs = data[cell]
        crash[cell] = {
            "rcs": cs["rcs"],
            "double_free": [r["err_has_double_free"] for r in cs["rows"]],
            "survived": ["SURVIVED" in r["pass"] or "survived=1" in r["pass"] for r in cs["rows"]],
            "by_cond": {},
        }
        for r in cs["rows"]:
            crash[cell]["by_cond"].setdefault(condition(cell), []).append(r["rc"])
    for arm in ("navfree2", "navfree5", "navfree6"):
        key = "dc_" + arm
        if key in data:
            cs = data[key]
            crash[key] = {
                "rcs": cs["rcs"],
                "double_free": [r["err_has_double_free"] for r in cs["rows"]],
                "survived": ["SURVIVED" in r["pass"] for r in cs["rows"]],
                "by_cond": {"disc": cs["rcs"]},
            }
    claims["teardown"] = crash

    # C8 paired A/B (default vs ff30/ff60/ff120, interleaved in one window)
    ab = {}
    for i in range(1, 13):
        for var in ("def", "f30", "f60", "f120"):
            cell = "ab%d_%s" % (i, var)
            if cell in data and data[cell]["rows"]:
                row = data[cell]["rows"][0]["fields"]
                ab.setdefault(str(i), {})[var] = {
                    "first_reach": row.get("first_reach"),
                    "first_iter1": row.get("first_iter1"),
                    "first_iter2": row.get("first_iter2"),
                    "async_first_reach": row.get("async_first_reach"),
                    "proc_per_await": row.get("proc_per_await"),
                    "wall": data[cell]["walls"][0] if data[cell]["walls"] else None,
                }
    claims["ab_fixedfps"] = ab

    # C7 fixed-fps effect accounting
    claims["fixed_fps"] = {
        "proc_per_await_by_cond": collections.defaultdict(list),
        "pf_per_await_by_cond": collections.defaultdict(list),
    }
    for r in g:
        claims["fixed_fps"]["proc_per_await_by_cond"][r["cond"]].append(r["fields"].get("proc_per_await"))
        claims["fixed_fps"]["pf_per_await_by_cond"][r["cond"]].append(r["fields"].get("pf_per_await"))

    # json-safe: defaultdicts -> dicts
    def conv(o):
        if isinstance(o, collections.defaultdict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, list):
            return [conv(v) for v in o]
        return o

    with open(OUT, "w") as f:
        json.dump(conv({"cells": data, "claims": claims}), f, indent=1, sort_keys=True)
    p("")
    p("json -> %s" % OUT)

    # compact claim summary for stdout
    p("")
    p("== claim summary ==")
    p(json.dumps(conv(claims), indent=1, sort_keys=True)[:12000])
    text.append("")
    with open(os.path.join(HERE, "analysis.txt"), "w") as f:
        f.write("\n".join(text) + "\n")
    print("\n".join(text))


if __name__ == "__main__":
    main()
