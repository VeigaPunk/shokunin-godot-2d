#!/usr/bin/env python3
"""r72-scribe — prior-row byte-stability scrubber for the pygame battery.

Reads two runs' probe.stdout.txt, parses PYGAME-ARM lines, and reports:
  - per-key value differences between the runs (which keys are volatile)
  - the set of keys differing only in wall-clock/jitter fields
  - sha256 of the normalized stream (volatile keys masked)

Volatile keys are declared from the r71 fixture semantics (timing fields);
any *non-volatile* difference is a stability failure and is listed.
"""
import hashlib
import re
import sys
from pathlib import Path

ARM_LINE = re.compile(r"^PYGAME-ARM (\S+) \| (.*)$")
VOLATILE = re.compile(r"(_ms$|^hz$|^fps$|^dt_|_total_ms$)")


def parse(path):
    arms = {}
    order = []
    for line in Path(path).read_text().splitlines():
        m = ARM_LINE.match(line.strip())
        if not m:
            continue
        arm, body = m.groups()
        kv = dict(p.split("=", 1) for p in body.split() if "=" in p)
        arms.setdefault(arm, {}).update(kv)
        order.append((arm, kv))
    return arms, order


def norm_hash(arms):
    h = hashlib.sha256()
    for arm in sorted(arms):
        for k in sorted(arms[arm]):
            v = "<V>" if VOLATILE.search(k) else arms[arm][k]
            h.update(f"{arm}|{k}={v}\n".encode())
    return h.hexdigest()


def main():
    a, b = sys.argv[1], sys.argv[2]
    arms_a, _ = parse(a)
    arms_b, _ = parse(b)
    diffs, nonvol = [], []
    for arm in sorted(set(arms_a) | set(arms_b)):
        ka, kb = arms_a.get(arm, {}), arms_b.get(arm, {})
        for k in sorted(set(ka) | set(kb)):
            va, vb = ka.get(k), kb.get(k)
            if va != vb:
                diffs.append((arm, k, va, vb))
                if not VOLATILE.search(k):
                    nonvol.append((arm, k, va, vb))
    print(f"differing fields: {len(diffs)}")
    for arm, k, va, vb in diffs:
        tag = "volatile" if VOLATILE.search(k) else "NON-VOLATILE"
        print(f"  {tag:12} {arm}|{k}: {va} vs {vb}")
    print(f"non-volatile differences: {len(nonvol)}")
    print(f"normalized sha256: {norm_hash(arms_a)} vs {norm_hash(arms_b)} "
          f"{'EQUAL' if norm_hash(arms_a) == norm_hash(arms_b) else 'DIFFER'}")
    return 1 if nonvol else 0


if __name__ == "__main__":
    sys.exit(main())
