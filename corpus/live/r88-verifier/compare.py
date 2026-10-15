#!/usr/bin/env python3
"""r79-baseline tuple compare — frozen post-fold replay vs reference runs.

Two modes:

  godot  Godot battery (`run_battery.py`): per-row *verdict tuple* =
         (case, script, flags, expected_exit, actual_exit, signature,
          verdict, error, expected_errors) for seeded rows;
         (case, verdict) + canonical JSON of the remaining stable keys for
         meta rows.  Also compares the merged stdout `output` list after
         normalizing declared-volatile tokens (scratch path, pids, elapsed
         seconds, artifact paths).

  love   LOVE battery (`love_battery.py`): per-row *receipt tuple* =
         (case, arm, key, pinned, verdict) — r62-r78 precedent — plus
         whole-row canonical-JSON sha and field-level diff (r76/r78
         procedure: byte-identical / observed-only jitter / real drift).

Usage: compare.py {godot|love} <mine-verdicts.json> <tag>=<ref-verdicts.json> ...
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")

# ---------------------------------------------------------------- godot ----
GODOT_STABLE = ("case", "script", "flags", "expected_exit", "actual_exit",
                "signature", "verdict", "error", "expected_errors")
GODOT_VOLATILE_KEYS = ("command", "xdg_data_home", "artifact")

NORM_RULES = [
    # any path token under corpus/live (scratch project, xdg-data user dir)
    (re.compile(r"[^\s'\"]*corpus/live/[^\s'\"]*"), "<runpath>"),
    # declared unpinned fixture line-number tokens (traceback text)
    (re.compile(r"\.(gd|lua|py):\d+"), r".\1:<N>"),
    (re.compile(r"srcline=\d+"), "srcline=<N>"),
    # pids in text form
    (re.compile(r"((?:write_)?ppid|godot_pid|descendant_pid|pid)[\"']?\s*[:=]\s*\d+"),
     r"\1=<pid>"),
    # ASLR addresses (crash dumps / backtraces)
    (re.compile(r"Load address: [0-9a-f]+"), "Load address: <addr>"),
    (re.compile(r"0x[0-9a-f]+"), "0x<addr>"),
    (re.compile(r"\b[0-9a-f]{8,}\b"), "<addr>"),
    # timing-dependent tween floats
    (re.compile(r"transient_modulate=\([0-9., ]+\)"),
     "transient_modulate=(<floats>)"),
    (re.compile(r"elapsed[_a-z]*[\"']?\s*[:=]\s*[0-9.]+"), "elapsed=<t>"),
    (re.compile(r"in [0-9.]+ seconds"), "in <t> seconds"),
    (re.compile(r"after [0-9.]+ seconds"), "after <t> seconds"),
]

# meta-row keys whose values are run-specific process bookkeeping
META_VOLATILE_KEY = re.compile(r"(^pids$|^artifact$|pid$|elapsed)")

# meta-row keys whose values are per-arm launch records (pids, raw streams)
META_ARM_RECORD_KEYS = {
    "arms", "hold_arm", "hold_output_lines", "genuine_control",
    "split_genuine", "split_release", "release_arm", "gated_genuine_reps",
    "gated_release_reps", "seam_split_run",
}


def norm(text: str) -> str:
    for pat, rep in NORM_RULES:
        text = pat.sub(rep, text)
    return text


def norm_obj(obj):
    """Recursively normalize a JSON-ish object for meta-row comparison."""
    if isinstance(obj, dict):
        return {k: norm_obj(v) for k, v in obj.items()
                if not META_VOLATILE_KEY.search(k)
                and k not in META_ARM_RECORD_KEYS}
    if isinstance(obj, list):
        return [norm_obj(v) for v in obj]
    if isinstance(obj, str):
        return norm(obj)
    return obj


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def rowsha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def godot_tuple(row: dict):
    """Stable verdict tuple for one Godot battery row."""
    if "script" in row:
        return ("seeded",) + tuple(canon(row.get(k)) for k in GODOT_STABLE)
    # meta row: verdict + every key that is not path/pid/elapsed-volatile,
    # recursively normalized (nested arms carry pids/paths in string form)
    stable = norm_obj({k: v for k, v in row.items()
                       if k not in GODOT_VOLATILE_KEYS})
    return ("meta", row.get("case"), row.get("verdict"), canon(stable))


def godot_output_norm(row: dict):
    """Normalized merged stdout for a row (or None when not carried)."""
    if "output" in row and isinstance(row["output"], list):
        return norm("\n".join(row["output"]))
    return None


def compare_godot(mine_p, refs) -> None:
    mine = json.loads(Path(mine_p).read_text())
    m = {r["case"]: r for r in mine["results"]}
    print(f"=== godot: mine {mine_p} rows={len(mine['results'])} "
          f"verdict={mine['verdict']} file_sha256="
          f"{hashlib.sha256(Path(mine_p).read_bytes()).hexdigest()} ===")
    for tag, ref_p in refs:
        p = ROOT / ref_p if not Path(ref_p).is_absolute() else Path(ref_p)
        if not p.exists():
            print(f"{tag}: SKIP missing ref {ref_p}")
            continue
        ref = json.loads(p.read_text())
        r = {x["case"]: x for x in ref["results"]}
        common = sorted(set(m) & set(r))
        new_only = sorted(set(m) - set(r))
        old_only = sorted(set(r) - set(m))
        mism = []
        mism_seeded = mism_meta = 0
        out_same = out_diff = out_missing = 0
        out_diffs = []
        for c in common:
            a, b = m[c], r[c]
            if godot_tuple(a) != godot_tuple(b):
                mism.append(c)
                if "script" in a:
                    mism_seeded += 1
                else:
                    mism_meta += 1
            na, nb = godot_output_norm(a), godot_output_norm(b)
            if na is None or nb is None:
                out_missing += 1
            elif na == nb:
                out_same += 1
            else:
                out_diff += 1
                out_diffs.append(c)
        print(f"\n{tag}: ref={ref_p} ref_rows={len(ref['results'])} "
              f"ref_verdict={ref['verdict']}")
        print(f"  common={len(common)} new_only={len(new_only)} "
              f"old_only={len(old_only)} tuple_mismatches={len(mism)} "
              f"(seeded={mism_seeded} meta={mism_meta})")
        print(f"  output-normalized identical={out_same} differing={out_diff} "
              f"not-carried={out_missing}")
        if new_only:
            print(f"  new_only_cases: {new_only}")
        if old_only:
            print(f"  old_only_cases: {old_only}")
        for c in mism:
            a, b = m[c], r[c]
            diff = {k: (str(a.get(k))[:90], str(b.get(k))[:90])
                    for k in sorted(set(a) | set(b))
                    if a.get(k) != b.get(k) and k not in GODOT_VOLATILE_KEYS}
            print(f"  TUPLE-MISMATCH {c}: {json.dumps(diff)[:400]}")
        for c in out_diffs[:8]:
            a, b = m[c], r[c]
            la = godot_output_norm(a).splitlines()
            lb = godot_output_norm(b).splitlines()
            for i, (x, y) in enumerate(zip(la, lb)):
                if x != y:
                    print(f"  OUT-DIFF {c} line {i}: mine={x[:110]!r} "
                          f"ref={y[:110]!r}")
                    break
            else:
                print(f"  OUT-DIFF {c}: line-count mine={len(la)} "
                      f"ref={len(lb)}")


# ----------------------------------------------------------------- love ----
def love_tuple(row: dict):
    return (row["arm"], row["key"], row["pinned"], row["verdict"])


def love_key(row: dict):
    return (row["arm"], row["key"])


def compare_love(mine_p, refs) -> None:
    mine = json.loads(Path(mine_p).read_text())
    m = {love_key(r): r for r in mine["results"]}
    print(f"=== love: mine {mine_p} rows={len(mine['results'])} "
          f"verdict={mine['verdict']} file_sha256="
          f"{hashlib.sha256(Path(mine_p).read_bytes()).hexdigest()} ===")
    for tag, ref_p in refs:
        p = ROOT / ref_p if not Path(ref_p).is_absolute() else Path(ref_p)
        if not p.exists():
            print(f"{tag}: SKIP missing ref {ref_p}")
            continue
        ref = json.loads(p.read_text())
        r = {love_key(x): x for x in ref["results"]}
        common = sorted(set(m) & set(r))
        new_only = sorted(set(m) - set(r))
        old_only = sorted(set(r) - set(m))
        mism, byte_same, observed_only, real = [], 0, [], []
        for k in common:
            a, b = m[k], r[k]
            if love_tuple(a) != love_tuple(b):
                mism.append((k, (a["pinned"], a["verdict"]),
                             (b["pinned"], b["verdict"])))
            if rowsha(a) == rowsha(b):
                byte_same += 1
            else:
                fields = {f for f in set(a) | set(b) if a.get(f) != b.get(f)}
                if fields <= {"observed"}:
                    observed_only.append(k)
                else:
                    real.append((k, sorted(fields)))
        print(f"\n{tag}: ref={ref_p} ref_rows={len(ref['results'])} "
              f"ref_verdict={ref['verdict']}")
        print(f"  common={len(common)} new_only={len(new_only)} "
              f"old_only={len(old_only)} tuple_mismatches={len(mism)} "
              f"byte_identical={byte_same}/{len(common)} "
              f"observed_only={len(observed_only)} real_drift={len(real)}")
        if new_only:
            print(f"  new_only_keys: {new_only}")
        if old_only:
            print(f"  old_only_keys: {old_only}")
        for k, a, b in mism:
            print(f"  TUPLE-MISMATCH {k[0]}|{k[1]}: mine={a} ref={b}")
        for k, fields in real:
            print(f"  REAL-DRIFT {k[0]}|{k[1]} fields={fields}")
        for k in observed_only:
            print(f"  observed-only {k[0]}|{k[1]}: "
                  f"mine={m[k]['observed']!r} ref={r[k]['observed']!r}")


def main() -> int:
    mode = sys.argv[1]
    mine_p = sys.argv[2]
    refs = []
    for arg in sys.argv[3:]:
        tag, _, path = arg.partition("=")
        refs.append((tag, path))
    if mode == "godot":
        compare_godot(mine_p, refs)
    elif mode == "love":
        compare_love(mine_p, refs)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
