#!/usr/bin/env python3
"""r69-baseline receipt diff: per-receipt tuple comparison vs r68 references.

Method (r62-r68 verifier precedent): CASES rows compared on the tuple
(script, flags, expected_exit, actual_exit, signature, verdict, error)
indexed by `case`; meta rows on verdict + discriminations bool-map equality.
Volatile fields (command/scratch/xdg_data_home/artifact/elapsed_seconds/
pids/shas) are outside the compared scope.
"""
import json, sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
MINE = ROOT / "corpus/live/r69-baseline/runs"
TUPLE_FIELDS = ("script", "flags", "expected_exit", "actual_exit",
                "signature", "verdict", "error")


def load(p):
    return json.loads(Path(p).read_text())


def rows_by_case(v):
    return {r["case"]: r for r in v["results"]}


def tuple_of(r):
    return tuple(json.dumps(r.get(f), sort_keys=True) for f in TUPLE_FIELDS)


def meta_sig(r):
    d = r.get("discriminations")
    return (r.get("verdict"), json.dumps(d, sort_keys=True) if isinstance(d, dict) else None)


def compare(mine_v, ref_v):
    m, r = rows_by_case(mine_v), rows_by_case(ref_v)
    common = sorted(set(m) & set(r))
    mism = []
    for c in common:
        a, b = m[c], r[c]
        if tuple_of(a) != tuple_of(b):
            mism.append((c, {f: (a.get(f), b.get(f)) for f in TUPLE_FIELDS
                             if a.get(f) != b.get(f)}))
        if meta_sig(a) != meta_sig(b):
            mism.append((c + " [meta]", {"mine": meta_sig(a), "ref": meta_sig(b)}))
    return common, sorted(set(m) - set(r)), sorted(set(r) - set(m)), mism


VOLATILE = {"command", "scratch", "xdg_data_home", "artifact",
            "elapsed_seconds", "descendant_pid", "godot_pid", "write_ppid",
            "pid", "artifact_sha256", "artifact_bytes", "seed", "scratch_sha256"}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o


def deep_diff(a, b, path=""):
    """Yield (path, a_val, b_val) for stripped-structure differences."""
    if type(a) is not type(b):
        yield (path, a, b); return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                yield (f"{path}/{k}", "<absent>", b[k])
            elif k not in b:
                yield (f"{path}/{k}", a[k], "<absent>")
            else:
                yield from deep_diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            yield (f"{path}/len", len(a), len(b)); return
        for i, (x, y) in enumerate(zip(a, b)):
            yield from deep_diff(x, y, f"{path}[{i}]")
    elif a != b:
        yield (path, a, b)


def main():
    mine = {
        "flagless88": load(MINE / "20261014T122503087808Z/verdicts.json"),
        "attrib89": load(MINE / "20261014T122618530700Z/verdicts.json"),
        "ladder89": load(MINE / "20261014T122741902523Z/verdicts.json"),
    }
    refs = {
        # tracked (committed) receipts
        "r68-scribe flagless88 [tracked]": "corpus/live/r68-scribe/runs-flagless/20261014T112326985567Z/verdicts.json",
        "r68-simplifier landed88 [tracked]": "corpus/live/r68-simplifier/runs-landed/20261014T112132992259Z/verdicts.json",
        "r68-boundary runs2 90 [tracked]": "corpus/live/r68-boundary/runs2/20261014T112024144893Z/verdicts.json",
        "r68-simplifier landed90 [tracked]": "corpus/live/r68-simplifier/runs-landed/20261014T112415928385Z/verdicts.json",
        "r68-simplifier vA 90 [tracked]": "corpus/live/r68-simplifier/del-measure/vA-runs/20261014T113237288715Z/verdicts.json",
        "r68-simplifier vB 90 [tracked]": "corpus/live/r68-simplifier/del-measure/vB-runs/20261014T113401334628Z/verdicts.json",
        "r68-simplifier vC 90 [tracked]": "corpus/live/r68-simplifier/del-measure/vC-runs/20261014T113534434175Z/verdicts.json",
        # cited in committed r68 reports but untracked on disk
        "r68-verifier flagless88 [cited]": "corpus/live/r68-verifier/runs/20261014T113409881703Z/verdicts.json",
        "r68-verifier attrib89 [cited]": "corpus/live/r68-verifier/runs/20261014T113649697385Z/verdicts.json",
        "r68-verifier ladder89 [cited]": "corpus/live/r68-verifier/runs/20261014T113804001922Z/verdicts.json",
        "integ-r68 90 [untracked]": "corpus/live/integ-r68/runs/20261014T114450090576Z/verdicts.json",
    }
    for rn, rp in refs.items():
        rv = load(ROOT / rp)
        for mn, mv in mine.items():
            common, new_only, old_only, mism = compare(mv, rv)
            print(f"{mn} vs {rn}: ref_rows={len(rv['results'])} common={len(common)} "
                  f"new_only={new_only} old_only={old_only} mismatches={len(mism)}")
            for c, d in mism:
                print(f"    MISMATCH {c}: {json.dumps(d)[:400]}")

    print("\n=== stream-attribution artifact deep-diff (volatile-stripped) ===")
    mine_sa = load(MINE / "20261014T122618530700Z/stream-attribution-verdicts.json")
    for rn, rp in {
        "r68-boundary runs2 [tracked]": "corpus/live/r68-boundary/runs2/20261014T112024144893Z/stream-attribution-verdicts.json",
        "r68-simplifier landed90 [tracked]": "corpus/live/r68-simplifier/runs-landed/20261014T112415928385Z/stream-attribution-verdicts.json",
        "r68-verifier attrib89 [cited]": "corpus/live/r68-verifier/runs/20261014T113649697385Z/stream-attribution-verdicts.json",
        "integ-r68 90 [untracked]": "corpus/live/integ-r68/runs/20261014T114450090576Z/stream-attribution-verdicts.json",
    }.items():
        diffs = list(deep_diff(strip(mine_sa), strip(load(ROOT / rp))))
        print(f"vs {rn}: {len(diffs)} diffs")
        for d in diffs[:15]:
            print("   ", d)

    print("\n=== midlineforge-ladder artifact comparison ===")
    mine_lad = load(MINE / "20261014T122741902523Z/midlineforge-ladder-verdicts.json")
    mw = mine_lad["measured_window"]
    print(f"mine: verdict={mine_lad['verdict']} window landed={mw['landed_offsets_ms']} "
          f"mixed={mw['mixed_offsets_ms']} missed={mw['missed_offsets_ms']} "
          f"lo={mw['lo_edge_ms']} hi={mw['hi_edge_ms']} gap={mw['nominal_gap_ms']}")
    print(f"mine discs: {json.dumps(mine_lad['discriminations'], sort_keys=True)}")
    for rn, rp in {
        "r68-boundary runs2 [tracked]": "corpus/live/r68-boundary/runs2/20261014T112024144893Z/midlineforge-ladder-verdicts.json",
        "r68-simplifier landed90 [tracked]": "corpus/live/r68-simplifier/runs-landed/20261014T112415928385Z/midlineforge-ladder-verdicts.json",
        "r68-simplifier vC [tracked]": "corpus/live/r68-simplifier/del-measure/vC-runs/20261014T113534434175Z/midlineforge-ladder-verdicts.json",
        "r68-verifier ladder89 [cited]": "corpus/live/r68-verifier/runs/20261014T113804001922Z/midlineforge-ladder-verdicts.json",
        "integ-r68 [untracked]": "corpus/live/integ-r68/runs/20261014T114450090576Z/midlineforge-ladder-verdicts.json",
    }.items():
        rv = load(ROOT / rp)
        rw = rv["measured_window"]
        discs_eq = rv["discriminations"] == mine_lad["discriminations"]
        outcomes_mine = [(c["offset_ms"], c["outcome"]) for c in mine_lad["ladder"]]
        outcomes_ref = [(c["offset_ms"], c["outcome"]) for c in rv["ladder"]]
        print(f"vs {rn}: ref verdict={rv['verdict']} landed={rw['landed_offsets_ms']} "
              f"mixed={rw['mixed_offsets_ms']} missed={rw['missed_offsets_ms']} "
              f"lo={rw['lo_edge_ms']} hi={rw['hi_edge_ms']} | cell_outcomes_equal={outcomes_mine == outcomes_ref} "
              f"discs_equal={discs_eq}")
    # sha256(merged) upgrade check: absent at frozen HEAD (wave's move)
    def has_merged_sha(o):
        if isinstance(o, dict):
            return any((k == "merged_sha256" or k == "sha256_merged") or has_merged_sha(v)
                       for k, v in o.items())
        if isinstance(o, list):
            return any(has_merged_sha(x) for x in o)
        return False
    print(f"\nsha256(merged) field present in my attribution artifact: {has_merged_sha(mine_sa)}")
    print(f"sha256(merged) field present in my ladder artifact: {has_merged_sha(mine_lad)}")


if __name__ == "__main__":
    main()
