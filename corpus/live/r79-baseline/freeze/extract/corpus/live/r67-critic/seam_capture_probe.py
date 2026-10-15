#!/usr/bin/env python3
"""Real-capture seam forgery: a subprocess emits stdout WITHOUT trailing
newline + a stderr line; capture exactly like run_process_streams, then
classify both ways. The merged 'ERROR:' exists only inside the harness's
own stdout+stderr concatenation."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verbatim_classifiers import classify_process, classify_streams

SIG = "CRITIC_E2E: expected marker"
child = ("import sys;"
         "sys.stdout.write('%s\\nERR');"
         "sys.stdout.flush();"
         "sys.stderr.write('OR: allowlisted tail\\n');"
         "sys.stderr.flush()" % SIG)
p = subprocess.run([sys.executable, "-c", child], capture_output=True, text=True)
merged_text = p.stdout + p.stderr
row = {
    "stdout_repr": p.stdout, "stderr_repr": p.stderr,
    "merged_repr": merged_text,
    "merged_contains_ERROR": "ERROR:" in merged_text,
    "either_stream_contains_ERROR": ("ERROR:" in p.stdout or "ERROR:" in p.stderr),
}
row["merged_verdict"] = classify_process(p.returncode, None, merged_text, 0, SIG, ())
row["streams_verdict"] = classify_streams(p.returncode, None, p.stdout, p.stderr, 0, SIG,
                                          ("OR: allowlisted tail",))
# twin: signature forged across the same seam
child2 = ("import sys;"
          "sys.stdout.write('banner\\n%s');"
          "sys.stdout.flush();"
          "sys.stderr.write('%s\\n');"
          "sys.stderr.flush()" % (SIG[:10], SIG[10:]))
p2 = subprocess.run([sys.executable, "-c", child2], capture_output=True, text=True)
m2 = p2.stdout + p2.stderr
row["sig_seam"] = {
    "stdout_repr": p2.stdout, "stderr_repr": p2.stderr,
    "sig_in_merged": SIG in m2,
    "sig_in_stdout": SIG in p2.stdout, "sig_in_stderr": SIG in p2.stderr,
    "merged_verdict": classify_process(p2.returncode, None, m2, 0, SIG, ()),
    "streams_verdict": classify_streams(p2.returncode, None, p2.stdout, p2.stderr, 0, SIG, ()),
}
(HERE / "seam_results.json").write_text(json.dumps(row, indent=2) + "\n")
print(json.dumps(row, indent=2))
