#!/usr/bin/env python3
"""r99-boundary analyzer.

Reads:
  - the scout's frozen rows (../r99-scout/author-rows.py.txt) — read-only
  - the production classify_process, AST-extracted from corpus/fixtures/run_battery.py
  - this lane's receipts runs/<mode>/r99b_<cell>.rep<N>.{out,err,rc}
  - the scout's own receipts ../r99-scout/runs/... for the cross-seat replay check

Prints / writes runs/analyze_r99b.json:
  A  per-mode row verdicts (ROWS_PREFIX via the production classifier)
  B  cross-mode prefix diff (which pinned keys move, and to what)
  C  cross-seat replay diff (quiet receipts vs the scout's canonical + loadtest)
  D  probe-arm key table per mode
"""
import ast
import hashlib
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"
SCOUT = HERE.parent / "r99-scout"
FIXTURE = HERE.parent.parent / "fixtures" / "run_battery.py"

CELLS = ["census", "bus", "autoplay", "stoppos", "peak_calib", "mixblock", "advance",
         "finish", "loop_degenerate", "loop_pts", "gen", "gen_peak", "poly",
         "bus_peak", "p2d", "pan_law", "gen2d", "pause"]
CORE_MODES = ["quiet", "load", "ff30", "ff60", "ff120"]
EXTRA_MODES = ["maxfps30", "maxfps60", "maxfps120", "ff1", "single", "proj2d"]
MODES = CORE_MODES + EXTRA_MODES
ARMS = ["modeinfo", "mixphase", "startphase", "peakphase", "mixfree", "finfree", "advfree"]

src = FIXTURE.read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src, "classify_process not found"
SEG_SHA = hashlib.sha256(fn_src.encode()).hexdigest()
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

rows_ns = {}
exec((SCOUT / "author-rows.py.txt").read_text(), rows_ns)
ROWS_PREFIX = {case: sig for case, _s, _f, _e, sig in rows_ns["ROWS_PREFIX"]}
EXPECTED = rows_ns.get("EXPECTED_ERRORS", {})


def pass_line(text):
    for line in text.splitlines():
        if line.startswith("PASS r99_audio "):
            return line
    return ""


def prefix_of(text):
    return pass_line(text).split(" | ")[0]


def tail_of(text):
    parts = pass_line(text).split(" | ", 1)
    return parts[1] if len(parts) > 1 else ""


def tokens(text):
    return dict(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=(\S+)", text))


def receipts(mode, cell):
    out = []
    for p in sorted((RUNS / mode).glob(f"r99b_{cell}.rep*.out")):
        rcp = p.with_suffix(".rc")
        if not rcp.exists():
            continue
        txt = rcp.read_text().strip()
        if not txt:          # rc not yet written (batch in flight) or lost to a driver break
            continue
        out.append((p.name, p.read_text(), p.with_suffix(".err").read_text(), int(txt)))
    return out


def scout_receipts(cell):
    out = []
    for p in sorted((SCOUT / "runs").glob(f"r99_{cell}.rep*.out")):
        out.append((p.name, p.read_text(), p.with_suffix(".err").read_text(),
                    int(p.with_suffix(".rc").read_text().strip())))
    lt = SCOUT / "runs" / "loadtest"
    if lt.exists():
        for p in sorted(lt.glob(f"{cell}.rep*.out")):
            out.append(("loadtest/" + p.name, p.read_text(), p.with_suffix(".err").read_text(),
                        int(p.with_suffix(".rc").read_text().strip())))
    return out


report = {"segment_sha": SEG_SHA, "modes": {}, "cross_mode": {}, "cross_seat": {},
          "probes": {}, "present_modes": []}
present = [m for m in MODES if (RUNS / m).exists() and list((RUNS / m).glob("r99b_*.out"))]
report["present_modes"] = present

# --- A: per-mode verdicts ------------------------------------------------
for mode in present:
    cells = {}
    for cell in CELLS:
        rs = receipts(mode, cell)
        if not rs:
            cells[cell] = {"reps": 0}
            continue
        case = f"r99_audio_{cell}"
        sig = ROWS_PREFIX[case]
        allowed = EXPECTED.get(case, ())
        ok = 0
        bad = []
        for name, out, err, rc in rs:
            if classify_process(rc, None, out + err, 0, sig, allowed):
                ok += 1
            else:
                bad.append(name)
        prefixes = {prefix_of(o) for _n, o, _e, _r in rs}
        cells[cell] = {"reps": len(rs), "accepted": ok, "rejected": bad,
                       "prefix_uniq": len(prefixes),
                       "err_bytes": sorted({len(e) for _n, _o, e, _r in rs}),
                       "rc": [r for _n, _o, _e, r in rs]}
    report["modes"][mode] = cells

# --- B: cross-mode prefix diff ------------------------------------------
for cell in CELLS:
    per_mode = {}
    for mode in present:
        rs = receipts(mode, cell)
        if rs:
            per_mode[mode] = sorted({prefix_of(o) for _n, o, _e, _r in rs})
    allp = set()
    for v in per_mode.values():
        allp.update(v)
    varying = {}
    if len(allp) > 1:
        base = tokens(sorted(allp)[0])
        for other in sorted(allp)[1:]:
            oth = tokens(other)
            for k in sorted(set(base) | set(oth)):
                if base.get(k) != oth.get(k):
                    varying.setdefault(k, set()).update({base.get(k, "<missing>"), oth.get(k, "<missing>")})
    tails = {}
    for mode in present:
        rs = receipts(mode, cell)
        if rs:
            tails[mode] = sorted({tail_of(o) for _n, o, _e, _r in rs})
    report["cross_mode"][cell] = {
        "prefix_uniq": len(allp),
        "per_mode_uniq": {m: len(v) for m, v in per_mode.items()},
        "varying_keys": {k: sorted(v) for k, v in varying.items()},
        "per_mode_prefix": per_mode,
        "tail_uniq_per_mode": {m: len(v) for m, v in tails.items()},
    }

# --- C: cross-seat replay diff (quiet vs scout canonical+loadtest) -------
for cell in CELLS:
    mine = receipts("quiet", cell)
    theirs = scout_receipts(cell)
    if not mine or not theirs:
        continue
    mine_set = {(o, e, r) for _n, o, e, r in mine}
    their_set = {(o, e, r) for _n, o, e, r in theirs}
    mine_pfx = {prefix_of(o) for _n, o, _e, _r in mine}
    their_pfx = {prefix_of(o) for _n, o, _e, _r in theirs}
    mine_tail = {tail_of(o) for _n, o, _e, _r in mine}
    their_tail = {tail_of(o) for _n, o, _e, _r in theirs}
    report["cross_seat"][cell] = {
        "mine": len(mine_set), "theirs": len(their_set),
        "prefix_sets_equal": mine_pfx == their_pfx,
        "mine_prefix_uniq": len(mine_pfx), "theirs_prefix_uniq": len(their_pfx),
        "full_line_sets_equal": mine_set == their_set,
        "mine_tail_uniq": len(mine_tail), "theirs_tail_uniq": len(their_tail),
        "mine_tail_subset_of_theirs": mine_tail <= their_tail,
    }

# --- D: probe arms --------------------------------------------------------
for mode in present:
    arms = {}
    for arm in ARMS:
        rs = sorted((RUNS / mode).glob(f"r99b_probe_{arm}.rep*.out"))
        vals = []
        for p in rs:
            for line in p.read_text().splitlines():
                if line.startswith(f"PASS r99b {arm} "):
                    vals.append(line[len(f"PASS r99b {arm} "):])
        if vals:
            arms[arm] = vals
    if arms:
        report["probes"][mode] = arms

(RUNS / "analyze_r99b.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

# --- console summary ------------------------------------------------------
print(f"segment_sha={SEG_SHA}")
print(f"present_modes={present}")
print("\n== A: per-mode ROWS_PREFIX verdicts (production classify_process) ==")
for mode in present:
    rej = {c: v["rejected"] for c, v in report["modes"][mode].items()
           if v.get("rejected")}
    total = sum(v.get("reps", 0) for v in report["modes"][mode].values())
    acc = sum(v.get("accepted", 0) for v in report["modes"][mode].values())
    print(f"{mode:10s} {acc}/{total} accepted  rejected={rej}")
print("\n== B: cross-mode prefix diff ==")
for cell in CELLS:
    cm = report["cross_mode"].get(cell, {})
    if cm.get("prefix_uniq", 1) > 1:
        print(f"{cell:18s} prefix_uniq={cm['prefix_uniq']} keys={cm['varying_keys']}")
print("\n== C: cross-seat replay (quiet) ==")
for cell, v in report["cross_seat"].items():
    if not v["prefix_sets_equal"]:
        print(f"{cell:18s} PREFIX DIFF mine_uniq={v['mine_prefix_uniq']} theirs_uniq={v['theirs_prefix_uniq']}")
    elif not v["mine_tail_subset_of_theirs"]:
        print(f"{cell:18s} prefix OK, tail not a subset of the scout's "
              f"(mine_uniq={v['mine_tail_uniq']} theirs_uniq={v['theirs_tail_uniq']})")
print("(no PREFIX DIFF lines above => every quiet pinned prefix equals the scout's)")
print("\n== D: probe arms ==")
for mode in present:
    for arm, vals in report["probes"].get(mode, {}).items():
        for v in vals:
            print(f"{mode:10s} {arm:10s} {v}")
