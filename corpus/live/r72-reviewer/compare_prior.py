"""r72-reviewer: prior-row stability comparator.

Compares ARM lines of two probe stdout receipts: key sets per arm must be
identical; all keys outside the declared jitter set must be byte-identical.
"""
import sys
import re

ARM = re.compile(r"^PYGAME-ARM (\S+) \| (.*)$")
JITTER = {"dt_mean_ms", "dt_min_ms", "dt_max_ms", "fps", "hz",
          "l1_wait_ms", "l2_wait_ms", "close_wait_ms", "total_ms",
          "first_read_ms", "mark1_ms", "mark2_ms", "eof_ms",
          "nopump_total_ms"}


def load(path):
    arms = {}
    for line in open(path):
        m = ARM.match(line.strip())
        if not m:
            continue
        arm, body = m.groups()
        kv = dict(p.split("=", 1) for p in body.split() if "=" in p)
        arms[arm] = kv
    return arms


a = load(sys.argv[1])
b = load(sys.argv[2])
diffs = 0
for arm in sorted(set(a) | set(b)):
    if arm not in a or arm not in b:
        print(f"MISSING arm={arm} in {sys.argv[1] if arm not in a else sys.argv[2]}")
        diffs += 1
        continue
    ka, kb = set(a[arm]), set(b[arm])
    if ka != kb:
        print(f"KEYSET arm={arm} only_left={ka - kb} only_right={kb - ka}")
        diffs += 1
    for k in sorted(ka & kb):
        if a[arm][k] != b[arm][k]:
            tag = "JITTER" if k in JITTER else "STABLE-DIFF"
            if tag == "STABLE-DIFF":
                diffs += 1
            print(f"{tag} arm={arm} key={k} left={a[arm][k]} right={b[arm][k]}")
print(f"arms_left={len(a)} arms_right={len(b)} stable_diffs={diffs}")
sys.exit(1 if diffs else 0)
