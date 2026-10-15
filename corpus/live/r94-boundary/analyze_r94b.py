#!/usr/bin/env python3
"""r94b boundary analyzer.

1. Classifies every scout ROWS_PREFIX row (loaded read-only from
   ../r94-scout/author-rows.py.txt) against THIS seat's receipts with the
   production `classify_process` (AST-extracted from corpus/fixtures/run_battery.py,
   exactly like the scout's verify_rows.py) — per condition.
2. Reports the measured-integer envelope per cell per condition and flags any
   value outside the quiet (canonical) envelope.
3. Dumps the attack-arm payloads per condition.

Output: runs/analyze_r94b.json + a printed text report.
"""
import ast
import collections
import hashlib
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"
SCOUT = HERE.parent / "r94-scout"
FIXTURE = HERE.parent.parent / "fixtures" / "run_battery.py"

CONDS = ["quiet", "load", "ff30", "ff60", "ff120", "ff120load", "reprobe"]
AB_CELLS = ["particles_cpu_lifetime", "particles_cpu_expl", "particles_cpu_request"]
AB_MODES = ["def", "f30", "f60", "f120"]

SCOUT_CELLS = [
    "particles_census", "particles_ppm", "particles_convert",
    "particles_cpu_lifetime", "particles_cpu_expl", "particles_cpu_speed_pre",
    "particles_cpu_stop", "particles_cpu_never", "particles_cpu_contam",
    "particles_cpu_oneshot_off", "particles_cpu_oneshot_flag", "particles_cpu_pause",
    "particles_cpu_restart", "particles_cpu_retrigger", "particles_cpu_lt_mid",
    "particles_cpu_speed_mid", "particles_cpu_amount_mid", "particles_cpu_request",
    "particles_gpu_headless",
]
TEXT_FREE = {"particles_census", "particles_ppm", "particles_convert"}


def load_classifier():
    src = FIXTURE.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("import re\n" + seg, ns)
            return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit("classify_process not found")


def load_rows():
    ns = {}
    exec((SCOUT / "author-rows.py.txt").read_text(), ns)
    return ns["ROWS"], ns["ROWS_PREFIX"], ns["EXPECTED_ERRORS"]


def pass_line(text):
    for line in text.splitlines():
        if line.startswith("PASS particles_lattice") or line.startswith("PASS r94b_particles"):
            return line
    return "<NO PASS LINE>"


def scan_dir(d):
    """cell -> dict(reps, lines, err_bytes, rc, common_prefix)"""
    out = {}
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.out")):
        stem = f.name.rsplit(".rep", 1)[0]
        err = f.with_suffix(".err")
        rc = f.with_suffix(".rc")
        text = f.read_text()
        entry = out.setdefault(stem, {"lines": [], "err_bytes": set(), "rc": []})
        entry["lines"].append(pass_line(text))
        entry["err_bytes"].add(len(err.read_text()) if err.exists() else -1)
        entry["rc"].append(int(rc.read_text().strip()) if rc.exists() else None)
    for stem, v in out.items():
        v["reps"] = len(v["lines"])
        v["out_uniq"] = len(set(v["lines"]))
        v["err_bytes"] = sorted(v["err_bytes"])
        v["common_prefix"] = common_prefix(v["lines"])
    return out


def common_prefix(strings):
    if not strings:
        return ""
    s = strings[0]
    for t in strings[1:]:
        i = 0
        while i < len(s) and i < len(t) and s[i] == t[i]:
            i += 1
        s = s[:i]
    return s


def receipts_of(d, case):
    """merged stdout+stderr, rc for every rep of a case stem (scout naming)."""
    got = []
    for out in sorted(d.glob(case + ".rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        got.append((out.name, out.read_text() + (err.read_text() if err.exists() else ""),
                    int(rc.read_text().strip()) if rc.exists() else None))
    return got


NUM_RE = re.compile(r"\b([a-z_][a-z_0-9]*)=(-?\d+)\b")


def nums(line):
    return {k: int(v) for k, v in NUM_RE.findall(line)}


def main():
    classify, seg_sha = load_classifier()
    ROWS, ROWS_PREFIX, EXPECTED = load_rows()
    report = {"classify_segment_sha256": seg_sha, "conditions": {}}

    print("classify_process segment sha256 =", seg_sha)
    print("scout rows: ROWS=%d ROWS_PREFIX=%d" % (len(ROWS), len(ROWS_PREFIX)))
    print()

    # ---- scout's own receipts, reproduced with this analyzer -----------------
    for label, d in [("scout_canonical", SCOUT / "runs"),
                     ("scout_loadtest", SCOUT / "runs" / "loadtest")]:
        rej_p, rej_f, n = [], [], 0
        for case, script, flags, exp, sig in ROWS_PREFIX:
            arm = next(f.split("=", 1)[1] for f in flags if f.startswith("--arm="))
            for name, text, code in receipts_of(d, case):
                n += 1
                if not classify(code, None, text, exp, sig, EXPECTED.get(case, ())):
                    rej_p.append((case, name))
        for case, script, flags, exp, sig in ROWS:
            arm = next(f.split("=", 1)[1] for f in flags if f.startswith("--arm="))
            for name, text, code in receipts_of(d, case):
                if not classify(code, None, text, exp, sig, EXPECTED.get(case, ())):
                    rej_f.append((case, name))
        print("[%s] receipts=%d ROWS_PREFIX_rejected=%d %s | ROWS_rejected=%d" % (
            label, n, len(rej_p), rej_p[:4], len(rej_f)))
        report[label] = {"receipts": n, "prefix_rejected": rej_p, "full_rejected": rej_f}
    print()

    # ---- this seat's conditions --------------------------------------------
    for cond in CONDS:
        d = RUNS / cond
        if not d.is_dir():
            continue
        rej_p, rej_f, checked = [], [], 0
        for case, script, flags, exp, sig in ROWS_PREFIX:
            for name, text, code in receipts_of(d, case):
                checked += 1
                if not classify(code, None, text, exp, sig, EXPECTED.get(case, ())):
                    rej_p.append((case, name))
        for case, script, flags, exp, sig in ROWS:
            for name, text, code in receipts_of(d, case):
                if not classify(code, None, text, exp, sig, EXPECTED.get(case, ())):
                    rej_f.append((case, name))
        cond_out = {"prefix_checked": checked, "prefix_rejected": rej_p, "full_rejected": rej_f}
        print("[%s] ROWS_PREFIX checked=%d rejected=%d" % (cond, checked, len(rej_p)))
        for case, name in rej_p:
            line = next((l for l in (d / name).read_text().splitlines()
                         if l.startswith("PASS")), "<none>")
            print("    REJECT %s  %s" % (name, line))
        print("        ROWS(full-line) rejected=%d" % len(rej_f))
        report["conditions"][cond] = cond_out

    # ---- measured-integer envelopes ----------------------------------------
    print("\n== measured-integer envelopes (quiet vs each condition) ==")
    base = scan_dir(RUNS / "quiet")
    env = {}
    for cond in CONDS:
        sc = scan_dir(RUNS / cond)
        for cell in SCOUT_CELLS:
            if cell in TEXT_FREE:
                continue
            stem = "r94_" + cell
            if stem not in sc or stem not in base:
                continue
            q_vals = collections.defaultdict(set)
            for l in base[stem]["lines"]:
                for k, v in nums(l).items():
                    q_vals[k].add(v)
            for l in sc[stem]["lines"]:
                for k, v in nums(l).items():
                    if k in q_vals and v not in q_vals[k]:
                        env.setdefault(cond, []).append((cell, k, v, sorted(q_vals[k])))
    for cond, items in sorted(env.items()):
        print("[%s] %d out-of-quiet-envelope values" % (cond, len(items)))
        seen = set()
        for cell, k, v, qv in items:
            sig = (cell, k, v)
            if sig in seen:
                continue
            seen.add(sig)
            print("    %-30s %s=%d  (quiet %s)" % (cell, k, v, qv))
    report["envelope_deviations"] = {c: [list(x) for x in v] for c, v in env.items()}

    # ---- attack-arm payloads ----------------------------------------------
    print("\n== attack arms per condition ==")
    arms = {}
    for cond in CONDS + ["smoke"]:
        sc = scan_dir(RUNS / cond)
        for stem in sorted(sc):
            if not stem.startswith("r94b_"):
                continue
            arms.setdefault(stem, {})[cond] = sorted(set(sc[stem]["lines"]))
    report["arms"] = arms
    for stem in sorted(arms):
        print("\n-- %s" % stem)
        for cond in CONDS + ["smoke"]:
            if cond not in arms[stem]:
                continue
            uniq = arms[stem][cond]
            for l in uniq:
                print("   %-9s %s" % (cond, l))

    # ---- ab paired comparison ---------------------------------------------
    print("\n== ab paired (default vs fixed-fps, interleaved) ==")
    ab = {}
    d = RUNS / "ab"
    if d.is_dir():
        for cell in AB_CELLS:
            for mode in AB_MODES:
                lines = []
                for out in sorted(d.glob("ab*_%s_%s.rep*.out" % (mode, cell))):
                    lines.append(pass_line(out.read_text()))
                if lines:
                    ab["%s|%s" % (cell, mode)] = sorted(set(lines))
        for k in sorted(ab):
            for l in ab[k]:
                print("   %-34s %s" % (k, l))
    report["ab"] = ab

    (RUNS / "analyze_r94b.json").write_text(json.dumps(report, indent=1))
    print("\nwrote", RUNS / "analyze_r94b.json")


if __name__ == "__main__":
    main()
