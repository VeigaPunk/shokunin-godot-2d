#!/usr/bin/env python3
"""r95 reviewer static audit — committed bytes only (9cd47507).

Checks, all against `git show 9cd47507:...` (never the dirty worktree):
  S1  diff scope: pure insertion, zero deletions, CASES 307 -> 359, names unique
  S2  r95 row shapes: 5-tuples, types, arms implemented in the landed fixtures
  S3  dss_lattice 17 signatures == scout ROWS_PREFIX element-wise (case/script/
      flags/exit/signature); the 13 full rows == ROWS full line; the 4 prefix
      rows cut before the first order vector at a token boundary
  S4  r95b_order 35 signatures == whole PASS lines in the boundary receipts
  S5  allowlists: expected_errors / required_stderr carry no r95 keys
  S6  gate: r95_expected_errors_all_matched present and prefix-covering
  S7  provenance: landed fixtures byte-identical to the frozen probes; sha256s
  S8  no refuted keys / no procwait / no env in any r95 signature
"""
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
HEAD = "9cd47507"
PARENT = "6f817d10"
OUT = REPO / "corpus/live/r95-reviewer/audit_static.json"


def git_show(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], cwd=REPO,
                          capture_output=True, text=True, check=True).stdout


def parse_cases(text):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("CASES not found")


def parse_named_list(text, name):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit(f"{name} not found")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def main():
    res = {}
    head_text = git_show(HEAD, "corpus/fixtures/run_battery.py")
    parent_text = git_show(PARENT, "corpus/fixtures/run_battery.py")
    head = parse_cases(head_text)
    parent = parse_cases(parent_text)

    # ---- S1 diff shape -------------------------------------------------
    head_names = [c[0] for c in head]
    r95 = [c for c in head if c[0].startswith(("dss_lattice_", "r95b_order_"))]
    prefix_len = 0
    while prefix_len < min(len(head), len(parent)) and head[prefix_len] == parent[prefix_len]:
        prefix_len += 1
    suffix_len = 0
    while (suffix_len < min(len(head), len(parent)) - prefix_len
           and head[-1 - suffix_len] == parent[-1 - suffix_len]):
        suffix_len += 1
    inserted = head[prefix_len:len(head) - suffix_len]
    res["S1"] = {
        "parent_cases": len(parent), "head_cases": len(head),
        "delta": len(head) - len(parent),
        "common_prefix": prefix_len, "common_suffix": suffix_len,
        "inserted_count": len(inserted),
        "inserted_all_r95": all(c[0].startswith(("dss_lattice_", "r95b_order_")) for c in inserted),
        "inserted_is_exactly_r95_block": sorted(inserted) == sorted(r95),
        "parent_rows_field_identical": (
            all(head[i] == parent[i] for i in range(prefix_len))
            and all(head[i + len(inserted)] == parent[i]
                    for i in range(len(parent) - suffix_len, len(parent)))),
        "names_unique": len(set(head_names)) == len(head_names),
        "all_5_tuples": all(isinstance(c, tuple) and len(c) == 5 for c in head),
        "r95_count": len(r95),
        "r95_exit_codes": sorted({c[3] for c in r95}),
        "r95_scripts": sorted({c[1] for c in r95}),
        "insert_after": head[prefix_len - 1][0] if prefix_len else None,
        "insert_before": head[prefix_len + len(inserted)][0] if len(head) > prefix_len + len(inserted) else None,
    }

    # ---- S2 arms implemented in the landed fixtures --------------------
    arm_ok, arm_missing = [], []
    dispatch = {}
    for script in ("dss_lattice.gd", "r95b_order.gd"):
        text = git_show(HEAD, f"corpus/fixtures/{script}")
        m = re.search(r"match arm:\n((?:\t\t\".*?\":.*\n)+)", text)
        arms = set(re.findall(r'"(.*?)":', m.group(1))) if m else set()
        dispatch[script] = sorted(arms)
    for c in r95:
        flags = c[2]
        arm = next((f.split("=", 1)[1] for f in flags if f.startswith("--arm=")), None)
        (arm_ok if arm in dispatch[c[1]] else arm_missing).append(c[0])
    res["S2"] = {"arms_ok": len(arm_ok), "arms_missing": arm_missing,
                 "dispatch": dispatch}

    # ---- S3 scout rows ------------------------------------------------
    scout_txt = (REPO / "corpus/live/r95-scout/author-rows.py.txt").read_text()
    rows = parse_named_list(scout_txt, "ROWS")
    rows_prefix = parse_named_list(scout_txt, "ROWS_PREFIX")
    rows_by_name = {r[0]: r for r in rows}
    prefix_by_name = {r[0]: r for r in rows_prefix}
    dss = [c for c in r95 if c[0].startswith("dss_lattice_")]
    vector_cells = {"dss_lattice_point_cap", "dss_lattice_point_cap_rev",
                    "dss_lattice_order_core", "dss_lattice_order_core_rev"}
    s3 = {"count": len(dss), "prefix_equal": [], "full_equal": [], "prefix_of_full": [],
          "cut_at_token_boundary": [], "prefix_shorter": []}
    for c in dss:
        name = c[0]
        s3["prefix_equal"].append(name in prefix_by_name and tuple(c) == tuple(prefix_by_name[name]))
        s3["full_equal"].append(name in rows_by_name and tuple(c) == tuple(rows_by_name[name]))
        full_sig = rows_by_name[name][4]
        sig = c[4]
        s3["prefix_of_full"].append(full_sig.startswith(sig))
        if name in vector_cells:
            rest = full_sig[len(sig):]
            s3["cut_at_token_boundary"].append(rest.startswith(" "))
            s3["prefix_shorter"].append(len(sig) < len(full_sig))
    s3 = {k: (sum(v) if isinstance(v, list) and v and isinstance(v[0], bool) else v)
          for k, v in s3.items()}
    s3["all_prefix_equal"] = s3.pop("prefix_equal") == len(dss)
    s3["all_full_equal"] = s3.pop("full_equal") == len(dss)
    s3["full_equal_cells"] = sorted(n for n in (c[0] for c in dss) if n not in vector_cells)
    s3["prefix_only_cells"] = sorted(vector_cells)
    s3["all_prefix_of_full"] = s3.pop("prefix_of_full") == len(dss)
    s3["all_cut_at_token_boundary"] = s3.pop("cut_at_token_boundary") == len(vector_cells)
    s3["all_prefix_shorter"] = s3.pop("prefix_shorter") == len(vector_cells)
    res["S3"] = s3

    # ---- S4 r95b rows vs boundary receipts -----------------------------
    boundary_runs = REPO / "corpus/live/r95-boundary/runs"
    r95b = [c for c in r95 if c[0].startswith("r95b_order_")]
    s4 = {"rows": [], "receipts_scanned": 0, "whole_line_hits": 0, "per_cell": {}}
    for c in r95b:
        sig = c[4]
        assert sig.startswith("PASS r95b_order "), c[0]
        cell = c[0].removeprefix("r95b_order_")
        hits, misses, total = 0, [], 0
        batches = []
        for batch in sorted(boundary_runs.iterdir()):
            if not batch.is_dir():
                continue
            files = sorted(batch.glob(f"{cell}.rep*.out"))
            if files:
                batches.append((batch.name, len(files)))
            for out in files:
                total += 1
                lines = out.read_text().splitlines()
                if sig in lines:
                    hits += 1
                elif any(line.startswith(sig) for line in lines):
                    misses.append((str(out.relative_to(boundary_runs)), "prefix-only"))
                else:
                    misses.append((str(out.relative_to(boundary_runs)), "absent"))
        s4["rows"].append({"case": c[0], "cell": cell, "receipts": total,
                           "whole_line_hits": hits, "batches": batches,
                           "misses": misses})
        s4["receipts_scanned"] += total
        s4["whole_line_hits"] += hits
        s4["per_cell"][c[0]] = {
            "receipts": total, "hits": hits, "batches": dict(batches),
            "payload_uniq": len({out.read_text().splitlines()[-1]
                                 for batch in boundary_runs.iterdir()
                                 if batch.is_dir()
                                 for out in batch.glob(f"{cell}.rep*.out")})}
    s4["all_whole_line"] = s4["receipts_scanned"] == s4["whole_line_hits"]
    s4["cells_with_zero_receipts"] = [c["case"] for c in s4["rows"] if c["receipts"] == 0]
    s4["cells_multi_payload"] = [c for c, v in s4["per_cell"].items()
                                 if v["receipts"] and v["payload_uniq"] != 1]
    res["S4"] = s4

    # ---- S4b dss_lattice 17 vs scout receipts --------------------------
    scout_runs = REPO / "corpus/live/r95-scout/runs"
    dss = [c for c in r95 if c[0].startswith("dss_lattice_")]
    # case -> scout receipt cell (canonical names use the r95_dss_ prefix; the
    # two shape cells are shape_lattice[_rev]; loadtest receipts drop r95_).
    cell_map = {c[0]: c[0].replace("dss_lattice_", "r95_dss_") for c in dss}
    cell_map["dss_lattice_shape"] = "r95_dss_shape_lattice"
    cell_map["dss_lattice_shape_rev"] = "r95_dss_shape_lattice_rev"
    s4b = {"rows": [], "canonical_hits": 0, "canonical_total": 0,
           "loadtest_hits": 0, "loadtest_total": 0}
    for c in dss:
        sig = c[4]
        cell = cell_map[c[0]]
        canon = sorted(scout_runs.glob(f"{cell}.rep*.out"))
        load = sorted((scout_runs / "loadtest").glob(
            f"{cell.replace('r95_dss_', 'dss_')}.rep*.out"))
        ch = sum(1 for out in canon if sig in out.read_text())
        lh = sum(1 for out in load if sig in out.read_text())
        s4b["rows"].append({"case": c[0], "cell": cell, "canonical": len(canon),
                            "canonical_hits": ch, "loadtest": len(load),
                            "loadtest_hits": lh})
        s4b["canonical_hits"] += ch
        s4b["canonical_total"] += len(canon)
        s4b["loadtest_hits"] += lh
        s4b["loadtest_total"] += len(load)
    s4b["all_canonical"] = s4b["canonical_hits"] == s4b["canonical_total"]
    s4b["all_loadtest"] = s4b["loadtest_hits"] == s4b["loadtest_total"]
    # prefix rows must NOT be whole lines (the unpinned vector text follows)
    prefix_rows = []
    for c in dss:
        sig = c[4]
        cell = cell_map[c[0]]
        receipts = sorted(scout_runs.glob(f"{cell}.rep*.out"))
        if receipts:
            out_lines = receipts[0].read_text().splitlines()
            whole = sig in out_lines
            pref = any(line.startswith(sig) and line != sig for line in out_lines)
            prefix_rows.append({"case": c[0], "whole_line": whole, "strict_prefix": pref})
    s4b["prefix_rows"] = prefix_rows
    s4b["prefix_rows_strict"] = [r for r in prefix_rows if r["strict_prefix"]]
    s4b["prefix_rows_full_line"] = [r for r in prefix_rows if r["whole_line"]]
    res["S4b"] = s4b

    # ---- S5 allowlists (AST: the expected_errors / required_stderr dicts) --
    tree = ast.parse(head_text)

    def find_dict_with_key(tree_, key):
        best = None
        for node in ast.walk(tree_):
            if isinstance(node, ast.Dict):
                ks = [k.value for k in node.keys
                      if isinstance(k, ast.Constant) and isinstance(k.value, str)]
                if key in ks:
                    if best is None or len(ks) > len(best[0]):
                        best = (ks, node)
        return best

    ee_keys, _ = find_dict_with_key(tree, "negative_overlap")
    rs_keys, _ = find_dict_with_key(tree, "nav_lattice_teardown_crash")
    rs_keys = rs_keys or []
    res["S5"] = {
        "expected_errors_keys": len(ee_keys),
        "r95_keys": [k for k in ee_keys if k.startswith(("dss_lattice_", "r95b_order_"))],
        "orphan_keys": [k for k in ee_keys if k not in head_names],
        "required_stderr_keys": len(rs_keys),
        "required_stderr_r95_keys": [k for k in rs_keys
                                     if k.startswith(("dss_lattice_", "r95b_order_"))],
        "r95_mentions_in_allowlists": len(re.findall(
            r'"(dss_lattice_|r95b_order_)[^"]*":', head_text)),
    }

    # ---- S6 gate -------------------------------------------------------
    gate = re.search(r'"r95_expected_errors_all_matched": all\((.*?)\n\s*\}', head_text, re.S)
    res["S6"] = {
        "gate_present": bool(gate),
        "gate_covers_both_prefixes": bool(gate) and '("dss_lattice_", "r95b_order_")' in gate.group(1),
        "gate_shape_same_as_r94": bool(re.search(
            r'"r94_expected_errors_all_matched": all\(', head_text)),
        "gate_count": len(re.findall(r'"\w+_expected_errors_all_matched": all\(', head_text)),
    }

    # ---- S7 provenance -------------------------------------------------
    prov = {}
    for script, frozen in (("dss_lattice.gd", "corpus/live/r95-scout/probes/dss_lattice.gd"),
                           ("r95b_order.gd", "corpus/live/r95-boundary/probes/r95b_order.gd")):
        committed = git_show(HEAD, f"corpus/fixtures/{script}").encode()
        frozen_bytes = (REPO / frozen).read_bytes()
        prov[script] = {
            "committed_sha256": sha256_bytes(committed),
            "frozen_path": frozen,
            "frozen_sha256": sha256_bytes(frozen_bytes),
            "byte_identical": committed == frozen_bytes,
            "lines": committed.decode().count("\n") + 1,
        }
    parent_proj = git_show(PARENT, "corpus/fixtures/project.godot")
    head_proj = git_show(HEAD, "corpus/fixtures/project.godot")
    prov["project_godot"] = {
        "unchanged": parent_proj == head_proj,
        "sha256": sha256_bytes(head_proj.encode()),
        "physics_tps_override": "physics_ticks_per_second" in head_proj,
    }
    res["S7"] = prov

    # ---- S8 refuted keys / unstable cells ------------------------------
    bad = ["layout_changes_order", "procwait", "env", "pile_b=", "pile_rev=",
           "repeat_stable", "instance_id", "RID("]
    res["S8"] = {k: sum(1 for c in r95 if k in c[4]) for k in bad}

    # ---- S9 duplicate signatures + the celloff --offy audit -------------
    import collections
    by_sig = collections.defaultdict(list)
    for c in r95:
        by_sig[c[4]].append(c[0])
    dups = {k: v for k, v in by_sig.items() if len(v) > 1}
    r95b_src = git_show(HEAD, "corpus/fixtures/r95b_order.gd")
    celloff_src = re.search(r"func _arm_celloff\(\) -> void:\n(.*?)\n\n", r95b_src, re.S)
    res["S9"] = {
        "duplicate_signature_pairs": {v[0] + "==" + v[1]: k[:80] for k, v in dups.items()},
        "celloff_offy_occurrences_in_fixture": r95b_src.count("offy"),
        "celloff_flags": {c[0]: c[2] for c in r95
                          if c[0].startswith("r95b_order_celloff")},
        "celloff_arm_reads_off_only": bool(celloff_src)
        and "_opt_float(\"off\"" in celloff_src.group(1)
        and "offy" not in celloff_src.group(1),
        "celloff_arm_source": celloff_src.group(1).strip() if celloff_src else None,
    }

    OUT.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
