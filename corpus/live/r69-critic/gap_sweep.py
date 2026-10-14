#!/usr/bin/env python3
"""r69 critic: independent gap-sweep measurement of the midlineforge window.

Replicates run_battery.surface_run record semantics (bounded Popen, merged
stdout+stderr text, signature/error scan, ppid provenance) against the
critic's own scratch copy of the fixture, which adds --midline-gap-ms=N
(same opt-in parse pattern as --midline-offset-ms).

Cells:
  declared  : offset=80  x gap {50,100,200,400,800} x REPS
  missing   : crossed cells the declared design never samples —
              offset>198ms at gap>offset, where gap-relative (fab) and
              absolute-~198ms-edge (miss) models DISAGREE.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

GODOT = "godot"
SCRATCH = Path(__file__).resolve().parent / "proj"
SIGNATURE = "DESCENDANT_PIPE_PROBE: expected signature"
MIDLINE_ERROR = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"
PPID_TOKEN = "DESCENDANT_PIPE_MIDLINE write_ppid="
BOUND = 8.0


def surface_run(offset_ms, gap_ms):
    cmd = [GODOT, "--headless", "--path", str(SCRATCH),
           "--script", "res://descendant_pipe_probe.gd", "--",
           "--spawn-midlineforge",
           f"--midline-offset-ms={offset_ms}",
           f"--midline-gap-ms={gap_ms}"]
    started = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=BOUND)
    elapsed = round(time.monotonic() - started, 3)
    so, se = proc.stdout or "", proc.stderr or ""
    text = so + se
    spliced = next(
        (line.strip() for line in text.splitlines()
         if "DESCENDANT_PIPE_PROBE: expected " in line
         and MIDLINE_ERROR in line), None)
    gp = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    wp = re.search(re.escape(PPID_TOKEN) + r"(\d+)", text)
    return {
        "offset_ms": offset_ms, "gap_ms": gap_ms,
        "exit": proc.returncode, "elapsed_s": elapsed,
        "signature_observed": SIGNATURE in text,
        "spliced_line": spliced,
        "fabrication_landed": spliced is not None,
        "standalone_error": any(
            line.strip() == MIDLINE_ERROR for line in text.splitlines()),
        "godot_pid": int(gp.group(1)) if gp else None,
        "write_ppid": int(wp.group(1)) if wp else None,
        "write_pre_death": bool(gp and wp and gp.group(1) == wp.group(1)),
        "raw_stdout_sha256": __import__("hashlib").sha256(so.encode()).hexdigest(),
        "raw_stderr_sha256": __import__("hashlib").sha256(se.encode()).hexdigest(),
        "merged_sha256": __import__("hashlib").sha256(text.encode()).hexdigest(),
        "swapped_sha256": __import__("hashlib").sha256((se + so).encode()).hexdigest(),
        "stdout_bytes": len(so.encode()), "stderr_bytes": len(se.encode()),
    }


def main():
    declared = [(80, g) for g in (50, 100, 200, 400, 800)]
    missing = [(300, 400), (300, 800), (600, 800), (300, 200)]
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    rows = []
    for off, gap in declared:
        for r in range(reps):
            rec = surface_run(off, gap)
            rec["cell"] = "declared"
            rec["rep"] = r
            rows.append(rec)
            print(f"off={off:>4} gap={gap:>4} r{r} "
                  f"fab={rec['fabrication_landed']} "
                  f"sig={rec['signature_observed']} "
                  f"pre_death={rec['write_pre_death']} "
                  f"elapsed={rec['elapsed_s']:.3f}", flush=True)
    for off, gap in missing:
        for r in range(reps):
            rec = surface_run(off, gap)
            rec["cell"] = "missing"
            rec["rep"] = r
            rows.append(rec)
            print(f"off={off:>4} gap={gap:>4} r{r} "
                  f"fab={rec['fabrication_landed']} "
                  f"sig={rec['signature_observed']} "
                  f"pre_death={rec['write_pre_death']} "
                  f"elapsed={rec['elapsed_s']:.3f}", flush=True)
    out = Path(__file__).resolve().parent / "gap-sweep-results.json"
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"wrote {out}", flush=True)


if __name__ == "__main__":
    main()
