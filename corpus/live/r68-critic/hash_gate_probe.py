#!/usr/bin/env python3
"""r68 critic — attack (4): can the sha256(raw_stdout)+sha256(raw_stderr)
'same-input gate' be gamed — same captured bytes, different delivery timing?

G1 delivery-order blindness: two REAL subprocess captures with opposite
   emission order produce byte-identical (stdout,stderr) → identical
   hashes. The hash binds byte content, never interleave/delivery timing —
   which is exactly the causal axis the seam arms exist to question.
G2 vacuity: in committed run_battery.py, dual_classify(so,se,code,error,..)
   feeds the SAME string objects to classify_process(so+se) and
   classify_streams(so,se) — hash equality is guaranteed by call
   construction, not measured. The gate witnesses a tautology.
G3 partial-input certification: the verdict depends on allowlists too;
   identical hashes + different allowlists → different verdicts. The gate
   certifies 2 of the ≥5 inputs.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verbatim_classifiers import classify_process, classify_streams

SIG = "STREAM_STDOUT: expected attribution marker"
STRUCT_ENTRY = "ERROR: chain incomplete"
STRUCT_LINE = ("ERROR: chain incomplete collections=streamdiv "
               "scene=SceneB:<Node#6700> old_alive=false")

def h(b):
    return hashlib.sha256(b.encode()).hexdigest()

results = {}

# G1 — real captures, opposite delivery order, byte-identical streams.
src_first = ("import sys; sys.stderr.write('MARK_B\\n'); sys.stderr.flush(); "
             "import time; time.sleep(0.05); sys.stdout.write('MARK_A\\n')")
src_last = ("import sys; sys.stdout.write('MARK_A\\n'); sys.stdout.flush(); "
            "import time; time.sleep(0.05); sys.stderr.write('MARK_B\\n')")
p1 = subprocess.run([sys.executable, "-c", src_first],
                    capture_output=True, text=True)
p2 = subprocess.run([sys.executable, "-c", src_last],
                    capture_output=True, text=True)
results["G1_delivery_order_blindness"] = {
    "capture_first_stderr_first": {
        "stdout": p1.stdout, "stderr": p1.stderr,
        "sha256_stdout": h(p1.stdout), "sha256_stderr": h(p1.stderr),
        "emission_order": "stderr BEFORE stdout (50ms separation)",
    },
    "capture_last_stderr_last": {
        "stdout": p2.stdout, "stderr": p2.stderr,
        "sha256_stdout": h(p2.stdout), "sha256_stderr": h(p2.stderr),
        "emission_order": "stderr AFTER stdout (50ms separation)",
    },
    "hashes_identical": (h(p1.stdout) == h(p2.stdout)
                         and h(p1.stderr) == h(p2.stderr)),
    "note": ("the gate cannot tell which capture has stderr-first vs "
             "stderr-last delivery — the exact fact that decides whether a "
             "merged-concat seam line is a real emission or an artifact."),
}

# G2 — vacuity: single capture feeds both classifiers by construction.
so = "Godot banner\n" + SIG + "\nERROR: x\n"
se = "WARN: y\n"
results["G2_same_object_construction"] = {
    "merged": classify_process(0, None, so + se, 0, SIG),
    "streams": classify_streams(0, None, so, se, 0, SIG),
    "sha256_stdout": h(so), "sha256_stderr": h(se),
    "note": ("dual_classify passes the same objects; a hash mismatch is "
             "impossible unless the record fields are mutated post-classify "
             "— the gate guards transcription drift, not input sameness."),
}

# G3 — same bytes, different allowlists → different verdicts, same hashes.
so3 = "Godot banner\n" + SIG + "\n"
se3 = STRUCT_LINE + "\n"
verdicts = {}
for label, ma, sa in (("bare", (), ()),
                      ("entry_both", (STRUCT_ENTRY,), (STRUCT_ENTRY,)),
                      ("entry_merged_only", (STRUCT_ENTRY,), ())):
    verdicts[label] = {
        "merged": classify_process(0, None, so3 + se3, 0, SIG, ma),
        "streams": classify_streams(0, None, so3, se3, 0, SIG, sa),
        "sha256_stdout": h(so3), "sha256_stderr": h(se3),
    }
results["G3_allowlist_not_covered"] = {
    "stdout": so3, "stderr": se3, "verdicts_by_allowlist": verdicts,
    "note": ("identical sha256 pairs across three records whose merged/"
             "streams verdict pairs differ (False/False, True/False, "
             "False/False) — 'same input' certifies bytes only; the "
             "allowlist is an unhashed input that flips verdicts."),
}

out = HERE / "hash-gate-results.json"
out.write_text(json.dumps(results, indent=2))
print(json.dumps({k: (v.get("hashes_identical") or "see file")
                  for k, v in results.items()}, indent=2))
