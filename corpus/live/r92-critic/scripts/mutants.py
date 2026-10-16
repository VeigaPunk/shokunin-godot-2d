#!/usr/bin/env python3
"""r92 critic seat — mutation tests against the COMMITTED fixture/harness.

Two mutant classes:
  FIXTURE mutants — patch a copy of the committed tilemap_lattice.gd in a
    scratch project, run the arm, re-classify with the PRODUCTION classifier.
    A claim is measured (not self-asserted) iff the mutant FAILs.
  HARNESS mutants — re-classify the seat's own real receipts with a single
    pin/allowlist/fragment perturbed. A row is discriminating iff the mutant
    FAILs; an allowlist entry is load-bearing iff removing it FAILs.

Nothing here writes to a tracked file; scratch projects live under the seat.
"""
import json, pathlib, shutil, subprocess, sys

SEAT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SEAT / "scripts"))
from probe import load_production, classify_receipt  # noqa: E402

PROJ = SEAT / "proj"
MUT = SEAT / "mutants"
RUNS = SEAT / "runs"
prod = load_production()

FIXTURE_MUTANTS = [
    # name, arm, old, new, expectation, rationale
    ("nav_f1_third_value", "nav",
     '_it("regions_f1", str(NavigationServer2D.map_get_regions(map).size()))',
     '_it("regions_f1", "2")', "FAIL",
     "a third regions_f1 value is admitted by neither payload"),
    ("nav_f2_zero", "nav",
     '_it("regions_f2", str(NavigationServer2D.map_get_regions(map).size()))',
     '_it("regions_f2", "0")', "FAIL",
     "regions_f2=1 is pinned in BOTH payloads (the settled law)"),
    ("nav_f1_stuck_zero", "nav",
     '_it("regions_f1", str(NavigationServer2D.map_get_regions(map).size()))',
     '_it("regions_f1", "0")', "PASS",
     "ENVELOPE COST: a permanent regression to the ratio>=2.5 mode still passes"),
    ("nav_f1_stuck_one_ff", "nav",
     '_it("regions_f1", str(NavigationServer2D.map_get_regions(map).size()))',
     '_it("regions_f1", "1")', "PASS",
     "control for the previous: the pinned production mode passes"),
    ("enc_cell_moved", "encoding",
     'layer.set_cell(Vector2i(7, -2), sid, Vector2i(0, 1), 0)',
     'layer.set_cell(Vector2i(7, -3), sid, Vector2i(0, 1), 0)', "FAIL",
     "the two_bytes/two_arr_len/stride pins are measured bytes"),
    ("enc_alt_field", "encoding",
     'layer.set_cell(Vector2i(3, 4), sid, Vector2i(1, 0), alt)',
     'layer.set_cell(Vector2i(3, 4), sid, Vector2i(1, 0), 0)', "FAIL",
     "alt_bytes pins the alternative-id field verbatim"),
    ("nullts_no_crash", "nullts",
     '\tvar td := layer.get_cell_tile_data(Vector2i(0, 0))',
     '\tvar td = null', "FAIL",
     "the row requires the crash (rc=-6), not just the arming diagnostic"),
    ("nullts_site_line_shift", "nullts",
     '\t_it("about_to_call_tile_data", "1")',
     '\t_it("about_to_call_tile_data", "1")\n\n', "FAIL",
     "the _nullts :927 site fragment is line-number-bound"),
    ("nullts_foreign_site", "nullts",
     '\tvar td := layer.get_cell_tile_data(Vector2i(0, 0))\n\t_it("td_after_set", "null" if td == null else "obj")\n\t_pass()',
     '\t_boom(layer)\n\t_it("td_after_set", "null")\n\t_pass()\n\nfunc _boom(layer: TileMapLayer) -> void:\n\tvar td := layer.get_cell_tile_data(Vector2i(0, 0))\n\t_it("td_after_set", "null" if td == null else "obj")',
     "FAIL",
     "same engine null-deref, different GDScript site -> site fragment must reject"),
    ("nullts_foreign_abort", "nullts",
     '\tvar td := layer.get_cell_tile_data(Vector2i(0, 0))\n\t_it("td_after_set", "null" if td == null else "obj")\n\t_pass()',
     '\tOS.crash("r92 forged abort")\n\t_pass()', "FAIL",
     "a foreign abort with the right exit code and the arming diagnostic"),
    ("nullts_foreign_cause", "nullts",
     [('\t\t"nullts":\n\t\t\t_nullts()',
       '\t\t"nullts":\n\t\t\t_nullts_forge()'),
      ('func _nullts() -> void:',
       'func _nullts_forge() -> void:\n\t_it("about_to_call_tile_data", "1")\n\tvar layer := TileMapLayer.new()\n\troot.add_child(layer)\n\tlayer.set_cell(Vector2i(0, 0), 0, Vector2i(0, 0), 0)\n\tvar td := layer.get_cell_tile_data(Vector2i(0, 0))\n\t_it("td_after_set", "null" if td == null else "obj")\n\nfunc _nullts() -> void:')], None,
     "FAIL",
     "same null-deref, same rc, same header, same stdout marker -- reached WITHOUT the _nullts:927 frame"),
    ("atlas_allowlist_dead", "atlas",
     '\tsrc.create_tile(Vector2i(0, 0))\n\t_it("tiles_after_dup", str(src.get_tiles_count()))',
     '\t_it("tiles_after_dup", str(src.get_tiles_count()))', "PASS-GATE-FALSE",
     "removing the refusal poke leaves the row PASSing but kills its allowlist entry"),
]


def run_mutant(name, arm, old, new, expect, rationale):
    src = (PROJ / "tilemap_lattice.gd").read_text()
    patches = old if isinstance(old, list) else [(old, new)]
    for o, n in patches:
        assert src.count(o) == 1, f"{name}: anchor not unique ({src.count(o)}): {o[:40]!r}"
        src = src.replace(o, n, 1)
    proj = MUT / name
    if proj.exists():
        shutil.rmtree(proj)
    shutil.copytree(PROJ, proj)
    (proj / "tilemap_lattice.gd").write_text(src)
    out = MUT / "receipts"
    out.mkdir(parents=True, exist_ok=True)
    tag = name
    rc = subprocess.run(
        ["python3", str(SEAT / "scripts" / "probe.py"), "run", "--proj", str(proj),
         "--outdir", str(out), "--tag", tag, "--arms", arm, "--reps", "1"],
        capture_output=True, text=True)
    if rc.returncode:
        return {"name": name, "arm": arm, "expect": expect, "error": rc.stderr[-400:]}
    code = int((out / f"{tag}.{arm}.rep1.rc").read_text().strip())
    o = (out / f"{tag}.{arm}.rep1.out").read_text()
    e = (out / f"{tag}.{arm}.rep1.err").read_text()
    case = "r92_tilemap_nullts_crash" if arm == "nullts" else f"r92_tilemap_{arm}"
    r = classify_receipt(prod, case, o, e, code)
    # census-style dead-entry check for the mutant receipt (floor gate)
    entries = prod["expected_errors"].get(case, ())
    dead = []
    for entry in entries:
        if not any((ln.strip() == entry) or
                   (entry.endswith(",") and ln.strip().startswith(entry)
                    and ln.strip().count("ERROR:") == 1)
                   for ln in (o + e).splitlines()):
            dead.append(entry)
    gate = not dead
    observed = ("FAIL" if not r["passed"] else
                ("PASS-GATE-FALSE" if dead else "PASS"))
    return {"name": name, "arm": arm, "expect": expect, "observed": observed,
            "rc": code, "passed": r["passed"], "dead_entries": len(dead),
            "gate_true": gate, "ok": observed == expect, "rationale": rationale,
            "stdout_tail": o.strip().splitlines()[-1][:160] if o.strip() else "",
            "stderr_head": next((l for l in e.splitlines() if "crash" in l.lower()), "")[:120]}


def harness_mutants():
    """Re-classify the seat's own real receipts with one pin perturbed."""
    res = []
    # (a) pin-side: every r92 pin is discriminating if perturbing one token fails
    perturbs = {
        "r92_tilemap_physics": ("travel=0.0000,1.9531", "travel=0.0000,1.9532"),
        "r92_tilemap_encoding": ("stride=12", "stride=16"),
        "r92_tilemap_nav": ("regions_f2=1", "regions_f2=0"),
        "r92_tilemap_cells": ("bad_src_readback=42", "bad_src_readback=43"),
        "r92_tilemap_timing": ("update_set_same_frame=hit", "update_set_same_frame=null"),
    }
    for case, (old, new) in perturbs.items():
        arm = case.replace("r92_tilemap_", "")
        sig = prod["cases"][case]["signature"]
        sigs = sig if isinstance(sig, (tuple, list)) else (sig,)
        sigs = tuple(s.replace(old, new) for s in sigs)
        stem = f"fresh.{arm}.rep1"
        o = (RUNS / f"{stem}.out").read_text()
        e = (RUNS / f"{stem}.err").read_text()
        code = int((RUNS / f"{stem}.rc").read_text().strip())
        ee = prod["expected_errors"].get(case, ())
        passed = any(prod["classify"](code, None, o + e, prod["cases"][case]["exit"], s, ee)
                     for s in sigs)
        res.append({"name": f"pin_{old.split('=')[0]}", "arm": arm, "expect": "FAIL",
                    "observed": "PASS" if passed else "FAIL", "ok": not passed,
                    "rationale": f"pin token {old} perturbed to {new}"})
    # (b) allowlist-side: drop one entry -> the row must FAIL (unrelated ERROR:)
    for case, entry in [("r92_tilemap_atlas", 0), ("r92_tilemap_srcids", 1)]:
        arm = case.replace("r92_tilemap_", "")
        stem = f"fresh.{arm}.rep1"
        o = (RUNS / f"{stem}.out").read_text()
        e = (RUNS / f"{stem}.err").read_text()
        code = int((RUNS / f"{stem}.rc").read_text().strip())
        ee = list(prod["expected_errors"][case])
        dropped = ee.pop(entry)
        sig = prod["cases"][case]["signature"]
        sigs = sig if isinstance(sig, (tuple, list)) else (sig,)
        passed = any(prod["classify"](code, None, o + e, prod["cases"][case]["exit"], s, tuple(ee))
                     for s in sigs)
        res.append({"name": f"allowlist_drop_{arm}", "arm": arm, "expect": "FAIL",
                    "observed": "PASS" if passed else "FAIL", "ok": not passed,
                    "rationale": f"entry {entry} dropped: {dropped[:50]}"})
    # (c) required_stderr-side: perturb the RECEIPT streams and re-run the
    # production check exactly as execute() does.
    stem = "fresh.nullts.rep1"
    o = (RUNS / f"{stem}.out").read_text()
    e = (RUNS / f"{stem}.err").read_text()
    case = "r92_tilemap_nullts_crash"
    sig = prod["cases"][case]["signature"]
    rs = prod["required_stderr"][case]

    def execute_check(stdout, stderr):
        ok = prod["classify"](-6, None, stdout + stderr, -6, sig, ())
        return ok and all(f in stderr for f in rs) and sig in stdout

    real = execute_check(o, e)
    # (c1) each fragment moved onto stdout only (merged-blob blindness shape)
    moved = []
    for f in rs:
        moved.append(execute_check(o + f, e.replace(f, "")))
    # (c2) signature moved onto stderr only
    sig_moved = execute_check(o.replace(sig, ""), sig + e)
    # (c3) each fragment deleted from the stderr text in turn
    dropped = [execute_check(o, e.replace(f, "")) for f in rs]
    res.append({"name": "nullts_stream_binding", "arm": "nullts", "expect": "FAIL",
                "observed": {"real_pass": real,
                             "fragment_on_stdout_only_passes": moved,
                             "signature_on_stderr_only_passes": sig_moved,
                             "fragment_deleted_passes": dropped},
                "ok": (real and not any(moved) and not sig_moved
                       and not any(dropped)),
                "rationale": "stream anchoring rejects both one-directional shapes"})
    # (d) exit-code-side: the -6 pin is load-bearing
    wrong_exit = prod["classify"](-11, None, o + e, -6, sig, ())
    res.append({"name": "nullts_exit_pin", "arm": "nullts", "expect": "FAIL",
                "observed": "PASS" if wrong_exit else "FAIL", "ok": not wrong_exit,
                "rationale": "rc=-6 required: rc=-11 (raw SIGSEGV) is rejected"})
    return res


if __name__ == "__main__":
    MUT.mkdir(exist_ok=True)
    results = []
    for m in FIXTURE_MUTANTS:
        r = run_mutant(*m)
        results.append(r)
        print(f"{'OK ' if r.get('ok') else 'BAD'} {r['name']}: expect={r['expect']} "
              f"observed={r.get('observed')} rc={r.get('rc')} "
              f"dead={r.get('dead_entries')} gate={r.get('gate_true')}", flush=True)
    hm = harness_mutants()
    for r in hm:
        print(f"{'OK ' if r['ok'] else 'BAD'} {r['name']}: expect={r['expect']} "
              f"observed={r['observed']}", flush=True)
    json.dump({"fixture": results, "harness": hm}, open(SEAT / "mutants.json", "w"), indent=1)
