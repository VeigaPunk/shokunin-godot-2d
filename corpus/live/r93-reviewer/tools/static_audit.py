#!/usr/bin/env python3
"""r93-reviewer static audit of the committed landing (4b75151) vs its parent
(d9edb72):

  S1  pure-insertion check of CASES (common prefix/suffix, 5-tuples, unique names)
  S2  classifier segment identity vs the r89-r92 recorded sha
  S3  r93 row shape: script exists, flag == one --arm=<name>, expected exit 0,
      signature str (or tuple), arm implemented by the named fixture
  S4  allowlists: zero r93 expected_errors / required_stderr entries; gate
      r93_expected_errors_all_matched covers the r93_ prefix; no orphan r93 keys
  S5  fixture provenance: pinned fixture shas vs the frozen scout/boundary probes
  S6  fixture-side arm inventory vs the rows' arms (dead-arm scan)
"""
import hashlib
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ufo_r93

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
PARENT = ROOT / "corpus/live/r93-reviewer/tools/parent_run_battery.py"
PINNED = ROOT / "corpus/live/r93-reviewer/pinned"
R92_SEG_SHA = "749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3"
FROZEN_SCOUT = ROOT / "corpus/live/r93-scout/probes/anim_lattice.gd"
FROZEN_BOUNDARY = ROOT / "corpus/live/r93-boundary/probes/r93b_anim.gd"


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    out = {}
    if not PARENT.exists():
        PARENT.write_bytes(subprocess.run(
            ["git", "show", "d9edb72:corpus/fixtures/run_battery.py"],
            cwd=ROOT, capture_output=True, check=True).stdout)
    Cp = ufo_r93.load(PARENT)
    Cc = ufo_r93.load(PINNED / "run_battery.py")
    out["parent_src_sha"] = Cp["src_sha"]
    out["committed_src_sha"] = Cc["src_sha"]

    # ---- S1 pure insertion
    a, b = Cp["order"], Cc["order"]
    pre = 0
    while pre < min(len(a), len(b)) and a[pre] == b[pre]:
        pre += 1
    suf = 0
    while suf < min(len(a) - pre, len(b) - pre) and a[len(a) - 1 - suf] == b[len(b) - 1 - suf]:
        suf += 1
    inserted = b[pre:len(b) - suf]
    out["S1"] = {"parent_cases": len(a), "committed_cases": len(b),
                 "common_prefix": pre, "common_suffix": suf,
                 "inserted": inserted, "inserted_n": len(inserted),
                 "all_5_tuples": all(len(Cc["cases"][k]["flags"]) is not None for k in b),
                 "unique_names": len(set(b)) == len(b)}
    # every committed case is a 5-tuple by construction of the loader; verify raw
    import ast
    tree = Cc["tree"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            tup_ok = all(isinstance(e, ast.Tuple) and len(e.elts) == 5 for e in node.value.elts)
            out["S1"]["all_5_tuples"] = tup_ok

    # ---- S2 classifier identity
    out["S2"] = {"seg_sha": Cc["seg_sha"], "matches_r89_r92": Cc["seg_sha"] == R92_SEG_SHA}

    # ---- S3 row shape
    rows = {k: v for k, v in Cc["cases"].items() if k.startswith("r93_")}
    scripts = {r["script"] for r in rows.values()}
    arms = {}
    for k, r in sorted(rows.items()):
        flag_arms = [f.removeprefix("--arm=") for f in r["flags"] if f.startswith("--arm=")]
        arms.setdefault(r["script"], set()).update(flag_arms)
        assert len(flag_arms) == 1, (k, r["flags"])
    fixture_arms = {}
    for s in scripts:
        txt = (PINNED / s).read_text()
        arms_in_match = set()
        in_match = False
        for line in txt.splitlines():
            st = line.strip()
            if st.startswith("match arm:"):
                in_match = True
                continue
            if in_match:
                if st.startswith('"') and '":' in st:
                    arms_in_match.add(st.split('"')[1])
                elif st.startswith("_"):
                    in_match = False
        fixture_arms[s] = sorted(arms_in_match)
    out["S3"] = {"rows": len(rows), "scripts": sorted(scripts),
                 "arm_flags": {s: sorted(a) for s, a in arms.items()},
                 "expected_exit_zero": all(r["expected_exit"] == 0 for r in rows.values()),
                 "signature_is_str_or_tuple": all(
                     isinstance(r["signature"], (str, tuple, list)) for r in rows.values()),
                 "declared_arms": fixture_arms,
                 "dead_arms": sorted(set().union(*arms.values()) - set().union(*fixture_arms.values()))}

    # ---- S4 allowlists + gate
    out["S4"] = {"r93_expected_errors": Cc["exp_err"],
                 "r93_required_stderr": Cc["req_err"],
                 "gate_present": '"r93_expected_errors_all_matched"' in Cc["src"],
                 "gate_covers_prefix": 'r["case"].startswith("r93_")' in Cc["src"],
                 "orphan_r93_allowlist_keys": sorted(
                     set(k for k in Cc["exp_err_all"] if k.startswith("r93_")) - set(rows)),
                 "all_allowlist_keys_are_cases": sorted(set(Cc["exp_err_all"]) - set(Cc["cases"]))}

    # ---- S5 provenance
    out["S5"] = {
        "anim_lattice_pinned": sha(PINNED / "anim_lattice.gd"),
        "anim_lattice_frozen_scout": sha(FROZEN_SCOUT) if FROZEN_SCOUT.exists() else None,
        "r93b_pinned": sha(PINNED / "r93b_anim.gd"),
        "r93b_frozen_boundary": sha(FROZEN_BOUNDARY) if FROZEN_BOUNDARY.exists() else None,
    }
    out["S5"]["anim_byte_copy"] = out["S5"]["anim_lattice_pinned"] == out["S5"]["anim_lattice_frozen_scout"]
    out["S5"]["r93b_byte_copy"] = out["S5"]["r93b_pinned"] == out["S5"]["r93b_frozen_boundary"]

    # ---- S6 author-claimed counts in the report
    rep = (ROOT / "reports/round-93/r93-author.md").read_text()
    out["S6"] = {"report_mentions_23_rows": "23 rows" in rep,
                 "report_mentions_295": "295" in rep}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
