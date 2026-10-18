#!/usr/bin/env python3
"""r101-VER-9: discrimination self-test for ver9_prior_rows.py.

Builds a post-dedupe "current" receipt from a real independent r100 battery run
and a matrix of single-defect mutants, then asserts the comparator's verdict
and failure class for each.  Nothing here runs the battery or touches the repo.

Usage:
  python3 ver9_selftest.py <prior-receipt.json> <runner.py> <workdir>
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPARATOR = HERE / "ver9_prior_rows.py"
BASELINE = HERE / "ver9_baseline_r100.json"
FIELDS = ("script", "flags", "expected_exit", "actual_exit", "signature", "verdict", "error")


def load(path):
    return json.loads(Path(path).read_bytes())


def make_current(src_receipt, out, strip_dups=("crash_spontaneous_sigabrt", "crash_self_sigkill")):
    """Mirror the 9ede7c50 dedupe: keep the first copy of each duplicated name.

    Verifies the removed copies are value-identical to the kept one before
    stripping, so the strip is a multiplicity change only, never a value change.
    """
    payload = load(src_receipt)
    seen, rows = {}, []
    for x in payload["results"]:
        name = x["case"]
        if name in strip_dups:
            if name in seen:
                a = {f: seen[name].get(f) for f in FIELDS}
                b = {f: x.get(f) for f in FIELDS}
                assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), name
                continue
            seen[name] = x
        rows.append(x)
    payload["results"] = rows
    Path(out).write_text(json.dumps(payload, indent=1) + "\n")
    return payload


def run_case(work, current, expect, expect_class, label, prefixes=(), runner=None,
             registry_only=False):
    out = work / f"report_{label}.json"
    cmd = [sys.executable, str(COMPARATOR), "--baseline", str(BASELINE),
           "--report", str(out)]
    if registry_only:
        cmd += ["--registry-only"]
    else:
        cmd += ["--current", str(current)]
    if prefixes:
        cmd += ["--expect-new-prefixes", *prefixes]
    if runner:
        cmd += ["--runner", str(runner)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    report = json.loads(out.read_text())
    classes = sorted({f["class"] for f in report["failures"]})
    ok = (report["verdict"] == expect)
    if expect == "FAIL":
        ok = ok and expect_class in classes
    else:
        ok = ok and not classes
    return {"label": label, "expected": expect, "expected_class": expect_class,
            "observed_verdict": report["verdict"], "observed_classes": classes,
            "ok": ok, "rc": proc.returncode, "mode": report["mode"],
            "criterion": report["criteria"]["new_prefix_census"]}


def slim(results):
    """Keep only comparison-scope fields (the mutant is then the only delta)."""
    out = []
    for x in results:
        if "script" in x:
            out.append({k: x.get(k) for k in ("case",) + FIELDS})
        else:
            out.append({k: x[k] for k in ("case", "verdict", "mode", "discriminations",
                                          "census") if k in x})
    return out


def main() -> int:
    src_receipt, runner, workdir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    work = Path(workdir)
    (work / "mut").mkdir(parents=True, exist_ok=True)

    cur = work / "cur_dedup.json"
    payload = make_current(src_receipt, cur)
    n_cased = sum(1 for x in payload["results"] if "script" in x)
    print(f"current built from {src_receipt}: rows={len(payload['results'])} cased={n_cased}")

    base = load(cur)
    rows = base["results"]
    names = [x["case"] for x in rows if "script" in x]

    def write(label, mutate):
        p = work / "mut" / f"{label}.json"
        doc = {"verdict": base.get("verdict"),
               "results": slim(json.loads(json.dumps(base["results"])))}
        mutate(doc["results"])
        p.write_text(json.dumps(doc, separators=(",", ":")) + "\n")
        return p

    def first(results, name):
        return next(x for x in results if x["case"] == name and "script" in x)

    m_drop = write("drop_row", lambda r: r.remove(first(r, "mechanic")))
    m_dup = write("dup_row", lambda r: r.insert(0, dict(first(r, "r100_gui_drag"))))
    m_verdict = write("verdict_flip", lambda r: first(r, "r100_gui_census").update(verdict="FAIL"))
    m_sig = write("sig_char_flip", lambda r: first(r, "r100_gui_clip").update(
        signature=first(r, "r100_gui_clip")["signature"][:-1] + "X"))
    m_exp = write("expected_exit_flip", lambda r: first(r, "r100_gui_touch").update(
        expected_exit=first(r, "r100_gui_touch")["expected_exit"] + 1))
    m_err = write("error_field_set", lambda r: first(r, "r100_gui_motion").update(error="Timeout"))
    m_pdrop = write("probe_drop", lambda r: r.remove(
        next(x for x in r if x["case"] == "probe_descendant_pipe_eof")))
    m_pverdict = write("probe_verdict_flip", lambda r: next(
        x for x in r if x["case"] == "probe_spontaneous_crash_classification").update(verdict="FAIL"))
    m_dflip = write("disc_flip", lambda r: next(
        x for x in r if x["case"] == "probe_descendant_error_spoof"
    )["discriminations"].update({"genuine_error_captured": False}))
    m_ddel = write("disc_delete", lambda r: next(
        x for x in r if x["case"] == "probe_while_live_signature_gate"
    )["discriminations"].pop("genuine_marker_accepted_while_live"))
    m_census = write("census_dead", lambda r: next(
        x for x in r if x["case"] == "probe_error_clause_surface"
    )["census"].update({"dead_entry_count": 1}))
    m_new = write("new_ok", lambda r: r.append(dict(
        first(r, "r100_gui_census"), case="r101_export_prod_base", verdict="PASS")))
    m_newbad = write("new_fail", lambda r: r.append(dict(
        first(r, "r100_gui_census"), case="r101_export_prod_base", verdict="FAIL")))
    m_stray = write("new_stray", lambda r: r.append(dict(
        first(r, "r100_gui_census"), case="r999_stray_row", verdict="PASS")))

    stub = work / "runner_stub.py"
    body = "".join(f'    ("{n}", "x.gd", [], 0, "PASS"),\n'
                   for n in ("mechanic", "scene_signal"))
    stub.write_text("CASES = [\n" + body + "]\n")

    cases = [
        ("R0 real-independent-run post-dedupe", cur, "PASS", None, (), runner),
        ("M1 prior row dropped", m_drop, "FAIL", "prior_case_dropped", (), None),
        ("M2 extra identical copy (forgery)", m_dup, "FAIL", "multiplicity", (), None),
        ("M3 verdict flip", m_verdict, "FAIL", "non_pass_rows", (), None),
        ("M4 one signature char", m_sig, "FAIL", "prior_tuple_mismatch", (), None),
        ("M5 expected_exit drift", m_exp, "FAIL", "prior_tuple_mismatch", (), None),
        ("M6 error field drift", m_err, "FAIL", "prior_tuple_mismatch", (), None),
        ("M7 probe row dropped", m_pdrop, "FAIL", "prior_probe_dropped", (), None),
        ("M8 probe verdict flip", m_pverdict, "FAIL", "probe_verdict_drift", (), None),
        ("M9 discrimination flipped", m_dflip, "FAIL", "discriminations_not_preserved", (), None),
        ("M10 discrimination deleted", m_ddel, "FAIL", "discriminations_not_preserved", (), None),
        ("M11 census dead entry", m_census, "FAIL", "census_dead_entry", (), None),
        ("M12 new row ok w/ prefix", m_new, "PASS", None, ("r101_",), None),
        ("M13 new row non-PASS", m_newbad, "FAIL", "new_row_non_pass", ("r101_",), None),
        ("M14 new row stray prefix", m_stray, "FAIL", "new_row_unexpected_prefix", ("r101_",), None),
        ("M15 registry drop (stub runner)", cur, "FAIL", "registry_prior_case_missing", (), stub),
        ("M16 registry-only preflight (real)", None, "PASS", None, (), runner),
        ("M17 registry-only via stub runner", None, "FAIL", "registry_prior_case_missing", (), stub),
    ]
    matrix = []
    for label, c, e, ec, p, r in cases:
        ro = c is None
        matrix.append(run_case(work, c, e, ec, label, p, r, registry_only=ro))
    for m in matrix:
        flag = "ok  " if m["ok"] else "BAD "
        print(f'{flag}{m["label"]:<36} expect={m["expected"]:<4} '
              f'got={m["observed_verdict"]:<4} classes={m["observed_classes"]}')
    (HERE / "ver9_selftest_matrix.json").write_text(json.dumps(matrix, indent=1) + "\n")
    bad = [m for m in matrix if not m["ok"]]
    print(f"selftest: {len(matrix) - len(bad)}/{len(matrix)} expected; rc={1 if bad else 0}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
