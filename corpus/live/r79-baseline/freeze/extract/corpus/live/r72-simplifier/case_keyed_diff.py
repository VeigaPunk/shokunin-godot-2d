"""r72-simplifier scratch: case-keyed verdict comparison.

Removing a CASES row shifts list indices, so positional diffs are noisy.
This comparator keys results by `case` and reports:
  * cases only in A / only in B
  * per-case differences in verdict/pinned/reasons (observed timing values
    are wall-clock by design and are reported separately, counted, not
    listed)
"""
import json
import sys
from pathlib import Path


def keyed(path):
    d = json.loads(Path(path).read_text())
    return {r["case"]: r for r in d["results"]}, d


def main():
    a, da = keyed(sys.argv[1])
    b, db = keyed(sys.argv[2])
    print(f"A={sys.argv[1]}  totals={da['totals']} verdict={da['verdict']}")
    print(f"B={sys.argv[2]}  totals={db['totals']} verdict={db['verdict']}")
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    print(f"cases only in A: {only_a if only_a else 'none'}")
    print(f"cases only in B: {only_b if only_b else 'none'}")
    changed, observed_only = [], 0
    for name in sorted(set(a) & set(b)):
        ra, rb = a[name], b[name]
        for field in ("arm", "key", "pinned", "verdict", "reasons"):
            if ra.get(field) != rb.get(field):
                changed.append(f"{name}.{field}: {ra.get(field)!r} != {rb.get(field)!r}")
        if ra.get("observed") != rb.get("observed"):
            observed_only += 1
    print(f"changed non-observed fields: {changed if changed else 'none'}")
    print(f"cases whose `observed` differs (wall-clock keys): {observed_only}")


if __name__ == "__main__":
    main()
