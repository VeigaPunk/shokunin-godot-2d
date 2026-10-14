#!/usr/bin/env python3
"""r72-baseline receipt diff: per-receipt comparison vs r68-r71 references.

Method (r62-r69 verifier precedent): Godot CASES rows compared on the tuple
(script, flags, expected_exit, actual_exit, signature, verdict, error)
indexed by `case`; meta rows on verdict + discriminations bool-map equality.
LOVE/pygame rows compared on (arm, key, pinned, verdict) + observed-equality
on exact-pinned rows (bound-pinned `observed` is jittered by construction).
Artifacts compared as volatile-stripped deep diffs.
"""
import json
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
GODOT_RUNS = ROOT / "corpus/live/r72-baseline/runs"
GODOT_TUPLE = ("script", "flags", "expected_exit", "actual_exit",
               "signature", "verdict", "error")


def load(p):
    return json.loads(Path(p).read_text())


def godot_compare(mine_v, ref_v):
    m = {r["case"]: r for r in mine_v["results"]}
    r = {r["case"]: r for r in ref_v["results"]}
    common = sorted(set(m) & set(r))
    mism = []
    for c in common:
        a, b = m[c], r[c]
        diff = {f: (a.get(f), b.get(f)) for f in GODOT_TUPLE
                if a.get(f) != b.get(f)}
        if diff:
            mism.append((c, diff))
        da, db = a.get("discriminations"), b.get("discriminations")
        if (a.get("verdict"), json.dumps(da, sort_keys=True) if isinstance(da, dict) else None) != \
           (b.get("verdict"), json.dumps(db, sort_keys=True) if isinstance(db, dict) else None):
            mism.append((c + " [meta]", {"mine": da, "ref": db}))
    return common, sorted(set(m) - set(r)), sorted(set(r) - set(m)), mism


def kv_compare(mine_v, ref_v):
    """LOVE/pygame runner rows: (arm,key) -> (pinned, verdict); plus
    observed==pinned check on rows whose pinned is an exact string."""
    m = {(r["arm"], r["key"]): r for r in mine_v["results"]}
    r = {(r["arm"], r["key"]): r for r in ref_v["results"]}
    common = sorted(set(m) & set(r))
    mism = []
    for k in common:
        a, b = m[k], r[k]
        if a["pinned"] != b["pinned"] or a["verdict"] != b["verdict"]:
            mism.append((f"{k[0]}|{k[1]}",
                         {"mine": (a["pinned"], a["verdict"]),
                          "ref": (b["pinned"], b["verdict"])}))
        # exact-pinned rows must have observed==pinned (both rows PASS)
        if a["pinned"] == a.get("observed") and b["pinned"] != a["pinned"]:
            mism.append((f"{k[0]}|{k[1]} [obs]", a["pinned"], b["pinned"]))
    return common, sorted(set(m) - set(r)), sorted(set(r) - set(m)), mism


VOLATILE = {"command", "scratch", "xdg_data_home", "artifact",
            "elapsed_seconds", "descendant_pid", "godot_pid", "write_ppid",
            "pid", "artifact_sha256", "artifact_bytes", "seed",
            "scratch_sha256", "started_utc", "bound_seconds",
            "elapsed_s", "elapsed", "probe_elapsed_s"}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o


def deep_diff(a, b, path=""):
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


def godot_section():
    mine = {
        "flagless88": load(GODOT_RUNS / "20261014T143946074058Z/verdicts.json"),
        "attrib89": load(GODOT_RUNS / "20261014T144122146924Z/verdicts.json"),
        "ladder89": load(GODOT_RUNS / "20261014T144234955551Z/verdicts.json"),
        "gapladder89": load(GODOT_RUNS / "20261014T144401150151Z/verdicts.json"),
    }
    refs = {
        "r71-baseline flagless88 [tracked]": "corpus/live/r71-baseline/godot-runs/20261014T142633675793Z/verdicts.json",
        "r69-scribe landed-flagged91 [tracked]": "corpus/live/r69-scribe/runs-landed-flagged/20261014T121035766840Z/verdicts.json",
        "r69-simplifier landed91 [tracked]": "corpus/live/r69-simplifier/runs-landed/20261014T121426485317Z/verdicts.json",
        "r69-simplifier base89 [tracked]": "corpus/live/r69-simplifier/del-measure/runs-base/20261014T124109211343Z/verdicts.json",
        "r68-boundary runs2 90 [tracked]": "corpus/live/r68-boundary/runs2/20261014T112024144893Z/verdicts.json",
    }
    for rn, rp in refs.items():
        rv = load(ROOT / rp)
        for mn, mv in mine.items():
            common, new_only, old_only, mism = godot_compare(mv, rv)
            print(f"{mn} vs {rn}: ref_rows={len(rv['results'])} common={len(common)} "
                  f"new_only={new_only} old_only={old_only} mismatches={len(mism)}")
            for c, d in mism:
                print(f"    MISMATCH {c}: {json.dumps(d)[:400]}")

    print("\n=== stream-attribution artifact deep-diff (volatile-stripped) ===")
    mine_sa = load(GODOT_RUNS / "20261014T144122146924Z/stream-attribution-verdicts.json")
    for rn, rp in {
        "r69-scribe landed-flagged [tracked]": "corpus/live/r69-scribe/runs-landed-flagged/20261014T121035766840Z/stream-attribution-verdicts.json",
        "r69-simplifier landed [tracked]": "corpus/live/r69-simplifier/runs-landed/20261014T121426485317Z/stream-attribution-verdicts.json",
        "r68-boundary runs2 (pre-sha256merged) [tracked]": "corpus/live/r68-boundary/runs2/20261014T112024144893Z/stream-attribution-verdicts.json",
        "r68-simplifier landed90 (pre-upgrade) [tracked]": "corpus/live/r68-simplifier/runs-landed/20261014T112415928385Z/stream-attribution-verdicts.json",
    }.items():
        diffs = list(deep_diff(strip(mine_sa), strip(load(ROOT / rp))))
        print(f"vs {rn}: {len(diffs)} diffs")
        for d in diffs[:15]:
            print("   ", d)

    print("\n=== midlineforge-ladder artifact comparison ===")
    mine_lad = load(GODOT_RUNS / "20261014T144234955551Z/midlineforge-ladder-verdicts.json")
    mw = mine_lad["measured_window"]
    print(f"mine: verdict={mine_lad['verdict']} landed={mw['landed_offsets_ms']} "
          f"mixed={mw['mixed_offsets_ms']} missed={mw['missed_offsets_ms']} "
          f"lo={mw['lo_edge_ms']} hi={mw['hi_edge_ms']} gap={mw['nominal_gap_ms']}")
    print(f"mine discs: {json.dumps(mine_lad['discriminations'], sort_keys=True)}")
    for rn, rp in {
        "r69-scribe landed-flagged [tracked]": "corpus/live/r69-scribe/runs-landed-flagged/20261014T121035766840Z/midlineforge-ladder-verdicts.json",
        "r69-simplifier landed [tracked]": "corpus/live/r69-simplifier/runs-landed/20261014T121426485317Z/midlineforge-ladder-verdicts.json",
        "r68-boundary runs2 [tracked]": "corpus/live/r68-boundary/runs2/20261014T112024144893Z/midlineforge-ladder-verdicts.json",
        "r68-simplifier vC [tracked]": "corpus/live/r68-simplifier/del-measure/vC-runs/20261014T113534434175Z/midlineforge-ladder-verdicts.json",
    }.items():
        rv = load(ROOT / rp)
        rw = rv["measured_window"]
        outcomes_mine = [(c["offset_ms"], c["outcome"]) for c in mine_lad["ladder"]]
        outcomes_ref = [(c["offset_ms"], c["outcome"]) for c in rv["ladder"]]
        print(f"vs {rn}: ref verdict={rv['verdict']} landed={rw['landed_offsets_ms']} "
              f"mixed={rw['mixed_offsets_ms']} missed={rw['missed_offsets_ms']} "
              f"lo={rw['lo_edge_ms']} hi={rw['hi_edge_ms']} | cell_outcomes_equal={outcomes_mine == outcomes_ref} "
              f"discs_equal={rv['discriminations'] == mine_lad['discriminations']}")

    print("\n=== midlineforge-gapladder artifact comparison ===")
    mine_gap = load(GODOT_RUNS / "20261014T144401150151Z/midlineforge-gapladder-verdicts.json")
    mr = mine_gap.get("measured_referent", {})
    print(f"mine: verdict={mine_gap['verdict']} referent={json.dumps(mr, sort_keys=True)[:300]}")
    print(f"mine discs: {json.dumps(mine_gap['discriminations'], sort_keys=True)}")
    for rn, rp in {
        "r69-scribe landed-flagged [tracked]": "corpus/live/r69-scribe/runs-landed-flagged/20261014T121035766840Z/midlineforge-gapladder-verdicts.json",
        "r69-simplifier landed [tracked]": "corpus/live/r69-simplifier/runs-landed/20261014T121426485317Z/midlineforge-gapladder-verdicts.json",
        "r69-simplifier base [tracked]": "corpus/live/r69-simplifier/del-measure/runs-base/20261014T124109211343Z/midlineforge-gapladder-verdicts.json",
    }.items():
        rv = load(ROOT / rp)
        diffs = list(deep_diff(strip(mine_gap), strip(rv)))
        print(f"vs {rn}: ref verdict={rv['verdict']} diffs={len(diffs)}")
        for d in diffs[:15]:
            print("   ", d)


def love_section():
    print("\n=== LOVE 19-row comparison ===")
    mine = load(ROOT / "corpus/live/r72-baseline/love-runs/love-20261014T144103820852Z/verdicts.json")
    refs = {
        "r71-baseline love19 [tracked]": "corpus/live/r71-baseline/love-runs/love-20261014T142608582031Z/verdicts.json",
        "r71-reviewer love-r1 [tracked]": "corpus/live/r71-reviewer/love-runs/love-20261014T142315444692Z/verdicts.json",
        "r71-reviewer love-r2 [tracked]": "corpus/live/r71-reviewer/love-runs/love-20261014T142319646506Z/verdicts.json",
        "r71-reviewer love-r3 [tracked]": "corpus/live/r71-reviewer/love-runs/love-20261014T143050643150Z/verdicts.json",
        "r71-simplifier runs-love [tracked]": "corpus/live/r71-simplifier/runs-love/love-20261014T142144814250Z/verdicts.json",
        "r71-simplifier del-control [tracked]": "corpus/live/r71-simplifier/del-measure/runs-control/love-20261014T142220988782Z/verdicts.json",
        "r71-simplifier del-vA [tracked]": "corpus/live/r71-simplifier/del-measure/runs-vA/love-20261014T142225830535Z/verdicts.json",
        "r71-simplifier del-vB [tracked]": "corpus/live/r71-simplifier/del-measure/runs-vB/love-20261014T142230539077Z/verdicts.json",
    }
    for rn, rp in refs.items():
        rv = load(ROOT / rp)
        common, new_only, old_only, mism = kv_compare(mine, rv)
        print(f"love19 vs {rn}: ref_rows={len(rv['results'])} common={len(common)} "
              f"new_only={new_only} old_only={old_only} mismatches={len(mism)}")
        for c, d in mism:
            print(f"    MISMATCH {c}: {json.dumps(d)[:300]}")


def pygame_section():
    print("\n=== pygame 36-row comparison ===")
    mine = load(ROOT / "corpus/live/r72-baseline/pygame-runs/pygame-20261014T144107924935Z/verdicts.json")
    refs = {
        "r71-author run1 [tracked]": "corpus/live/r71-author/verdicts-run1.json",
        "r71-author run2 [tracked]": "corpus/live/r71-author/verdicts-run2.json",
        "r71-author run3 [tracked]": "corpus/live/r71-author/verdicts-run3.json",
        "r71-simplifier pg [tracked]": "corpus/live/r71-simplifier/runs-pygame/pygame-20261014T142911180884Z/verdicts.json",
        "r71-simplifier pg-rep2 [tracked]": "corpus/live/r71-simplifier/runs-pygame-rep2/pygame-20261014T143001173516Z/verdicts.json",
        "r71-simplifier pg-rev2 [tracked]": "corpus/live/r71-simplifier/runs-pygame-rev2/pygame-20261014T143056604653Z/verdicts.json",
        "r71-simplifier del-pg-control [tracked]": "corpus/live/r71-simplifier/del-measure-pygame/runs-control/pygame-20261014T143017826941Z/verdicts.json",
        "r71-simplifier del-pg-vA [tracked]": "corpus/live/r71-simplifier/del-measure-pygame/runs-vA/pygame-20261014T143026296183Z/verdicts.json",
        "r71-simplifier del-pg-vB [tracked]": "corpus/live/r71-simplifier/del-measure-pygame/runs-vB/pygame-20261014T143034693361Z/verdicts.json",
        "r71-simplifier del-pg-vC [tracked]": "corpus/live/r71-simplifier/del-measure-pygame/runs-vC/pygame-20261014T143122730763Z/verdicts.json",
        "r71-reviewer pg-1 [tracked]": "corpus/live/r71-reviewer/pg-runs/pygame-20261014T142915865093Z/verdicts.json",
        "r71-reviewer pg-2 [tracked]": "corpus/live/r71-reviewer/pg-runs/pygame-20261014T142927721427Z/verdicts.json",
        "r71-reviewer pg-3 [tracked]": "corpus/live/r71-reviewer/pg-runs/pygame-20261014T143034575334Z/verdicts.json",
        "r71-reviewer pg-4 [tracked]": "corpus/live/r71-reviewer/pg-runs/pygame-20261014T143118354542Z/verdicts.json",
        "r71-reviewer pg-5 [tracked]": "corpus/live/r71-reviewer/pg-runs/pygame-20261014T143126878900Z/verdicts.json",
        "r71-reviewer pg-6 [tracked]": "corpus/live/r71-reviewer/pg-runs/pygame-20261014T143329679841Z/verdicts.json",
        "r71-reviewer pg-loaded [tracked]": "corpus/live/r71-reviewer/pg-runs-loaded/pygame-20261014T143102300395Z/verdicts.json",
        "r71-critic scout-idle [tracked]": "corpus/live/r71-critic/scout-battery-idle/pygame-20261014T142340388258Z/verdicts.json",
        "r71-critic scout-loaded64 [tracked]": "corpus/live/r71-critic/scout-battery-loaded64/pygame-20261014T142403982059Z/verdicts.json",
    }
    for rn, rp in refs.items():
        rv = load(ROOT / rp)
        common, new_only, old_only, mism = kv_compare(mine, rv)
        print(f"pygame36 vs {rn}: ref_rows={len(rv['results'])} common={len(common)} "
              f"new_only={new_only} old_only={old_only} mismatches={len(mism)}")
        for c, d in mism:
            print(f"    MISMATCH {c}: {json.dumps(d)[:300]}")


if __name__ == "__main__":
    godot_section()
    love_section()
    pygame_section()
