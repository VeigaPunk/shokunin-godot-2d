#!/usr/bin/env python3
"""r87-baseline compare — frozen-tree replay vs committed/landed receipts.

Reports, per reference:
  * row set: common / new_only / old_only (case names)
  * tuple byte-identical: rows whose stable verdict tuple canonical JSON is
    byte-equal (this is the "byte-identical count")
  * tuple mismatches: named individually with the differing fields
  * raw output byte-identical: merged stdout list joined and compared with NO
    normalization (strict bytes)
  * normalized output identical: r81 convention (declared-volatile masking)

Usage: r87_compare.py <mine-verdicts.json> <tag>=<ref-verdicts.json> ...
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare import GODOT_VOLATILE_KEYS, canon, godot_output_norm, godot_tuple, norm  # noqa: E402


def raw_output(row):
    if "output" in row and isinstance(row["output"], list):
        return "\n".join(row["output"])
    return None


def main():
    mine_p = Path(sys.argv[1])
    mine = json.loads(mine_p.read_text())
    m = {r["case"]: r for r in mine["results"]}
    print(f"=== mine {mine_p} rows={len(mine['results'])} "
          f"verdict={mine['verdict']} sha256="
          f"{hashlib.sha256(mine_p.read_bytes()).hexdigest()} ===")
    for arg in sys.argv[2:]:
        tag, ref_p = arg.split("=", 1)
        p = Path(ref_p)
        if not p.exists():
            print(f"\n{tag}: SKIP missing ref {ref_p}")
            continue
        ref = json.loads(p.read_text())
        r = {x["case"]: x for x in ref["results"]}
        common = sorted(set(m) & set(r))
        new_only = sorted(set(m) - set(r))
        old_only = sorted(set(r) - set(m))
        tuple_same, tuple_mism = [], []
        raw_same = raw_diff = raw_missing = 0
        nrm_same = nrm_diff = nrm_missing = 0
        raw_diffs = []
        for c in common:
            a, b = m[c], r[c]
            if canon(godot_tuple(a)) == canon(godot_tuple(b)):
                tuple_same.append(c)
            else:
                tuple_mism.append(c)
            ra, rb = raw_output(a), raw_output(b)
            if ra is None or rb is None:
                raw_missing += 1
            elif ra == rb:
                raw_same += 1
            else:
                raw_diff += 1
                raw_diffs.append(c)
            na, nb = godot_output_norm(a), godot_output_norm(b)
            if na is None or nb is None:
                nrm_missing += 1
            elif na == nb:
                nrm_same += 1
            else:
                nrm_diff += 1
        print(f"\n{tag}: ref={ref_p} ref_rows={len(ref['results'])} "
              f"ref_verdict={ref['verdict']} ref_sha256="
              f"{hashlib.sha256(p.read_bytes()).hexdigest()}")
        print(f"  common={len(common)} new_only={len(new_only)} "
              f"old_only={len(old_only)}")
        print(f"  tuple byte-identical={len(tuple_same)}/{len(common)} "
              f"tuple_mismatches={len(tuple_mism)}")
        print(f"  output RAW byte-identical={raw_same}/{len(common)} "
              f"differing={raw_diff} not-carried={raw_missing}")
        print(f"  output NORMALIZED identical={nrm_same}/{len(common)} "
              f"differing={nrm_diff} not-carried={nrm_missing}")
        if new_only:
            print(f"  new_only_cases({len(new_only)}): {new_only}")
        if old_only:
            print(f"  old_only_cases({len(old_only)}): {old_only}")
        for c in tuple_mism:
            a, b = m[c], r[c]
            diff = {k: (str(a.get(k))[:120], str(b.get(k))[:120])
                    for k in sorted(set(a) | set(b))
                    if a.get(k) != b.get(k) and k not in GODOT_VOLATILE_KEYS}
            print(f"  TUPLE-MISMATCH {c}: {json.dumps(diff)[:500]}")
        for c in raw_diffs:
            a, b = m[c], r[c]
            la, lb = raw_output(a).splitlines(), raw_output(b).splitlines()
            shown = False
            for i, (x, y) in enumerate(zip(la, lb)):
                if x != y:
                    print(f"  RAW-OUT-DIFF {c} line {i}:\n"
                          f"      mine={x[:160]!r}\n      ref ={y[:160]!r}")
                    shown = True
                    break
            if not shown:
                print(f"  RAW-OUT-DIFF {c}: line-count mine={len(la)} "
                      f"ref={len(lb)} "
                      f"(normalized-equal={godot_output_norm(a) == godot_output_norm(b)})")


if __name__ == "__main__":
    main()
