#!/usr/bin/env python3
"""r95 critic: verify the author's report claims against the committed artifacts
(no godot needed) — provenance, row arithmetic, token/claim arithmetic, and the
specific numbers quoted in reports/round-95/r95-author.md."""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SEAT = ROOT / "corpus" / "live" / "r95-critic"
FZ = SEAT / "frozen" / "corpus" / "fixtures"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cases(src):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "CASES":
                    return ast.literal_eval(node.value)


def main():
    rows = json.loads((SEAT / "scripts" / "rows.json").read_text())["r95_rows"]
    sig = {r["case"]: r["sig"] for r in rows}
    out = {}

    # 1 provenance
    out["sha256"] = {
        "dss_lattice.gd": sha(FZ / "dss_lattice.gd"),
        "dss_lattice.gd_claimed": "77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627",
        "dss_lattice.gd_scout_probe": sha(ROOT / "corpus/live/r95-scout/probes/dss_lattice.gd"),
        "r95b_order.gd": sha(FZ / "r95b_order.gd"),
        "r95b_order.gd_claimed": "4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490",
        "r95b_order.gd_boundary_probe": sha(ROOT / "corpus/live/r95-boundary/probes/r95b_order.gd"),
    }
    out["provenance_ok"] = (
        out["sha256"]["dss_lattice.gd"] == out["sha256"]["dss_lattice.gd_claimed"]
        == out["sha256"]["dss_lattice.gd_scout_probe"]
        and out["sha256"]["r95b_order.gd"] == out["sha256"]["r95b_order.gd_claimed"]
        == out["sha256"]["r95b_order.gd_boundary_probe"])

    # 2 row arithmetic / prefix rows
    prefix_rows = [c for c in sig if c in ("dss_lattice_point_cap", "dss_lattice_point_cap_rev",
                                           "dss_lattice_order_core", "dss_lattice_order_core_rev")]
    out["prefix_rows"] = sorted(prefix_rows)
    out["prefix_rows_count"] = len(prefix_rows)
    out["dss_rows"] = sum(1 for c in sig if c.startswith("dss_lattice_"))
    out["order_rows"] = sum(1 for c in sig if c.startswith("r95b_order_"))
    out["total_rows"] = len(sig)

    # 3 token scan of the r95 CASES block only
    head = (FZ / "run_battery.py").read_text()
    block = "\n".join(head.splitlines()[877:878 + 152])
    out["token_scan"] = {t: (t in "\n".join(f"{c} {s}" for c, s in sig.items()))
                         for t in ("procwait", "env", "layout_changes_order", "instance_id", "RID(")}
    out["block_contains_case_names"] = sorted(re.findall(r"\('(r95b_order_[a-z0-9_]+|dss_lattice_[a-z0-9_]+)'", block))

    # 4 perm distinctness (t2_relpos + ladder)
    perms = {c: sig[c] for c in sig if c.startswith("r95b_order_perm")}
    t2 = {c: re.search(r"t2_relpos=(\[[^\]]*\])", s).group(1) for c, s in perms.items()}
    lad = {c: re.search(r"ladder=(\[.*?\]) distinct_ticks", s).group(1) for c, s in perms.items()}
    out["perm_t2_distinct"] = len(set(t2.values()))
    out["perm_ladder_distinct"] = len(set(lad.values()))
    out["perm_t2"] = t2

    # 5 cap40 distinctness
    caps = {c: sig[c] for c in sig if c.startswith("r95b_order_cap40_")}
    out["cap40_set32_t2_distinct"] = len({re.search(r"set32_t2=(\[.*?\]) n32", s).group(1) for s in caps.values()})
    out["cap40_counts"] = {c: re.findall(r"n32=(\d+) n64=(\d+) n0=(\d+)", s)[0] for c, s in caps.items()}
    out["cap40_set32_distinct"] = {c: re.search(r"set32_distinct=(\d+)", s).group(1) for c, s in caps.items()}

    # 6 periodx law arithmetic in the pinned bytes
    per = {c: sig[c] for c in sig if c.startswith("r95b_order_periodx_")}
    out["periodx"] = {c: re.search(r"k=(\d+) spacing=([\d.]+) cycle_len=(-?\d+) expected_kk1=(\d+) distinct_ticks=(\d+) n_ticks=(\d+)", s).groups()
                      for c, s in per.items()}
    out["periodx_law_holds_in_pinned_bytes"] = all(
        int(g[2]) == int(g[3]) == int(g[0]) * (int(g[0]) - 1) for g in out["periodx"].values())

    # 7 canon ladder structure from the pinned bytes
    canon = sig["r95b_order_canon"]
    ladder = re.search(r"ladder=(\[.*?\]) distinct_ticks", canon).group(1)
    pairs = dict((p.split(":")[0], p.split(":")[1]) for p in ladder[1:-1].split(";"))
    out["canon_t0"] = pairs["t0"]
    out["canon_t20"] = pairs["t20"]
    out["canon_t20_eq_t0"] = pairs["t20"] == pairs["t0"]
    out["canon_distinct_ticks"] = re.search(r"distinct_ticks=(\d+)", canon).group(1)

    # 8 harness hygiene: expected_errors / required_stderr r95 keys
    for name in ("EXPECTED_ERRORS", "REQUIRED_STDERR"):
        m = re.search(rf"^{name} = \{{", head, re.M)
        if not m:
            m = re.search(rf"^\s*{name} = \{{", head, re.M)
        out[f"{name}_found"] = bool(m)
    out["r95_in_expected_errors"] = bool(re.search(r"['\"](?:dss_lattice_|r95b_order_)", head))
    out["gate_name_present"] = "r95_expected_errors_all_matched" in head

    # 9 fixture write-surface
    for fx in ("dss_lattice.gd", "r95b_order.gd"):
        text = (FZ / fx).read_text()
        out[f"{fx}_write_surface"] = {t: text.count(t) for t in
                                      ("FileAccess", "DirAccess", "ResourceSaver", "OS.execute", "OS.create_process")}

    # 10 receipt counts
    def count(pattern, base):
        return len(list(base.rglob(pattern)))
    scout = ROOT / "corpus/live/r95-scout/runs"
    bnd = ROOT / "corpus/live/r95-boundary/runs"
    out["scout_out_maxdepth1"] = len(list(scout.glob("*.out")))
    out["scout_out_loadtest"] = len(list((scout / "loadtest").glob("*.out")))
    out["scout_out_all"] = count("*.out", scout)
    out["boundary_out"] = count("*.out", bnd)
    out["boundary_batches"] = sorted(p.name for p in bnd.iterdir() if p.is_dir())

    (SEAT / "scripts" / "claims.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
