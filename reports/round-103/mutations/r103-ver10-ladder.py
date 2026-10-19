#!/usr/bin/env python3
"""r103 V10 — byte-stability protocol tool for official battery runs (v4: mask ladder).

v4 fixes found by the teeth test: (a) META/count divergences are keyed "META"
(was Python None -> json.dumps(sort_keys=True) crash), (b) float literals are
masked BEFORE bare-hex (bare-hex was eating float decimals like 0.3146...),
(c) raw_uid= joins the uid mask.

Compares two verdicts.json receipt sets (two fresh runs of the same CASES set)
case-by-case over *stored bytes* and reports the highest mask level at which
each case becomes byte-identical. Pure read: no engine run, no battery, no
shared-file write.

Mask ladder (each level = previous + the named class):
  L0  raw bytes.
  L1  + engine banner, absolute path tokens (scratch roots differ per run).
  L2  + process/instance-global ids and float literals:
        "Load address: <hex>", bare hex >=12 digits (backtrace frames),
        0x<hex>, <any>pid=<int>, unique_id=<int>, uid_[sc]=<int>, raw_uid=<int>,
        sample=<int,...>, <min|max>=<int>, uid embedded in _conn<digits>
        /_disc<digits> names, all -?\\d+\\.\\d+.
  L3  + artifact-content and timing tokens:
        sha256=<hex>, <key>=<int> for key in NUM_KEYS, chg=[...] timing list.
  L4  + explicit per-case allowlist (structurally nondeterministic rows
        declared by name, never by pattern) — see --l4-allow.
  META case-level, result-level or line-count divergence: never maskable.

Protocol (freeze mode): run the ladder over a KNOWN-GOOD pair (r102 run1 vs
run2) with --freeze out.json to produce the per-row stability class table;
r103 official runs are then checked so that no row's class falls below its
frozen class.  Rows still divergent at L3 are declared nondeterministic and
must be compared field-wise, never by raw hash.

Usage:
  r103-ver10-ladder.py A.json B.json [--json OUT.json] [--label NAME]
      [--l4-allow c1,c2] [--freeze FREEZE.json]
"""
import argparse
import json
import re
import sys

BANNER = re.compile(r"^Godot Engine v[\d.]+\.stable[^\n]*$")
LOAD_ADDR = re.compile(r"Load address: [0-9a-f]+")
FLOATISH = re.compile(r"(?<![\w.])-?\d+\.\d+(?![\w.])")
BARE_HEX = re.compile(r"\b[0-9a-f]{12,}\b")
HEX = re.compile(r"0x[0-9a-fA-F]+")
PID = re.compile(r"\b[\w_]*pid=\d+")
UNIQUE_ID = re.compile(r"unique_id=\d+")
UID = re.compile(r"\b(?:uid_[sc]|raw_uid)=\d+")
UID_NAME = re.compile(r"_(?:conn|disc)(\d{6,})")
SAMPLE = re.compile(r"\bsample=\d+(?:,\d+)*")
MINMAX = re.compile(r"\b(?:min|max)=\d+")
ABSPATH = re.compile(r"(?<![\w/.])/(?:[^\s'\"\]\[,;()]*)")
SHA256 = re.compile(r"sha256=[0-9a-f]{16,}")
CHG_LIST = re.compile(r"chg=\[[^\]]*\]")
NUM_KEYS = ("fin_us", "us", "proc", "proc_frames_during_6phys", "pf", "frames",
            "first_at", "second_at", "fin_frame", "transition_f", "bytes",
            "size", "count")
NUM = re.compile(r"\b(%s)=\d+" % "|".join(NUM_KEYS))

LEVELS = ("L0", "L1", "L2", "L3")


def norm(line, level, root_a, root_b):
    if level == "L0":
        return line
    s = line.replace(root_a, "<ROOT>").replace(root_b, "<ROOT>")
    s = ABSPATH.sub("<PATH>", s)
    if level == "L1":
        s = BANNER.sub("<BANNER>", s)
        return s
    s = FLOATISH.sub("<FLOAT>", s)
    s = BANNER.sub("<BANNER>", s)
    s = LOAD_ADDR.sub("Load address: <ADDR>", s)
    s = HEX.sub("<HEX>", s)
    s = BARE_HEX.sub("<HEX>", s)
    s = PID.sub("<PID>", s)
    s = UNIQUE_ID.sub("unique_id=<ID>", s)
    s = UID.sub("uid=<ID>", s)
    s = UID_NAME.sub("_uid=<ID>", s)
    s = SAMPLE.sub("sample=<SAMPLE>", s)
    s = MINMAX.sub("<NUM>", s)
    s = s.replace(root_a, "<ROOT>").replace(root_b, "<ROOT>")
    s = ABSPATH.sub("<PATH>", s)
    if level == "L2":
        return s
    s = CHG_LIST.sub("chg=[<LIST>]", s)
    s = SHA256.sub("sha256=<SHA>", s)
    s = NUM.sub(lambda m: "%s=<N>" % m.group(1), s)
    return s


def load(path):
    d = json.load(open(path))
    rows = d.get("results") if isinstance(d, dict) else d
    root = (d.get("scratch") or "") if isinstance(d, dict) else ""
    return {r["case"]: r for r in rows}, root


def case_level(row_a, row_b, root_a, root_b):
    """Highest ladder level at which the two case records match."""
    meta = (row_a.get("verdict") == row_b.get("verdict")
            and row_a.get("actual_exit") == row_b.get("actual_exit"))
    la, lb = row_a.get("output") or [], row_b.get("output") or []
    if not meta or len(la) != len(lb):
        return "META"  # record-level divergence can never be masked
    for level in LEVELS:
        if all(norm(a, level, root_a, root_b) == norm(b, level, root_a, root_b)
               for a, b in zip(la, lb)):
            return level
    return "L4"


def first_div(row_a, row_b, level, root_a, root_b):
    la, lb = row_a.get("output") or [], row_b.get("output") or []
    for i in range(min(len(la), len(lb))):
        na, nb = norm(la[i], level, root_a, root_b), norm(lb[i], level, root_a, root_b)
        if na != nb:
            return i, na, nb
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--json")
    ap.add_argument("--label", default="")
    ap.add_argument("--l4-allow", default="")
    ap.add_argument("--freeze")
    args = ap.parse_args()
    allow = set(x for x in args.l4_allow.split(",") if x)
    map_a, root_a = load(args.a)
    map_b, root_b = load(args.b)
    counts = {}
    rows = []
    for case in sorted(set(map_a) & set(map_b)):
        lv = case_level(map_a[case], map_b[case], root_a, root_b)
        counts[lv] = counts.get(lv, 0) + 1
        entry = {"case": case, "level": lv}
        if lv in ("META", "L4"):
            fd = first_div(map_a[case], map_b[case], "L3", root_a, root_b)
            if fd:
                entry["first_div_at_L3"] = {"line": fd[0], "a": fd[1][:300], "b": fd[2][:300]}
            else:
                entry["record_level_diff"] = {
                    "verdict": [map_a[case].get("verdict"), map_b[case].get("verdict")],
                    "exit": [map_a[case].get("actual_exit"), map_b[case].get("actual_exit")],
                    "lines": [len(map_a[case].get("output") or []), len(map_b[case].get("output") or [])],
                }
        rows.append(entry)
    unresolved = [r["case"] for r in rows if r["level"] in ("META", "L4") and r["case"] not in allow]
    report = {
        "label": args.label, "a": args.a, "b": args.b,
        "root_a": root_a, "root_b": root_b,
        "cases_a": len(map_a), "cases_b": len(map_b),
        "only_in_a": sorted(set(map_a) - set(map_b)),
        "only_in_b": sorted(set(map_b) - set(map_a)),
        "level_counts": counts,
        "l4_allow": sorted(allow),
        "unresolved_after_allow": unresolved,
        "rows": rows,
    }
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(report, fh, indent=1)
    if args.freeze:
        frozen = {
            "protocol": "r103-ver10-ladder v4",
            "source": {"a": args.a, "b": args.b, "label": args.label},
            "l4_allow": sorted(allow),
            "classes": {r["case"]: r["level"] for r in rows},
            "unresolved": unresolved,
        }
        with open(args.freeze, "w") as fh:
            json.dump(frozen, fh, indent=1, sort_keys=True)
    print("label=%s cases_a=%d cases_b=%d" % (args.label or "-", len(map_a), len(map_b)))
    print("level_counts=%s" % json.dumps(counts, sort_keys=True))
    print("only_in_a=%s only_in_b=%s" % (report["only_in_a"], report["only_in_b"]))
    print("unresolved_after_allow(L4_allow=%s)=%s" % (sorted(allow), unresolved))
    for r in rows:
        if r["level"] in ("META", "L4") and "first_div_at_L3" in r:
            print("-- %s level=%s" % (r["case"], r["level"]))
            print("   A: %s" % r["first_div_at_L3"]["a"])
            print("   B: %s" % r["first_div_at_L3"]["b"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
