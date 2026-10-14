#!/usr/bin/env python3
"""r61-verifier: independent forgery spot-checks for the spontaneous-crash meta row.

ast-extracts classify_process from the COMMITTED runner and feeds forged
inputs; then re-evaluates the committed crash_meta_ok expression verbatim
against a markerless -6 construction.
"""
import ast, json, sys, textwrap, pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
SRC = REPO / "corpus/fixtures/run_battery.py"
VERDICTS = REPO / "corpus/live/r61-verifier/runs/20261013T230731579744Z/verdicts.json"

src = SRC.read_text()
tree = ast.parse(src)
node = None
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and n.name == "classify_process":
        node = n  # first definition inside main()
        break
assert node is not None, "classify_process not found"
seg = ast.get_source_segment(src, node)
ns = {}
exec(textwrap.dedent(seg), ns)
classify_process = ns["classify_process"]
print("extracted classify_process: lines", node.lineno, "-", node.end_lineno)

results = {r["case"]: r for r in json.load(open(VERDICTS))["results"]}
sigabrt = results["crash_spontaneous_sigabrt"]
captured = "\n".join(sigabrt["output"])
MARKER = "SPONTANEOUS_CRASH_PROBE: expected signature"
ALLOW = ("ERROR: r60 spontaneous crash probe",)

# --- rejected arm 1: real captured sigabrt output, expected -6, EMPTY allowlist
t1 = classify_process(sigabrt["actual_exit"], sigabrt["error"], captured, -6, MARKER, ())
print("T1 captured sigabrt, expected -6, allowlist=() ->", t1, "(expect False)")

# --- sanity: same input WITH the committed allowlist -> True
t2 = classify_process(sigabrt["actual_exit"], sigabrt["error"], captured, -6, MARKER, ALLOW)
print("T2 captured sigabrt, expected -6, allowlist=(crash err,) ->", t2, "(expect True)")

# --- rejected arm 2: markerless -6 construction through the committed
# crash_meta_ok expression (lines 529-538 of committed run_battery.py,
# re-evaluated verbatim against a forged record whose output lacks the
# ERROR marker that the allowlist forgives).
forged_sigabrt = {
    "case": "crash_spontaneous_sigabrt", "script": "spontaneous_crash_probe.gd",
    "verdict": "PASS", "actual_exit": -6, "error": None,
    "output": ["Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf", "",
               "SPONTANEOUS_CRASH_PROBE: expected signature",
               "exited without the ERROR crash marker"],
}
self_sigkill = results["crash_self_sigkill"]
crash_marker = "SPONTANEOUS_CRASH_PROBE: expected signature"
crash_allowlist = ("ERROR: r60 spontaneous crash probe",)

def reclassify_crash(record, expected, allowed):
    return classify_process(record["actual_exit"], record["error"],
                            "\n".join(record["output"]), expected,
                            crash_marker, allowed)

def meta_ok(sa, sk):
    crash_discriminations = {
        "sigabrt_expected_-9_rejects": sa is not None and not reclassify_crash(sa, -9, crash_allowlist),
        "sigabrt_missing_allowlist_rejects": sa is not None and not reclassify_crash(sa, -6, ()),
        "sigabrt_wrong_allowlist_rejects": sa is not None and not reclassify_crash(sa, -6, ("ERROR: unrelated different diagnostic",)),
        "self_sigkill_expected_-6_rejects": sk is not None and not reclassify_crash(sk, -6, crash_allowlist),
    }
    return (sa is not None and sa["verdict"] == "PASS" and sa["actual_exit"] == -6
            and "ERROR: r60 spontaneous crash probe" in "\n".join(sa["output"])
            and sk is not None and sk["verdict"] == "PASS"
            and sk["actual_exit"] == -9
            and all(crash_discriminations.values()))

t3_real = meta_ok(sigabrt, self_sigkill)
t3_forged = meta_ok(forged_sigabrt, self_sigkill)
print("T3a meta expression on REAL records ->", t3_real, "(expect True)")
print("T3b meta expression on MARKERLESS -6 forged record ->", t3_forged, "(expect False)")

# also: markerless output THROUGH classify_process with allowlist -> False
# (signature present but ERROR line absent -> allowlist irrelevant; a version
# where the signature itself is missing also rejects)
forged_no_sig = dict(forged_sigabrt); forged_no_sig["output"] = ["no marker at all", "ERROR: r60 spontaneous crash probe"]
t4 = classify_process(-6, None, "\n".join(forged_no_sig["output"]), -6, MARKER, ALLOW)
print("T4 signature-missing -6 with allowlist ->", t4, "(expect False)")

ok = (t1 is False) and (t2 is True) and (t3_real is True) and (t3_forged is False) and (t4 is False)
print("SPOTCHECK:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
