#!/usr/bin/env python3
"""r95-simplifier fold re-verification on the LANDED bytes (9cd47507).

For all 52 r95 rows (17 `dss_lattice_*` + 35 `r95b_order_*`) this script:

  1. launches each row N times in the battery's exact launch shape
     (`godot --headless --path <scratch> --script res://<fixture> -- <flags>`,
     8 s bound, separate streams merged like the production `run_process`),
  2. classifies every launch with the **production** `classify_process`
     AST-extracted from the committed harness (segment sha recorded),
  3. checks the emitted PASS line against the committed signature
     (exact for full-line rows, prefix for the four head-prefix rows),
  4. re-derives the boundary-fold laws from the FRESH receipts in Python
     (k(k-1) ladder arithmetic, perm0-7 distinctness under a fixed tag->x map,
     scoutrev counter-pin, celloff translation invariance, twopiles
     co-presence, warm k32/keep8, free/readd, cap40 set32_distinct=5,
     layers k0/k1 conditions, rigid determinism),
  5. proves the emitted bytes are rep-stable modulo the declared unstable
     diagnostic keys (`ids`, `env`, `fresh_id`, `t*_bodypos`), which the
     fixture itself documents as non-signature diagnostics.

Usage: python3 verify_folds.py [--reps 3]
Outputs: fold-verification.json, fold-verification.log, fold-runs/<stamp>/
"""
import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CF = HERE / "committed-fixtures"
HARNESS = CF / "run_battery.py"
REPO = HERE.parents[2]
FIXTURES = REPO / "corpus" / "fixtures"  # staging source, as the battery does
GODOT = "godot"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
MASK_KEYS = ("ids", "env", "fresh_id")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract_rows_and_classifier():
    src = HARNESS.read_text()
    tree = ast.parse(src)
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": list(t[2]),
                               "expected_exit": t[3], "signature": t[4]}
    r95 = {k: v for k, v in cases.items()
           if k.startswith("dss_lattice_") or k.startswith("r95b_order_")}
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
    segment = ast.get_source_segment(src, fn)
    ns = {}
    exec("import re\n" + segment, ns)
    return r95, ns["classify_process"], hashlib.sha256(segment.encode()).hexdigest()


def stage_scratch(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    src = FIXTURES
    for item in src.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    pf = dest / "project.godot"
    pf.write_text(pf.read_text().replace(
        'config/name="MechanicOneShotTest"',
        'config/name="MechanicOneShotTest-%s"' % dest.name, 1))
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    chain.write_text(text.replace(
        anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    return dest


def launch(scratch: Path, script: str, flags: list, timeout=8):
    cmd = [GODOT, "--headless", "--path", str(scratch),
           "--script", "res://" + script, "--", *flags]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return out, err, None, "TIMEOUT"
    except OSError as exc:
        return "", str(exc), None, "OSError"


def mask_diag(stdout: str) -> str:
    lines = []
    for l in stdout.splitlines():
        m = re.match(r"^R95B \S+ (\w+)=", l)
        if m and (m.group(1) in MASK_KEYS or re.fullmatch(r"t\d+_bodypos", m.group(1))):
            lines.append("MASKED %s" % m.group(1))
        else:
            lines.append(l)
    return "\n".join(lines)


def kvparse(pass_line: str) -> dict:
    return dict(re.findall(r"([A-Za-z0-9_]+)=(\S+)", pass_line))


def ladder_dict(s: str) -> dict:
    out = {}
    for m in re.finditer(r"t(\d+):([0-9,]+)", s):
        out[int(m.group(1))] = m.group(2)
    return out


def law_checks(fresh: dict) -> list:
    """fresh: row -> PASS line. Returns [(check, ok, detail), ...]."""
    res = []

    def add(name, ok, detail=""):
        res.append((name, bool(ok), detail))

    # ---- canon: dense ladder, t20==t0, k(k-1)=20, t64==t4 ----
    p = kvparse(fresh["r95b_order_canon"])
    lad = ladder_dict(p["ladder"])
    add("canon cycle_len_dense==20", p.get("cycle_len_dense") == "20", p.get("cycle_len_dense"))
    add("canon distinct_ticks==20", p.get("distinct_ticks") == "20", p.get("distinct_ticks"))
    add("canon t0==0,1,2,3,4", p.get("t0_pidx") == "0,1,2,3,4", p.get("t0_pidx"))
    add("canon t20==t0", lad.get(20) == lad.get(0), "%s vs %s" % (lad.get(20), lad.get(0)))
    add("canon t21==t1", lad.get(21) == lad.get(1), "%s vs %s" % (lad.get(21), lad.get(1)))
    add("canon t64==t4 (64-3*20)", lad.get(64) == lad.get(4), "%s vs %s" % (lad.get(64), lad.get(4)))
    add("canon t40==t0", lad.get(40) == lad.get(0), "%s vs %s" % (lad.get(40), lad.get(0)))
    add("canon t48==t8", lad.get(48) == lad.get(8), "%s vs %s" % (lad.get(48), lad.get(8)))
    add("canon t56==t16", lad.get(56) == lad.get(16), "%s vs %s" % (lad.get(56), lad.get(16)))
    add("canon t2_pt_eq_sh", p.get("t2_pt_eq_sh") == "true")
    add("canon pt_stable_interleaved", p.get("pt_stable_interleaved") == "true")
    add("canon end_pt_eq_sh", p.get("end_pt_eq_sh") == "true")

    # ---- periodx k=2..10: cycle_len == k(k-1) == expected, distinct == same ----
    for k in (2, 3, 4, 5, 6, 7, 8, 10):
        row = "r95b_order_periodx_k%d" % k
        if row not in fresh:
            continue
        p = kvparse(fresh[row])
        want = k * (k - 1)
        add("%s k==%d" % (row, k), p.get("k") == str(k), p.get("k"))
        add("%s expected_kk1==%d" % (row, want), p.get("expected_kk1") == str(want), p.get("expected_kk1"))
        add("%s cycle_len==%d" % (row, want), p.get("cycle_len") == str(want), p.get("cycle_len"))
        add("%s distinct_ticks==%d" % (row, want), p.get("distinct_ticks") == str(want), p.get("distinct_ticks"))
        add("%s n_ticks==%d" % (row, want + 3), p.get("n_ticks") == str(want + 3), p.get("n_ticks"))
        add("%s t0 is insertion order" % row, p.get("t0_vec") == "[%s]" % ",".join("p%d#0" % i for i in range(k)),
            p.get("t0_vec"))
        for key in ("t2_vec", "t3_vec"):
            tags = re.findall(r"p(\d+)#0", p.get(key, ""))
            add("%s %s is a permutation of 0..%d" % (row, key, k - 1),
                sorted(int(t) for t in tags) == list(range(k)), p.get(key))

    # k=5 spacing-8 identical to spacing-4
    p5 = kvparse(fresh["r95b_order_periodx_k5"])
    p5s = kvparse(fresh["r95b_order_periodx_k5s8"])
    add("k5 spacing-independent", all(p5.get(x) == p5s.get(x) for x in
                                      ("cycle_len", "distinct_ticks", "t0_vec", "t2_vec", "t3_vec")),
        "s4 cycle=%s s8 cycle=%s" % (p5.get("cycle_len"), p5s.get("cycle_len")))
    add("k5s8 spacing==8.0", p5s.get("spacing") == "8.0", p5s.get("spacing"))

    # ---- period (k=5) ----
    pp = kvparse(fresh["r95b_order_period_k5"])
    add("period_k5 cycle_len==20", pp.get("cycle_len") == "20", pp.get("cycle_len"))
    add("period_k5 distinct==20", pp.get("distinct_ticks") == "20", pp.get("distinct_ticks"))

    # ---- perm0..7: fixed tag->x map, 8 distinct ladders ----
    perm_t2, perm_relpos, perm_ladders, perm_add = {}, {}, {}, {}
    for i in range(8):
        row = "r95b_order_perm%d" % i
        p = kvparse(fresh[row])
        perm_add[i] = p.get("add_order")
        perm_t2[i] = p.get("t2_vec")
        perm_relpos[i] = p.get("t2_relpos")
        perm_ladders[i] = p.get("ladder")
        # fixed tag->x map: a@0 b@8 c@16 d@24 e@32
        want = {"a": "0.0000", "b": "8.0000", "c": "16.0000", "d": "24.0000", "e": "32.0000"}
        pairs = re.findall(r"([a-e])#0", p.get("t2_vec", ""))
        rel = p.get("t2_relpos", "").strip("[]").split("|")
        ok = len(pairs) == 5 and len(rel) == 5
        detail = ""
        if ok:
            for tag, rp in zip(pairs, rel):
                x = rp.split(",")[0]
                if want[tag] != x:
                    ok = False
                    detail = "%s@%s" % (tag, x)
        add("%s t2_vec maps tag->fixed x" % row, ok, detail or p.get("t2_vec"))
        add("%s map key present" % row, p.get("map") == "[a@0,b@8,c@16,d@24,e@32]", p.get("map"))
    add("perm0-7: 8 distinct add_order", len(set(perm_add.values())) == 8, sorted(perm_add.values()))
    add("perm0-7: 8 distinct t2_vec", len(set(perm_t2.values())) == 8, len(set(perm_t2.values())))
    add("perm0-7: 8 distinct ladders", len(set(perm_ladders.values())) == 8, len(set(perm_ladders.values())))
    add("perm0: add_order==a,b,c,d,e", perm_add[0] == "[a,b,c,d,e]", perm_add[0])

    # ---- scoutrev: label permutation of the same construction ----
    sr = kvparse(fresh["r95b_order_scoutrev"])
    add("scoutrev t2_vec_matches_scout_row", sr.get("t2_vec_matches_scout_row") == "true")
    add("scoutrev t2_relpos_equals_canon", sr.get("t2_relpos_equals_canon") == "true")
    add("scoutrev relpos == canon relpos (cross-row)",
        sr.get("t2_relpos") == kvparse(fresh["r95b_order_canon"]).get("t2_relpos"),
        "%s vs %s" % (sr.get("t2_relpos"), kvparse(fresh["r95b_order_canon"]).get("t2_relpos")))
    add("scoutrev t2_vec != canon t2_vec (labels differ)",
        sr.get("t2_vec") != kvparse(fresh["r95b_order_canon"]).get("t2_vec"))

    # ---- celloff: translation invariance ----
    co = {name: kvparse(fresh["r95b_order_celloff_%s" % name]) for name in ("x0", "x1000", "y1000")}
    add("celloff ladders identical x0/x1000",
        co["x0"].get("ladder") == co["x1000"].get("ladder"),
        "%s vs %s" % (co["x0"].get("ladder"), co["x1000"].get("ladder")))
    add("celloff ladders identical x0/y1000",
        co["x0"].get("ladder") == co["y1000"].get("ladder"),
        "%s vs %s" % (co["x0"].get("ladder"), co["y1000"].get("ladder")))
    add("celloff relpos identical x0/x1000",
        co["x0"].get("t2_relpos") == co["x1000"].get("t2_relpos"))
    add("celloff off echoed", co["x1000"].get("off") == "1000.0000" and co["y1000"].get("off") == "0.0000")

    # ---- twopiles: co-presence attribution ----
    tp = kvparse(fresh["r95b_order_twopiles"])
    add("twopiles A-alone != A-with-B (t2 vs t4)",
        tp.get("a_t2_vec") != tp.get("a_t4_with_b_vec"),
        "%s vs %s" % (tp.get("a_t2_vec"), tp.get("a_t4_with_b_vec")))
    add("twopiles B pile is a 5-vector",
        len(re.findall(r"#0", tp.get("b_t2_vec", ""))) == 5, tp.get("b_t2_vec"))

    # ---- warm k32 inert vs canon, keep8 perturbs ----
    w32 = kvparse(fresh["r95b_order_warm_k32"])
    w8 = kvparse(fresh["r95b_order_warm_keep8"])
    canon_lad = ladder_dict(kvparse(fresh["r95b_order_canon"]).get("ladder", ""))
    lad32 = ladder_dict(w32.get("ladder", ""))
    common = sorted(set(lad32) & set(canon_lad))
    same = all(lad32[t] == canon_lad[t] for t in common)
    add("warm_k32 ladder == canon on common ticks", same,
        ", ".join("t%d %s/%s" % (t, lad32[t], canon_lad[t]) for t in common if lad32[t] != canon_lad[t]) or "all equal")
    add("warm_keep8 t2_vec != canon t2_vec",
        w8.get("t2_vec") != kvparse(fresh["r95b_order_canon"]).get("t2_vec"),
        "%s vs %s" % (w8.get("t2_vec"), kvparse(fresh["r95b_order_canon"]).get("t2_vec")))
    add("warm_keep8 distinct_ticks==4", w8.get("distinct_ticks") == "4", w8.get("distinct_ticks"))

    # ---- free: order matters, post-free cycle k=3 -> 6 ----
    fab = kvparse(fresh["r95b_order_free_ab"])
    fba = kvparse(fresh["r95b_order_free_ba"])
    add("free_ab != free_ba ladders", fab.get("ladder") != fba.get("ladder"))
    for tag, p in (("ab", fab), ("ba", fba)):
        lad = ladder_dict(p.get("ladder", ""))
        add("free_%s post-free t2==t8 (k=3 cycle 6)" % tag, lad.get(2) == lad.get(8),
            "%s vs %s" % (lad.get(2), lad.get(8)))
        add("free_%s freed echoed" % tag, p.get("freed") == ("[a,b]" if tag == "ab" else "[b,a]"),
            p.get("freed"))

    # ---- readd: fresh body inherits the freed slot ----
    ra = kvparse(fresh["r95b_order_readd_a"])
    add("readd which==a", ra.get("which") == "a")
    add("readd set at t16 has 5 entries",
        len(re.findall(r"#0", ra.get("set", ""))) == 5, ra.get("set"))

    # ---- cap40: set is NOT invariant above the cap ----
    caps = {i: kvparse(fresh["r95b_order_cap40_p%d" % i]) for i in range(3)}
    for i, p in caps.items():
        add("cap40_p%d n0==0" % i, p.get("n0") == "0", p.get("n0"))
        add("cap40_p%d n32==32" % i, p.get("n32") == "32", p.get("n32"))
        add("cap40_p%d n64==40" % i, p.get("n64") == "40", p.get("n64"))
        add("cap40_p%d set32_distinct==5" % i, p.get("set32_distinct") == "5", p.get("set32_distinct"))
        add("cap40_p%d set32_t2 has 32 entries" % i,
            len(re.findall(r"#0", p.get("set32_t2", ""))) == 32)
    add("cap40 set32_t2 distinct across p0/p1/p2",
        len({caps[i].get("set32_t2") for i in range(3)}) == 3)

    # ---- layers: order agreement is canvas-layer-conditional ----
    l0 = kvparse(fresh["r95b_order_layers_k0"])
    l1 = kvparse(fresh["r95b_order_layers_k1"])
    add("layers_k0 pt_eq_sh==true", l0.get("pt_eq_sh") == "true", l0.get("pt_eq_sh"))
    add("layers_k0 sh_len==5", l0.get("sh_len") == "5", l0.get("sh_len"))
    add("layers_k0 pt0_t2_eq_sh==true", l0.get("pt0_t2_eq_sh") == "true")
    add("layers_k1 pt_eq_sh==false", l1.get("pt_eq_sh") == "false", l1.get("pt_eq_sh"))
    add("layers_k1 sh_len==6", l1.get("sh_len") == "6", l1.get("sh_len"))
    add("layers_k1 pt0_t2_eq_sh==false", l1.get("pt0_t2_eq_sh") == "false")
    add("layers_k1 invisible collider perturbs pt0 ladder",
        l0.get("pt0_ladder") != l1.get("pt0_ladder"))

    # ---- rigid: solver determinism ----
    rg = kvparse(fresh["r95b_order_rigid"])
    add("rigid distinct_ticks==1", rg.get("distinct_ticks") == "1", rg.get("distinct_ticks"))
    add("rigid t10_relpos pinned", rg.get("t10_relpos") == "[15.9999,14.8732]", rg.get("t10_relpos"))

    # ---- dss cross-row rev checks ----
    def dsskv(row):
        return dict(re.findall(r"(\w+)=(\[.*?\]|\S+)", fresh[row]))

    add("point_cap_rev add_order is reverse of point_cap",
        dsskv("dss_lattice_point_cap_rev").get("add_order") == "[e,d,c,b,a]")
    add("order_core_rev add_order is reverse of order_core",
        dsskv("dss_lattice_order_core_rev").get("add_order") == "[e,d,c,b,a]")
    add("ray_order_rev tie==tie_a vs ray_order tie==tie_b",
        "tie=r={tie_a" in fresh["dss_lattice_ray_order_rev"]
        and "tie=r={tie_b" in fresh["dss_lattice_ray_order"])
    add("shape_lattice_rev touch==[a#0] vs shape_lattice touch==[e#0]",
        "touch=[a#0]" in fresh["dss_lattice_shape_rev"]
        and "touch=[e#0]" in fresh["dss_lattice_shape"])
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    args = ap.parse_args()

    r95, classify_process, segment_sha = extract_rows_and_classifier()
    print("r95 rows: %d   production classify_process segment sha256: %s"
          % (len(r95), segment_sha))
    run_dir = HERE / "fold-runs" / STAMP
    scratch = stage_scratch(run_dir / "scratch-committed")
    print("scratch: %s" % scratch)

    per_row, fresh_pass = {}, {}
    t0 = time.time()
    for i, (row, spec) in enumerate(sorted(r95.items()), 1):
        reps = []
        for rep in range(1, args.reps + 1):
            out, err, rc, terr = launch(scratch, spec["script"], spec["flags"])
            merged = out + err
            passed = classify_process(rc, terr, merged, spec["expected_exit"],
                                      spec["signature"], ())
            pass_line = next((l for l in out.splitlines() if l.startswith("PASS ")), "")
            masked = mask_diag(out)
            reps.append({"rep": rep, "rc": rc, "error": terr, "passed": passed,
                         "pass_line": pass_line, "masked_sha": hashlib.sha256(masked.encode()).hexdigest(),
                         "stdout": out, "stderr": err})
            if rep == 1:
                fresh_pass[row] = pass_line
        per_row[row] = reps
        ok = sum(1 for r in reps if r["passed"])
        exact = all(r["pass_line"] == spec["signature"] for r in reps)
        prefix = all(r["pass_line"].startswith(spec["signature"]) for r in reps)
        stable = len({r["masked_sha"] for r in reps}) == 1
        print("%3d/%d %-34s pass=%d/%d exact=%s prefix=%s masked_stable=%s"
              % (i, len(r95), row, ok, len(reps), exact, prefix, stable))
        sys.stdout.flush()

    print("launch phase: %.1fs" % (time.time() - t0))

    laws = law_checks(fresh_pass)
    bad = [l for l in laws if not l[1]]
    print()
    print("== law checks: %d, failures: %d ==" % (len(laws), len(bad)))
    for name, ok, detail in laws:
        print("  %s %s %s" % ("OK  " if ok else "FAIL", name, ("| " + str(detail)) if detail else ""))

    summary = {
        "stamp": STAMP,
        "reps": args.reps,
        "rows": len(r95),
        "production_classify_process_sha256": segment_sha,
        "scratch": str(scratch),
        "per_row": {row: {
            "script": r95[row]["script"], "flags": r95[row]["flags"],
            "signature_len": len(r95[row]["signature"]),
            "passes": sum(1 for r in reps if r["passed"]),
            "exact_line": all(r["pass_line"] == r95[row]["signature"] for r in reps),
            "prefix_line": all(r["pass_line"].startswith(r95[row]["signature"]) for r in reps),
            "masked_stable": len({r["masked_sha"] for r in reps}) == 1,
            "receipts": [{k: v for k, v in r.items() if k not in ("stdout", "stderr")}
                         for r in reps],
        } for row, reps in per_row.items()},
        "laws": [{"check": n, "ok": ok, "detail": d} for n, ok, d in laws],
        "law_failures": len(bad),
        "all_rows_pass_all_reps": all(
            all(r["passed"] for r in reps) for reps in per_row.values()),
    }
    (HERE / "fold-verification.json").write_text(json.dumps(summary, indent=1))
    print()
    print("all rows pass all reps: %s" % summary["all_rows_pass_all_reps"])
    print("law failures: %d" % summary["law_failures"])
    return 0 if summary["all_rows_pass_all_reps"] and not bad else 1


if __name__ == "__main__":
    sys.exit(main())
