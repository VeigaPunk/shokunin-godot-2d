#!/usr/bin/env python3
r"""r101-VER-10 — receipt byte-stability checker for two battery runs.

Usage:
    python3 ver10_receipt_stability.py RUN_A RUN_B [--json OUT] [--ordered]

RUN_A/RUN_B are run dirs (each holding `verdicts.json`) or `verdicts.json` paths.

Verdicts:
    IDENTICAL           every receipt line equal after run-identity normalisation
    ACCEPTED-VARIANCE   all differences fall in the evidence-backed classes below
                        (census printed; `--json` for machine use)
    REJECT              unclassified difference -> the two runs differ in content
    NOT-A-PAIR          precondition failed (case list / seed / verdict / row count)

Exit codes: 0 IDENTICAL, 0 ACCEPTED-VARIANCE, 1 REJECT, 2 NOT-A-PAIR.

Claim-level arm (always strict, no masking): `signature`, `required_stderr`,
`expected_errors`, `expected_exit`, `actual_exit` of every row must be byte-equal
after run-stamp normalisation. `signature` holds the full pinned evidence
(`run_battery.py` L2293 `"signature": evidence`, incl. multi-variant tuples), so
a difference there means the pin itself changed between runs -> REJECT.

Variance classes and the observed pair that admits each one:
    stamp_path     run-dir / scratch / xdg-data paths and the run stamp.
                   (structural: two runs never share a stamp)
    pid_token      godot_pid= / spawned_pid= / pipe_pid= / pid= / child_pid=.
                   (r88-author runs1<->runs2, 215 rows, and every pid-launching row)
    aslr_address   crash dumps: `Load address:`, `0x...`, bare 12+ hex runs.
                   (crash_spontaneous_sigabrt pair; harness L2262 says the C++
                   backtrace is deliberately NOT pinned)
    masked_digits  bare 4+ digit runs (peer UID / kernel ppid / thread ids).
                   (r88_surfaces_mp_loopback uid_c; r88 rep_analysis.py declares
                   the same `\d{4,}` -> <UID> rule)
    float_drift    tween_flash.transient_modulate only — an interpolated value
                   sampled at whatever frame the host delivered.
                   (r25-export-executor/absolute pair: 2 full runs, same harness
                   bytes, this was the ONLY content difference)
    frame_phase    `post_ph`/`post_pr` step lists and `ph+N`/`pr+N` counts.
                   (r88-author pair input_lattice_press_phys: post_ph 2 vs 3
                   steps; harness L2270-2276 declares such rows bimodal and
                   admits both observed modes)
    line_order     merged-stream interleave: same masked lines, different order.
                   (r88-author pair probe_descendant_error_spoof output_lines:
                   the ERROR line lands at index 4 in one run, 5 in the other)
    timing_float   measured wall-clock: *_elapsed*/measured_*/cleanup_*/seconds.
                   (harness L1331: "Pinning them would pin the host's scheduling")
    race_presence  probe_* fields that are None in one run and measured in the
                   other (`dead_observed_at`, `descendant_kernel_ppid_at_return`).
                   (r88-author pair; bounded-race observational fields)

Anything else -> REJECT. This tool reads artifacts only; it never runs the battery.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

STAMP_RE = re.compile(r"\d{8}T\d{6}\d{6}Z")
PID_RE = re.compile(r"\b(godot_pid|spawned_pid|pipe_pid|pid|child_pid|parent_pid|descendant_pid)=(\d+)")
ADDR_RE = re.compile(r"0x[0-9a-f]{6,}|Load address: [0-9a-f]+|\b[0-9a-f]{12,}\b")
DIGITS_RE = re.compile(r"\d{4,}")
FLOAT_RE = re.compile(r"-?\d+\.\d+")
STEP_RE = re.compile(r"\b(ph|pr)\+(\d+)\{[^}]*\}")
STEPCNT_RE = re.compile(r"\b(ph|pr)\+(\d+)\b")
STEPSEQ_RE = re.compile(r"(<STEP>\s*(?:\|?\s*)?)+")

TIMING_FIELD_RE = re.compile(r"(elapsed|measured|cleanup|seconds|dead_observed|bound_seconds|probe_elapsed|_s\b)")
RACE_FIELD_RE = re.compile(r"(dead_observed_at|descendant_kernel_ppid|child_exit_at_timeout|observed_at)")
FLOAT_CASE_ALLOWLIST = {"tween_flash"}
FRAME_PHASE_CASE_RE = re.compile(r"^(input_lattice_|r95b_order_|r96b_)")


def resolve(arg):
    p = Path(arg)
    return p / "verdicts.json" if p.is_dir() else p


def stamp_of(run_dir, doc=None):
    m = STAMP_RE.search(str(run_dir))
    if m:
        return m.group(0)
    if doc:
        m = STAMP_RE.search(str(doc.get("scratch", "")))
        if m:
            return m.group(0)
    return None


def identity_prefixes(doc, run_dir):
    """Path prefixes that identify this run; longest first so no partial overlap."""
    out = {str(run_dir)}
    sc = doc.get("scratch")
    if isinstance(sc, str) and sc:
        out.add(sc)
        for suffix in ("/scratch", "scratch"):
            if sc.endswith(suffix):
                out.add(sc[: -len(suffix)].rstrip("/") or "/")
                break
    return sorted(out, key=len, reverse=True)


def norm_identity(v, prefixes, run_stamp, stamp_path_re_=None):
    if isinstance(v, str):
        for p in prefixes:
            if p:
                v = v.replace(p, "<RUNPREFIX>")
        if run_stamp and stamp_path_re_ is not None:
            v = stamp_path_re_.sub("<RUNPATH>", v)
        if run_stamp:
            v = v.replace(run_stamp, "<STAMP>")
        return v
    if isinstance(v, list):
        return [norm_identity(x, prefixes, run_stamp, stamp_path_re_) for x in v]
    if isinstance(v, dict):
        return {k: norm_identity(x, prefixes, run_stamp, stamp_path_re_) for k, x in v.items()}
    return v


def frame_phase_mask(s):
    s = STEP_RE.sub("<STEP>", s)
    s = STEPSEQ_RE.sub("<STEPS> ", s)
    s = STEPCNT_RE.sub(r"\1+<N>", s)
    return s


def mask_soft(s):
    """Identity/token masks only — floats survive as <F>."""
    s = STAMP_RE.sub("<STAMP>", s)
    s = PID_RE.sub(r"\1=<PID>", s)
    s = ADDR_RE.sub("<ADDR>", s)
    s = FLOAT_RE.sub("<F>", s)
    return s


def mask_hard(s):
    """mask_soft plus bare 4+ digit runs (peer UID / kernel ppid)."""
    return DIGITS_RE.sub("<N4>", mask_soft(s))


def mask(s):
    return mask_hard(s)


def classify_line(a, b, case, field, path):
    """Return variance class for one differing string pair, or None."""
    if STAMP_RE.sub("<STAMP>", a) == STAMP_RE.sub("<STAMP>", b):
        return "stamp_path"
    if frame_phase_mask(a) == frame_phase_mask(b):
        return "frame_phase"
    if mask_soft(a) == mask_soft(b):
        if PID_RE.search(a):
            return "pid_token"
        if ADDR_RE.search(a):
            return "aslr_address"
        if FLOAT_RE.search(a):
            if case in FLOAT_CASE_ALLOWLIST:
                return "float_drift"
            if (case and case.startswith("probe_")) or TIMING_FIELD_RE.search(field or "") or TIMING_FIELD_RE.search(path or ""):
                return "timing_float"
            return None
        return "masked_digits"
    if mask_hard(a) == mask_hard(b):
        return "masked_digits"
    return None


def classify_field(a, b, case, field, path):
    if isinstance(a, list) and isinstance(b, list):
        # ordered line list: classify element-wise; a pure permutation is line_order
        if len(a) == len(b):
            ma = sorted(mask(x) for x in a)
            mb = sorted(mask(y) for y in b)
            if ma == mb:
                return "line_order"
        if len(a) != len(b):
            # step-list growth (frame_phase) still compares equal after step collapse
            if sorted(frame_phase_mask(x) for x in a) == sorted(frame_phase_mask(y) for y in b):
                return "frame_phase"
            return None
        classes = set()
        for x, y in zip(a, b):
            if x == y:
                continue
            if not (isinstance(x, str) and isinstance(y, str)):
                return None
            c = classify_line(x, y, case, field, path)
            if c is None:
                return None
            classes.add(c)
        return classes.pop() if len(classes) == 1 else None
    if isinstance(a, str) and isinstance(b, str):
        return classify_line(a, b, case, field, path)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if TIMING_FIELD_RE.search(field or "") or TIMING_FIELD_RE.search(path or ""):
            return "timing_float"
        if case and case.startswith("probe_"):
            return "timing_float"
        return None
    if a is None or b is None:
        if case and case.startswith("probe_") and RACE_FIELD_RE.search(field or path):
            return "race_presence"
        return None
    return None


def diff_walk(a, b, path, case, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((path + "/" + k, "key_presence", a.get(k), b.get(k), case))
                continue
            diff_walk(a[k], b[k], path + "/" + k, case, out)
    elif isinstance(a, list) and isinstance(b, list):
        if a != b:
            out.append((path, "list", a, b, case))
    else:
        if a != b:
            out.append((path, "value", a, b, case))


CLAIM_FIELDS = ("signature", "required_stderr", "expected_errors", "expected_exit", "actual_exit")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    pa, pb = resolve(args.a), resolve(args.b)
    A, B = json.loads(pa.read_text()), json.loads(pb.read_text())
    run_a, run_b = pa.parent, pb.parent
    va, vb = A.get("verdict"), B.get("verdict")
    ra, rb = A.get("results", []), B.get("results", [])

    pre = []
    if [r.get("case") for r in ra] != [r.get("case") for r in rb]:
        pre.append("case-name list differs")
    if A.get("seed") != B.get("seed"):
        pre.append("seed differs (not the same harness tree)")
    if va != "PASS" or vb != "PASS":
        pre.append(f"verdict not PASS ({va}/{vb})")
    if len(ra) != len(rb):
        pre.append(f"row count differs ({len(ra)}/{len(rb)})")
    if pre:
        print(f"NOT-A-PAIR: {'; '.join(pre)}")
        print(f"  A={pa} rows={len(ra)} verdict={va} seed={A.get('seed')}")
        print(f"  B={pb} rows={len(rb)} verdict={vb} seed={B.get('seed')}")
        return 2

    harness = Path(str(A.get("seed", ""))) / "run_battery.py"
    harness_sha = hashlib.sha256(harness.read_bytes()).hexdigest() if harness.is_file() else None

    sa, sb = stamp_of(run_a, A), stamp_of(run_b, B)

    def stamp_path_re(stamp):
        # any token carrying the run stamp identifies that run, absolute or relative
        return re.compile(r'[^\s"\'\[\],;]*' + re.escape(stamp) + r'[^\s"\'\[\],;]*')

    Am = norm_identity(A, identity_prefixes(A, run_a), sa, stamp_path_re(sa) if sa else None)
    Bm = norm_identity(B, identity_prefixes(B, run_b), sb, stamp_path_re(sb) if sb else None)

    claim_diffs, receipt_diffs, raw_equal = [], [], 0
    for x, y in zip(Am["results"], Bm["results"]):
        case = x.get("case")
        for k in CLAIM_FIELDS:
            if x.get(k) != y.get(k):
                claim_diffs.append((case, k, x.get(k), y.get(k)))
        out_a, out_b = x.get("output") or [], y.get("output") or []
        if out_a == out_b:
            raw_equal += 1
            continue
        receipt_diffs.append({"case": case, "a": out_a, "b": out_b})

    census, census_ex, unclassified = {}, {}, []
    for d in receipt_diffs:
        case = d["case"]
        if d["a"] == d["b"]:
            continue
        classes = set()
        if len(d["a"]) == len(d["b"]):
            pos_classes = set()
            pos_unclassified = False
            for i, (x, y) in enumerate(zip(d["a"], d["b"])):
                if x == y:
                    continue
                c = classify_line(x, y, case, "output", f"output[{i}]")
                if c is None:
                    pos_unclassified = True
                    break
                pos_classes.add(c)
                census_ex.setdefault((c, case), (x, y))
            if not pos_unclassified:
                classes |= pos_classes
            elif sorted(mask(l) for l in d["a"]) == sorted(mask(l) for l in d["b"]):
                classes.add("line_order")
                first = next(((x, y) for x, y in zip(d["a"], d["b"]) if x != y), None)
                if first:
                    census_ex.setdefault(("line_order", case), first)
            else:
                classes.add("UNCLASSIFIED")
                for i, (x, y) in enumerate(zip(d["a"], d["b"])):
                    if x != y and classify_line(x, y, case, "output", f"output[{i}]") is None:
                        unclassified.append((case, f"output[{i}]", x, y))
        else:
            if sorted(frame_phase_mask(l) for l in d["a"]) == sorted(frame_phase_mask(l) for l in d["b"]):
                classes.add("frame_phase")
                census_ex.setdefault(("frame_phase", case), (d["a"], d["b"]))
            elif sorted(mask(l) for l in d["a"]) == sorted(mask(l) for l in d["b"]):
                classes.add("line_order")
                census_ex.setdefault(("line_order", case), (d["a"], d["b"]))
            else:
                classes.add("UNCLASSIFIED")
                extra = [l for l in (d["a"] if len(d["a"]) > len(d["b"]) else d["b"]) if mask(l) not in {mask(m) for m in (d["b"] if len(d["a"]) > len(d["b"]) else d["a"])}]
                unclassified.append((case, "output(len)", extra[:3], len(d["b"])))
        for c in classes:
            if c == "UNCLASSIFIED":
                continue
            census.setdefault((c, case), []).append(d)

    # non-result drift (paths, probe artifacts at top level)
    for k in sorted(set(Am) | set(Bm)):
        if k == "results":
            continue
        if Am.get(k) != Bm.get(k):
            c = classify_field(Am[k], Bm[k], None, k, k)
            if c is None:
                unclassified.append((None, k, Am.get(k), Bm.get(k)))
            else:
                census.setdefault((c, None), []).append({"case": None, "a": Am.get(k), "b": Bm.get(k)})
                census_ex.setdefault((c, None), (Am.get(k), Bm.get(k)))

    verdict = "REJECT" if (unclassified or claim_diffs) else ("IDENTICAL" if not census else "ACCEPTED-VARIANCE")
    norm_sha_a = hashlib.sha256(json.dumps(Am, sort_keys=True).encode()).hexdigest()
    norm_sha_b = hashlib.sha256(json.dumps(Bm, sort_keys=True).encode()).hexdigest()
    report = {
        "verdict": verdict,
        "run_a": str(pa), "run_b": str(pb), "rows": len(ra),
        "harness_seed": A.get("seed"), "harness_sha256": harness_sha, "godot": A.get("godot"),
        "rows_raw_equal": raw_equal,
        "normalized_sha256_a": norm_sha_a, "normalized_sha256_b": norm_sha_b,
        "normalized_byte_equal": norm_sha_a == norm_sha_b,
        "claim_diffs": [
            {"case": c, "field": f, "a": str(x)[:300], "b": str(y)[:300]} for c, f, x, y in claim_diffs
        ],
        "census": {f"{k[0]}|{k[1]}": len(v) for k, v in sorted(census.items())},
        "unclassified": [
            {"case": c, "path": p, "a": str(x)[:300], "b": str(y)[:300]} for c, p, x, y in unclassified[:40]
        ],
        "examples": {
            f"{k[0]}|{k[1]}": {
                "a": str((census_ex.get(k) or ("", ""))[0])[:200],
                "b": str((census_ex.get(k) or ("", ""))[1])[:200],
            }
            for k in sorted(census)
        },
    }
    print(f"{verdict}  rows={report['rows']}  raw_equal_rows={raw_equal}  harness_sha256={harness_sha}")
    print(f"  A={pa}\n  B={pb}")
    if claim_diffs:
        print(f"  CLAIM DIFFS ({len(claim_diffs)}) — the pin itself changed:")
        for c, f, x, y in claim_diffs[:10]:
            print(f"    {c}.{f}\n      A={str(x)[:200]}\n      B={str(y)[:200]}")
    for (c, case), v in sorted(census.items()):
        ex = report["examples"][f"{c}|{case}"]
        print(f"    {c:14s} case={str(case):34s} n={len(v)}")
        print(f"        A={ex['a']}")
        print(f"        B={ex['b']}")
    for c, p, x, y in unclassified[:20]:
        print(f"    UNCLASSIFIED {p} case={c}\n        A={str(x)[:220]}\n        B={str(y)[:220]}")
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=1) + "\n")
    return 1 if verdict == "REJECT" else 0


if __name__ == "__main__":
    sys.exit(main())
