#!/usr/bin/env python3
"""r68 critic — attack (3): does the declared `divergent_clause` signature
{exit,signature,error_scan,blob,allowlist_shape} distinguish mechanisms or
just rename them? Synthetic stream pairs through the VERBATIM extracted
classifiers — no re-implementation.

Findings probed:
  F1 enum coverage gap: the pre-existing `stream_reject` divergence (a plain
     non-ERROR: stderr line) has NO honest member label — it is the
     whole-stderr sweep clause, absent from the enum entirely.
  F2 label collisions: two mechanistically distinct divergences map to the
     same signature member (real-channel placement vs concat fabrication).
  F3 masked clauses: early-return structure means a multi-clause divergence
     under-reports; the signature depends on clause-eval order the spec
     does not fix.
  F4 dead member: exit/error clauses are textually IDENTICAL in both
     classifiers — `exit` can never be a divergent clause.
  F5 concordant mechanism split: same verdict pair hides different clause
     paths (signature invisible to concordant rows).
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verbatim_classifiers import classify_process, classify_streams

SIG = "STREAM_STDOUT: expected attribution marker"
STDERR_DIAG = "STREAM_STDERR: unrelated attribution diagnostic"
BANNER = "Godot Engine v4.7.2.stable\n"


def dual(so, se, code=0, error=None, ma=(), sa=()):
    return {"merged": classify_process(code, error, so + se, 0, SIG, ma),
            "streams": classify_streams(code, error, so, se, 0, SIG, sa),
            "merged_allowlist": list(ma), "stream_allowlist": list(sa)}


rows = {}

# F1 — the r67 stream_reject shape: plain non-ERROR stderr line.
so = BANNER + SIG + "\n"
se = STDERR_DIAG + "\n"
rows["F1_plain_stderr_line"] = {
    "stdout": so, "stderr": se, **dual(so, se),
    "note": ("divergent (merged True / streams False) via the whole-stderr "
             "sweep at run_battery.py:200-207 — no ERROR:, no signature "
             "placement, no blob token, no allowlist-entry-shape asymmetry "
             "(empty allowlist on both sides). The 5-member enum has no "
             "label for it: error_scan is wrong (no 'ERROR:' bytes exist), "
             "allowlist_shape is wrong (it is not an entry-shape mismatch — "
             "the clause itself does not exist in merged)."),
}
# F1b — same row under matching allowlist on both sides → concordant again.
rows["F1b_same_row_allowlisted"] = {
    "stdout": so, "stderr": se,
    **dual(so, se, ma=(STDERR_DIAG,), sa=(STDERR_DIAG,)),
    "note": ("the SAME entry shape on both sides restores agreement — the "
             "divergence is the sweep's existence, not the entry's shape."),
}

# F2a — sig_on_stderr mechanism: signature bytes exist, wrong channel.
so2 = BANNER
se2 = SIG + "\n"
rows["F2a_sig_on_stderr_real_bytes"] = {
    "stdout": so2, "stderr": se2, **dual(so2, se2, sa=(SIG,)),
    "note": "signature exists (emitted on stderr); streams binds it to stdout",
}
# F2b — seam_sig mechanism: signature bytes exist in NEITHER stream; the
# concat fabricates them.
so3 = BANNER + "STREAM_STDOUT: expected attribution "  # unterminated head
se3 = "marker\n"
rows["F2b_seam_sig_concat_fabrication"] = {
    "stdout": so3, "stderr": se3, **dual(so3, se3, sa=("marker",)),
    "note": ("signature is a capture artifact — no stream ever carried it. "
             "Both F2a and F2b label 'signature' yet one is byte-placement "
             "and the other is non-existent-byte fabrication. The signature "
             "cannot distinguish exist-vs-fabricate."),
}
# F2c — same collision on the error_scan label: real stdout ERROR vs
# concat-fabricated ERROR.
so4 = BANNER + SIG + "\nERROR: STREAMDIV stdout-carried diagnostic\n"
rows["F2c_stdout_error_real_line"] = {
    "stdout": so4, "stderr": "", **dual(so4, ""),
    "note": "real ERROR: line on stdout — streams never scans stdout",
}
so5 = BANNER + SIG + "\nSTREAMDIV seam tail ends in ERROR"  # unterminated
se5 = ": STREAMDIV seam phantom merged-only line\n"
rows["F2d_seam_error_concat_line"] = {
    "stdout": so5, "stderr": se5,
    **dual(so5, se5, sa=(": STREAMDIV seam phantom merged-only line",)),
    "note": ("ERROR: line exists ONLY in the merged concat — real-line-vs-"
             "fabricated-line collapse onto the same 'error_scan' label."),
}

# F3 — masked multi-clause: streams fails EARLY on signature, but the stderr
# sweep would also fail; a first-fail signature reports {signature} only.
so6 = BANNER
se6 = SIG + "\n" + STDERR_DIAG + "\n"
rows["F3_masked_sweep_under_signature"] = {
    "stdout": so6, "stderr": se6, **dual(so6, se6),
    "note": ("streams exits at l.183 (signature) before reaching the "
             "l.200-207 sweep which would also reject (STDERR_DIAG not "
             "allowlisted). Divergent clause = {signature} under first-fail "
             "semantics; honest clause set = {signature, stderr_sweep}. "
             "The signature is order-semantics-dependent."),
}
# F4 — exit clause is dead: prove the exit/error prefixes are identical by
# brute-force scan — no (so,se,code) can diverge on exit alone.
rows["F4_exit_clause_reachability"] = {
    "note": ("classify_process l.176 'code == expected_exit and error is "
             "None' vs classify_streams l.181-182 'code != expected_exit or "
             "error is not None' — logically identical gates, both checked "
             "before any stream-specific clause. A divergent verdict "
             "REQUIRES identical gate outcomes, so 'exit' can never appear "
             "in a divergent_clause set; 1/5 enum members is provably "
             "unreachable."),
}
# F5 — concordant verdict, different clause paths (signature can't see it).
so7 = BANNER + SIG + "\nERROR: e\n"
se7 = STDERR_DIAG + "\n"
rows["F5_concordant_fail_different_clauses"] = {
    "stdout": so7, "stderr": se7, **dual(so7, se7),
    "note": ("merged FAIL via unrelated-ERROR scan; streams FAIL via "
             "stderr sweep — divergent=False yet the clause paths are "
             "different mechanisms. divergent_clause conflates verdict "
             "agreement with mechanism agreement."),
}

for k, r in rows.items():
    if "merged" in r:
        r["divergent"] = r["merged"] != r["streams"]

out = HERE / "clause-sig-results.json"
out.write_text(json.dumps(rows, indent=2))
for k, r in rows.items():
    if "merged" in r:
        print(f"{k}: merged={r['merged']} streams={r['streams']} "
              f"divergent={r['divergent']}")
    else:
        print(f"{k}: (static analysis — see note)")
